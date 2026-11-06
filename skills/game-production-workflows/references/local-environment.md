# 本机工具与执行入口

先按[运行路线](runtime-selection.md)选择执行层。本文件的UE/MCP探测和原生引擎要求适用于Unreal分支；Web实际调用Game Studio检查其代码、依赖、构建与试玩，素材需要时再使用本机ComfyUI/Blender。不为Web项目启动UE或创建原生工程。

初始环境核对：2026-10-30；流程职责复核：2026-11-02。以下安装记录不等于当前进程/连接状态，执行前以当前探测、引擎版本和实际只读调用为准。

## 快速探测

```powershell
python -m lightstory doctor
```

具体UE项目可使用本Skill的`scripts/probe_local.py --project '<项目绝对路径>/Game.uproject'`，特殊引擎安装增加`--engine-root`；这些参数属于该脚本，不属于`lightstory doctor`。探测不启动UE、Blender或生成任务，不修改服务和工程；可显式用`--output`写到一个新的项目记录文件。安装存在、历史验收和当前连接状态是不同证据。

| 工具 | 位置/入口 | 当前证据与边界 |
|---|---|---|
| UE 5.8.3（原主机记录） | 配置中的`executables.unreal_editor` | 原主机发现编辑器、Build.version、模板和原生工具插件；新安装须核对版本和实际连接 |
| UE 操作技能 | 用户选定 Unreal Engine Skills for Codex → `unreal-mcp` | 已安装技能与操作文档；本会话工具目录及实际调用决定能否操作 |
| Blender 5.2.2 LTS | `${BLENDER_EXE}`，`$blender-core` | 专项模块以blender-core当前路由为准；基础启动、网格检查和FBX回读有记录，不是所有生产功能已验收 |
| ComfyUI模型执行 | [ComfyUI Local Workflows](../../comfyui-local-workflows/SKILL.md) | 模型、接口、输入输出、启动/保护及实时目录只在其[运行参考](../../comfyui-local-workflows/references/runtime.md)维护；历史通过不是本次资产合格 |
| Mixamo | Adobe免费在线服务 | 按用户选择使用，检查登录、素材许可和角色适配性 |
| 系统工具 | PATH上的Python、Node、Git、Git LFS | 按所选分支定位；UE的C++ Build Tools与SDK按引擎/项目要求检查 |

硬件记录为RTX 4080 16GB、RAM约32GB；初始探测时D盘分页已分配64GiB，执行前查真实物理内存/提交/显存余量，不把历史配置当当前值。分页不是等速物理内存或显存。游戏性能测试时避免无关生成重任务，不能用带着Comfy推理的帧率代表玩家性能。

## 本机命令行与 Python 工具

可按任务使用本机命令行程序、Python 库和自编脚本，工具范围不限于上表或已列出的技能/插件。例如 FFmpeg/ffprobe 可处理游戏视频、音频、抽帧和序列图；Python 可做图像/网格预处理、资产清单、批量转换、检查和本地 API 自动化；构建、导入和测试使用所选项目的实际工具。简单确定性处理可直接执行，按能力和结果选择方法。

先核对路径、版本、帮助或已安装库接口。普通 Python 工作优先 PATH 上的系统 `python`；缺包按全局规则先用 `python -m pip install <package>` 安装到同一环境。只有用户指定、仓库要求或系统环境实际无法完成时才改用其他环境并说明原因；引擎/Blender 内部脚本及 Comfy 推理使用各自正式运行环境。

新增非Python共享工具和包缓存放配置的`tools_root`（Windows示例`D:/codex/tools`），任务脚本、中间文件与日志归本项目。保留源资产并验证目标端读取；按[空间管理](project-operations.md)清理。可用工具增加不扩大上传、收费、发布或删除权限，也不授权无关环境升级。

## UE MCP

在当前代理客户端的插件目录中发现`unreal-engine-skills-for-codex`的`unreal-mcp`入口；原主机参考版本为0.1.7。配置和连接不随Skill文件迁移，按[工程集成说明](../../../docs/integrations.md)配置，避免固定某个用户目录或缓存版本。

1. 核对 `.uproject`、对应引擎、当前编辑器和未保存状态；使用用户指定或已确认项目，不连到另一个项目。
2. 按 `unreal-mcp` 发现工具集、读取实际参数再调用，不能照文档臆造本会话工具。
3. 服务器/工具集、当前端点和代理按`unreal-mcp`的setup/operations及本机实际配置核对，不在本总流程固定端口或私有调用字段。
4. Codex 插件自带连接时优先复用，不增加重复直连/代理。按其 setup/operations 恢复；代理在线、缓存工具或端口打开都不证明 UE 调用成功。
5. 用只读调用确认项目/关卡可读取，再改动。已有项目注册的相关Agent Skill按`unreal-mcp`读取并遵从；协调编译、PIE与对象操作，依赖变更串行。

插件的`unreal-skill`用于创建/维护UE内部Agent Skill，不是普通工程制作的必经步骤，也不是本机Codex总Skill的编辑入口；本次维护不创建UAsset或连接编辑器。

没有 MCP 时继续独立工作，并在已安装引擎支持范围内使用编辑器 Python、命令行导入/构建/测试替代。Python 用来制作工程和编辑资源，**不当作打包后玩法脚本**。缺连接时保留准确状态，不把脚本文本当成已生成 UAsset。

## 生成和渲染调度

- 从当前 ComfyUI 技能 runtime/cleanup 读取 API、配置和输入；先查队列、模型、余量，不自动使用旧验证素材。
- 同时只执行一个重 GPU 阶段，避免 Pixal/Qwen/H3、Cycles、UE 高负载运行或材质编译互相挤占资源。任务结束或 `/free` 不表示物理驻留页/磁盘缓存全部释放。
- Comfy由执行技能按当前模型参考选择启动配置/注意力/内存处理，保留保护，不在本总流程另维护档位配方。
- Blender经`blender-core`选择当前运行器/接口，后台处理指定文件副本，不接管GUI中未保存场景。
- Rigify可发现，具体metarig、蒙皮和动作仍按角色检查；SkinTokens和Motion2MixamoRig经已有ComfyUI/Blender技能按场景选用。StableGen、UniRig不是前提，不自动安装。

锁定项目UE版本与插件，记录实际接口与参数，不为“最新版”中途升级正常环境。普通脚本用系统Python；共享工具用`tools_root`，引擎、Skill和模型保留各自管理位置。

已有工程的 `EngineAssociation` 与找到的引擎不匹配时，先定位兼容版本或准备可回退的迁移方案，不直接用5.8打开旧工程并默默升级。
