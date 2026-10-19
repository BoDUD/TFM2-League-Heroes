# 暮光星灵 佐伊：第 0 步，先画像素风原图（给 Codex 的提示词）

> 佐伊是一个**活泼的小个子女孩**，最显眼的是一大蓬**又长又多的魔法头发**：头顶两侧扎着两个**深藏青色的发髻**，头发主体是**深藏青色**的，里面夹着一条条**青绿、金黄、珊瑚橙、粉红色的星光彩带**，几缕头发上套着**金色的发环**，像飘在风里一样向身后**飘出去很长**。脸圆圆的，**一双大眼睛，左右颜色不一样（一只紫罗兰色、一只浅蓝色）**，咧嘴大笑。脖子上缠着一条**青绿色的围巾**；**深蓝色的短上衣**露出肚子；腰上是**蓝色多层的裹裙**，下面是深色短裤，腰带上一个**金色的圆扣**；两只手腕上戴**金色的手镯**；小腿套着**深藏青色的护腿**，光脚。请 Codex 画**两张全身像**（同一个佐伊，长相、颜色、**格子大小**都一样）：
> - **A：英雄联盟里的待机**（附图 1、2、8a）。3/4 正面朝右：胯往前、上身微微往后仰，两只手臂向身体两侧稍稍张开、手掌朝外摊开，脸朝右前方笑，头发向身后（画面左边）飘出去。
> - **B：站直的样子**（附图 8b 只看大小和地面线）。同一个佐伊**站直**，3/4 正面朝右，**两只手臂自然垂在身体两侧**（手离开身体一点，看得见手和手镯），两条腿并拢一点站稳，头发**垂在身后**、只往后飘一小段（不要飘出很远），这一张是后面所有动作的底子。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型（3/4 正面、侧面）。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的波比（小个子女孩）、迦娜（长头发飘起来）和卡西奥佩娅，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、6、7）。
> - **比例**：Q 版，**头大**（头连发髻约占身高的三分之一），身子短、腿细短；不要细长的写实比例。
> - **脸**（附图 3、6 特写）：圆脸，**两只大眼睛一样大、一样高、都看得见**（每只至少 2×3 格，带一个白色高光点）；**画面左边那只紫罗兰色，右边那只浅蓝色**（附图 6），咧嘴笑，嘴里露一点白牙；脸是暖肉色，两颊一点粉。
> - **头发**：深藏青色分 3–4 档，彩带的青绿、金黄、珊瑚橙、粉红每种分 2–3 档，彩带的边清楚；两个发髻圆鼓鼓的。
> - **画布用正方形 1536×1536**。**从发髻顶到脚底约 660 px，也就是约 60 格**，脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。头发、手全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。头发的深藏青、各色彩带、肉色皮肤、紫色眼睛、青绿围巾、深蓝上衣、蓝色裹裙、金色手镯和扣子、深藏青护腿要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（星星、传送门、气泡都放到第 3 步单独画）；不拿任何道具（没有乒乓拍、溜溜球、跳绳、冰淇淋）；不画地面，不画影子。
> - 交付：`outputs/zoe-picture/zoe-A.png`、`zoe-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/zoe-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/zoe_picture_done.zip`。

## 附图（在压缩包 `zoe_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_zoe_idle.png` | 英雄联盟原版佐伊的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_zoe_frontal.png` | 同一帧，正面 | 衣服、围巾、裙子、手镯、护腿 |
| `refs/3_zoe_head.png` | 头部特写（3/4） | 发髻、脸、眼睛、围巾 |
| `refs/4_zoe_back.png` | 同一帧的背后 | 头发从背后看：彩带怎么排 |
| `refs/5_zoe_splash.png` | 官方加载画面 | 气质、颜色、头发的彩带 |
| `refs/6_zoe_head_front.png` | 头部特写（正面） | 两只眼睛（一紫一蓝）、笑脸 |
| `refs/7_zoe_side.png` | 待机，接近侧面 | 侧面的身形、头发往后飘 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看大小和地面线） | 大小、地面线（灰）；**姿势按文字：站直、手臂垂下** |
| `style/11_style_poppy.png` | 本包的波比，8 倍放大，一格 = 一个像素 | **只看风格**：小个子女孩的大头、脸、眼睛在格子上怎么画 |
| `style/12_style_janna.png` | 本包的迦娜（8 倍） | **只看风格**：长头发在格子上怎么画 |
| `style/13_style_cassiopeia.png` | 本包的卡西奥佩娅（8 倍） | **只看风格**：格子密度、描边、金饰在格子上怎么画 |

