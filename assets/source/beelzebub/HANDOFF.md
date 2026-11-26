# 别西卜 · 素材交接

资源 ID 为 `ragnarok_beelzebub`。造型参考《终末的女武神》第三季，黑发、深色高领长袍、双银扣、紫纹长带与阿波弥俄斯骸骨杖贯穿战斗造型。

## 资源和坐标

- `runtime/sprites/` 包含 8 组角色动作和 8 组独立特效，每组 8 帧。沿用特斯拉素材包的 256×256 逻辑单格与 512×512 HD 单格，精确最近邻 2×。使用同版本的 `#sheet.png` 与 `#anim.fanim`。
- 默认朝右。逻辑脚底锚点 (128, 232)，特效中心 (128, 128)，HD 坐标乘 2。游戏内显示比例由 Claude 接入 PPU。
- 角色图集已包含骸骨杖。独立器物原图在 `runtime/props/apomyius.png`。`staff-registration.json` 记录同一根直杖的轴线、103 逻辑像素长度和逐帧握点、角度以及像素校验值。掉杖后位置在最后四帧锁定。镜像整个角色格即可保持反向握点。
- `reference/master.png` 为透明造型基准。选人插画 `runtime/beelzebub_card.png` 为 1216×1428，游戏选人图为 304×405。四张技能图标各 256×256。

## 技能挂接

| 动作 | 帧与表现 |
| --- | --- |
| `attack` | 右手振动斩，第 4 帧释放。挥击和确认命中分别有特效与声音。 |
| `skill` | 骸骨杖强化的暴食的堕天使。第 4 帧从杖头放出主波，第 5 帧叠加扩散环。预览使用示例坐标，实战波形应挂到投射或范围中心。 |
| `skill2` | 左手持杖格挡，第 3 帧展开地狱之门的振动屏障。示例在第 5 帧出现格挡涟漪，实战由真实格挡回调触发。 |
| `ult` | 虚神〈混沌〉。第 3 帧黑核开始压缩，第 5 帧爆发为大范围振动。 |
| `dead` | 第 5 帧骸骨杖脱手落地，第 7 帧身体接地，各有独立音效。 |

`cues.json` 采用从 1 开始的帧序号和动作起点的累计毫秒数。按实际命中位置挂接 `confirmed_hit` 和 `confirmed_block`。格挡语音可接 `voice_guard`。

## 审阅和音频

- `review/review.html` 可以连播、逐帧、切换深浅背景与朝向、查看独立或叠加特效和试听。
- 5 条浪川大辅的日语动画原声来自官方公开视频，保留原片部分音乐或环境音。台词、来源和时间范围在 `audio/sources.json`。另有 16 条原创战斗音效，均提供 44.1 kHz 单声道 WAV 和 MP3。
- Claude 接手角色注册、PPU、技能判定、伤害与格挡、AI 和实战验证。

[官方角色图与配音](https://ragnarok-official.com/chara/beelzebub.html) · [振动能力](https://ragnarok-official.com/story/08.html) · [虚神参考](https://ragnarok-official.com/story/10.html) · [Netflix Japan 对战片段](https://www.youtube.com/watch?v=Yv7wxDqS6vI)
