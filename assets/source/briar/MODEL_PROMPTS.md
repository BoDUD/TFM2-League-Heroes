# 贝蕾亚：按用户的图重画造型（给 Codex 的提示词）

> **这一轮只画造型图（A、B 两版），不画动作。** 用户给的图是 `briar/briar_source.png`（就是你之前生成的 briar_B_generated.png），要照它做游戏里的贝蕾亚。
> - 原图是不规则的约 7 像素网格（59×71 格）。直接按行列删减缩到游戏尺寸（约 45 格）会把头发、眼睛、金边切碎（`briar/size_guide.png` 最右），你上次 46 格的缩小版是面积平均缩的，也糊了，两种都不能用。
> - 所以请先画成**约 76 格高**的干净像素画（宝石顶到脚底，游戏尺寸的约 1.7 倍），Claude 再按行列删减缩到游戏尺寸、整理后给用户挑。
> - 两版：A 照原图比例；B 按原版英雄的 Q 版比例（头约占身高（头顶到脚底）的三分之一，腿稍长），枷锁大小不变。
> - 交回前请整理成严格网格：每个像素一个对齐的 8×8 纯色块，透明度只有 0/255，颜色不超过 32 种。附 `HANDOFF.md`（用了哪条提示词、哪里没做到）和各版的原尺寸图 `briar_design_A_1x.png` / `_B_1x.png`。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `briar/briar_source.png` | 用户选定的造型图 | 长相、颜色、姿势都照它 |
| `briar/briar_on_grid_8x.png` | 同一张图按它自己的网格取格（59×71 格）并压平颜色，8 倍 | 看比例和配色；它是 1.55 倍大小，这次要画到约 76 格 |
| `briar/size_guide.png` | 游戏尺寸（8 倍）的原版剑士、包里的李青/卢锡安/莫甘娜，和原图直接缩小的结果 | 只看最终大小关系（缩小版是反面例子） |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，8 倍 | 干净程度：大块平涂、颜色少、形状清楚 |

## 规则（来自对最好的社区包的测量）

- **只描一圈**：外轮廓 1 格近黑描边，描边内侧那一格用材质自己最暗的颜色，**不能再是黑**；不拿黑色当阴影（枷锁是黑铁，用带颜色的深灰，和描边分开）。
- 每种材质 4–5 个平涂色阶，暗部带颜色，全图不超过 32 色。
- 大块纯色，不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块。
- **每个细节至少 2 格宽**：之后要按行列删减缩小，1 格宽的细节会被删掉（金边、发梢红色、腿上的束带都至少 2 格）。
- 眼睛：两只眼睛在同一行，每只至少 3 格宽；眼白是冷色的冰白，**只用在眼睛上**（头发是暖白、皮肤是淡粉，不能和眼睛同色）。
- 嘴：脸中线上 2–3 格深红，带 1 格白色獠牙；脸颊、下巴不要有别的深色格（之前的英雄出现过像歪嘴笑的阴影）。
- 3/4 正面朝右，站在一条平线上（最低一行是脚底），脚底以下什么都不能有（游戏在脚下画血条）。背景透明（做不到时用 `#FF00FF`）。
- 枷锁很宽：保持原图的宽度就好，不要再加宽；两只手从枷锁两端的铁箍里伸出来，看得清。

## 提示词：`briar_design_A.png`、`briar_design_B.png`

```text
Three attached images. FIRST: the approved look of this character (briar_source.png) - copy it exactly: the shapes, colours, face, pose and details. SECOND: the same picture put on its own square grid (59 x 71 squares) - use it for proportions and colours. THIRD: official heroes of the game Teamfight Manager 2 at 8x - match their cleanliness: big flat areas, few colours, bold readable shapes.
Task: redraw the character of the FIRST image as clean hand-made pixel art about 76 pixels tall from the top of the pillory's gem to the soles, drawn as true low-resolution pixel art and shown enlarged 8x.
The character: Briar from League of Legends as a chibi: messy chin-length WHITE hair (warm white and pale warm greys) whose lower ends are rose-red on both sides of the face; very pale skin; two big glowing MILKY-WHITE eyes with no pupils and near-black lashes, a small open grin with one white fang; a torn black leather bodice and short black skirt with gold straps and buckles, a torn crimson under-layer at the hips; bare pale legs with dark shackle bands round the calves; bare clawed feet. Her signature: a big BLACK IRON PILLORY behind her head and shoulders - two thick arches with gold edges and six short gold spikes, a RED diamond gem in a gold setting at the top centre - whose two lower ends are cuffs locking her wrists at shoulder height, her small pale clawed hands sticking out beside them.
Pixel rules (most important, measured from the best community pack for this game): true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency. ONE 1-square near-black outline around the whole silhouette; the squares just inside it are the material's own darkest shade - never a second ring of black, and black is never used as a shadow. Every material 4-5 flat shades with coloured (hue-shifted) darks, at most 32 colours in total; big flat areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area. Every detail at least 2 squares wide (this drawing is shrunk to game size by deleting whole rows and columns, so 1-square details can vanish).
Face: both eyes on the same rows, each at least 3 squares wide and 3 tall at this size (a near-black lash row on top, then milky white with a pale-blue glint); the near eye (left, the character faces right) a little wider than the far one; one row of skin between the eyes and the fringe; the eye white is a cool ice-white used NOWHERE else (the hair is warm white, the skin pale pink). Mouth: 2-3 squares of dark red with one white fang square, on the face's middle line under the eyes; no other dark squares on the cheeks or the jaw.
Two versions: A: the FIRST image's proportions. B: official-hero chibi proportions - the head about a third of the height from the crown to the soles, slightly longer legs; the same pillory, face and colours.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, standing on a flat line - the lowest row is the soles; nothing below the soles (the game draws the health bar there).
Layout: one square image per version, 1024x1024 (a 128x128-square canvas at 8x), the character centred horizontally with the soles about 16 squares above the bottom. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 76 squares tall, every square 8x8 on one grid, at most 32 colours, one outline ring only, both eyes level and clearly visible, the eye white used only in the eyes, nothing below the soles.
```

## Claude 收到后（给 Claude 看）

- 解压到临时目录，`regrid` → `seam` 缩到约 45 行（宝石顶到脚底）→ 手修脸和眼睛（两眼同高同大、眼白只用在眼睛）→ `one_outline` 清描边 → 游戏尺寸预览（和原版英雄、包里英雄比大小）给用户挑 A/B。
- 用户认可后按 18 个英雄重画那一轮的动作帧包格式出贝蕾亚的动作帧包（待机由造型图直接生成，参考图来自英雄联盟原版动作的游戏尺寸渲染）。
