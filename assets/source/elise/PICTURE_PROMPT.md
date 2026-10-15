# 伊莉丝（蜘蛛女皇）：先画像素风原图（第 0 步，给 Codex 的提示词）

> 伊莉丝是一个**冷艳、危险的蜘蛛女祭司**，能在**人形**和**蜘蛛形**之间变身。这一步请 Codex 画**四张**全身像素风原图：**人形 A、B**（同一个人、同样的长相衣服，只差姿势）和**蜘蛛形 A、B**（同一只蜘蛛，只差角度）。用户各挑一张，之后第 1 步再按选中的画造型。这一版每个游戏像素约 **1.5 格**（附图 10–15 是本包同样密度的加里奥、布隆、泽丽、奈德丽、奈德丽的美洲狮、杰斯）：像素块清楚、整齐、大小一致，描边约 **2 格**，人形身材**偏 Q 版**。你画的原图会直接按格子读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–9）。
> - **人形的头**（附图 3 特写）：一个冷艳的女人，头约占身高的**四分之一到三分之一**（偏 Q 版，像附图 13 的奈德丽、15 的杰斯）；**苍白偏灰紫的皮肤**；**深红黑色的头发**向上梳成**两根尖角一样的发髻**（尖端红色），额前一个**深色尖头冠**；**红色的眼睛**，**两只眼睛看得清**；**深红的嘴唇**，冷笑；**脸朝右前方平视**。
> - **人形的衣服**：**黑紫色的紧身长裙 / 紧身衣**，胸前一个**深红色 V 形领口镶边**、腰上和腿侧有**深红色的条纹**；**手指是又长又尖的黑色爪子**；双腿裹在黑色里，**脚尖是尖的**（她像踮着脚站）。**背上伸出六条又长又弯的黑色蜘蛛腿**，每条腿**末端是发红光的尖爪**（只是红色，不画光晕特效），向上、向两侧张开，像一圈王冠围在她身后——**不能挡住她的脸**。
> - **蜘蛛形**（附图 6–9）：**一只很大的蜘蛛**，没有人的上半身。**背甲是黑紫色的、层层尖刺状的甲片**，甲片边缘和背上的脊是**发亮的深红色**，背顶一个**红色菱形斑**；**八条又长又弯的腿**，腿是**黑色带一点深青灰**，**每条腿的尖端是红色的尖爪**；前面一对**弯弯的大毒牙**和几只**红色的小眼睛**。整只蜘蛛很暗，所以**每块甲片和每条腿的上边缘都要有亮一点的高光、红色要鲜亮**，不能糊成一团黑。
> - **人形 A = 英雄联盟的待机**（附图 1）：踮着脚尖站，近侧膝盖微微弯，**两只爪子手抬在胸前、手指张开像爪子**，背后六条蜘蛛腿张开。**人形 B = 施法站姿**：两脚分开站稳（仍是尖脚尖），**一只手高高举在头旁边、五指张开**，另一只手垂在身侧，背后蜘蛛腿向上高高竖起。
> - **蜘蛛形 A = 3/4 视角朝右**（附图 6：头在画面右前方，能看到前脸、毒牙和背甲的顶面）；**蜘蛛形 B = 正侧面朝右**（附图 7：头在画面右边，能看到一侧的四条腿在前、另一侧的四条腿稍暗在后）。两张都是待机站姿，八只脚尖落在同一条地面线上。
> - **人形姿势**：3/4 正面朝右（脸朝右前方，胸口朝向看画的人），**近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、稍暗、稍高**，两只脚尖落在同一条地面线上。
> - **比例**：人形**偏 Q 版**——头大一点，身材苗条但不要细长的写实比例；风格完全照附图 10–15。蜘蛛形按真实蜘蛛的比例，但整体紧凑。
> - **大小**：**人形 A、B 用竖版画布 1024×1536**：她**从头顶（不算发髻尖角和蜘蛛腿）到脚尖约 684 px，也就是约 57 格**，脚尖在离画布底边约 196 px 的地方（附图 5a 的灰线），蜘蛛腿和发髻尖角可以高出头顶，全部在画面里。**蜘蛛形 A、B 用横版画布 1536×1024**：同样的格子大小，**从背甲顶到脚尖约 540 px（约 45 格）**，**从头到身后的腿约 860 px（约 72 格）**，脚尖在离画布底边约 124 px 的地方（附图 5b 的灰线），全部在画面里。
> - **像素块**：大小一致的方块，**每块 12 像素**，横平竖直对齐成网格（这张图会被按格子读回，一格就是一个像素）；**外轮廓一圈 2 块宽的近黑描边**；内部每种材质 3–4 档平涂，不要细碎的单个杂色格。
> - 不画任何特效（毒液、蛛网、茧、红光光晕、小蜘蛛、变身的烟都在第 3 步单独画）；不画地面和影子。
> - 交付：`outputs/elise-picture/elise-human-A.png`、`elise-human-B.png`（1024×1536 竖版）、`elise-spider-A.png`、`elise-spider-B.png`（1536×1024 横版），都是**真透明背景**；原始生成图原样放进 `outputs/elise-picture/raw/`；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `elise_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_elise_human.png` | 英雄联盟原版伊莉丝人形待机，3/4 朝右 | 人形的颜色、形状、**角度**、A 的姿势 |
| `refs/2_elise_human_frontal.png` | 同一帧，正面 | 紧身衣的红色镶边、蜘蛛腿怎么从背上长出来 |
| `refs/3_elise_head.png` | 头部特写 | 发髻尖角、头冠、红眼睛、嘴唇、皮肤颜色 |
| `refs/4_elise_back.png` | 同一帧的背后 | 背上六条蜘蛛腿的根部 |
| `refs/5_elise_splash.png` | 官方加载画面 | 气质（冷艳、危险） |
| `refs/5a_layout_human.png` | 人形的布局示意（模型剪贴，只看位置和大小） | 竖版画布上她的位置、脚尖线 |
| `refs/5b_layout_spider.png` | 蜘蛛形的布局示意（同一比例的格子） | 横版画布上蜘蛛的位置、脚尖线 |
| `refs/6_spider_34.png` | 蜘蛛形待机，3/4 朝右 | 蜘蛛 A 的样子和**角度** |
| `refs/7_spider_side.png` | 蜘蛛形待机，正侧面朝右 | 蜘蛛 B 的样子和**角度** |
| `refs/8_spider_front.png` | 蜘蛛形待机，几乎正面 | 背甲、红色菱形斑、腿怎么排 |
| `refs/9_spider_head.png` | 蜘蛛正面特写（背甲下面的脸） | 毒牙、红眼睛、甲片的红边 |
| `style/10_style_galio.png` | 本包同样密度（每游戏像素 1.5 格）的加里奥待机（8 倍放大，一格 = 一个像素） | **只看风格**：像素粗细、描边、比例 |
| `style/11_style_braum.png` | 同样密度的布隆（8 倍） | **只看风格** |
| `style/12_style_zeri.png` | 同样密度的泽丽（8 倍） | **只看风格** |
| `style/13_style_nidalee.png` | 同样密度的奈德丽人形（8 倍） | **只看风格**：女英雄的头身比例 |
| `style/14_style_nidalee_cougar.png` | 同样密度的奈德丽美洲狮（8 倍） | **只看风格**：野兽形态的大小和画法 |
| `style/15_style_jayce.png` | 同样密度的杰斯（8 倍），本包最新的英雄 | **只看风格** |

