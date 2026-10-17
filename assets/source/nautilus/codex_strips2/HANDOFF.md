# 诺提勒斯动作条 · STRIPS2 侧身重画

## 状态

本包包含 8 张重画动作条、48 帧，另附输入包原样保留的待机条（8 帧）。这是一版可审阅的侧身重画，**尚未完全满足 MODEL_STRIPS2 的造型与动作一致性标准，不应标为最终验收通过**。

已通过机械检查：尺寸、帧数与格子顺序、128×128 逻辑格、8 倍输出的严格纯色块、0/255 透明度、仅使用定稿 23 色、地面第 99 行以下无像素、站位 pivot 与每帧毫秒值和输入 JSON 一致；待机 PNG 的 SHA256 与输入完全一致。出手帧标为普攻 4/tick13、Q 5/tick14、W/E 3/tick8、R 5/tick16。详见 validation.json。

## 未达到的要求（必须继续审美验收）

- 共通：头盔、身躯、四肢和锚没有逐格复刻 p35 的大小与细节；不同帧的轮廓、尺寸及遮挡仍有变化。站姿整体高度未严格收敛到定稿 48 行，头盔到脚底也未全部保持 37 行。没有用缩小或删不透明行的方式伪造这个指标。色板归并不能弥补造型差异。
- run：头盔转右、锚背在背上、腿有屈膝与迈步；但第 1/5 帧的近远腿交换仍不够明确，整体还不等同 oppi 的交叉步。部件高度变化导致实际头部起伏可能超过 1 格，不能把脚底对位当作头部稳定。
- attack：第 4 帧向右横扫，已重画过薄的锚冠；握持位置仍像链条与锚杆的过渡段，未稳定做到握在粗锚杆上。锚冠和双爪的尺寸、角度没有严格保持同一刚体。
- skill：第 5/6 帧无锚，朝右出手；已去除第 5 帧邻格锚碎片和第 6 帧向左多余链条。但链条末端未全部延伸到格子右边界，抛出前后手臂比例和头盔细节仍有变化。
- skill_pull：第 1/2 帧无锚，第 3 帧锚返回，第 4 帧背锚；第 2 帧未充分表现双脚离地，拉动的身体前倾仍不足。
- skill2：第 3 帧下蹲向右捶地，锚留在背上；拳头接地姿势、远侧手臂归属及全程锚的固定几何仍需修正。
- ult：第 5/6 帧锚在右侧向下接地，无地下部分；但锚相对身体的比例变化较大，第 6 帧压低姿态与第 5 帧衔接不够稳定，未达到刚体不变形标准。
- hit：两帧朝右，保留背锚；当前身体与头盔细节变化仍多于仅向左震动 1–2 格。
- dead：第 2 帧起左侧竖锚，第 4 帧坐下，眼光逐渐变暗。第 7/8 帧使用相同第 7 帧绘图静止收尾、时长仍分别为 200/400ms。前段锚形、坐下的比例与定稿仍有差异。

## 文件

- nautilus_<action>.png：正式尺寸透明 PNG；_1x.png 是相同逻辑像素格的核对版。
- manifest.json：每帧 cell_rect_px（x,y,w,h；8 倍像素）、pivot、bbox（左上含、右下不含；格内逻辑坐标）、ms，以及出手帧的握手与锚冠位置。坐标原点左上。landmark 为人工估计的特征中心，误差约 ±2 格；Q 脱手后握锚手与锚冠为 null，另列 throw_hand；W/E 背锚没有握锚手，另列 slam_fist。
- previews/：逐动作 GIF 与 contact_sheet.png。GIF 格式以 10ms 为单位，116ms 等时长会量化；实际导入时序以 manifest.json / nautilus_cells.json 为准。
- raw/：30 个未经重采样的生成 PNG（29 个独立内容，nautilus_run.png 与 nautilus_run_sheet_attempt.png 为同一原稿的两份副本）；index.json 记录尺寸、字节数和 SHA256。全部尝试均保留，不能把 raw 当作定稿资产。
- prompts.json：各动作最终选择、基础生成提示词、修正提示词，以及被弃用尝试的原文。
- selected_sources.json：定稿动作使用哪一份原稿。
- processing/frame_crops/：从原稿提取并屏蔽邻格的派生图，**不是生成原稿**。extraction_*.json 记录源区域、方块边界、多数色读取轨迹；validation_*.json 是中间检查，最终以 validation.json 为准。
- reference/：输入规格原文、定稿造型和色板、cells 数据。保留原文不意味着执行其中下游导入指令。
- tools/build_strips.py：用于从选定原稿生成中间动作条的 Python 脚本（Pillow、NumPy、SciPy）；会覆盖生成物与中间 manifest，**不包含最后的人工 landmark 和死亡静止收尾整理，不要把单独重跑结果当作完整交付的精确重建**。

