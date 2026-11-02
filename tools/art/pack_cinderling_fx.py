#!/usr/bin/env python3
"""Build cinderling_fx_pack.zip: step 3 of the Cinderling's (绯红树怪) sprite - Codex draws its effects and its three
skill icons (the tft heroes' way).

    python tools/lol/fx_ref_cinderling.py            # the particle references -> C:/t/cf_work/fxref
    python tools/art/pack_cinderling_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name cinderling_fx_redo_pack]

The pack (C:/t/cf_work/fx/cinderling_fx_pack, zipped into --out, default D:/TFM2-Workshop/cinderling_packs) holds
PROMPTS.md (also written to assets/source/cinderling/PROMPTS_FX.md), design/cinderling_design.png (the approved idle
at 4x on its own squares), design/cinderling_size.png (it at game size, 4x, on the arena colour with the ground line,
a 10-px ruler and the base fighter) and refs/tft_fx_ref.png (the Rift's Red camp's particle textures and Zyra's,
Brand's and Rek'Sai's - grey shapes the game tints, grouped by the effect they inform). The effects are the views the
kit binds (tools/kit/build_cinderling.py, the user's OK 2026-11-02: bottom lane, the proposed kit):
view_projectiles a_leaf, q_leaf, r_leaf; view_effects a_hit, q_hit, e_dig, e_pop, r_cast, r_hit; view_buffs p_full,
p_burn, q_wound, e_slow, r_blaze. Plus the three skill icons.
Its colours: the orange-red glow of its eye and spiral (the red buff's ember), its warm brown wood mask, its dark
purple-brown bark, its pale green leaves.
Red side: the flying leaves are symmetric top to bottom, pointing right (turned with their flight); every other
picture is symmetric left to right (the client never mirrors an effect picture).
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/cf_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "cinderling", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "cinderling", "hd")
NAME = "cinderling_fx_pack"
PPU = 2.33

FIRE = "#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C"   # its glowing eye and spiral: the red buff's ember
LEAF = "#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A"           # its leaf mane
WOOD = "#E0A878, #B97A4E, #8A5536, #5A3524"                     # its wooden mask and leg plates
BARK = "#7A5A6A, #54384A, #3A2433, #22141E"                     # its dark purple-brown bark
DIRT = "#A88A62, #7A6044, #54402E, #33261C"                     # the earth it digs through
FI = f"an ember fire ramp ({FIRE})"
LE = f"a leaf green ramp ({LEAF})"
WO = f"a warm wood ramp ({WOOD})"
BA = f"a dark bark ramp ({BARK})"
DI = f"an earth ramp ({DIRT})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red "
         "edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little "
         "bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams")
HIM = ("the critter crouches in the middle, not drawn: about 40 squares wide and 30 tall from its tallest leaf to the "
       "ground, on all fours, its round wooden mask at the front right, its leaf spines on top")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square warm wood frame with little "
        "orange ember corners, a deep green-black inside, the symbol big and centred, lit from the upper left; pixel art "
        "at 2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_leaf", "普攻「余烬叶」：飞出去的一片燃烧的叶子，4 帧循环",
     "view_projectiles `tft_cinderling_a_leaf`（追踪弹道，随飞行方向转；上下对称、朝右）", "10 × 6",
     "一片**边缘烧着橙红火光的绿叶**，叶尖朝右，后面拖两三颗火星。4 帧循环：叶子微微翻动、火星闪。**上下对称、朝右**。",
     LE + ", " + FI,
     "A FLYING EMBER LEAF, 4 looping frames, " + TB + ": a pointed green leaf 7 squares long and 3 tall, its tip to the "
     "right, a 1-square glowing orange-red rim along its edges and a light vein down the middle, two or three tiny "
     "embers trailing behind it on the left (mirrored top and bottom); frames 1-4 the leaf's light and dark halves "
     "swapping as it flutters and the embers flickering. " + MAGIC + ".",
     row(4, 10, 6) + CENTER),
    ("a_hit", "普攻：叶子打中，4 帧", "view_effects `tft_cinderling_a_hit`（跟随目标，z 2；左右对称）", "14 × 12",
     "叶子打中：一下橙黄的小闪光，**两道交叉的绿色叶痕**（像叶刃划过），几颗火星和两片碎叶往两边飞。**左右对称**，4 帧。",
     LE + ", " + FI,
     "A LEAF CUT, 4 frames, " + LR + ": 1 a small hot yellow-white flash 4 squares across; 2 TWO short green LEAF SLASHES "
     "crossing in an X, 8 squares tall, glowing orange-red edges, a few embers flying out to both sides; 3 the slashes "
     "fading, two torn leaf bits falling outward; 4 the last embers. " + MAGIC + ".",
     row(4, 14, 12) + CENTER),
    ("p_full", "被动「绯红霸符」：叠满层，6 帧循环", "view_buffs `tft_cinderling_p_full`（大表，跟随它，z 3；左右对称）",
     "44 × 36",
     "霸符叠满的时候：它**背上的叶尖冒出小小的橙红火苗**，一颗颗火星往上飘，身体两侧边缘有一点红光。很淡，只在叶尖和边缘。"
     "**它的身体位置留空**。**左右对称**，6 帧循环。",
     FI,
     "AN EMBER CROWN, 6 looping frames, " + LR + ": round " + HIM + ": small orange-red FLAME TIPS 2-4 squares tall at "
     "the tips of its leaf spines along the top of the cell (mirrored), single embers rising above them, a faint red "
     "glint at both side edges of the body; frames 1-6 the flame tips flickering in turn and the embers rising a few "
     "squares a frame (every frame left-right symmetric). Only at the top and the edges; INSIDE stays EMPTY (its body). "
     + MAGIC + ".",
     row(6, 44, 36) + CENTER),
    ("p_burn", "灼烧（被动叠满的普攻、刃叶、大招都用），6 帧循环",
     "view_buffs `tft_cinderling_p_burn`（跟随被烧的人，z 4；左右对称）", "20 × 26",
     "被烧着的人：身体两侧下半身**几簇小小的橙红火苗**往上窜，夹着一两片烧焦的小叶子，几颗火星往上飘。很小，不要盖住人。"
     "**人站的地方留空**。**左右对称**，6 帧循环。",
     FI + ", " + LE,
     "A LEAF-FIRE BURN, 6 looping frames, " + LR + ": round " + CHAMP + ": on EACH side of its lower body (mirrored) two "
     "small orange-red FLAME TONGUES 3-6 squares tall with yellow cores, one tiny scorched leaf curling in the flames, "
     "two or three single embers rising beside its body; frames 1-6 the flames flickering up and down in turn and the "
     "embers rising (every frame left-right symmetric). Small; the middle (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 20, 26) + CENTER),
    ("q_leaf", "技能 1「刃叶」：飞出去的锋利叶刃，4 帧循环",
     "view_projectiles `tft_cinderling_q_leaf`（五片一起绕弧飞向目标，随飞行方向转；上下对称、朝右）", "12 × 7",
     "一片**又细又尖的锋利绿叶刃**（比普攻的叶子更长更尖、边缘是亮橙红的刃口），叶尖朝右，后面一道短短的绿色残影。"
     "4 帧循环：叶刃转动发亮。**上下对称、朝右**。",
     LE + ", " + FI,
     "A RAZOR LEAF, 4 looping frames, " + TB + ": a long narrow pointed green LEAF BLADE 9 squares long and 3 tall, its tip "
     "to the right, its two edges a bright orange-red cutting line, a pale vein, and a short faint green streak behind it "
     "on the left; frames 1-4 the blade spinning along its length (the light edge moving from top to bottom and back, "
     "mirrored) and a glint running along it. " + MAGIC + ".",
     row(4, 12, 7) + CENTER),
    ("q_hit", "技能 1「刃叶」：五片叶刃聚在目标身上，5 帧", "view_effects `tft_cinderling_q_hit`（跟随目标，z 3；左右对称）",
     "26 × 22",
     "五片叶刃从四周**一起扎到目标身上**：一圈叶刃划痕从外往里聚拢成星形，中间爆一下橙红的火花，碎叶和火星往外飞。**人站的地方留空**。"
     "**左右对称**，5 帧。",
     LE + ", " + FI,
     "A FIVE-LEAF CONVERGENCE, 5 frames, " + LR + ": round " + CHAMP + " (only its middle third): 1 five short green LEAF "
     "SLASHES at the edges of the cell, pointing inward like a star (one from the top, two from the upper sides, two from "
     "the lower sides, mirrored); 2 the slashes meeting at the body's middle, glowing orange-red edges, a small yellow-"
     "white flash where they meet; 3 an orange-red spark burst 10 squares across, torn leaf bits and embers flying out; "
     "4 the slashes and sparks fading to dark red, leaf bits falling; 5 the last embers and one falling leaf on each "
     "side. " + MAGIC + ".",
     row(5, 26, 22) + CENTER),
    ("q_wound", "技能 1「刃叶」：重伤印记，6 帧循环", "view_buffs `tft_cinderling_q_wound`（跟随被重伤的人，头顶上方，z 3；左右对称）",
     "10 × 10",
     "被重伤（受到的治疗变少）的人头顶：**一片裂成两半的绿叶**，裂口冒橙红的光，下面一个小小的暗红「十」字被叶子划破（表示治疗被削弱）。"
     "一跳一跳地发光。**左右对称**，6 帧循环。",
     LE + ", " + FI,
     "A WOUND MARK, 6 looping frames, " + LR + ": above a unit's head: a small round green LEAF 8 squares tall SPLIT down "
     "the middle by a glowing orange-red crack, the two halves a square apart, a small dark red PLUS SIGN behind it cut "
     "through by the crack (healing cut); frames 1-6 the crack pulsing brighter and dimmer and the mark bobbing one "
     "square up and down. " + MAGIC + ".",
     row(6, 10, 10) + CENTER),
    ("e_dig", "技能 2「钻土突袭」：钻进地里，5 帧", "view_effects `tft_cinderling_e_dig`（它钻下去的地方，地面上，z 3；左右对称）",
     "40 × 18",
     "它钻进地里的地方：**地面裂开一个土坑**，一圈泥块、草屑和几片叶子往两边上方喷起再落下，最后留一小堆土。"
     "**左右对称**，5 帧。",
     DI + ", " + LE,
     "A DIG-IN BURST, 5 frames, " + LR + ": low on the ground (a flat ellipse, seen from above at an angle): 1 the ground "
     "cracking in a ring 24 squares wide; 2 clods of brown EARTH, grass bits and two green leaves thrown up and out to "
     "both sides, a dark hole in the middle (an ellipse 16 squares wide, 4 tall); 3 the clods at their highest (10 "
     "squares up), dust puffs; 4 the clods falling back; 5 a small mound of loose earth over the hole and a few last "
     "falling bits. " + MAGIC + ".",
     row(5, 40, 18) + CENTER),
    ("e_pop", "技能 2「钻土突袭」：钻出来的冲击，6 帧", "view_effects `tft_cinderling_e_pop`（它钻出来的地方，地面上，z 3；左右对称）",
     "48 × 26",
     "它从地里钻出来：**地面炸开**，一圈泥土冲击环往外扩（扁椭圆），大块泥块、草根和绿叶往上往两边飞，周围的人被震得减速。"
     "**中间（它的位置）留空**。**左右对称**，6 帧。",
     DI + ", " + LE,
     "A BURST OUT OF THE GROUND, 6 frames, " + LR + ": low on the ground: 1 a crack ring and a puff of dust 16 squares "
     "wide; 2 the ground bursting: big clods of brown EARTH, roots and green leaves thrown up and out to both sides, a "
     "flat ring of dust and earth (an ellipse 34 squares wide, 8 tall); 3 the ring 46 squares wide, clods at their "
     "highest (14 squares up); 4 the ring thinning into dust, clods falling; 5 dust settling, leaves fluttering down; "
     "6 the last dust. The middle (where it lands) stays EMPTY. " + MAGIC + ".",
     row(6, 48, 26) + CENTER),
    ("e_slow", "技能 2「钻土突袭」：被震得减速，6 帧循环", "view_buffs `tft_cinderling_e_slow`（跟随被减速的人，脚下，z 3；左右对称）",
     "22 × 8",
     "被减速的人：脚边**一圈松土和几根细草根缠着脚踝**，几粒泥土轻轻跳动。很淡、只在脚下。**左右对称**，6 帧循环。",
     DI + ", " + LE,
     "MUD AND ROOTS, 6 looping frames, " + LR + ": low round a unit's feet only (the unit not drawn): on EACH side "
     "(mirrored) a low heap of loose brown earth and two thin pale ROOTS curling round the ankle line, a tiny green "
     "sprout; frames 1-6 the roots tightening and loosening a square and a few earth grains hopping (every frame "
     "left-right symmetric). Subtle. " + MAGIC + ".",
     row(6, 22, 8) + CENTER),
    ("r_cast", "大招「燎原叶暴」：叶子着火，6 帧", "view_effects `tft_cinderling_r_cast`（大表，跟随它，z 3；左右对称）",
     "56 × 48",
     "它站起来开大的一下：**背上的叶子一下子烧起来**，一圈橙红的火焰从它身后往上冲，火星和燃烧的叶片往四周炸开，地面一圈火光。"
     "**它的身体位置留空**。**左右对称**，6 帧。",
     FI + ", " + LE,
     "A WILDFIRE IGNITION, 6 frames, " + LR + ": round the critter standing up on its back legs in the middle, not drawn "
     "(about 26 squares wide and 40 tall): 1 a hot yellow-white flash behind its upper back; 2 a fan of orange-red FLAMES "
     "bursting up behind and round its upper body, tallest at the top (12 squares), a flat ring of fire light on the "
     "ground (an ellipse 40 squares wide, 8 tall); 3 BURNING LEAVES (green with orange flaming edges) blown out to both "
     "sides (mirrored), embers everywhere; 4 the flames sinking to the edges, the leaves still flying; 5 small flames "
     "and the ground glow fading; 6 the last rising embers. The middle (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 56, 48) + CENTER),
    ("r_blaze", "大招「燎原叶暴」：燃烧的叶子环绕，6 帧循环", "view_buffs `tft_cinderling_r_blaze`（大表，跟随它，z 3；左右对称）",
     "52 × 40",
     "大招期间：**几片燃烧的叶子绕着它转**（前后各几片，像一圈火叶旋风），叶尖拖着火星，背上叶尖有火苗。"
     "**它的身体位置留空**，叶子只在身体外圈。**左右对称**，6 帧循环。",
     FI + ", " + LE,
     "A RING OF BURNING LEAVES, 6 looping frames, " + LR + ": round " + HIM + ": six small BURNING LEAVES (green, 4 squares "
     "long, orange-red flaming edges, a tiny ember trail) circling round the body on a flat ellipse 48 squares wide and "
     "14 tall at the body's middle height, three on each side in mirrored positions, the ones behind the body darker; "
     "small flame tips on its leaf spines along the top; frames 1-6 the leaves moving round the ellipse (mirrored pairs: "
     "every frame left-right symmetric) and embers rising. Only round the body's edge; INSIDE stays EMPTY (its body). "
     + MAGIC + ".",
     row(6, 52, 40) + CENTER),
    ("r_leaf", "大招「燎原叶暴」：射出去的燃烧叶刃，4 帧循环",
     "view_projectiles `tft_cinderling_r_leaf`（追踪弹道，随飞行方向转；上下对称、朝右）", "12 × 8",
     "一片**整个烧着的叶刃**：叶子被火包住，叶尖朝右，后面拖一道短短的火焰尾巴。4 帧循环：火焰跳动。**上下对称、朝右**。",
     FI + ", " + LE,
     "A FLAMING LEAF BLADE, 4 looping frames, " + TB + ": a pointed leaf 7 squares long wrapped in orange-red FLAME, its "
     "tip to the right (a hot yellow core along the leaf, the green showing at its middle), a short flame tail 4 squares "
     "long streaming to the left (mirrored top and bottom); frames 1-4 the flames flickering and the tail waving. "
     + MAGIC + ".",
     row(4, 12, 8) + CENTER),
    ("r_hit", "大招：燃烧叶刃打中，4 帧", "view_effects `tft_cinderling_r_hit`（跟随目标，z 3；左右对称）", "16 × 16",
     "燃烧的叶刃打中：一下橙黄的火花爆开，几片烧焦的碎叶和火星往外飞。**左右对称**，4 帧。",
     FI + ", " + LE,
     "A FIERY LEAF IMPACT, 4 frames, " + LR + ": 1 a hot yellow-white flash 5 squares across; 2 an orange-red burst of "
     "flame 12 squares across, two scorched leaf bits and embers flying out to both sides; 3 the flames breaking into "
     "embers, the leaf bits falling; 4 the last embers. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
]
ICONS = [
    ("skill", "技能 1「刃叶」图标", "skill_icons[0] `asset/tft/icons/tft_cinderling_skill`",
     ICON + ": five sharp green leaf blades with glowing orange-red edges flying in a curve from the left and "
               "converging on one point at the right, small embers."),
    ("skill2", "技能 2「钻土突袭」图标", "skill_icons[1] `asset/tft/icons/tft_cinderling_skill2`",
     ICON + ": a little round wooden mask with one glowing orange eye bursting up out of cracked brown earth, clods and "
               "green leaves flying up."),
    ("ult", "大招「燎原叶暴」图标", "skill_icons[2] `asset/tft/icons/tft_cinderling_ult`",
     ICON + ": a whirl of burning green leaves wreathed in orange-red flames spiralling round a hot ember core, sparks "
               "flying."),
]
BIG_FX = ["p_full", "r_cast", "r_blaze"]
FLYING = ("a_leaf", "q_leaf", "r_leaf")

GROUPS = [
    ("a_leaf q_leaf r_leaf a_hit q_hit (the leaves)",
     ["zyra_base_q_leaves", "zyra_base_leaves", "sru_redbuff_ba_leaves_2x2_pink", "zyra_base_flash_green_sharp",
      "zyra_base_aa_mis_trail"]),
    ("p_full p_burn r_cast r_blaze r_hit (the red buff's fire)",
     ["sru_redbuff_sparks", "sru_red_skin04_embers", "brand_base_p_fire_mult", "brand_base_w_fireup",
      "brand_base_flame_ring"]),
    ("e_dig e_pop e_slow (the earth)",
     ["reksai_base_burrowed_q_tar_crown_dirt", "reksai_base_burrowed_q_ground_clump", "zyra_base_pebbles_4x4",
      "zyra_base_grass_clodbits", "zyra_base_rootgrasp"]),
    ("q_wound (the cut healing)",
     ["zyra_base_poison_spike", "zyra_base_flare_red", "sru_redbuffshare_centerglow_core", "zyra_base_sliver",
      "reksai_base_p_healing_spark"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", k=1 / PPU):
    """A design at game size (k of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The critter at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x()]
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    figs.append(k[ky.min():ky.max() + 1, kx.min():kx.max() + 1])
    Z, pad = 4, 6
    W = pad + sum(f.shape[1] + pad for f in figs)
    top = max(f.shape[0] for f in figs)
    img = Image.new("RGBA", (max(W * Z, 560), (pad + top + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + top
    x = pad
    for f in figs:
        img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST),
                            (x * Z, (base - f.shape[0]) * Z + 64))
        x += f.shape[1] + pad
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, W, 10):
        xx = (pad + i) * Z
        d.line([(xx, 8), (xx, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((xx + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"绯红树怪 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape, icons=True):
    h, w = shape[:2]
    L = []
    a = L.append
    n_ic = len(ICONS) if icons else 0
    a("# 绯红树怪：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/cinderling_design.png`："
      "3/4 朝右、四脚着地蹲着的矮胖小树皮兽：深紫褐的树皮身子，前腿上暖褐的木头甲片和青苔；背上一排浅绿色的高尖叶；"
      "脸是圆圆的木头面具，左边一只发光的橙色大眼睛，右边一个发光的螺旋纹，下面一排尖牙）。"
      f"它在游戏里是**高清**的（每个游戏格子里约 2.3×2.3 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/cinderling_size.png`：它缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是峡谷红 buff 营地（火星、红霸符的火光）、婕拉（叶子、草根）、布兰德（火焰）和雷克塞（钻地的泥土）的特效贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **绯红树怪是红 buff 营地的小树苗兽，特效都是它的味道**：**锋利的绿叶刃（边缘是发光的橙红刃口）**、红 buff 的**火星和橙红小火苗**、"
      "**棕色的泥块和草根**、一点树皮；不要闪电、不要蓝色、不要紫色魔法、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个火光和刃口都有最亮一档的黄白色芯，暗底上一眼能看见。**火焰、冲击环、尘土没有黑描边**（叶子和泥块可以有深色的边）。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a(f"> - **对称**：飞行的三张（{'、'.join(FLYING)}）**上下对称、朝右**（游戏按飞行方向转）；"
      "其余所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 交付方式：")
    a(">   - 每张生成后按格子取回（每格取多数颜色）。")
    a(">   - 交付 8 倍的 `cinderling_fx_<名字>.png`，和原尺寸的 `pixel_1x/`：严格按格子取色、透明度只有 0 和 255、逐格对称。Claude 直接用 `pixel_1x/` 切格导入。")
    if n_ic:
        a(">   - 图标交付 `cinderling_icon_<名字>.png`（64×64）。")
    a(">   - 另附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`。")
    a(f">   - 都放在 `outputs/{NAME.replace('_pack', '')}/` 里。**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。")
    a("> - **请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「余烬叶」 | 往前一蹦，甩出一片带火星的叶子 | `a_leaf` · `a_hit` |")
    a("| 被动「绯红霸符」 | 每放一个技能攻击力叠一层；叠满后普攻带灼烧 | `p_full` · `p_burn` |")
    a("| 技能 1「刃叶」 | 五片叶刃绕弧聚向目标：物理伤害 + 重伤 + 灼烧 | `q_leaf` · `q_hit` · `q_wound` · `p_burn` |")
    a("| 技能 2「钻土突袭」 | 钻进地里，从离敌人远的地方钻出来，周围敌人减速 | `e_dig` · `e_pop` · `e_slow` |")
    a("| 大招「燎原叶暴」 | 站起来，背上的叶子着火；几秒内不停朝附近敌人射燃烧的叶刃，自己攻速变快 | `r_cast` · `r_blaze` · `r_leaf` · `r_hit` · `p_burn` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("余烬火光（它的眼睛和螺旋纹）", FIRE), ("叶子", LEAF), ("木头（面具、腿上的甲片）", WOOD),
                        ("树皮（深紫褐）", BARK), ("泥土", DIRT)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `cinderling_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `cinderling_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `cinderling_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `cinderling_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_cinderling_fx`（小的）和 `tft_cinderling_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a(f"- {'、'.join(FLYING)} 断言上下对称（朝右），其余断言左右对称。")
    a("- a_leaf 是普攻的追踪弹道；q_leaf 是五片绕弧的追踪弹（伤害在它身上）；r_leaf 是大招每一下的追踪弹；a_hit、q_hit、r_hit 跟随目标；"
      "e_dig 在它钻下去的地方，e_pop 在它钻出来的地方；r_cast 是它身上的 caster 画面；p_full、r_blaze 是它身上的 buff；"
      "p_burn、q_wound、e_slow 是敌人身上的 buff。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="cinderling_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/cinderling_packs", help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    RF.REF, RF.GROUPS = REF, GROUPS
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_cinderling.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "cinderling_design.png"))
    shape = size_sheet(os.path.join(out, "design", "cinderling_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"cinderling_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"cinderling_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
                   if not a.only else []), f, ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
        os.makedirs(lp(os.path.dirname(zpath)), exist_ok=True)
        if os.path.exists(lp(zpath)):
            os.remove(lp(zpath))
        with zipfile.ZipFile(lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(lp(zpath)) // 1024, "KB")


if __name__ == "__main__":
    main()
