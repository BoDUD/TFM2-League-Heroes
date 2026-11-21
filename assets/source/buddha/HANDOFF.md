# 释迦 · 高清素材交接

资源 ID 为 `ragnarok_buddha`。造型参照动画第二季，银灰发髻、粉色眼镜、深蓝背心、白色兔纹、白紫下装和金色披带贯穿动作。普攻使用六道棍。枪刃和观音盾是六道棍的技能造型。大招将第 15 话的七枝神器大圆寂刀·零独立表现为显形和斩击，保留常态服装以方便回到战斗循环。

- 角色和特效各有 8 组、每组 8 帧。运行图集每格 512×512，`_native` 图集每格 256×256。两者采用最近邻整数倍缩放。默认朝右，脚底锚点为 (128, 232)，特效中心为 (128, 128)，512 版坐标乘 2。PPU 按游戏中的实际身高调节。
- `cues.json` 列出出招、命中、格挡、显形和落地的帧号及毫秒。资产预览演示每个 cue。接入时只有判定成功才触发 `confirmed_hit` 或 `confirmed_block`，锚点改为真实接触目标。
- 攻击与技能自带持械像素。横扫、未来视、撤步、挡击、涅槃剑显形和斩击的效果可独立播放。技能数值、目标、判定和 AI 由 Claude 确定。
- 选人插画 1216×1428，运行选人图 304×405，四张技能图标各 256×256。
- `audio/sources.json` 记录中村悠一官方日语录音的源帖、切点及 WAV／MP3 文件校验值。语音包含两段短版和一段仅供试听的宣传收尾。独立音效已拆分为起手、挥出与实际命中等事件。
- `review/review.html` 支持连播、逐帧、镜像、切深浅底、单独或叠加特效、试听。游戏内资源注册、PPU、技能状态及判定留给 Claude 接入验证。

[官方人物设定](https://ragnarok-official.com/chara/buddha.html) · [第 12 话](https://ragnarok-official.com/2nd/story/ep12/) · [第 13 话](https://ragnarok-official.com/2nd/story/ep13/) · [第 15 话](https://ragnarok-official.com/2nd/story/ep15/) · [中村悠一官方原声](https://twitter.com/ragnarok_PR/status/1646660788990476289)