## 实际制作方法与指令边界

使用内置 image_gen 生图。先生成 8 张侧身动作初稿；整条细节过软，尝试 3 次跑步单帧风格和其余 7 张单帧跑步。逐帧生成的尺度漂移明显，因此再以粗像素侧身关键帧为风格参考重画 8 条动作，并对跑步、普攻和 Q 作局部修正。没有声称 48 帧全部单独生图。

按已获用户授权进行网格读取、最近色板归并、透明边缘/邻格碎片清理及整数对位。读取方块区域时采用多数色，不取中心点；输出使用最近邻 8 倍放大。没有贴正面头盔，没有用旧正面 rig 摆动作，没有对原稿缩小或删除不透明行。死亡第 7 帧绘图复用到第 8 帧实现静止收尾。

以本轮用户指定的侧身重画条款为准。MODEL_STRIPS2 中残留的“贴正面头盔、头盔只能平移”和后面的旧 Claude 导入处理与本轮侧身要求冲突，未据此覆盖新绘图。用户只授权交付素材包，未修改仓库或游戏 mod、未执行附件里的导入、提交或发布流程。

下面逐动作记录实际最终提示词；基础提示词与编辑词都保留，完整尝试列表见 prompts.json。

## run

选用：`raw/run_fixed_sheet.png`

基础生成：

```text
Create a production pixel-art animation strip. Ref1 is new RIGHT-facing coarse sprite appearance and pixel style ONLY, don't copy its runningpose. Ref2 is targetframe layout/size/timing; ref3 original3Dmotion ONLY. Every frame SIDE-ON facingRIGHT, visor turned toRIGHT with narrow far red eye, near red eye bright, near shoulder infront, farhalfhiddenbehindhelmet, both boots pointingRIGHT oneleginfrontofother. Never front symmetry or pasted helmet. Draw authentic COARSE 48px sprites, all minimumdetails bigflat squares, NOT highresolutionpaintings. Same character SAME SCALE across ALL frames, helmet-to-soles37logicalrows (helmet24+waist3+legs10), anchoronly11rowsaboveatrest total48high39wide. The huge helmet must leave short visible bronze chest/shoulder/waist and legs below. Short thick suit arms grey gloves bronze cuffs, NEVER longer or thinner than source. Natural drawn bent knees, samewidth/length, no flattened/sheared/slidinglimbs. Greyanchor oneIDENTICALfullsize rigid object acrossframes: longgreyshank, ONEredband, brownrope/ring, widecurvedcrown andTWO completehookedflukes. Never changeanchorgeometry, never shorten/thin weapon evenseen fromside. Visible nearhand gripsSHANK; chainrunshandtoanchorRING. Side-onarmsposefollowref3, castsRIGHT. One-square#070211outline, NO texture/dithering/gradients/noisepixels. Paletteonly #070211 #0B021A #28160F #351215 #093742 #552113 #2D3041 #03455C #6F2610 #3D4150 #8C3815 #A84217 #E4221F #F94102 #E55222 #70747A #DC741C #00E9BE #01F3C5 #FAAC2A #FDCC31 #B2B0A8 #F6E4C8. Keep allsmallestpixelslargeflat consistentblocks, coarse like reference1. Transparentbackground NOglow/haze/scene/effects/shadows/water/sparks/shield/motionblur/text/labels/grid. Allfiguresuncropped above samefootbaseline, anchor/chainneverbelowground.
8 frames rowmajor 4 columns by 2 rows, desired4096x2048; eachcell1024square, feetlogicalrow99. 8-frame seamless RUN loop, anchor always on back, near hand chain and far fist swing slightly. Boots truly CROSS and exchange front/back every half cycle. Frames1/5 maximum stride with opposite front leg; frames3/7 lifted boot passes BESIDE other,1-2 pixels up. Body bobs only1pixel. Same horizontal helmet position relative pivot. Last flows to first. EveryframeincludingfirstandlastisSIDE-ON RIGHT. Maintain same turnedhelmet shape and rigidanchor in ALLframes ofthisanimation, actualbentlegswhenkneesbend.
```

