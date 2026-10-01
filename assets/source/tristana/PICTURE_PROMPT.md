# 崔丝塔娜（Tristana）原画提示词包 · 第 0 步

**给用户（中文说明）**：崔丝塔娜还没有原画。请把整个 zip 交给 Codex，它按下面的英文提示词画两张原画，
两张是同一个姿势（英雄联盟的待机：半蹲、大炮夹在腰间朝前），只是镜头角度不同：
A = 3/4 正面（脸最清楚，炮口朝右前方、炮身有透视缩短），
B = 转向侧面一些（两只眼睛仍然看得见，炮身整根朝右，游戏里小尺寸时炮的轮廓更清楚）。
你挑一张，我再按它写游戏尺寸（约 40 行，护目镜算在内）的造型包（第 1 步）。
Codex 交付：`outputs/tristana-model-A.png`、`outputs/tristana-model-B.png`（1536x1024 横图，透明背景）。

附图：
- `01_style_akali.png`、`02_style_vayne.png`、`03_style_nami.png`：你之前让 Codex 画的原画，只当**画风**参照。
- `04_style_veigar_yordle.png`：Codex 画的维迦原画（你选的 A），约德尔人（大头、短身）在这个画风里的样子。
- `05_league_front.png`：英雄联盟经典皮肤的游戏内模型，待机姿势，3/4 正面朝右 = 原画 A 的角度和姿势。
- `06_league_head.png`：头部特写（护目镜、白发、大耳朵、金色大眼睛）。
- `07_league_pose_B.png`：同一个待机姿势转向侧面一些 = 原画 B 的角度。
- `08_league_side.png`：接近侧面，看大炮整根的结构和耳朵的轮廓。
- `09_league_back.png`：背面，看后脑的白发、护目镜的皮带和炮尾。
- `10_league_splash.png`：加载画面原画，只参照脸和气质（自信、调皮），服装配色以游戏内模型为准。

---

## Prompt (English, for Codex image generation)

Draw **Tristana, the Yordle Gunner** from League of Legends, in her **classic in-game model** (the lavender
yordle with white hair, aviator goggles and the huge bronze cannon "Boomer" of `05_league_front.png`), as a
full-body character picture for a pixel-art game. Make two pictures, A and B: **the same pose, the same
costume, only the camera angle differs.**

**Style** - copy the attached pictures `01_style_akali.png`, `02_style_vayne.png`, `03_style_nami.png` and
`04_style_veigar_yordle.png` exactly: a detailed pixel-art illustration, a crisp dark outline around every
shape, 3-5 flat shades per material, bright highlights on metal and glass, no blur, no soft gradients, no
noise, no text, no frame. `04_style_veigar_yordle.png` shows how a yordle (big head, short body) looks in
this style.

**View** - full body, **facing RIGHT**: we see her face and chest, never her back. She stands on one flat
ground line with both feet down. **Nothing below the soles**: no shadow, no ground, no base, and the cannon's
rear end stays above the feet line.

**Canvas** - **1536 x 1024 px (landscape)**, **transparent background**, the figure centred, about **850 px
from the top of the goggles to the soles** (the cannon makes her wide: keep all of it inside the canvas).

**Proportions (important)** - Tristana is a yordle: short, with a big head and huge ears. This picture will be
redrawn at game size, about 40 pixels tall **with the goggles**, so keep big clear shapes:
- the head (goggles to chin) is about **40% of her height**, the face wide and round, with **two big eyes**:
  warm **amber-gold irises**, a dark pupil and one white highlight each, both eyes the same shape; a small nose;
  a small confident grin;
- **huge pointed ears** sticking out sideways and a little up, lavender outside, **pink inside**; a small
  brass ring earring on the near ear;
- short legs in a wide, slightly crouched stance.

**Costume and colours** (from `05`-`09`):
- skin: soft **lavender-violet** (not blue-grey), a darker violet in the shadows;
- hair: **white**, short and fluffy, shaded with pale blue-grey; a side-swept fringe over the forehead, a
  fluffy mane round the back of the head and the neck;
- goggles: two big **cylindrical goggle cups pushed up on top of her head** - crimson-red leather cups with a
  thin purple band, **dull brass rims**, pale glass lenses facing up - joined by a brown leather strap across
  her forehead;
- top: an **olive-green sleeveless vest** over a tan shirt, a brown leather shoulder strap;
- arms: the **near arm** (her right) in a quilted brown leather sleeve with a **red cuff**, its hand holding the
  rear of the cannon at her hip; the **far hand** (her left) in a **big brown padded glove**, gripping the
  handle on top of the cannon at chest height;
- belt: brown leather with small **red pouches**;
- legs: olive-green shorts, the lower legs wrapped in quilted brown leather; **bare lavender yordle feet** with
  dark toe claws;
- **cannon "Boomer"**: as long as she is tall, held **level at her hip, in front of her body, pointing to the
  right**: a **bronze-brown barrel** with two **brass bands engraved with an X pattern**, a wide flared
  **octagonal steel-blue muzzle** at the front, a steel-blue cap at the rear, a brown leather-wrapped lower body,
  a small steel handle frame on top and a red grip.
Keep the **eyes' bright amber** for the eyes only: the goggle rims, the earring and the cannon's bands are a
duller, darker brass.

**Picture A - League's idle, 3/4 front** (`05_league_front.png`): her face and chest turned toward the viewer
about as in `05`, the cannon's muzzle toward the front-right (the round muzzle opening partly visible), feet
apart, knees bent.

**Picture B - the same idle, turned more to the side** (`07_league_pose_B.png`): the same pose and colours,
the camera a little further round to her front-right side, so the **whole length of the cannon points
straight to the right** and reads as a long barrel; her face still in 3/4 view with **both eyes visible** (the
far eye a little narrower), the near ear toward the back of the picture.

**Checks before you deliver**: facing right, face and both amber eyes visible and not covered by the cannon,
the gloves or the ears; the goggle cups on top of the head; two eyes the same shape; nothing below the soles;
transparent background; the silhouette (head, ears, goggles, cannon) readable when the picture is shrunk to
40 px tall.

Deliver: `outputs/tristana-model-A.png` and `outputs/tristana-model-B.png` (1536 x 1024, RGBA, transparent).
