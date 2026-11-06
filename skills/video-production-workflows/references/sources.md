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

更新时确定上游提交和文件清单，比较官方正文与本地overlay，审查许可和工具变化，只合入需要的改动；保留项目风格、参考和已认可素材。依赖版本在工程lock维护，总流程不再复制具体采样表或安装脚本。