## 提示词 1：`elise-human-A.png`（人形，英雄联盟的待机）

十七张图都附上，顺序同上表。

```text
Seventeen attached images. Images 1-9 are 3D renders and art of a character from the game: a cold, beautiful, dangerous spider priestess who turns between a HUMAN form and a giant SPIDER form (1 the woman in 3/4 view facing right - the look, the ANGLE and the POSE of this picture; 2 the same from the front: the red trim of her dress and how the six spider legs grow from her back; 3 her head close-up: the horn-like hair, the crown, the red eyes, the lips, the skin; 4 the same from behind: the roots of the spider legs; 5 the official illustration: her cold, menacing mood; 5a THIS picture's layout guide: where she goes on the canvas, the grey line is the ground; 5b the spider pictures' layout guide: ignore it here; 6-9 the spider form - not drawn here). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-15 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chunky chibi-ish proportions and head size (13 and 15 are the closest: a woman and a man of this series).
Create ONE pixel-art picture of the woman, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha). She is about 684 px (about 57 squares) from the top of her head (not counting the hair horns and the spider legs) to the tips of her toes, the toe tips about 196 px above the bottom edge (the grey line of image 5a); the spider legs and hair horns may rise above her head; everything whole, comfortable transparent margins, nothing cut off; both toe tips on one ground line.
THE WOMAN: cold and beautiful. THE HEAD, a little big (chibi-ish, about a quarter to a third of her height): PALE grey-lilac skin; DARK RED-BLACK hair swept up into TWO HORN-LIKE POINTS with red tips, a dark pointed crown on the brow; RED EYES, TWO EYES clearly readable; dark red lips, a cold smile; the face turned to the front-right, looking straight ahead. THE BODY: slim; a BLACK-PURPLE tight gown with a DEEP RED V-shaped trim at the neckline and DEEP RED stripes on the waist and the sides of the legs; long, sharp BLACK CLAW fingers; legs in black ending in POINTED toes (she stands as if on tiptoe). SIX long curved BLACK SPIDER LEGS grow from her back, each ending in a sharp RED claw tip (red colour only, no glow effect), spread up and out behind her like a crown - NEVER covering her face.
THE POSE: League's idle (image 1): 3/4 view facing right (face to the front-right, chest toward the viewer), on tiptoe, the near knee a little bent, BOTH CLAWED HANDS RAISED BEFORE HER CHEST with the fingers spread like claws, the six spider legs spread behind her: the NEAR leg on the image LEFT in full tone, the FAR leg on the image RIGHT a step darker and a little higher; both toe tips on one ground line.
PROPORTIONS: chibi-ish like images 10-15 - a slightly big head, slim but NOT slender realistic proportions, legs not too long.
THE PIXEL GRID: every square the SAME size, 12 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure and the spider legs; inside it every material in its own 3-4 flat shades, no stray single odd squares: the skin pale grey-lilac, the hair dark red-black with red tips, the eyes red, the gown black-purple with LIGHTER purple edge highlights so it never reads as one black blob, the trim and stripes deep red with a bright red highlight, the claws black with a grey edge light, the spider legs black-purple with lit top edges and bright red tips; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no venom, no webs, no glow aura, no spiderlings), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 2：`elise-human-B.png`（人形，施法站姿）

十七张图都附上，顺序同上表；**最好把 A 画好的那张也附上**，让人和衣服一模一样。

```text
Seventeen attached images (plus, if you have it, your finished picture A of the same woman: keep her IDENTICAL). Images 1-9 are 3D renders and art of a character from the game: a cold, beautiful, dangerous spider priestess who turns between a HUMAN form and a giant SPIDER form (1 the woman in 3/4 view facing right - the look and the ANGLE of this picture; 2 the same from the front: the red trim of her dress and how the six spider legs grow from her back; 3 her head close-up: the horn-like hair, the crown, the red eyes, the lips, the skin; 4 the same from behind: the roots of the spider legs; 5 the official illustration: her cold, menacing mood; 5a THIS picture's layout guide: where she goes on the canvas, the grey line is the ground; 5b the spider pictures' layout guide: ignore it here; 6-9 the spider form - not drawn here). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-15 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chunky chibi-ish proportions and head size (13 and 15 are the closest: a woman and a man of this series).
Create ONE pixel-art picture of the woman, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha). She is about 684 px (about 57 squares) from the top of her head (not counting the hair horns and the spider legs) to the tips of her toes, the toe tips about 196 px above the bottom edge (the grey line of image 5a); the spider legs, the hair horns and the raised hand may rise above her head; everything whole, comfortable transparent margins, nothing cut off; both toe tips on one ground line.
THE WOMAN: exactly as in picture A - PALE grey-lilac skin; DARK RED-BLACK hair swept up into TWO HORN-LIKE POINTS with red tips, a dark pointed crown on the brow; RED EYES, two eyes clearly readable; dark red lips, a cold smile; the face to the front-right looking straight ahead, the head a little big (a quarter to a third of her height); a BLACK-PURPLE tight gown with a DEEP RED V-shaped neckline trim and DEEP RED stripes on the waist and legs; long sharp BLACK CLAW fingers; POINTED toes; SIX long curved BLACK SPIDER LEGS from her back with sharp RED claw tips (colour only, no glow).
THE POSE: a casting stance: 3/4 view facing right (face to the front-right, chest toward the viewer), feet apart and planted (still on pointed toes), ONE CLAWED HAND RAISED HIGH beside her head with the fingers spread, the other hand down at her side, the six spider legs raised HIGH above and behind her like a crown, never covering her face: the NEAR leg on the image LEFT in full tone, the FAR leg on the image RIGHT a step darker and a little higher; both toe tips on one ground line.
PROPORTIONS: chibi-ish like images 10-15 - a slightly big head, slim but NOT slender realistic proportions, legs not too long.
THE PIXEL GRID: every square the SAME size, 12 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure and the spider legs; inside it every material in its own 3-4 flat shades, no stray single odd squares (colours as in picture A: the gown black-purple with LIGHTER purple edge highlights, the trim deep red with a bright red highlight, the spider legs with lit top edges and bright red tips); light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no venom, no webs, no glow aura, no spiderlings, no magic in the raised hand), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 3：`elise-spider-A.png`（蜘蛛形，3/4 视角）

