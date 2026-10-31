#!/usr/bin/env python3
"""Import Aurelion Sol's effects (assets/source/aurelionsol/PROMPTS_FX.md, 19 pictures) as the game sheets
league_aurelionsol_fx and league_aurelionsol_big (import_belveth_fx.py's way).

    python tools/art/import_aurelionsol_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/aurelionsol/codex_fx/aurelionsol_fx, Codex 2026-10-24/new-chat-3:
pixel_1x/aurelionsol_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json ("items":
cell_1x, frames, symmetry); alpha 0 / 255; the star bolt and the breath drawn flying right and symmetric top to bottom,
the black-hole seed round (both ways), every other one symmetric left to right - checked again here, then made an odd
number of squares across the symmetric way).
Each frame is placed as the kit plays it: spots are game px from the pivot (x forward, y down); a unit's soles are 11
under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's middle), "bottom" (the lowest
drawn row of all its frames), (0, k) (the cell's own row k from its bottom: pictures drawn in part of their cell).
He floats 4 squares (2 game px) over his ground and stands 44 px tall: his body's middle is 24 px over the ground.
The lasting ones loop (tools/kit/build_aurelionsol.py: the black hole e_t - its first three frames turning, the last
three closing it -, the flight's stardust w_t, the Skies' stars over his head, the slows, the projectiles); the rest
play once. The falling star (r_fall) lasts r_fall (30 ticks), its last frame the flash on the ground as r_impact begins.
Stardust grows the star, the Skies, the shockwave and the black hole (tools/kit/build_aurelionsol.py: a size step every
grow_n stardust, grow_x% at d_max; the user 2026-10-31: 「应该后期大招会很大吧」), so each of those four is drawn again at
every step's size as `<tag>_<step>` (GROWN): every frame resized smoothly with its alpha, cut back into its own colours,
mirrored left to right again; the impact, the shockwave and the black hole grow about their middle (the zone's centre),
the Skies about the ground they hit.
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from import_hwei_fx import anchor, lp, odd, rows_drawn  # noqa: E402
import build_aurelionsol as K  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aurelionsol", "codex_fx", "aurelionsol_fx")
MOD = os.path.join(ROOT, "league")

BIG = {"e_hole", "r_fall", "r_impact", "r_sky", "r_wave"}
FLYING = {"a_bolt", "q_beam"}   # turned with their flight: drawn going right, symmetric top to bottom
ROUND = {"e_orb"}               # turned with its flight too: symmetric both ways
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
GROUND = (0, 12)                # a picture's lowest row on the ground line
LINE = (0, 0)                   # a projectile's point
BODY = (0, -12)                 # his body's middle (24 px over the ground: 44 tall, floating 2)
OVER_HEAD = (0, -26)            # r_call's cell bottom: its upper half (the constellation) over his crest


seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def lasting(opening, looped, closing, total):
    """An opening (frames with ms), the looped frames at their ms repeated while the total lasts, a closing: a picture
    stretched to a zone's life (total ms)."""
    head = sum(ms for _, ms in opening) + sum(ms for _, ms in closing)
    per = sum(ms for _, ms in looped)
    n = max(1, round((total - head) / per))
    return opening + looped * n + closing


T = lambda ticks: ticks * 1000 / 60     # noqa: E731

# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the star bolt (homing; Animated pictures repeat) and its pop
    "a_bolt": ("a_bolt", "core", loop(3, 60), [LINE]),
    "a_hit": ("a_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    # Breath of Light: a segment of the beam every q_p ticks, the sear on each one in it (short: it comes every 167 ms)
    "q_beam": ("q_beam", "core", loop(3, 50), [(10, 0)]),   # the segment ahead of its point (it starts at his pivot)
    "q_hit": ("q_hit", "core", seq(range(3), [30, 40, 50]), [HIT]),
    # Singularity: the seed flying, the black hole on the ground for e_t (frames 1-3 turning, 4-6 closing it), the core
    # crushing a champion, the slow at the feet
    "e_orb": ("e_orb", "core", loop(3, 60), [LINE]),
    "e_hole": ("e_hole", "bottom", lasting([(0, 100)], seq(range(3), [120, 120, 120]),
                                          seq(range(3, 6), [120, 140, 160]), T(300)), [GROUND]),
    "e_core": ("e_core", "bottom", seq(range(4), [60, 80, 100, 120]), [GROUND]),
    "slow": ("slow", "bottom", loop(4, 110), [GROUND]),
    # Falling Star / The Skies Descend: the star called over his head, the star coming down on the spot (r_fall 30
    # ticks), the impact, the giant star, the shockwave, the hit
    "r_call": ("r_call", (0, 0), seq(range(4), [60, 60, 60, 80]), [OVER_HEAD]),
    "r_fall": ("r_fall", (0, 0), seq([0, 1, 2, 6, 7, 5], [84, 84, 84, 84, 84, 80]), [GROUND]),
    "r_impact": ("r_impact", "bottom", seq(range(5), [60, 80, 100, 120, 150]), [GROUND]),
    "r_sky": ("r_sky", "bottom", seq(range(6), [70, 90, 110, 130, 150, 170]), [GROUND]),
    "r_wave": ("r_wave", "bottom", seq(range(5), [70, 80, 90, 100, 120]), [GROUND]),
    "r_hit": ("r_hit", "core", seq(range(3), [50, 70, 90]), [HIT]),
    # Cosmic Creator / Astral Flight: the lift into flight, the stardust stream while it lasts, stardust drawn in, the
    # Skies charged, the stars over his head while they wait
    "w_lift": ("w_lift", "bottom", seq(range(4), [70, 90, 110, 130]), [GROUND]),
    "w_trail": ("w_trail", "bottom", loop(4, 110), [GROUND]),
    "d_gain": ("d_gain", "core", seq(range(4), [80, 100, 120, 140]), [BODY]),
    "sky_ready": ("sky_ready", "core", seq(range(4), [80, 100, 120, 140]), [BODY]),
    "sky_glow": ("sky_glow", (0, 0), loop(4, 150), [GROUND]),
}