后续编辑：

```text
Edit image1's 8-frame RUN sheet (4columns2rows). ONLY fix LEGS in frames5,6,7,8 (BOTTOM ROW); preserve upper bodies, RIGHT-facing helmets, arms, anchors, pixel scale and top row frames1-4 exactly. Currently bottomrow repeats the same leading leg as toprow. Bottomrow must show OPPOSITE leg leading: frame5 FAR darker leg extends FORWARD RIGHT with flat boot, NEAR brighter bronze-knee leg bent BACK LEFT. Frame6 farboot beginslift,nearbootplants. Frame7 farKNEE bends andfarboot lifts1-2pixels passingBESIDE nearleg as theyCROSS. Frame8 farlegrecoveringback,nearlegbeginsforward toflow back toframe1. See image2 real side-on crossover gait standard. Both boots alwayspointRIGHT; side-on legs onefrontoneback, no frontalwide stance. Sameleglength,width andbootheight, thickbronzesoles. Draw naturalbentknees, do NOT stretch/squash/shear orslidecutoutlegs. Do NOT redrawhelmetfronton. Nothing below footbaseline. Samecoarseflatpixelstyle,one-squareoutline,sourcepalette, transparentbackground,noeffects/noextras. Keep ALL8cells andoriginal4x2layout.
```

## attack

选用：`raw/attack_fixed_sheet.png`

基础生成：

```text
Create a SIX FRAME BASIC ATTACK pixel sprite strip,3columns2rows, equal square cells, all side-on facingRIGHT. Ref1 is pixel identity/style and coarse PIXEL COUNT (use its48px look, do NOT copy its running pose). Ref2 is exact six pose sequence/layout. Ref3 is3Dmotion only. Draw MUCH COARSER than any detailed raster illustration: every smallest square about10px in this strip output, NO subpixels, flat23colors, singlepixel blackoutline, authentic tiny 48px sprite enlarged nearest-neighbour. At rest body helmet-to-sole37logicalrows, head24rows +waist3 +legs10rows; anchor11rowsabove. Identical proportions in all6frames, short thick arms no stretched extension, helmet turnsright visorright far eye tiny and near eye red, visible chest/shoulder/waist/shortlegs. Same source bronze/sea-green/darkgrey/grey/cream palette. Entire grey anchor same shape and dimensions all6frames, a rigid longshank redband rope/ring widecrown with2curvedflukes. It must look like the SAME weapon each frame. Near glove visible gripping shank; chain only betweenhandandring. SIX KEY POSES:1rightside ready takesanchoroffback;2windsanchorbackdownleft bodycoils;3sweepsanchorforwardRIGHT lowaboveground;4IMPACT lunge toRIGHT frontknee bent anchorhorizontal atkneelevel armshort;5recoversanchorup;6returnsRIGHT-facingready backanchor. Both boots pointRIGHT, knees bend naturally, samelegswidthlength. Feet identicalbaseline eachcell, nothingbelowbaseline includinganchor. No glow/background/haze/effects/text/labels/grid. TRUE transparent background. Desired3072x2048, eachcell1024square. Simplified coarsepixelstyle precisely like ref1. NO smooth shading, no micro-detail, only large flat colored squares.
```

后续编辑：

```text
Edit this pixel sprite sheet. Change ONLY the weapon in frame4 (BOTTOM LEFT cell). In that frame it currently looks edge-on, a thin vertical black/silver strip. Replace this thin anchor crown with the FULL WIDE CURVED GREY CROWN AND TWO COMPLETE HOOKED FLUKES, same size and shape as the anchor in frame3 (TOP RIGHT) and frame5 (BOTTOM MIDDLE), displayed broadside with both flukes visible. The complete anchor is a rigid object facingRIGHT, held horizontally by shank at knee height, ONEredband and brown rope/ring. Do not bend or shrink it. Preserve frame4's short arm/visible grip, RIGHT-facing helmet/body and crouched forward lunge. Preserve every other frame unchanged. Same coarse pixel sizes, flat colors, no detailed textures; transparent background and no glow/haze/effects. No pixel of anchor below soles baseline. Keep all6frames,3columns2rows. Only fix frame4's thin weapon.
```

## skill