## 提示词：`zoe-A.png` / `zoe-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a SMALL CHEERFUL GIRL with a HUGE MANE of LONG MAGICAL HAIR - two round DARK-NAVY BUNS on top of her head, the hair itself DARK NAVY woven with RIBBONS of TEAL, GOLD, CORAL-ORANGE and PINK starlight, streaming far behind her as if in a wind, GOLD RINGS round some of the strands; a round face with BIG EYES of two different colours (one VIOLET, one LIGHT BLUE) and a wide grin; a TEAL SCARF wound round her neck, a DARK-BLUE CROP TOP showing her belly, a BLUE LAYERED WRAP SKIRT over dark shorts with a round GOLD BUCKLE, GOLD BANGLES on both wrists, DARK-NAVY LEG WARMERS over BARE FEET (1 her idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: the clothes, the scarf, the skirt, the bangles, the leg warmers; 3 the head close-up in 3/4: the buns, the face, the eyes, the scarf; 4 the same from behind: how the ribbons run through the hair; 5 the official illustration: her mood, her colours, the ribbons of the hair; 6 the head close-up from the front: both eyes and the grin; 7 the idle nearly from the side: her body from the side, the hair streaming back). Images 8a and 8b are layout guides: where she goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a small girl's big head, face and eyes on the grid (11), long hair on the grid (12), the square density, the outline and gold trim on the grid (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (all the hair and both hands whole); the lowest point level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b).
PROPORTIONS: chibi - the head with its buns about ONE THIRD of her height; a short body, short slim legs; NOT realistic slim proportions.
THE FACE: round, warm skin with a little pink on the cheeks; TWO BIG EYES of the SAME size at the SAME height, both visible (each at least 2x3 squares, with one white highlight square): the eye on the image LEFT VIOLET, the one on the image RIGHT LIGHT BLUE (image 6); a wide grin showing a little white.
THE HAIR: the dark navy in 3-4 shades, each ribbon colour (teal, gold, coral-orange, pink) in 2-3 shades with clear edges; the two buns round and full.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the navy hair, each ribbon colour, the gold hair rings, the skin, the violet and the blue eye, the teal scarf, the dark-blue top, the blue skirt, the gold bangles and buckle, the navy leg warmers clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no stars, no portals, no bubbles, no sparkles, no glow), no props (no paddle, no yo-yo, no jump rope, no ice cream), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (zoe-A.png): her idle (images 1, 2 and 8a) - 3/4 view facing right (the face to the front-right): the hips forward and the upper body leaning back a little, both arms held a little out from her sides with the open palms turned outward, grinning, the hair streaming back behind her (to the image left); the NEAR leg on the image left in full tone, the FAR one on the image right a step darker; both soles on the ground line. She is about 660 px (about 60 squares) from the top of her buns to her soles.
POSE B (zoe-B.png): STANDING STRAIGHT - the SAME Zoe with the SAME 11-px squares, 3/4 view facing right: standing upright, BOTH ARMS HANGING at her sides a little away from the body (both hands and bangles visible), the legs a little apart and planted, the hair hanging down BEHIND her and streaming back only a short way (not far out); the same height, about 660 px (about 60 squares) from the top of her buns to her soles (image 8b shows only her size and the ground line).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头发、手完整，不出画。
- Q 版：头连发髻约占身高三分之一；**两只大眼睛一样大、一样高**、带白色高光，画面左边那只紫罗兰色、右边那只浅蓝色；咧嘴笑。
- 头发：深藏青色、两个圆发髻，夹着青绿、金黄、珊瑚橙、粉红的彩带。青绿围巾、深蓝短上衣、蓝色裹裙、金扣、金手镯、深藏青护腿、光脚。
- A：上身微微后仰、两只手臂稍稍张开手掌朝外、头发向身后飘出去；B：站直、两只手臂垂在两侧（看得见手和手镯）、头发垂在身后只飘一小段。
- 两张都是从发髻顶到脚底约 660 px（约 60 格），脚底在地面线上。
- 没有任何特效，没有道具。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- A、B 两张都画完后，最后写 `outputs/zoe-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/zoe_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/zoe/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回，和已合并的中单、小个子女孩（波比、阿尼维亚、卡西奥佩娅、吉格斯、辛德拉、璐璐）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）。
- 定下后第 1 步按游戏格子重画：3/4 正面（待机、选人卡片）和**侧面朝右**（所有动作的底子；脸用 3/4 正面的同一张脸）。动作帧不找 Codex，自己从造型的像素无损摆（`rig_zoe.py`：只整格平移、绕半格点的四分之一转、镜像）。英雄联盟的动作：普攻 Zoe_attack1 / Attack2 / Attack3，强化普攻 Zoe_Empowered_Attack；Q Spell1；E Spell3（踢出气泡）；R Zoe_Spell2（传送门）；W spell2_missile；跑 Zoe_Run1；死亡 Zoe_Death。
