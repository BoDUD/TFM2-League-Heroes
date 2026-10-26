#!/usr/bin/env python3
"""Import Norra's effects (assets/source/norra/PROMPTS_FX.md, 15 pictures) as the game sheets tft_norra_fx and
tft_norra_big, and Yuumi on her book (hd/yuumi.png) as tft_norra_yuumi.

    python tools/art/process_norra_fx.py               # the delivery made right where it came out wrong -> fx_1x/
    python tools/art/import_norra_fx.py [--review out.png]

The source is assets/source/norra/fx_1x (process_norra_fx.py's copy of the step-3 delivery, Codex 2026-10-26/new-chat-5:
one row of equal frames each at game size, frame sizes in its manifest.json; alpha 0 / 255; the bolt and the ball
flying right and symmetric top to bottom, the paint symmetric both ways, every other one left to right - checked again
here, then made an odd number of squares across the symmetric way). import_locke_fx.py's way. Each frame is placed as
the kit plays it (tools/kit/build_norra.py's views): spots are game px from the pivot (x forward, y down); a unit's
soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's middle),
"bottom" (the lowest drawn row of all the picture's frames), (0, k) (the row k over the cell's last).
Three pictures are cut in two, the fall and the landing: the anvil and the giant book fall out of their gate while the
hidden lob flies (e_anvil_drop / e_book_drop: the lob's range_effect_name, played on the landing point the tick it is
fired, e_travel 18 ticks long) and slam when it lands (e_anvil_hit / e_book_hit, with the stun or the knock-up); the
Book of Thresholds' gate opens and lets its page fall while the gate's lob flies (r_fall, played on the target's spot in
the tick the lob leaves, r_open 40 ticks long) and the page slams (r_book). r_book's ninth frame (a lone light pillar
after the scraps settled, which the delivery had already emptied) is skipped.
Yuumi (tft_norra_yuumi, her passive's ride picture over an ally's head - league_yuumi_ride's way): tag idle = hd/yuumi.png
brought to RIDE_PX game px, tag hd_idle = hd/yuumi.png on its own squares (PPU 2.0, league.dll draws it dense), both with
the book's bottom on a 36-px champion's crown.
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
from import_hwei_fx import anchor, lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "norra", "fx_1x")
HD = os.path.join(ROOT, "assets", "source", "norra", "hd")
MOD = os.path.join(ROOT, "tft")

FLYING = {"a_bolt", "q_ball"}       # turned with their flight: drawn going right, symmetric top to bottom
BOTH = {"q_paint"}                  # a zone's picture: symmetric both ways
HIT = (0, -14)                      # a hit on the upper body of a 32-46 px unit
CHEST = (0, -16)                    # Yuumi's little heal rising from a unit's chest
MIDDLE = (0, -7)                    # the middle of a 36 px unit (the shield bubble, the paper frame)
OVERHEAD = (0, -2)                  # the potion's lowest drops at a unit's waist, its gate over the head
GROUND = (0, 12)                    # a picture's lowest row on the ground line
FEETRING = (0, 11)                  # the middle of a ring drawn round a unit's feet
LINE = (0, 0)                       # a projectile's point
CROWN = (0, -25)                    # on a 36-px champion's crown (Yuumi's book)
RIDE_PX = 17                        # Yuumi's height in game px (the user's 「B-1 17px」)
RIDE_PPU = 2.0

seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# tag -> (picture, anchor, frames with ms, spots, sheet)
FX = {
    # the attack: a star bolt off her finger, its hit
    "a_bolt": ("a_bolt", "core", loop(4, 60), [LINE], "fx"),
    "a_hit": ("a_hit", "core", seq(range(3), [40, 60, 80]), [HIT], "fx"),
    # Best Friends: Yuumi's heal on the ally she rides
    "p_heal": ("p_heal", "core", seq(range(4), [80, 90, 100, 120]), [CHEST], "fx"),
    # Portalpalooza: the ball (q_travel 26 ticks), its burst on the ground, the hit, the painted paper ground (300 ticks)
    "q_ball": ("q_ball", "core", loop(4, 70), [LINE], "fx"),
    "q_blast": ("q_blast", "bottom", seq(range(7), [50, 60, 70, 80, 90, 100, 110]), [GROUND], "big"),
    "q_hit": ("q_hit", "core", seq(range(3), [40, 60, 80]), [HIT], "fx"),
    "q_paint": ("q_paint", "core", loop(6, 150), [FEETRING], "big"),
    # Otherworld Delivery: the gate over the champion and the anvil falling while the hidden lob flies (e_travel 18
    # ticks = 300 ms), its slam; the giant book the same; the potion over each ally; the shield bubble (also R's ward)
    "e_anvil_drop": ("e_anvil_hit", "bottom", seq(range(4), [75, 75, 75, 75]), [GROUND], "big"),
    "e_anvil_hit": ("e_anvil_hit", "bottom", seq(range(4, 8), [70, 90, 110, 140]), [GROUND], "big"),
    "e_book_drop": ("e_book_hit", "bottom", seq(range(4), [75, 75, 75, 75]), [GROUND], "big"),
    "e_book_hit": ("e_book_hit", "bottom", seq(range(4, 8), [70, 90, 110, 140]), [GROUND], "big"),
    "e_potion": ("e_potion", "bottom", seq(range(6), [60, 70, 70, 70, 80, 100]), [OVERHEAD], "fx"),
    "e_guard": ("e_guard", "core", loop(6, 120), [MIDDLE], "fx"),
    # the Book of Thresholds: the ring on the ground while the gate's lob flies (r_open 40 ticks = 667 ms), the gate
    # opening and its page falling meanwhile, the page's slam (frame 9, a lone pillar, skipped), the hit, the paper look
    "r_warn": ("r_warn", "core", seq(range(6), [90, 100, 110, 120, 120, 127]), [FEETRING], "big"),
    "r_fall": ("r_book", "bottom", seq(range(5), [100, 120, 149, 149, 149]), [GROUND], "big"),
    "r_book": ("r_book", "bottom", seq([5, 6, 7, 9], [90, 110, 140, 160]), [GROUND], "big"),
    "r_hit": ("r_hit", "core", seq(range(4), [50, 60, 80, 100]), [HIT], "fx"),
    "r_paper": ("r_paper", "core", loop(6, 130), [MIDDLE], "fx"),
}


def sym_of(name):
    return "top-bottom" if name in FLYING else "both" if name in BOTH else "left-right"


def odd(c, name):
    """A symmetric picture an even number of squares across gets its middle column (top to bottom for a projectile: its
    middle row) twice: the game mirrors and turns about the pivot's square, so only an odd width lies even about it."""
    axes = {"top-bottom": (0,), "left-right": (1,), "both": (0, 1)}[sym_of(name)]
    for ax in axes:
        n = c.shape[ax]
        if not n % 2:
            c = np.insert(c, n // 2, np.take(c, n // 2, axis=ax), axis=ax)
    return c


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        s = sym_of(name)
        ok = {"top-bottom": (c == c[::-1]).all(), "left-right": (c == c[:, ::-1]).all(),
              "both": (c == c[::-1]).all() and (c == c[:, ::-1]).all()}[s]
        if not ok:
            sys.exit(f"{name} frame {k + 1} is not symmetric {s}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return [odd(c, name) for c in out]


def ride_frames():
    """tft_norra_yuumi's tags: idle (RIDE_PX game px) and hd_idle (yuumi.png's own squares, RIDE_PPU a game px), both
    with the book's bottom on the host's crown; one frame each, held (import_yuumi_fx.ride_frames' way)."""
    import pixel_down as D
    d = np.asarray(Image.open(lp(os.path.join(HD, "yuumi.png"))).convert("RGBA"))
    d = d[np.ix_(np.any(d[..., 3] > 0, 1), np.any(d[..., 3] > 0, 0))]

    def book_bottom(a):
        # the lowest row of the red-brown cover (gold corners and the tail may hang lower)
        c = a[..., :3].astype(int)
        red = (a[..., 3] > 0) & (c[..., 0] > 90) & (c[..., 1] < 70) & (c[..., 2] < 70) & (c[..., 0] > c[..., 1] + 50)
        rows = np.nonzero(red.any(1))[0]
        return int(rows.max()) if len(rows) else a.shape[0] - 1
    k = RIDE_PX / d.shape[0]
    g, _ = D.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), D.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    one = J.place(g, [(g.shape[1] - 1) / 2, book_bottom(g)], [CROWN])
    H, W = round(one.shape[0] * RIDE_PPU), round(one.shape[1] * RIDE_PPU)
    dense = np.zeros((H, W, 4), np.uint8)
    ax = (W - 1) / 2 + CROWN[0] * RIDE_PPU
    ay = (H - 1) / 2 + CROWN[1] * RIDE_PPU
    top = int(round(ay - book_bottom(d)))
    left = int(round(ax - (d.shape[1] - 1) / 2))
    for y in range(d.shape[0]):
        for x in range(d.shape[1]):
            if d[y, x, 3] and 0 <= top + y < H and 0 <= left + x < W:
                dense[top + y, left + x] = d[y, x]
    return {"idle": [(one, 1000)], "hd_idle": [(dense, 1000)]}


def manifest():
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))
    return {e["id"]: e for e in man["items"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = manifest()
    pics = {v[0] for v in FX.values()}
    if set(meta) != pics:
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(pics)}")
    allc = {n: cells(n, meta[n]) for n in pics}
    tables = {"tft_norra_fx": {}, "tft_norra_big": {}}
    for tag, (pic, kind, frames, spots, sheet) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)                          # over all the picture's frames: the fall and the slam agree
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_norra_big" if sheet == "big" else "tft_norra_fx"][tag] = out
    tables["tft_norra_yuumi"] = ride_frames()
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
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
