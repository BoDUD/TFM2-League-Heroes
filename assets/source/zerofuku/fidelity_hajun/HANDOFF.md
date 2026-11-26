# 波旬补画交接

游戏资源 ID 为 `ragnarok_zerofuku`。逻辑格 [144, 112]，脚点 [65, 99]。
魔廻天衝、灼按 3×3 网格重出。头部像素来自包内对应形态的待机参考帧，随动作平移和转动。
逻辑图集旁的 _hd.png 是按 hd_multiplier 最近邻放大后的版本。朝右绘制，镜像时 X 偏移也翻转。
动作时长和事件时序沿用 v3。演员位移记录在 placement_changes，特效挂点、偏移和有效帧见 fx_events。

## 魔廻天衝

动作轨 `h_skill`，8 帧。

- 第 2 帧，0.115 秒，`transfigure`。
- 第 4 帧，0.315 秒，`drill_launch`。
- 第 7 帧，0.535 秒，`recovery`。

## 灼

动作轨 `h_ult`，8 帧。

- 第 2 帧，0.125 秒，`sword_form`。
- 第 5 帧，0.440 秒，`sword_drop`。
- 第 5 帧，0.440 秒，`contact`。

## 特效

- 黑钻头，轨 `drill_launch`，挂层 `projectile`，逻辑偏移 [32, -23]。
- 大剑竖劈，轨 `sword_drop`，挂层 `actor_front`，逻辑偏移 [28, -19]。
- 重斩接触光，轨 `sword_hit`，挂层 `target_contact`，逻辑偏移 [0, 0]。
