# 巴德（星界游神）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 巴德还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**乐器怎么拿**，人、脸、鬃毛、衣服、乐器完全一样：**A = 英雄联盟里的待机，乐器扛在近侧肩膀上**（附图 1、8、9）；**B = 同一个人，乐器提在近侧手里垂在腿边**（更紧凑）。你挑一版，之后第 1 步再按它画正面 + 侧面的高清（PPU）造型。这一版走**高清（PPU）1.5**（和加里奥一样）：**每个游戏像素约 1.5 格**，像素块清楚、**描边粗（约 2 格）**、身材**敦实、偏 Q 版**。附图 10–13 是包里已经是这个密度的英雄（加里奥高清待机，布隆、泽丽、奈德丽的 1.5 密度待机，都放大 8 倍，一格 = 一个高清像素）。你画的原图会直接按格子读回成游戏里的高清造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–9）：巴德，一个**高大、温和、四处漫游的星界守护者**，体型魁梧、肩膀宽、肚子圆。
> - **头**（附图 3 特写）：整个头和胸口被一大团**蓬松的浅绿白色鬃毛**包住（像一件毛茸茸的兜帽 + 大胡子，垂到肚子），鬃毛顶上两边各一撮**尖尖的耳朵状毛簇**；鬃毛正中是一张**小小的圆形青铜色面具脸**，上面**三个发金光的孔**（两只眼睛 + 一个嘴），这是全身最重要的地方，必须看得清（面具至少 6×6 格）；面具上方一根**短短的天线**，顶上一颗**金色小圆珠**。头（鬃毛团）约占身高（头顶到脚底，不算天线）的**三分之一**。
> - **身体和衣服**：皮肤是**灰绿色**（鼠尾草绿，亮部浅绿、暗部深灰绿），胳膊又粗又长，上面有几块**十字缝的补丁**；**一双大手**，手指是**橄榄褐色**；两条小臂上各缠着**红色 + 暗紫色的条纹护腕**（几道粗环）；近侧肩膀一块**红色护肩布**；胸前鬃毛下面垂着一大片**红色的围裙式长挂布**，上面有**橙色的卷曲花纹**，下摆尖尖的，挂布中间垂着一根**绑着皮绳的小发辫**；腰上一条**棕色皮带**、一条**深蓝灰色的腰布**，下摆有几颗**深紫色流苏**；腰侧挂着一个**金色的圆筒铃铛**；下身是**宽松的深酒红色灯笼裤**，裤腿上有暗红的旋涡纹；**腿很短，脚是两根粗短的深铁色圆柱脚**（像木桩），两腿之间垂着一个**小小的浅绿色挂饰**。
> - **乐器（很重要，附图 8 特写）**：一把**又长又弯的象牙色号角**（像一根弯弯的獠牙），上面缠着几道**棕色皮带**，下面挂着三四个**金色小铃铛**；号角一端是一个**大大的金色喇叭口**，喇叭口里嵌着一颗**发光的青绿色圆球**（上面有旋涡纹）。总长约为他身高的**三分之二**。**A**：乐器扛在**近侧肩膀**（画面左边）上——近侧的手举到肩膀，握着前面的金色喇叭口（青绿圆球朝着看画的人），象牙号角从肩膀上往后、**在他背后画面左边弯下来**，小铃铛挂在号角下面（像附图 1、8、9）；**B**：近侧的手垂下来提着金色喇叭口，**象牙号角往下、往后弯，垂在近侧腿边**，号角尖离地面一点点。乐器和手**不能挡住面具脸**。
> - **姿势**：3/4 正面朝右（面具脸、胸口朝向看画的人），两条粗短的腿分开站稳：**近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、稍暗、稍高**，两只柱子脚踏在同一条地面线上；远侧手（画面右边）自然垂着、手指微微弯。
> - **比例**：**敦实、偏 Q 版**——身体宽度约为身高的六成（他本来就魁梧），鬃毛头约占三分之一，腿短；风格完全照附图 10–13。
> - **画布用竖版 1024×1536**：**头顶（鬃毛顶，不算天线）到脚底约 720 px，也就是约 60 格**（A、B 一样大）；天线、乐器可以伸出去一点，全部在画面里，不能出画；脚底平平地落在一条地面线上（游戏在脚下画血条）。
> - **像素块**：大小一致的方块，**每块 12 像素**，横平竖直对齐成网格（这张图会被按格子读回，一格就是一个高清像素）；**外轮廓一圈 2 块宽的近黑描边**（附图 10–13 的粗描边）；内部每种材质 3–4 档平涂，不要细碎的单个杂色格。
> - 不画任何特效（米普小精灵、星光、传送门、金色时停穹顶都在第 3 步单独画）；不画地面和影子。
> - 交付：`outputs/bard-picture/bard-model-A.png`、`outputs/bard-picture/bard-model-B.png`（都是 1024×1536 竖版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，原始生成稿放 `outputs/bard-picture/raw/`，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `bard_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_bard_league_front.png` | 英雄联盟原版巴德待机，3/4 朝右 | 颜色、形状、**角度**、A 的扛法 |
| `refs/2_bard_league_frontal.png` | 同一帧，更正一点的角度 | 红色挂布、腰布、流苏、金铃铛、柱子脚 |
| `refs/3_bard_league_head.png` | 头的特写 | 鬃毛、耳朵毛簇、**青铜面具 + 三个金光孔**、天线金珠 |
| `refs/4_bard_league_back.png` | 同一帧的背后 | 号角在背后怎么弯下来、鬃毛背面 |
| `refs/5_bard_splash.png` | 官方加载画面 | 气质（温和、神秘） |
| `refs/6_bard_league_run.png` | 英雄联盟里他跑动的几个瞬间 | 第 2 步用（这一步不用） |
| `refs/7_bard_league_actions.png` | 普攻、星界束缚、神奇旅程、调和命运的瞬间 | 第 2 步用（这一步不用） |
| `refs/8_bard_league_instrument.png` | 扛在肩上的乐器特写 | 象牙号角、皮带、小金铃、金色喇叭口 + 青绿圆球 |
| `refs/9_bard_league_side.png` | 待机的侧面（朝右） | 号角从肩上往后弯的样子；第 1 步还会用 |
| `style/10_style_galio.png` | 游戏里加里奥的高清待机（8 倍放大，一格 = 一个高清像素）——同样是 1.5 左右的密度 | **只看风格**：像素粗细、粗描边、敦实比例 |
| `style/11_style_braum.png` | 布隆 1.5 密度待机（8 倍） | **只看风格**（同样魁梧的辅助，最接近巴德的体型） |
| `style/12_style_zeri.png` | 泽丽 1.5 密度待机（8 倍） | **只看风格**（像素风的样板） |
| `style/13_style_nidalee.png` | 奈德丽 1.5 密度待机（8 倍） | **只看风格** |

