# UE 工程与运行时

默认 native UE5，复用实际安装版本和合适游戏模板。模板是起点，不是最终游戏；不要自动引入整套大型示例或收费插件。First Person、Third Person、Top Down、Paper2D 等按本项目选路，玩法并不由模板名称决定。

## 工程与自动化

- 在用户指定项目目录保存 `.uproject`、Config、Content、需要的 Source/Plugins 与项目记录。明确引擎关联和必要插件，先得到可启动的最小工程和构建。
- 以 Blueprints 或 C++ 实现游戏运行时，按复杂度混合；Python/MCP 是编辑器制作工具，不能代替打包后运行逻辑。
- 在已授权项目中用用户选定 `unreal-mcp` 发现当前工具。编译蓝图/脚本、保存资源、运行并检查返回值；生成一段 Python 或 JSON 不能算生成了对应 UAsset。
- 实际读取`unreal-mcp`及当前项目相关的已有Agent Skill；工具发现、保存恢复点、编译/PIE和调用细节按其当前规则处理。本总流程只给功能/资产要求并核对回接结果，不另维护固定工具schema。
- 无 live MCP 时按官方编辑器自动化/命令行能力处理可执行部分；有 GUI 工作需要时使用现有 computer-use 能力。接口必须实际可用，不能用“应该支持”声称工程已写入。
- C++ 改动按版本匹配 VS/SDK，检查编译日志。Live Coding 与完整构建的适用边界不同；结构变化或失败时采用可恢复的项目级完整重建，不反复杀归属不明进程。

调用超时或失联时先核对对象、保存状态和日志，确认操作是否已经生效，再恢复/重试；不能直接换接口重复创建资源。未知状态不标成功，相关失败修复后再继续依赖步骤，独立工作可继续。

## 功能结构

把玩家输入、移动、镜头、交互、角色状态、动画、AI、UI、音频、存档与内容数据分开组织，使用清楚接口和事件。组件/数据资产/数据表按复用需求引入；小项目不为“架构完整”强行上 GAS、复杂框架或联机系统。

Enhanced Input 明确动作与映射环境，覆盖键鼠/手柄实际支持范围、暂停与菜单焦点、重绑定和输入丢失。角色移动用引擎适合的移动/碰撞系统，按帧率独立方式处理连续行为。只有确需连续更新的对象 Tick，避免每个角色每帧扫描整个场景。

## 镜头与控制

第一人称验证 FOV、鼠标灵敏度、俯仰限制、身体/手部显示、近墙裁剪；第三人称验证跟随、肩位、避障、转身/锁定和目标遮挡；俯视验证缩放、边缘移动/拖动、选择、命令、相机与世界坐标映射。不要把不可达或被 UI 遮挡的位置当有效命令。

重映射、相机反转、晃动/运动模糊可调项按项目需要提供，默认值由参考与试玩确定。避免用强后处理掩盖控制问题。

## 物理与交互

以 collision channel、object type、query/physics response 明确玩家、环境、可拾取物、弹体、交互检测的关系。复杂可视网格与简单碰撞代理分开；静态三角网格和动态刚体的可用方式不同。

常见交互先定义状态、条件和结果：可用/被持有/移动中/锁定/损坏/消耗；用稳定实例标识关联 UI 和存档。拾取、开门、推拉、开关、使用道具或触发任务按本项目选择，不默认全部实现。

高速物体用合适的 trace/sweep 或 CCD，检查不同帧率下穿透、重复命中、生成在墙内、拾取后碰撞、释放弹飞和恢复。质量、惯性、阻尼、约束和单位应合理；不是给所有物体勾选 Simulate Physics 就完成物理。

联机项目还要确定服务端权威、所有权、复制、预测/校正、交互去重及网络延迟测试；本机单人通过不能算联机通过。

## AI、导航与游戏状态

先定义可观察行为和失败恢复，再选 AIController、Behavior Tree/Blackboard、StateTree 或小型状态机。按需要配置 NavMesh、agent 尺寸、可走区域、动态障碍和导航链接；“直线追踪目标”不代表可靠寻路。

测试走不通、卡角、失去目标、目标不可达、角色死亡/禁用、存档恢复与多角色拥堵。俯视游戏的大量单位根据规则选择分组命令、局部避让、阵型或网格系统；不将普通人形 NavMesh 当作所有 RTS 的完整方案。

生命/资源、目标、任务、物品、对白和进度按需求建立数据与状态机。避免仅用场景对象名字或临时引用当长期身份。

## 存档、设置与完整体验

明确需要保存的字段、格式版本、稳定 ID、默认值与失败恢复。测试新游戏、保存、退出、重启读取、检查点和对象状态恢复。UI 显示“已保存”前确认真实写入；不要只在内存里存一份变量。

图形/音量/控制等设置实际应用并持久化；重开验证。完成/失败/重试/返回菜单/退出路径按用户范围接通。教程引导和必要提示使用真实输入状态，不写死和键位设置冲突的文本。

来源：[UE 模板](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-templates-reference)、[Enhanced Input](https://dev.epicgames.com/documentation/en-us/unreal-engine/enhanced-input-in-unreal-engine)、[Gameplay Framework](https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-framework-in-unreal-engine)、[碰撞](https://dev.epicgames.com/documentation/en-us/unreal-engine/collision-in-unreal-engine---overview)、[导航](https://dev.epicgames.com/documentation/en-us/unreal-engine/navigation-system-in-unreal-engine)、[存档](https://dev.epicgames.com/documentation/en-us/unreal-engine/saving-and-loading-your-game-in-unreal-engine)、[编辑器 Python 边界](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)。