# the pictures drawn again at each stardust size step (the kit's tier_tag), and the point each grows about: "mid" (its
# drawn rows' middle, kept where it was: the zone's centre) or "bottom" (its lowest row, kept on the ground)
GROWN = {"e_hole": "mid", "r_impact": "mid", "r_sky": "bottom", "r_wave": "mid"}


def grown_cell(c, k):
    """A delivered cell k times bigger: resized smoothly (its see-through squares are black, so its colours are already
    weighted by their alpha), alpha cut at half, each square the nearest of the cell's own colours, mirrored left to
    right about the middle column (an odd width)."""
    from skimage import color
    h, w = c.shape[:2]
    W = int(round(w * k))
    W += 1 - W % 2
    H = int(round(h * k))
    big = np.asarray(Image.fromarray(c).resize((W, H), Image.LANCZOS)).astype(float)
    alpha = big[..., 3]
    on = alpha >= 128
    pal = np.unique(c[c[..., 3] > 0][:, :3], axis=0)
    rgb = np.clip(big[..., :3][on] * 255.0 / np.maximum(alpha[on], 1.0)[:, None], 0, 255)
    pal_lab = color.rgb2lab(pal[None].astype(float) / 255.0)[0]
    lab = color.rgb2lab(rgb[None] / 255.0)[0]
    near = ((lab[:, None, :] - pal_lab[None, :, :]) ** 2).sum(-1).argmin(1)
    out = np.zeros((H, W, 4), np.uint8)
    out[on, :3] = pal[near]
    out[on, 3] = 255
    m = W // 2
    out[:, m + 1:] = out[:, :m][:, ::-1]
    return out


def grown_frames(cs, kind, frames, spots, k, fix):
    """One size step of a ground picture: its cells k times bigger, placed so the fixed point stays where the original's
    is (its anchor `kind` on `spots`)."""
    big = [grown_cell(c, k) for c in cs]
    if fix == "bottom":
        anc, at = anchor(big, "bottom"), spots
    else:
        y0, y1 = rows_drawn(cs)
        a0 = anchor(cs, kind)
        mid = [(sx, sy - (a0[1] - (y0 + y1) / 2)) for sx, sy in spots]
        b0, b1 = rows_drawn(big)
        anc, at = [(big[0].shape[1] - 1) / 2, (b0 + b1) / 2], mid
    return [(J.place(big[i], anc, at), ms) for i, ms in frames]


# frames made here from a delivered one moved whole squares down (picture -> [(frame, rows down)], appended in order):
# Codex's r_fall frames 4 and 5 show two stars side by side (its left-right symmetry pass mirrored an off-centre star),
# so the single star of frame 3 comes on down to the ground instead
DOWN = {"r_fall": [(2, 9), (2, 17)]}


def moved_down(c, dy):
    out = np.zeros_like(c)
    out[dy:] = c[:c.shape[0] - dy]
    if c[c.shape[0] - dy:, :, 3].any():
        sys.exit("a frame moved down runs off its cell")
    return out


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        mirrors = [c[::-1], c[:, ::-1]] if name in ROUND else [c[::-1] if name in FLYING else c[:, ::-1]]
        if not all((c == m).all() for m in mirrors):
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    out += [moved_down(out[k], dy) for k, dy in DOWN.get(name, [])]
    return [odd_(c, name) for c in out]


def odd_(c, name):
    """import_hwei_fx.odd with this hero's projectile."""
    if name in FLYING or name in ROUND:
        n = c.shape[0]
        c = c if n % 2 else np.insert(c, n // 2, c[n // 2], axis=0)
        if name in FLYING:
            return c
    return odd(c, name)


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    if isinstance(man, dict):                     # a delivery shaped {"schema_version", ..., "effects": [...]}
        man = man.get("effects") or man.get("items")
    meta = {}
    for e in man:
        f = os.path.basename(e["file"])
        name = f[:-4].replace("aurelionsol_fx_", "")
        meta[name] = dict(e, pixel_1x=os.path.join("pixel_1x", f))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC, help="the delivery (the folder holding manifest.json and pixel_1x/)")
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = manifest(a.src)
    pics = {v[0] for v in FX.values()}
    if set(meta) != pics:
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(pics)}")
    allc = {n: cells(n, meta[n], a.src) for n in pics}
    tables = {"league_aurelionsol_fx": {}, "league_aurelionsol_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_aurelionsol_big" if tag in BIG else "league_aurelionsol_fx"][tag] = out
    for tag, fix in GROWN.items():
        pic, kind, frames, spots = FX[tag]
        for t in range(1, K.tiers(K.P) + 1):
            tables["league_aurelionsol_big"][K.tier_tag(tag, t)] = grown_frames(allc[pic], kind, frames, spots,
                                                                                 K.grown(K.P, t), fix)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name in sorted(allc):
            cs = allc[name]
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
        sheet = Image.new("RGB", (W, sum(r.height + 10 for _, r in rows)), (20, 20, 26))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.paste(r.convert("RGB"), (120, y))
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += r.height + 10
        sheet.save(lp(a.review))
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
