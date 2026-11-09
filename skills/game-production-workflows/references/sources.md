# 来源、版本与维护

本流程将行业制作阶段与本地工具链衔接，制作方法相对稳定；接口、安装状态、模型许可和引擎功能以当前版本为准。证据顺序：用户工程/样例 → 当前源码、配置、日志与接口 → 已安装Skill及对应版本资料 → 原作者/官方文档。

## 流程与执行来源

| 来源 | 用途与边界 |
|---|---|
| [GameDevFoundry制作阶段](https://www.gamedevfoundry.com/StagesOfGameDevelopment.html) | 原型、切片、生产、稳定和发布的工序参考，不强制统一阶段命名 |
| [EL4CTEO/blender-skills](https://github.com/EL4CTEO/blender-skills/tree/71d031dab8bc6729504d11a78cbe91945401045f) | 固定MIT快照；资产清理、拓扑、UV、烘焙、绑定、QA和导出，入口为`blender-core` |
| `comfyui-local-workflows` | 模型选路、输入、实际运行与局部检查；生成物仍需资产和引擎验收 |
| Unreal Engine Skills for Codex | 发现live MCP、保存、编译与恢复；插件、连接和目标项目分别核对 |
| Game Studio（`game-studio@openai-curated-remote`） | 选Web后实际承接架构、运行时、UI、素材规范和试玩；使用当前客户端已安装能力 |
| [StableGen](https://github.com/sakalond/StableGen) | 多视角生成/投影、局部编辑的方法参考；可选，不是本流程必需依赖 |
| [Game Development Studio](https://github.com/theisegoria/game-development-studio) | 资产清单、来源、版本与证据分类参考；不依赖其CLI、外部生成服务或审批机制 |

## 玩法、界面与美术模块

| 固定来源 | 本地模块与适配 |
|---|---|
| [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills/tree/1ed5976b000fc0df2910d32ed33717794da1bee2/skills/game-development/game-design)，MIT | [game-design-theory](../../game-design-theory/SKILL.md)：设计假设、决策与反例、真实试玩；不强加固定循环时长或奖励策略 |
| [gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/19d93f97c9c1ea0f8b306e77aa81e0d3e352d3e9/skills/disciplines/game-ui-ux)，Apache-2.0 | [game-ui-design](../../game-ui-design/SKILL.md)与美术参考：布局、输入/焦点、状态与适配；将引擎示例映射到所选UE/Web路线 |
| [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios/tree/05ad7c8a5b8aa2aa86bbd3439ae7cf7295cac418/.claude/skills/art-bible)，MIT | [game-art-direction](../../game-art-direction/SKILL.md)：Art Bible与视觉规范；不引入其整套Agent框架和逐节审批 |

模块保留原许可与NOTICE。总流程只负责调用、依赖和整体验收；执行细节留对应模块。可选渲染参考[3D Game Shaders for Beginners](https://github.com/lettier/3d-game-shaders-for-beginners)用于理解技术，不要求安装额外引擎插件。

## 操作手感与联机参考

- [game-feel固定参考](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/19d93f97c9c1ea0f8b306e77aa81e0d3e352d3e9/skills/disciplines/game-feel)：借鉴事件反馈、分层强度、时序与恢复的方法，未复制上游代码或新增独立Skill；[本流程参考](game-feel.md)补入UE/Web分工、控制诊断、联机表现和项目验收，不强加示例数值/引擎。
- [Epic网络概览](https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-overview-for-unreal-engine)与[角色网络移动](https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-networked-movement-in-the-character-movement-component-for-unreal-engine)：[联机分支](multiplayer.md)的UE权威/复制/移动边界依据；具体API、构建能力和工具按本次实际引擎版本核对，参考网页版本不代表本机已升级。
- [Rivet当前联机示例](https://github.com/rivet-dev/skills/tree/main/rivet-actors/examples/multiplayer-game-patterns)：后端候选的方法参考，不是已安装依赖；仅在项目明确选用后核对当前版本与完整配套，不沿用已移除的旧入口或将其设为UE/Web通用前置。

更新时比较固定上游版本与本地改动，保留用户已确认的玩法/风格、模块调用关系及本地执行映射。对受影响分支验证；不把Skill结构检查或历史模型运行成功等同于完整游戏品质、玩家体验、联网与打包通过。工程级验证边界见[validation](../../../docs/validation.md)。
