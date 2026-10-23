# 阿狸：全部动作逐帧重画（给 Codex 的提示词）

> 阿狸的定稿设计图（`refs/design.png`，8 倍放大，一格 = 一个像素块；`refs/design_1x.png` 是 1 倍原图，78 × 88 格）。请把她的**七个动作每一帧都重新画整个人**：跑步、平A、Q、E、R、受击、死亡。**姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作），**画法照 oppi 的阿狸**（`refs/oppi_<动作>.png`）。待机不用画。
>
> 一共 **26 张模板**（`templates/*.png`，每张 1536×1024，一张两帧，每格 768×1024），49 帧：
> - 跑步 `run_1..4`（8 帧）：英雄联盟的跑法，身体略前倾，头发、尾巴往后飘，腿一前一后交叉迈步
> - 平A `attack_1..4`（7 帧）：手收到胸前、身体后仰蓄力，第 4 帧手往前甩出法球，收回
> - Q 欺诈宝珠 `skill_1..4`（8 帧）：下蹲 → 起跳举手 → 第 4 帧在空中往前甩出宝珠 → 落地弓步 → 站起
> - E 魅惑妖术 `skill2_1..4`（7 帧）：手放到嘴边，第 3 帧往前吹出飞吻，收回
> - R 灵魄突袭 `ult_1..5`（9 帧）：起跳 → **整个人横着往前飞**（头抬起在最前面，长发和九尾一起往后拖成一条，手往前伸，腿往后拖）→ 落地
> - 受击 `hit_1`（2 帧）：被打得往后一仰
> - 死亡 `dead_1..4`（8 帧）：被击飞 → 跌坐在地 → 撑起抬手 → 仰面躺倒
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的姿势、位置和大小**重新画成设计图里的阿狸；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站直时从狐耳尖到脚底的高度（88 格）。旧版是 1 倍小图、颜色和细节都不对，**只照它的动作**，人物本身全部照设计图。

**最重要的四条：**

1. **九条尾巴必须一直连在身体上**：尾巴从**后腰（短裙后面）长出来**，尾根始终贴着她的腰和背，**尾巴和身体、头发之间不能露出空隙**，也不能像一团单独的东西飘在身后。尾巴是一整扇，不要画成断开的几截。每帧都要看得见、和设计图一样大（约 36–40 格宽），白色带淡紫尾尖，跟着动作甩动（尾尖比尾根慢半拍）。R 横飞时九尾和长发一起往后拖成一条，尾根仍然连在腰上。
2. **人物和设计图一模一样，不变形**：同样的深蓝黑长发、黑狐耳（粉色耳内）、同样的脸（金黄色眼睛，两只眼睛一样高）、红白和风上衣和白毛领、金色腰带和紫色流苏、米白金边短裙、**红色长筒袜和白护膝**、红棕色靴子；头的大小、身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **R 一定要横飞**（照 `refs/old_ult_*.png`）：起跳后身体整个横过来往前冲，头在最前面保持正常朝向（不要歪头、不要转成侧脸以外的角度），长发盖着背往后飘，九尾接在后面，前手往前伸、腿往后拖；身体从侧面看，衣服、腰带、流苏、短裙都要画对，不要糊成一团。
4. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；在空中的帧按浅色人影的高度。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- **画风照 oppi**（只看动作的画法和力度，不照它的衣服、颜色和比例）：每帧一个清楚的剪影，动作有力，手脚动起来时身体跟着顶住。

**像素规则**：每块 **6 像素**的方块，横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**不画法球、狐火、爱心、光效等任何特效**，不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

- 交付：`outputs/ahri-actions/<模板同名>.png`（26 张，都是 1536×1024，**和模板一样的两格布局**，每帧画在模板对应格子的位置上；不用的格子留空）；原始生成图原样放进 `outputs/ahri-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/ahri-actions/HANDOFF.md`（交付说明），再打包成 `outputs/ahri_actions_done.zip`。

