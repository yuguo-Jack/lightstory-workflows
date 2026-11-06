---
name: game-production-workflows
description: 根据目标平台、体验和品质要求选择 Web 或 Unreal 游戏制作路线，编排本机 ComfyUI、Blender、Mixamo 与引擎；Web 路线交由 Game Studio 执行，并按需复用本地资产链。覆盖创意与审美、灰盒、垂直切片、资产分工、动画、交互、关卡、音画、性能、测试、交付及制作期空间管理，保留用户的玩法和美术决定。
metadata:
  version: "1.4.0"
  environment_checked: "2026-10-30"
  workflow_reviewed: "2026-11-02"
---

## LightStory 工程版入口

先读[统一路径与执行映射](../runtime-map.md)。本文保留原制作方法、选路与质量边界；机器路径通过工程配置解析。标注为历史实测的内容只代表原主机，当前安装由doctor和本次产物验证。缺少第三方执行器时明确选用已配置路线或报告依赖，不假装插件已连接。


# Game Production Workflows

把用户的玩法想法、内容需求和审美样例变成可运行、可迭代、可交付的游戏。先确定运行路线：用户明确选择优先；轻量需求、浏览器分发或快速验证适合时可交由 Game Studio 接管 Web 实现；较高表现、复杂角色/物理及原生交付通常优先本机 UE5。不能仅按视角、2D/3D或引擎名字判断品质。具体依据见[路线选择](references/runtime-selection.md)。

这是制作总入口，不是新引擎、生成模型或已完成的游戏。用户授权制作时持续实施、检查、修复和交付，不能仅返回计划或生成素材后停止。大项目通过可复用的高质量切片逐步扩展；切片不是擅自缩减后的最终交付，也不承诺任意规模游戏都能一次自动完成。

## 总入口的职责与交接

本技能维护项目目标、玩法/美术决定、运行路线、需求和资产依赖、阶段安排、跨工具调度及游戏端整体验收。具体模型配方/节点/资源排错由ComfyUI技能维护；可编辑3D与资产QA由Blender技能负责；Web交Game Studio及其专项技能，UE实际工程操作交`unreal-mcp`；完整视频交Video总流程。不在总入口另维护这些工具的操作手册。

