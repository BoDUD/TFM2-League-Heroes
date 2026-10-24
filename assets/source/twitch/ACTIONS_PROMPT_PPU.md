# 图奇：全部动作逐帧重画（给 Codex 的提示词）

> 图奇的定稿设计图（`refs/design.png`，8 倍放大，一格 = 一个像素块；`refs/design_1x.png` 是 1 倍原图，109 × 71 格）。请把他的**八个动作每一帧都重新画整个人**：跑步、平A、Q、W、E、R、受击、死亡。**姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作），**动作的力度和细节看英雄联盟里同一个动作**（`refs/lol_<动作>.png`）。待机不用画。
>
> 一共 **22 张模板**（`templates/*.png`，每张 1536×1024，一张两帧，每格 768×1024），41 帧：
> - 跑步 `run_1..4`（8 帧）：弓着背往前小跑，两手端着弩，腿一前一后交叉迈步，尾巴在身后甩
> - 平A `attack_1..4`（8 帧）：端平弩瞄准，第 3 帧扣扳机射出，弩往后一顶（后坐），再端回来
> - Q 埋伏 `skill_1..2`（3 帧）：压低身子蹲下、弩收在身前，像要潜行隐身
> - W 剧毒之桶 `skill2_1..2`（4 帧）：远侧的手抡起一个**小毒桶**，第 3 帧往前扔出去，手收回（扔出去以后手里就没有桶了）
> - E 毒性爆发 `skill2_e_1..3`（5 帧）：原地一跳，身子和弩猛地一抖，第 4 帧落地
> - R 火力全开 `ult_1..2`（3 帧）：举起弩用力往前射，第 2 帧射出，后坐很大
> - 受击 `hit_1`（2 帧）：被打得往后一仰
> - 死亡 `dead_1..4`（8 帧）：被打飞 → 摔倒 → 躺在地上，弩掉在身边
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的姿势、位置和大小**重新画成设计图里的图奇；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站直时从耳朵尖到脚底的高度（71 格）。旧版是 1 倍小图、颜色和细节都不对、弩和尾巴也比设计图短，**只照它的动作**，人物本身全部照设计图（弩和尾巴照设计图的长度）。

**最重要的四条：**

1. **人物和设计图一模一样，不变形**：同样的灰色鼠头和长嘴、粉色大耳朵、**金色单片护目镜**（圆框、奶白镜片、黑瞳孔）、**咧嘴露出的一排尖牙和嘴角的獠牙**、红棕色鼻头、橙色围巾、绿色皮肤、棕色背包（青绿圆珠、金扣）、皮带和护腕、**蓝绿色的破烂长衣摆**、紫灰色的腿和白爪子、**棕灰条纹的长尾巴**；头的大小、身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
2. **弩一直是设计图那把弩**：黄铜和木头的弩身、淡蓝色的钢弩臂、上面一颗绿宝石，**长度和样子每帧不变、是直的**，不弯不断；两只手握着它（W 扔桶时远侧的手离开弩去扔桶，近侧的手仍握着弩）。
3. **尾巴一直连在身体上**：从衣摆后面的屁股上长出来，尾根贴着身体，不能和身体分开、不能拖在地上（死亡躺下的帧除外），跟着动作甩，尾尖比尾根慢半拍。
4. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；在空中的帧（E 的跳、死亡被打飞）按浅色人影的高度。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- 每帧一个清楚的剪影，动作有力：扣扳机时弩往后顶、肩膀跟着动；扔桶时整个身子转过去带动手臂。

**像素规则**：每块 **5 像素**的方块，横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**不画箭矢、枪口火光、毒雾、毒液、隐身效果等任何特效**（W 手里的小毒桶要画，扔出去以后不画），不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

- 交付：`outputs/twitch-actions/<模板同名>.png`（22 张，都是 1536×1024，**和模板一样的两格布局**，每帧画在模板对应格子的位置上；不用的格子留空）；原始生成图原样放进 `outputs/twitch-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/twitch-actions/HANDOFF.md`（交付说明），再打包成 `outputs/twitch_actions_done.zip`。

