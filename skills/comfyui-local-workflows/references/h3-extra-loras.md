# H3 扩展 LoRA：选用、作者配方与操作



这些是可选通用能力。正式画布位于 `MiniMax H3/人物与风格`、`运镜与视频编辑`及`动作与运镜`，安装时前置配置的命名空间。历史状态查工程`workflows/catalog.json`，新运行单独验收，不能把候选画布或已下载算作实测通过。



这些是各发布者训练/转换的社区 LoRA，不是 MiniMax 官方统一配方。下表区分发布者建议与本机适配；作者未说明的参数不冒充官方最优。专项 LoRA 均可不加，普通 H3、Turbo、Flex 仍按目标选择。



## 按目标选择



| 通用功能 | 所选权重 / 家族 | 发布者配方及本机起点 |

|---|---|---|

| 人物与风格/01 自然人物运动 | `better_motion_h3_lora_v1_500`；FL2VA | 作者强度0.4–0.8、20–30步；本机0.65、20步、res_multistep/simple。步行/转身/蹲起/重心过渡，不保证脚底无滑动 |

| 人物与风格/02 复古绘本动画 | `studio1939-light` r16；FL2VA | `gulliv3r,`开头，扩写关；1.0完整风格，0.4–0.8混合。本机1、25步、1024×576，柔和绘本与笔触背景 |

| 人物与风格/03 复古赛璐璐动画 | `studio1939-strong` r64；FL2VA | 同一触发/配方，更强轮廓与平涂；不是02再叠一层。重复角色描述有助统一，不等于身份严格锁定 |

| 运镜与视频编辑/01 主体360环绕 | `minimax_h3_orb360_step1500`；Ref2VA | 强度1、Euler/simple20步、124帧/24fps、作者时间标注结构及`ORB360_CW`。Euler对应作者引用CLI的积分形式，shift12/3；本机800×800、单主体展示；可生成一周外观变化，但背景/动物冻结有下述限制 |

| 运镜与视频编辑/02 照片卡片旋转 | `minimax_h3_orb360_cardspin_v2_step50`；Ref2VA | 强度1、20步、124帧/24fps、`ORB360_CARDSPIN`。薄照片卡片特效，与实体相机环绕用途不同；作者也提示细节更软 |

| 运镜与视频编辑/03 源视频换机位 | `MiniMax-H3_Ref2VA-LoRA-CrossView-Warp_v1_3500`＋指定DMD Ref8；Ref2VA | CrossView0.8、DMD1、res_multistep/simple八步、shift12/3、`crossview`；MoGe2几何及Warp/Guide为必要配套。先约0.5MP一采 |

| 人物与风格/04 自然表情与英语口播 | `nafasp_h3_lora_v2_500`；FL2VA | 作者0.6–0.8、20–30步；本机0.7、20步。固定seed、固定开场词可减轻音色漂移，不等于配音克隆或任意音频口型驱动 |

| 人物与风格/05_成人级_NSFW_参考人物运动_AfterMidnight | `AfterMidnight_ref2va_h3_sexytime_rank64-v1.2`；Ref2VA | 作者强度1，明确要求Euler＋beta以避免音频问题；本机25步、CFG1，图片接Reference Group |

| 人物与风格/06_成人级_NSFW_参考人物质感_AfterMidnight | `AfterMidnight_ref2va_h3_softer_rank64_v1`；Ref2VA | 作者0.8–1、Euler＋beta；本机1、25步。训练目标偏细节/幻想质感，不和05默认叠加 |

| 人物与风格/07_成人级_NSFW_人物表现_NaughtyTimes | `SexGod_NaughtyTimes_v3_rank64_pruned_NOADALN`；FL2VA pruned | 使用用户指定的去AdaLN版本匹配本机pruned W6A8。作者偏好unpruned且提示pruned可能弱于其演示；本机强度1、25步、res_multistep/simple是本地起点，非作者公布最优 |

| 人物与风格/08_成人级_NSFW_人物表现_Unlocked | `Minimax_H3_Unlocked_V2.1`＋已有FL8 Turbo；FL2VA | 作者Euler ancestral、CFG1、4–8步配Turbo，专项权重0.3–1、起点0.5；本机选匹配FL2VA八步Turbo1＋专项0.5，不拿Ref4替代 |

| 动作与运镜/07 子弹时间 | `BulletTime-MMH3`；FL2VA | 精确触发词`bullet-time`；本机普通H3、强度1、20步、res_multistep/simple、192帧/8秒。提示明确正常动作→1.5秒触发冻结/慢环绕→5.5秒恢复实时；作者提示Turbo/特殊注意力或强叠加时应降低专项强度 |



### 成人级 NSFW 快速选型

先分图片/视频，再按输入方式和侧重选择；以下均为专项LoRA。

