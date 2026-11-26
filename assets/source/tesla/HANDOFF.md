# 尼古拉·特斯拉 · 素材交接

资源 ID 为 `ragnarok_tesla`。机甲参考《终末的女武神》第三季的超人自动机兵 β。铜金外甲、深蓝关节、红铜胸口线圈及青绿背环保持一致。特斯拉以机甲双拳作战。

## 资源和坐标

- `runtime/sprites/` 包含角色和特效各 8 组，每组 8 帧。逻辑单格 256×256，HD 单格 512×512，精确 2× 最近邻。使用同一倍率的一对 `#sheet.png` 与 `#anim.fanim`。
- 角色默认朝右。逻辑脚底锚点 (128, 232)，特效中心 (128, 128)，HD 坐标乘 2。与哈迪斯素材包的单格规格一致，由 Claude 在游戏内按实际比例配置 PPU。
- 特斯拉步第 3～5 帧包含额外离地高度；第 5～7 帧带少量前移，用于表现动作。实际位移、瞬移距离及目标位置由战斗逻辑决定。
- `reference/master.png` 为透明底造型基准。选人插画为 `runtime/tesla_card.png`，1216×1428。选人用图为 304×405。等离子脉冲拳、特斯拉步与瞬移、领域和双电光拳图标各 256×256。

## 技能接入

| 动作 | 此包提供的动画 |
| --- | --- |
| `attack` | 等离子脉冲拳第 4 帧出手。出拳与实际命中各有独立特效和声音。 |
| `skill` | 特斯拉步起跳，第 4 帧离场闪光，第 5 帧到达闪光。若该次仅为特斯拉步，使用起跳与掠行事件。按原作机制在活动中的神之监狱内启用瞬移。将两次闪光挂到实际出发与到达坐标。 |
| `skill2` | 神之监狱第 4 帧开始展开。展开动画播完切换 `zone_idle` 循环，循环跟随固定领域中心。领域尺寸和持续时间由技能配置决定。 |
| `ult` | 借用双向电光拳概念，角色两臂依序出拳；第 4 帧和第 5 帧分别给出两次释放点，并保留双手完整的机甲造型。实战由 Claude 决定如何表现远端打击。 |

`cues.json` 给出自帧起点累计的毫秒数，帧索引从 1 开始。预览使用表内示例锚点，实战中 `confirmed_hit` 由命中回调触发并使用命中世界坐标。`zone_loop` 标记领域保持段，`sfx_zone_loop` 是一次短尾音。真人语音按实战需要接入角色选择、技能和退场事件，另见 `audio/sources.json`。

## 审阅与语音

- `review/review.html` 支持连播、逐帧、深浅底、左右朝向、独立及叠加特效和试听。
- 8 条古川慎日语动画原声来自 Netflix Japan 官方片段，保留少量原声配乐或环境声。16 条机甲、电弧、位移、领域和命中音效为原创。均有 44.1 kHz 单声道 WAV 和 MP3。切点、配音演员、来源及 SHA-256 在 `audio/sources.json`。
- 此分支为素材交接。角色注册、PPU、领域及瞬移条件、伤害判定、AI 和实战验证由 Claude 接入。

[动画人物设定](https://ragnarok-official.com/chara/nikolatesla.html) · [第八话机甲参考](https://ragnarok-official.com/story/08.html) · [第九话特斯拉步](https://ragnarok-official.com/story/09.html) · [Netflix Japan 领域片段](https://www.youtube.com/watch?v=qF3T_NiQ62I) · [Netflix Japan 双拳片段](https://www.youtube.com/watch?v=Yv7wxDqS6vI) · [Netflix Japan 退场片段](https://www.youtube.com/watch?v=-nwMDDgSp_Q)
