# 可酷伯动作姿势交接

交付 16 张姿势 PNG，全部由 image_gen 逐张绘制，以本轮包内 0_design.png、1_head.png、对应动作渲染和骨架为参考。没有使用代码绘制替代角色。

## 文件清单

- kobuko-pose-a_wind.png、kobuko-pose-a_strike.png、kobuko-pose-a_back.png：普攻起手、推出掌、收势。
- kobuko-pose-q_raise.png、kobuko-pose-q_spread.png、kobuko-pose-q_claw.png：抬臂、张臂、金爪重掌。
- kobuko-pose-e_crouch.png、kobuko-pose-e_leap.png、kobuko-pose-e_land.png：深蹲、腾空、落地双掌。
- kobuko-pose-run1.png 至 kobuko-pose-run4.png：四个跑步姿势。
- kobuko-pose-d_hit.png、kobuko-pose-d_fall.png、kobuko-pose-d_down.png：后仰、前扑、趴地。
- raw/：18 张未经处理的生成原稿，包含张臂和 run3 的初稿与修正版；最终选用的原稿见 manifest.json。
- pixel_1x/：16 张 104×104 的逻辑网格图，与最终大图对应。
- pose-contact-sheet.png：16 张总览。
- run-preview.gif：四帧顺序预览，仅供离线美术检查，不代表游戏内动作验收。
- generation-prompts.txt、generation-addenda.txt、repair-prompts.txt：实际提示词和修订记录。
- manifest.json：尺寸、网格、包围盒、源图、处理尺度和 SHA-256。
- qa-report.json：独立文件检查结果。

## 已检查

所有最终姿势均为 1254×1254 RGBA；透明度仅 0/255；每个完整逻辑方格为 12×12 同色像素，原点在 (0,0)。1254 不能被 12 整除，最右和最下 6px 为透明余边。最低可见像素为 y=1175，边界为 y=1176，符合脚底地面线。角色画面与技能特效分开，没有参考骨架、网格、地面线或文字。

生成后仅进行了多数颜色取格、硬 alpha、孤立杂点清除、全身等比近邻缩放与整格放置；未逐格代码绘制身体，也没有额外生成待机或挨打。

## 导入须知

这是动作美术素材交付，未改动仓库、安装模组或运行游戏。生成图以同一个定稿头部为参考，但不是逐像素复制同一头图；手臂层次、骨架关节和四帧跑步的前后腿关系仍属于生成近似。不要把离线尺寸检查等同于逐关节、逐头部像素一致或游戏内流畅性验收。导入前请同时对照 raw/、原始骨架包和 run-preview.gif；如果需要刚性完全一致的头部，应在最终拼帧环节使用定稿头部对齐。

总览已人工查看，张臂贴边初稿保留在 raw/，最终文件使用补全双掌的修正版。最终造型、颜色和轮廓以这次包内定稿为准。
