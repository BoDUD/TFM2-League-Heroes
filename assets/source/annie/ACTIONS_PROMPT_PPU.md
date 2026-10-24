# 安妮：全部动作逐帧重画（给 Codex 的提示词）

> 安妮的定稿设计图（`refs/design.png`，8 倍放大，一格 = 一个像素块；`refs/design_1x.png` 是 1 倍原图，44 × 75 格）。请把她的**七个动作每一帧都重新画整个人**：跑步、平A、Q、W、R、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏），**画法照 oppi 的安妮**（`refs/oppi_<动作>.png`）。待机不用画。
>
> **提伯斯的位置不照旧版**：旧版是把提伯斯抱在胸前，新设计是**近侧的手（画面左边、她身后那只）拎着提伯斯的一只胳膊**，远侧的手空着。所以：
> - **所有的火都由远侧那只空手放**（平A、Q、W）；
> - **提伯斯一直挂在近侧的手上**，跟着手和身体晃，只有大招时被扔出去；
> - 每张模板要画的提伯斯位置写在 `sheets.json` 的 `tibbers` 里（下面提示词的 `<TIBBERS>`）。
>
> 一共 **22 张模板**（`templates/*.png`，每张 1536×1024，一张两帧，每格 768×1024），41 帧：
> - 跑步 `run_1..4`（8 帧）：英雄联盟的小跑，身体略前倾，两条腿一前一后交替迈步；提伯斯在近侧手里前后甩
> - 平A `attack_1..3`（5 帧）：远侧的手收到肩膀，**第 4 帧往前一甩**（扔出小火球），收回
> - Q 碎裂之火 `skill_1..3`（6 帧）：远侧的手从头顶抡下来，**第 4 帧往前扔出大火球**，往前迈半步，收回
> - W 焚烧 `skill2_1..4`（7 帧）：**第 3 帧起远侧的手掌往前推**，身体前倾，停 3 帧（手心喷出扇形火），收回
> - R 提伯斯之怒 `ult_1..4`（7 帧）：近侧的手把提伯斯往后上方抡，**第 3 帧提伯斯离手往前上方飞出去**，之后两只手都空着，远侧的手往前一指
> - 受击 `hit_1`（2 帧）：被打得往后一缩，提伯斯被甩起来
> - 死亡 `dead_1..3`（6 帧）：被击飞，提伯斯脱手飞出去 → 仰面倒地 → 躺着；提伯斯掉在她旁边地上
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的安妮；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站直时从猫耳尖到脚底的高度（75 格）。旧版是 1 倍小图、颜色和细节都不对，提伯斯的位置也不对，**只照它的身体动作**，人物本身全部照设计图。

**最重要的四条：**

1. **人物和设计图一模一样，不变形**：同样的洋红短发和齐刘海、粉色猫耳发箍、同样的脸（绿色眼睛，两只眼睛一样高）、紫色泡泡袖连衣裙、蓝色菱格纹背心、白翻领、暗红手镯、粉色兔子背包、紫色蓬蓬短裙、紫色条纹长袜、黑皮鞋；头的大小、身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
2. **提伯斯每帧都和设计图里一样大、一样的样子**（棕色泰迪熊、补丁、缝线、纽扣眼睛），挂在近侧手上时**手一直握着他的胳膊**，熊和手之间不能有空隙，也不能飘在手外面。位置照每张的 `<TIBBERS>`。
3. **放火的永远是远侧那只空手**：平A、Q、W 出手那一帧手往前（画面右边）伸出去，手要画清楚（手指张开或握拳都可以）。R 扔出提伯斯以后两只手都是空的。
4. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；在空中、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- **画风照 oppi**（只看动作的画法和力度，不照它的衣服、颜色和比例）：每帧一个清楚的剪影，动作有力，手脚动起来时身体跟着顶住，头发和裙摆跟着动作晃。

**像素规则**：每块 **7 像素**的方块，横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**不画火球、火焰、护盾、光效等任何特效**，不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

