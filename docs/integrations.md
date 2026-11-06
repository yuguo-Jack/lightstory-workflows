# 客户端、原生插件和外部工具

Skill提供执行规范，实际工具来自当前代理客户端、安装应用、CLI或本地API。源码/目录链接不会转移账户登录、MCP服务器、客户端原生工具或收费授权。

| 集成 | 获取/配置 | 就绪证据 | 缺失时的处理 |
|---|---|---|---|
| Codex Skills | 原生用户Skill目录，通过本工程installer链接 | 新会话读取Skill及其依赖 | 保留安装冲突并审阅，不覆盖 |
| Claude Skills | 相同Skill内容链接到Claude目录 | 新会话读取；具体工具按该客户端配置 | 文件共享不代表Codex插件也存在 |
| Blender | 官方Blender，配置可执行文件；第三方MIT模块已收纳 | 路径/版本、实际任务env_report、资产检查与回读 | 仅头less CLI也可；不假定MCP在线 |
| Game Studio | 支持客户端的`game-studio@openai-curated-remote`插件 | 发现真实game-studio及运行时/资产/UI/试玩入口 | 选择该Web路线时安装连接；其他客户端需自行具备等价执行工具并明确记录，不能声称已调用Game Studio |
| Unreal Engine Skills for Codex | 支持客户端安装`unreal-engine-skills-for-codex`；引擎/项目侧按其unreal-mcp setup | 正确编辑器项目、真实只读工具调用、编译/PIE/保存/打包结果 | 可在引擎支持范围使用Python/CLI/手工工程操作；不把Python当打包后玩法脚本 |
| CapCut云剪辑 | 对应客户端CapCut插件并由用户登录 | 当前工具真实可用、草稿实际保存、最终导出另验 | 用户可选本地CapCut桌面或已配置编辑工具；不把云草稿当桌面工程 |
| 本地CapCut/桌面操作 | 配置exe，客户端提供受支持Computer Use | 真实时间线/工程/导出文件 | FFmpeg适合确定性处理；复杂可编辑工程按已选编辑器实际完成 |
| Mixamo | [Adobe Mixamo](https://www.mixamo.com/)，用户登录 | 本角色绑定、实际下载动作、Blender/引擎变形 | 普通可自制/Rigify动作，许可和质量按具体资产 |
| Motion2MixamoRig | 固定第三方后端+许可模型+可选Blender扩展 | doctor后真实短片、rig匹配、动作/接触/材质/导出回读 | 常见动作可Mixamo；商业受限路线改用符合授权的动作源 |
| FFmpeg/ffprobe | 系统命令，或按平台安装便携版 | 版本/能力、实际媒体读取和输出检查 | 先定位工具与编解码能力 |
| glTF Transform / KTX | 可选共享CLI，按相应官方项目安装 | 优化后GLB/纹理回读及目标端检查 | 不是基础生成前提；Rust/CMake只在需要编译的依赖上配置 |
| Playwright CLI | 可选浏览器工具与用户持久profile | 可见浏览器与真实页面状态 | 账号/CAPTCHA交给用户；不打包profile或cookies |

## 权限与本机管理

新非Python共享工具按配置的`tools_root`放置；Windows示例沿用D盘共享tools。Skill只放仓库与代理原生Skill目录，不额外复制进tools。每个具体制作项目使用同一项目根目录推进，临时下载、日志、转换和验证集中收纳。

API密钥、登录、购买和发布按用户授权与当前服务规则处理；不自动复制Codex/Claude配置、浏览器状态或账户令牌。插件的工具接口、版本和可用性由现场发现，源代码中的名字和缓存文档不是就绪证明。

## 版本策略

原记录的客户端插件版本只是兼容证据，不能在别人的缓存目录写死。源码节点和模型用本项目lock；客户端原生插件用其官方更新机制。制作期间锁定版本，升级先做受影响功能回归；不要求每个项目都升级所有工具。
