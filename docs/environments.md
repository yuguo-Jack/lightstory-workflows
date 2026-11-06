# 环境分工与最小依赖

把环境分开能避免为一个分支安装依赖时破坏其他已可用分支。本工程不会把Comfy、Blender和Motion包混装到同一个Python，也不要求只读制作方法的用户下载全部模型。

| 需要做什么 | 最小软件/依赖 | 配置与验证 |
|---|---|---|
| 阅读方法、查目录、准备请求 | 系统Python3.11+；Git用于取得源码 | 宿主CLI、`validate`；无GPU包要求 |
| 交给Codex/Claude执行 | 上述+相应客户端+Skill安装 | 29个基础Skill；按需加9个H3方法 |
| Qwen基础图像与Fun控制 | 固定Comfy基线及其requirements、对应模型 | 查看目标图的`node-requirements`与`models plan`；在线object_info |
| Qwen Next-Scene | 上述+外取Viggle运行时加载器、已校验的原LoRA及前缀兼容转换 | 只借加载器，不混入Viggle Turbo模型/采样表 |
| Pixal3D与网格 | 原生Trellis2/网格节点、两项本项目适配、对应模型 | 这些能力已在固定Comfy源码；不再叠装旧独立Trellis节点包 |
| H3普通/Turbo/Flex与长片 | 原生H3节点及Director、对应底模/适配器/编码器/VAE | 按家族配套；CrossView额外取warp节点，Fun走原生控制链 |
| Ming TTS | Ming节点；当前pyproject无额外运行包 | 复用匹配Comfy环境+模型；实际试听 |
| Music3 | 原生Music节点+模型 | 实际试听；不替代TTS |
| SkinTokens | 固定节点+补丁及其requirements，配置allow_download=false | Comfy Python安装，无需Blender/bpy/强制flash-attn；Qwen3配置已登记 |
| Blender建模、精修、动画、渲染 | Blender原生Python+bpy；宿主runner定位实际exe | 不把Torch动作推理装进bpy环境；资产与引擎回读 |
| Motion真人动作 | 固定Motion后端、独立外部Python、Torch及其上游依赖、许可模型 | [Motion安装](blender-motion.md)，doctor后真实短片；不借Comfy环境装包 |
| Web/Unreal/剪辑 | 所选客户端插件及实际引擎/编辑器/构建工具 | [集成](integrations.md)，不因Skill文件存在宣称工具已连接 |

## 原机的版本记录怎么用

固定Comfy源提交在依赖lock；可读的已安装版本见[compatibility.windows4080.json](../config/compatibility.windows4080.json)。该文件是2026-11-06只读读取的包元数据，**不是经过另一轮GPU验收的requirements锁**，也不要求不同平台强装相同CUDA wheel。此前Motion的Python3.12/Torch2.11+cu128是另一个外部环境，不能与当前Comfy的Python3.13/Torch2.10+cu130记录混为一套环境。

首先使用匹配驱动/GPU平台的官方Comfy安装和其requirements。版本变化时从目标解释器执行`-m pip check`，读启动日志，再做受影响分支实测。不要把“安装成功”“依赖解析成功”“节点出现”“真实任务通过”“产物质量合格”混成一个结论。

## 节点requirements的安装位置

`deps fetch`返回固定checkout的真实目录。先查看该目录的requirements/pyproject；要安装时使用**配置的Comfy Python**，例如：

```powershell
& '<配置中的Comfy Python>' -m pip install -r '<SkinTokens固定checkout>/requirements.txt'
& '<配置中的Comfy Python>' -m pip check
```

先查看现有Torch/NumPy/Transformers组合；需要新增约束时在自己的环境分支解决，不无条件更新其他正常包。Director按固定README核对原生H3与媒体支持；Ming和CrossView当前没有必装的额外requirements。CrossView的numba只是可选加速，不为了它改变正常NumPy组合。

FFmpeg/ffprobe、Git、Node/构建工具等需要时用本机现有命令或按官方平台发行版安装，共享工具路径由`tools_root`配置。插件、UE SDK、Blender扩展和浏览器账号按各自原生管理；本仓不复制整套应用安装。

## 常见安装排查

| 现象 | 优先确认 |
|---|---|
| Skill同名冲突 | 旧安装属于哪个来源；先隔离target比较，按迁移步骤切换，不覆盖旧内容 |
| 符号链接权限不足 | 系统是否允许；Skill可显式使用copy，后续更新需人工对比；节点链接按系统方式解决 |
| 画布缺节点 | online object_info、provider/版本、节点启动错误；不要只重装画布 |
| 模型选择器找不到文件 | 配置models根、模型相对路径/扩展、hash和前端刷新；不要重复下载已校验文件 |
| 固定补丁不匹配 | 确认基线commit、LF换行、是否本地改动；保留原件，不能强制重置 |
| CUDA/编译扩展导入失败 | Torch/CUDA/Python/驱动与wheel兼容，按目标环境排查，不在宿主随意装同名包 |
| 桌面卡顿或保护中断 | 物理RAM、提交余量、显存、任务串行及实际缓存；分页不等于增加物理RAM |
| 只有源文件，没有实时工具 | 当前客户端插件和MCP服务未连接，按选择路线配置或使用已具备的CLI/API |
