# 佐佐木小次郎 · 美术及语音交接

资源 ID 为 `ragnarok_kojiro`。按第一季第三回合制作年长造型。前半用备前长光单刀，二天岩流动作持两柄颜色和长度有区分的刀。单刀 8 个动作各 8 帧，另有双刀待机 8 帧。角色格 256×256，脚底基准点 (128, 232)，镜像轴 x=128。跑步第 3、7 帧底边抬 2 px。

## 资源

- `runtime/sprites/*_native#sheet.png` 加匹配的 `#anim.fanim` 为 256 px 图集。无 `_native` 后缀的同组为 512 px，严格最近邻 2 倍。分辨率和游戏内 PPU 独立，维持与同组英雄一致的屏幕尺寸。游戏内接入及镜像待验证。
- `ragnarok_kojiro` 为主动作。 `ragnarok_kojiro_niten` 提供双刀待机，`ult` 使用双刀。切换形态的条件和持续时间由 Claude 处理。
- `ragnarok_kojiro_fx` 是燕返刀光、预判涟漪、双刀交错、金属命中四组独立图集，每组 8 帧，效果图中心 (128, 128)。
- `runtime/icons` 为四张 256 px 图标，选人插画为 1216×1428，选人运行图为 304×405。
- `audio` 提供日语角色剪辑与战斗音效、WAV、MP3 及来源和时间表。语音剪自山路和弘官方单角色倒计时。
- `review/review.html` 可播放，逐帧，切换正反向和背景，听语音、看特效和插画。 `review/checks.csv` 记录每格边界和哈希。

## 动作与触发点

具体技能数值、伤害、命中条件、目标预测和 AI 由 Claude 实现。 `cues.json` 的时刻均以动作起点计，锚点为 256 逻辑格。格斗中确认命中的火花、金属声跟目标走。

| 动作 | 画面及音效 |
| --- | --- |
| 普攻 | 单刀。第 4 帧出刀，接普通斩击音和确认命中。 |
| 燕返 | 第 4 帧向前斩下，第 6 帧反刃上撩。沿用刀光动画并在第二段命中时接火花。 |
| 千手无双 | 第 3 帧到预判段，侧避并回防。预判涟漪在身体中心。 |
| 二天岩流 | 双刀交替。第 4 帧出刀，第 6 帧交错。用双刀刀光，命中事件单独触发。 |

[第一季官方人物设定](https://ragnarok-official.com/1st/character/) · [燕返](https://ragnarok-official.com/1st/story/ep10/) · [断刀与二刀](https://ragnarok-official.com/1st/story/ep11/) · [二天岩流](https://ragnarok-official.com/1st/story/ep12/) · [官方日语语音](https://ragnarok-official.com/1st/news/127/)

