# 辛德拉：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 辛德拉还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**两只手臂的姿势**，长相、头盔、衣服完全一样：**A = 英雄联盟里的待机：两臂向下张开、爪子张着，一边膝盖弯起，悬浮着**（附图 1、2）；**B = 画面左侧那只手举到头旁边（像托着一颗暗黑法球，但不画球），另一只手弯在胸前，两腿并拢**（附图 8），人物更窄更紧凑。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40–42 行，和维克托、赛娜差不多高）。
> - **长相照英雄联盟原版**（附图 1–8，经典造型）：暗黑元首辛德拉，一个高傲、强大的暗黑女法师，**悬浮在空中**。**头上一顶紫色头盔**，两侧各有一根**很高的弯角**向上弯成新月形，角尖发紫光；头盔正面一块**发洋红色光的面罩 / 眼睛**（眼睛是亮洋红色）；头盔下露出脸的下半部分（**深一点的肤色、红唇**）；**银白色的长直发**从头盔两侧垂到腰。
> - **身体和衣服**：肩上一对**紫色的尖角护肩**（金色描边 + 卷纹）；**深紫色的紧身胸甲 / 束腰**，金色细边，腰上一条亮紫色腰带和金扣；**露出的肚子和大腿是小麦色皮肤**；腰两侧垂下**两片很长的深紫色裙摆**（金边、下摆尖尖地拖在身后）；**到大腿的深紫黑色长靴**，靴尖尖的；**手臂上是紫色的护臂**，手套发亮紫光，**手指是尖尖的黑紫色爪子**。
> - **姿势**（附图 1、2 / 8）：3/4 正面朝右，**悬浮着**：脚尖朝下、两腿一前一后（A 一个膝盖弯起；B 两腿并拢），裙摆在身后飘（她朝右，所以裙摆往**画面左边**飘）。**脸、两只手（爪子）都不能被挡住**，头发不能盖住手。
> - **风格和比例照附图 9–11**（之前让你画的萨勒芬妮、霞、维克托）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（头盔、洋红色眼睛、红唇、银发在小尺寸下要看得出来）；**两根弯角可以比模型短一点**（大约头盔高度的一倍），不然一帧太高；身体、手臂、裙摆都要收得紧凑。她浑身是紫色系，容易糊成一片：**头盔和护肩用偏蓝的紫 + 浅紫高光，胸甲和裙摆用更深的黑紫，金边用最亮的金色，皮肤是暖小麦色，头发是带一点青的银白，眼睛和手套的光是亮洋红 / 亮紫**。
> - **画布用横版 1536×1024**：A 从角尖到脚尖约 760 px，B 约 760 px；角、裙摆、手都在画面里，不能出画。
> - 不画任何特效（法球、光球、紫色能量第 3 步再单独画）；**脚尖是最低点**，平平地落在一条地面线上（她在游戏里离地很近地飘着，游戏在脚下画血条），裙摆不能低于这条线。
> - 交付：`outputs/syndra-picture/syndra-model-A.png`、`outputs/syndra-picture/syndra-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `syndra_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_syndra_league_front.png` | 英雄联盟原版辛德拉待机，3/4 朝右 | 颜色、形状、A 的姿势 |
| `refs/2_syndra_league_frontal.png` | 同一帧，正面 | 胸甲、腰带、裙摆、长靴 |
| `refs/3_syndra_league_head.png` | 头和上身的特写 | 弯角头盔、洋红色眼睛、红唇、银发、护肩 |
| `refs/4_syndra_league_back.png` | 同一帧的背后 | 头发、裙摆在身后的样子 |
| `refs/5_syndra_splash.png` | 官方加载画面 | 气质（高傲、强大） |
| `refs/6_syndra_league_run.png` | 英雄联盟里她移动的几个瞬间 | 悬浮时腿和裙摆怎么动 |
| `refs/7_syndra_league_actions.png` | 普攻、Q、W、E、大招的瞬间 | 手和爪子怎么动 |
| `refs/8_syndra_league_hand_up.png` | 一只手举到头旁边的待机 | **B 的姿势** |
| `style/9_style_seraphine.png` | 你之前的萨勒芬妮像素图 | **只看风格**（女法师） |
| `style/10_style_xayah.png` | 你之前的霞像素图 | **只看风格** |
| `style/11_style_viktor.png` | 你之前的维克托像素图 | **只看风格**（中路法师，最近通过） |

## 提示词 A：`syndra-model-A.png`（两臂向下张开）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture; 2 the same from the front: the corset, the belt, the skirt panels and the boots; 3 the head and upper body close-up: the horned helmet, the glowing magenta eyes, the red lips, the silver hair and the pauldrons; 4 the same pose from behind: the hair and the skirt panels; 5 the official illustration: her mood; 6 moments of her moving: how the floating legs and the skirt move; 7 moments of her attack and spells: how the hands and claws move; 8 one hand raised beside her head - not used in this version). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 11 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 760 px from the tips of the horns to the tips of her toes, centred, comfortable transparent margins, nothing cut off (the horns, the hands and the skirt inside the picture).
The character: Syndra, the Dark Sovereign, a proud and powerful dark sorceress who FLOATS in the air. HEAD: a VIOLET HELMET with two TALL CURVED HORNS rising on both sides into a crescent, their tips glowing violet; on its front a GLOWING MAGENTA visor / eyes (bright magenta eyes); below the helmet the lower half of her face (warm tan skin, RED LIPS); LONG STRAIGHT SILVER-WHITE HAIR falling from both sides of the helmet to her waist. BODY: a pair of pointed VIOLET PAULDRONS with gold trim and scroll ornaments; a tight DARK VIOLET CORSET with thin gold edges, a bright violet belt with gold buckles; a bare midriff and bare thighs in warm tan skin; two very LONG DARK VIOLET SKIRT PANELS hanging from her hips with gold edges, their pointed ends trailing behind her; THIGH-HIGH dark violet-black BOOTS with pointed toes; VIOLET BRACERS on the forearms, gloves glowing violet, the fingers sharp black-violet CLAWS.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the helmet, the magenta eyes, the red lips and the silver hair drawn a little oversized so they read at small size), a slim body. The horns may be a little shorter than in the model (about one helmet-height above it) so the figure is not too tall. Keep the figure COMPACT: arms, hair and skirt close to her body. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands (the hair stays behind the arms).
Pose: League's idle (images 1 and 2): floating, facing image right, BOTH ARMS SPREAD DOWN AND OUT from her sides with the claws open, one knee bent and the other leg hanging straight, toes pointing down, the skirt panels trailing behind her (toward image LEFT). The tips of her toes are the lowest thing in the picture, on one ground line (the game draws the health bar under them; she floats just above the ground); the skirt panels stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the helmet and pauldrons a bluish violet with light lilac highlights, the corset and skirt a darker black-violet, the trims the brightest gold, the skin a warm tan, the hair silver-white with a slight cyan tint, the eyes and the glowing gloves bright magenta / violet; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no dark spheres, no orbs, no energy, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`syndra-model-B.png`（一只手举到头旁边）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - her look, but with the pose of image 8; 2 the same from the front: the corset, the belt, the skirt panels and the boots; 3 the head and upper body close-up: the horned helmet, the glowing magenta eyes, the red lips, the silver hair and the pauldrons; 4 the same pose from behind: the hair and the skirt panels; 5 the official illustration: her mood; 6 moments of her moving: how the floating legs and the skirt move; 7 moments of her attack and spells: how the hands and claws move; 8 ONE HAND RAISED BESIDE HER HEAD - the pose of this picture). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 11 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 760 px from the tips of the horns to the tips of her toes, centred, comfortable transparent margins, nothing cut off (the horns, the hands and the skirt inside the picture).
The character: Syndra, the Dark Sovereign, a proud and powerful dark sorceress who FLOATS in the air. HEAD: a VIOLET HELMET with two TALL CURVED HORNS rising on both sides into a crescent, their tips glowing violet; on its front a GLOWING MAGENTA visor / eyes (bright magenta eyes); below the helmet the lower half of her face (warm tan skin, RED LIPS); LONG STRAIGHT SILVER-WHITE HAIR falling from both sides of the helmet to her waist. BODY: a pair of pointed VIOLET PAULDRONS with gold trim and scroll ornaments; a tight DARK VIOLET CORSET with thin gold edges, a bright violet belt with gold buckles; a bare midriff and bare thighs in warm tan skin; two very LONG DARK VIOLET SKIRT PANELS hanging from her hips with gold edges, their pointed ends trailing behind her; THIGH-HIGH dark violet-black BOOTS with pointed toes; VIOLET BRACERS on the forearms, gloves glowing violet, the fingers sharp black-violet CLAWS.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the helmet, the magenta eyes, the red lips and the silver hair drawn a little oversized so they read at small size), a slim body. The horns may be a little shorter than in the model (about one helmet-height above it) so the figure is not too tall. Keep the figure COMPACT: arms, hair and skirt close to her body. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands (the hair stays behind the arms).
Pose: image 8: floating, facing image right, the hand on the image-LEFT side RAISED BESIDE HER HEAD with the palm up and the claws open (as if a dark sphere floated above it - but draw no sphere; image 8), the other arm bent in front of her chest with the claws open, both legs hanging close together, toes pointing down, the skirt panels trailing behind her (toward image LEFT). The tips of her toes are the lowest thing in the picture, on one ground line (the game draws the health bar under them; she floats just above the ground); the skirt panels stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the helmet and pauldrons a bluish violet with light lilac highlights, the corset and skirt a darker black-violet, the trims the brightest gold, the skin a warm tan, the hair silver-white with a slight cyan tint, the eyes and the glowing gloves bright magenta / violet; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no dark spheres, no orbs, no energy, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物、弯角、裙摆、双手都完整。
- 紫色弯角头盔 + **发光的洋红色眼睛**、红唇、银白色长直发。
- 紫色尖护肩（金边）、深紫胸甲 + 亮紫腰带金扣、小麦色肚子和大腿、两片长裙摆（金边）、到大腿的黑紫长靴、紫色护臂 + 黑紫爪子。
- A：两臂向下张开、一个膝盖弯起；B：画面左侧的手举在头旁边、另一只手弯在胸前、两腿并拢。
- 脸和两只手（爪子）没被挡住；头发在手臂后面；整体紧凑。
- 脚尖是最低点，落在一条水平线上；裙摆不低于它；没有任何法球或特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变；紫色的几种材质分得开。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/syndra-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/syndra/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40–42 行，按角尖到脚尖算还是按头盔顶到脚尖算要说清楚）。
- 技能动作里手臂是整块转动的部件；施法身体 = 待机身体，手不能藏起来；法球都是特效（第 3 步）。
