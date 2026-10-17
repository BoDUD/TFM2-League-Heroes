# 斯维因（诺克萨斯统领）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 斯维因是一个**高大、冷峻的诺克萨斯老将军**：**银白色的长发**整齐地向后梳、垂到肩上；脸窄长、眉骨高、眉头紧锁，嘴角向下，表情阴沉。身上一件**及脚踝的近黑色长大衣**（灰紫色的翻领和衣摆滚边，衣摆上有方折纹的**灰色饰边**），大衣**内衬是暗红色**；大衣里面是**深色的胸甲**（一道道弧形的甲片，暗铜色高光）、**暗红色的衬里和腰间的皮带扣**、深色的长靴。肩上是**带尖棱的深色肩甲**，背后从肩甲垂下几片**像乌鸦羽毛一样的金属片**。他的一只手是**恶魔之手**：施法时从袖子里伸出**赤红到洋红的恶魔手臂，五根尖爪**。请 Codex 画**两张全身像**（同一个斯维因，长相、颜色、格子大小都一样；两张**都要用**，不是二选一）：
> - **A：平时的样子**（英雄联盟里的待机，附图 1）。他笔直地站着，大衣垂下来，双手垂在身侧，脸朝右前方。
> - **B：恶魔升华（大招变身）**。还是他本人、**同一个比例、同样的站姿**，但大衣**向身后两边张开，变成一对巨大的恶魔翅膀**：外面是近黑的大衣面料，里面是**暗红的内衬**，翅膀边缘撕裂成**一片片乌鸦羽毛一样的尖片**（附图 6 是他大衣张开的样子）；**近侧的手臂换成赤红的恶魔手臂**、五根尖爪张开（附图 7）；**两只眼睛发出红白色的光**；胸甲的缝里透出几道**暗红的恶魔裂纹**。英雄联盟里这个形态是特效叠在原模型上的，没有单独的模型，所以 B 照这段文字画。B 用来做附加包里变身后的整个身体和大招的动作。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型（PPU 1.5）。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的弗拉基米尔、潘森、莫甘娜（带翅膀）、卡特琳娜，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–5）。
> - **比例**：成年男性将军，**头稍大一点**（约占身高的四分之一，约 18 格），不要大头娃娃，也不要写实的细长比例。身材高、肩宽，大衣让他的下半身像一个长长的梯形。
> - **头**（附图 3 特写）：**银白长发**向后梳，两侧垂到肩，分出亮白、浅灰、灰、暗灰几档，不要糊成一片白；**偏白的肤色**，眉骨和颧骨的阴影明显；**两只眼睛一样大、一样高**，眼神凶，深色瞳孔；嘴角下垂。A 的眼睛是正常的，B 的眼睛发红白色光。
> - **大衣**：近黑偏紫灰的面料，翻领高高立起；衣摆到脚踝，下沿有**灰色方折纹饰边**；敞开的前襟露出**暗红内衬**。肩甲深色带尖棱，背后垂着几片乌鸦羽毛状的金属片（附图 4）。
> - **大衣里面**：深色弧形胸甲，**暗铜色的高光**；腰上一条深色皮带、铜色扣；长靴是深色的。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**。两只鞋底落在同一条地面线上。
> - **画布用正方形 1536×1536**：**从头发顶到鞋底约 792 px，也就是约 72 格**，鞋底在离画布底边约 146 px 的地方（附图 8a 的灰线）。**B 和 A 同一个比例**：他本人的头、身体大小一样，鞋底在同一条线上；翅膀向两边、向上张开，**总宽不超过约 1250 px**，翼尖不超过头顶以上约 220 px（附图 8b）。翅膀、恶魔手爪全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。近黑大衣、灰色饰边、暗红内衬、深色胸甲（暗铜高光）、银白头发、偏白皮肤、赤红恶魔手臂要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。**大衣很黑，一定要有偏紫灰的亮边和褶子的高光**，不然在深色背景上会糊成一团。
> - 不画任何特效（乌鸦、魂屑、恶魔光雾、吸取的光束都放到第 3 步单独画；B 的发光眼睛、恶魔手臂、胸口裂纹是身体的一部分，用平涂的亮色画，不要柔光）；不画手杖；不画地面，不画影子。
> - 交付：`outputs/swain-picture/swain-A.png`、`swain-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/swain-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/swain_picture_done.zip`。

