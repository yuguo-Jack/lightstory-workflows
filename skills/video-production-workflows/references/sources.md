# 来源、版本与维护

本流程编排本地生成、CG和后期工具，不是MiniMax、Flova或CapCut的联合产品。核心方法见总入口；模型配方由ComfyUI Skill维护，具体作品仍需实际播放、内容检查和返工。

## 执行方法来源

- [MiniMax-AI/MiniMax-H3 Skills](https://github.com/MiniMax-AI/MiniMax-H3/tree/199b7d0e1fd95e7b3eafa8c15eca692534142427/skills)：固定提交`199b7d0e1fd95e7b3eafa8c15eca692534142427`。官方创作正文外部取得，运行映射独立组装，调用关系见[h3-skill-adaptation.md](h3-skill-adaptation.md)。
- ComfyUI模型执行、权重、当前画布和限制见`comfyui-local-workflows`；Blender由`blender-core`及动画/渲染/仿真模块承接。
- CapCut云端与本地桌面路线按当前插件/桌面能力分别执行，工具规则以正在使用的版本为准，保存草稿与导出成片分开验收。
- Flova仅作可选风格参考，阅读入口与可用范围见[style-reference.md](style-reference.md)，不安装为系统必需Skill。

## 行业工序参考

| 来源 | 用途 |
|---|---|
| [Adobe Video Production](https://www.adobe.com/creativecloud/video/production.html) | 开发、前期、拍摄/镜头覆盖与后期职责链 |
| [Toon Boom Animatic](https://learn.toonboom.com/modules/animatic) | 真实时长的动态分镜、对白与节奏验证 |
| [Runway Image References](https://help.runwayml.com/hc/en-us/articles/40042718905875-Creating-with-Gen-4-Image-References) | 先准备主体、场景和构图，再进入运动的制作思路；不迁移其专有模型上限 |
| [Blackmagic官方培训](https://www.blackmagicdesign.com/products/davinciresolve/training) | 剪辑、特效/遮罩、调色、声音与交付分工；不强制安装DaVinci |
| [Blender手册](https://docs.blender.org/manual/en/5.2/) | 相机、动画、跟踪/遮罩、合成与渲染；操作以实际安装版本接口为准 |
| [H3 Fun Union2.0](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union-2.0)、[Qwen Fun Union](https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union)、[Next-Scene](https://huggingface.co/akhaliq/Qwen-Image-2.1-Next-Scene-LoRA) | 结构控制与静帧故事板；执行细节在ComfyUI扩展参考，不视为任意长链自动无缝保证 |

参考资料支持方法选择，不表示每项组合、风格或整部影片均已实测。[工程验证](../../../docs/validation.md)区分历史模型记录与宿主检查。

## 2026-11-10 提示词与制作工序核对

本轮对照可公开读取的官方生成指南及专业后期方法。开发/剧本、视觉定稿与角色多视图、动态分镜/预演、逐镜选路、挑片返工、合成、色彩、声音、剪辑、导出与播放检查已有对应章节；新增重点是详细提示词及风格转译、批量前完整链路试片、镜头送修后的正确回套，不重写一套重复的总流程。

| 直接核对的来源 | 采用与适用边界 |
|---|---|
| [Runway Image to Video Prompting Guide](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide) | 首帧提供视觉依据，文字展开动作/相机/环境变化及时间过程；检查起始图的运动暗示。其Gen-4.5写法不替代H3官方结构 |
| [Runway Video Prototyping](https://runway.com/resources/video-prototyping)（2026-10-12）、[AI Previs](https://runway.com/resources/ai-previs)（2026-08-28） | 只对不确定动作/机位等做动态试片，其余可用占位；粗分镜转为实际生成关键帧时升级质量检查。生成预演传达意图，精确几何/物理仍交Blender等确定性路线 |
| [Google Veo 3.1提示指南](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) | 将摄影、主体、动作、环境和风格具体化；角色/场景参考、关键帧及声音各有职责。仅借导演方法，不移植其片长、接口或对白格式 |
| [Adobe Firefly生成与时间线](https://helpx.adobe.com/firefly/web/firefly-video-editor/generate-videos/generate-video-using-firefly-models.html) | 图片、首尾帧、构图与运动参考是不同制作条件，部分组合有界面/模型限制；本地仍核对现有节点，不能据此宣称支持任意控制组合 |
| [Frame.io回套方法](https://blog.frame.io/2019/03/29/conforming-with-resolve/) | 正式素材/代理、参考剪辑、源范围与返回版本逐帧核对；这是稳定的后期方法参考，不要求安装其服务或强制某种工程交换格式 |
| [Toon Boom前期与Animatic](https://learn.toonboom.com/modules/animation-workflow/topic/pre-production)、[Adobe制作流程](https://www.adobe.com/creativecloud/video/production.html) | 再核对设计/色彩依据、对白和真实时长分镜、生产与后期职责；补明临时声音到正式表演/口型依赖的版本切换，相关环节按项目规模使用 |

本项目自写提示示例用于说明细致程度，不是上游模板复制或已实测样片。H3基础/参考正文继续从固定官方技能读取；类型/Flova风格仅按实际已读范围采用，用户审美优先。没有因此安装Runway、Veo、Adobe云工具或改变本地模型路线。

更新时确定上游提交和文件清单，比较官方正文与本地overlay，审查许可和工具变化，只合入需要的改动；保留项目风格、参考和已认可素材。依赖版本在工程lock维护，总流程不再复制具体采样表或安装脚本。
