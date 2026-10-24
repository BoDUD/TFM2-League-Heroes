# 交付文件 QA

验证对象为已保存的最终PNG和原稿，不是只检查生成参数。

| 项目 | 尺寸/格子/帧数 | 硬透明、对应关系、哈希 |
|---|---|---|
| a_rock | 4帧 / 8×6 / top-bottom | 通过 |
| a_hit | 3帧 / 12×12 / left-right | 通过 |
| q_rock | 4帧 / 12×8 / top-bottom | 通过 |
| q_hit | 3帧 / 14×14 / left-right | 通过 |
| q_boulder | 4帧 / 22×16 / top-bottom | 通过 |
| q_big_hit | 4帧 / 22×20 / left-right | 通过 |
| q_ground | 6帧 / 30×10 / left-right | 通过 |
| e_mines | 8帧 / 46×16 / left-right | 通过 |
| w_erupt | 5帧 / 36×32 / left-right | 通过 |
| w_hit | 3帧 / 18×20 / left-right | 通过 |
| e_blast | 4帧 / 20×24 / left-right | 通过 |
| slow | 4帧 / 18×7 / left-right | 通过 |
| r_wall | 8帧 / 16×126 / left-right | 通过 |
| surf | 4帧 / 36×8 / left-right | 通过 |

所有最终PNG的alpha只有0/255，透明RGB为0；放大PNG和pixel_1x逐格一致；raw原稿SHA-256一致。

全部64帧非空、单帧与横向序列一致、逐像素对称、可见色属于规定色板。

未进行游戏内或rig装配验证。格式通过与视觉/运行限制分别记录于HANDOFF.md。
