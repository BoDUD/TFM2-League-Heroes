#!/usr/bin/env python3
"""Import Gromp's effects (assets/source/gromp/PROMPTS_FX.md: 15 pictures and 3 skill icons) as the tft pack's sheets
tft_gromp_fx and tft_gromp_big and its icons.

    python tools/art/import_gromp_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/gromp/codex_fx/gromp_fx: pixel_1x/gromp_fx_<name>.png, one row of
equal frames at game size; manifest.json's effects list each one's frames, cell_1x, its raw draft's source_layout
(columns x rows of drawn frames) and source_cell_trim; raw/ its drafts; 64 px icons). Every frame is cut from pixel_1x
as delivered (alpha 0 / 255) and placed as the kit plays it (import_murkwolf_fx.py's way): spots are game px from the
pivot (x forward, y down); a unit's soles are 11 under it. Every picture is checked symmetric left to right, the
flying ones (a_spit, q_bubble, e_glob) top to bottom, pointing right (they turn with their flight).
RECUT (cut again from the raw draft, each square the commonest colour of the delivered strip's palette and the
prompt's ramps among its raw pixels, alpha by majority, the left half mirrored onto the right; the drawings' shared box
centred and fitted to the cell):
  r_cast  84 x 50: Codex kept the prompt's empty body (62 x 32 at the bottom of an 84 x 44 cell) by deleting every square
          there, which cut its belch arch into boxes; the raw arch rises over the body and comes down beside it, so a
          cell 6 rows taller holds it whole and the body stays clear but for the arch's crest above its back.
  q_poison 22 x 40: its bubbles voted down to single squares, and at the raw's own scale still to one or two: each
          green blob Codex placed is stamped as a bubble (BUBBLE: a mid-green rim, a light body, a near-white glint;
          3 x 3, the smallest 2 x 2) where it stands, the purple wisp over the head kept.
Anchors: the hits on the struck body (the cell's middle, HIT); the projectiles on their own point (FLY); the burst,
the slime and the fog on the ground where they land or lie (SOLES: a ground point's view is drawn at a unit's pivot);
the belch and Purple Buff round its body (BODY: the design's middle is 3 game px ahead of its standing point); the
poison and the slows on the unit that carries them (SOLES).
Icons: Codex's 64 px icons were its 1254 px tiles voted down into mud (skill2 a field of noise); brought to 64 x 64 again
from the raw tiles with LANCZOS (the Raptor, Sohm, Terra, Sentinel and Murk Wolf way).
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import pack_gromp_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gromp", "codex_fx", "gromp_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
FLY = (0, 0)                    # a projectile's own point
SOLES = (0, 11)                 # on the ground under a unit (or under a ground point)
BODY = (3, 11)                  # under the middle of its body (3 game px ahead of its standing point), on its soles
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped
EDGE_STRIP = 3                  # and parts within this many columns of a side and narrower than it
EDGE_KEEP = {"p_ap", "q_poison", "r_slow", "r_cast", "q_burst", "e_land", "r_fog"}   # drawn out at the sides on purpose
# name -> the cell (game px) to cut again from the raw draft
RECUT = {"r_cast": (84, 50), "q_poison": (22, 40)}
# q_poison's bubble stamps: R rim, L body, W glint (pack_gromp_fx.TOXIC's shades 3, 2 and 1)
BUBBLE = {3: ("RLR", "LWL", "RLR"), 2: ("WL", "LR")}


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core", "foot" or a row, frames with ms, spots)
FX = {
    # Toxic Spit: the glob in flight, the splat on the struck
    "a_spit": ("core", loop(4, 60), [FLY]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Belchy Bubble: the bubble in flight, its pop on the first struck, the burst where it stopped, the poisoned
    "q_bubble": ("core", loop(4, 70), [FLY]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "q_burst": ("foot", seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES]),
    "q_poison": ("foot", loop(6, 90), [SOLES]),
    # Slime Swamp: the glob in flight, its splash on landing, the pool (replayed every e_show ticks), the stuck
    "e_glob": ("core", loop(4, 70), [FLY]),
    "e_land": ("foot", seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "e_pool": ("foot", loop(6, 50), [SOLES]),
    "e_slow": ("foot", loop(6, 100), [SOLES]),
    # Swamp Belch: the shockwave round it, the blast on the struck, the fog (replayed every r_show ticks), the choked
    "r_cast": ("foot", seq(range(6), [60, 70, 80, 90, 100, 100]), [BODY]),
    "r_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "r_fog": ("foot", loop(6, 50), [SOLES]),
    "r_slow": ("foot", loop(6, 100), [SOLES]),
    # Purple Buff: the rune above its back while its stacks hold
    "p_ap": ("foot", loop(6, 110), [BODY]),
}
ICONS = {"icon_skill": "tft_gromp_skill", "icon_skill2": "tft_gromp_skill2", "icon_ult": "tft_gromp_ult"}


def ramps():
    cols = []
    for ramp in (PK.TOXIC, PK.SWAMP, PK.SLIME):
        cols += [[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in ramp.split(", ")]
    return np.array(cols, float)


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        m = json.load(f)
    return {e["file"][len("gromp_fx_"):-4]: e for e in m["effects"]}


def palette(strip):
    return np.unique(np.concatenate([strip[strip[..., 3] >= 128][:, :3].astype(float), ramps()]), axis=0)


def tiles_of(name, e):
    """The raw draft's frames: its source_layout's grid (columns x rows, read row by row), each cell trimmed by
    source_cell_trim (fractions x0, y0, x1, y1 of the cell)."""
    raw = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"gromp_fx_{name}.png"))).convert("RGBA"))
    cols, rows = e["source_layout"]
    tx0, ty0, tx1, ty1 = e.get("source_cell_trim") or (0, 0, 1, 1)
    cw, ch = raw.shape[1] / cols, raw.shape[0] / rows
    out = []
    for k in range(e["frames"]):
        c, r = k % cols, k // cols
        x0, y0 = c * cw, r * ch
        out.append(raw[int(y0 + ty0 * ch):int(y0 + ty1 * ch), int(x0 + tx0 * cw):int(x0 + tx1 * cw)])
    return out


def vote(t, ox, oy, k, w, h, pal):
    """A w x h read of tile t from (ox, oy) at k raw px a square: the commonest palette colour, alpha by majority."""
    n = max(1, int(k))
    out = np.zeros((h, w, 4), np.uint8)
    for j in range(h):
        for i in range(w):
            ya, xa = int(oy + j * k), int(ox + i * k)
            if ya + n <= 0 or xa + n <= 0:
                continue
            win = t[max(0, ya):max(0, ya) + n, max(0, xa):max(0, xa) + n].reshape(-1, 4)
            if len(win) == 0:
                continue
            on = win[win[:, 3] >= 128]
            if len(on) * 2 < len(win):
                continue
            idx = np.argmin(((on[:, None, :3].astype(float) - pal[None]) ** 2).sum(-1), axis=1)
            out[j, i, :3] = pal[np.bincount(idx).argmax()]
            out[j, i, 3] = 255
    return out


def recut(name, strip, e):
    """An effect cut again from its raw draft into RECUT[name]'s cell, mirrored about the tiles' middle column, the
    drawings' shared box centred and fitted (its lowest row on the cell's bottom). -> a new strip."""
    w, h = RECUT[name]
    tiles = tiles_of(name, e)
    pal = palette(strip)
    boxes = [np.nonzero(t[..., 3] >= 128) for t in tiles]
    xc = tiles[0].shape[1] / 2
    y1 = max(b[0].max() for b in boxes) + 1
    y0 = min(b[0].min() for b in boxes)
    half = max(max(abs(b[1].min() - xc), abs(b[1].max() + 1 - xc)) for b in boxes)
    k = max(2 * half / w, (y1 - y0) / h)
    out = np.zeros((h, w * len(tiles), 4), np.uint8)
    for f, t in enumerate(tiles):
        c = vote(t, xc - w / 2 * k, y1 - h * k, k, w, h, pal)
        c[:, w - w // 2:] = c[:, :w // 2][:, ::-1]
        out[:, f * w:(f + 1) * w] = c
    print(f"{name}: recut at {k:.1f} raw px a square")
    return out


def bubbles(a, w):
    """q_poison: each green blob of every cell stamped as a bubble (BUBBLE) about its middle, mirrored as before."""
    tox = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in PK.TOXIC.split(", ")]
    col = {"W": tox[0], "L": tox[1], "R": tox[2]}
    r_, g_, b_ = (a[..., i].astype(int) for i in range(3))
    green = (a[..., 3] > 0) & (g_ > r_) & (g_ > b_ + 40)
    out = a.copy()
    out[green] = 0
    for f in range(a.shape[1] // w):
        m = green[:, f * w:(f + 1) * w]
        lb, n = ndimage.label(m, structure=np.ones((3, 3), bool))
        for j in range(1, n + 1):
            ys, xs = np.nonzero(lb == j)
            size = 3 if len(ys) >= 2 else 2
            top, left = int(round(ys.mean() - (size - 1) / 2)), int(round(xs.mean() - (size - 1) / 2))
            for dy, rw in enumerate(BUBBLE[size]):
                for dx, c in enumerate(rw):
                    y, x = top + dy, left + dx
                    if 0 <= y < a.shape[0] and 0 <= x < w:
                        out[y, f * w + x, :3], out[y, f * w + x, 3] = col[c], 255
        c = out[:, f * w:(f + 1) * w]
        c[:, w - w // 2:] = c[:, :w // 2][:, ::-1]
    return out


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    e = m[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"gromp_fx_{name}.png"))).convert("RGBA")).copy()
    w, h = e["cell_1x"]
    if name in RECUT:
        a = recut(name, a, e)
        w, h = RECUT[name]
        if name == "q_poison":
            a = bubbles(a, w)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    if a.shape[0] != h or a.shape[1] != w * e["frames"]:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {e['frames']} cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(e["frames"])]
    for c in ([] if name in EDGE_KEEP or name in FLYING else out):   # bits of a neighbour at the cell's sides
        op = c[..., 3] > 0
        lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
        for j in range(1, n + 1):
            part = lb == j
            side = part[:, :EDGE_STRIP].any() or part[:, -EDGE_STRIP:].any()
            thin = np.ptp(np.nonzero(part.any(0))[0]) < EDGE_STRIP
            if side and (part.sum() < EDGE_SPECK or thin):
                c[part] = 0
    for k, c in enumerate(out):
        flip = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == flip).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric " + ("top to bottom" if name in FLYING else "left to right"))
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "foot":
        return [(w - 1) / 2, h - 1]
    return [(w - 1) / 2, kind]


def icon(name):
    """Codex's raw 1254 px icon tile -> 64 x 64 (LANCZOS): its own 64 px cut voted into mud."""
    im = Image.open(lp(os.path.join(SRC, "raw", f"gromp_{name}.png"))).convert("RGB")
    return im.resize((64, 64), Image.LANCZOS).convert("RGBA")


