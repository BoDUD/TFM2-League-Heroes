# 雷电为右卫门 · 高清素材交接

资源 ID `ragnarok_raiden`。造型参考动画第二季，保留白鬓、扇形束发、深蓝膝带和红色肌肉拘束纹。角色采用紫色廻搭配不透明深蓝运动短裤。

- 主图集含 8 个动作，每个 8 帧。另附 `muscle_release` 解放过渡 8 帧，接入时可在原角色图集和过渡图集之间切换。此片段可供技能或入场使用，持续状态由实际玩法决定。
- `runtime/sprites/*_native#sheet.png` 和对应动画表为 256 格。无 `_native` 的同组图集为 512 格、严格最近邻两倍导出。脚底锚点 (128, 232)，镜像轴 x=128，跑步第 3、7 帧抬高 2 px。PPU 与贴图格尺寸分开配置，换算以实机为准。
- `runtime/sprites/ragnarok_raiden_fx_native#sheet.png` 含 8 组独立特效，每组 8 帧，中心 (128, 128)。演出帧与特效挂点见 `cues.json`。确认命中的火花和音效应由实际命中事件触发。
- 四股第 3 至 4 帧抬足，第 5 帧落地。连掌第 4、6 帧分别出掌。八咫乌第 3 帧蓄劲，第 5 帧出掌。
- `runtime/icons` 的图标每张 256×256。选人插画为 1216×1428，附 304×405 选人图。
- `audio` 的木村昴日语剪辑来自官方单角色倒计时。附 WAV、MP3 和原始时间码，战斗音效为独立制作。
- `review/review.html` 可连播、逐帧、翻向、切深浅底、叠加特效和听音频。

玩法、目标与伤害判定、状态时长、AI 和实机 PPU 由 Claude 接入验证。

[第二季官方角色设定](https://ragnarok-official.com/2nd/character/) · [神器与肌肉控制](https://ragnarok-official.com/2nd/story/ep08/) · [八咫乌](https://ragnarok-official.com/2nd/story/ep10/) · [木村昴官方原声](https://ragnarok-official.com/2nd/special/countdown1/)
