# 哈迪斯 · 高清素材交接

资源 ID 为 `ragnarok_hades`。白外套、银发和蓝额纹来自动画第三季设定。常态保留白外套，Mod 的强化枪动作暂时采用无袖战斗服，收招恢复常态。

- 8 组角色动作与 8 组独立特效，每组 8 帧。原始单格 256×256，HD 单格 512×512，最近邻整数倍放大。面朝右，脚底锚点 (128, 232)，特效中心 (128, 128)，HD 坐标乘 2。实际显示尺寸由 Claude 接入 PPU。
- `runtime/props/bident.png` 为双叉枪完整图。 `runtime/props/desmos.png` 共用同一根枪杆和轴线，枪头加宽为单尖德斯莫斯。 `spear-registration.json` 记录各帧握点和枪形。双手持枪的角度以两只手决定，武器和效果可以独立预览。
- 大招显形点从第 3 帧起换成强化枪头，第 5 帧出刺。 `cues.json` 包含出手、枪头强化、实际命中、双叉枪落地和身体接地时点。实际战斗中的 `confirmed_hit` 接到命中回调，位置使用真实目标锚点。
- 选人插画 1216×1428，运行选人图 304×405，技能图标 4 张，各 256×256。
- `audio/sources.json` 记有置鮎龍太郎的日语原声片段、切点和校验值。保留原视频部分配乐和环境音，挥刺、命中、强化、双叉枪落地等战斗音效为原创。全部音频提供 WAV 和 MP3。
- `review/review.html` 提供连播、逐帧、双朝向、深浅底、独立与叠加特效、音频试听。

Claude 对接角色注册、技能参数、伤害判定、AI、PPU 和实战验证。

[官方人物设定](https://ragnarok-official.com/chara/) · [枪头强化参考](https://ragnarok-official.com/story/05.html) · [强化枪突刺](https://ragnarok-official.com/story/06.html) · [Netflix Japan 对战片段](https://www.youtube.com/watch?v=Kaeo8gE_3SM) · [Netflix Japan 发布片段](https://www.youtube.com/watch?v=YuEA2X8f_Pg)
