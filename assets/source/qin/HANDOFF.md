# 秦始皇 · 高清素材交接

角色资源 ID 为 `ragnarok_qin`。造型采用动画第三季的白眼罩、红纹、金指爪和红金外袍。承力天凤在动作中短暂显示神罗铠袖，大招在显剑阶段暂时摘下眼罩并在收招时回到待机造型。这两处是 Mod 的动画编排。

- 8 组角色动作，每组 8 帧。8 组独立特效，每组 8 帧。原始单格 256×256，HD 单格 512×512，严格最近邻整数倍放大。角色朝右，原始脚底锚点 (128, 232)，特效中心 (128, 128)。HD 版锚点乘 2，实际大小由游戏接入时的 PPU 定。
- `runtime/props/goujian.png` 是始皇勾践剑的直轴母版。`sword-registration.json` 保存大招持剑帧的握点、角度及长度。剑的柄、护手和剑身共用同一个刚体旋转。原身体帧保留握剑拳形，合成时手掌在柄前面。
- `cues.json` 列出指爪出手、波流龟气弹、神罗铠袖护势、承力、回推、勾践剑显形和释放等素材事件。预览会展示命中效果。实际接入时将 `confirmed_hit` 和 `confirmed_block` 绑定服务器或战斗逻辑确认的目标位置。气弹飞行的方向、速度和碰撞由 Claude 对接。
- 选人插画 1216×1428，运行选人图 304×405，四张技能图标各 256×256。
- `audio/sources.json` 记录石川界人原声切点、出处和 WAV／MP3 摘要。原片部分保留背景配乐或音效。指爪、格挡、回推和斩击另有独立原创音效。
- `review/review.html` 支持逐帧、连播、双朝向、深浅背景、特效叠加和音频试听。

Claude 负责技能逻辑、PPU、角色注册、AI、判定和游戏实测。

[动画人物设定](https://ragnarok-official.com/chara/qinshihuang.html) · [神罗铠袖与武术](https://ragnarok-official.com/story/03.html) · [勾践剑画面](https://ragnarok-official.com/story/06.html) · [Netflix 入场片段](https://www.youtube.com/watch?v=fAgeLsSIvZA) · [Netflix 承力天凤片段](https://www.youtube.com/watch?v=Kaeo8gE_3SM)
