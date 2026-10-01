# 塔里克：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 用户还没有塔里克的图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差武器的拿法，其余一样；用户挑一版，之后第 1 步再按它画游戏尺寸（约 40 格）的精灵。
> - **长相照英雄联盟原版**（附图 1–4 是原版模型渲染）：棕红长发中分、两缕前发垂到下巴、蓝眼、方下巴；青蓝色斜襟上衣开 V 领、蓝宝石吊坠；两肩巨大的银白肩甲各镶一颗大蓝宝石；近侧手臂（图左）是深色皮袖加钢护手，远侧手臂（图右）光着；宽钢腰带、圆扣镶紫蓝宝石；深蓝前摆、深紫棕裤子、深灰绿护腿靴；身后深蓝紫长披风；近侧手（图左）拿一把短柄水晶斧锤：两片弯弯的银紫刃中间嵌一颗发光的紫蓝宝珠。
> - **风格和比例照附图 5、6**（用户之前让 Codex 画的卢锡安、贾克斯）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；结实的 Q 版比例，头（发顶到下巴）约占身高的三分之一，肩宽腿短。3/4 正面朝右，两只蓝眼睛都看得见。
> - **A = 英雄联盟原版站姿**：武器垂在身侧，斧头在膝盖旁（但不低于脚底）。**B = 持械守势**：武器竖着握在身前，斧头举到肩旁、下巴高度，不挡脸。
> - 脚底线以下什么都不能有（游戏在脚下画血条）：武器、披风下摆都在脚底以上结束。
> - 交付：`outputs/taric-model-A.png`、`outputs/taric-model-B.png`（1024×1536，真透明背景，人物约 1250 px 高），再附一个 `generation-prompts.txt` 写明实际用的提示词。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_taric_league_front.png` | 英雄联盟原版塔里克，待机第一帧，3/4 正面朝右 | 长相、服装、颜色、武器、站姿 |
| `refs/2_taric_league_head.png` | 头部特写 | 头发、脸、吊坠 |
| `refs/3_taric_league_weapon.png` | 武器头特写 | 武器的形状和颜色 |
| `refs/4_taric_league_side.png` | 更侧一点的角度 | 肩甲、披风、头发的后面 |
| `style/5_style_lucian.png` | 用户之前的卢锡安像素图 | **只看风格和比例** |
| `style/6_style_jax.png` | 用户之前的贾克斯像素图 | **只看风格和结实的体型** |

## 提示词 A：`taric-model-A.png`

六张图都附上，顺序同上表。

```text
Six attached images. Images 1-4 are 3D renders of the character from the game (1 full figure 3/4 front, 2 head close-up, 3 weapon close-up, 4 side view): copy from them the costume, the colours, the face, the hair and the weapon - NOT their 3D shading and NOT their adult proportions. Images 5 and 6 are STYLE ONLY, other characters: copy their pixel-art style and their compact, sturdy game-character proportions.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the hair to the soles, centred, comfortable transparent margins.
The character: Taric, the Shield of Valoran: a big heroic gem knight. Long dark auburn-brown hair parted in the middle, two long front locks falling past his cheeks to the jaw, the rest flowing back over his shoulders; a handsome square-jawed face with thick dark brows, bright blue eyes and a confident small smile; fair warm skin; a thin dark cord necklace with a small triangular blue gem at the throat. A teal-blue tunic wrapping diagonally across his chest, open in a deep V at the neck, a dark brown leather half-vest over his far shoulder. HUGE angular silver-white pauldrons on both shoulders, each set with a big round sapphire-blue gem. His near arm (image left) in a dark grey-brown leather sleeve with dark steel gauntlet plates and a small blue gem at the elbow; his far arm (image right) bare and muscular. A heavy dark steel belt with a big round buckle holding a violet-blue gem, a dark navy tabard panel with a steel-grey rim hanging from it to his knees; dark plum-brown trousers; dark grey-green armoured greaves and boots. A long dark navy-violet cape hanging behind him. Weapon: a short-hafted crystal mace-axe in his NEAR hand (image left): a dark wrapped grip, a steel collar, and a head of two curved silver-lilac blades (a double axe that curls like a claw) with a glowing violet-blue orb set between them.
Proportions: sturdy heroic chibi like images 5 and 6 - the head (top of the hair to the chin) about one third of the height from the crown to the soles, broad shoulders made even wider by the pauldrons, thick strong arms, short strong legs. 3/4 FRONT view facing image right, face and chest visible, BOTH blue eyes visible and level, the front locks framing the face without covering the eyes.
Pose A - League's own idle: he stands tall and confident, feet apart, knees straight; his near hand (image left) holds the mace-axe low at his side, arm hanging down and a little out, the weapon's head beside his knee with the blades pointing down-left - its lowest point ends ABOVE the soles line; his far hand (image right) open at his side. The cape hangs behind him; its hem, the weapon and everything else end AT OR ABOVE the soles line (the game draws the health bar under the feet). Both soles on the same horizontal line.
Style: detailed crisp pixel art like images 5 and 6 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks, black is only the outline); bright white-silver highlights on the pauldrons and the blades; saturated sapphire and violet gems with one white glint each; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 提示词 B：`taric-model-B.png`

