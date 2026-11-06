# H3：可选LoRA与连续长视频



适用本机导演台`4c6245e`。本页专项增强以普通H3为已验证基线；增强LoRA、Turbo、条件桥均按需使用。常规/Turbo/Flex按题材与配套流程选择，Flex可直接用于审片合格的正式镜头。操作入口、素材、导出和通用返工见[H3使用说明](h3.md)，本页只讲LoRA相关差异。



Pika Flex 是可选的另一套后训练/六步采样路线，配置集中在[Flex说明](h3-pika-flex.md)。选择该路线后对应Flex适配器是必需配套，不与Turbo叠加；本页专项动作组合、普通二采和SelfLift的历史通过不自动覆盖Flex。



新增人物运动/表情、复古动画、环绕/卡片、子弹时间和CrossView见[扩展LoRA说明](h3-extra-loras.md)。以下六份原动作配方不覆盖新增项的采样例外，也不自动证明它们与Flex、Turbo或彼此任意叠加。



## 选哪种增强



六份动作画布使用FL2VA、25步、CFG1、res_multistep/simple。下表是选用对应增强画布后的预设，不要求该题材必须挂LoRA；移到Ref2VA前核对作者兼容性。



| 用途 | 当前文件与强度 | 用法 |

|---|---|---|

| 格斗 | `H3_Combat_V2.safetensors` 0.65＋`Motion_Repair_V2.safetensors` 0.5 | Combat偏打击/反应，Repair辅助衔接；Combat可不写触发词，作者提供可选`prfight2`增强动作强度 |

| 兵器 | `Bunny_weapon_combatV1.safetensors` 0.45 | 触发词`BUNNY`；当前版本优先单独使用，与Combat/Repair等强动态LoRA混用可能冲突 |

| 枪斗 | `GunFu.safetensors` 0.9 | 触发词`BUNNY`；写清持物、行动者、目标及接触后的状态 |

| 运镜 | `camera_motion_h3_lora_v1_3000_pruned.safetensors` 0.8 | 在生效视觉描述开头写`camera motion, ...`，再写方向/速度/目标；不提供精确轨迹 |

| 动作衔接 | `Motion_Repair_V2.safetensors` 0.9 | 可选`bunny_crisp_motion`；辅助运动连续性，不是已生成MP4的自动修复器 |

| 物理观感 | `wushu_spatial_physics_clean_3000_pruned.safetensors` 0.35 | 描述碰撞、支撑与轨迹；作者模型卡同时保留新0.3–0.5和旧0.8–1.0说明，本机沿用0.35；不执行物理模拟 |



强度分别作用于补丁，不需要相加为1。软件每段最多8条，不代表应叠满；只选H3兼容文件。现有兵器、枪斗、运镜模板缺相应触发词，准备新任务副本时补到实际segment/Group；图库标签要点击才插入，选择文件不会自动补词。缺词不代表权重完全未加载。



作者的可选GunFu组合：远程枪战一采0.9＋Repair0.5；近身枪斗一采GunFu0.9＋Combat0.5＋Repair0.3；二采GunFu0.65＋Repair0.25。Repair自身建议二采约0.2–0.3。这些额外组合未作为本机新增实测或默认配置。



## Turbo：速度与质量的独立选择



| 本机模板 | 对应Turbo LoRA | 强度 / 步数 |

|---|---|---|

| 02、11；FL2VA | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | 1 / 8 |

| 18；Ref2VA | `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | 1 / 4 |



接法：`H3底模 → LoraLoaderModelOnly(Turbo) → Director.model`，同步匹配采样参数。Turbo通过少步蒸馏改变生成行为，可能影响细节、身份、动作和音画，不能当无损注意力加速；合格结果可以成片，但质量优先默认不启用。当前没有系统的同条件质量评分。



回到常规路线，同时绕过Turbo并恢复常规参数：当前01/10起点为25步、CFG1、res_multistep/simple。只设Turbo强度0却保留4/8步，或挂Turbo盲目加到25步，都不等于常规路线。两套Turbo不能交换；与动作LoRA的全部交叉组合也未逐一验证。



同一次Director的一采步数/采样器为全局配置，不能只给某段卸Turbo却继续沿用全局4/8步。Turbo草稿转常规版本应使用新缓存、重新生成目标镜头/连续段；同种子不保证复刻，可用已确认关键帧/参考帮助约束。追加低幅度二采不保证补回Turbo缺失的细节。



## 全局、分组与二采分别控制



- **全局**：外接`LoraLoaderModelOnly → Director.model`作用于全部段；六份动作模板采用此接法。

- **分组**：要让部分动作阶段介入，给Director接未挂该专项LoRA的底模，在对应片段的“分组LoRA → + LoRA”选择文件、权重和启用状态。每段从输入MODEL克隆并加自己的补丁，不累计上一段的分组LoRA。空分组只是不再加补丁，不能撤掉全局已有LoRA，也不要两处重复加同一补丁。

- **二采**：Refine不接`refine_model`时继承该段一采模型。要用较弱二采LoRA，应独立接MODEL分支；仅降低denoise/步数不会降低LoRA强度。该外部输入目前全片共用，不会自动跟随各段再换不同强度。



API在`timeline_data.segments[i].loras`中写列表，例如：



```json

