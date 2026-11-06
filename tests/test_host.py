"""Observable host invariants; no real weights, GPU, account or editor calls."""
from pathlib import Path
import contextlib
import hashlib
import io
import importlib.util
import json
import os
import shutil
import struct
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import wave
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'src'))
from lightstory.config import Config,contained,write_new
from lightstory import audit,cli,dependencies,exporter,install,models,portal,runtime,workflows


class HostTests(unittest.TestCase):
    def setUp(self):
        parent=REPO/'.local/test-runs';parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='host-',dir=parent)
        self.root=Path(self.temp.name).resolve()
        if not self.root.is_relative_to(parent.resolve()):raise RuntimeError('Test root escaped workspace')
        self.profile=self.root/'host.json'
        self.data={'paths':{'state_root':str(self.root/'state'),'projects_root':str(self.root/'projects'),'tools_root':str(self.root/'tools'),'models_root':str(self.root/'models'),'comfyui_root':str(self.root/'ComfyUI')}}
        write_new(self.profile,self.data)
        self.cfg=Config(REPO,self.profile,self.data)

    def tearDown(self):
        self.temp.cleanup()

    def test_configuration_has_no_creation_side_effect_and_is_relocatable(self):
        self.assertFalse(self.cfg.state_root.exists())
        self.assertEqual(self.cfg.models,self.root/'models')
        self.assertFalse(self.cfg.state_root.exists())
        self.data['paths']['state_root']='${REPO}/.lightstory-test'
        self.assertEqual(self.cfg.state_root,REPO/'.lightstory-test')
        self.assertFalse(self.cfg.state_root.exists())

    def test_existing_configuration_is_never_overwritten(self):
        old=self.profile.read_bytes()
        with self.assertRaises(FileExistsError):write_new(self.profile,{'bad':True})
        self.assertEqual(old,self.profile.read_bytes())

    def test_local_endpoint_and_path_escape_guards(self):
        self.data['services']={'comfyui_url':'http://example.org:8188'}
        with self.assertRaises(ValueError):_ = self.cfg.url
        with self.assertRaises(ValueError):contained(self.root/'../outside',self.root)

    def test_published_library_closure(self):
        value=audit.validate(self.cfg)
        self.assertTrue(value['passed'],value['errors'])
        self.assertEqual(value['UI_API_JSON_checked'],2*value['workflows'])

    def test_prepare_preserves_source_and_isolated_output(self):
        name='Qwen-Image 2.1/01_文生图';row=workflows.resolve(self.cfg,name);source=workflows.api(self.cfg,row)
        before=source.read_bytes();dest=self.root/'job/request.api.json'
        result=workflows.prepare(self.cfg,name,out=dest,prefix='Projects/demo/t2i')
        self.assertFalse(result['submitted']);self.assertTrue(dest.is_file());self.assertEqual(source.read_bytes(),before)
        with self.assertRaises(FileExistsError):workflows.prepare(self.cfg,name,out=dest)
        with self.assertRaises(ValueError):workflows.prepare(self.cfg,name,out=REPO/'workflows/bad.json')
        with self.assertRaises(ValueError):workflows.prepare(self.cfg,name,prefix='../other',out=self.root/'bad.json')

    def test_unbound_media_and_wrong_override_are_rejected(self):
        with self.assertRaises(ValueError):workflows.prepare(self.cfg,'Qwen-Image 2.1/02_单图编辑',out=self.root/'bad.json')
        with self.assertRaises(ValueError):workflows.prepare(self.cfg,'Qwen-Image 2.1/01_文生图',overrides={'not-a-node':{'seed':1}},out=self.root/'bad.json')

    def test_ui_install_conflicts_preserve_existing_files(self):
        destination=self.root/'native-ui';plan=install.ui(self.cfg,target=destination)
        self.assertFalse(destination.exists());self.assertFalse(plan['applied'])
        result=install.ui(self.cfg,target=destination,apply=True);self.assertTrue(result['applied'])
        row=workflows.catalog(self.cfg)[0];p=destination/row['model']/(row['function']+'.json')
        p.write_text('user modified','utf-8')
        conflict=install.ui(self.cfg,target=destination,apply=True)
        self.assertFalse(conflict['applied']);self.assertTrue(conflict['conflicts']);self.assertEqual(p.read_text('utf-8'),'user modified')

    def test_skill_copy_install_and_discovery(self):
        dst=self.root/'native-skills'
        result=install.skills(self.cfg,target=dst,copy=True,apply=True)
        self.assertTrue(result['applied']);self.assertTrue((dst/'runtime-map.md').is_file())
        self.assertEqual(len(list(dst.glob('*/SKILL.md'))),29)
        self.assertTrue((dst/'blender-core/LICENSE').is_file())
        self.assertFalse(install.skills(self.cfg,target=dst,copy=True)['applied'])

    def test_symlink_install_resolves_when_platform_allows(self):
        source=self.root/'source';source.mkdir();(source/'SKILL.md').write_text('fixture','utf-8');target=self.root/'link'
        try:install.execute(install.install_plan([(source,target)]),apply=True)
        except OSError as e:self.skipTest('Symlink privilege not available: '+str(e))
        self.assertTrue(target.is_symlink());self.assertEqual(target.resolve(),source)
        self.assertEqual(install.install_plan([(source,target)])[0]['action'],'keep')

    def test_upstream_copy_install_needs_no_symbolic_links(self):
        upstream=self.root/'official-skills'
        overlays=REPO/'third_party/overlays/minimax-h3'
        for overlay in overlays.glob('*.md'):
            if overlay.name=='README.md':continue
            name='music-video-subtitle-generator' if overlay.stem=='mv-subtitle-skill-confirmed' else overlay.stem
            folder=upstream/'skills'/name;folder.mkdir(parents=True)
            (folder/'SKILL.md').write_text(f'---\nname: {name}\ndescription: |\n  Official fixture description.\n---\n\n# Official fixture body\n','utf-8')
            (folder/'reference.txt').write_text('Upstream resource preserved.','utf-8')
        target=self.root/'copied-skills'
        with patch.object(dependencies,'verify',return_value=True), patch.object(dependencies,'location',return_value=upstream), patch.object(Path,'symlink_to',side_effect=AssertionError('Copy mode attempted a symlink')):
            result=install.skills(self.cfg,target=target,upstream=True,copy=True,apply=True)
        self.assertTrue(result['applied'])
        self.assertEqual(len(list(target.glob('*/SKILL.md'))),38)
        self.assertTrue((self.cfg.state_root/'skills/runtime-map.md').is_file())
        for overlay in overlays.glob('*.md'):
            if overlay.name=='README.md':continue
            text=(target/overlay.stem/'SKILL.md').read_text('utf-8')
            self.assertIn('Official fixture body',text)
            self.assertIn('  Official fixture description.',text)
            self.assertTrue((target/overlay.stem/'reference.txt').is_file())

    def test_model_conversion_changes_only_header(self):
        original=self.root/'original.safetensors';dest=self.root/'converted.safetensors'
        header={'diffusion_model.layer.lora_A.weight':{'dtype':'F32','shape':[1],'data_offsets':[0,4]}}
        raw=json.dumps(header,separators=(',',':')).encode();raw+=b' '*(-len(raw)%8);payload=struct.pack('<f',0.125)
        original.write_bytes(struct.pack('<Q',len(raw))+raw+payload)
        result=models.normalize_next_scene(original,dest,models.sha(original))
        self.assertEqual(result['tensor_count'],1);self.assertTrue(result['payload_identical'])
        with dest.open('rb') as f:length=struct.unpack('<Q',f.read(8))[0];converted=json.loads(f.read(length));self.assertEqual(f.read(),payload)
        self.assertIn('layer.lora_A.weight',converted)
        with self.assertRaises(FileExistsError):models.normalize_next_scene(original,dest,models.sha(original))

    def test_resumable_download_checks_payload_and_preserves_existing(self):
        data=b'synthetic model fixture, not a real checkpoint'
        item={'id':'fixture','target_root':'models','relative_path':'test/fixture.safetensors','source':'https://example.org/public-file','size':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        p=models.target(self.cfg,item);p.parent.mkdir(parents=True);p.with_name(p.name+'.part').write_bytes(data[:5])
        class Response(io.BytesIO):
            status=206
            headers={'Content-Range':f'bytes 5-{len(data)-1}/{len(data)}'}
        with patch('urllib.request.urlopen',return_value=Response(data[5:])) as fetch:
            result=models.acquire(self.cfg,item,acknowledge_license=True)
            self.assertTrue(result['verified']);self.assertEqual(p.read_bytes(),data)
            self.assertEqual(fetch.call_args.args[0].headers.get('Range'),'bytes=5-')
        p.write_bytes(b'local user file')
        with self.assertRaises(ValueError):models.acquire(self.cfg,item,acknowledge_license=True)
        self.assertEqual(p.read_bytes(),b'local user file')

    def test_corrupted_download_is_not_installed(self):
        item={'id':'fixture','target_root':'models','relative_path':'test/bad.safetensors','source':'https://example.org/public-file','sha256':'0'*64}
        class Response(io.BytesIO):status=200;headers={}
        with patch('urllib.request.urlopen',return_value=Response(b'corrupt')):
            with self.assertRaises(ValueError):models.acquire(self.cfg,item,acknowledge_license=True)
        self.assertFalse(models.target(self.cfg,item).exists())

    def test_completed_partial_recovers_without_network(self):
        data=b'complete-but-not-renamed'
        item={'id':'fixture','target_root':'models','relative_path':'test/finished.safetensors','source':'https://example.org/public-file','size':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        p=models.target(self.cfg,item);p.parent.mkdir(parents=True);partial=p.with_name(p.name+'.part');partial.write_bytes(data)
        with patch('urllib.request.urlopen') as network:
            result=models.acquire(self.cfg,item,acknowledge_license=True)
        network.assert_not_called();self.assertTrue(result['recovered_partial']);self.assertEqual(p.read_bytes(),data)

    def test_dependency_requires_exact_patch_result(self):
        row={'id':'fixture','kind':'git','revision':'a'*40,'patched_files':{'node.py':hashlib.sha256(b'expected\n').hexdigest()}}
        root=dependencies.location(self.cfg,row);(root/'.git').mkdir(parents=True);(root/'node.py').write_bytes(b'expected\r\n')
        with patch('lightstory.dependencies.run',side_effect=lambda p,*a:'a'*40 if a[0]=='rev-parse' else 'node.py'):
            self.assertTrue(dependencies.verify(self.cfg,row))
            (root/'node.py').write_bytes(b'extra local changes\n')
            self.assertFalse(dependencies.verify(self.cfg,row))
            self.assertTrue(dependencies.verify(self.cfg,row,baseline_only=True))

    def test_export_snapshot_preserves_graph_and_source(self):
        src=self.root/'source';src.mkdir();api=src/'a.json';ui=src/'ui.json';catalog=src/'catalog.json'
        graph={'1':{'class_type':'LoadImage','inputs':{'image':'personal-photo.png'}},'2':{'class_type':'SaveImage','inputs':{'images':['1',0],'filename_prefix':'test'}}}
        write_new(api,graph);write_new(ui,{'nodes':[]});write_new(catalog,[{'model':'Fixture','function':'generic','api':str(api),'workflow':str(ui)}]);old=api.read_bytes()
        dst=self.root/'snapshot';result=exporter.export(self.cfg,catalog,dst);out=json.loads((dst/'workflows/api/Fixture/generic.api.json').read_text('utf-8'))
        self.assertEqual(out['2'],graph['2']);self.assertTrue(out['1']['inputs']['image'].startswith('UPLOAD_'));self.assertEqual(api.read_bytes(),old)
        with self.assertRaises(FileExistsError):exporter.export(self.cfg,catalog,dst)

    def test_portal_blocks_config_traversal_and_links(self):
        repo=self.root/'public';(repo/'docs').mkdir(parents=True);(repo/'config').mkdir();(repo/'workflows').mkdir();(repo/'config/local.json').write_text('private','utf-8')
        cfg=Config(repo,self.profile,{})
        h=object.__new__(portal.handler(cfg))
        for path in ['/config/local.json','/.local/secret','/workflows/%2e%2e/config/local.json']:
            self.assertTrue(h.translate_path(path).endswith('__not_served__'))
        try:(repo/'workflows/link.json').symlink_to(repo/'config/local.json')
        except OSError:return
        self.assertTrue(h.translate_path('/workflows/link.json').endswith('__not_served__'))

    def test_public_video_supports_seek_suffix_head_and_invalid_ranges(self):
        repo=self.root/'film-public';folder=repo/'docs/film';folder.mkdir(parents=True)
        payload=bytes(range(256))*4;(folder/'lightstory-intro.mp4').write_bytes(payload)
        cfg=Config(repo,self.profile,self.data)
        server=ThreadingHTTPServer(('127.0.0.1',0),portal.handler(cfg))
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        url=f'http://127.0.0.1:{server.server_port}/docs/film/lightstory-intro.mp4'
        try:
            with urlopen(Request(url,headers={'Range':'bytes=300-399'})) as response:
                self.assertEqual(response.status,206);self.assertEqual(response.read(),payload[300:400])
                self.assertEqual(response.headers['Content-Range'],'bytes 300-399/1024')
            with urlopen(Request(url,headers={'Range':'bytes=-7'})) as response:self.assertEqual(response.read(),payload[-7:])
            with urlopen(Request(url,method='HEAD')) as response:
                self.assertEqual(response.headers['Content-Length'],'1024');self.assertEqual(response.headers['Accept-Ranges'],'bytes');self.assertEqual(response.read(),b'')
            with self.assertRaises(HTTPError) as error:urlopen(Request(url,headers={'Range':'bytes=1024-'}))
            self.assertEqual(error.exception.code,416)
        finally:server.shutdown();server.server_close();worker.join(timeout=2)

    def test_blender_flags_are_forwarded_without_launching_editor(self):
        with patch('lightstory.cli.subprocess.run',return_value=subprocess_result(0)) as invoke,contextlib.redirect_stdout(io.StringIO()):
            code=cli.main(['--config',str(self.profile),'blender','--which'])
        self.assertEqual(code,0);self.assertIn('--which',invoke.call_args.args[0])

    def test_runtime_plan_does_not_start_process(self):
        self.cfg.comfy.mkdir();(self.cfg.comfy/'main.py').write_text('# fixture','utf-8')
        self.data['executables']={'comfyui_python':sys.executable}
        with patch('subprocess.Popen') as popen:
            plan=runtime.start(self.cfg,'Conservative')
        popen.assert_not_called();self.assertIn('--disable-dynamic-vram',plan['command']);self.assertFalse(self.cfg.runtime.exists())

    def test_owned_backend_accepts_absolute_entry_and_checks_identity(self):
        command=[sys.executable,str(self.cfg.comfy/'main.py'),'--port','8188']
        self.assertTrue(runtime.backend_command_matches(command,self.cfg.comfy,8188))
        self.assertFalse(runtime.backend_command_matches(command,self.root/'unrelated',8188))
        self.assertFalse(runtime.backend_command_matches(command,self.cfg.comfy,8189))

    def test_registered_existing_dependency_is_reused_without_mutation(self):
        root=self.root/'existing-node';root.mkdir();(root/'node.py').write_bytes(b'fixture')
        row={'id':'fixture','kind':'file','file':'node.py','sha256':hashlib.sha256(b'fixture').hexdigest()}
        self.data['dependency_paths']={'fixture':str(root)}
        with patch('lightstory.dependencies.resolve',return_value=row),patch('urllib.request.urlopen') as network:
            result=dependencies.fetch(self.cfg,'fixture')
        self.assertTrue(result['reused_existing_install']);network.assert_not_called()
        (root/'node.py').write_bytes(b'user edited')
        with patch('lightstory.dependencies.resolve',return_value=row),self.assertRaises(ValueError):dependencies.fetch(self.cfg,'fixture')
        self.assertEqual((root/'node.py').read_bytes(),b'user edited')

    def test_equivalent_existing_skin_model_path_is_preserved(self):
        source=self.root/'skin-node';source.mkdir();file=source/'local_config.json'
        write_new(file,{'models_dir':str(self.cfg.models/'skintokens').replace('\\','/'),'allow_download':False})
        original=file.read_bytes();row={'id':'skintokens','kind':'git','node_directory':'ComfyUI-SkinTokens-NoBlender'}
        with patch('lightstory.dependencies.registry',return_value=[row]),patch('lightstory.dependencies.verify',return_value=True),patch('lightstory.dependencies.location',return_value=source):
            result=install.nodes(self.cfg)
        self.assertFalse(result['applied']);self.assertEqual(file.read_bytes(),original)

    def test_native_workflow_namespace_can_preserve_existing_categories(self):
        self.assertEqual(self.cfg.ui_library,self.cfg.ui_root/'LightStory')
        self.data['installation']={'workflow_namespace':''};self.assertEqual(self.cfg.ui_library,self.cfg.ui_root)
        self.data['installation']['workflow_namespace']='../outside'
        with self.assertRaises(ValueError):_ = self.cfg.ui_library

    def test_linked_native_ui_is_recognized_without_following_leaf_for_containment(self):
        root=self.root/'ui-links';row=workflows.catalog(self.cfg)[0];target=root/row['model']/(row['function']+'.json');target.parent.mkdir(parents=True)
        source=self.cfg.repository/row['workflow']
        try:target.symlink_to(source)
        except OSError as e:self.skipTest('Symlink privilege unavailable: '+str(e))
        result=install.ui(self.cfg,target=root)
        match=next(x for x in result['plan'] if Path(x['target'])==target)
        self.assertEqual(match['action'],'keep');self.assertEqual(target.resolve(),source)

    def test_graph_authoring_roundtrip_and_h3_silent_fallback_checks(self):
        def load(name,relative):
            spec=importlib.util.spec_from_file_location(name,REPO/relative);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
        helper=load('graph_helpers','adapters/comfyui/graph_tools.py')
        info={'Source':{'input':{'required':{'value':['INT',{'default':1}]}},'output':['IMAGE'],'output_name':['image']},'Sink':{'input':{'required':{'images':['IMAGE',{}]}}}}
        graph={'1':{'class_type':'Source','inputs':{'value':7}},'2':{'class_type':'Sink','inputs':{'images':['1',0]}}}
        restored=helper.template_to_api(helper.api_to_ui(graph,info=info),info=info)
        self.assertEqual({k:{x:y for x,y in v.items() if x!='_meta'} for k,v in restored.items()},graph)
        checks=load('h3_checks','adapters/validation/h3_features.py')
        requested={'1':{'class_type':'LoraLoaderModelOnly','inputs':{'lora_name':'fixture.safetensors'}}}
        self.assertFalse(checks.inspect_features(requested,{'outputs':{}},'',(64,64))['passed'])
        self.assertTrue(checks.inspect_features(requested,{'outputs':{}},'Model MiniMaxH3 prepared 8 patches attached',(64,64))['passed'])

    def test_media_probe_and_complete_decode_on_synthetic_audio(self):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):self.skipTest('Optional FFmpeg tools unavailable')
        from lightstory import media
        source=self.root/'synthetic.wav'
        with wave.open(str(source),'wb') as stream:stream.setnchannels(1);stream.setsampwidth(2);stream.setframerate(8000);stream.writeframes(b'\0\0'*800)
        result=media.inspect(self.cfg,source,decode=True)
        self.assertTrue(result['decode_passed']);self.assertEqual(result['streams'][0]['codec_type'],'audio')

    def test_history_preview_requires_explicit_flag_and_rejects_escape(self):
        archive=self.root/'history';(archive/'validation').mkdir(parents=True);example=archive/'validation/report.json';example.write_text('{}','utf-8')
        self.data['paths']['history_root']=str(archive)
        plain=object.__new__(portal.handler(self.cfg));enabled=object.__new__(portal.handler(self.cfg,True))
        self.assertTrue(plain.translate_path('/workflow-support/validation/report.json').endswith('__not_served__'))
        self.assertEqual(enabled.translate_path('/workflow-support/validation/report.json'),str(example))
        self.assertTrue(enabled.translate_path('/workflow-support/runtime/process.json').endswith('__not_served__'))
        self.assertTrue(enabled.translate_path('/workflow-support/../host.json').endswith('__not_served__'))


def subprocess_result(code):
    import subprocess
    return subprocess.CompletedProcess([],code,'','')


if __name__=='__main__':unittest.main()
