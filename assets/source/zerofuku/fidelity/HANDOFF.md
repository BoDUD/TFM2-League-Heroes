# 零福补画交接

游戏资源 ID 为 `ragnarok_zerofuku`。逻辑格 [144, 112]，脚点 [65, 99]。
斧爻岚阵按 3×3 网格重出。头部像素来自包内对应形态的待机参考帧，随动作平移和转动。
逻辑图集旁的 _hd.png 是按 hd_multiplier 最近邻放大后的版本。朝右绘制，镜像时 X 偏移也翻转。
动作时长和事件时序沿用 v3。演员位移记录在 placement_changes，特效挂点、偏移和有效帧见 fx_events。

## 斧爻岚阵

动作轨 `skill2`，8 帧。

- 第 4 帧，0.312 秒，`axe_burst`。
- 第 5 帧，0.377 秒，`flying_blade`。
- 第 7 帧，0.529 秒，`recovery`。

## 特效

- 斧爻裂开黑气，轨 `axe_burst`，挂层 `actor_behind`，逻辑偏移 [9, -45]。
- 追踪黑刃，轨 `flying_blade`，挂层 `projectile`，逻辑偏移 [27, -23]。
