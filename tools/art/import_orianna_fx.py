#!/usr/bin/env python3
"""Import Orianna's effects (assets/source/orianna/PROMPTS_FX.md) as the game sheets league_orianna_fx and
league_orianna_big.

    python tools/art/import_orianna_fx.py [--review out.png]

The source is Codex's step-3 run as the user forwarded it (2026-10-16, 「特效做好了 你完善吧 然后导入」: 15 JPEG
screenshots, each 2000 px wide, on black, assets/source/orianna/codex_fx/orianna_fx_<name>.jpg; no ball_side came). The
light effects are read import_pantheon_fx.py's way through import_kassadin.py: each picture a row (w_haste a 2 x 2 grid)
of equal cells, the background keyed out, one scale per effect (the biggest frame's content to SIZE), every game pixel
the commonest colour under it snapped to the prompt's ramps with the bright cores kept, symmetric left to right about
each frame's best axis (the fuller half mirrored; a_bolt top to bottom). Codex drew some round where the ground wants a
flat ellipse: R's vortex and rings are squashed to half their height (the blast's column comes out ~48 px, not 97),
E's bubble to 0.72 of its width (the prompt's 26 x 40 ellipse). R's darkest blue is kept only on the drawing's edges
(its first vortex and its fading ring were solid dark pools).
The Ball: Codex drew it ~25 squares across, a blur at the 10-14 game px it is shown at - every Ball picture uses the
user's own Ball instead (assets/source/orianna/hd/ball2.png, the step-1 pick 「第2稿球」, 27 x 29) brought to BALL_W x
BALL_H by whole rows and columns (the centre of each band kept; the user, 2026-10-16: 「球太大了吧？」 - the 14 x 15 cut
was as big as her head - picked 11 px of a 14 / 12 / 11 / 10 sheet) with a faint blue glow ring: beside a champion (ball_side, bobbing 0 / -1 / -1 / 0 / +1 / +1, a spark on frames 2 and 5), lying (ball_ground,
over a dark ground shadow, bobbing a square) and flying (ball_fly: Codex's electric trail, read like the light, behind it).
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(build_orianna.P, 60 ticks a second).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import import_kassadin as K  # noqa: E402
from design_varus import srgb2lab  # noqa: E402
from build_orianna import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "orianna", "codex_fx")
# the chibi redesign's Ball (2026-10-22): Codex's new Ball drawn again by hand at game size in the design's own steel
# and bronze (its line cuts and votes came out a dark blot at 12 px) - used as it is
BALL_PNG = os.path.join(ROOT, "assets", "source", "orianna", "chibi", "ball_1x.png")
BALL_W, BALL_H = 12, 12
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)
MS = 1000 / 60


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# the prompt's ramps (pack_orianna_fx.py)
ELEC = ["#FFFFFF", "#DDFBFF", "#93EDFF", "#45C6F7", "#2183DC", "#143F8E"]
GEAR = ["#FFF4C4", "#FFD75E", "#E7A41C", "#A36608"]
DARKS = {rgb("#143F8E"), rgb("#A36608")}
RAMPS = {"e": ELEC, "eg": ELEC + GEAR}

# effect -> (columns, rows, [(column, row) used], ramps); the pictures are named orianna_fx_<effect>.jpg
CELLS = {
    "r_hit": (4, 1, [(k, 0) for k in range(4)], "e"),
    "r_wave": (9, 1, [(k, 0) for k in range(9)], "eg"),
    "e_hit": (4, 1, [(k, 0) for k in range(4)], "e"),
    "e_shield": (6, 1, [(k, 0) for k in range(6)], "e"),
    "w_haste": (2, 2, [(0, 0), (1, 0), (0, 1), (1, 1)], "e"),
    "w_slow": (4, 1, [(k, 0) for k in range(4)], "e"),
    "w_hit": (4, 1, [(k, 0) for k in range(4)], "e"),
    "w_ring": (6, 1, [(k, 0) for k in range(6)], "eg"),
    "b_home_in": (4, 1, [(k, 0) for k in range(4)], "e"),
    "q_hit": (5, 1, [(k, 0) for k in range(5)], "eg"),
    "q_land": (5, 1, [(k, 0) for k in range(5)], "e"),
    "a_hit": (4, 1, [(k, 0) for k in range(4)], "e"),
    "a_bolt": (3, 1, [(k, 0) for k in range(3)], "e"),
    "ball_fly": (4, 1, [(k, 0) for k in range(4)], "e"),     # the trail only (the Ball is the user's)
}
SQUASH = {"r_wave": (1.0, 0.5), "e_shield": (0.72, 1.0)}      # (x, y) before reading: round where a flat one is meant
EDGE = {"q_hit": 14, "a_bolt": 24, "q_land": 8}               # pixels off each cell's sides (white / grey lines)
# the biggest frame's size in game px: ("w" | "h", n)
SIZE = {"r_hit": ("w", 22), "r_wave": ("w", 2 * P["r_r"] // 1000), "e_hit": ("w", 16), "e_shield": ("h", 42),
        "w_haste": ("w", 22), "w_slow": ("w", 18), "w_hit": ("w", 18), "w_ring": ("w", 2 * P["w_r"] // 1000 + 4),
        "b_home_in": ("w", 16), "q_hit": ("w", 18), "q_land": ("w", 2 * P["q_r"] // 1000 + 2), "a_hit": ("w", 14),
        "a_bolt": ("w", 14), "ball_fly": ("h", 12)}
SYM = {"a_bolt": "tb", "ball_fly": "tb"}      # every other one "lr"
BIG = {"w_ring", "r_wave"}

HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
BALL_AT = (17, -9)              # the Ball beside a champion: 17 px ahead of the feet's middle, 20 over the ground (12 covered
                                # her face as she ran: 「奥利安娜走路的时候球有点挡脸了」 - 17 clears her idle and run)
EMPTY = J.EMPTY
seq = J.seq


def key(rgb_):
    """Black (or near-black JPEG noise) out; the white cell lines go with the cell edges (EDGE)."""
    mx, mn = rgb_.max(-1), rgb_.min(-1)
    a = (mx > 40) & ((mx - mn > 20) | (mn > 170))
    return np.where(a, 255, 0).astype(np.int16)


def strip(name):
    """The used cells of the picture side by side, keyed, as one RGBA sheet; the frames' boxes in it."""
    cols, rows, used, _ = CELLS[name]
    img = Image.open(lp(os.path.join(SRC, f"orianna_fx_{name}.jpg"))).convert("RGB")
    if name in SQUASH:
        fx, fy = SQUASH[name]
        img = img.resize((max(1, round(img.width * fx)), max(1, round(img.height * fy))), Image.LANCZOS)
    im = np.asarray(img).astype(np.int16)
    H, W = im.shape[:2]
    cw, ch = W // cols, H // rows
    e = EDGE.get(name, 2)
    pieces = []
    for c, r in used:
        p = im[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw].copy()
        p[:, :e] = 0
        p[:, -e:] = 0
        p[:3] = 0
        p[-3:] = 0
        pieces.append(p)
    rgb_ = np.concatenate(pieces, 1)
    a = key(rgb_)
    sheet = np.concatenate([rgb_, a[..., None]], -1)
    return sheet, (1, ch - 1), [(k * cw + 2, (k + 1) * cw - 2) for k in range(len(pieces))]


