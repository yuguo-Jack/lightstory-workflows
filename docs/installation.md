# 分阶段安装

支持目标为有本地GPU工具链的工作站。原实现验证主机是Windows/4080 16GB/32GB RAM；POSIX示例用于可移植配置与宿主脚本，不表示所有GPU依赖已在Linux/macOS测试。先读[许可](models-and-licenses.md)，按实际用途配置所需分支。

各分支最小依赖、Python环境边界和安装排查见[环境分工](environments.md)；不要为仅用一项功能安装整个模型库。

## 1. 宿主辅助入口

克隆[公开仓库](https://github.com/yuguo-Jack/lightstory-workflows)，进入源码目录。按需配置分支，先确保实际使用的能力完整。

```powershell
python --version
python -m pip install -e .
python tools/lightstory.py config init --template windows
```

Python至少3.11。普通宿主工具无第三方运行依赖；Windows保护/安全进程检查用`python -m pip install -e ".[windows]"`，开发检查用`python -m pip install -e ".[dev]"`。不把这些依赖安装到Blender或ComfyUI的Python中。

编辑`config/local.json`。示例的E盘应用/项目与D盘共享tools只是可修改例子，必须填自己的真实目录。没有的可选工具删掉对应字段；不要将示例存在视为已安装。已有配置可用`--config <绝对路径>`或进程环境`LIGHTSTORY_CONFIG`指定；不要提交本机配置。

已有匹配安装可用顶层`dependency_paths`按依赖ID登记真实源码目录；doctor/fetch会校验并复用，版本不符时保留，不替该安装下载、打补丁或重置。默认第三方获取位置仍是共享tools。`installation.workflow_namespace`默认`LightStory`；迁移已有本机模型栏目可显式设为空字符串，避免重复栏目。

```powershell
python tools/lightstory.py paths
python tools/lightstory.py validate
python tools/lightstory.py doctor
```

## 2. Skill与第三方方法

默认安装7个自主/本地适配Skill和22个MIT Blender模块。安装以目录链接复用本仓库；既有同名不同内容会返回冲突，用户可先选隔离`--target`审阅，不覆盖原件。

```powershell
python tools/lightstory.py install skills --agent codex
python tools/lightstory.py install skills --agent codex --apply
# 或：--agent claude
```

Windows目录符号链接需要系统允许。也可显式选择`--copy --apply`进行内容复制；复制模式后续不会自动同步，更新前自行对比旧文件。仅复制不会复制Codex插件或MCP配置。安装后新开代理会话，按名称指定总入口。

需要MiniMax官方9个类型/提示词Skill时，阅读其README指向的许可证，再获取固定源码并安装组合：

```powershell
python tools/lightstory.py deps fetch minimax-h3-skills --acknowledge-license
python tools/lightstory.py install skills --agent codex --with-upstream
python tools/lightstory.py install skills --agent codex --with-upstream --apply
```

外部源码保存在配置的共享tools目录，组装后的本地Skill在`state_root/skills`。官方创作正文保持上游版本，本项目仅前置运行映射并适配元数据。MiniMax材料有独立Community条款，不当作MIT内容向全球捆绑分发。只做游戏方法、已有素材剪辑或CG时可不安装该分支。

## 3. ComfyUI与节点

使用已有ComfyUI或按[官方仓库](https://github.com/Comfy-Org/ComfyUI)安装；原库源码基线为`426f5eea52a7ece1dd599fff4cb6cd1f352ddd24`。配置其根目录、实际Python、模型、input/output和当前用户workflows目录。显存、CUDA、Torch、驱动和3D扩展必须匹配该安装；不要为了本工程把正常Comfy环境的Torch盲目重装。

`config/local.json`配置LightStory辅助工具，不会自动改写Comfy Desktop设置。由本工程启动器启动时会传入模型、输入、输出及temp目录；若继续用Desktop或其他启动器，要在其设置/模型路径配置中指向同一批目录。已有后端只复用，不会因为改了本工程配置就在线切换路径。用当前模型选择器、`object_info`与实际产物确认一致，避免重复启动同一安装。

按需取节点源码；全功能组合包括：

```powershell
python tools/lightstory.py deps fetch h3-director
python tools/lightstory.py deps fetch ming-tts
python tools/lightstory.py deps fetch skintokens
python tools/lightstory.py deps fetch crossview-warp
python tools/lightstory.py deps fetch viggle-loader --acknowledge-license
python tools/lightstory.py install nodes
python tools/lightstory.py install nodes --apply
```

`deps fetch`固定提交并检查/应用本仓库登记补丁；已有不同版本或无关修改会保留并报错。`install nodes`链接两个自主节点及已取到的第三方节点，返回`not_fetched`清单；这个清单非空时相关能力仍缺依赖。无运行服务时完成安装，再按需重启匹配后端。

新取得的托管checkout显式使用LF换行；补丁文件、固定基线及补丁后文件哈希共同核对。已有自改checkout不会被重置来强行完成安装。

节点依赖在**配置的ComfyUI Python**安装。Ming声明复用原生依赖；SkinTokens按其固定`requirements.txt`安装，当前实现不要求bpy/Blender/强制flash-attn；CrossView按其README配置深度/几何链；Director按其README确认视频编码与原生H3节点。升级前保留现有Torch/Transformers约束并执行目标环境`pip check`，不在宿主Python安装整套Comfy推理环境。

## 4. 模型与画布

模型不随Git分发。优先按单个工作流选择，不自动下载整库：

```powershell
python tools/lightstory.py models plan --workflow 'Qwen-Image 2.1/01_文生图'
python tools/lightstory.py models check --workflow 'Qwen-Image 2.1/01_文生图'
python tools/lightstory.py models fetch --workflow 'Qwen-Image 2.1/01_文生图' --acknowledge-license
python tools/lightstory.py models check --workflow 'Qwen-Image 2.1/01_文生图' --hash
python tools/lightstory.py install workflows
python tools/lightstory.py install workflows --apply
```

权重放配置的原生models目录，完成前使用同目录`.part`，完成后检查大小和SHA256。受限/登录源不能匿名取得时按发布者方式手动放置，再用`check --hash`核对；不索要或存储浏览器cookie/令牌。Next-Scene兼容文件由同一下载入口从已校验原件生成，不另发一份数百MB转换权重。SMPL-X/MANO等注册许可模型按[动作安装](blender-motion.md)由使用者自行取得。

画布默认安装到原生工作流的`LightStory/<模型>/<功能>`，避免与既有库重名；API留本仓库用于程序调用。`UPLOAD_*`为明确待上传输入，不伪造示例文件。打开画布后用自己的图片、视频、声音、蒙版或GLB替换每个占位项。复杂Director Group/时间线中的素材也要同步绑定。

UI使用可编辑原生副本，`state_root/installed/workflows.json`登记维护源和哈希；日常换素材不会直接改公开模板。真正改通用流程时再按维护步骤导出/审阅回仓库。Skill和自主节点可使用目录链接同步维护。

```powershell
python tools/lightstory.py runtime start --profile Balanced
python tools/lightstory.py runtime start --profile Balanced --apply
python tools/lightstory.py doctor --online --workflow 'Qwen-Image 2.1/01_文生图'
```

原机Qwen五参考用Conservative、一般H3/音频/绑定用Balanced、原Pixal回归有PixalStable记录；具体输入先小规模校准。启动器会检查所选版本支持的参数；不支持时报告，不能默默删掉保护参数再宣称配置相同。已有后端仅复用，不在线切配置。Desktop自行启动不自动包含本保护器配置。

## 5. Blender、游戏引擎、剪辑与动作

- Blender配置可执行文件，`python tools/lightstory.py blender --which`仅查路径；实际资产操作按`blender-core`选择模块。原记录5.2.2 LTS；不同版本按其API复核。
- Web、Unreal、CapCut等客户端插件按[集成说明](integrations.md)安装并验证真实工具，不由本项目复制托管插件源码。
- Mixamo需要Adobe账号与用户交互；普通动作可用其动作库。角色适配、接触、服饰、碰撞和运行端验收仍独立进行。
- Motion2MixamoRig后端和Blender扩展按[专门说明](blender-motion.md)配置，包含许可模型、外部Python、GVHMR补丁、手指与材质恢复的顺序。

## 安装完成的含义

`validate`证明发布包结构、脚本语法、版本/哈希登记等成立；`doctor`报告配置和工具状态；`doctor --online`才核对运行Comfy接口。代表素材实际推理、逐项内容检查、Blender/引擎回读、整片播放或打包试玩分别留证。未做的项保留未验证状态，不能用原机历史通过代替新安装验收。
