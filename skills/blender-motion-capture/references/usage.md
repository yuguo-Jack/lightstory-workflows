# Motion2MixamoRig 本机使用

## 已安装环境

- 工具/权重/许可模型：`${MOTION2MIXAMORIG_ROOT}`，版本0.1.8、上游提交`f05a718188026b06e7ee64b47bab077970444b19`。
- 外部Python：上述目录`.venv/Scripts/python.exe`，3.12；复用系统torch2.11.0+cu128，局部numpy1.26/opencv4.11，隔离于ComfyUI与Blender Python。
- Blender5.2.2的扩展`bl_ext.user_default.motion2mixamorig`已安装、启用并配置好外部Python和工具目录。入口：3D视图 → N面板 → Motion2MixamoRig；⚙展开Setup，Advanced可核对路径。不要再次点One-click安装而另建C盘环境。
- Advanced的Project Directory是后端根目录，不是任意新项目目录。当前上游面板把任务写入该目录的`outputs/blender_jobs/<job-id>`；需要资料统一放项目工作目录时优先用下述CLI显式指定OutputDir。不要为改输出路径搬走模型/运行时；面板任务按job-id盘点和清理。
- `assets/body_models/smplx/SMPLX_NEUTRAL.npz`与`mano/MANO_RIGHT.pkl`由用户从官网注册取得，MANO的NPZ转换已完成。不要请求账号、cookie，不从非授权位置补许可模型。
- `weights`包含GVHMR、HMR2、YOLO、RTMPose及HaMeR；手部从作者官方HF Space只取所需两份文件，未下载6GB整包。当前RTMPose在CPU上运行，HMR2/HaMeR用CUDA。已登记权重的来源、目标与SHA256统一见工程[模型登记](../../../models/weights.lock.json)；本机历史校验与新环境验收的区别见[验证说明](../../../docs/validation.md)。

仓库要求独立外部运行环境，因此这里使用其venv；普通辅助/启动脚本仍用系统Python。不要对正常环境泛化重装pip/torch或向ComfyUI环境安装Motion依赖。

## 输入准备

1. 有使用权的真实单人全身视频，人物和双脚尽量可见，避免切镜、严重运动模糊、遮挡和近距离大幅透视。小背景人物也可能触发多人预检，先做不截断肢体的裁剪；不要关闭预检硬吃群舞。
2. 先记录/统一真实FPS；可用FFmpeg转普通MP4/CFR，保留原片和转换记录。5秒30fps150帧是实测规模，不是任意时长的资源承诺。长片按可复用动作分段并留合理衔接上下文，检查根位移、速度与首尾，不直接硬拼曲线。
3. 本工具当前提取路径固定使用静止相机假设。明显移动相机先稳定/改选素材或单独评估GVHMR高级相机路线；现有安装不代表那些附加模型也已部署。没有相机标定时深度/尺度是推测，不能当物理测量。
4. 目标为合格Mixamo二进制FBX、T-pose、完整人形骨架，常见`mixamorig:*`命名。静态PixalGLB先经绑定/返工；Rigify控制rig、动物rig、仅改成Mixamo名字的SkinTokens骨架不能默认直接兼容，先比对骨层级、骨轴和rest校验。
5. 需要手指时手应足够大、清楚；HaMeR有效标志不代表每个手指与真实表演完全一致。握剑/拿杯要明确握点、道具尺寸与接触方向，不能只套一段拿网球拍的视频。

## CLI：身体 → 手指 → 多角色复用

新任务在自己的项目目录，以下`${PROJECT_DIR}`仅是示例，先替换为真实路径。启动前按ComfyUI runtime检查队列和实际内存，重GPU阶段与Comfy/Blender渲染串行。空闲Comfy可`/free`，不要结束用户应用或关闭保护。D盘分页已实际扩至64GiB，仍不能代替显存/物理RAM。

环境检查（doctor检查工具默认assets目录；实际run使用显式路径）：

```powershell
& '${MOTION2MIXAMORIG_ROOT}\.venv\Scripts\python.exe' -B -X utf8 -m motion2mixamorig.cli doctor --detect-hands
```

身体动作，工程`adapters/motion2mixamorig/run.ps1`会把本次TEMP、绘图/YOLO配置放进该输出的`runtime`，公共权重仍在工具目录：

```powershell
& '${LIGHTSTORY_ROOT}\adapters\motion2mixamorig\run.ps1' -ToolRoot '${MOTION2MIXAMORIG_ROOT}' -Python '${MOTION_PYTHON}' -Video '${PROJECT_DIR}\inputs\motion.mp4' -Rig '${PROJECT_DIR}\assets\hero_tpose.fbx' -OutputDir '${PROJECT_DIR}\motion\body' -NoPreview
```

追加手指，复用body骨骼与其旁边body cache，不再提取身体：

```powershell
& '${LIGHTSTORY_ROOT}\adapters\motion2mixamorig\run.ps1' -ToolRoot '${MOTION2MIXAMORIG_ROOT}' -Python '${MOTION_PYTHON}' -Video '${PROJECT_DIR}\inputs\motion.mp4' -Rig '${PROJECT_DIR}\assets\hero_tpose.fbx' -OutputDir '${PROJECT_DIR}\motion\hands' -Skeleton '${PROJECT_DIR}\motion\body\skeleton_motion.npz' -DetectHands -NoPreview
```

多角色：再用`-Skeleton .../hands/skeleton_motion.npz`换另一个`-Rig`和新输出目录；已有完整手指数据无需再加`-DetectHands`。同一时间只跑一个重阶段，先一个代表性rig验好再批量。每个新角色的碰撞和接触仍需单独检查。

