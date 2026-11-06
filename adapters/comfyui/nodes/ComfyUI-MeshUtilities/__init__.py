"""Reusable mesh utilities; no character-, project- or camera-specific rules.

UV processing follows ComfyUI's native UnwrapMesh implementation (GPL-3.0),
with original vertex normals propagated through the exact UV vertex map.
Core files are never patched by this extension.
"""
import numpy as np
import torch

import comfy.model_management
import comfy.utils
from comfy_api.latest import ComfyExtension, IO
from comfy_extras import nodes_mesh_postprocess as native
from server import PromptServer


class UnwrapMeshPreserveNormals(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        base = native.UnwrapMesh.define_schema()
        return IO.Schema(
            node_id="UnwrapMeshPreserveNormals",
            display_name="Unwrap Mesh UVs (Preserve Normals)",
            category="3d/texturing",
            description="Unwrap UVs using the native algorithm, retaining input normals through the exact vertex remapping. Works on any mesh; no asset-specific corrections.",
            inputs=base.inputs,
            outputs=base.outputs,
            hidden=[IO.Hidden.unique_id],
        )

    @classmethod
    def execute(cls, mesh, segmenter, resolution, padding, weld_distance):
        compute_device = comfy.model_management.get_torch_device()
        native._prepare_gpu_mesh_processing(compute_device, native._mesh_face_count(mesh) * 14 * 1024)
        seg_device = compute_device if segmenter == "pec" else torch.device("cpu")
        is_list = isinstance(mesh.vertices, list)
        is_batched = not is_list and mesh.vertices.ndim == 3
        batch = len(mesh.vertices) if is_list else (mesh.vertices.shape[0] if is_batched else 1)
        progress = comfy.utils.ProgressBar(batch)
        out_v, out_f, out_uv, out_c = [], [], [], []
        out_n = [] if mesh.normals is not None else None
        for index in range(batch):
            if is_list or is_batched:
                vertices, faces = mesh.vertices[index], mesh.faces[index]
                colors = mesh.vertex_colors
                colors = colors[index] if colors is not None and (isinstance(colors, list) or colors.ndim == 3) else colors
            else:
                vertices, faces, colors = mesh.vertices, mesh.faces, mesh.vertex_colors
            source_device = vertices.device
            vertices_np = vertices.detach().cpu().numpy().astype(np.float32)
            extent = float(np.linalg.norm(vertices_np.max(0) - vertices_np.min(0))) if len(vertices_np) else 0.0
            mapping, indices, uvs = native._uv_unwrap(
                vertices.to(seg_device).float(), faces.to(seg_device).long(),
                segmenter, int(resolution), int(padding), weld_distance * extent if weld_distance > 0 else 0.0,
            )
            uvs = uvs.copy()
            uvs[:, 1] = 1.0 - uvs[:, 1]
            out_v.append(torch.from_numpy(vertices_np[mapping]).to(source_device))
            out_f.append(torch.from_numpy(indices).to(device=source_device, dtype=torch.int32))
            out_uv.append(torch.from_numpy(uvs.astype(np.float32)).to(source_device))
            if colors is not None:
                color_np = colors.detach().cpu().numpy()
                out_c.append(torch.from_numpy(np.ascontiguousarray(color_np[mapping])).to(source_device))
            if out_n is not None:
                normals = mesh.normals
                normals = normals[index] if isinstance(normals, list) or normals.ndim == 3 else normals
                remap = torch.as_tensor(mapping, dtype=torch.long, device=normals.device)
                out_n.append(normals[remap].to(source_device))
            progress.update(1)
        output = native._pack_uv_meshes(out_v, out_f, out_uv, out_c if out_c else None)
        if out_n is not None:
            output.normals = torch.zeros_like(output.vertices)
            for index, normals in enumerate(out_n):
                output.normals[index, :normals.shape[0]] = normals
        if mesh.texture is not None:
            output.texture = mesh.texture
        if cls.hidden.unique_id:
            PromptServer.instance.send_progress_text(
                f"UV: {native._fmt_count(out_v[0].shape[0])} verts / {native._fmt_count(out_f[0].shape[0])} faces; original normals retained",
                cls.hidden.unique_id,
            )
        return IO.NodeOutput(output)


class MeshUtilitiesExtension(ComfyExtension):
    async def get_node_list(self):
        return [UnwrapMeshPreserveNormals]


async def comfy_entrypoint():
    return MeshUtilitiesExtension()