推进到某阶段时，实际读取并调用相关技能及本次需要的参考，传入同一项目的要求，收回真实产物、检查结果、限制和保留依赖，再接回当前制作阶段。执行成功、素材合格、运行端集成与整体验收分开；子任务不重新立项、重选引擎或递归启动游戏总入口。见[子任务执行与结果回接](references/project-operations.md#子任务执行与结果回接)。

## 开始或恢复

1. 若已有项目，先读项目说明、当前状态、最近可用构建、验收和未决问题；复用已有成果。纯分析请求不启动生成、编辑工程或安装软件。
2. 从用户提供的想法与样例提取：核心体验、视角/控制、内容范围、目标平台、分发方式、画质/帧率、参考图职责与交付标准。读[设计与审美输入](references/design-and-art.md)，需要深化玩法、界面或美术时分别调用下表设计技能；按[路线选择](references/runtime-selection.md)确定 Web/Unreal及执行入口。只追问真正影响路线且无法推断的决定；其余记录假设并继续。
3. 按路线检查相关环境：UE/本地资产处理可执行 `scripts/probe_local.py` 并读[本机入口](references/local-environment.md)；Web按 Game Studio 检查当前工程与构建工具，不为浏览器项目启动UE。使用用户目录；无指定时在 `${PROJECTS_ROOT}` 建立语义明确的项目目录并检查重名。按[空间管理](references/project-operations.md)登记磁盘基线、临时目录、缓存归属与保留用途。
4. 批量制作前按[资产分工](references/asset-production.md)确定生成模型、Blender、引擎及现有素材各自职责，区分共享源资产与目标端导出，明确后处理、依赖和验收位置。不要求每个项目都用全部工具。
5. 新项目按需采用[创作简报](assets/project-brief.md)、[项目状态](assets/project-state.json)、[资产清单](assets/asset-register.csv)和[验收矩阵](assets/acceptance-matrix.md)；已有等价记录沿用。选最小相关执行分支，Web接管后保持同一简报与状态，素材可选调用本地链，不重复立项。新任务素材/脚本留项目，不把角色/关卡特化写进全局技能或通用Comfy模板。

使用ComfyUI时优先复用能满足要求的通用画布；仅换素材、提示词或参数的任务保留项目运行副本。确需改节点/流程时，以最接近的现有画布另存定制版，放入原生工作流栏目`Projects/<项目ID>/<模型>/<功能>.json`，不覆盖通用模板。来源、修改、UI/API、验收与清理归属按[画布复用与项目定制](references/project-operations.md#comfyui-画布复用与项目定制)记录；游戏调用视频总流程时沿用同一项目ID和目录。模型/节点安装更新、通用画布补充及验收属于能力维护，其通用画布归模型/功能栏目，验收样例不因此成为游戏制作项目。

新会话调用这个总入口即可按下表选择设计与执行技能；实际读取相关 `SKILL.md` 及本轮需要的参考，再在当前项目执行，不能只把名字写进计划。按[子任务交接](references/project-operations.md#子任务执行与结果回接)携带用户要求并接回结果；创作模块另见[设计决定回接](references/design-and-art.md#子技能调用与结果回接)。若技能未出现在本轮目录中，可沿表中本地链接或当前插件目录读取；文件确实缺失时核对安装位置，不能声称已调用。跨会话恢复依据项目落盘记录，不假设能继承旧聊天中的未保存想法或附件。

局部返工沿用项目已有 brief 和目标，只处理受影响范围。单张图、单个模型或一次 Blender 操作直接使用对应执行层，不强制启动完整游戏立项流程。

执行时可按需组合本机系统命令行工具、系统 Python 环境及其库、自编脚本、技能和插件。FFmpeg/ffprobe 等是可用工具的示例；按任务选择可靠方法，简单确定性处理可以直接完成。环境选择和文件约定见[本机工具使用原则](references/local-environment.md#本机命令行与-python-工具)。

## 分工与按需阅读

| 当前工作 | 执行入口与参考 |
|---|---|
| Web/Unreal路线选择、Web接管和跨端资产边界 | [运行路线选择](references/runtime-selection.md)；Web使用 `game-studio:game-studio` |
| 工具职责、素材制作方法、共享源资产与目标版本 | [资产生产与分工](references/asset-production.md) |
| 核心循环、玩家决策、进度/难度、灰盒设计假设 | [Game Design Theory](../game-design-theory/SKILL.md)（`$game-design-theory`）；[设计与审美输入](references/design-and-art.md) |
| 美术方向、风格规范、视觉切片与批量一致性 | [Game Art Direction](../game-art-direction/SKILL.md)（`$game-art-direction`）；[设计与审美输入](references/design-and-art.md) |
| 全项目阶段、范围与可重复生产 | [制作阶段与推进规则](references/production-cycle.md) |
| 生图、参考/蒙版/结构控制、图片转3D、绑定、语音、音乐及单项视频 | [ComfyUI Local Workflows](../comfyui-local-workflows/SKILL.md)；按其相关模型参考查当前画布、用法和注意事项，再按[资产生产](references/asset-production.md)或[音频/演出](references/presentation.md)接入游戏 |
| 完整过场、片头片尾、预渲染动效、循环背景等视频素材 | 调用[Video Production Workflows](../video-production-workflows/SKILL.md)，按[游戏视频制作与回接](references/presentation.md#游戏视频与动效的制作和回接)交付并接回游戏；实时交互效果由运行端实现 |
| 网格、UV、材质、烘焙、优化、Blender 动画与导出 | `$blender-core`，多阶段资产按需读取 `blender-workflow-recipes`；[资产生产](references/asset-production.md) |
| 人物、服饰、绑定、动作与接触 | [角色与动画](references/character-animation.md)；按场景选Comfy/SkinTokens、Mixamo、Rigify；真人动作经`blender-core`路由到`blender-motion-capture`，再做接触与引擎适配 |
| 工程、玩家、镜头、输入、AI、存档、交互 | [UE 工程与运行时](references/unreal-implementation.md) |
| 场景、灯光、材质一致性、VFX、2D/2.5D | [关卡与视觉质量](references/levels-and-visuals.md) |
| HUD、菜单、屏幕/状态流、焦点与适配 | [Game UI Design](../game-ui-design/SKILL.md)（`$game-ui-design`）→ 已选UE/Web执行层；[界面接入](references/presentation.md) |
| 声音、配音、音乐、过场 | [音频、演出和界面](references/presentation.md) |
| 测试、性能与成品交付 | [质量、性能与发布](references/quality-performance-release.md) |
| 子任务交接、文件组织、续作、授权、资源调度、缓存清理 | [项目运行与收尾](references/project-operations.md) |
| 文档和经验来源、适用版本 | [来源与维护](references/sources.md) |

**执行层**：Web由用户指定的 **Game Studio** 路由到Phaser、Three.js或React Three Fiber及资产/UI/试玩技能；项目目标和本机素材约定继续有效。UE使用 **Unreal Engine Skills for Codex** 的 `unreal-mcp`，按当前真实接口执行；未连接时按其 setup/operations 排查，插件文件/引擎存在不算在线证明。不为方法论创建UE的AgentSkill UAsset。

## 制作闭环

按[阶段表](references/production-cycle.md)推进：需求与可行性 → 可玩灰盒 → 可重复的垂直切片 → 功能/内容生产 → 整体打磨 → 性能与稳定性 → 打包验收 → 修复/更新。

运行路线和素材制作路线分开决定。Web也可复用Qwen、Pixal、Blender、Mixamo及音频素材；UE也可直接制作规则构件、地形/关卡、材质、VFX和运行时逻辑。按资产需求分工，不把全部内容都先送生成模型。路线选定后不因难点无解释地改引擎。

- **玩法不是跳过项**：需要时用 `game-design-theory` 把体验目标变成可检验的规则和灰盒假设；用 `game-art-direction` 将审美样例转成视觉规范，再由 `game-ui-design` 落实信息、状态和操作流。主观决定由用户给定或评审，设计技能不替代实际实现与试玩，也不默认一种个人风格。
- **质量先在小范围成立**：代表性角色、一个场景单元和一次完整交互按最终品质串通，再批量生产。避免只能对一张图或一个角色奏效的特化补丁。
- **制作和验证同时推进**：尽早得到能独立启动的构建，之后在真实镜头和实际负载下验收；不等全部美术做完才第一次打包。
- **客观关卡自主处理**：发现缺陷就修复并重测受影响部分，不为每个导入、保存和普通返工索要批准。核心玩法、主要审美或项目范围需要用户决定时，先提供可审阅的具体结果，再集中请求评审；继续不依赖该决定的工作。
- **同一项目保留一个当前事实**：状态记录中写清本轮改动、仍未通过项、证据路径、下一个可执行步骤。用户中途纠正目标时更新记录，不重新从零生成。
- **制作期间持续管理空间**：每批生成、渲染、构建及阶段结束后检查清理，导入/烘焙后也检查；连续工作至少每 **2小时**检查一次。临时数据较上次检查增长 **30 GiB**、累计超过 **60 GiB**，或所在盘可用空间低于 **60 GiB**，提前盘点处理。这些是可按项目记录调整的预警值，非删除上限。确认属于制作需要的增长可保留，仅记录用途；实际剩余空间足以完成后续任务时，无需因触发预警清理、暂停或降品质。确认无用的大临时文件当轮清理，覆盖项目及工具原生目录；模型、源资产、工程依赖、可用构建和必要返工缓存保留。暂停/交接前检查并登记保留项；Web接管也继承同一规则，不等整个游戏结束才清理。

## 完成标准

交付目标由用户范围决定，但一个高完成度游戏至少需要：进入游戏和理解操作的路径、完整核心循环、正确的输入/镜头/碰撞/动画、所需的存档与恢复、统一音画与可读 UI、目标硬件性能、可启动的打包版本及使用说明。适用项可标 `not_applicable` 并说明依据，不能直接删除难做的需求。

分别记录 `not_started / in_progress / blocked / failed / passed / needs_user_review / not_applicable`。证明边界必须清楚：

- 模型/音视频生成成功，不等于资产达到游戏品质。
- Blender 检查或文件回读，不等于目标引擎/浏览器正确导入、材质和变形。
- 编辑器里看起来正常，不等于运行时交互正确。
- PIE 通过，不等于打包版本可用。
- Web开发服务器可玩，不等于正式构建的资源、输入、声音和存档都通过。
- 截图、合成测试或静态代码检查，不等于玩家体验和性能实测。

交付前按[验收与发布](references/quality-performance-release.md)检查当前构建，并按[收尾规则](references/project-operations.md)清理不再使用的临时文件。保留源工程、原始输入、合格资产、当前成品、必要证据和仍需返工缓存；明确剩余限制，不用“已生成”替代“已验收”。

## 调用示例

`$game-production-workflows 根据这些玩法想法和参考图，在指定目录制作第三人称游戏。先做可玩的灰盒，再把代表性场景提升到目标品质，继续完成约定内容和打包验收。`

`$game-production-workflows 接着这个 UE 工程做，先读当前状态和已有构建，修复镜头、人物动作和交互，再补齐音画、设置、存档和成品测试。`

`$game-production-workflows 根据我的玩法和审美样例，按需调用Game Design Theory、Game Art Direction与Game UI Design，先验证核心循环与视觉切片，再进入正式生产；保留我已确定的规则与风格。`

`$game-production-workflows 将这套俯视游戏的审美样例转成资产和镜头规范，保留我的玩法，安排生产顺序与质量关卡；这次只做分析。`

`$game-production-workflows 根据这些需求先判断Web或UE路线。若适合Web，调用Game Studio完成开发和试玩；素材按需复用本机生成模型与Blender，并按目标端预算处理。`
