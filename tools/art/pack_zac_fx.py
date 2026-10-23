#!/usr/bin/env python3
"""Build zac_fx_pack.zip: step 3 of Zac's sprite - Codex draws his effects (pack_aurora_fx.py's way).

    python tools/lol/fx_ref_zac.py              # League's particle textures -> C:/t/za_work/fxref (Riot's art, local only)
    python tools/art/pack_zac_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name zac_fx_redo_pack]

The pack (C:/t/za_work/fx/zac_fx_pack, zipped into --out, default dist/zac_packs) holds PROMPTS.md (also written to
assets/source/zac/PROMPTS_FX.md), design/zac_design.png (the idle at 4x, its own squares), design/zac_size.png (at game
size, 4x, on the arena colour with the ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png (League's
own particle textures for Zac, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_zac.py, the user's picks 2026-10-23: jungle, layout A - Q / E /
R, W in the attack): view_projectiles q_fist, b_fly; view_effects a_hit, q_hit, q_slam (big), w_burst (big), w_hit,
e_land (big), e_hit, r_land (big), r_hit, b_lie, b_pick; view_buffs q_held, slow (q_slow and r_slow share it).
League's colours: Zac's living goo - a translucent bright GREEN slime with yellow-green wet highlights, dark green
depths, white glints; splats, drips, droplets and stretched strands. Red side: the client never mirrors an effect
picture, so every hit, buff, ground and body picture is symmetric left to right; a projectile is turned with its flight,
so it is drawn flying right and symmetric top to bottom.
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

TMP = "C:/t/za_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "zac", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "zac", "hd")
NAME = "zac_fx_pack"
PPU = 1.5

GOO = "#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A"     # Zac's living goo: wet yellow-green to deep green
DEEP = "#3A9A66, #1E6448, #0E3A2C, #06201A"                       # the dark green depths inside the slime
GLINT = "#FFFFFF, #F2FFE0, #D2F6A0"                              # the wet white glints
DUST = "#E6E0C8, #BDB394, #8C8466, #5E5844"                       # the ground's dust where he lands
GO_ = f"a living green goo ramp ({GOO})"
DE = f"a dark green depth ramp ({DEEP})"
GL = f"a wet white glint ramp ({GLINT})"
DU = f"a pale dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
row = RF.row
GOOEY = ("everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and "
         "white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, "
         "no electricity, no smooth neon beams")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HIM = "Zac stands in the middle, not drawn: 58 squares wide and 44 tall (to the tendril's tip)"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack and W
    ("a_hit", "普攻：大拳头砸中，3 帧", "view_effects `league_zac_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "拳头砸中敌人：一团绿色黏液啪地溅开，中间一个白亮的闪光，四周甩出几颗圆圆的黏液滴。**左右对称**，3 帧。",
     GO_ + ", " + GL,
     "A GOO PUNCH LANDING, 3 frames, " + LR + ": 1 a white-green flash 5 squares across with a splat of green goo round "
     "it; 2 the goo splashing out into a ring of round droplets and short drips 13 across at mirrored places; 3 the "
     "droplets further out and smaller, dimming to their darker shades. " + GOOEY + ".",
     row(3, 14, 14) + CENTER),
    ("w_burst", "不稳定物质：扎克身上爆开的黏液，6 帧", "view_effects `league_zac_w_burst`（大表，在他身上，不跟随，z -1；左右对称）",
     "64 × 44",
     "不稳定物质（参考 goo_02、chunk、goo_e_pool）：扎克**整个人往外一鼓，一圈黏液从他身上往四周炸开**——地上溅开一个绿色的椭圆水花圈，"
     "空中飞出十几块大小不一的黏液块和水滴，越飞越远越小。扎克站在正中间不画（58 格宽、44 格高），**身体的位置留空**。**左右对称**，6 帧。",
     GO_ + ", " + DE + ", " + GL,
     "AN EXPLOSION OF GOO, 6 frames, " + LR + "; " + HIM + " - leave his body's place EMPTY: 1 a bulging green rim "
     "hugging his outline with white glints; 2 the rim bursting outward: a dozen goo chunks and round droplets (2 to 5 "
     "squares) flying out all round at mirrored places, a green splash ring opening " + FEET + " 40 wide; 3 the chunks "
     "further out, the ring 56 wide with goo drips rising from its edge; 4 the chunks at the cell's edge, smaller, the "
     "ring 62 wide and thinner; 5 a few drops left, the ring breaking into puddle spots; 6 the last spots fading. " + GOOEY + ".",
     row(6, 64, 44) + CENTER),
    ("w_hit", "不稳定物质：黏液砸中，3 帧", "view_effects `league_zac_w_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "被不稳定物质的黏液块砸中：一块黏液啪地糊在敌人身上溅开，几颗小水滴。**左右对称**，3 帧。",
     GO_ + ", " + GL,
     "A GOO CHUNK SPLATTING, 3 frames, " + LR + ": 1 a green goo chunk 5 squares across with a white glint; 2 it "
     "splatting flat into a wide splash 11 across with four short drips at mirrored places; 3 the splash dripping down, "
     "fading. " + GOOEY + ".",
     row(3, 12, 12) + CENTER),
    # ---- Q Stretching Strikes
    ("q_fist", "延伸打击：拉长的手臂和大手，4 帧循环", "view_projectiles `league_zac_q_fist`（弹道，z 2；上下对称）", "30 × 12",
     "延伸打击（参考 q_stretcharm、q_orb_mis）：扎克**像橡皮一样拉长的绿色手臂**——一截长长的黏液手臂，前面是**张开的大手（三根粗手指朝右张开）**，"
     "后面的手臂一截截有点波纹。**朝右飞、上下对称**，4 帧循环（手指一张一合、手臂上的高光往后走）。",
     GO_ + ", " + DE + ", " + GL,
     "A STRETCHED RUBBER ARM, 4 looping frames, " + TB + ": at the right a BIG OPEN GREEN HAND 10 squares tall with three "
     "thick fingers spread forward (one in the middle, two mirrored above and below it), behind it a long stretched arm "
     "of glossy green goo 20 squares long and 6 thick with a dark green underside on both edges (mirrored) and a yellow-"
     "green highlight band along its middle; the fingers open and close a little and the highlight slides back along "
     "the arm frame to frame. " + GOOEY + ".",
     row(4, 30, 12) + CENTER),
    ("q_hit", "延伸打击：抓中，4 帧", "view_effects `league_zac_q_hit`（跟随目标，z 2；左右对称）", "16 × 18",
     "大手抓中敌人：一团绿色黏液啪地糊在敌人身上，拉出几根黏糊糊的丝往下滴，白色闪光一下。**左右对称**，4 帧。",
     GO_ + ", " + DE + ", " + GL,
     "A GOOEY GRAB, 4 frames, " + LR + ": 1 a white flash 5 squares across on the target's chest; 2 a big green goo splat "
     "15 across wrapping round it; 3 sticky strands stretching down from the splat at mirrored places, a few drops; "
     "4 the strands dripping, fading. " + TARGET + ".",
     row(4, 16, 18) + CENTER),
    ("q_held", "延伸打击：被抓住的敌人身上的黏液手印，4 帧循环", "view_buffs `league_zac_q_held`（跟随，胸口，z 3；左右对称）",
     "12 × 12",
     "被扎克抓住的敌人胸口：一团**黏在身上的绿色黏液**（像一只手按着），边缘慢慢往下滴，一闪一闪的高光。**左右对称**，4 帧循环。",
     GO_ + ", " + GL,
     "A GOO GRIP STUCK ON THE TARGET, 4 looping frames, " + LR + ": a glossy green goo blob 10 squares across like a "
     "hand pressed on the chest, three short drips under it at mirrored places that stretch and shorten, a yellow-green "
     "highlight that pulses. " + GOOEY + ".",
     row(4, 12, 12) + CENTER),
    ("q_slam", "延伸打击：甩人砸地，6 帧", "view_effects `league_zac_q_slam`（大表，在他身前的地上，不跟随，z 2；左右对称）",
     "56 × 26",
     "把人甩过来砸在地上（参考 goo_e_pool、dust）：地上溅起一个**绿色的黏液水花圈**，中间一下白光，四周飞起黏液滴和尘土。**左右对称**，6 帧。",
     GO_ + ", " + DU + ", " + GL,
     "A SLAM ON THE GROUND, 6 frames, " + LR + ": 1 a white-green flash 10 squares wide " + FEET + "; 2 a splash of green "
     "goo bursting up from it 30 wide with pale dust puffs at both sides; 3 a goo splash ring 46 wide on the ground with "
     "droplets thrown up in arcs at mirrored places; 4 the ring 54 wide, the droplets falling, the dust spreading; "
     "5 puddle spots and settling dust; 6 fading. " + GOOEY + ".",
     row(6, 56, 26) + CENTER),
    ("slow", "减速：脚下的黏液，4 帧循环（Q 和 R 的减速共用）",
     "view_buffs `league_zac_q_slow` / `r_slow`（tag `slow`，跟随，脚下，z -1；左右对称）", "18 × 7",
     "被减速的敌人脚下：一小滩**黏糊糊的绿色黏液**粘着脚，边上冒一两个小泡。**左右对称**，4 帧循环。",
     GO_ + ", " + DE,
     "A STICKY GOO PUDDLE, 4 looping frames, " + LR + ": a flat glossy green puddle " + FEET + " 16 wide and 5 tall with a "
     "darker rim, two small bubbles at mirrored places that swell and pop in turn, a highlight sliding across. " + GOOEY + ".",
     row(4, 18, 7) + CENTER),
    # ---- E Elastic Slingshot
    ("e_land", "橡筋弹弓：落地，6 帧", "view_effects `league_zac_e_land`（大表，在他落地的地方，不跟随，z -1；左右对称）", "66 × 28",
     "弹弓落地（参考 goo_e、goo_e_pool、dust）：扎克重重砸在地上，**一大圈绿色黏液水花炸开**，地上一圈波纹往外推，尘土和黏液滴飞起。"
     "比甩人砸地更大。**左右对称**，6 帧。",
     GO_ + ", " + DU + ", " + GL,
     "A HEAVY LANDING, 6 frames, " + LR + "; " + HIM + " - leave his body's place EMPTY: 1 a white-green impact flash 24 "
     "wide " + FEET + "; 2 a crown of green goo splashing up all round 40 wide with pale dust bursting out at both sides; "
     "3 a goo shockwave ring 56 wide on the ground, droplets and dust thrown out at mirrored places; 4 the ring 64 wide, "
     "thinner, the droplets falling; 5 puddle spots and settling dust; 6 fading. " + GOOEY + ".",
     row(6, 66, 28) + CENTER),
    ("e_hit", "橡筋弹弓：被撞飞，4 帧", "view_effects `league_zac_e_hit`（跟随目标，z 2；左右对称）", "14 × 20",
     "被弹弓砸中击飞的敌人：脚下一团黏液往上溅，几颗水滴往上飞。**左右对称**，4 帧。",
     GO_ + ", " + GL,
     "A KNOCK-UP SPLASH, 4 frames, " + LR + ": 1 a green goo splash bursting up from the target's feet 12 wide; 2 goo "
     "spikes and droplets flying upward past the target's sides at mirrored places; 3 the droplets high, the splash "
     "falling; 4 fading. " + TARGET + ".",
     row(4, 14, 20) + CENTER),
    # ---- R Let's Bounce!
    ("r_land", "动感弹球：每一下落地，5 帧", "view_effects `league_zac_r_land`（大表，在他落地的地方，不跟随，z -1；左右对称）",
     "58 × 24",
     "弹球每一次落地（参考 r_puddle、r_bubble）：扎克压扁砸在地上，**地上溅开一个绿色黏液水花圈**，几个泡泡和水滴弹起来。"
     "比弹弓落地小一点、快一点。**左右对称**，5 帧。",
     GO_ + ", " + DE + ", " + GL,
     "A BOUNCE LANDING, 5 frames, " + LR + "; " + HIM + " - leave his body's place EMPTY: 1 a flat green goo splat 36 "
     "wide " + FEET + " with a white glint; 2 a splash ring 50 wide with goo bubbles and droplets bouncing up at mirrored "
     "places; 3 the ring 56 wide, the bubbles popping; 4 puddle spots; 5 fading. " + GOOEY + ".",
     row(5, 58, 24) + CENTER),
    ("r_hit", "动感弹球：被弹中，3 帧", "view_effects `league_zac_r_hit`（跟随目标，z 2；左右对称）", "14 × 18",
     "被弹球砸中击飞的敌人：一团黏液从脚下弹起来糊在身上，几颗泡泡。**左右对称**，3 帧。",
     GO_ + ", " + GL,
     "A BOUNCE HIT, 3 frames, " + LR + ": 1 a green goo splash rising from the target's feet 12 wide; 2 goo droplets "
     "and two bubbles flying up past its sides at mirrored places; 3 fading. " + TARGET + ".",
     row(3, 14, 18) + CENTER),
    # ---- passive Cell Division: the blobs
    ("b_fly", "细胞分裂：甩出去的黏液块，3 帧循环", "view_projectiles `league_zac_b_fly`（弹道，z 2；上下对称）", "10 × 6",
     "技能打中英雄时从扎克身上甩出去的一小块黏液：一颗圆圆的绿色黏液球，后面拖两三颗小水滴。**朝右飞、上下对称**，3 帧循环。",
     GO_ + ", " + GL,
     "A FLYING GOO BLOB, 3 looping frames, " + TB + ": a round glossy green goo blob 5 squares across at the right with a "
     "white glint, two or three tiny droplets trailing behind it on the left that shift frame to frame. " + GOOEY + ".",
     row(3, 10, 6) + CENTER),
    ("b_lie", "细胞分裂：地上的黏液块，3 帧循环", "view_effects `league_zac_b_lie`（在地上，不跟随，z -1；左右对称；每 15 帧放一次）",
     "10 × 7",
     "掉在地上等扎克去吃的黏液块（参考 blob_health）：一小团**圆鼓鼓的绿色黏液**趴在地上，轻轻地一鼓一缩，顶上一格白亮。"
     "**左右对称**，3 帧循环（一共 15 帧长，循环放）。",
     GO_ + ", " + DE + ", " + GL,
     "A GOO BLOB ON THE GROUND, 3 looping frames, " + LR + ": a small round glossy green blob 8 squares wide and 5 tall "
     "sitting on the ground, a darker flat rim at its foot, a white glint on top; it wobbles - a little taller and "
     "narrower, then lower and wider. " + GOOEY + ".",
     row(3, 10, 7) + CENTER),
    ("b_pick", "细胞分裂：吃回黏液块回血，4 帧", "view_effects `league_zac_b_pick`（跟随他，z 3；左右对称）", "30 × 40",
     "扎克走过去把黏液块吸回身上：几团绿色黏液往他身上飞回去融进身体，冒出一圈淡绿色的小光点（回血）。扎克在中间不画，**身体的位置留空**。**左右对称**，4 帧。",
     GO_ + ", " + GL,
     "ABSORBING A BLOB, 4 frames, " + LR + "; the body in the middle not drawn (leave a place 26 squares wide and 36 "
     "tall EMPTY): 1 two goo blobs at the bottom corners moving in; 2 the blobs merging into the body's lower edge with "
     "a green splash; 3 small pale green sparkles rising up both sides at mirrored places; 4 the sparkles at the top, "
     "fading. " + GOOEY + ".",
     row(4, 30, 40) + CENTER),
]
BIG_FX = ["w_burst", "q_slam", "e_land", "r_land"]
FLYING = ["q_fist", "b_fly"]
FORWARD = []

GROUPS = [
    ("a_hit q_hit q_held (the punch, the grab)", ["zac_goo_03", "zac_goo_e_pool", "zac_specs_02", "zac_base_q_orb_mis"]),
    ("q_fist (Stretching Strikes)", ["zac_base_q_stretcharm", "zac_base_q_orb_mis", "zac_base_q_shape_mis", "zac_goo_02"]),
    ("q_slam w_burst w_hit (the slam, Unstable Matter)", ["zac_goo_02", "zac_dust_01", "zac_goo_e_pool", "zac_specs_02"]),
    ("e_land e_hit (Elastic Slingshot)", ["zac_goo_e", "zac_goo_e_pool", "zac_dust_01", "zac_goo_03"]),
    ("r_land r_hit slow (Let's Bounce!)", ["zac_base_r_puddle", "zac_base_r_bubble", "zac_goo_e", "zac_goo_03"]),
    ("b_lie b_pick b_fly (Cell Division)", ["zac_blob_health", "zac_goo_e", "zac_specs_02", "zac_goo_03_ot"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", ppu=PPU):
    """A design at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / ppu, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Zac at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"扎克 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 生化魔人 扎克：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/zac_design.png`：半透明亮绿色黏液做的大块头，身体里深绿色的纹路，"
      "驼着背，头埋在两个大肩膀中间，两只发黄光的眼睛，咧开的大嘴和尖牙，头顶一根弯触须，两条又粗又长的手臂、三根粗手指的大手，短粗的腿）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽（高×宽，连触须）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/zac_size.png`：扎克放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里扎克自己的特效贴图（大多是灰度或绿色的形状），按用在我们哪张特效分好了行，只在本地用。"
      "**扎克是活的黏液，所有特效都是他的黏液**：亮绿色、半透明的光泽、几块大的黄绿色湿亮高光和白色亮点、深绿色的暗部；"
      "黏液块、水花、水滴、往下滴的丝、拉长的橡皮手臂；不要火、不要电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每块黏液都有最亮一档或白色的亮点，暗底上一眼能看见。")
    a("> - **黏液、水花、冲击波、尘土都没有黑描边**（用它自己最深的一档）。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" +
      "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `zac_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/zac_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 大拳头砸 | `a_hit` |")
    a("| 被动「细胞分裂」 | 技能打中英雄时甩出一块黏液落在地上，扎克走过去吃掉回血（复活在扩展包里） | `b_fly` · `b_lie` · `b_pick` |")
    a("| 普攻里的「不稳定物质」（W） | 冷却好了普攻时身上的黏液往四周炸开，按敌人最大生命值加伤害 | `w_burst` · `w_hit` |")
    a("| 技能 1 =「延伸打击」 | 手臂像橡皮一样拉长抓住敌人，再把他甩过来砸在地上 | `q_fist` · `q_hit` · `q_held` · `q_slam` · `slow` |")
    a("| 技能 2 =「橡筋弹弓」 | 两手按地把自己拉成弹弓，远远飞过去砸在地上，击飞一圈 | `e_land` · `e_hit` |")
    a("| 大招 =「动感弹球」 | 压扁身体连弹 4 次，每次落地击飞、减速 | `r_land` · `r_hit` · `slow` |\n")
    a("连招：**弹弓落地 → 不稳定物质**（落地马上炸开），**弹弓击飞 → 延伸打击**（马上抓住被击飞的英雄），"
      "**延伸打击甩人 → 动感弹球**，**最后一弹 → 不稳定物质**（并刷新）。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**黏液、水花、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **都是扎克的黏液**：亮绿、黄绿高光、白色亮点、深绿暗部；每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的亮点。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("黏液·绿", GOO), ("暗部·深绿", DEEP), ("亮点·白", GLINT), ("尘土·浅灰黄", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（水花圈、冲击波、脚下的黏液）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `zac_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `zac_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_zac_fx`（小的）和 `league_zac_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_zac.py 的 views；两个减速用 `slow`）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称；b_lie 每 15 帧盖一次（3 帧循环），q_held 跟随约 34 帧，slow 1 秒。")
    a("- 用 `pixel_1x/` 切格（import_aurora_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="zac_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "zac_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_zac.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "zac_design.png"))
    shape = size_sheet(os.path.join(out, "design", "zac_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"zac_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else ("none (forward)" if x[0] in FORWARD else "left-right")}
                   for x in FX], f, ensure_ascii=False, indent=1)
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
