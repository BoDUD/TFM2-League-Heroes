#!/usr/bin/env python3
"""Build sohm_fx_pack.zip: step 3 of Sohm's sprite - Codex draws her effects and her three skill icons
(the tft dragons' way).

    python tools/lol/fx_ref_sohm.py            # the particle references -> C:/t/so_work/fxref
    python tools/art/pack_sohm_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name sohm_fx_redo_pack]

The pack (C:/t/so_work/fx/sohm_fx_pack, zipped into --out, default D:/TFM2-Workshop/sohm_packs) holds PROMPTS.md
(also written to assets/source/sohm/PROMPTS_FX.md), design/sohm_design.png (the approved idle at 4x on its own
squares), design/sohm_size.png (her at game size, 4x, on the arena colour with the ground line, a 10-px ruler and
the base fighter) and refs/tft_fx_ref.png (her own set-7 particle textures - grey shapes the game tints, grouped by the
effect they inform). The effects are the views the kit binds (tools/kit/build_sohm.py, the user's picks 2026-10-30:
mid, plan A 「潮汐之花」): view_projectiles a_bolt, q_wave, q_jump; view_effects a_hit, q_hit, e, r_bloom, r_hit;
view_buffs q_flower, e_shield, p_glow. Plus the three skill icons.
Her colours: aqua and deep sea blue with white foam (her body, her water), the pink of her spine fin and the gold of
her crown in the water flower.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the three flying pictures (FLYING) point right and are symmetric top to bottom (the game turns a projectile
with its flight).
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

TMP = "C:/t/so_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "sohm", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "sohm", "hd")
NAME = "sohm_fx_pack"
PPU = 1.8

WATER = "#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C"            # her water: white-cyan, aqua, sky, sea blue, deep blue
FOAM = "#FFFFFF, #DDF6FF, #A8DCEF"                                 # foam and spray
PETAL = "#FFE6F8, #FF9AD8, #E85AB8, #A02C88"                       # her spine fin: the flower's petals
GOLD = "#FFF4C0, #FFD25A, #F0A020, #A8640C"                        # her crown: the flower's heart
WA = f"a sea water ramp ({WATER})"
FO = f"a foam ramp ({FOAM})"
PE = f"a pink petal ramp ({PETAL})"
GO = f"a gold ramp ({GOLD})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave "
         "crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; "
         "flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams")
HER = "the sea dragon floats in the middle, not drawn: 32 squares wide and 40 tall, her head at the top right"
CHAMP = "a champion 16 squares wide and 34 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square deep blue frame with little gold "
        "corners, a dark sea-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square "
        "(32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_bolt", "普攻：水泡弹飞行中，4 帧循环", "view_projectiles `tft_sohm_a_bolt`（飞向目标，随飞行方向旋转；上下对称、朝右）", "10 × 8",
     "她吐出来的**水泡弹**：一颗圆圆的水球在右边（近白的高光、浅青到海蓝），后面拖着一小截往左的水花尾巴和两三颗小水珠。"
     "**朝右、上下对称**（游戏会按飞行方向转），4 帧循环。",
     WA + ", " + FO,
     "A WATER BOLT IN FLIGHT, 4 looping frames, " + TB + ": at the RIGHT a round water ball 6 squares across (a "
     "white-cyan highlight, aqua, a sea-blue rim), behind it to the LEFT a short spray tail 4 squares long tapering to "
     "a point, two or three tiny droplets; frames 1-4 the water rippling. " + MAGIC + ".",
     row(4, 10, 8) + CENTER),
    ("a_hit", "普攻：水泡弹打中，4 帧", "view_effects `tft_sohm_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "水泡弹打中：一下白色的水花，一圈浅青色的水滴往两边溅开，最后几颗小水泡。**左右对称**，4 帧。",
     WA + ", " + FO,
     "A WATER SPLASH, 4 frames, " + LR + ": 1 a white-cyan burst 4 squares across in the middle; 2 a crown of aqua "
     "water drops splashing up and out to both sides, 12 squares across; 3 the drops falling outward, a thin foam ring; "
     "4 a few small bubbles. " + MAGIC + ".",
     row(4, 14, 14) + CENTER),
    ("q_wave", "潮涌：冲出去的水浪，6 帧循环", "view_projectiles `tft_sohm_q_wave`（大表，从她身上朝目标直线飞，随飞行方向旋转；上下对称、朝右）", "40 × 16",
     "「潮涌」冲出去的**一道水浪**：横着躺在飞行方向上的一股水流，**右边是翻卷的浪头**（上下两边都卷着白色浪花），"
     "往左越来越细，拖着一串水珠和泡沫；中间亮青色、外圈海蓝。**朝右、上下对称**，6 帧循环。",
     WA + ", " + FO,
     "A RUSHING TORRENT OF WATER, 6 looping frames, " + TB + ": lying along the flight, the HEAD of the torrent at the "
     "RIGHT is a round churning mass of water 14 squares tall, its top and bottom edges curling into white foam crests "
     "(mirrored top to bottom), a white-cyan core; behind it to the LEFT the stream narrowing to 4 squares at the left "
     "edge, aqua in the middle, sea blue at the edges, a trail of droplets and foam flecks; frames 1-6 the crests "
     "rolling and the foam streaming back. " + MAGIC + ".",
     row(6, 40, 16) + CENTER),
    ("q_hit", "潮涌：水浪冲过，4 帧", "view_effects `tft_sohm_q_hit`（跟随被冲到的人，z 2；左右对称）", "16 × 16",
     "被水浪冲到：一下大一点的水花，水往上冲起再往两边落下，带一圈白色泡沫。**左右对称**，4 帧。",
     WA + ", " + FO,
     "A WAVE SPLASH, 4 frames, " + LR + ": 1 a white-cyan flash 6 squares across; 2 a column of aqua water bursting up "
     "and out, foam at its rim, 14 squares across; 3 the water falling back to both sides in curling drops; 4 a fading "
     "ring of foam and bubbles. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_flower", "潮涌：头上的水之花，6 帧循环", "view_buffs `tft_sohm_q_flower`（跟随带标记的敌人，在他头顶上方，z 3；左右对称）", "14 × 12",
     "带标记的敌人**头顶上飘着一朵水做的莲花**：几片半透明感的水蓝色花瓣，花瓣尖是粉色，花心一点金色，"
     "花下面滴下一两颗水珠；轻轻上下浮动、发光。**左右对称**，6 帧循环。",
     WA + ", " + PE + ", " + GO,
     "A FLOATING WATER LOTUS, 6 looping frames, " + LR + ": a lotus flower made of water, 12 squares wide and 9 tall, "
     "seen a little from the side: five aqua water petals (white-cyan highlights) opening upward with PINK TIPS, a small "
     "GOLD heart in the middle, one or two droplets falling from under it; frames 1-6 the flower bobbing up and down "
     "one square and its glow pulsing (every frame left-right symmetric). " + MAGIC + ".",
     row(6, 14, 12) + CENTER),
    ("q_jump", "潮涌：飞走的花，4 帧循环", "view_projectiles `tft_sohm_q_jump`（从倒下的人飞向下一个敌人，随方向旋转；上下对称、朝右）", "10 × 8",
     "带花的人倒下时**飞走的那朵花**：一朵收拢的小水莲花苞在右边（粉色的尖、金色的芯），后面拖着一小串往左的水珠。"
     "**朝右、上下对称**，4 帧循环。",
     WA + ", " + PE + ", " + GO,
     "A FLYING LOTUS BUD, 4 looping frames, " + TB + ": at the RIGHT a closed water lotus bud 5 squares across (aqua "
     "petals with pink tips, a gold glint at its heart), behind it to the LEFT a short trail of droplets and sparkles 4 "
     "squares long; frames 1-4 the bud glowing. " + MAGIC + ".",
     row(4, 10, 8) + CENTER),
    ("e", "海潮护佑：爪前的水波，5 帧", "view_effects `tft_sohm_e`（跟随她，z 3；左右对称）", "24 × 16",
     "她小爪往前一推：身前**一圈水波纹扩散开**（竖着的椭圆，像推开的水面），几颗水珠往外飞。**左右对称**，5 帧。",
     WA + ", " + FO,
     "A PUSHED RIPPLE, 5 frames, " + LR + ": 1 a small white-cyan glow 4 squares across in the middle; 2-3 two "
     "concentric aqua ripple rings (upright ellipses, 2 squares thick, white-cyan on their edges) spreading out from the "
     "middle, a few droplets flying outward to both sides; 4 the rings reaching the cell edge and thinning; 5 a few "
     "fading droplets. " + MAGIC + ".",
     row(5, 24, 16) + CENTER),
    ("e_shield", "海潮护佑：水盾，6 帧循环", "view_buffs `tft_sohm_e_shield`（跟随被保护的队友，罩住全身，z 3；左右对称）", "24 × 38",
     "被保护的队友**被一个水泡罩住**：一个竖着的椭圆水泡，只画**边上一圈**（浅青色、亮的地方近白），左上一道高光，"
     "里面几乎透明，几颗小气泡沿着边往上飘。**身体位置留空**。**左右对称**，6 帧循环。",
     WA + ", " + FO,
     "A WATER BUBBLE SHIELD, 6 looping frames, " + LR + ": round " + CHAMP + ": a tall upright ellipse 22 squares wide "
     "and 36 tall, ONLY ITS RIM drawn, 2 squares thick, aqua with white-cyan highlights where it is thinnest, a curved "
     "highlight streak on its upper left and the same on its upper right (mirrored); a few small bubbles rising along "
     "the rim on both sides; frames 1-6 the rim shimmering and the bubbles rising (every frame left-right symmetric). "
     "The inside of the bubble (the body) stays EMPTY. " + MAGIC + ".",
     row(6, 24, 38) + CENTER),
    ("r_bloom", "潮汐绽放：水莲爆开，7 帧", "view_effects `tft_sohm_r_bloom`（大表，在每朵花的人身上，不跟随，z 3；左右对称）", "40 × 40",
     "大招在每朵花的位置**炸开一朵巨大的水莲**：先是一朵大花苞在中间亮起，然后水做的花瓣往外、往上猛地绽开，"
     "中间冲起一根水柱，粉色的花瓣尖和金色的光点往四周飞，最后变成落下的水花和泡沫。**左右对称**，7 帧。",
     WA + ", " + FO + ", " + PE + ", " + GO,
     "A GIANT WATER LOTUS BURSTING, 7 frames, " + LR + ": 1 a glowing closed water lotus bud 10 squares across in the "
     "middle of the lower half, a gold light at its heart; 2 the bud swelling, its pink tips opening; 3 big aqua water "
     "petals bursting OPEN outward and upward, 36 squares across, white-cyan edges, PINK TIPS; 4 a column of water and "
     "foam shooting up from the heart to the top of the cell, gold sparks flying out in a symmetric star; 5 the petals "
     "breaking into big drops falling outward to both sides; 6 a wide ring of splash and foam at the bottom; 7 a few "
     "fading drops and bubbles. " + MAGIC + ".",
     row(7, 40, 40) + CENTER),
    ("r_hit", "潮汐绽放：被水花打中，4 帧", "view_effects `tft_sohm_r_hit`（在被炸到的人身上，z 3；左右对称）", "16 × 16",
     "被绽放的水花打中：一下白色的冲击，几片粉尖的水花瓣往两边飞散，几颗水珠。**左右对称**，4 帧。",
     WA + ", " + PE,
     "A PETAL SPLASH HIT, 4 frames, " + LR + ": 1 a white-cyan flash 6 squares across; 2 four aqua water petals with "
     "pink tips flung out to the four diagonals (mirrored), 14 squares across, droplets between them; 3 the petals "
     "breaking into drops; 4 a few fading drops. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("p_glow", "被动「碧波之力」：身边的潮水，6 帧循环", "view_buffs `tft_sohm_p_glow`（大表，跟随她，在她身后，z -1；左右对称）", "44 × 48",
     "她叠起潮汐时：身体**两侧和下面**绕着一圈流动的水（像小小的潮水环），几颗气泡往上冒，身下一圈淡淡的水光。"
     "**身体位置留空**（画在她身后，只露出边上）。**左右对称**，6 帧循环。",
     WA + ", " + FO,
     "A SWIRLING TIDE AURA, 6 looping frames, " + LR + ": round " + HER + ": a flowing ribbon of aqua water curling "
     "round her on BOTH sides (mirrored) from her middle down under her, 2-3 squares thick, white-cyan crests on it, "
     "small bubbles rising along both sides, a faint aqua glow ring under her (an ellipse 36 squares wide, 9 tall); "
     "frames 1-6 the water flowing round and the bubbles rising (every frame left-right symmetric). The middle of the "
     "cell (her body) stays EMPTY. " + MAGIC + ".",
     row(6, 44, 48) + CENTER),
]
ICONS = [
    ("skill", "技能 1「潮涌」图标", "skill_icons[0] `asset/tft/icons/tft_sohm_skill`",
     ICON + ": a big curling aqua wave crest rushing to the right, white foam on its lip, and above it a small water "
               "lotus with pink petal tips and a gold heart."),
    ("skill2", "技能 2「海潮护佑」图标", "skill_icons[1] `asset/tft/icons/tft_sohm_skill2`",
     ICON + ": a round shining water bubble shield with a white highlight, a little pale blue dragon claw held up in "
               "front of it, small bubbles rising."),
    ("ult", "大招「潮汐绽放」图标", "skill_icons[2] `asset/tft/icons/tft_sohm_ult`",
     ICON + ": a huge water lotus bursting open, aqua petals with pink tips flung outward, a column of water and gold "
               "sparks rising from its heart."),
]
BIG_FX = ["q_wave", "r_bloom", "p_glow"]
FLYING = ("a_bolt", "q_wave", "q_jump")

GROUPS = [
    ("a_bolt a_hit (the water bolt, its splash)",
     ["tft7_aquaticdragon_base_ba_mis_water01", "tft7_aquaticdragon_base_missilefront", "tft_splash_ring",
      "base_bubble01"]),
    ("q_wave q_hit (Tideblossom's wave)",
     ["tft7_aquaticdragon_base_q_trail_fill", "tft7_aquaticdragon_base_wave_foam_stylized_01",
      "tft7_aquaticdragon_base_q_linearsplashes_02", "tft_smearwater"]),
    ("q_flower q_jump r_bloom (the water flower, its burst)",
     ["tft7_aquaticdragon_base_q_dash_tar_splash", "tft_water5",
      "tft7_aquaticdragon_base_q_03", "tft7_aquaticdragon_base_q_lensflare01"]),
    ("r_bloom r_hit (the bloom's splash)",
     ["tft7_aquaticdragon_base_q_ripples02", "tft7_aquaticdragon_base_q_groundwater01",
      "tft7_aquaticdragon_base_q_water_spike_dark", "tft7_aquaticdragon_base_circledissolve_flipbook"]),
    ("e e_shield p_glow (the ripple, the bubble shield, the tide)",
     ["tft_base_shieldring", "tft7_aquaticdragon_base_q_heath_swirl", "tft_base_waves", "tft_bubble01"]),
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
    """Sohm at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"索姆 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 索姆：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/sohm_design.png`："
      "正侧面朝右、浮在空中、身子在身下盘成一圈的东方海龙：浅水蓝的蛇形身子、粉色背鳍、深绿海草尾鳍；青绿到深紫的鬃毛；"
      "金橙头冠、紫色宝石、两根珊瑚红鹿角、尖耳朵、蓝色杏仁眼）。"
      f"索姆在游戏里是**高清**的（每个游戏格子里约 1.8×1.8 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/sohm_size.png`：索姆缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里索姆自己的特效贴图（水弹、潮涌的水流和浪花、水之花、水花爆开、波纹）"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **索姆是海龙，特效都是水**：清澈的浅青到海蓝的水、近白的高光、翻卷的浪头、圆圆的水珠和气泡、白色泡沫；"
      "**水之花**是一朵水做的莲花，花瓣尖是她背鳍的粉色，花心是她头冠的金色。不要火、不要闪电、不要紫烟、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个水花都有最亮一档或近白的高光，暗底上一眼能看见。**水、泡沫、波纹没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人（水盾只画水泡的边）。")
    a(f"> - **对称**：**三张飞行的画面（{'、'.join(FLYING)}）朝右、严格上下对称**（游戏会按飞行方向转）；"
      "其余所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sohm_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `sohm_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「水泡弹」 | 吐出一颗水弹 | `a_bolt` · `a_hit` |")
    a("| 被动「碧波之力」 | 每放一个技能叠一层潮汐（法强、攻速），最多 5 层 | `p_glow` |")
    a("| 技能 1 =「潮涌」 | 一道水浪冲向还没开花的敌人，沿途都受伤，目标头上开出水之花；带花的人倒下，花飞到附近的敌人身上 | `q_wave` · `q_hit` · `q_flower` · `q_jump` |")
    a("| 技能 2 =「海潮护佑」 | 小爪一推，给身边血最少的队友一个水盾、加攻速 | `e` · `e_shield` |")
    a("| 大招 =「潮汐绽放」 | 所有水之花同时炸开成巨大的水莲，周围的敌人都受伤 | `r_bloom` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**水、泡沫、波纹没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("海水（她的身子和水）", WATER), ("泡沫和水花", FOAM), ("花瓣粉（她的背鳍）", PETAL),
                        ("金（她的头冠）", GOLD)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `sohm_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `sohm_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `sohm_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `sohm_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_sohm_fx`（小的）和 `tft_sohm_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a(f"- {'、'.join(FLYING)} 断言上下对称（朝右），其余断言左右对称。")
    a("- q_wave 由 tft.dll 直线发射（穿过所有人）；q_jump 由 tft.dll 从倒下的人发出；q_flower 挂在敌人头顶（buff，z 3）；"
      "e_shield 罩住被保护的队友（buff，z 3）；p_glow 是她身后的 caster buff（z -1）；r_bloom 在每朵花的人身上（不跟随，z 3）；"
      "a_hit、q_hit、r_hit 打在目标身上；e 跟随她。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="sohm_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/sohm_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_sohm.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "sohm_design.png"))
    shape = size_sheet(os.path.join(out, "design", "sohm_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"sohm_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"sohm_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
