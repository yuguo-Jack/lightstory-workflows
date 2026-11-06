# ComfyUI画布与执行

总入口：[ComfyUI Local Workflows](../skills/comfyui-local-workflows/SKILL.md)。具体模型优势、采样配套、LoRA/参考/控制/输入限制与排错仍在其`references`维护，本页只说明工程化入口。

**模型画布实测基准：Windows＋NVIDIA GeForce RTX 4080（16GB显存）＋32GB物理内存。** 81组工作流覆盖Qwen-Image-2.1、Pixal3D、MiniMax H3、Ming-3.0-TTS Tiny、MiniMax Music 3与SkinTokens；量化/低内存方案、输入规模和GPU/CPU执行范围见[验证说明](validation.md#验证环境与范围)。

## 目录和输入

`workflows/catalog.json`是发布目录，UI在`workflows/ui/<模型>/<功能>.json`，API在`workflows/api`。`node-requirements.json`登记每图节点，`node-providers.json`说明原生、第三方或本项目适配来源。UI导入和API执行是两个检查：复杂动态控件要在当前前端回读实际`graphToPrompt`。

原素材已替换成`UPLOAD_*`。不分发原人物图、参考声、Mixamo人物或视频，用户必须上传自己的合法输入。蒙版与控制素材按同坐标/时间对齐，Director编码Group中的参考也必须更换。多参考不是张数越多越好；同一主体的多视角先筛一致性。

仅换参数/素材时保存项目请求；需要项目特化节点时另存原生`Projects/<项目ID>/<模型>/<功能>.json`，不覆盖通用图。能力补充属于通用库维护，其通过画布继续按模型/功能入库。

## 查询到实际产物

1. `doctor --online --workflow <名称>`核对服务、当前节点和模型文件；SHA核对另用`models check --hash`。
2. `workflows show`读取当前节点ID、有效输入和预设；按项目制作覆盖对象。
3. `workflows prepare`生成独立请求与小型receipt，检查媒体、参考职责、尺寸和有效时间线。
4. 根据用户生成授权，执行者POST`/prompt`，保留prompt_id；轮询`/history/<id>`，核对真实完成/失败/中断及输出元数据。工具本身不因查询/准备而提交。
5. 实际查看图像/Alpha、GLB/材质/变形、视频接点与运动或声音。HTTP成功、文件存在、历史passed都不是本次内容验收。
6. 按归属释放空闲内存并清理确认无用的磁盘中间缓存；保留必要返工依赖。

## 原主机的内存方案

Balanced、Conservative、PixalStable保留原参数组合；启动器先核对当前版本是否支持。Windows内存保护只管其可验证归属的Comfy后端；Pixal低内存节点用文件映射与分块运算，临时磁盘峰值仍可能很高。分页提高提交余量，不增加物理RAM/显存，也不能保证无换页停顿。

可选保护器需要宿主psutil，GPU推理留在Comfy环境。保护不覆盖Motion、UE或其他应用；多个重阶段按总流程串行。没有基于同条件实测的加速/质量声明时，不能把INT8、Turbo、Flex或缓存等同于无损注意力加速。

`resources.reserve_commit_gib`和`reserve_ram_gib`默认6/2.5GiB；`heavy_minimum_commit_gib`默认63GiB，保留原机对H3/五参考等重任务的提交上限要求。较大内存主机可按实测调整，不能为掩盖失败随意降低保护。保护器不会修改系统分页设置。配置项`serial_gpu_jobs`是调度约束，独立的外部提交者仍要遵守，启动器不是全系统任务队列。

## 维护者从原生画布回收修改

先在自己的ComfyUI保存UI与API；运行维护导出到一个**新**快照目录，再审阅与仓库差异。保留来源、输入要求和历史验证边界，重新导出不应带回本机路径、嵌入预览、用户文件名或运行输出。通过受影响功能后再替换仓库的通用版本，更新目录/依赖/模型和文档。不要把测试运行副本当正式API发布。
