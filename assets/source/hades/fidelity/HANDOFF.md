# 哈迪斯补画交接

游戏资源 ID 为 `ragnarok_hades`。逻辑格 [216, 168]，脚点 [98, 148]。
冥府铁槌按 2×2 网格重出。头部像素来自包内对应形态的待机参考帧，随动作平移和转动。
逻辑图集旁的 _hd.png 是按 hd_multiplier 最近邻放大后的版本。朝右绘制，镜像时 X 偏移也翻转。
动作时长和事件时序沿用 v3。演员位移记录在 placement_changes，特效挂点、偏移和有效帧见 fx_events。

## 冥府铁槌

动作轨 `skill`，8 帧。

- 第 3 帧，0.210 秒，`jump_start`。
- 第 5 帧，0.380 秒，`ground_break`。
- 第 5 帧，0.380 秒，`air_edge`。
- 第 5 帧，0.380 秒，`contact`。
- 第 6 帧，0.443 秒，`recover`。

## 特效

- 落枪爆地，轨 `ground_break`，挂层 `actor_ground`，逻辑偏移 [42, 0]。
- 向前风刃，轨 `air_edge`，挂层 `projectile`，逻辑偏移 [48, -20]。
