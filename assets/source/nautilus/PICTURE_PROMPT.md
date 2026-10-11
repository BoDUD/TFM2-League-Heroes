# 诺提勒斯：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 诺提勒斯还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**那只大铁锚的位置**，潜水服、头盔、锁链、锚完全一样：**A = 英雄联盟里的待机：大锚背在背上，锚冠在头盔后上方、两只锚爪像拱门一样弯在他头顶两侧**（附图 1、2、4）；**B = 英雄联盟的第四个待机：大锚竖着立在他身前的地上（锚爪朝下着地、锚环朝上），近侧的手扶着锚杆**（附图 8），人物更矮更紧凑。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 38–42 行）。
> - **长相照英雄联盟原版**（附图 1–8）：深海泰坦诺提勒斯，一个穿着**古老锈蚀的铜色潜水服**的巨人，沉默、厚重、可靠。**没有脸**：头是一个**圆圆的铜色潜水头盔**，和胸甲连成一整块（没有脖子），头盔顶上**三个小黑圆孔**，前面一道**黑色的观察窗缝**，里面是**两只发红橙光的方眼睛**；头盔下半是**一块厚厚的方形铜护颌**；头盔后面一根**弯弯的铜管**从头顶连到背后。
> - **身体**：**矮壮、驼背、肩很宽**，上身特别大、腿短粗。**锈铜色的大块胸甲和肩甲**（铜褐色、带一点铜绿锈斑和铆钉），**胸甲边缘和腰上有发光的海绿色（青绿）缝线**，像潜水服里透出来的光；两条粗胳膊是**深灰黑的厚橡胶潜水服**，套着**铜护臂**，**大大的深灰手套**；腰下是深色的潜水服短裤、**铜色护膝**；脚是**很大的铜底潜水靴（铜褐色厚鞋底）**。
> - **锁链和锚**：**一条粗大的灰铁锁链**绕在近侧前臂上、垂下来连到锚环；**大锚**是**灰色的石铁质地**，和他差不多高：一根粗锚杆（杆上一圈**红色的箍**、几圈**棕色的绳子**缠着），顶上一个**大圆锚环**，底下是**很宽的锚冠**（中间刻着一个**浅色的箭头/三叉花纹**），两边**弯钩状的锚爪**，爪尖很锋利。
> - **姿势**（附图 1、2、4 = A；附图 8 = B）：3/4 正面朝右，身体前倾、驼背、两腿岔开稳稳地站着，**两只脚都踩在地面线上**。A：锚斜背在背上，锚杆从他远侧肩膀后面斜向上，锚冠和两只锚爪在头盔后上方像拱门一样弯过来（一只爪尖在头盔左上、一只在右上，**不能遮住观察窗和眼睛**）；近侧手握着垂下来的锁链。B：大锚立在他身前右侧的地上，锚爪着地、锚环朝上齐他胸口，近侧手扶着锚杆上端；远侧手握拳垂在身旁（**不要举手**）。**观察窗、两只红眼和两只手都不能被挡住**。
> - **风格和比例照附图 9–11**（之前让你画的佛耶戈、派克、阿利斯塔）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头盔已经很大，**不要再放大**，按原版比例（头盔约占身高 1/3）；**整体收紧凑，不要画成巨大的块**（游戏里他和其他英雄差不多大）。颜色：**头盔和铠甲是锈铜褐（亮部偏橙铜、暗部深棕），潜水服是深灰黑，缝线是发光的海绿色，眼睛是红橙色，锚和锁链是冷灰色（锚上一圈红箍、棕绳）**；深色部分之间要有清楚的亮边，不要糊成一团黑。
> - **画布用横版 1536×1024**：从头盔顶到脚底约 560 px（A 的锚爪会比头盔高很多，留足边距）；锚、锁链都在画面里，不能出画。
> - 不画任何特效（水花、冲击波、漩涡、护盾第 3 步再单独画）；脚底是最低点，平平地落在一条地面线上（游戏在脚下画血条）；B 的锚爪着地，**也不能低于这条线**。
> - 交付：`outputs/nautilus-picture/nautilus-model-A.png`、`outputs/nautilus-picture/nautilus-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `nautilus_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_nautilus_league_front.png` | 英雄联盟原版诺提勒斯待机，3/4 朝右 | 颜色、形状、A 的姿势（锚背在背上） |
| `refs/2_nautilus_league_frontal.png` | 同一帧，正面 | 头盔的观察窗和红眼、胸甲、发光缝线、锁链 |
| `refs/3_nautilus_league_head.png` | 头盔和上身的特写 | 头盔顶上的三个孔、观察窗、护颌、铜管、锈斑 |
| `refs/4_nautilus_league_back.png` | 同一帧的背后 | 锚怎么背在背上 |
| `refs/5_nautilus_splash.png` | 官方加载画面 | 气质（沉重、深海、锈蚀） |
| `refs/6_nautilus_league_run.png` | 英雄联盟里他跑动的几个瞬间 | 背着锚怎么走 |
| `refs/7_nautilus_league_actions.png` | 普攻、Q 抛锚、E、大招的瞬间 | 手、锁链和锚怎么动 |
| `refs/8_nautilus_league_idle4.png` | 第四个待机：锚立在身前地上 | **B 的锚的位置**（他举起的那只手 B 里不要） |
| `style/9_style_viego.png` | 你之前的佛耶戈像素图 | **只看风格**（最近通过的一张） |
| `style/10_style_pyke.png` | 你之前的派克像素图 | **只看风格**（同是比尔吉沃特深海主题） |
| `style/11_style_alistar.png` | 你之前的阿利斯塔像素图 | **只看风格**（同是坦克辅助） |

## 提示词 A：`nautilus-model-A.png`（锚背在背上）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture, the anchor carried on his back; 2 the same from the front: the helmet's viewing slit with the red eyes, the chest plate, the glowing seams, the chain; 3 the helmet and upper body close-up: the three holes on top of the helmet, the slit, the jaw guard, the bent pipe, the rust; 4 the same pose from behind: how the anchor sits on his back; 5 the official illustration: his mood; 6 moments of him running; 7 moments of his attack and spells: how the hands, the chain and the anchor move; 8 his fourth idle with the anchor planted on the ground - not used in this version). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, image 10 the same sea-and-harbour theme, image 11 another tank).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 560 px from the top of his helmet to the soles of his feet, centred, comfortable transparent margins, nothing cut off (the whole anchor, both flukes and the chain inside the picture).
The character: Nautilus, the Titan of the Depths, a silent, heavy giant in an ancient RUSTED BRONZE DIVING SUIT. NO FACE: his head is a ROUND BRONZE DIVING HELMET fused with the chest plate (no neck), THREE SMALL BLACK ROUND HOLES on top, a BLACK VIEWING SLIT in front with TWO GLOWING RED-ORANGE SQUARE EYES inside, a THICK SQUARE BRONZE JAW GUARD below the slit, and a BENT BRONZE PIPE from the top of the helmet down to his back. BODY: short, stocky and HUNCHED, very broad shoulders, a huge upper body on short thick legs; big RUSTED BRONZE CHEST AND SHOULDER PLATES (copper-brown with a little green patina and rivets) with GLOWING SEA-GREEN SEAMS along the chest plate's edge and at the waist, like light from inside the suit; thick arms in DARK GREY-BLACK RUBBER diving suit with bronze bracers and BIG DARK GREY GLOVES; dark suit shorts, bronze knee guards, and HUGE DIVING BOOTS with thick bronze-brown soles. CHAIN AND ANCHOR: a THICK GREY IRON CHAIN wound round his near forearm, hanging down; the ANCHOR is GREY STONE-IRON and about as tall as he is: a thick shank with a RED BAND and a few turns of BROWN ROPE, a BIG ROUND RING at its top, a very wide CROWN at the bottom carved with a pale arrow-like trident emblem, and two HOOKED FLUKES with sharp points. Here the anchor is CARRIED ON HIS BACK (images 1, 2 and 4): the shank slants up behind his far shoulder and the crown with its two flukes ARCHES OVER THE BACK OF HIS HELMET like a gate, one fluke tip above each side of the helmet - never covering the viewing slit or the eyes; his near hand holds the hanging chain.
Proportions: game-sprite proportions like images 9-11; the helmet is already big - do NOT enlarge it further, keep the game's proportions (the helmet about a third of his height). Keep the whole figure COMPACT, not a giant block. 3/4 FRONT view facing image right, the helmet's slit turned toward the viewer, nothing covers the slit, the eyes or the hands.
Pose: League's own idle (images 1 and 2): leaning forward, hunched, legs apart, both feet planted firmly. The soles of his feet are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the helmet and armour a rusty bronze-brown (orange-copper highlights, dark brown shadows), the suit dark grey-black, the seams glowing sea-green, the eyes red-orange, the anchor and the chain a cool grey with the red band and brown rope; the dark parts separated by clear light edges, never one black blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no water, no splashes, no shockwaves, no shield, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`nautilus-model-B.png`（锚立在身前地上）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look of this picture; 2 the same from the front: the helmet's viewing slit with the red eyes, the chest plate, the glowing seams, the chain; 3 the helmet and upper body close-up: the three holes on top of the helmet, the slit, the jaw guard, the bent pipe, the rust; 4 the same from behind; 5 the official illustration: his mood; 6 moments of him running; 7 moments of his attack and spells: how the hands, the chain and the anchor move; 8 HIS FOURTH IDLE WITH THE ANCHOR PLANTED UPRIGHT ON THE GROUND IN FRONT OF HIM - the anchor position of this picture, but NOT his raised arm). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, image 10 the same sea-and-harbour theme, image 11 another tank).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 560 px from the top of his helmet to the soles of his feet, centred, comfortable transparent margins, nothing cut off (the whole anchor, both flukes and the chain inside the picture).
The character: Nautilus, the Titan of the Depths, a silent, heavy giant in an ancient RUSTED BRONZE DIVING SUIT. NO FACE: his head is a ROUND BRONZE DIVING HELMET fused with the chest plate (no neck), THREE SMALL BLACK ROUND HOLES on top, a BLACK VIEWING SLIT in front with TWO GLOWING RED-ORANGE SQUARE EYES inside, a THICK SQUARE BRONZE JAW GUARD below the slit, and a BENT BRONZE PIPE from the top of the helmet down to his back. BODY: short, stocky and HUNCHED, very broad shoulders, a huge upper body on short thick legs; big RUSTED BRONZE CHEST AND SHOULDER PLATES (copper-brown with a little green patina and rivets) with GLOWING SEA-GREEN SEAMS along the chest plate's edge and at the waist, like light from inside the suit; thick arms in DARK GREY-BLACK RUBBER diving suit with bronze bracers and BIG DARK GREY GLOVES; dark suit shorts, bronze knee guards, and HUGE DIVING BOOTS with thick bronze-brown soles. CHAIN AND ANCHOR: a THICK GREY IRON CHAIN wound round his near forearm, running to the anchor's ring; the ANCHOR is GREY STONE-IRON and about as tall as he is: a thick shank with a RED BAND and a few turns of BROWN ROPE, a BIG ROUND RING at its top, a very wide CROWN at the bottom carved with a pale arrow-like trident emblem, and two HOOKED FLUKES with sharp points. Here the anchor STANDS UPRIGHT ON THE GROUND IN FRONT OF HIM, a little to the image's right (image 8): its crown and flukes resting on the ground line, the ring up at the height of his chest, his near hand resting on the top of the shank; his far hand a fist hanging at his side (NOT raised).
Proportions: game-sprite proportions like images 9-11; the helmet is already big - do NOT enlarge it further, keep the game's proportions (the helmet about a third of his height). Keep the whole figure COMPACT, not a giant block. 3/4 FRONT view facing image right, the helmet's slit turned toward the viewer, nothing covers the slit, the eyes or the hands.
Pose: League's fourth idle without the raised arm (image 8): leaning forward, hunched, legs apart, both feet planted firmly, the anchor beside his front foot. The soles of his feet and the anchor's flukes are the lowest things in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the helmet and armour a rusty bronze-brown (orange-copper highlights, dark brown shadows), the suit dark grey-black, the seams glowing sea-green, the eyes red-orange, the anchor and the chain a cool grey with the red band and brown rope; the dark parts separated by clear light edges, never one black blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no water, no splashes, no shockwaves, no shield, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物、整只锚（锚环、两只锚爪）和锁链都完整。
- 圆铜头盔：顶上三个小孔、黑色观察窗里**两只红橙色发光的方眼睛**、方形护颌、后面的弯铜管；没有脖子，头盔和胸甲连成一块。
- 锈铜色胸甲肩甲（带铆钉、一点铜绿）、**发光的海绿色缝线**、深灰黑潜水服胳膊、大手套、铜护膝、厚底大潜水靴；矮壮驼背、肩很宽。
- 粗灰铁锁链绕在近侧前臂；灰色石铁大锚：红箍、棕绳、大圆环、刻纹锚冠、两只弯钩锚爪。A 背在背上、锚爪在头盔后上方拱起；B 立在身前地上、近侧手扶锚杆、远侧手握拳垂下。
- 观察窗、红眼和两只手没被挡住；深色部分之间有亮边，不糊成一团黑；整体紧凑，头盔不要比原版更大。
- 脚底是最低点，落在一条水平线上；B 的锚爪也落在这条线上，不低于它；没有任何特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/nautilus-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/nautilus/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 38–42 行，按头盔顶到脚底算；锚另算，A 的锚爪高出头盔的部分要限制，模型不能过大）。
- 技能动作里锚、锁链和握锚的手是一整块部件，只做平移和 90° 整转，不按任意角度转；施法身体 = 待机身体，手不能藏起来。
