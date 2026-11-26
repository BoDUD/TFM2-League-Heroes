# 湿婆补画交接

游戏资源 ID 为 `ragnarok_shiva`。逻辑格 [216, 168]，脚点 [98, 148]。
虎爪炎舞按 2×2 网格重出。头部像素来自包内对应形态的待机参考帧，随动作平移和转动。
逻辑图集旁的 _hd.png 是按 hd_multiplier 最近邻放大后的版本。朝右绘制，镜像时 X 偏移也翻转。
动作时长和事件时序沿用 v3。演员位移记录在 placement_changes，特效挂点、偏移和有效帧见 fx_events。

## 虎爪炎舞

动作轨 `skill2`，8 帧。

- 第 3 帧，0.210 秒，`jump_start`。
- 第 4 帧，0.288 秒，`kick_flame`。
- 第 5 帧，0.355 秒，`contact`。
- 第 6 帧，0.422 秒，`land`。

## 特效

- 脚踝炎轨，轨 `kick_flame`，挂层 `actor_behind`，逻辑偏移 [10, -30]。
- 踢中火光，轨 `flame_hit`，挂层 `target_contact`，逻辑偏移 [0, 0]。
