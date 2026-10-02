# 卡莎（Kai'Sa）原图提示词包 · 第 0 步

**给用户（中文说明）**：卡莎还没有原图。请把整个 zip 交给 Codex，它按下面的英文提示词画两张高清像素风原图。
造型都照英雄联盟经典皮肤（浅灰蓝的紧身衣 + 深紫黑的虚空甲壳、金色细边、洋红色发光纹路、背后两片翼舱），
只是**翼舱的状态和站姿**不同：
- **A**：英雄联盟的默认待机（参考 04）——站直放松，两片翼舱**收拢**，像一层合起来的深色甲壳披在背后，边缘从两肩后面露出来，接缝透出洋红光。
- **B**：英雄联盟的大招准备 / 战斗姿态（参考 07、08）——同样站直，两片翼舱**抬起、半张开**，像向后上方收着的一对翅膀，
  金边，每片翼舱里亮着一只洋红色的椭圆光眼（导弹舱）。跑步时她的翼舱也是这样抬着（参考 08）。

两张都是面朝右的 3/4 正面（看得到脸，**两只淡紫色眼睛都要看见**，头发不能挡眼睛），完整全身、**透明背景**，
**鞋底以下什么都不能有**（游戏里血条在脚下）。她通身深色，所以要求了亮边、高光和亮的点缀色（洋红光、金边、浅色紧身衣），
游戏里缩小后才不会糊成一团黑。你挑一张，我再按它写游戏尺寸（约 40 行，翼舱算在内）的造型包（第 1 步）。
Codex 交付：`outputs/kaisa-model-A.png`、`outputs/kaisa-model-B.png`（1024x1536 竖图，真透明 PNG）和 `outputs/HANDOFF.md`。

附图：
- `01_style_caitlyn.png`、`02_style_diana.png`：你之前采用的凯特琳、戴安娜原图，只当**画风和人物比例**参考，不要照抄她们的衣服和武器。
- `03_style_dark_palette_nocturne.png`：魔腾的原图，只看**深色英雄怎么打亮边、留高光**，不要照抄他的造型。
- `04_league_pose_A.png`：英雄联盟经典皮肤的游戏内模型，默认待机，3/4 正面朝右 = 原图 A 的姿势和角度（以它为准）。
- `05_league_face.png`：头部特写（深紫黑长发、淡紫色眼睛、脸上的粉紫色虚空纹、深色嘴唇、颈下的甲壳领）。
- `06_league_head_side.png`：头部侧面（头发的长度和分缝）。
- `07_league_pose_B.png`：大招准备的站姿，翼舱抬起张开 = 原图 B 的姿势。
- `08_league_run_pods_up.png`：跑步时翼舱抬起向后掠的样子（B 的翼舱可以参考它）。
- `09_league_side.png`、`10_league_back.png`：待机的侧面和背面（翼舱收拢时怎么贴在背上）。
- `11_league_pods_open_back.png`：翼舱张开时从背后看（甲壳、金边和洋红光的结构）。
- `12_league_attack.png`：普攻的样子，只看她**用前臂/手掌发射**，手里不拿枪；不用画这个姿势。
- `13_league_splash.png`：加载画面原画，只参照脸和气质（冷静、专注），服装配色以游戏内模型为准。

---

## Prompt (English, for Codex image generation)

Draw **Kai'Sa, Daughter of the Void** from League of Legends, in her **classic in-game model** (the pale steel-blue
bodysuit under dark violet-black void carapace armour with thin gold trims and glowing magenta lines, and the two
large wing-pods on her back, as in `04_league_pose_A.png`), as a full-body character picture for a pixel-art game.
Make TWO pictures, A and B: **the same character, costume and camera; only the wing-pods and the stance differ.**