## 提示词 A：`bard-model-A.png`（乐器扛在近侧肩上）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look, the ANGLE and the INSTRUMENT HOLD of this picture; 2 the same from a more frontal angle: the red tabard, the sash and tassels, the golden bell at the hip, the peg feet; 3 the head close-up: the fluffy mane, the ear tufts, the small bronze MASK FACE with three glowing golden holes, the antenna with a golden bead; 4 the same from behind: how the horn curves down his back; 5 the official illustration: his mood; 6 moments of his running - not used here; 7 moments of his attack and spells - not used here; 8 a close-up of the instrument on his shoulder; 9 the idle from the side: how the horn goes back over the shoulder). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the THICK near-black outline, flat 3-4 step shading, STOCKY chunky proportions (image 11 is a big burly support, the closest body type to this character).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 720 px (about 60 squares) from the top of his mane to his soles, the antenna and the instrument may stick out further, centred, comfortable transparent margins, nothing cut off, the soles level on one ground line.
The character: Bard, the Wandering Caretaker, a big, gentle, mysterious cosmic wanderer - broad shoulders, a round belly, long heavy arms. THE HEAD: his head and chest are wrapped in ONE BIG FLUFFY PALE GREEN-WHITE MANE (like a fluffy hood and a long beard down to his belly), with a pointed EAR-LIKE TUFT on each side of the top; in the middle of the mane a SMALL ROUND BRONZE MASK FACE with THREE GLOWING GOLDEN HOLES (two eyes and a mouth) - the most important detail, clearly readable, at least 6x6 squares; a short ANTENNA on top of the mask with a small GOLDEN BEAD at its tip. The mane is about ONE THIRD of his height. THE BODY: SAGE-GREEN skin (light green highlights, dark grey-green shadows), thick long arms with a few CROSS-STITCHED PATCHES, BIG HANDS with OLIVE-BROWN fingers, RED-AND-DARK-PURPLE STRIPED BRACERS (a few thick rings) on both forearms, a RED SHOULDER CLOTH on the near shoulder; under the mane a long RED TABARD with ORANGE SWIRL PATTERNS hangs down the front to a point, a small LEATHER-BOUND BRAID hanging over it; a BROWN LEATHER BELT and a DARK BLUE-GREY WAIST CLOTH with a few DARK PURPLE TASSELS; a GOLDEN CYLINDER BELL hanging at his hip; LOOSE DARK WINE-RED TROUSERS with dark swirl patterns; SHORT LEGS ending in two THICK DARK IRON PEG FEET (like short posts); a tiny pale green charm hanging between the legs. THE INSTRUMENT (image 8): a LONG CURVED IVORY HORN like a big tusk, wrapped with a few BROWN LEATHER BANDS, three or four SMALL GOLDEN BELLS hanging under it, and at one end a BIG GOLDEN BELL-MOUTH holding a GLOWING TEAL ORB with a swirl on it; about two thirds of his height long.
Pose: League's own idle (images 1, 8, 9): standing firm on his two short legs, feet apart, the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher; the NEAR HAND (image left) is raised to his near shoulder holding the golden bell-mouth there (the teal orb toward the viewer), the ivory horn goes back over that shoulder and CURVES DOWN BEHIND HIM on the image left, its little golden bells hanging under it; the far arm hangs relaxed, fingers slightly curled. The instrument and the hands never cover the mask face. 3/4 FRONT view facing image right, mask face and chest toward the viewer.
Proportions: STOCKY and CHUNKY like images 10-13, a burly figure - the body about 0.6 as wide as it is tall, the mane about one third of the height, short legs. Keep the whole figure COMPACT.
Style: crisp chunky pixel art like images 10-13 - EVEN SQUARE PIXELS OF 12 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a TWO-SQUARE-THICK near-black outline around the silhouette, inside it every material in its own 3-4 flat shades, no stray single odd squares: the mane pale green-white, the skin sage green, the tabard red with orange swirls, the trousers dark wine red, the feet dark iron, the mask bronze with golden glowing holes, the horn ivory with brown bands, the bell-mouth and bells gold, the orb teal; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no little spirits, no stars, no portals, no golden dome), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`bard-model-B.png`（乐器提在近侧手里垂在腿边）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and the ANGLE of this picture; 2 the same from a more frontal angle: the red tabard, the sash and tassels, the golden bell at the hip, the peg feet; 3 the head close-up: the fluffy mane, the ear tufts, the small bronze MASK FACE with three glowing golden holes, the antenna with a golden bead; 4 the same from behind; 5 the official illustration: his mood; 6 moments of his running - not used here; 7 moments of his attack and spells - not used here; 8 a close-up of the instrument; 9 the idle from the side). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the THICK near-black outline, flat 3-4 step shading, STOCKY chunky proportions (image 11 is a big burly support, the closest body type to this character).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 720 px (about 60 squares) from the top of his mane to his soles, the antenna may stick out further, centred, comfortable transparent margins, nothing cut off, the soles level on one ground line.
The character: Bard, the Wandering Caretaker, a big, gentle, mysterious cosmic wanderer - broad shoulders, a round belly, long heavy arms. THE HEAD: his head and chest are wrapped in ONE BIG FLUFFY PALE GREEN-WHITE MANE (like a fluffy hood and a long beard down to his belly), with a pointed EAR-LIKE TUFT on each side of the top; in the middle of the mane a SMALL ROUND BRONZE MASK FACE with THREE GLOWING GOLDEN HOLES (two eyes and a mouth) - the most important detail, clearly readable, at least 6x6 squares; a short ANTENNA on top of the mask with a small GOLDEN BEAD at its tip. The mane is about ONE THIRD of his height. THE BODY: SAGE-GREEN skin (light green highlights, dark grey-green shadows), thick long arms with a few CROSS-STITCHED PATCHES, BIG HANDS with OLIVE-BROWN fingers, RED-AND-DARK-PURPLE STRIPED BRACERS (a few thick rings) on both forearms, a RED SHOULDER CLOTH on the near shoulder; under the mane a long RED TABARD with ORANGE SWIRL PATTERNS hangs down the front to a point, a small LEATHER-BOUND BRAID hanging over it; a BROWN LEATHER BELT and a DARK BLUE-GREY WAIST CLOTH with a few DARK PURPLE TASSELS; a GOLDEN CYLINDER BELL hanging at his hip; LOOSE DARK WINE-RED TROUSERS with dark swirl patterns; SHORT LEGS ending in two THICK DARK IRON PEG FEET (like short posts); a tiny pale green charm hanging between the legs. THE INSTRUMENT (image 8): a LONG CURVED IVORY HORN like a big tusk, wrapped with a few BROWN LEATHER BANDS, three or four SMALL GOLDEN BELLS hanging under it, and at one end a BIG GOLDEN BELL-MOUTH holding a GLOWING TEAL ORB with a swirl on it; about two thirds of his height long.
Pose: standing firm on his two short legs, feet apart, the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher; the NEAR ARM (image left) hangs down and its hand carries the instrument by the golden bell-mouth beside his near hip, the ivory horn CURVES DOWN AND BACK beside his near leg, its tip a little above the ground, the little golden bells hanging from it; the far arm hangs relaxed, fingers slightly curled. A compact silhouette. The instrument and the hands never cover the mask face. 3/4 FRONT view facing image right, mask face and chest toward the viewer.
Proportions: STOCKY and CHUNKY like images 10-13, a burly figure - the body about 0.6 as wide as it is tall, the mane about one third of the height, short legs. Keep the whole figure COMPACT.
Style: crisp chunky pixel art like images 10-13 - EVEN SQUARE PIXELS OF 12 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a TWO-SQUARE-THICK near-black outline around the silhouette, inside it every material in its own 3-4 flat shades, no stray single odd squares: the mane pale green-white, the skin sage green, the tabard red with orange swirls, the trousers dark wine red, the feet dark iron, the mask bronze with golden glowing holes, the horn ivory with brown bands, the bell-mouth and bells gold, the orb teal; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no little spirits, no stars, no portals, no golden dome), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），竖版 1024×1536，四周留边，天线、乐器都完整，不出画。
- 浅绿白色的大鬃毛团（兜帽 + 大胡子，两撮耳朵状毛簇）；正中**小小的青铜面具脸 + 三个金光孔**，清楚可见（至少 6×6 格）；天线 + 金珠。
- 灰绿皮肤、十字补丁、橄榄褐色大手、红紫条纹护腕、红色护肩布；红色长挂布 + 橙色卷纹 + 小发辫；棕皮带、深蓝灰腰布 + 紫流苏、腰侧金铃铛；深酒红灯笼裤；**两根深铁色柱子脚**。
- 乐器：象牙色弯号角 + 棕皮带 + 小金铃 + 金色喇叭口 + 发光青绿圆球；A 扛在近侧肩上、号角在背后画面左边弯下来，B 提在近侧手里垂在腿边。
- 头顶（鬃毛顶）到脚底约 720 px（约 60 格，两版一样大）；鬃毛约占三分之一；敦实、偏 Q 版（像附图 10–13）。
- 近侧腿在画面左边亮色、远侧腿在右边稍暗稍高；脚底落在同一条水平线上；没有任何特效。
- **每块 12 像素、大小一致、对齐网格**；外轮廓 2 块宽的近黑描边；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/bard-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画和 raw/ 放进 `assets/source/bard/codex_picture/`，按格子读回（regrid，按实际格子大小），和包里的英雄（加里奥 hd_idle、布隆/泽丽 lo_idle）并排、在游戏实际大小下给用户挑 A / B 和大小。
- 选定后写第 1 步 `MODEL_PROMPTS.md`：**正面（3/4，待机 + 选人卡）+ 侧面（朝右，所有动作的底子）**两个视图，同一个高度、同一套格子、同样的细节（side-view-design）；PPU 1.5，原稿 1:1 按格读回，绝不先画大再缩；描边约 1 游戏像素；大小用 hd.rs SIZES 调，不删躯干行。
- 同一张面具脸贯穿所有帧（one-face-all-frames）；跑步按 Caitlyn 的交叉步（run-legs-caitlyn-way）；乐器是刚体（只平移或 90 度转），米普、星光在第 3 步特效里画。
