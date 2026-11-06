"""Bounded-memory NAF inference and file-backed CPU feature storage.

The attention formula follows comfy.image_encoders.naf (GPL-3.0).
Only independent spatial cells are tiled; model weights, dtypes, window sizes,
interpolation and output resolution are unchanged.
"""
import gc
import logging
import math
import os
from pathlib import Path
import shutil
import threading
import uuid
import weakref

import torch
import torch.nn.functional as F

import comfy.model_management as mm
import folder_paths

_pending = set()
_lock = threading.Lock()
_wake = threading.Event()
_janitor = None


def _cleanup_loop():
    while True:
        _wake.wait(2)
        with _lock:
            paths = list(_pending)
        for name in paths:
            try:
                Path(name).unlink(missing_ok=True)
            except OSError:
                # Windows keeps mapped files locked until the last storage view
                # is gone. Retry later; never close a live tensor's mapping.
                continue
            with _lock:
                _pending.discard(name)
        with _lock:
            if not _pending:
                _wake.clear()
        if paths:
            threading.Event().wait(1)


def _retire(path):
    global _janitor
    with _lock:
        _pending.add(str(path))
        if _janitor is None:
            _janitor = threading.Thread(target=_cleanup_loop, name='PixalFeatureCleanup', daemon=True)
            _janitor.start()
    _wake.set()


def mapped_empty(shape, dtype, directory=None):
    """A normal CPU tensor backed by its own writable file, not pagefile commit."""
    directory = Path(directory or (Path(folder_paths.get_temp_directory()) / 'pixal_features'))
    directory.mkdir(parents=True, exist_ok=True)
    count = math.prod(shape)
    size = count * torch.empty((), dtype=dtype).element_size()
    if shutil.disk_usage(directory).free < size + 2 * 1024**3:
        raise RuntimeError(f'Pixal3D needs {size / 1024**3:.2f} GiB of temporary feature storage plus 2 GiB headroom')
    path = directory / f'features-{os.getpid()}-{uuid.uuid4().hex}.bin'
    try:
        base = torch.from_file(str(path), shared=True, size=count, dtype=dtype)
        weakref.finalize(base, _retire, path)
        output = base.view(shape)
        # In inference_mode, PyTorch may omit Python view-base tracking. Keep
        # the owning tensor alive explicitly so cleanup cannot retire the
        # pathname while the returned feature tensor is still in use.
        output._pixal_storage_owner = base
    except Exception:
        _retire(path)
        raise
    logging.info('[PixalLowMemory] file-backed %s %s: %.3f GiB', shape, dtype, size / 1024**3)
    return output


def neighborhood_attention(q, k, v, kernel_size, scale, output=None, chunk_bytes=64 * 1024**2):
    """Native NAF neighborhood attention, bounded in both LR rows and columns."""
    batch, heads, dq, height, width = q.shape
    low_h, low_w = k.shape[-2:]
    dv = v.shape[1] // heads
    kh, kw = kernel_size
    dh, dw = height // low_h, width // low_w
    neighbors, queries = kh * kw, dh * dw
    out = output if output is not None else torch.empty((batch, heads, dv, height, width), device=q.device, dtype=q.dtype)
    k = F.pad(k, (kw // 2, kw // 2, kh // 2, kh // 2))
    v = F.pad(v, (kw // 2, kw // 2, kh // 2, kh // 2))
    element = q.element_size()
    cell_bytes = batch * heads * (neighbors * (dq * (element + 4) + dv * element) + queries * (dq * (element + 4) + neighbors * (8 + element) + 2 * dv * element))
    cells_per_tile = max(1, chunk_bytes // cell_bytes)
    columns = min(low_w, cells_per_tile)
    rows = max(1, min(low_h, cells_per_tile // columns))
    for r0 in range(0, low_h, rows):
        r1 = min(r0 + rows, low_h)
        for c0 in range(0, low_w, columns):
            mm.throw_exception_if_processing_interrupted()
            c1 = min(c0 + columns, low_w)
            nr, nc = r1 - r0, c1 - c0
            cells = nr * nc
            keys = F.unfold(k[:, :, r0:r1 + kh - 1, c0:c1 + kw - 1], (kh, kw)).view(batch, heads, dq, neighbors, cells).transpose(2, 4)
            values = F.unfold(v[:, :, r0:r1 + kh - 1, c0:c1 + kw - 1], (kh, kw)).view(batch, heads, dv, neighbors, cells).transpose(2, 4)
            query = q[..., r0 * dh:r1 * dh, c0 * dw:c1 * dw].reshape(batch, heads, dq, nr, dh, nc, dw).permute(0, 1, 3, 5, 4, 6, 2).reshape(batch, heads, cells, queries, dq)
            attention = (torch.matmul(query.float(), keys.float().transpose(-1, -2)) * scale).softmax(dim=-1).to(values.dtype)
            tile = torch.matmul(attention, values).view(batch, heads, nr, nc, dh, dw, dv)
            out[..., r0 * dh:r1 * dh, c0 * dw:c1 * dw] = tile.permute(0, 1, 6, 2, 4, 3, 5).reshape(batch, heads, dv, nr * dh, nc * dw)
    if q.is_cuda:
        torch.cuda.synchronize(q.device)
    return out


def naf_forward(model, image, features, target, output, chunk_mb):
    query = model.image_encoder(image, output_size=target)
    key = F.adaptive_avg_pool2d(query, output_size=features.shape[-2:])
    batch, channels, height, width = query.shape
    heads = model.upsampler.num_heads
    result = neighborhood_attention(
        query.view(batch, heads, channels // heads, height, width),
        key.to(query.dtype), features.to(query.dtype), model.upsampler.kernel_size,
        model.upsampler.scale,
        output=output.view(batch, heads, features.shape[1] // heads, height, width),
        chunk_bytes=int(chunk_mb) * 1024**2,
    )
    return result.view(batch, -1, height, width)


def release_models(phase):
    logging.info('[PixalLowMemory] releasing sampling models before %s', phase)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    mm.unload_all_models()
    gc.collect()
    mm.soft_empty_cache(force=True)
