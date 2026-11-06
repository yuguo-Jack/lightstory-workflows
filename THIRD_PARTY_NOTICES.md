# Third-party notices / 第三方来源

根MIT只覆盖本项目自主贡献。以下组件保留原许可；外部模型、注册资产、客户端插件和服务另有条件。不得用本项目许可覆盖这些条件。

| 组件 | 来源/固定版本 | 收纳形式 / 许可 |
|---|---|---|
| Blender Skills | [EL4CTEO/blender-skills](https://github.com/EL4CTEO/blender-skills)，`71d031dab8bc6729504d11a78cbe91945401045f` | `third_party/skills/blender-skills`，22模块MIT快照，各目录LICENSE保留；本地路径/兼容适配有记录 |
| Game Design Theory | [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills)，`1ed5976b000fc0df2910d32ed33717794da1bee2` | `skills/game-design-theory`本地适配，原MIT许可保留 |
| Game UI Design / Art参考 | [gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills)，`19d93f97c9c1ea0f8b306e77aa81e0d3e352d3e9` | 原Apache-2.0和NOTICE保留在对应Skill |
| Game Art Direction | [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)，`05ad7c8a5b8aa2aa86bbd3439ae7cf7295cac418` | 局部方法适配，原MIT许可保留 |
| ComfyUI | [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI)，`426f5eea52a7ece1dd599fff4cb6cd1f352ddd24` | 外部GPU宿主，GPL-3.0。衍生Pixal低内存和UV节点在adapters内独立保留GPL原文 |
| H3 Director | [AIMixer/ComfyUI_MiniMaxH3_Director](https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director)，`4c6245e518dd8a494f3afc4f3cccd53f22d82d10` | Apache-2.0外部库；缓存根目录补丁单独提供 |
| Ming TTS节点 | [Nynxz/ComfyUI-MingTTS](https://github.com/Nynxz/ComfyUI-MingTTS)，`55cfe4f9bb558cb15717727b912ea7829428de5d` | Apache-2.0外部库，模型许可另查 |
| SkinTokens节点 | [stevelittlefish/ComfyUI-SkinTokens-NoBlender](https://github.com/stevelittlefish/ComfyUI-SkinTokens-NoBlender)，`0f7cb09af87001333aa1127eb1df4a4b154487e7` | MIT外部包装及本机兼容补丁，内部vendored来源/权重仍按上游NOTICE |
| CrossView Warp | [cseti007/ComfyUI-CrossViewWarp](https://github.com/cseti007/ComfyUI-CrossViewWarp)，`3266a83a84eaa6833a9ebc38ac7cdd8789e44f5b` | Apache-2.0外部库 |
| Motion2MixamoRig | [MaxLiu22/Motion2MixamoRig](https://github.com/MaxLiu22/Motion2MixamoRig)，`f05a718188026b06e7ee64b47bab077970444b19` | Apache-2.0后端；其NOTICE涉及的GVHMR/SMPL-X/MANO等不由Apache覆盖 |
| MiniMax官方9个Skill | [MiniMax-AI/MiniMax-H3/skills](https://github.com/MiniMax-AI/MiniMax-H3/tree/199b7d0e1fd95e7b3eafa8c15eca692534142427/skills) | 官方正文不捆绑；固定来源外部取得，本项目只保留自写overlay。README指向独立Community协议 |
| Viggle运行时LoRA加载器 | [固定文件](https://huggingface.co/Viggle/Qwen-Image-2.1-viggle-turbo/blob/009a44a895ef85f7e643c80fdca9543795248867/comfyui/viggle_turbo.py) | 外部获取，锁定文件SHA；使用者核对上游条件 |

可自动获取的软件依赖及patch哈希见[dependencies.lock.json](third_party/dependencies.lock.json)。第三方许可证副本在`third_party/licenses`或各vendored目录。模型文件来源单独登记在`models/weights.lock.json`，其许可不能由节点源码许可推断。

Flova、行业课程/手册和其他美术参考仅作为方法来源引用，未复制私有资源或宣称移植整站内容。Game Studio、Unreal Engine Skills、CapCut、Computer Use等由客户端原生管理，本仓不重新分发其托管插件。

## 产品介绍片

`media/product-film`使用Three.js 0.183.0（MIT）、GSAP 3.14.2（[GreenSock标准免费许可](https://gsap.com/standard-license/)）、Noto Sans SC及DM Serif Display字体子集（SIL OFL）。分发包头、Three.js与字体许可均在源工程内保留；GSAP不由根MIT覆盖。HyperFrames 0.9.19（Apache-2.0）作为外部工具使用。三维场景与合成配乐为本项目原创，中文旁白通过Microsoft Edge TTS合成；详见[制作说明](media/product-film/README.md)。
