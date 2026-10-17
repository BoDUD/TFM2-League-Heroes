# 蔚（Vi）原图提示词包 · 第 0 步

**给用户（中文说明）**：蔚还没有原图。请把整个 zip 交给 Codex，它按下面的英文提示词画两张高清像素风原图。
造型都照英雄联盟经典皮肤（粉色短发、额头上推着护目镜、脸颊上的“VI”纹身、暗红色围巾领、深钢蓝色的护甲配金色包边、
腿上的粉色条纹、黑色重靴），最重要的是**两只巨大的海克斯拳套**（钢灰色的指节甲 + 金色的前臂外壳 + 一个圆形仪表盘 + 蓝色海克斯水晶），
两张只是**拳套的位置和站姿**不同：
- **A**：英雄联盟的默认待机（参考 04）——拳击手的架势，重心在后脚，两只拳套举在胸前，近处的拳头低一点、远处的拳头高一点到下巴旁边。
- **B**：英雄联盟回城动作里的站姿（参考 07）——站直，抬着下巴，两只拳套**垂在身体两侧**，拳头在胯部到膝盖的高度，身体和脸完全露出来。

两张都是面朝右的 3/4 正面（看得到脸，**两只眼睛都要看见**，刘海和护目镜不能挡眼睛），完整全身、**透明背景**，
**鞋底以下什么都不能有**（游戏里血条在脚下）。拳套要画得**夸张地大**（每只拳头至少和她的头一样宽，从手肘到指节和她的躯干差不多长），
缩到游戏尺寸（约 40 行）以后拳套仍然是最显眼的东西。她的头发是粉色的，所以**不要用洋红色背景**（会把头发一起抠掉）。
你挑一张，我再按它写游戏尺寸的造型包（第 1 步）。
Codex 交付：`outputs/vi-picture/vi-model-A.png`、`outputs/vi-picture/vi-model-B.png`（1024x1536 竖图，真透明 PNG）和 `outputs/vi-picture/HANDOFF.md`。

附图：
- `01_style_caitlyn.png`：你之前采用的凯特琳原图（蔚的皮城搭档），只当**画风和人物比例**参考，不要照抄她的衣服和武器。
- `02_style_kaisa.png`：卡莎的原图，同上，只看画风（亮边、高光、干净的描边）。
- `03_style_metal_fists_blitzcrank.png`：布里茨的原图，只看**金色和钢色的金属大拳头怎么用像素画**（铆钉、分段的手指、高光），不要照抄他的造型。
- `04_league_pose_A.png`：英雄联盟经典皮肤的游戏内模型，默认待机，3/4 正面朝右 = 原图 A 的姿势和角度（以它为准）。
- `05_league_face.png`：头部特写（粉色短发、额头上的护目镜、脸颊上的纹身、暗红色围巾）。
- `06_league_head_side.png`：头部侧面（头发的长度、后脑翘起的发梢）。
- `07_league_pose_B.png`：回城动作里双拳垂在两侧的站姿 = 原图 B 的姿势。
- `08_league_gauntlet_closeup.png`：拳套特写（指节甲、金色外壳、仪表盘、蓝色水晶的结构）。
- `09_league_run.png`、`10_league_side.png`、`11_league_back.png`：跑步、侧面、背面（拳套怎么挂在前臂上，后背的护甲）。
- `12_league_attack.png`、`13_league_q_charge.png`：普攻出拳、Q 蓄力（拳头向后拉）——只是让你知道她怎么用拳套，不用画这些姿势。
- `14_league_splash.png`：加载画面原画，只参照脸和气质（自信、桀骜、带点痞气），服装配色以游戏内模型为准。

---

## Prompt (English, for Codex image generation)

Draw **Vi, the Piltover Enforcer** from League of Legends, in her **classic in-game model** (short pink hair with
goggles pushed up on her head, a dark-red scarf collar, dark steel-blue plated armour with brass trims, pink stripes on
the legs, heavy black boots, and her two HUGE hextech gauntlets, as in `04_league_pose_A.png`), as a full-body
character picture for a pixel-art game. Make TWO pictures, A and B: **the same character, costume and camera; only the
stance and where the gauntlets are differ.**

