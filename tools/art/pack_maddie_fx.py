#!/usr/bin/env python3
"""Build maddie_fx_pack.zip: step 3 of Maddie's sprite - Codex draws her effects and her three skill icons
(pack_silco_fx.py's way).

    python tools/lol/fx_ref_maddie.py            # her TFT particle textures -> C:/t/md_work/fxref
    python tools/art/pack_maddie_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name maddie_fx_redo_pack]

The pack (C:/t/md_work/fx/maddie_fx_pack, zipped into --out, default dist/maddie_packs) holds PROMPTS.md (also written
to assets/source/maddie/PROMPTS_FX.md), design/maddie_design.png (the approved idle at 4x on its own squares),
design/maddie_size.png (her at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (her own TFT particle textures - grey shapes the game tints - grouped by the effect
they inform). The effects are the views the kit binds (tools/kit/build_maddie.py, the user's picks 2026-10-27: bot,
plan A 「狙神·通缉」): view_projectiles a_bullet, q_bullet, r_round; view_effects a_hit, q_hit, e_mark, r_sight, r_hit and
tft.dll's p_bounty; view_buffs e_wanted, p_bounty (tag p_bounty_loop). Plus the muzzle flashes a_flash and r_flash,
which point right and so go into her own action frames (SKILL.md "Both sides": the client never mirrors an effect
picture), and the three skill icons.
Her colours: Piltover HEXTECH BLUE (her rifle's crystal), the GOLD of her uniform, the white-yellow of a MUZZLE FLASH,
a WANTED red, gun smoke grey.
Red side: every hit, buff and mark is symmetric left to right; the flying ones point right and are symmetric top to
bottom (the game turns them); the muzzle flashes are not symmetric (baked into her frames, mirrored with them).
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

TMP = "C:/t/md_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "maddie", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "maddie", "hd")
NAME = "maddie_fx_pack"
PPU = 1.5

HEX = "#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A"              # Piltover hextech blue (her rifle's crystal)
GOLD = "#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08"             # her uniform's gold
FLASH = "#FFFFF4, #FFF2A0, #FFC444, #E8762A, #8A3812"            # a muzzle flash
WANT = "#FFE0D8, #FF7A60, #E0302C, #9A1420, #4A0A12"             # the Wanted red
SMOKE = "#EEEEF0, #BCBCC6, #868694, #545462"                      # gun smoke
HX = f"a hextech blue ramp ({HEX})"
GD = f"a gold ramp ({GOLD})"
FL = f"a muzzle-flash ramp ({FLASH})"
WR = f"a wanted red ramp ({WANT})"
SM = f"a gun smoke grey ramp ({SMOKE})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
TB = ("pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns "
      "it to its flight)")
RIGHT = ("pointing RIGHT (it comes out of a muzzle on the left edge of the cell, its middle on the cell's middle row), "
         "NOT symmetric left to right, SYMMETRIC TOP TO BOTTOM")
MAGIC = ("everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, "
         "hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat "
         "shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls")
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted "
        "corners, a deep navy-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_bullet", "普攻：飞出去的子弹，4 帧循环", "view_projectiles `tft_maddie_a_bullet`（弹道，z 2；朝右、上下对称）", "12 × 4",
     "她的步枪打出去的**海克斯子弹**：一颗发蓝白光的小弹头，后面拖一道细细的蓝色光尾。**朝右飞，上下对称**，4 帧循环（光尾一闪一闪）。",
     HX + ", " + GD,
     "A FLYING HEXTECH BULLET, 4 looping frames, " + TB + ": a bright white-blue bullet head 3 squares long and 2 tall "
     "at the front (right), a thin hextech blue tracer tail 8 squares long behind it, tapering; frames 1-4 the tail "
     "flickering longer and shorter, one gold spark winking. " + MAGIC + ".",
     row(4, 12, 4) + CENTER),
    ("a_hit", "普攻：子弹打中，4 帧", "view_effects `tft_maddie_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "子弹打在人身上：一下蓝白的闪光，几道蓝色的火花往四周溅开，一小团灰色硝烟。**左右对称**，4 帧。",
     HX + ", " + GD + ", " + SM,
     "A BULLET IMPACT, 4 frames, " + LR + ": 1 a white-blue star flash 6 squares across; 2 short hextech blue sparks "
     "bursting out in an X and to both sides (mirrored), two gold sparks; 3 the sparks flying farther and thinning, a "
     "small grey smoke puff in the middle; 4 the smoke fading. " + MAGIC + ".",
     row(4, 14, 14) + CENTER),
    ("a_flash", "枪口火光（画进她的开枪帧），3 帧", "画进她的动作帧（a_fire、q_fire：枪口那一点）；不做单独的画面", "14 × 10",
     "她开枪那一下枪口喷出的火光：白黄色的一团，往右喷开成三叉的尖焰，带一点蓝色的海克斯电光。**朝右**，左边贴着枪口；**上下对称**。3 帧。",
     FL + ", " + HX,
     "A MUZZLE FLASH, 3 frames, " + RIGHT + ": 1 a white-yellow burst 6 squares across at the left edge with three "
     "pointed flame tongues shooting to the right (the middle one longest, 10 squares), a thin hextech blue spark "
     "inside; 2 the tongues shorter and orange, a little grey smoke; 3 a small smoke puff only. " + MAGIC + ".",
     row(3, 14, 10) + CENTER),
    ("q_bullet", "连拨击锤：连发的子弹，4 帧循环", "view_projectiles `tft_maddie_q_bullet`（弹道，z 2；朝右、上下对称）", "14 × 4",
     "连拨击锤快速连开的子弹：比普攻更**热**的一颗**金黄色**弹头，后面一道金色和蓝色交错的光尾，速度感更强。**朝右飞，上下对称**，4 帧循环。",
     GD + ", " + FL + ", " + HX,
     "A RAPID-FIRE ROUND, 4 looping frames, " + TB + ": a hot gold-white bullet head 3 squares long and 2 tall at the "
     "front (right), a gold tracer tail 10 squares long with a hextech blue core line, tapering; frames 1-4 the tail "
     "streaking and flickering. " + MAGIC + ".",
     row(4, 14, 4) + CENTER),
    ("q_hit", "连拨击锤：子弹打中，4 帧", "view_effects `tft_maddie_q_hit`（跟随被打中的人，z 2；左右对称）", "16 × 16",
     "连射的子弹打中：一下金色的闪光，铜色的弹片和金色火花往两边溅开，一点硝烟。比普攻的打中更狠一点。**左右对称**，4 帧。",
     GD + ", " + FL + ", " + SM,
     "A HEAVY BULLET IMPACT, 4 frames, " + LR + ": 1 a gold-white flash 8 squares across; 2 gold and brass sparks and "
     "tiny shrapnel bursting out to both sides (mirrored), a short orange ring 12 across; 3 the sparks farther, a grey "
     "smoke puff in the middle; 4 the smoke fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("e_mark", "通缉令：打上通缉标记，6 帧", "view_effects `tft_maddie_e_mark`（跟随被通缉的人，z 4；左右对称）", "22 × 48",
     "被通缉的人头顶上方「啪」地砸下来一枚**皮城执法官的金色徽章**（盾形，中间一颗蓝宝石），落下时撞出一圈红色的光环，"
     "然后变成一个红金色的**准星标记**悬在头顶。身体位置留空，标记在格子最上面 14 格里。**左右对称**，6 帧。",
     GD + ", " + WR + ", " + HX,
     "A WANTED MARK SLAMMING DOWN, 6 frames, " + LR + ", " + TARGET + ": everything over the unit's head, in the top 14 "
     "squares of the cell: 1 a gold Piltover ENFORCER BADGE (a shield shape 8 squares wide and 9 tall with a blue gem "
     "in its middle) appearing high up; 2 it drops down; 3 it lands just above the head with a red ring of light 16 "
     "squares wide and 4 tall bursting out flat from it; 4 the badge flashes white, red sparks to both sides "
     "(mirrored); 5 it shrinks into a red-and-gold CROSSHAIR RETICLE (a circle 7 squares across with four ticks); 6 "
     "the reticle settling. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 22, 48) + CENTER),
    ("e_wanted", "通缉令：通缉中（受伤加深），6 帧循环", "view_buffs `tft_maddie_e_wanted`（跟随被通缉的人，z 4；左右对称）", "16 × 46",
     "通缉中的人：头顶一个**红金色的准星**慢慢转、一明一暗，脚下一圈淡淡的红色光圈。身体位置留空。**左右对称**，6 帧循环。",
     WR + ", " + GD,
     "A WANTED TARGET, 6 looping frames, " + LR + ", " + TARGET + ": over the head (the top 10 squares of the cell) a "
     "red-and-gold CROSSHAIR RETICLE 7 squares across (a circle with four short ticks, a gold dot in the middle), and "
     "a faint red ring " + GROUND_E + " 14 squares wide and 4 tall at the bottom; frames 1-6 the reticle pulsing "
     "brighter and dimmer, its ticks flicking in and out in turn (mirrored), the ring breathing. The middle (the body) "
     "left empty. " + MAGIC + ".",
     row(6, 16, 46) + CENTER),
    ("p_bounty", "赏金：通缉的人死了，她领赏，6 帧", "view_effects `tft_maddie_p_bounty`（跟随她，z 4；左右对称）", "24 × 46",
     "被通缉的敌人死了、麦迪领到一份赏金：她身边「叮」地蹦出几枚**金币**往上飞，一圈蓝色的海克斯光从脚下往上扫（攻速提高）。"
     "身体位置留空。**左右对称**，6 帧。",
     GD + ", " + HX,
     "A BOUNTY COLLECTED, 6 frames, " + LR + ", " + TARGET + ": 1 a gold flash at her chest; 2 four small GOLD COINS "
     "(2x2 squares, a bright glint) popping out to both sides of the body (mirrored); 3 the coins arcing up past her "
     "shoulders, a hextech blue ring " + GROUND_E + " 18 squares wide rising from her feet; 4 the blue ring at her "
     "waist, the coins at the top spinning; 5 the ring at her head thinning, the coins twinkling; 6 the last sparkles. "
     "The middle (the body) left empty. " + MAGIC + ".",
     row(6, 24, 46) + CENTER),
    ("p_bounty_loop", "赏金：领过赏金（攻速加成），6 帧循环", "view_buffs `tft_maddie_p_bounty`（tag p_bounty_loop，跟随她，z 3；左右对称）",
     "22 × 10",
     "领过赏金的麦迪：脚下一圈淡淡的**金色光圈**，几颗小金星一闪一闪（不要太显眼，她会一直带着）。只画脚下这一截。**左右对称**，6 帧循环。",
     GD,
     "A BOUNTY GLOW, 6 looping frames, " + LR + ": a faint thin gold ring " + GROUND_E + " 20 squares wide and 6 tall "
     "round the unit's feet, three tiny gold star glints on it at mirrored places; frames 1-6 the glints winking in "
     "turn and a soft brighter arc running round the ring. Subtle: thin lines, few squares. The upper part of the cell "
     "empty. " + MAGIC + ".",
     row(6, 22, 10) + CENTER),
    ("r_sight", "执法狙杀：瞄准（准星锁定），8 帧", "view_effects `tft_maddie_r_sight`（大表，跟随大招的目标，z 4；左右对称）", "36 × 48",
     "麦迪瞄准的那一秒：目标身上出现一个**很大的红色狙击准星**（一个圆、十字线、四个刻度），从大慢慢缩小、锁定在目标身上，"
     "最后两帧一闪一闪。准星的中心在格子中间往下一点（人的胸口）。准星是细线，**可以盖在人身上**。**左右对称**，8 帧。",
     WR + ", " + GD,
     "A SNIPER'S LOCK-ON, 8 frames, " + LR + ": a big red SNIPER SCOPE RETICLE centred on the middle of the cell, 4 "
     "squares below the centre (the unit's chest): a thin circle, a thin cross of lines with a gap in the middle, four "
     "short gold ticks on the circle; 1 the circle 34 squares across, faint; 2-5 it shrinks steadily (28, 22, 16, 12 "
     "across) and grows brighter, the cross lines shortening with it; 6 locked at 10 across, a small gold diamond in "
     "the centre; 7 a bright white-red flash of the whole reticle; 8 it dims a step. Thin 1-square lines only, so the "
     "unit under it stays readable. " + MAGIC + ".",
     row(8, 36, 48) + CENTER),
    ("r_flash", "执法狙杀：大口径枪口火光（画进她的狙击帧），5 帧", "画进她的动作帧（r_fire：枪口那一点）；不做单独的画面", "30 × 20",
     "狙击那一枪的**巨大枪口火光**：白黄色的一大团，往右喷出长长的尖焰，外面一圈蓝色的海克斯冲击波环，后面拖一大团硝烟。"
     "**朝右**，左边贴着枪口；**上下对称**。5 帧。",
     FL + ", " + HX + ", " + SM,
     "A HEAVY MUZZLE BLAST, 5 frames, " + RIGHT + ": 1 a big white-yellow burst 10 squares across at the left edge, a "
     "long pointed flame tongue shooting 26 squares to the right with two shorter ones at angles; 2 a hextech blue "
     "shockwave ring (an upright ellipse 6 wide and 16 tall) pushed out to the right of the burst, the flame orange; 3 "
     "the ring farther right and thinner, grey smoke billowing at the muzzle; 4 smoke 12 across drifting; 5 thin "
     "smoke. " + MAGIC + ".",
     row(5, 30, 20) + CENTER),
    ("r_round", "执法狙杀：飞出去的狙击弹，4 帧循环", "view_projectiles `tft_maddie_r_round`（大表，弹道，z 2；朝右、上下对称）", "34 × 8",
     "狙击打出去的**穿甲海克斯弹**：一颗大的蓝白色尖头弹，后面一道很长、很亮的蓝色能量尾迹，尾迹两边有一圈圈的螺旋。"
     "**朝右飞，上下对称**，4 帧循环。",
     HX + ", " + GD,
     "A PIERCING HEXTECH ROUND, 4 looping frames, " + TB + ": a big pointed white-blue round 6 squares long and 4 tall "
     "at the front (right) with a gold ring at its base, a long bright hextech blue energy trail 26 squares long "
     "behind it with small spiral rings around it, tapering to the left; frames 1-4 the spiral rings sliding back "
     "along the trail. " + MAGIC + ".",
     row(4, 34, 8) + CENTER),
    ("r_hit", "执法狙杀：狙击命中，7 帧", "view_effects `tft_maddie_r_hit`（大表，跟随被打中的人，z 3；左右对称）", "40 × 40",
     "狙击弹打中（它会穿过去继续飞）：一下巨大的蓝白闪光，一道**横向的冲击线**往两边炸开，蓝色和金色的碎光四溅，一圈冲击环，留下一点硝烟。"
     "**左右对称**，7 帧。",
     HX + ", " + GD + ", " + SM,
     "A SNIPER ROUND PUNCHING THROUGH, 7 frames, " + LR + ": 1 a big white-blue star flash 14 squares across in the "
     "middle; 2 a thin bright horizontal shock line 36 squares long through the middle, hextech blue and gold sparks "
     "bursting out to both sides (mirrored); 3 a hextech blue shock ring 30 wide and 12 tall around the middle, sparks "
     "farther; 4 the ring bigger and thinner, the shock line breaking up; 5-6 grey smoke puffs in the middle, the last "
     "sparks; 7 thin smoke. " + MAGIC + ".",
     row(7, 40, 40) + CENTER),
]
ICONS = [
    ("skill", "技能 1「连拨击锤」图标", "skill_icons[0] `asset/tft/icons/tft_maddie_skill`",
     "一只握枪的手快速扳动击锤，枪口喷出一串扇形排开的六颗金色子弹。",
     ICON + ": a gloved hand fanning the hammer of a dark navy-and-gold hextech gun, the muzzle at the upper right "
     "spitting SIX gold bullets in a fan, each with a short tracer, a white-yellow flash at the muzzle. Colours: " +
     HX + ", " + GD + ", " + FL + "."),
    ("skill2", "技能 2「通缉令」图标", "skill_icons[1] `asset/tft/icons/tft_maddie_skill2`",
     "一枚金色的皮城执法官徽章（中间蓝宝石），外面套着一个红色的准星。",
     ICON + ": a gold Piltover ENFORCER BADGE (a shield shape with a glowing blue gem in its middle) inside a red "
     "CROSSHAIR RETICLE (a circle with four ticks), a few red sparks. Colours: " + GD + ", " + WR + ", " + HX + "."),
    ("ult", "大招「执法狙杀」图标", "skill_icons[2] `asset/tft/icons/tft_maddie_ult`",
     "瞄准镜里的视野：一个红色的十字准星，中间一颗拖着蓝色长尾迹的狙击弹正冲出来。",
     ICON + ": the round view of a SNIPER SCOPE with a thin red cross and gold ticks, a big hextech blue ROUND with a "
     "long glowing trail bursting out of its centre toward the viewer, a white flash. Colours: " + WR + ", " + HX +
     ", " + GD + "."),
]
BIG_FX = ["r_sight", "r_round", "r_hit"]
FLYING = ["a_bullet", "q_bullet", "r_round"]
ASYM = ["a_flash", "r_flash"]     # baked into her frames (they point right, top-bottom symmetric)

GROUPS = [
    ("a_bullet q_bullet r_round (bullets)", ["shooter_ba_bullet", "tft13_shooter_base_ba_bullet_1",
                                             "shooter_ba_mis_trail", "shooter_ba_mis_trail_2", "jhin_base_ba_mis_mult"]),
    ("a_flash r_flash (muzzle)", ["tft13_shooter_muzzle_2", "corki_base_ba_muzzle_flash", "spikey_flash",
                                  "sion_skin05_speedlines"]),
    ("a_hit q_hit r_hit (hits)", ["bolts_hiteffect_physical_s_01", "kled_skin18_r_hit_flash_01",
                                  "sion_skin06_r_cas_meshtex_sonicwaves", "star"]),
    ("r_round e_mark p_bounty (glow)", ["tft13_shooter_base_r_missile_tx_cm", "shooter_base_wisplayertrail",
                                        "sion_skin05_r_flares_01", "tft6_trait_scrap_glow_bright"]),
    ("smoke", ["shooter_base_fog", "drmundo_base_trail", "caitlyn_skin11_z_small_mote"]),
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
    """Maddie at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"麦迪 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def symmetry(name):
    return "top-bottom" if name in FLYING or name in ASYM else "left-right"


