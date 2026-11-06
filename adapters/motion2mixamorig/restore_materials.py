"""Blender-only: restore source FBX UVs/PBR on M2MR's animated GLB when topology matches exactly."""
import argparse
import json
from pathlib import Path
import sys
import bpy
from collections import Counter

def main():
    p=argparse.ArgumentParser();p.add_argument('--motion-glb',required=True);p.add_argument('--source-fbx',required=True);p.add_argument('--out',required=True);p.add_argument('--fps',type=int,default=30);p.add_argument('--frames',type=int,default=150)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete()
    sc=bpy.context.scene;sc.render.fps=a.fps;sc.frame_start=0;sc.frame_end=a.frames-1
    bpy.ops.import_scene.gltf(filepath=a.motion_glb)
    target=[o for o in sc.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]
    before=set(sc.objects);bpy.ops.import_scene.fbx(filepath=a.source_fbx)
    source_objects=set(sc.objects)-before
    source=[o for o in source_objects if o.type=='MESH']
    results=[]
    for dst in target:
        choices=[s for s in source if dst.name.endswith('_'+s.name) or dst.name==s.name]
        if len(choices)!=1:raise ValueError(f'No unique source geometry for {dst.name}')
        src=choices[0]
        if len(src.data.vertices)!=len(dst.data.vertices):raise ValueError('Vertex counts differ; use animation retargeting on the original asset instead')
        # M2MR fan-triangulates FBX polygons without changing vertex numbering.
        # Compare that exact triangulation, not approximate positions/projection.
        faces={}
        for original in src.data.polygons:
            vertices=list(original.vertices)
            for i in range(1,len(vertices)-1):
                key=tuple(sorted((vertices[0],vertices[i],vertices[i+1])))
                if key in faces:raise ValueError('Ambiguous duplicate source triangle; use the original asset for retargeting')
                faces[key]=original
        if len(dst.data.polygons)!=len(faces):raise ValueError('Face counts differ after exact FBX fan triangulation')
        mapping=[]
        seen=Counter()
        for f in dst.data.polygons:
            key=tuple(sorted(f.vertices));match=faces.get(key);seen[key]+=1
            if match is None:raise ValueError('Topology differs; refusing approximate UV projection')
            mapping.append(match)
        if any(n!=1 for n in seen.values()) or len(seen)!=len(faces):raise ValueError('Triangle identity is not one-to-one')
        dst.data.materials.clear()
        for mat in src.data.materials:dst.data.materials.append(mat)
        for layer in src.data.uv_layers:
            target_uv=dst.data.uv_layers.get(layer.name) or dst.data.uv_layers.new(name=layer.name)
            for polygon,original in zip(dst.data.polygons,mapping):
                source_uv={src.data.loops[i].vertex_index:layer.data[i].uv.copy() for i in original.loop_indices}
                for i in polygon.loop_indices:target_uv.data[i].uv=source_uv[dst.data.loops[i].vertex_index]
        for polygon,original in zip(dst.data.polygons,mapping):polygon.material_index=original.material_index
        results.append({'target':dst.name,'source':src.name,'vertices':len(dst.data.vertices),'faces':len(mapping),'source_polygons':len(src.data.polygons),'uv_maps':len(dst.data.uv_layers),'material_slots':len(dst.data.materials),'topology_exact':True,'triangulation':'Exact FBX polygon fan; vertex identities and every triangle checked'})
    for name in [o.name for o in source_objects]:
        o=bpy.data.objects.get(name)
        if o is not None:bpy.data.objects.remove(o,do_unlink=True)
    helpers={pb.custom_shape for ar in sc.objects if ar.type=='ARMATURE' for pb in ar.pose.bones if pb.custom_shape}
    for ar in [o for o in sc.objects if o.type=='ARMATURE']:
        for pb in ar.pose.bones:pb.custom_shape=None
    for h in helpers:bpy.data.objects.remove(h,do_unlink=True)
    sc.frame_set(0);bpy.ops.file.pack_all()
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'textured-motion.blend'))
    bpy.ops.export_scene.gltf(filepath=str(out/'textured-motion.glb'),export_format='GLB',export_animations=True,export_skins=True,export_animation_mode='ACTIVE_ACTIONS',export_cameras=False,export_lights=False)
    report={'source_fbx':a.source_fbx,'motion_glb':a.motion_glb,'fps':a.fps,'frames':a.frames,'meshes':results,'blend':str(out/'textured-motion.blend'),'glb':str(out/'textured-motion.glb'),'images':[{'name':im.name,'packed':bool(im.packed_file),'size':list(im.size)} for im in bpy.data.images if im.type=='IMAGE' and im.users]}
    (out/'material-restoration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('@@JSON@@'+json.dumps(report,ensure_ascii=False))

main()
