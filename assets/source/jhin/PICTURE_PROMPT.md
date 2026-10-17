# 烬：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 烬还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（站得笔直放松，远侧的金色机械手握拳搭在腰间垂着的手杖枪顶上，近侧手提着手炮「低语」枪口朝下）；**B = 戏剧化的举枪**（近侧手把「低语」高举在面具旁边、枪口朝上，远侧金手张开在肩旁，像谢幕前的亮相，接近官方原画）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵。
> - **长相照英雄联盟原版**（附图 1–5）：整张脸被一副**白色带浅蓝阴影的瓷面具**盖住——刻出来的严肃面孔：浓眉骨、两道细长的**眯眼缝**、高颧骨、挺直的鼻子、一张往下撇的小嘴、尖下巴；头顶和后脑包着**深紫蓝色的紧头套**；脖子一圈**高高的品红色立领**一直到下巴。
> - **衣服**：一件**米白色大披风**（淡淡的金棕色漩涡花纹），搭在远侧肩上（比肩稍高）、从胸前垂到胯部，领口一枚**镶绿宝石的金扣**；里面是深红紫色马甲，身后一条**紫红色长衬里**垂到膝盖；两肩各有一个**金色尖刺肩甲**；**远侧手臂是整条金色铠甲机械臂**（金铜色甲片、金手指），**近侧手臂是裸露的肤色手臂**加深紫护腕；深紫色长裤；膝盖以下是**金铜色金属腿撑**（圆形膝关节、细杆小腿、像蹄子一样带爪的金属鞋）。
> - **两把枪都是他的标志道具，必须画清楚**：**「低语」**——一把华丽的长管手炮，深铁灰枪身、方形弹膛、长枪管，枪身上有卷曲的**金色花饰**，**象牙白的长弯握把**；**手杖枪**——一根笔直细长的手杖兼步枪，深钢色杆身、一段**青绿色布缠**、几道**金环**、顶上金色弯把手，下端挂一个小小的**品红色流苏**（以后每个动作都要看得到这两把枪，而且要直）。
> - **风格和比例照附图 7–9**（你之前让 Codex 画的瑞兹、乐芙兰、凯特琳）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（面具加头套约占身高 28–30%），但他仍然是**最高最瘦**的体型：披风下窄肩、细长腿。白面具和米白披风是最亮的部分，金色机械臂、腿撑、枪上花饰和金扣用亮金色，一点亮绿宝石。
> - 不画枪口火光、烟、子弹、莲花花瓣等任何特效（特效第 3 步再单独画）；脚底是最低点，衬里下摆、流苏和两把枪都不能低于脚底线（游戏在脚下画血条）。
> - 交付：`outputs/jhin-model-A.png`、`outputs/jhin-model-B.png`（1024×1536，真透明背景，人物约 1150 px 高），附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**写一个 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_jhin_league_front.png` | 英雄联盟原版烬，待机第一帧，3/4 正面朝右 | 服装、颜色、A 的姿势 |
| `refs/2_jhin_league_side.png` | 同一帧，更侧一点 | 金色机械手搭在手杖枪上、近侧手提着「低语」 |
| `refs/3_jhin_league_head.png` | 头部特写 | 瓷面具（眯眼缝、眉骨、下撇的嘴）、头套、品红立领、绿宝石金扣 |
| `refs/4_jhin_league_back.png` | 背面 | 披风和紫红衬里、腰间的手杖枪 |
| `refs/5_jhin_league_poseB.png` | 举枪：「低语」举在面具旁，金手张开 | B 的姿势、「低语」的样子 |
| `refs/6_jhin_splash.png` | 官方加载画面 | **看气氛和面具**（举枪的样子） |
| `style/7_style_ryze.png` | 你之前的瑞兹像素图 | **只看风格**（男性角色、金色镶边的画法） |
| `style/8_style_leblanc.png` | 你之前的乐芙兰像素图 | **只看风格**（披风、红色布料、金色镶边） |
| `style/9_style_caitlyn.png` | 你之前的凯特琳像素图 | **只看风格**（长枪怎么画） |

## 提示词 A：`jhin-model-A.png`（英雄联盟待机：金手搭在手杖枪上，「低语」垂在近侧手里）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 the full figure 3/4 front; 2 the same pose seen more from the side: the golden arm on the cane-rifle and Whisper; 3 the head close-up: the porcelain mask, the hood cap, the collar and the brooch; 4 a back view: the cape and the cloak lining; 5 the theatrical pose with Whisper raised; 6 the official illustration, for the mood and the mask). Copy from them the costume, the colours, the mask and both guns - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (image 9 also shows how a long gun is drawn).
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1150 px tall from the highest point to the soles, centred, comfortable transparent margins.
The character: Jhin, the Virtuoso: a tall, slender, theatrical gunman, an artist-killer who treats every shot as a performance. HEAD: his whole face is hidden by a smooth PORCELAIN MASK, white with cool pale-blue shading, sculpted like a stern face: a heavy brow ridge, two narrow carved EYE SLITS that read as calm half-closed eyes (dark slits with a tiny pale glint), high cheekbones, a long straight nose and a small carved frowning mouth, a pointed chin; the back and top of his head are covered by a tight DARK NAVY-PURPLE hood cap; a high CRIMSON-MAGENTA COLLAR stands around his neck up to the jaw. OUTFIT: a big CREAM-IVORY CAPE with faint gold-tan swirl patterns, draped over his FAR shoulder (rising a little above it) and hanging down over his chest to the hips, fastened at the throat by a small GOLD brooch with a GREEN gem; under it a crimson-purple vest; a long PURPLE-CRIMSON cloak lining hangs behind him down to the knees; small GOLD spiked pauldron tips at both shoulders; his FAR arm is a full GOLD ARMOURED ARM (bronze-gold plates, jointed gold fingers); his NEAR arm is bare tan skin with a dark purple wrist guard; dark plum-purple trousers; from the knees down GOLD-BRONZE metal LEG BRACES (round knee joints, slim rod shins, clawed hoof-like metal shoes). WEAPONS (his signature props, both must be clearly seen): WHISPER, an ornate long-barrelled HAND CANNON - a dark gunmetal body with a boxy chamber and a long barrel, curled GOLD scroll ornaments along it, and a long curved IVORY grip; and his CANE-RIFLE, a slim straight walking cane that is also a rifle - a dark steel shaft with a TEAL cloth-wrapped section and GOLD rings, a gold curled handle on top, a small MAGENTA tassel hanging from its lower end.
Proportions: game-sprite proportions like images 7 and 8 - a bigger head than in the 3D model (the masked head with its hood about 28-30% of his height), but he stays the TALLEST and SLIMMEST of these characters: narrow shoulders under the cape, long thin legs, the guns a little oversized so they read at small size. 3/4 FRONT view facing image right, the mask turned toward the viewer, BOTH eye slits visible, level and the same size, nothing covering the mask (both guns stay beside the body, never in front of the face).
Pose: League's own idle (images 1 and 2): he stands upright and relaxed, body in 3/4 view facing image right, weight on the back leg; his FAR (golden) arm is bent at the elbow, the gold fist resting on the top of the CANE-RIFLE, which hangs straight down at his far hip (its lower end at mid-shin, well above the soles); his NEAR arm hangs down holding WHISPER by its ivory grip, the hand cannon pointing at the ground beside his near thigh; the cape falls over his far shoulder and down his front; his masked face turned toward the viewer. The soles are the lowest thing in the picture: the cloak lining, the tassel and both guns end AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: deep plum for the trousers and the hood cap, dark crimson for the collar and the lining, dark bronze for the gold, never black fill - black is only the outline); lit edges and bright highlights: the white mask and the ivory cape are the brightest areas, bright gold on the armoured arm, the leg braces, the gun ornaments and the brooch, a small bright green gem; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No muzzle flash, no smoke, no bullets, no lotus petals, no magic effects, no background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 提示词 B：`jhin-model-B.png`（戏剧化举枪：「低语」举在面具旁、枪口朝上，金手张开在肩旁）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 the full figure 3/4 front; 2 the same pose seen more from the side: the golden arm on the cane-rifle and Whisper; 3 the head close-up: the porcelain mask, the hood cap, the collar and the brooch; 4 a back view: the cape and the cloak lining; 5 the theatrical pose with Whisper raised; 6 the official illustration, for the mood and the mask). Copy from them the costume, the colours, the mask and both guns - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (image 9 also shows how a long gun is drawn).
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1150 px tall from the highest point to the soles, centred, comfortable transparent margins.
The character: Jhin, the Virtuoso: a tall, slender, theatrical gunman, an artist-killer who treats every shot as a performance. HEAD: his whole face is hidden by a smooth PORCELAIN MASK, white with cool pale-blue shading, sculpted like a stern face: a heavy brow ridge, two narrow carved EYE SLITS that read as calm half-closed eyes (dark slits with a tiny pale glint), high cheekbones, a long straight nose and a small carved frowning mouth, a pointed chin; the back and top of his head are covered by a tight DARK NAVY-PURPLE hood cap; a high CRIMSON-MAGENTA COLLAR stands around his neck up to the jaw. OUTFIT: a big CREAM-IVORY CAPE with faint gold-tan swirl patterns, draped over his FAR shoulder (rising a little above it) and hanging down over his chest to the hips, fastened at the throat by a small GOLD brooch with a GREEN gem; under it a crimson-purple vest; a long PURPLE-CRIMSON cloak lining hangs behind him down to the knees; small GOLD spiked pauldron tips at both shoulders; his FAR arm is a full GOLD ARMOURED ARM (bronze-gold plates, jointed gold fingers); his NEAR arm is bare tan skin with a dark purple wrist guard; dark plum-purple trousers; from the knees down GOLD-BRONZE metal LEG BRACES (round knee joints, slim rod shins, clawed hoof-like metal shoes). WEAPONS (his signature props, both must be clearly seen): WHISPER, an ornate long-barrelled HAND CANNON - a dark gunmetal body with a boxy chamber and a long barrel, curled GOLD scroll ornaments along it, and a long curved IVORY grip; and his CANE-RIFLE, a slim straight walking cane that is also a rifle - a dark steel shaft with a TEAL cloth-wrapped section and GOLD rings, a gold curled handle on top, a small MAGENTA tassel hanging from its lower end.
Proportions: game-sprite proportions like images 7 and 8 - a bigger head than in the 3D model (the masked head with its hood about 28-30% of his height), but he stays the TALLEST and SLIMMEST of these characters: narrow shoulders under the cape, long thin legs, the guns a little oversized so they read at small size. 3/4 FRONT view facing image right, the mask turned toward the viewer, BOTH eye slits visible, level and the same size, nothing covering the mask (both guns stay beside the body, never in front of the face).
Pose: the theatrical pose (image 5, like the official art in image 6): he stands upright, body in 3/4 view facing image right; his NEAR hand raises WHISPER high beside his head, the barrel pointing straight up and the gun body beside the mask (never in front of the face); his FAR golden hand is lifted open beside his far shoulder, fingers spread like a showman's flourish; the CANE-RIFLE hangs straight at his far hip (its lower end at mid-shin); the cape as in image 5; his masked face turned toward the viewer. The soles are the lowest thing in the picture: the cloak lining, the tassel and both guns end AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: deep plum for the trousers and the hood cap, dark crimson for the collar and the lining, dark bronze for the gold, never black fill - black is only the outline); lit edges and bright highlights: the white mask and the ivory cape are the brightest areas, bright gold on the armoured arm, the leg braces, the gun ornaments and the brooch, a small bright green gem; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No muzzle flash, no smoke, no bullets, no lotus petals, no magic effects, no background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，枪口、枪托、手杖枪两端都没被切掉。
- 面具是白色瓷面具：两道眯眼缝都看得见、同一高度、一样大；面具没被枪或手挡住；头顶和后脑是深色头套；品红立领。
- 两把枪都清楚：「低语」是深铁灰枪身 + 金色花饰 + 象牙白握把的长管手炮；手杖枪是笔直的细杆（青绿布缠、金环、品红流苏）。
- 远侧手臂是金色机械臂，近侧是肤色手臂；膝盖以下是金色金属腿撑。
- 脚底是最低点，衬里、流苏和两把枪都不低于它；没有火光、烟、花瓣、光晕。
- 大像素块清楚，没有糊、没有柔光、没有渐变；米白披风和白面具不要画成一片死白（要有冷色阴影和描边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。
