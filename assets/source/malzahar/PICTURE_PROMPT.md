# 玛尔扎哈（虚空先知）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 玛尔扎哈还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**下半身怎么悬浮**，人、脸、兜帽、衣服、手完全一样：**A = 长袍盖住双腿**，袍子下摆悬在半空、轻轻飘着（用户选的）；**B = 英雄联盟原版的悬浮**，袍子下面露出蓬松的蓝裤子和尖头靴，**脚尖朝下垂着**，双脚不着地（附图 1、9）。他**从来不走路，是飘着滑行的**。你挑一版，之后第 1 步再按它画正面 + 侧面的高清（PPU）造型。这一版走**高清（PPU）1.5**（和加里奥一样）：**每个游戏像素约 1.5 格**，像素块清楚、**描边粗（约 2 格）**、身材**偏 Q 版**。附图 10–13 是包里已经是这个密度的英雄（加里奥高清待机，布隆、泽丽、奈德丽的 1.5 密度待机，都放大 8 倍，一格 = 一个高清像素）。你画的原图会直接按格子读回成游戏里的高清造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–9）：玛尔扎哈，一个**清瘦、神秘的虚空先知**，悬浮在半空，双臂张开、手掌微微向上托着（像在召唤虚空）。
> - **头**（附图 3 特写）：一顶**高高的尖顶洋红色兜帽**，帽尖往后微弯；兜帽正面额头上有**四颗发光的浅蓝白色菱形印记**（排成一个菱形：上一颗、中间两颗、下一颗），这是全身最醒目的标志；兜帽下的脸藏在阴影里，**下半张脸蒙着洋红色面巾**，只露出**两只发白光的眼睛**（必须看得清，至少各 2×1 格）。兜帽连着一条**又大又厚的洋红色围巾**，在脖子和肩膀上绕成一大圈褶皱。头（兜帽 + 围巾领）约占身高的**三分之一**。
> - **身体和衣服**：一件**敞开的宝蓝色长袍**（亮部偏青蓝、暗部深靛蓝），袍子前襟敞开露出**裸露的胸口和腹肌**（灰褐色皮肤）；袍子里面一件**洋红色内衫**，腰上一条**深色布腰带**；肩上一对**淡紫灰色金属护肩**，小臂上一对**喇叭口状的淡紫灰色金属护腕**（又大又厚）；**一双大大的深藏青色手套手**，手指张开；腰带上横插着一把**弯弯的匕首**（刀鞘灰蓝色、上面有**金色卷曲花纹**，**金色刀柄护手**，刀身朝后、在画面左边伸出去）；背后垂下一条**洋红色的长布尾**（在画面右边飘着）。
> - **A 的下半身**：宝蓝色长袍一直垂到脚下，**完全盖住双腿**，下摆宽一点、边缘几道深靛蓝的褶，下摆底边**悬空**、微微向后飘（不碰地）。
> - **B 的下半身**（附图 1、9）：袍子到膝盖，下面是**蓬松的宝蓝色灯笼裤**，裤脚收进**深色护胫**，再下面是**尖头的深洋红色靴子**，**双脚脚尖朝下垂着**、一前一后微微错开，不踩地。
> - **姿势**：3/4 正面朝右（脸、胸口朝向看画的人），悬浮着：**近侧手臂（画面左边）**向外下方张开、手掌朝上；**远侧手臂（画面右边）**向外抬到肩高、手掌朝上托着，像在召唤虚空；手不能挡住脸和兜帽上的菱形印记。
> - **比例**：**偏 Q 版**——兜帽头约占三分之一，身体宽度（不算张开的手）约为身高的一半；风格完全照附图 10–13。
> - **画布用竖版 1024×1536**：**兜帽尖到最低点（A 是袍子下摆，B 是靴尖）约 624 px，也就是约 52 格**（A、B 一样大）；张开的手、匕首可以伸出去一点，全部在画面里，不能出画；人在画面中间偏下，最低点下面留**至少 5 格空白**（游戏里他会离地悬浮）。
> - **像素块**：大小一致的方块，**每块 12 像素**，横平竖直对齐成网格（这张图会被按格子读回，一格就是一个高清像素）；**外轮廓一圈 2 块宽的近黑描边**（附图 10–13 的粗描边）；内部每种材质 3–4 档平涂，不要细碎的单个杂色格。
> - 不画任何特效（虚空裂隙、虚空虫、紫色能量、光球都在第 3 步单独画）；不画地面和影子。
> - 交付：`outputs/malzahar-picture/malzahar-model-A.png`、`outputs/malzahar-picture/malzahar-model-B.png`（都是 1024×1536 竖版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词；**所有原始生成稿（没有经过任何缩放、裁切、调色、重画的那一版）原样放 `outputs/malzahar-picture/raw/`**，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `malzahar_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_malzahar_league_front.png` | 英雄联盟原版玛尔扎哈待机，3/4 朝右 | 颜色、形状、**角度**、张开双手的姿势、B 的下半身 |
| `refs/2_malzahar_league_frontal.png` | 同一帧，更正一点的角度 | 敞开的长袍、腹肌、腰带、匕首、布尾 |
| `refs/3_malzahar_league_head.png` | 头和上身的特写 | **尖顶兜帽 + 四颗发光菱形**、面巾、**发光的眼睛**、大围巾、护腕、匕首花纹 |
| `refs/4_malzahar_league_back.png` | 同一帧的背后 | 兜帽、围巾和布尾的背面 |
| `refs/5_malzahar_splash.png` | 官方加载画面 | 气质（阴森、神秘、虚空紫） |
| `refs/6_malzahar_league_run.png` | 英雄联盟里他移动的几个瞬间（滑行） | 第 2 步用（这一步不用） |
| `refs/7_malzahar_league_actions.png` | 普攻、虚空召唤、煞星幻象、冥府之握的瞬间 | 第 2 步用（这一步不用） |
| `refs/8_malzahar_league_hands.png` | 上身和双手特写 | 护肩、喇叭口护腕、深藏青大手套、匕首 |
| `refs/9_malzahar_league_side.png` | 待机的侧面（朝右） | 悬浮时脚尖朝下的样子、兜帽侧面；第 1 步还会用 |
| `style/10_style_galio.png` | 游戏里加里奥的高清待机（8 倍放大，一格 = 一个高清像素）——同样是 1.5 左右的密度 | **只看风格**：像素粗细、粗描边、Q 版比例 |
| `style/11_style_braum.png` | 布隆 1.5 密度待机（8 倍） | **只看风格** |
| `style/12_style_zeri.png` | 泽丽 1.5 密度待机（8 倍） | **只看风格**（像素风的样板，同样清瘦的体型） |
| `style/13_style_nidalee.png` | 奈德丽 1.5 密度待机（8 倍） | **只看风格** |

