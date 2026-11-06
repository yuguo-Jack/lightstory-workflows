# LightStory Workflows · 光影故事工作流

把创作想法、审美参考与交付要求，组织成可执行、可检查、可迭代的**游戏和视频制作流程**。通过 Agent Skill 串联 ComfyUI、Blender、游戏引擎与剪辑工具，保留创作者对玩法、故事和风格的决定，并完成实际制作、检查和返工。

> **本机实测环境：Windows＋NVIDIA GeForce RTX 4080（16GB显存）＋32GB内存。** 下列81组模型画布均有该环境上的样例运行验证记录，其中包含GPU推理和CPU辅助流程。按所记录的量化、尺寸、时长及内存配置运行，详见[验证环境与范围](docs/validation.md#验证环境与范围)。

[工程总览](docs/overview.html) · [安装](docs/installation.md) · [快速开始](docs/quickstart.md) · [架构](docs/architecture.md) · [依赖与许可](THIRD_PARTY_NOTICES.md) · [验证](docs/validation.md) · [维护](docs/maintenance.md) · [命令参考](docs/commands.md)

## 两个制作入口

| 入口 | 负责什么 | 按需接到哪里 |
|---|---|---|
| [`game-production-workflows`](skills/game-production-workflows/SKILL.md) | 简报、玩法/审美、路线、灰盒、垂直切片、资产分工、游戏集成、性能、测试与交付 | Web → Game Studio；原生/较高表现 → Unreal；生成与资产 → ComfyUI / Blender；过场 → Video |
| [`video-production-workflows`](skills/video-production-workflows/SKILL.md) | 剧本、视觉开发、分镜/动态分镜、样片、镜头生产、连续性、合成、声音、剪辑、导出与整片验收 | Qwen-Image-2.1制作关键帧；MiniMax H3生成视频；Blender预演/CG；Ming-3.0-TTS Tiny配音；MiniMax Music 3配乐；CapCut等工具后期 |

单张图、单段视频、3D、绑定、配音或音乐可以直接调用[`comfyui-local-workflows`](skills/comfyui-local-workflows/SKILL.md)，无需先启动整部作品立项。Blender由`blender-core`统一路由。进入具体阶段才读取相应Skill，避免一次加载所有类型与互相冲突的审美默认。

## 包含的内容

- **7个自主/本地适配 Skill**：两个总流程、ComfyUI执行、游戏玩法/美术/UI三个创作模块、真人动作提取分支。三个创作模块保留上游许可和NOTICE。
- **22个Blender第三方模块**：以固定MIT源码快照作为第三方库收纳，并保留本机兼容适配。
- **9个MiniMax官方类型/提示词 Skill的外部依赖声明及本地执行overlay**：按固定提交获取后再组装，不将其正文混用本项目MIT许可。
- **81组通用ComfyUI工作流**：每组包含一份可编辑画布和一份API文件，按下表的模型与功能归类。
- Pixal3D低内存处理及UV节点、内存保护、GLB检查、动作材质恢复、Qwen-Image-2.1 Next-Scene LoRA兼容转换等适配；第三方节点的补丁单独保存。
- 固定Git提交、文件SHA256、模型来源、安装配置、只读诊断、非覆盖安装及维护说明。

模型权重、虚拟环境、用户素材、私人样片、登录信息、运行缓存和大型验收工程由各用户在本地配置，不随源码分发。准确边界见[文件归属](docs/architecture.md)和[许可清单](docs/models-and-licenses.md)。

### 模型与画布

| 模型名称 | 主要用途 | 画布数量 | 本机部署方案 |
|---|---|---:|---|
| [Qwen-Image-2.1](skills/comfyui-local-workflows/references/qwen.md) | 文生图、参考图编辑、蒙版局部修改、透明图、结构控制与分镜 | 17份 | INT8主模型；控制与LoRA按功能选配 |
| [Pixal3D](skills/comfyui-local-workflows/references/pixal3d.md) | 单图/多视图生成3D模型及PBR材质，输出GLB | 7份 | INT8单图/多视图模型，配套TRELLIS.2形状与纹理VAE；含低内存适配 |
| [MiniMax H3](skills/comfyui-local-workflows/references/h3.md) | 文生/图生视频、多参考、连续长视频、视频编辑、结构控制与精修 | 46份 | W6A8主模型；涵盖普通版、Turbo及Pika H3 Flex，按各自配套选用 |
| [Ming-3.0-TTS Tiny](skills/comfyui-local-workflows/references/tts.md) | 文字配音、音色设计/参考、情绪表演与多角色对白 | 5份 | INT8语音主模型及配套音频VAE |
| [MiniMax Music 3](skills/comfyui-local-workflows/references/music.md) | 文字生成纯音乐配乐或歌词歌曲 | 2份 | INT8主模型和文本编码器，配套DAV音频解码器 |
| [SkinTokens](skills/comfyui-local-workflows/references/skintokens.md) | 3D模型自动骨架/蒙皮、既有骨架补权重、命名与权重修复 | 4份 | TokenRig GRPO＋Skin VAE；2份GPU推理、2份CPU处理 |

点击模型名称查看使用方法、优势、输入要求和限制；实际权重文件与SHA256登记在`models/weights.lock.json`。

## 最短安装路径

使用系统Python **3.11+**和Git，在希望长期保留源码的位置执行：

```powershell
git clone https://github.com/yuguo-Jack/lightstory-workflows.git
cd lightstory-workflows
python -m pip install -e .
python tools/lightstory.py config init --template windows
# 编辑 config/local.json，把示例路径改为自己的安装路径
python tools/lightstory.py paths
python tools/lightstory.py validate
python tools/lightstory.py doctor
```

Windows启动内存保护或使用托管停止命令时安装`python -m pip install -e ".[windows]"`。这是宿主辅助环境；ComfyUI推理继续用它自己的解释器，Blender内部用其原生Python，Motion按独立分支配置。

安装自带的Skill与Blender库，先看计划，再执行：

```powershell
python tools/lightstory.py install skills --agent codex
python tools/lightstory.py install skills --agent codex --apply
# Claude使用 --agent claude；新开会话读取。既有同名不同内容会报告冲突。
```

Windows目录链接需系统允许，Skill也可用`--copy --apply`；复制模式需自行同步更新。保留源码目录，editable安装和链接都以它为维护来源。

完整的ComfyUI节点/模型、MiniMax类型Skill、Blender、Motion、Unreal、Web与剪辑集成见[分阶段安装](docs/installation.md)，无需为了只读流程方法安装所有GPU模型。这里只完成基础Skill安装；实际生成前还需配置所用分支并真实验收。安装文件不代表MCP已连接或生成质量已通过。

## 使用示例

> 使用 `game-production-workflows`，结合我的玩法和审美参考，先确定目标平台与Web/Unreal路线，再做可玩灰盒、代表性品质切片，继续完成约定功能、内容和可独立运行的交付。

> 使用 `video-production-workflows`，根据我的剧本、参考风格、时长和交付规格制作成片；先整理视觉/连续性依据和全片动态分镜，验证难点镜头，再逐镜制作、剪辑混音和真实播放验收。

> 使用 `comfyui-local-workflows`，从通用画布选择最适合这张输入的单项流程，执行并检查实际结果。只改参数时保存任务副本；改节点时放本项目的原生`Projects/<项目ID>/<模型>/<功能>`栏目。

本地浏览工程总览可运行`python tools/lightstory.py runtime serve`，打开`http://127.0.0.1:8192/`；该入口仅预览公开文档/画布，不公开用户输入、输出或机器配置。

## 质量和资源边界

上述4080工作站的81组画布验证包含79项GPU运行和2项CPU辅助处理；其中7项Pixal3D历史样片已清理，成功记录仍保留。已验过的输入规模、量化配套和资源处理见各模型说明；新素材、不同规模和其他硬件仍需校准。工程安装检查与实际模型运行分别记录，见[验证说明](docs/validation.md)。

Windows是主要部署目标；POSIX宿主工具支持不代表全部GPU依赖已在Linux/macOS验收。接近的配置可复用同一套能力与流程，具体作品质量仍取决于输入、版本、资源与返工。

生成模型输出、Blender资产检查、引擎集成、实际游戏构建和整片播放分别验收。重GPU阶段串行。每批/阶段及连续工作至少每2小时检查空间；临时增长30GiB、累计60GiB或可用不足60GiB提前盘点，制作必需的数据允许保留。模型、源资产、成品和待返工依赖不作为无用缓存删除。

## 继续维护

源码是统一维护入口；Skill、画布、适配、第三方补丁、配置和文档各有独立位置。改流程先改对应Skill，改画布同时保存UI/API和输入要求，升级依赖先审查版本与补丁，按受影响能力验证。详见[更新流程](docs/maintenance.md)、[贡献规则](CONTRIBUTING.md)和[发布准备](docs/publication.md)。

## 欢迎提需求与反馈

欢迎在 [Issues](https://github.com/yuguo-Jack/lightstory-workflows/issues) 提需求、反馈问题或分享实际使用场景。新模型与工作流、游戏/视频制作环节、部署适配、批量处理、性能和文档改进，都欢迎讨论。

不需要先有完整方案：说说**你想做什么、目前卡在哪里、使用什么硬件环境**，有参考样例或复现步骤更好。真实需求会帮助确定后续完善方向，也欢迎通过 Pull Request 一起改进。希望大家多提想法，让这套流程越来越实用。

## 打赏支持

如果这套流程对你有帮助，欢迎通过支付宝自愿打赏，支持持续维护、模型适配和本地验证。**提需求和反馈无需打赏，欢迎大家多提建议。**

<a href="docs/assets/alipay-support.jpg"><img src="docs/assets/alipay-support.jpg" alt="支付宝打赏收款码，收款人：Jack" width="300"></a>

使用支付宝扫码；点击图片可查看原图。
