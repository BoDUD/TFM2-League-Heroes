# 瑟提（Sett，腕豪）原图提示词包 · 第 0 步

**给用户（中文说明）**：瑟提还没有原图。请把整个 zip 交给 Codex，它按下面的英文提示词画**两张**高清像素风原图，
同一个人物、同一画风、同一镜头和比例，只差姿势：
- **A：英雄联盟的待机**（附图 4 就是待机第一帧）——站直、身子微微后仰、挺胸抬下巴，一副「老大」的样子；两臂垂在身侧微弯，拳头半握；前脚在前，两脚分开。
- **B：拳击架势**（英雄联盟普攻出拳之后的姿势）——压低重心的宽站姿，双拳握紧举在身前，远侧的拳在前、近侧的拳护在下巴旁。

你挑一张，第 1 步再按它画游戏尺寸的精灵（约 40 行，和亚托克斯、德莱厄斯一样的大块头上单）。

参考图是你给的 `sett_refs.zip` 里的 `refs/`（3 官方原画、4 游戏内模型待机、5 头部特写）。`pose_refs/` 是英雄联盟的动作关键帧，留到第 2 步画动作时用，这一轮不附。
它们都是 Riot 的素材，只当参考，不进仓库。

- **长相照英雄联盟原版（经典皮肤，以 3–5 号为准）**：半瓦斯塔亚人的大块头拳手，宽肩厚胸、手臂粗壮、腰窄、腿长；暖肤色。
  - **头**：**鲜艳的绯红色头发**，不长，往上往后翘成几撮尖，额前垂下几缕；头顶一对**竖起的兽耳**（外面红、里面深紫）；
    脑后一条细长的**小辫**垂到腰，末端一颗红珠子和一个金色尖坠。**琥珀色眼睛**、浓眉、下巴硬朗，神情傲气。
  - **上身**：**赤裸上身**，胸肌腹肌分明；脖子上一个**金色项圈**（V 字形）；两肩前面各一个**金色兽头扣饰**（张着嘴的兽头），
    扣着一圈**巨大的深紫色毛领**——毛领一簇簇像羽毛一样往后、往外炸开，是他剪影里最大的一块。
  - **外套**：**深紫红（近黑的梅子色）无袖长外套**挂在肩上、前面敞开，下摆到小腿，边上有金色镶边。
  - **手**：上臂裸着；前臂缠着**浅灰白的绷带**；**深紫色露指手套**，外侧有紫色的毛；手腕上**金色护腕**，拳头上有金饰。
    拳头是他的武器，要**画得大**（每只拳头差不多和头一样大）。
  - **下身**：金色 V 形腰扣；**白色（略带灰蓝）的紧身长裤**，两侧金色细条纹；**金边的尖头翘鞋**（金色配深红）。
  - 配色：绯红头发 + 深紫毛领 + 金饰 + 梅子色外套 + 白裤子 + 暖肤色。
- **风格照 1、2 号**（你之前画的凯隐、蔚，用户都采用了）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；
  头比英雄联盟模型大一些（头加头发约占身高 25–28%），这样缩到游戏尺寸还看得见脸。深色都用有颜色的深色
  （毛领深紫、外套梅子色、头发深绯红），黑色只用在描边；白裤子要用浅灰蓝的阴影画出体积，不是一片纯白。
- 不画任何特效（拳头的光、护盾、冲击波都等第 3 步单独画）；**脚底是最低点**，外套下摆、小辫、毛领都不能低于脚底线（游戏在脚下画血条）。
- **背景**：真透明；做不到就用纯绿 `#00FF00`，**不要洋红色**（他的头发是绯红色，会被一起抠掉）。
- 交付：`outputs/sett-picture/` 里的 `sett-model-A.png`、`sett-model-B.png`（1024×1536，真透明，人物约 1100 px 高），
  附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**写 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `style/1_style_kayn.png` | 你之前画的凯隐原图 A（用户采用） | **只看画风**：赤裸上身的男性英雄、肌肉的画法、深色的亮边 |
| `style/2_style_vi.png` | 你之前画的蔚原图 A（用户采用） | **只看画风**：拳手、超大的拳头和金属饰件怎么画清楚 |
| `refs/3_sett_splash.png` | 瑟提经典皮肤的官方原画 | 长相、毛领和兽头扣饰、气质 |
| `refs/4_sett_ingame_front.png` | 游戏内模型，3/4 正面朝右，待机第一帧 | **服装和配色以它为准**；也是 A 的姿势 |
| `refs/5_sett_head.png` | 头部特写 | 红发、兽耳、琥珀色眼睛、表情 |

图像工具一次最多收 5 张参考：就是上面这 5 张，按顺序附上。

## 提示词 A：`sett-model-A.png`（英雄联盟的待机）

