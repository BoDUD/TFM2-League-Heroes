# 卡兹克：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 卡兹克还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版姿势相同（英雄联盟的待机：身子压低半蹲、两腿一前一后、两只镰刀爪垂在身前），只差**进化形态**：**A = 未进化**（英雄联盟出生时的样子）；**B = 本包的最终形态**（进化了 Q 收割利爪、E 虫翼、R 动态遮蔽：更大的锯齿镰刀爪、背上一对绿黄色的透明虫翼、背上一块更大的青蓝甲壳；**W 的背刺不进化，不画**）。游戏里换不了待机造型，所以只能选一个形态做精灵；你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行）。
> - **长相照英雄联盟原版**（附图 1–8）：虚空掠夺者卡兹克，一只**螳螂一样的虚空昆虫猎手**。**紫色 / 靛紫的甲壳**，甲壳边缘有**青绿色的反光**；关节、腹部、肩下露出**锈橙 / 棕红色的软肉**；**昆虫的头**，下颚和嘴是暗红色，**一双发黄白光的小眼睛**；头顶两根**细长的青绿色触角**向后上方翘起，头后一圈棕色的刺状颈饰。
> - **身体**：肩上两块**大大的紫色甲壳护肩**，上面有几颗**红色的小斑点 / 腺体**；细腰；两条手臂末端是**又长又弯的镰刀爪**（紫色刀身，刃口是**骨白 / 浅粉色**）；**反关节的昆虫腿**（膝盖朝后弯），小腿细长，脚是**几根棕色的爪趾**；背上一块**青蓝色的甲壳**。
> - **B 多出来的**：两只爪子更大、刃口一排**锯齿**；背上一对**半透明的绿黄色虫翼**，向后斜着伸出去，翅脉清楚；背上的青蓝甲壳更大、盖住后背（照附图 6、7）。
> - **风格和比例照附图 9–11**（之前让你画的派克、牛头、凯隐）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些，身体精瘦；发光的眼睛、触角、镰刀爪的骨白刃口、红色斑点画大一点，小尺寸下才看得出来。紫色甲壳容易和暗色糊成一片：**甲壳用亮一点的蓝紫加青绿高光边，软肉用暖锈橙，刃口是最亮的骨白，眼睛是亮点**。
> - **画布用横版 1536×1024**：人物从触角尖到脚爪约 820 px（蹲着，比站直矮），两只镰刀爪、触角、B 的翅膀都在画面里，不能出画。
> - **3/4 正面朝右**，脸朝向观众：眼睛和下颚要看得见，不能画成背影；两只镰刀爪都不能藏在身体后面。
> - 不画任何特效（尖刺、紫色虚空能量、隐身第 3 步再单独画）；脚爪是最低点，平平地落在一条地面线上（游戏在脚下画血条），镰刀爪也不能低于这条线。
> - 交付：`outputs/khazix-picture/khazix-model-A.png`、`outputs/khazix-picture/khazix-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `khazix_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_khazix_league_front.png` | 英雄联盟原版卡兹克（未进化），待机第一帧，3/4 朝右 | 颜色、形状、A 的样子和姿势 |
| `refs/2_khazix_league_side.png` | 同一帧，更侧一点 | 反关节腿、镰刀爪的长度和弯度 |
| `refs/3_khazix_league_head.png` | 头和肩的特写 | 昆虫头、眼睛、下颚、触角、护肩上的红斑点 |
| `refs/4_khazix_league_back.png` | 同一帧的背后 | 背上的甲壳、颈后的棕色刺饰 |
| `refs/5_khazix_splash.png` | 官方加载画面 | 气质（虚空猎手、凶狠） |
| `refs/6_khazix_league_evolved.png` | 本包的最终形态（Q 爪 + E 翅膀 + R 甲壳进化），3/4 朝右 | B 的样子 |
| `refs/7_khazix_league_evolved_side.png` | 同上，更侧一点 | B 的翅膀和甲壳 |
| `refs/8_khazix_league_actions.png` | 英雄联盟里普攻、Q、W、E 跳跃、跑步的几个瞬间（未进化） | 爪子和腿怎么动 |
| `style/9_style_pyke.png` | 你之前的派克像素图 | **只看风格**（最近通过的一张，半蹲的姿势） |
| `style/10_style_alistar.png` | 你之前的牛头像素图 | **只看风格**（非人类的角色） |
| `style/11_style_kayn.png` | 你之前的凯隐像素图 | **只看风格**（深色系、带镰刀） |

## 提示词 A：`khazix-model-A.png`（未进化）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, UNEVOLVED - the look and pose of version A; 2 the same, more from the side: the backward-bending insect legs and the length and curve of the scythe claws; 3 the head and shoulders close-up: the insect head, the eyes, the mandibles, the antennae, the red spots on the shoulder plates; 4 the same pose from behind: the back shell and the brown spiky frill behind the head; 5 the official illustration: his mood; 6 and 7 the EVOLVED form of version B, not for this picture; 8 a few moments of his attack, his spells, his leap and his run: how the claws and legs move). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, a crouching figure; image 10 a non-human character; image 11 a dark-palette character with a scythe).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 820 px tall from the antenna tips to the foot claws (crouched), centred, comfortable transparent margins, nothing cut off (both scythe claws and both antennae inside the picture).
The character: Kha'Zix, the Voidreaver: a mantis-like insect predator from the Void. CARAPACE: PURPLE / INDIGO-VIOLET chitin plates with TEAL-GREEN glints on their edges; RUSTY ORANGE-BROWN soft flesh showing at the joints, the belly and under the shoulders. HEAD: an insect head with dark red mandibles and mouth, two small GLOWING PALE YELLOW-WHITE eyes, two long thin TEAL ANTENNAE sweeping up and back, a brown spiky frill behind the head. BODY: two big purple chitin SHOULDER PLATES with a few small RED SPOTS / glands; a thin waist; both arms end in long curved SCYTHE CLAWS - purple blades with a BONE-WHITE / PALE PINK cutting edge; a teal-blue shell on the back. LEGS: digitigrade insect legs bending BACKWARD at the knee, thin long shins, feet of a few brown hooked toe claws.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model, a lean wiry body; the glowing eyes, the antennae, the white edges of the scythe claws and the red spots drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: the eyes and the mandibles visible, nothing covers the face; both scythe claws visible, never hidden behind the body.
Pose: League's own idle (image 1), turned a little more toward the viewer: crouched low facing image right, the front leg (image right) forward and bent, the back leg (image left) stretched behind, knees bent the insect way; both arms held low in front of the body, the scythe claws pointing forward and down, ready to strike. The foot claws are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the scythes stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the carapace a brighter blue-violet with teal-green lit edges, the flesh warm rusty orange-brown, the scythe edges the brightest bone-white, the eyes glowing pale yellow, the antennae teal, the toe claws brown; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
UNEVOLVED: no wings, no spikes on the back, normal-sized claws.
No effects, no void energy, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`khazix-model-B.png`（本包的最终形态：Q 爪、E 翅膀、R 甲壳进化）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, unevolved - the pose of this picture; 2 the same, more from the side: the backward-bending insect legs and the scythe claws; 3 the head and shoulders close-up: the insect head, the eyes, the mandibles, the antennae, the red spots on the shoulder plates; 4 the same pose from behind: the back shell and the brown spiky frill behind the head; 5 the official illustration: his mood; 6 and 7 the EVOLVED form to draw here - bigger serrated claws, a pair of translucent green-yellow insect wings and a bigger teal-blue back shell, seen from 3/4 and more from the side; 8 a few moments of his attack, his spells, his leap and his run: how the claws and legs move). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, a crouching figure; image 10 a non-human character; image 11 a dark-palette character with a scythe).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 820 px tall from the antenna tips to the foot claws (crouched), centred, comfortable transparent margins, nothing cut off (both scythe claws, both antennae and both wings inside the picture).
The character: Kha'Zix, the Voidreaver, EVOLVED: a mantis-like insect predator from the Void. CARAPACE: PURPLE / INDIGO-VIOLET chitin plates with TEAL-GREEN glints on their edges; RUSTY ORANGE-BROWN soft flesh showing at the joints, the belly and under the shoulders. HEAD: an insect head with dark red mandibles and mouth, two small GLOWING PALE YELLOW-WHITE eyes, two long thin TEAL ANTENNAE sweeping up and back, a brown spiky frill behind the head. BODY: two big purple chitin SHOULDER PLATES with a few small RED SPOTS / glands; a thin waist; both arms end in BIG curved SCYTHE CLAWS with a row of JAGGED SERRATIONS - purple blades with a BONE-WHITE / PALE PINK cutting edge (images 6-7); a pair of TRANSLUCENT GREEN-YELLOW INSECT WINGS with clear darker veins on the back, folded and angled up and back behind him; a BIG TEAL-BLUE SHELL covering the back between the wings. LEGS: digitigrade insect legs bending BACKWARD at the knee, thin long shins, feet of a few brown hooked toe claws.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model, a lean wiry body; the glowing eyes, the antennae, the white serrated edges of the claws, the wings' veins and the red spots drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: the eyes and the mandibles visible, nothing covers the face; both scythe claws visible, never hidden behind the body; the wings behind the body, not over the face.
Pose: League's own idle (image 1), turned a little more toward the viewer: crouched low facing image right, the front leg (image right) forward and bent, the back leg (image left) stretched behind, knees bent the insect way; both arms held low in front of the body, the scythe claws pointing forward and down, ready to strike; the wings folded up and back. The foot claws are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the scythes stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the carapace a brighter blue-violet with teal-green lit edges, the flesh warm rusty orange-brown, the scythe edges the brightest bone-white, the wings light green-yellow (drawn opaque in flat light shades, darker green veins, no real transparency), the back shell teal-blue, the eyes glowing pale yellow, the antennae teal, the toe claws brown; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
NOT evolved: no spikes / quills on the back or shoulders (only the claws, the wings and the shell are evolved).
No effects, no void energy, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物、两只镰刀爪、触角（B 还有翅膀）都完整。
- 紫色甲壳带青绿高光边、锈橙色软肉、昆虫头 + 暗红下颚 + 发黄白光的眼睛、两根青绿触角。
- 护肩上的红斑点；镰刀爪的骨白刃口；反关节腿、棕色爪趾。
- A：没有翅膀、没有背刺、普通大小的爪子。B：大锯齿爪、绿黄色虫翼（不透明的浅色平涂 + 深绿翅脉）、更大的青蓝背甲；没有背刺。
- 两只镰刀爪没有藏在身体后面；脚爪是最低点，落在一条水平线上；没有多余特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/khazix-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/khazix/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40 行；蹲姿 + 镰刀爪 + B 的翅膀会让每帧又宽又高——先给用户看取舍）。
