# 内瑟斯：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户采用了你第 0 步画的 **A（平时）** 和 **B（死神降临）**（`1_picked_A.png`、`1_picked_B.png`），定的大小（每个游戏像素 1.2 格）：
>   - **A：从耳尖到鞋底 53 格**（游戏里 44 行），连法杖约 70 格宽。
>   - **B：同一个内瑟斯放大 1.35 倍**：从耳尖到鞋底 **71 格**（游戏里 59 行），连法杖约 86 格宽。格子大小和 A 一样，只是人更大。
> - 比例照原画（头连耳朵约占身高四分之一），不用改。
> - 我把 A、B 按这个大小直接缩好了（`2_target_A.png`、`2_target_B.png`，每格 11 px），**大小、位置、姿势都对，但糊了**：脸和眼睛糊成几格，金色头冠和铠甲的几档金色分不开，青绿宝石变成零散的亮格，深色的毛糊成一片，手臂和小腿的条纹布条成了杂点，法杖的木杆断断续续，斧刃边缘有零散的格子。
> - **这一轮就是在同样的格子上把它们重画清楚**：同样大小、同样位置、同样姿势，**每块 11 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**A、B 各画两稿。**

## 大小和位置（照 `2_target_*.png` / `3_layout_*.png`）

- 画布 **1024 × 1024**，**每格 11 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A**：**耳尖在 y = 407**（绿线），**两只鞋底在 y = 990**（红线）；人连法杖从 x ≈ 121 到 x ≈ 891，位置照 `2_target_A.png`。
- **B**：**耳尖在 y = 209**（绿线），**两只鞋底在 y = 990**（红线）；人连法杖从 x ≈ 33 到 x ≈ 979，位置照 `2_target_B.png`。

## 要画清楚的地方

- **头**（`4_head.png` 是 A 的头，第 0 步读回后 8 倍放大）：
  - **金色豺狼头冠**分 3–4 档（亮金、金、暗金、棕金），额前一颗**青绿宝石**；两只长耳朵竖起，**近侧耳朵里面暗红色**。
  - **长嘴向前**，黑褐色的毛（要有偏暖的亮边），嘴边露出 **1–2 格白色尖牙**；**眼睛发青绿光**（至少 2 格），A、B 里头的形状一样，只是 B 更大、更亮。
- **铠甲**：金色大肩甲（3–4 档金、青绿镶边）、胸口金色领甲，露出**黑褐色的毛和肌肉**（暗处是它自己最暗的褐色，亮处偏暖）；金色护臂、金色长靴，宝石是**整齐的青绿小块**（2×2 左右，一格亮点），不要散成单格。
- **布料**：深蓝色编织腰带（能看出编织的斜纹）；青绿色长腰布垂到膝盖，下面一条浅灰色的布；**手臂和小腿上灰白相间的条纹布条**，每条 1 格，规整地一深一浅。
- **法杖**：**木杆连续不断**（2 格粗，棕色，亮暗两档），两端青绿色金属；**金色月牙斧刃**形状清楚，边缘整齐，镶青绿宝石；杖尾的小金色尖刃也要清楚。
- **A 平时**：微微弓背站着，法杖横握在身前偏下，斧刃在前（画面右边）靠近地面，杖尾斜向身后（画面左边）。
- **B 死神降临**：和 A **一样的姿势和握杖方式**，只是整个人大 1.35 倍；**眼睛和铠甲上所有青绿宝石、花纹都是亮青白色**（平涂的亮格，不要光晕），斧刃也更亮。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–8（本包的塔姆、厄加特，每游戏像素 1.2 格，和内瑟斯一样；斯维因 1.5 格；雷克顿 1 格；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照原画（金色铠甲、青绿宝石、黑褐色的毛、深蓝腰带、青绿腰布、灰白布条、棕色木杆）。毛很暗，**一定要有亮边**，不然在游戏里会糊成一团。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图边缘是半透明的，这次不要）。不要网格线、文字、边框、影子、地面、特效（沙暴、灵魂火、发光拖尾都不画）。

## 附图（压缩包 `nasus_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` / `1_picked_B.png` | 你第 0 步画的 A、B（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` / `2_target_B.png` | 按新大小缩到每格 11 px 放在画布上（糊的） | **大小、位置、姿势**照它，糊的地方重画 |
| `3_layout_A.png` / `3_layout_B.png` | 同一张加网格线：绿线 = 耳尖，红线 = 地面 | 对齐网格、耳尖和地面线的位置 |
| `4_head.png` | A 的头（第 0 步读回后 8 倍放大） | 头冠、耳朵、长嘴、眼睛 |
| `style/5_style_tahmkench.png` … `8_style_renekton.png` | 本包的塔姆、厄加特（每游戏像素 1.2 格）、斯维因（1.5 格）、雷克顿（1 格），8 倍放大 | **只看风格**：这个密度下一格有多大、暗色身体怎么留亮边、金饰和长柄武器怎么画 |

