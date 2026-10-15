#!/usr/bin/env python3
"""Build tahmkench_fx_pack.zip: step 3 of Tahm Kench's sprite - Codex draws his effects (pack_elise_fx.py's way).

    python tools/art/pack_tahmkench_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name tahmkench_fx_redo_pack]

The pack (%TEMP%/tk_work/fx/tahmkench_fx_pack, zipped into --out, default dist/tahmkench_packs) holds PROMPTS.md (also
written to assets/source/tahmkench/PROMPTS_FX.md), design/tahmkench_idle.png (his design at 3x),
design/tahmkench_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base
fighter), design/tahmkench_shots.png (the finished action frames the pictures start from, 4x), design/code_fx.png (the
stand-ins drawn by tools/art/fx_tahmkench.py: the sizes and places, not the look) and refs/lol_fx_ref.png (League's own
particle textures for Tahm Kench grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/tk_work/fxref, written by work/tk/fx_ref_tk.py from TahmKench.wad.client's base-skin particle paths).
The effects are the views the kit binds (tools/kit/build_tahmkench.py: view_projectiles q_tongue; view_effects a_hit,
q_hit, q_stun, q_heal, e_shield, w_down, w_warn, w_up, w_hit, r_gulp, r_in, r_spit; view_buffs t_pip1-3, q_slow,
r_full, r_bubble).
League's colours: river water in teals with white foam (Q's splashes, the dive, the bubbles, the swallow), the tongue
and its drool pink, the passive's marks little teal fish, the W marker a red ring with fish shapes, Thick Skin's
shield blue-violet wisps; light gets no outline.
Red side: the flying tongue symmetric top to bottom (it turns with the flight), every picture on a unit, on him, on
the ground and every buff symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "tk_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "tahmkench", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_tahmkench")
HD = os.path.join(ROOT, "assets", "source", "tahmkench", "hd")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


WATER = "#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52"     # river water and foam
PINK = "#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C"              # the tongue, drool, the passive's taste
GOLD = "#FFFFFF, #FFF2A8, #FFD23F, #E39A1E, #9E5A12"              # stun stars
GREEN = "#F2FFE0, #B6F57A, #5ED45A, #2A9A44"                      # heal
SHIELD = "#FFFFFF, #E2E8FF, #A9B6F2, #7B7FD6, #4E4AA0"            # Thick Skin: blue-violet wisps
RED = "#FFE0DA, #FF6A5A, #D62A2A, #8E1414"                        # the W marker's ring (enemies)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
WA = f"a river-water ramp ({WATER})"
PK = f"a tongue-pink ramp ({PINK})"
GO = f"a gold ramp ({GOLD})"
GR = f"a heal-green ramp ({GREEN})"
SH = f"a blue-violet shield ramp ({SHIELD})"
RD = f"a red marker ramp ({RED})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
ROUND = ("the middle EMPTY where he stands (his body is about 50 squares wide and 40 tall, not drawn: only the outer "
         "edge and the sides)")


def pip(k):
    where = {1: "at the LEFT of the cell's top row band", 2: "in the MIDDLE", 3: "at the RIGHT"}[k]
    return (f"t_pip{k}", f"被动 培养品味：第 {k} 层的标记（英雄头顶，循环），2 帧",
            f"view_buffs `league_tahmkench_t_pip{k}`（头顶，第 {k} 个位置；三张叠在一起就是 3 层；左右对称）", "5 × 5",
            f"被动叠层标记：一条小小的青绿色鱼头标记（参考 P_Marker_Update 的鱼），朝上、正面，**左右对称**，画在格子{'左边' if k == 1 else '中间' if k == 2 else '右边'}，"
            "三张图位置不同、可以叠在一起显示 1–3 层。",
            f"{WA} and {PK}",
            f"a TASTE MARK over a champion's head, 2 frames, a seamless loop, {LR}: a tiny teal FISH HEAD seen from the front, "
            "5 squares wide and 5 tall, mouth up, a white glint, a pink tongue-tip dot; the second frame lifted 1 square "
            f"(a bob); drawn {where} of the cell (three cells side by side make the 1-3 stack row).",
            row(2, 21, 7) + "; the mark's middle on the cell's middle row; slot 1 at column 4, slot 2 at column 10, slot 3 at column 16.")


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("q_tongue", "Q 巨舌鞭笞：甩出去的舌头（朝目标飞，循环），2 帧",
     "view_projectiles `league_tahmkench_q_tongue`（朝飞行方向转，画成朝右；上下对称）", "28 × 6",
     "Q 的长舌头：一条湿漉漉的粉红色长舌头从左往右伸出去（舌尖在最右边，圆的），上面一道亮光，后段带一点口水滴（参考 Q_WaterTrail、TongueSaliva）。**上下对称**。",
     f"{PK} and {WA}",
     f"a LASHING TONGUE flying to the RIGHT, 2 frames, a seamless loop, {TB}: a long wet pink tongue 26 squares long, 3 squares "
     "thick at its rounded tip on the right, thinning to 2 at the left end, a white wet highlight along its middle; 2 small "
     "teal-white drool drops trailing at mirrored places; a gentle wave along it that alternates between the frames.",
     row(2, 30, 8) + "; the tongue tip 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），3 帧", "view_effects `league_tahmkench_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "舌头抽中：一小团粉红色的口水溅开（白芯），夹着几点青绿色的水花（参考 ImpactTest、BA_Tar）。**左右对称**。约 12 格。",
     f"{PK} and {WA}",
     f"a SLAP SPLAT on a unit, 3 frames, {LR}: 1 a white flash 3 squares; 2 a pink drool splat 9 squares across with a white "
     "core and teal water flecks; 3 the splat 12 squares, droplets flying out at mirrored places, fading.",
     row(3, 14, 14) + CENTER),
    ("q_hit", "Q 巨舌鞭笞打中（目标身上），4 帧", "view_effects `league_tahmkench_q_hit`（跟随，画在人物上面；左右对称）", "20",
     "舌鞭命中：一团青绿色的河水尖刺状溅开（参考 Q_SpikeSplashes：一根根弯弯的水刺往外甩），中间一点粉红的口水和白色水沫。**左右对称**。约 20 格。",
     f"{WA} and {PK}",
     f"a TONGUE-LASH IMPACT on a unit, 4 frames, {LR}: 1 a white-and-pink flash 6 squares; 2 curved teal water spikes "
     "bursting out to both sides, 14 squares across, white foam at their tips; 3 the spikes 20 squares across, pink drool "
     "drops between them; 4 the spikes falling apart into fading droplets.",
     row(4, 22, 22) + CENTER),
    ("q_stun", "Q 三层眩晕（头顶），4 帧", "view_effects `league_tahmkench_q_stun`（跟随，头顶，约 1.25 秒）", "18 × 7",
     "眩晕：头顶三颗金色的小星星绕着转（白芯），中间夹两滴青绿色水珠。**左右对称**，4 帧合起来转一圈。",
     f"{GO} and {WA}",
     f"STUN STARS circling over a head, 4 frames, a loop, {LR} in every frame: three gold 5-point stars 3 squares across with "
     "white cores on a flat ellipse 18 squares wide and 5 tall (the front one bigger), two teal water drops between them; "
     "each frame the stars a quarter of the way further round, kept mirrored by placing them in mirrored pairs.",
     row(4, 20, 9) + CENTER),
    ("q_heal", "Q 命中英雄时回血（他身上），4 帧", "view_effects `league_tahmkench_q_heal`（跟随，画在他上面；左右对称）", "40 × 40",
     "回血：几缕绿色的治疗光（参考 Heal_Wisps），从他身体两边往上飘，带几个小加号。**左右对称**，" + "中间身体位置留空。",
     GR,
     f"HEALING WISPS rising round a big body, 4 frames, {LR}, {ROUND}: green wisps and small plus signs 3 squares across "
     "rising up both sides and fading at the top, white cores.",
     row(4, 44, 44) + "; the body's middle on the cell's center, its feet on row 33."),
    ("e_shield", "厚实表皮：护盾（他身上），4 帧", "view_effects `league_tahmkench_e_shield`（跟随，画在他上面；左右对称）", "56 × 50",
     "厚实表皮护盾：一层蓝紫色的半透明感的气泡壳包住他（参考 E_Shield_Glow / Wisps：蓝紫色的流光），只画外圈和几道流光高光，中间身体位置留空。"
     "第 1 帧张开、第 2–3 帧罩住、第 4 帧碎掉。**左右对称**。",
     SH,
     f"a SHIELD SHELL round a big body, 4 frames, {LR}, {ROUND}: an oval shell 56 squares wide and 50 tall drawn as a 2-square "
     "rim with blue-violet wisps flowing along it and a few white glints; 1 the shell forming, 36 wide; 2 full; 3 full, the "
     "wisps moved round; 4 breaking into pieces that fade.",
     row(4, 60, 54) + "; the shell's middle on the cell's center, the body's feet on row 44."),
    ("w_down", "W 深渊潜航：潜下去的水花（他脚下），4 帧", "view_effects `league_tahmkench_w_down`（跟随，画在他身后；大图）", "44 × 32",
     "潜下去：他脚下的地面变成一圈河水，水从四周往上翻起又落下（参考 W_Splashes、Z_LinearSplashes），中间留空让他沉下去。**左右对称**。",
     WA,
     f"a DIVE SPLASH round a big body's feet, 4 frames, {LR}, the middle EMPTY above the ground where he sinks: 1 a ring of river "
     "water opening on the ground, an ellipse 30 squares wide and 8 tall; 2 water walls splashing up at both sides 18 squares "
     "high with white foam crests; 3 the splashes falling back, drops; 4 the ring closing, ripples.",
     row(4, 48, 36) + "; the ring's middle 2 squares above the cell's bottom, centered across."),
    ("w_warn", "W 深渊潜航：冒出地点的预警（地上，不跟随），6 帧", "view_effects `league_tahmkench_w_warn`（地上，不跟随，画在人物下面；大图）",
     "30 × 12",
     "他要冒出来的地方：地上一圈红色的预警环（参考 W_Decal：红色的环，上面三条小鱼的花纹），环里面是翻滚的深色河水和一串冒上来的气泡。6 帧循环约 1 秒。**左右对称**。",
     f"{RD} and {WA}",
     f"a GROUND WARNING where he will burst up, 6 frames, a seamless loop, {LR}: a red ring seen from above at an angle, an "
     "ellipse 30 squares wide and 12 tall, 1 square thick, with three small fish shapes on it at mirrored places; inside it "
     "dark churning river water with bubbles rising and popping, a different pair of bubbles each frame.",
     row(6, 32, 14) + CENTER),
    ("w_up", "W 深渊潜航：冒出来的水柱（他身上），4 帧", "view_effects `league_tahmkench_w_up`（跟随，画在他身后；大图）", "44 × 50",
     "冒出来：一根粗水柱从地里冲上来（白色水沫芯，青绿色），落地时四周溅起一圈水花（参考 W_portal、Z_Splases）。**左右对称**。",
     WA,
     f"a WATER BURST as a big body shoots out of the ground, 4 frames, {LR}: 1 a thick column of river water 16 squares wide "
     "shooting up 46 squares from the ground, a white foam core; 2 the column breaking at the top into drops, a splash ring "
     "on the ground 30 squares wide; 3 the drops falling at both sides, the ring 44 wide; 4 ripples and the last drops.",
     row(4, 48, 54) + "; the ground ring's middle 2 squares above the cell's bottom, centered across."),
    ("w_hit", "W 击飞（被击飞的单位脚下），3 帧", "view_effects `league_tahmkench_w_hit`（跟随，画在人物上面；左右对称）", "18 × 12",
     "被掀飞：单位脚下溅起一小团河水（参考 WaterSplash）。**左右对称**。",
     WA,
     f"a SMALL SPLASH under a unit thrown up, 3 frames, {LR}: water splashing up from the ground at both sides, 12 squares high "
     "with white foam tips, then falling as drops.",
     row(3, 20, 14) + "; the splash's base on the cell's bottom row, centered across."),
    ("r_gulp", "R 大快朵颐：一口吞下（他头上），4 帧", "view_effects `league_tahmkench_r_gulp`（跟随，画在他上面；左右对称）", "30 × 22",
     "一口吞下：他嘴巴的位置上一对大牙齿（参考 R_UI：上下两排米黄色的尖牙）从上下合拢「咔嚓」咬合，四周甩出粉红色的口水滴和青绿色水珠。**左右对称**。",
     f"{PK} and {WA}",
     f"a CHOMP over a big head, 4 frames, {LR}: two rows of cream-white fangs (upper and lower jaws, 22 squares wide) snapping "
     "shut; 1 the jaws wide apart 16 squares; 2 closing; 3 shut with a white flash where they meet, pink drool drops flung out "
     "to both sides; 4 the teeth gone, drops falling.",
     row(4, 32, 24) + CENTER),
    ("r_in", "R 大快朵颐：被吞的单位（目标身上），3 帧", "view_effects `league_tahmkench_r_in`（跟随，画在人物上面）", "22 × 26",
     "被吞进去：被吞的英雄身上卷起一团青绿色的河水漩涡把他裹住缩小（参考 R_Target_waterwave）。**左右对称**（漩涡用两股对称的水流）。",
     WA,
     f"a SWALLOWING WHIRL on a unit, 3 frames, {LR}: two mirrored streams of river water swirling up round an upright figure 10 "
     "squares wide and 22 tall (not drawn), closing in; 1 the streams wide 22 squares; 2 wrapping the figure; 3 shrunk to a "
     "small whirl 8 squares with a white core.",
     row(3, 24, 28) + "; centered across, the figure's feet on the cell's bottom row."),
    ("r_spit", "R 吐出来（目标身上），3 帧", "view_effects `league_tahmkench_r_spit`（跟随，画在人物上面；左右对称）", "20",
     "吐出来：一团粉红色的口水加青绿色的水哗地溅开（白芯）。**左右对称**。",
     f"{PK} and {WA}",
     f"a SPIT-OUT SPLASH on a unit, 3 frames, {LR}: 1 a white-and-pink burst 8 squares; 2 a splash of pink drool and teal water "
     "16 squares across, drops at mirrored places; 3 the drops falling and fading.",
     row(3, 22, 22) + CENTER),
    pip(1), pip(2), pip(3),
    ("q_slow", "Q 减速（目标脚下，循环），2 帧", "view_buffs `league_tahmkench_q_slow`（脚下，画在人物下面；左右对称）", "22 × 6",
     "减速：目标脚下一滩粉红色的黏口水，表面一两点亮光（参考 TongueSaliva）。**左右对称**。",
     PK,
     f"a STICKY DROOL PUDDLE at a unit's feet, 2 frames, a seamless loop, {LR}: a flat pink puddle seen from above at an angle, "
     "an ellipse 22 squares wide and 6 tall, two white glints that move between the frames, a drip at each side.",
     row(2, 24, 8) + CENTER),
    ("r_full", "R 消化中（他身上，循环），3 帧", "view_buffs `league_tahmkench_r_full`（他身上；左右对称）", "40 × 40",
     "吞着人的时候：他身体周围冒几个青绿色的小气泡往上飘。**左右对称**，中间身体位置留空。",
     WA,
     f"DIGESTION BUBBLES round a big body, 3 frames, a seamless loop, {LR}, {ROUND}: small teal bubbles 2-3 squares with white "
     "glints rising at both sides, a different height each frame.",
     row(3, 44, 44) + "; the body's middle on the cell's center, its feet on row 33."),
    ("r_bubble", "R 被吞的单位的标记（循环），2 帧", "view_buffs `league_tahmkench_r_bubble`（被吞的单位身上；左右对称）", "22 × 26",
     "被吞的单位：裹在一个青绿色的水泡里（只画水泡的外圈和高光）。**左右对称**。",
     WA,
     f"a WATER BUBBLE round a unit, 2 frames, a seamless loop, {LR}: a teal bubble rim 1 square thick round an upright figure "
     "10 squares wide and 22 tall (not drawn), 22 wide and 26 tall, two white glints moving between the frames.",
     row(2, 24, 28) + "; centered across, the figure's feet on the cell's bottom row."),
]
BIG = {"w_down", "w_warn", "w_up"}
GROUPS = [
    ("q_tongue", ["TahmKench_Base_Q_WaterTrail_01", "TahmKench_Base_Z_TongueSaliva_Mask", "TahmKench_Base_BA_Tar"]),
    ("a_hit / q_hit", ["TahmKench_Base_Q_SpikeSplashes", "TahmKench_Base_ImpactTest_2", "TahmKench_Base_ImpactTest_4",
                       "TahmKench_Base_Q_Buf_Sparkle"]),
    ("q_heal", ["TahmKench_Global_SS_Heal_Wisps_2x2", "Global_SS_Heal_glow-soft"]),
    ("e_shield", ["TahmKench_Base_E_Shield_Wisps", "TahmKench_Base_E_Shield_Glow"]),
    ("w_down / w_up / w_hit", ["Tahmkench_Base_W_Splashes", "TahmKench_Base_Z_LinearSplashes_02", "TahmKench_Base_Z_Splases",
                               "TahmKench_Base_W_portal_tex", "TahmKench_Base_WaterSplash_01_Dissolve"]),
    ("w_warn", ["TahmKench_Base_W_Decal", "TahmKench_Base_W_Decal_Ally", "TahmKench_Base_W_SpeedBuffGround"]),
    ("r_gulp / r_in / r_full", ["TahmKench_Base_R_UI", "TahmKench_Base_R_Target_waterwave", "TahmKench_Base_Dots"]),
    ("t_pip", ["TahmKench_Base_P_Marker_Update", "TahmKench_Base_P_Marker_Update_Glow"]),
]
SHOTS = [("attack", 3, "舌头抽中（a_hit）"), ("skill", 4, "嘴张大、舌根伸出（q_tongue 从嘴里飞出）"), ("skill2", 2, "跳起准备下潜（w_down）"),
         ("w_land", 1, "从地里冲出（w_up）"), ("ult", 2, "嘴张到最大（r_gulp）"), ("dead", 6, "死亡")]


def ref_sheet(path):
    S, LW = 170, 150
    sheet = Image.new("RGBA", (LW + 5 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
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
            d.text((LW + c * S + 4, y + 2), nm.replace("TahmKench_Base_", "").replace("Tahmkench_Base_", "")[:24],
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
    d.text((8, 36), f"塔姆 {figs[0].shape[1]}×{figs[0].shape[0]} 格（连帽子和尾巴），原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
        py = f.shape[0] // 2 + 11                       # the frame is centred on the pivot; the ground 11 under it
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0, x1 = int(min(xs.min(), px)) - 3, int(max(xs.max(), px)) + 4
        y0, y1 = int(ys.min()) - 3, int(max(ys.max(), py)) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 300), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((px - x0) * Z), int((py - y0) * Z) + 24
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
    th, tw = shape[:2]
    L = []
    a = L.append
    a("# 塔姆·肯奇（河流之王）：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/tahmkench_idle.png`：3/4 正面朝右的待机）。他在游戏里是**高清**的"
      f"（每个游戏格子里 1.2×1.2 个细像素），连帽子和尾巴 {th} 格高、{tw} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/tahmkench_size.png`：待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/tahmkench_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - `design/code_fx.png`：Claude 先用代码画的占位特效（6 倍），**只看大小和位置，不要照它的画法**。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里塔姆自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**河水是青绿色的（白色水沫芯）**，**舌头和口水是粉红色的**，**被动的叠层标记是青绿色的小鱼**，"
      "**W 落点的预警是一圈红色的环（上面有小鱼花纹）**，**厚实表皮的护盾是蓝紫色的流光**。")
    a("> - **特效要亮**：每团水、每道光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光圈、护盾、气泡只画外圈和两边，中间身体位置留空**（他很宽：约 50 格宽、40 格高）。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的舌头 `q_tongue` 画成朝右，**上下对称**（往左飞时会上下翻）。"
      "其余所有画面（打中、他身上、脚下、头顶、地上的水花和预警环、标记）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `tahmkench_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `tahmkench_fx_pack_done.zip`。"
      "**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「培养品味」 | 舌头抽打；打中英雄叠一层，最多 3 层（头顶的小鱼标记） | `a_hit` · `t_pip1` · `t_pip2` · `t_pip3` |")
    a("| 技能 1 = Q「巨舌鞭笞」 | 舌头甩出去打中第一个单位：伤害、减速；打中英雄回血、叠层，3 层眩晕 | `q_tongue` · `q_hit` · `q_slow` · `q_heal` · `q_stun` |")
    a("| 被动里的 E「厚实表皮」 | 被两名敌方英雄围住时获得护盾 | `e_shield` |")
    a("| 技能 2 = W「深渊潜航」 | 潜进地里，在目标处冒出来，击飞周围的敌人 | `w_down` · `w_warn` · `w_up` · `w_hit` |")
    a("| 大招 = R「大快朵颐」 | 吞下队友（保护）或叠满 3 层的敌人（伤害），再吐出来 | `r_gulp` · `r_in` · `r_spit` · `r_full` · `r_bubble` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**水、光、水沫、星星、环都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("河水（水花、水柱、气泡、漩涡）", WATER), ("舌头和口水", PINK), ("眩晕星星", GOLD), ("回血", GREEN),
                        ("厚实表皮护盾", SHIELD), ("W 预警环", RED)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位："
      "Q 射程 60000、宽 3000，W 落地击飞半径 14000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `tahmkench_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## 交回前请检查\n")
    a(f"- {len(FX)} 张都在、文件名对；每张有 8 倍图和 `pixel_1x/` 原尺寸图，透明度只有 0 和 255。")
    a("- 舌头上下对称、舌尖朝右；其余每张逐格左右对称。")
    a("- 围着他的画面中间留空；没有黑描边；每个形状有亮芯。")
    a("- 全部画完后最后写 `outputs/tahmkench-fx/HANDOFF.md`，打包成 `outputs/tahmkench_fx_pack_done.zip`。\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `tahmkench_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_tahmkench_fx`（小的）和 `league_tahmkench_big`（w_down、w_warn、w_up），tag = 名字"
      "（build_tahmkench.py 的 views；现在是 tools/art/fx_tahmkench.py 用代码画的占位，导入后替换）。")
    a("- `q_tongue` 是飞行投射物，画面朝飞行方向转；`w_warn` 不跟随、画在地上；`q_slow` 脚下 buff（z -1）；`t_pip1-3` 头顶三个位置。")
    a("- 用 `pixel_1x/` 切格，断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="tahmkench_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "tahmkench_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/tk/fx_ref_tk.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    des = np.asarray(Image.open(lp(os.path.join(HD, "A.png"))).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(des, 3, 0), 3, 1)).save(os.path.join(out, "design", "tahmkench_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "tahmkench_size.png"))
    shots_sheet(os.path.join(out, "design", "tahmkench_shots.png"))
    code_fx = os.path.join(TMP, "fx_code.png")
    if os.path.isfile(code_fx):
        shutil.copyfile(code_fx, os.path.join(out, "design", "code_fx.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"tahmkench_fx_{x[0]}.png", "binding": x[2], "size": x[3], "big": x[0] in BIG} for x in FX], f,
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
