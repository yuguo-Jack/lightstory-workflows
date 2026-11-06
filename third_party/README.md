# 第三方库管理

两种形式：

1. **小型、允许再分发且有本地适配的源码快照**：Blender Skills保存在`skills/blender-skills`，来源、固定提交、LICENSE和本地改动明确，按第三方库维护。
2. **大型、运行环境独立或条款需要单独取得的上游**：记录于`dependencies.lock.json`，用`deps fetch <id>`按提交获取到配置的共享tools；节点通过原生custom_nodes链接使用。MiniMax类型Skill获取后在本地套用自写overlay，不向公开包混入官方正文。

`patches`只适用于清单固定基线。获取时检查原文SHA和`git apply --check`，已应用同一patch时跳过，遇到无关修改不覆盖。更新提交后重新审查patch和受影响功能；不通过把分支名改成main自动更新。

共享依赖、源码checkout、虚拟环境和权重不是每次生成都应删除的任务缓存。依赖许可、模型许可和客户程序插件条款分别维护，见根目录THIRD_PARTY_NOTICES。