选用：`raw/skill_fixed_sheet.png`

基础生成：

```text
Create a production pixel-art animation strip. Ref1 is new RIGHT-facing coarse sprite appearance and pixel style ONLY, don't copy its runningpose. Ref2 is targetframe layout/size/timing; ref3 original3Dmotion ONLY. Every frame SIDE-ON facingRIGHT, visor turned toRIGHT with narrow far red eye, near red eye bright, near shoulder infront, farhalfhiddenbehindhelmet, both boots pointingRIGHT oneleginfrontofother. Never front symmetry or pasted helmet. Draw authentic COARSE 48px sprites, all minimumdetails bigflat squares, NOT highresolutionpaintings. Same character SAME SCALE across ALL frames, helmet-to-soles37logicalrows (helmet24+waist3+legs10), anchoronly11rowsaboveatrest total48high39wide. The huge helmet must leave short visible bronze chest/shoulder/waist and legs below. Short thick suit arms grey gloves bronze cuffs, NEVER longer or thinner than source. Natural drawn bent knees, samewidth/length, no flattened/sheared/slidinglimbs. Greyanchor oneIDENTICALfullsize rigid object acrossframes: longgreyshank, ONEredband, brownrope/ring, widecurvedcrown andTWO completehookedflukes. Never changeanchorgeometry, never shorten/thin weapon evenseen fromside. Visible nearhand gripsSHANK; chainrunshandtoanchorRING. Side-onarmsposefollowref3, castsRIGHT. One-square#070211outline, NO texture/dithering/gradients/noisepixels. Paletteonly #070211 #0B021A #28160F #351215 #093742 #552113 #2D3041 #03455C #6F2610 #3D4150 #8C3815 #A84217 #E4221F #F94102 #E55222 #70747A #DC741C #00E9BE #01F3C5 #FAAC2A #FDCC31 #B2B0A8 #F6E4C8. Keep allsmallestpixelslargeflat consistentblocks, coarse like reference1. Transparentbackground NOglow/haze/scene/effects/shadows/water/sparks/shield/motionblur/text/labels/grid. Allfiguresuncropped above samefootbaseline, anchor/chainneverbelowground.
6 frames rowmajor 3 columns by 2 rows, desired3072x2048; eachcell1024square, feetlogicalrow99. 6-frame Q DREDGE LINE:1 lift anchor from back;2 raise overhead;3 draw back;4 swing forward;5 RELEASE near arm flung RIGHT open hand chain runs right off cell, NO ANCHOR;6 hold taut chain with BOTH hands in front, NO ANCHOR. Whole-body lean, side-on planted legs. No projectile or effects. EveryframeincludingfirstandlastisSIDE-ON RIGHT. Maintain same turnedhelmet shape and rigidanchor in ALLframes ofthisanimation, actualbentlegswhenkneesbend.
```

后续编辑：

```text
Edit this sprite sheet, preserving all SIX poses, pixel-art character appearance, coarse blocks and figure sizes. Layout is 3 columns by 2 rows. Make truly transparent background, no aura/paint haze. Correct only release and separation: frame5 (bottom middle) has NO anchor anywhere, only the open right hand and chain starting there and extending RIGHT to its cell edge. Frame6 (bottom right) holds chain with both hands in front to the RIGHT; ERASE chain behind him on LEFT. Frame4 (bottom left) must retain its entire anchor, but move its weapon slightly LEFT so the whole weapon stays within the bottom-left cell and never intrudes into frame5. Keep other poses as they are, including right-facing turned helmet and bronze body. Every figure separated from neighbors by transparent margins; no floating fragments. Do not add text, guides, grid or effects.
```

## skill_pull

选用：`raw/skill_pull_coarse_sheet.png`

