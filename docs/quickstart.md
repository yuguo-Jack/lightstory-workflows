# 快速使用与顺序

完成[安装](installation.md)后，新开代理会话选择总入口。可以直接说明剧本/玩法、审美样例、规格、交付与工作目录，普通技术缺项由执行者按流程补齐。已有项目先恢复状态，不重新生成已认可素材。

## 视频

1. 用户给剧本/核心信息、风格参考、时长、比例、交付分辨率和声音要求。
2. Video总流程锁定要求，按需Qwen视觉开发，再做可播放时长的分镜/animatic和难点试片。
3. 按镜头选H3模式、普通/Turbo/Flex、Blender实际CG、结构引导或后期，逐镜制作与检查。
4. 做剪辑/合成/对白/配乐/拟音/调色/字幕，导出实际文件，完整观看后交付。

详见[Video方法](video-workflow.md)；模板在`skills/video-production-workflows/assets`。

## 游戏

1. 用户给玩法、视角/控制、平台、目标画质/帧率、范围与审美样例。
2. Game总流程决定Web或Unreal执行路线、验证核心循环与可玩灰盒。
3. 先做目标品质的垂直切片，明确哪些素材用生成、Blender、引擎或现有库；再扩大生产。
4. 集成人物/动作/碰撞/交互、关卡、UI、声音、存档等，测试性能、打包和真实试玩。

详见[Game方法](game-workflow.md)；模板在`skills/game-production-workflows/assets`。

## 单项生成

```powershell
python tools/lightstory.py workflows list --model 'Qwen-Image 2.1'
python tools/lightstory.py workflows show 'Qwen-Image 2.1/02_单图编辑'
```

从show读取当前真实节点ID和输入，制作覆盖JSON；不要照抄另一份画布的ID。准备时传项目内绝对路径：

```json
{"实际LoadImage节点ID":{"image":"已经上传并能在当前选择器选中的图片.png"}}
```

```powershell
python tools/lightstory.py workflows prepare 'Qwen-Image 2.1/02_单图编辑' --overrides '<项目绝对路径>/overrides.json' --prefix 'Projects/my-project/image-edit' --out '<项目绝对路径>/request.api.json'
```

准备工具拒绝残留`UPLOAD_*`、错误节点/输入、目录越界及覆盖正式模板，且不会提交推理。执行者按Comfy Skill把准备好的`prompt`对象POST到当前服务，保存`prompt_id`、查询history并检查实际产物。用户要求生成时不能在prepare后就停止；超时先找已有任务，避免重复提交。

## 创建项目资料

```powershell
python tools/lightstory.py project init --kind video --name my-film
python tools/lightstory.py project init --kind game --name my-game
```

可用`--path`指定用户项目目录；已有目录不覆盖。新项目只是简报/状态/目录脚手架，不算已经制作成片/游戏。按任务规模裁剪文档，但保留素材、版本、未决问题、实际产物与下一步。