`-NoPreview`只跳过原工具渲染，仍输出动画；不要把打印的`videos`路径当已存在预览。默认脚锁/地面修正开启；它们是后处理，检查实际效果，不一概关掉或宣称完全消除足滑。

## 输出、Blender 与材质

- `skeleton_motion.npz`：可复用身体/手指数据、FPS、时间戳、foot contact等；通常很小，作为动作源保留。
- `mixamo_rotations.npz`：对应rig的通道，四元数顺序 **wxyz**；别直接当glTF的xyzw。只按名字复制给另一套骨轴可能错误，必要时用Blender重定向与参考姿势校准。
- `mixamo_character.glb`：蒙皮+动画，原工具只写简化颜色，不保留完整UV/贴图/表情。它适合预览和动作交接，不能拿它覆盖已有精修成品资产。
- `run.json`、`progress.jsonl`、`diagnostics.json`：实际输入、执行和质量报告。自交报告不含全部足滑、地面、道具/环境碰撞，`also_in_rest_pose`表示原静态造型就存在的重叠。

Blender导入**之前**设置FPS，再导入GLB。扩展的Import Generated Character已按此顺序实现。人工导入也如此：30fps150帧应是0..149；先按24fps导入再改30fps会把动作压到119.2帧，不能靠多添结尾帧掩盖。导入器Icosphere是骨骼显示辅助物，隐藏/识别custom_shape，不把它输出成角色网格。

源FBX与输出完全同顶点编号、面拓扑时，可恢复原UV和材质而不重新生成。用`blender-core`启动器执行已验证脚本：

```powershell
python -m lightstory blender '${LIGHTSTORY_ROOT}\adapters\motion2mixamorig\restore_materials.py' -- --motion-glb '${PROJECT_DIR}\motion\hands\mixamo_character.glb' --source-fbx '${PROJECT_DIR}\assets\hero_tpose.fbx' --out '${PROJECT_DIR}\motion\textured' --fps 30 --frames 150
```

该脚本检查同顶点编号、每个FBX原面按上游同样方式三角化后逐三角形一一对应，按每面顶点号恢复UV/材质槽，打包纹理，输出`textured-motion.blend`和`.glb`。因此支持保持顶点身份的四边面转三角面，不要求源FBX本来全是三角面。Maria例实际保留三张2K贴图；YBot恢复原UV和纯色材质，本身没有纹理图。不匹配会拒绝，不做近似投影；这种情况回到原最终资产上做动作重定向。面部形态键/控制器等也应保留原成品资产另接，不能指望预览GLB带回它们。

后续按`blender-animation`做必要的足滑、根运动、手腕/握点、接触与循环修整；再按asset-qa、export-pipelines导出并回读，目标引擎另测。重定向只解决动作映射，不自动解决不同身材、装甲、长裙或长武器的安全空间。

## 已知质量与失败处理

- 本次身体例150帧无>1cm身体自交；追加手指后第42帧右手/大腿1.38cm。厚肩甲/持长剑的第二角色123帧触发自交，最大14.84cm，部分头/肩重叠在静态就存在。技术复用成功不等于该持剑动作可以直接交付。
- 修正时按原质量报告和用户/项目目标定位帧段，保留原版；Blender/UE中调整握点、IK、动作覆盖及身体接触。不要删报告、忽略武器或改阈值把失败变成通过。具体动作返工按授权进行，不因一次验证擅自重写用户表演。
- 多人拒绝：换单人镜头/裁剪；模型错包：核对SMPL-X NPZ与MANO；缺手指：检查手部大小和MANO/HaMeR；缺参考缓存：恢复对应body cache或只重做必要提取。
- 相机移动、焦距未知或根轨迹不对：固定机位/标定/稳定、局部修正或改用可控动画；当前CLI不等于已验过所有GVHMR相机后端。
- 内存/显存不足：新任务监控外部Motion进程的RAM、提交和显存；ComfyUI的保护器只管其后端，不能替外部进程兜底。先短片、串行、释放空闲模型；保持桌面余量，别让浏览器一起失去响应。本次手指阶段最低可用RAM约7.34GiB，采样全卡峰值6641MiB，含其他应用且可能漏过瞬时峰。
- 环境更新：当前gvhmr1.6.1做了小型依赖选择修复，RTMPose模式不再误下载无用ViTPose。更新包后核对本机补丁、doctor与真实短片，不沿用旧通过结论。安装/补丁证据在管理目录maintenance的rigging-motion-install。

## 清理与许可

沿用项目总Skill的每批/阶段及至少每2小时检查；临时增长30GiB、累计60GiB或磁盘可用不足60GiB提前盘点。必要增长可保留，阈值不是删除上限。

需要追加手指或只返工某段时，保留相应body cache和原输入；已有完整手指骨骼且不再重提取时，可清理`cache`内分阶段中间张量/重复解码视频、任务`runtime`、无用渲染序列/重复GLB与`.blend1`。保留模型、许可文件、源FBX/贴图、动作NPZ、成品Blend/GLB/FBX、必要日志/报告及待返工数据。覆盖项目和工具原生`outputs`、临时目录，但只删归属明确的本次数据；不要清空tools/weights、body_models、共享缓存或用户原始下载。

授权以[项目NOTICE](https://github.com/MaxLiu22/Motion2MixamoRig/blob/main/NOTICE.md)及GVHMR、SMPL-X、MANO条款为准；自身开源代码不代表整条链已获得商业授权。商业项目先选符合授权的动作源。
