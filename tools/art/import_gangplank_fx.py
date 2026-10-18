#!/usr/bin/env python3
"""Import Gangplank's effects (assets/source/gangplank/PROMPTS_FX.md, 20 pictures) as the game sheets
league_gangplank_fx and league_gangplank_big.

    python tools/art/import_gangplank_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/gangplank/codex_fx: pixel_1x/gangplank_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json's `assets` (cell_1x); alpha 0 / 255; the projectiles
symmetric top to bottom, the three pictures drawn into his own frames free, everything else left to right - checked
again here). Each frame is cut by the manifest's frame size and placed as the kit plays it (import_ziggs_fx.py's way):
spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Times from
the kit (build_gangplank.P, 60 ticks a second). q_flash / w_cast / r_cast are only tags for rig_gangplank.py's bake
(assets/source/native/gangplank_bake.json): each frame centred on the pivot, the bake moves it to the muzzle / hand.
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
from build_gangplank import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gangplank", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"q_bullet", "e_throw"}                 # turned with their flight: drawn going right, symmetric top to bottom
OWN = {"q_flash", "w_cast", "r_cast"}        # drawn into his frames (they turn with him): any direction
BIG = {"e_boom", "r_warn", "r_wave"}
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
Q_MS = P["q_range"] / P["q_speed"] * MS * 2                # the homing bullet (twice its straight flight)
E_MS = P["e_travel"] * MS                                  # the keg's lob
LINK_MS = P["e_link"] * MS                                 # a keg re-stamped every e_link ticks
CALL_MS = P["r_call"] * MS                                 # the flare's flight: the warning under it
WAVE_MS = P["r_p"] * MS                                    # one wave of the barrage
LOOP = [120, 120, 120, 120]
R_GROW = P["r_r"] / 44000                      # Codex drew R for a 44000 radius; the user: 「R大招做大点」 (League's 580)
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "p_hit": ("core", seq(range(5), [40, 60, 70, 80, 90]), [HIT]),
    "p_ms": (("feet", 0), seq(range(4), LOOP), [SOLES]),
    "q_flash": ("core", seq(range(3), [50, 50, 60]), [(0, 0)]),
    "q_bullet": ("core", flight(2, 60, Q_MS, lead=1), [(0, 0)]),
    "q_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "e_throw": ("core", flight(3, 70, E_MS, lead=1), [(0, 0)]),
    "e_land": (("feet", 0), seq(range(4), [50, 70, 90, 110]), [SOLES]),
    "e_keg": (("feet", 0), seq(range(2), [LINK_MS / 2] * 2), [SOLES]),
    "e_keg_lit": (("feet", 0), seq(range(2), [LINK_MS / 2] * 2), [SOLES]),
    "e_boom": (("feet", 5), seq(range(7), [40, 50, 60, 70, 80, 100, 120]), [SOLES]),
    "e_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "e_slow": (("feet", 2), seq(range(4), LOOP), [SOLES]),
    "w_cast": ("core", seq(range(3), [60, 60, 60]), [(0, 0)]),
    "w_imm": (("feet", 4), seq(range(4), LOOP), [SOLES]),
    "r_cast": ("core", seq(range(4), [50, 60, 70, 80]), [(0, 0)]),
    "r_warn": (("feet", round(15 * R_GROW)), seq(range(8), [CALL_MS / 8] * 8), [SOLES]),
    "r_wave": (("feet", 16), seq(range(6), [WAVE_MS / 6] * 6), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "r_slow": (("feet", 2), seq(range(4), LOOP), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", os.path.basename(meta["file"])))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        if name not in OWN:
            sym = (c == c[::-1]).all() if name in TB else (c == c[:, ::-1]).all()
            if not sym:
                sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in TB else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out




def grow_ring(c, f):
    """The warning's dashed rings at f x without thickening them: every square's centre moved out from the cell's
    centre, plus the point between it and each touching square (the lines stay 1 square and unbroken); the left
    half mirrored onto the right."""
    h, w = c.shape[:2]
    H, W = int(round(h * f)), int(round(w * f)) // 2 * 2
    out = np.zeros((H, W, 4), np.uint8)
    cy, cx, CY, CX = (h - 1) / 2, (w - 1) / 2, (H - 1) / 2, (W - 1) / 2
    ys, xs = np.nonzero(c[..., 3] > 0)
    for y, x in zip(ys, xs):
        for dy, dx in ((0, 0), (0, 1), (1, 0), (1, 1), (1, -1)):
            y2, x2 = y + dy, x + dx
            if (dy or dx) and not (0 <= y2 < h and 0 <= x2 < w and c[y2, x2, 3]):
                continue
            out[int(round(CY + (y + dy / 2 - cy) * f)), int(round(CX + (x + dx / 2 - cx) * f))] = c[y, x]
    out[:, W // 2:] = out[:, :W // 2][:, ::-1]
    return out


def barrage(cs, f):
    """A wave over the bigger area: Codex's three blasts in the middle and the same wave a frame late to each side
    and a little behind (spread to f x the radius) - more cannonballs at once; the left half mirrored onto the right."""
    h, w = cs[0].shape[:2]
    side = int(round(w * (f - 1) / 2 + 18))
    W, H = w + 2 * side, h + 4
    out = []
    for k in range(len(cs)):
        can = np.zeros((H, W, 4), np.uint8)
        for c, x, y in ((cs[k - 1] if k else None, 0, 0), (cs[k], side, 4)):
            if c is not None:
                m = c[..., 3] > 0
                can[y:y + h, x:x + w][m] = c[m]
        can[:, W // 2:] = can[:, :W // 2][:, ::-1]
        out.append(can)
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
    meta = {e["name"][len("gangplank_fx_"):]: e for e in man["assets"]}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in sorted(FX)}
    if R_GROW > 1:
        allc["r_warn"] = [grow_ring(c, R_GROW) for c in allc["r_warn"]]
        allc["r_wave"] = barrage(allc["r_wave"], R_GROW)
        for n in ("r_warn", "r_wave"):
            for k, c in enumerate(allc[n]):
                if not (c == c[:, ::-1]).all():
                    sys.exit(f"{n} frame {k + 1} lost its symmetry")
    for n, (_, frames, _) in FX.items():
        used = {k for k, _ in frames if k != EMPTY}
        if max(used) >= len(allc[n]):
            sys.exit(f"{n}: the kit plays frame {max(used) + 1} of {len(allc[n])}")
    tables = {"league_gangplank_fx": {}, "league_gangplank_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_gangplank_big" if name in BIG else "league_gangplank_fx"][name] = out
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