def use_ramps(names):
    K.PAL = np.array([rgb(h) for h in names], np.uint8)
    K.PAL_LAB = srgb2lab(K.PAL.astype(float))
    K.PAL_LUM = K.PAL.astype(float) @ np.array([0.3, 0.59, 0.11])
    K.DARKS = DARKS


def trail_only(sheet):
    """ball_fly: Codex's Ball (grey, gold, violet - not the blue light) cleared, its trail kept."""
    r, g, b = (sheet[..., i].astype(int) for i in range(3))
    blue = (b > r + 25) & (b >= g - 10)
    sheet[(sheet[..., 3] > 0) & ~blue] = 0
    return sheet


def thin_dark(c):
    """The darkest blue only where it edges the drawing: Codex filled R's first vortex and its fading ring with it,
    a heavy dark pool at game size."""
    navy = np.all(c[..., :3] == rgb("#143F8E"), -1) & (c[..., 3] > 0)
    op = np.pad(c[..., 3] > 0, 1)
    inner = np.ones_like(navy)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            inner &= op[1 + dy:op.shape[0] - 1 + dy, 1 + dx:op.shape[1] - 1 + dx]
    out = c.copy()
    out[navy & inner] = 0
    return out


THIN_DARK = {"r_wave"}


def build_cells():
    cells = {}
    for name in CELLS:
        sheet, band, boxes = strip(name)
        if name == "ball_fly":
            sheet = trail_only(sheet)
        use_ramps(RAMPS[CELLS[name][3]])
        K.BOXES = {name: (name, band, boxes)}
        K.SIZE, K.SYM, K.AXIS = SIZE, SYM, {}
        frames, s, _ = K.frames_of(name, {name: sheet})
        sym = SYM.get(name, "lr")
        cs = K.common_cell(frames, sym, None, s, band)
        if sym == "lr":
            cs, _ = K.trim_rows(cs)
        else:
            any_col = np.zeros(cs[0].shape[1], bool)
            for c in cs:
                any_col |= c[..., 3].any(0)
            xs = np.nonzero(any_col)[0]
            cs = [c[:, xs.min():xs.max() + 1] for c in cs]
        if name in THIN_DARK:
            cs = [thin_dark(c) for c in cs]
        if name == "r_wave":            # frame 7: the faded column's dark outline over the swirl goes
            c = cs[6]
            navy = np.all(c[..., :3] == rgb("#143F8E"), -1) & (c[..., 3] > 0)
            top = np.nonzero((c[..., 3] > 0).any(1) & ~(navy | (c[..., 3] == 0)).all(1))[0].min()
            c[:top][navy[:top]] = 0
        K.check(name, cs, sym)
        cells[name] = cs
        print(f"{name}: {len(cs)} cells {cs[0].shape[1]}x{cs[0].shape[0]} (scale {s:.4f})")
    return cells


