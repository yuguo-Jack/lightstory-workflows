# Pixal3D bounded-memory nodes

Generic replacements for the native single/multi-view conditioning and shape/texture VAE decode nodes. No ComfyUI core patches or character-specific corrections.

- NAF features keep the native dtype and full 512/1024 spatial resolutions. Large CPU buffers use writable file mappings in ComfyUI's temporary directory, reducing Windows pagefile commit.
- Neighborhood attention evaluates the same independent cells in bounded 2D tiles (default 64MiB working estimate). No model precision or sampling-step change.
- Decode wrappers release sampling-model allocations before native VAE decoding.
- Use the `PixalStable` launcher profile (`--cache-none`, split attention, reserved VRAM). With caching disabled, mapped storage is released after execution. Windows locked mappings are retried by a cleanup thread; after a crash ComfyUI's normal temp cleanup handles leftovers on restart.
- Four views can temporarily use about 12GiB of disk-backed feature data. These are temporary buffers, not additional weights.

Attention and conditioning logic derives from the local GPL-3.0 ComfyUI implementation. Native private helper APIs may require review after ComfyUI upgrades.
