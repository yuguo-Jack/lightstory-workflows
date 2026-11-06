"""Read-only local media checks with ffprobe/ffmpeg; never certifies artistic quality."""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys


def run(argv: list[str], timeout: float) -> subprocess.CompletedProcess:
    return subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, encoding='utf-8', errors='replace', timeout=timeout)


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def rational(value):
    try:
        result = Fraction(str(value))
        return result if result > 0 else None
    except (ValueError, ZeroDivisionError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('media', type=Path)
    parser.add_argument('--expected-size', help='WIDTHxHEIGHT')
    parser.add_argument('--expected-fps', help='24, 25, 30000/1001, etc.')
    parser.add_argument('--expected-duration', type=float, help='Seconds, compared to video duration')
    parser.add_argument('--duration-tolerance', type=float, default=None, help='Default: one video frame or 0.05s')
    parser.add_argument('--expected-frames', type=int)
    parser.add_argument('--require-audio', action='store_true')
    parser.add_argument('--count-frames', action='store_true', help='Decode to count frames using ffprobe')
    parser.add_argument('--decode', action='store_true', help='Decode first video and all audio streams with ffmpeg')
    parser.add_argument('--audio-stats', action='store_true', help='Measure first audio loudness; does not normalize media')
    parser.add_argument('--timeout', type=float, default=300, help='Per subprocess seconds; extend for long films')
    parser.add_argument('--out', type=Path, help='New absolute JSON report path; refuses overwrite')
    args = parser.parse_args()

    try:
        path = args.media.resolve(strict=True)
        if not path.is_file():
            raise ValueError('Input must be an existing local file')
        if args.out:
            if not args.out.is_absolute():
                raise ValueError('--out must be absolute')
            if args.out.exists():
                raise FileExistsError(f'Report already exists: {args.out}')
        if args.timeout <= 0 or (args.duration_tolerance is not None and args.duration_tolerance < 0):
            raise ValueError('Timeout must be positive and tolerance nonnegative')
        if args.expected_duration is not None and args.expected_duration < 0:
            raise ValueError('Expected duration must be nonnegative')
        if args.expected_frames is not None and args.expected_frames < 1:
            raise ValueError('Expected frames must be positive')
        size = None
        if args.expected_size:
            match = re.fullmatch(r'([1-9]\d*)[xX]([1-9]\d*)', args.expected_size)
            if not match:
                raise ValueError('--expected-size must be positive WIDTHxHEIGHT')
            size = tuple(map(int, match.groups()))
        wanted_fps = rational(args.expected_fps) if args.expected_fps else None
        if args.expected_fps and not wanted_fps:
            raise ValueError('Invalid expected FPS')
        probe = shutil.which('ffprobe')
        ffmpeg = shutil.which('ffmpeg')
        if not probe:
            raise RuntimeError('ffprobe is not on PATH')
        if (args.decode or args.audio_stats) and not ffmpeg:
            raise RuntimeError('Requested check needs ffmpeg on PATH')
        command = [probe, '-v', 'error']
        if args.count_frames:
            command += ['-count_frames']
        command += ['-show_streams', '-show_format', '-of', 'json', str(path)]
        result = run(command, args.timeout)
        if result.returncode:
            raise RuntimeError('ffprobe failed: ' + result.stderr[-3000:])
        info = json.loads(result.stdout)
        videos = [s for s in info.get('streams', []) if s.get('codec_type') == 'video'
                  and not s.get('disposition', {}).get('attached_pic')]
        audios = [s for s in info.get('streams', []) if s.get('codec_type') == 'audio']
        video = videos[0] if videos else {}
        fps = rational(video.get('avg_frame_rate'))
        duration = number(video.get('duration'))
        if duration is None:
            ticks = number(video.get('duration_ts'))
            time_base = rational(video.get('time_base'))
            if ticks is not None and time_base:
                duration = ticks * float(time_base)
        frames = video.get('nb_read_frames') if args.count_frames else video.get('nb_frames')
        frames = int(frames) if str(frames).isdigit() else None
        errors, warnings = [], []
        if not videos:
            errors.append('No video stream')
        if size and (video.get('width'), video.get('height')) != size:
            errors.append(f'Expected {size[0]}x{size[1]}, got {video.get("width")}x{video.get("height")}')
        if wanted_fps and (not fps or abs(float(fps - wanted_fps)) > 0.0001):
            errors.append(f'Expected FPS {wanted_fps}, got {fps}')
        if args.expected_frames is not None and frames != args.expected_frames:
            errors.append(f'Expected {args.expected_frames} frames, got {frames}; use --count-frames if metadata is absent')
        if args.expected_duration is not None:
            tolerance = args.duration_tolerance if args.duration_tolerance is not None else max(0.05, 1 / float(fps) if fps else 0.05)
            if duration is None or abs(duration - args.expected_duration) > tolerance:
                errors.append(f'Expected duration {args.expected_duration}s ±{tolerance}s, got {duration}')
        if args.require_audio and not audios:
            errors.append('Audio required but absent')
        if audios:
            warnings.append('Audio-stream presence alone does not establish audible sound or sync')
        if not fps:
            warnings.append('Average video FPS unavailable')
        warnings.append('Average FPS and metadata do not certify CFR, visual continuity, lip sync, color accuracy or artistic quality')

        report = {'scope': 'technical checks only; no visual or listening acceptance',
                  'media': str(path), 'bytes': path.stat().st_size,
                  'video': {k: video.get(k) for k in ['index', 'codec_name', 'width', 'height', 'pix_fmt',
                      'avg_frame_rate', 'r_frame_rate', 'time_base', 'start_time', 'color_space',
                      'color_transfer', 'color_primaries', 'color_range']},
                  'duration_seconds': duration, 'format_duration_seconds': number(info.get('format', {}).get('duration')),
                  'frame_count': frames, 'count_frames_requested': args.count_frames,
                  'audio': [{k: s.get(k) for k in ['index', 'codec_name', 'sample_rate', 'channels',
                      'channel_layout', 'start_time', 'duration']} for s in audios],
                  'decode': {'requested': args.decode}, 'audio_measurements': None}
        if args.decode:
            decoded = run([ffmpeg, '-hide_banner', '-nostdin', '-v', 'error', '-xerror',
                           '-threads', '2', '-i', str(path), '-map', '0:v:0?', '-map', '0:a?',
                           '-f', 'null', '-'], args.timeout)
            report['decode'].update(returncode=decoded.returncode, diagnostics=decoded.stderr[-4000:])
            if decoded.returncode:
                errors.append('Full decode reported an error')
        if args.audio_stats and audios:
            measured = run([ffmpeg, '-hide_banner', '-nostdin', '-i', str(path), '-map', '0:a:0',
                            '-vn', '-af', 'loudnorm=I=-16:TP=-1:LRA=11:print_format=json',
                            '-f', 'null', '-'], args.timeout)
            chunks = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', measured.stderr, flags=re.S)
            if measured.returncode or not chunks:
                errors.append('Audio loudness measurement failed')
            else:
                raw = json.loads(chunks[-1])
                report['audio_measurements'] = {k: raw[k] for k in ['input_i', 'input_tp', 'input_lra', 'input_thresh'] if k in raw}
                if raw.get('input_i') == '-inf':
                    warnings.append('Measured first audio stream is silent; check whether intentional')
                elif number(raw.get('input_i')) is not None and float(raw['input_i']) < -50:
                    warnings.append('First audio stream is extremely quiet (below -50 LUFS); listen and verify intent')
                if number(raw.get('input_tp')) is not None and float(raw['input_tp']) > 0:
                    warnings.append('Measured true peak exceeds 0 dBTP; inspect clipping and delivery headroom')
                report['audio_measurements']['note'] = 'Read-only loudnorm analysis; no output normalization or lip-sync proof'
        elif args.audio_stats:
            warnings.append('No audio stream to measure')
        report.update(errors=errors, warnings=warnings, ok=not errors)
        content = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open('x', encoding='utf-8', newline='\n') as handle:
                handle.write(content)
        print(content, end='')
        return 0 if not errors else 1
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
