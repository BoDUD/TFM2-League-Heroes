# 阿卡丽：按用户的图画造型（给 Codex 的提示词）

> **这一轮只画造型图（A、B 两版），不画动作。** 用户给的图是 `akali/akali_source.png`（你之前生成的 akali-model.png），要照它做游戏里的阿卡丽。
> - 原图是约 4 像素的网格，约 330 格高。直接缩到游戏尺寸（约 46 格）会把马尾、眼睛、镰刀切碎（`akali/size_guide.png` 最右是直接缩小的样子，不能用）。
> - 所以请先画成**约 80 格高**的干净像素画（头顶到脚底，不算马尾尖，游戏尺寸的约 1.7 倍），Claude 再按行列删减缩到游戏尺寸、整理后给用户挑。
> - 两版：A 照原图比例；B 按原版英雄的 Q 版比例（头约占身高（头顶到脚底）的三分之一，腿稍短），马尾和武器大小不变。
> - 交回前请整理成严格网格：每个像素一个对齐的 8×8 纯色块，透明度只有 0/255，颜色不超过 32 种。附 `HANDOFF.md`（用了哪条提示词、哪里没做到）和各版的原尺寸图 `akali_design_A_1x.png` / `_B_1x.png`。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `akali/akali_source.png` | 用户选定的造型图 | 长相、颜色、姿势、武器都照它 |
| `akali/size_guide.png` | 游戏尺寸（8 倍）：原版忍者、双刀、猎人、剑士，包里的李青、永恩、阿狸，最右是原图直接缩小的结果 | 只看最终大小关系（最右是反面例子） |
| `akali/face_guide.png` | 原版忍者（蒙面）、双刀（马尾）、猎人（镰刀）的头，12 倍 | 蒙面时眼睛怎么画得清楚 |
| `style/tfm2_style_ref_swordsman.png`、`style/tfm2_style_ref_martial.png` | 团战经理2 原版英雄，8 倍 | 干净程度：大块平涂、颜色少、形状清楚 |

## 规则（来自对最好的社区包的测量）

- **只描一圈**：外轮廓 1 格近黑描边，描边内侧那一格用材质自己最暗的颜色，**不能再是黑**；不拿黑色当阴影。头发是黑发：用带颜色的蓝黑和深灰画，和描边分开。
- 每种材质 4–5 个平涂色阶，暗部带颜色，全图不超过 32 色。
- 大块纯色，不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块。
- **每个细节至少 2 格宽**：之后要按行列删减缩小，1 格宽的细节会被删掉（金护腕、纹身、腰布的螺旋、绷带、苦无、镰刀刃都至少 2 格）。
- 眼睛：蒙着面，只露眼睛——两只眼睛在同一行，每只至少 3 格宽、3 格高，上面一行黑色眼线（外侧带一点上挑），下面是白色高光 + 棕色瞳孔；近眼（左）比远眼稍宽；眼睛和刘海之间、眼睛和面罩上沿之间各留一行皮肤；眼白和棕色瞳孔**只用在眼睛上**。
- 面罩：深绿平涂，最多一道浅色褶，不画嘴。
- 3/4 正面朝右，站在一条平线上（最低一行是脚底），脚底以下什么都不能有（游戏在脚下画血条）：苦无、镰刀都要在脚底以上。背景透明（做不到时用 `#FF00FF`）。

## 提示词：`akali_design_A.png`、`akali_design_B.png`

```text
Four attached images. FIRST: the approved look of this character (akali_source.png) - copy it exactly: the shapes, colours, face, pose, weapons and details. SECOND: game-size heroes at 8x (size_guide.png) - use it ONLY for the size relation; its rightmost figure is the FIRST image shrunk straight to game size, the result we must avoid. THIRD: masked and ponytailed heroes of the game at 12x (face_guide.png) - how eyes read above a mask. FOURTH: official heroes of the game Teamfight Manager 2 at 8x - match their cleanliness: big flat areas, few colours, bold readable shapes.
Task: redraw the character of the FIRST image as clean hand-made pixel art about 80 pixels tall from the crown to the soles (the ponytail may rise above that), drawn as true low-resolution pixel art and shown enlarged 8x.
The character: Akali from League of Legends as a chibi ninja: a huge spiky BLACK ponytail (blue-black and dark grey strands) rising from the back of her head in a dark green band and sweeping back behind her, black hair with a side fringe framing the face; a DARK GREEN cloth mask over her nose and mouth; tan skin; sharp brown eyes with a black winged liner; a sleeveless moss-green wrap top with dark green trim cut above a bare toned midriff; a dark tattoo swirl on her near upper arm; dark fingerless gloves, bandaged forearms with gold bracers; a cream cloth sash tied at the hip with a gold ring, a green loincloth panel with a pale spiral and a small gold tip hanging in front; baggy charcoal-purple trousers gathered at the knees, bandaged shins in cream and green, dark ninja shoes. Weapons: a steel KUNAI held point-down in her near hand (image left), a KAMA (a short wrapped handle with a big steel crescent blade) in her far hand (image right).
Pixel rules (most important, measured from the best community pack for this game): true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency. ONE 1-square near-black outline around the whole silhouette; the squares just inside it are the material's own darkest shade - never a second ring of black, and black is never used as a shadow (her black hair is drawn in coloured blue-black and dark greys, apart from the outline). Every material 4-5 flat shades with coloured (hue-shifted) darks, at most 32 colours in total; big flat areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area. Every detail at least 2 squares wide (this drawing is shrunk to game size by deleting whole rows and columns, so 1-square details can vanish): the gold bracers, the tattoo, the loincloth spiral, the bandage bands, the kunai and the kama's blade.
Face (it must read at game size): the mask covers from under the eyes to the chin, so only the eyes show - make them clear: both eyes on the same rows, each at least 3 squares wide and 3 tall here (a near-black liner row on top with a small wing at the outer end, then a white glint beside a warm brown iris), the near eye (left, she faces right) a little wider than the far one, one row of skin between the eyes and the fringe and one row of skin between the eyes and the mask's top edge; the iris brown and the eye white are used NOWHERE else (the skin is tan, the trim gold). The mask is flat dark green with one lighter fold, no mouth line.
Two versions: A: the FIRST image's proportions. B: official-hero chibi proportions - the head (without the ponytail) about a third of the height from the crown to the soles, a slightly bigger face and eyes, slightly shorter legs; the same ponytail, clothes, weapons and colours.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, standing on a flat line - the lowest row is the soles; nothing below the soles (the game draws the health bar there): the kunai and the kama's blade end above that line.
Layout: one square image per version, 1024x1024 (a 128x128-square canvas at 8x), the character centred horizontally with the soles about 16 squares above the bottom. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 80 squares from the crown to the soles, every square 8x8 on one grid, at most 32 colours, one outline ring only, both eyes level and clearly visible above the mask, the eye colours used only in the eyes, nothing below the soles.
```

## Claude 收到后（给 Claude 看）

- 解压到临时目录，`regrid` → `seam` 缩到约 46 行（头顶到脚底）→ 手修眼睛（两眼同高同大、眼白和瞳孔色只用在眼睛）→ `one_outline` 清描边 → 游戏尺寸预览（和原版英雄、包里英雄比大小，暗色卡片上也看）给用户挑 A/B。
- 用户认可后出动作帧包（待机由造型图直接生成，参考图来自英雄联盟原版动作的游戏尺寸渲染，眼睛颜色只用在眼睛上，每帧贴回定稿的头）。