十七张图都附上，顺序同上表。

```text
Seventeen attached images. Images 6-9 are 3D renders of THIS picture's subject from the game, the SPIDER FORM of a spider priestess (6 the spider in 3/4 view facing right - the look, the ANGLE and the POSE of this picture; 7 the same exactly side-on facing right; 8 the same nearly from the front: the carapace, the red diamond mark, how the eight legs are arranged; 9 a close-up of its face from the front, under the carapace: the fangs, the red eyes, the red edges of the plates). 5b is THIS picture's layout guide: where the spider goes on the canvas, the grey line is the ground; 5a is the other pictures' guide: ignore it. Images 1-5 are the same character in human form (ignore them here, except for her red-and-black colours). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-15 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading (image 14, a beast form of this series, shows how big an animal form is and how it is drawn).
Create ONE pixel-art picture of the spider, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha). The spider is about 540 px (about 45 squares) from the top of its carapace to the tips of its feet and about 860 px (about 72 squares) from its head to its hindmost legs, the foot tips about 124 px above the bottom edge (the grey line of image 5b); everything whole, comfortable transparent margins, nothing cut off; all foot tips on one ground line.
THE SPIDER: a GIANT spider, no human body. The CARAPACE: BLACK-PURPLE, built of layered SPIKY PLATES, the plate edges and the ridge along the back a GLOWING DEEP RED (colour only, no glow effect), a RED DIAMOND mark on the top. EIGHT long curved legs, BLACK with a hint of DARK TEAL-GREY, each ending in a sharp RED claw tip. At the front a pair of big curved FANGS and a cluster of small RED EYES. It is very dark, so give EVERY plate and EVERY leg a lighter lit top edge and keep the reds BRIGHT - it must never read as one black blob.
THE POSE: idle, standing on all eight legs, the body raised a little: 3/4 view facing right (image 6): the head on the image RIGHT and toward the viewer, its face, fangs and the top of the carapace visible; the NEAR legs in full tone, the FAR legs a step darker; all foot tips on one ground line.
PROPORTIONS: a real spider's build, compact; like the beast form in image 14, not cute, not chibi.
THE PIXEL GRID: every square the SAME size, 12 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the spider; inside it every material in its own 3-4 flat shades, no stray single odd squares: the carapace black-purple with violet edge highlights, the red edges and diamond deep red with a bright red highlight, the legs black / dark teal-grey with lit top edges, the claw tips red, the eyes bright red, the fangs dark with a grey edge light; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no venom, no webs, no glow aura, no spiderlings), no background, no ground, no shadow, no text, no frame, no human, no other characters.
```

