#!/usr/bin/env python3
"""Build kalista_fx_pack.zip: step 3 of Kalista's sprite - Codex draws her effects (pack_elise_fx.py's way).

    python tools/art/pack_kalista_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name kalista_fx_redo_pack]

The pack (%TEMP%/kl_work/fx/kalista_fx_pack, zipped into --out, default dist/kalista_packs) holds PROMPTS.md (also
written to assets/source/kalista/PROMPTS_FX.md), design/kalista_idle.png (her dense design at 3x),
design/kalista_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/kalista_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Kalista grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/kl_work/fxref, read out of Kalista.wad.client's base-skin particle paths by work/kl/fx_ref_kl.py).
The effects are the views the kit binds (tools/kit/build_kalista.py: view_projectiles a_spear, q_spear; view_effects
a_hit, q_hit, w_hit, sp_mark, e_rip, e_cast, e_reset, r_take, r_fly, r_land, r_up; view_buffs e_slow, r_safe).
League's colours (refs/lol_fx_ref.png): her spears black with a spectral sea-green glow, the hits green-white, Rend's
rip green shards, Fate's Call a deeper soul blue; light gets no outline.
Red side: the flying pictures (a_spear, q_spear) symmetric top to bottom (they turn with the flight), every picture on
a unit, on her, on the ground and every buff symmetric left to right.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "kl_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "kalista", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_kalista")
HD = os.path.join(ROOT, "assets", "source", "kalista", "hd")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GHOST = "#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443"     # her spectral light, League's sea green: white core to deep teal
SPEAR = "#E8F4F8, #8A8FA0, #4C4F60, #26262F, #121217"             # the spear's black blade and shaft (with sea-green streaks)
SOUL = "#FFFFFF, #CFE9FF, #7EB8FF, #3C7BE0, #1D3E8A"              # Fate's Call: the bound soul's blue
EARTH = "#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39"             # dust kicked up by the landing
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
GH = f"a spectral sea-green ramp ({GHOST})"
SP = f"a black spear ramp ({SPEAR})"
SO = f"a soul blue ramp ({SOUL})"
ER = f"an earth-dust ramp ({EARTH})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack, Pierce
    ("a_spear", "普攻：投出去的幽灵矛（朝目标飞，循环），2 帧", "view_projectiles `league_kalista_a_spear`（朝飞行方向转，画成朝右飞；上下对称）",
     "16 × 5", "普攻投出去的矛：一支细长的黑色矛（矛头尖、在右边），矛身有青绿色的发光条纹，后面拖一小段青绿偏白的幽灵光尾（参考 BA_Spear_CA、BA_Spear_Glow、BA_trail）。**上下对称**。",
     f"{SP} and {GH}",
     f"a GHOST SPEAR flying to the RIGHT, 2 frames, a seamless loop, {TB}: a slim black spear 12 squares long and 1 square thick "
     "with a pointed leaf blade 3 squares long and 3 tall at its RIGHT end, 2 sea-green glowing streaks along the shaft; a green-white "
     "ghost trail 4 squares long behind it, flickering between the two frames.",
     row(2, 18, 6) + "; the blade's tip 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_spear", "Q 穿刺：投出去的长矛（朝目标飞，循环），4 帧", "view_projectiles `league_kalista_q_spear`（朝飞行方向转，画成朝右飞；上下对称）",
     "24 × 8", "穿刺：一支更长更亮的黑矛，矛头整个包在青绿偏白的幽灵光里，后面拖一条长长的青绿色光尾和几缕幽灵烟（参考 Q_Mis_Glow、Q_Mis_Trail、Q_GhostTrail、Q_Mist）。**上下对称**。",
     f"{SP} and {GH}",
     f"a PIERCING SPEAR flying to the RIGHT, 4 frames, a seamless loop, {TB}: a black spear 14 squares long, its leaf blade 4 "
     "squares long wrapped in a bright green-white glow 6 squares across; a tapering sea-green trail 10 squares long behind it with "
     "ghostly wisps above and below it at mirrored places, drifting between frames.",
     row(4, 26, 10) + "; the glow's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_kalista_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "矛打中：一小团青绿偏白的闪光，几道短短的青绿色光线往外射（参考 BA_flash、BA_Hit_Poof、Cross_Stars）。**左右对称**。约 10 格。", GH,
     f"a SMALL SPECTRAL HIT on a unit, 4 frames, {LR}: 1 a white dot 2 squares; 2 a green-white flash 7 squares with a white "
     "core; 3 the flash 10 squares, 6 short sea-green rays at mirrored places; 4 a few fading sea-green motes.",
     row(4, 12, 12) + CENTER),
    ("q_hit", "Q 穿刺打中（目标身上），5 帧", "view_effects `league_kalista_q_hit`（跟随，画在人物上面；左右对称）", "18",
     "穿刺命中：一圈青绿色的冲击波炸开（白芯），几道青绿色的光痕往外射，几块碎光飞出（参考 Q_Tar_Shockwave_1/2、Q_Tar_Streaks_4x1、Q_Tar_Bits_4x4）。**左右对称**。约 18 格。",
     GH,
     f"a PIERCING IMPACT on a unit, 5 frames, {LR}: 1 a white flash 5 squares; 2 a sea-green burst 10 squares across with a white "
     "core; 3 a sea-green shockwave ring 16 squares across, 8 sea-green streaks shooting out at mirrored places; 4 the ring 18 squares "
     "and fading, small sea-green bits flying out; 5 fading motes.",
     row(5, 20, 20) + CENTER),
    ("w_hit", "W 哨兵（灵魂绑定）：额外伤害（目标身上），4 帧", "view_effects `league_kalista_w_hit`（跟随，画在人物上面；左右对称）", "14",
     "灵魂绑定触发：目标身上浮出一个青绿色的幽灵手印 / 灵魂标记，一闪后化成光点（参考 W_Radial_1、P_Hit_Splat）。**左右对称**。约 14 格。",
     GH,
     f"a SOUL MARK flaring on a unit, 4 frames, {LR}: 1 a sea-green glow 4 squares; 2 a sea-green rune 12 squares wide - a ring with four "
     "short spikes pointing in, mirrored - with a white core; 3 the rune brightest, 14 squares; 4 the rune breaking into sea-green "
     "motes.",
     row(4, 16, 16) + CENTER),
    # ---- spears and Rend
    ("sp_mark", "插在敌人身上的矛（目标身上，循环），2 帧", "view_effects `league_kalista_sp_mark`（跟随，画在人物上面；左右对称）", "6 × 14",
     "插在敌人身上的矛（撕裂的层数）：一支短短的黑矛竖着从上往下插进目标的身体，矛尾露在外面，矛身上一圈青绿色的幽灵光微微闪（参考 P_blade3_full、P_Hit_Tips、BackSpear_rgba）。"
     "**左右对称**：矛竖直、在格子正中。",
     f"{SP} and {GH}",
     f"a SPEAR STUCK in a unit, 2 frames, a seamless loop, {LR}: a short black spear standing straight UP in the middle column, "
     "its blunt end at the top, 12 squares long and 2 squares thick, its lower 3 squares hidden (stuck in the body: the cell's "
     "bottom 3 rows empty); a faint sea-green glow 4 squares wide round its middle that pulses between the frames.",
     row(2, 8, 16) + "; the spear in the middle column of every cell."),
    ("e_rip", "E 撕裂：拔出一支矛（目标身上），5 帧", "view_effects `league_kalista_e_rip`（跟随，画在人物上面；左右对称）", "16",
     "撕裂：插着的矛被猛地往上拔出，拔出的地方一团青绿色的光爆开，几块青绿色的碎片往外飞（参考 P_PullOut、DarkImpact_01、ImpactSparks_4x4）。**左右对称**。约 16 格。",
     f"{GH} and {SP}",
     f"a SPEAR RIPPED OUT of a unit, 5 frames, {LR}: 1 a short black spear standing up in the middle, a sea-green glow at its foot; "
     "2 the spear jerked UP 6 squares, a green-white burst 8 squares where it was; 3 the spear gone above the cell's top, the "
     "burst 14 squares with 6 sea-green shards flying out at mirrored places; 4 the burst 16 squares and fading, the shards further "
     "out; 5 a few fading motes.",
     row(5, 18, 22) + "; the burst's middle 6 squares above the cell's bottom row, centered across."),
    ("e_cast", "E 撕裂：发动（她身上，不跟随），5 帧", "view_effects `league_kalista_e_cast`（不跟随，画在她身上；左右对称；大图表）", "36 × 28",
     "撕裂发动：她握拳往回一扯，身边一圈青绿色的幽灵光往里一收（像一圈线被扯紧），然后散成光点。**左右对称**，中间她的身体位置留空（只画外圈）。",
     GH,
     f"a PULL-IN RING round a figure, 5 frames, {LR}, the middle EMPTY (a clear area 18 squares wide and 26 tall where she is, not "
     "drawn): 1 a thin sea-green ellipse 36 wide and 10 tall round her waist; 2 eight sea-green threads from the ring's edge pointing in "
     "toward her, mirrored; 3 the ring and threads snapping inward to 24 wide, brightest; 4 the threads breaking into sea-green "
     "motes; 5 the last motes.",
     row(5, 38, 30) + "; centered across, the figure's feet on the cell's bottom row."),
    ("e_reset", "E 撕裂击杀刷新（她头顶，不跟随），4 帧", "view_effects `league_kalista_e_reset`（不跟随，她头顶；左右对称）", "12",
     "撕裂击杀返还冷却：她头顶一闪青绿色的十字星光（参考 Cross_Stars、Q_LensFlare）。**左右对称**。约 12 格。", GH,
     f"a STAR FLARE over a head, 4 frames, {LR}: 1 a white dot 2 squares; 2 a four-pointed sea-green star 10 squares with a white "
     "core; 3 the star 12 squares, a ring 8 squares round it; 4 fading.",
     row(4, 14, 14) + CENTER),
    # ---- Fate's Call
    ("r_take", "大招 命运的召唤：把队友拉进来（队友身上），6 帧", "view_effects `league_kalista_r_take`（跟随队友，画在人物上面；左右对称；大图表）", "18 × 28",
     "命运的召唤：被召唤的队友身上缠上几道蓝色的灵魂锁链 / 光带，从脚下往上缠住，全身泛起一层蓝光（参考 R_Charged_Glow、R_Charged_Sphere、P_Link_Swirls、R_Start_Waves）。"
     "**左右对称**，光带可以横着盖过身体，但不要画成实心的一团。",
     f"{SO} and {GH}",
     f"SOUL BONDS wrapping a figure, 6 frames, {LR} (an upright figure 10 squares wide and 22 tall stands in the middle, not "
     "drawn): 1 blue soul light rising from the ground at both sides; 2 two blue bands spiralling up round the legs, crossing "
     "in front; 3 the bands up to the shoulders, a soft blue glow outline round the figure 16 wide and 26 tall; 4 the bands and "
     "glow brightest with a white core line; 5 the bands drawing in tight; 6 a blue shimmer left round the figure.",
     row(6, 18, 30) + "; centered across, the figure's feet on the cell's bottom row."),
    ("r_fly", "大招：被甩出去的队友（队友身上，跟随），4 帧", "view_effects `league_kalista_r_fly`（跟随队友，画在人物上面；左右对称；大图表）", "20 × 28",
     "被甩出去：飞行中的队友全身包着一层蓝色的灵魂光，身后拖着上下两条光带（参考 R_Trail、R_Knockup_Trail、R_mis_tube）。**左右对称**（光往上下两边散，不画方向）。",
     f"{SO} and {GH}",
     f"a SOUL AURA round a flying figure, 4 frames, {LR} (a figure 10 squares wide and 22 tall in the middle, not drawn): a blue "
     "glow outline 18 wide and 26 tall round it, white-blue light flickering on it, streaks of blue light peeling off its top "
     "and bottom at mirrored places, changing between frames.",
     row(4, 20, 30) + "; centered across, the figure's feet on the cell's bottom row."),
    ("r_land", "大招：落地冲击（地上，不跟随），6 帧", "view_effects `league_kalista_r_land`（不跟随，地上；左右对称；大图表）", "40 × 18",
     "落地：地面炸开一圈蓝色的灵魂冲击波（扁椭圆），中间一团白蓝色的光往上冲，尘土往两边溅（参考 R_Shockwave、R_Shockwave_Ring、R_Hit_Shockwave、R_Ground_rgba、R_Push_Out_Smoke）。**左右对称**。",
     f"{SO} and {ER}",
     f"a SOUL SHOCKWAVE on the ground, 6 frames, {LR}: 1 a white flash 6 squares on the ground; 2 a blue burst 12 squares wide "
     "rising 10 squares, a flat ground ring 20 wide and 6 tall; 3 the ring 32 wide, dust kicked out at both sides; 4 the ring "
     "40 wide and fading, the burst breaking into blue motes, dust settling; 5 the last ring arcs and motes; 6 a faint glow.",
     row(6, 42, 20) + "; centered across, the ground ring's middle 4 squares above the cell's bottom row."),
    ("r_up", "大招：被击飞的敌人（目标身上），5 帧", "view_effects `league_kalista_r_up`（跟随，画在人物上面；左右对称）", "14 × 26",
     "被击飞：敌人身边几道蓝色的光痕往上冲（参考 R_Knockup_Trail、R_Flare）。**左右对称**，中间身体位置留空。",
     SO,
     f"UPWARD SOUL STREAKS round a figure, 5 frames, {LR}, the middle EMPTY (a figure 10 squares wide and 22 tall, not drawn): "
     "1 blue light at both sides of the feet; 2 four blue streaks shooting up at both sides, mirrored, 12 squares tall with white "
     "cores; 3 the streaks 24 squares tall; 4 the streaks thinning; 5 a few blue motes.",
     row(5, 16, 28) + "; centered across, the figure's feet on the cell's bottom row."),
    # ---- buffs
    ("e_slow", "E 撕裂减速（敌人脚下，循环），4 帧", "view_buffs `league_kalista_e_slow`（跟随，画在人物下面；左右对称）", "16 × 5",
     "被撕裂减速：敌人脚下一圈淡淡的青绿色幽灵环，几点青绿光轮流闪。**左右对称**。", GH,
     f"a FAINT CYAN RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin flat ellipse 14 squares wide and 4 tall "
     "in sea-green, 4 brighter motes on it at mirrored places taking turns to light up.",
     row(4, 16, 6) + CENTER),
    ("r_safe", "大招：被保护的队友（队友身上，循环），4 帧", "view_buffs `league_kalista_r_safe`（跟随队友，画在人物上面；左右对称；大图表）", "16 × 26",
     "在她体内被保护：队友身上一层半透明感的蓝色灵魂光晕（用稀疏的蓝色光点和外圈光边表现，不要实心），慢慢呼吸。**左右对称**。",
     SO,
     f"a SOUL SHROUD round a figure, 4 frames, a seamless loop, {LR} (a figure 10 squares wide and 22 tall in the middle, not "
     "drawn): a blue glow outline 14 wide and 24 tall, sparse blue light dots inside it, the outline brightening and dimming "
     "through the loop.",
     row(4, 16, 28) + "; centered across, the figure's feet on the cell's bottom row."),
]

GROUPS = [
    ("a_spear a_hit", ["Kalista_Base_BA_Spear_CA", "Kalista_Base_BA_Spear_Glow", "Kalista_Base_BA_trail",
                       "Kalista_Base_BA_flash", "Kalista_Base_BA_Hit_Poof", "Kalista_Base_Cross_Stars"]),
    ("q_*", ["Kalista_Base_Q_Mis_Glow", "Kalista_Base_Q_Mis_Trail", "Kalista_Base_Q_GhostTrail",
             "Kalista_Base_Q_Tar_Shockwave_1", "Kalista_Base_Q_Tar_Streaks_4x1", "Kalista_Base_Q_Tar_Bits_4x4"]),
    ("sp_mark e_* w_hit", ["Kalista_Base_P_blade3_full", "Kalista_Base_P_Hit_Tips", "Kalista_Base_P_PullOut",
                           "Kalista_Base_DarkImpact_01", "Kalista_Base_ImpactSparks_4x4", "Kalista_Base_W_Radial_1"]),
    ("r_take r_safe r_fly", ["Kalista_Base_R_Charged_Glow", "Kalista_Base_R_Charged_Sphere", "Kalista_Base_P_Link_Swirls",
                             "Kalista_Base_R_Start_Waves", "Kalista_Base_R_Trail", "Kalista_Base_R_mis_tube"]),
    ("r_land r_up", ["Kalista_Base_R_Shockwave", "Kalista_Base_R_Shockwave_Ring", "Kalista_Base_R_Hit_Shockwave",
                     "Kalista_Base_R_Ground_rgba", "Kalista_Base_R_Knockup_Trail", "Kalista_Base_R_Flare"]),
]
# the action frames the pictures start from: (tag, frame, what) - the sea-green cross is her standing point
SHOTS = [("attack", 3, "a_spear：普攻出手"), ("skill", 3, "q_spear：穿刺出手"), ("skill2", 2, "e_cast：撕裂（握拳回扯）"),
         ("ult", 3, "r_take：召唤（举手）"), ("ult2", 3, "r_fly：甩出队友")]


def ref_sheet(path):
    S, LW = 180, 140
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                continue
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Kalista_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def sheet_frames(tag):
    anims = json.load(open(lp(SHEET + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sh = Image.open(lp(SHEET + "#sheet.png")).convert("RGBA")
    out = []
    for fr in anims[tag]["frames"]:
        r = fr["data"]
        out.append(np.asarray(sh.crop((int(r["x"]), int(r["y"]), int(r["x"] + r["w"]), int(r["y"] + r["h"])))))
    return out


def first_1x(tag):
    f = sheet_frames(tag)[0]
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    import tfm2_ase as T
    figs = [first_1x("idle")]
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    figs.append(k[ky.min():ky.max() + 1, kx.min():kx.max() + 1])
    Z, pad = 4, 6
    W = pad + sum(f.shape[1] + pad for f in figs)
    top = max(f.shape[0] for f in figs)
    img = Image.new("RGBA", (W * Z, (pad + top + 4) * Z + 64), (104, 112, 72, 255))
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
    d.text((8, 36), f"卡莉丝塔 {figs[0].shape[1]}×{figs[0].shape[0]} 格（连长矛），原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def shots_sheet(path):
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(sheet_frames(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px = f.shape[1] // 2
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(ys.max()) + 1)
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(ys.max()) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 300), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((pt[0] - x0) * Z), int((pt[1] - y0) * Z) + 24
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    sheet = Image.new("RGB", (sum(t.width + 10 for t in tiles), max(t.height for t in tiles)), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 复仇之矛 卡莉丝塔：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/kalista_idle.png`：3/4 正面朝右的低蹲，近侧手低握长矛、矛头指向身后，"
      f"背上两支备用矛）。她在游戏里是**高清**的（每个游戏格子里 1.4×1.4 个细像素），连长矛 {h} 格高、{w} 格宽；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/kalista_size.png`：她的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/kalista_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡莉丝塔自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**矛是黑色的、带青绿色的幽灵光纹**，**打中和撕裂是青绿偏白的幽灵光（白芯）**，**大招「命运的召唤」是偏深的灵魂蓝**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光圈、光带只画外圈和两边，中间身体位置留空**（`r_take` 的光带可以横着盖过身体，但要有空隙）。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `a_spear`、`q_spear` 画成朝右，**上下对称**（往左飞时会上下翻）。"
      "其余所有画面（打中、身上、脚下、头顶、地上的冲击）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）——插在身上的矛竖直、拔矛竖直往上，不要画成斜的。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `kalista_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `kalista_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「武术姿态」+ W「哨兵」 | 投矛，矛插在目标身上；被贴身时投矛后往后跳；队友在目标身边时额外伤害 | `a_spear` · `a_hit` · `sp_mark` · `w_hit` |")
    a("| 技能 1 = Q「穿刺」 | 投出长矛，击杀则穿过去打下一个 | `q_spear` · `q_hit` |")
    a("| 技能 2 = E「撕裂」 | 拔出所有矛：每支矛一次伤害和减速；击杀英雄刷新 | `e_rip` · `e_cast` · `e_reset` · `e_slow` |")
    a("| 大招「命运的召唤」 | 把身边队友拉进身体保护，再甩向目标，落地击飞周围敌人 | `r_take` · `r_safe` · `r_fly` · `r_land` · `r_up` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、火星、碎片、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（矛例外：黑色的矛身可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("幽灵青绿（打中、撕裂、她的光）", GHOST), ("黑矛（矛身、矛头）", SPEAR), ("灵魂蓝（大招）", SOUL),
                        ("尘土（大招落地）", EARTH)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 52500，"
      "Q 射程 100000，大招落地击飞半径 26000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `kalista_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `kalista_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_kalista_fx`（小的）和 `league_kalista_big`（e_cast、r_take、r_fly、r_land、r_safe），tag = 名字（build_kalista.py 的 views）。")
    a("- `a_spear`、`q_spear` 是飞行投射物，画面朝飞行方向转；`e_cast`、`e_reset`、`r_land` 不跟随；`e_slow` 脚下 buff（z -1）；`sp_mark` 每 12 tick 播一次（循环 2 帧）。")
    a("- 用 `pixel_1x/` 切格（import_nidalee 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="kalista_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "kalista_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/kl/fx_ref_kl.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    des = np.asarray(Image.open(lp(os.path.join(HD, "A.png"))).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(des, 3, 0), 3, 1)).save(os.path.join(out, "design", "kalista_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "kalista_size.png"))
    shots_sheet(os.path.join(out, "design", "kalista_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"kalista_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
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
