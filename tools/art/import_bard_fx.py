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
import json
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

# sheet -> (frames, anchor on the middle column: "core" (the drawing's middle), ("bottom", k): k 1x squares (times the
# sheet's SCALE) above the drawing's lowest row, "widest": the widest row of the last frame (a ground ring's middle),
# ("row", r): row r of the delivered cell, symmetry)
SHEETS = {
    "a_bolt": (4, "core", "tb"), "a_hit": (4, "core", "lr"), "p_meep": (4, "core", "tb"),
    "p_hit": (5, "core", "lr"), "q_bolt": (4, "core", "tb"), "q_hit": (5, "core", "lr"),
    "q_bind": (6, "core", "lr"), "w_shrine": (4, "core", "tb"), "w_land": (6, ("row", 25), "lr"),
    "e_door": (6, ("bottom", 0), "lr"), "e_ride": (4, ("bottom", 0), "lr"), "r_orb": (4, "core", "both"),
    "r_mark": (6, "widest", "lr"), "r_dome": (5, ("bottom", 5), "lr"), "r_lock": (6, ("bottom", 6), "lr"),
    "r_free": (4, "core", "lr"), "slow": (4, "core", "lr"), "haste": (4, ("row", 8), "lr"),
}
# R drawn bigger (the user, 2026-10-14: 「R的特效做大点」, with the zone League's size, r_r 26000 -> 36000): these sheets
# are read again from Codex's own drafts (raw/, its read-back's way: the drawing's bounds over all frames brought to
# its 1x extent times SCALE, every square the majority of the draft's opaque pixels snapped to the sheet's palette,
# mirrored squares voting together) - the ground ring and the dome with the zone, the orb with them, the bubble a unit
# tall
SCALE = {"r_orb": 1.4, "r_mark": 1.4, "r_dome": 1.4, "r_lock": 1.25, "r_free": 1.25,
         # the door a little taller than Bard, so it shows round him (z -1, behind him)
         "e_door": 1.5}
RAW = os.path.join(ROOT, "assets", "source", "bard", "codex_fx", "bard-fx")
# read again from Codex's drafts (the user: 「是不是codex的特效你没完全用啊 好怪啊」): its read-back (pixel_1x) cleared the
# stun ring's front and back (only two side bits left) and the door's starry tunnel, and thinned the travel sparkles to
# lines; and R's pictures, drawn bigger. The small hits and bolts keep Codex's read-back (cleaner than a new read)
REREAD = {"q_bind", "e_door", "e_ride"} | set(SCALE)
MARGIN = 2                      # clear squares round a re-read drawing
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
WAIST = (0, -4)
SOLES = (0, 11)                 # on the ground under a unit or a point
# the middle of R's bubble (its drawing's middle) where the bubble's is: its figure's feet (6 squares above its lowest row,
# times SCALE) on the soles
BUBBLE = (0, 11 - ((round(30 * SCALE["r_lock"]) - 1) / 2 - round(6 * SCALE["r_lock"])))
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
    # the add-on's portal at the wall (the user: 「你这个特效应该放在墙前面 LOL不就这样吗 现在还是看不出」): the door x2.5, well
    # taller than Bard, a buff picture behind him (z -1) while he stands at the wall's face - it opens and shimmers until he
    # goes through - and on the far side as he steps out (it closes)
    "e_portal": ("e_door", seq([0, 1, 2, 3, 2, 3, 2, 3], [40, 60, 120, 120, 120, 120, 120, 1000]), SOLES, 2.5),
    "e_portal_out": ("e_door", seq([2, 3, 2, 4, 5], [100, 100, 100, 60, 1000]), SOLES, 2.5),
    # R: the orb lobbed (r_travel 24 ticks = 400 ms) over its mark, the dome where it lands, every unit in it frozen
    # for r_t 150 ticks (2.5 s: the bubble forms, then holds), the bubble shattering when it ends
    "r_orb": ("r_orb", seq(range(4), [70] * 4), (0, 0)),
    "r_mark": ("r_mark", seq(range(6), [60, 60, 70, 70, 70, 70]), SOLES),
    # the dome stands over the zone for the whole stasis (r_t 150 ticks = 2.5 s; 0.4 s was missed in game: 「现在R好像
    # 不是用的这个特效？」): it lands (frames 1-3), its rim and its stars take turns (3 / 4), it fades (5)
    "r_dome": ("r_dome", seq([0, 1, 2] + [3, 2] * 4 + [4], [40, 60, 80] + [260] * 8 + [240]), SOLES),
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


BRIGHT = 200                    # a colour this light (0.3 R + 0.59 G + 0.11 B) is a core, a ray or a star


def LUM(pal):
    return pal @ np.array([0.3, 0.59, 0.11])


def BRIGHT_OF(pal):
    return LUM(pal) >= BRIGHT


def manifest():
    with open(G.lp(os.path.join(RAW, "manifest.json")), encoding="utf-8") as f:
        return {a["tag"]: a for a in json.load(f)["assets"]}


