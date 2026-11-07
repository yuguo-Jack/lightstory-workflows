# 产品介绍

[在线观看](https://yuguo-jack.github.io/lightstory-workflows/film/) · [可编辑源工程](../../media/product-film/README.md)

- `index.html`：播放器。
- `assets/`：正式MP4、海报、字幕和章节。
- 本地：运行`python tools/lightstory.py runtime serve`后，打开 http://127.0.0.1:8192/docs/film/ 。
- 发布：相关文件推送到`main`后自动部署，也可手动运行`Publish product film`。
- 渲染帧、日志和缓存留在忽略的`.local/product-video/`，不放进本站点。
