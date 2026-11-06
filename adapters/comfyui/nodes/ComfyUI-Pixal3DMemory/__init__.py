"""Quality-preserving bounded-memory Pixal3D nodes. No core files are patched."""
import math
import logging

import torch

import comfy.model_management as mm
import comfy.utils
from comfy_api.latest import ComfyExtension, IO
from comfy_extras import nodes_trellis2 as native

from .memory import mapped_empty, naf_forward, release_models


def upsample(naf_model, low, composites, image_size, target, chunk_mb):
    if naf_model is None:
        return None
    mm.load_model_gpu(naf_model)
    inner = naf_model.model
    dtype = next(inner.parameters()).dtype
    result = mapped_empty((len(composites), low.shape[1], *target), dtype)
    device = mm.get_torch_device()
    for index, composite in enumerate(composites):
        image = comfy.utils.common_upscale(composite, image_size, image_size, 'lanczos', 'disabled').to(device, dtype)
        feature = low[index:index + 1].to(device, dtype)
        naf_forward(inner, image, feature, target, result[index:index + 1], chunk_mb)
    return result


def conditioning(clip_vision_model, image, transform, angle, mesh_scale, views, chunk_mb):
    out_device = torch.device('cpu')
    device = mm.get_torch_device()
    cond = native._dino_encode_batch(clip_vision_model, image, out_device, want_patches=True)
    batch = cond['batch_size'] // views
    low512, low1024 = cond['patches_512'], cond['patches_1024']
    composites = cond['composites']
    naf = clip_vision_model.naf
    shape512 = upsample(naf, low512, composites, 512, (512, 512), chunk_mb)
    shape1024 = upsample(naf, low1024, composites, 1024, (512, 512), chunk_mb)
    texture = upsample(naf, low1024, composites, 1024, (1024, 1024), chunk_mb)
    global512 = cond['global_512'].unflatten(0, (batch, views)).mean(dim=1)
    global1024 = cond['global_1024'].unflatten(0, (batch, views)).mean(dim=1)
    pack = {
        'stages': {
            'ss': {'feature_map': low512, 'feature_map_hr': None, 'image_resolution': 512},
            'shape_512': {'feature_map': low512, 'feature_map_hr': shape512, 'image_resolution': 512},
            'shape_1024': {'feature_map': low1024, 'feature_map_hr': shape1024, 'image_resolution': 1024},
            'tex_1024': {'feature_map': low1024, 'feature_map_hr': texture, 'image_resolution': 1024},
        },
        'transform_matrix': transform.to(out_device), 'camera_angle_x': angle.to(out_device),
        'mesh_scale': mesh_scale.to(out_device), 'num_views': views, 'patch_size': 16,
    }
    features = native.compute_stage_proj_feats(pack, 'ss', dense_grid_resolution=16, batch_size=batch, device=device)
    positive = [[global512, {'embeds': global1024, 'proj_feat_pack': pack, 'trellis2_proj_feats': features}]]
    negative = [[torch.zeros_like(global512), {'embeds': torch.zeros_like(global1024), 'proj_feat_pack': pack, 'trellis2_proj_feats': features}]]
    return IO.NodeOutput(positive, negative)


