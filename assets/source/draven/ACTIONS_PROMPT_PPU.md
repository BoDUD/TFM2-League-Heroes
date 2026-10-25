# 德莱文：全部动作逐帧重画（给 Codex 的提示词）

> 德莱文的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，114 × 76 格，每格一个像素）是用户选定的那张：双斧垂在身体两侧、斧刃朝外。请把他的**七个动作每一帧都重新画整个人**：跑步、普攻、Q、E、R、受击、死亡。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；Q 的第 4 帧就是待机姿势，也不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：往后梳成尖刺的深红棕头发、金色头箍和青绿宝石、八字胡、白青护肩、赤裸的胸膛和交叉皮带、红色护腕、红色长布条、深色长裤和银灰护甲、靴子。
> - **两把飞斧照设计图**：银白色弯刃、红金装饰、斧柄握在手里。
> - 不画任何特效（旋转的残影、速度线、火花、尘土）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、斧子怎么拿（下面提示词的 `<WEAPONS>`）。
> - 跑步 `run_*`：大摇大摆地快跑，两手各拿一把斧张在身体两侧。**左右腿每半圈要明显地交换**（一会儿左脚在前、一会儿右脚在前），**身体随步子上下起伏**；8 帧不能是同一个姿势。
> - 普攻 `attack_*`：把一把斧举过肩膀往前扔出去，再准备下一把。
> - Q `skill_*`：近侧的手（画面左边）把斧子转起来接住。
> - E `skill2_*`：双斧挥起往前扔出去，扔完往前跨一步。
> - R `ult_*`：双斧高举过头，再往前猛扔、身体深深前扑。
> - 受击 `hit_*`：被打得往后一缩。
> - 死亡 `dead_*`：双臂扬起往后踉跄、倒下，最后躺在地上。
> - **斧子跟着浅色人影走**：浅色人影手里有斧就画斧，**手是空的就画空手**（斧子已经扔出去了，不要画在空中）。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的德莱文；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站直时从头顶到脚底的高度（76 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：从发尖到下巴约 **22 格**（设计图里的头），**不要画小、也不要画大**。上一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的发型、脸、胡子、头箍、护肩、皮带、布条和护甲；**体格和设计图一样壮**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **斧子跟着浅色人影**：有斧画斧、空手画空手，同一只手的斧子不要换到另一只手；斧刃形状和设计图一样，不要变形。
4. **跑步要有交替**：两条腿轮流在前，身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；前扑、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- 手臂和身体之间、两腿之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 7 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**脸上的眼睛、胡子、牙齿各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

- 交付：`outputs/draven-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/draven-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/draven-actions/HANDOFF.md`（交付说明），再打包成 `outputs/draven_actions_done.zip`。

## 附图（压缩包 `draven_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、斧子、衣服、比例、头的大小、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作和斧子在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、斧子怎么拿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a muscular, swaggering axe-wielder with dark red-brown hair swept back in spikes, a gold headband with a teal gem, a thick moustache and a grin, white-and-teal fur shoulder guards, a bare chest with crossed dark straps, red wrist wraps, a long red cloth at the waist, dark trousers with silver-grey armour plates, and a silver-white spinning axe in each hand held low at his sides, in 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of his <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (his old animation frame scaled to his height), the grey horizontal line is the ground, the short tick his standing point, the grey bar on the left his height standing (top of the hair to soles). Image 3 is the same old frame(s) in colour: copy ONLY their body pose, motion and where the axes are - the old costume is wrong. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, soles on the ground line at the standing point when he stands. One scale for the whole sheet, set by the grey bar.
He must be EXACTLY image 1 in every frame: the same hair, face, moustache, headband, shoulder guards, straps, cloth and armour, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 22 squares from the top of the hair to the chin) - never smaller, never bigger. The build as sturdy as image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE AXES are image 1's, never reshaped. <WEAPONS>
NO EFFECTS AT ALL: no spin blur, no speed lines, no sparks, no dust.
Always 3/4 view, face toward the front-right as in image 1; the eyes, moustache and teeth each a clear shape.
THE PIXEL GRID: every square the size of the template's (7 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<WEAPONS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons` 填。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字。
- **每帧的头和设计图一样大**（发尖到下巴约 22 格）；发型、脸、衣服和设计图一样，脸朝右前方；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **斧子跟着浅色人影**：有斧画斧、空手画空手；斧刃形状不变。
- **跑步两腿轮流在前、身体有起伏**，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/draven-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/draven_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读原始生成图（不读导出图），照 `tools/art/casts_samira_hd.py` 的办法按 7 像素一格、从站位点和地面线读回到设计图的格子上；`same_as_design` 的帧用设计图。
- **逐帧量头顶到下巴**（和设计图的 22 格比，差一格以上的帧要处理，莎弥拉的教训）、**逐帧查斧子在哪只手**、**跑步查换腿和起伏**。
- 旧版的特效锚点（飞斧出手点、接斧点）按新的手的位置重新定位；做完连同待机、选人卡轮播一起给用户审。