def document(shape, icons=True):
    h, w = shape[:2]
    L = []
    a = L.append
    n_ic = len(ICONS) if icons else 0
    a("# 麦迪：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/maddie_design.png`："
      "把海克斯步枪扛在肩上的皮城女执法官，橙红短发、歪戴贝雷帽，金边宝蓝制服，步枪上一颗蓝水晶）。"
      f"麦迪在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/maddie_size.png`：麦迪缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里麦迪自己的特效贴图（**灰色的形状，游戏里再染色**：子弹、弹道尾迹、枪口火光、打中的闪光、硝烟），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **麦迪是皮尔特沃夫的执法官神枪手，特效都是她的枪火**：步枪蓝水晶的**海克斯蓝**能量、白黄色的枪口火光、铜金色的火花、"
      "一点灰色硝烟，「通缉令」是红金色的执法官徽章和准星；不要光滑的霓虹光束，不要魔法符文，不要火球。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、火、烟没有黑描边**（徽章、金币这些实物可以有一圈深色描边）。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人（`r_sight` 的准星是细线，可以压在人身上）。")
    a("> - **对称**：打中、标记、身上和脚下的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道 `a_bullet`、`q_bullet`、"
      "`r_round` 朝右画、尾巴在左边，严格上下对称**（游戏按方向转这张图）。**枪口火光 `a_flash`、`r_flash` 朝右画、上下对称**"
      "（我把它们画进她自己的开枪帧里，跟着她一起翻转）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `maddie_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、按上面的要求逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `maddie_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「狙神」 | 离她越远的目标受到的伤害越高；被通缉的敌人死了她领一份赏金（攻速提高，最多 4 份） | `p_bounty` · `p_bounty_loop` |")
    a("| 普攻 | 步枪开一枪，后坐力把枪口顶起来 | `a_flash` · `a_bullet` · `a_hit` |")
    a("| 技能 1 =「连拨击锤」 | 半蹲朝最远的敌人连开 6 枪，每枪打中路上第一个敌人 | `a_flash` · `q_bullet` · `q_hit` |")
    a("| 技能 2 =「通缉令」 | 给附近血最多的敌方英雄打上通缉标记，所有人打它都更痛 | `e_mark` · `e_wanted` |")
    a("| 大招 =「执法狙杀」 | 瞄准 1 秒，一发穿透狙击弹射向血量比例最低的敌方英雄，路上的人都挨打 | `r_sight` · `r_flash` · `r_round` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、烟没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("海克斯蓝", HEX), ("金色（制服、火花、图标边框）", GOLD), ("枪口火光", FLASH), ("通缉红", WANT),
                        ("硝烟灰", SMOKE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `maddie_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `maddie_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `maddie_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `maddie_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_maddie_fx`（小的）和 `tft_maddie_big`（{'、'.join(BIG_FX)}），tag = 名字；"
      "p_bounty_loop 是 view_buffs 里 p_bounty 的 tag；a_flash / r_flash 不进表，画进 a_fire、q_fire、r_fire 那几帧的枪口。")
    a(f"- 弹道（{'、'.join(FLYING)}）和枪口火光（{'、'.join(ASYM)}）断言上下对称；其余断言左右对称。")
    a("- r_sight 在大招瞄准的 r_rel 拍里放完（8 帧拉到那么长）；q_hit / r_hit / p_bounty 由 tft.dll 在打中、领赏时播。")
    a("- 用 `pixel_1x/` 切格（import_silco_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="maddie_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "maddie_packs"), help="folder for the zip")
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
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_maddie.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "maddie_design.png"))
    shape = size_sheet(os.path.join(out, "design", "maddie_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"maddie_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": symmetry(x[0])}
                   for x in FX] +
                  ([{"file": f"maddie_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