| 优先需求 | 选择 |
|---|---|
| 参考生成，侧重运动连贯 | H3 `05` AfterMidnight **sexytime v1.2**，Ref2VA |
| 参考生成，侧重细节、清晰度及幻想/超现实质感 | H3 `06` AfterMidnight **softer v1**，Ref2VA；不等于柔光或更写实 |
| 文生/首帧图生视频，输入方式灵活 | H3 `07` **NaughtyTimes v3 pruned_NOADALN**，FL2VA；本机裁剪适配可能弱于作者推荐的未裁剪配套 |
| 快速试片 | H3 `08` **NSFW Unlocked v2.1＋匹配的FL8 Turbo**；本机八步，效率来自整套配方，不代表质量全面领先 |
| 静态人物图、关键帧 | [Qwen **TheseAlpacas v2.0**](qwen-extensions.md#成人级nsfwlora来源独立配方与验证范围)，使用图像专项独立配方 |

AfterMidnight两支是同数据、不同训练取向，二选一，不是版本升级替换。以上是作者定位与本机配套差异，未做同条件质量排名；不默认叠加专项，具体参数沿用上表及对应模型说明。

所有权重名补`.safetensors`即实际文件名；LoRA在原生 `models/loras`，MoGe2在`models/geometry_estimation`。正式来源、固定修订、完整SHA256及目标路径统一见工程[模型登记](../../../models/weights.lock.json)。Natural Face取得的公开文件与Civitai指定版本、作者仓库重命名文件的完整SHA256均一致，获取来源也保留在登记中，不需要提供账号令牌。



本机复用FL2VA/Ref2VA的pruned W6A8、Qwen3-VL NVFP4 AWQ、INT8视频VAE及FP32音频VAE。运动/口播作者给720×1280，本机为原生32对齐使用704×1280；不是原封不动复刻作者所有硬件和精度。步数/分辨率/速度及质量判断以实际验收记录为准。



本批共同起点为CFG1、video/audio shift12/3、24fps、batch1；CrossView用BasicGuider表达CFG1。各行的采样器、调度、步数与适配器配套仍分别执行，不能只保留共同参数就交换路线。



## 操作顺序与可调位置



1. 按上述目标打开通用功能，更换素材并同步提示里的主体、环境、动作和参考标签；初始样例可以完整替换，不依赖验收角色、猫或杯子。不要把示例中的服装、天气或背景描述原封不动套给无关新图。

2. 核对底模家族、专项版本、强度和采样配套。普通专项只挂一份；Unlocked的FL8、CrossView的DMD Ref8是各自明确配套的例外，不能自动推广到全部LoRA。

3. Director内部时间线模板编辑实际生效的分段；连着Reference Group的模板在Group改提示词/时长/输入。原生Reference动态槽`ref_image_0/ref_video_0`对应文中`<Picture 1>/<Video 1>`。增加参考时同时说明每份材料的职责，删材料也删对应标签。

4. 新任务换独立输出前缀、Director `cache_name`，再Queue；同一GPU串行。新Director预设已保存为“自定义”宽高，改尺寸在输出设置同步调整，不让缺省0.4MP重算覆盖。多数预设124帧@24fps约5.17秒，子弹时间为192帧/8秒；用真实帧数对齐音频/镜头节奏。

5. 核对实际音画与本次素材：身体与接触、表情/口型/词句、风格、环绕方向/回到起点、换机位后的遮挡和物体身份。真实补丁加载、成功出MP4与“审美/物理/连续性完全正确”分开判断。



AfterMidnight、NaughtyTimes、Unlocked均标为**成人级（NSFW）LoRA**。按各发布版本区分，属于可选专项；本机输入、输出和验证范围记录在对应批次验收页。



本批ORB与AfterMidnight为单张参考实测；ORB三/四视角的角度标注用法来自作者，未另做本批多图出片。NaughtyTimes、Unlocked的本机配套与输入模式见验收记录，不把这些结果自动推广到全部首尾帧/参考/长片组合。逐项参数、补丁、样片与审查见本批验收页和实时索引。



## CrossView的完整链与限制



源视频先转24fps，截取所需124帧 → 一次Resize同时供两条支路 → MoGe2逐帧几何（batch1）→ CrossViewWarp → 原生`MiniMaxH3AddGuide(frame_idx=0)`；同一源帧另接原生`MiniMaxH3ReferenceToVideo`，承载身份/外观。最后八步采样、视频/音频VAE解码并保存结果；画布也保存小型Warp检查片并预览机位图。



- 源与warp的尺寸、帧率、帧数必须一致；改Resize尺寸/截帧数量时同步Reference的width/height/length。普通LoadVideo/GetVideoComponents不自动把任意原片变成24fps，先用本机ffmpeg等工具转换。长源片也应预先截成所需短段；图内ImageFromBatch在解码之后，不能阻止上游整片解码占满内存。

- 当前样例Resize为960×544、中心裁切。换新片先按源片比例选32对齐尺寸；需要保留全构图时先等比缩放/补边，再同步两支路，避免把横幅预设直接用于竖片。

- 初始约±30°方位、小幅仰俯，`keep_source_aim=true`、距离1。距离调节作者已明确不可靠；角度过小、过大、深度边缘、遮挡、透明/反光和快速运动都可能出错。

- 洋红空洞代表未观测区域，最终须由模型猜测填充；不是可精确还原的真实第二机位。MoGe是单目估计，不是场景真实3D或相机标定。

- 本机画布保留作者的Guide＋Reference角色分工；视频IO、缩放和注意力使用已有原生方案，不额外安装作者图中的便捷节点/稀疏注意力。作者另有1.5MP二采展示，不能把约0.5MP一采验收写成二采已测。

- 当前Director没有任意AddGuide条件输入，因此本功能使用完整原生专用链；普通导演台只挂LoRA或把warp当第二个普通参考不等价。可把合格结果作为后续分镜/编辑素材；不要声称所有导演台功能直接无缝叠加到这条链。

- 当前链的声音由H3生成，未把源片音轨另接声音条件，不保证保留原声；需要原声时先按同一截帧范围和时间基准抽出音轨，在后期核对同步后混入。



## 与导演台分段、Turbo、Flex配合



全局`LoraLoaderModelOnly`影响全部生成段；只在某动作阶段使用可选专项时，用[导演台分组LoRA](h3-lora-continuity.md)并避免全局/分组重复加载。移除的是专项全局补丁；若当前路线要求Turbo，应保留匹配的全局Turbo，不能把全部Loader都绕过。外接Reference Group的提示/素材/时长在Group修改，逐段LoRA则优先读取对应时间线UI行，不是给标准Group凭空增加LoRA端口。底模、实际参考模式和采样路线仍须匹配；目前不承诺所有交叉组合的效果。



采样器/调度是Director级设置：AfterMidnight的Euler/beta与普通res_multistep/simple、Unlocked的八步Turbo配方不能靠“每段换一个LoRA”就自动按各作者要求切换。同一连续计划保持可兼容的全局配置；必须改采样路线的镜头分开生成并重新审接点。Flex固定LCM六步、已有Ref4 Turbo和CrossView DMD Ref8是不同配套，勿互换或默认同时加载。



ORB360一周、CardSpin和Bullet Time有明确时间阶段；改变片长要重写时间标注/动作阶段，不把原五秒提示直接复制到任意长段。段间引导可承接历史但不能保证换风格/LoRA后身份、光色、姿态与声音等同不换LoRA；详见连续性说明。



## 资源、排错和收尾



- Balanced配置、一次一个GPU任务，保持既有RAM/提交内存保护；分页可降低提交失败风险，不替代物理RAM/显存。CrossView增加逐帧几何、双视频条件与较大DMD适配器，不与别的GPU生成并跑。MoGe先用batch1。

- 无LoRA效果先查家族、真实补丁数量、未加载键、触发词和实际生效的Group/时间线，不先堆更多LoRA。NaughtyTimes只用指定pruned_NOADALN，不拿unpruned文件硬套本机pruned底模。

- AfterMidnight音频异常先查Euler/beta；口播缺字、漂移或口型不准先缩短台词、稳定参考与种子，不能靠音轨可解码即判通过。需要独立配音时可在本技能直接使用Ming；若属于整片制作，将实际音轨和时长交给上层做同步/混音，不强制单项口播任务启动Video总流程。

- ORB正式预设用单主体展示提示；实拍环境改相应背景段。作者猫图在本机res_multistep与Euler均有头部跟随、未完成冻结360。刚性道具可完成一周：首轮不相关天气词引入雪景，清理提示后雪景消失，但背面阶段仍有灰底漂移。它适合生成式展示，不适合承诺原环境/身份/物理精确保留；人物/动物冻结先试片，真实背面可补一致实角度参考。照片卡片偏软是作者已知边界。

- Bullet Time事件/恢复不清先简化为一次动作和一个明确触发，精确`bullet-time`写在冻结中段，给定相机方向与角度，再调整强度；不等于真实物理时间冻结。

- 新任务清理遵从[运行规则](runtime.md)与[任务收尾](cleanup.md)：保留模型、输入、成片和仍要返工的段缓存；清掉本任务无用的无损段帧/潜变量、重复抽帧、转换副本与失败残留。检查本次项目临时目录、配置的`${STATE_ROOT}/runtime`及当前Comfy原生output下的实际段缓存，不整库清空。



## 发布者资料



[Better Human Motion](https://huggingface.co/vpakarinen/better-human-motion-h3-lora) · [Studio1939](https://huggingface.co/lovis93/studio-1939-old-animation-lora-minimax-h3) · [ORB360/CardSpin](https://huggingface.co/MATLOWAI/MiniMax-H3-ORB360-CardSpin) · [CrossView](https://huggingface.co/Cseti/MiniMax-H3_Ref2VA-LoRA-CrossView-Warp_v1)及[节点](https://github.com/cseti007/ComfyUI-CrossViewWarp) · [Natural Face & Speech](https://civitai.com/models/2925394?modelVersionId=3339123) · [Bullet Time](https://civitai.com/models/2934116) · [AfterMidnight](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW) · [NaughtyTimes](https://huggingface.co/SexGod1979/NaughtyTimes-MiniMax-H3) · [Unlocked](https://civitai.com/models/2925727).
