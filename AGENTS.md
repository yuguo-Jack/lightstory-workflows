# LightStory维护约定

## 先定位职责

- 制作游戏/视频：按用户目标读取`skills/game-production-workflows`或`skills/video-production-workflows`。单项模型任务直接进入`skills/comfyui-local-workflows`，不强行立整片/游戏项目。
- 修改本工程：先读[架构](docs/architecture.md)、[维护](docs/maintenance.md)和[许可边界](THIRD_PARTY_NOTICES.md)。已授权的任务按范围推进，不把准备请求、进程启动或文件存在当作任务完成。
- 核心方法、用户确认的风格/玩法和质量目标不能因移植或优化被悄悄改写。总流程编排，执行层维护具体配方，避免重复两套操作细节。

## 目录和环境

机器路径用`config/local.json`或`LIGHTSTORY_CONFIG`；公开文件不能重新写入某台机器的私人绝对路径。项目素材、脚本、下载、日志、临时数据和交付统一收纳在用户项目根目录。模型与共享工具保留各自配置的位置。

系统Python负责宿主辅助；Comfy自己的解释器负责GPU节点依赖；Blender原生Python负责bpy；Motion按其独立环境要求执行。不要无关升级已经正常的Torch、模型、驱动或编辑器。

## 修改和检验

- 画布的UI/API、catalog、输入要求、节点来源和模型登记一并维护。替换示例媒体为`UPLOAD_*`，不带入用户素材、嵌入预览和运行状态。
- 优先复用通用画布；具体作品需要特化时另存原生`Projects/<项目ID>/<模型>/<功能>`，不覆盖通用库。能力补充继续按模型/功能归类。
- 第三方按固定版本和独立许可管理；升级先看差异、补丁与受影响验证，不直接修改托管原生插件或混用根MIT。MiniMax官方Skill正文、权重和注册资产外部取得，不加入源码包。
- 常规检查：`python tools/lightstory.py validate`、`python -B -X utf8 -m unittest discover -s tests -v`；画布目录改动后`python tools/build_docs.py`。
- 测试强度随变更范围。静态/隔离检查不算新GPU品质验收，历史成功不算新素材通过；实际内容任务继续看图、试听、播放、资产回读或打包试玩。

## 空间与发布

每批生成、渲染、构建及阶段结束后检查，连续工作至少每2小时检查；临时增长30GiB、累计超过60GiB或磁盘可用不足60GiB提前盘点。制作必需的数据可以保留。模型、用户原件、成品和仍需返工的缓存不能当废弃临时文件删除。

清理前核对真实路径、链接、归属、占用与消费者；仅处理确认无用的任务文件，使用原生LiteralPath命令，先不加Force，尊重策略拒绝。`.lightstory/skills`和外部checkout可能被安装链接依赖，不整目录清空。删除后记录实际可用空间变化。

不得发布local配置、权重、账户凭据、浏览器profile、聊天/完整日志或私人样片。创建远端、上传与push遵从用户当时授权；计划维护账号是`yuguo-Jack`，执行发布前核对真实认证账号，不能仅凭提交署名判断。
