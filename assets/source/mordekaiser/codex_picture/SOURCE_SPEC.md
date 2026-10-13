# 莫德凯撒（铁铠冥魂）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 莫德凯撒还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**角度**，人、盔甲、武器、颜色完全一样：**A = 英雄联盟里的待机，3/4 正面朝右**（附图 1）；**B = 同一个待机的正侧面，朝画面右边**（附图 9，侧脸、近侧肩膀在前、两腿一前一后、靴尖朝右）。这一版走**高清（PPU）**：你画的原图会直接读回当游戏里的高清造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–9）：莫德凯撒，一个**非常高大的亡灵铁甲巨人**，全身**黑铁色的尖刺重甲**（深灰带一点蓝绿的金属，亮部灰蓝、暗部近黑），**盔甲的缝隙里透出幽绿色的灵魂光**（胸口两块、上臂、腰、膝盖处，亮青绿色，全身最亮的颜色）。
> - **头**（附图 3 特写）：一顶**高高的尖刺头盔**，头盔顶上竖着**两根又高又尖的黑铁角**（像王冠），面甲是窄窄的一条缝，**缝里两只发光的青绿色眼睛**（要看得清）；看不到脸，整个头被盔甲包住。
> - **身体**：**两边肩膀是巨大的尖刺肩甲**（向两侧张开、边缘一排尖角）；胸甲厚重、中间一道尖角；**腰带下面垂着一块破烂的暗红色布**（下摆是撕裂的尖角），两侧是尖角的铁裙甲；**手是带爪子的铁手套**；**两条腿是粗壮的铁甲腿，膝盖有尖角护膝，脚上是厚重的铁靴**。整个人上宽下窄、像一座铁塔。
> - **武器「夜临」**：一把**巨大的长柄狼牙锤**——锤头是一块**黑铁的、四面都是尖刺的大锤头**，锤头中间一道**青绿色的发光裂纹**；长长的黑铁锤柄，**锤柄尾端挂着一小段铁链**。待机时他**单手把锤子扛在肩上**，锤头在头的后上方，锤柄斜着从肩膀伸出来（附图 1、9）。
> - **姿势**（A = 附图 1；B = 附图 9）：站得很稳，两腿分开，扛着锤子，另一只手垂在身旁、爪子微张。**头盔和两只绿眼睛不能被锤头、锤柄挡住**。B 是正侧面（朝右）：侧面的头盔、侧面的肩甲、两腿一前一后、靴尖朝右；锤子同样扛在肩上，锤头在背后上方，锤柄从肩膀往前伸。
> - **比例**：头按原版比例稍大一点就行（游戏里绿眼睛要看得清），**不要画成大头娃娃**；他是重甲巨人，肩膀很宽，比别的英雄壮一圈。参照附图 10–12 的风格（你之前画的卡萨丁、诺提勒斯、古拉加斯）。
> - **画布用竖版 1024×1536**：**从锤头顶（或头盔角尖）到靴底约 1250 px**，左右（锤头到锤柄尾的铁链）不超过 960 px，全部在画面里，不能出画；靴底平平地落在一条地面线上。
> - **像素块**：大小一致的方块，**每块约 8 像素**，横平竖直对齐成网格（这张图会被按格子读回成高清造型）；外轮廓一圈 1 块宽的近黑描边。
> - 不画任何特效（锤子砸地、黑暗光环、拉人的爪、大招的领域都在第 3 步再单独画；锤头裂纹的绿光和盔甲缝里的绿光是他身上的一部分，可以画，但只用平涂色块，不要发光晕）；不画地面和影子。
> - 交付：`outputs/mordekaiser-picture/mordekaiser-model-A.png`、`outputs/mordekaiser-picture/mordekaiser-model-B.png`（都是 1024×1536 竖版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `mordekaiser_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_mordekaiser_league_front.png` | 英雄联盟原版莫德凯撒待机，3/4 朝右 | 颜色、形状、**A 的角度** |
| `refs/2_mordekaiser_league_frontal.png` | 同一帧，正面 | 胸甲、两肩的尖刺肩甲、暗红色垂布、腿甲 |
| `refs/3_mordekaiser_league_head.png` | 头的特写 | 头盔两根高角、面甲的缝、两只绿眼睛、锤头 |
| `refs/4_mordekaiser_league_back.png` | 同一帧的背后 | 背后的盔甲、锤子扛在肩上的样子 |
| `refs/5_mordekaiser_splash.png` | 官方加载画面 | 气质（阴森、压迫感、亡灵的绿光） |
| `refs/6_mordekaiser_league_run.png` | 英雄联盟里他走动的几个瞬间 | 沉重地迈步 |
| `refs/7_mordekaiser_league_actions.png` | 普攻、Q 破灭之锤、E 断魂一扼、R 轮回绝境的瞬间 | 锤子怎么挥 |
| `refs/8_mordekaiser_league_side_b.png` | 待机，3/4 和侧面之间 | 角度过渡参考 |
| `refs/9_mordekaiser_league_side.png` | 待机的侧面（朝右） | **B 的角度** |
| `style/10_style_kassadin.png` | 你之前的卡萨丁像素图 | **只看风格**（最近通过的一张，同样走高清） |
| `style/11_style_nautilus.png` | 你之前的诺提勒斯像素图 | **只看风格**（重甲、扛着大武器） |
| `style/12_style_gragas.png` | 你之前的古拉加斯像素图 | **只看风格** |

