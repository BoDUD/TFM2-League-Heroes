# 凯隐（Kayn）原图提示词包 · 第 0 步

**给用户（中文说明）**：凯隐还没有原图。请把整个 zip 交给 Codex，它按下面的英文提示词画**四张**高清像素风原图，
四张是同一个人物、同一种画风、同一个镜头和比例：
- **A**：本体，英雄联盟的默认待机（参考 04）——镰刀拉亚斯特握在身后，弯刀刃在身后（画面左边）垂向地面，长柄斜着伸到身前快碰到地。
- **B**：本体，竖握镰刀的「死神」站姿（镰刀的位置看参考 07）——镰刀竖在远侧肩膀旁，刀刃在头顶上方向前弯；
  人站直、头摆正看向右边（不要像 07 那样仰头大笑），近处的手叉腰。
- **C**：暗裔杀手形态（拉亚斯特占据了身体，参考 15–17）：红色暗裔肉甲、钢灰护甲、一对巨大的弯角头盔、两只红眼，镰刀更大更红。
- **D**：影流刺客形态（凯隐驯服了拉亚斯特，参考 18–20）：苍白皮肤上爬满深蓝暗影纹，长黑发披散到膝盖（不扎辫子），镰刀刃口发青色光。

A、B 你挑一张做本体的造型（之后全套动作都从它来）；C、D 是两种形态出招动作（普攻 / Q / W / R）的设定。
四张都是面朝右的 3/4 正面，看得到脸和**两只眼睛**（本体：近处的眼睛金黄色，远处那只是被拉亚斯特侵蚀的红眼，周围一块深蓝灰的印记），
完整全身，**透明背景**，**鞋底以下什么都不能有**（游戏里血条在脚下）。镰刀是他的标志：要画得大、整把都在画面里、和手接上不留缝，
刀刃上的红眼和钢蓝刃口要亮；缩到游戏尺寸（约 40 行）后还要认得出「黑色刺头 + 蓝色挑染 + 长辫子 + 月牙镰刀」。
他的配色很暗（黑发、深靛蓝裤子、暗红镰刀），所以每块深色都要有亮边和高光（参考 02 魔腾的画法）。
镰刀和暗裔形态有大量红色、粉红色，**不要用洋红色背景**（会被一起抠掉），透明做不到就用纯绿 `#00FF00`。
Codex 交付：`outputs/kayn-picture/` 里的 `kayn-model-A.png`、`kayn-model-B.png`、`kayn-darkin.png`、`kayn-shadow.png`
（1024x1536 竖图，真透明 PNG），四张都画完以后最后写 `outputs/kayn-picture/HANDOFF.md`。

附图：
- `01_style_jhin.png`：你之前采用的烬的原图，只当**画风和人物比例**参考（男性英雄、修长的身材），不要照抄他的衣服和武器。
- `02_style_nocturne_dark_palette.png`：魔腾的原图，看**深色角色怎么保持清楚**（每块深色护甲的亮边、高光、红白刀刃），不要照抄造型。
- `03_style_kaisa.png`：卡莎的原图，同上，只看画风（亮边、高光、干净的描边）。
- `04_league_pose_A.png`：英雄联盟经典皮肤的游戏内模型，默认待机，3/4 正面朝右 = 原图 A 的姿势和角度（以它为准）。
- `05_league_face.png`：头部特写（刺头、蓝色挑染、金色的近眼、远处被侵蚀的红眼和深蓝灰印记、垂在脸两侧的两缕头发）。
- `06_league_head_side.png`：头部侧面（头顶的尖刺、脑后的长辫子）。
- `07_league_pose_B.png`：竖握镰刀、刀刃在头顶的动作 = 原图 B 的**镰刀位置**（他的头不要仰，照 04 摆正）。
- `08_league_scythe_closeup.png`：镰刀特写（暗红的月牙刀身、钢蓝的内侧刃口、外侧的尖刺、刀根的红眼、缠着红色布条的深紫长柄）。
- `09_league_run.png`、`10_league_side.png`、`11_league_back.png`：跑步、侧面、背面（辫子的长度、腰带的系法、裤子的形状）。
- `12_league_attack.png`、`13_league_q_spin.png`：普攻、Q 旋转——只是让你知道他怎么挥镰刀，不用画这些姿势。
- `14_league_splash.png`：加载画面原画，只参照脸和气质（傲慢、危险），服装配色以游戏内模型为准。
- `15_league_darkin_form.png`、`16_league_darkin_head.png`、`17_league_darkin_back.png`：暗裔杀手形态 = 原图 C。
- `18_league_shadow_form.png`、`19_league_shadow_face.png`、`20_league_shadow_back.png`：影流刺客形态 = 原图 D。

