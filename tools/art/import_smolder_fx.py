#!/usr/bin/env python3
"""Import Smolder's effects (assets/source/smolder/PROMPTS_FX.md, 20 sheets) as the game sheets league_smolder_fx and
league_smolder_big, from Codex's step-3 delivery (assets/source/smolder/codex_fx/smolder-fx) - league_malzahar's way
(tools/art/import_malzahar_fx.py).

    python tools/art/import_smolder_fx.py [--review out.png]

Codex delivered every sheet at game size (pixel_1x/: one game pixel a square, a row of equal cells, hard alpha, the
prompt's ramps, every cell symmetric), so most sheets are only cut, checked, given their anchor and placed. Two are
read again from Codex's own drafts (raw/), whose shapes its read-back lost:
  * r_mom - the mother's shadow: the draft is a clean dragon silhouette with an unbroken orange rim; the read-back
    broke the rim into dashes and smeared the wings. Read at one scale both ways (the draft's own proportions, its
    height brought to MOM_H = 60 squares: at 42 the tail broke into dashes), the rim kept (a square takes the fire's colour where it covers a fifth of the drawn
    pixels), the shadow the commonest colour, mirrored squares voting together (top to bottom);
  * r_fire - the fire band: Codex drew it in a frame far taller than the prompt's 132 x 24 and squeezed the whole
    frame into 24 rows, the band 6-9 rows thick. Read with the band's own body (the rows where a tenth of the frame's
    width is drawn) brought to 22 rows across the whole 132 columns.
One sheet gets a hand fix (PAINT): r_heal's small hearts in frames 2 and 4 read back as a round blob and a flat-topped
bowl, and frame 3's has 2-px lobes over a 2-px cleft - all three redrawn as hearts with a 1-px cleft in the sheet's own
colours (on the cell made odd first).
Even cells are made odd across their mirror axis (the column left of it doubled; for the flying and turned ones the
row above it): a game frame has the pivot's pixel in its middle. The flying pictures and the turned bands are
symmetric top to bottom, everything else left to right; check() asserts it on the game frames.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Hits on the upper body (0, -12);
the ground explosions' ellipse middles, the burn's and the heal's roots, the soot, the wind ring on the soles; the
blowback's three fireballs start at the explosion's point (the band's picture is drawn centred on that point, so the
cell is anchored at its left edge); the fire band is drawn at the middle of its 130000 line (its cell spans the line).
Times from the kit (tools/kit/build_smolder.py P, 60 ticks a second).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import import_bard_fx as B  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "smolder", "codex_fx", "smolder-fx")
SRC = os.path.join(RAW, "pixel_1x")
MOD = os.path.join(ROOT, "league")

# sheet -> (frames, anchor: "core" (the cell's middle), ("bottom", k): k squares above the drawing's lowest row on the
# middle column, "left": the cell's left edge at its middle row; symmetry)
SHEETS = {
    "a_bolt": (4, "core", "tb"), "a_hit": (4, "core", "lr"), "q_bolt": (4, "core", "tb"), "q_hit": (4, "core", "lr"),
    "q_t1": (6, ("bottom", 7), "lr"), "q_t2": (5, "left", "tb"), "q_t2_hit": (3, "core", "lr"),
    "q_burn": (4, ("bottom", 0), "lr"), "w_bolt": (4, "core", "tb"), "w_hit": (4, "core", "lr"),
    "w_boom": (6, ("bottom", 8), "lr"), "e_shot": (3, "core", "tb"), "e_hit": (3, "core", "lr"),
    "e_haste": (4, "core", "lr"), "r_mom": (4, "core", "tb"), "r_fire": (4, "core", "tb"), "r_hit": (4, "core", "lr"),
    "r_heal": (5, ("bottom", 0), "lr"), "p_up": (6, ("bottom", 0), "lr"), "slow": (4, "core", "lr"),
}
FG = 128                         # a draft pixel this opaque is drawn
HIT = (0, -12)                   # a hit on the upper body of a 30-44 px unit
SOLES = (0, 11)                  # on the ground under a unit or a point
seq = J.seq
flight = J.flight

FX = {
    # the attack: 55 px at 6 a tick (~9 ticks), homing: drawn for twice that; Q 55 px at 7; W's line 100 px at 8;
    # E's shots 70 px at 7
    "a_bolt": ("a_bolt", flight(4, 60, 320, lead=2), (0, 0)),
    "a_hit": ("a_hit", seq(range(4), [40, 50, 60, 70]), HIT),
    "q_bolt": ("q_bolt", flight(4, 60, 300, lead=2), (0, 0)),
    "q_hit": ("q_hit", seq(range(4), [40, 50, 60, 80]), HIT),
    "q_t2_hit": ("q_t2_hit", seq(range(3), [40, 60, 80]), HIT),
    # tier 3: played every q_burn_p 60 ticks while it burns (3 s): 4 frames a second
    "q_burn": ("q_burn", seq(range(4), [250] * 4), SOLES),
    "w_bolt": ("w_bolt", flight(4, 60, 260, lead=2), (0, 0)),
    "w_hit": ("w_hit", seq(range(4), [40, 50, 60, 80]), HIT),
    "e_shot": ("e_shot", flight(3, 50, 240, lead=1), (0, 0)),
    "e_hit": ("e_hit", seq(range(3), [40, 50, 70]), HIT),
    "r_hit": ("r_hit", seq(range(4), [40, 60, 70, 90]), HIT),
    "r_heal": ("r_heal", seq(range(5), [80, 110, 130, 130, 120]), SOLES),
    "p_up": ("p_up", seq(range(6), [70, 90, 110, 120, 110, 120]), SOLES),
    # buffs while they last (looped): W / R's slow, E's flight
    "slow": ("slow", seq(range(4), [150] * 4), SOLES),
    "e_haste": ("e_haste", seq(range(4), [90] * 4), SOLES),
}
BIG = {
    # tier 1: the explosion on the target's spot; W's on the first champion hit
    "q_t1": ("q_t1", seq(range(6), [50, 70, 90, 100, 110, 130]), SOLES),
    "w_boom": ("w_boom", seq(range(6), [50, 70, 90, 110, 120, 140]), SOLES),
    # tier 2: the three fireballs over the band's q_t2_pic 24 ticks (400 ms)
    "q_t2": ("q_t2", seq(range(5), [60, 70, 80, 90, 100]), (0, 0)),
    # R: mom's shadow flies the 130 px line at 6 a tick (~22 ticks, 360 ms), wings beating; her fire lies r_pic 45
    # ticks (750 ms): catching, burning (twice), burning out
    "r_mom": ("r_mom", seq([0, 1, 2, 3, 0, 1, 2, 3], [70] * 7 + [1000]), (0, 0)),
    "r_fire": ("r_fire", seq([0, 1, 2, 1, 2, 3], [90, 120, 130, 120, 130, 160]), (0, 0)),
}
TB_TAGS = {"a_bolt", "q_bolt", "w_bolt", "e_shot", "q_t2", "r_mom", "r_fire"}


def manifest():
    with open(G.lp(os.path.join(RAW, "manifest.json")), encoding="utf-8") as f:
        return {a["name"]: a for a in json.load(f)["sheets"]}


# hand fixes on Codex's 1x cells, made odd first (a heart's 1-px cleft needs a middle column):
# {sheet: {frame index: (top row, [rows of the odd cell's columns, "." clear, " " kept])}}
HEART = {"A": (255, 134, 168), "B": (255, 255, 255), "C": (232, 90, 134), "D": (255, 230, 238), "E": (255, 184, 204)}
PAINT = {"r_heal": {1: (4, ["      .CC.CC.      ",
                            "      .CBBBC.      ",
                            "      ..CBC..      ",
                            "      ...C...      "]),
                    2: (3, ["     ..CC.CC..     ",
                            "     .CDBCBDC.     ",
                            "     .CBBBBBC.     ",
                            "     ..CBBBC..     ",
                            "     ...CEC...     ",
                            "     ....C....     "]),
                    3: (1, ["     ..CC.CC..     ",
                            "     .CDBCBDC.     ",
                            "     ..CBBBC..     ",
                            "     ...CEC...     ",
                            "     ....C....     "])}}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"smolder_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"smolder_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(n)]
    if name in PAINT:
        out = [B.odd(c, SHEETS[name][2]) for c in out]
    for k, (top, rows) in PAINT.get(name, {}).items():
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == ".":
                    out[k][top + j, i] = 0
                elif ch != " ":
                    out[k][top + j, i] = (*HEART[ch], 255)
    return out


def draft(name):
    """Codex's draft for the sheet (the raw its manifest chose), its palette and its frame windows (the source crop cut
    in equal columns, as Codex cut it)."""
    a = manifest()[name]
    raw = np.asarray(Image.open(G.lp(os.path.join(RAW, a["raw_file"]))).convert("RGBA")).astype(float)
    pal = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in a["palette"]], float)
    x0, y0, x1, y1 = a["source_crop"]
    n = a["frames"]
    wins = [(x0 + (x1 - x0) * k / n, y0, x0 + (x1 - x0) * (k + 1) / n, y1) for k in range(n)]
    return raw, pal, [tuple(int(round(v)) for v in w) for w in wins]


def vote_grid(raw, pal, box, W, H, need, pick):
    """Squares of the box (x0, y0, x1, y1 in draft px) on a W x H grid: (votes per palette colour, drawn share)."""
    x0, y0, x1, y1 = box
    op = raw[..., 3] >= FG
    snap = ((raw[..., None, :3] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    votes = np.zeros((H, W, len(pal)))
    cover = np.zeros((H, W))
    sx, sy = (x1 - x0) / W, (y1 - y0) / H
    for j in range(H):
        ya, yb = int(round(y0 + j * sy)), max(int(round(y0 + j * sy)) + 1, int(round(y0 + (j + 1) * sy)))
        for i in range(W):
            xa, xb = int(round(x0 + i * sx)), max(int(round(x0 + i * sx)) + 1, int(round(x0 + (i + 1) * sx)))
            o = op[ya:yb, xa:xb]
            if o.size:
                cover[j, i] = o.mean()
                if o.any():
                    votes[j, i] = np.bincount(snap[ya:yb, xa:xb][o], minlength=len(pal))
    return votes, cover


def paint(votes, cover, pal, need, pick):
    H, W = cover.shape
    share = votes / np.maximum(votes.sum(-1), 1)[..., None]
    c = np.zeros((H, W, 4), np.uint8)
    for j in range(H):
        for i in range(W):
            if cover[j, i] < need:
                continue
            c[j, i, :3] = pal[pick(share[j, i])].astype(np.uint8)
            c[j, i, 3] = 255
    return c


def reread_mom():
    """r_mom from the draft: each frame's silhouette (its largest piece's bounds over all frames, one box) at one scale,
    MOM_H squares tall; the fire rim from a fifth of the drawn pixels, else the commonest colour; top / bottom votes
    pooled."""
    raw, pal, wins = draft("r_mom")
    op = raw[..., 3] >= FG
    boxes = []
    for x0, y0, x1, y1 in wins:
        lab, m = ndimage.label(op[y0:y1, x0:x1], structure=np.ones((3, 3)))
        big = lab == 1 + int(np.argmax(np.bincount(lab.ravel())[1:]))
        yy, xx = np.nonzero(big)
        boxes.append((xx.min(), yy.min() + y0, xx.max() + 1, yy.max() + 1 + y0))
    bx0, bx1 = min(b[0] for b in boxes), max(b[2] for b in boxes)
    by0, by1 = min(b[1] for b in boxes), max(b[3] for b in boxes)
    H = MOM_H
    s = (by1 - by0) / H
    W = int(round((bx1 - bx0) / s))
    fire = [k for k, p in enumerate(pal) if p[0] > 150]                 # the rim's orange (the fire ramp)
    lum = B.LUM(pal)

    def pick(sh):
        lit = [k for k in fire if sh[k] >= 0.2]
        return max(lit, key=lambda k: sh[k]) if lit else int(np.argmax(sh))
    out = []
    for x0, y0, x1, y1 in wins:
        v, cov = vote_grid(raw, pal, (x0 + bx0, by0, x0 + bx1, by1), W, H, 0.35, pick)
        v, cov = v + v[::-1], (cov + cov[::-1]) / 2
        out.append(paint(v, cov, pal, 0.3, pick))
    del lum
    return out


def reread_fire():
    """r_fire from the draft: the band's body (rows where a tenth of the frame's width is drawn, over all frames) on
    22 rows, the frame's full width on 132 columns; the lightest colour holding a third of the drawn pixels (the white
    centre line and the flame tips), top / bottom votes pooled; 1 clear row above and below (24)."""
    raw, pal, wins = draft("r_fire")
    op = raw[..., 3] >= FG
    rows = np.zeros(op.shape[0])
    for x0, y0, x1, y1 in wins:
        rows = np.maximum(rows, op[:, x0:x1].mean(1))
    body = np.nonzero(rows >= 0.10)[0]
    by0, by1 = body.min(), body.max() + 1
    lum = B.LUM(pal)

    def pick(sh):
        for q in np.argsort(-lum):
            if sh[q] >= 0.33:
                return int(q)
        return int(np.argmax(sh))
    out = []
    for x0, y0, x1, y1 in wins:
        v, cov = vote_grid(raw, pal, (x0, by0, x1, by1), 132, 22, 0.35, pick)
        v, cov = v + v[::-1], (cov + cov[::-1]) / 2
        c = paint(v, cov, pal, 0.35, pick)
        out.append(np.pad(c, ((1, 1), (0, 0), (0, 0))))
    return out


REREAD = {"r_mom": reread_mom, "r_fire": reread_fire}
MOM_H = 60                       # the shadow's height in squares (wing tip to wing tip): an adult dragon, twice his size


def anchor(strip, kind):
    h, w = strip[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "left":
        return [0, (h - 1) / 2]
    low = max(int(np.nonzero(c[..., 3].any(1))[0].max()) for c in strip)
    return [(w - 1) / 2, low - kind[1]]


def build(table):
    out = {}
    for tag, (src, frames, spot) in table.items():
        n, kind, sym = SHEETS[src]
        strip = REREAD[src]() if src in REREAD else cells(src, n)
        B.check_cells(src, strip, sym)
        strip = [B.odd(c, sym) for c in strip]
        anc = anchor(strip, kind)
        out[tag] = []
        for k, ms in frames:
            if k == J.EMPTY:
                out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out[tag].append((J.place(strip[k], anc, [spot]), ms))
    return out


def check(tags):
    bad = []
    for name, frames in tags.items():
        for k, (a, _) in enumerate(frames):
            if a.shape[0] % 2 == 0 or a.shape[1] % 2 == 0:
                bad.append(f"{name} {k + 1}: even size {a.shape[:2]}")
            if name in TB_TAGS and not (a == a[::-1]).all():
                bad.append(f"{name} {k + 1}: not symmetric top to bottom")
            if name not in TB_TAGS and not (a == a[:, ::-1]).all():
                bad.append(f"{name} {k + 1}: not symmetric left to right")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game frames at 6x here")
    a = ap.parse_args()
    used = {v[0] for table in (FX, BIG) for v in table.values()}
    if used != set(SHEETS) or set(manifest()) != set(SHEETS):
        sys.exit(f"sheets not imported: {sorted(set(SHEETS) ^ used)} / {sorted(set(manifest()) ^ set(SHEETS))}")
    out, bad = [], []
    for sheet, table in (("league_smolder_fx", FX), ("league_smolder_big", BIG)):
        tags = build(table)
        bad += check(tags)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
        out.append(tags)
    for b in bad:
        print("BAD", b)
    if a.review:
        B.review(out, a.review)
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
