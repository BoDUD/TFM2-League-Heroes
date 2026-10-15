# 斯莫德（炽炎雏龙）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 斯莫德还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版是**同一条小龙、同样大小**，只差**姿势**：**A = 英雄联盟里的待机，坐在后腿上、上身立起来**（附图 1、2、9）；**B = 四条腿站着**（英雄联盟里他跑动的站姿，附图 8）。你挑一版，之后第 1 步再按它画正面 + 侧面的高清（PPU）造型。这一版走**高清（PPU）1.5**（和加里奥一样）：**每个游戏像素约 1.5 格**，像素块清楚、**描边粗（约 2 格）**、身材**圆滚、偏 Q 版**。附图 10–13 是包里已经是这个密度的英雄（加里奥高清待机，布隆、泽丽、奈德丽的 1.5 密度待机，都放大 8 倍，一格 = 一个高清像素）。你画的原图会直接按格子读回成游戏里的高清造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–9）：斯莫德，一条**小小的、活泼可爱的幼龙**，头大身子小。
> - **头**（附图 3 特写）：**大脑袋**（约占身高的四成），**橙黄 / 杏色的鳞片脸**，下巴和喉咙浅奶油色；**一双大大的青绿色眼睛**（白眼白、深色瞳孔、亮点）——全身最重要的地方，必须看得清（每只眼至少 3×3 格）；**咧嘴笑**，露出一排**小白牙**；头顶到后脑是一片**深红色的鳞冠**（中间一道紫色），往后垂；**头两侧一对大大的扇形耳鳍**（外面深红 / 深蓝紫，里面浅杏色），耳鳍边缘和脸颊两边一排**青绿色的叶片状鳞刺**；头顶两只**很短的青绿色小角**，角尖上各冒着一小撮**橙黄色火苗**（附图 5 加载画面里的那种头顶小火焰，小小的、不能大）。
> - **身体**：胸口和肚子**浅奶油色、一道道横鳞**；背、肩是杏橙色；**两只翅膀收起来披在背上像一件斗篷**：外面**深海军蓝 / 深紫色**、上面有一排排**青绿色的鳞片**（肩膀上几片青绿大鳞像护肩），翅膀往下渐变成**深红 → 粉红**，下摆尖尖的几片；**四条腿短短的**，前腿**深酒红色**、前面有**一片片深蓝紫色的鳞甲**，后腿圆圆的深红色，**脚上小小的深蓝色爪子**；**一条长尾巴**：上面红色、下面杏色，尾巴尖一片**深蓝色的尾鳍**。
> - **尾巴不能拖在地上**：英雄联盟里他的尾巴平放在地上，这里改成**从身后往上卷起来**（S 形或一个大弧，尾巴尖在他背后半空，离地面至少 4 格），这样游戏里走路时尾巴不贴地。尾巴也比原版**短一些**（大约等于他的身高），让整个轮廓紧凑。
> - **A 的姿势**（附图 1、2、9）：**坐在后腿上，上身立起来**，两只前爪并排撑在身前地上，抬头笑着看前方；翅膀斗篷披在身后，下摆落在他身后；尾巴从身后卷起来。**近侧（画面左边）的前腿颜色亮，远侧（画面右边）的前腿稍暗、稍高**。
> - **B 的姿势**（附图 8 = 他跑动时的站姿）：**四条腿站着**，抬着头、胸口挺起，前腿直立、后腿微微弯，像一只精神的小狗；翅膀斗篷披在背上；尾巴从屁股后面往上卷起来。近侧两条腿亮、远侧两条腿稍暗、稍高。
> - 两版都是 **3/4 正面朝右**（脸、胸口朝着看画的人，鼻子朝画面右边），四只脚（A 是两只前爪 + 后腿）都踏在**同一条地面线**上。
> - **比例**：**圆滚、偏 Q 版**——大头、短腿、胖胖的身子；风格完全照附图 10–13。
> - **画布用横版 1536×1024**（尾巴需要宽度）：**A 从头顶（不算小火苗）到脚底约 612 px，也就是约 51 格**；**B 用同一个比例**（同一条龙，所以站着时头顶低一点、身子长一点，**眼睛和头一样大**）；小火苗、尾巴可以伸出去一点，全部在画面里，不能出画；脚底平平地落在一条地面线上（游戏在脚下画血条），地面线在离画布底边约 120 px 的地方。
> - **像素块**：大小一致的方块，**每块 12 像素**，横平竖直对齐成网格（这张图会被按格子读回，一格就是一个高清像素）；**外轮廓一圈 2 块宽的近黑描边**（附图 10–13 的粗描边）；内部每种材质 3–4 档平涂，不要细碎的单个杂色格。
> - 不画任何特效（喷火、火球、喷嚏、妈妈的火焰都在第 3 步单独画；只有头顶两小撮火苗算他的身体）；不画地面和影子。
> - 交付：`outputs/smolder-picture/smolder-model-A.png`、`outputs/smolder-picture/smolder-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，原始生成稿**原样**放 `outputs/smolder-picture/raw/`（不要再缩小或重新描），**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `smolder_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_smolder_league_front.png` | 英雄联盟原版斯莫德待机（坐着），3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_smolder_league_frontal.png` | 同一帧，更正一点的角度 | 肚子横鳞、前腿鳞甲、爪子、翅膀斗篷 |
| `refs/3_smolder_league_head.png` | 头的特写 | **大眼睛**、笑脸小白牙、深红鳞冠、耳鳍、青绿鳞刺、小角 |
| `refs/4_smolder_league_back.png` | 同一帧的背后 | 翅膀斗篷从背后看的样子 |
| `refs/5_smolder_splash.png` | 官方加载画面 | 气质（活泼、得意）、**头顶小火苗** |
| `refs/6_smolder_league_run.png` | 英雄联盟里他跑动的几个瞬间（四条腿） | 第 2 步用（这一步只看 B 的站法） |
| `refs/7_smolder_league_actions.png` | 普攻、喷嚏、起飞、妈妈来了的瞬间 | 第 2 步用（这一步不用） |
| `refs/8_smolder_league_stand.png` | 四条腿站着，3/4 朝右 | **B 的姿势** |
| `refs/9_smolder_league_side.png` | 待机的侧面（朝右） | 翅膀斗篷、耳鳍的侧面；第 1 步还会用 |
| `style/10_style_galio.png` | 游戏里加里奥的高清待机（8 倍放大，一格 = 一个高清像素）——同样是 1.5 左右的密度 | **只看风格**：像素粗细、粗描边、敦实比例 |
| `style/11_style_braum.png` | 布隆 1.5 密度待机（8 倍） | **只看风格** |
| `style/12_style_zeri.png` | 泽丽 1.5 密度待机（8 倍） | **只看风格**（像素风的样板，大眼睛的画法） |
| `style/13_style_nidalee.png` | 奈德丽 1.5 密度待机（8 倍） | **只看风格** |