## 附图（在压缩包 `swain_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_swain_idle.png` | 英雄联盟原版斯维因的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_swain_frontal.png` | 同一帧，正面 | 翻领、胸甲、内衬、皮带怎么排 |
| `refs/3_swain_head.png` | 头部特写 | 银白长发、窄长的脸、皱眉、深色胸甲的弧形甲片 |
| `refs/4_swain_back.png` | 同一帧的背后 | 肩甲、背后垂下的乌鸦羽毛状金属片、大衣下摆 |
| `refs/5_swain_splash.png` | 官方加载画面 | 气质（阴沉、暗红）、**赤红的恶魔手臂** |
| `refs/6_swain_demon_cast.png` | 大招落地的一帧：大衣向两边张开 | B 的翅膀：大衣怎么张开、外黑内红 |
| `refs/7_swain_demon_arm.png` | 放技能时伸出的恶魔手臂 | B 近侧的赤红恶魔手臂和五根尖爪 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（和 A 同一比例；翅膀在他身后向两边张开） | 他本人的位置和大小、地面线（灰） |
| `style/11_style_vladimir.png` | 本包的弗拉基米尔，8 倍放大，一格 = 一个像素（PPU 1.8） | **只看风格**：深红长衣、白发在这个密度下怎么分档 |
| `style/12_style_pantheon.png` | 本包的潘森（8 倍，PPU 1.5，和斯维因一样） | **只看风格**：铠甲和披风怎么分档、怎么留亮边 |
| `style/13_style_morgana.png` | 本包的莫甘娜（8 倍，PPU 1.5） | **只看风格**：暗色翅膀和长袍的画法 |
| `style/14_style_katarina.png` | 本包的卡特琳娜（8 倍，PPU 1.5） | **只看风格**：脸、眼睛、黑色衣服的亮边 |