{

  "continuityFromPrev": true,

  "loras": [

    {"name": "H3_Combat_V2.safetensors", "strength": 0.65, "active": true},

    {"name": "Motion_Repair_V2.safetensors", "strength": 0.5, "active": true}

  ]

}

```



这是单段字段，需并入完整时间线。无外部Group的全局编辑模式使用`global.loras`。接外部Group时，提示词/素材/时长仍由Group提供，但LoRA先取`timeline_data`中对应序号的UI行（按`segments`、`shots`、`r2vGroups`、`fl2vGroups`顺序查找）；只有没有对应UI行时才回退到Group payload。标准Group节点没有单独LoRA输入口，不能凭空加端口或只改被UI行遮盖的payload。切模式也会影响提示词与参考继承，按[生效优先级](h3.md#提示词与素材的生效位置)核对。



Semantic Bridge不是动作LoRA：本机有原版`MiniMaxH3_SemanticBridge_v1.safetensors`和`BUNNY_H3_ActionLogic_Bridge_V2.safetensors`，16模板默认原版alpha0.15。换BUNNY是替换adapter，不串两座；它是一套全局条件适配，不随分组LoRA自动切换。两者都不能锁定像素或保证关系。



## 动作阶段如何保持衔接



开启导演台“段间引导”，连续后段勾“引用上段”；当前连续模板用22帧历史上下文。切分组LoRA不会关闭上一段尾部运动/可用声音的引导。



如果选择使用专项LoRA，可安排“准备时低强度 → 动作主体用所选强度 → 收势减弱 → 退出”；全程不加同样有效。边界落在可承接的姿态，提示词接住脚位、手位、惯性和镜头方向。此为编排建议，不是新测最佳参数。



当前是每段固定权重，没有内置单段内按帧渐变曲线。保持底模家族、量化、采样、FPS、画幅和身份/色光锚点一致，必要时加过渡段；差异过大的场景允许明确切镜并关闭该段引用。历史引导降低跳变，不能保证换LoRA后无缝，相同种子也不能替代上下文。精确运动/接触优先用Blender预演或参考视频。



## 换LoRA后的缓存处理



当前内部时间线缓存身份未显式纳入`seg.loras`及外部MODEL补丁；外部Group记录更多payload，但不能假设所有路径都追踪模型文件和上游输出变化。



- 从头做新LoRA版本：使用独立`cache_name`。

- 保留前段只改中段：用原项目缓存“选择运行”重算目标段，确认没有因一采确认/修脸复用而跳过采样。不能只重导出或用二采确认冒充新的动作一采。

- B段结尾改变时检查A→B、B→C。旧C基于旧B，必要时从C顺序重做受影响后段直到衔接稳定或明确切镜；缓存不会自动完整追踪这条依赖链。

- 保存本版LoRA清单、有效请求及成片，所需返工缓存保留；不用的版本按[清理规则](cleanup.md)收尾。



## 证据与来源



普通/Turbo、六份动作模板和基础连续生成已有运行证据；逐段换LoRA、过渡强度及全部交叉组合只核对了源码/用法，未新增出片验证。说明审校不触发旧样例回归。



作者用法见[Weapon](https://huggingface.co/JOKER141/MiniMax-H3-Weapon-Combat-LoRA)、[GunFu](https://huggingface.co/JOKER141/MiniMaxH3-GunFu-Gunfight-LORA)、[Camera](https://huggingface.co/Jojocodex/minimax-h3-Camera-Motion-lora)、[Turbo配套](https://huggingface.co/Comfy-Org/MiniMax-H3)、[导演台](https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director)。完整来源及其余模型卡在W的`model-downloads/model_manifest.h3.json`和`model-downloads/sources`；不把其他FastH3完整模型参数套到当前Turbo LoRA上。
