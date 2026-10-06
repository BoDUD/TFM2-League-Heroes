# 格温：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 格温还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（站得端正，一只手在身侧握着张开的大剪刀，剪刀刃斜斜朝身后下方拖着）；**B = 英雄联盟的被动待机**（剪刀竖起来举在身侧，把手圈在胸口高度，刀刃朝上）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行）。
> - **长相照英雄联盟原版**（附图 1–7）：灵罗娃娃格温，一个**活泼可爱的布娃娃少女**，白皙皮肤、大大的蓝眼睛、粉色嘴唇、笑容甜。**亮天蓝色的头发**：齐刘海、头顶一撮呆毛，**两边各垂着两三个又大又卷的螺旋卷**（像钻头一样一圈圈）到肩下；头顶**两个大大的黑色蝴蝶结**（像一对猫耳朵竖着）。
> - **服装**：**白色到淡蓝紫色的蓬蓬短裙连衣裙**（裙摆鼓起、到膝盖），裙子正中一块深紫色前片；**裙底一圈深藏青 / 黑色的荷叶边衬裙**，上面一排**金色菱形小饰钉**；腰间一个**大大的紫色条纹蝴蝶结**，中间别着**金色星形胸针**；**黑色的泡泡短袖**；手臂白皙，戴**紫色手套**；腿上是**深灰蓝色菱格纹长袜**，脚上**灰白色短靴**，靴口有一圈荷叶边 / 小蝴蝶结。
> - **武器**：**一把巨大的剪刀**：两片**亮青蓝色的水晶刀刃**（像冰一样透亮，刃口最亮），**把手是两个华丽的银蓝色圆环**，环上带几根尖刺装饰。英雄联盟里剪刀比她还长一倍，**这里画得和她身高差不多长**（游戏里太长每帧都太宽）。
> - **风格和比例照附图 8–10**（你之前让 Codex 画的莎弥拉、伊芙琳、韦鲁斯）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（约占身高三分之一），身材娇小，腿稍短；大眼睛、黑蝴蝶结、螺旋卷、金星胸针、裙底金饰钉、剪刀的亮刃口画大一点，小尺寸下才看得出来。白裙子和淡色皮肤容易糊在一起：**裙子用冷白带淡紫蓝的阴影，皮肤用暖一点的白粉，裙底深藏青压住下沿**；剪刀用几档青蓝加近白的亮刃口。
> - **画布用横版 1536×1024**（剪刀太长，竖版放不下）：人物从头顶到鞋底约 800 px，整把剪刀（刀尖、两个把手圈）都在画面里，不能出画。
> - **3/4 正面朝右**，脸朝向观众：两只眼睛和眉毛都要看得见，不能画成背影。
> - 不画任何特效（剪刀的光、雾、丝线、针第 3 步再单独画），不画她的小娃娃（伊索德）；鞋底是最低点，平平地落在一条地面线上（游戏在脚下画血条），剪刀也不能低于这条线。
> - 交付：`outputs/gwen-picture/gwen-model-A.png`、`outputs/gwen-picture/gwen-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `gwen_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_gwen_league_front.png` | 英雄联盟原版格温，待机第一帧，3/4 朝右 | 服装、颜色、A 的姿势 |
| `refs/2_gwen_league_frontal.png` | 同一帧，正面 | 裙子、蝴蝶结、星形胸针、长袜和靴子 |
| `refs/3_gwen_league_head.png` | 头和肩的特写 | 脸、眼睛、刘海、螺旋卷、黑蝴蝶结 |
| `refs/4_gwen_league_back.png` | 同一帧的背后 | 后脑的头发和蝴蝶结、裙子背面 |
| `refs/5_gwen_splash.png` | 官方加载画面 | 气质（活泼甜美）、颜色 |
| `refs/6_gwen_league_passive.png` | 英雄联盟被动待机：剪刀竖着举在身侧 | B 的姿势 |
| `refs/7_gwen_league_actions.png` | 英雄联盟里普攻、剪剪剪、冲刺、扔针的几个瞬间 | 剪刀拿在手里的样子 |
| `style/8_style_samira.png` | 你之前的莎弥拉像素图 | **只看风格**（最近通过的一张，女性、大兵器） |
| `style/9_style_evelynn.png` | 你之前的伊芙琳像素图 | **只看风格**（女性身材比例） |
| `style/10_style_varus.png` | 你之前的韦鲁斯像素图 | **只看风格** |

## 提示词 A：`gwen-model-A.png`（英雄联盟待机：剪刀握在身侧、刀刃朝后下方）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen from the front: the dress, the bow, the star brooch, the stockings and boots; 3 the head and shoulders close-up: the face, the bangs, the drill curls, the black bows; 4 the same pose from behind; 5 the official illustration: her mood and colours; 6 League's passive idle with the scissors held upright at her side, the pose of version B; 7 a few moments of her snipping, dashing and throwing a needle: how she holds the scissors). Copy from the images the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 the latest approved picture of this series, a woman with a big weapon; image 9 a woman's proportions; image 10 another approved picture).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 800 px tall from the top of her head (bows included) to the soles, centred, comfortable transparent margins, nothing cut off (the whole pair of scissors inside the picture, points and both handle rings).
The character: Gwen, the Hallowed Seamstress: a cheerful, sweet living doll girl with fair skin, big bright BLUE eyes, pink lips and a happy smile. HEAD: bright SKY-BLUE hair with straight bangs and a little cowlick on top, and on each side two or three BIG SPIRAL DRILL CURLS hanging below her shoulders; TWO BIG BLACK RIBBON BOWS standing up on top of her head like a pair of ears. BODY: a puffy knee-length doll dress in WHITE with pale lavender-blue shading and a dark purple front panel, a full skirt; under its hem a ruffled DARK NAVY-BLACK petticoat with a row of small GOLD DIAMOND studs; a BIG PURPLE STRIPED BOW at the waist with a GOLD STAR brooch in its middle; BLACK puffed short sleeves; fair arms with PURPLE gloves. LEGS: dark grey-blue diamond-quilted stockings and short grey-white boots with a ruffle at the top. WEAPON: a GIANT PAIR OF SCISSORS: two glowing CYAN-BLUE CRYSTAL blades (icy and bright, the cutting edges brightest) and two ornate silvery-blue RING HANDLES with a few small spikes. In the game they are twice her height; here make the scissors about AS LONG AS SHE IS TALL.
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of her height), a small girlish body, legs a little shorter; the eyes, the black bows, the drill curls, the gold star, the gold studs and the scissors' bright edges drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both eyes and both brows visible, nothing covers the face.
Pose: League's own idle (image 1), turned a little more toward the viewer: standing neatly facing image right, feet close together; one hand at her side holding the OPEN scissors by a ring handle near her hip, the blades trailing diagonally down and back behind her toward image left, the points above the ground line; the other hand relaxed near her waist. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the scissors stay above that line.
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the dress cool white with pale lavender-blue shadows, the front panel and bow purple, the petticoat dark navy, the brooch and studs gold, the sleeves black, the skin warm pinkish white, the hair bright sky blue with lighter highlights and deeper blue shadows, the stockings dark grey-blue, the boots grey-white, the scissor blades cyan-blue with near-white edges, the handles silvery blue; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no mist, no threads, no needles, no doll, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`gwen-model-B.png`（英雄联盟被动待机：剪刀竖着举在身侧）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen from the front: the dress, the bow, the star brooch, the stockings and boots; 3 the head and shoulders close-up: the face, the bangs, the drill curls, the black bows; 4 the same pose from behind; 5 the official illustration: her mood and colours; 6 League's passive idle with the scissors held upright at her side, the pose of version B; 7 a few moments of her snipping, dashing and throwing a needle: how she holds the scissors). Copy from the images the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 the latest approved picture of this series, a woman with a big weapon; image 9 a woman's proportions; image 10 another approved picture).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 800 px tall from the top of her head (bows included) to the soles, centred, comfortable transparent margins, nothing cut off (the whole pair of scissors inside the picture, points and both handle rings).
The character: Gwen, the Hallowed Seamstress: a cheerful, sweet living doll girl with fair skin, big bright BLUE eyes, pink lips and a happy smile. HEAD: bright SKY-BLUE hair with straight bangs and a little cowlick on top, and on each side two or three BIG SPIRAL DRILL CURLS hanging below her shoulders; TWO BIG BLACK RIBBON BOWS standing up on top of her head like a pair of ears. BODY: a puffy knee-length doll dress in WHITE with pale lavender-blue shading and a dark purple front panel, a full skirt; under its hem a ruffled DARK NAVY-BLACK petticoat with a row of small GOLD DIAMOND studs; a BIG PURPLE STRIPED BOW at the waist with a GOLD STAR brooch in its middle; BLACK puffed short sleeves; fair arms with PURPLE gloves. LEGS: dark grey-blue diamond-quilted stockings and short grey-white boots with a ruffle at the top. WEAPON: a GIANT PAIR OF SCISSORS: two glowing CYAN-BLUE CRYSTAL blades (icy and bright, the cutting edges brightest) and two ornate silvery-blue RING HANDLES with a few small spikes. In the game they are twice her height; here make the scissors about AS LONG AS SHE IS TALL.
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of her height), a small girlish body, legs a little shorter; the eyes, the black bows, the drill curls, the gold star, the gold studs and the scissors' bright edges drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both eyes and both brows visible, nothing covers the face.
Pose: League's passive idle (image 6): standing lightly facing image right, the chest open toward the viewer; the BACK hand (image left side of her body) holds the scissors UPRIGHT beside her, the ring handles at chest height, the blades OPEN in a narrow V pointing UP past her head; the scissors stand BESIDE her body, never across the face; the front hand relaxed near her waist. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the dress cool white with pale lavender-blue shadows, the front panel and bow purple, the petticoat dark navy, the brooch and studs gold, the sleeves black, the skin warm pinkish white, the hair bright sky blue with lighter highlights and deeper blue shadows, the stockings dark grey-blue, the boots grey-white, the scissor blades cyan-blue with near-white edges, the handles silvery blue; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no mist, no threads, no needles, no doll, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物和整把剪刀（刀尖、两个把手圈）都完整。
- 亮天蓝色头发：齐刘海 + 呆毛 + 两边大螺旋卷；头顶两个竖起来的大黑蝴蝶结；两只蓝眼睛和眉毛看得见。
- 白色（淡紫蓝阴影）蓬蓬裙 + 深紫前片 + 裙底深藏青荷叶边和金菱形饰钉；腰间紫条纹大蝴蝶结 + 金星胸针；黑泡泡袖、紫手套。
- 深灰蓝菱格长袜、灰白短靴。
- 剪刀：两片青蓝水晶刃（刃口近白）+ 两个银蓝把手圈，长度和她身高差不多。
- 鞋底是最低点，落在一条水平线上；没有特效、没有小娃娃。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/gwen-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/gwen/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40 行；剪刀在游戏里还要再短一些，否则每帧太宽——先给用户看取舍）。
