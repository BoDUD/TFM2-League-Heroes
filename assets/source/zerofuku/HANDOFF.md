# 零福／波旬 · 高清素材交接

一个英雄名额。零福和波旬共用朝右的锚点。双形态各 8 组动作，每组 8 帧。两张选人插画各为 1216×1428，两张运行选人图分别为 304×405，四张技能图标各为 256×256。

- 常态资源为 `ragnarok_zerofuku`，波旬为 `ragnarok_zerofuku_hajun`。常态 `ult` 是吞没至破茧的 8 帧过渡。第 6 帧已出现波旬造型，播放完毕衔接 `h_idle`。形态触发条件、持续时间、是否可回退由 Claude 在玩法接入时确定。
- 零福的 58 个有斧画面共用 `runtime/props/misery_cleaver.png` 的直轴斧爻。重斧扩大斧刃时，柄轴和斧头的接点保留在同一直线上。怨气冲击第 3–6 帧横持，倒地第 4–8 帧保持同一落地位置。`axe-registration.json` 记录作者校准的握点和角度。波旬的臂刃、魔钻从前臂延伸，角色帧已包含这部分身体造型。魔钻光圈、斩击、命中、怨气和碎壳均采用独立特效层。
- `runtime/sprites` 两个角色图集和一个特效图集，原始单格 256×256，HD 单格 512×512，严格最近邻 2 倍放大。脚底锚点 (128, 232)，面朝右，镜像轴 x=128，特效以 (128, 128) 为中心。HD 图集锚点相应乘 2，实际游戏尺寸由 PPU 定。
- `cues.json` 使用像素坐标和帧时覆盖分阶段出手、命中、放出钻击与破茧。把 `confirmed_hit` 绑定至实际目标命中。预览按节拍表现所有相应 cue。
- `audio/sources.json` 为日语音频、原始切点、说话人和事件文件的清单。零福语音来自第四弹官方预告。波旬语音来自第 15 话公开转贴的原声片段，保留原背景音和伴奏。横砍、实际命中、落斧、聚集、钻击、破茧等效果另提供原创音效，均附 WAV 和 MP3。
- `review/review.html` 可切换两种形态、连播、逐帧、切深浅底、向左镜像、查看独立特效及叠加，并试听交付音频。

Claude 接入验证角色注册、PPU、技能逻辑、判定、AI 和比赛回放。

[官方人物](https://ragnarok-official.com/2nd/character/) · [零福](https://ragnarok-official.com/2nd/story/ep12/) · [波旬破茧](https://ragnarok-official.com/2nd/story/ep14/) · [第四弹官方 PV](https://ragnarok-official.com/2nd/news/606/) · [声优官方特别节目](https://ragnarok-official.com/2nd/news/644/)
