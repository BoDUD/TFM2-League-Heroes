# 冲田总司补画交接

游戏资源 ID 为 ragnarok_okita。逻辑大小 116×92，脚点 (52, 84)。4× 图集为最近邻导出。
朝向为右。角色脚点为偏移原点，左向镜像时 X 偏移也翻转。帧号从 1 起。

## 天翔散段突

第 4、5、6 帧分别发出上、中、下三条真空刃。逻辑帧和脚点使用包内冲田规格。

动作轨为 ult。事件帧如下。

- 第 3 帧，0.220 秒，dash_start
- 第 4 帧，0.291 秒，vacuum_upper
- 第 5 帧，0.343 秒，vacuum_mid
- 第 6 帧，0.390 秒，vacuum_lower
- 第 7 帧，0.435 秒，dash_end

- 第一刺真空刃，轨 vacuum_upper，挂点 projectile，偏移 [26, -28]。
- 第二刺真空刃，轨 vacuum_mid，挂点 projectile，偏移 [29, -22]。
- 第三刺真空刃，轨 vacuum_lower，挂点 projectile，偏移 [28, -16]。

实际技能触发、动画接入和 PPU 仍需游戏端验证。
