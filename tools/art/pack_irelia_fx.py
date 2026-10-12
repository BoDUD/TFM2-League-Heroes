#!/usr/bin/env python3
"""Build irelia_fx_pack.zip: step 3 of Irelia's sprite - Codex draws her effects (after tools/art/pack_zeri_fx.py).

    python tools/art/pack_irelia_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name irelia_fx_redo_pack]

The pack (%TEMP%/ir_work/fx/irelia_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/irelia/PROMPTS_FX.md), design/irelia_design.png (the idle at 8x), design/irelia_size.png (the idle at
4x on the arena colour with the feet line, a 10-px ruler and the base fighter beside her) and design/irelia_shots.png
(the release frames at 4x from league/champions/league_irelia, the point each picture starts from). No League
textures this time: the effects follow her own model (the user's, 2026-10-12: the blades float round her and she drives
them by will - crimson blades with navy backs, silver edges and a cyan gem), so the pictures are her blades and their
crimson-and-cyan light.
The effects are the views the kit binds (tools/kit/build_irelia.py: view_projectiles e_line, w_line, r_blades;
view_effects a_hit, p_hit, q_hit, e_cast, e_hit, w_slash, w_hit, r_hit, r_wall_v; view_buffs pv4, mark, e_stun, w_on,
r_slow, r_wslow), in two sheets: league_irelia_fx (the small ones) and league_irelia_big (e_line, w_line, r_blades,
w_slash, r_wall_v). Placement (champion-data section 6): a line's picture (e_line, w_line) spans the whole line from
her (its left end) to its far end, turned to the cast direction, so it is drawn pointing right and symmetric top to
bottom; the flying volley the same; everything on a unit or on the ground is never mirrored, so it is drawn left-right
symmetric square for square. Codex also delivers pixel_1x/ game-size sheets.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ir_work")
DOC = os.path.join(ROOT, "assets", "source", "irelia", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "irelia_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


CRIMSON = "#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629"     # her blades' red and its light
CYAN = "#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA"                # the gems' light, the stun, the guard
SILVER = "#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98"              # the blades' edges and tips
NAVY = "#4D6085, #344367, #222B51, #131A37, #0A081C"                # the blades' backs (outline #0A081C)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT "
        "colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), "
        "colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
CR = f"a crimson ramp ({CRIMSON})"
CY = f"a cyan ramp ({CYAN})"
SV = f"a silver ramp ({SILVER})"
NV = f"a navy ramp for the blades' backs ({NAVY})"
BLADE = ("HER BLADE: a slim crescent blade like a curved leaf, crimson edge, navy back, a silver tip and a small cyan gem "
         "at its base, a 1-square dark outline - exactly the blades floating round her in design/irelia_design.png")


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
FIGURE = "the figure's place in the middle (16 x 40 squares, its bottom on the cell's bottom) EMPTY"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and the passive
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_irelia_a_hit`（跟随目标，画在人物上面；左右对称）", "14",
     "她的普攻是浮在身边的刀飞过去砍一下：目标身上一道红色的斜十字刀光（白芯、绯红光），两道交叉、左右对称，外面几点银白火星。约 14 格，居中画。",
     f"{CR} and {SV}",
     f"a BLADE STRIKE on the target, 4 frames, {LR}: 1 a white flash 4 squares across; 2 two crimson slash arcs crossing "
     "in an X 14 squares across, white cores; 3 the arcs thinning, a few silver sparks flying out at mirrored places; "
     "4 fading sparks.",
     row(4, 16, 16) + "; centered in every cell."),
    ("p_hit", "被动满层时普攻附带的伤害（目标身上），4 帧", "view_effects `league_irelia_p_hit`（跟随目标；左右对称）", "12",
     "被动「艾欧尼亚热诚」叠满 4 层后，普攻多一段伤害：在目标身上一小圈青色的光（白芯），四周 4 片很小的刀形光点向外散开。**左右对称**。约 12 格。",
     f"{CY} and {CR}",
     f"a SMALL CYAN BURST on the target, 4 frames, {LR}: 1 a white-cyan dot; 2 a cyan ring 10 squares across with a white "
     "core; 3 four tiny crimson-edged leaf sparks flying out diagonally (mirrored); 4 fading.",
     row(4, 14, 14) + "; centered in every cell."),
    ("pv4", "被动叠满 4 层（她身上，循环），4 帧", "view_buffs `league_irelia_pv4`（画在人物上面，循环；左右对称）", "34 × 42",
     "被动叠满时她身边的刀发出青光：在她身体外围上下左右几个位置有青色小光点一闪一闪（像刀上的宝石在发光），**中间人形的位置留空**，**左右对称**。约 34 格宽、42 格高。",
     f"{CY}",
     f"a CYAN GLOW round her, 4 frames, a seamless loop, {LR}, {FIGURE}: six small cyan glints (2-3 squares, white cores) "
     "spread round the figure's outline - two at shoulder height, two at the hips, two at the knees, each pair "
     "mirrored - twinkling in turn, with 1-square cyan sparkles drifting up between them.",
     row(4, 36, 44) + "."),
    # ---- Q Bladesurge
    ("q_hit", "Q 利刃冲击打中（目标身上），5 帧", "view_effects `league_irelia_q_hit`（跟随目标；左右对称）", "18",
     "她冲到目标身上砍下：一道又亮又粗的红色刀光从左上到右下、另一道从右上到左下交叉（白芯、绯红光），中心一闪白光，几片红色的光屑往外飞。**左右对称**。约 18 格。",
     f"{CR} and {SV}",
     f"a DASH STRIKE on the target, 5 frames, {LR}: 1 a white flash 6 squares across; 2 two thick crimson slash arcs "
     "crossing in an X 18 squares across, white cores; 3 the X at its brightest with a silver-white ring 12 squares across; "
     "4 crimson shards flying out at mirrored places; 5 a few fading shards.",
     row(5, 20, 20) + "; centered in every cell."),
    ("mark", "被 E / R 打中的标记（敌方英雄头上，循环），4 帧", "view_buffs `league_irelia_mark`（画在人物上面，5 秒；左右对称）", "10",
     "被 E 或 R 打中的英雄身上的「不稳」标记（Q 打它会刷新）：头顶上方一个小小的刀形印记（青色宝石在中间、红色的刀尖朝上下），一闪一闪。**左右对称**。约 10 格，画在格子上部（人头上方）。",
     f"{CR} and {CY}",
     f"a SMALL MARK over the head, 4 frames, a seamless loop, {LR}: a diamond sigil 8 squares tall and 6 wide - a cyan gem "
     "in the middle, two small crimson blade points above and below it - pulsing brighter and dimmer, two 1-square cyan "
     "sparkles at its sides.",
     row(4, 12, 48) + "; the sigil's middle 4 squares from the TOP of the cell, centered; the rest of the cell empty."),
    # ---- E Flawless Duet
    ("e_cast", "E 比翼双刃出手（她脚下），5 帧", "CasterViewEffect `league_irelia_e_cast`（跟随她，画在人物上面；左右对称）", "24 × 10",
     "她把第一把刀插在脚边：脚下一圈青色的光闪起来再收回（地上的椭圆，宽是高的 2–3 倍），中间一道竖着的白光一闪。**左右对称**，**画在格子下部（她的脚下）**。",
     f"{CY} and {SV}",
     f"a FLASH AT HER FEET, 5 frames, {LR}: 1 a white vertical glint 2 squares wide and 8 tall rising from the bottom "
     "middle; 2 a flat cyan ellipse 24 squares wide and 8 tall round it on the ground, white inner rim; 3 the ellipse at "
     "its brightest; 4 the ellipse breaking into cyan dashes; 5 a few fading dashes.",
     row(5, 26, 12) + "; the ellipse's middle 4 squares above the cell's bottom, centered."),
    ("e_line", "E 两把刀会合的那条线（从她到目标后方，转向），6 帧", "view_projectiles `league_irelia_e_line`（LineRangeProjectile 的画面：整条线，从她到 80 格外，朝方向转；上下对称）", "80 × 12",
     "E 的两把刀一把在她脚边、一把在目标身后，互相飞向对方，中间连成一道发光的线，线上的敌人被眩晕。画成**朝右的一整条线：左端是她，右端 80 格外**，两把刀从两端往中间飞（刀用她身边那种绯红刀刃、深蓝刀背、银色刀尖、青色宝石的样子），后面拖着青色的细光线，第 5 帧在中间会合一闪，第 6 帧整条线亮一下。**上下对称**。",
     f"{CR}, {CY}, {SV} and {NV}",
     f"a LINE BETWEEN TWO BLADES pointing RIGHT, 6 frames, {TB}: the picture spans the whole line, its LEFT edge is "
     f"where she stands and its RIGHT edge 80 squares away. {BLADE}, lying flat along the line, 9 squares long. 1 a "
     "blade at each end; 2-4 the two blades flying toward the middle, each trailing a thin cyan beam (2 squares thick, "
     "white core) back to its end; 5 the blades meet in the middle in a white-cyan flash 10 squares tall; 6 the whole "
     "line glowing cyan-white 3 squares thick, the blades gone.",
     row(6, 82, 14) + "; the line on the cell's middle row from the LEFT edge to the RIGHT edge."),
    ("e_hit", "E 线上的敌人被打中（目标身上），4 帧", "view_effects `league_irelia_e_hit`（跟随目标；左右对称）", "14",
     "E 的线扫过敌人：青色的横向光闪一下、中心白光，几道青色短线往外跳。**左右对称**。约 14 格。",
     f"{CY} and {CR}",
     f"a CYAN SLICE HIT on the target, 4 frames, {LR}: 1 a white horizontal glint 6 squares long; 2 a cyan flash 14 "
     "squares wide and 6 tall, white core, a thin crimson rim; 3 short cyan streaks jumping out at mirrored places; "
     "4 fading streaks.",
     row(4, 16, 16) + "; centered in every cell."),
    ("e_stun", "E 眩晕（敌人头上，循环），4 帧", "view_buffs `league_irelia_e_stun`（画在人物上面，循环 0.75 秒；左右对称）", "14 × 6",
     "被 E 眩晕的敌人头顶：三片很小的青色刀形光片绕着转（从斜上方看的小椭圆）。**左右对称**（每帧逐格对称，所以画成两边对称地转）。约 14 格宽，画在格子上部（人头上方）。",
     f"{CY} and {SV}",
     f"STUN over the head, 4 frames, a seamless loop, {LR}: a small flat ellipse of light 14 squares wide and 5 tall with "
     "three tiny cyan-silver leaf glints on it (one in the middle front, two at mirrored sides), the glints moving "
     "outward and back in turn.",
     row(4, 16, 48) + "; the ellipse's middle 4 squares from the TOP of the cell, centered; the rest of the cell empty."),
    # ---- W Defiant Dance (folded into skill2)
    ("w_on", "W 距破之舞蓄力（她身上，循环），4 帧", "view_buffs `league_irelia_w_on`（画在人物上面，蓄力约 1 秒；左右对称）", "34 × 40",
     "W 蓄力时她用刀护身、受到的物理伤害减半：她身体两侧各一把刀交叉成盾的样子（刀尖朝上、在她头部两侧，左右对称），刀上有青色的光在流动，**中间人形位置留空**。",
     f"{CR}, {CY}, {SV} and {NV}",
     f"a GUARD OF BLADES round her, 4 frames, a seamless loop, {LR}, {FIGURE}: {BLADE}, 12 squares long - one on each "
     "side of the figure, standing upright at shoulder height with the tips leaning in over the head, mirrored; a thin "
     "cyan glow running along each blade's edge from base to tip, moving up a few squares each frame.",
     row(4, 36, 44) + "."),
    ("w_slash", "W 出手（她身上），5 帧", "CasterViewEffect `league_irelia_w_slash`（跟随她，画在人物上面；左右对称）", "30",
     "W 蓄满出手的一瞬：她身前身后各一道红色的弧形刀光（左右对称地展开），中心白光一闪。**左右对称**（游戏不给它镜像，往哪边砍由 `w_line` 表现）。约 30 格宽。",
     f"{CR} and {SV}",
     f"a RELEASE BURST round her, 5 frames, {LR}, the figure's place (16 x 40 squares, bottom on the cell's bottom) "
     "EMPTY: 1 a white flash at chest height 6 squares across; 2 two crimson crescent arcs opening to both sides, 30 "
     "squares from tip to tip, white cores; 3 the arcs at their widest; 4 the arcs thinning into silver streaks; 5 fading.",
     row(5, 32, 44) + "; the flash at chest height (26 squares above the cell's bottom), centered."),
    ("w_line", "W 那一刀扫出去的刀光（从她往前，转向），5 帧", "view_projectiles `league_irelia_w_line`（LineRangeProjectile 的画面：整条线，从她到 55 格外，朝方向转；上下对称）", "55 × 14",
     "W 的一刀沿直线砍出去：一道又宽又亮的红色刀光（像月牙形的冲击波）从她身前往前冲到 55 格外，后面拖着红色的残光。画成**朝右的一整条线：左端是她，右端 55 格外**。**上下对称**。",
     f"{CR} and {SV}",
     f"a SLASH WAVE pointing RIGHT, 5 frames, {TB}: the picture spans the whole line, its LEFT edge is where she stands and "
     "its RIGHT edge 55 squares away; a crimson crescent wave 12 squares tall (its bow toward the right, white core) "
     "travelling from the left end to the right end over frames 1-4, a crimson trail 4 squares thick behind it, thinning; "
     "5 only the fading trail.",
     row(5, 57, 16) + "; the wave on the cell's middle row."),
    ("w_hit", "W 打中（目标身上），4 帧", "view_effects `league_irelia_w_hit`（跟随目标；左右对称）", "16",
     "W 的刀光扫过目标：一道粗的横向红色刀光闪过，白芯，几片红色光屑。**左右对称**。约 16 格。",
     f"{CR} and {SV}",
     f"a HEAVY SLASH HIT on the target, 4 frames, {LR}: 1 a white horizontal flash 8 squares long; 2 a thick crimson "
     "horizontal slash 16 squares long and 4 tall, white core; 3 crimson shards flying out at mirrored places; 4 fading.",
     row(4, 18, 18) + "; centered in every cell."),
    # ---- R Vanguard's Edge
    ("r_blades", "R 先锋之刃飞出去的一群刀（飞行中，循环），4 帧", "view_projectiles `league_irelia_r_blades`（直线弹，朝飞行方向转，画成朝右飞；上下对称）", "26 × 16",
     "大招：她身边的刀全部飞出去：画成朝右飞的一群刀（5 把，排成箭头形：最前面 1 把、上下各 2 把错开在后面），每把都是她身边那种刀的样子，后面拖着红色的光尾。**上下对称**。约 26 格长、16 格高。",
     f"{CR}, {CY}, {SV} and {NV}",
     f"a VOLLEY OF BLADES flying to the RIGHT, 4 frames, a seamless loop, {TB}: {BLADE}, 8 squares long, pointing right; "
     "five of them in an arrowhead - one in front on the middle row, two above and two below it stepped back 4 squares "
     "each, mirrored - every blade trailing a crimson streak 6 squares long; the streaks flicker and the blades bob a "
     "square in turn.",
     row(4, 28, 18) + "; the front blade's tip 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("r_hit", "R 打中（目标身上），5 帧", "view_effects `league_irelia_r_hit`（跟随目标；左右对称）", "20",
     "大招的刀群砍中：几道红色刀光同时交叉（米字形），中心白光，外面一圈青色光环，碎光往外飞。**左右对称**。约 20 格。",
     f"{CR}, {CY} and {SV}",
     f"a VOLLEY HIT on the target, 5 frames, {LR}: 1 a white flash 8 squares across; 2 three crimson slashes crossing in a "
     "star 20 squares across (one horizontal, two diagonal), white cores; 3 a cyan ring 16 squares across round them; "
     "4 crimson and cyan shards flying out at mirrored places; 5 fading shards.",
     row(5, 22, 22) + "; centered in every cell."),
    ("r_wall_v", "R 刀墙（地上一圈插着的刀，5 秒），10 帧", "ViewEffect `league_irelia_r_wall_v`（在落点，画在人物下面 z -1，播一遍 5 秒；左右对称）", "60 × 28",
     "大招打中后，刀插在地上围成一圈刀墙（圆圈从斜上方看是椭圆，宽 60 格、高约 26 格），里面的敌人被减速。10 帧播一遍：1–2 刀从地里冒出来，3–8 刀墙立着、刀上的青色宝石一闪一闪、地上的圈有红光流动，9–10 刀往下沉、光淡掉。刀是她身边那种刀，刀尖朝上、竖着插。**左右对称**。",
     f"{CR}, {CY}, {SV} and {NV}",
     f"a RING WALL OF BLADES on the ground, 10 frames played once, {LR}: a flat ellipse 60 squares wide and 26 tall seen "
     f"from above at an angle; twelve of {BLADE.lower()}, 7 squares tall, standing upright round the ellipse's rim with "
     "their tips up (the front ones lower on the picture, the back ones higher, the side ones smaller); a thin crimson "
     "glow line on the ground along the rim. 1-2 the blades rising out of the ground; 3-8 the wall standing, the cyan "
     "gems twinkling in turn and a brighter crimson pulse running round the rim; 9-10 the blades sinking, the glow fading.",
     row(10, 64, 36) + "; the ellipse's middle 16 squares above the cell's bottom, centered."),
    ("r_slow", "R 刀群打中的减速（脚下，循环），4 帧", "view_buffs `league_irelia_r_slow`（画在人物下面 z -1，2 秒；左右对称）", "18 × 6",
     "被大招打中的敌人脚下一圈红色的小刀印（地上的椭圆），慢慢转。**左右对称**，画在格子下部（脚下）。",
     f"{CR}",
     f"a SLOW RING at the feet, 4 frames, a seamless loop, {LR}: a flat crimson ellipse 18 squares wide and 6 tall on the "
     "ground, six tiny blade-shaped notches on it (mirrored) pulsing in turn, white highlights on the front.",
     row(4, 20, 8) + "; the ellipse's middle 3 squares above the cell's bottom, centered."),
    ("r_wslow", "在刀墙里的减速（脚下，循环），4 帧", "view_buffs `league_irelia_r_wslow`（画在人物下面 z -1，刀墙里每 10 tick 续；左右对称）", "16 × 6",
     "站在刀墙里的敌人脚下一圈淡一点的红色光圈（比 r_slow 小一点、暗一点），一闪一闪。**左右对称**，画在格子下部。",
     f"{CR}",
     f"a FAINT SLOW RING at the feet, 4 frames, a seamless loop, {LR}: a thin crimson ellipse 16 squares wide and 5 tall "
     "on the ground, dimmer than a full slow (mid crimson, no white), a brighter dash running round it.",
     row(4, 18, 8) + "; the ellipse's middle 3 squares above the cell's bottom, centered."),
]
BIG = {"e_line", "w_line", "r_blades", "w_slash", "r_wall_v"}
# where the pictures start: (tag, frame, what, marks) on the imported release frames (kit retime: attack 3, Q 3, E 3,
# W 5, R 3)
SHOTS = [("attack", 3, "a_hit / p_hit：刀飞出去砍中的那一帧（打中画在目标身上）", "feet"),
         ("skill2", 3, "e_cast / e_line：站位点（线从她这里朝目标方向，80 格）", "feet"),
         ("skill2_w", 5, "w_slash / w_line：站位点（刀光从她这里朝目标方向，55 格）", "feet"),
         ("ult", 3, "r_blades：刀群从她这里飞出", "feet"),
         ("idle", 1, "pv4 / w_on：围着她（人形位置留空）", "feet")]


def design_1x():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    a = a[4::8, 4::8] if a.shape[0] == 1024 else a
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside her."""
    import tfm2_ase as T
    fig = design_1x()
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    kn = k[ky.min():ky.max() + 1, kx.min():kx.max() + 1]
    Z, pad = 4, 6
    W = pad + fig.shape[1] + pad + kn.shape[1] + pad
    img = Image.new("RGBA", (max(W * Z, 420), (pad + max(fig.shape[0], kn.shape[0]) + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + max(fig.shape[0], kn.shape[0])
    img.alpha_composite(Image.fromarray(fig).resize((fig.shape[1] * Z, fig.shape[0] * Z), Image.NEAREST),
                        (pad * Z, (base - fig.shape[0]) * Z + 64))
    img.alpha_composite(Image.fromarray(kn).resize((kn.shape[1] * Z, kn.shape[0] * Z), Image.NEAREST),
                        ((2 * pad + fig.shape[1]) * Z, (base - kn.shape[0]) * Z + 64))
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, fig.shape[1] + 1, 10):
        x = (pad + i) * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"刀妹 {fig.shape[1]}×{fig.shape[0]} 格（连浮刀），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The release frames at 4x (league/champions/league_irelia), her standing point as a cyan cross under her feet
    (the standing column is the frame's middle: the sheet's frames are centred on it)."""
    import tfm2_ase as T
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", "league_irelia"))
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    PAD = 8
    for tag, k, what, marks in SHOTS:
        f = np.pad(np.asarray(sp.frames[sp.tag_frames(tag)[k - 1]].convert("RGBA")), ((PAD, PAD), (PAD, PAD), (0, 0)))
        px = (f.shape[1] - 2 * PAD) // 2 + PAD
        ys, xs = np.nonzero(f[..., 3] > 0)
        py = int(ys.max()) + 1                      # her feet (the soles' row), on the standing column
        pts = [(px, py)]
        x0, x1 = int(min(xs.min(), px)) - 3, int(max(xs.max(), px)) + 4
        y0, y1 = int(min(ys.min(), py)) - 3, int(max(ys.max(), py)) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 440), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        for mx, my in pts:
            cx, cy = int((mx - x0) * Z), int((my - y0) * Z) + 24
            d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
            d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    W = sum(t.width + 10 for t in tiles)
    H = max(t.height for t in tiles)
    sheet = Image.new("RGB", (W, H), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 刀锋舞者 艾瑞莉娅：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/irelia_design.png`，idle 第 1 帧放大 8 倍，{h} 行、{w} 格宽，连身边的浮刀）。")
    a(f"> - 大小对照 `design/irelia_size.png`：idle 放大 4 倍，鞋底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/irelia_shots.png`：定稿动作的出手帧（4 倍），青色十字是她的站位点（线、刀群、身上的画面都从这里算）。")
    a("> - **她的特效就是她的刀**：她不握刀，四把弯月形的刀浮在身边、用意念驱动——刀刃绯红、刀背深蓝、银色刀尖、刀根一颗青色宝石，"
      "和 `design/irelia_design.png` 里浮在她身边的刀一模一样。刀光是绯红色（白芯），宝石和眩晕、护身是青色。这次没有英雄联盟的特效贴图参考。")
    a("> - **特效要亮**：每道刀光、光圈、光点都用最亮的几档和白色的芯，暗底上一眼能看见。")
    a("> - **围着人的画面（被动满层、W 蓄力、W 出手）只画外圈和两边，中间人形位置留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方不会镜像）**：`e_line`、`w_line` 是**一整条线的画面**：游戏把整张图从她（左端）铺到线的尽头（右端）、"
      "朝施放方向转，所以**画成朝右、左端是她**，而且要**上下对称**（往左放时会上下翻）。飞出去的刀群 `r_blades` 画成朝右飞，同样**上下对称**。"
      "画在人身上、脚下、地上的（打中、标记、眩晕、减速、被动、W 蓄力、W 出手、E 出手、刀墙）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `irelia_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。")
    a("> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`irelia_fx_done.zip`）放在 outputs 里，或放在 `outputs/irelia-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 浮刀飞过去砍一下 | `a_hit` |")
    a("| 被动「艾欧尼亚热诚」 | Q 每打中一个单位、E/W/R 每打中一个英雄叠一层（攻速），满 4 层时普攻多一段伤害、身边的刀发青光 | `pv4` · `p_hit` |")
    a("| 技能 1 = Q「利刃冲击」 | 冲向目标砍一刀并回血；打带标记的目标或打死目标就能再冲一次 | `q_hit` · `mark` |")
    a("| 技能 2 = E「比翼双刃」 | 一把刀在她脚边、一把在目标身后，互相飞向对方，连成的线上的敌人被眩晕并打上标记 | `e_cast` · `e_line` · `e_hit` · `e_stun` · `mark` |")
    a("| 技能 2（E 冷却时）= W「距破之舞」 | 蓄力约 1 秒（物理伤害减半），然后沿直线砍出一刀 | `w_on` · `w_slash` · `w_line` · `w_hit` |")
    a("| 大招 = R「先锋之刃」 | 身边的刀全部飞向一个英雄，打中后对后方扇形里的敌人造成伤害、减速、缴械，再在落点插出一圈刀墙减速 | `r_blades` · `r_hit` · `r_slow` · `r_wall_v` · `r_wslow` · `mark` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**刀光、光圈、光点都没有黑描边，也不要用最深的颜色给它们描一圈边**；只有实体的刀有 1 格深色描边 `#0A081C`。")
    a("- **要亮**：每道光都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只做很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("绯红（刀刃、刀光、减速、刀墙的光）", CRIMSON), ("青色（宝石、眩晕、被动、护身、E 的线）", CYAN),
                        ("银色（刀尖、火星）", SILVER), ("深蓝（刀背，只用在实体的刀上）", NAVY)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 25000，"
      "E 的线长 80000，W 的线长 55000，R 刀群打中后的扇形半径 35000，刀墙半径 30000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `irelia_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） | 图集 |")
    a("|---|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `irelia_fx_{name}` | {bind} | {size} | {'league_irelia_big' if name in BIG else 'league_irelia_fx'} |")
    a("")
    a("- `e_line`、`w_line`：LineRangeProjectile 的画面从她铺到线尽头（champion-data「Cone / fan」：精灵中心在线的中点，左端在施法者）；按每条格子切，确认上下对称；`e_line` 循环（repeat），帧时长让 6 帧盖住 delay 24 tick。")
    a("- `r_blades`：直线弹，y_offset 0，朝飞行方向转；`r_wall_v`：ViewEffect 在落点（z -1），10 帧铺满 r_wall_t 150 tick（第 1–2、9–10 帧短，中间长）。")
    a("- `e_cast`、`w_slash` 是 CasterViewEffect（不转、不镜像）：逐格左右对称；`pv4`、`w_on`、`mark`、`e_stun` 画在人物上面，`r_slow`、`r_wslow` 在脚下（z -1）。")
    a("- 用 `pixel_1x/` 切格（import_syndra 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="irelia_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", help="folder for the zip (default: next to the pack folder)")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out or os.path.join(TMP, "fx"), a.name + ".zip")
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "design"))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    ys, xs = np.nonzero(d[..., 3] > 0)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    d = np.pad(d, ((4, 4), (4, 4), (0, 0)))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "irelia_design.png"))
    shape = size_sheet(os.path.join(out, "design", "irelia_size.png"))
    shots_sheet(os.path.join(out, "design", "irelia_shots.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"irelia_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "sheet": "league_irelia_big" if x[0] in BIG else "league_irelia_fx"} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC)
    if not a.no_zip:
        os.makedirs(os.path.dirname(zpath), exist_ok=True)
        if os.path.exists(zpath):
            os.remove(zpath)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(zpath) // 1024, "KB")


if __name__ == "__main__":
    main()
