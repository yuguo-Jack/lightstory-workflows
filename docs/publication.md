# 发布与版本维护

公开仓库：[yuguo-Jack/lightstory-workflows](https://github.com/yuguo-Jack/lightstory-workflows)。发布前检查：

1. 查看差异和实际暂存清单，只收纳源码、可再分发第三方库及许可、去素材画布、依赖锁与文档。
2. 运行`validate`、宿主测试与独立源码安装检查；排除`.local`、`.lightstory`、local配置、权重、用户素材、浏览器/聊天/日志和外部依赖checkout。
3. 核对MIT自主部分、GPL节点、第三方MIT/Apache模块，以及不分发的Community/研究许可材料。
4. 核对当前授权、实际GitHub账号、远端和分支，正常提交推送；提交署名不能代替推送账号验证。
5. 检查远端内容与CI；记录版本、受影响能力和未验证范围。源码检查不提升为GPU或作品品质通过。

依赖升级按[维护顺序](maintenance.md)进行，新的硬件/平台和真实作品分别验收。账户凭据不写入工程或Git历史。
