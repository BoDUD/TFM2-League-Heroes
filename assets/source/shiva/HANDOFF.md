# 湿婆 · 高清素材交接

资源 ID `ragnarok_shiva`。常态保留第二季的黄额巾、蓝紫肤色、三眼和青蓝几何纹。轮回舞踊燃烧形态采用第 10 话的赤铜肤色和散发。Mod 适配中两种形态都维持完整四臂。

- 常态和燃烧各 8 个动作、各 64 帧。常态 `ult` 为转换动画，第 5 帧（510 ms）起已进入燃烧造型。待过渡播完后可切换到 `ragnarok_shiva_tandava`。这只定义美术节点，触发、持续时间及结束条件由玩法接入确定。
- `runtime/sprites/*_native#sheet.png` 与同名 `#anim.fanim` 每格 256×256。无 `_native` 的同组图集每格 512×512，严格最近邻放大。脚底锚点 (128, 232)，朝右，镜像轴 x=128，两套跑步第 3、7 帧抬高 2 px。实际显示大小按 PPU 接入。
- `ragnarok_shiva_fx` 为 8 组独立效果，每组 8 帧，中心 (128, 128)。`cues.json` 提供出手、点燃、舞步和确认命中时点。接入中命中火花与对应音效绑定实际目标。
- `runtime/icons` 四张 256×256 图标。选人插画 1216×1428，运行图 304×405。
- `audio` 提供铃木达央官方单角色录音的日语切片及独立音效，附 WAV、MP3、来源和时点。
- `review/review.html` 支持切换形态、连播、逐帧、镜像、切深浅底、独立或叠加特效和音频试听。

技能代码、状态切换、判定、AI 和游戏内 PPU 留给 Claude 接入验证。

[动画第二季人物设定](https://ragnarok-official.com/2nd/character/) · [轮回舞踊](https://ragnarok-official.com/2nd/story/ep09/) · [燃烧画面](https://ragnarok-official.com/2nd/story/ep10/) · [铃木达央官方语音](https://ragnarok-official.com/2nd/special/countdown1/)
