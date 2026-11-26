# 吕布补画交接

游戏资源 ID 为 `ragnarok_lubu`。逻辑格 [304, 192]，脚点 [128, 172]。
赤兔天喰按 2×2 网格重出。头部像素来自包内对应形态的待机参考帧，随动作平移和转动。
逻辑图集旁的 _hd.png 是按 hd_multiplier 最近邻放大后的版本。朝右绘制，镜像时 X 偏移也翻转。
动作时长和事件时序沿用 v3。演员位移记录在 placement_changes，特效挂点、偏移和有效帧见 fx_events。

## 赤兔天喰

动作轨 `ult`，8 帧。

- 第 1 帧，0.000 秒，`mounted_entry`。
- 第 2 帧，0.105 秒，`rush_start`。
- 第 5 帧，0.390 秒，`sky_eater`。
- 第 5 帧，0.390 秒，`contact`。
- 第 7 帧，0.526 秒，`rush_end`。

## 特效

- 天喰开天光，轨 `sky_eater`，挂层 `projectile`，逻辑偏移 [78, -48]。
