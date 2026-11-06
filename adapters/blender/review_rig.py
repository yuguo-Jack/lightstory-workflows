"""Blender-only verification of a generated rig or imported motion, using installed Blender skills."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path
import bpy

SK=Path(__file__).resolve().parents[2]/'third_party/skills/blender-skills'

def module(skill,name):
    p=SK/skill/'scripts'/f'{name}.py'
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--out',required=True);p.add_argument('--motion',action='store_true');p.add_argument('--generic',action='store_true');p.add_argument('--fps',type=int,default=30);p.add_argument('--frames',type=int,default=150);p.add_argument('--no-topology',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete()
    # glTF animation times are seconds; Blender converts them using FPS during import.
    bpy.context.scene.render.fps=a.fps
    bpy.ops.import_scene.gltf(filepath=a.model)
    arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    # glTF importer creates viewport bone custom-shape objects. They are display
    # aids, not source geometry; exclude them from QA, renders, and FBX export.
    helpers={pb.custom_shape for ar in arms for pb in ar.pose.bones if pb.custom_shape is not None}
    for ar in arms:
        for pb in ar.pose.bones:
            if pb.custom_shape in helpers:pb.custom_shape=None
    for h in helpers:bpy.data.objects.remove(h,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    if len(arms)!=1:raise ValueError(f'Expected one armature, found {len(arms)}')
    arm=arms[0];names=[o.name for o in meshes]
    report={'source':a.model,'blender':bpy.app.version_string,'bones':len(arm.data.bones),'meshes':[{'name':o.name,'tris':sum(len(f.vertices)-2 for f in o.data.polygons),'verts':len(o.data.vertices),'materials':len(o.data.materials),'dimensions':list(o.dimensions)} for o in meshes]}
    if any(abs(v-1)>1e-5 for v in arm.scale):
        report['source_transform_warning']='Input rig transforms were preserved; normalize the source rig before a new binding when the target engine requires unit armature scale.'
    bpy.context.scene.render.fps=a.fps
    bpy.context.scene.frame_start=0;bpy.context.scene.frame_end=a.frames-1
    report['rig_qa']=module('blender-character-rigging','rig_check').run(armature=arm.name,meshes=names,profile='game')
    (out/'rig-check.json').write_text(json.dumps(report['rig_qa'],ensure_ascii=False,indent=2),encoding='utf-8')
    if not a.no_topology:
        report['mesh_qa']=module('blender-asset-qa','qa_check').run(objects=names,profile='game')
        (out/'mesh-check.json').write_text(json.dumps(report['mesh_qa'],ensure_ascii=False,indent=2),encoding='utf-8')
    else:report['mesh_qa']={'skipped':'Geometry is unchanged; topology reviewed on source separately.'}
    if a.generic:
        arm.animation_data_create();arm.animation_data.action=bpy.data.actions.new('QA_Generic_Deformation')
        selected=[pb.name for i,pb in enumerate(arm.pose.bones) if pb.parent and i%3==0]
        for f,angle in [(1,0),(20,.25),(40,-.25)]:
            bpy.context.scene.frame_set(f)
            for pb in arm.pose.bones:
                pb.rotation_mode='XYZ';pb.rotation_euler=(angle if pb.name in selected else 0,0,0)
                pb.keyframe_insert('rotation_euler',frame=f)
        frames=[1,20,40];bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=40
        report['stress']={'type':'small-angle generic deformation smoke, not an anatomical walk cycle','bones':selected,'radians':.25}
    elif not a.motion:
        report['stress']=module('blender-character-rigging','stress_poses').run(armature=arm.name)
        frames=[1,10,20,30,40,50]
    else:
        frames=[0,a.frames//5,2*a.frames//5,3*a.frames//5,4*a.frames//5,a.frames-1]
        report['actions']=[{'name':act.name,'frame_range':list(act.frame_range)} for act in bpy.data.actions]
    review=module('blender-asset-qa','review_shots')
    bpy.context.scene.frame_set(frames[0]);bpy.context.view_layer.update()
    report['rest_angles']=review.run(objects=names,out=str(out/'angles.png'),views=['front','right','back','three_quarter'],mode='material',res=512)
    report['wire']=review.run(objects=names,out=str(out/'wire.png'),views=['front','three_quarter'],mode='wire',res=512)
    report['poses']=[]
    for f in frames:
        bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
        sheet=review.run(objects=names,out=str(out/f'pose_{f:03d}.png'),views=['three_quarter'],mode='material',res=512)
        report['poses'].append({'frame':f,**sheet})
    bpy.context.scene.frame_set(frames[0])
    blend=out/'review.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(blend));report['blend']=str(blend)
    report['export']=module('blender-export-pipelines','export_asset').run(preset='unreal_skeletal',objects=[arm.name]+names,out=str(out/'animation.fbx'))
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete()
    bpy.ops.import_scene.fbx(filepath=str(out/'animation.fbx'),anim_offset=0.0)
    ra=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];rm=[o for o in bpy.context.scene.objects if o.type=='MESH']
    report['fbx_roundtrip']={'armatures':len(ra),'bones':[len(o.data.bones) for o in ra],'armature_scales':[list(o.scale) for o in ra],'mesh_dimensions':[list(o.dimensions) for o in rm],'actions':[{'name':act.name,'frames':list(act.frame_range)} for act in bpy.data.actions if act.users]}
    (out/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('@@JSON@@'+json.dumps({k:v for k,v in report.items() if k not in ('rig_qa','mesh_qa','meshes','rest_angles','wire','poses')},ensure_ascii=False))

main()
