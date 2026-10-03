# 基兰：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 基兰还没有原图。这一步请 Codex 画一张全身像素风原图。A、B 两版服装一样、背上都有大时钟，只差手上的东西：**A = 英雄联盟的待机**（悬浮在空中，两只手向两边张开、掌心向上，手里不拿东西）；**B = 拄着沙漏法杖**（近侧手握一根顶上是沙漏的长法杖，远侧手张开、掌心向上）。说明：英雄联盟现在的基兰模型手里**没有法杖**，他的道具是背在背上的大金色时钟（附图1–4）；B 版按「拄沙漏法杖」的说法加了一根，你挑哪版都行。之后第 1 步再按你挑的这版画游戏尺寸的精灵。
> - **长相照英雄联盟原版**（附图 1–6）：清瘦的老法师，长脸、大鼻子、额头皱纹、**尖耳朵**、浓眉；眼睛发着淡青色的光（提示词要求给眼睛点一个小瞳孔，游戏尺寸下才看得出是眼睛）；头发一绺一绺往上往后竖起、像蓝色火焰；**大长胡子**连着八字胡，往前飘、在胸前卷出去（附图 3）。头发和胡子照游戏模型是**蓝色**（亮处天蓝、中间蓝、暗处深海军蓝；官方原画里浅一些、偏银蓝），一定比长袍亮，看得出是老人的须发。
> - **衣服**：一直垂到脚踝的深炭灰色长袍、宽袖；下半身前片是浅一点的灰色、带小圆环花纹；下摆和袖口一圈**红色宽边**，上面印着深色的**钟表数字**；两条**红色长披带**从肩膀垂到身前，末端飘起；金色腰扣配一圈粗绳腰带；**光脚**，脚尖朝下（他是飘着的）。
> - **背上的大时钟**（他的标志道具，以后每个动作都要看得见）：比上半身还大的圆形钟面，象牙白底、**青色发光的数字**和一圈青色内环，外面一圈厚厚的**金色齿轮边框**（方齿、铆钉）；一根大大的**金色时针**从钟面往右上方伸出、越过远侧肩膀；旁边飘着两三个小金齿轮；钟下面挂着一个圆球**钟摆**（在袍子后面露出来）；钟顶上是一个小小的深色木头罩子、金边尖顶，高过他的头发。
> - **风格和比例照附图 7–9**（你之前让 Codex 画的瑞兹、乐芙兰、娑娜）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；大头（头发顶到下巴约占身高 30%，不算时钟和胡子）、修长的长袍身体；深色长袍要有亮边和高光，金色时钟、象牙钟面、青色数字、冰蓝色的发光点都要亮，发光的眼睛是脸上最亮的点。
> - 不画时间波纹、光效和任何特效（特效第 3 步再单独画）；脚尖是最低点，袍子下摆、钟摆和法杖都不能低于它（游戏在脚下画血条）。
> - 交付：`outputs/zilean-model-A.png`、`outputs/zilean-model-B.png`（1024×1536，真透明背景，人物连时钟约 1150 px 高），附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**写一个 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_zilean_league_front.png` | 英雄联盟原版基兰，待机第一帧，3/4 正面朝右 | 服装、颜色、A 的姿势 |
| `refs/2_zilean_league_side.png` | 同一帧，更侧一点 | 背上的时钟有多厚、钟摆、红披带 |
| `refs/3_zilean_league_head.png` | 头部特写 | 头发、胡子、尖耳朵、眉毛 |
| `refs/4_zilean_league_back.png` | 背面 | 钟面的数字、齿轮、时针、顶上的木罩子 |
| `refs/5_zilean_splash.png` | 官方加载画面 | 脸、头发和胡子（原画里偏银蓝，模型是蓝色，照模型） |
| `refs/6_zilean_icon.png` | 游戏头像 | 脸、发光的眼睛 |
| `style/7_style_ryze.png` | 你之前的瑞兹像素图 | **只看风格和比例**（同样是大胡子法师） |
| `style/8_style_leblanc.png` | 你之前的乐芙兰像素图 | **只看风格、竖着拿长杖的画法** |
| `style/9_style_sona.png` | 你之前的娑娜像素图 | **只看风格、长袍和镶边的画法** |

## 提示词 A：`zilean-model-A.png`（英雄联盟待机：悬浮，两手张开掌心向上，背着大时钟）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 full figure 3/4 front; 2 the same pose seen more from the side: the clock drum strapped on his back and the pendulum; 3 the head close-up: hair, beard, ears, eyes; 4 a back view: the clock face with its numerals, the gears, the clock hand and the wooden top; 5 the official illustration and 6 the game's portrait, for the face, the hair and the beard). Copy from them the costume, the colours, the hair, the beard and the clock - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style; image 7 (another bearded mage) also shows the proportions.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1150 px tall from the top of the clock to his toes, centred, comfortable transparent margins.
The character: Zilean, the Chronokeeper: an ancient, wise and slightly grumpy time MAGE, a thin old man who FLOATS a little above the ground. HEAD: a long narrow old face with tan skin, a big nose, deep frown lines, POINTED elf-like EARS, thick bushy eyebrows; his eyes GLOW pale cyan (give each eye a tiny dark pupil so it reads at small size); a tall mane of HAIR standing up and back in big spiky locks like blue flames, and a big LONG BEARD with a moustache that flows forward and curls out in front of his chest toward image right (image 3) - hair and beard BLUE as on the game model (bright sky-blue highlights, mid blue, deep navy shadows; the official art in image 5 shows them paler, silver-blue), always lighter than the robe so the old man's mane reads. OUTFIT: a long dark CHARCOAL-GREY robe with wide sleeves reaching down to his ankles; the front panel of the lower robe is lighter grey with a pattern of small grey RINGS; a wide RED band runs along the hem and the sleeve ends with dark CLOCK NUMERALS (1 2 3 ...) printed on it; a long RED stole/scarf hangs from both shoulders down the front, its ends fluttering; a GOLD belt buckle with a thick knotted rope belt; BARE FEET with tan skin, the toes pointing down as he hovers. THE CLOCK (his signature prop, worn on his back like a huge backpack, taller than his torso): a big round CLOCK FACE of pale ivory-white with glowing CYAN numerals and a cyan inner ring, framed by a thick polished GOLD gear rim with square teeth and rivets; a big golden CLOCK HAND (arrow) sticking out of it up and to the right past his far shoulder; two or three loose small golden GEARS floating beside it; a golden PENDULUM with a round bob hanging below the clock behind his robe; a little dark-wood housing with a gold-trimmed peaked top crowning the clock above his hair.
Proportions: a stylised chibi-leaning hero like image 7 - a BIG head (hair top to the tip of the chin, beard excluded, about 30% of his height without the clock), a slim body in the long robe, the hands and the clock a little oversized. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH glowing eyes visible, level and the same size, nothing covering the eyes (the bushy brows sit above them, the hair and the clock stay behind the head, the beard below the eyes). Show the whole clock: its round face must be seen behind him, not hidden by his body.
Pose: League's own idle (images 1 and 2): he hovers upright in 3/4 view facing image right, the robe hanging straight down to his dangling bare feet; BOTH arms held out to his sides at chest height, elbows bent, the palms OPEN and turned UP like a sage weighing time, the wide sleeves hanging from his forearms; the red stole flutters; the giant golden clock rises behind his back, its round face centred behind his head and shoulders and clearly larger than his torso, the clock hand pointing up-right, the small gears floating beside it, the pendulum bob peeking out below it behind his robe. His toes are the lowest thing in the picture: the robe's hem, the pendulum and anything he holds end AT OR ABOVE the line of his lowest toe (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: charcoal-blue greys for the robe, deep red for the trims, deep blue for the hair shadows, dark bronze for the clock's shadows - never black fill, black is only the outline); lit edges and bright highlights so the dark robe reads: light grey edges on the robe folds and sleeves, bright gold on the clock rim, the gears and the belt, the ivory clock face and its cyan numerals, the icy-blue lights in the hair and beard; the glowing eyes the brightest spots of the face; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects, no time ripples, no sparks, no background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 提示词 B：`zilean-model-B.png`（同样的服装和时钟，近侧手拄着沙漏法杖）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 full figure 3/4 front; 2 the same pose seen more from the side: the clock drum strapped on his back and the pendulum; 3 the head close-up: hair, beard, ears, eyes; 4 a back view: the clock face with its numerals, the gears, the clock hand and the wooden top; 5 the official illustration and 6 the game's portrait, for the face, the hair and the beard). Copy from them the costume, the colours, the hair, the beard and the clock - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style; image 7 (another bearded mage) also shows the proportions.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1150 px tall from the top of the clock to his toes, centred, comfortable transparent margins.
The character: Zilean, the Chronokeeper: an ancient, wise and slightly grumpy time MAGE, a thin old man who FLOATS a little above the ground. HEAD: a long narrow old face with tan skin, a big nose, deep frown lines, POINTED elf-like EARS, thick bushy eyebrows; his eyes GLOW pale cyan (give each eye a tiny dark pupil so it reads at small size); a tall mane of HAIR standing up and back in big spiky locks like blue flames, and a big LONG BEARD with a moustache that flows forward and curls out in front of his chest toward image right (image 3) - hair and beard BLUE as on the game model (bright sky-blue highlights, mid blue, deep navy shadows; the official art in image 5 shows them paler, silver-blue), always lighter than the robe so the old man's mane reads. OUTFIT: a long dark CHARCOAL-GREY robe with wide sleeves reaching down to his ankles; the front panel of the lower robe is lighter grey with a pattern of small grey RINGS; a wide RED band runs along the hem and the sleeve ends with dark CLOCK NUMERALS (1 2 3 ...) printed on it; a long RED stole/scarf hangs from both shoulders down the front, its ends fluttering; a GOLD belt buckle with a thick knotted rope belt; BARE FEET with tan skin, the toes pointing down as he hovers. THE CLOCK (his signature prop, worn on his back like a huge backpack, taller than his torso): a big round CLOCK FACE of pale ivory-white with glowing CYAN numerals and a cyan inner ring, framed by a thick polished GOLD gear rim with square teeth and rivets; a big golden CLOCK HAND (arrow) sticking out of it up and to the right past his far shoulder; two or three loose small golden GEARS floating beside it; a golden PENDULUM with a round bob hanging below the clock behind his robe; a little dark-wood housing with a gold-trimmed peaked top crowning the clock above his hair.
Proportions: a stylised chibi-leaning hero like image 7 - a BIG head (hair top to the tip of the chin, beard excluded, about 30% of his height without the clock), a slim body in the long robe, the hands and the clock a little oversized. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH glowing eyes visible, level and the same size, nothing covering the eyes (the bushy brows sit above them, the hair and the clock stay behind the head, the beard below the eyes). Show the whole clock: its round face must be seen behind him, not hidden by his body.
Pose: the same costume, the same giant golden clock on his back and the same hovering stance, but now he LEANS ON A STAFF: his NEAR hand grips a tall HOURGLASS STAFF held upright in front of his near side, its foot reaching the soles line beside his feet (never below it) and its head as high as his hair; the staff is dark polished wood with gold bands, crowned by a gold-framed HOURGLASS (two glass bulbs with glowing CYAN sand, a little cyan glow); his FAR arm is held out to the side at chest height, palm open and turned up as in League's idle. His toes are the lowest thing in the picture: the robe's hem, the pendulum and anything he holds end AT OR ABOVE the line of his lowest toe (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: charcoal-blue greys for the robe, deep red for the trims, deep blue for the hair shadows, dark bronze for the clock's shadows - never black fill, black is only the outline); lit edges and bright highlights so the dark robe reads: light grey edges on the robe folds and sleeves, bright gold on the clock rim, the gears and the belt, the ivory clock face and its cyan numerals, the icy-blue lights in the hair and beard; the glowing eyes the brightest spots of the face; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects, no time ripples, no sparks, no background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，时钟顶上的木罩子、时针尖和小齿轮都没被切掉。
- 两只发光的眼睛都看得见、同一高度、一样大；眉毛在眼睛上面，头发和时钟在头后面，胡子在眼睛下面，没有东西挡住眼睛。
- 背上的时钟清楚：圆钟面、青色数字、金色齿轮边框、往右上伸出的时针，钟面没被身体全挡住。
- 头发和胡子是亮一些的蓝色（不是深蓝一团），胡子长、在胸前卷出去；长袍深灰但看得出褶子和亮边，下摆的红边上有数字。
- 手是手：宽袖子里伸出掌心向上的手（B 版近侧手握住法杖），不是细黑线。
- 脚尖是最低点，袍子下摆、钟摆和法杖都不低于它；没有特效、光晕。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。
