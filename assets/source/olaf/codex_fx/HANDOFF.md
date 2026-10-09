# 奥拉夫最后一步：13 张特效 / 56 帧

已用 imagegen 生成全部13张特效，不用代码绘制或拼装方块。根目录PNG与raw中的选定原稿相同，保留原始透明通道。Q落地、E命中、W开启和R开启另作了生图修复，以改善帧间距；修复前原稿保存在raw/attempts。

## 交付清单

| 图名 | 帧数 | 内容 | 提示词记录 | 具体差异 |
|---|---:|---|---|---|
| a_hit | 4 | 白蓝竖劈痕与双侧火花 | prompts/olaf_fx_a_hit.txt | 末帧火花较多，对称性为近似 |
| q_fly | 4 | 向右飞、四分之一圈旋转的实物斧与左侧残影 | prompts/olaf_fx_q_fly.txt | 刃形及旋转中心略漂移，柄比定稿粗 |
| q_land | 5 | 地面裂纹、向上碎石、消退 | prompts/olaf_fx_q_land.txt | 展开面积与石块数量需按范围调整 |
| q_axe | 3 | 斧刃入地、柄朝上、刃光脉冲 | prompts/olaf_fx_q_axe.txt | 斧刃造型与定稿略有差异 |
| q_hit | 4 | 横向白蓝刃光和碎光 | prompts/olaf_fx_q_hit.txt | 少量边缘碎点接近分格边界 |
| q_slow | 4 | 脚下扁椭圆寒气 | prompts/olaf_fx_q_slow.txt | 仍有细碎边缘和轻微形状漂移 |
| q_pick | 4 | 腰间光环、沿两侧上升的光带 | prompts/olaf_fx_q_pick.txt | 半透明碎点较多，严格像素导入时需清理 |
| e_hit | 5 | 白蓝X劈痕、闪电、地面冲击环 | prompts/olaf_fx_e_hit.txt | 末帧仍保留小地面环；外侧零星碎点近边界 |
| w_cast | 5 | 红橙爆发、白蓝闪电、空心护盾边 | prompts/olaf_fx_w_cast.txt | 第4–5帧比淡红护罩要求更像火环 |
| w_on | 4 | 人物身后的红色光环、闪电闪烁 | prompts/olaf_fx_w_on.txt | 比所需淡光晕更亮、更厚，建议导入后调透明度 |
| r_cast | 6 | 怒吼闪光、地面火环、向上怒火、余烬 | prompts/olaf_fx_r_cast.txt | 第5帧火焰仍较完整；脚下站位需导入时校正 |
| r_on | 4 | 地面火环、两侧火苗与背后怒火 | prompts/olaf_fx_r_on.txt | 循环火焰偏强，严格左右镜像未做到 |
| p_4 | 4 | 肩膀与头部两侧的细怒火 | prompts/olaf_fx_p_4.txt | 顶部较亮，两侧并非严格镜像 |

## 裁切与预览

manifest.json 的 assets[].frames[].rect 是实际交付PNG内的像素矩形 [x,y,width,height]，每组为一行；同组各帧等宽。裁切使用同一纵向范围，保留纵向相对位置；不要按原提示词的目标尺寸直接切实际原稿。

target_sheet_size / target_cell 是请求的目标画布，game_size 是导入后的游戏尺寸。实际原稿尺寸并未达到全部目标尺寸，符合原说明允许交回生图原稿的路径。anchor_local 当前是默认中心，并不是已校准的脚下锚点；地面和套身特效需按SOURCE_SPEC.md的脚下距离设置。

preview/包含每张的循环GIF与联系表，overview.png总览只选一帧示意。GIF背景为深色，仅用于检查，原PNG保持透明。GIF时长为审阅用途，不是已确认的游戏时序；留地斧头3帧预览80/90/80ms共250ms。一次性特效在GIF中重复播放便于审阅。

## 实际检查与未达到的硬规格

validation.json记录实际尺寸、帧数、透明背景、亮芯、半透明像素数量、亮度和边界像素。13张都有透明背景和接近白色的亮芯，56帧全部非空，帧矩形在文件内部。重画后Q落地、W开启、R开启的主要图形在各自区域内；Q命中、捡斧、E命中边缘仍有少量碎点。

原稿尚未满足严格16px方格、仅指定色板、无抗锯齿/二值透明及绝对左右对称。没有用代码强行清除半透明边缘，也没有量化后宣称美术规格通过。原说明允许保留生图原稿，由导入流程转成像素条。需要导入时清理光效深色边、量化色板、规范方格和左右对称；斧头实物的近黑描边应保留。未拿到其他英雄素材，未作跨英雄亮度比较。

## 导入对应关系

小图与buff组为league_olaf_fx；e_hit、r_cast、r_on为league_olaf_big。飞行斧使用view_projectiles的league_olaf_q_axe绑定，但tag为q_fly；留地斧才使用q_axe。飞行物可随方向旋转，q_land/e_hit/r_cast保持竖直；地面环按斜视椭圆处理。w_on和r_on画在人后面，其他套身光效按原说明层级。

本次完成的是特效素材交付，没有修改游戏资源、技能数据或执行Claude导入段落中的程序。完整原始规格保存在SOURCE_SPEC.md，实际不足逐图如上。