---

## Prompt (English, for Codex image generation)

Draw **Kayn, the Shadow Reaper** from League of Legends, in his **classic in-game model**, as full-body character
pictures for a pixel-art game. Make **FOUR pictures - the same character, style, camera and scale**:
- **A** and **B**: Kayn in his normal look (references `04`-`14`); the same costume, only the stance and where the
  scythe is differ;
- **C**: his **Darkin Slayer** form - Rhaast, the darkin inside the scythe, has taken over his body (`15`-`17`);
- **D**: his **Shadow Assassin** form - Kayn has mastered Rhaast (`18`-`20`).

**Style** - copy the attached pictures `01_style_jhin.png`, `02_style_nocturne_dark_palette.png` and
`03_style_kaisa.png` exactly: a detailed pixel-art illustration, hand-placed pixel clusters, a crisp 1-2 px dark
outline around every shape, hard cel shading with 3-5 flat shades per material, bright highlights on metal, hair and
skin edges, no blur, no soft gradients, no noise, no text, no frame. Use them for the STYLE and the heroic
proportions (about 6.5-7 heads tall, a lean athletic man) only: do NOT copy their costumes, weapons or poses.
Kayn is a very dark character (black hair, indigo trousers, dark crimson scythe): draw him the way `02` keeps
Nocturne readable - a lighter rim on every dark shape, clear highlights, and bright accents (the blue hair streak,
the gold and red eyes, the scythe's steel-blue edge and glowing red eye). References `04`-`20` (renders of League's
own model) are authoritative for his look; do not copy their 3D lighting, redraw them as pixel art.

**View** - full body, a 3/4 FRONT view **facing RIGHT**: face and chest turned toward the viewer's right, **both
eyes visible** (the far eye a little narrower), never his back or a pure side view. He stands on one flat ground line,
both feet down. **Nothing below the soles**: no shadow, no ground, no base, no dust (the game draws the health bar
right under the feet).

**Canvas** - **1024 x 1536 px (portrait)**, a **real transparent background** (alpha 0 outside the silhouette).
Do NOT use a magenta or pink background: the scythe and the Darkin form are crimson and pink and would be keyed out
with it. If you cannot write transparency, use a flat pure green `#00FF00` background with no shadow and no
anti-aliased halo. The figure centred, about **1000-1100 px from the top of the hair (C: the top of the horns) to the
soles**, with **the whole scythe inside the canvas** and at least 60 px of empty margin all round. If the scythe
would not fit, draw the whole figure a little smaller instead of cutting the scythe. Keep one scale for all four:
Kayn's soles-to-chin height the same in A, B and D (C's body is bigger, see below).

**Kayn's look (A and B):**
- **Hair:** jet-black, glossy, swept up and back into a few sharp SPIKES on top of his head; two long thin strands
  fall on both sides of his face down to the chin; one bright **BLUE streak** (a dyed lock, 2-3 blue shades) runs from
  the crown down the near side of his face. At the back the hair is tied into **one VERY LONG thick braid** hanging
  down his back to about the knees, with a small dark tie near its end.
- **Face:** young, lean and arrogant; tan-beige skin; sharp dark brows. The **NEAR eye amber-gold** with a black
  eyeliner flick; the **FAR eye glowing magenta-red inside a jagged dark blue-grey patch** (Rhaast's corruption, from
  the brow down onto the cheek). Both eyes the same size and on one level. A thin, confident mouth.
- **Body:** shirtless, athletic and lean (not bulky), defined chest and abs; a few dark blue-grey corruption cracks
  spreading from the neck onto the chest.
- **Waist:** a wide dark-brown / maroon **obi sash** wrapped round the waist, a thick **braided rope belt** tied in
  front and a rope **tassel** hanging at the near hip.
- **Trousers:** very baggy dark **navy-indigo** trousers (hakama-like) with a lighter violet front apron panel and
  thin maroon seams, gathered just under the knees.