## 提示词 A：`mordekaiser-model-A.png`（3/4 正面）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and the ANGLE of this picture; 2 the same from the front: the chest plate, the huge spiked pauldrons, the maroon cloth, the leg armour; 3 the head close-up: the helmet's two tall horns, the visor slit, the two green eyes, the mace head; 4 the same from behind: the back armour and how the mace rests on the shoulder; 5 the official illustration: his mood; 6 moments of him walking; 7 moments of his attack and spells; 8 the idle between 3/4 and side - not used in this version; 9 the idle from the side). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters: copy their pixel-art style (image 10 the latest approved picture of this series, image 11 a heavy armoured character carrying a big weapon on the shoulder, image 12 another approved picture).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 1250 px from the top of the mace head (or the helmet horns) to the soles and no more than 960 px wide, centred, comfortable transparent margins, nothing cut off, the soles level on one ground line.
The character: Mordekaiser, the Iron Revenant, a TOWERING UNDEAD WARLORD IN SPIKED BLACK IRON PLATE ARMOUR (dark gunmetal with a slight blue-green tint: grey-blue highlights, near-black shadows), GHOSTLY TEAL-GREEN LIGHT SEEPING FROM THE GAPS of the armour (two patches on the chest, the upper arms, the waist, the knees - the brightest colour on him). THE HEAD: a TALL SPIKED HELM with TWO TALL POINTED IRON HORNS rising from the top like a crown, a narrow visor slit with TWO GLOWING TEAL-GREEN EYES (clearly readable); no face visible, the whole head is armour. THE BODY: HUGE SPIKED PAULDRONS flaring out on both shoulders (a row of points along their edges); a heavy chest plate with a central point; a TATTERED DARK-MAROON CLOTH hanging from the belt (ragged pointed hem) between pointed iron tassets; CLAWED IRON GAUNTLETS; thick armoured legs with pointed knee guards and heavy iron boots. Broad on top, narrower below, like an iron tower. THE WEAPON, Nightfall: a HUGE LONG-HANDLED MACE - a black iron head with SPIKES ON EVERY SIDE and a GLOWING TEAL-GREEN CRACK across its middle, a long black iron haft with a SHORT IRON CHAIN hanging from its butt end.
Pose: League's own idle (image 1): standing firm, feet apart, the mace RESTING ON ONE SHOULDER with its head behind and above his head and the haft slanting forward from the shoulder; the other arm hanging at his side, claws slightly open. Nothing covers the helm's visor or the two green eyes (keep the mace head and the haft clear of them). 3/4 FRONT view facing image right.
Proportions: the head may be a little bigger than in the game model so the eyes read at a small size, but NOT a chibi big head; he is a heavy armoured giant, broader in the shoulders than other characters. Keep the whole figure COMPACT, not a giant block.
Style: crisp pixel art like images 10-12 - EVEN SQUARE PIXELS ABOUT 8 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a one-square near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the armour dark gunmetal (grey-blue highlights, slate mid-tones, near-black shadows), the ghost light teal-green (pale mint core, teal, deep teal), the eyes bright teal-green, the cloth dark maroon, the mace black iron with its teal crack; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no slam, no dark aura, no grasping claw, no realm, no glow halo), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`mordekaiser-model-B.png`（正侧面朝右）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look of this picture; 2 the same from the front: the chest plate, the huge spiked pauldrons, the maroon cloth, the leg armour; 3 the head close-up: the helmet's two tall horns, the visor slit, the two green eyes, the mace head; 4 the same from behind: the back armour and how the mace rests on the shoulder; 5 the official illustration: his mood; 6 moments of him walking; 7 moments of his attack and spells; 8 the idle between 3/4 and side; 9 THE IDLE FROM THE SIDE - the ANGLE of this picture). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters: copy their pixel-art style (image 10 the latest approved picture of this series, image 11 a heavy armoured character carrying a big weapon on the shoulder, image 12 another approved picture).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 1250 px from the top of the mace head (or the helmet horns) to the soles and no more than 960 px wide, centred, comfortable transparent margins, nothing cut off, the soles level on one ground line.
The character: Mordekaiser, the Iron Revenant, a TOWERING UNDEAD WARLORD IN SPIKED BLACK IRON PLATE ARMOUR (dark gunmetal with a slight blue-green tint: grey-blue highlights, near-black shadows), GHOSTLY TEAL-GREEN LIGHT SEEPING FROM THE GAPS of the armour (the chest, the upper arm, the waist, the knees - the brightest colour on him). THE HEAD: a TALL SPIKED HELM with TWO TALL POINTED IRON HORNS rising from the top like a crown, a narrow visor slit with a GLOWING TEAL-GREEN EYE seen from the side (clearly readable); no face visible, the whole head is armour. THE BODY: HUGE SPIKED PAULDRONS (a row of points along their edges); a heavy chest plate; a TATTERED DARK-MAROON CLOTH hanging from the belt (ragged pointed hem) between pointed iron tassets; CLAWED IRON GAUNTLETS; thick armoured legs with pointed knee guards and heavy iron boots. THE WEAPON, Nightfall: a HUGE LONG-HANDLED MACE - a black iron head with SPIKES ON EVERY SIDE and a GLOWING TEAL-GREEN CRACK across its middle, a long black iron haft with a SHORT IRON CHAIN hanging from its butt end.
Pose: the same idle SEEN EXACTLY FROM THE SIDE, FACING IMAGE RIGHT (image 9): the helm in profile, the near shoulder and pauldron in front, the legs one in front of the other (front boot pointing right), the mace RESTING ON THE SHOULDER with its head behind and above his back and the haft reaching forward from the shoulder, the chain hanging from the butt end in front of him; the free arm hanging at his side. Nothing covers the visor and the eye.
Proportions: the head may be a little bigger than in the game model so the eye reads at a small size, but NOT a chibi big head; a heavy armoured giant. Keep the whole figure COMPACT, not a giant block. Same height, same square size and the same details as the 3/4 version.
Style: crisp pixel art like images 10-12 - EVEN SQUARE PIXELS ABOUT 8 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a one-square near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the armour dark gunmetal (grey-blue highlights, slate mid-tones, near-black shadows), the ghost light teal-green (pale mint core, teal, deep teal), the eye bright teal-green, the cloth dark maroon, the mace black iron with its teal crack; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no slam, no dark aura, no grasping claw, no realm, no glow halo), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），竖版 1024×1536，四周留边，锤头、头盔角、铁链、靴子都完整。
- 像素块大小一致（约 8 像素一块）、横平竖直对齐；一圈近黑描边；没有半透明边、没有柔光、没有渐变。
- 头盔两根高角、面甲缝里的青绿眼睛清楚可见，没被锤子挡住。
- 尖刺肩甲、胸口和关节缝里的青绿灵魂光、暗红色破布、带爪铁手套、尖角护膝、铁靴都在。
- 锤子：四面尖刺的黑铁锤头 + 中间青绿裂纹、长锤柄、柄尾一小段铁链；扛在肩上，锤头在头后上方。
- A 是 3/4 正面朝右；B 是正侧面朝右（侧面头盔、两腿一前一后、靴尖朝右）；两版高度、方块大小、细节一致。
- 不画特效、不画地面和影子；靴底落在同一条地面线上。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/mordekaiser-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 先看 `raw/`（如果有）原稿，用 `regrid.py` 按原稿自己的格子读回；Codex 自己处理后的版本可能走样（库奇的教训），两种并排给用户挑。
- 用户已选 **PPU 高清**：读回的原画就是高清造型（k-means 按 Lab 取色，不用中位切分），动作从高清造型整块平移/部件替换拼（rig_corki_hd.py / rig_kassadin.py 的做法），1 倍帧由高清帧按 PPU 降采样兜底。用户也可能要求全部动作用 A（正面）造型。
- 同一个头盔（两只绿眼睛）贯穿所有帧；武器要直；只做无损平移，不变形不乱转。
