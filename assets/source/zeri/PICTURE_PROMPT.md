# 泽丽：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 泽丽还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**拿枪的姿势**，长相、发型、衣服完全一样：**A = 英雄联盟里的待机：电击步枪竖着举在画面右侧的肩旁（枪口朝上），另一只手垂在身侧**（附图 1、2）；**B = 射击站姿：步枪平端在腰前、枪口朝右（朝前），两腿分开站稳**（附图 8）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40–42 行，和辛德拉、萨勒芬妮差不多高）。
> - **长相照英雄联盟原版**（附图 1–8，经典造型）：祖安花火泽丽，一个活泼、自信、带电的祖安街头少女。**头顶两个很大的尖刺发髻**（像两团炸开的火花：外面一圈深青蓝色的尖刺，里面是**亮柠檬黄绿色**的头发），前额有黄绿和深蓝的刘海，两侧垂下黄绿色的发丝；**小麦色皮肤**，**黄绿色的大眼睛**，左脸颊上一块小创可贴。
> - **身体和衣服**：一件**宽大的青蓝色长外套**（衣摆到大腿，袖子宽大、卷到小臂，领口和下摆有银色金属扣，胸前一根**发亮的银色管子**连到背后的电池背包）；外套里是**黄色吊带背心**，胸前一道**洋红 + 绿色的闪电图案**；腰上一条红棕色皮带；**深紫红色紧身裤**，一边膝盖上有一块圆形护膝；**棕色短靴 + 橙色袜口**；一只手戴**紫红色的半指手套**。
> - **武器**：一把**电击步枪**（柠檬黄 + 橙色的枪身、深色金属零件、枪口有小电极），长度大约和她的上身一样；背后露出一点电池背包（黄色发光的电池）。
> - **姿势**（附图 1、2 / 8）：3/4 正面朝右站立。A：枪竖着举在画面右侧的肩旁、枪口朝上，另一只手自然垂下；B：两手把枪平端在腰前、枪口朝画面右边，两腿分开。**脸、两只手都不能被挡住**，枪和外套不能盖住手。
> - **风格和比例照附图 9–11**（之前让你画的萨勒芬妮、莎弥拉、辛德拉）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（发髻、黄绿色眼睛、脸在小尺寸下要看得出来）；**两个尖刺发髻可以比模型小一点**（每个大约和她的脸一样大），不然一帧太宽太高；外套、枪都要收得紧凑。颜色要分得开：**外套青蓝（亮青高光 + 深蓝暗部），头发柠檬黄绿 + 深青蓝尖刺，背心是暖黄色，裤子深紫红，靴子棕色，枪身柠檬黄 + 橙色，皮肤暖小麦色**。
> - **画布用横版 1536×1024**：A 从发髻尖到鞋底约 760 px，B 约 740 px；发髻、枪、手都在画面里，不能出画。
> - 不画任何特效（电光、火花、子弹第 3 步再单独画）；**鞋底是最低点**，平平地落在一条地面线上。
> - 交付：`outputs/zeri-picture/zeri-model-A.png`、`outputs/zeri-picture/zeri-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `zeri_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_zeri_league_front.png` | 英雄联盟原版泽丽待机，3/4 朝右 | 颜色、形状、A 的姿势 |
| `refs/2_zeri_league_frontal.png` | 同一帧，正面 | 外套、背心、裤子、靴子 |
| `refs/3_zeri_league_head.png` | 头的特写 | 尖刺发髻、黄绿眼睛、创可贴 |
| `refs/4_zeri_league_back.png` | 同一帧的背后 | 外套背面、电池背包 |
| `refs/5_zeri_splash.png` | 官方加载画面 | 气质（活泼、自信、带电） |
| `refs/6_zeri_league_run.png` | 英雄联盟里她跑动的几个瞬间 | 腿和外套怎么动 |
| `refs/7_zeri_league_actions.png` | 普攻、Q、W、E、大招的瞬间 | 手和枪怎么动 |
| `refs/8_zeri_league_shooting.png` | Q 电火迸射的射击站姿 | **B 的姿势** |
| `style/9_style_seraphine.png` | 你之前的萨勒芬妮像素图 | **只看风格**（少女） |
| `style/10_style_samira.png` | 你之前的莎弥拉像素图 | **只看风格**（拿枪的射手） |
| `style/11_style_syndra.png` | 你之前的辛德拉像素图 | **只看风格**（最近通过） |

## 提示词 A：`zeri-model-A.png`（枪竖着举在肩旁）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture; 2 the same from the front: the jacket, the tank top, the leggings and the boots; 3 the head close-up: the spiky hair buns, the yellow-green eyes and the plaster on her cheek; 4 the same pose from behind: the back of the jacket and the battery backpack; 5 the official illustration: her mood; 6 moments of her running: how the legs and the jacket move; 7 moments of her attack and spells: how the hands and the rifle move; 8 the shooting stance - not used in this version). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 11 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 760 px from the tips of the hair buns to the soles of her boots, centred, comfortable transparent margins, nothing cut off (the hair buns, the hands and the rifle inside the picture).
The character: Zeri, the Spark of Zaun, a lively, confident street girl crackling with electricity. HEAD: two big SPIKY HAIR BUNS on top of her head like bursting sparks - an outer ring of dark teal-blue spikes around bright LIME YELLOW-GREEN hair; lime and dark blue bangs, lime strands falling at both sides; warm tan skin, big YELLOW-GREEN EYES, a small plaster on her left cheek. BODY: an OVERSIZED TEAL-BLUE COAT reaching her thighs, wide sleeves rolled to the forearms, silver metal clasps on the collar and hem, a glowing SILVER TUBE across her chest running to the battery backpack on her back; under it a YELLOW TANK TOP with a magenta-and-green LIGHTNING print; a red-brown leather belt; tight DARK MAROON LEGGINGS with a round knee pad on one knee; BROWN ANKLE BOOTS with orange socks; a maroon fingerless glove on one hand. WEAPON: an ELECTRIC RIFLE, lime yellow and orange body, dark metal parts, small electrodes at the muzzle, about as long as her upper body; a bit of the glowing yellow battery backpack shows behind her shoulder.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the hair buns, the yellow-green eyes and the face drawn a little oversized so they read at small size), a slim body. The hair buns may be a little smaller than in the model (each about the size of her face) so the figure is not too wide or tall. Keep the figure COMPACT: the coat, the arms and the rifle close to her body. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands.
Pose: League's idle (images 1 and 2): standing, facing image right, the RIFLE HELD UPRIGHT beside her image-RIGHT shoulder, muzzle pointing up, her hand on its grip; the other arm hanging relaxed at her side; legs slightly apart. The soles of her boots are the lowest thing in the picture, on one ground line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the coat teal-blue with bright cyan highlights and deep blue shadows, the hair lime yellow-green with dark teal spikes, the tank top warm yellow, the leggings dark maroon, the boots brown, the rifle lime yellow and orange, the skin warm tan; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no lightning, no sparks, no bullets, no energy, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`zeri-model-B.png`（射击站姿，枪平端在腰前）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - her look, but with the pose of image 8; 2 the same from the front: the jacket, the tank top, the leggings and the boots; 3 the head close-up: the spiky hair buns, the yellow-green eyes and the plaster on her cheek; 4 the same pose from behind: the back of the jacket and the battery backpack; 5 the official illustration: her mood; 6 moments of her running: how the legs and the jacket move; 7 moments of her attack and spells: how the hands and the rifle move; 8 THE SHOOTING STANCE - the pose of this picture). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 11 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 740 px from the tips of the hair buns to the soles of her boots, centred, comfortable transparent margins, nothing cut off (the hair buns, the hands and the rifle inside the picture).
The character: Zeri, the Spark of Zaun, a lively, confident street girl crackling with electricity. HEAD: two big SPIKY HAIR BUNS on top of her head like bursting sparks - an outer ring of dark teal-blue spikes around bright LIME YELLOW-GREEN hair; lime and dark blue bangs, lime strands falling at both sides; warm tan skin, big YELLOW-GREEN EYES, a small plaster on her left cheek. BODY: an OVERSIZED TEAL-BLUE COAT reaching her thighs, wide sleeves rolled to the forearms, silver metal clasps on the collar and hem, a glowing SILVER TUBE across her chest running to the battery backpack on her back; under it a YELLOW TANK TOP with a magenta-and-green LIGHTNING print; a red-brown leather belt; tight DARK MAROON LEGGINGS with a round knee pad on one knee; BROWN ANKLE BOOTS with orange socks; a maroon fingerless glove on one hand. WEAPON: an ELECTRIC RIFLE, lime yellow and orange body, dark metal parts, small electrodes at the muzzle, about as long as her upper body; a bit of the glowing yellow battery backpack shows behind her shoulder.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the hair buns, the yellow-green eyes and the face drawn a little oversized so they read at small size), a slim body. The hair buns may be a little smaller than in the model (each about the size of her face) so the figure is not too wide or tall. Keep the figure COMPACT: the coat, the arms and the rifle close to her body. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands.
Pose: the shooting stance (image 8): standing, facing image right, BOTH HANDS HOLDING THE RIFLE LEVEL AT HER HIP, the muzzle pointing to image RIGHT (forward), the rifle in front of her body but not covering her face or hands; legs apart, firmly planted. The soles of her boots are the lowest thing in the picture, on one ground line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the coat teal-blue with bright cyan highlights and deep blue shadows, the hair lime yellow-green with dark teal spikes, the tank top warm yellow, the leggings dark maroon, the boots brown, the rifle lime yellow and orange, the skin warm tan; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no lightning, no sparks, no bullets, no energy, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物、发髻、枪、双手都完整。
- 两个尖刺发髻（深青蓝尖刺 + 柠檬黄绿头发）、黄绿色大眼睛、小麦色皮肤、脸颊创可贴。
- 宽大的青蓝外套（银扣、胸前发亮的管子）、黄色背心（洋红绿闪电）、红棕皮带、深紫红紧身裤 + 护膝、棕色短靴 + 橙色袜口、紫红半指手套。
- 柠檬黄 + 橙色的电击步枪；背后露一点电池背包。
- A：枪竖着举在画面右侧的肩旁、枪口朝上，另一只手垂下；B：枪平端在腰前、枪口朝右，两腿分开。
- 脸和两只手没被挡住；整体紧凑（发髻不要太大）。
- 鞋底是最低点，落在一条水平线上；没有任何电光或特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变；青蓝、黄绿、黄、紫红几种颜色分得开。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/zeri-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/zeri/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40–42 行，从发髻尖到鞋底算）。
- 技能动作里手臂 + 枪是一整块转动的部件（只做 90° 整转 / 翻转）；施法身体 = 待机身体，手不能藏起来；子弹、电光都是特效（第 3 步）。