## 提示词：`swain-A.png` / `swain-B.png`（同一段提示词，只换最后一句）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-7 are 3D renders and art of a character from the game: a TALL, GRIM OLD GENERAL with SWEPT-BACK SILVER-WHITE HAIR falling to his shoulders, a narrow long pale face with a heavy brow, a deep frown and a downturned mouth, an ANKLE-LENGTH NEAR-BLACK GREATCOAT (purple-grey lapels standing high, a GREY MEANDER TRIM along the hem) with a DARK CRIMSON LINING, under it a DARK CHEST ARMOUR of curved plates with dark-bronze highlights, a dark belt with a bronze buckle, dark tall boots, spiked dark pauldrons with a few RAVEN-FEATHER METAL PLATES hanging down his back; one of his arms is a DEMON ARM - crimson to magenta, with five long claws - that comes out of the sleeve when he casts (1 his idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: the lapels, the chest armour, the lining, the belt; 3 the head close-up: the silver hair, the narrow frowning face; 4 the same from behind: the pauldrons, the raven-feather plates, the coat hem; 5 the official illustration: his mood, dark crimson, the glowing demon arm; 6 his ultimate's landing frame: the coat flung open to both sides like wings, black outside and crimson inside; 7 a cast: the crimson demon arm with its claws stretched out). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, how a long dark-red coat and white hair are split into clear shades (11), how armour and a cape get lit edges (12), how dark wings and a long robe are drawn (13), a face with two clear eyes and black clothes with light edges (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). He is about 792 px (about 72 squares) from the top of his hair to his soles, the soles about 146 px above the bottom edge (the grey line of image 8a). Everything whole inside the picture with comfortable transparent margins, nothing cut off; both soles level on one ground line.
PROPORTIONS: an adult tall general - the head a little large (about a quarter of his height, about 18 squares), NOT a big-headed doll and NOT realistic slim proportions; broad shoulders, the long coat making his lower body a long trapezoid.
THE HEAD: SILVER-WHITE hair combed straight back and falling to the shoulders on both sides, in bright white / light grey / grey / dark grey (never one flat white blob); pale skin with clear shadows under the brow and the cheekbones; TWO EYES of the SAME size at the SAME height, a fierce look, dark pupils; the mouth turned down.
THE COAT: near-black with a purple-grey tint, the lapels standing high; down to the ankles with a GREY MEANDER TRIM on its lower edge; open at the front showing the DARK CRIMSON lining; dark spiked pauldrons; a few raven-feather metal plates hanging down the back.
UNDER THE COAT: dark curved chest plates with DARK-BRONZE highlights; a dark belt with a bronze buckle; dark tall boots.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the near-black coat with PURPLE-GREY LIT EDGES and fold highlights so it never turns into one black mass, the grey trim, the crimson lining, the dark chest plates with bronze highlights, the silver hair, the pale skin, the crimson demon arm clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no ravens, no soul fragments, no demon mist, no drain beams), no cane, no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (swain-A.png): his idle (image 1) - standing straight, the coat hanging down, both hands at his sides (normal dark-gloved hands), the face to the front-right.
POSE B (swain-B.png): DEMONIC ASCENSION - the SAME man at EXACTLY the same scale and square size as A, the same standing pose, the soles on the same ground line (image 8b), but his greatcoat FLUNG OPEN BEHIND HIM INTO A PAIR OF HUGE DEMON WINGS spreading to both sides and upwards (image 6): near-black coat cloth outside, the DARK CRIMSON lining inside, the wing edges torn into sharp RAVEN-FEATHER points; the NEAR arm is the CRIMSON-MAGENTA DEMON ARM with five long claws spread (images 5, 7); BOTH EYES GLOW red-white (flat bright squares, no glow halo); a few dark-crimson DEMONIC CRACKS show between the chest plates. The wings at most about 1250 px wide in total and their tips at most about 220 px above his hair; the wings, the claws and everything whole inside the picture.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，翅膀、恶魔手爪完整，不出画。
- 比例：成年高个将军，头约占身高四分之一（约 18 格），不是大头娃娃；两只眼睛一样大、一样高。
- 头：银白长发向后梳、垂到肩，分出几档灰白；脸窄长、皱眉、嘴角下垂。
- 大衣：近黑偏紫灰、有亮边和褶子高光；翻领高；衣摆灰色方折纹饰边；暗红内衬；肩甲、背后乌鸦羽毛状金属片。
- 里面：深色弧形胸甲带暗铜高光、皮带、长靴。
- A：笔直站立，双手垂在身侧（正常的深色手套）；从头发顶到鞋底约 792 px（约 72 格），鞋底在同一条地面线上。
- B：和 A **同一个比例、同样的格子、同样的站姿**；大衣张开成一对恶魔翅膀（外黑内红、边缘撕成羽毛状尖片）；近侧是赤红恶魔手臂、五根尖爪；眼睛红白色发光（平涂）；胸甲缝里几道暗红裂纹；总宽不超过约 1250 px。
- 没有任何特效、没有手杖。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/swain-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/swain_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/swain/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_rell_hd.py` 的做法），和已合并的中单法师（弗拉基米尔、维克托、辛德拉、奥莉安娜）、潘森、德莱厄斯按游戏里的大小并排，**每个动作的显示高度**都要和德莱厄斯比（潘森的教训），B 带翅膀还要量宽度，给用户定大小；PPU 1.5（不超过 1.5，用户规则）。
- 定下后第 1 步按游戏格子重画 A 和 B，再自己做动作帧（塔姆 / 芮尔 / 雷克塞的方式，`tools/art/rig_swain.py`，无损：只平移、整块直角转、整行移）：跑步照 Swain_Run；普攻 Swain_Attack1–3（远程，恶魔之手一挥）；Q 解脱之触 Swain_Spell1（恶魔手臂前伸）；E 永不复行 Swain_Spell3；W 帝国视界是被动自动放，用 Swain_Spell2 做一个可选的抬手；R 恶魔升华 Swain_DemonWindup → Swain_DemonLand；死亡 Swain_Death。B 形态（附加包整身换图）：b_idle / b_run / b_attack / b_skill / b_hit / b_dead，主包里 R 期间的普攻和技能也用 B 的动作。
