#!/usr/bin/env python3
"""Import Zyra's effects (assets/source/zyra/PROMPTS_FX.md, 16 pictures) as the game sheets league_zyra_fx and
league_zyra_big.

    python tools/art/import_zyra_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/zyra/codex_fx/zyra_fx: pixel_1x/zyra_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255; the projectiles
symmetric top to bottom, the hits / ground / buff pictures left to right - checked again here; the plants' sway frames
are left alone). Each frame is cut by the manifest's frame size and placed as the kit plays it (import_vex_fx.py's
way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Times
from the kit (build_zyra.P, 60 ticks a second):
  * the plants (t_plant, v_plant) are one tag as long as the plant lives (t_life / v_life): it grows in GROW_MS (its first
    strike comes t_first ticks after it appears), then one cycle a strike period - the strike frame, then the four sway
    frames - and wilts in its last frames;
  * the thicket (r_thicket) writhes (its three loop frames) until the knock-up r_knock ticks after it appears, closes
    like a cage on that tick and falls apart;
  * the add-on's seed (s_seed) is as long as the add-on replays it (s_show ticks).
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
from build_zyra import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zyra", "codex_fx", "zyra_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"a_seed", "t_spit", "e_roots"}            # turned with their flight: drawn going right
BIG = {"q_burst", "t_plant", "v_plant", "r_thicket"}
FRONT = {"t_plant", "v_plant"}                   # drawn from the front, swaying left and right: not mirrored
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
seq = J.seq
flight = J.flight
MS = 1000 / 60
SEED_MS = P["atk_range"] / P["a_speed"] * MS * 2                     # the homing seed (twice its straight flight)
E_MS = P["e_len"] / P["e_speed"] * MS                                # Grasping Roots' line
SPIT_MS = P["t_r"] / P["spit_speed"] * MS * 2                        # the add-on's spit
GROW_MS = [100, 100, 133]           # the plants' growing frames, stretched to their first strike


def loop(n, ms):
    return seq(range(n), [ms] * n)


def plant(life, first, period):
    """A plant's frames (10 drawn: 3 growing, 4 swaying - left, middle, right, middle -, 1 striking, 2 wilting) over its
    life: it grows until its first strike `first` ticks in, strikes on every period (the strike frame, then the sway on
    from the left), wilts in its last frames."""
    total = life * MS
    grow = first * MS
    out = [(k, grow * m / sum(GROW_MS)) for k, m in enumerate(GROW_MS)]
    wilt = [(8, 160), (9, 200)]
    t, end = grow, total - sum(m for _, m in wilt)
    while t < end - 1:
        left = min(period * MS, end - t)
        out.append((7, min(150, left)))
        rest = left - 150
        if rest > 0:
            out += [(k, rest / 4) for k in (3, 4, 5, 6)]
        t += left
    return out + wilt


def thicket():
    """The thicket's 10 frames over its life: the ring, the vines, the thicket rising, writhing (frames 4-6 looped) until
    the knock-up, the cage closing on its tick, falling apart."""
    knock = P["r_knock"] * MS
    head = [(0, 80), (1, 80), (2, 100)]
    close = [(6, 100), (7, 100)]
    tail = [(8, 130), (9, 160)]
    writhe = knock - sum(m for _, m in head) - close[0][1]
    n = max(3, int(round(writhe / 120)))
    mid = [(3 + i % 3, writhe / n) for i in range(n)]
    return head + mid + close + tail


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom row), frames with ms, spots)
FX = {
    # the seed hidden its first 4 ticks (18 px at 4.5 a tick): it leaves the whip's tip, 22 px ahead on the release frame
    "a_seed": ("core", flight(4, 60, SEED_MS, lead=4), [(0, 0)]),
    "e_roots": ("core", flight(4, 60, E_MS, lead=1), [(0, 0)]),
    "t_spit": ("core", flight(2, 60, SPIT_MS, lead=1), [(0, 0)]),
    "a_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "q_burst": (("feet", 7), seq(range(6), [60, 60, 80, 120, 110, 120]), [SOLES]),
    "q_hit": ("core", seq(range(4), [40, 60, 70, 90]), [HIT]),
    "t_plant": (("feet", 0), plant(P["t_life"], P["t_first"], P["t_per"]), [SOLES]),
    "t_hit": ("core", seq(range(3), [40, 50, 60]), [HIT]),
    "v_plant": (("feet", 0), plant(P["v_life"], P["v_first"], P["v_per"]), [SOLES]),
    "v_hit": ("core", seq(range(3), [40, 60, 70]), [HIT]),
    "e_bound": (("feet", 0), loop(4, 120), [SOLES]),
    "v_slow": (("feet", 0), loop(4, 100), [SOLES]),
    "r_thicket": (("feet", 10), thicket(), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 60, 80, 100]), [HIT]),
    "r_knock": (("feet", 0), seq(range(4), [60, 80, 100, 120]), [SOLES]),
    "s_seed": (("feet", 0), loop(4, P["s_show"] * MS / 4), [SOLES]),
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
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
        mirror = c[::-1] if name in TB else c[:, ::-1]
        off = int(((c != mirror).any(axis=2) & ((c[..., 3] > 0) | (mirror[..., 3] > 0))).sum())
        if name in FRONT:
            if off:
                print(f"  {name} frame {k + 1}: {off} squares off its mirror (drawn from the front, swaying)")
        elif off:
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in TB else 'left to right'}"
                     f" ({off} squares)")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man.get("effects") or man["entries"]:
        name = e.get("name") or e.get("id") or e["file"][len("zyra_fx_"):-len(".png")]
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", e["file"]))
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_zyra_fx": {}, "league_zyra_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_zyra_big" if name in BIG else "league_zyra_fx"][name] = out
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
