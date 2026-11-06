"""FFprobe metadata and optional complete CPU decode; no content-quality claims."""
import json
from pathlib import Path
import subprocess


def inspect(cfg, filename, *, decode=False):
    source=Path(filename).expanduser().resolve()
    if not source.is_file():raise FileNotFoundError(source)
    probe=cfg.executable('ffprobe','ffprobe')
    if not probe:raise ValueError('Configure ffprobe first')
    command=[probe,'-v','error','-show_format','-show_streams','-of','json',str(source)]
    process=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
    if process.returncode:raise RuntimeError('ffprobe failed: '+process.stderr[-1000:])
    metadata=json.loads(process.stdout)
    result={'source':str(source),'bytes':source.stat().st_size,'streams':metadata.get('streams',[]),'format':metadata.get('format',{}),'full_decode_checked':False,
            'scope':'Technical media metadata/decode only; view/listen and review continuity/content separately.'}
    if decode:
        ffmpeg=cfg.executable('ffmpeg','ffmpeg')
        if not ffmpeg:raise ValueError('Configure ffmpeg first')
        decoded=subprocess.run([ffmpeg,'-hide_banner','-v','error','-xerror','-i',str(source),'-map','0:v?','-map','0:a?','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
        if decoded.returncode:raise RuntimeError('Media decode failed: '+decoded.stderr[-1000:])
        result.update(full_decode_checked=True,decode_passed=True)
    return result
