# 艾瑞莉娅：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 艾瑞莉娅还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**飞刃的摆法和站姿**，长相、发型、衣服完全一样：**A = 英雄联盟里的待机：几把飞刃在她身边展开成扇形（一把高高竖在背后肩上方，两三把斜向下伸在身体两侧），一只手抬到脸旁**（附图 1、2）；**B = 收拢站姿：飞刃收成一束、竖着叠在背后（像收起的折扇），两手自然放在身前/身侧**（附图 8）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 36–38 行）。
> - **长相照英雄联盟原版**（附图 1–8，经典造型）：刀锋舞者艾瑞莉娅，冷静、坚毅的艾欧尼亚女武者。**很长的深靛蓝色头发**（发尾在背后束成一条低马尾，一直垂到腰下），前额一条**银色头冠**，头顶竖着一根**深红色、银边的尖角发饰**；白皙皮肤，**青蓝色眼睛**，红唇。
> - **身体和衣服**：**银白色的肩甲**（边缘向外卷起成尖钩）；**深红（洋红偏红）色的紧身衣**，胸前一块银色胸甲、领口一颗**青蓝色宝石**；腰前垂下一条**深红色长前摆**（到大腿中间），两侧有银色甲片；**深红色的长袖护臂**；**深藏青色紧身裤**；**深红色长靴**，膝盖上有**银色的尖角护膝**。
> - **武器 = 飞刃**：她不握武器，几把**又长又弯的刀刃浮在身边**（像弯月形的羽毛，刃面深藏青 + 深红，边缘和刀背是银色，刃根有小块青蓝宝石）。
> - **姿势**（附图 1、2 / 8）：3/4 正面朝右站立，脸朝观众。A：飞刃展开成扇形但**收得紧凑**，扇面的总宽度不超过她身高的 0.9 倍，竖在背后的那把尖不要比她头顶高出太多；一只手抬到脸旁，另一只手张开垂在身侧。B：飞刃收成一束竖在背后（从肩膀到大腿），整体最窄；两腿微分站稳。**脸、两只手都不能被挡住**，飞刃不能盖住脸、手和身体正面。
> - **风格和比例照附图 9–11**（之前让你画的萨勒芬妮、莎弥拉、辛德拉）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；**头只比英雄联盟模型稍大一点，不要 Q 版**（头顶到下巴大约占身高的 1/4），身材修长；颜色要分得开：**头发深靛蓝（亮蓝紫高光），衣服深红 + 洋红高光，盔甲和刀背银白（浅灰蓝暗部），裤子深藏青，眼睛和宝石青蓝，皮肤白皙暖色**。深色多的角色要给头发、刀刃、裤子加亮边和高光，不要糊成一片黑。
> - **画布用横版 1536×1024**：A 从头顶（头冠尖）到鞋底约 720 px，B 约 740 px；飞刃、手都在画面里，不能出画。
> - 不画任何特效（刀光、拖尾、能量第 3 步再单独画）；**鞋底是最低点**，平平地落在一条地面线上。
> - 交付：`outputs/irelia-picture/irelia-model-A.png`、`outputs/irelia-picture/irelia-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `irelia_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_irelia_league_front.png` | 英雄联盟原版艾瑞莉娅待机，3/4 朝右 | 颜色、形状、A 的姿势 |
| `refs/2_irelia_league_frontal.png` | 同一帧，正面 | 肩甲、胸甲、前摆、靴子 |
| `refs/3_irelia_league_head.png` | 头的特写 | 头顶尖角发饰、银色头冠、深靛蓝长发、青蓝眼睛 |
| `refs/4_irelia_league_back.png` | 同一帧的背后 | 马尾、背面、飞刃 |
| `refs/5_irelia_splash.png` | 官方加载画面 | 气质（冷静、坚毅） |
| `refs/6_irelia_league_run.png` | 英雄联盟里她跑动的几个瞬间 | 腿、头发和飞刃怎么动 |
| `refs/7_irelia_league_actions.png` | 普攻、Q、W、E、大招的瞬间 | 手和飞刃怎么动 |
| `refs/8_irelia_league_folded.png` | 飞刃收在背后的站姿 | **B 的姿势** |
| `style/9_style_seraphine.png` | 你之前的萨勒芬妮像素图 | **只看风格**（少女） |
| `style/10_style_samira.png` | 你之前的莎弥拉像素图 | **只看风格**（女剑士） |
| `style/11_style_syndra.png` | 你之前的辛德拉像素图 | **只看风格**（最近通过） |

## 提示词 A：`irelia-model-A.png`（飞刃展开成扇形）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture; 2 the same from the front: the shoulder guards, the breastplate, the tabard and the boots; 3 the head close-up: the silver tiara and the crimson crest spike on top of her head, the long dark indigo hair, the cyan eyes; 4 the same pose from behind: the ponytail and the blades; 5 the official illustration: her mood; 6 moments of her running: how the legs, the hair and the blades move; 7 moments of her attack and spells: how the hands and the blades move; 8 the folded stance - not used in this version). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 11 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 720 px from the tip of her tiara to the soles of her boots, centred, comfortable transparent margins, nothing cut off (the blades and the hands inside the picture).
The character: Irelia, the Blade Dancer, a calm, resolute Ionian warrior woman. HEAD: very LONG DARK INDIGO-BLUE HAIR tied in a low ponytail falling down her back past her waist, a SILVER TIARA band on her forehead and a tall CRIMSON CREST SPIKE edged in silver rising from the top of her head; fair skin, CYAN-BLUE EYES, red lips. BODY: SILVER-WHITE SHOULDER GUARDS whose edges curl outward into hooks; a CRIMSON fitted bodysuit with a silver breastplate and a CYAN GEM at the collar; a long CRIMSON TABARD hanging in front to mid-thigh with silver plates at its sides; crimson long sleeves / bracers; DARK NAVY LEGGINGS; CRIMSON BOOTS with pointed SILVER KNEE GUARDS. WEAPON: she holds no weapon - several LONG CURVED FLOATING BLADES hover around her, crescent-shaped like feathers, the flat dark navy and crimson, the edges and spines silver, a small cyan gem at each blade's root.
Proportions: game-sprite proportions like images 9-11 but NOT chibi - the head only a little bigger than in the 3D model (tiara tip to chin about one quarter of her height), a slim, tall body, long legs. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands.
Pose: League's idle (images 1 and 2): standing, facing image right, legs apart; one hand raised beside her face, the other arm out and down with the fingers spread; the FLOATING BLADES FANNED OUT AROUND HER but kept COMPACT: one blade standing tall behind her shoulder (its tip only a little above her head), two or three blades angled down and out at both sides of her body, the whole fan no wider than 0.9 of her height. The blades never cover her face, her hands or the front of her body. The soles of her boots are the lowest thing in the picture, on one ground line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the hair dark indigo with bright blue-violet highlights, the bodysuit and tabard crimson with magenta highlights, the armour and blade spines silver-white with cool grey-blue shadows, the blades dark navy and crimson with a bright edge, the leggings dark navy with a lit edge, the eyes and gems cyan, the skin fair and warm; dark materials get lit edges and highlights so they never melt into black; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no slash trails, no motion lines, no energy, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`irelia-model-B.png`（飞刃收在背后）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - her look, but with the pose of image 8; 2 the same from the front: the shoulder guards, the breastplate, the tabard and the boots; 3 the head close-up: the silver tiara and the crimson crest spike on top of her head, the long dark indigo hair, the cyan eyes; 4 the same pose from behind: the ponytail and the blades; 5 the official illustration: her mood; 6 moments of her running: how the legs, the hair and the blades move; 7 moments of her attack and spells: how the hands and the blades move; 8 THE FOLDED STANCE - the pose of this picture). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 11 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 740 px from the tip of her tiara (or the blades, if higher) to the soles of her boots, centred, comfortable transparent margins, nothing cut off (the blades and the hands inside the picture).
The character: Irelia, the Blade Dancer, a calm, resolute Ionian warrior woman. HEAD: very LONG DARK INDIGO-BLUE HAIR tied in a low ponytail falling down her back past her waist, a SILVER TIARA band on her forehead and a tall CRIMSON CREST SPIKE edged in silver rising from the top of her head; fair skin, CYAN-BLUE EYES, red lips. BODY: SILVER-WHITE SHOULDER GUARDS whose edges curl outward into hooks; a CRIMSON fitted bodysuit with a silver breastplate and a CYAN GEM at the collar; a long CRIMSON TABARD hanging in front to mid-thigh with silver plates at its sides; crimson long sleeves / bracers; DARK NAVY LEGGINGS; CRIMSON BOOTS with pointed SILVER KNEE GUARDS. WEAPON: she holds no weapon - several LONG CURVED FLOATING BLADES hover around her, crescent-shaped like feathers, the flat dark navy and crimson, the edges and spines silver, a small cyan gem at each blade's root.
Proportions: game-sprite proportions like images 9-11 but NOT chibi - the head only a little bigger than in the 3D model (tiara tip to chin about one quarter of her height), a slim, tall body, long legs. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands.
Pose: the folded stance (image 8): standing upright, facing image right, legs slightly apart and firmly planted; her hands relaxed in front of / beside her body; the FLOATING BLADES FOLDED TOGETHER INTO ONE NARROW UPRIGHT BUNDLE BEHIND HER BACK like a closed fan, from above her shoulder down to her thigh, the tips pointing up, peeking out beside her shoulder and hip. The figure is narrow and compact. The blades never cover her face, her hands or the front of her body. The soles of her boots are the lowest thing in the picture, on one ground line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the hair dark indigo with bright blue-violet highlights, the bodysuit and tabard crimson with magenta highlights, the armour and blade spines silver-white with cool grey-blue shadows, the blades dark navy and crimson with a bright edge, the leggings dark navy with a lit edge, the eyes and gems cyan, the skin fair and warm; dark materials get lit edges and highlights so they never melt into black; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no slash trails, no motion lines, no energy, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物、飞刃、双手都完整。
- 深靛蓝长发 + 低马尾、银色头冠 + 头顶深红银边尖角发饰、青蓝眼睛、白皙皮肤。
- 银白卷钩肩甲、深红紧身衣 + 银胸甲 + 领口青蓝宝石、深红长前摆、深红护臂、深藏青紧身裤、深红长靴 + 银色尖角护膝。
- 弯月形飞刃（深藏青 + 深红刃面、银色刀背、刃根青蓝宝石），不拿在手里。
- A：飞刃扇形展开但紧凑（总宽不超过身高的 0.9 倍），一只手抬到脸旁；B：飞刃收成一束竖在背后，整体最窄。
- 头不要 Q 版（头冠尖到下巴约占身高 1/4），身材修长。
- 脸和两只手没被挡住；飞刃不挡身体正面。
- 鞋底是最低点，落在一条水平线上；没有任何刀光或特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变；深色（头发、裤子、刀刃）有亮边和高光，不糊成黑块。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/irelia-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/irelia/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 36–38 行，从头冠尖到鞋底算，直接在游戏尺寸画，不画大再缩）。
- 技能动作里飞刃是整块的刚性部件（只平移 / 90° 整转 / 翻转，不任意角度旋转）；施法身体 = 待机身体；动作侧身朝右（只有待机朝观众，见诺提勒斯的教训）；刀光、拖尾、刃墙都是特效（第 3 步）。
