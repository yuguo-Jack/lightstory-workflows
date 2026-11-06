"""Original 128 BPM launch-film score and fresh Chinese narration. No stock samples.

System Python dependencies: numpy, edge-tts; FFmpeg/ffprobe on PATH.
Voice text is sent to Microsoft Edge TTS; all scratch files remain under --work.
"""
from __future__ import annotations
import argparse,asyncio,hashlib,json,subprocess,wave
from pathlib import Path
import numpy as np
import edge_tts
HERE=Path(__file__).resolve().parent
SR=48000
def run(*args):
    p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if p.returncode:raise RuntimeError(p.stderr[-1600:])
    return p
def duration(p):return float(run('ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)).stdout)
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ac','1','-ar',str(SR),'pipe:1']),dtype='<f4').copy()
def wavefile(p,data):
    with wave.open(str(p),'wb') as f:f.setnchannels(data.shape[1] if data.ndim>1 else 1);f.setsampwidth(2);f.setframerate(SR);f.writeframes((np.clip(data,-1,1)*32767).astype('<i2').tobytes())
def score(length,starts):
    """16-bar electronic groove; deterministic oscillators, percussion and whooshes."""
    rng=np.random.default_rng(230128);n=round(length*SR);t=np.arange(n,dtype=np.float32)/SR
    out=np.zeros((n,2),np.float32);beat=60/128
    chords=[[38,45,50,53],[34,41,46,50],[41,48,53,57],[36,43,48,52]]
    def add(start,data,pan=0):
        a=round(start*SR);b=min(n,a+len(data))
        if a<0:data=data[-a:];a=0
        if b<=a:return
        out[a:b,0]+=data[:b-a]*(1-pan*.65);out[a:b,1]+=data[:b-a]*(1+pan*.65)
    # Pads are short and gated. Percussion and bass lead the edit.
    for bar in range(16):
        start=bar*4*beat;notes=chords[(bar//2)%4];u=np.arange(round(4.4*beat*SR),dtype=np.float32)/SR
        env=np.minimum(u/.018,1)*np.exp(-u*1.45)
        for k,note in enumerate(notes):
            f=440*2**((note+12-69)/12);tone=np.zeros(len(u),np.float32)
            for h in range(1,6):tone+=np.sin(2*np.pi*f*h*u)/h**1.55
            add(start,tone*env*.018,(k-1.5)/2)
    for k in range(64):
        start=k*beat;u=np.arange(round(.38*SR),dtype=np.float32)/SR
        active=1 if start>=1.875 and start<28.125 else .58
        # Low drum: punch rather than a loud sustained sub.
        kick=np.sin(2*np.pi*(46*u+1.7*(1-np.exp(-u*48))))*np.exp(-u*17)
        kick+=rng.normal(0,.15,len(u))*np.exp(-u*240)
        add(start,np.tanh(kick*1.7)*.12*active)
        if k%4 in (1,3):
            clap=rng.normal(0,1,len(u)).astype(np.float32);clap-=np.convolve(clap,np.ones(18)/18,mode='same')
            env=np.exp(-u*42)*(1+.5*np.cos(2*np.pi*74*u));add(start,clap*env*.026*active)
        bassnote=chords[(k//8)%4][0];f=440*2**((bassnote-69)/12)
        bass=(np.sin(2*np.pi*f*u)+.27*np.sin(4*np.pi*f*u)+.1*np.sin(6*np.pi*f*u))
        add(start+.027,bass*np.minimum(u/.007,1)*np.exp(-u*9)*.079*active)
    # Sixteenth / eighth-note texture and a minor arpeggio, with a breathing break.
    for k in range(128):
        start=k*beat/2;u=np.arange(round(.21*SR),dtype=np.float32)/SR
        if start>28.125:continue
        hats=rng.normal(0,1,len(u)).astype(np.float32);hats=np.r_[0,np.diff(hats)]
        add(start,hats*np.exp(-u*95)*(.006 if k%2 else .009),.32 if k%2 else -.32)
        if start<1.875 or k%2==0:
            notes=chords[(k//16)%4];midi=notes[k%4]+24;f=440*2**((midi-69)/12)
            synth=(np.sin(2*np.pi*f*u)+.28*np.sin(2*np.pi*2*f*u)+.12*np.sin(2*np.pi*3*f*u))
            add(start,synth*np.minimum(u/.003,1)*np.exp(-u*19)*.039,np.sin(k*1.31)*.7)
    accents=sorted(set(starts[1:]+[3.75,5.625,7.96875,9.375,11.71875,12.65625,15.46875,16.875,19.21875,20.625,23.90625,25.3125,28.125]))
    for at in accents:
        start=max(0,at-.15);u=np.arange(round(.35*SR),dtype=np.float32)/SR;center=at-start
        noise=rng.normal(0,1,len(u)).astype(np.float32);noise=np.convolve(noise,np.ones(8)/8,mode='same')
        env=np.exp(-np.abs(u-center)*23)*.043
        add(start,noise*env,-.25);add(start+.014,noise*env,.25)
        if at in starts:
            hit=np.sin(2*np.pi*(49*u+1.2*(1-np.exp(-u*30))))*np.exp(-u*12)*.12
            add(at,hit)
    # Lift into the first real world and an intentional quiet logo tail.
    rise=np.minimum(t/1.875,1);out*=np.where(t<1.875,.55+.45*rise,1)[:,None]
    out*=np.minimum(t/.055,1)[:,None]*np.clip((length-t)/.45,0,1)[:,None]
    out[t>28.125]*=.65
    return out
async def main():
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--voice');args=p.parse_args()
    work=args.work.resolve();work.mkdir(parents=True,exist_ok=True);plan=json.loads((HERE/'shots.json').read_text('utf-8'))
    voice=args.voice or plan['voice'];n=round(plan['duration']*SR);narration=np.zeros(n,np.float32);captions=[];records=[]
    for i,s in enumerate(plan['shots']):
        digest=hashlib.sha256((s['voice']+voice+plan['rate']).encode()).hexdigest()[:10];file=work/f'{i:02}-{s["id"]}-{digest}.mp3'
        if not file.exists():
            for attempt in range(2):
                try:await edge_tts.Communicate(s['voice'],voice,rate=plan['rate'],pitch='-3Hz').save(str(file));break
                except Exception:
                    if file.exists():file.unlink()
                    if attempt:raise
        # Trim only the leading and trailing service padding, retaining internal phrasing.
        clean=work/f'{i:02}-trimmed.wav'
        trim='silenceremove=start_periods=1:start_duration=0.02:start_threshold=-45dB:start_silence=0.025'
        run('ffmpeg','-v','error','-y','-i',str(file),'-af',trim+',areverse,'+trim+',areverse','-ar',str(SR),'-ac','1',str(clean))
        seconds=duration(clean);available=s['end']-s['start']-.29;speed=max(1,seconds/available)
        if speed>1.18:raise RuntimeError(f'{s["id"]}: narration too long ({seconds:.3f}s for {available:.3f}s); shorten script')
        actual=clean
        if speed>1.002:
            actual=work/f'{i:02}-fitted.wav';run('ffmpeg','-v','error','-y','-i',str(clean),'-af',f'atempo={speed:.6f}','-ar',str(SR),'-ac','1',str(actual))
        samples=read(actual);samples*=min(4,.13/np.sqrt(np.mean(samples*samples)+1e-12))
        start=s['start']+.12;a=round(start*SR);b=min(n,a+len(samples));narration[a:b]+=samples[:b-a]
        weights=[len(x) for x in s['captions']];cursor=start
        for line,w in zip(s['captions'],weights):
            end=cursor+len(samples)/SR*w/sum(weights);captions.append({'start':round(cursor,3),'end':round(end,3),'text':line});cursor=end
        record={'shot':s['id'],'raw_seconds':seconds,'speed':speed,'placed_seconds':len(samples)/SR};records.append(record);print(json.dumps(record),flush=True)
    music=score(plan['duration'],[s['start'] for s in plan['shots']]);active=np.convolve((np.abs(narration)>.018).astype(np.float32),np.ones(4800,dtype=np.float32)/4800,mode='same')
    music*=np.clip(1-.55*active,.58,1)[:,None];mix=music+np.stack([narration,narration],axis=1)*1.15
    wavefile(work/'mix.wav',mix);assets=HERE/'assets'
    run('ffmpeg','-v','error','-y','-i',str(work/'mix.wav'),'-af','loudnorm=I=-14:TP=-1.7:LRA=7','-ar',str(SR),'-c:a','aac','-b:a','192k',str(assets/'soundtrack.m4a'))
    (HERE/'captions.js').write_text('window.LIGHTSTORY_CAPTIONS = '+json.dumps(captions,ensure_ascii=False)+';\n','utf-8')
    (work/'audio-report.json').write_text(json.dumps({'voice':voice,'bpm':128,'duration':30,'records':records,'score':'original deterministic electronic synthesis; no third-party samples'},indent=2),'utf-8')
if __name__=='__main__':asyncio.run(main())