**Style** - copy the attached pictures `01_style_caitlyn.png` and `02_style_diana.png` exactly: a detailed pixel-art
illustration, hand-placed pixel clusters, a crisp 1-2 px dark outline around every shape, hard cel shading with 3-5
flat shades per material, bright highlights on armour edges, no blur, no soft gradients, no noise, no text, no frame.
Use them for the STYLE and the heroic proportions (about 6.5-7 heads tall) only: do NOT copy their costumes, weapons
or poses. Kai'Sa is almost all dark violet and black, so light her the way `03_style_dark_palette_nocturne.png` lights
a dark hero: **every armour plate gets a lighter rim highlight along its top / outer edge**, the dark areas are deep
violet-navy (never flat pure black), and the bright accents (magenta glow, gold trims, the pale bodysuit, her skin)
stay clearly visible. References `04`-`12` (renders of League's own model) are authoritative for Kai'Sa's look; do not
copy their 3D lighting, redraw them as pixel art.

**View** - full body, a 3/4 FRONT view **facing RIGHT**: her face and chest turned toward the viewer's right, both
eyes visible (the far eye a little narrower), never her back or a pure side view. She stands on one flat ground line,
both feet down. **Nothing below the soles**: no shadow, no ground, no base, no glow puddle (the game draws the health
bar right under the feet).

**Canvas** - **1024 x 1536 px (portrait)**, a **real transparent background** (alpha 0 outside the silhouette).
Do NOT use a magenta or purple background: her glows are magenta and would be keyed out with it. If you cannot write
transparency, use a flat pure green `#00FF00` background with no shadow and no anti-aliased halo. The figure centred,
about **1100 px from the top of her head to the soles** (picture B's raised pods may rise higher: keep all of them
inside the canvas), at least 80 px of empty margin all round.

**Kai'Sa's look (both pictures):**
- **Hair:** long, thick, DARK PURPLE-BLACK hair (deep aubergine with violet highlights), parted on one side, a heavy
  lock falling over her far shoulder, the rest down her back past the shoulder blades; a few strands frame her face.
- **Face:** pale skin, a calm, focused, slightly fierce look; **LILAC / pale violet eyes** (dark pupil, one white
  highlight each, both the same shape), dark straight brows, dark mauve lips, a small straight nose. Her **void
  markings**: thin pinkish-violet lines on the face - one stripe up the middle of the forehead, a few thin diagonal
  strokes on each cheek - subtle, never covering the eyes.
- **Bodysuit:** a sleek, form-fitting PALE STEEL-BLUE / lavender-grey suit (3-4 cool shades) on the torso, the upper
  arms and the inner thighs, with thin dark ridges like a living carapace; at the chest a dark violet plated collar /
  sternum guard with rib-like ridges (armour, keep it modest and heroic, not revealing).
- **Carapace armour:** DARK VIOLET-BLACK plates (deep violet-navy with lighter violet rims): big rounded SHOULDER
  plates; long FOREARM gauntlets ending in **clawed armoured hands** (sharp dark fingers); long plates down the outer
  thighs and the shins with pointed knee guards; clawed, pointed boots. Thin **GOLD / bronze trim lines** run along the
  edges of the shoulder plates, the pods and some leg plates.
- **Magenta glow:** bright MAGENTA-VIOLET glowing slits and lines (hot pink-violet core, lighter pink centre) on the
  outer thighs, the forearms and inside the pods. Keep the glow the brightest colour on her; it is her signature.
- **Wing-pods (her signature):** two LARGE curved pod-shells mounted on her upper back / shoulder blades, one behind
  each shoulder, each about as long as her torso: dark violet-black shells with gold rims, pointed tips, and on the
  inner side of each pod a glowing MAGENTA oval "eye" (the missile bay). They must read clearly in both pictures and
  attach to her back with no gap.
- **No weapon in her hands**: she fights with the suit itself (plasma bolts from the forearms). Do not add guns,
  swords or staffs. No helmet (her face stays uncovered).
- Colour plan: pale steel-blue suit + dark violet-black armour with lighter violet rims + gold trims + magenta glows +
  pale skin + dark purple hair. Lilac is used only for the eyes.

**Picture A - League's idle** (`04_league_pose_A.png`): standing upright and relaxed, feet a little apart, arms
hanging by her sides slightly away from the body, clawed fingers loosely curled. The two pods are **FOLDED DOWN** over
her back like a closed dark shell: their gold-rimmed edges show behind and past both shoulders, the tips pointing down
toward her waist; only thin magenta glints show in the seams.

**Picture B - pods raised** (`07_league_pose_B.png`, `08_league_run_pods_up.png`): the same character standing
upright, arms a little out from her sides with the clawed fingers spread and a faint magenta glow at the palms. The two
pods are **RAISED AND HALF-OPEN** behind her shoulders like a pair of swept-back wings: tips pointing up and back,
the near pod lower and the far pod a little higher, the glowing magenta oval eye of each pod clearly visible, gold rims
catching the light. The pods may rise a little above her head (at most about one head-height above the crown) and
must not cover her face.

**Checks before you deliver**: facing right; face and both lilac eyes visible and not covered by the hair or the
pods; two eyes the same shape; both pods visible and joined to her back; the dark armour has lit rims (no flat black
areas); the magenta glows are bright; nothing below the soles; real transparent background (or flat #00FF00, never
magenta); the silhouette (long hair, the two pods, the clawed gauntlets, the long legs) readable when the picture is
shrunk to 40 px tall.

Deliver: `outputs/kaisa-model-A.png` and `outputs/kaisa-model-B.png` (1024 x 1536, RGBA, transparent), and when both
are final, a short `outputs/HANDOFF.md` listing the files.
