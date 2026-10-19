#!/usr/bin/env python3
"""Import Yuumi's effects (assets/source/yuumi/PROMPTS_FX.md, 19 pictures) as the game sheets league_yuumi_fx and
league_yuumi_big (+ the ride picture w_ride from the ride pack).

    python tools/art/import_yuumi_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/yuumi/codex_fx/yuumi_fx: pixel_1x/yuumi_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255; the projectiles
symmetric top to bottom, everything else left to right - checked again here). Each frame is cut by the manifest's frame
size and placed as the kit plays it (import_zoe_fx.py's way): spots are game px from the pivot (x forward, y down); a
unit's soles are 11 under it, a point's ground too. Times from the kit (build_yuumi.P, 60 ticks a second).
The ride picture (assets/source/yuumi/hd/ride.png, the ride pack's pick, 21 rows at 1.5 squares a game px) gets a sheet
of its own, league_yuumi_ride, when it is there: tag idle = it brought to 14 game px by pixel_down, tag hd_idle = the 21
rows themselves on a frame exactly 1.5 times as big (league.dll's hd.rs registers the sheet like a hero's and hands the
battlefield the dense frame), its book's bottom on the host's crown in both.
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from build_yuumi import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "yuumi", "codex_fx", "yuumi_fx")
RIDE = os.path.join(ROOT, "assets", "source", "yuumi", "hd", "ride.png")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"a_bolt", "q_missile", "r_wave"}       # turned with their flight: drawn going right
BIG = {"r_cast", "r_wave"}
RIDE_PPU = 1.5
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
ME = (0, -1)                    # round her: she is 24 game px tall at 75 %, the pivot near her middle
SOLES = (0, 11)                 # on the ground under a unit or a point
CROWN = (0, -25)                # on a 36-px champion's crown (the ride picture's book)
RIDE_PX = 14                    # the ride picture's height in game px (the user's 14)
seq = J.seq
flight = J.flight
MS = 1000 / 60
BOLT_MS = P["atk_range"] / P["a_speed"] * MS * 2                     # the homing bolt (twice its straight flight)
Q_MS = P["q_len"] / P["q_speed"] * MS                                # the missile's line
R_MS = P["r_len"] / P["r_speed"] * MS                                # a wave's line


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_bolt": ("core", flight(4, 60, BOLT_MS, lead=1), [(0, 0)]),
    "q_missile": ("core", flight(4, 70, Q_MS, lead=1), [(0, 0)]),
    "r_wave": ("core", flight(4, 80, R_MS, lead=1), [(0, 0)]),
    "a_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "p_hit": ("core", seq(range(4), [40, 60, 70, 90]), [HIT]),
    "p_heal": ("core", seq(range(4), [80, 100, 110, 120]), [ME]),
    "q_hit": ("core", seq(range(4), [40, 60, 70, 90]), [HIT]),
    "q_ehit": ("core", seq(range(4), [40, 60, 80, 100]), [HIT]),
    "q_slow": (("feet", 0), loop(4, 100), [SOLES]),
    "q_eslow": (("feet", 0), loop(4, 90), [SOLES]),
    "e_hit": (("feet", 0), seq(range(5), [50, 70, 90, 90, 100]), [SOLES]),
    "e_haste": (("feet", 0), loop(4, 80), [SOLES]),
    "w_heal": ("core", seq(range(4), [80, 100, 110, 120]), [HIT]),
    "w_jump": (("feet", 1), seq(range(4), [50, 70, 90, 100]), [SOLES]),
    "w_land": (("feet", 0), seq(range(4), [50, 70, 90, 100]), [SOLES]),
    "r_cast": (("feet", 6), seq(range(6), [60, 80, 100, 100, 80, 80]), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 60, 70, 90]), [HIT]),
    "r_heal": ("core", seq(range(4), [60, 80, 100, 110]), [HIT]),
    "r_root": (("feet", 0), loop(4, 100), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        mirror = c[::-1] if name in TB else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in TB else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def ride_frames():
    """league_yuumi_ride's tags: idle (RIDE_PX game px) and hd_idle (ride.png's own squares, RIDE_PPU a game px), both
    with the book's bottom on the host's crown; one frame each, held."""
    import pixel_down as D
    d = np.asarray(Image.open(lp(RIDE)).convert("RGBA"))
    d = d[np.ix_(np.any(d[..., 3] > 0, 1), np.any(d[..., 3] > 0, 0))]

    def book_bottom(a):
        # the lowest row of the dark-red cover (the tail hangs lower)
        c = a[..., :3].astype(int)
        red = (a[..., 3] > 0) & (c[..., 0] > 90) & (c[..., 1] < 50) & (c[..., 2] < 70)
        rows = np.nonzero(red.any(1))[0]
        return int(rows.max()) if len(rows) else a.shape[0] - 1
    k = RIDE_PX / d.shape[0]
    g, _ = D.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), D.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    one = J.place(g, [(g.shape[1] - 1) / 2, book_bottom(g)], [CROWN])     # odd sizes, the pivot in the middle
    # the dense frame: RIDE_PPU times the 1x frame, rounded (league.dll takes hd_idle within half a pixel of PPU times
    # idle's width), the same pivot in its middle; the picture's book bottom on the crown at RIDE_PPU squares a game px
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = {}
    if os.path.isfile(lp(os.path.join(SRC, "manifest.json"))):
        man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
        # Codex's manifest (2026-10-19): a list of entries with name, file, pixel_1x, frames and cell_1x
        for e in man if isinstance(man, list) else (man.get("effects") or man.get("entries") or []):
            meta[e.get("name") or e["id"]] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", e["file"]))
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_yuumi_fx": {}, "league_yuumi_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_yuumi_big" if name in BIG else "league_yuumi_fx"][name] = out
    if os.path.isfile(lp(RIDE)):
        tables["league_yuumi_ride"] = ride_frames()
    else:
        print("no hd/ride.png yet: league_yuumi_ride left out (the ride pack is not in)")
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name, cs in allc.items():
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
        sheet.save(lp(a.review))
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
