"""Inspect skinning/animation and optional geometry/material preservation in a GLB, without loading a GPU."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
import numpy as np

DT={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}
N={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16,'MAT3':9,'MAT2':4}

class GLB:
    def __init__(self,path):
        self.path=Path(path);data=self.path.read_bytes()
        magic,v,length=struct.unpack_from('<4sII',data)
        if (magic,v,length)!=(b'glTF',2,len(data)):raise ValueError('Invalid GLB header')
        size,typ=struct.unpack_from('<II',data,12)
        if typ!=0x4e4f534a:raise ValueError('Missing JSON chunk')
        self.j=json.loads(data[20:20+size]);self.b=data[28+size:]
    def accessor(self,i):
        a=self.j['accessors'][i];v=self.j['bufferViews'][a['bufferView']]
        dtype=np.dtype(DT[a['componentType']]).newbyteorder('<');width=N[a['type']]
        off=v.get('byteOffset',0)+a.get('byteOffset',0)
        arr=np.ndarray((a['count'],width),dtype=dtype,buffer=self.b,offset=off,strides=(v.get('byteStride',dtype.itemsize*width),dtype.itemsize)).copy()
        if a.get('normalized') and dtype.kind in 'ui':arr=arr.astype(float)/np.iinfo(dtype).max
        return arr
    def signatures(self):
        rows=[]
        for m in self.j.get('meshes',[]):
            for p in m['primitives']:
                attr={k:hashlib.sha256(self.accessor(i).tobytes()).hexdigest() for k,i in p['attributes'].items() if not k.startswith(('JOINTS','WEIGHTS'))}
                rows.append({'attributes':attr,'indices':hashlib.sha256(self.accessor(p['indices']).tobytes()).hexdigest() if 'indices'in p else None,'material':p.get('material')})
        imgs=[]
        for a in self.j.get('images',[]):
            if 'bufferView'in a:
                v=self.j['bufferViews'][a['bufferView']];start=v.get('byteOffset',0)
                imgs.append(hashlib.sha256(self.b[start:start+v['byteLength']]).hexdigest())
            else:imgs.append(a.get('uri'))
        return {'primitives':rows,'materials':self.j.get('materials',[]),'images_sha256':imgs}
    def world_geometry(self):
        parents={c:i for i,n in enumerate(self.j.get('nodes',[])) for c in n.get('children',[])}
        cache={}
        def matrix(i):
            if i in cache:return cache[i]
            n=self.j['nodes'][i]
            if 'matrix'in n:m=np.asarray(n['matrix']).reshape(4,4).T
            else:
                x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4)
                m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]))
                m[:3,3]=n.get('translation',[0,0,0])
            cache[i]=matrix(parents[i])@m if i in parents else m
            return cache[i]
        rows=[]
        for i,n in enumerate(self.j.get('nodes',[])):
            if 'mesh' not in n:continue
            m=matrix(i)
            for p in self.j['meshes'][n['mesh']]['primitives']:
                v=self.accessor(p['attributes']['POSITION'])
                rows.append((np.c_[v,np.ones(len(v))]@m.T)[:,:3])
        return rows

def inspect(path,source=None):
    g=GLB(path);j=g.j;prims=[];skins=[];animations=[]
    for i,s in enumerate(j.get('skins',[])):
        names=[j['nodes'][n].get('name',str(n)) for n in s['joints']]
        ib=g.accessor(s['inverseBindMatrices']) if 'inverseBindMatrices'in s else None
        skins.append({'index':i,'joints':len(names),'joint_names':names,'inverse_bind_count':len(ib) if ib is not None else None,'inverse_bind_finite':bool(np.isfinite(ib).all()) if ib is not None else None})
    for ni,node in enumerate(j.get('nodes',[])):
        if 'mesh' not in node:continue
        for p in j['meshes'][node['mesh']]['primitives']:
            att=p['attributes'];pos=g.accessor(att['POSITION'])
            sets=sorted(k for k in att if k.startswith('WEIGHTS_'))
            r={'node':node.get('name',ni),'vertices':len(pos),'positions_finite':bool(np.isfinite(pos).all()),'bounds_local':[pos.min(0).tolist(),pos.max(0).tolist()],'weight_sets':len(sets)}
            if sets:
                weights=np.concatenate([g.accessor(att[k]) for k in sets],axis=1)
                joints=np.concatenate([g.accessor(att[k.replace('WEIGHTS_','JOINTS_')]) for k in sets],axis=1)
                sums=weights.sum(1);count=len(j['skins'][node['skin']]['joints'])
                r.update({'weights_finite':bool(np.isfinite(weights).all()),'weights_nonnegative':bool((weights>=-1e-7).all()),'unweighted_vertices':int((sums<1e-6).sum()),'max_weight_sum_error':float(np.abs(sums-1).max()),'max_influences':int((weights>1e-6).sum(1).max()),'invalid_joint_influences':int(((joints>=count)&(weights>1e-6)).sum())})
            prims.append(r)
    for a in j.get('animations',[]):
        times=[g.accessor(s['input']).reshape(-1) for s in a.get('samplers',[])]
        animations.append({'name':a.get('name'),'channels':len(a.get('channels',[])),'duration':max((float(t[-1]) for t in times if len(t)),default=0),'max_key_count':max((len(t) for t in times),default=0),'times_monotonic':all(bool((np.diff(t)>=0).all()) for t in times),'values_finite':all(bool(np.isfinite(g.accessor(s['output'])).all()) for s in a.get('samplers',[]))})
    r={'path':str(g.path),'bytes':g.path.stat().st_size,'sha256':hashlib.sha256(g.path.read_bytes()).hexdigest(),'skins':skins,'primitives':prims,'animations':animations,'mesh_count':len(j.get('meshes',[])),'materials':len(j.get('materials',[])),'images':len(j.get('images',[]))}
    r['structural_pass']=bool(skins) and all(p.get('weights_finite',True) and p.get('weights_nonnegative',True) and p.get('max_weight_sum_error',0)<.001 and p.get('unweighted_vertices',0)==0 and p.get('invalid_joint_influences',0)==0 and p['positions_finite'] for p in prims)
    if source:
        a=GLB(source).signatures();b=g.signatures()
        def normalize_material(m):
            import copy
            m=copy.deepcopy(m)
            m.setdefault('alphaMode','OPAQUE');m.setdefault('emissiveFactor',[0,0,0]);m.setdefault('doubleSided',False)
            p=m.setdefault('pbrMetallicRoughness',{})
            p.setdefault('baseColorFactor',[1,1,1,1]);p.setdefault('metallicFactor',1);p.setdefault('roughnessFactor',1)
            for d in (m,p):
                for k,v in d.items():
                    if k.endswith('Texture') and isinstance(v,dict):
                        v.setdefault('texCoord',0)
                        if k=='normalTexture':v.setdefault('scale',1)
                        if k=='occlusionTexture':v.setdefault('strength',1)
            return m
        r['preservation']={'source':str(source),'geometry_attributes_indices_equal':a['primitives']==b['primitives'],'materials_exact_json_equal':a['materials']==b['materials'],'materials_semantically_equal':list(map(normalize_material,a['materials']))==list(map(normalize_material,b['materials'])),'embedded_images_equal':a['images_sha256']==b['images_sha256']}
        source_g=GLB(source).world_geometry();target_g=g.world_geometry()
        compatible=len(source_g)==len(target_g) and all(x.shape==y.shape for x,y in zip(source_g,target_g))
        error=max((float(np.abs(x-y).max()) for x,y in zip(source_g,target_g)),default=0) if compatible else None
        r['preservation'].update(world_positions_max_abs_error_m=error,world_positions_preserved=compatible and error<1e-5)
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('model');p.add_argument('--source');p.add_argument('--output');a=p.parse_args()
    r=inspect(a.model,a.source)
    if a.output:Path(a.output).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in r.items() if k not in ('primitives','skins')},ensure_ascii=False))
