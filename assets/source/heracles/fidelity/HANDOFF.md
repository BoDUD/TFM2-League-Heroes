# 赫拉克勒斯补画交接

游戏资源 ID 为 `ragnarok_heracles`。逻辑格 [216, 168]，脚点 [98, 148]。
刻耳柏洛斯突爪按 2×2 网格重出。头部像素来自包内对应形态的待机参考帧，随动作平移和转动。
逻辑图集旁的 _hd.png 是按 hd_multiplier 最近邻放大后的版本。朝右绘制，镜像时 X 偏移也翻转。
动作时长和事件时序沿用 v3。演员位移记录在 placement_changes，特效挂点、偏移和有效帧见 fx_events。

## 刻耳柏洛斯突爪

动作轨 `c_skill2`，8 帧。

- 第 3 帧，0.210 秒，`dash_echo`。
- 第 3 帧，0.210 秒，`rush_start`。
- 第 5 帧，0.335 秒，`triple_claw`。
- 第 5 帧，0.335 秒，`contact`。
- 第 6 帧，0.401 秒，`rush_end`。

## 特效

- 贴地冲刺残影，轨 `dash_echo`，挂层 `actor_behind`，逻辑偏移 [-20, -18]。
- 三道爪痕，轨 `triple_claw`，挂层 `actor_front`，逻辑偏移 [48, -34]。