## 附图（压缩包 `ahri_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（8 倍） | **每张都附，第一张**：人物、尾巴、衣服、比例、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第五张**：只用这些颜色 |
| `templates/<名>.png` | 两帧的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样两帧的彩色原图（放大） | **第三张**：看清动作（只照动作） |
| `refs/oppi_<动作>.png` | oppi 的阿狸同一种动作（4 倍） | **第四张**：动作画法（只看画法） |
| `sheets.json` | 每张模板是哪个动作的第几帧、每帧时长 | 对照 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/oppi_<动作>.png`、`refs/design_palette.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (8x: every square one pixel): a fox-girl mage with long dark navy-black hair, black fox ears with pink insides, golden-yellow eyes, a short red-and-white Korean-style robe with a white fur collar and gold trim, a gold sash with a violet tassel, a short cream skirt with gold edges, long RED stockings with white knee guards, red-brown boots, and NINE big fluffy WHITE tails with pale violet tips fanned out behind her, in 3/4 view facing right. Image 2 is a TEMPLATE of two animation frames of her <ACTION>, frames <N1>-<N2>: in each 768x1024 cell the PALE FIGURE is the pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (ear tips to soles). Image 3 is the same old frames in colour: copy ONLY their pose and motion (they are small and their colours and details are wrong). Image 4 is another pixel artist's version of this character doing this kind of move: copy only HOW IT IS ANIMATED (a strong readable silhouette, the body bracing into the move, hair and tails swinging), not its costume, colours or proportions. Image 5 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME two-cell layout as image 2: in each cell draw the character of image 1 in the pose of that cell's pale figure, at its place and size, soles on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar.
She must be EXACTLY image 1 in every frame: the same hair, ears, face with both golden eyes at the same height, the same robe, collar, sash, tassel, skirt, stockings and boots, image 5's colours only, the same head size, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
HER NINE TAILS STAY ATTACHED TO HER BODY: they grow from her lower back behind the skirt, their roots always touching her waist and back - NO gap between the tails and her body or hair, never a separate cloud floating behind her, never broken into pieces. One big fan of white tails with pale violet tips, as big as in image 1 (about 36-40 squares wide), visible in every frame, swinging with the move, the tips lagging behind the roots.
<EXTRA>
Always 3/4 view, face toward the front-right as in image 1.
THE PIXEL GRID: every square the SAME size, 6 px, on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing, no glow.
No orb, no fox-fire, no hearts, no sparkles, no effects, no ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<ACTION>` / `<N1>-<N2>` 照 `sheets.json` 的 `action` 和 `frames` 填。`<EXTRA>`：R（`ult_*`）的飞行帧填
`SPIRIT RUSH FLIES LEVEL: her whole body turned level, flying forward to the right, the head held up in front facing front-right, the long hair lying back over her back, the nine tails streaming straight back behind her hips in one bundle still joined to her waist, the far hand reaching forward, the legs trailing behind; draw the torso seen from the side (robe, sash, tassel, skirt), clean, not a heap.`，
其他动作留空。

## 交回前请检查

- 26 张，每张 1536×1024、两格布局，背景真透明（或纯白），没有模板的浅色人影、线和字。
- 每帧：**九尾连着后腰，尾巴和身体之间没有空隙**；脸朝右前方、两只眼睛一样高；头、手臂、腿的大小粗细和设计图一样；红长袜、白护膝、靴子和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- R 的飞行帧是横着飞的，头在最前、尾巴和头发往后拖。
- 平A 第 4 帧、Q 第 4 帧、E 第 3 帧手朝前方伸出。
- 最后写 `outputs/ahri-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/ahri_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读原始生成图（不读导出图），照 `tools/art/casts_lux_hd.py` 的办法修：按站直那帧的眼睛到地面的高度定每张的比例，头换成设计图的头（对准近侧眼睛，挡在脸前的手臂保留），脚站稳；逐帧查**尾巴和身体有没有缝**、尾巴大小；平A、Q、E 的出手高度照出手帧的手重算。
