/* A deterministic, real WebGL/PBR miniature workshop, driven by film time. */
(() => {
  'use strict';
  const T = THREE;
  const palette = { ink:0x080f13, ivory:0xf4eee2, gold:0xe4b86d, green:0x739888, muted:0xb2bec1,
    ground:0x263f35, grass:0x53765a, slate:0x22323a, stone:0x8c9e91, copper:0x996f43 };
  const canvas = document.querySelector('#world');
  const renderer = new T.WebGLRenderer({ canvas, antialias:true, alpha:true, powerPreference:'high-performance', preserveDrawingBuffer:true });
  renderer.setSize(1920,1080,false); renderer.setPixelRatio(1);
  renderer.outputColorSpace = T.SRGBColorSpace;
  renderer.toneMapping = T.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFShadowMap;
  const scene = new T.Scene();
  scene.background = new T.Color(palette.ink);
  scene.fog = new T.FogExp2(palette.ink, .018);
  const camera = new T.PerspectiveCamera(34,1920/1080,.1,250);
  const pmrem = new T.PMREMGenerator(renderer);
  const room = new T.RoomEnvironment();
  scene.environment = pmrem.fromScene(room,.04).texture;
  room.dispose();
  const hemi = new T.HemisphereLight(0xd4e2db,0x1b2420,1.7); scene.add(hemi);
  const key = new T.DirectionalLight(0xffe1ae,4.4);key.position.set(5,11,6);key.castShadow=true;
  key.shadow.mapSize.set(2048,2048);key.shadow.camera.left=-12;key.shadow.camera.right=12;
  key.shadow.camera.top=12;key.shadow.camera.bottom=-12;key.shadow.camera.near=.5;key.shadow.camera.far=50;
  key.shadow.bias=-.0003;key.shadow.normalBias=.03;scene.add(key,key.target);
  const rim = new T.DirectionalLight(0x9bcbbd,2.3);rim.position.set(-6,6,-8);scene.add(rim,rim.target);
  const fill = new T.PointLight(0xe4b86d,35,22,2);scene.add(fill);
  const ground = new T.Mesh(new T.PlaneGeometry(240,160),new T.MeshStandardMaterial({color:palette.ink,roughness:1,metalness:0,envMapIntensity:.12}));
  ground.rotation.x=-Math.PI/2;ground.position.set(56,-1.12,0);ground.receiveShadow=true;scene.add(ground);
  const materials = {};
  const mat=(name,color,metalness=.05,roughness=.5,extra={}) => materials[name] ||= new T.MeshStandardMaterial({color,metalness,roughness,...extra});
  const gold=mat('gold',palette.gold,.76,.23),dark=mat('dark',palette.slate,.52,.36),ivory=mat('ivory',palette.ivory,.12,.43),green=mat('green',palette.green,.12,.47);
  const moss=mat('moss',palette.grass,.02,.92),rock=mat('rock',palette.stone,.12,.86),wood=mat('wood',0x6e5238,.03,.82);
  const emit=mat('emit',palette.gold,.4,.3,{emissive:palette.gold,emissiveIntensity:1.8});
  const glass=new T.MeshPhysicalMaterial({color:0xa6ccbf,metalness:.15,roughness:.08,transparent:true,opacity:.28,side:T.DoubleSide});
  const objects=[];
  function mesh(parent,geometry,material,x=0,y=0,z=0) {
    const m=new T.Mesh(geometry,material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;
  }
  function box(p,w,h,d,m,x=0,y=0,z=0,r=.07) {
    const radius=Math.min(r,w*.25,h*.25,d*.25);
    return mesh(p,new T.RoundedBoxGeometry(w,h,d,2,radius),m,x,y,z);
  }
  const cylinder=(p,r,h,m,x=0,y=0,z=0,segments=48)=>mesh(p,new T.CylinderGeometry(r,r,h,segments),m,x,y,z);
  const sphere=(p,r,m,x=0,y=0,z=0)=>mesh(p,new T.SphereGeometry(r,24,16),m,x,y,z);
  function rod(p,a,b,r,m) {
    const from=new T.Vector3(...a),to=new T.Vector3(...b),v=to.clone().sub(from);
    const item=mesh(p,new T.CylinderGeometry(r,r,v.length(),10),m);
    item.position.copy(from).add(to).multiplyScalar(.5);item.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),v.normalize());return item;
  }
  function ring(p,r,tube,m,x=0,y=0,z=0,rx=Math.PI/2) {
    const item=mesh(p,new T.TorusGeometry(r,tube,10,90),m,x,y,z);item.rotation.x=rx;return item;
  }
  function path(p,points,color=palette.gold,width=.045) {
    const curve=new T.CatmullRomCurve3(points.map(a=>new T.Vector3(...a)));
    return mesh(p,new T.TubeGeometry(curve,60,width,8,false),new T.MeshStandardMaterial({color,emissive:color,emissiveIntensity:.6,metalness:.5,roughness:.3}));
  }
  function stage(index) {
    const root=new T.Group();root.position.x=index*18;scene.add(root);
    const set=new T.Group();set.position.set(2.65,0,0);root.add(set);
    const base=cylinder(set,4.9,.22,dark,0,-.9,0,96);
    ring(set,4.74,.025,gold,0,-.77,0);
    return {root,set,base,index,animated:[]};
  }
  function core(set,small=false) {
    const root=new T.Group();set.add(root);
    const size=small?.9:1.8;
    const stone=mesh(root,new T.IcosahedronGeometry(size,0),gold,0,small?1.1:2,0);
    stone.rotation.z=Math.PI/7;
    const shell=mesh(root,new T.IcosahedronGeometry(size*1.25,0),new T.MeshBasicMaterial({color:palette.gold,wireframe:true,transparent:true,opacity:.24}),0,stone.position.y,0);
    const a=ring(root,size*1.8,.028,emit,0,stone.position.y,0,.9);
    const b=ring(root,size*2,.015,gold,0,stone.position.y,0,.2);b.rotation.y=.65;
    const c=ring(root,size*1.62,.04,dark,0,stone.position.y,0,1.2);c.rotation.z=.7;
    cylinder(root,size*.7,.18,ivory,0,-.6,0);
    return {root,stone,shell,rings:[a,b,c]};
  }
  function tree(p,x,z,s=1) {
    const g=new T.Group();g.position.set(x,-.25,z);g.scale.setScalar(s);p.add(g);
    cylinder(g,.1,1.3,wood,0,.55,0,10);
    const leaves=mat('leaves',0x456a4f,.01,.86);
    for(let k=0;k<3;k++){const v=mesh(g,new T.ConeGeometry(.7-k*.13,1.35,8),leaves,0,1.35+k*.5,0);v.rotation.y=k*.5;}
    return g;
  }
  function house(p,x,z,s=1) {
    const g=new T.Group();g.position.set(x,0,z);g.scale.setScalar(s);p.add(g);
    box(g,1.2,1.4,1.25,ivory,0,.48,0);
    const roof=mesh(g,new T.ConeGeometry(1.05,.75,4),dark,0,1.55,0);roof.rotation.y=Math.PI/4;
    box(g,.34,.7,.08,wood,0,.15,.66,.01);
    const windowMat=mat('window',0xf0c77e,.3,.17,{emissive:0xe4b86d,emissiveIntensity:.45});
    box(g,.3,.34,.04,windowMat,-.36,.72,.66,.01);box(g,.3,.34,.04,windowMat,.36,.72,.66,.01);
    box(g,.3,.34,.04,windowMat,0,.75,-.66,.01);
    return g;
  }
  function robot(p,scale=1) {
    const rig=new T.Group();rig.scale.setScalar(scale);p.add(rig);
    const trunk=box(rig,1.1,1.25,.65,ivory,0,2.05,0,.19);
    box(rig,.86,.7,.12,gold,0,2.14,.38,.12);box(rig,.35,.08,.1,emit,0,2.26,.47,.02);
    box(rig,.78,.65,.62,ivory,0,3.06,0,.17);
    box(rig,.58,.21,.08,dark,0,3.1,.33,.045);
    box(rig,.08,.06,.04,emit,-.16,3.1,.39,.01);box(rig,.08,.06,.04,emit,.16,3.1,.39,.01);
    cylinder(rig,.13,.2,dark,0,2.66,0,20);
    const limbs=[];
    for(const side of [-1,1]) {
      sphere(rig,.23,dark,side*.76,2.47,0);
      const arm=new T.Group();arm.position.set(side*.76,2.47,0);rig.add(arm);
      box(arm,.32,.75,.4,green,side*.09,-.42,0,.11);sphere(arm,.17,gold,side*.12,-.85,0);
      box(arm,.3,.65,.37,ivory,side*.15,-1.22,.035,.1);sphere(arm,.16,dark,side*.17,-1.63,.05);limbs.push(arm);
      sphere(rig,.2,dark,side*.31,1.3,0);
      box(rig,.43,.71,.48,green,side*.31,.85,0,.12);
      sphere(rig,.2,gold,side*.31,.44,.045);
      box(rig,.4,.7,.45,ivory,side*.31,-.01,.045,.13);
      box(rig,.47,.25,.78,dark,side*.31,-.48,.18,.08);
    }
    const skeleton=new T.Group();rig.add(skeleton);
    const joint=mat('joint',palette.gold,.25,.24,{emissive:palette.gold,emissiveIntensity:.9});
    const joints=[[0,-.34,.55],[0,.45,.55],[0,1.3,.55],[0,2.1,.55],[0,2.63,.55],[0,3.15,.55],[-.76,2.47,.55],[.76,2.47,.55],[-.88,1.62,.55],[.88,1.62,.55],[-.92,.84,.55],[.92,.84,.55],[-.31,1.3,.55],[.31,1.3,.55],[-.31,.44,.55],[.31,.44,.55],[-.31,-.48,.55],[.31,-.48,.55]];
    for(const a of joints)sphere(skeleton,.065,joint,...a);
    for(const [a,b] of [[0,1],[1,2],[2,3],[3,4],[4,5],[3,6],[3,7],[6,8],[7,9],[8,10],[9,11],[2,12],[2,13],[12,14],[13,15],[14,16],[15,17]])rod(skeleton,joints[a],joints[b],.024,joint);
    return {rig,limbs,skeleton,trunk};
  }
  function cameraProp(p,x=0,z=0,scale=1) {
    const g=new T.Group();p.add(g);g.position.set(x,.25,z);g.scale.setScalar(scale);
    box(g,1.35,.85,.75,dark,0,1.4,0,.1);box(g,.38,.35,.16,gold,-.37,1.52,.43,.025);
    const lens=mesh(g,new T.CylinderGeometry(.31,.35,.9,32),dark,.28,1.42,.72);lens.rotation.x=Math.PI/2;
    const lensGlass=mesh(g,new T.CircleGeometry(.265,32),new T.MeshStandardMaterial({color:0x3f6967,metalness:.95,roughness:.04}),.28,1.42,1.18);
    ring(g,.28,.027,gold,.28,1.42,1.19,0);
    cylinder(g,.12,1.1,gold,0,.42,0,12);
    for(let i=0;i<3;i++){const angle=i*Math.PI*2/3;rod(g,[0,.55,0],[Math.cos(angle)*.65,-.5,Math.sin(angle)*.65],.045,dark);}
    cylinder(g,.33,.12,dark,-.3,2.02,0,32).rotation.x=Math.PI/2;
    cylinder(g,.33,.12,dark,.4,2.02,0,32).rotation.x=Math.PI/2;
    return g;
  }
  function frame(p,x,y,z,w,h) {
    const g=new T.Group();g.position.set(x,y,z);p.add(g);
    box(g,w+.18,h+.18,.12,gold,0,0,0,.035);
    box(g,w,h,.14,dark,0,0,.055,.025);
    box(g,w*.85,h*.75,.035,mat('screen',0x3b5d50,.1,.75),0,0,.15,.01);
    const sun=sphere(g,.14,emit,w*.25,h*.21,.22);sun.scale.z=.1;
    for(let j=0;j<3;j++){const peak=mesh(g,new T.ConeGeometry(.35+j*.06,.7+j*.18,3),green,-w*.22+j*.27,-h*.14,.2);peak.scale.z=.1;}
    return g;
  }
  // 00 — physical story nucleus.
  const hero=stage(0);hero.core=core(hero.set);objects.push(hero);
  for(let i=0;i<7;i++){const a=i*Math.PI*2/7;const block=box(hero.set,.38,.38,.38,i%2?ivory:green,Math.cos(a)*3.9,.45,Math.sin(a)*3.9,.09);hero.animated.push(block);}
  // 01 — a playable-looking miniature world, not claimed as a captured game.
  const game=stage(1);objects.push(game);
  cylinder(game.set,4.3,.75,mat('island',palette.ground,.03,.94),0,-.36,0,7);
  cylinder(game.set,4.34,.16,moss,0,.07,0,7);
  const water=mesh(game.set,new T.CircleGeometry(1.45,48),new T.MeshPhysicalMaterial({color:0x315f66,roughness:.23,metalness:.45,transparent:true,opacity:.85}),1.9,.18,1.65);water.rotation.x=-Math.PI/2;
  path(game.set,[[-3.7,.19,-.5],[-1,.19,-.25],[1,.19,.65],[3.3,.19,1.05]],0xc5b18a,.27);
  for(const [x,z,s] of [[-2.3,-1.9,.9],[-.6,-2.1,1.15],[1.5,-1.9,.75]])house(game.set,x,z,s);
  for(const [x,z,s] of [[-3,1.2,.8],[-2,2.4,.66],[-.3,2.8,.65],[2.8,-.9,.65],[3.1,-2.2,.6],[-2.5,-2.8,.55]])tree(game.set,x,z,s);
  const player=robot(game.set,.37);player.rig.position.set(.15,.43,1.07);player.skeleton.visible=false;game.player=player;
  ring(game.set,.46,.035,emit,.15,.21,1.07);
  const gate=new T.Group();gate.position.set(2.4,.2,-.2);game.set.add(gate);
  box(gate,.18,2.2,.25,ivory,-.7,1,0);box(gate,.18,2.2,.25,ivory,.7,1,0);box(gate,1.65,.22,.3,gold,0,2.1,0);
  // 02 — miniature virtual production studio with a real lens and light rig.
  const film=stage(2);objects.push(film);
  box(film.set,6.8,.2,4.9,ivory,0,-.45,0,.14);
  box(film.set,6.6,3.3,.16,mat('backdrop',0x45685b,.03,.9),0,1.16,-2.15,.07);
  const actor=robot(film.set,.68);actor.rig.position.set(.1,.07,-.4);actor.skeleton.visible=false;film.actor=actor;
  const cinema=cameraProp(film.set,-2.25,2,1.1);cinema.rotation.y=-.45;film.cinema=cinema;
  for(const side of [-1,1]) {
    rod(film.set,[side*2.7,-.3,-1.4],[side*2.7,4.3,-1.4],.06,dark);
    const softbox=box(film.set,1.05,.65,.18,ivory,side*2.7,4,-1.35,.05);softbox.rotation.x=.45;softbox.rotation.z=side*.2;
    box(film.set,.88,.47,.06,emit,side*2.7,3.95,-1.2,.02);
  }
  film.frames=[frame(film.set,-2.3,1.7,-.7,1.3,.8),frame(film.set,2.35,1.6,.8,1.45,.86)];
  // 03 — image, geometry, rig: one asset is shown at different production stages.
  const assets=stage(3);objects.push(assets);
  cylinder(assets.set,2,.24,ivory,0,-.55,0,64);ring(assets.set,1.9,.035,emit,0,-.41,0);
  const asset=robot(assets.set,1.15);asset.rig.position.y=.23;assets.robot=asset;
  const wire=new T.Group();asset.rig.add(wire);
  asset.rig.traverse(child=>{
    if(child.isMesh&&child.material===ivory){const lines=new T.LineSegments(new T.WireframeGeometry(child.geometry),new T.LineBasicMaterial({color:palette.gold,transparent:true,opacity:.22}));lines.position.copy(child.position);lines.rotation.copy(child.rotation);wire.add(lines);}
  });assets.wire=wire;
  const reference=frame(assets.set,-2.8,2.15,.3,1.55,2.55);reference.rotation.y=.45;
  const mini=robot(reference,.43);mini.rig.position.set(0,-.45,.3);mini.skeleton.visible=false;
  path(assets.set,[[-2.6,.35,.3],[-1.8,.45,.2],[-1,.3,.15]],palette.gold,.035);
  // 04 — motion-picture rails and sound as tangible moving objects.
  const sound=stage(4);objects.push(sound);sound.frames=[];sound.bars=[];
  for(let i=0;i<3;i++){const f=frame(sound.set,-1.9+i*1.8,2.15,-.3+i*.5,1.6,2);f.rotation.y=-.3+i*.15;sound.frames.push(f);}
  cameraProp(sound.set,-2.2,2,1);
  for(let i=0;i<25;i++){const bar=box(sound.set,.1,1,.14,i%4?green:gold,-1.9+i*.18,.1,2.8,.035);sound.bars.push(bar);}
  path(sound.set,[[-3.9,-.25,2.5],[-1.4,-.25,3.6],[2.4,-.25,2.7],[3.7,-.25,.1]],palette.gold,.03);
  // 05 — reusable workflow nodes with a continuous physical routing path.
  const usage=stage(5);objects.push(usage);usage.nodes=[];
  for(let i=0;i<5;i++) {
    const x=-2.8+i*1.4,z=Math.sin(i*.9)*1.2;
    const g=new T.Group();g.position.set(x,.1+i*.12,z);usage.set.add(g);
    box(g,1,.34,1,dark,0,0,0,.1);box(g,.72,.12,.72,i===2?gold:green,0,.23,0,.06);
    sphere(g,.11,emit,0,.41,0);usage.nodes.push(g);
  }
  path(usage.set,usage.nodes.map(g=>[g.position.x,g.position.y-.1,g.position.z]),palette.gold,.055);
  const stack=new T.Group();usage.set.add(stack);stack.position.set(.2,1.4,-1.5);
  for(let i=0;i<3;i++){const board=box(stack,2.6,.08,1.65,i===2?gold:dark,0,i*.4,0,.05);board.rotation.y=-.25;}
  usage.stack=stack;
  // 06 — a workstation whose memory and graphics capacity are stated, not inflated.
  const scope=stage(6);objects.push(scope);
  const card=box(scope.set,5.4,.46,2.4,dark,0,1.2,0,.12);
  for(let i=0;i<3;i++) {
    cylinder(scope.set,.64,.17,mat('fan',0x0c171c,.6,.26),-1.75+i*1.75,1.52,0,48);
    const fan=new T.Group();fan.position.set(-1.75+i*1.75,1.64,0);scope.set.add(fan);
    for(let j=0;j<9;j++){const blade=box(fan,.15,.045,.78,green,0,0,.24,.02);blade.rotation.y=j*Math.PI*2/9;}
    cylinder(fan,.16,.08,gold,0,.02,0,24);scope.animated.push(fan);
  }
  for(let i=0;i<2;i++){const stick=box(scope.set,4.7,.55,.18,green,0,.32,-1.15-i*.4,.03);for(let j=0;j<8;j++)box(scope.set,.36,.34,.08,dark,-1.75+j*.5,.33,-1.01-i*.4,.02);}
  box(scope.set,3.1,.18,1.3,gold,0,-.35,1.4,.08);
  for(let i=0;i<11;i++)box(scope.set,.17,.12,.4,ivory,-1.25+i*.25,-.22,1.4,.01);
  // 07 — return to a smaller nucleus, with the world and studio united around it.
  const outro=stage(7);objects.push(outro);outro.core=core(outro.set);
  house(outro.set,-2.7,1.5,.72);tree(outro.set,-3.1,-.9,.6);
  const endingCamera=cameraProp(outro.set,2.8,1,.86);endingCamera.rotation.y=-.5;
  const edge=frame(outro.set,2.6,2,-1,1.15,1.65);edge.rotation.y=-.3;
  // Small suspended points establish depth without a neon particle wall.
  let seed=28471;const rand=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296;};
  const points=new Float32Array(160*3);
  for(let i=0;i<160;i++){points[i*3]=rand()*150-10;points[i*3+1]=rand()*11;points[i*3+2]=rand()*22-11;}
  const particles=new T.BufferGeometry();particles.setAttribute('position',new T.BufferAttribute(points,3));
  scene.add(new T.Points(particles,new T.PointsMaterial({color:palette.gold,size:.027,transparent:true,opacity:.28})));
  const starts=[0,1.875,6.5625,10.3125,14.0625,17.8125,22.5,26.25];
  const ends=[1.875,6.5625,10.3125,14.0625,17.8125,22.5,26.25,30];
  const smooth=x=>x*x*(3-2*x);
  const clamp=x=>Math.max(0,Math.min(1,x));
  // Cache pristine transforms once: seeking backwards rebuilds the same assembly.
  const parts=objects.map(o=>o.set.children.map((node,i)=>({node,i,p:node.position.clone(),s:node.scale.clone(),r:node.rotation.clone()})));
  // Shot changes on the 128-BPM grid: wider reads alternate with real 3D closeups.
  const shots=[
    [0,0,.62,4.8,9.2,1.8,''],[.9375,0,1.08,6.9,12.0,1.2,''],
    [1.875,1,.64,7.0,11.8,.9,'BUILD / PLAY'],[3.28125,1,1.03,10.9,9.2,.2,'WORLD / TOP VIEW'],[4.6875,1,.18,4.7,8.9,1.2,'CHARACTER / INTERACTION'],[5.625,1,.81,7.1,12.4,.8,'WEB / UNREAL'],
    [6.5625,2,.72,6.8,11.9,1.4,'SCRIPT → SCREEN'],[7.96875,2,1.18,4.2,9.6,1.8,'CAMERA / PREVIS'],[9.375,2,.35,8.6,12.8,1.0,'FRAME / EDIT'],
    [10.3125,3,.76,6.3,11.1,1.6,'IMAGE → MESH'],[11.71875,3,.12,4.5,9.0,1.9,'MESH / MATERIAL'],[12.65625,3,.53,5.2,10.4,1.8,'RIG / REFINE'],
    [14.0625,4,.80,7.1,11.4,1.1,'PICTURE × SOUND'],[15.46875,4,.20,4.3,9.5,1.5,'VOICE / MUSIC'],[16.875,4,1.04,8.8,12.8,.9,'CUT / MIX'],
    [17.8125,5,.61,7.2,11.3,1.0,'CONFIGURE'],[19.21875,5,1.02,5.1,9.9,1.3,'BRIEF / REFERENCE'],[20.625,5,.18,10.6,10.9,.6,'CREATE / REVIEW / DELIVER'],
    [22.5,6,.71,6.0,10.7,1.2,'81 WORKFLOWS'],[23.90625,6,.26,8.1,8.9,1.1,'RTX 4080 / 16GB'],[25.3125,6,1.04,6.8,12.4,1.0,'32GB RAM / TESTED'],
    [26.25,7,.68,5.7,10.2,1.6,''],[28.125,7,.94,7.4,13.6,1.3,'']
  ];
  const pose=(s,u)=>{
    const index=s[1],center=index*18,centered=index===0||index===7;
    const angle=s[2]+u*.045,dist=s[4]-.25*u;
    return {x:center+2.65+Math.sin(angle)*dist,y:s[3]+.1*Math.sin(u*2),z:Math.cos(angle)*dist,tx:center+(centered?2.65:.15),ty:s[5]};
  };
  function draw(t) {
    t=Math.max(0,Math.min(30,t));
    let index=0;for(let i=1;i<starts.length;i++)if(t>=starts[i])index=i;
    const local=t-starts[index];let si=0;for(let i=1;i<shots.length;i++)if(t>=shots[i][0])si=i;
    const current=shots[si],u=t-current[0],a=pose(current,u);
    if(si&&u<.2){const b=pose(shots[si-1],current[0]-shots[si-1][0]);const k=smooth(clamp(u/.2));for(const key of ['x','y','z','tx','ty'])a[key]=b[key]+(a[key]-b[key])*k;}
    const x=a.tx;
    for(let i=0;i<objects.length;i++){
      objects[i].root.visible=i===index||(local<.3&&i===index-1);
      const li=t-starts[i];
      parts[i].forEach(({node,p,s,r,i:j})=>{
        node.position.copy(p);node.scale.copy(s);node.rotation.copy(r);
        if(j<2)return;
        const p0=clamp((li-.018*(j%9))/.52),k=1-(1-p0)**3;
        node.position.y+=(1-k)*(1.7+(j%3)*.4);node.position.x+=(1-k)*((j%2?1:-1)*(1.3+(j%4)*.3));node.position.z+=(1-k)*(j%2?1.2:-1.2);
        node.scale.multiplyScalar(.16+.84*k);node.rotation.y+=(1-k)*(j%2?.65:-.65);
      });
    }
    camera.position.set(a.x,a.y,a.z);camera.lookAt(a.tx,a.ty,0);
    key.position.set(x+5,11,6);key.target.position.set(x+2,0,0);
    rim.position.set(x-6,6,-8);rim.target.position.set(x+2,1,0);
    fill.position.set(x+4,4,2);
    for(const a of [hero,outro]) {
      a.core.stone.rotation.y=t*.72;a.core.shell.rotation.y=-t*.38;
      a.core.root.position.y=.09*Math.sin(t*2.1);
      a.core.rings[0].rotation.z=t*.26;a.core.rings[1].rotation.y=.65+t*.31;
    }
    for(let i=0;i<hero.animated.length;i++){hero.animated[i].position.y=.35+.35*Math.sin(t*2.4+i);hero.animated[i].rotation.y=t*.8;}
    game.player.rig.position.x=.15+.8*Math.sin((t-1.875)*1.2);game.player.rig.rotation.y=.24*Math.sin(t*2);
    game.player.limbs[0].rotation.x=.35*Math.sin(t*7);game.player.limbs[1].rotation.x=-.35*Math.sin(t*7);
    film.cinema.position.x=-2.25+.5*Math.sin(t*.9);film.actor.limbs[1].rotation.z=-.2-.26*Math.sin(t*2.8);
    assets.robot.rig.rotation.y=.12+Math.sin((t-10.3125)*.75)*1.1;
    assets.robot.skeleton.visible=index===3&&local>2.05;assets.wire.visible=index===3&&local<2.45;
    for(let i=0;i<sound.frames.length;i++){sound.frames[i].position.y=2.15+.13*Math.sin(t*2+i);sound.frames[i].rotation.y=-.3+i*.15+.2*Math.sin(t*1.8+i);}
    for(let i=0;i<sound.bars.length;i++){const h=.3+1.1*(.5+.5*Math.sin(t*13.4+i*.8));sound.bars[i].scale.y=h;sound.bars[i].position.y=-.25+h*.5;}
    for(let i=0;i<usage.nodes.length;i++)usage.nodes[i].position.y=.1+i*.12+.13*Math.sin(t*3-i);
    usage.stack.rotation.y=.2*Math.sin(t*1.2);
    for(const fan of scope.animated)fan.rotation.y=t*7;
    renderer.render(scene,camera);
    window.__film3DFrame={time:t,chapter:index,shot:si,label:current[6],renderer:renderer.info.render.calls};
  }
  window.LightStoryWorld={draw,renderer,camera};
  draw(0);
})();
