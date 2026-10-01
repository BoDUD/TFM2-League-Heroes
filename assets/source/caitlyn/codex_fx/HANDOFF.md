# 凯特琳独立特效交接

本包补齐最后一组：22 张特效条、107 帧。没有改动角色动画或写入已安装游戏目录。原始 LoL 贴图集只用于参考，不在交付中。

## 文件用法

- 根目录 `caitlyn_fx_*.png`：按需求尺寸输出的 8 倍像素透明条；用 `manifest.json` 的 `frames[].rect` 分帧，索引从 0 开始，矩形为 `[x,y,w,h]`。
- `game_size/`：同样帧布局的游戏像素大小版本。需要直接使用低分辨率资源时选这一组；不要同时载入两组叠画。材质采样用 nearest/point。
- `preview.html`：单文件离线逐帧预览，支持暂停、倍率、慢速、翻转和透明棋盘；`overview.gif`、`previews/*.gif` 是动画预览。
- `generation_prompts.json`：每张生成提示词与生成来源记录；`validation.json`：文件和分帧检查。

部分生成原稿未遵守尺寸、透明度和色板，因此输出经过分帧、统一每张的像素比例、指定色板和二值透明清理。各帧使用同一比例，消散末帧没有单独放大。横向弹道和绳网执行上下对称规范。爆头命中原稿额外生成了一行无关网图，只采用上方 6 个命中帧，准确原稿矩形写在 manifest；无关网图未交付。

`w_snap` 原需求高 170px，不能整除 8；采用顶部/底部各 1px 透明留边，中间 168px 按 8px 方块构图，仍输出 2304×170。

## 绑定与建议时长

tick 按 60Hz。网住目标、夹住目标、夹子埋伏循环分别严格为 60、75、15 tick，其余 tick 是建议值，需和导入后的动作释放帧校准。

| 文件 | 帧数 | 游戏尺寸 px | 绑定表 / 键 | 播放 | 总 tick |
|---|---:|---|---|---|---:|
| caitlyn_fx_bolt.png | 4 | 12 × 4 | view_projectiles / `league_caitlyn_bolt` | 循环 | 8 |
| caitlyn_fx_hs_bolt.png | 4 | 18 × 6 | view_projectiles / `league_caitlyn_hs_bolt` | 循环 | 8 |
| caitlyn_fx_q_bolt.png | 4 | 24 × 10 | view_projectiles / `league_caitlyn_q_bolt` | 循环 | 12 |
| caitlyn_fx_e_net.png | 4 | 16 × 14 | view_projectiles / `league_caitlyn_e_net` | 末帧停住 | 8 |
| caitlyn_fx_w_throw.png | 4 | 8 × 8 | view_projectiles / `league_caitlyn_w_throw` | 循环 | 12 |
| caitlyn_fx_r_bullet.png | 4 | 32 × 6 | view_projectiles / `league_caitlyn_r_bullet` | 循环 | 8 |
| caitlyn_fx_shot.png | 4 | 10 × 8 | view_effects / `league_caitlyn_shot` | 单次 | 10 |
| caitlyn_fx_hs_shot.png | 5 | 16 × 12 | view_effects / `league_caitlyn_hs_shot` | 单次 | 12 |
| caitlyn_fx_e_shot.png | 4 | 12 × 12 | view_effects / `league_caitlyn_e_shot` | 单次 | 10 |
| caitlyn_fx_q_muzzle.png | 5 | 18 × 14 | view_effects / `league_caitlyn_q_muzzle` | 单次 | 10 |
| caitlyn_fx_r_muzzle.png | 6 | 26 × 18 | view_effects / `league_caitlyn_r_muzzle` | 单次 | 21 |
| caitlyn_fx_hit.png | 4 | 10 × 10 | view_effects / `league_caitlyn_hit` | 单次 | 10 |
| caitlyn_fx_hs_hit.png | 6 | 20 × 20 | view_effects / `league_caitlyn_hs_hit` | 单次 | 15 |
| caitlyn_fx_q_hit.png | 5 | 16 × 16 | view_effects / `league_caitlyn_q_hit` | 单次 | 13 |
| caitlyn_fx_e_hit.png | 10 | 22 × 22 | view_effects / `league_caitlyn_e_hit` | 单次 | 60 |
| caitlyn_fx_r_hit.png | 7 | 28 × 28 | view_effects / `league_caitlyn_r_hit` | 单次 | 22 |
| caitlyn_fx_w_land.png | 5 | 16 × 10 | view_effects / `league_caitlyn_w_land` | 单次 | 15 |
| caitlyn_fx_w_trap.png | 2 | 16 × 10 | view_effects / `league_caitlyn_w_trap` | 循环 | 15 |
| caitlyn_fx_w_fade.png | 3 | 16 × 10 | view_effects / `league_caitlyn_w_fade` | 单次 | 9 |
| caitlyn_fx_w_snap.png | 9 | 18 × 12 | view_effects / `league_caitlyn_w_snap` | 单次 | 75 |
| caitlyn_fx_r_mark.png | 4 | 24 × 24 | view_buffs / `league_caitlyn_r_mark` | 循环 | 24 |
| caitlyn_fx_e_slow.png | 4 | 16 × 8 | view_buffs / `league_caitlyn_e_slow` | 循环 | 24 |

## 挂点与事件

枪口火光使用左边中点锚点 `[0,0.5]`，默认向右，朝左时水平翻转；必须将锚点放在角色出手帧的枪口，而非站位中心。CasterViewEffect 仅跟随角色朝向，不会自动跟随角色图中的枪，所以枪口移动之后不得仍显示燃烧的火焰。动画建议仅供对时，导入者需按实际动画切换烟段或结束效果。

飞行物按飞行方向旋转。`bolt/hs_bolt/q_bolt/e_net/r_bullet` 上下对称，可旋转 180°；`w_throw` 本身为翻滚动画。量出手帧的枪口高度后填入对应 `y_offset`（仅画面偏移），并按 projectile 的飞行速度计算从站位到枪口的隐藏 tick。这里未填未经测量的引擎值。

普通命中、爆头、Q、R 在目标中心触发并跟随；`e_hit` 以网底部 90% 高度对齐目标下部，内部网孔保持透明，不包含目标。`w_land/w_trap/w_fade` 不跟随，`z=-1`，地面位于格子 80% 高度。`w_snap` 跟随目标脚下，以格子 95% 高度对齐脚点。`e_slow` 跟随目标脚边，以 85% 高度对齐。`r_mark` 在目标中心循环。

夹子落地结束后切换 `w_trap`；未触发到期切换 `w_fade`；踩中触发 `w_snap` 和夹子爆头，后者复用 `hs_bolt/hs_hit`。E 命中触发 `e_hit`，随后按减速状态切换/保留 `e_slow`；R 蓄力期间显示 `r_mark`，出手时移除并生成 R 弹道和枪口效果，命中时生成 `r_hit`。

## 验证边界

文件检查已覆盖 22 张/107 帧、透明度、色板、分帧矩形、8px 方块、旋转弹道上下对称、游戏尺寸、指定 tick 和循环标记。另逐张查看了清理后的帧和游戏尺寸预览。这些检查不等于游戏内接入验证；本包未验证引擎坐标系、释放时点、挂点、碰撞、左右朝向和运行时循环行为。