```text
Create a production pixel-art animation strip. Ref1 is new RIGHT-facing coarse sprite appearance and pixel style ONLY, don't copy its runningpose. Ref2 is targetframe layout/size/timing; ref3 original3Dmotion ONLY. Every frame SIDE-ON facingRIGHT, visor turned toRIGHT with narrow far red eye, near red eye bright, near shoulder infront, farhalfhiddenbehindhelmet, both boots pointingRIGHT oneleginfrontofother. Never front symmetry or pasted helmet. Draw authentic COARSE 48px sprites, all minimumdetails bigflat squares, NOT highresolutionpaintings. Same character SAME SCALE across ALL frames, helmet-to-soles37logicalrows (helmet24+waist3+legs10), anchoronly11rowsaboveatrest total48high39wide. The huge helmet must leave short visible bronze chest/shoulder/waist and legs below. Short thick suit arms grey gloves bronze cuffs, NEVER longer or thinner than source. Natural drawn bent knees, samewidth/length, no flattened/sheared/slidinglimbs. Greyanchor oneIDENTICALfullsize rigid object acrossframes: longgreyshank, ONEredband, brownrope/ring, widecurvedcrown andTWO completehookedflukes. Never changeanchorgeometry, never shorten/thin weapon evenseen fromside. Visible nearhand gripsSHANK; chainrunshandtoanchorRING. Side-onarmsposefollowref3, castsRIGHT. One-square#070211outline, NO texture/dithering/gradients/noisepixels. Paletteonly #070211 #0B021A #28160F #351215 #093742 #552113 #2D3041 #03455C #6F2610 #3D4150 #8C3815 #A84217 #E4221F #F94102 #E55222 #70747A #DC741C #00E9BE #01F3C5 #FAAC2A #FDCC31 #B2B0A8 #F6E4C8. Keep allsmallestpixelslargeflat consistentblocks, coarse like reference1. Transparentbackground NOglow/haze/scene/effects/shadows/water/sparks/shield/motionblur/text/labels/grid. Allfiguresuncropped above samefootbaseline, anchor/chainneverbelowground.
4 frames rowmajor 4 columns by 1 row, desired4096x1024; eachcell1024square, feetlogicalrow99. 4-frame Q PULL:1 whole body pulled forward RIGHT both hands taut chain boots trailing NO ANCHOR;2 same lower boots just above baseline NO ANCHOR;3 land anchor back near hand low in front;4 side-on ready with anchor on back. Never change helmet orientation, no flying-anchor effects. EveryframeincludingfirstandlastisSIDE-ON RIGHT. Maintain same turnedhelmet shape and rigidanchor in ALLframes ofthisanimation, actualbentlegswhenkneesbend.
```

## skill2

选用：`raw/skill2_coarse_sheet.png`

```text
Create a production pixel-art animation strip. Ref1 is new RIGHT-facing coarse sprite appearance and pixel style ONLY, don't copy its runningpose. Ref2 is targetframe layout/size/timing; ref3 original3Dmotion ONLY. Every frame SIDE-ON facingRIGHT, visor turned toRIGHT with narrow far red eye, near red eye bright, near shoulder infront, farhalfhiddenbehindhelmet, both boots pointingRIGHT oneleginfrontofother. Never front symmetry or pasted helmet. Draw authentic COARSE 48px sprites, all minimumdetails bigflat squares, NOT highresolutionpaintings. Same character SAME SCALE across ALL frames, helmet-to-soles37logicalrows (helmet24+waist3+legs10), anchoronly11rowsaboveatrest total48high39wide. The huge helmet must leave short visible bronze chest/shoulder/waist and legs below. Short thick suit arms grey gloves bronze cuffs, NEVER longer or thinner than source. Natural drawn bent knees, samewidth/length, no flattened/sheared/slidinglimbs. Greyanchor oneIDENTICALfullsize rigid object acrossframes: longgreyshank, ONEredband, brownrope/ring, widecurvedcrown andTWO completehookedflukes. Never changeanchorgeometry, never shorten/thin weapon evenseen fromside. Visible nearhand gripsSHANK; chainrunshandtoanchorRING. Side-onarmsposefollowref3, castsRIGHT. One-square#070211outline, NO texture/dithering/gradients/noisepixels. Paletteonly #070211 #0B021A #28160F #351215 #093742 #552113 #2D3041 #03455C #6F2610 #3D4150 #8C3815 #A84217 #E4221F #F94102 #E55222 #70747A #DC741C #00E9BE #01F3C5 #FAAC2A #FDCC31 #B2B0A8 #F6E4C8. Keep allsmallestpixelslargeflat consistentblocks, coarse like reference1. Transparentbackground NOglow/haze/scene/effects/shadows/water/sparks/shield/motionblur/text/labels/grid. Allfiguresuncropped above samefootbaseline, anchor/chainneverbelowground.
6 frames rowmajor 3 columns by 2 rows, desired3072x2048; eachcell1024square, feetlogicalrow99. 6-frame W/E:1 side-on ready fists clenched;2 far fist raised HIGH from outer shoulder;3 IMPACT crouch far fist punches DOWN to ground in front RIGHT, glove at foot line, anchor stays on BACK;4 rise fist up;5 braced;6 side-on ready. NO shield water ripple effect. EveryframeincludingfirstandlastisSIDE-ON RIGHT. Maintain same turnedhelmet shape and rigidanchor in ALLframes ofthisanimation, actualbentlegswhenkneesbend.
```

