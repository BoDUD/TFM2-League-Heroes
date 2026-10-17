# 乐芙兰基础特效交付

19 张基础特效、99 帧。普攻 3 张、Q 5 张、E 5 张、W 6 张。大招强化版及分身按任务清单留给导入阶段，本包未制作。没有修改游戏或执行给 Claude 的导入步骤。

## 使用文件

顶层 leblanc_fx_*.png 为规定尺寸的透明 8 倍像素条。manifest.json 的 assets[].frames[].rect = [x,y,width,height] 可直接切片；不要裁掉格子留白再平均分。native/ 中同名图是 1 倍像素条，*_game.png 为按给定游戏显示尺寸制作的初步预览条，细节可能在小尺寸下减少，实际导入优先用同名完整条。

generated/ 保存选用的生图原稿。原稿尺寸和方块比例不完全符合要求，因此正式条逐帧用共同裁剪区域、统一比例整理，再限色和二值透明处理。四种飞行/链节特效做了上下对称整理，链节使用贯穿格子的光丝，左右端逐像素匹配。

## 预览与检查

fx_contact.png 是效果索引，fx_overview.gif 便于同时检查所有特效（统一展示速度）；previews/ 为各效果单独 GIF。Q 印记为 4×50ms=200ms；E 定身共 1500ms；W 法阵共 1250ms；其他 GIF 使用 80ms/帧作为预览速度，实际技能时间由导入方绑定。

validation.json 记录实际检查：张数与帧数、目标尺寸、每帧非空、严格 8×8 色块、二值透明、限定色板、四种飞行特效上下对称、链节左右接缝匹配。未检验游戏内挂点、混合方式与强化版缩放效果。

## 修正及限制

E 定身针对原稿实心光团重画为低矮中空锁链；W 落地爆炸针对不均匀间距重排成七等宽帧。部分符文和碎片在游戏小尺寸下会减少细节；需结合游戏播放验证亮度和位置。低分辨率边缘使用紫色材质暗部，不含黑色描边；这不代表每一处生成暗部都已达到人工美术终审。

本地英雄联盟参考贴图未放入交付包。

## 每张图对应提示与帧数

完整初始提示见 generation_prompts.json，修正提示见 generation_corrections.json。

|文件|提示编号|帧数|
|---|---|---|
|leblanc_fx_a_orb.png|1|4|
|leblanc_fx_a_cast.png|2|4|
|leblanc_fx_a_hit.png|3|4|
|leblanc_fx_q_orb.png|4|4|
|leblanc_fx_q_cast.png|5|4|
|leblanc_fx_q_hit.png|6|5|
|leblanc_fx_q_mark.png|7|4|
|leblanc_fx_q_pop.png|8|6|
|leblanc_fx_e_chain.png|9|4|
|leblanc_fx_e_tether.png|10|4|
|leblanc_fx_e_cast.png|11|4|
|leblanc_fx_e_hit.png|12|4|
|leblanc_fx_e_root.png|13|12|
|leblanc_fx_w_pad.png|14|10|
|leblanc_fx_w_trail.png|15|5|
|leblanc_fx_w_blast.png|16|7|
|leblanc_fx_w_hit.png|17|4|
|leblanc_fx_w_out.png|18|5|
|leblanc_fx_w_in.png|19|5|