## 提示词 A：`smolder-model-A.png`（坐着，上身立起来）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure sitting, in 3/4 view facing right - the look, the ANGLE and the POSE of this picture; 2 the same from a more frontal angle: the belly scales, the armoured forelegs, the claws, the folded wings; 3 the head close-up: the BIG TEAL EYES, the toothy grin, the crimson crest, the big ear fins, the teal leaf-like spikes, the small horns; 4 the same from behind: the folded wings like a cape; 5 the official illustration: his mood and the LITTLE FLAMES on top of his head; 6 moments of his running on four legs - not used here; 7 moments of his attack and spells - not used here; 8 him standing on four legs - not used here; 9 the idle from the side). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the THICK near-black outline, flat 3-4 step shading, chunky proportions (image 12 shows how big readable eyes are drawn in this style).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 612 px (about 51 squares) from the top of his head (not counting the little flames) to his soles, centred, comfortable transparent margins, nothing cut off, the soles level on one ground line about 120 px above the bottom edge.
The character: Smolder, the Fiery Fledgling, a SMALL, CUTE, CHEERFUL BABY DRAGON - a big head on a small round body. THE HEAD (about 40 % of his height): an orange-apricot scaly face with a pale cream chin and throat; TWO BIG TEAL EYES (white around them, dark pupils, a bright highlight) - the most important detail, clearly readable, each at least 3x3 squares; a wide happy GRIN showing a row of SMALL WHITE TEETH; a DARK CRIMSON SCALY CREST over the top and back of the head (a purple stripe down its middle); a pair of BIG FAN-SHAPED EAR FINS on the sides of the head (crimson / dark navy outside, pale apricot inside), a row of TEAL LEAF-LIKE SPIKES along the fins and the cheeks; two VERY SHORT TEAL HORNS on top of the head, each with a SMALL ORANGE-YELLOW FLAME TUFT on its tip (image 5) - small, never big. THE BODY: a pale cream chest and belly with horizontal belly scales; apricot-orange back and shoulders; his TWO WINGS FOLDED OVER HIS BACK LIKE A CAPE - dark navy / dark purple outside with rows of TEAL SCALES (a few big teal scales on the shoulders like pauldrons), fading down to CRIMSON and then PINK at the pointed lower edge; FOUR SHORT LEGS - the forelegs DARK WINE RED with a row of DARK NAVY-PURPLE SCALE PLATES down their front, round dark red hind legs, SMALL DARK NAVY CLAWS; a LONG TAIL, red on top and apricot underneath, with a DARK NAVY FIN at its tip.
THE TAIL MUST NOT LIE ON THE GROUND: unlike image 1, it CURLS UP behind him (an S-curve or a big arc), its tip in the air behind his back, at least 4 squares above the ground; make the tail a bit shorter than in the game, about as long as he is tall, so the silhouette stays compact.
Pose: League's own idle (images 1, 2, 9): SITTING UP ON HIS HAUNCHES, the upper body upright, both front paws planted side by side on the ground in front of him, head raised, smiling ahead; the wing cape hangs behind him; the tail curls up behind. The near foreleg (image left) in full tone, the far foreleg (image right) a shade darker and a little higher. 3/4 FRONT view facing image right, face and chest toward the viewer, snout pointing to the image right. All feet on one ground line.
Proportions: ROUND and CHUNKY like images 10-13, chibi - a big head, short legs, a plump body. Keep the whole figure COMPACT.
Style: crisp chunky pixel art like images 10-13 - EVEN SQUARE PIXELS OF 12 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a TWO-SQUARE-THICK near-black outline around the silhouette, inside it every material in its own 3-4 flat shades, no stray single odd squares: the face and back apricot-orange, the chest and belly pale cream, the crest and the legs dark crimson / wine red, the wings dark navy-purple fading to crimson and pink, the spikes, horns and shoulder scales teal, the claws and the tail fin dark navy, the eyes teal with white; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no fire breath, no fireballs, no sneeze, no big dragon), only the two small flame tufts on the horns; no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`smolder-model-B.png`（四条腿站着）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure sitting, in 3/4 view facing right - the look and the ANGLE of this picture; 2 the same from a more frontal angle: the belly scales, the armoured forelegs, the claws, the folded wings; 3 the head close-up: the BIG TEAL EYES, the toothy grin, the crimson crest, the big ear fins, the teal leaf-like spikes, the small horns; 4 the same from behind: the folded wings like a cape; 5 the official illustration: his mood and the LITTLE FLAMES on top of his head; 6 moments of his running on four legs; 7 moments of his attack and spells - not used here; 8 him STANDING ON FOUR LEGS in 3/4 view facing right - the POSE of this picture; 9 the idle from the side). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the THICK near-black outline, flat 3-4 step shading, chunky proportions (image 12 shows how big readable eyes are drawn in this style).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), at the SAME SCALE as a version of him sitting up that measures about 612 px (about 51 squares) from head to soles - standing on four legs his head is a little lower and his body a little longer, but the head and the eyes are just as big; centred, comfortable transparent margins, nothing cut off, the soles level on one ground line about 120 px above the bottom edge.
The character: Smolder, the Fiery Fledgling, a SMALL, CUTE, CHEERFUL BABY DRAGON - a big head on a small round body. THE HEAD (big, like a puppy's): an orange-apricot scaly face with a pale cream chin and throat; TWO BIG TEAL EYES (white around them, dark pupils, a bright highlight) - the most important detail, clearly readable, each at least 3x3 squares; a wide happy GRIN showing a row of SMALL WHITE TEETH; a DARK CRIMSON SCALY CREST over the top and back of the head (a purple stripe down its middle); a pair of BIG FAN-SHAPED EAR FINS on the sides of the head (crimson / dark navy outside, pale apricot inside), a row of TEAL LEAF-LIKE SPIKES along the fins and the cheeks; two VERY SHORT TEAL HORNS on top of the head, each with a SMALL ORANGE-YELLOW FLAME TUFT on its tip (image 5) - small, never big. THE BODY: a pale cream chest and belly with horizontal belly scales; apricot-orange back and shoulders; his TWO WINGS FOLDED OVER HIS BACK LIKE A CAPE - dark navy / dark purple outside with rows of TEAL SCALES (a few big teal scales on the shoulders like pauldrons), fading down to CRIMSON and then PINK at the pointed lower edge; FOUR SHORT LEGS - the forelegs DARK WINE RED with a row of DARK NAVY-PURPLE SCALE PLATES down their front, round dark red hind legs, SMALL DARK NAVY CLAWS; a LONG TAIL, red on top and apricot underneath, with a DARK NAVY FIN at its tip.
THE TAIL MUST NOT LIE ON THE GROUND: unlike image 8, it CURLS UP from behind his hips (an S-curve or a big arc), its tip in the air behind him, at least 4 squares above the ground; make the tail a bit shorter than in the game, about as long as he is tall, so the silhouette stays compact.
Pose (image 8): STANDING ON ALL FOUR LEGS like a lively puppy, head raised, chest out, smiling ahead; the forelegs straight, the hind legs a little bent; the wing cape over his back; the tail curling up behind. The two near legs (image left side of each pair) in full tone, the two far legs a shade darker and a little higher. 3/4 FRONT view facing image right, face and chest toward the viewer, snout pointing to the image right. All four feet on one ground line.
Proportions: ROUND and CHUNKY like images 10-13, chibi - a big head, short legs, a plump body. Keep the whole figure COMPACT.
Style: crisp chunky pixel art like images 10-13 - EVEN SQUARE PIXELS OF 12 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a TWO-SQUARE-THICK near-black outline around the silhouette, inside it every material in its own 3-4 flat shades, no stray single odd squares: the face and back apricot-orange, the chest and belly pale cream, the crest and the legs dark crimson / wine red, the wings dark navy-purple fading to crimson and pink, the spikes, horns and shoulder scales teal, the claws and the tail fin dark navy, the eyes teal with white; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no fire breath, no fireballs, no sneeze, no big dragon), only the two small flame tufts on the horns; no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，小火苗、尾巴都完整，不出画。
- **大头**、杏橙色鳞片脸、奶油色下巴；**一双大大的青绿眼睛**清楚可见（每只至少 3×3 格）；咧嘴笑 + 小白牙；深红鳞冠、扇形大耳鳍、青绿叶片鳞刺；两只短短的青绿小角 + 小撮橙黄火苗（小）。
- 奶油色横鳞肚子；翅膀收起来像斗篷（深蓝紫 + 青绿鳞 → 深红 → 粉红）；前腿深酒红 + 深蓝紫鳞甲；小深蓝爪子；尾巴红 / 杏色 + 深蓝尾鳍。
- **尾巴往上卷、不贴地**（尾巴尖离地至少 4 格），长度约等于身高。
- A 坐着上身立起、两只前爪并排撑地；B 四条腿站着、抬头挺胸。两版同一个比例：头和眼睛一样大；A 头顶到脚底约 612 px（约 51 格）。
- 近侧腿在画面左边亮色、远侧腿稍暗稍高；脚底落在同一条水平线上（离底边约 120 px）；除了头顶小火苗没有任何特效。
- **每块 12 像素、大小一致、对齐网格**；外轮廓 2 块宽的近黑描边；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 原始生成稿原样放 `raw/`；全部画完后最后写 `outputs/smolder-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画和 raw/ 放进 `assets/source/smolder/codex_picture/`，先在 8 倍下数清实际格子大小（Codex 常常不是 12 px，千珏是 5.5 px），按格子读回（regrid），和包里的英雄（加里奥 hd_idle、布隆/泽丽 lo_idle、本包 ADC 1x）并排、在游戏实际大小下给用户挑 A / B 和大小。raw 稿通常比 Codex 自己缩的成品干净（巴德、赛恩、马尔扎哈的教训）。
- 选定后写第 1 步 `MODEL_PROMPTS.md`：**正面（3/4，待机 + 选人卡）+ 侧面（朝右，所有动作的底子；四条腿跑动）**两个视图，同一个高度、同一套格子、同样的细节（side-view-design；用户也可能说不要侧面，先问）；PPU 1.5，原稿 1:1 按格读回，绝不先画大再缩；描边约 1 游戏像素；大小用 hd.rs SIZES 调。
- 同一张脸贯穿所有帧（one-face-all-frames）；尾巴待机 / 走路都不贴地（tail-off-ground）；跑步四条腿交替；翅膀只在 E 起飞时张开；妈妈（R）是第 3 步的特效。