- **Lower legs:** dark purple wrapped boots with a few plates, flat dark shoes. No cape, no helmet, no shirt.
- **Rhaast, the scythe (his signature) - draw it HUGE:** the shaft about as long as Kayn is tall. The **blade** is a
  big CRESCENT of dark **CRIMSON / maroon** darkin metal-flesh, with a **STEEL-BLUE sharpened cutting edge** along the
  inner curve, a few sharp spikes on the outer curve, and a **glowing magenta-red EYE** set in the base of the blade
  (the brightest accent of the weapon). The **shaft** is dark violet-blue, wrapped, with crimson bands, ending in a
  crimson **spike** at the butt. The hand that holds it grips the shaft firmly (fingers round it, no gap).
- Colour plan: black hair + blue streak, tan skin, maroon sash + brown rope, navy-indigo trousers, dark purple
  boots; scythe crimson + steel blue + the glowing red eye.

**Picture A - League's idle** (`04_league_pose_A.png`): a relaxed, confident stance, weight on the back leg, feet
apart. The near arm hangs loose by his side, fingers slightly open. The **FAR hand holds Rhaast low behind his
hips**: the blade is BEHIND him (toward the viewer's LEFT), its crescent curving down toward the ground behind his
back leg, and the shaft runs diagonally down past his hips to the ground in front of him (toward the viewer's right),
the crimson butt spike just above the ground. The braid hangs down his back. Face and chest unobstructed.

**Picture B - upright reaper**: the same character standing straight and confident, **head level and looking ahead
to the right** (NOT leaning back or laughing as in `07`). His **far hand holds Rhaast UPRIGHT** beside his far
shoulder: the shaft vertical, its butt spike near the ground by his front foot, and the **blade ABOVE his head, the
crescent curving forward (to the right) over his head** like a reaper's scythe - `07_league_pose_B.png` shows where
the scythe is. The **near hand rests on his hip**. Face, chest and sash fully visible.

**Picture C - Darkin Slayer** (`15`, `16`, `17`): Rhaast's form, the same camera; the body about 10% taller and much
more muscular. **CRIMSON-RED darkin flesh** with dark-red sinews covers the whole body; **steel-grey / blue-grey
armour plates** on the shoulders, the chest and the forearms, spiked bracers, clawed steel-tipped hands. A **horned
steel HELM** with **two HUGE curved horns** sweeping out and up (blue-grey steel with light edges) and a skull-like
face plate with **two glowing red eyes**. The same maroon sash and rope belt, the same baggy navy trousers, grey knee
plates, red lower legs ending in clawed steel feet. Stance as in `15`: wide and low, legs apart; the near arm hangs
with the claws open, the far hand holds Rhaast low in front of him with the blade at the front right near the ground.
Rhaast is bigger and redder here: a crimson blade with steel spikes and a big glowing red eye.

**Picture D - Shadow Assassin** (`18`, `19`, `20`): Kayn has mastered the scythe. **Pale grey-white skin** with
**dark NAVY-blue shadow markings** (his arms and parts of the torso covered by the dark shadow), **glowing pale
violet-white eyes**, the blue streak still in his hair, but the hair now hangs **LOOSE: very long straight black hair
falling down his back to the knees** (no braid, no spikes). The same sash and trousers, plus a long dark-purple robe
tail flowing behind. Rhaast changes too: a **silver-grey shaft** with a long silver spike, the blade **dark
navy-black with a bright CYAN glowing cutting edge** (no red eye). Stance as in `18`: light and poised, the near arm
reaching forward with open fingers, the scythe trailing low beside and behind him, the blade near the ground at the
front right.

**Checks before you deliver**: facing right; the faces and eyes visible (A/B: the near eye gold, the far eye red in
the dark patch; C: two red eyes in the helm; D: two pale glowing eyes); the scythe whole, joined to the hand, its
blade, edge and eye readable; every dark area has lit edges (no flat black blobs); nothing below the soles; real
transparent background (or flat `#00FF00`, never magenta or pink); readable when the picture is shrunk to 40 px tall:
A/B = black spiky hair with the blue streak + the long braid + the crescent scythe, C = the horns + the red body, D =
the long loose hair + the cyan blade.

Deliver into a folder named **`outputs/kayn-picture/`**: `kayn-model-A.png`, `kayn-model-B.png`, `kayn-darkin.png`
and `kayn-shadow.png` (1024 x 1536, RGBA, transparent), and when all four are final, a short
`outputs/kayn-picture/HANDOFF.md` listing the files.
