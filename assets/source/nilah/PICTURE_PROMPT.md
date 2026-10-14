# 尼菈（不羁之悦）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 尼菈还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**武器怎么拿**，人、脸、头发、衣服、武器完全一样：**A = 英雄联盟里的待机，收起来的鞭刃竖直举在身边**（附图 1）；**B = 同一个人，鞭刃竖直朝下垂在近侧腿边**（更紧凑）。你挑一版，之后第 1 步再按它画正面 + 侧面的高清（PPU）造型。这一版走**高清（PPU）**，并且按 2026-10-13 定下的**统一画风（以泽丽为样板，附图 10–12 是重做后的泽丽、奈德丽、卡尔玛）**：像素块清楚、**每个游戏像素约 2.2 格**、**描边粗（约 2 格）**、身材**偏 Q 版、敦实**（不要细长）。你画的原图会直接按格子读回成游戏里的高清造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–9）：尼菈，一个**开朗、爱笑、身手灵活的近战女武者**。**深棕色的皮肤**（亮部暖棕、暗部深咖啡）。
> - **头**（附图 3 特写）：头约占身高（头顶到脚底）的**五分之一**（和附图 11 奈德丽差不多，脸要看得清）；**蓝黑色的头发**：齐刘海、两边耳前各一缕到下巴的短发，**后面一条又粗又长的低马尾一直垂到膝盖后面**（全身最有特点的轮廓，在身后、画面左边）；**紫色的眼睛**、粗眉毛、**笑着**；两只耳朵挂着**圆圆的青绿色耳坠**，鼻子上一个小鼻环，用一根细链连到耳朵。
> - **衣服**：**明黄色的单肩上衣**（一边肩膀露出来），领口一圈**青铜色的金属交叉项圈**、胸前一道紫青色的亮边；没有袖子的那条胳膊**手臂上缠着几道黄色布条**；**拿武器的那条胳膊从手到手肘缠着暗红色的护臂**、手肘上一圈黄色布；黄色上衣下摆长到大腿，**腰上一条紫青相间的腰带**、下面**一片紫色带青铜边的飘带裙片**垂在一侧；腰侧挂着一个**青铜笼子里装着深色圆球的饰物**；下身是**宽松的深紫红色灯笼裤**，裤腿上有暗红色的花纹，**膝盖和小腿外侧是青铜青绿色的弯曲护甲**；脚上一双**黑色平底软鞋**，脚踝露出皮肤。
> - **武器（要直）**：**鞭刃**——一把能伸长成长鞭的分节刀刃。待机时**收起来，成一把短刃**（附图 8 特写）：中间是**青铜青绿色的握柄**（几道环纹），握柄下端伸出**一截青色的尖刃**，握柄上端是**收拢的暗红紫色鞭刃**（几节刀片叠在一起，边缘青色），总长约为她身高的三分之一。**整把武器是一条直线**，A 竖直朝上、B 竖直朝下，不弯、不歪、不斜。
> - **姿势**：3/4 正面朝右（脸、胸口朝向看画的人），两腿分开站稳：**近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、稍暗、稍高**，两只脚踏在同一条地面线上。**A**：近侧手（画面左边）把收起来的鞭刃**竖直举在肩膀旁边**、刃尖朝上，远侧手张开放在胸前（像附图 1）；**B**：近侧手垂下握着鞭刃，**鞭刃竖直朝下贴在近侧腿边**（刃尖离地面一点点），远侧手叉在腰上。武器和手**不能挡住她的脸**，长马尾在身后。
> - **比例**（统一画风）：**敦实、偏 Q 版**——身体宽度约为身高的一半，头约占五分之一，灯笼裤蓬松、腿短一点；**不要细长的写实比例**。风格完全照附图 10–12（重做后的泽丽、奈德丽、卡尔玛）。
> - **画布用竖版 1024×1536**：**头顶到脚底约 670 px，也就是约 84 格**（A、B 一样大）；A 的刃尖可以再往上一点，全部在画面里，不能出画；脚底平平地落在一条地面线上（游戏在脚下画血条）。
> - **像素块**：大小一致的方块，**每块 8 像素**，横平竖直对齐成网格（这张图会被按格子读回，一格就是一个高清像素）；**外轮廓一圈 2 块宽的近黑描边**（附图 10–12 的粗描边）；内部每种材质 3–4 档平涂，不要细碎的单个杂色格。
> - 不画任何特效（鞭子甩出去的光、轻纱飞漾的水雾、神恩激荡的水流都在第 3 步单独画）；不画地面和影子。
> - 交付：`outputs/nilah-picture/nilah-model-A.png`、`outputs/nilah-picture/nilah-model-B.png`（都是 1024×1536 竖版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `nilah_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_nilah_league_front.png` | 英雄联盟原版尼菈待机，3/4 朝右 | 颜色、形状、**角度**、A 的拿法 |
| `refs/2_nilah_league_frontal.png` | 同一帧，更正一点的角度 | 上衣、腰带、飘带裙片、腰上的笼子球、护甲 |
| `refs/3_nilah_league_head.png` | 头的特写 | 刘海、短发、紫眼睛、青绿耳坠、鼻环链、青铜项圈 |
| `refs/4_nilah_league_back.png` | 同一帧的背后 | 长马尾怎么垂下来 |
| `refs/5_nilah_splash.png` | 官方加载画面 | 气质（开朗、爱笑、灵活） |
| `refs/6_nilah_league_run.png` | 英雄联盟里她跑动的几个瞬间 | 灯笼裤、马尾怎么飘 |
| `refs/7_nilah_league_actions.png` | 普攻、游刃万变、纵情逐流、神恩激荡的瞬间 | 鞭刃伸长的样子（这一步不画伸长的鞭子） |
| `refs/8_nilah_league_weapon.png` | 收起来的鞭刃特写（在她手里） | 握柄、下端青色尖刃、上端收拢的暗红紫刀片；暗红护臂 |
| `refs/9_nilah_league_side.png` | 待机的侧面（朝右） | 第 1 步用（这一步不用） |
| `style/10_style_zeri.png` | 游戏里重做后的泽丽高清待机（8 倍放大，一格 = 一个高清像素）——统一画风的样板 | **只看风格**：像素粗细、粗描边、敦实比例、头的大小 |
| `style/11_style_nidalee.png` | 重做后的奈德丽高清待机（8 倍） | **只看风格**（同样是深肤色、长马尾的女英雄，最接近尼菈） |
| `style/12_style_karma.png` | 重做后的卡尔玛高清待机（8 倍） | **只看风格** |

