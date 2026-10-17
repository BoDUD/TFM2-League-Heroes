# 维克托：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 维克托还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**背后那条机械臂的位置**，长相、面具、衣服、法杖完全一样：**A = 英雄联盟里的待机：机械臂从背后高高举过头顶，顶端的三叉金爪在头上方**（附图 1、2）；**B = 机械臂收在肩后，三叉金爪只比头顶高一点、靠在肩膀后面**（附图 8），人物整体更矮更紧凑。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40–42 行，和雷克顿、布兰德差不多高）。
> - **长相照英雄联盟原版**（附图 1–8，当前的奥术造型）：奥术先驱维克托，一个瘦高、冷静的海克斯科技发明家，半人半机械。**脸上是一张蓝灰色的金属长面具**，像细长的鸟喙一样往前下方伸，面具上有一道道竖纹，**两只眼睛发橙色的光**；**头顶一顶金色的尖角头冠**（中间一个高尖，两边弯角），头冠后面露出**一撮乱乱的棕色头发**。
> - **身体和衣服**：**身体是蓝灰色的**（皮肤和金属合在一起，有肌肉一样的分块纹路），胸口、腰、大腿上有**金色的铠甲片和金色纹饰**；脖子和肩膀上围着一条**宽大的蓝色披肩 / 围巾**，正面扣着一枚**圆形金色徽章**，披肩下面是一件**深红色的长斗篷**，从肩后一直拖到脚边，下摆是撕裂的尖角；小腿和脚踝套着**金色的环**，**赤脚**（深蓝灰色的脚）。
> - **法杖**：近侧（离我们近的那只）手握着一根**很长的深色扭曲法杖**，杖身是黑紫色、像缠绕的金属和根须，**顶端弯成两三个钩状的环**，有一点红色和金色；法杖从手里竖直往下，杖尾快到地面。
> - **机械臂**：从他背后伸出一条**细长的蓝灰色机械臂**（一节一节的），末端是**三根金色的弯爪围着一颗发青蓝光的圆核**（像三叉的金色钩子）。A：机械臂高高举起，金爪在头顶上方；B：机械臂弯折收在肩膀后面，金爪在肩头 / 后脑旁边，只比头顶高一点。
> - **姿势**（附图 1、2）：3/4 正面朝右，站得笔直、有点傲慢，近侧手竖握法杖，远侧手垂在身旁、手指微张（像要施法）；斗篷在身后自然垂下（他朝右，所以斗篷往**画面左边**飘一点）。**脸（面具）和两只手都不能被挡住**。
> - **风格和比例照附图 9–11**（之前让你画的雷克顿、布兰德、泽拉斯）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（面具、橙色眼睛、金色头冠在小尺寸下要看得出来）；他很瘦很高，**身体、法杖、斗篷都要收得紧凑**，不要比身体宽太多（游戏里一帧很小）。蓝灰色身体、蓝色披肩、蓝灰面具容易糊成一片：**身体用偏紫的蓝灰，披肩用更鲜亮的青蓝，面具用浅一点的钢蓝 + 白色高光，金饰用最亮的金色，斗篷是深红，眼睛是亮橙**。
> - **画布用横版 1536×1024**：A 从金爪顶到脚底约 820 px（人物本身从头冠到脚底约 640 px），B 从头冠 / 金爪顶到脚底约 720 px；法杖、斗篷、机械臂都在画面里，不能出画。
> - 不画任何特效（射线、重力场、风暴第 3 步再单独画）；脚底是最低点，平平地落在一条地面线上（游戏在脚下画血条），法杖尾巴和斗篷也不能低于这条线。
> - 交付：`outputs/viktor-picture/viktor-model-A.png`、`outputs/viktor-picture/viktor-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `viktor_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_viktor_league_front.png` | 英雄联盟原版维克托待机，3/4 朝右 | 颜色、形状、姿势、A 的机械臂 |
| `refs/2_viktor_league_frontal.png` | 同一帧，正面 | 胸口、腰、腿上的金色铠甲片，脚踝金环 |
| `refs/3_viktor_league_head.png` | 头和上身的特写 | 长喙面具、橙色眼睛、金色头冠、棕色头发、蓝色披肩 + 金徽章、机械臂的金爪 |
| `refs/4_viktor_league_back.png` | 同一帧的背后 | 斗篷、机械臂从背后伸出的位置 |
| `refs/5_viktor_splash.png` | 官方加载画面 | 气质（冷静、傲慢的发明家） |
| `refs/6_viktor_league_run.png` | 英雄联盟里他跑动的几个瞬间 | 斗篷怎么飘、法杖怎么拿 |
| `refs/7_viktor_league_actions.png` | 普攻、Q、W、E、大招的瞬间 | 手、法杖、机械臂怎么动 |
| `refs/8_viktor_league_arm_low.png` | 机械臂收在肩后的样子 | **B 的机械臂位置** |
| `style/9_style_renekton.png` | 你之前的雷克顿像素图 | **只看风格**（最近通过的一张） |
| `style/10_style_brand.png` | 你之前的布兰德像素图 | **只看风格**（中路法师） |
| `style/11_style_xerath.png` | 你之前的泽拉斯像素图 | **只看风格**（中路法师、蓝金配色） |

## 提示词 A：`viktor-model-A.png`（机械臂高举过头顶）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture, the mechanical arm raised high over his head; 2 the same from the front: the gold armour plates on the chest, waist and thighs, the gold rings at the ankles; 3 the head and upper body close-up: the beaked metal mask, the glowing orange eyes, the gold crown, the brown hair, the blue shawl with its gold medallion and the gold claw of the mechanical arm; 4 the same pose from behind: the cape and where the mechanical arm leaves his back; 5 the official illustration: his mood; 6 moments of him running: how the cape flows and how he holds the staff; 7 moments of his attack and spells: how the hands, the staff and the mechanical arm move; 8 the mechanical arm folded behind his shoulders - not used in this version). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 820 px from the top of the raised gold claw to the soles of his feet (the figure itself about 640 px from the crown to the soles), centred, comfortable transparent margins, nothing cut off (the claw, the staff and the cape inside the picture).
The character: Viktor, the Herald of the Arcane, a tall thin cold hextech inventor, half man half machine. HEAD: a long BLUE-GREY METAL MASK covering the face, narrow and beaked, pointing forward and down, with vertical grooves, TWO GLOWING ORANGE EYES; on top a GOLD SPIKED CROWN (one tall central spike, curved horns on both sides) with a tuft of messy BROWN HAIR behind it. BODY: slim, BLUE-GREY (skin and metal as one, with muscle-like segment lines), GOLD ARMOUR PLATES and gold filigree on the chest, waist and thighs; around the neck and shoulders a wide BRIGHT BLUE SHAWL fastened in front with a ROUND GOLD MEDALLION; under it a long DEEP CRIMSON CAPE falling from behind the shoulders to his feet, its hem torn into points; GOLD RINGS on the shins and ankles; BARE dark blue-grey feet. THE STAFF: in his near hand a very long DARK TWISTED STAFF (black-violet, like wound metal and roots) whose top curls into two or three hooked loops with touches of red and gold; held upright, its foot just above the ground. THE MECHANICAL ARM: a thin segmented blue-grey mechanical arm rising from his back, ending in THREE CURVED GOLD CLAWS around a GLOWING CYAN-BLUE CORE; here it is RAISED HIGH, the gold claw well above his head (images 1 and 2).
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the mask, the orange eyes and the gold crown drawn a little oversized so they read at small size), a tall slim body. Keep the figure COMPACT: the cape and the staff close to his body, nothing much wider than his shoulders. 3/4 FRONT view facing image right, the mask turned toward the viewer, nothing covers the mask or the hands.
Pose: League's own (images 1 and 2): standing straight and haughty, facing image right, the near hand holding the staff upright, the far arm hanging at his side with the fingers slightly open as if about to cast, the cape hanging behind him (toward image LEFT a little). The soles of his feet are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the staff's foot and the cape stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the body a violet-tinged blue-grey, the shawl a brighter cyan-blue, the mask a lighter steel blue with white highlights, the gold the brightest gold, the cape deep crimson, the eyes bright orange, the claw's core glowing cyan; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no laser, no lightning, no light rings, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`viktor-model-B.png`（机械臂收在肩后）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture, but with the mechanical arm folded as in image 8; 2 the same from the front: the gold armour plates on the chest, waist and thighs, the gold rings at the ankles; 3 the head and upper body close-up: the beaked metal mask, the glowing orange eyes, the gold crown, the brown hair, the blue shawl with its gold medallion and the gold claw of the mechanical arm; 4 the same pose from behind: the cape and where the mechanical arm leaves his back; 5 the official illustration: his mood; 6 moments of him running: how the cape flows and how he holds the staff; 7 moments of his attack and spells: how the hands, the staff and the mechanical arm move; 8 THE MECHANICAL ARM FOLDED BEHIND HIS SHOULDERS - the arm position of this picture). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 720 px from the top of the crown / gold claw to the soles of his feet, centred, comfortable transparent margins, nothing cut off (the claw, the staff and the cape inside the picture).
The character: Viktor, the Herald of the Arcane, a tall thin cold hextech inventor, half man half machine. HEAD: a long BLUE-GREY METAL MASK covering the face, narrow and beaked, pointing forward and down, with vertical grooves, TWO GLOWING ORANGE EYES; on top a GOLD SPIKED CROWN (one tall central spike, curved horns on both sides) with a tuft of messy BROWN HAIR behind it. BODY: slim, BLUE-GREY (skin and metal as one, with muscle-like segment lines), GOLD ARMOUR PLATES and gold filigree on the chest, waist and thighs; around the neck and shoulders a wide BRIGHT BLUE SHAWL fastened in front with a ROUND GOLD MEDALLION; under it a long DEEP CRIMSON CAPE falling from behind the shoulders to his feet, its hem torn into points; GOLD RINGS on the shins and ankles; BARE dark blue-grey feet. THE STAFF: in his near hand a very long DARK TWISTED STAFF (black-violet, like wound metal and roots) whose top curls into two or three hooked loops with touches of red and gold; held upright, its foot just above the ground. THE MECHANICAL ARM: a thin segmented blue-grey mechanical arm from his back, ending in THREE CURVED GOLD CLAWS around a GLOWING CYAN-BLUE CORE; here it is FOLDED close behind his shoulders (image 8): the gold claw sits beside the back of his head / above his far shoulder, only a little higher than the top of his crown.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the mask, the orange eyes and the gold crown drawn a little oversized so they read at small size), a tall slim body. Keep the figure COMPACT: the cape, the staff and the folded arm close to his body, nothing much wider than his shoulders. 3/4 FRONT view facing image right, the mask turned toward the viewer, nothing covers the mask or the hands.
Pose: League's own (images 1 and 2): standing straight and haughty, facing image right, the near hand holding the staff upright, the far arm hanging at his side with the fingers slightly open as if about to cast, the cape hanging behind him (toward image LEFT a little). The soles of his feet are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the staff's foot and the cape stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the body a violet-tinged blue-grey, the shawl a brighter cyan-blue, the mask a lighter steel blue with white highlights, the gold the brightest gold, the cape deep crimson, the eyes bright orange, the claw's core glowing cyan; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no laser, no lightning, no light rings, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物、法杖、斗篷、机械臂都完整。
- 蓝灰长喙金属面具 + **发光的橙色眼睛**、金色尖角头冠、后面一撮棕发。
- 蓝灰色身体 + 金色铠甲片、鲜亮的青蓝披肩 + 圆形金徽章、深红长斗篷（下摆撕裂）、小腿 / 脚踝金环、赤脚。
- 近侧手竖握深色扭曲长法杖（顶端几个钩环）；远侧手垂在身旁、手指微张。
- 机械臂：三根金爪围着青蓝光核。A 高举过头顶；B 收在肩后，只比头冠高一点。
- 面具和两只手没被挡住；整体紧凑，不比肩膀宽太多。
- 脚底是最低点，落在一条水平线上；法杖尾和斗篷不低于它；没有任何特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/viktor-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/viktor/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40–42 行；A 的机械臂会让每帧高很多——先给用户看取舍，行数按人物本身算还是按金爪顶算要说清楚）。
- 技能动作里机械臂和法杖都是整块转动的部件；施法身体 = 待机身体，手不能藏起来。
