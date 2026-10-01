# Diana (黛安娜) - picture for the TFM2 League pack

给 Codex 的说明（中文摘要）：

- 画一张戴安娜（英雄联盟，经典皮肤）的像素风原图，风格和附带的阿卡丽、薇恩原图（1、2 号图）一样。
- 造型照 3-5 号图（英雄联盟原版模型的渲染）来画，不要自己设计新衣服。
- 全身，面朝右的 3/4 正面（看得到脸和胸口），透明背景，1024x1536。
- 出两个版本：A 弯刀斜举在身后、刀尖朝上；B 弯刀横在身前、指向右边。两版的弯刀都不能低于脚底线。
- 交付：`outputs/diana-model-A.png`、`outputs/diana-model-B.png`。

## Prompt (English, use as-is)

Create a pixel-art character illustration of **Diana, Scorn of the Moon** (League of Legends, classic skin) for a
Teamfight Manager 2 hero pack.

**Style - copy the attached pictures `1_style_akali.png` and `2_style_vayne.png`:**
- Same crisp, hand-placed pixel clusters.
- A 1-2 px dark outline.
- Hard cel shading: 3-4 flat shades per material, with no soft gradients, no blur and no anti-aliased glow.
- The same heroic proportions (about 6.5 heads tall).
- Full body on a transparent background.
- Canvas 1024x1536, the figure about 1300 px tall and centred, the feet near the bottom with a small margin.

**Model - copy her classic in-game look from the attached League renders, not a new costume**
(`3_league_diana_front.png`, `4_league_diana_head.png`, `5_league_diana_side.png`):
- **Hair:** platinum ash-blonde, combed tightly back from the face. Two teal-green bands wrap over the top of the
  head, one thin lock falls beside the near cheek, and a long ponytail hangs down her back.
- **Face:** pale, cool skin, calm and serious. Violet eyes with dark eyeliner, and a thin dark streak running down
  from under each eye. In the centre of the forehead sits a round glowing moon disc with a crescent in it, pale
  lavender-white; it is the brightest thing on her head.
- **Armour:** moonsilver plates with an iridescent teal-to-lavender sheen:
  - pauldrons with sharp, upswept crescent spikes;
  - a round crescent collar piece on the upper chest;
  - lavender-silver forearm guards;
  - a high dark collar.
- **Body:**
  - a dark navy bodysuit;
  - a gold crescent-moon belt buckle;
  - hanging dark teal-green hip tassets with thin gold-green edges;
  - a dark purple mantle / back cloth behind the shoulders.
- **Legs:** dark navy, with gold knee guards over moonsilver greaves and dark navy pointed boots.
- **Weapon:** the Moonsilver Blade, held in her right hand. It is a long, thin crescent-shaped blade of pale
  cyan-silver with a brighter cutting edge and a short grip near one end.

**Pose and camera:**
- 3/4 FRONT view facing RIGHT: her face and chest turn toward the viewer's right and both eyes are visible. Never
  draw her back or a pure side view.
- A calm combat stance: feet planted, weight slightly forward.
- **Nothing below the soles.** The game draws the health bar right under the feet, so the whole blade must stay
  above the feet line. League's idle lets the blade hang to the floor; do NOT copy that.
- Keep the face clear: no blade and no hair across the eyes.

**Two versions:**
- **A:** she holds the blade in her right hand, on the picture's LEFT behind her body line. It is angled up and
  back, so its curve rises behind her shoulder and its lower tip is no lower than her knees. Her free hand is
  relaxed at her side.
- **B:** she holds the blade forward at waist height, pointing to the RIGHT and ready to slash. Its lower tip stays
  above the knees. Her free hand is relaxed at her side.

**Deliver** `outputs/diana-model-A.png` and `outputs/diana-model-B.png`:
- 1024x1536, RGBA, transparent background;
- no text, no ground shadow and no frame.