- 交付：`outputs/annie-actions/<模板同名>.png`（22 张，都是 1536×1024，**和模板一样的两格布局**，每帧画在模板对应格子的位置上；不用的格子留空）；原始生成图原样放进 `outputs/annie-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/annie-actions/HANDOFF.md`（交付说明），再打包成 `outputs/annie_actions_done.zip`。

## 附图（压缩包 `annie_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（8 倍） | **每张都附，第一张**：人物、提伯斯、衣服、比例、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第五张**：只用这些颜色 |
| `templates/<名>.png` | 两帧的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样两帧的彩色原图（放大） | **第三张**：看清身体动作（提伯斯的位置不照它） |
| `refs/oppi_<动作>.png` | oppi 的安妮同一种动作（4 倍） | **第四张**：动作画法（只看画法） |
| `sheets.json` | 每张模板是哪个动作的第几帧、每帧时长、提伯斯在哪 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/oppi_<动作>.png`、`refs/design_palette.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (8x: every square one pixel): a little girl fire mage with short magenta hair and straight bangs, a pink cat-ear headband, green eyes, a purple dress with puffed sleeves under a blue argyle vest, a small white collar, a dark red bracelet, a small pink bunny backpack, a full purple skirt, purple striped stockings and black shoes, in 3/4 view facing right; her NEAR hand (image left) holds her brown teddy bear TIBBERS by one arm, her FAR hand is free. Image 2 is a TEMPLATE of two animation frames of her <ACTION>, frames <N1>-<N2>: in each 768x1024 cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (cat-ear tips to soles). Image 3 is the same old frames in colour: copy ONLY their body pose and motion (they are small, their colours and details are wrong, and in them she hugs the bear in front - DO NOT copy where the bear is). Image 4 is another pixel artist's version of this character doing this kind of move: copy only HOW IT IS ANIMATED (a strong readable silhouette, the body bracing into the move, hair and skirt swinging), not its costume, colours or proportions. Image 5 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME two-cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, soles on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar.
She must be EXACTLY image 1 in every frame: the same hair, headband, face with both green eyes at the same height, the same dress, vest, collar, bracelet, backpack, skirt, stockings and shoes, image 5's colours only, the same head size, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE FAR (FREE) HAND CASTS: every spell is thrown or pushed from her far hand, reaching forward to the right on the casting frame, the hand clearly drawn.
TIBBERS: the same bear as in image 1 (the same size, brown with patches, stitches and a button eye) in every frame he is in; while she holds him her near hand GRIPS HIS ARM - no gap between hand and bear, never floating loose. <TIBBERS>
Always 3/4 view, face toward the front-right as in image 1.
THE PIXEL GRID: every square the SAME size, 7 px, on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing, no glow.
No fire, no fireball, no flames, no shield, no sparkles, no effects, no ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<ACTION>`、`<N1>-<N2>`、`<TIBBERS>` 照 `sheets.json` 的 `action`、`frames`、`tibbers` 填。

## 交回前请检查

- 22 张，每张 1536×1024、两格布局，背景真透明（或纯白），没有模板的浅色人影、线和字。
- 每帧：脸朝右前方、两只眼睛一样高；头、手臂、腿的大小粗细和设计图一样；衣服、背包、条纹袜、皮鞋和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- 提伯斯：除了 R 第 3 帧以后和死亡，都挂在近侧的手上、手握着他的胳膊，大小和设计图一样；R 第 3 帧飞出去、第 4 帧起两手空；死亡第 1–2 帧飞出去，之后躺在她旁边。
- 平A 第 4 帧、Q 第 4 帧、W 第 3–6 帧远侧的手朝前方伸出。
- 最后写 `outputs/annie-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/annie_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读原始生成图（不读导出图），照 `tools/art/casts_ahri_hd.py` 的办法修：每张按头的大小 × 身高定比例，头换成设计图修好脸的头（缩小模板匹配，不要在头周围清一圈），脚站稳；逐帧查**提伯斯和手有没有缝**、提伯斯大小；平A、Q 的出手高度照出手帧的手重算（火球是追踪的，出手点不要高出脚下中心点 8 px 以上）。
- 跑步要和英雄联盟的节奏一样，腿照待机的颜色、两只脚轮流在前；做完连同待机、选人卡轮播一起给用户审。
