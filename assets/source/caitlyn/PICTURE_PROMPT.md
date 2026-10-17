# 凯特琳（Caitlyn）原图提示词包 · 第 0 步

**给用户（中文说明）**：凯特琳还没有原图。请把整个 zip 交给 Codex，它按下面的英文提示词画两张高清像素风原图，
造型都照英雄联盟经典皮肤（紫色高礼帽、深紫黑长发、紫裙配棕色皮外套、金白色海克斯狙击枪），只是持枪姿势不同：
- **A**：英雄联盟的默认待机（参考 03）——双手把长枪斜握在身前，枪托在腰后、枪管斜向右上方，枪口高过肩膀。
- **B**：英雄联盟的另一种待机（参考 06）——长枪竖着靠在身后一侧，枪口朝上高过帽子，近处的手叉在腰上。

两张都是面朝右的 3/4 正面（看得到脸，**两只蓝眼睛都要看见**，帽檐和头发不能挡住眼睛），完整全身、透明背景，
**鞋底以下什么都不能有**（游戏里血条在脚下）。你挑一张，我再按它写游戏尺寸（约 40 行，高礼帽算在内）的造型包（第 1 步）。
Codex 交付：`outputs/caitlyn-model-A.png`、`outputs/caitlyn-model-B.png`（1024x1536 竖图，真透明 PNG）。

附图：
- `01_style_vayne.png`、`02_style_diana.png`：你之前采用的薇恩、戴安娜原图，只当**画风和人物比例**参考，不要照抄她们的衣服和武器。
- `03_league_pose_A.png`：英雄联盟经典皮肤的游戏内模型，默认待机，3/4 正面朝右 = 原图 A 的姿势和角度（以它为准）。
- `04_league_face.png`：头部特写（高礼帽的金色 V 形饰条和蓝色圆宝石、长发、蓝眼睛、红唇、白色褶边领巾）。
- `05_league_head_side.png`：头部侧面（帽子的高度和帽檐、头发的长度）。
- `06_league_pose_B.png`：另一种待机，枪竖在身后 = 原图 B 的姿势。
- `07_league_side.png`、`08_league_back.png`：侧面和背面（长发垂到腰、外套背面、腿上的皮带和枪套）。
- `09_league_rifle.png`：步枪特写（金色枪身、象牙白护板、发光的青蓝能量线、两个金框蓝镜片的圆形瞄具、细长枪管、镂空枪托）。
- `10_league_aim.png`：她举枪瞄准的样子，只看枪的结构和瞄具，不用画这个姿势。
- `11_league_splash.png`：加载画面原画，只参照脸和气质（冷静、自信），服装配色以游戏内模型为准。

---

## Prompt (English, for Codex image generation)

Draw **Caitlyn, the Sheriff of Piltover** from League of Legends, in her **classic in-game model** (the purple top
hat, very long dark violet hair, purple dress under a short brown leather jacket and the long gold-and-ivory hextech
sniper rifle of `03_league_pose_A.png`), as a full-body character picture for a pixel-art game. Make TWO pictures,
A and B: **the same character, costume and camera, only the way she holds the rifle differs.**

