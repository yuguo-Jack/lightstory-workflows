"""Flat-graph authoring helpers; use live frontend graphToPrompt to verify dynamic widgets."""
import copy
import json
from lightstory.config import Config
from lightstory.workflows import http


def api_to_ui(prompt, positions=None, notes=None, info=None):
    """Build an ordinary editable LiteGraph workflow for a flat native-node API graph."""
    if info is None:
        info = http(Config.load(), "/object_info")
    graph = {"last_node_id": max(int(i) for i in prompt), "last_link_id": 0, "nodes": [], "links": [], "groups": [], "config": {}, "extra": {"ds": {"scale": 0.65, "offset": [250, 150]}}, "version": 0.4}
    nodes = {}
    for order, (identifier, entry) in enumerate(prompt.items()):
        schema = info[entry["class_type"]]
        required = schema["input"].get("required", {})
        optional = schema["input"].get("optional", {})
        definitions = {**required, **optional}
        expanded = {}
        for name, definition in definitions.items():
            if definition[0] == "COMFY_AUTOGROW_V3":
                child_definition = next(iter(definition[1]["template"]["input"]["required"].values()))
                for child in entry["inputs"]:
                    if child.startswith(name + "."):
                        expanded[child] = child_definition
                continue
            expanded[name] = definition
            if definition[0] == "COMFY_DYNAMICCOMBO_V3":
                selected = entry["inputs"].get(name, definition[1]["options"][0]["key"])
                option = next(item for item in definition[1]["options"] if item["key"] == selected)
                for child, child_definition in option.get("inputs", {}).get("required", {}).items():
                    expanded[name + "." + child] = child_definition
        definitions = expanded
        node = {"id": int(identifier), "type": entry["class_type"], "pos": (positions or {}).get(identifier, [(order % 4) * 390, (order // 4) * 280]), "size": [350, 180], "flags": {}, "order": order, "mode": 0, "inputs": [], "outputs": [], "properties": {"Node name for S&R": entry["class_type"]}, "widgets_values": [], "widgets_values_named": {}, "title": entry.get("_meta", {}).get("title", entry["class_type"])}
        for name, definition in definitions.items():
            kind = definition[0]
            options = definition[1] if len(definition) > 1 and isinstance(definition[1], dict) else {}
            combo = isinstance(kind, list) or kind in ("COMBO", "COMFY_DYNAMICCOMBO_V3")
            widget = (combo or kind in ("INT", "FLOAT", "STRING", "BOOLEAN", "LOAD_3D", "BOUNDING_BOX", "BDGROUP")) and not options.get("forceInput")
            value = entry["inputs"].get(name, options.get("default"))
            is_link = isinstance(value, list) and len(value) == 2 and isinstance(value[0], str)
            if widget:
                if value is None:
                    choices = kind if isinstance(kind, list) else options.get("options", [])
                    value = (choices[0]["key"] if kind == "COMFY_DYNAMICCOMBO_V3" else choices[0]) if choices else {"INT": 0, "FLOAT": 0.0, "STRING": "", "BOOLEAN": False, "LOAD_3D": "", "BOUNDING_BOX": {"x": 0, "y": 0, "width": 512, "height": 512}}.get(kind, "")
                widget_value = options.get("default", kind[0] if isinstance(kind, list) else 0) if is_link else value
                node["widgets_values"].append(widget_value)
                node["widgets_values_named"][name] = widget_value
                if options.get("control_after_generate"):
                    node["widgets_values"].append("fixed")
                    node["widgets_values_named"]["control_after_generate"] = "fixed"
                if options.get("multiline"):
                    node["size"][1] = 330
            if not widget or is_link:
                inp = {"name": name, "type": "COMBO" if isinstance(kind, list) else kind, "link": None}
                if widget:
                    inp["widget"] = {"name": name}
                if name in optional:
                    inp["shape"] = 7
                node["inputs"].append(inp)
        for index, kind in enumerate(schema.get("output", [])):
            node["outputs"].append({"name": schema.get("output_name", schema["output"])[index], "type": kind, "links": []})
        if entry["class_type"] == "LoadImage":
            node["size"] = [350, 430]
            node["widgets_values"].append("image")
            node["widgets_values_named"]["upload"] = "image"
        elif entry["class_type"] in ("Save3DAdvanced", "Preview3DAdvanced"):
            node["size"] = [560, 650]
        graph["nodes"].append(node)
        nodes[identifier] = node
    for identifier, entry in prompt.items():
        for name, value in entry["inputs"].items():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                source, slot = value
                target_slot = next(i for i, inp in enumerate(nodes[identifier]["inputs"]) if inp["name"] == name)
                graph["last_link_id"] += 1
                number = graph["last_link_id"]
                kind = nodes[source]["outputs"][slot]["type"]
                graph["links"].append([number, int(source), slot, int(identifier), target_slot, kind])
                nodes[identifier]["inputs"][target_slot]["link"] = number
                nodes[source]["outputs"][slot]["links"].append(number)
    for text, position in notes or []:
        graph["last_node_id"] += 1
        graph["nodes"].append({"id": graph["last_node_id"], "type": "MarkdownNote", "pos": position, "size": [950, 400], "flags": {}, "order": len(graph["nodes"]), "mode": 0, "properties": {}, "widgets_values": [text]})
    if any(entry["class_type"] == "Pixal3DConditioning" or entry["class_type"] == "Pixal3DMultiViewConditioning" for entry in prompt.values()):
        graph["extra"]["ds"] = {"scale": 0.18, "offset": [70, 650]}
        graph["groups"] = [
            {"title": "① 输入与抠图", "bounding": [-30, 40, 1200, 1800], "color": "#536677", "font_size": 26, "flags": {}},
            {"title": "② 条件与权重", "bounding": [1180, 40, 1950, 680], "color": "#635477", "font_size": 26, "flags": {}},
            {"title": "③ 结构与形状细化", "bounding": [3150, 240, 1600, 1240], "color": "#547764", "font_size": 26, "flags": {}},
            {"title": "④ 原生几何与UV", "bounding": [4750, 260, 1600, 650], "color": "#547764", "font_size": 26, "flags": {}},
            {"title": "⑤ PBR 材质体素", "bounding": [4350, 1100, 1400, 500], "color": "#775a54", "font_size": 26, "flags": {}},
            {"title": "⑥ 烘焙、预览与输出", "bounding": [6350, 480, 2250, 1200], "color": "#776c54", "font_size": 26, "flags": {}},
        ]
    return graph


def template_to_api(workflow, info=None):
    if info is None: info = http(Config.load(), "/object_info")
    links = {item[0]: item for item in workflow["links"]}
    prompt = {}
    for node in workflow["nodes"]:
        kind = node["type"]
        if kind in ("Note", "MarkdownNote"):
            continue
        schema = info[kind]
        names = {**schema["input"].get("required", {}), **schema["input"].get("optional", {})}
        values = node.get("widgets_values_named", {})
        inputs = {name: copy.deepcopy(value) for name, value in values.items() if name in names or any(name.startswith(key + ".") for key in names)}
        for socket in node.get("inputs", []):
            if socket.get("link") is not None:
                edge = links[socket["link"]]
                inputs[socket["name"]] = [str(edge[1]), edge[2]]
        prompt[str(node["id"])] = {"class_type": kind, "inputs": inputs, "_meta": {"title": node.get("title", kind)}}
    return prompt


def prune(prompt, roots, aliases=None):
    aliases = aliases or {}
    result = {}

    def resolve(value):
        if not (isinstance(value, list) and len(value) == 2 and isinstance(value[0], str)):
            return value
        identifier, slot = value
        if (identifier, slot) in aliases:
            return resolve(aliases[identifier, slot])
        entry = prompt[identifier]
        if entry["class_type"] == "ComfySwitchNode":
            selection = entry["inputs"]["switch"]
            if isinstance(selection, list):
                selection = prompt[selection[0]]["inputs"]["value"]
            return resolve(entry["inputs"]["on_true" if selection else "on_false"])
        if entry["class_type"] == "PreviewImage":
            return resolve(entry["inputs"]["images"])
        visit(identifier)
        return [identifier, slot]

    def visit(identifier):
        if identifier in result:
            return
        entry = copy.deepcopy(prompt[identifier])
        result[identifier] = entry
        entry["inputs"] = {name: resolve(value) for name, value in entry["inputs"].items()}

    for identifier in roots:
        visit(str(identifier))
    return dict(sorted(result.items(), key=lambda item: int(item[0])))