def reread(name, scale, sym):
    """The sheet read again from Codex's draft: the drawing's bounds over all frames brought to the prompt's size
    (manifest `size`) times `scale`, MARGIN clear squares round it."""
    a = manifest()[name]
    raw = np.asarray(Image.open(G.lp(os.path.join(RAW, "raw", a["raw_file"]))).convert("RGBA")).astype(float)
    pal = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in a["palette"]], float)
    n = a["frames"]
    tw = raw.shape[1] / n
    op = raw[..., 3] > 128
    # each frame in its own equal tile; pieces of the next frames' drawings reaching into a tile (touching its left or
    # right side) are not its own
    from scipy import ndimage
    b = []
    for k in range(n):
        x0, x1 = int(round(k * tw)), int(round((k + 1) * tw))
        lab, m = ndimage.label(op[:, x0:x1], structure=np.ones((3, 3)))
        edge = set(np.unique(lab[:, 0])) | set(np.unique(lab[:, -1]))
        area = np.bincount(lab.ravel())
        for i in edge - {0}:
            if area[i] < 0.03 * area[1:].sum():
                op[:, x0:x1][lab == i] = False
        yy, xx = np.nonzero(op[:, x0:x1])
        b.append((xx.min(), xx.max() + 1, yy.min(), yy.max() + 1))
    gx0, gx1 = min(x[0] for x in b), max(x[1] for x in b)
    gy0, gy1 = min(x[2] for x in b), max(x[3] for x in b)
    size = [int(v) for v in a["size"].replace("×", " ").split()]
    sw, sh = size if len(size) == 2 else size * 2
    W0, H0 = round(sw * scale), round(sh * scale)            # the prompt's size in game px (the read-back's extent)
    sx, sy = (gx1 - gx0) / W0, (gy1 - gy0) / H0
    W, H = W0 + 2 * MARGIN, H0 + 2 * MARGIN
    snap = ((raw[..., None, :3] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    cells = []
    for k in range(n):
        votes = np.zeros((H, W, len(pal)))
        cover = np.zeros((H, W))
        for j in range(H):
            y0, y1 = max(0, int(round(gy0 + (j - MARGIN) * sy))), max(0, int(round(gy0 + (j + 1 - MARGIN) * sy)))
            for i in range(W):
                x0 = max(0, int(round(k * tw + gx0 + (i - MARGIN) * sx)))
                x1 = max(0, int(round(k * tw + gx0 + (i + 1 - MARGIN) * sx)))
                o = op[y0:y1, x0:x1]
                if o.size:
                    cover[j, i] = o.mean()
                    if o.any():
                        votes[j, i] = np.bincount(snap[y0:y1, x0:x1][o], minlength=len(pal))
        if sym in ("lr", "both"):
            votes, cover = votes + votes[:, ::-1], (cover + cover[:, ::-1]) / 2
        if sym in ("tb", "both"):
            votes, cover = votes + votes[::-1], (cover + cover[::-1]) / 2
        c = np.zeros((H, W, 4), np.uint8)
        tot = votes.sum(-1)
        share = votes / np.maximum(tot, 1)[..., None] * cover[..., None]       # of the square's whole area
        lit = share[..., BRIGHT_OF(pal)].sum(-1)
        for j in range(H):
            for i in range(W):
                if lit[j, i] >= 0.2:            # a bright core or a thin ray: the brightest colour with a tenth or more
                    ids = [q for q in np.argsort(-LUM(pal)) if share[j, i, q] >= 0.1 and LUM(pal)[q] >= BRIGHT]
                    best = ids[0] if ids else int(np.argmax(np.where(BRIGHT_OF(pal), share[j, i], -1)))
                elif cover[j, i] >= 0.45:       # else the commonest, a brighter one from 35%
                    best = int(np.argmax(share[j, i]))
                    for q in np.argsort(-LUM(pal)):
                        if share[j, i, q] / max(cover[j, i], 1e-9) >= 0.35:
                            if LUM(pal)[q] > LUM(pal)[best]:
                                best = int(q)
                            break
                else:
                    continue
                c[j, i, :3] = pal[best].astype(np.uint8)
                c[j, i, 3] = 255
        cells.append(c)
    return cells


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


def anchor(strip, kind, scale):
    h, w = strip[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind[0] == "row":
        return [(w - 1) / 2, kind[1]]
    if kind == "widest":
        rows = (strip[-1][..., 3] > 0).sum(1)
        return [(w - 1) / 2, int(np.argmax(rows))]
    return [(w - 1) / 2, h - 1 - MARGIN - round(kind[1] * scale)]


def build(table):
    out = {}
    for tag, (src, frames, spot, *own) in table.items():
        n, kind, sym = SHEETS[src]
        scale = own[0] if own else SCALE.get(src, 1.0)
        if src in REREAD:
            strip = reread(src, scale, sym)
        else:
            strip = cells(src, n)
        check_cells(src, strip, sym)
        strip = [odd(c, sym) for c in strip]
        anc = anchor(strip, kind, scale)
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
            if name in ("e_door_out", "q_slow", "e_haste", "e_portal_out"):
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
    used = {v[0] for table in (FX, BIG) for v in table.values()}
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
