# LightStory 路径与执行入口

在源码仓库完成`config/local.json`，运行`python tools/lightstory.py paths`取得当前路径。安装`python -m pip install -e .`后，在其他项目目录使用`python -m lightstory ...`。`${...}`是文档标记，执行命令前替换成真实路径。

| 标记 | 配置或来源 |
|---|---|
| `LIGHTSTORY_ROOT` | 源码根目录，即`paths`返回的`repository`，也可用同名环境变量指定 |
| `STATE_ROOT` | `paths.state_root`，默认仓库内忽略的`.lightstory` |
| `COMFYUI_ROOT` / `C` | `paths.comfyui_root`；推理解释器是`executables.comfyui_python`，不假设一定在`.venv` |
| 模型 / 输入 / 输出 | `paths.models_root`、`input_root`、`output_root`；三者允许分别存放 |
| `COMFY_SHARED_ROOT` / `S` | 共享目录简称；实际操作以上一行各自解析路径为准 |
| 通用UI / API | UI安装到`paths.workflow_root/<命名空间>/<模型>/<功能>`；API源在仓库`workflows/api` |
| 目录 / 状态 | `workflows/catalog.json`含历史验证状态；当前运行记录自己的请求、history与产物 |
| `SKILLS_ROOT` | 当前客户端Skill目录；完整工程资源用`paths`定位，不假定客户端目录旁有docs或adapters |
| `BLENDER_EXE` / `CAPCUT_EXE` | 配置的可执行文件；插件执行以当前客户端实际连接为准 |
| `MOTION2MIXAMORIG_ROOT` | `paths.motion2mixamorig_root`，独立Motion后端 |
| `MOTION_PYTHON` | `executables.motion_python`，外部动作推理；Blender Python只处理资产/动画 |
| `PROJECTS_ROOT` / `PROJECT_DIR` | 新项目默认根目录 / 本次用户指定项目 |

```powershell
python -m lightstory doctor
python -m lightstory doctor --online --workflow 'Qwen-Image 2.1/01_文生图'
python -m lightstory workflows list --model 'MiniMax H3'
python -m lightstory workflows show 'Qwen-Image 2.1/02_单图编辑'
python -m lightstory workflows prepare 'Qwen-Image 2.1/02_单图编辑' --overrides '<项目绝对路径>/overrides.json' --out '<项目绝对路径>/request.api.json'
python -m lightstory runtime start --profile Balanced --apply
python -m lightstory runtime stop --apply
```

`prepare`只写新请求；按Comfy Skill提交API、记录prompt_id并检查产物。start/stop不加`--apply`仅看计划；有活动队列时先处理任务，不停止其他应用启动的进程。运行临时数据在`state_root/runtime`；项目专用临时数据优先放本项目。

以下链接按源码布局阅读；安装到客户端后，用`paths`返回的`repository`定位全文：[安装](../docs/installation.md)、[插件](../docs/integrations.md)、[动作](../docs/blender-motion.md)、[验证边界](../docs/validation.md)。MiniMax官方Skill按固定依赖获取并组装；Blender模块保留独立许可。插件文件存在不等于当前客户端已连接。