class Pixal3DConditioningLowMemory(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        base = native.Pixal3DConditioning.define_schema()
        return IO.Schema(node_id='Pixal3DConditioningLowMemory', display_name='Pixal3D Conditioning (Low Memory)', category='3d/Pixal3D', description='FP32 file-backed NAF features and spatially tiled attention. Same model precision and feature resolutions. Use --cache-none to release temporary maps after each run.', inputs=base.inputs + [IO.Int.Input('chunk_mb', default=64, min=16, max=256)], outputs=base.outputs)

    @classmethod
    def execute(cls, clip_vision_model, image, camera_angle_x, chunk_mb=64):
        batch = image.shape[0]
        angle = math.radians(float(camera_angle_x))
        distance = torch.full((batch,), 0.5 / math.tan(angle / 2))
        transform = native.build_proj_transform_matrix(distance, batch, distance.device)
        return conditioning(clip_vision_model, image, transform, torch.full((batch,), angle), torch.ones(batch), 1, chunk_mb)


class Pixal3DMultiViewConditioningLowMemory(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        base = native.Pixal3DMultiViewConditioning.define_schema()
        return IO.Schema(node_id='Pixal3DMultiViewConditioningLowMemory', display_name='Pixal3D Multi-View Conditioning (Low Memory)', category='3d/Pixal3D', description='Native fixed view rig with bounded-memory FP32 features. No image-, character- or project-specific rules.', inputs=base.inputs + [IO.Int.Input('chunk_mb', default=64, min=16, max=256)], outputs=base.outputs)

    @classmethod
    def execute(cls, clip_vision_model, fov, front=None, left=None, back=None, right=None, chunk_mb=64):
        images = {'front': front, 'left': left, 'back': back, 'right': right}
        names = [name for name in native._VIEW_AZIMUTHS if images[name] is not None]
        if not names:
            raise ValueError('At least one view is required')
        batch = images[names[0]].shape[0]
        azimuths = [native._VIEW_AZIMUTHS[name] - native._VIEW_AZIMUTHS[names[0]] for name in names]
        items = []
        for index in range(batch):
            for name in names:
                view = images[name][index % images[name].shape[0]][None]
                if view.shape[-1] == 4:
                    view = view[..., :3] * view[..., 3:4]
                if view.shape[1:3] != (1024, 1024):
                    view = comfy.utils.common_upscale(view.movedim(-1, 1), 1024, 1024, 'lanczos', 'disabled').movedim(1, -1)
                items.append(view)
        angle = math.radians(float(fov))
        transform = native._orbit_camera_to_world(azimuths, [0.0] * len(names), native._VIEW_PAD * 0.5 / math.tan(angle / 2))
        return conditioning(clip_vision_model, torch.cat(items), transform.repeat(batch, 1, 1), torch.full((batch * len(names),), angle), torch.ones(batch), len(names), chunk_mb)


class Pixal3DDecodeShapeLowMemory(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        base = native.VaeDecodeShapeTrellis.define_schema()
        return IO.Schema(node_id='Pixal3DDecodeShapeLowMemory', display_name='Pixal3D Decode Shape (Low Memory)', category='3d/Pixal3D', description='Release sampling-model VRAM before native shape decoding; decoding parameters are unchanged.', inputs=base.inputs, outputs=base.outputs)

    @classmethod
    def execute(cls, samples, vae):
        release_models('shape decode')
        coord_resolution = samples.get('coord_resolution')
        logging.info('[PixalLowMemory] shape coord_resolution=%s target_geometry=%s', coord_resolution, int(coord_resolution) * 16 if coord_resolution is not None else 'native_default')
        return native.VaeDecodeShapeTrellis.execute(samples, vae)


class Pixal3DDecodeTextureLowMemory(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        base = native.VaeDecodeTextureTrellis.define_schema()
        return IO.Schema(node_id='Pixal3DDecodeTextureLowMemory', display_name='Pixal3D Decode Texture (Low Memory)', category='3d/Pixal3D', description='Release sampling-model VRAM before native texture decoding; decoding parameters are unchanged.', inputs=base.inputs, outputs=base.outputs)

    @classmethod
    def execute(cls, samples, vae, shape_subdivides):
        release_models('texture decode')
        return native.VaeDecodeTextureTrellis.execute(samples, vae, shape_subdivides)


class PixalMemoryExtension(ComfyExtension):
    async def get_node_list(self):
        return [Pixal3DConditioningLowMemory, Pixal3DMultiViewConditioningLowMemory, Pixal3DDecodeShapeLowMemory, Pixal3DDecodeTextureLowMemory]


async def comfy_entrypoint():
    return PixalMemoryExtension()
