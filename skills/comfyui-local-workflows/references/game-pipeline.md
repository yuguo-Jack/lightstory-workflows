# 从静态资产到游戏角色：能力边界与选路

分析日期2026-10-29，部署状态更新于2026-10-30。完整游戏项目用`$game-production-workflows`编排；SkinTokens的4份Comfy画布已部署，详细操作读[SkinTokens](skintokens.md)。真人动作由`$blender-core`路由到`blender-motion-capture`，不把该外部软件说成Comfy模型。原文章对照中的旧安装状态以当前Skill为准。

## 现有库适用范围

Qwen生成概念/人物参考，Pixal生成静态GLB/PBR，H3生成视频，Ming/Music生成声音。Pixal的可读网格没有自动成为好用的低模、骨架、蒙皮、面部表情、布料或物理角色。H3的视频/动作LoRA不输出可直接重定向的骨骼动画。旧验证游戏已清理，不能当作现存依赖。

## 建议路线

1. Qwen清楚正面，人工检查后按需要补一致背/侧面；Pixal先单图1024，必要时比较双/四图及1536。
2. Blender审白模、修缺失/粘连，分离身体、衣服和道具；重拓扑/低模、UV与烘焙，保留源高模。四边面或4K纹理本身不证明游戏资产质量。
3. 标准人形可选Mixamo免费云绑定；批量/非标准软体或需要既有骨架重算权重，可试已部署SkinTokens；需要控制器/精修用Rigify或针对性骨架。机械刚性部件按约束/铰链处理。用户已接受免费Mixamo，但每个新资产仍需验收。
4. 动作来源按需求选Mixamo/已有合法动作、Epic示例、Blender关键帧；符合上游授权的真人动作需求可由Blender入口用Motion2MixamoRig。许可、单人固定机位、角色接触和材质交接细节放在专用Skill，不能当商用通用mocap认证。
5. UE IK Retargeter适配已有动作；Control Rig/FBIK修脚底与手部接触。握持/放下还要手指、接触点、附着/释放时序和碰撞控制；服饰另做权重、辅助骨骼或布料。
6. 最后做玩家控制、镜头、动画过渡、碰撞和道具交互；至少验待机/走跑/转向/停步、抬臂/下蹲、接触不滑动及性能。重型GPU阶段串行。

## 工具状态与尚待项目验证的部分

| 方案 | 用途和边界 |
|---|---|
| Blender Rigify | 本机Blender5.2.2及对应技能已可用；拟合metarig后仍需摆关节、蒙皮和变形验收。基础安装不等于角色流程通过 |
| UniRig | 未部署、当前流程不依赖。用户已要求不下载；除非后来明确改变安排，不因查用法自动安装 |
| SkinTokens/TokenRig | 已部署社区Comfy节点与4通用画布；本机人形/长颈鹿/Pixal机甲实测，详细条件与限制读SkinTokens参考 |
| Motion2MixamoRig | 已安装CLI/Blender扩展，真实视频身体/手指、复用及Blender回读已验；部分角色接触仍需修正，上游许可限制决定可用场景 |
| UE5原生工具 | 原主机已确认UE5.8.3、原生MCP及工具集插件；工程版由`executables.unreal_editor`配置真实位置。使用客户端的Unreal Engine Skills for Codex；实际项目和live MCP执行前另验，不把文件存在算连接成功 |

不要为说明方案擅自安装环境或购买服务。后续用户请求部署时，按项目依赖隔离验证，避免改坏当前ComfyUI。AI绑骨也不能补回网格缺失的手指或自动生成合格服饰物理。

来源：[Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html)、[Rigify](https://docs.blender.org/manual/en/latest/addons/rigify/basics.html)、[UniRig](https://github.com/VAST-AI-Research/UniRig)、[SkinTokens](https://github.com/VAST-AI-Research/SkinTokens)、[UE骨架编辑](https://dev.epicgames.com/documentation/en-us/unreal-engine/skeleton-editing-in-unreal-engine)、[UE动画示例](https://www.unrealengine.com/blog/game-animation-sample?lang=en-US)。
