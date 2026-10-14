#!/usr/bin/env python3
"""Import Bard's effects (assets/source/bard/PROMPTS_FX.md, 18 sheets) as the game sheets league_bard_fx and
league_bard_big, from Codex's step-3 delivery - the user, 2026-10-14: 「用这个特效包」, in place of the ones drawn in
code (tools/art/fx_bard.py, acf202cb, removed).

    python tools/art/import_bard_fx.py [--review out.png]

Codex delivered every sheet at game size as well (assets/source/bard/codex_fx/bard-fx/pixel_1x/, one game pixel a
square, a row of equal cells, hard alpha, the prompt's ramps, every cell symmetric), so nothing is resampled here
(tools/art/import_irelia.py's way): each cell is cut out, checked, given its anchor and placed on its spot.
The cells are an even number of squares across (the flying ones also tall), so their mirror axis lies between two
squares; a game frame has the pivot's pixel in its middle (odd sizes, art-spec), so the column left of the axis is
doubled (for the flying pictures the row above it: import_kassadin.mirror_lr's way) - the picture one square wider,
still symmetric.
Red side and blue side alike: the client never mirrors an effect picture and turns a flying one with its flight, so
a_bolt, p_meep, q_bolt and w_shrine are symmetric top to bottom, r_orb both ways, everything else left to right
(check() asserts it on the game frames).
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. The anchors are the cells' own
rows: a hit's middle on the upper body (0, -12), the stun ring's middle on the waist (0, -4), the shrine's pedestal,
the door's foot and the travel streaks' foot on the soles, the ground rings' middles (R's mark, the dome's base, the
slow) on the ground, the frozen figure's feet on the soles and the shattering bubble's middle where the bubble's was.
Times from the kit (tools/kit/build_bard.py P, 60 ticks a second).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "bard", "codex_fx", "bard-fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# sheet -> (frames, anchor: "core" (the middle) or a row of the delivered cell (on its middle column), symmetry)
SHEETS = {
    "a_bolt": (4, "core", "tb"), "a_hit": (4, "core", "lr"), "p_meep": (4, "core", "tb"),
    "p_hit": (5, "core", "lr"), "q_bolt": (4, "core", "tb"), "q_hit": (5, "core", "lr"),
    "q_bind": (6, 7, "lr"), "w_shrine": (4, "core", "tb"), "w_land": (6, 25, "lr"),
    "e_door": (6, 30, "lr"), "e_ride": (4, 21, "lr"), "r_orb": (4, "core", "both"),
    "r_mark": (6, 11, "lr"), "r_dome": (5, 33, "lr"), "r_lock": (6, 24, "lr"),
    "r_free": (4, 17, "lr"), "slow": (4, "core", "lr"), "haste": (4, 8, "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
WAIST = (0, -4)
SOLES = (0, 11)                 # on the ground under a unit or a point
BUBBLE = (0, 3)                 # the middle of R's bubble (its figure's feet on the soles)
seq = J.seq
flight = J.flight

FX = {
    # the attack: 52 px at 5 a tick (~10 ticks), homing: drawn for twice that; the Meep at 4.5 a tick
    "a_bolt": ("a_bolt", flight(4, 60, 360, lead=2), (0, 0)),
    "a_hit": ("a_hit", seq(range(4), [40, 50, 60, 70]), HIT),
    "p_meep": ("p_meep", flight(4, 70, 420, lead=2), (0, 0)),
    "p_hit": ("p_hit", seq(range(5), [40, 50, 60, 70, 80]), HIT),
    # Q: 95 px at 6 a tick (16 ticks); the stun's ring for the stun (q_stun 90 ticks = 1.5 s): it snaps shut, holds,
    # fades
    "q_bolt": ("q_bolt", flight(4, 60, 300, lead=1), (0, 0)),
    "q_hit": ("q_hit", seq(range(5), [40, 50, 60, 70, 80]), HIT),
    "q_bind": ("q_bind", seq(range(6), [220, 256, 256, 256, 256, 256]), WAIST),
    # W: the shrine to an ally within 50 px at 4 a tick; its heal at his feet
    "w_shrine": ("w_shrine", flight(4, 80, 480, lead=2), (0, 0)),
    "w_land": ("w_land", seq(range(6), [60, 80, 100, 110, 110, 90]), SOLES),
    "e_ride": ("e_ride", seq(range(4), [60, 80, 80, 80]), SOLES),
    # the buffs, looped while they last
    "p_slow": ("slow", seq(range(4), [100] * 4), SOLES),
    "q_slow": ("slow", seq(range(4), [100] * 4), SOLES),
    "w_haste": ("haste", seq(range(4), [90] * 4), SOLES),
    "e_haste": ("haste", seq(range(4), [90] * 4), SOLES),
}
BIG = {
    # E: the door opens, holds while he steps in (e_wind 9 + e_tick 15 ticks = 400 ms), closes; again where he comes out
    "e_door": ("e_door", seq(range(6), [50, 60, 150, 150, 60, 50]), SOLES),
    "e_door_out": ("e_door", seq(range(6), [50, 60, 150, 150, 60, 50]), SOLES),
    # R: the orb lobbed (r_travel 24 ticks = 400 ms) over its mark, the dome where it lands, every unit in it frozen
    # for r_t 150 ticks (2.5 s: the bubble forms, then holds), the bubble shattering when it ends
    "r_orb": ("r_orb", seq(range(4), [70] * 4), (0, 0)),
    "r_mark": ("r_mark", seq(range(6), [60, 60, 70, 70, 70, 70]), SOLES),
    "r_dome": ("r_dome", seq(range(5), [40, 60, 80, 100, 120]), SOLES),
    "r_lock": ("r_lock", seq(range(6), [100, 480, 480, 480, 480, 480]), SOLES),
    "r_free": ("r_free", seq(range(4), [50, 60, 70, 80]), BUBBLE),
}
TB_TAGS = {"a_bolt", "p_meep", "q_bolt", "w_shrine"}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"bard_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"bard_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    return [a[:, k * w:(k + 1) * w].copy() for k in range(n)]


def check_cells(name, strip, sym):
    """The delivery's symmetry, cell by cell, before anything is moved."""
    for k, c in enumerate(strip):
        if sym in ("lr", "both") and not (c == c[:, ::-1]).all():
            sys.exit(f"bard_fx_{name} cell {k + 1} is not symmetric left to right")
        if sym in ("tb", "both") and not (c == c[::-1]).all():
            sys.exit(f"bard_fx_{name} cell {k + 1} is not symmetric top to bottom")


