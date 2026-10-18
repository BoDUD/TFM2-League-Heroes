#!/usr/bin/env python3
"""Build akshan_fx_pack.zip: step 3 of Akshan's sprite - Codex draws his effects (pack_wukong_fx.py's way).

    python work/aks/fx_ref_ak.py             # League's particle textures -> C:/t/ak_work/fxref (Riot's art, local only)
    python tools/art/pack_akshan_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name akshan_fx_redo_pack]

The pack (C:/t/ak_work/fx/akshan_fx_pack, zipped into --out, default dist/akshan_packs) holds PROMPTS.md (also written
to assets/source/akshan/PROMPTS_FX.md), design/akshan_idle.png (his idle at 4x, the design's squares at PPU 1.5),
design/akshan_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/akshan_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Akshan grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_akshan.py): view_projectiles a_shot (a_shot2, e_shot), q_rang
(q_out, q_back), r_bullet; view_effects a_hit (e_hit), p_hit, q_hit, q_catch, r_hit, e_hook, w_camo, r_lock; view_buffs
p_sh, w_ms and w_mark (the add-on's Scoundrel mark). League's colours: the shots gold, the Sentinel light (Dirty Fighting,
the shield, the camouflage) pale sky blue, Comeuppance and the mark red-gold, the boomerang and the hook bronze.
Red side: the client never mirrors an effect picture, so every picture that is not a projectile is symmetric left to
right; projectiles are drawn pointing right (the game turns them to their flight).
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
TMP = "C:/t/ak_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "akshan", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_akshan")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "akshan_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GOLD = "#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12"      # the shots, the hits, the relic gun's light
SKY = "#FFFFFF, #E8FBFF, #B8ECF4, #7FD3E2, #3FA9BF, #1F6E86"       # the Sentinel light: Dirty Fighting, the camouflage
RED = "#FFFFFF, #FFD0C0, #FF7A5A, #E8341C, #A8160E, #600A08"       # Comeuppance, the Scoundrel mark
BRONZE = "#FFF6E0, #F2C77A, #C98A3A, #8E5524, #5A3216, #2E180C"    # the boomerang, the hook and its rope
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
SOLID = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
         "solid objects with a 1-square near-black outline and flat 3-4 step shading, light on them without an outline, "
         "colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
GO = f"a gold light ramp ({GOLD})"
SK = f"a pale sky-blue Sentinel light ramp ({SKY})"
RE = f"a red ramp ({RED})"
BR = f"a bronze ramp ({BRONZE})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
HIM = "the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn"
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"
FLY = ("pointing RIGHT (the game turns it to its flight), centered vertically, its nose at the right of the cell")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout, solid?
FX = [
    # ---- flying
    ("a_shot", "普攻 / E 的子弹（飞行，跟着方向转），3 帧", "view_projectiles `league_akshan_a_shot`、`a_shot2`、`e_shot`", "10 × 4",
     "遗迹手枪打出的子弹：一颗金白色的小光弹，后面拖一道短短的橙金色光尾（参考 Missile、Trail07、Glow01）。**朝右画**（游戏会按飞行方向转）。约 10 × 4 格。",
     GO,
     f"a SMALL GLOWING BULLET in flight, 3 frames, a loop, {FLY}: a white-gold bolt 3x2 squares at the front, a short "
     "orange-gold tail 6 squares behind it thinning out; the tail flickers a little frame to frame.",
     row(3, 10, 4) + "; the bolt's nose 1 square from the cell's right edge.", False),
    ("q_rang", "Q 去而复还：转着飞的回旋镖（飞行），4 帧", "view_projectiles `league_akshan_q_out`、`q_back`（去和回同一张）", "12",
     "从枪上甩出去的回旋镖：一把青铜色的弯刃（像他枪口那两道弯钩，V 字形，刃口一圈金白色的亮边），一帧一帧转（每帧转 90 度），身后一圈淡金色的残影弧"
     "（参考 Boomerang、Boomerang02、Swirl02）。约 12 格见方。",
     f"{BR} and {GO}",
     f"a SPINNING BOOMERANG BLADE in flight, 4 frames, a seamless loop: a bronze V-shaped curved blade 10 squares across (a "
     "1-square dark outline, a lit gold-white cutting edge, a dark bronze inner edge), turned a quarter turn more each "
     "frame (0, 90, 180, 270 degrees), a faint gold motion arc (no outline) following its tips.",
     row(4, 12, 12) + CENTER, True),
    ("r_bullet", "R 恩怨相抵：大子弹（飞行），3 帧", "view_projectiles `league_akshan_r_bullet`", "16 × 6",
     "大招打出的子弹：比普攻大的金红色光弹，中心白色，后面一道长长的红金色光尾，尾巴两边几颗火星（参考 Beam05B、Trail01、P_LensFlare）。**朝右画**。约 16 × 6 格。",
     f"{GO} and {RE}",
     f"a HEAVY GLOWING ROUND in flight, 3 frames, a loop, {FLY}: a white-hot core 4x3 squares wrapped in gold at the front, "
     "a red-gold tail 11 squares behind it tapering to a point, 2 sparks beside the tail; the tail flickers frame to frame.",
     row(3, 16, 6) + "; the core's nose 1 square from the cell's right edge.", False),
    # ---- hits
    ("a_hit", "普攻 / E 命中（目标身上），4 帧", "view_effects `league_akshan_a_hit`、`e_hit`（跟随，画在人物上面；左右对称）", "10",
     "子弹打中：一个小小的金白色星形闪光，几颗火星往外蹦（参考 BA_LensFlare、Glow02、Impact01）。**左右对称**。约 10 格。",
     GO,
     f"a SMALL BULLET IMPACT on a unit, 4 frames, {LR}: 1 a white dot 3 squares; 2 a gold-white 4-point star 8 squares; "
     "3 the star thinner, 4 gold sparks at mirrored places; 4 fading sparks.",
     row(4, 10, 10) + CENTER, False),
    ("p_hit", "被动无所不用：第 3 下爆发（目标身上），5 帧", "view_effects `league_akshan_p_hit`（跟随，画在人物上面；左右对称）", "18",
     "同一目标打中 3 下时的额外伤害：一圈淡蓝白色的哨兵之光猛地炸开（一个菱形 + 一个圆环叠在一起，像他那一族哨兵的纹章），中间一道金白色闪光"
     "（参考 SacGeo01、ShieldGeometry03、Glow01B、Shockwave）。**左右对称**。约 18 格。",
     f"{SK} and {GO}",
     f"a SENTINEL BURST on a unit, 5 frames, {LR}: 1 a white-gold flash 6 squares; 2 a pale sky-blue diamond outline 12 "
     "squares (1 square thick) round a ring 9 squares, a white core; 3 the diamond and the ring 16 squares, light rays at "
     "the diamond's 4 points; 4 the shapes thinner and 18 squares, breaking into sparks; 5 fading sparks.",
     row(5, 18, 18) + CENTER, False),
    ("q_hit", "Q 回旋镖划过（目标身上），4 帧", "view_effects `league_akshan_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "回旋镖划过目标：两道交叉的青铜金色弧形刀光（X 字，左右对称），中间白色，几颗火星（参考 Swirl02、Impact01）。**左右对称**。约 14 格。",
     f"{GO} and {BR}",
     f"a BOOMERANG SLASH on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 two gold crescent slashes crossing in an "
     "X (mirrored, 12 squares across, white edges, no outline); 3 the slashes thinner and wider, bronze sparks at mirrored "
     "places; 4 fading.",
     row(4, 14, 14) + CENTER, False),
    ("r_hit", "R 子弹命中（目标身上），4 帧", "view_effects `league_akshan_r_hit`（跟随，画在人物上面；左右对称）", "18",
     "大招子弹打中：一团金红色的爆闪，中心白色，一圈红色的冲击环往外扩，几颗火星（参考 Shockwave、P_LensFlare、Glow02）。**左右对称**。约 18 格。",
     f"{GO} and {RE}",
     f"a HEAVY ROUND IMPACT on a unit, 4 frames, {LR}: 1 a white flash 6 squares; 2 a red-gold burst 12 squares with a "
     "white core, a thin red shock ring round it; 3 the ring 18 squares (1 square thick), gold sparks at mirrored places; "
     "4 the ring fading, a few sparks.",
     row(4, 18, 18) + CENTER, False),
    # ---- on him
    ("q_catch", "Q 接住回旋镖（他手上，跟随），3 帧", "view_effects `league_akshan_q_catch`（跟随，画在人物上面；左右对称）", "12",
     f"回旋镖飞回到他手里的一下：胸前一道金白色的小闪光，一圈淡金色的小环（参考 Glow02、BA_LensFlare）。**左右对称**，画在他胸口高度（{HIM}，闪光在他脚底以上 24 格的位置）。",
     GO,
     f"a CATCH GLINT, 3 frames, {LR} ({HIM}): 1 a white-gold 4-point star 6 squares, its middle 24 squares above the "
     "cell's bottom row; 2 a thin gold ring 10 squares round it; 3 fading.",
     row(3, 12, 30) + "; centered across.", False),
    ("e_hook", "E 骄行荡寇：甩出的钩索（他身上，不跟随），5 帧", "view_effects `league_akshan_e_hook`（不跟随，画在人物上面 z 2；左右对称；大图表）", "24 × 70",
     f"他朝天上甩出钩索：一根青铜色的绳子从他头顶笔直地射上去，顶上是一个金色的三叉抓钩，抓住时一闪；之后绳子绷直、轻轻抖动（参考 Rope、RopeB、"
     f"Arrows）。**左右对称**（绳子在正中竖直），绳子下端在他头顶（{HIM}，绳子从他头顶 2 格往上画到格子顶）。",
     f"{BR} and {GO}",
     f"A GRAPPLING HOOK SHOT STRAIGHT UP, 5 frames, {LR} ({HIM}): a bronze rope 2 squares thick (a twisted pattern, a "
     "1-square dark outline) going straight up the middle from 2 squares above his head (42 squares above the cell's "
     "bottom row) to a gold three-pronged hook (8 squares across, outlined) at its top; 1 the rope half way up with the "
     "hook flying; 2 the rope at the top, the hook there; 3 a gold-white flash 10 squares round the hook as it bites; "
     "4 the rope taut; 5 like 4, the rope shaking a square side to side (kept symmetric by shaking only its texture).",
     row(5, 24, 70) + "; centered across, the rope's bottom 42 squares above the cell's bottom row.", True),
    ("w_camo", "W 赴险夺人：伪装（他身上，不跟随），5 帧", "view_effects `league_akshan_w_camo`（不跟随，画在人物上面 z 2；左右对称；大图表）", "40 × 48",
     f"他被围住时伪装起来：身上泛起一层淡蓝白色的哨兵之光，几片像羽毛一样的光片从身上飘起、向两边散开，最后淡去（参考 W_feather、W_SmokeShape01、"
     f"W_cloudRing_edge、W_glow_distort）。**左右对称**，围着身体画，中间身体位置的光要淡（{HIM}）。",
     SK,
     f"A CAMOUFLAGE SHIMMER round a figure, 5 frames, {LR} ({HIM}): 1 a thin pale sky-blue outline glow hugging the "
     "figure's edge (1 square wide, no dark outline); 2 a faint shimmer ring at its feet (an ellipse 30 wide and 6 tall) "
     "and 6 small feather-like light flakes (2x4 squares) rising at both sides at mirrored places; 3 the flakes higher and "
     "spreading out; 4 the flakes fading, the glow thinner; 5 a few faint flakes.",
     row(5, 40, 48) + "; centered across, the figure's feet 4 squares above the cell's bottom row.", False),
    ("r_lock", "R 恩怨相抵：锁定（他身上，不跟随），5 帧", "view_effects `league_akshan_r_lock`（不跟随，画在人物上面 z 2；左右对称；大图表）", "44 × 44",
     f"他开大锁定目标的那一下：身边亮起一个金红色的瞄准纹章（一个大菱形套一个圆环，四个角上有小三角，像准星），由小变大、一闪后淡去（参考 SacGeo01、"
     f"ShieldGeometry03、Counter、P_LensFlare）。**左右对称**，围着他的上半身画，中间身体位置留空（{HIM}）。",
     f"{GO} and {RE}",
     f"A TARGET-LOCK SIGIL round a figure, 5 frames, {LR} ({HIM}): a red-gold reticle centred on his chest (24 squares "
     "above the cell's bottom row): a diamond outline round a ring, small triangles at the diamond's 4 points (lines 1 "
     "square thick, white cores, no dark outline), the middle 16 squares left empty; 1 the sigil 14 squares; 2 30 squares; "
     "3 40 squares, brightest; 4 the same, thinner; 5 fading.",
     row(5, 44, 44) + "; centered across.", False),
    # ---- buffs
    ("p_sh", "被动护盾（他身上，跟随，循环），4 帧", "view_buffs `league_akshan_p_sh`（跟随，画在人物上面；左右对称；循环）", "40 × 46",
     f"打中英雄后得到的护盾：一个淡蓝白色的半透明光罩（只画一圈边，边上有菱形的哨兵花纹），一闪一闪（参考 P_shield、ShieldGeometry03b、P_SheildMult）。"
     f"**左右对称**，中间身体位置留空（{HIM}，光罩把他整个人罩住）。",
     SK,
     f"A SHIELD BUBBLE round a figure, 4 frames, a seamless loop, {LR} ({HIM}): an oval outline 34 squares wide and 42 "
     "tall round the figure (1-2 squares thick, white highlights at the top, no dark outline), 4 small diamond marks on it "
     "at mirrored places; the inside left EMPTY; 1 dim, 2 brighter, 3 brightest, 4 like 2.",
     row(4, 40, 46) + "; centered across, the figure's feet 2 squares above the cell's bottom row.", False),
    ("w_ms", "W 伪装加速（他脚下，跟随，循环），4 帧", "view_buffs `league_akshan_w_ms`（跟随，画在人物下面 z -1；左右对称；循环）", "36 × 10",
     f"伪装加速时脚下的风：一圈淡蓝色的风线贴着地面往后吹（两边对称的几道短风线），一帧一帧流动（参考 P_Speed_Pierce、Trail02、Trail03）。"
     f"**左右对称**，只画在脚下（{HIM}）。",
     SK,
     f"SPEED STREAKS at a figure's feet, 4 frames, a seamless loop, {LR} ({HIM}): a faint pale sky-blue ellipse 30 wide "
     "and 6 tall on the ground, 3 short wind streaks on each side (mirrored, 4-6 squares long, 1 square thick, no outline) "
     "flowing outward a square each frame.",
     row(4, 36, 10) + "; centered across, the ellipse's middle 3 squares above the cell's bottom row.", False),
    ("w_mark", "恶徒标记（敌人头顶，循环），4 帧", "view_buffs `league_akshan_w_mark`（跟随，画在人物上面；左右对称；循环；扩展包加在恶徒身上）", "14 × 48",
     f"杀了阿克尚队友的敌人被标记成恶徒：头顶上方浮着一个红色的骷髅准星标记（一个小骷髅头套在菱形准星里），一闪一闪（参考 Counter、SacGeo02、"
     f"Shuriman01）。**左右对称**，只画在头顶上方（{CHAMP}，标记在他头顶上面 2 格）。",
     f"{RE} and {GO}",
     f"A SCOUNDREL MARK floating over a unit's head, 4 frames, a seamless loop, {LR} ({CHAMP}): a small red diamond reticle "
     "10 squares wide and 10 tall (a white-red rim) with a little pale skull 5x5 squares inside (a 1-square dark outline on "
     "the skull), its bottom 2 squares above the champion's head (38 squares above the cell's bottom row); 1 dim, 2 "
     "brighter, 3 brightest (the rim flashing white), 4 like 2; nothing below it.",
     row(4, 14, 48) + "; centered across, the mark's bottom 38 squares above the cell's bottom row.", True),
]
BIG_FX = ["e_hook", "w_camo", "r_lock"]
REDO = {}
GROUPS = [
    ("a_shot a_hit", ["Missile", "Trail07", "Glow01", "BA_LensFlare", "Glow02", "Impact01"]),
    ("q_rang q_hit q_catch", ["Boomerang", "Boomerang02", "Swirl02", "Swirl05", "Frontal01"]),
    ("p_hit p_sh", ["SacGeo01", "ShieldGeometry03", "ShieldGeometry03b", "P_shield", "Shockwave", "Glow01B"]),
    ("e_hook", ["Rope", "RopeB", "Arrows", "DirectionalGuide2"]),
    ("w_camo w_ms", ["W_feather", "W_SmokeShape01", "W_cloudRing_edge", "W_glow_distort", "P_Speed_Pierce", "Trail02"]),
    ("r_lock r_bullet r_hit", ["SacGeo02", "Counter", "Beam05B", "Trail01", "P_LensFlare", "UltimateRelic"]),
    ("w_mark", ["Shuriman01", "SacGeo05", "SacGeo03"]),
]
FEET = 11.5
SHOTS = [("attack", 2, "a_shot 子弹出膛（朝右飞），a_hit 打在目标身上"), ("skill", 2, "q_rang 回旋镖扔出去再飞回，q_hit / q_catch"),
         ("skill2", 2, "e_hook 钩索从他头顶往上射"), ("e_swing", 1, "荡在空中开枪（子弹 a_shot）"),
         ("ult", 2, "r_lock 锁定纹章围着他"), ("ult_shot", 1, "r_bullet 大子弹、r_hit"),
         ("idle", 1, "p_sh 护盾罩住他；w_camo / w_ms 伪装和脚下的风"), ("hit", 2, "（受击，不需要特效）")]


def ref_sheet(path):
    S, LW = 170, 200
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                p = os.path.join(REF, "Akshan_Base_" + nm + ".png")
            if not os.path.isfile(p):
                cand = [f for f in os.listdir(REF) if f.startswith(nm)]
                if not cand:
                    sys.exit(f"missing reference {p}")
                p = os.path.join(REF, sorted(cand)[0])
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm[:26],
                   fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"阿克尚 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
        pt = (px, int(f.shape[0] / 2 + FEET))           # the frame's centre is his pivot, FEET rows over the ground
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(max(ys.max(), pt[1])) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 440), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((pt[0] - x0) * Z), int((pt[1] - y0) * Z) + 24
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    cols = 4
    rows_ = (len(tiles) + cols - 1) // cols
    cw = max(t.width for t in tiles) + 10
    ch = max(t.height for t in tiles) + 10
    sheet = Image.new("RGB", (cols * cw, rows_ * ch), (60, 64, 50))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), ((i % cols) * cw, (i // cols) * ch))
    sheet.save(path)


def design_sheet(path):
    """His idle at 4x, the design's own squares (PPU 1.5: 1.5 squares a game pixel)."""
    import rig_akshan as M
    F = M.form()
    c = F.rig.finish(F.pose())
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 影哨 阿克尚：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/akshan_idle.png`：3/4 正面朝右的游侠枪手，深棕长卷发和小发髻、"
      f"短胡子、浅蓝白围巾、橙红饰带、暗红长披风、青绿布片，近侧手把一把暗红青铜的回旋镖手枪举在头边）。他在游戏里是**高清**的"
      f"（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/akshan_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/akshan_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里阿克尚自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**子弹和命中是金色的光**，**哨兵之光（被动爆发、护盾、伪装）是淡天蓝色**，"
      "**大招和恶徒标记是红金色**，**回旋镖和钩索是青铜色**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **飞行物（子弹、回旋镖、大子弹）朝右画**：游戏会按飞行方向转。**其他所有图严格左右对称**（逐格对称）：这些画面在红色方不会镜像。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 14]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `akshan_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/akshan_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。"
      "中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「无所不用」 | 每次普攻开两枪；对同一目标第 3 下多一段伤害，打英雄还给自己护盾 | `a_shot` · `a_hit` · `p_hit` · `p_sh` |")
    a("| 技能 1 = Q「去而复还」 | 扔出回旋镖，去和回各打一次，接回手里 | `q_rang` · `q_hit` · `q_catch` |")
    a("| 技能 2 = E「骄行荡寇」 | 朝天甩出钩索，荡过去一路开枪，最后翻滚落地 | `e_hook` · `a_shot` · `a_hit` |")
    a("| W「赴险夺人」 | 被围住时伪装加速；（扩展包）杀了队友的敌人头顶出现恶徒标记 | `w_camo` · `w_ms` · `w_mark` |")
    a("| 大招「恩怨相抵」 | 锁定受伤的英雄蓄力，然后连射大子弹 | `r_lock` · `r_bullet` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、风、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：回旋镖、钩索和绳子、恶徒标记里的小骷髅可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色的光（子弹、命中）", GOLD), ("淡天蓝的哨兵之光（被动、护盾、伪装）", SKY), ("红色（大招、恶徒标记）", RED),
                        ("青铜色（回旋镖、钩索）", BRONZE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头（光的特效一段，有实心东西的另一段）。大小写在每条里（1 个游戏像素约等于 1000 距离单位：普攻射程 55000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout, solid) in enumerate(FX, 1):
        a(f"### {k}. `akshan_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a((SOLID if solid else LEAD).format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `akshan_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_akshan_fx`（小的）和 `league_akshan_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_akshan.py 的 views：`a_shot2` / `e_shot` 用 `a_shot`，`q_out` / `q_back` 用 `q_rang`，`e_hit` 用 `a_hit`；`w_mark` 由扩展包加在恶徒身上）。")
    a("- 用 `pixel_1x/` 切格（import_wukong_fx 的做法），断言非飞行物左右对称；清掉 Codex 给光描的最深色边（回旋镖、钩索、骷髅保留描边）；"
      "核对交回的张数和这份清单；和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="akshan_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "akshan_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/aks/fx_ref_ak.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "akshan_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "akshan_size.png"))
    shots_sheet(os.path.join(out, "design", "akshan_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"akshan_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