## 提示词 1：`nasus-model-A-1.png`、`nasus-model-A-2.png`（平时，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A and 1B approved pixel-art pictures of this character - a tall muscular jackal-headed warrior with dark brown fur, a gold jackal headdress with a teal brow gem, two tall upright ears (the near one dark red inside), a long snout with white fangs, glowing teal eyes, huge gold pauldrons and a gold collar plate with teal inlays, gold bracers and tall gold boots, a dark-blue braided belt, a long teal loincloth over a light-grey cloth, grey-and-white striped wraps on the forearms and shins, and a very long staff (a brown wooden shaft, teal metal ends, a gold crescent axe blade with teal gems, a small gold spike at the other end) held low across in front of him, the blade forward near the ground; in 1B the same warrior 1.35x bigger with his eyes and every teal gem and line blazing cyan-white (the LOOK, the COLOURS and the DETAILS to keep); 2A and 2B the same two pictures shrunk to their final game size on a 1024x1024 canvas, 11 px squares - the SIZE, the PLACE and the POSE are right, but they are muddy (the face and eyes blurred, the gold shades of the headdress and armour mixed, the teal gems scattered into loose bright squares, the dark fur smeared into one mass, the striped wraps turned to noise, the staff's shaft broken, stray squares on the blade's edge); 3A and 3B the same with grid lines every 5 squares: the green line = the tips of his ears, the red line = the ground; 4 his head enlarged; 5-8 STYLE ONLY: other characters from the same game, shown 8x so every square is one pixel (5 and 6 at this same square density) - copy their pixel-art look, the lit edges on a dark body, how gold ornaments and a long polearm are drawn.
Draw with the image generator ONE clean pixel-art picture of the character in his NORMAL form (picture A): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2A: every square 11 px, aligned on one straight grid starting at the canvas corner, the tips of his ears at y 407, both soles on the ground line y 990, about 53 squares from the ear tips to the soles, the figure with the staff from about x 121 to about x 891 - standing slightly hunched, the staff held low across in front of him, the crescent blade forward (image right) near the ground, the shaft slanting back behind him (image left) - as if a pixel artist redrew image 1A square by square on image 2A's grid.
Make it CRISP and READABLE at this size: the GOLD JACKAL HEADDRESS in 3-4 gold shades (bright gold, gold, dark gold, brown-gold) with its teal brow gem; both ears upright, the near one dark red inside; the long snout, dark brown fur with WARM LIT EDGES, 1-2 squares of white fangs; the eyes glowing teal (at least 2 squares); the huge gold pauldrons with teal trims, the gold collar plate over the dark-furred muscular chest; gold bracers and tall gold boots; every teal gem a neat small block (about 2x2 with a 1-square light), never loose single squares; the dark-blue braided belt; the teal loincloth to the knees over a light-grey cloth; the grey-and-white striped wraps on the forearms and shins, one square per stripe, evenly light and dark; the staff's brown shaft CONTINUOUS (2 squares thick, a light and a dark shade), teal metal at both ends, the GOLD CRESCENT BLADE with clean edges and teal gems, the small gold spike at the other end.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`nasus-model-B-1.png`、`nasus-model-B-2.png`（死神降临，两稿）

附同样的图。**用 image_gen 画。**

```text
Same attached images. Draw with the image generator ONE clean pixel-art picture of the character in his FURY form (picture B): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2B: every square 11 px (the SAME square size as picture A - he is simply bigger), aligned on one straight grid starting at the canvas corner, the tips of his ears at y 209, both soles on the ground line y 990, about 71 squares from the ear tips to the soles, the figure with the staff from about x 33 to about x 979 - the same pose and staff grip as picture A - as if a pixel artist redrew image 1B square by square on image 2B's grid.
Make it CRISP and READABLE at this size: the same gold jackal headdress, ears, snout, fangs, dark brown fur with warm lit edges, gold armour, dark-blue belt, teal loincloth, grey-white striped wraps and staff as in picture A, drawn with more squares; his EYES and EVERY TEAL GEM AND TEAL LINE on the armour BLAZE bright CYAN-WHITE (flat bright squares, no glow halo); the staff's crescent blade brighter too.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no sandstorm, no glowing trails), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` / `2_target_B.png` 一样：每格 11 px、对齐网格；A 耳尖 y 407、B 耳尖 y 209，鞋底都在 y 990。
- 头冠几档金色分得开、眼睛发光、尖牙看得见；毛有亮边；宝石是整齐的小块；条纹布条规整；木杆连续、斧刃完整；外描边连续；没有任何特效。
- B 和 A 同样的格子大小，只是人大 1.35 倍；眼睛和所有青绿宝石、花纹是亮青白色。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/nasus-model/`）

- `nasus-model-A-1.png`、`nasus-model-A-2.png`、`nasus-model-B-1.png`、`nasus-model-B-2.png`；**image_gen 的原始生成图原样放 `outputs/nasus-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/nasus_model_done.zip`，这样我这边知道已经交付完了。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），需要时删整行整列到 53 / 71 行（不经过脸），和 `2_target_*.png` 并排、按游戏大小和德莱厄斯、塔姆、厄加特、斯维因放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后做第 2 步动作（自己用造型部件无损摆，塔姆 / 斯维因的方式；法杖只整根平移或直角转）：A 待机、走路（换皮法：oppi 的雷克顿当骨架）、普攻 nasus_attack1 / Nasus_Attack2、Q Nasus_Spell1、W Nasus_Base_Spell2_Full、E Nasus_Base_Spell3_Full、R Nasus_Base_Spell4_Full、受击、死亡 Nasus_Base_Death；B（附加包整身换图 + 主包 R 期间的出手）：b_idle、b_run、b_attack、b_skill、b_skill2、b_hit。
