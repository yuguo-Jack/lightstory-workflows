# 本机执行映射

此模块决定界面的行为与规格，具体调用按工程和当前接口执行。不为使用设计方法安装另一套引擎，或直接复制不同引擎的示例API。

| 已选路线 | 执行入口 | 需要落实 |
|---|---|---|
| Unreal | 已安装 Unreal Engine Skills for Codex 的 unreal-mcp，先确认当前项目连接 | UMG或项目已有UI系统；按需求选CommonUI，锚点/布局与DPI、焦点、输入模式、暂停/恢复、状态绑定及打包资源 |
| Web | game-studio:game-studio → game-studio:game-ui-frontend，并配合当前Phaser/Three.js/R3F路线 | 游戏画布与界面布局、事件传递、键鼠/手柄/触控、浏览器缩放、安全区、输入穿透与正式构建 |
| Blender/ComfyUI视觉素材 | blender-core / comfyui-local-workflows，使用项目资产分工 | 只制作确实需要的图标、背景、立绘、预渲染动效等；交回真实格式/尺寸/Alpha/版本，再接入运行端 |

UE的设计名词不是“已经写入工程”的证据。按当前live工具schema、工程源码和对应版本文档创建或修改，再保存、编译/导入并检查运行。Web由Game Studio接管实际实现，不能只引用插件名字后停止。

unreal-skill用于创建或维护UE项目自己的AgentSkill资源，不是普通UMG/界面制作入口；只有用户任务确实涉及这种资源时才使用。

资源与测试输出留游戏项目；正式模型/工具环境继续使用现有原生位置。制作期缓存清理沿用[总流程空间规则](../../game-production-workflows/references/project-operations.md)，不复制整套模型或把项目素材写进全局Skill。

官方入口：[UMG](https://dev.epicgames.com/documentation/en-us/unreal-engine/umg-ui-designer-in-unreal-engine)、[CommonUI](https://dev.epicgames.com/documentation/en-us/unreal-engine/common-ui-plugin-for-advanced-user-interfaces-in-unreal-engine)。需要准确参数时以本机安装版本与可用接口为准。
