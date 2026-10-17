# 维迦（Veigar）原画提示词包 · 第 0 步

**给用户（中文说明）**：维迦还没有原画。请把整个 zip 交给 Codex，它按下面的英文提示词画两张原画：
A = 英雄联盟待机姿势（法杖竖在身旁，远侧的大铁手套举到头边做"邪恶爪"手势），
B = 法杖向前上方斜指（施法姿势）。你挑一张，我再按它出游戏尺寸（约 40 行，帽子算在内）的造型包（第 1 步）。
Codex 交付：`outputs/veigar-model-A.png`、`outputs/veigar-model-B.png`（1024x1536，透明背景）。

附图：
- `01_style_akali.png`、`02_style_vayne.png`、`03_style_nami.png`：你之前让 Codex 画的原画，只当**画风**参照。
- `04_league_front.png`：英雄联盟经典皮肤的游戏内模型，3/4 正面朝右（造型、配色以它为准）。
- `05_league_head.png`：帽子和脸的特写（帽檐下是全黑的脸 + 两只发光的黄眼睛，没有嘴）。
- `06_league_side.png`、`07_league_back.png`：侧面、背面，看帽子尖、披布、裙摆的结构。
- `08_pose_A.png`、`09_pose_B.png`：两种持杖姿势的参照。
- `10_league_splash.png`：加载画面原画，只参照脸（黑暗里的黄眼）和邪恶的气质，服装配色以游戏内模型为准。

---

## Prompt (English, for Codex image generation)

Draw **Veigar, the Tiny Master of Evil** from League of Legends, in his **classic in-game model** (the
blue-violet wizard of `04_league_front.png`), as a full-body character picture for a pixel-art game.
Make two pictures, A and B, that differ only in how he holds his staff.

**Style** - copy the attached pictures `01_style_akali.png`, `02_style_vayne.png`, `03_style_nami.png`
exactly: a detailed pixel-art illustration, a crisp dark outline around every shape, 3-5 flat shades per
material, bright highlights on metal, no blur, no soft gradients, no noise, no text, no frame.

**View** - full body, **3/4 FRONT view facing RIGHT** (like `04_league_front.png`): we see his face and chest,
never his back. He stands on one flat ground line with both feet down. **Nothing below the soles**: no
shadow, no ground, no base, and no part of the staff under the feet line.

**Canvas** - 1024 x 1536 px, **transparent background**, the figure centred, about 1250 px from the highest
point (hat or staff head) to the soles.

**Proportions (important)** - Veigar is a yordle: short, stocky, a big head under a huge hat. This picture
will be redrawn at game size, about 40 pixels tall **with the hat**, so keep big clear shapes:
- the hat is the largest shape: from the brim to its highest point about **one third** of his height. Its
  pointed tip **bends backward (to the left, behind him) and droops**, so the hat adds width, not height;
- under the brim: **no skin at all** - a pitch-black face with **two big glowing yellow eyes** (slanted,
  evil, both the same size, the near eye a little larger is fine), **no mouth, no nose**;
- a compact body in a wide flared robe; short legs.

**Costume** (from `04`-`07`):
- hat: royal blue-violet, turning purple toward the bent tip; a band of **silver metal plates with small
  spikes** around the crown with one square buckle; a wide flat brim;
- robe: blue-violet with a wide, flared skirt whose hem is a **dark steel rim studded with small spikes**;
  a brown leather belt with small spikes; a **magenta-purple cloth** hanging from the belt at the far hip;
- arms: blue sleeves, silver shoulder guard, steel bracers;
- the **far hand (his left) wears a huge spiked silver-grey gauntlet** with claw-like fingers;
- the near hand (his right) grips the staff in a smaller steel glove;
- legs: short and dark, **dark gunmetal pointed boots with spikes**;
- **staff**: a grey metal shaft with square steel collars; its head is **two long silver blades forming a
  claw/fork** with a glowing **orange** crystal flame between them. Keep the crystal clearly orange-gold
  (warmer and darker than the eyes): the eyes' bright yellow appears nowhere else.

**Picture A - League's idle pose** (`08_pose_A.png`): feet apart, knees slightly bent. The staff stands
**upright in his near hand at his side** (not in front of his face), its lower end on the ground beside the
near foot, its claw head reaching **about the height of the top of the hat** (a short, chibi staff - never
much taller than the hat). The far gauntlet is raised to head height, fingers curled like a claw, an evil
gleeful gesture.

**Picture B - staff pointed forward** (`09_pose_B.png`): the same figure and colours, but the staff is held in
the near hand **tilted forward-up about 45 degrees**, its claw head ahead of the hat's brim, pointing where he
casts; its lower end stays behind the near foot and above the feet line. The far gauntlet raised the same way.

**Checks before you deliver**: facing right, face and both yellow eyes visible and not covered by the staff
or the gauntlet; the hat tip bent backward; two eyes the same shape; no mouth; nothing below the soles;
transparent background; the silhouette readable when the picture is shrunk to 40 px tall.

Deliver: `outputs/veigar-model-A.png` and `outputs/veigar-model-B.png` (1024 x 1536, RGBA, transparent).