**Style** - copy the attached pictures `01_style_caitlyn.png` and `02_style_kaisa.png` exactly: a detailed pixel-art
illustration, hand-placed pixel clusters, a crisp 1-2 px dark outline around every shape, hard cel shading with 3-5
flat shades per material, bright highlights on metal and armour edges, no blur, no soft gradients, no noise, no text,
no frame. Use them for the STYLE and the heroic proportions (about 6.5-7 heads tall) only: do NOT copy their costumes,
weapons or poses. For the gauntlets' metal, look at how `03_style_metal_fists_blitzcrank.png` draws big gold and steel
fists in this style (segmented fingers, rivets, a bright highlight on every plate, a darker shade underneath) - only the
rendering, not his design. References `04`-`13` (renders of League's own model) are authoritative for Vi's look; do not
copy their 3D lighting, redraw them as pixel art.

**View** - full body, a 3/4 FRONT view **facing RIGHT**: her face and chest turned toward the viewer's right, both
eyes visible (the far eye a little narrower), never her back or a pure side view. She stands on one flat ground line,
both feet down. **Nothing below the soles**: no shadow, no ground, no base, no dust (the game draws the health bar right
under the feet).

**Canvas** - **1024 x 1536 px (portrait)**, a **real transparent background** (alpha 0 outside the silhouette).
Do NOT use a magenta or pink background: her hair is pink and would be keyed out with it. If you cannot write
transparency, use a flat pure green `#00FF00` background with no shadow and no anti-aliased halo. The figure centred,
about **1100 px from the top of her hair to the soles**, at least 80 px of empty margin all round (the gauntlets
included).

**Vi's look (both pictures):**
- **Hair:** short, choppy, BRIGHT PINK / hot-pink hair (3-4 pink shades, darker magenta-pink in the shadows), longer on
  top and swept toward her far side, a few spiky ends sticking out at the back of the head, cut short at the nape. A
  fringe falls over the far side of her forehead but **never covers her eyes**.
- **Goggles:** a pair of dark navy-grey goggles with dark blue lenses and a strap, pushed UP on top of her head above
  the forehead (not over her eyes).
- **Face:** fair skin, a confident, cocky, slightly smirking look; blue-grey eyes (dark pupil, one white highlight
  each, both the same shape), dark straight brows, a small straight nose, neutral pink-mauve lips. Her tattoo: the
  letters **"VI"** in small dark ink on the cheek under the near eye (a couple of small dark strokes; keep it subtle).
- **Scarf / collar:** a DARK RED / maroon scarf wrapped round her neck and spilling onto the chest and shoulders.
- **Armour:** a fitted suit of DARK STEEL-BLUE / navy plates (3-4 cool blue-grey shades with lighter steel-blue
  highlights on top edges): a rounded steel-blue breastplate trimmed with brass, steel shoulder plates, a belt with a
  brass buckle, plated thighs with **PINK / magenta stripes and patches** at the hips and thighs, round knee guards,
  olive-brown wraps on the shins, and heavy BLACK boots with brass buckles.
- **Hextech gauntlets (her signature) - draw them HUGE:** each gauntlet covers the whole forearm from the elbow to the
  fist and each fist is **at least as wide as her head** (the gauntlet from elbow to knuckles about as long as her
  torso). Each one: thick segmented STEEL-GREY / blue-grey knuckle and finger plates (four big blocky fingers and a
  thumb), a **GOLD / brass** forearm housing with rivets and pistons, a **round gauge dial** (a small clock-like face)
  on the outer side of the forearm, and glowing **BLUE hextech crystals** (bright cyan-blue, triangle-ish) on the back of
  the hand and between the plates. Both gauntlets are the same design; they must attach to her arms with no gap and
  read clearly as two separate big fists.
- **No other weapon.** No cape, no helmet.
- Colour plan: pink hair + fair skin + maroon scarf + navy/steel-blue armour + brass trims + pink leg stripes + black
  boots; the gauntlets are steel-grey + gold + bright blue crystals. Keep the blue crystals and the gold the brightest
  accents of the gauntlets.

**Picture A - League's idle** (`04_league_pose_A.png`): a boxer's guard. She stands with the weight on her back leg,
knees slightly bent, feet apart (the near foot a little forward), chin down, looking ahead to the right. Both gauntlets
are raised in front of her: the near fist lower, at chest height, the far fist higher, beside her chin, knuckles toward
the viewer's right. Keep her face, the scarf and the top of the breastplate visible above / between the fists.

**Picture B - fists down** (`07_league_pose_B.png`): the same character standing upright and confident, chin up, legs
apart in a solid stance, both arms hanging by her sides a little away from the body so that the two big gauntlets rest
at her hips, the knuckles at about knee height, one on each side of her body. Her face, scarf, breastplate, belt and
legs are fully visible between the gauntlets.

**Checks before you deliver**: facing right; face and both eyes visible and not covered by the hair, the goggles or a
gauntlet; two eyes the same shape; both gauntlets huge, the same design, joined to the arms; the gold, steel and blue
crystal of the gauntlets clearly separated; the armour has lit edges (no flat black areas); nothing below the soles;
real transparent background (or flat #00FF00, never magenta or pink); the silhouette (pink hair with goggles, the two
huge fists, the boots) readable when the picture is shrunk to 40 px tall.

Deliver into a folder named **`outputs/vi-picture/`**: `vi-model-A.png` and `vi-model-B.png` (1024 x 1536, RGBA,
transparent), and when both are final, a short `outputs/vi-picture/HANDOFF.md` listing the files.
