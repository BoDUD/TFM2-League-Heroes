# 炼金（辛吉德）：跑步逐帧重画（给 Codex 的提示词）

> 用户：「炼金的跑步动作是不是让codex重画一下比较好」。
>
> 现在游戏里的跑步（8 帧 × 100 毫秒）：**两只脚基本钉在原地**，只有前脚跟抬一下落一下；背上的药罐、近侧竖着的盾、远侧拿药瓶的手
> 8 帧几乎不动，整个人只是上下晃——看起来像原地跺脚、往前平移。
>
> 英雄联盟的 `singed_run`（一圈 0.967 秒、两步）：**弓着身子往前倾**，两条腿**大步交替**，后腿往后踢起，前腿抬膝迈步，空着的手跟着
> 步子前后摆。这次按设计图把跑步的 8 帧（每 121 毫秒一帧）逐帧重画。

## 交付

- 一共 **3 张模板**（`templates/run_1.png` 第 1–3 帧、`run_2.png` 第 4–6 帧、`run_3.png` 第 7–8 帧，第三格空着），每张 1536×1024，
  一张三格，每格 512×1024。
- 交付 `outputs/singed-run/run_1.png`、`run_2.png`、`run_3.png`：都是 1536×1024，**和模板一样的三格布局**，每帧画在模板对应格子的位置上。
  `run_3.png` 的第三格留空（透明）。
- 原始生成图原样放进 `outputs/singed-run/raw/`，不要裁、不要缩放。

**每一格里**：

- **灰色横线是地面**，短竖线是他的站位点。**左边的灰色竖条是他站直时的高度**：顶端是药罐盖子顶（62 格），短横线是光头顶（51 格）。
- **火柴人是英雄联盟这一帧的骨骼**，已经按他的身材缩放过：
  - **蓝色是近侧的腿**（画面前面那条），**灰色是远侧的腿**；腿的末端先到**脚踝**，再一小段到**脚尖**；
  - 深灰的竖线是身体（骨盆到脖子）；
  - **黑圈是他的光头（不算药罐）该在的位置和大小**；
  - **绿圈是远侧那只手握着的绿色药瓶该在的位置**，浅绿线是那条手臂；
  - 有的帧两只脚都离地（跑步腾空），就按火柴人的高度画，不要硬拉到地上；踩地的那只脚，鞋底贴着地面线。
  - 火柴人只定**位置和大小**。具体姿势（身体怎么倾、腿怎么踢）看 `refs/league_run_<同名>.png` 里同一帧的渲染图。
- **注意盾和药瓶**：英雄联盟的模型把盾举在身前、药瓶在另一只手里；**我们的设计不一样，照设计图**：
  - **近侧（画面左）的手竖着举带刺的盾**：盾一直竖着，跟着身体一起起伏、前倾，不前后摆；
  - **远侧（画面右）的手握着药瓶**，照绿圈的位置前后摆。

**跑步要注意的**：

- 8 帧是**一圈两步**：第 1–4 帧和第 5–8 帧各迈一步，两条腿要**交替、交叉**着走，腿的远近照火柴人的颜色（蓝近灰远）。
- 每一步都是大步：后腿往后踢起，前腿抬膝往前迈；身体一直往前倾、微微弓着背。
- **药罐背在背上，跟着身体一起动**，不自己晃。
- **8 帧的人一样大**：头、药罐、盾、身体、手臂、腿的长短粗细每帧都和设计图一样，只是摆法不同；不拉长、不压扁、不变粗变细。
- **两只手都要在**：盾后面露出近侧手的几根指头（和设计图一样），远侧手握着药瓶。

**人物必须和设计图一模一样**（`refs/design_8x.png` 8 倍、`refs/design_1x.png` 1 倍原图、`refs/design_palette.png` 全部颜色）：

- 外观：苍白的光头（两只眼睛一样高）、灰蓝的围巾面罩、背上**亮绿的圆药罐**（深灰铆钉、顶上深灰金属盖）、红夹克和交叉的金色扣带、
  两个带刺的红金护肩、近侧竖着的**灰绿带刺盾**、远侧暗红棕的手套和**圆圆的亮绿药瓶**、棕皮带和小绿药管、深蓝细腿、带尖刺的
  红棕大靴子。**只用调色板里的颜色**。
- 朝向：四分之三侧身、**脸朝右前方**，和设计图一样。

**画法照** `refs/style_run.png`（我们包里另一个英雄用户认可过的跑步，4 倍；**只看跑步的画法和力度**：剪影清楚、腿的交替一眼能看出来；
**不要照它的衣服、颜色和比例**）。

**像素规则**：

