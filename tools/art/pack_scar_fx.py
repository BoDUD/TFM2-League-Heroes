#!/usr/bin/env python3
"""Build scar_fx_pack.zip: step 3 of Scar's sprite - Codex draws his effects and his three skill icons
(pack_violet_fx.py's way).

    python tools/lol/fx_ref_scar.py           # his TFT particle textures -> C:/t/sc_work/fxref
    python tools/art/pack_scar_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name scar_fx_redo_pack]

The pack (C:/t/sc_work/fx/scar_fx_pack, zipped into --out, default dist/scar_packs) holds PROMPTS.md (also written to
assets/source/scar/PROMPTS_FX.md), design/scar_design.png (the approved idle at 4x on its own squares),
design/scar_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (his own TFT particle textures - grey shapes the game tints - grouped by the effect
they inform). The effects are the views the kit binds (tools/kit/build_scar.py, the user's picks 2026-10-28: top,
plan A 「野火坦克」): view_projectiles q_bomb; view_effects a_hit, p_hit, p_heal, q_hit, e_hit, r_bomb, r_land, r_hit;
view_buffs q_stun, r_guard. Plus the three skill icons. The hoverboard and the sweep are in his own frames.
His colours: the Firelights' TEAL-GREEN glow (his TFT bomb's own band), a hot blast orange-white, his spear blade's
purple-magenta GRAFFITI paint, its gold, the bombs' dark metal, Zaun dust.
Red side: every picture is symmetric left to right (the client never mirrors an effect picture), and the bomb is round
(its picture turns with its flight).
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

TMP = "C:/t/sc_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "scar", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "scar", "hd")
NAME = "scar_fx_pack"
PPU = 2.0

GOLD = "#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010"              # his spear's gold graffiti and butt cap
FIRE = "#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48"              # the Firelights' teal-green glow (his bombs, the boards)
IMPACT = "#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C"            # a hot blast
PAINT = "#FFD8F6, #F27AD8, #C23AB8, #7A1E86, #3E0E50"             # graffiti paint: his spear blade's purple-magenta
DUST = "#F0E2C8, #C8AE88, #9A7E5C, #64503A"                       # Zaun dust and grit
STEEL = "#E8ECF4, #B4BCCC, #7C8698, #4A5262, #262A34"             # the bombs' metal shell
GD = f"a gold ramp ({GOLD})"
FG = f"a Firelight teal-green ramp ({FIRE})"
IM = f"a hot blast ramp ({IMPACT})"
PT = f"a graffiti paint ramp ({PAINT})"
DS = f"a dust brown ramp ({DUST})"
SL = f"a dark metal ramp ({STEEL})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and "
         "hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat "
         "shades, crisp shapes; no magic runes, no smooth neon beams, no lightning")
HIM = "the lanky masked man stands in the middle, not drawn: 30 squares wide and 38 tall"
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark purple frame with little "
        "riveted gold corners, a deep navy-teal inside, the symbol big and centred, lit from the upper left; pixel art at "
        "2 px a square (32 x 32 squares), chunky and readable at 64 px")
SPEAR = ("his long SPEAR (a dark purple shaft with copper bands, a broad purple arrowhead blade with gold graffiti "
         "marks)")
BOARD = ("a small Firelight HOVERBOARD (a dark grey-brown deck with a raised nose, a row of glowing teal-green thruster "
         "vents underneath)")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：长矛刺中，4 帧", "view_effects `tft_scar_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "矛尖扎在人身上：一个白热的**四角星闪光**，几颗金色和紫色的碎屑往两边崩开，一小圈冲击环。**左右对称**，4 帧。",
     IM + ", " + GD + ", " + PT,
     "A SPEAR STAB IMPACT, 4 frames, " + LR + ": 1 a white-hot four-pointed STAR flash 8 squares across; 2 a short "
     "orange shock ring 12 squares wide and 6 tall, gold and purple chips flying out to both sides (mirrored); 3 the "
     "ring thinner and wider, the chips farther; 4 the last glints fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("p_hit", "野火冲刺：滑板冲过去捅一矛，5 帧", "view_effects `tft_scar_p_hit`（跟随目标，z 2；左右对称）", "24 × 24",
     "被动冲刺的那一矛：比普攻大，一个白热的星形闪光外面裹着一圈**青绿色的野火光**，青绿色和金色的火星往两边四溅，最后几缕青绿色的烟。"
     "**左右对称**，5 帧。",
     IM + ", " + FG + ", " + GD,
     "A FIRELIGHT DASH STRIKE, 5 frames, " + LR + ": 1 a big white-hot STAR flash 10 squares across ringed with teal-"
     "green glow; 2 a teal-green shock ring 20 squares wide and 8 tall, teal and gold sparks spraying out to both sides "
     "(mirrored); 3 the ring wider and thinner, the sparks farther, two small teal smoke puffs; 4 the smoke rising and "
     "thinning; 5 the last wisps. " + MAGIC + ".",
     row(5, 24, 24) + CENTER),
    ("p_heal", "野火冲刺：冲完回血，5 帧", "view_effects `tft_scar_p_heal`（跟随他，z 3；左右对称）", "36 × 42",
     "冲刺打中后回一口血：脚下「呼」地一圈**青绿色的光环**，身体两侧往上冒一串青绿色和白色的小光点（像野火帮的萤火），头顶一闪。"
     "身体位置留空。**左右对称**，5 帧。",
     FG,
     "A FIRELIGHT HEAL, 5 frames, " + LR + ", " + HIM + ": 1 a teal-green flash ring " + GROUND_E + " 14 squares wide; "
     "2 the ring 28 squares wide and 8 tall, two columns of teal-green and white firefly motes (1-2 squares) rising at "
     "both sides of him (mirrored); 3 the motes up at his shoulders, a white glint over his head; 4 the ring fading, "
     "the motes higher; 5 the last motes. The middle (the body) left empty. " + MAGIC + ".",
     row(5, 36, 42) + CENTER),
    ("q_bomb", "水坑狙击惊喜：飞出去的炸弹，4 帧循环", "view_projectiles `tft_scar_q_bomb`（随飞行方向转；必须是圆的）", "10 × 10",
     "他扔出去的土炸弹：一个**圆圆的深色金属球**，中间一圈发光的**青绿色**条纹，顶上一根引线冒着小火星。飞行时整张图会跟着方向转，"
     "所以**画成圆的、转起来一样**：引线的火星画小一点，4 帧里球慢慢转（条纹的位置变），火星一闪一闪。",
     SL + ", " + FG + ", " + IM,
     "A THROWN BOMB IN FLIGHT, 4 looping frames, ROUND and the same turned any way (the picture is rotated with its "
     "flight): a ball 8 squares across of dark metal with a glowing teal-green band round its middle and a tiny "
     "spark (1-2 squares) at its fuse on top; frames 1-4 the band shifting round the ball as it spins, the spark "
     "flickering. " + MAGIC + ".",
     row(4, 10, 10) + CENTER),
    ("q_hit", "水坑狙击惊喜：炸弹炸开（晕眩），6 帧", "view_effects `tft_scar_q_hit`（跟随目标，z 2；左右对称）", "34 × 34",
     "炸弹在人身上炸开：一团**青绿色和橙色**的爆炸火球，往外喷出几块**紫红色的涂鸦颜料**（像泼出去的颜料点），金属碎片往两边飞，"
     "最后剩一团烟。比普攻大得多。**左右对称**，6 帧。",
     IM + ", " + FG + ", " + PT + ", " + DS,
     "A BOMB BLAST, 6 frames, " + LR + ": 1 a white-hot flash 10 squares across; 2 a round fireball 22 squares across "
     "- a teal-green outer burst with a hot orange-white core; 3 the fireball at 30 squares, splats of purple-magenta "
     "GRAFFITI PAINT (blobs and drops 2-4 squares) and dark metal shards flung out to both sides (mirrored); 4 the fire "
     "breaking into puffs, the paint drops falling; 5 grey-green smoke rising; 6 the last smoke and paint specks. "
     + MAGIC + ".",
     row(6, 34, 34) + CENTER),
    ("q_stun", "水坑狙击惊喜：被炸晕，6 帧循环", "view_buffs `tft_scar_q_stun`（跟随被晕的人，头顶，z 3；左右对称）", "20 × 10",
     "被炸晕的人头顶：几颗**青绿色和金色的小星星**转圈，中间一点小烟。**左右对称**，6 帧循环。",
     FG + ", " + GD,
     "A STUN OVER THE HEAD, 6 looping frames, " + LR + ": in the cell (it rides over the unit's head) three small "
     "stars (3 squares) in teal-green and gold circling on a flat ring 16 squares wide and 4 tall, a tiny smoke puff in "
     "the middle; frames 1-6 the stars going round. " + MAGIC + ".",
     row(6, 20, 10) + CENTER),
    ("e_hit", "长矛横扫：扫中（打退），4 帧", "view_effects `tft_scar_e_hit`（跟随目标，z 2；左右对称）", "22 × 22",
     "长矛横着扫到人：一道**横向的白热光弧**（左右对称的扁月牙，两头尖），金色碎屑往两边飞，一团尘土。**左右对称**，4 帧。",
     IM + ", " + GD + ", " + DS,
     "A SWEEPING SPEAR HIT, 4 frames, " + LR + ": 1 a flat white-hot slash ARC 18 squares wide and 5 tall, both ends "
     "pointed, centred (the same mirrored); 2 the arc wider and thinner, gold chips flying out to both sides; 3 a puff "
     "of dust in the middle, the arc fading; 4 the last dust. " + MAGIC + ".",
     row(4, 22, 22) + CENTER),
    ("r_bomb", "野火突袭：一路丢下的燃烧弹，6 帧", "view_effects `tft_scar_r_bomb`（留在他经过的地上，z -1；左右对称）", "40 × 24",
     "他踩着滑板冲过去时丢在地上的燃烧弹：地上「轰」地炸开一团**青绿色和橙色的火**，往上窜几簇火苗，地上溅开一圈紫红色的涂鸦颜料，"
     "最后火苗变小、剩一片烧焦的痕迹。画在**地上**（从斜上方看的扁椭圆），中心在格子底部中间。**左右对称**，6 帧。",
     IM + ", " + FG + ", " + PT + ", " + DS,
     "A FIRE BOMB ON THE GROUND, 6 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the "
     "cell: 1 a white-hot flash 10 squares wide; 2 a burst of teal-green and orange fire 24 squares wide, a few flame "
     "tongues shooting up 14 squares; 3 the fire at 34 squares wide, a ring of purple-magenta PAINT splats on the "
     "ground (mirrored); 4 the flames lower and flickering; 5 small flames and smoke; 6 a scorched patch with paint "
     "specks fading. " + MAGIC + ".",
     row(6, 40, 24) + CENTER),
    ("r_land", "野火突袭：落地大爆炸，8 帧", "view_effects `tft_scar_r_land`（大表，留在他脚下的地上，z -1；左右对称）", "84 × 34",
     "大招冲到头、跳下滑板落地：地面炸开**一圈很大的青绿色和橙色冲击波**，环上溅着紫红色的涂鸦颜料，碎石和尘土往四周飞，几簇青绿色的"
     "火苗留在地上，最后慢慢暗下去。这是画在**地上**的（从斜上方看的扁椭圆），中心在格子底部中间（他的脚下）。**左右对称**，8 帧。",
     IM + ", " + FG + ", " + PT + ", " + DS,
     "A BIG GROUND BLAST, 8 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the cell "
     "(his feet): 1 a white-hot flash 16 squares wide; 2 a thick teal-green shock ring 34 squares wide and 12 tall with "
     "a hot orange inner edge; 3 the ring 54 wide and 18 tall, purple-magenta PAINT splats thrown along it, chunks of "
     "stone and dust flung up to both sides (mirrored); 4 the ring 76 wide and 26 tall, thinner; 5 the ring at the edge "
     "breaking into bright segments, small teal flames left on the ground; 6 the dust settling, the flames flickering; "
     "7 the flames dimming; 8 faint paint specks and thin dust. " + MAGIC + ".",
     row(8, 84, 34) + CENTER),
    ("r_hit", "野火突袭：被炸到 / 击飞，4 帧", "view_effects `tft_scar_r_hit`（跟随被炸的人，z 2；左右对称）", "18 × 20",
     "被燃烧弹和落地爆炸炸到的人：脚下「砰」地一下青绿色和橙色的闪光，尘土往上喷，两边几点紫红色颜料。**左右对称**，4 帧。",
     IM + ", " + FG + ", " + PT + ", " + DS,
     "A UNIT CAUGHT IN A BLAST, 4 frames, " + LR + ": 1 a teal-green and orange flash at the bottom middle 10 squares "
     "wide; 2 a jet of dust and teal sparks shooting upward 14 squares high, paint specks to both sides (mirrored); 3 "
     "the dust spreading and thinning; 4 the last puffs. " + MAGIC + ".",
     row(4, 18, 20) + CENTER),
    ("r_guard", "野火突袭：落地后的减伤护体，6 帧循环", "view_buffs `tft_scar_r_guard`（跟随他，z 3；左右对称）", "40 × 44",
     "落地后几秒大幅减伤：他身体两侧各一道**半透明感的青绿色护罩弧**（像一层野火的光幕，只画轮廓的几格亮边），脚下一圈淡淡的青绿色光圈，"
     "几点青绿色光点往上飘。身体位置留空。**左右对称**，6 帧循环。",
     FG + ", " + GD,
     "A GUARD, 6 looping frames, " + LR + ", " + HIM + ": at both sides of him (mirrored) a tall curved teal-green "
     "shield ARC 4 squares wide and 34 tall (only a bright rim and a few lit squares, the inside empty), a faint "
     "teal ring " + GROUND_E + " 30 squares wide and 7 tall at the bottom, a few teal motes drifting up; frames 1-6 a "
     "glint running up the arcs, the motes rising. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 40, 44) + CENTER),
]
ICONS = [
    ("skill", "技能 1「水坑狙击惊喜」图标", "skill_icons[0] `asset/tft/icons/tft_scar_skill`",
     "三颗冒着引线火星的圆炸弹飞出去，中间一颗炸开青绿色和橙色的火球，溅出紫红色颜料。",
     ICON + ": three round dark metal BOMBS with teal-green bands and sparking fuses flying out in a fan from the lower "
     "left, the middle one bursting in a teal-green and orange blast with purple-magenta paint splats. Colours: " + SL +
     ", " + FG + ", " + IM + ", " + PT + "."),
    ("skill2", "技能 2「长矛横扫」图标", "skill_icons[1] `asset/tft/icons/tft_scar_skill2`",
     "一杆长矛横着扫过画面，矛头后面拖着一道白热的光弧和金色碎屑。",
     ICON + ": " + SPEAR + " swung across the tile from the left to the right, a white-hot curved slash ARC trailing "
     "behind its blade, gold chips flying. Colours: " + GD + ", " + PT + ", " + IM + "."),
    ("ult", "大招「野火突袭」图标", "skill_icons[2] `asset/tft/icons/tft_scar_ult`",
     "一块野火帮的悬浮滑板从左下往右上冲，底下喷着青绿色的推进火，后面一路掉下炸开的燃烧弹。",
     ICON + ": " + BOARD + " rushing from the lower left to the upper right with teal-green thruster flames, a line of "
     "small fire bombs bursting behind it in teal-green and orange. Colours: " + SL + ", " + FG + ", " + IM + ", " +
     PT + "."),
]
BIG_FX = ["r_land"]

GROUPS = [
    ("a_hit p_hit e_hit (impacts)", ["caitlyn_skin22_star", "caitlyn_skin22_animemuzzle", "rengar_skin40_q_tar_01_flash",
                                     "skin21_animeshapes01"]),
    ("q_bomb q_hit (his bombs)", ["tft13_flyguy_base_ball", "tft13_flyguy_base_shard", "ziggs_base_r_white",
                                  "tft_ksante_hit2ball32_02"]),
    ("q_hit r_bomb r_land (paint, fire)", ["rengar_skin40_streetdemonexploration_graffitisprites_v01",
                                          "rengar_skin40_r_ground03", "lux_skin38_e_trail_flame",
                                          "rengar_skin40_fire_trail_up_03"]),
    ("r_land r_hit (ground, dust)", ["tft_ground_rock_shards", "tft_vi_smoke_2x2_128",
                                     "tft5_dmg_skin36_ground_cracknoise_mult"]),
    ("p_heal r_guard q_stun (Firelight glow)", ["petchibiekko_skin2_emote_firelight", "tft9_soraka_healstreaks",
                                                "tft_firefly_mote", "tft11_ahri_base_w_ringflare"]),
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
    """Scar at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"刀疤 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 刀疤：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/scar_design.png`："
      "野火帮的哨兵，瘦高的紫皮肤祖安人，白骷髅面具、蓝紫尖发、两只红尖耳，双手横握一杆紫金色的长矛、矛尖朝前）。"
      f"刀疤在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/scar_size.png`：刀疤缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里刀疤自己的特效贴图（**灰色的形状，游戏里再染色**：星形打击、炸弹、涂鸦颜料、火、尘土、光点），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **刀疤是祖安的野火帮，特效都是他的土炸弹、长矛和滑板**：野火帮的**青绿色**光（他金铲铲炸弹上就是这个颜色）、白热和橙色的爆炸、"
      "**紫红色的涂鸦颜料**（他矛头的颜色，野火帮到处喷涂鸦）、矛尖的金色闪光、祖安的尘土和碎石；不要魔法符文，不要光滑的霓虹光束，不要闪电。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、电光、冲击波、尘土没有黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。唯一的飞行道具是炸弹 `q_bomb`，飞的时候整张图跟着方向转，"
      "所以画成**圆的**。悬浮滑板和横扫的动作画在他自己的动作帧里，这里不画。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `scar_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格左右对称——Claude 直接用这一份切格导入）" + ("；图标交付 `scar_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「野火冲刺 + 监察」 | 每 6 秒下一次普攻变成踩滑板冲到目标身上捅一矛，回复上次冲刺以来受到伤害的一部分；血量越高减伤越多 | `p_hit` · `p_heal` |")
    a("| 普攻 | 长矛往前一刺 | `a_hit` |")
    a("| 技能 1 =「水坑狙击惊喜」 | 向最近的 3 名敌人各扔一颗炸弹：魔法伤害 + 晕眩，自己回血 | `q_bomb` · `q_hit` · `q_stun` |")
    a("| 技能 2 =「长矛横扫」 | 长矛往前方横扫，把敌人打退 | `e_hit` |")
    a("| 大招 =「野火突袭」 | 踩滑板冲向敌人，一路丢下燃烧弹；落地大爆炸击飞周围的敌人，之后几秒大幅减伤 | `r_bomb` · `r_land` · `r_hit` · `r_guard` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("野火青绿（炸弹、滑板、回血、护体）", FIRE), ("白热和橙色（爆炸）", IMPACT),
                        ("紫红涂鸦颜料（矛头的颜色）", PAINT), ("金色（矛头花纹、图标角）", GOLD), ("深色金属（炸弹壳）", STEEL),
                        ("尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `scar_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, zh, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `scar_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `scar_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `scar_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_scar_fx`（小的）和 `tft_scar_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称；q_bomb 断言转 180 度也一样（圆的）。")
    a("- p_heal 由 tft.dll 在冲刺打中时播；q_hit / q_stun 由 tft.dll 在炸弹打中时播 / 挂上（--plain 的数据自己播）。")
    a("- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="scar_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "scar_packs"), help="folder for the zip")
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
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_scar.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "scar_design.png"))
    shape = size_sheet(os.path.join(out, "design", "scar_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"scar_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "round" if x[0] == "q_bomb" else "left-right"} for x in FX] +
                  ([{"file": f"scar_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
