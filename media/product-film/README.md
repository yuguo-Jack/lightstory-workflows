# LightStory 产品介绍片

30秒、1920×1080、30fps的可编辑HyperFrames工程。[观看与发布](../../docs/film/README.md)。

## 如何编辑

1. 先读[视觉规范](DESIGN.md)。`shots.json`定义分镜、旁白和时长；`index.html`控制文字、字幕与GSAP时间线；`world.js`定义三维场景和运镜；`assets/`保存必要源素材，`vendor/`保存固定版本运行库与许可。
2. 使用固定版本HyperFrames **0.9.19**。项目已包含可播放的本地依赖包、字体子集和配音配乐，普通预览不需要重新下载模型或安装全部游戏 / 视频生产依赖。
3. 运行`hyperframes preview media/product-film --background`，使用CLI实际返回的Studio地址；保持预览到审阅结束，再用`preview --stop`关闭。可通过`HYPERFRAMES_BROWSER_PATH`选择本机Chrome或Edge，`HYPERFRAMES_CACHE_DIR`把缓存放进工程的`.local/product-video/cache`。
4. 修改HTML后运行下方完整检查、抽帧，查看实际画面，再渲染。音频或旁白发生变化时同步更新字幕和时长。

以下命令在仓库根目录执行，`hyperframes`为已安装的0.9.19 CLI；也可通过`npm exec --package=hyperframes@0.9.19 -- hyperframes ...`使用相同版本。共享CLI和npm缓存遵循本机工具配置，不需要提交`node_modules`。

```powershell
hyperframes check media/product-film --at 1,3,8,12,16,19,24,28 --browser-gpu
hyperframes snapshot media/product-film --at 1,1.98,3,8,12,16,19,24,28 --no-end --output .local/product-video/frames --browser-gpu
hyperframes render media/product-film --output .local/product-video/renders/review.mp4 --fps 30 --workers 2 --crf 20 --gpu --browser-gpu --no-best-effort
```

GPU后端不适用时移除`--gpu` / `--browser-gpu`，依实际硬件校准速度和画面。成片确认后再替换`docs/film/assets/lightstory-intro.mp4`，同步同目录海报和VTT。捕帧、渲染缓存和日志留在`.local`，不要提交中间文件。

## 依赖、声音与字体

| 组件 | 版本 / 来源 | 说明 |
|---|---|---|
| HyperFrames | 0.9.19，Apache-2.0 | 本地外部CLI，未把CLI本体复制到仓库 |
| Three.js | 0.183.0，MIT | `vendor/three.min.js`包含RoundedBoxGeometry、RoomEnvironment，许可在同目录 |
| GSAP | 3.14.2，GreenSock标准免费许可 | 保留分发头部及上游许可链接，**不属于本项目MIT** |
| Noto Sans SC | Google Fonts，SIL OFL | 自托管中文可变字体子集，许可在`assets/FONT-LICENSE.txt` |
| DM Serif Display | Google Fonts，SIL OFL | 自托管英文子集，许可在`assets/DISPLAY-FONT-LICENSE.txt` |
| 中文旁白 | Microsoft Edge TTS，`zh-CN-YunxiNeural` | 本片实际使用的在线合成声音；视频介绍的Ming模型是工程能力，并非本片所用配音引擎 |
| 配乐与三维场景 | 本项目原创 | Python合成配乐及Three.js程序场景，没有第三方影视 / 游戏采样 |

合成音轨`assets/soundtrack.m4a`是必要源素材，已混合旁白与原创配乐。`prepare_audio.py`可用系统Python的`numpy`、`edge-tts`和FFmpeg重新制作；该脚本需要联网合成旁白。分镜中的字幕按句子时长排布，是说明字幕，不冒称逐字强制对齐结果。

重新打包Three.js / GSAP时，按`package.json`固定版本取得依赖，运行`node build-vendor.cjs`；本机共享依赖可通过`NODE_PATH`指定。已经随工程提供可运行包，普通审阅无需重建。`vendor/three-entry.js`保留实际入口，esbuild版本0.28.2。

## 验收与清理

检查覆盖时间线、运行、布局、对比度、音频和转场抽帧；正式成片还要检查编码、时长、完整解码及浏览器播放 / 跳转。当前画面由RTX 4080硬件WebGL捕帧，不要求ComfyUI服务在线。

30秒内的八个章节共用一个WebGL场景与材质，保留内联章节时间线，因此CLI会提示轨道密集和可拆子合成；这些结构建议已审查，未拆成八个重复GPU上下文。布局、对比度、阅读时长和音轨需分别通过。ANGLE的浮点精度驱动提示不作为成功画面的替代证据，仍检查实际抽帧。

确认不再返工后，可清理`.local/product-video/`内的渲染帧缓存、旧版成片、原始WAV混音和下载暂存；保留本目录、正式成片、许可和必要的小型验收记录。`.hyperframes`是本地编辑历史，可按返工需要保留，始终不入Git。
