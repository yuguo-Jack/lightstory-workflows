# 依赖、模型和许可边界

本工程的自主方法/宿主代码与第三方源码、生成权重、客户端插件、服务和用户素材分别管理。根MIT许可不能覆盖所有依赖，更不等于所有模型可在任意地区/用途使用。

## 源码与方法

| 类别 | 处理 |
|---|---|
| 自主Game/Video总流程、宿主CLI和一般适配 | 根MIT；保留引用和明确的第三方例外 |
| Game Design / Art / UI局部模块 | 已有MIT/Apache文本和NOTICE继续随模块分发；来源固定在各自references/sources |
| Blender第三方Skill库 | EL4CTEO固定MIT快照，逐模块LICENSE保留，本机修改标明 |
| 自主Pixal/UV节点 | 派生自GPL-3.0 ComfyUI实现，目录内GPL许可证单独适用；不以根MIT覆盖 |
| Director、Ming、CrossView、SkinTokens、Motion后端 | 以锁定上游仓和各自许可证为准，源码外部获取，补丁独立登记 |
| MiniMax H3类型/提示词Skill | 官方固定Git来源，README指向独立Community协议；仅自写overlay纳入本仓，官方正文用户按条款自行获取 |
| Viggle运行时加载器 | 固定来源文件与SHA，外部获取并核对上游条款；这里只用于Next-Scene运行时加载，不启用其Turbo权重/采样 |
| Flova | 只保留公开方法的转译与来源链接，不复制其私有Skill/辅助材料，不假装完整移植 |
| 原生客户端插件 | 使用者按客户端官方方式安装/授权，本仓不再分发托管插件 |

完整软件清单见[THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md)。本文件记录打包事实和需要核对的条件；使用者应阅读所选版本的原始条款。

## 权重获取

`models/weights.lock.json`只包含相对目标、发布源、Git/HF修订、文件大小、SHA和派生转换规则。它不是许可证本身。大多数条目固定revision+SHA；少数早期来源没有可恢复revision的使用SHA固定内容，清单显式标为`sha256`，不伪造提交号。下载入口遇到不同已有文件会保留并报错。

- Qwen主权重/编码器/VAE、Pixal/Trellis相关组件、H3底模/编码器/音视频VAE、Ming/Music、SkinTokens等逐项来自原清单登记来源。
- 社区打包、量化、LoRA和ControlNet不自动继承一个统一许可；检查底模及各适配器自己的说明。发布者、镜像分发者和原作者要区分。
- 成人级（NSFW）适配器保留明确分类，为可选能力，安装基本生图/视频不要求下载它们；不同专项的标签和真实测试范围分别记录。
- Next-Scene原件保留，兼容版本只改变safetensors模块前缀，验证张量数据区不变；清单登记两份哈希，不随源码上传转换后的权重。
- SkinTokens还需要Qwen3-0.6B配置/分词资料，已单独登记；该节点不因这些配置另要求一份完整Qwen3权重。
- SMPL-X、MANO由用户注册取得，Mixamo/其他人物和真实视频按其实际素材使用权处理。

MiniMax原README指向的[Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)包含地域、商业规模、再分发和使用条件，不能把公开可下载等同全球无条件使用。Motion的上游研究/非商业限制同样不能由其自身Apache代码许可消除。模型许可可能变化，按清单所选版本与当前原文核对。

## 不纳入公开包

模型、受限body模型、原用户照片/语音、Mixamo角色、私人样片、第三方演示视频、浏览器profile、cookies/令牌、私有服务配置、原始聊天和完整运行日志不纳入源码发布。公开历史摘要不包含这些文件的本机绝对路径。