## 提示词 A：`malzahar-model-A.png`（长袍盖住双腿）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look, the ANGLE and the ARM POSE of this picture; 2 the same from a more frontal angle: the open robe, the bare chest, the belt, the dagger, the cloth tail; 3 the head and chest close-up: the tall pointed HOOD with FOUR GLOWING DIAMOND MARKS, the face cloth, the GLOWING EYES, the big scarf, the bracers, the dagger's pattern; 4 the same from behind; 5 the official illustration: his mood; 6 moments of his gliding - not used here; 7 moments of his attack and spells - not used here; 8 a close-up of the upper body and hands; 9 the idle from the side: how he floats). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the THICK near-black outline, flat 3-4 step shading, CHUNKY chibi proportions.
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 624 px (about 52 squares) from the tip of his hood to the lowest point of his robe, the open hands and the dagger may stick out sideways, centred a little low, at least 5 empty squares under his lowest point (he floats), comfortable transparent margins, nothing cut off.
The character: Malzahar, the Prophet of the Void, a lean, eerie void prophet who FLOATS in the air and never walks. THE HEAD: a TALL POINTED MAGENTA HOOD, its tip bending slightly back; on the front of the hood above the brow FOUR GLOWING PALE BLUE-WHITE DIAMOND MARKS arranged as a diamond (one on top, two in the middle, one below) - his most recognisable detail, clearly readable; the face hidden in shadow under the hood, the lower face covered by a MAGENTA FACE CLOTH, only TWO GLOWING WHITE EYES showing (clearly readable, at least 2x1 squares each); the hood joins a BIG THICK MAGENTA SCARF wound in heavy folds round his neck and shoulders. Hood and scarf collar about ONE THIRD of his height. THE BODY: an OPEN ROYAL-BLUE ROBE (cyan-blue highlights, deep indigo shadows) open at the front over a BARE CHEST WITH ABS (greyish tan skin); a MAGENTA INNER TUNIC, a DARK CLOTH BELT; LILAC-GREY METAL PAULDRONS on the shoulders and BIG FLARED LILAC-GREY METAL BRACERS on the forearms; BIG DARK NAVY GLOVED HANDS with spread fingers; a CURVED DAGGER thrust sideways through the belt (blue-grey sheath with GOLDEN SCROLL PATTERNS, a GOLDEN HILT GUARD, the blade pointing back toward the image left); a LONG MAGENTA CLOTH TAIL hanging down his back, fluttering on the image right. THE LOWER BODY (this version): the royal-blue robe falls all the way down and COMPLETELY COVERS HIS LEGS, the skirt flaring a little at the bottom with a few deep indigo folds, the hem FLOATING in the air and trailing slightly back - no legs, no feet visible, nothing touching the ground.
Pose: floating, 3/4 FRONT view facing image right, face and chest toward the viewer; the NEAR ARM (image left) spread out and down with the palm turned up; the FAR ARM (image right) raised out to shoulder height with the palm up, as if conjuring the void; the hands never cover the face or the diamond marks.
Proportions: CHUNKY CHIBI like images 10-13 - the hood head about one third of the height, the body (without the spread arms) about half as wide as it is tall. Keep the whole figure COMPACT.
Style: crisp chunky pixel art like images 10-13 - EVEN SQUARE PIXELS OF 12 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a TWO-SQUARE-THICK near-black outline around the silhouette, inside it every material in its own 3-4 flat shades, no stray single odd squares: the hood and scarf magenta, the diamond marks and the eyes glowing pale blue-white, the robe royal blue, the skin greyish tan, the pauldrons and bracers lilac grey, the gloves dark navy, the dagger sheath blue-grey with gold; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no void rifts, no void creatures, no purple energy, no orbs), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`malzahar-model-B.png`（英雄联盟原版：露出双腿，脚尖朝下悬着）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look, the ANGLE, the ARM POSE and the HANGING LEGS of this picture; 2 the same from a more frontal angle: the open robe, the bare chest, the belt, the dagger, the cloth tail; 3 the head and chest close-up: the tall pointed HOOD with FOUR GLOWING DIAMOND MARKS, the face cloth, the GLOWING EYES, the big scarf, the bracers, the dagger's pattern; 4 the same from behind; 5 the official illustration: his mood; 6 moments of his gliding - not used here; 7 moments of his attack and spells - not used here; 8 a close-up of the upper body and hands; 9 the idle from the side: how he floats with his toes pointing down). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the THICK near-black outline, flat 3-4 step shading, CHUNKY chibi proportions.
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 624 px (about 52 squares) from the tip of his hood to the tips of his boots, the open hands and the dagger may stick out sideways, centred a little low, at least 5 empty squares under his lowest point (he floats), comfortable transparent margins, nothing cut off.
The character: Malzahar, the Prophet of the Void, a lean, eerie void prophet who FLOATS in the air and never walks. THE HEAD: a TALL POINTED MAGENTA HOOD, its tip bending slightly back; on the front of the hood above the brow FOUR GLOWING PALE BLUE-WHITE DIAMOND MARKS arranged as a diamond (one on top, two in the middle, one below) - his most recognisable detail, clearly readable; the face hidden in shadow under the hood, the lower face covered by a MAGENTA FACE CLOTH, only TWO GLOWING WHITE EYES showing (clearly readable, at least 2x1 squares each); the hood joins a BIG THICK MAGENTA SCARF wound in heavy folds round his neck and shoulders. Hood and scarf collar about ONE THIRD of his height. THE BODY: an OPEN ROYAL-BLUE ROBE (cyan-blue highlights, deep indigo shadows) open at the front over a BARE CHEST WITH ABS (greyish tan skin); a MAGENTA INNER TUNIC, a DARK CLOTH BELT; LILAC-GREY METAL PAULDRONS on the shoulders and BIG FLARED LILAC-GREY METAL BRACERS on the forearms; BIG DARK NAVY GLOVED HANDS with spread fingers; a CURVED DAGGER thrust sideways through the belt (blue-grey sheath with GOLDEN SCROLL PATTERNS, a GOLDEN HILT GUARD, the blade pointing back toward the image left); a LONG MAGENTA CLOTH TAIL hanging down his back, fluttering on the image right. THE LOWER BODY (this version, images 1 and 9): the robe reaches the knees; under it PUFFY ROYAL-BLUE TROUSERS gathered into DARK GREY SHIN GUARDS, then POINTED DARK MAGENTA BOOTS; both feet HANG WITH THE TOES POINTING DOWN, one a little in front of the other, the near leg on the image left in full tone, the far leg on the image right a shade darker - nothing touching the ground.
Pose: floating, 3/4 FRONT view facing image right, face and chest toward the viewer; the NEAR ARM (image left) spread out and down with the palm turned up; the FAR ARM (image right) raised out to shoulder height with the palm up, as if conjuring the void; the hands never cover the face or the diamond marks.
Proportions: CHUNKY CHIBI like images 10-13 - the hood head about one third of the height, the body (without the spread arms) about half as wide as it is tall, short legs. Keep the whole figure COMPACT.
Style: crisp chunky pixel art like images 10-13 - EVEN SQUARE PIXELS OF 12 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a TWO-SQUARE-THICK near-black outline around the silhouette, inside it every material in its own 3-4 flat shades, no stray single odd squares: the hood and scarf magenta, the diamond marks and the eyes glowing pale blue-white, the robe and trousers royal blue, the skin greyish tan, the pauldrons and bracers lilac grey, the gloves dark navy, the shin guards dark grey, the boots dark magenta, the dagger sheath blue-grey with gold; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no void rifts, no void creatures, no purple energy, no orbs), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），竖版 1024×1536，四周留边，手、匕首都完整，不出画；最低点下面至少 5 格空白。
- **高高的尖顶洋红兜帽 + 额头四颗发光的浅蓝白菱形**，清楚可见；面巾蒙住下半张脸，**两只发白光的眼睛**看得清；洋红色大围巾绕在脖子肩膀上。
- 敞开的宝蓝长袍、裸露的胸口腹肌、洋红内衫、深色腰带；淡紫灰护肩 + 喇叭口护腕；深藏青大手套；腰上横插的弯匕首（灰蓝刀鞘 + 金色花纹 + 金色护手）；背后洋红长布尾。
- A：长袍盖住双腿、下摆悬空；B：袍子下面露出蓬松蓝裤子 + 深灰护胫 + 尖头深洋红靴子，**脚尖朝下垂着**。两版都不碰地。
- 兜帽尖到最低点约 624 px（约 52 格，两版一样大）；兜帽头约占三分之一；偏 Q 版（像附图 10–13）。
- 近侧手臂（画面左边）向外下方张开、远侧手臂抬到肩高，手掌朝上；手不挡脸；没有任何特效。
- **每块 12 像素、大小一致、对齐网格**；外轮廓 2 块宽的近黑描边；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- **所有原始生成稿原样放 `raw/`**（我这边会直接从原稿按格子读回，原稿比处理后的版本更重要）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/malzahar-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画和 raw/ 放进 `assets/source/malzahar/codex_picture/`。**先看 raw/ 原稿**，用 regrid.py 按原稿自己的格子读回，和 Codex 处理后的版本并排；和包里的英雄（加里奥 hd_idle、布隆/泽丽 lo_idle）一起、在游戏实际大小下给用户挑 A / B 和大小。
- 选定后写第 1 步 `MODEL_PROMPTS.md`：**正面（3/4，待机 + 选人卡）+ 侧面（朝右，所有动作的底子）**两个视图，同一个高度、同一套格子、同样的细节（side-view-design）；PPU 1.5，原稿 1:1 按格读回，绝不先画大再缩；描边约 1 游戏像素；大小用 hd.rs SIZES 调，不删躯干行。
- 同一张脸（兜帽 + 菱形 + 发光眼）贯穿所有帧（one-face-all-frames）；他悬浮滑行，**没有跑步腿**：移动 = 待机整体前倾 + 上下浮动 + 袍摆/布尾飘动；匕首是刚体；虚空裂隙、虫子、能量在第 3 步特效里画。
