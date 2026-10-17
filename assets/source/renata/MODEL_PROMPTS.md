# 烈娜塔：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户选了你第 0 步画的 **A**（`1_picked_A.png`），定的大小是：游戏里**从头发顶到脚底 40 行**，每个游戏像素 1.5 格，也就是她要画成 **60 格高**。
> - 用户还要求：
>   - **头放大到约四分之一**：从头发顶到下巴（面罩下沿）约 **15 格**（A 里只有 18%，在游戏里脸和面罩看不清）。下巴以下约 45 格，身体仍然高挑修长。
>   - **C（大招）去掉多余的手臂**：你第 0 步的 C 里有三条手臂（金色机械臂高举、后面又多一条戴黑手套的棕色手臂举起、还有一条垂着）。**只留两条**：近侧的金色机械臂高高举起，远侧戴黑手套的手臂垂在身侧。
>   - **背后的炼金机械单独画一张**。
> - 我把 A 按这个比例直接缩好了（`2_target_body.png`，每格 12 px）；把 C 按她同样的身高缩好了（`6_target_ult.png`，每格 12 px，画布 1536）。**大小、位置、姿势、头身比都对，但是糊了**：脸、品红眼睛和面罩糊成几格，银蓝挑染没了，披肩的金边、马甲的金扣、胸针、机械臂的品红线条都糊在一起；脖子那里还有一道接缝。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 12 px，横平竖直对齐网格**，就像一个像素画师照着 A / C，在目标图的格子里一格一格重画出来。
> - **每种图各画两稿**：她（A）两稿、大招（C）两稿、机械单独两稿。

## 大小和位置

- **她（A）**：画布 **1024 × 1024**，每格 12 px，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
  - **头发顶在 y = 240**（绿线），**下巴在 y ≈ 420**（蓝线），**脚底在 y = 960**（红线），两只脚底在同一条线上。
  - 左右位置、远侧手把手枪竖举在肩旁、近侧金色机械臂垂在身侧的样子，都照 `2_target_body.png`。
- **大招（C）**：画布 **1536 × 1536**，每格 12 px，网格从左上角对齐（`7_layout_ult.png`）。
  - **头发顶在 y = 720**（绿线），**下巴约 y = 900**（蓝线，头和 A 一样大，约 15 格），**脚底在 y = 1440**（红线）。
  - 她站的位置、背后机械的大小和位置照 `6_target_ult.png`：机械约 83 格宽，最高处在 y ≈ 372，**全部在脚底线以上**。
  - 近侧（画面左边）的**金色机械臂高高举过头顶**，手指张开；远侧戴黑手套的手臂**垂在身侧**；**没有第三条手臂**。腰间的手枪插在枪套里。
- **机械单独**：画布 **1536 × 1536**，每格 12 px。**照你画的大招稿，把她整个人去掉，只留背后的机械，位置一格不动**（这样我能把机械直接叠回她身后）。机械挡住她的地方，原来被她挡住的部分要补画完整。

## 要画清楚的地方（她）

- **头**（`4_head.png`，**画大**，头发顶到下巴约 15 格）：
  - **黑紫色长发**，分 3–4 档，边上带一点亮紫的高光；额前一大缕**银蓝色挑染**（亮银白、浅蓝灰、蓝灰三档）向后梳成一道大波浪；长发垂到背后，到腰附近。
  - **棕色皮肤**；**品红色的眼睛**（一只眼约 2 格，只用在眼睛上），黑而锋利的眉毛。
  - **银色金属面罩**盖住口鼻到下巴（亮银、蓝灰、暗灰三档），侧面一格**金色小圆环**。
- **身体**：
  - **白色短披肩外套**（白、浅蓝灰、蓝灰三档），**金色卷纹边**，肩头一点灰色浮雕，里衬**品红色**。
  - **深藏青色收腰马甲**，分 3 档，边上亮一档，免得在深色背景上看不清；一排**金色尖扣**（每颗约 1 格）。
  - **品红衬衫和领带**，领口**金框红宝石胸针**（约 2 格）。
  - **白色高腰喇叭长裤**，分 3 档，裤脚变宽，侧面一排小圆扣。
  - **黑色短靴**，**金色鞋尖、金色鞋跟**。
- **近侧的金色机械臂**（亮金、金、暗棕金三档），沿手臂 1 格宽的**品红线条**，手指是细长的金爪。
- **远侧手戴黑手套**，A 里竖举一把**深色长枪管手枪**（黑、暗灰，带一点红和金的小饰件）。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再画一圈黑；没有孤立的杂色格。

## 要画清楚的地方（机械）

- 铜金色的机体（亮金、金、暗棕金三档），**品红色的管线**；
- 两侧几片**又长又尖的刀翼**：深色刀身（深灰、蓝灰），刀身上**品红和金色的纹路**；刀翼朝外、朝上伸；
- 后面挂一块**暗红棕色的斗篷**（3 档）。
- 一圈近黑外描边；刀尖可以是 1–2 格宽，但要连续。

