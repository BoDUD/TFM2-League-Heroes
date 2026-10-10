# 佛耶戈：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 佛耶戈还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**那把大剑的位置**，长相、衣服、王冠、剑完全一样：**A = 英雄联盟里的待机：破败王剑扛在肩上，剑身从肩头朝前上方伸出、越过头顶**（附图 1、2）；**B = 英雄联盟的第二个待机：一只手在腰边握着剑柄，剑身斜着拖在身后、剑尖朝后下方**（附图 8），人物整体更矮更紧凑。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40–42 行）。
> - **长相照英雄联盟原版**（附图 1–8）：破败之王佛耶戈，一个苍白、阴郁、骄傲的亡灵国王。**一头乱蓬蓬的银白色头发**，盖住额头、垂到脸颊两边；头顶一顶**青绿色发光的荆棘王冠**（一圈晶莹的尖刺，和剑同色）；**脸很苍白（灰白皮肤）**，眼睛是**发青绿光的细眼**，表情冷淡。
> - **身体和衣服**：一件**深藏青（近黑的蓝紫色）长风衣**，高高的立领，衣摆垂到膝盖后面、下摆分叉；**风衣敞开，露出苍白的胸口**，胸口中间一个**倒三角的黑色印记（边缘一圈青绿色）**；两肩和前臂套着**带尖刺的深藏青铠甲**（边缘有银灰亮边），双手是**黑色的尖指铠甲手套**；腰上一条**棕红色的宽皮带，一排银色圆钉**；深藏青紧身裤；膝盖上是**带尖刺的护膝**，小腿到脚是**尖头的深藏青铠甲靴**。
> - **剑（破败王剑）**：一把**巨大的双手大剑**，比他还长：**剑身是发光的青绿色（翡翠绿），有一道亮色的中线**，剑柄是暗色的；护手是**一个很大的、十字形的青绿色装饰护手**，四个方向都伸出带钩的尖角（像一个华丽的十字）。
> - **黑雾**：原版他身边会飘一点黑雾，这里**不要画**（特效第 3 步再单独画）。
> - **姿势**（附图 1、2 = A；附图 8 = B）：3/4 正面朝右，站姿松垮、有点颓废又傲慢，**两只脚都踩在地面线上**。A：近侧（离我们近的那只）手握剑柄，把剑扛在远侧肩上，剑身朝画面**右上方**伸出、越过头顶，大护手在他脑后 / 肩后；远侧手垂在身旁。B：近侧手在腰边握剑柄，剑身斜着拖在身后、剑尖朝画面**左下方**，但**剑尖不能低于脚底**；远侧手垂在身旁。**脸和两只手都不能被挡住**。
> - **风格和比例照附图 9–11**（之前让你画的泰隆、雷克顿、赵信）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（银白头发、荆棘王冠、青绿眼睛在小尺寸下要看得出来）；**身体、风衣收得紧凑**。他的衣服很暗：**风衣用偏紫的深藏青、铠甲用更蓝一点的深藏青 + 银灰亮边，皮带是棕红，皮肤和头发是最亮的灰白，剑是鲜亮的青绿**，深色部分之间要有清楚的亮边，不要糊成一团黑。
> - **画布用横版 1536×1024**：从头顶（王冠）到脚底约 640 px；剑和护手都在画面里，不能出画（A 的剑尖可以比头高很多，留足边距）。
> - 不画任何特效（黑雾、灵魂、刺击光、冲击波第 3 步再单独画）；脚底是最低点，平平地落在一条地面线上（游戏在脚下画血条），剑尖和风衣下摆也不能低于这条线。
> - 交付：`outputs/viego-picture/viego-model-A.png`、`outputs/viego-picture/viego-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `viego_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_viego_league_front.png` | 英雄联盟原版佛耶戈待机，3/4 朝右 | 颜色、形状、A 的姿势（剑扛肩上） |
| `refs/2_viego_league_frontal.png` | 同一帧，正面 | 敞开的风衣、胸口的倒三角印记、皮带、护膝 |
| `refs/3_viego_league_head.png` | 头和上身的特写 | 银白乱发、荆棘王冠、苍白的脸、青绿眼睛、立领 |
| `refs/4_viego_league_back.png` | 同一帧的背后 | 风衣后摆、剑在背后的样子 |
| `refs/5_viego_splash.png` | 官方加载画面 | 气质（颓废、骄傲的亡灵国王） |
| `refs/6_viego_league_run.png` | 英雄联盟里他跑动的几个瞬间 | 风衣怎么飘、剑怎么拿 |
| `refs/7_viego_league_actions.png` | 普攻、Q、W 蓄力、大招的瞬间 | 手和剑怎么动 |
| `refs/8_viego_league_idle2.png` | 第二个待机：剑拖在身后 | **B 的剑的位置** |
| `style/9_style_talon.png` | 你之前的泰隆像素图 | **只看风格**（暗色系的近战刺客，最近通过的一张） |
| `style/10_style_renekton.png` | 你之前的雷克顿像素图 | **只看风格** |
| `style/11_style_xinzhao.png` | 你之前的赵信像素图 | **只看风格**（持长兵器的近战） |

## 提示词 A：`viego-model-A.png`（剑扛在肩上）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture, the greatsword resting on his shoulder; 2 the same from the front: the open coat, the bare pale chest with its triangle mark, the belt and the knee guards; 3 the head and upper body close-up: the messy white hair, the teal-green thorn crown, the pale face, the glowing teal eyes, the high collar; 4 the same pose from behind: the coat tails and the sword behind him; 5 the official illustration: his mood; 6 moments of him running: how the coat flows and how he carries the sword; 7 moments of his attack and spells: how the hands and the sword move; 8 his second idle with the sword trailing low behind him - not used in this version). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, also a dark-clothed melee fighter).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 640 px from the top of his crown to the soles of his feet, centred, comfortable transparent margins, nothing cut off (the whole sword, its tip and its big cross guard inside the picture).
The character: Viego, the Ruined King, a pale, gloomy, proud undead king. HEAD: MESSY SILVER-WHITE HAIR falling over the forehead and down beside the cheeks; on top a GLOWING TEAL-GREEN THORN CROWN (a ring of sharp crystal spikes, the same green as the sword); a PALE GREY-WHITE face with narrow GLOWING TEAL EYES and a cold expression. BODY: slim; a long DARK NAVY (near-black blue-violet) COAT with a HIGH COLLAR, its tails split and hanging to the back of the knees; the coat OPEN over a BARE PALE CHEST with a black INVERTED-TRIANGLE MARK edged in teal in the middle; SPIKED DARK NAVY ARMOUR on the shoulders and forearms with silver-grey edges; BLACK POINTED ARMOURED GAUNTLETS; a wide REDDISH-BROWN LEATHER BELT with a row of silver studs; tight dark navy trousers; SPIKED KNEE GUARDS; pointed dark navy armoured boots. THE SWORD (the Blade of the Ruined King): a HUGE two-handed GREATSWORD longer than he is tall: a GLOWING TEAL-GREEN (emerald) blade with a bright central line, a dark grip, and a very big ornate CROSS-SHAPED TEAL-GREEN GUARD whose four arms end in hooked spikes; here it RESTS ON HIS FAR SHOULDER: his near hand holds the grip, the big guard sits behind his head and shoulders, the blade points forward and UP to the image's upper right, over his head (images 1 and 2).
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the white hair, the thorn crown and the teal eyes drawn a little oversized so they read at small size), a slim body. Keep the body and the coat COMPACT. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands.
Pose: League's own idle (images 1 and 2): a loose, weary yet arrogant stance facing image right, both feet planted, the near hand holding the sword on the far shoulder, the far arm hanging at his side. The soles of his feet are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the coat tails stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the coat a violet-tinged dark navy, the armour a bluer dark navy with clear silver-grey edge highlights, the belt reddish brown, the skin and hair the brightest pale grey-white, the eyes and the chest mark's edge glowing teal, the sword a vivid teal-green with a white-green highlight line; the dark parts separated by clear light edges, never one black blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no black mist, no souls, no light rings, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`viego-model-B.png`（剑拖在身后）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look of this picture; 2 the same from the front: the open coat, the bare pale chest with its triangle mark, the belt and the knee guards; 3 the head and upper body close-up: the messy white hair, the teal-green thorn crown, the pale face, the glowing teal eyes, the high collar; 4 the same pose from behind: the coat tails; 5 the official illustration: his mood; 6 moments of him running: how the coat flows and how he carries the sword; 7 moments of his attack and spells: how the hands and the sword move; 8 HIS SECOND IDLE WITH THE SWORD TRAILING LOW BEHIND HIM - the sword position of this picture). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, also a dark-clothed melee fighter).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 640 px from the top of his crown to the soles of his feet, centred, comfortable transparent margins, nothing cut off (the whole sword, its tip and its big cross guard inside the picture).
The character: Viego, the Ruined King, a pale, gloomy, proud undead king. HEAD: MESSY SILVER-WHITE HAIR falling over the forehead and down beside the cheeks; on top a GLOWING TEAL-GREEN THORN CROWN (a ring of sharp crystal spikes, the same green as the sword); a PALE GREY-WHITE face with narrow GLOWING TEAL EYES and a cold expression. BODY: slim; a long DARK NAVY (near-black blue-violet) COAT with a HIGH COLLAR, its tails split and hanging to the back of the knees; the coat OPEN over a BARE PALE CHEST with a black INVERTED-TRIANGLE MARK edged in teal in the middle; SPIKED DARK NAVY ARMOUR on the shoulders and forearms with silver-grey edges; BLACK POINTED ARMOURED GAUNTLETS; a wide REDDISH-BROWN LEATHER BELT with a row of silver studs; tight dark navy trousers; SPIKED KNEE GUARDS; pointed dark navy armoured boots. THE SWORD (the Blade of the Ruined King): a HUGE two-handed GREATSWORD longer than he is tall: a GLOWING TEAL-GREEN (emerald) blade with a bright central line, a dark grip, and a very big ornate CROSS-SHAPED TEAL-GREEN GUARD whose four arms end in hooked spikes; here it TRAILS LOW BEHIND HIM (image 8): his near hand holds the grip at his hip with the big guard beside his near hip, the blade slanting down and BACK toward the image's lower left, its tip just ABOVE the ground line behind his feet.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the white hair, the thorn crown and the teal eyes drawn a little oversized so they read at small size), a slim body. Keep the body and the coat COMPACT. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands.
Pose: League's second idle (image 8): a loose, weary yet arrogant stance facing image right, both feet planted, the near hand at his hip holding the trailing sword, the far arm hanging at his side. The soles of his feet are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the sword's tip and the coat tails stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the coat a violet-tinged dark navy, the armour a bluer dark navy with clear silver-grey edge highlights, the belt reddish brown, the skin and hair the brightest pale grey-white, the eyes and the chest mark's edge glowing teal, the sword a vivid teal-green with a white-green highlight line; the dark parts separated by clear light edges, never one black blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no black mist, no souls, no light rings, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物和整把剑（剑尖、十字护手）都完整。
- 银白乱发、青绿荆棘王冠、苍白的脸 + **发青绿光的眼睛**。
- 深藏青长风衣（立领、敞开）、苍白胸口 + 青绿边的倒三角印记、带刺的肩甲和臂甲（银灰亮边）、黑色尖指手套、棕红钉扣皮带、带刺护膝、尖头铠甲靴。
- 巨大的青绿发光大剑 + 大十字形护手。A 扛在肩上、剑身朝右上越过头顶；B 拖在身后、剑尖朝左下但高于脚底。
- 脸和两只手没被挡住；深色部分之间有亮边，不糊成一团黑。
- 脚底是最低点，落在一条水平线上；剑尖和风衣下摆不低于它；没有黑雾或任何特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/viego-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/viego/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40–42 行；剑很长，A 的剑会让每帧宽很多——行数按王冠到脚底算）。
- 技能动作里剑和握剑的手是一整块转动的部件；施法身体 = 待机身体，手不能藏起来。