def odd(c, sym):
    """An even cell made odd across its mirror axis: the column (row) left of (above) the axis doubled."""
    if sym in ("lr", "both") and c.shape[1] % 2 == 0:
        k = c.shape[1] // 2 - 1
        c = np.concatenate([c[:, :k + 1], c[:, k:k + 1], c[:, k + 1:]], 1)
    if sym in ("tb", "both") and c.shape[0] % 2 == 0:
        k = c.shape[0] // 2 - 1
        c = np.concatenate([c[:k + 1], c[k:k + 1], c[k + 1:]], 0)
    return c


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, kind]


def build(table):
    out = {}
    for tag, (src, frames, spot) in table.items():
        n, kind, sym = SHEETS[src]
        strip = cells(src, n)
        check_cells(src, strip, sym)
        strip = [odd(c, sym) for c in strip]
        anc = anchor(strip[0], kind)
        out[tag] = []
        for k, ms in frames:
            if k == J.EMPTY:
                out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out[tag].append((J.place(strip[k], anc, [spot]), ms))
    return out


def check(tags):
    """The game frames: odd sizes, the flying pictures symmetric top to bottom (r_orb both ways), the rest left to
    right about the pivot's column."""
    bad = []
    for name, frames in tags.items():
        for k, (a, _) in enumerate(frames):
            if a.shape[0] % 2 == 0 or a.shape[1] % 2 == 0:
                bad.append(f"{name} {k + 1}: even size {a.shape[:2]}")
            if (name in TB_TAGS or name == "r_orb") and not (a == a[::-1]).all():
                bad.append(f"{name} {k + 1}: not symmetric top to bottom")
            if name not in TB_TAGS and not (a == a[:, ::-1]).all():
                bad.append(f"{name} {k + 1}: not symmetric left to right")
    return bad


def review(sheets, path, z=6):
    """Every tag's frames (the empty first ticks left out) at z on the arena's colour."""
    rows = []
    for tags in sheets:
        for name, frames in tags.items():
            if name in ("e_door_out", "q_slow", "e_haste"):
                continue
            seen, fr = set(), []
            for a, _ in frames:
                key = (a.shape, a.tobytes())
                if a[..., 3].any() and key not in seen:
                    seen.add(key)
                    fr.append(a)
            rows.append((name, fr))
    W = max(sum(f.shape[1] + 2 for f in fr) for _, fr in rows) * z + 90
    H = sum(max(f.shape[0] for f in fr) * z + 6 for _, fr in rows)
    img = Image.new("RGBA", (W, H), (104, 112, 72, 255))
    d = ImageDraw.Draw(img)
    y = 0
    for name, fr in rows:
        d.text((4, y + 2), name, fill=(255, 255, 255, 255))
        x = 90
        hh = max(f.shape[0] for f in fr)
        for f in fr:
            img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST),
                                (x, y + (hh - f.shape[0]) * z // 2))
            x += (f.shape[1] + 2) * z
        y += hh * z + 6
    img.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game frames at 6x here")
    a = ap.parse_args()
    used = {src for table in (FX, BIG) for src, _, _ in table.values()}
    if used != set(SHEETS):
        sys.exit(f"sheets not imported: {sorted(set(SHEETS) - used)}")
    out = []
    bad = []
    for sheet, table in (("league_bard_fx", FX), ("league_bard_big", BIG)):
        tags = build(table)
        bad += check(tags)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
        out.append(tags)
    for b in bad:
        print("BAD", b)
    if a.review:
        review(out, a.review)
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