## 干净

- 像素画的样子和附图 8–11 一样（本包的卡特琳娜、芸阿娜、斯维因、娜美，都是每游戏像素 1.5 格；8 倍放大，一格 = 一个像素）：大小一致的方块，对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照 A / C。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效（化学波、飞弹、护盾、发光的雾都不画）。

## 附图（压缩包 `renata_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节**全照它 |
| `2_target_body.png` | A 按新比例（头约四分之一）缩到游戏大小，每格 12 px 放在 1024 画布上（糊的） | **她的大小、位置、姿势、头身比**照它，糊的地方重画 |
| `3_layout.png` | 同一张加网格线：绿线 = 头发顶 y 240，蓝线 = 下巴 y 420，红线 = 脚底 y 960 | 对齐网格，头和脚底的位置 |
| `4_head.png` | A 的头（读回后 8 倍放大） | 头发、挑染、品红眼睛、面罩 |
| `5_picked_C.png` | 你第 0 步画的 C | 大招姿势和机械的**样子**（**多出来的那条手臂不要**） |
| `6_target_ult.png` | C 按她同样的身高缩好，每格 12 px 放在 1536 画布上（糊的） | 大招里她和机械的**大小、位置** |
| `7_layout_ult.png` | 同一张加网格线：绿线 = 头发顶 y 720，蓝线 = 下巴 y 900，红线 = 脚底 y 1440 | 对齐网格 |
| `style/8_style_katarina.png` … `11_style_nami.png` | 本包的卡特琳娜、芸阿娜、斯维因、娜美（每游戏像素 1.5 格），8 倍放大 | **只看风格**：这个密度下一格有多大，脸怎么画，描边，分档 |

## 提示词 1：`renata-model-1.png`、`renata-model-2.png`（她，两稿）

附全部 11 张图。**用 image_gen 画。**

```text
Attached images: 1 an approved pixel-art picture of this character - a tall commanding woman with very long black-violet hair and a big silver-blue streak swept back from the forehead, brown skin, magenta eyes, a silver metal respirator mask over her mouth and nose with a small gold ring, a white short cape-jacket with gold scroll trim and magenta lining, a dark navy fitted vest with gold spike clasps, a magenta shirt and tie with a gold-framed ruby brooch, white high-waisted flared trousers, black ankle boots with gold toes and heels, a GOLD-AND-MAGENTA MECHANICAL near arm with long golden claw fingers, and a dark long-barrelled pistol held upright in her black-gloved far hand (the LOOK, the COLOURS and the DETAILS to keep); 2 the same woman shrunk to her final game size on a 1024x1024 canvas, 12 px a square, with her HEAD MADE BIGGER - about a quarter of her height: the SIZE, the PLACE, the POSE and the HEAD-TO-BODY PROPORTION are right, but it is muddy (the face, the magenta eyes and the mask blurred, the silver-blue streak lost, the gold trim, the vest clasps, the brooch and the magenta lines of the arm smeared together, a seam at the neck); 3 the same with grid lines every 5 squares: the green line = the top of her hair (y 240), the blue line = her chin, the lower edge of the mask (y 420), the red line = her soles (y 960); 4 the head of image 1 enlarged; 5 the ultimate pose drawn before; 6 and 7 the ultimate pose at her scale (for another picture); 8-11 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - copy their pixel-art look.
Draw with the image generator ONE clean pixel-art picture of the same woman: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2: every square 12 px, aligned on one straight grid starting at the canvas corner, the top of her hair at y 240, her chin at y 420 (the head from the hair's top to the chin about 15 squares, about a quarter of her height - much bigger than in image 1, so the face reads at game size), her soles at y 960 on one ground line; the far hand holding the pistol upright beside her shoulder, the golden mechanical near arm hanging at her side - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: BLACK-VIOLET HAIR in 3-4 shades with a few lighter violet highlight squares, falling down her back to the waist, a big SILVER-BLUE STREAK (bright silver-white, light blue-grey, blue-grey) swept back from the forehead in one wave; BROWN skin; MAGENTA EYES about 2 squares each, the eye colour used only there, sharp dark brows; the SILVER RESPIRATOR MASK (bright silver, blue-grey, dark grey) over the mouth and nose down to the chin with ONE gold square ring on its side; the WHITE CAPE-JACKET (white, light blue-grey, blue-grey) with GOLD SCROLL TRIM and MAGENTA lining; the DARK NAVY VEST in 3 shades with a lighter edge so it reads on a dark background, a row of GOLD SPIKE CLASPS about 1 square each; the MAGENTA SHIRT and TIE, the GOLD-FRAMED RUBY BROOCH (about 2 squares); the WHITE FLARED TROUSERS in 3 shades, wider at the hem, a row of small round buttons on the side; BLACK ANKLE BOOTS with GOLD toes and GOLD heels; the GOLDEN MECHANICAL ARM (bright gold, gold, dark brown-gold) with 1-square MAGENTA lines along it and long thin golden claw fingers; the BLACK GLOVE and the DARK PISTOL (black, dark grey, small red and gold fittings).
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`renata-ult-1.png`、`renata-ult-2.png`（大招，两稿）

附同样 11 张图。**用 image_gen 画。**

```text
Same attached images. Draw with the image generator ONE clean pixel-art picture of the same woman in her ULTIMATE pose (image 5, at the size and place of image 6): a 1536x1536 PNG with a real transparent background (alpha only 0 or 255), every square 12 px aligned on one straight grid starting at the canvas corner, the top of her hair at y 720, her chin at y 900 (her head about 15 squares, the SAME size and look as in the first picture), her soles at y 1440 on one ground line.
ONLY TWO ARMS: the GOLDEN MECHANICAL near arm (image left) raised high above her head, the claw fingers spread; the far arm in its BLACK GLOVE hanging down at her side; NO third arm anywhere. The pistol sits in a holster at her hip.
Behind her the CHEMTECH MACHINE unfolded, its size and place as in image 6 (about 83 squares wide, its top near y 372): a bronze-gold body (bright gold, gold, dark brown-gold) with MAGENTA TUBES behind her shoulders, several LONG POINTED BLADE-WINGS (dark grey and blue-grey blades with magenta and gold markings) spreading OUTWARD AND UPWARD on both sides, a DARK RED-BROWN CAPE (3 shades) hanging behind; the whole machine ABOVE the ground line, no blade below her soles.
Her body, face, mask, hair, cape-jacket, vest, shirt, trousers and boots exactly as in the first picture.
One continuous near-black outline round her and round the machine; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no chemical wave, no glow), no background, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 3：`renata-machine-1.png`、`renata-machine-2.png`（机械单独，两稿）

