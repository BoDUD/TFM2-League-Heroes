# 派克：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 派克还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（身子前倾半蹲，后手把鱼叉高高举在身侧、叉刃斜朝上，前手空着垂在膝前、手指张开像爪子）；**B = 英雄联盟的入场站姿**（站得直一些，后手攥着鱼叉尾部的金钩、整把鱼叉竖在身侧、叉刃朝下，前手空着垂在身侧）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行）。
> - **长相照英雄联盟原版**（附图 1–7）：血港鬼影派克，一个**溺死后归来的鱼叉手**，高大精瘦、**深棕偏紫灰的皮肤**（像泡过水的死人），**光头**、头顶几道疤；**一双发着淡青白光的眼睛**；**下半张脸蒙着红色面巾**，面巾上一道道**锯齿状的浅粉 / 骨白色条纹**（像一排鲨鱼牙），面巾尾巴垂到胸口。
> - **服装**：**两肩一圈巨大的骨白色獠牙 / 鲸骨尖刺**，像一圈鲨鱼牙披在肩上，绕过脖子；**青蓝色的短外套 / 背心，镶金色花纹边**，敞着胸口；背后**一条很长的深海军蓝外套下摆**拖到小腿；**腰上一圈棕色皮带，挂着几个金色圆形徽章 / 扣子**，一条红色腰布；**深灰绿色的宽松长裤**；**膝盖前一块大大的棕色皮护膝（金扣）**；棕色皮靴；两条前臂有深色的纹身环带，手是**深色的、手指细长的爪子样**。
> - **武器：一把鱼叉**（约他身高的 0.7）：**骨白色、带一排倒钩锯齿的宽叉刃**，叉刃和杆子之间一个**古铜金色的护手，镶一颗青色宝石**；杆子缠**红色**布条；杆子尾端一个**金色的弯钩**。
> - **风格和比例照附图 8–10**（之前让你画的莎弥拉、烬、凯隐）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（约占身高三分之一），身材精瘦，腿稍短；发光的眼睛、红面巾和上面的白色锯齿条纹、肩上的骨白獠牙、金色徽章、鱼叉的骨白叉刃和青宝石画大一点，小尺寸下才看得出来。深色皮肤、深灰绿裤子、深蓝下摆容易糊成一片：**皮肤用暖一点的紫棕加亮边，外套用青蓝加金边，獠牙和叉刃是最亮的骨白，红面巾和发光眼睛是亮点**。
> - **画布用横版 1536×1024**：人物从头顶到鞋底约 820 px，整把鱼叉（叉尖、金钩）都在画面里，不能出画。
> - **3/4 正面朝右**，脸朝向观众：两只发光的眼睛和红面巾都要看得见，不能画成背影；拿鱼叉的手和鱼叉不能藏在身体后面。
> - 不画任何特效（钩子的锁链、水花、魅影第 3 步再单独画）；鞋底是最低点，平平地落在一条地面线上（游戏在脚下画血条），鱼叉也不能低于这条线。
> - 交付：`outputs/pyke-picture/pyke-model-A.png`、`outputs/pyke-picture/pyke-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `pyke_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_pyke_league_front.png` | 英雄联盟原版派克，待机第一帧，3/4 朝右 | 服装、颜色、A 的姿势 |
| `refs/2_pyke_league_frontal.png` | 同一帧，正面 | 外套、獠牙、腰带徽章、护膝、靴子 |
| `refs/3_pyke_league_head.png` | 头和肩的特写 | 光头和疤、发光的眼睛、红面巾的锯齿条纹、肩上的獠牙 |
| `refs/4_pyke_league_back.png` | 同一帧的背后 | 背后的深蓝外套下摆、獠牙绕过后颈 |
| `refs/5_pyke_splash.png` | 官方加载画面 | 气质（阴森、溺死归来）、发光的眼睛 |
| `refs/6_pyke_league_standing.png` | 英雄联盟入场站姿：鱼叉竖着拿在身侧、叉刃朝下 | B 的姿势、鱼叉的样子 |
| `refs/7_pyke_league_actions.png` | 英雄联盟里普攻、Q 戳刺、扔鱼叉、跑步的几个瞬间 | 鱼叉拿在手里的样子 |
| `style/8_style_samira.png` | 你之前的莎弥拉像素图 | **只看风格**（最近通过的一张） |
| `style/9_style_jhin.png` | 你之前的烬像素图 | **只看风格**（蒙面的男性角色） |
| `style/10_style_kayn.png` | 你之前的凯隐像素图 | **只看风格**（深色系的男性角色） |

## 提示词 A：`pyke-model-A.png`（英雄联盟待机：前倾半蹲、鱼叉高举）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen from the front: the coat, the bone spikes, the belt medallions, the knee guard, the boots; 3 the head and shoulders close-up: the bald scarred head, the glowing eyes, the red face mask with its jagged stripes, the bone spikes on the shoulders; 4 the same pose from behind: the long dark coat tail and the spikes round the neck; 5 the official illustration: his mood and the glowing eyes; 6 League's standing pose with the harpoon held upright at his side, blade down, the pose of version B; 7 a few moments of his attack, his stab, his harpoon throw and his run: how he holds the harpoon). Copy from the images the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 the latest approved picture of this series, image 9 a masked man, image 10 a dark-palette man).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 820 px tall from the top of his head to the soles, centred, comfortable transparent margins, nothing cut off (the whole harpoon inside the picture, the barbed blade and the gold hook).
The character: Pyke, the Bloodharbor Ripper: a drowned harpooner come back from the sea, tall and lean, with dark brown-purple skin like a drowned man's. HEAD: BALD with a few scars on the scalp; two eyes GLOWING PALE CYAN-WHITE; the lower half of the face covered by a RED CLOTH MASK with jagged PALE BONE-WHITE stripes like a row of shark teeth, its end hanging down to the chest. BODY: a ring of HUGE BONE-WHITE SPIKES / SHARK TEETH wrapped over both shoulders and round the neck like a mantle; a short TEAL-BLUE coat / vest with GOLD patterned trim, open at the chest; a LONG DARK NAVY COAT TAIL hanging behind him down to the calves; a brown leather belt with several round GOLD MEDALLIONS and a red waist cloth; dark tattoo bands on the forearms; dark hands with long thin claw-like fingers. LEGS: baggy dark grey-green trousers; a big brown leather KNEE GUARD with a gold buckle on the front knee; brown leather boots. WEAPON: a HARPOON about 0.7 of his height: a wide BONE-WHITE BLADE with a row of jagged barbs on one edge, a bronze-gold guard with a CYAN GEM between the blade and the shaft, the shaft wrapped in RED cloth, a curved GOLD HOOK at the butt end.
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of his height), a lean wiry body, legs a little shorter; the glowing eyes, the red mask and its white stripes, the bone spikes, the gold medallions, the harpoon's bone-white blade and cyan gem drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both glowing eyes and the red mask visible, nothing covers the face; the hand holding the harpoon and the harpoon itself are never hidden behind the body.
Pose: League's own idle (image 1), turned a little more toward the viewer: crouched forward facing image right, knees bent, feet apart; the BACK hand (image left) holds the harpoon RAISED HIGH out beside his head, the blade pointing up and forward diagonally, the gold hook down behind; the FRONT hand (image right) empty, hanging low in front of the front knee with the claw fingers spread; the coat tail hanging behind. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the harpoon stays above that line.
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the skin warm dark purple-brown with lighter lit edges, the coat teal-blue with gold trim, the spikes and the harpoon blade the brightest bone-white with warm grey shading, the mask red with bone-white stripes, the eyes glowing pale cyan, the trousers dark grey-green, the coat tail dark navy, the belt, knee guard and boots brown leather with gold; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no chain, no water, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`pyke-model-B.png`（英雄联盟入场站姿：鱼叉竖着拿在身侧）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen from the front: the coat, the bone spikes, the belt medallions, the knee guard, the boots; 3 the head and shoulders close-up: the bald scarred head, the glowing eyes, the red face mask with its jagged stripes, the bone spikes on the shoulders; 4 the same pose from behind: the long dark coat tail and the spikes round the neck; 5 the official illustration: his mood and the glowing eyes; 6 League's standing pose with the harpoon held upright at his side, blade down, the pose of version B; 7 a few moments of his attack, his stab, his harpoon throw and his run: how he holds the harpoon). Copy from the images the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 the latest approved picture of this series, image 9 a masked man, image 10 a dark-palette man).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 820 px tall from the top of his head to the soles, centred, comfortable transparent margins, nothing cut off (the whole harpoon inside the picture, the barbed blade and the gold hook).
The character: Pyke, the Bloodharbor Ripper: a drowned harpooner come back from the sea, tall and lean, with dark brown-purple skin like a drowned man's. HEAD: BALD with a few scars on the scalp; two eyes GLOWING PALE CYAN-WHITE; the lower half of the face covered by a RED CLOTH MASK with jagged PALE BONE-WHITE stripes like a row of shark teeth, its end hanging down to the chest. BODY: a ring of HUGE BONE-WHITE SPIKES / SHARK TEETH wrapped over both shoulders and round the neck like a mantle; a short TEAL-BLUE coat / vest with GOLD patterned trim, open at the chest; a LONG DARK NAVY COAT TAIL hanging behind him down to the calves; a brown leather belt with several round GOLD MEDALLIONS and a red waist cloth; dark tattoo bands on the forearms; dark hands with long thin claw-like fingers. LEGS: baggy dark grey-green trousers; a big brown leather KNEE GUARD with a gold buckle on the front knee; brown leather boots. WEAPON: a HARPOON about 0.7 of his height: a wide BONE-WHITE BLADE with a row of jagged barbs on one edge, a bronze-gold guard with a CYAN GEM between the blade and the shaft, the shaft wrapped in RED cloth, a curved GOLD HOOK at the butt end.
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of his height), a lean wiry body, legs a little shorter; the glowing eyes, the red mask and its white stripes, the bone spikes, the gold medallions, the harpoon's bone-white blade and cyan gem drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both glowing eyes and the red mask visible, nothing covers the face; the hand holding the harpoon and the harpoon itself are never hidden behind the body.
Pose: League's standing pose (image 6): standing a little hunched facing image right, feet a little apart, the shoulders forward; the BACK hand (image left) grips the harpoon near its gold hook at shoulder height, the harpoon hanging UPRIGHT beside his body on image left, the barbed blade pointing DOWN, its tip at about knee height; the FRONT hand (image right) empty, hanging at his side with the claw fingers slightly spread; the coat tail hanging behind. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the harpoon stays above that line.
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the skin warm dark purple-brown with lighter lit edges, the coat teal-blue with gold trim, the spikes and the harpoon blade the brightest bone-white with warm grey shading, the mask red with bone-white stripes, the eyes glowing pale cyan, the trousers dark grey-green, the coat tail dark navy, the belt, knee guard and boots brown leather with gold; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no chain, no water, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物和整把鱼叉（叉尖、金钩）都完整。
- 光头带疤、两只发淡青白光的眼睛、红面巾上一道道骨白锯齿条纹。
- 两肩一圈骨白獠牙；青蓝外套 + 金边；背后深蓝长下摆；腰带金色圆徽章 + 红腰布。
- 深灰绿宽裤、前膝棕色大护膝（金扣）、棕色靴子。
- 鱼叉：骨白带倒钩的叉刃、古铜金护手 + 青宝石、红布缠杆、尾端金钩。
- 拿鱼叉的手和鱼叉没有藏在身体后面；鞋底是最低点，落在一条水平线上；没有多余特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/pyke-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/pyke/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40 行；A 高举的鱼叉在游戏里会让每帧又高又宽——先给用户看取舍）。