## 提示词 4：`elise-spider-B.png`（蜘蛛形，正侧面）

十七张图都附上，顺序同上表；**最好把蜘蛛 A 画好的那张也附上**，让蜘蛛一模一样。

```text
Seventeen attached images (plus, if you have it, your finished spider picture A: keep the spider IDENTICAL, only the angle changes). Images 6-9 are 3D renders of THIS picture's subject from the game, the SPIDER FORM of a spider priestess (7 the spider EXACTLY SIDE-ON facing right - the ANGLE and the POSE of this picture; 6 the same in 3/4 view; 8 the same nearly from the front: the carapace, the red diamond mark, how the eight legs are arranged; 9 a close-up of its face from the front, under the carapace: the fangs, the red eyes, the red edges of the plates). 5b is THIS picture's layout guide: where the spider goes on the canvas, the grey line is the ground; 5a is the other pictures' guide: ignore it. Images 1-5 are the same character in human form (ignore them here, except for her red-and-black colours). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-15 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading (image 14, a beast form of this series drawn side-on, shows how big an animal form is and how it is drawn).
Create ONE pixel-art picture of the spider, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha). The spider is about 540 px (about 45 squares) from the top of its carapace to the tips of its feet and about 860 px (about 72 squares) from its head to its hindmost legs, the foot tips about 124 px above the bottom edge (the grey line of image 5b); everything whole, comfortable transparent margins, nothing cut off; all foot tips on one ground line.
THE SPIDER: exactly as in spider picture A - a GIANT spider, no human body; a BLACK-PURPLE carapace of layered SPIKY PLATES, the plate edges and the back ridge DEEP RED (colour only, no glow), a RED DIAMOND mark on the top; EIGHT long curved legs, BLACK with a hint of DARK TEAL-GREY, each with a sharp RED claw tip; a pair of big curved FANGS and small RED EYES at the front; every plate and leg with a lighter lit top edge, the reds BRIGHT.
THE POSE: idle, standing on all eight legs: EXACTLY SIDE-ON facing IMAGE RIGHT (image 7): the head and fangs on the image right, one side's four legs in front in full tone, the other side's four legs a step darker showing behind them; all foot tips on one ground line.
PROPORTIONS: a real spider's build, compact; like the beast form in image 14, not cute, not chibi.
THE PIXEL GRID: every square the SAME size, 12 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the spider; inside it every material in its own 3-4 flat shades, no stray single odd squares (colours as in spider picture A); light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no venom, no webs, no glow aura, no spiderlings), no background, no ground, no shadow, no text, no frame, no human, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底）；人形 A、B 竖版 1024×1536，蜘蛛 A、B 横版 1536×1024；四周留边，人物、蜘蛛腿、发髻尖角都完整，不出画。
- 人形的头：苍白偏灰紫的皮肤、深红黑色的两根尖角发髻（尖端红）、深色尖头冠、**红眼睛、两只眼睛看得清**、深红嘴唇、**平视前方**；头约占身高四分之一到三分之一。
- 人形的衣服：黑紫紧身衣、胸前深红 V 形镶边、腰和腿侧深红条纹、黑色长爪、尖脚尖；**背后六条黑色蜘蛛腿 + 红色尖爪**，张开在身后，**不挡脸**。
- A：踮脚尖、两只爪子手抬在胸前；B：两脚分开站稳、一只手高举在头旁边、蜘蛛腿高高竖起。A 和 B 是同一个人、同样的格子大小、同样大的头和身体。
- 蜘蛛：没有人的上半身；黑紫色尖刺甲片 + 深红色的甲片边和背脊 + 背顶红色菱形斑；八条黑色（带深青灰）的腿 + 红色尖爪；前面一对大毒牙、几只红色小眼睛；**甲片和腿都有亮一点的上边缘，红色鲜亮，不糊成一团黑**。A 是 3/4 视角朝右，B 是正侧面朝右；A 和 B 是同一只蜘蛛。
- 人形从头顶到脚尖约 684 px（约 57 格）；蜘蛛从背甲顶到脚尖约 540 px（约 45 格）、从头到身后的腿约 860 px（约 72 格）。
- 人形近侧腿在画面左边亮色、远侧腿在右边稍暗稍高；脚尖都在同一条水平线上；没有任何特效。
- **每块 12 像素、大小一致、对齐网格**；2 块宽的近黑外描边；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述（提示词里本来就没写名字）。
- 全部画完后最后写 `outputs/elise-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/elise/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 12 px），按它自己的格子读回，和同位置英雄（奈德丽人形 / 美洲狮、伊芙琳、卡兹克等）并排、按游戏里的大小给用户挑人形 A / B、蜘蛛 A / B 各一张（密度已定 PPU 1.5）。
- 选定后写第 1 步 `MODEL_PROMPTS.md`：人形 **3/4 正面**（待机 + 选人卡）+ 动作需要的侧身；蜘蛛按用户选的角度；同一个高度、同一套格子、同样的细节；原稿 1:1 按格读回，绝不先画大再缩。背后的六条蜘蛛腿是刚体部件，动作里只平移和整块摆动，不变形。
- 同一张脸贯穿所有人形帧；人形跑步照英雄联盟（她踮脚滑行）；蜘蛛跑步是八条腿交替的爬行循环（Codex 画）。附加包会整身换成蜘蛛，所以蜘蛛要有自己的待机、跑步、受击、阵亡（`c_*`）。
