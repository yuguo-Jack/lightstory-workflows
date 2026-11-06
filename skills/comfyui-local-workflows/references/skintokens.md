# SkinTokens：骨架、蒙皮与 GLB 交接

本机2026-10-30验过：官方TokenRig GRPO＋Skin VAE，通过 `ComfyUI-SkinTokens-NoBlender` 使用现有ComfyUI的PyTorch/CUDA，不另装bpy或第二套CUDA。Blender自带bpy留给资产准备、变形检查与导出。

## 选哪个画布

正式栏目 `SkinTokens`，可用 `scripts/library.py list --model SkinTokens` 查询当前UI/API与状态。

| 画布 | 输入与用途 | 执行/边界 |
|---|---|---|
| `01_自动骨架与蒙皮` | 静态GLB → 自动关节层级、四影响蒙皮 → GLB | CUDA；人形、动物/异形的起点，不输出控制器或动作 |
| `02_已有骨架补蒙皮` | 已有绑定骨架的GLB → 只重算权重 | CUDA；保留原关节、骨轴、层级和inverse bind matrices；不是重定向。已有精修权重时按实际问题选择，优先局部处理 |
| `03_骨骼命名适配` | 有骨架GLB → Mixamo/UE5式命名 | CPU；只改识别到的名字，不补骨、不调整骨轴或参考姿势 |
| `04_蒙皮权重修复` | 有蒙皮GLB → 清除跨身体的不合理权重 | CPU；不是通用平滑器，也不保证比已精修权重更好 |

机器上的默认示例只是可替换输入，不含角色特化规则。实际验证用人形、官方长颈鹿和Pixal3D官方机甲输入；没有将早期已清理的人物GLB冒充本次输入。核心参数与语义来自同一套通用节点。

## 运行顺序

1. **先整理资产。** 在Blender副本检查直立/朝向、真实尺度、脚底、分离的四肢和手指、关节可弯的拓扑。身体、衣服、头发和刚性道具尽量有清楚组织。新骨架流程在绑定前规范尺度；已有复杂rig不要盲目对骨架和子网格一起Apply Transform，这可能改变已有绑定。保留原件。
2. **Pixal交接走GLB。** 先用Pixal的Save 3D保存含UV/PBR的GLB，再上传至左侧Load 3D；这条路线实际验过世界几何、原材质和内嵌贴图保留。不要为了省一个保存步骤，直接把仅有MESH的分支当成保材质路径。
3. **选流程并替换输入。** 上传自己的GLB，确认预览方向、对象与尺寸。新骨架选01；确需重算既有骨架权重选02；只改名/清权重用03/04，不重新推理。
4. **设置开关。** 人形可开`relabel`并选Mixamo/UE5；动物、异形关闭。01的`use_skeleton=false`，02为true。保留`use_transfer=true`，否则会重新导出模型代理，不能保留完整原材质。默认`use_postprocess=true`、`clean_weights=true`；不确定的长衣/额外肢体可比较关掉清权重的任务副本。03/04不需要加载模型。
5. **采样默认。** `top_k=5, top_p=0.95, temperature=1, repetition_penalty=2, num_beams=10`已在4080上运行。没有把减少beam当成默认质量策略；显存确实不足时再按runtime排查并记录变更。模型有随机性，不能保证重新运行得到完全同一骨架；批准后的GLB保留用于后续制作。
6. **提交并保存。** 按runtime规则一次一个重任务。节点先写当前ComfyUI `temp/skintokens/...` 的中间GLB；右侧 **Save 3D** 写`output/SkinTokens/<功能>/...glb`，成品以history的`3d`元数据为准。768×768是预览窗口，和网格/纹理精度无关。
7. **进入Blender检查。** 调用`$blender-core` → character-rigging/asset-qa。检查单一骨架、关节位置、无漏权重、归一化、每顶点最多4影响、抬肩/弯肘/深蹲/手指及原材质。glTF导入器可能生成Icosphere骨骼显示辅助物，识别`pose_bone.custom_shape`，不要当身体网格渲染/导出。
8. **按目标端导出。** 选Blender export-pipelines并回读FBX/GLB，检查尺度、骨轴、动画时长；目标引擎另验。命名适配不等于UE Manny、Mixamo动作、Rigify控制器或插件已经完全兼容。

