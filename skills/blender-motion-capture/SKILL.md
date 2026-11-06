---
name: blender-motion-capture
description: Recover body and optional finger motion from a real single-person video using this Windows host's installed Motion2MixamoRig, reuse it on compatible Mixamo FBX rigs, restore source UV/materials when topology matches, and review/bake/export the animation in Blender. Use through blender-core for video mocap, not AI video generation or automatic cloth/face animation.
metadata:
  version: "1.0.0"
  environment_checked: "2026-10-30"
---

## LightStory 工程版入口

先读[统一路径与执行映射](../runtime-map.md)。本文保留原制作方法、选路与质量边界；机器路径通过工程配置解析。标注为历史实测的内容只代表原主机，当前安装由doctor和本次产物验证。缺少第三方执行器时明确选用已配置路线或报告依赖，不假装插件已连接。


# Blender Motion Capture

这是`blender-core`下的本机执行分支。真实视频 → 身体/可选手指动作 → 合格Mixamo骨架 → Blender修整/烘焙/导出。先读[本机使用、排错及清理](references/usage.md)，按目标选择CLI或已配置的Blender面板；不把软件安装、doctor通过或预览GLB存在作为质量验收。

## 选路

- 希望复现真人表演、输入为清楚完整的单人固定机位视频，且用途符合上游授权：可用本路线。
- 只是常见走跑/跳跃：Mixamo现成动作或已有动作通常更省工；精确交互/导演表演可直接Blender关键帧、IK与接触修正。
- 这是人形动作提取器，不给坦克/机械/动物自动推导动作；不生成脸部表情、口型、布料或物理碰撞。SkinTokens绑定另走`$comfyui-local-workflows`，其骨骼改名也不自动保证符合本工具的Mixamo输入要求。
- **授权边界影响路线选择**：Motion2MixamoRig自身Apache代码不覆盖GVHMR、SMPL-X、MANO等上游限制。当前依赖有非商业研究限制；没有相应额外授权时只用于符合条款的研究/原型，商业成品优先Mixamo合法动作/自制动画或另行取得授权。原视频与素材的使用权另核对。

## 执行闭环

1. 沿用项目目录，确认原视频、目标rig、FPS/帧范围、是否要手指和道具接触。测试资源放项目的runtime，不把内容写回工具源码或全局Skill。
2. 读usage的环境/输入要求；先短片校准，再扩展。外部推理由已配置Python执行；Blender自带bpy只处理资产和动画，不在Blender Python里import torch/GVHMR或装推理依赖。
3. 身体先提取，核对方向、时长、脚底和根位移；需要手指时复用身体结果与原body cache追加HaMeR。用带手指的完整skeleton再给多个合格rig复用，不为每个角色重跑真人提取。
4. 进入Blender先设置源FPS再导入。保留原成品资产：原工具GLB只含简化颜色，若源FBX与输出网格严格同拓扑可用已验证恢复工具带回UV/PBR；不符合时在原最终角色上重定向动作，不投机投影纹理。
5. 用`blender-animation`处理动作、参考姿势、根运动、足滑和接触；用`blender-character-rigging`核对rig。具体返工按项目目标或用户标注处理，保留原版本，不把质量报告上的错误悄悄标成通过。
6. 调用`blender-asset-qa`和`blender-export-pipelines`，检查实际动画、骨架、材质及FBX/GLB回读。目标引擎另验；衣物/道具碰撞与接触仍是独立工作。
7. 交付命名本次`diagnostics.json`并说明它只检测指定身体自交，不检测所有足滑、地面/道具碰撞。保留骨骼NPZ、动画、成品工程与必要返工数据，按usage清理无用大缓存。

## 已验证的范围

历史主机（2026-10-30，4080 16GB / 32GB RAM）：5秒30fps真人视频 → 150帧身体动作，约31秒；复用身体追加双手30根手指约12秒；复用到第二个Mixamo角色约3秒。GLB、Blender动作和FBX回读已检查。这是当时单个样例的结果，新角色/视频仍需按[验证边界](../../docs/validation.md)检查。

身体例未发现>1cm自交；手指例第42帧右手/右大腿1.38cm；持剑厚装甲角色有明显碰撞。后两项保留质量限制，不是“所有新角色都自动成片/入游戏”的认证。单目/小手部/遮挡预测没有真实动作捕捉的精确保证。
