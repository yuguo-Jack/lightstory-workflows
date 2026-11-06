# 产品介绍视频

30秒、1920×1080、30fps，中文旁白、画内字幕与128BPM原创电子配乐。V2重新编排23个三维镜头段，包含装配、近景、俯视、环绕与节拍转场。三维场景由HyperFrames、Three.js和GSAP制作，使用可寻址时间线，源工程见[media/product-film](../../media/product-film/README.md)。

## 本地观看

在仓库根目录运行：

```powershell
python tools/lightstory.py runtime serve
```

打开 http://127.0.0.1:8192/docs/film/ ，可播放、全屏及按章节跳转。也可直接用本机播放器打开本目录的`lightstory-intro.mp4`。HTTP预览更适合字幕轨和章节载入。

## GitHub首页观看入口

README的海报和“观看产品介绍”均直接打开公开播放器：

https://yuguo-jack.github.io/lightstory-workflows/film/

维护者更新时，先审阅成片并检查本目录文件，再提交和推送，随后手动运行`Publish product film`工作流。首次部署需在GitHub仓库的Settings → Pages选择GitHub Actions。工作流只发布本目录的播放器、MP4、海报与字幕，不发布机器配置、源工程缓存、历史验证素材或整个仓库。没有定时或自动推送触发的发布。

GitHub的Markdown不执行HTML播放器，因此首页使用海报观看入口，网页使用原生`video`播放。后续替换视频需同步海报、VTT字幕 / 章节和HTML中的时长、说明；保持此观看地址不变。

## 文件归属

- `index.html`、`lightstory-intro.mp4`、`poster.jpg`、`chapters.vtt`、`captions.vtt`：正式交付内容，供公开观看；MP4是明确允许的产品宣传片，不是私人验证素材。
- 本片三维画面是流程示意，不是模型推理或完整游戏的运行录像；模型能力和81组画布验证范围以工程文档为准。
- 临时渲染帧、音频中间件、捕帧、日志、浏览器缓存位于忽略的`.local/product-video/`和源工程`.hyperframes/`，不应提交。
