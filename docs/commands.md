# 工程命令参考

源码目录使用`python tools/lightstory.py ...`；完成editable安装后，在任意项目目录使用`python -m lightstory ...`。两者进入同一实现。每个命令可用`--help`查看实际参数，全局`--config <配置路径>`放在子命令之前。

| 命令 | 用途 | 写入或实际执行边界 |
|---|---|---|
| `config init` | 创建Windows/POSIX示例配置 | 新建配置，不覆盖既有文件 |
| `paths` | 显示解析后的统一路径 | 只读，不创建目录 |
| `validate` | 检查公开包完整性、语法、来源、隐私与链接 | 不运行模型 |
| `doctor [--online] [--workflow ...]` | 检查配置、工具、固定依赖；online读Comfy接口 | 不自动启动/安装/提交推理 |
| `workflows list/show/status` | 查目录、节点输入或后端队列 | 只读；status访问本地API |
| `workflows prepare` | 用覆盖JSON绑定自己的输入、生成请求和receipt | 只写新请求，不提交GPU任务 |
| `models plan/check/fetch` | 按ID/画布/模型族选择，核对或取得文件 | fetch需显式选择和许可确认；完成后大小/SHA校验 |
| `deps list/fetch` | 查或取得固定第三方代码 | 不自动pip；补丁有上下文与哈希检查 |
| `install skills/workflows/nodes` | 安装到对应原生目录 | 默认计划；`--apply`执行；不同既有内容报冲突 |
| `runtime start/stop` | 查看或执行托管Comfy服务方案 | 默认计划；`--apply`才执行；不接管其他应用的服务 |
| `runtime serve` | loopback公开文档预览 | **直接启动**本机HTTP服务，Ctrl+C停止；不服务用户输入/输出 |
| `project init` | 新项目目录、状态和简报模板 | 新建项目，不生成内容，不覆盖已有项目 |
| `cleanup --project ...` | 盘点已建立归属的项目runtime/下载大小 | 只盘点，不自动删除；实际清理按Skill规则 |
| `inspect media <文件> [--decode]` | FFprobe元数据和可选FFmpeg完整CPU解码 | 不生成新媒体；不替代观看、试听和内容检查 |
| `blender ...` | 向Blender原生运行器传参数 | `--which`只定位；执行脚本将启动编辑器处理任务 |

`runtime stop --cancel --apply`仅在已经决定取消托管后端队列时使用；默认有任务则保留并报错。安装冲突的原文件需要用户/维护者审阅处置，工具不自动改名搬走或覆盖。

PowerShell习惯入口为`tools/start_comfy.ps1 -Profile Balanced`、`tools/stop_comfy.ps1`，默认执行对应服务操作；`-PlanOnly`只显示计划。它们复用同一CLI/配置，不是另一套启动管理器，不会因安装/迁移自动启动服务。

## 维护工具

- `tools/export_workflows.py --help`：从登记的原生UI/API目录导出新快照，不覆盖源库。
- `python tools/build_docs.py`：按当前catalog重建`docs/overview.html`。
- [通用检查辅助](helpers.md)覆盖媒体、H3执行、GLB、绑定与UI维护。
- `tools/patch_gvhmr.py --help`：检查指定Motion Python中的GVHMR1.6.1修复；只有`--apply`写入，并保留小型回退记录。

直接用系统Python、FFmpeg、原生工具CLI、当前Comfy API和客户端插件均可。统一入口帮助定位和隔离，不限制执行者使用任务需要的现有工具；也不扩大账号、付费、删除或发布权限。

`runtime serve --with-history`显式启用本机历史档案和原生output的loopback预览，用于旧`/workflow-support/...`书签；默认预览不会开放这些本机资料，不把该端口反向代理到公网。
