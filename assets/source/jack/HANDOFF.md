# 开膛手杰克 · 高清像素素材交接

资源 ID `ragnarok_jack`。按第二季造型重画，保留酒红礼帽、白羽、单片镜、银色翘须和黑手套。8 个动作各 8 帧。普攻与扇形飞刀完整覆盖持刀、离手和收势，飞出的实体刀与刀光使用独立资源。撤退防御会展开酒红雨伞。黑手套触物和收招的特效分别交付。

- `runtime/sprites/ragnarok_jack_native#sheet.png` 与同前缀 `#anim.fanim` 是主要接入组。每格 256×256，脚底基准 (128, 232)，镜像轴 x=128。跑步第 3、7 帧腾空抬 2 px。无 `_native` 后缀的同组图集每格 512×512，为整倍数最近邻导出。游戏中视觉大小仍由 PPU 决定。
- `ragnarok_jack_fx` 带 8 组 × 8 帧，独立特效中心 (128, 128)。`runtime/props/knife.png` 可作为游戏投射物，右指向。雨伞安放参考在 `runtime/props/umbrella.png`，展开动作已经含实际持伞。
- `cues.json` 是演出时点，从该动作首帧 0 ms 起算，锚点为 256 逻辑格。投射物创建、命中火花、伤害和移位由实际战斗系统触发。用相同表驱动左向时镜像。
- `runtime/icons` 为四张 256 px 技能图标，`runtime/jack_card.png` 为 1216×1428 插画，`banpick_illustrations` 另有 304×405 图。
- `audio` 提供杉田智和官方台词剪辑与独立战斗音效，含原声来源时间码、WAV 和 MP3。保留原录音底音。
- `review/review.html` 支持动作播放、逐帧、左右朝向、深浅底、特效叠加和音效试听。

游戏注册、AI、伤害、投射物速度、控制和 PPU 待 Claude 接入验证。技能演出以现有竞技场为基础，伦敦特色由插画、薄雾和道具呈现。

[第二季官方人物设定](https://ragnarok-official.com/2nd/character/) · [第四回合手套神器设定](https://ragnarok-official.com/2nd/story/ep04/) · [杉田智和官方倒计时原声](https://ragnarok-official.com/2nd/special/countdown1/)