```text
Attached images, in order: 1 and 2 are STYLE ONLY - pixel-art pictures of OTHER characters from the same game that the user approved (1: a shirtless male fighter, 2: a woman brawler with huge fists); copy their pixel-art style and their way of drawing muscles, gold trims and big fists, NOT their costumes, colours or poses. Images 3, 4 and 5 are the character from League of Legends (3 the official illustration, 4 the in-game model 3/4 front facing right in his idle pose, 5 the head): they are authoritative for his look - copy the costume, the hair and the colours from them, NOT their 3D shading or painted lighting.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha; if impossible, a flat pure green #00FF00 background - never magenta or pink), the character about 1100 px tall from the top of the ears to the soles, centred, with at least 60 px of transparent margin all round (the fur mantle included).
The character: Sett, the Boss - a towering half-vastayan pit fighter. A very muscular build: broad shoulders, a huge chest, thick arms, a narrow waist, long legs; warm tan skin. HEAD: vivid CRIMSON-RED hair, not long, swept up and back into a few spiky tufts with some locks falling over the forehead; two pointed furry VASTAYAN EARS standing up on top of his head (crimson outside, dark purple inside); a long thin BRAID hanging from the back of his head down to his waist, ending in a red bead and a small gold spike; AMBER-ORANGE eyes, heavy brows, a strong jaw, an arrogant expression. NECK: a thick GOLD torc (V-shaped collar). SHOULDERS: two ornate GOLD BEAST-HEAD clasps (snarling beast heads) on the front of his shoulders pinning a HUGE shaggy DARK PURPLE FUR MANTLE that bursts out behind his shoulders and back in big feather-like tufts (the biggest shape of his silhouette after his body). BODY: bare muscular chest and abs; a long SLEEVELESS dark PLUM (near-black purple-red) COAT hanging from his shoulders, open in front, its tails down to his calves, with gold trim along the edges. ARMS: bare upper arms; forearms wrapped in pale grey-white bandages; dark purple fingerless gloves with purple fur tufts on the outer forearm, GOLD cuffs at the wrists and gold ornaments on the knuckles; the FISTS big and solid - his weapons - each fist about as big as his head. LEGS: a gold V-shaped belt buckle; fitted WHITE trousers (pale blue-grey shading) with thin gold stripes down the sides; curled pointed shoes trimmed in gold and dark red.
Proportions: game-sprite proportions like images 1 and 2 - a bigger head than the 3D model (the head with its hair about 25-28% of his height, not counting the mantle), the fists a little oversized; heroic and massive, not stocky or fat. 3/4 FRONT view facing image right: face and chest turned toward the viewer's right, BOTH eyes visible, level and the same size, nothing covering the face; never his back or a pure side view.
Pose: League's own idle (image 4): he stands upright and leans back a little, chest out, chin slightly raised in a cocky way but the face still turned to the viewer; both arms hang at his sides slightly bent, the fists loosely clenched; the front foot a step ahead, feet apart on one flat ground line. The soles are the lowest thing in the picture: the coat's tails, the braid and the mantle end AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 1 and 2 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: deep violet for the mantle, dark plum for the coat, deep crimson for the hair - never black fill, black is only the outline; the white trousers shaded in pale blue-greys, never one flat white); bright gold highlights on the torc, the beast-head clasps, the cuffs, the trims and the shoes; light rim lights on the muscles, the hair and the fur; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No glowing fists, no shockwave, no shield, no effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`sett-model-B.png`（拳击架势）

附图同上。

```text
Attached images, in order: 1 and 2 are STYLE ONLY - pixel-art pictures of OTHER characters from the same game that the user approved (1: a shirtless male fighter, 2: a woman brawler with huge fists); copy their pixel-art style and their way of drawing muscles, gold trims and big fists, NOT their costumes, colours or poses. Images 3, 4 and 5 are the character from League of Legends (3 the official illustration, 4 the in-game model 3/4 front facing right in his idle pose, 5 the head): they are authoritative for his look - copy the costume, the hair and the colours from them, NOT their 3D shading or painted lighting.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha; if impossible, a flat pure green #00FF00 background - never magenta or pink), the character about 1100 px tall from the top of the ears to the soles, centred, with at least 60 px of transparent margin all round (the fur mantle included).
The character: Sett, the Boss - a towering half-vastayan pit fighter. A very muscular build: broad shoulders, a huge chest, thick arms, a narrow waist, long legs; warm tan skin. HEAD: vivid CRIMSON-RED hair, not long, swept up and back into a few spiky tufts with some locks falling over the forehead; two pointed furry VASTAYAN EARS standing up on top of his head (crimson outside, dark purple inside); a long thin BRAID hanging from the back of his head down to his waist, ending in a red bead and a small gold spike; AMBER-ORANGE eyes, heavy brows, a strong jaw, an arrogant expression. NECK: a thick GOLD torc (V-shaped collar). SHOULDERS: two ornate GOLD BEAST-HEAD clasps (snarling beast heads) on the front of his shoulders pinning a HUGE shaggy DARK PURPLE FUR MANTLE that bursts out behind his shoulders and back in big feather-like tufts (the biggest shape of his silhouette after his body). BODY: bare muscular chest and abs; a long SLEEVELESS dark PLUM (near-black purple-red) COAT hanging from his shoulders, open in front, its tails down to his calves, with gold trim along the edges. ARMS: bare upper arms; forearms wrapped in pale grey-white bandages; dark purple fingerless gloves with purple fur tufts on the outer forearm, GOLD cuffs at the wrists and gold ornaments on the knuckles; the FISTS big and solid - his weapons - each fist about as big as his head. LEGS: a gold V-shaped belt buckle; fitted WHITE trousers (pale blue-grey shading) with thin gold stripes down the sides; curled pointed shoes trimmed in gold and dark red.
Proportions: game-sprite proportions like images 1 and 2 - a bigger head than the 3D model (the head with its hair about 25-28% of his height, not counting the mantle), the fists a little oversized; heroic and massive, not stocky or fat. 3/4 FRONT view facing image right: face and chest turned toward the viewer's right, BOTH eyes visible, level and the same size, nothing covering the face; never his back or a pure side view.
Pose: a boxer's fighting guard, as League's Sett stands after a punch - a wide, low stance, knees bent, feet far apart on one flat ground line, weight forward; the FAR fist held forward at chest height, the NEAR fist raised beside his chin; elbows in, shoulders hunched a little, a cocky grin. The soles are the lowest thing in the picture: the coat's tails, the braid and the mantle end AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 1 and 2 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: deep violet for the mantle, dark plum for the coat, deep crimson for the hair - never black fill, black is only the outline; the white trousers shaded in pale blue-greys, never one flat white); bright gold highlights on the torc, the beast-head clasps, the cuffs, the trims and the shoes; light rim lights on the muscles, the hair and the fur; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No glowing fists, no shockwave, no shield, no effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底）；做不到就是纯绿 `#00FF00`，**不是洋红**；四周留边，人物和毛领完整，拳头没被切掉。
- 面朝右的 3/4 正面；两只眼睛都看得见、同一高度、一样大、琥珀色；脸没被拳头或毛领挡住。
- 绯红头发、两只兽耳、脑后的小辫；金项圈和两个金色兽头扣饰；深紫大毛领；梅子色无袖长外套；缠绷带的前臂和深紫手套；白裤子和金色尖头鞋——都在，配色和 4 号一致。
- 缩到 40 px 高还认得出「红头发 + 紫毛领 + 白裤子 + 两只大拳头」。
- 脚底是最低点，外套下摆、小辫、毛领都不低于它；没有光效、冲击波、护盾。
- 大像素块清楚，没有糊、没有柔光、没有渐变；深色部分有颜色（不是一片纯黑），白裤子有灰蓝的阴影。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/sett-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## 之后的步骤（给用户看，Codex 这一轮不用管）

