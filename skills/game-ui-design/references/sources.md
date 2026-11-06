# 来源与本机适配

2026-11-01由 [gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/19d93f97c9c1ea0f8b306e77aa81e0d3e352d3e9/skills/disciplines/game-ui-ux) 的 `game-ui-ux` 模块安装并适配，本机名称为 `game-ui-design`。保留 [Apache-2.0许可证](../LICENSE)与[原NOTICE](../NOTICE)。原仓星数属于集合。

本机修改：入口与布局参考改成引擎中立；原Godot/Unity示例不作为本机API；补齐屏幕/状态规划、视觉与真实数据分工、UE执行及Game Studio路由；仅要求项目支持设备，不普遍强制手柄优先、所有控件绝对禁用像素位置或固定安全边距。

已比较同名的 [omer-metin版本](https://github.com/omer-metin/skills-for-antigravity/tree/e8dcf4e8737921a10088bd5c9eb65e81f74c051f/skills/game-ui-design)，其参考资料有价值，但固定阈值、正则检查及多处绝对化规定不直接作为本机验收标准；未安装该版本。UI视觉还需遵从项目美术方向。本轮只验证结构/路由，未创建新游戏UI。
