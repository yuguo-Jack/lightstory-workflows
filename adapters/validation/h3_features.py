"""Inspect requested H3 feature execution evidence; never submit or alter inference."""
import argparse
import json
import re
from pathlib import Path

def inspect_features(graph, history, log, output_size):
    report = '\n'.join(line for output in history.get('outputs', {}).values() for line in output.get('text', []) if isinstance(line,str))
    features, errors, warnings = {}, [], []
    classes = {node['class_type']: node for node in graph.values()}
    if 'LoraLoaderModelOnly' in classes:
        patches = [int(x) for x in re.findall(r'Model MiniMaxH3 prepared[^\n]*? (\d+) patches attached', log)]
        unloaded = re.findall(r'[^\n]*lora key not loaded[^\n]*', log, re.I)
        features['lora'] = {'active_patches': max(patches, default=0), 'unloaded_keys': unloaded,
                            'requested': [n['inputs']['lora_name'] for n in graph.values() if n['class_type'] == 'LoraLoaderModelOnly']}
        if not patches or max(patches) == 0:
            errors.append('LoRA workflow has no active MiniMaxH3 patches in its execution log')
        if unloaded:
            errors.append('Some requested LoRA keys did not load; inspect compatibility before acceptance')
    if 'MiniMaxH3DirectorRefine' in classes:
        mode = classes['MiniMaxH3DirectorRefine']['inputs']['mode']
        applied = 'refine ' + mode in report and 'refine FAILED' not in report
        features['refine'] = {'mode': mode, 'applied': applied,
                              'actual_reports': [line for line in report.splitlines() if 'refine ' in line.lower()]}
        if not applied:
            errors.append('Requested refinement/upscale did not complete; base-pass fallback is not a pass')
        if mode in ('upscale', 'latent_upscale'):
            director = classes['MiniMaxH3Director']['inputs']
            timeline = json.loads(director['timeline_data'])
            base = timeline.get('output', {})
            area = int(base.get('width') or director['width']) * int(base.get('height') or director['height'])
            if output_size[0] * output_size[1] <= area:
                errors.append('Upscale workflow did not increase actual output area')
    if 'MiniMaxH3DirectorSelfLift' in classes:
        applied = ': SelfLift scale=' in report
        features['selflift'] = {'applied': applied}
        if not applied:
            errors.append('SelfLift was connected but no actual per-segment execution was reported')
    if 'MiniMaxH3DirectorSemanticBridge' in classes:
        applied = 'Semantic Bridge applied' in report + '\n' + log
        features['semantic_bridge'] = {'applied': applied}
        if not applied:
            errors.append('SemanticBridge was skipped or not reported as applied')
    if 'MiniMaxH3DirectorFaceRefine' in classes:
        counts = [(int(a), int(b)) for a, b in re.findall(r'FaceRefine track: (\d+)/(\d+) faces', report + '\n' + log)]
        applied = any(found > 0 for found, _ in counts) and 'FaceRefine skipped' not in report
        features['face_refine'] = {'applied': applied, 'detected_frames': counts}
        if not applied:
            errors.append('FaceRefine had no positive face tracking/refinement execution evidence')
    warnings += [line for line in log.splitlines() if re.search(r'falling back|has NaN|refine failed|Semantic Bridge skipped', line, re.I)]
    return {'schema_version': 2, 'passed': not errors, 'features': features, 'errors': errors, 'warnings': warnings,
            'scope': 'Checks actual feature execution and catches silent no-op/fallback; does not certify visual improvement.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['request','history','log']:p.add_argument('--'+name,required=True)
    p.add_argument('--width',type=int,required=True);p.add_argument('--height',type=int,required=True);p.add_argument('--out')
    a=p.parse_args();graph=json.loads(Path(a.request).read_text('utf-8-sig'));history=json.loads(Path(a.history).read_text('utf-8-sig'))
    result=inspect_features(graph,history,Path(a.log).read_text('utf-8-sig'),[a.width,a.height])
    if a.out:
        target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('x',encoding='utf-8') as f:f.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
