# 塞薇卡特效与图标交付

已交付 17 组特效，共 99 帧；另有 3 个 64×64 技能图标。

正式特效 `sevika_fx_<名称>.png` 为 8 倍最近邻放大横向条带；导入请使用 `pixel_1x/` 中同名的 1 倍图，以 manifest 的 `cell_1x` 和 `frames` 从左到右切格。条带无间距、无边框。图标 `sevika_icon_skill.png`、`sevika_icon_skill2.png`、`sevika_icon_ult.png` 为 64×64，每个逻辑像素 2×2。

`raw/` 保留最终源稿，原稿使用 2×2、3×2 或 4×2 布局生成，再切回横条；不要把 raw 的布局直接当作游戏横条。`motion/` 包含各组动画 GIF；`preview-*.png`、`icons-preview.png` 便于总览。

生成全部使用内置 image_gen；未用代码拼装替代特效。整理步骤为读取每格主色、去除半透明柔光、稀疏粒子保留、映射到提示词色阶、对称校正和切格排版。亮光的柔光在导入版本中已硬化，原稿可能仍有柔光。老虎机面板单独裁出；护盾/微光侧边素材按规格收窄并留出身体位置；头奖前两帧移到头顶区，后续帧留空身体区域。具体变换见 manifest，不能把整理图当作未经处理的 raw。

对称验收：q_flame、p_rocket、e_fist 朝右，逐帧上下完全对称；其余 14 组逐帧左右完全对称。已检查 99 帧均非空、各组有不同动画帧、尺寸和 alpha 只有 0/255。需要围绕演员的护盾、微光与头奖，主体位置保持透明。所有处理都可由对应源稿追溯。

图标和特效的语义、色彩及阶段已按包内方案制作；实际战斗读图、锚点、帧时长、伤害时机和技能绑定仍由后续导入验证。本次未修改游戏或模组文件。

## 文件清单
- `sevika_fx_a_hit.png`
- `sevika_fx_a2_hit.png`
- `sevika_fx_p.png`
- `sevika_fx_p_rocket.png`
- `sevika_fx_p_rocket_hit.png`
- `sevika_fx_p_shield.png`
- `sevika_fx_p_jackpot.png`
- `sevika_fx_p_shimmer.png`
- `sevika_fx_p_triple.png`
- `sevika_fx_q_flame.png`
- `sevika_fx_q_burn.png`
- `sevika_fx_e_fist.png`
- `sevika_fx_e_hit.png`
- `sevika_fx_e_stun.png`
- `sevika_fx_r_hit.png`
- `sevika_fx_r_bleed.png`
- `sevika_fx_r_kill.png`
- `sevika_icon_skill.png`
- `sevika_icon_skill2.png`
- `sevika_icon_ult.png`
