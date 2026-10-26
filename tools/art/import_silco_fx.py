#!/usr/bin/env python3
"""Import Silco's effects (assets/source/silco/PROMPTS_FX.md: 18 pictures and 3 skill icons) as the tft pack's sheets
tft_silco_fx and tft_silco_big and its icons.

    python tools/art/import_silco_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/silco/codex_fx/silco_fx: pixel_1x/silco_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; the flying ones symmetric top to
bottom, m_bite not symmetric, the rest left to right - checked again here, after the cleaning; silco_icon_<slot>.png
64 x 64). Each frame is cut by the manifest's frame size and placed as the kit plays it (import_alune_fx.py's way):
spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Times from
the kit (build_silco.P, 60 ticks a second).
Cleaned here (fix-delivered-art-myself): Codex's sheets kept bits of its raws' separator lines - a one- or two-row bar
across the top of the bursts' later frames (q_burst, r_burst: LINE parts) and the dashed vertical lines at the cells'
sides that made a box round the unit in the dose and the comedown (e_dose, e_crash: SIDE parts, a column or two wide at
the cell's edges).
The ground rows were measured on the cells (2026-10-27): the bursts' lowest rows (q_burst 28, r_burst 52), the rings'
ellipse middles (q_warn 4.5, r_warn 11.5, e_shimmer 38, r_slow 9), the fog's middle (r_fog 19), the puddle (m_die 9);
the pictures drawn round a 36-row unit standing in the cell's middle put its soles on their row: m_leap 41, m_bite 37,
e_dose 40, p_shield 42 (the shell's foot a row under), p_dom 42; the comedown's smoke pools at its feet (e_crash 28).
m_bite is the grub on the victim's LEFT; m_bite_r (the second monstrosity of a pair) is it mirrored.
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
from build_silco import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "silco", "codex_fx", "silco_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


FLYING = {"a_vial", "q_can", "r_can"}     # turned with their flight: symmetric top to bottom instead
ASYM = {"m_bite"}                          # the grub on the victim's left (mirrored for the right)
LINE = {"q_burst", "r_burst"}              # separator bars left across the top
SIDE = {"e_dose", "e_crash"}               # dashed lines left down the cell's sides
BIG = {"q_burst", "r_can", "r_warn", "r_burst", "r_fog"}
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
seq = J.seq
flight = J.flight
MS = 1000 / 60
VIAL_MS = P["atk_range"] / P["a_speed"] * MS * 2           # the homing vial (twice its straight flight)
CAN_MS = P["q_fall"] * MS                                  # the canister's lob
BIG_MS = P["r_fall"] * MS                                  # the giant canister's lob
LEAP_MS = P["m_leap"] * MS                                 # a monstrosity's pounce
BITE_MS = P["m_gap"] * MS                                  # one bite (tft.dll plays it every m_gap ticks)
FOG_MS = 1000                                              # tft.dll replays the fog every 60 ticks


def loop(n, ms):
    return seq(range(n), [ms] * n)


def spread(frames, total):
    """frames over `total` ms, evenly (the last takes the rounding)."""
    frames = list(frames)
    n = len(frames)
    each = [round(total / n)] * (n - 1)
    return seq(frames, each + [total - sum(each)])


# effect -> (source picture, anchor: "core" or ("ground", the cell's ground row), frames with ms, spots, mirrored)
FX = {
    "a_vial": ("a_vial", "core", flight(4, 60, VIAL_MS, lead=1), [(0, 0)], False),
    "a_hit": ("a_hit", "core", seq(range(4), [50, 60, 70, 80]), [HIT], False),
    "q_can": ("q_can", "core", flight(4, 70, CAN_MS, lead=1), [(0, 0)], False),
    "q_warn": ("q_warn", ("ground", 4.5), spread(range(4), CAN_MS), [SOLES], False),
    "q_burst": ("q_burst", ("ground", 28), seq(range(7), [50, 60, 70, 80, 90, 100, 110]), [SOLES], False),
    "m_leap": ("m_leap", ("ground", 41), spread(range(5), LEAP_MS), [SOLES], False),
    "m_bite": ("m_bite", ("ground", 37), spread(range(4), BITE_MS), [SOLES], False),
    "m_bite_r": ("m_bite", ("ground", 37), spread(range(4), BITE_MS), [SOLES], True),
    "m_die": ("m_die", ("ground", 9), seq(range(5), [80, 100, 110, 120, 130]), [SOLES], False),
    "e_dose": ("e_dose", ("ground", 40), seq(range(5), [60, 80, 100, 100, 120]), [SOLES], False),
    "e_shimmer": ("e_shimmer", ("ground", 38), loop(6, 110), [SOLES], False),
    "e_crash": ("e_crash", ("ground", 28), seq(range(5), [80, 100, 110, 120, 130]), [SOLES], False),
    "r_can": ("r_can", "core", flight(4, 70, BIG_MS, lead=1), [(0, 0)], False),
    "r_warn": ("r_warn", ("ground", 11.5), spread(range(6), BIG_MS), [SOLES], False),
    "r_burst": ("r_burst", ("ground", 52), seq(range(10), [50, 60, 70, 80, 90, 100, 110, 110, 120, 130]), [SOLES],
                False),
    "r_fog": ("r_fog", ("ground", 19), spread(range(6), FOG_MS), [SOLES], False),
    "r_slow": ("r_slow", ("ground", 9), loop(4, 120), [SOLES], False),
    "p_shield": ("p_shield", ("ground", 42), loop(6, 110), [SOLES], False),
    "p_dom": ("p_dom", ("ground", 42), loop(6, 120), [SOLES], False),
}
ICONS = {"icon_skill": "tft_silco_skill", "icon_skill2": "tft_silco_skill2", "icon_ult": "tft_silco_ult"}


def clean(name, c):
    """Codex's leftover separator lines (LINE: a bar at most 2 rows tall and 4+ wide in the cell's top half; SIDE: a part
    at most 2 columns wide touching the cell's outer 3 columns)."""
    if name not in LINE | SIDE:
        return c
    h, w = c.shape[:2]
    lb, n = ndimage.label(c[..., 3] > 0, structure=np.ones((3, 3), bool))
    for j in range(1, n + 1):
        ys, xs = np.nonzero(lb == j)
        hh, ww = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
        bar = name in LINE and hh <= 2 and ww >= 4 and ys.max() < h * 0.45
        side = name in SIDE and ww <= 2 and (xs.min() <= 2 or xs.max() >= w - 3)
        if bar or side:
            c[lb == j] = 0
    return c


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [clean(name, a[:h, k * w:(k + 1) * w].copy()) for k in range(meta["frames"])]
    for k, c in enumerate(out):
        if name in FLYING:
            if not (c == c[::-1]).all():
                sys.exit(f"{name} frame {k + 1} is not symmetric top to bottom")
        elif name not in ASYM and not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, kind[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man["assets"]:
        if not e["file"].startswith("silco_fx_"):
            continue
        name = e["file"].replace("silco_fx_", "").replace(".png", "")
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", f"silco_fx_{name}.png"))
    need = {src for src, *_ in FX.values()}
    if need - set(meta):
        sys.exit(f"missing {sorted(need - set(meta))} (delivered {sorted(meta)})")
    allc = {n: cells(n, meta[n]) for n in sorted(need)}
    tables = {"tft_silco_fx": {}, "tft_silco_big": {}}
    for tag, (src, kind, frames, spots, mirror) in FX.items():
        cs = [c[:, ::-1].copy() for c in allc[src]] if mirror else allc[src]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_silco_big" if tag in BIG else "tft_silco_fx"][tag] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"silco_{src}.png"))).convert("RGBA")
        if im.size != (64, 64):
            sys.exit(f"silco_{src}.png is {im.size}, not 64 x 64")
        im.save(lp(os.path.join(MOD, "icons", dst + ".png")))
        print(f"tft/icons/{dst}.png")
    if a.review:
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
            rows.append(img)
        sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 8 for r in rows)), (24, 24, 30, 255))
        y = 0
        for r in rows:
            sheet.alpha_composite(r, (0, y))
            y += r.height + 8
        sheet.convert("RGB").save(a.review)
        print(a.review)


if __name__ == "__main__":
    main()
