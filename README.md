# LightStory Workflows · 光影故事工作流

把创作想法、审美参考与交付要求，组织成可执行、可检查、可迭代的**游戏和视频制作流程**。以 Agent Skill 编排本地 ComfyUI、Blender、游戏引擎与剪辑工具，保留创作者对玩法、故事和风格的决定。

以可配置的路径、固定依赖、通用画布和执行适配串联制作步骤。创作者决定玩法、故事和风格；执行工具完成操作，实际产物接受检查和返工。

[GitHub](https://github.com/yuguo-Jack/lightstory-workflows) · [工程总览](docs/overview.html) · [English overview](README.en.md) · [安装](docs/installation.md) · [快速开始](docs/quickstart.md) · [架构](docs/architecture.md) · [依赖与许可](THIRD_PARTY_NOTICES.md) · [验证](docs/validation.md) · [维护](docs/maintenance.md) · [命令参考](docs/commands.md)

## 两个制作入口

| 入口 | 负责什么 | 按需接到哪里 |
|---|---|---|
| [`game-production-workflows`](skills/game-production-workflows/SKILL.md) | 简报、玩法/审美、路线、灰盒、垂直切片、资产分工、游戏集成、性能、测试与交付 | Web → Game Studio；原生/较高表现 → Unreal；生成与资产 → ComfyUI / Blender；过场 → Video |
| [`video-production-workflows`](skills/video-production-workflows/SKILL.md) | 剧本、视觉开发、分镜/animatic、样片、镜头生产、连续性、合成、声音、剪辑、导出与整片验收 | Qwen关键帧、H3各生成分支、Blender预演/CG、TTS/Music、CapCut或已配置的后期路线 |

单张图、单段视频、3D、绑定、配音或音乐可以直接调用[`comfyui-local-workflows`](skills/comfyui-local-workflows/SKILL.md)，无需先启动整部作品立项。Blender由`blender-core`统一路由。进入具体阶段才读取相应Skill，避免一次加载所有类型与互相冲突的审美默认。

## 包含的内容

- **7个自主/本地适配 Skill**：两个总流程、ComfyUI执行、游戏玩法/美术/UI三个创作模块、真人动作提取分支。三个创作模块保留上游许可和NOTICE。
- **22个Blender第三方模块**：以固定MIT源码快照作为第三方库收纳，并保留本机兼容适配。
- **9个MiniMax官方类型/提示词 Skill的外部依赖声明及本地执行overlay**：按固定提交获取后再组装，不将其正文混用本项目MIT许可。
- **81份通用ComfyUI画布和81份API**：Qwen17、Pixal3D7、MiniMax H3 46、Ming5、Music2、SkinTokens4。按模型/功能分组；原示例媒体改为上传占位符。
- 通用低内存Pixal/UV节点、内存保护、GLB检查、动作材质恢复、Next-Scene兼容转换等自主适配；第三方节点的补丁单独保存。
- 固定Git提交、文件SHA256、模型来源、安装配置、只读诊断、非覆盖安装及维护说明。

模型权重、虚拟环境、用户素材、私人样片、登录信息、运行缓存和大型验收工程由各用户在本地配置，不随源码分发。准确边界见[文件归属](docs/architecture.md)和[许可清单](docs/models-and-licenses.md)。

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

历史主机为Windows、RTX4080 16GB、32GB RAM。原库记录72项GPU成功、7项历史成功但旧样片已清理、2项CPU辅助成功；这些不是新机器的实测结果，也不是任意角色、时长和风格的质量保证。移植后的静态、隔离安装和脚本检查单独记录，见[验证说明](docs/validation.md)。

Windows是主要部署目标；POSIX宿主工具支持不代表全部GPU依赖已在Linux/macOS验收。接近的配置可复用同一套能力与流程，具体作品质量仍取决于输入、版本、资源与返工。

生成模型输出、Blender资产检查、引擎集成、实际游戏构建和整片播放分别验收。重GPU阶段串行。每批/阶段及连续工作至少每2小时检查空间；临时增长30GiB、累计60GiB或可用不足60GiB提前盘点，制作必需的数据允许保留。模型、源资产、成品和待返工依赖不作为无用缓存删除。

## 继续维护

源码是统一维护入口；Skill、画布、适配、第三方补丁、配置和文档各有独立位置。改流程先改对应Skill，改画布同时保存UI/API和输入要求，升级依赖先审查版本与补丁，按受影响能力验证。详见[更新流程](docs/maintenance.md)、[贡献规则](CONTRIBUTING.md)和[发布准备](docs/publication.md)。
