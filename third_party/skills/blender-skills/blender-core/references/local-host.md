# 本机入口与使用

## 从一个入口调用

在 Codex 中使用 `$blender-core`，后面说明输入文件、期望结果、目标引擎和输出目录。这个入口会按任务读取同目录下的专门技能；用户无需记住 22 个模块名。

例如：`$blender-core 检查这个 GLB 的网格、UV 和材质，给出适合 UE 的处理建议，先保留原文件。`

建模、绑定、动画、材质或导出任务都可从这个入口开始。多阶段任务再读取 `blender-workflow-recipes`；只做材质连接时不必跑完整角色制作流程。

## 执行环境

- 本机 Blender：`${BLENDER_EXE}`。
- 启动器：本技能的 `scripts/run_in_blender.py`，由 PATH 上的系统 `python` 启动。
- 路径从LightStory统一`config/local.json`读取，无需修改全局PATH；旧独立`local_runtime.json`仅作兼容回退。显式 `BLENDER_EXE` 环境变量仍优先，便于换用其他版本。
- 先执行启动器 `--which`，再通过启动器运行 `scripts/env_report.py` 确认版本与可用插件。示例：

```powershell
python -X utf8 '${SKILLS_ROOT}\blender-core\scripts\run_in_blender.py' --which
python -X utf8 '${SKILLS_ROOT}\blender-core\scripts\run_in_blender.py' '${SKILLS_ROOT}\blender-core\scripts\env_report.py'
```

优先在任务副本上处理用户指定的文件，输出放用户指定的项目目录；中间文件收纳于该任务目录的临时子目录。后台启动使用独立进程，不会接管用户当前打开但未保存的 Blender 场景。只有明确可用的 Blender MCP 连接才按现场编辑模式执行，不假定 MCP 已部署。

## 与本机现有流程衔接

- 需要生成图片或静态模型时，调用已有 `$comfyui-local-workflows`，按需读取其中的 Qwen/Pixal3D 参考，再将合格 GLB 导入 Blender。
- SkinTokens已通过`$comfyui-local-workflows`部署，需自动骨架/蒙皮或重算既有权重时读其`references/skintokens.md`；不重复安装StableGen或另一套模型环境。普通人形仍可选Mixamo，需控制器/精修可选Rigify。
- 真人视频到动作由本入口调用本机新增`blender-motion-capture`，其安装路径、CLI/面板、材质保留、FPS、局限与清理都在专用Skill。它使用外部Python；Blender自带bpy可用，无需把Torch/GVHMR装进Blender。
- Rigify 的 `--fit` 只缩放、居中 metarig，不是自动定位全部关节。ARKit 脚本建立的是空的命名形态键，实际表情还需制作和检查。
- 本机 Pixal3D 模型常为 350k/600k 三角面。QA 的默认 300k 门槛会跳过部分重检查；保留跳过记录，按部件或对优化副本检查，不能把未执行的检查算作通过。
- 操作规范不等于所有资产已达到生产质量。按本次实际任务检查网格、材质、动画及导入结果；安装验证不代表 UE/Mixamo 全链已验收。
- 任务结束清理本次不再需要的临时文件，保留原始输入、最终资产和仍需返工的缓存；不清空共享模型或其他任务目录。

## 安装来源与维护

上游：`https://github.com/EL4CTEO/blender-skills`。
安装提交：`71d031dab8bc6729504d11a78cbe91945401045f`，包含 22 个技能。
原22个上游技能之外，本机新增`blender-motion-capture`，仍以`blender-core`为统一入口。本机改动包括路径/入口说明，以及`blender-character-rigging/scripts/rig_check.py`对bpy集合不支持步长切片的兼容修复；不是另写一套绑定算法。上游`compatibility`已移入Codex支持的metadata。更新时保留本机配置和补丁，并核对接口。

安装与基础运行证据：`${HISTORY_ROOT}\maintenance\2026-10-30\blender-skills-install`。该目录仅为安装记录，不是所有新任务必须使用的工作目录。
