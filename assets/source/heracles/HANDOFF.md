# 赫拉克勒斯 · 动画素材交接

资源 ID `ragnarok_heracles`。常态持银白狮头巨棒，御业形态以双拳近战，沿用角色骨架、皮裙和脚底比例。条纹纹样从右臂和侧腹蔓延到脸、双臂与躯干，御业形态增加肩背骨爪。

- 常态 8 个动作 × 8 帧。其中 `ult` 是第十二御业的过渡动作，第 5 帧起切到空手形态。御业形态另有 8 个动作 × 8 帧。状态触发条件、持续时间、消耗和效果由 Claude 接入。
- `runtime/sprites` 中的 `*_native#sheet.png` 和匹配的 `#anim.fanim` 为 256 px 格。无 `_native` 后缀的对应图集为精确最近邻 512 px 格。坐标以动画表为准，跑步第 3、7 帧抬高 2 px，脚底锚点 (128, 232)，默认朝右，镜像轴 x=128。游戏 PPU 和实机注册待验证。
- `ragnarok_heracles_fx` 含 8 组独立特效，每组 8 帧。中心 (128, 128)。其中棒风与确认命中分开，变身环独立于模型。 `cues.json` 按形态列出帧编号、毫秒、特效锚点和音效事件，确认命中时可将对应特效跟随目标。
- `runtime/icons` 有四张 256×256 图标，插画提供 1216×1428 原图尺寸的交付版本以及 304×405 选人切图。插画右手的握柄、柄尾和狮头中心已按同一斜轴重画。
- `audio` 有小西克幸的日语原声和独立战斗音效，同步提供 WAV、MP3 和来源时间码。
- `review/review.html` 可播放或逐帧检查两套动作，可单看特效或叠加出招效果，也可试听原声和音效。格边界和 SHA-256 见 `review/checks.csv`。

[第二季人物设定](https://ragnarok-official.com/2nd/character/) · [十二御业的初次施展](https://ragnarok-official.com/2nd/story/ep02/) · [第十二御业](https://ragnarok-official.com/2nd/story/ep04/) · [官方语音](https://ragnarok-official.com/2nd/special/countdown1/)