## ult

选用：`raw/ult_coarse_sheet.png`

```text
Create a production pixel-art animation strip. Ref1 is new RIGHT-facing coarse sprite appearance and pixel style ONLY, don't copy its runningpose. Ref2 is targetframe layout/size/timing; ref3 original3Dmotion ONLY. Every frame SIDE-ON facingRIGHT, visor turned toRIGHT with narrow far red eye, near red eye bright, near shoulder infront, farhalfhiddenbehindhelmet, both boots pointingRIGHT oneleginfrontofother. Never front symmetry or pasted helmet. Draw authentic COARSE 48px sprites, all minimumdetails bigflat squares, NOT highresolutionpaintings. Same character SAME SCALE across ALL frames, helmet-to-soles37logicalrows (helmet24+waist3+legs10), anchoronly11rowsaboveatrest total48high39wide. The huge helmet must leave short visible bronze chest/shoulder/waist and legs below. Short thick suit arms grey gloves bronze cuffs, NEVER longer or thinner than source. Natural drawn bent knees, samewidth/length, no flattened/sheared/slidinglimbs. Greyanchor oneIDENTICALfullsize rigid object acrossframes: longgreyshank, ONEredband, brownrope/ring, widecurvedcrown andTWO completehookedflukes. Never changeanchorgeometry, never shorten/thin weapon evenseen fromside. Visible nearhand gripsSHANK; chainrunshandtoanchorRING. Side-onarmsposefollowref3, castsRIGHT. One-square#070211outline, NO texture/dithering/gradients/noisepixels. Paletteonly #070211 #0B021A #28160F #351215 #093742 #552113 #2D3041 #03455C #6F2610 #3D4150 #8C3815 #A84217 #E4221F #F94102 #E55222 #70747A #DC741C #00E9BE #01F3C5 #FAAC2A #FDCC31 #B2B0A8 #F6E4C8. Keep allsmallestpixelslargeflat consistentblocks, coarse like reference1. Transparentbackground NOglow/haze/scene/effects/shadows/water/sparks/shield/motionblur/text/labels/grid. Allfiguresuncropped above samefootbaseline, anchor/chainneverbelowground.
8 frames rowmajor 4 columns by 2 rows, desired4096x2048; eachcell1024square, feetlogicalrow99. 8-frame R DEPTH CHARGE:1 take anchor off back;2 raise anchor overhead BOTH hands;3 draw it back body arches;4 swing forward;5 IMPACT crouch anchor crown DOWN ground RIGHT at feet baseline;6 hold upright anchor planted;7 pull up;8 back toward side-on ready. Rigid fullsize anchor, no effects, nothing below baseline. EveryframeincludingfirstandlastisSIDE-ON RIGHT. Maintain same turnedhelmet shape and rigidanchor in ALLframes ofthisanimation, actualbentlegswhenkneesbend.
```

## hit

选用：`raw/hit_coarse_sheet.png`

