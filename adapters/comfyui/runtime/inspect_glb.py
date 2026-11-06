import io
import json
from pathlib import Path
import struct

from PIL import Image
import numpy as np
import trimesh


def inspect(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise ValueError("Invalid GLB header")
    json_length, json_type = struct.unpack_from("<II", data, 12)
    if json_type != 0x4E4F534A:
        raise ValueError("Missing glTF JSON chunk")
    document = json.loads(data[20:20 + json_length])
    binary_header = 20 + json_length
    binary = data[binary_header + 8:]
    image_info = []
    for index, image in enumerate(document.get("images", [])):
        entry = {"index": index, "name": image.get("name"), "mime_type": image.get("mimeType")}
        if "bufferView" in image:
            view = document["bufferViews"][image["bufferView"]]
            start = view.get("byteOffset", 0)
            with Image.open(io.BytesIO(binary[start:start + view["byteLength"]])) as bitmap:
                entry.update(size=list(bitmap.size), mode=bitmap.mode, embedded=True)
        image_info.append(entry)
    scene = trimesh.load_scene(path, process=False)
    geometries = []
    for name, mesh in scene.geometry.items():
        if not isinstance(mesh, trimesh.Trimesh):
            continue
        _, first, inverse, counts = np.unique(np.round(mesh.vertices, 7), axis=0, return_index=True, return_inverse=True, return_counts=True)
        seam = counts[inverse] > 1
        normals = mesh.vertex_normals
        cosines = np.sum(normals * normals[first[inverse]], axis=1).clip(-1, 1)
        angles = np.degrees(np.arccos(cosines))
        welded = mesh.copy()
        welded.merge_vertices(merge_tex=True, merge_norm=True, digits_vertex=7)
        geometries.append({"name": name, "vertices": len(mesh.vertices), "triangles": len(mesh.faces), "bounds": mesh.bounds.tolist(), "watertight_before_uv_weld": bool(mesh.is_watertight), "has_uv": getattr(mesh.visual, "uv", None) is not None, "welded_winding_consistent": bool(welded.is_winding_consistent), "welded_watertight": bool(welded.is_watertight), "uv_seam_vertex_count": int(seam.sum()), "uv_seam_max_normal_angle_degrees": float(angles[seam].max()) if seam.any() else 0, "uv_seam_vertices_over_5_degrees": int(((angles > 5) & seam).sum())})
    return {"path": str(path), "bytes": len(data), "meshes": geometries, "materials": document.get("materials", []), "images": image_info, "texture_count": len(document.get("textures", [])), "extensions_used": document.get("extensionsUsed", [])}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inspect(args.model.resolve())
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