02允许多个mesh/skin共享同一套关节；不同骨架或不同关节集合分开处理。骨架token化若因重合关节改变层级会明确拒绝，先整理骨架，不强制套错。保留源rig变换意味着带0.01等缩放的输入也会保留缩放；需要单位骨架的引擎，应在源资产准备阶段规范化，而非声称补权重自动修好了所有导出问题。

## 本机证据与限制

来源与验证：

- 历史状态见工程`workflows/catalog.json`。新任务分别记录UI回读、请求、history、GLB检查及Blender变形/FBX回读；详见[验证边界](../../../docs/validation.md)。
- 先前通用样例：人形52骨、长颈鹿59骨、Pixal机甲28骨，约25–29秒；既有65骨补权重约20–25秒。最终正式模板以`published-validation.json`的实际输出和时间为准；不得把这些短样例速度套到任意高模/复杂骨架。
- 原关节/绑定矩阵保留经过比较；世界几何、材质语义、内嵌图像经过检查；Blender可变形和FBX可回读不代表任意网格的生产动画、引擎碰撞或布料已经验收。
- 预测存在左右不完全对称、肩肘/髋膝极限形变等需审查项；AI不能补回粘连/缺失手指、面部拓扑或精修权重。质量不合适时回到Blender局部修权重/关节，普通人形也可改用Mixamo，需控制器用Rigify。
- 本次自动52骨样例在大幅屈肘/转身压力姿态有明显的分件拉扯；既有65骨补权重保留了原骨架，仍有极限关节形变和对称性检查项。已验证的是推理、数据保留与可回读；没有把这些结果认证为直接可用的精修角色。02默认测试输入来自动作工具的简化预览，原输入无UV，输出也不会凭空补UV；真实带PBR输入应从原资产GLB开始。
- **坦克、车辆和机械**：炮塔、车轮、履带、铰链用刚性分件/父子关系/约束或程序运动。自动软蒙皮可作为起点，但不能把弯曲装甲、拉伸轮子当成正确结果。
- **斗篷/尾巴/头发**：骨骼影响只是前提，额外骨骼、碰撞代理与Blender/UE布料/物理另做。此模型不生成动作、面部表情或实时物理。

## 位置、更新与清理

权重在`${COMFY_SHARED_ROOT}/models/skintokens`，两份官方checkpoint合计约1.51GiB，Qwen3只需配置；官方SHA记录在`${LIGHTSTORY_ROOT}/models/weights.lock.json`。节点在正式ComfyUI的`custom_nodes/ComfyUI-SkinTokens-NoBlender`。上游：[SkinTokens](https://github.com/VAST-AI-Research/SkinTokens)、[节点包装](https://github.com/stevelittlefish/ComfyUI-SkinTokens-NoBlender)。后者是社区节点，不是ComfyUI官方原生模型。

兼容补丁处理输出子目录、glTF绑定坐标/scale、既有骨架重复/骨轴丢失、共享骨架多skin和权重清理坐标，见工程`third_party/patches/skintokens/local-compatibility.patch`及依赖lock。更新节点后核对补丁与实际回读，不直接覆盖并沿用旧通过结论。

每批结束按[cleanup](cleanup.md)清理本任务不再使用的`temp/skintokens`、失败/重复GLB及导出备份；确认Save 3D成品和必要返工数据已保留后再清理。原有模型、用户输入、正式画布、批准的GLB/Blend/FBX和小型运行记录保留。绝不整库清空共享output或模型缓存。