```text
Create a production pixel-art animation strip. Ref1 is new RIGHT-facing coarse sprite appearance and pixel style ONLY, don't copy its runningpose. Ref2 is targetframe layout/size/timing; ref3 original3Dmotion ONLY. Every frame SIDE-ON facingRIGHT, visor turned toRIGHT with narrow far red eye, near red eye bright, near shoulder infront, farhalfhiddenbehindhelmet, both boots pointingRIGHT oneleginfrontofother. Never front symmetry or pasted helmet. Draw authentic COARSE 48px sprites, all minimumdetails bigflat squares, NOT highresolutionpaintings. Same character SAME SCALE across ALL frames, helmet-to-soles37logicalrows (helmet24+waist3+legs10), anchoronly11rowsaboveatrest total48high39wide. The huge helmet must leave short visible bronze chest/shoulder/waist and legs below. Short thick suit arms grey gloves bronze cuffs, NEVER longer or thinner than source. Natural drawn bent knees, samewidth/length, no flattened/sheared/slidinglimbs. Greyanchor oneIDENTICALfullsize rigid object acrossframes: longgreyshank, ONEredband, brownrope/ring, widecurvedcrown andTWO completehookedflukes. Never changeanchorgeometry, never shorten/thin weapon evenseen fromside. Visible nearhand gripsSHANK; chainrunshandtoanchorRING. Side-onarmsposefollowref3, castsRIGHT. One-square#070211outline, NO texture/dithering/gradients/noisepixels. Paletteonly #070211 #0B021A #28160F #351215 #093742 #552113 #2D3041 #03455C #6F2610 #3D4150 #8C3815 #A84217 #E4221F #F94102 #E55222 #70747A #DC741C #00E9BE #01F3C5 #FAAC2A #FDCC31 #B2B0A8 #F6E4C8. Keep allsmallestpixelslargeflat consistentblocks, coarse like reference1. Transparentbackground NOglow/haze/scene/effects/shadows/water/sparks/shield/motionblur/text/labels/grid. Allfiguresuncropped above samefootbaseline, anchor/chainneverbelowground.
2 frames rowmajor 2 columns by 1 row, desired2048x1024; eachcell1024square, feetlogicalrow99. 2-frame HIT:1 entire design body jolts2pixels LEFT,2 recovers. Same side-on legs and turned helmet, no damaged changes, same size anchor. EveryframeincludingfirstandlastisSIDE-ON RIGHT. Maintain same turnedhelmet shape and rigidanchor in ALLframes ofthisanimation, actualbentlegswhenkneesbend.
```

## dead

选用：`raw/dead_coarse_sheet.png`

```text
Create a production pixel-art animation strip. Ref1 is new RIGHT-facing coarse sprite appearance and pixel style ONLY, don't copy its runningpose. Ref2 is targetframe layout/size/timing; ref3 original3Dmotion ONLY. Every frame SIDE-ON facingRIGHT, visor turned toRIGHT with narrow far red eye, near red eye bright, near shoulder infront, farhalfhiddenbehindhelmet, both boots pointingRIGHT oneleginfrontofother. Never front symmetry or pasted helmet. Draw authentic COARSE 48px sprites, all minimumdetails bigflat squares, NOT highresolutionpaintings. Same character SAME SCALE across ALL frames, helmet-to-soles37logicalrows (helmet24+waist3+legs10), anchoronly11rowsaboveatrest total48high39wide. The huge helmet must leave short visible bronze chest/shoulder/waist and legs below. Short thick suit arms grey gloves bronze cuffs, NEVER longer or thinner than source. Natural drawn bent knees, samewidth/length, no flattened/sheared/slidinglimbs. Greyanchor oneIDENTICALfullsize rigid object acrossframes: longgreyshank, ONEredband, brownrope/ring, widecurvedcrown andTWO completehookedflukes. Never changeanchorgeometry, never shorten/thin weapon evenseen fromside. Visible nearhand gripsSHANK; chainrunshandtoanchorRING. Side-onarmsposefollowref3, castsRIGHT. One-square#070211outline, NO texture/dithering/gradients/noisepixels. Paletteonly #070211 #0B021A #28160F #351215 #093742 #552113 #2D3041 #03455C #6F2610 #3D4150 #8C3815 #A84217 #E4221F #F94102 #E55222 #70747A #DC741C #00E9BE #01F3C5 #FAAC2A #FDCC31 #B2B0A8 #F6E4C8. Keep allsmallestpixelslargeflat consistentblocks, coarse like reference1. Transparentbackground NOglow/haze/scene/effects/shadows/water/sparks/shield/motionblur/text/labels/grid. Allfiguresuncropped above samefootbaseline, anchor/chainneverbelowground.
8 frames rowmajor 4 columns by 2 rows, desired4096x2048; eachcell1024square, feetlogicalrow99. 8-frame DEATH:1 recoil;2 anchor slips off back lands UPRIGHT LEFT feet baseline;3 stagger slumps;4-6 sinks to SIT against anchor;7-8 same still seated. Keep turned-right helmet and bow body, dim eyes at finalseatedframes. Never lie horizontal or rotate face. Nothing below baseline. EveryframeincludingfirstandlastisSIDE-ON RIGHT. Maintain same turnedhelmet shape and rigidanchor in ALLframes ofthisanimation, actualbentlegswhenkneesbend.
```
