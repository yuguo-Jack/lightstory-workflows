# Blender、绑定、动作与材质恢复

Blender资产总入口为`blender-core`，第三方模块收纳于`third_party/skills/blender-skills`。真人动作分支由本项目[blender-motion-capture](../skills/blender-motion-capture/SKILL.md)负责；详细输入/质量限制保留在其usage。SkinTokens属于Comfy自动骨架/蒙皮，Motion属于外部真人动作提取，两者职责不同。

## 选择路线

- 常见人形绑定与走跑跳：Mixamo；需要控制器与手工精修可Rigify/Blender。
- 自动生成骨架/蒙皮、既有骨架补权重或权重修复：SkinTokens。改名不保证直接兼容Mixamo动作或UE重定向，需要检查rest、骨轴、层级和形变。
- 真实单人表演复现：Motion2MixamoRig；精确道具/脚底/碰撞仍做Blender或引擎修正。
- 机械、坦克部件、动物、面部/口型、布料与物理：按对象使用Blender/引擎专项，不能把单目人形动作提取当万能动画器。

## Motion后端安装

```powershell
python tools/lightstory.py deps fetch motion2mixamorig
```

将返回的真实路径填入`paths.motion2mixamorig_root`；它在配置的共享tools下。按固定版本README创建独立外部推理环境，此分支的环境要求是使用venv的明确理由，普通宿主辅助脚本继续用系统Python。原主机为Python3.12，复用已有Torch2.11.0+cu128，局部numpy1.26.4/opencv4.11；这组版本是原机证据，不是要求所有平台重装同一CUDA包。

先按上游与GPU平台安装合适Torch，再参考：

```powershell
# 在实际Motion后端根目录执行；不要在ComfyUI或Blender的环境里执行
python -m venv --system-site-packages .venv
.\.venv\Scripts\python.exe -m pip install setuptools wheel
.\.venv\Scripts\python.exe -m pip install "numpy==1.26.4"
.\.venv\Scripts\python.exe -m pip install --no-build-isolation "chumpy==0.70"
.\.venv\Scripts\python.exe -m pip install -e . -c '<LightStory源码>/adapters/motion2mixamorig/constraints-windows.txt'
.\.venv\Scripts\python.exe -m pip check
```

`--system-site-packages`仅在系统已有匹配Torch且希望复用时采用；否则按上游独立安装Torch及依赖。把外部Python绝对路径填到`executables.motion_python`。不得为了满足新分支升级现有Comfy环境。

GVHMR1.6.1原机采用RTMPose资产选择修复，避免无关ViTPose下载。补丁和版本保留于`adapters/motion2mixamorig/patches`；可从仓库运行下述严格上下文工具，先预览再应用：

```powershell
python tools/patch_gvhmr.py --python '<Motion外部Python>' --record-dir '<项目目录>/runtime/patch-record'
python tools/patch_gvhmr.py --python '<Motion外部Python>' --record-dir '<项目目录>/runtime/patch-record' --apply
```

上下文/版本不匹配时保留原文件并审查，不重复硬套补丁。模型checkpoints按`models/weights.lock.json`的motion组来源取得；RTMPose的额外资产由该版本上游依赖管理，首次运行前按doctor核对。手指额外需要HaMeR；不要为试用盲目下载所有可选相机/渲染模型。

## 注册取得的模型和扩展

- [SMPL-X](https://smpl-x.is.tue.mpg.de/)注册下载NPZ包，放`<Motion>/assets/body_models/smplx/SMPLX_NEUTRAL.npz`。
- [MANO](https://mano.is.tue.mpg.de/)注册下载Models & Code，手指使用`<Motion>/assets/body_models/mano/MANO_RIGHT.pkl`，按上游转换要求准备NPZ。
- 这些模型和用户Mixamo资产不随本仓分发，不从第三方网盘替代注册许可。
- 需要Blender面板时按固定Motion仓库`blender_extension/README.md`构建/取得扩展并在Blender中Install from Disk，设置外部Python和后端根目录；不要另建重复C盘运行时。

上游代码Apache许可不覆盖GVHMR、SMPL-X、MANO等全部上游条件。原机此链按研究/原型范围使用；商业生产先核对具体许可，必要时选择Mixamo合法动作或自制动画。

## 使用顺序

先doctor，再用短的固定机位、单人全身视频和合格Mixamo T-pose FBX做身体提取；需要手指时复用身体NPZ与body cache追加；再复用于其他合格rig，逐角色检查接触与变形。

```powershell
& '<Motion外部Python>' -B -X utf8 -m motion2mixamorig.cli doctor --detect-hands
& '.\adapters\motion2mixamorig\run.ps1' -ToolRoot '<Motion后端根目录>' -Python '<Motion外部Python>' -Video '<项目目录>/inputs/motion.mp4' -Rig '<项目目录>/assets/hero.fbx' -OutputDir '<项目目录>/motion/body' -NoPreview
```

追加手指使用新OutputDir并传`-Skeleton '<body目录>/skeleton_motion.npz' -DetectHands`；完整骨骼复用到另一角色时仅更换Rig与OutputDir，不重提取。长片先分段与校准，不承诺任意时长资源稳定。

## Blender交接

导入之前设置源FPS，检查根位移、时间、足滑、手部和道具接触。上游预览GLB只保留简化颜色；最终源资产不能被其覆盖。同顶点编号与对应三角形拓扑时可使用自主`restore_materials.py`恢复原UV/材质；不匹配就回到原成品rig重定向动作，不能近似贴图后声称完整保真。

```powershell
python tools/lightstory.py blender adapters/motion2mixamorig/restore_materials.py -- --motion-glb '<生成GLB>' --source-fbx '<原始FBX>' --out '<项目目录>/motion/textured' --fps 30 --frames 150
```

真实帧率/帧数来自本片，150仅是示例。之后按动画、asset-qa、导出模块检查并回读，目标引擎继续检查。自交诊断不涵盖所有足滑、衣服/道具碰撞和动作自然度。

## 清理

保留模型、许可文件、源FBX/贴图、动作NPZ、最终Blend/FBX/GLB和必要报告；还要追加手指/返工时保留body cache。确认结束后清理项目runtime、重复渲染/解码和工具原生outputs中属于该任务的无用中间文件。不要清空共享weights、body_models或用户原下载。
