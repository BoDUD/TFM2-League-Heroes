# 魔腾特效补充包（11张）

上一轮8张特效不改。本包补齐11张、44个帧位，每张4帧2×2，1920×1664透明PNG；1×图在effects_1x，逐张GIF和联系表在previews。manifest记录120×104格子、脚底pivot(60,88)、每帧bbox、时长、层级及指定绑定名称。

## 制作
使用内置imagegen按每项提示词分别绘制，以上一轮总览为风格参考。脚本清除淡透明边缘、按逐格不透明范围定位并规范化尺度、吸附指定19色、二值透明、最近邻放大8倍。环绕效果的中心留空掩膜避免遮住身体或脸。角色只出现在预览里，不在特效PNG里。完整提示词与原图路径在generation_prompts.json。

## 位置与绑定
- hit: view_effects `league_nocturne_hit`；中心(60, 70)；一次播放；跟随单位。
- p_hit: view_effects `league_nocturne_p_hit`；中心(60, 70)；一次播放；跟随单位。
- q_hit: view_effects `league_nocturne_q_hit`；中心(60, 72)；一次播放；跟随单位。
- q_dusk: view_buffs `league_nocturne_q_dusk`；中心(60, 88)；循环；跟随单位。
- e_grip: view_effects `league_nocturne_e_grip`；中心(60, 72)；一次播放；跟随单位。
- e_tick: view_effects `league_nocturne_e_tick`；中心(60, 70)；一次播放；跟随单位。
- e_fear: view_effects `league_nocturne_e_fear`；中心(60, 44)；循环；跟随单位。
- w_proc: view_effects `league_nocturne_w_proc`；中心(60, 68)；一次播放；跟随单位。
- r_burst: view_effects `league_nocturne_r_burst`；中心(60, 88)；一次播放；固定原地。
- r_veil: view_effects `league_nocturne_r_veil`；中心(60, 71)；一次播放；跟随单位。
- r_dark: view_buffs `league_nocturne_r_dark`；中心(60, 58)；循环；跟随单位。

## 建议时长与循环
一次效果60/70/90/110ms，共330ms；循环每格110ms，共440ms。q_dusk、e_fear、r_dark保留三种生成相位，按1-2-3-2组成往返循环，末格到首格的变化反向对应首格到第2格的变化，避免末帧淡出后重新出现；恐惧旋涡小幅往返摆动；这是三种不同形态组成的四帧位循环，没有声称四个独立造型。E伤害脉冲的500ms调度、Q标记持续、R队友隐身与敌方黑雾持续均需要游戏端绑定，不包含技能逻辑修改。

## 差异
R地面波纹的满格宽约120、宽高比2:1与中心y88在104高格内无法同时满足；本包使用114×28的更扁椭圆，中心仍在(60,88)，不裁掉底部。Q命中中心采用详细提示词的16格高度(y72)，通用表里的胸口18格(y70)与它相差2格。恐惧标记的灰眼使用#D3D7DC，不使用眼睛纯白。

## 检查范围
尺寸、44帧位、严格8×8方块、二值透明、19色色板子集、无纯白、bbox与中心留空以及三个往返循环闭合关系已检查。叠加GIF用于看尺寸和挂点，角色保持定稿站姿，各特效重复展示；没有模拟真实出手、伤害、目标移动、地形遮挡或游戏BUFF。尚未导入游戏验证。