**Style** - copy the attached pictures `01_style_vayne.png` and `02_style_diana.png` exactly: a detailed pixel-art
illustration, hand-placed pixel clusters, a crisp 1-2 px dark outline around every shape, hard cel shading with 3-5
flat shades per material, bright highlights on metal and glass, no blur, no soft gradients, no noise, no text, no
frame. Use them for the STYLE and the heroic proportions (about 6.5-7 heads tall) only: do NOT copy their costumes,
weapons or poses. References `03`-`10` (renders of League's own model) are authoritative for Caitlyn's look; do not
copy their 3D lighting, redraw them as pixel art.

**View** - full body, a 3/4 FRONT view **facing RIGHT**: her face and chest turned toward the viewer's right, both
eyes visible (the far eye a little narrower), never her back or a pure side view. She stands on one flat ground line,
both boots down. **Nothing below the soles**: no shadow, no ground, no base, and the rifle's stock stays above the
feet line (the game draws the health bar right under the feet).

**Canvas** - **1024 x 1536 px (portrait)**, a **real transparent background** (alpha 0 outside the silhouette), the
figure centred, about **1100 px from the top of the hat to the soles**, at least 80 px of empty margin all round
(picture B's rifle rises above the hat: keep all of it inside the canvas).

**Caitlyn's look (both pictures):**
- **Top hat:** a TALL PURPLE TOP HAT (violet, darker violet in the shadows) with a wide flat brim; on its front two
  vertical GOLD stripes that meet in a V / chevron; a GOLD band round its base with a round TEAL-CYAN lens-gem in a
  gold rim on the front-left. The hat is about one sixth of her height and sits slightly tilted on her head.
- **Hair:** very long, straight, DARK INDIGO-VIOLET hair (almost black, with violet-blue highlights), parted at the
  side, long strands framing both cheeks and falling over the shoulders, the rest hanging down her back to the waist.
- **Face:** pale skin, a calm, confident, slightly superior look; clear **BLUE eyes** (dark pupil, one white highlight
  each, both the same shape), dark defined brows, deep rose-red lips, a small straight nose.
- **Collar:** a white ruffled cravat / jabot at the throat with a small round GOLD brooch at the neck.
- **Jacket:** a short, cropped DARK BROWN LEATHER jacket (bolero) open over the dress, with GOLD-trimmed rounded
  shoulder plates; dark brown sleeves with gold-trimmed cuffs at the forearms; dark brown leather gloves.
- **Dress:** a fitted PURPLE (violet) bodice and a short flared purple skirt to mid-thigh, thin GOLD piping along the
  seams and the hem, a white ruffled petticoat edge peeking out under the hem.
- **Belt:** a brown leather belt with a gold buckle and a row of small brown ammunition pouches.
- **Legs:** dark navy-violet leggings; brown leather straps round both thighs holding small holsters / pouches; brown
  knee pads.
- **Boots:** tall KNEE-HIGH BROWN LEATHER boots with gold rings at the top and the ankle and small heels.
- **The rifle** (`09`, `10`): a very long hextech sniper rifle, about 80% of her height: a GOLD / brass frame with
  IVORY-WHITE side panels, thin glowing CYAN-BLUE energy lines along the body, two round gold-rimmed BLUE lens rings
  (the scope) standing on top, a long thin gold barrel ending in a ringed muzzle, and a skeletonised gold stock with a
  white butt pad.
- Colour accents: violet hat and dress, dark violet hair, brown leather, gold trims, ivory and gold rifle, small cyan
  glows. Keep the **blue of her eyes** for the eyes; the rifle's lenses and lines and the hat's gem are a brighter
  cyan-teal glow.

**Picture A - League's idle** (`03_league_pose_A.png`): standing relaxed, weight on one leg, holding the rifle
**diagonally across her body with both hands**: the stock low at her hip on the picture's LEFT (behind her), the
barrel rising forward to the UPPER RIGHT at about 30-35 degrees, the muzzle in front of her above shoulder height.
The rifle crosses her waist and lower chest, never her face.

**Picture B - League's other idle** (`06_league_pose_B.png`): the same character standing upright, the rifle held
**UPRIGHT on her far side, behind her body line** (the picture's LEFT), its stock at her hip and its barrel rising
past her shoulder and hat with the muzzle at the top; her NEAR hand rests on her hip. Her face and front stay clear
of the rifle.

**Checks before you deliver**: facing right; face and both blue eyes visible and not covered by the brim, the hair
or the rifle; two eyes the same shape; the top hat with its gold V and teal gem; nothing below the soles; real
transparent background; the silhouette (top hat, long hair, skirt, tall boots, rifle) readable when the picture is
shrunk to 40 px tall.

Deliver: `outputs/caitlyn-model-A.png` and `outputs/caitlyn-model-B.png` (1024 x 1536, RGBA, transparent).