def review(allc, path):
    Z = 6
    rows = []
    for cs in allc.values():
        W = sum(c.shape[1] + 2 for c in cs)
        H = max(c.shape[0] for c in cs)
        img = Image.new("RGBA", (W * Z, H * Z), (104, 112, 72, 255))
        x = 0
        for c in cs:
            img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                (x * Z, (H - c.shape[0]) * Z))
            x += c.shape[1] + 2
        rows.append(img)
    sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 8 for r in rows)), (24, 24, 30, 255))
    y = 0
    for r in rows:
        sheet.alpha_composite(r, (0, y))
        y += r.height + 8
    sheet.convert("RGB").save(path)
    icons = Image.new("RGB", (3 * 202, 192), (24, 24, 30))
    for i, src in enumerate(ICONS):
        icons.paste(icon(src).convert("RGB").resize((192, 192), Image.NEAREST), (i * 202, 0))
    icons.save(path.replace(".png", "_icons.png"))
    print(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here (nothing else written)")
    a = ap.parse_args()
    m = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    allc = {n: cells(n, m) for n in FX}
    if a.review:
        review(allc, a.review)
        return
    tables = {"tft_gromp_fx": {}, "tft_gromp_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_gromp_big" if tag in BIG else "tft_gromp_fx"][tag] = out
        print(f"{tag:9s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        icon(src).save(lp(os.path.join(MOD, "icons", dst + ".png")))
        print(f"tft/icons/{dst}.png")


if __name__ == "__main__":
    main()
