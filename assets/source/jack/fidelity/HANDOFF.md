# 开膛手杰克补画交接

游戏资源 ID 为 `ragnarok_jack`。逻辑格 [216, 168]，脚点 [98, 148]。
Dear GOD、神器之伞按 2×2 网格重出。头部像素来自包内对应形态的待机参考帧，随动作平移和转动。
逻辑图集旁的 _hd.png 是按 hd_multiplier 最近邻放大后的版本。朝右绘制，镜像时 X 偏移也翻转。
动作时长和事件时序沿用 v3。演员位移记录在 placement_changes，特效挂点、偏移和有效帧见 fx_events。

## Dear GOD

动作轨 `ult`，8 帧。

- 第 2 帧，0.130 秒，`glove_aura`。
- 第 4 帧，0.370 秒，`rush_start`。
- 第 6 帧，0.507 秒，`contact`。
- 第 7 帧，0.579 秒，`rush_end`。

## 神器之伞

动作轨 `skill2`，8 帧。

- 第 2 帧，0.105 秒，`umbrella_open`。
- 第 3 帧，0.195 秒，`umbrella_spin`。
- 第 4 帧，0.268 秒，`umbrella_guard_spark`。
- 第 7 帧，0.495 秒，`back_hop`。
- 第 8 帧，0.615 秒，`umbrella_close`。

## 特效

- 染红手套光，轨 `glove_aura`，挂层 `actor_behind`，逻辑偏移 [18, -30]。
- 命中红光，轨 `dear_god_hit`，挂层 `target_contact`，逻辑偏移 [0, 0]。
- 旋伞残影，轨 `umbrella_spin`，挂层 `actor_front`，逻辑偏移 [22, -22]。
- 格挡火花，轨 `umbrella_guard_spark`，挂层 `actor_front`，逻辑偏移 [24, -22]。

染红手套光贴合手套下沿并放至身后。神器之伞保留旋转与后跳。