1. **第 1 步造型**：按选定的 A 或 B，直接画游戏尺寸（约 40 格，耳尖到脚底），8 倍方格；读回后给你看，选定再往下。
2. **第 2 步动作**：参考 `sett_refs.zip` 的 `pose_refs/`（英雄联盟的关键帧）。标签和出手时机已经在技能数据里定好（`tools/kit/sett_kit.py`），
   画出来的出手帧和这里差得多的话，就按动作条改技能数据的时机：
   | 标签 | 内容 | 英雄联盟的参考 | 时长 / 出手 |
   |---|---|---|---|
   | `idle` / `run` | 待机、移动 | `Sett_Idle`、`Sett_Run` | — |
   | `attack` | 左拳刺拳 | `Sett_Attack1` | 0.4 秒，第 12 tick 打中 |
   | `attack2` | 右拳重拳（更快） | `Sett_attack2` | 从第 3 tick 播 21 tick，第 9 tick 打中 |
   | `skill` | E 强手裂颅：双臂往两侧张开、往前合拢对撞 | `Sett_Spell3_Start`、`Sett_Spell3_Front` | 0.5 秒，第 10 tick 抓住，第 18 tick 对撞 |
   | `skill2` | W 蓄意轰拳：拳头往后拉蓄力，一拳轰出 | `Sett_spell2`（英雄联盟蓄力 0.78 秒） | 0.9 秒，第 29 tick 出拳 |
   | `ult` | R 往前一扑、抓住英雄、往前扔 | `Sett_Spell4_Grab` | 前 8 tick |
   | `ult_dash` | R 平飞着追上去 | `Sett_Spell4_Dash` | 循环，到落地为止 |
   | `ult_slam` | R 高举后翻身砸地、起身 | `Sett_Spell4_PowerBomb` | 0.4 秒，第 4 tick 砸中 |
   | `hit` / `dead` | 受击、死亡（往后倒、仰躺） | `Sett_Death` | — |
3. **第 3 步特效**：`league_sett_fx`（普攻左右拳命中、屈人之威的金色拳光和命中、E 抓中、W 护盾、W 真伤命中、R 抓取和命中、满豪意的热浪）
   和 `league_sett_big`（W 拳头冲击波和地面预警、E 对撞的爆点、R 砸地的大坑）。