# ---------------------------------------------------------------- the Ball (the user's)
GLOW = rgb("#2183DC")
SPARK = rgb("#93EDFF")
SHADOW = (22, 24, 46)


def ball_sprite():
    a = np.asarray(Image.open(lp(BALL_PNG)).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    H, W = a.shape[:2]
    if (W, H) == (BALL_W, BALL_H):
        return a
    ys = [int((i + 0.5) * H / BALL_H) for i in range(BALL_H)]
    xs = [int((i + 0.5) * W / BALL_W) for i in range(BALL_W)]
    return a[ys][:, xs]


def glowed(ball):
    """The Ball with a 1-px faint blue glow ring round it (4-neighbours of its silhouette)."""
    h, w = ball.shape[:2]
    out = np.zeros((h + 2, w + 2, 4), np.uint8)
    out[1:-1, 1:-1] = ball
    m = out[..., 3] > 0
    ring = np.zeros_like(m)
    ring[1:] |= m[:-1]
    ring[:-1] |= m[1:]
    ring[:, 1:] |= m[:, :-1]
    ring[:, :-1] |= m[:, 1:]
    ring &= ~m
    out[ring] = (*GLOW, 255)
    return out


def ball_side(ball):
    """Six frames: the glowing Ball bobbing 0 / -1 / -1 / 0 / +1 / +1, a spark beside it on frames 2 and 5; each frame
    on one canvas with the Ball's centre at its (cx, cy)."""
    g = glowed(ball)
    h, w = g.shape[:2]
    H, W = h + 4, w + 4
    cx, cy = (W - 1) / 2, (H - 1) / 2
    out = []
    for k, dy in enumerate((0, -1, -1, 0, 1, 1)):
        c = np.zeros((H, W, 4), np.uint8)
        c[2 + dy:2 + dy + h, 2:2 + w] = g
        if k in (1, 4):
            c[2 + dy + 2, 0] = (*SPARK, 255)
            c[2 + dy + h - 3, W - 1] = (*SPARK, 255)
        out.append(c)
    return out, (cx, cy)


def ball_ground(ball):
    """Two frames: the glowing Ball over a flat dark shadow (its bottom 3 over the shadow's row, then 2); the anchor is
    the shadow's middle."""
    g = glowed(ball)
    h, w = g.shape[:2]
    sw = w - 4
    H = h + 4
    out = []
    for k, lift in enumerate((4, 3)):
        c = np.zeros((H, w, 4), np.uint8)
        y0 = H - 1 - lift - (h - 1)
        c[y0:y0 + h] = g
        sh = np.zeros((H, w), bool)
        sh[H - 1, (w - sw) // 2 + 1:(w + sw) // 2 - 1] = True
        sh[H - 2, (w - sw) // 2:(w + sw) // 2] = True
        c[sh & (c[..., 3] == 0)] = (*SHADOW, 255)
        out.append(c)
    return out, ((w - 1) / 2, H - 1.5)


def ball_fly(ball, trails):
    """The Ball at the right end of each trail frame (the trail's own right end under the Ball's middle), the trail's
    middle row on the Ball's; the anchor is the Ball's centre."""
    g = glowed(ball)
    h, w = g.shape[:2]
    out = []
    TH = trails[0].shape[0]
    tw = max(t.shape[1] for t in trails)
    H = max(h, TH)
    W = tw + w // 2
    for t in trails:
        c = np.zeros((H, W, 4), np.uint8)
        y = (H - TH) // 2
        c[y:y + TH, :t.shape[1]] = t
        bx, by = W - w, (H - h) // 2
        m = g[..., 3] > 0
        c[by:by + h, bx:bx + w][m] = g[m]
        out.append(c)
    return out, (W - w + (w - 1) / 2, (H - 1) / 2)


def ring_mid(cell):
    """A ground ring's middle row: halfway between its top and bottom edges (the rows with half the widest row's
    squares or more)."""
    n = (cell[..., 3] > 0).sum(1)
    ys = np.nonzero(n >= 0.5 * n.max())[0]
    return [(cell.shape[1] - 1) / 2, (ys.min() + ys.max()) / 2]


def core(cell):
    h, w = cell.shape[:2]
    return [(w - 1) / 2, (h - 1) / 2]


def bolt_tip(cell):
    """The bolt's orb: 1.5 squares in from the right end of its drawn columns, on the middle row."""
    xs = np.nonzero(cell[..., 3].any(0))[0]
    return [xs.max() - 1.5, (cell.shape[0] - 1) / 2]


SHIELD_MS = P["e_t"] * MS
N_SHIELD = int((SHIELD_MS - 150) // 120)
# effect -> (anchor (a function of the cells), frames with ms, spots)
FX = {
    "a_bolt": (lambda cs: bolt_tip(cs[0]), J.flight(3, 50, 420, lead=2), [(0, 0)]),
    "a_hit": (lambda cs: core(cs[0]), seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_land": (lambda cs: ring_mid(cs[3]), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "q_hit": (lambda cs: core(cs[0]), seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    # the Ball's flash where it sits beside her
    "b_home_in": (lambda cs: core(cs[0]), seq(range(4), [50, 60, 70, 80]), [BALL_AT]),
    "w_ring": (lambda cs: ring_mid(cs[5]), seq(range(6), [P["w_anim"] * MS / 3, 80, 110, 110, 100, 90]), [SOLES]),
    "w_hit": (lambda cs: core(cs[0]), seq(range(4), [40, 50, 70, 80]), [HIT]),
    "w_slow": (lambda cs: ring_mid(cs[0]), seq(range(4), [100] * 4), [SOLES]),
    "w_haste": (lambda cs: ring_mid(cs[3]), seq(range(4), [100] * 4), [SOLES]),
    # the bubble for e_t ticks: frames 1-5 looped, 6 the fade; its bottom 2 under the feet
    "e_shield": (lambda cs: [(cs[0].shape[1] - 1) / 2, cs[0].shape[0] - 1],
                 seq([k % 5 for k in range(N_SHIELD)] + [5], [120] * N_SHIELD + [150]), [(0, 13)]),
    "e_hit": (lambda cs: core(cs[0]), seq(range(4), [40, 50, 60, 70]), [HIT]),
    # the gathering over the r_delay ticks before the blow (frames 1-5), the blast (frame 6) when it lands; the
    # ground rings on the ground
    "r_wave": (lambda cs: ring_mid(cs[8]), seq(range(9), [P["r_delay"] * MS / 5] * 5 + [90, 110, 120, 140]), [SOLES]),
    "r_hit": (lambda cs: core(cs[0]), seq(range(4), [40, 50, 70, 90]), [HIT]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    cells = build_cells()
    tables = {"league_orianna_fx": {}, "league_orianna_big": {}}
    for name, (anc_of, frames, spots) in FX.items():
        cs = cells[name]
        anc = anc_of(cs)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_orianna_big" if name in BIG else "league_orianna_fx"][name] = out
    # the Ball's three pictures
    ball = ball_sprite()
    side, anc = ball_side(ball)
    tables["league_orianna_fx"]["ball_side"] = [(J.place(c, anc, [BALL_AT]), 120) for c in side]
    ground, anc = ball_ground(ball)
    half = P["b_step"] * MS / 2       # re-stamped every b_step ticks: the two frames fill one step (+15 ms overlap)
    tables["league_orianna_fx"]["ball_ground"] = [(J.place(c, anc, [SOLES]), ms)
                                                  for c, ms in zip(ground, (half, half + 15))]
    fly, anc = ball_fly(ball, cells["ball_fly"])
    loop = int(np.ceil(900 / 70))
    tables["league_orianna_fx"]["ball_fly"] = [(J.place(fly[i % 4], anc, [(0, 0)]), 70 if i < loop - 1 else 1000)
                                               for i in range(loop)]
    cells.update({"ball_side": side, "ball_ground": ground, "ball_fly*": fly})
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name, cs in cells.items():
            W = sum(c.shape[1] + 2 for c in cs)
            H = max(c.shape[0] for c in cs)
            img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
            x = 0
            for c in cs:
                img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                    (x * Z, (H - c.shape[0]) * Z))
                x += c.shape[1] + 2
            rows.append((name, img))
        W = max(r.width for _, r in rows) + 120
        Ht = sum(r.height + 10 for _, r in rows)
        sheet = Image.new("RGB", (W, Ht), (20, 20, 26))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.paste(r.convert("RGB"), (120, y))
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += r.height + 10
        sheet.save(a.review)
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
