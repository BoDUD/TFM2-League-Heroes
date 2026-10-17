# 布隆（弗雷尔卓德之心）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 布隆还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**盾的位置**，人、脸、衣服、盾完全一样：**A = 盾立在地上、挡在他身前（画面右边），远侧手按着盾顶**；**B = 盾离地、挂在远侧手臂上举在身前（盾底在膝盖高度），近侧手握拳在腰前，随时要冲**。你挑一版，之后第 1 步再按它画高清（PPU）造型，所有动作都用 3/4 正面。
> - **长相照英雄联盟原版**（附图 1–8）：布隆，一个**又高又壮的弗雷尔卓德大力士**，憨厚开朗。**光头**，粉色皮肤；**一大撇深棕色八字胡**，两头往上卷，又宽又浓（全身最有特点的地方）；**深棕色粗眉毛**、小眼睛、下巴上一层青灰色胡茬；脖子上一根皮绳挂着**一颗青绿色的宝石坠子**。
> - **身体**：**赤裸的上身，粉色皮肤，胸口、肚子和双臂上有一圈圈紫红色的部落纹身条纹**（附图 3、4）；肩膀和手臂特别粗壮（大力士体型，手臂比头还粗）；**一边肩膀上是蓝灰色钢肩甲，肩甲上盖着一大团白灰色的毛皮披肩**；前臂套着**蓝灰色钢护腕**，手上缠着棕色皮绳；腰上一圈棕色皮带，**正中是一块圆形大腰扣：深蓝钢色圆盘、金色边框、上面一个羊角图案**；**深棕色长裤**，膝盖下一圈**灰白色毛皮**，**深蓝灰色的厚靴子**。
> - **盾（他的武器，要立得正）**：一面**像门一样的巨大方盾**，高到他的胸口：**石板灰色的厚门板，金色的边框，顶上一条横出来的金色横梁，横梁上刻着回纹**；盾面正中是**一个深钢色的公羊头，两只卷曲的大羊角，羊头的眼睛和额头上的宝石发青蓝色的光**，一条棕色皮带横过羊角（附图 2）；盾的背面是一扇木门、铁合页（附图 4，这张图里看不到背面）。**盾始终竖直立正，边是竖直的，不要歪、不要斜。**
> - **姿势**：3/4 正面朝右（脸、八字胡、胸口朝向看画的人），**盾在他身前、画面右边，羊头那一面朝外（朝右朝前）**，可以挡住他远侧的腿和一点远侧身体，但**不能挡住他的脸、八字胡、胸口和近侧手臂**。注意：附图 1、2、7 里盾在画面左边（他转向了），**你的图里盾在画面右边、在他前面**；附图 4 是没有被盾挡住的身体（没镜像，朝左），只用来看身体的样子。两腿分开站稳（近侧的腿在画面左边、颜色亮，远侧的腿在画面右边、稍暗、稍高，被盾挡住一部分），两只脚踏在同一条地面线上。
> - **风格和比例照附图 10–12**（之前画的卡萨丁、古拉加斯、库奇）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；**头按原版比例，不要大头娃娃**（他是大块头，头只占身高的六分之一左右）；**整体收紧凑**。颜色：皮肤粉色（亮部浅粉、暗部玫红）、纹身紫红、胡子和眉毛深棕、毛皮白灰、钢件蓝灰、金件土金色、盾面石板灰（亮部浅灰蓝、暗部深紫灰）、羊头深钢、宝石和羊眼青蓝发光、裤子深棕、靴子深蓝灰；深浅之间分界清楚，不要糊成一团。
> - **画布用横版 1536×1024**：从头顶到鞋底约 780 px；人和整面盾都在画面里，不出画。
> - 不画任何特效（寒冬之咬的冰、挺身而出、坚不可摧的冰盾光、冰川裂隙第 3 步再单独画）；**不画附图里他脚边的小魄罗**；鞋底和盾底是最低点，平平地落在同一条地面线上（游戏在脚下画血条）。
> - 交付：`outputs/braum-picture/braum-model-A.png`、`outputs/braum-picture/braum-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `braum_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_braum_league_front.png` | 英雄联盟原版布隆待机，3/4 视角 | 整体样子、颜色（盾在左边：你的图里放右边） |
| `refs/2_braum_league_shield.png` | 同一帧，转到能看清盾面 | **盾的正面**：金边框、横梁回纹、羊头、卷角、发光的眼睛和宝石、皮带 |
| `refs/3_braum_league_head.png` | 头的特写 | 光头、八字胡、眉毛、胡茬、宝石坠子、毛皮披肩、纹身 |
| `refs/4_braum_league_body.png` | 同一帧从另一边看（没镜像，朝左） | 没被盾挡住的身体：纹身、腰扣、护腕、裤子、膝盖毛皮、靴子；盾的木门背面 |
| `refs/5_braum_splash.png` | 官方加载画面 | 气质（憨厚、强壮、冰雪） |
| `refs/6_braum_league_run.png` | 英雄联盟里他跑动的几个瞬间 | 盾怎么拿（B 的参考） |
| `refs/7_braum_league_actions.png` | 普攻、Q 寒冬之咬、W 挺身而出、R 冰川裂隙的瞬间 | 手和盾怎么动 |
| `refs/8_braum_league_unbreakable.png` | E 坚不可摧：举盾挡在身前 | 盾举起来的样子（B 的参考） |
| `style/9_style_kassadin.png` | 你之前画的卡萨丁像素图 | **只看风格** |
| `style/10_style_gragas.png` | 你之前画的古拉加斯像素图 | **只看风格**（同是大块头） |
| `style/11_style_corki.png` | 之前通过的库奇像素图 | **只看风格**（最近通过的一张） |

## 提示词 A：`braum-model-A.png`（盾立在身前地上）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view - the look; 2 the same turned so the FRONT OF THE SHIELD shows: the gold frame, the gold top bar with a key pattern, the dark-steel ram's head with curled horns, its glowing cyan eyes and forehead gem, the leather strap; 3 the head close-up: bald head, big dark-brown handlebar moustache, thick brows, stubble, the teal pendant, the white fur mantle, the tattoos; 4 the same pose from the other side, NOT mirrored, facing left: his body unhidden - the tattoo bands, the round belt buckle with a ram emblem, the bracers, the trousers, the fur at the knees, the boots - and the wooden back of the shield; 5 the official illustration: his mood; 6 moments of him running with the shield; 7 moments of his attack and spells; 8 the shield raised in front of him). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. In images 1, 2 and 7 the shield is on the image left because he is turned; in YOUR picture the shield is on the IMAGE RIGHT, in front of him. Ignore the small pink creature at his feet in the renders. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 11 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 780 px from the top of his head to his soles, centred, comfortable transparent margins, nothing cut off (the whole shield inside the picture).
The character: Braum, the Heart of the Freljord, a huge, broad, good-natured strongman. HEAD: BALD, pink skin, a BIG DARK-BROWN HANDLEBAR MOUSTACHE curling up at both ends (his most striking feature), thick dark-brown brows, small friendly eyes, grey-blue stubble on the chin; a TEAL GEM PENDANT on a leather cord. BODY: a BARE, MASSIVE CHEST AND ARMS, pink skin with MAUVE TRIBAL TATTOO BANDS across the chest, belly and arms; arms thicker than his head; a BLUE-STEEL PAULDRON on one shoulder under a big WHITE-GREY FUR MANTLE; blue-steel bracers on the forearms with brown leather wraps; a brown leather belt with a BIG ROUND BUCKLE: a dark steel-blue disc with a gold rim and a ram emblem; DARK-BROWN TROUSERS, grey-white fur below the knees, heavy dark blue-grey boots. SHIELD: a HUGE DOOR-LIKE RECTANGULAR SHIELD reaching his chest: a thick slate-grey slab framed in earthy gold, a gold crossbar sticking out on top carved with a key pattern; on its face a DARK-STEEL RAM'S HEAD with two big CURLED HORNS, its eyes and a forehead gem GLOWING CYAN-BLUE, a brown leather strap across the horns. The shield stands STRAIGHT UPRIGHT, its sides vertical - never tilted.
Here the shield STANDS ON THE GROUND IN FRONT OF HIM on the image right, the ram face turned outward (toward image right and the viewer); his far hand rests on its top bar; his near arm hangs relaxed at his side, the hand a loose fist. The shield may hide his far leg and a little of his far side, but NEVER his face, moustache, chest or near arm.
Proportions: game-sprite proportions like images 9-11, but keep HIS OWN proportions: huge and broad, the head about one sixth of his height - do NOT make a big-headed chibi. Keep the whole figure COMPACT, not a giant block. 3/4 FRONT view facing image right, face and chest toward the viewer.
Pose: standing firm, feet apart: the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher, partly behind the shield; both boots and the bottom of the shield flat on ONE ground line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 6-8 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: skin pink (pale pink highlights, rose shadows), tattoos mauve, moustache and brows dark brown, fur white-grey, steel blue-grey, gold earthy yellow, the shield slab slate grey (pale blue-grey highlights, dark purple-grey shadows), the ram's head dark steel, the gem and eyes glowing cyan, trousers dark brown, boots dark blue-grey; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no ice, no frost, no particles, no small creature, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`braum-model-B.png`（盾挂在手臂上举在身前）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view - the look; 2 the same turned so the FRONT OF THE SHIELD shows: the gold frame, the gold top bar with a key pattern, the dark-steel ram's head with curled horns, its glowing cyan eyes and forehead gem, the leather strap; 3 the head close-up: bald head, big dark-brown handlebar moustache, thick brows, stubble, the teal pendant, the white fur mantle, the tattoos; 4 the same pose from the other side, NOT mirrored, facing left: his body unhidden - the tattoo bands, the round belt buckle with a ram emblem, the bracers, the trousers, the fur at the knees, the boots - and the wooden back of the shield; 5 the official illustration: his mood; 6 moments of him running with the shield - HOW HE CARRIES IT in this picture; 7 moments of his attack and spells; 8 the shield raised in front of him). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. In images 1, 2, 6 and 7 the shield is on the image left because he is turned; in YOUR picture the shield is on the IMAGE RIGHT, in front of him. Ignore the small pink creature at his feet in the renders. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 11 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 780 px from the top of his head to his soles, centred, comfortable transparent margins, nothing cut off (the whole shield inside the picture).
The character: Braum, the Heart of the Freljord, a huge, broad, good-natured strongman. HEAD: BALD, pink skin, a BIG DARK-BROWN HANDLEBAR MOUSTACHE curling up at both ends (his most striking feature), thick dark-brown brows, small friendly eyes, grey-blue stubble on the chin; a TEAL GEM PENDANT on a leather cord. BODY: a BARE, MASSIVE CHEST AND ARMS, pink skin with MAUVE TRIBAL TATTOO BANDS across the chest, belly and arms; arms thicker than his head; a BLUE-STEEL PAULDRON on one shoulder under a big WHITE-GREY FUR MANTLE; blue-steel bracers on the forearms with brown leather wraps; a brown leather belt with a BIG ROUND BUCKLE: a dark steel-blue disc with a gold rim and a ram emblem; DARK-BROWN TROUSERS, grey-white fur below the knees, heavy dark blue-grey boots. SHIELD: a HUGE DOOR-LIKE RECTANGULAR SHIELD reaching his chest: a thick slate-grey slab framed in earthy gold, a gold crossbar sticking out on top carved with a key pattern; on its face a DARK-STEEL RAM'S HEAD with two big CURLED HORNS, its eyes and a forehead gem GLOWING CYAN-BLUE, a brown leather strap across the horns. The shield stays STRAIGHT UPRIGHT, its sides vertical - never tilted.
Here the shield is LIFTED OFF THE GROUND on his far arm, held up IN FRONT OF HIM on the image right with its bottom at knee height, the ram face turned outward (toward image right and the viewer); his near hand is a big fist held at his waist in front of the belt, ready to charge. The shield may hide his far leg and a little of his far side, but NEVER his face, moustache, chest or near arm.
Proportions: game-sprite proportions like images 9-11, but keep HIS OWN proportions: huge and broad, the head about one sixth of his height - do NOT make a big-headed chibi. Keep the whole figure COMPACT, not a giant block. 3/4 FRONT view facing image right, face and chest toward the viewer.
Pose: standing firm, feet apart, knees a little bent: the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher, partly behind the shield; both boots flat on ONE ground line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 6-8 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: skin pink (pale pink highlights, rose shadows), tattoos mauve, moustache and brows dark brown, fur white-grey, steel blue-grey, gold earthy yellow, the shield slab slate grey (pale blue-grey highlights, dark purple-grey shadows), the ram's head dark steel, the gem and eyes glowing cyan, trousers dark brown, boots dark blue-grey; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no ice, no frost, no particles, no small creature, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底、不是暗色渐变底），横版 1536×1024，四周留边，人和整面盾都完整。
- 光头、深棕八字胡（两头上卷）、粗眉、胡茬、青绿宝石坠子；粉色皮肤上紫红纹身条纹；手臂粗壮。
- 一边肩膀蓝灰钢肩甲 + 白灰毛皮披肩；蓝灰护腕；圆形大腰扣（深蓝钢盘、金边、羊角图案）；深棕长裤、膝下灰白毛皮、深蓝灰靴子。
- 盾在画面右边、他身前，羊头那面朝外：石板灰门板、金框、顶上金横梁回纹、深钢羊头卷角、青蓝发光的眼睛和额头宝石；**盾竖直立正，不歪**。
- A 盾立在地上、远侧手按盾顶；B 盾离地挂在远侧手臂上（盾底在膝盖高）、近侧拳头在腰前。
- 脸、八字胡、胸口、近侧手臂没被盾挡住；头按原版比例，不要大头娃娃；整体紧凑。
- 近侧腿在画面左边亮色、远侧腿在右边稍暗稍高；鞋底（A 还有盾底）落在同一条水平线上；没有任何特效、没有小魄罗。
- 大像素块清楚，没有糊、没有柔光、没有渐变；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/braum-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/braum/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`：用户选了 **PPU 高清、所有动作 3/4 正面**（卡萨丁 / 库奇的方式），所以第 1 步只要正面造型，Codex 直接在网格上画（像素块就是高清像素，原稿 1:1 读回，绝不先画大再缩）；在游戏里要和别的英雄一样高（约 41–42 格，用 hd.rs SIZES 调），外描边约 1 游戏像素，待机要有呼吸。
- 腿：待机两腿分开站稳（three-quarter-legs）；跑步按 Caitlyn 的交叉步方式；盾是刚体，只做平移和 90 度转，始终竖直；同一张脸贯穿所有帧。