- 每块 **8 像素**的方块，横平竖直对齐成网格。
- 外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂。
- 不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。
- **不画特效、毒雾、地面、影子、文字**；模板上的线、圈、字、格子边框**全部不要留在交付图里**。

**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明的话，用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

## 附图（压缩包 `singed_run_pack.zip`，解压到一个新的文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design_8x.png` | 设计图 8 倍（游戏里的高清待机第 0 帧） | **每张都附，第一张**：人物的样子、比例、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | 只用这些颜色 |
| `templates/run_<k>.png` | 三帧的模板 | **第二张**：每帧的位置、大小、头和药瓶在哪 |
| `refs/league_run_<k>.png` | 英雄联盟同样几帧的渲染（Q 版模型） | **第三张**：每帧腿和身体的姿势 |
| `refs/style_run.png` | 我们包里另一个英雄认可过的跑步（4 倍） | **第四张**：跑步的画法（只看画法） |
| `sheets.json` | 每张模板是第几帧 | 对照 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design_8x.png`、`templates/run_<k>.png`、`refs/league_run_<k>.png`、`refs/style_run.png`。`<N1>-<N3>` 按 `sheets.json` 填：
run_1 是 1-3，run_2 是 4-6，run_3 是 7-8（第三格留空）。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (8x: every square one pixel): Singed, a hunched mad chemist in 3/4 view facing right: a pale bald head with both eyes at the same height, a grey-blue scarf over his mouth, a round bright green chem-tank on his back (dark grey rivets, a dark grey metal cap) rising behind his shoulders, a red jacket with two crossing gold straps, two spiked red-and-gold shoulder pads, on his NEAR side (left in the picture) a tall grey-green spiked shield held upright by his near arm (only a few fingers show behind it), his FAR hand (right in the picture) in a dark red-brown glove holding a round bright green potion flask, a brown belt with small green vials, thin dark blue legs and big spiked red-brown boots. Image 2 is a TEMPLATE of animation frames <N1>-<N3> of his RUN CYCLE (one loop of two strides, 8 frames in all): in each 512x1024 cell the grey horizontal line is the ground, the short tick is his standing point, the grey bar on the left is his height standing (its top = the top of the tank cap, the short mark = the top of his bald head); the stick figure is the game's skeleton of that frame fitted to his build (blue = his near leg, grey = his far leg; each leg ends at the ankle and then a short stroke to the toe; the dark line is his body from the pelvis to the neck; the black circle = where his bald head goes and how big it is; the green circle = where the green flask in his far hand goes, the light green line = that arm). In the frames where both feet are off the ground he is in mid-stride: keep the feet as high as drawn; a planted foot's sole sits on the ground line. Image 3 is the same frames from the game's 3D run animation (a chibi model of him): copy each frame's POSE OF THE LEGS AND BODY from it - the hunched forward lean, the long stride, the back leg kicked up behind, the front knee lifted. Image 3's model holds the shield in front and the flask in the other hand: IGNORE that and keep image 1's arrangement - the shield upright on his near side, moving only with his body, and the flask in his far hand swinging forward and back as the green circle shows. Image 4 is another approved pixel-art run from the same game: copy only HOW IT IS ANIMATED (a strong readable silhouette, the legs clearly alternating), not its character.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if transparency is impossible, a flat pure white background with no glow and no shadow), the SAME three-cell layout as image 2: in each used cell draw the character of image 1 in that frame's pose, placed and sized by the stick figure of image 2: his bald head where the black circle is and as big, the green flask inside the green circle. Leave any unused cell empty.
He must be EXACTLY the character of image 1 in every frame: the same head, face and scarf, the same tank on his back (it moves with his body, it does not swing on its own), the same shield and shoulder pads, the same colours (image 1's colours only), the same head size, and his arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned). Both hands are always there. The same size in every frame. Always the 3/4 view facing right, as image 1.
THE PIXEL GRID: every square the SAME size, 8 px, aligned on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material, no stray single odd squares, no dithering, no gradients, no blur, no anti-aliasing, no glow.
No effects, no poison cloud, no ground, no shadow, no text. Remove every template mark: no lines, circles, stick figures, numbers or cell borders in the result.
```

## 回来以后（我们这边）

1. 读回 3 张图，按格子切出 8 帧，每 8 像素读回一格（高清帧）。
2. 每帧的头、药罐、盾和设计图比大小，差了就单独缩放；脸每帧不一样就锁成同一张；数两只手都在。
3. 鞋底放到地面上（腾空的帧按游戏里看着顺来定）。
4. 做成跑步（8 帧 × 121 毫秒，照英雄联盟），出"现在 | 新"的像素原样动图给用户看，点头才装。
