"""Write assets/source/qiyana/POSE_PROMPTS.md from tools/art/pack_qiyana_poses.py's POSES (run from the repo root)."""
import sys
sys.path.insert(0, 'tools/art')
import pack_qiyana_poses as P
names = list(P.POSES)
n = len(names)
L = []
a = L.append
a("# 元素女皇 奇亚娜：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 奇亚娜的造型用户已经定稿（`2_design.png`，你上一轮画的 A-1：3/4 正面朝右的高傲女王——暖棕皮肤、银白长发和齐刘海、金王冠嵌翠绿宝石、"
  "白玉尖冠、琥珀金眼睛和黑眼线、翠绿金珠项圈、青绿抹胸短裙加金边和墨绿裙摆、金臂环手镯、深棕紧身裤和金三角纹、紫棕凉鞋，"
  "近侧的手握着竖在身边的大圆环刀刃——深色弯刃、青绿内圈、金箍、玫瑰铜护手、两颗白玉水晶刃头）。英雄联盟里她每个动作都把圆环抡起来——"
  "抡到身后、扫到身前、平举、拖着突进、举过头、砸地、扛在背上跑、掉在地上——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 "
  f"**{n} 个姿势，每个一张图**（{n - 4} 个动作姿势 + 4 帧跑步）。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张图都是同一个奇亚娜**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，"
  "**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边）**；"
  "**黄色的椭圆 = 圆环刀刃**（看成椭圆是因为它侧过来或放平了：椭圆越扁，圆环越接近平放或侧对着我们），**青色的两段 = 两颗白玉水晶刃头**的位置；"
  "握环的那只手臂的末端就在椭圆上（那里是手握着环的地方）；**灰框 = 头的位置**。`0_design_skeleton.png` 是同样的骨架画在定稿上，"
  "看每条线对应身体的哪一部分。**腿、手臂的长短粗细和定稿一样**（骨架就是按定稿量的），关节处弯折，**不要拉长或压短，不要把直的腿整块转个方向贴上去**。"
  "手臂从肩膀长出来，不能悬空。**圆环和定稿一样大、一样粗**（只是转了方向：竖着、放平、侧过来、斜着），环中间是空的。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（连尖冠和头发 28 × 31 格，同样朝右前方、两只琥珀金眼睛都看得见）。每个姿势都是这一个头，"
  "只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、圆环**不要盖住脸**（眼睛和嘴）。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的奇亚娜是正常比例、圆环比她还大；"
  "我们的是 Q 版大头、圆环小一些：身子短、手臂短，**圆环不要举到脸前面，手臂往两边、往前、往后伸，不要从脸前面横过去**。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `qiyana-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi PROUD YOUNG EMPRESS with a BIG head: warm tan-brown skin, long wavy silver-white hair with straight bangs, a gold tiara with emerald gems and a "
  "tall white-jade crest, amber-gold eyes with thick black eyeliner, an emerald-and-gold bead choker, a turquoise-teal strapless short dress with gold "
  "trim and a dark green flap behind, gold armlets and bracelets, dark brown-black leggings with gold triangle markings, purple-brown sandals, and her "
  "HUGE RING BLADE held in her hand (a dark brown-black curved blade, a teal inner rim, gold and teal bands, rose-copper guards, two white-jade crystal "
  "blade heads at opposite points); B its HEAD with the crest and the hair shown 8x (28 squares wide, 31 tall); C a SKELETON on the same 1254 canvas and "
  f"{P.PX} px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), "
  "ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right), the YELLOW ELLIPSE = the RING BLADE as it is seen in this pose (a flatter "
  "ellipse = the ring turned flat or edge-on; the ring keeps the design's size and thickness), the two CYAN strokes = its two crystal heads, the arm "
  "that ends on the ellipse holds the ring there, GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in "
  "this pose, 3/4 view facing right (copy the POSE and the ring's swing from it, never its 3D look, its realistic proportions or its oversized ring); E "
  "(if attached) the same skeleton drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a("Lay the body along the skeleton: the torso along the green line, each leg along its line (bending at the dots: the dark leggings with their gold "
  "triangles, the purple-brown sandal - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (the arms grow "
  "from the shoulders, never floating; the gold armlet and bracelet stay on), the hand on the ellipse GRIPPING the ring there. THE RING drawn along the "
  "yellow ellipse at the design's size and blade thickness, its middle EMPTY, its teal inner rim, gold bands and rose-copper guards, its two white-jade "
  "crystal heads where the cyan strokes are; turned flat or edge-on it reads as a long narrow oval or a thick curved bar. Never stretch or shorten a "
  "limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both amber-gold eyes with their eyeliner, the mouth, the gold "
  "tiara, the white-jade crest, the silver-white hair) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand "
  "or part of the ring covers the face (the eyes and the mouth).")
a("The same colours as image A; one continuous 1-square near-black outline (round the ring's inner edge too); no stray single squares, no dithering, no "
  "gradients, no glow, no blur, no anti-aliasing.")
a("No effects (no elemental glow, no leaves, no water, no rocks, no shock waves, no motion trails), no background, no ground, no shadow, no text, no grid "
  "lines, no skeleton lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。")
a("- 每张都是定稿的同一个奇亚娜：**同一个头（照图 B，脸朝右前方、两只琥珀金眼睛和黑眼线、金王冠、白玉尖冠、银白头发）**、同样粗的腿和手臂；"
  "**圆环和定稿一样大、一样粗**，中间空，两颗白玉刃头，握着它的手在环上；手臂从肩膀长出来，手和圆环没有盖住脸；姿势沿着骨架；着地的脚在 "
  f"y {P.SOLE_Y}。")
a("- 所有图没有特效、没有骨架线、没有网格线。\n")
a("## 交付（`outputs/qiyana-poses/`）\n")
a("- " + "、".join(f"`qiyana-pose-{x}.png`" for x in names) + "；原始生成图原样放 `outputs/qiyana-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/qiyana_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `qiyana_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，黄椭圆 = 圆环） |")
a("| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_neeko_poses / design_ksante_poses 的做法：按身体面积定比例，头换成定稿的头），颜色对到定稿的调色板；"
  "**先在 8 倍下量每条腿、手臂和圆环的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_qiyana.py 的动作里，逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟）：普攻 = a_wind → a_strike → 定稿；Q（skill，四种元素共用姿势，特效画进帧里）= q_wind → q_sweep → q_end；"
  "E（skill2）= e_dash（突进）→ e_hit；R（ult）= r_leap → r_slam；死亡 = d_fall → d_lie；跑 = run1–4；待机 = 定稿一帧；受击 = 定稿后退一格闪白。")
open('assets/source/qiyana/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses")
