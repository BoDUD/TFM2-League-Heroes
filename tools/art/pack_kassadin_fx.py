#!/usr/bin/env python3
"""Build kassadin_fx_pack.zip: step 3 of Kassadin's sprite - Codex draws his effects (after tools/art/pack_gragas_fx.py).

    python tools/art/pack_kassadin_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name kassadin_fx_redo_pack]

The pack (%TEMP%/ks_work/fx/kassadin_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/kassadin/PROMPTS_FX.md), design/kassadin_idle.png (his 3/4 front idle at 8x, as imported),
design/kassadin_size.png (the idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter
beside him), design/kassadin_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png
(League's own particle textures for Kassadin, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/ks_work/fxref, extracted from Kassadin.wad.client's base-skin particles by %TEMP%/ks_work/fx/fx_ref_ks.py).
The design sheets need the imported sprite (league/champions/league_kassadin#sheet.png): build the pack after step 2.
The effects are the views the kit binds (tools/kit/build_kassadin.py: view_projectiles q_orb, e_cone; view_effects
a_hit, w_hit, q_hit, q_shield, e_hit, r_out, r_in, r_hit; view_buffs e_slow, q_sil).
League's colours: void violet light with white cores and magenta sparks, a black-violet void at the heart of the orb and
the rift; the shield a cool violet-blue shell. Light gets no outline. Red side: the orb and the cone picture symmetric
top to bottom (they turn with the cast), every picture on a unit or on the ground and every buff symmetric left to
right. Codex also delivers pixel_1x/ game-size sheets.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ks_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "kassadin", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_kassadin")
HD_FRONT = os.path.join(ROOT, "assets", "source", "kassadin", "ppu", "front.png")   # the approved PPU design
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


VOID = "#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A"     # void light: white core to deep violet
MAG = "#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E"               # magenta sparks and edges
DARK = "#3A1466, #24093F, #140426"                                # the void itself (the orb's heart, the rift's hole)
SHELL = "#FFFFFF, #E2E6FF, #AEB8FF, #7280F4, #4248C6"             # Null Sphere's shield: a cool violet-blue shell
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades "
        "and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
VO = f"a void-light ramp ({VOID})"
MG = f"a magenta ramp ({MAG})"
DK = f"a deep void ramp used only inside ({DARK})"
SH = f"a violet-blue shell ramp ({SHELL})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and Nether Blade
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_kassadin_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "手上带着虚空能量的一记爪击：目标身上一个紫色的十字星光（白芯，参考 voidslash），外面几点品红火花。**左右对称**。约 12 格，居中画。",
     f"{VO} and {MG}",
     f"a VOID CLAW HIT, 4 frames, {LR}: 1 a white flash 4 squares across; 2 a four-point violet star 12 squares across "
     "(long horizontal and vertical rays, white core); 3 the star thinner, 4 magenta sparks at mirrored places; 4 a few "
     "fading sparks.",
     row(4, 14, 14) + "; centered in every cell."),
    ("w_hit", "W 虚空之刃：强化普攻的虚空刃砍中（目标身上），5 帧", "view_effects `league_kassadin_w_hit`（跟随，画在人物上面；左右对称）",
     "22",
     "虚空之刃出鞘的一刀：两道又长又亮的紫色刀光交叉成 X（白芯、紫光、刀边一点品红，参考 voidblade_glow、W_blade_swirls），中心一团深紫的虚空裂口一闪，碎光往外飞。**左右对称**。约 22 格。",
     f"{VO}, {MG} and {DK}",
     f"a VOID BLADE SLASH on a unit, 5 frames, {LR}: 1 a white flash 6 squares; 2 two long violet blade slashes crossing "
     "in an X 20 squares across, white cores, magenta edges; 3 the X at its brightest round a small black-violet rift "
     "4 squares across in the middle; 4 violet shards flying out at mirrored places; 5 fading shards.",
     row(5, 24, 24) + "; centered in every cell."),
    # ---- Q Null Sphere
    ("q_orb", "Q 虚无法球：飞出去的法球（朝目标飞，循环），4 帧",
     "view_projectiles `league_kassadin_q_orb`（朝飞行方向转，画成朝右飞；上下对称）", "12 × 10",
     "一颗虚空法球：中心是深紫近黑的虚空，外面一圈亮紫色的光环（白色亮边），后面拖一条短短的紫色尾迹和几颗品红火星（参考 OrbGlow、Q_ChargeMask、darkflame）。**上下对称**。",
     f"{VO}, {MG} and {DK}",
     f"a VOID ORB flying to the RIGHT, 4 frames, a seamless loop, {TB}: a round orb 8 squares across - a black-violet "
     "heart 4 squares across inside a bright violet ring with a white rim - pulsing one square bigger and smaller; a short "
     "violet tail 4 squares long behind it to the left, tapering, with 2-3 magenta sparks (mirrored top to bottom).",
     row(4, 14, 12) + "; the orb's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_hit", "Q 打中（目标身上），5 帧", "view_effects `league_kassadin_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "法球在目标身上炸开：一圈紫色的光环往外扩（白边），中心一团深紫虚空收缩，几颗品红火星溅开（参考 OrbGlow、VoidSwirl）。**左右对称**。约 16 格。",
     f"{VO}, {MG} and {DK}",
     f"a VOID ORB BURST on a unit, 5 frames, {LR}: 1 a white flash 5 squares; 2 a violet ring 10 squares across round a "
     "black-violet heart; 3 the ring 16 squares across, white rim, the heart shrinking; 4 magenta sparks flying out at "
     "mirrored places, the ring breaking; 5 fading sparks.",
     row(5, 18, 18) + "; centered in every cell."),
    ("q_shield", "Q 自身护盾（他身上，约 1.5 秒），6 帧", "view_effects `league_kassadin_q_shield`（跟随，画在人物上面；左右对称）",
     "34 × 44",
     "放出法球时多余的能量包住自己：身体外面一层蓝紫色的护盾外壳（只画外轮廓的一圈弧线和几块六边形的亮片，像一个罩住全身的大椭圆的边），**中间人形位置留空**，一闪出现、闪几下、最后碎掉。**左右对称**。",
     SH,
     f"a SHIELD SHELL round a tall figure, 6 frames, {LR}, its inside EMPTY (a clear upright area 26 squares wide and 36 "
     "tall in the middle): only the rim of a tall ellipse 34 squares wide and 42 tall round it - a thin violet-blue arc "
     "2 squares thick with a white inner edge and a few small hexagon glints on it at mirrored places; 1 the rim faint "
     "and short (arcs at the shoulders only); 2-4 the whole rim bright, the glints twinkling in turn; 5 the rim cracking "
     "into pieces; 6 fading pieces.",
     row(6, 36, 46) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- E Force Pulse
    ("e_cone", "E 能量脉冲：从他身前扇形推出去的冲击波（朝目标转向），6 帧",
     "view_projectiles `league_kassadin_e_cone`（LineRangeProjectile 的画面：整张图从他（左端）铺到 42 格外（右端），朝施放方向转；上下对称）",
     "44 × 56",
     "向前方扇形推出的一圈圈紫色冲击波（参考 Z_PraxisWave、EyeoftheStormSwipe）：**画成朝右**，左端是他，几道弧形的紫色波纹（白芯）从左往右扩散、越往右越宽（扇形，约 80 度张开），最后一帧在最远处散成光点。**上下对称**。",
     f"{VO} and {MG}",
     f"a CONE OF FORCE WAVES pointing RIGHT, 6 frames, {TB}: the picture's LEFT edge is where he stands, its RIGHT edge 42 "
     "squares away; the cone opens 40 degrees above and below the middle row (56 squares tall at the right end). Arc-"
     "shaped violet waves (2-3 squares thick, white cores, magenta trailing edges) curving like ripples: 1 a small arc 6 "
     "squares from the left; 2 that arc 16 squares out and a second one behind it; 3 three arcs spread over the cone; 4 "
     "the front arc near the right edge, the arcs widening with the cone; 5 the arcs thinning, sparks in the cone; 6 a few "
     "fading sparks at the far end.",
     row(6, 44, 58) + "; the cone's tip on the LEFT edge of every cell, vertically centered."),
    ("e_hit", "E 打中（目标身上），4 帧", "view_effects `league_kassadin_e_hit`（跟随，画在人物上面；左右对称）", "14",
     "被冲击波打中：一圈扁的紫色波纹闪一下、中心白光，几道紫色短线往外跳。**左右对称**。约 14 格。",
     f"{VO} and {MG}",
     f"a FORCE WAVE HIT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 a flat violet ring 12 squares wide and 6 "
     "tall with a white core; 3 short violet streaks jumping out at mirrored places; 4 fading streaks.",
     row(4, 16, 16) + "; centered in every cell."),
    ("e_slow", "E 减速（被减速的人脚下，循环），4 帧", "view_buffs `league_kassadin_e_slow`（跟随，画在人物下面；左右对称）", "16 × 6",
     "脚下一圈紫色的虚空涟漪（从斜上方看的扁椭圆），几缕紫色细丝往下拽着（像被虚空拉住）。**左右对称**。4 帧无缝循环。",
     f"{VO} and {DK}",
     f"a VOID RIPPLE under a figure's feet, 4 frames, a seamless loop, {LR}: an ellipse 16 squares wide and 5 tall - a "
     "dark violet pool with a bright violet rim - and 2-4 thin violet wisps at mirrored places rising one square and "
     "sinking again in turn.",
     row(4, 18, 8) + "; centered in every cell."),
    ("q_sil", "沉默（被沉默的人头顶，循环），4 帧", "view_buffs `league_kassadin_q_sil`（跟随，画在人物上面；左右对称）", "10 × 8",
     "E 打中后再被 Q 打中的英雄被沉默：头顶一个小小的紫色虚空符印（一个圆圈中间一道横杠，白芯），一闪一闪。**左右对称**。画在格子上部（人头上方）。",
     f"{VO} and {MG}",
     f"a SILENCE SIGIL over a head, 4 frames, a seamless loop, {LR}: a violet ring 8 squares across with a horizontal bar "
     "through it, white cores, pulsing brighter and dimmer, two 1-square magenta sparkles at its sides.",
     row(4, 12, 48) + "; the sigil's middle 5 squares from the TOP of the cell, centered; the rest of the cell empty."),
    # ---- R Riftwalk
    ("r_out", "R 虚空行走：他消失的地方（留在原地），6 帧", "view_effects `league_kassadin_r_out`（不跟随，画在人物上面；左右对称）",
     "28 × 40",
     "他从原地消失：一道竖着的深紫色虚空裂缝撕开（中间近黑、边缘亮紫白光），紫色碎光往裂缝里吸进去，然后裂缝合上、留几点火星（参考 VoidSwirl、voidslash、VoidBackground）。**左右对称**。他已经走了，所以可以画满人形的位置。",
     f"{VO}, {MG} and {DK}",
     f"a VOID RIFT CLOSING where he stood, 6 frames, {LR}: 1 a vertical white-violet slit 2 squares wide and 30 tall; "
     "2 the slit opening into a tall black-violet rift 10 squares wide and 36 tall with a bright violet-white edge; "
     "3 violet and magenta sparks streaming INTO the rift from both sides (mirrored); 4 the rift narrowing; 5 a thin slit "
     "again; 6 a few fading sparks.",
     row(6, 30, 42) + "; centered across, the rift's bottom 2 squares above the cell's bottom."),
    ("r_in", "R 虚空行走：他出现的地方（落点，爆炸），7 帧", "view_effects `league_kassadin_r_in`（不跟随，画在人物上面；左右对称）",
     "44 × 40",
     "他从虚空里出来、周围炸开：先一道竖着的虚空裂缝，然后地上一圈扁椭圆的紫色冲击环往外炸开（约 40 格宽，白边），裂缝里冒出的紫色能量往上飘，最后散成光点（参考 VoidSwirl、PraxisWave、VoidBackground）。**左右对称**，**中间人形位置在第 3 帧以后留空**（他已经站在那）。",
     f"{VO}, {MG} and {DK}",
     f"a VOID RIFT OPENING with a blast on the ground, 7 frames, {LR}: 1 a vertical white-violet slit 2 squares wide and "
     "30 tall; 2 a black-violet rift 10 squares wide with a bright edge; 3 the rift gone, the middle EMPTY (a clear upright "
     "area 24 squares wide and 36 tall where he now stands), a flat violet ring on the ground 20 squares wide and 7 tall "
     "with a white rim; 4 the ring at 40 x 13, violet wisps rising on both sides of the empty middle (mirrored); 5 the ring "
     "breaking into violet and magenta sparks; 6 sparks rising and fading; 7 a few embers.",
     row(7, 46, 42) + "; centered across, the ground ring's middle 5 squares above the cell's bottom."),
    ("r_hit", "R 打中（被炸到的人身上），4 帧", "view_effects `league_kassadin_r_hit`（跟随，画在人物上面；左右对称）", "14",
     "被虚空冲击打中：一团紫色碎光和品红火星溅在身上，中心一点深紫虚空一闪。**左右对称**。约 14 格。",
     f"{VO}, {MG} and {DK}",
     f"a VOID BLAST HIT on a unit, 4 frames, {LR}: 1 a white-violet flash 6 squares; 2 violet shards and magenta sparks "
     "bursting 12 squares across round a 2-square black-violet dot; 3 shards at mirrored places; 4 fading sparks.",
     row(4, 16, 16) + "; centered in every cell."),
]

GROUPS = [
    ("a_hit w_hit", ["voidslash", "voidblade_glow", "Kassadin_Base_W_blade_swirls", "Kassadin_base_idle_blade",
                     "Kassadin_Base_W_buf_sparks", "EveFlames01"]),
    ("q_* sil", ["OrbGlow", "ball32_02", "Kassadin_Base_Q_ChargeMask", "Aura_Self", "kassadin-darkflame-purple",
                 "color-turretcrystal"]),
    ("e_*", ["Kassadin_Base_Z_PraxisWave", "EyeoftheStormSwipe_Frost", "voidline", "color-bellcurve", "Aura_Self",
             "Kassadin_Base_W_buf_sparks"]),
    ("r_*", ["Kassadin_Base_Z_VoidSwirl", "Kassadin_Base_Z_VoidBackground_04", "distort-bulge", "voidslash", "OrbGlow",
             "kassadin-darkflame-purple"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point (set after step 2)
SHOTS = [("attack", 3, "a_hit：爪子打到的地方（画在目标身上）"),
         ("attack_w", 3, "w_hit：虚空之刃砍到的地方"),
         ("skill", 3, "q_orb：法球从手里飞出去；q_shield 包住全身"),
         ("skill2", 3, "e_cone：冲击波从他身前推出去"),
         ("ult", 2, "r_out / r_in：消失和出现的地方"),
         ("idle", 1, "e_slow / q_sil：站位点")]


def ref_sheet(path):
    S, LW = 180, 90
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            im = Image.open(os.path.join(REF, nm + ".png")).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Kassadin_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def idle_1x():
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    f = np.asarray(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA"))
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """His idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
    import tfm2_ase as T
    fig = idle_1x()
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
    d.text((8, 36), f"卡萨丁 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (the imported sheet), his standing point as a cyan cross."""
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    px = sp.w // 2 + PAD
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(np.asarray(sp.frames[sp.tag_frames(tag)[k - 1]].convert("RGBA")), ((PAD, PAD), (PAD, PAD), (0, 0)))
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(ys.max()) + 1)
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(ys.max()) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 330), sub.shape[0] * Z + 24), (104, 112, 72, 255))
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
    a("# 虚空行者 卡萨丁：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/kassadin_idle.png`：游戏里的 3/4 正面待机）。他在游戏里是**高清**的（PPU：每个游戏格子里 3.62×3.62 个细像素，这张图就是高清造型放大 3 倍），连角 {h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/kassadin_size.png`：待机放大 4 倍，长袍下摆在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/kassadin_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡萨丁自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**虚空的紫色光（白芯）和品红色火星**，法球和裂缝的中心是**深紫近黑的虚空**；Q 的护盾是冷一点的**蓝紫色外壳**。")
    a("> - **特效要亮**：每道光、每圈波纹都要有白色或最亮一档的芯，暗底上一眼能看见；深紫近黑只用在法球和裂缝的最里面。")
    a("> - **围着人的护盾、R 出现时的能量只画外圈和两边，中间人形位置留空**，不然会把人整个挡住（`r_out` 例外：他已经走了）。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的法球 `q_orb` 画成朝右飞；E 的冲击波 `e_cone` 是**一整片扇形的画面**：游戏把整张图从他（左端）铺到 42 格外（右端）、朝施放方向转，所以**画成朝右、左端是他**。"
      "这两张都要**上下对称**（往左放时会上下翻）。其余所有画面（打中、身上、脚下、头顶、裂缝）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `kassadin_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `kassadin_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + W「虚空之刃」 | 带虚空能量的爪击；每 7 秒一次虚空刃强化普攻 | `a_hit` · `w_hit` |")
    a("| 技能 1 = Q「虚无法球」 | 向目标发射虚空法球，打断英雄；自己获得护盾 | `q_orb` · `q_hit` · `q_shield` · `q_sil` |")
    a("| 技能 2 = E「能量脉冲」 | 向前方扇形推出冲击波，打中的人减速 | `e_cone` · `e_hit` · `e_slow` |")
    a("| 大招 = R「虚空行走」 | 从原地消失、闪到敌方英雄身边，周围炸开 | `r_out` · `r_in` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、波纹、火星、光环、护盾都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("虚空紫光", VOID), ("品红火星", MAG), ("虚空深处（只用在最里面）", DARK), ("护盾外壳（Q）", SHELL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 24000，"
      "E 扇形半径 42000、张角约 80 度，R 爆炸半径 20000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `kassadin_fx_{name}.png`：{title}\n")
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
        a(f"| `kassadin_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_kassadin_fx`（小的）和 `league_kassadin_big`（e_cone、r_out、r_in），tag = 名字（build_kassadin.py 的 views）。")
    a("- `q_orb` 是 TargetProjectile，画面朝飞行方向转；`e_cone` 是 LineRangeProjectile 的画面（从他铺到 42 格外）；`r_out`、`r_in` 不跟随；`e_slow` 脚下 buff（z -1）；`q_sil` 头顶（z 3）；`q_shield` 跟随画在人物上面，中间必须是空的。")
    a("- 用 `pixel_1x/` 切格（import_gragas / import_irelia 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="kassadin_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", help="folder for the zip (default: next to the pack folder)")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out or os.path.join(TMP, "fx"), a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run %TEMP%/ks_work/fx/fx_ref_ks.py first")
    if not os.path.exists(SHEET + "#sheet.png"):
        sys.exit(f"no imported sprite {SHEET}#sheet.png: build this pack after step 2")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    # his idle as the game shows it with league.dll: the PPU design (3.62 fine squares a game square), 3x
    hd = np.asarray(Image.open(HD_FRONT).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(hd, 3, 0), 3, 1)).save(os.path.join(out, "design", "kassadin_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "kassadin_size.png"))
    shots_sheet(os.path.join(out, "design", "kassadin_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"kassadin_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
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
