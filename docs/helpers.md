# 通用检查与维护辅助

这些辅助不提交生成任务。系统Python执行宿主检查，Blender脚本由`lightstory blender`交给原生Blender；真实图像、声音、动画和成片仍需按Skill审查。

GLB结构检查使用宿主NumPy/Pillow/Trimesh；缺少时按需安装`python -m pip install -e ".[asset-checks]"`。这不是给Comfy或Blender重装依赖；媒体检查只需配置现有FFmpeg/ffprobe。

## 媒体与H3执行检查

```powershell
python -m lightstory inspect media '<项目>/delivery/shot.mp4' --decode --out '<项目>/runtime/media-check.json'
python '<工程>/adapters/validation/h3_features.py' --request '<本次api.json>' --history '<本次单项history.json>' --log '<本次后端日志>' --width 1280 --height 720 --out '<新检查记录.json>'
```

`inspect media`用已配置ffprobe读取实际编码/流/尺寸/FPS/时长，`--decode`通过FFmpeg完整CPU解码；不会把技术可读当作内容或无缝运动合格。H3辅助读取保存的真实请求、单项history和日志，发现LoRA未加载、二采/放大回退、无脸跳过、条件桥未执行等情况；它不是美学评分器，也不能证明未覆盖的新节点功能已执行。

## GLB与Blender绑定检查

```powershell
python '<工程>/adapters/comfyui/runtime/inspect_glb.py' --help
python '<工程>/adapters/comfyui/runtime/inspect_rigged_glb.py' --help
python -m lightstory blender '<工程>/adapters/blender/review_rig.py' -- --model '<GLB绝对路径>' --out '<项目>/runtime/rig-review' --motion --fps 30 --frames 150
```

绑定检查组合已有rig/mesh QA、角度/姿态图、FBX导出和回读；需要实际Blender，可能消耗较多时间/内存，只按受影响资产调用。`--generic`是小角度通用烟雾测试，不是人体正确走路；`--motion`审查已有动画。FPS/帧数来自本片，不照抄150。静态模型的常规展示可直接用Blender asset-qa的review_shots和lighting/rendering模块，不沿用旧人物样例机位。

## API/UI编写与前端回读

```powershell
python '<工程>/tools/convert_workflow.py' --api '<任务api.json>' --object-info '<当前object_info.json>' --out '<新的UI.json>'
```

不传`--object-info`时只读当前Comfy接口。底层`adapters/comfyui/graph_tools.py`保留扁平图编写、命名widget读取及裁剪辅助；复杂动态Group、3D控件、前端扩展可能仍需专门布局与适配，生成JSON后必须在实际前端回读，不把转换成功当作已验证。

`adapters/comfyui/frontend/audit.js`是给已连接Playwright page调用的异步函数，第二参数形如`{baseURL:'http://127.0.0.1:8192/',selected:['MiniMax H3/01_文生视频'],strictTimeline:true}`。它从catalog/UI/API取图，核对`graphToPrompt`并恢复原图；不POST`/prompt`。前端/后端和预览服务必须确实运行；JavaScript语法检查不代替真实前端回读。

所有输出写本项目新路径。检查记录中可能含素材路径、提示词和日志，按项目归属保存，不自动放进公开源码。