**每一稿照着对应的大招稿画**（machine-1 照 ult-1，machine-2 照 ult-2）。

```text
Take your ultimate picture (renata-ult-1 for this one, renata-ult-2 for the second) and draw with the image generator the SAME picture WITHOUT THE WOMAN: only the chemtech machine behind her, on the same 1536x1536 canvas, every square 12 px on the same grid, the machine EXACTLY where it was, not moved by a single square. Where her body, head or raised arm covered the machine, complete the machine there (the bronze-gold body, the magenta tubes, the blade roots, the cape) so it is whole on its own. Real transparent background (alpha only 0 or 255), one continuous near-black outline, no stray single squares, no blur, no effects, no text.
```

## 交回前请检查

- **六张图都是 image_gen 画的**（不是脚本写的格子图）；她 1024 × 1024，大招和机械 1536 × 1536；真透明背景，**alpha 只有 0 / 255**。
- 她：
  - 大小、位置、姿势和 `2_target_body.png` 一样：头发顶 y 240，下巴约 y 420，脚底 y 960，每格 12 px，对齐网格。
  - **头约占身高四分之一**，身体仍然高挑修长。
  - 品红眼睛、银色面罩和金环、银蓝挑染、披肩金边、马甲金扣、胸针、机械臂的品红线条都清楚。
- 大招：
  - 头发顶 y 720，下巴约 y 900，脚底 y 1440；头和 A 一样大。
  - **只有两条手臂**：近侧金色机械臂高举，远侧黑手套手臂垂着；手枪在腰间枪套里。
  - 机械约 83 格宽，全部在脚底线以上。
- 机械单独：和对应的大招稿位置一格不差，被她挡住的地方补完整。
- 颜色照 A / C；没有任何特效。
- 如果模型不肯画有名字的角色：提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/renata-model/`）

- 六张图：`renata-model-1.png`、`renata-model-2.png`、`renata-ult-1.png`、`renata-ult-2.png`、`renata-machine-1.png`、`renata-machine-2.png`。
- **image_gen 的原始生成图原样放进 `outputs/renata-model/raw/`**，不要再处理成格子图。
- `generation-prompts.txt`：写明实际用的提示词。
- **最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/renata_model_done.zip`，这样我这边才知道已经交付完了。中间不要停，六张都画完再交。

## Claude 收到后（给 Claude 看）

- 读回：原稿在 8 倍下数描边台阶量出格子大小，按它自己的格子读回；和 `2_target_body.png` 并排，再按游戏大小和娜美、迦娜、芸阿娜、斯维因、德莱厄斯放在一起，给用户挑一稿（用户审核，不要自己判定）。大招和机械两稿也一起给用户挑。
- 动作帧由 Claude 按塔姆的方式从造型的部件绑定（无损平移 / 整格转动，不变形）：跑步照英雄联盟 Run；普攻 Attack1（开枪）；E Spell3（双发飞弹）；Q Spell1_Activate / Spell1_Fling_Back（机械手抓住后往身后甩）；W Spell2（给队友打气）；R Spell4（机械臂高举、机械展开，机械用单独那张整块平移）；死亡 Death。