## 提示词 A：`nilah-model-A.png`（鞭刃竖直举在身边）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look, the ANGLE and the WEAPON HOLD of this picture; 2 the same from a more frontal angle: the top, the sash, the hanging skirt panel, the caged orb at her hip, the leg armour; 3 the head close-up: fringe, short side locks, purple eyes, teal earrings, nose ring chain, bronze collar; 4 the same from behind: how the long ponytail hangs; 5 the official illustration: her mood; 6 moments of her running; 7 moments of her attack and spells with the whip-blade stretched long - NOT drawn here; 8 a close-up of the folded whip-blade in her hand and her dark red arm wrap; 9 the idle from the side - not used here). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the THICK near-black outline, flat 3-4 step shading, STOCKY chunky proportions and head size (image 10 the model of this series' look; image 11 a dark-skinned woman with a long ponytail, the closest to this character).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 670 px (about 84 squares) from the top of her head to her soles, the raised blade tip may go a little higher, centred, comfortable transparent margins, nothing cut off, the soles level on one ground line.
The character: Nilah, the Joy Unbound, a cheerful, laughing, nimble melee fighter with DEEP BROWN SKIN (warm brown highlights, dark coffee shadows). THE HEAD: about ONE FIFTH of her height, the face clearly readable; BLUE-BLACK HAIR with a straight fringe, a short lock on each side down to the chin, and ONE VERY LONG THICK LOW PONYTAIL hanging behind her down to the back of her knees (her most recognisable outline, behind her on the image left); PURPLE EYES, thick brows, a happy SMILE; round TEAL EARRINGS, a small nose ring with a thin chain to the ear. THE CLOTHES: a BRIGHT YELLOW ONE-SHOULDERED TOP (one shoulder bare), a BRONZE-TEAL METAL CROSSED COLLAR at the neck and a purple-teal shining trim across the chest; the arm without a sleeve wrapped with a few YELLOW CLOTH BANDS; the weapon arm wrapped in a DARK RED ARM WRAP from the hand to the elbow with a yellow cloth band at the elbow; the yellow top hangs down to the thighs, a PURPLE-AND-TEAL SASH at the waist, a PURPLE SKIRT PANEL WITH BRONZE EDGES hanging at one side; a BRONZE CAGE HOLDING A DARK ORB hangs at her hip; LOOSE DARK PLUM HAREM TROUSERS with dark red patterns, CURVED BRONZE-TEAL ARMOUR on the outside of the knees and shins; FLAT BLACK SLIPPERS, bare ankles. THE WEAPON, A STRAIGHT LINE: her WHIP-BLADE folded into its short form (image 8): a BRONZE-TEAL GRIP with a few rings, a short TEAL POINTED BLADE out of the bottom of the grip, and on top the FOLDED DARK RED-PURPLE BLADE SEGMENTS stacked together with teal edges; about one third of her height long; perfectly STRAIGHT and VERTICAL, never bent or tilted.
Pose: League's own idle (image 1): standing firm, feet apart, the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher; the NEAR HAND (image left) holds the folded whip-blade UPRIGHT beside her shoulder, the blade tip pointing straight UP; the far hand open in front of her chest. The weapon and the hands never cover her face; the long ponytail hangs behind her. 3/4 FRONT view facing image right, face and chest toward the viewer.
Proportions: STOCKY and CHUNKY like images 10-12, NOT a tall slender realistic woman - the body about half as wide as it is tall, the head about one fifth of the height, puffy harem trousers, slightly short legs. Keep the whole figure COMPACT.
Style: crisp chunky pixel art like images 10-12 - EVEN SQUARE PIXELS OF 8 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a TWO-SQUARE-THICK near-black outline around the silhouette, inside it every material in its own 3-4 flat shades, no stray single odd squares: the skin deep brown, the hair blue-black with a dark blue-violet highlight, the top bright yellow (pale yellow, golden yellow, orange-ochre), the trousers dark plum, the armour and grip bronze-teal, the arm wrap dark red, the blade segments dark red-purple with teal edges, the eyes purple; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no whip trail, no mist, no water), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`nilah-model-B.png`（鞭刃竖直朝下垂在腿边）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and the ANGLE of this picture; 2 the same from a more frontal angle: the top, the sash, the hanging skirt panel, the caged orb at her hip, the leg armour; 3 the head close-up: fringe, short side locks, purple eyes, teal earrings, nose ring chain, bronze collar; 4 the same from behind: how the long ponytail hangs; 5 the official illustration: her mood; 6 moments of her running; 7 moments of her attack and spells with the whip-blade stretched long - NOT drawn here; 8 a close-up of the folded whip-blade in her hand and her dark red arm wrap; 9 the idle from the side - not used here). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the THICK near-black outline, flat 3-4 step shading, STOCKY chunky proportions and head size (image 10 the model of this series' look; image 11 a dark-skinned woman with a long ponytail, the closest to this character).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 670 px (about 84 squares) from the top of her head to her soles, centred, comfortable transparent margins, nothing cut off, the soles level on one ground line.
The character: Nilah, the Joy Unbound, a cheerful, laughing, nimble melee fighter with DEEP BROWN SKIN (warm brown highlights, dark coffee shadows). THE HEAD: about ONE FIFTH of her height, the face clearly readable; BLUE-BLACK HAIR with a straight fringe, a short lock on each side down to the chin, and ONE VERY LONG THICK LOW PONYTAIL hanging behind her down to the back of her knees (her most recognisable outline, behind her on the image left); PURPLE EYES, thick brows, a happy SMILE; round TEAL EARRINGS, a small nose ring with a thin chain to the ear. THE CLOTHES: a BRIGHT YELLOW ONE-SHOULDERED TOP (one shoulder bare), a BRONZE-TEAL METAL CROSSED COLLAR at the neck and a purple-teal shining trim across the chest; the arm without a sleeve wrapped with a few YELLOW CLOTH BANDS; the weapon arm wrapped in a DARK RED ARM WRAP from the hand to the elbow with a yellow cloth band at the elbow; the yellow top hangs down to the thighs, a PURPLE-AND-TEAL SASH at the waist, a PURPLE SKIRT PANEL WITH BRONZE EDGES hanging at one side; a BRONZE CAGE HOLDING A DARK ORB hangs at her hip; LOOSE DARK PLUM HAREM TROUSERS with dark red patterns, CURVED BRONZE-TEAL ARMOUR on the outside of the knees and shins; FLAT BLACK SLIPPERS, bare ankles. THE WEAPON, A STRAIGHT LINE: her WHIP-BLADE folded into its short form (image 8): a BRONZE-TEAL GRIP with a few rings, a short TEAL POINTED BLADE out of the bottom of the grip, and on top the FOLDED DARK RED-PURPLE BLADE SEGMENTS stacked together with teal edges; about one third of her height long; perfectly STRAIGHT and VERTICAL, never bent or tilted.
Pose: standing firm, feet apart, the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher; the NEAR ARM (image left) hangs down and its hand holds the folded whip-blade pointing STRAIGHT DOWN beside the near leg, the blade tip a little above the ground; the far hand rests on her hip. A compact silhouette. The weapon and the hands never cover her face; the long ponytail hangs behind her. 3/4 FRONT view facing image right, face and chest toward the viewer.
Proportions: STOCKY and CHUNKY like images 10-12, NOT a tall slender realistic woman - the body about half as wide as it is tall, the head about one fifth of the height, puffy harem trousers, slightly short legs. Keep the whole figure COMPACT.
Style: crisp chunky pixel art like images 10-12 - EVEN SQUARE PIXELS OF 8 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a TWO-SQUARE-THICK near-black outline around the silhouette, inside it every material in its own 3-4 flat shades, no stray single odd squares: the skin deep brown, the hair blue-black with a dark blue-violet highlight, the top bright yellow (pale yellow, golden yellow, orange-ochre), the trousers dark plum, the armour and grip bronze-teal, the arm wrap dark red, the blade segments dark red-purple with teal edges, the eyes purple; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no whip trail, no mist, no water), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），竖版 1024×1536，四周留边，马尾、武器都完整，不出画。
- 深棕皮肤；蓝黑头发：齐刘海、两侧短发、**一条垂到膝盖后的长马尾**；紫眼睛、笑脸、青绿耳坠、鼻环链。
- 明黄单肩上衣 + 青铜交叉项圈；一条胳膊黄布条、拿武器的胳膊暗红护臂；紫青腰带、紫色飘带裙片、腰侧青铜笼子球；深紫红灯笼裤、青铜护膝护腿、黑色平底鞋。
- 收起来的鞭刃：青铜握柄、下端青色尖刃、上端暗红紫刀片，**一条直线**：A 竖直朝上举在肩旁，B 竖直朝下贴在近侧腿边。
- 头顶到脚底约 670 px（约 84 格，两版一样大）；头约占五分之一；敦实、偏 Q 版（像附图 10–12），不是细长的写实比例。
- 近侧腿在画面左边亮色、远侧腿在右边稍暗稍高；脚底落在同一条水平线上；没有任何特效。
- **每块 8 像素、大小一致、对齐网格**；外轮廓 2 块宽的近黑描边；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/nilah-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画（和 raw/）放进 `assets/source/nilah/codex_picture/`，按格子读回（regrid），和包里的英雄（league/*#sheet.png 的 hd_idle）并排给用户挑 A / B 和大小。
- 选定后写第 1 步 `MODEL_PROMPTS.md`：**正面（3/4，待机 + 选人卡）+ 侧面（朝右，所有动作的底子）**两个视图，同一个高度、同一套格子、同样的细节（side-view-design）；高清 PPU，原稿 1:1 按格读回，绝不先画大再缩。统一画风：PPU 约 2.2（头顶到脚底约 84 格 ≈ 38 游戏行），描边约 1 游戏像素，敦实比例（ppu_restyle crisp）；大小用 hd.rs SIZES 调，不删躯干行。
- 同一张脸贯穿所有帧（one-face-all-frames）；跑步按 Caitlyn 的交叉步、ADC 直腿（run-legs-caitlyn-way）；鞭刃收起时是刚体直线，伸长的鞭子在第 3 步特效里画。
