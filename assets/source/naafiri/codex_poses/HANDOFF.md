# 纳亚菲利动作关键姿势交接

本轮交付18张由内置 image_gen 独立绘制的动作关键姿势候选图。输入只来自 naafiri_pose_pack.zip，角色外观依据其造型图和头部图，动作依据各姿势 guide / league 图。角色美术没有用脚本逐格绘制。

## 文件清单

本体13张：

- naafiri-pose-crouch.png
- naafiri-pose-rear.png
- naafiri-pose-lunge.png
- naafiri-pose-fling.png
- naafiri-pose-flare.png
- naafiri-pose-dash.png
- naafiri-pose-rise.png
- naafiri-pose-howl.png
- naafiri-pose-lie.png
- naafiri-pose-run1.png
- naafiri-pose-run2.png
- naafiri-pose-run3.png
- naafiri-pose-run4.png

伙伴5张：

- naafiri-pose-p_run1.png
- naafiri-pose-p_run2.png
- naafiri-pose-p_run3.png
- naafiri-pose-p_run4.png
- naafiri-pose-p_bite.png

附 raw/ 下对应18张未经修改的生成原图、generation-prompts.txt 实际最终提示词、validation.json 检查结果、preview.png 18图总览。预览采用各自轮廓等比缩放排版，不能用于比较真实游戏体型。

## 处理与验证

最终18张均实测为1254×1254 RGBA，透明度仅0/255；主体轮廓均未接触画布边缘。原图含有半透明像素，交付版只按alpha>=128清理透明度，没有改RGB、角色位置、比例、画布大小或像素网格，没有程序重绘或粘贴头部。raw/保留生成原文件。

蓄势初稿过于接近待机，已用姿势优先的提示词重画；本体和伙伴的run2收腿不足，也已重画。最终提示词均在generation-prompts.txt中。旧的被替代稿没有混入本次交付。

## 视觉复查与尚未通过的项目

18种关键姿势的轮廓可区分：蓄势前胸抬起、rear大张嘴双前爪离地、lunge低扑、fling斜向跃空、flare后高前低张刃、dash水平伸展、rise抬前身、howl坐姿仰头、lie平卧、两组跑步四阶段及伙伴下扑。白口鼻/黄眼/白牙/骨柄、紫刃绿边、蓝青甲壳，以及伙伴灰盔前刃和红身身份保留。

**精确格子检查未通过，不能作为可直接按格读取的最终动画资产。** 逐个检查从(0,0)起的11px/22px目标方格，18张均存在格内多种RGBA值；它们并非统一整块网格。单靠清理alpha不能修复这一点。

头部没有做到逐像素完全一致，部分动作存在头身尺度变化、腿长/粗细变化及较多细碎色阶；rear/rise尤其偏高大。腿部大体可分，但仍需骨架及逐格复核，不能宣称所有关节正确。

动作布局没有完全复制guide：多张占画幅过大；ground接触位置不齐；dash、run4、p_run4的离地高度明显大于目标3/2/1格；fling的甩头弯曲不完全贴合原始渲染。lie更接近低趴倒地，侧翻与四腿伸向一侧的表达不足，右侧仅余7px，不满足完整一格安全边。fling等部分图也只有较窄边距。具体主体bbox与地面偏差见validation.json，底部偏差记录的是最低不透明像素，不等同于所有爪子的接地点。

这些文件适用于动作方向、姿势和造型的后续参考；导入前仍需统一头部、逻辑网格、角色尺度、地面基准和腿部骨架。未声称连续跑步循环已验证流畅。未将伙伴合入本体帧，未修改rig、动作表、技能代码、仓库或安装模组，未进行游戏内测试。
