#!/usr/bin/env python3
"""Import Malzahar's effects (assets/source/malzahar/PROMPTS_FX.md, 13 sheets) as the game sheets league_malzahar_fx and
league_malzahar_big, from Codex's step-3 delivery (assets/source/malzahar/codex_fx/malzahar-fx) - league_bard's way
(tools/art/import_bard_fx.py).

    python tools/art/import_malzahar_fx.py [--review out.png]

Codex delivered every sheet at game size (pixel_1x/: one game pixel a square, a row of equal cells, hard alpha, the
prompt's ramps, every cell symmetric), so most sheets are only cut, checked, given their anchor and placed. Two are
read again from Codex's own drafts (raw/): its read-back turned the voidlings to mud at 9 squares (their shells, eyes
and claws gone) and cut the shield's slanted arcs with the empty-middle box. The voidlings are read 1.3 times the
prompt's size (one scale both ways: 12 squares a voidling, eyes and claws kept), the shield's ring brought to the
prompt's 34 x 44 (its motes kept round it).
Even cells are made odd across their mirror axis (the column left of it doubled; for the flying ones the row above it):
a game frame has the pivot's pixel in its middle. a_bolt and e_bolt are symmetric top to bottom (the client turns a
flying picture with its flight), everything else left to right (the client never mirrors an effect picture on the red
side); check() asserts it on the game frames.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. The hits on the upper body
(0, -12); the vision's wisps round it; the gate, the voidlings' feet, the tentacles' roots, the rifts' feet and the
null zone's middle on the soles; the shield's lowest row 1 over the ground round Malzahar (he floats: boots 2 over it,
head 31 over the pivot at hd.rs SIZES 1.15).
Times from the kit (tools/kit/build_malzahar.py P, 60 ticks a second).
R's beam (the user: 「大招没连接线啊」): r_link, a 16 px link of the chain flying from his hands to the grasped
champion (tools/kit/build_malzahar.py r_lp / r_lspeed / r_ly), cut from Codex's own beam in q_rift frame 5 (link()).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import import_bard_fx as B  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "malzahar", "codex_fx", "malzahar-fx")
SRC = os.path.join(RAW, "pixel_1x")
MOD = os.path.join(ROOT, "league")

# sheet -> (frames, anchor on the middle column: "core" (the cell's middle), ("bottom", k): k squares above the
# drawing's lowest row, symmetry)
SHEETS = {
    "a_bolt": (4, "core", "tb"), "a_hit": (4, "core", "lr"), "e_bolt": (4, "core", "tb"),
    "e_hit": (5, "core", "lr"), "e_mark": (4, "core", "lr"), "w_spawn": (4, "core", "lr"),
    "w_swarm": (4, ("bottom", 0), "lr"), "w_bite": (3, "core", "lr"), "q_rift": (6, ("bottom", 0), "lr"),
    "q_hit": (4, "core", "lr"), "r_grasp": (4, ("bottom", 0), "lr"), "r_pool": (8, "core", "lr"),
    "p_shift": (4, ("bottom", 0), "lr"), "r_link": (4, "core", "tb"),
}
# read again from the drafts: (the drawing's size in squares the read maps to, "ring": the largest piece's bounds
# brought to that size (both ways) / "all": every piece's bounds, one scale (the width's), clear squares round it,
# the least drawn share a square needs, the vote)
REREAD = {"w_swarm": ((round(34 * 1.3), None), "all", 2, 0.35, "body"),
          "p_shift": ((34, 44), "ring", 4, 0.25, "light")}
FG = 12                          # a draft pixel this light (its largest channel) is drawn; black is the background key
HIT = (0, -12)                   # a hit on the upper body of a 36-44 px unit
SOLES = (0, 11)                  # on the ground under a unit or a point
SHELL = (0, 10)                  # the shield's lowest row: 1 over the ground under Malzahar
LINK_LEAD = 5                    # R's beam hidden its first ticks (r_link below)
seq = J.seq
flight = J.flight

# R's zone: r_zone_t 300 ticks = 5 s - it opens (1-2), its swirl loops (3-6) 7 times, it fades (7-8)
POOL = seq([0, 1] + [2, 3, 4, 5] * 7 + [6, 7], [80, 100] + [160] * 28 + [150, 190])
FX = {
    # the attack: 52 px at 4.5 a tick (~12 ticks), homing: drawn for twice that; E's vision 65 px at 5 a tick
    "a_bolt": ("a_bolt", flight(4, 60, 360, lead=2), (0, 0)),
    "a_hit": ("a_hit", seq(range(4), [40, 50, 60, 70]), HIT),
    "e_bolt": ("e_bolt", flight(4, 60, 420, lead=2), (0, 0)),
    "e_hit": ("e_hit", seq(range(5), [40, 50, 60, 70, 80]), HIT),
    # played every 60 ticks while the vision burns (e_t 240): 4 frames a second
    "e_mark": ("e_mark", seq(range(4), [250] * 4), HIT),
    "w_spawn": ("w_spawn", seq(range(4), [60, 90, 100, 90]), SOLES),
    # played every 60 ticks while they bite (w_t 240)
    "w_swarm": ("w_swarm", seq(range(4), [250] * 4), SOLES),
    "w_bite": ("w_bite", seq(range(3), [50, 60, 80]), HIT),
    "q_hit": ("q_hit", seq(range(4), [40, 50, 60, 70]), HIT),
    # the shield while it holds (a buff picture, looped)
    "p_shift": ("p_shift", seq(range(4), [120] * 4), SHELL),
    # R's beam: each link flies from over his pivot to the champion (4 px a tick: ~13-18 ticks), hidden for the first
    # LINK_LEAD ticks (its first tick points it up, and it starts inside him: his hands are 20 px out)
    "r_link": ("r_link", flight(4, 50, 350, lead=LINK_LEAD), (0, 0)),
}
BIG = {
    # Q: the rifts open over q_lag 24 ticks (400 ms: frames 1-4), the beams meet as the damage lands (frame 5)
    "q_rift": ("q_rift", seq(range(6), [80, 100, 110, 110, 120, 150]), SOLES),
    # R: the hands round him, played by every channel wave (r_p 15 ticks = 250 ms)
    "r_grasp": ("r_grasp", seq(range(4), [60, 60, 65, 65]), SOLES),
    "r_pool": ("r_pool", POOL, SOLES),
}
TB_TAGS = {"a_bolt", "e_bolt", "r_link"}
# R's beam from Q's: q_rift frame 5's beam between the flash and the rift (its rows 13-15: the white core, the lit
# edge, the dark rim; columns 9-16: one period of its pattern), the core's lower half mirrored up (symmetric top to
# bottom, as a flying picture must be); 4 frames, the pattern 2 px further along each (flowing on to the champion)
LINK_ROWS, LINK_COLS, LINK_LEN = (13, 16), (9, 17), 17


def manifest():
    with open(G.lp(os.path.join(RAW, "manifest.json")), encoding="utf-8") as f:
        return {a["tag"]: a for a in json.load(f)["assets"]}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"malzahar_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"malzahar_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    return [a[:, k * w:(k + 1) * w].copy() for k in range(n)]


def reread(name):
    """The sheet read again from Codex's draft (its manifest's frame windows): the drawing brought to REREAD's size,
    every square voted from the draft's drawn pixels snapped to the sheet's palette, mirrored squares voting together."""
    from scipy import ndimage
    (W0, H0), bound, margin, need, vote = REREAD[name]
    a = manifest()[name]
    raw = np.asarray(Image.open(G.lp(os.path.join(RAW, "raw", f"malzahar_fx_{name}.png"))).convert("RGB")).astype(float)
    pal = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in a["palette"]], float)
    op = raw.max(-1) >= FG
    snap = ((raw[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    wins = [[int(round(v)) for v in w] for w in a["source_frame_viewports"]]
    b = []
    for x0, y0, x1, y1 in wins:
        o = op[y0:y1, x0:x1]
        if bound == "ring":
            lab, m = ndimage.label(o, structure=np.ones((3, 3)))
            o = lab == 1 + int(np.argmax(np.bincount(lab.ravel())[1:]))
        yy, xx = np.nonzero(o)
        b.append((x0 + xx.min(), x0 + xx.max() + 1, y0 + yy.min(), y0 + yy.max() + 1, x0))
    # one box for all frames, from each frame's own window (the drawings stand at the same place in their windows)
    gx0 = min(x[0] - x[4] for x in b)
    gx1 = max(x[1] - x[4] for x in b)
    gy0, gy1 = min(x[2] for x in b), max(x[3] for x in b)
    sx = (gx1 - gx0) / W0
    if H0 is None:
        H0 = int(round((gy1 - gy0) / sx))
    sy = (gy1 - gy0) / H0
    W, H = W0 + 2 * margin, H0 + 2 * margin
    lum = B.LUM(pal)
    out = []
    for x0, y0, x1, y1 in wins:
        votes = np.zeros((H, W, len(pal)))
        cover = np.zeros((H, W))
        for j in range(H):
            ya = max(0, int(round(gy0 + (j - margin) * sy)))
            yb = max(0, int(round(gy0 + (j + 1 - margin) * sy)))
            for i in range(W):
                xa = min(x1, max(x0, int(round(x0 + gx0 + (i - margin) * sx))))
                xb = min(x1, max(x0, int(round(x0 + gx0 + (i + 1 - margin) * sx))))
                o = op[ya:yb, xa:xb]
                if o.size:
                    cover[j, i] = o.mean()
                    if o.any():
                        votes[j, i] = np.bincount(snap[ya:yb, xa:xb][o], minlength=len(pal))
        votes, cover = votes + votes[:, ::-1], (cover + cover[:, ::-1]) / 2
        share = votes / np.maximum(votes.sum(-1), 1)[..., None]
        c = np.zeros((H, W, 4), np.uint8)
        for j in range(H):
            for i in range(W):
                if cover[j, i] < need:
                    continue
                s = share[j, i]
                best = int(np.argmax(s))
                if vote == "light":
                    # a light's rim and its arcs: the lightest colour with a third of the drawn pixels or more
                    for q in np.argsort(-lum):
                        if s[q] >= 0.3:
                            best = int(q)
                            break
                else:
                    # a creature: the commonest colour; a glowing eye (the magenta ramp's three lightest) from a
                    # quarter
                    eyes = [q for q, h in enumerate(a["palette"]) if h.upper() in ("#FFE3F4", "#FF86D2", "#EE3AA6")]
                    lit = [q for q in eyes if s[q] >= 0.25]
                    if lit:
                        best = max(lit, key=lambda q: s[q])
                c[j, i, :3] = pal[best].astype(np.uint8)
                c[j, i, 3] = 255
        out.append(c)
    return out


def link():
    c = cells("q_rift", SHEETS["q_rift"][0])[4]
    half = c[LINK_ROWS[0]:LINK_ROWS[1], LINK_COLS[0]:LINK_COLS[1]]
    tile = np.concatenate([half[:0:-1], half], 0)
    per = tile.shape[1]
    out = []
    for k in range(4):
        cols = [(i - 2 * k) % per for i in range(LINK_LEN)]
        out.append(tile[:, cols].copy())
    return out


def anchor(strip, kind):
    h, w = strip[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    low = max(int(np.nonzero(c[..., 3].any(1))[0].max()) for c in strip)
    return [(w - 1) / 2, low - kind[1]]


def build(table):
    out = {}
    for tag, (src, frames, spot) in table.items():
        n, kind, sym = SHEETS[src]
        strip = link() if src == "r_link" else reread(src) if src in REREAD else cells(src, n)
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
    if used != set(SHEETS) or set(manifest()) != set(SHEETS) - {"r_link"}:
        sys.exit(f"sheets not imported: {sorted(set(SHEETS) ^ used)}")
    out, bad = [], []
    for sheet, table in (("league_malzahar_fx", FX), ("league_malzahar_big", BIG)):
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