## 附图（压缩包 `twitch_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（8 倍） | **每张都附，第一张**：人物、弩、尾巴、衣服、比例、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第五张**：只用这些颜色 |
| `templates/<名>.png` | 两帧的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样两帧的彩色原图（放大） | **第三张**：看清动作（只照动作） |
| `refs/lol_<动作>.png` | 英雄联盟里同一个动作的几帧 | **第四张**：动作的力度和手、弩、尾巴怎么动（只看动作） |
| `sheets.json` | 每张模板是哪个动作的第几帧、每帧时长 | 对照 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/lol_<动作>.png`、`refs/design_palette.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (8x: every square one pixel): a hunched plague rat-man with a grey rat head and long snout, big pink ears, a round brass goggle over his eye (gold rim, cream lens, black pupil), a wide grin with a row of sharp teeth and a fang at the corner, a red-brown nose, an orange scarf, green skin, a brown backpack with teal orbs and gold studs, leather straps and bracers, a long tattered blue-green coat, purple-grey legs with white claws, a long brown-grey striped rat tail, holding a brass-and-wood crossbow with pale steel-blue bow arms and a green gem on top in both hands, in 3/4 view facing right. Image 2 is a TEMPLATE of two animation frames of his <ACTION>, frames <N1>-<N2>: in each 768x1024 cell the PALE FIGURE is the pose to draw (his old animation frame scaled to his height), the grey horizontal line is the ground, the short tick his standing point, the grey bar on the left his height standing (ear tips to soles). Image 3 is the same old frames in colour: copy ONLY their pose and motion (they are small, their colours and details are wrong, their crossbow and tail too short). Image 4 is the same action from the 3D game: copy only HOW he moves (the body bracing into the move, the crossbow recoiling, the arms, the tail swinging), not its look. Image 5 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME two-cell layout as image 2: in each cell draw the character of image 1 in the pose of that cell's pale figure, at its place and size, soles on the ground line at the standing point when he stands. One scale for the whole sheet, set by the grey bar.
He must be EXACTLY image 1 in every frame: the same head, ears, goggle, teeth and fang, nose, scarf, backpack, straps, coat, legs, claws and tail, image 5's colours only, the same head size, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE CROSSBOW is always image 1's crossbow: the same length and shape, straight, never bent or broken, held in his hands. THE TAIL stays attached to his rear under the coat, never a separate piece, never lying on the ground while he stands, swinging with the move.
<EXTRA>
Always 3/4 view, face toward the front-right as in image 1.
THE PIXEL GRID: every square the SAME size, 5 px, on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing, no glow.
No bolts, no muzzle flash, no poison cloud, no venom, no stealth shimmer, no effects, no ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<ACTION>` / `<N1>-<N2>` 照 `sheets.json` 的 `action` 和 `frames` 填。`<EXTRA>`：
- W（`skill2_*`）填 `HE THROWS A SMALL POISON CASK: a small round wooden keg with green poison, held in his far hand and swung up and forward; his near hand keeps the crossbow; after the throw frame (frame 3) his far hand is empty.`
- 死亡（`dead_*`）填 `IN THE LAST FRAMES HE LIES ON THE GROUND on his back or side, the crossbow dropped beside him (still the same straight crossbow), the tail lying behind him.`
- 其他动作留空。

## 交回前请检查

- 22 张，每张 1536×1024、两格布局，背景真透明（或纯白），没有模板的浅色人影、线和字。
- 每帧：脸朝右前方，护目镜、牙齿、獠牙、鼻头清楚；头、手臂、腿的大小粗细和设计图一样；弩是设计图那把、直的、一样长；尾巴连在身上；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- 平A 第 3 帧、R 第 2 帧弩往前射（没有箭和火光）；W 第 3 帧桶扔出去，之后手里空了。
- 最后写 `outputs/twitch-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/twitch_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读原始生成图（不读导出图），照 `casts_ahri_hd.py`（ahri-ppu22 分支）/ `casts_lux_hd.py` 的办法修：按身体定每张的比例，头换成设计图的头（对准护目镜），弩换成设计图的直弩（对准握把，取最近的方向），后脚钉住；逐帧查尾巴有没有和身体断开、牙齿和护目镜在不在。
- 出手高度：平A / R 的 bolt_y、W 毒桶出手点照出手帧的弩口和手重算；`skill2_e` 标签、hd.rs、塞拉斯 / 佛耶戈 / 妮蔻的表、待机和选人卡轮播都要跟上。
