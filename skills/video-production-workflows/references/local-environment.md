# 本机能力与入口



核对：2026-11-02。此表记录安装与历史证据；每次执行以实时目录、接口和输出为准。



| 环节 | 当前入口 | 选择及边界 |

|---|---|---|

| ComfyUI模型执行 | `$comfyui-local-workflows` | 图像、视频、3D、绑定、配音、配乐的目录、参数、运行与模型产物检查；总数/状态查实时catalog，单项成功不是整片品质保证 |

| 造型/美术/关键帧 | Qwen-Image 2.1 INT8 | 概念/角色/场景/道具定稿、色光样张、逐镜关键帧、静帧修复、合成素材；见[视觉开发](image-development.md) |

| 视频 | MiniMax H3 导演台及原生专用链 | 常规/Turbo、Flex、专项及Fun结构控制；家族、采样、兼容与真实验证范围由Comfy执行参考维护 |

| 配音 | Ming-3.0-TTS Tiny INT8 | 内置、设计音色、参考音色、表演、多角色；试听才判断音色和情绪 |

| 配乐/演唱 | MiniMax Music 3 INT8 | 纯音乐或歌词歌曲；不是精准拟音器，也非无限无缝配乐系统 |

| 白模预演/CG | Blender 5.2.2 LTS，`$blender-core` | 相机、布景、动作、灯光、渲染/合成；按需加载 animation/rendering/simulation 等模块 |

| 本地剪辑 | `${CAPCUT_EXE}` | 配置后核对安装与桌面控制能力；不假定存在本地草稿写入API |

| CapCut 云剪辑 | CapCut 插件 | 可上传、组装、字幕、素材、STDraft 协作保存；不等于编辑桌面草稿或已经导出 |

| 技术处理 | PATH 上 `ffmpeg` / `ffprobe` | 代理、转码、抽帧、波形/响度检查、确定性拼接；实际配置以本机帮助为准 |



## 正式入口与位置



- ComfyUI路径、实例、原生UI/API/输入输出、启动器、保护器及验收索引以执行技能的[运行参考](../../comfyui-local-workflows/references/runtime.md)和实时配置为准，本总流程不另维护一套路径/启动配置。

- 需要时从执行入口查询；不为读取文档或只做剪辑/CG启动模型服务。

- Blender：`${BLENDER_EXE}`；辅助运行器 `${SKILLS_ROOT}/blender-core/scripts/run_in_blender.py`。

- 普通辅助脚本用PATH系统Python；Comfy推理由配置的`executables.comfyui_python`执行，不将日常辅助脚本塞入其环境。



查询示例（不提交推理）：



```powershell

python -m lightstory workflows status

python -m lightstory workflows list --model 'MiniMax H3'

```



由Comfy执行技能据当前目录选择实际模板并生成项目内任务副本，再完成提交、等待与单项产物检查；本总流程接收真实结果。准确命名来自目录，不凭本文猜节点ID或API字段。



## 本机命令行与 Python 工具



按具体任务使用本机可用的命令行程序、Python 库和自编脚本；表中工具是常用入口，其他合适工具也可使用。例如用 FFmpeg/ffprobe 做转码、抽帧、代理、音视频处理和探测，用 Python 做图像/音频批处理、分镜时长计算、文件组织或调用本地 API。简单确定性处理可直接完成；涉及交互式剪辑或专有工程时使用对应编辑器/插件。



先确认可执行路径、版本及所需能力，参数不明确时查本机 `--help` 或已安装库接口。普通 Python 工作优先 PATH 上的系统 `python`；缺包按全局规则先用 `python -m pip install <package>` 安装到同一环境。只有用户指定、仓库要求或系统环境实际无法完成时使用其他环境并说明原因；Blender 内部 API 与 Comfy 推理沿用各自正式运行环境。



必要的新非Python共享工具及包缓存放配置的`tools_root`（Windows示例`D:/codex/tools`）；不改动无关的模型、Comfy依赖或共享工具。任务脚本、转换中间文件和日志归本项目，按[空间管理](project-operations.md)清理。保留输入原件，验证实际媒体与工程；工具可用范围不扩大上传、收费、发布或删除权限。



## 资源调度



配方资源基准是RTX4080 16GB、RAM32GB；其他配置先做代表输入校准。实际分页、物理内存、提交余量、显存和启动配置现场检查，不复制历史数值作当前状态。



本总流程统一排重GPU阶段，避免模型推理、Cycles渲染及UE互相挤占；Comfy具体启动档位、内存保护与回收由执行技能负责，Blender等按自己的运行参考处理。释放模型与清理磁盘是不同操作，继续下一重任务前仍需检查实际资源。



各执行技能复用确认归属的现有实例，按各自规则处理队列和恢复，不打断用户任务。缺工具时先查看当前插件目录，不因技能里列过名字就宣称连接正常。
