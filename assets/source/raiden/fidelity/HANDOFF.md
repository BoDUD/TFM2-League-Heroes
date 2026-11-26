# 雷电为右卫门补画交接

游戏资源 ID 为 `ragnarok_raiden`。逻辑格 [216, 168]，脚点 [98, 148]。
狮子舞按 2×2 网格重出。头部像素来自包内对应形态的待机参考帧，随动作平移和转动。
逻辑图集旁的 _hd.png 是按 hd_multiplier 最近邻放大后的版本。朝右绘制，镜像时 X 偏移也翻转。
动作时长和事件时序沿用 v3。演员位移记录在 placement_changes，特效挂点、偏移和有效帧见 fx_events。

## 狮子舞

动作轨 `skill2`，8 帧。

- 第 2 帧，0.110 秒，`hands_plant`。
- 第 5 帧，0.370 秒，`flip_start`。
- 第 6 帧，0.432 秒，`stomp_wave`。
- 第 6 帧，0.432 秒，`contact`。
- 第 7 帧，0.507 秒，`recover`。

## 特效

- 双脚落地冲击，轨 `stomp_wave`，挂层 `actor_ground`，逻辑偏移 [20, 0]。