六张图都附上，顺序同上表。

```text
Six attached images. Images 1-4 are 3D renders of the character from the game (1 full figure 3/4 front, 2 head close-up, 3 weapon close-up, 4 side view): copy from them the costume, the colours, the face, the hair and the weapon - NOT their 3D shading and NOT their adult proportions. Images 5 and 6 are STYLE ONLY, other characters: copy their pixel-art style and their compact, sturdy game-character proportions.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the hair to the soles, centred, comfortable transparent margins.
The character: Taric, the Shield of Valoran: a big heroic gem knight. Long dark auburn-brown hair parted in the middle, two long front locks falling past his cheeks to the jaw, the rest flowing back over his shoulders; a handsome square-jawed face with thick dark brows, bright blue eyes and a confident small smile; fair warm skin; a thin dark cord necklace with a small triangular blue gem at the throat. A teal-blue tunic wrapping diagonally across his chest, open in a deep V at the neck, a dark brown leather half-vest over his far shoulder. HUGE angular silver-white pauldrons on both shoulders, each set with a big round sapphire-blue gem. His near arm (image left) in a dark grey-brown leather sleeve with dark steel gauntlet plates and a small blue gem at the elbow; his far arm (image right) bare and muscular. A heavy dark steel belt with a big round buckle holding a violet-blue gem, a dark navy tabard panel with a steel-grey rim hanging from it to his knees; dark plum-brown trousers; dark grey-green armoured greaves and boots. A long dark navy-violet cape hanging behind him. Weapon: a short-hafted crystal mace-axe in his NEAR hand (image left): a dark wrapped grip, a steel collar, and a head of two curved silver-lilac blades (a double axe that curls like a claw) with a glowing violet-blue orb set between them.
Proportions: sturdy heroic chibi like images 5 and 6 - the head (top of the hair to the chin) about one third of the height from the crown to the soles, broad shoulders made even wider by the pauldrons, thick strong arms, short strong legs. 3/4 FRONT view facing image right, face and chest visible, BOTH blue eyes visible and level, the front locks framing the face without covering the eyes.
Pose B - guard: he stands tall, feet apart; his near hand (image left) holds the mace-axe UPRIGHT in front of his near hip, the grip at waist height, the double-bladed head up beside his near shoulder at about chin height (never covering the face); his far hand (image right) open at his side. The cape hangs behind him; its hem, the weapon and everything else end AT OR ABOVE the soles line (the game draws the health bar under the feet). Both soles on the same horizontal line.
Style: detailed crisp pixel art like images 5 and 6 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks, black is only the outline); bright white-silver highlights on the pauldrons and the blades; saturated sapphire and violet gems with one white glint each; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整。
- 两只蓝眼睛都在、同一高度；前发不挡眼。
- 武器在近侧手（图左）；武器、披风、脚都不低于脚底线，两只脚底在同一条水平线上。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
