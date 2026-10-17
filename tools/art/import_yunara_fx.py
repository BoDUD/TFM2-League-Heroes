#!/usr/bin/env python3
"""Import Yunara's effects (assets/source/yunara/PROMPTS_FX.md, 22 pictures) as the game sheets league_yunara_fx and
league_yunara_big.

    python tools/art/import_yunara_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/yunara/codex_fx: pixel_1x/yunara_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json's effects (frame_width / frame_height / frames); alpha 0 / 255,
the red side's symmetry already exact - checked again here - and no dark outline round the light). Each frame is cut by
the manifest's frame size and placed as the kit plays it (import_reksai_fx.py's way): spots are game px from the pivot
(x forward, y down); a unit's soles are 11 under it, a point's ground too. Times from the kit (build_yunara.P, 60 ticks a
second).
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
from build_yunara import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "yunara", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


SYM = {"a_bead": "tb", "q_bead": "tb", "w_bead": "tb", "rw_beam": "tb"}     # every other one "lr"
BIG = {"q_spread", "q_burst", "rw_charge", "rw_beam", "re_trail", "r_burst", "r_on"}
HIT = (0, -14)                     # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                    # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
# the laser's picture lives rw_apply + rw_show ticks (its LineRangeProjectile's delay): the aiming line until the hit
# (rw_apply ticks), the blast after it
BEAM_LIFE = (P["rw_apply"] + P["rw_show"] - 1) * MS
AIM = (P["rw_apply"] - 1) * MS
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # the beads: homing (the attack: twice its straight flight), W's straight along w_len
    "a_bead": ("core", flight(2, 60, 2 * P["atk_range"] / P["bead_speed"] * MS), [(0, 0)]),
    "q_bead": ("core", flight(4, 60, 2 * P["atk_range"] / P["bead_speed"] * MS), [(0, 0)]),
    "w_bead": ("core", flight(4, 60, P["w_len"] / P["w_speed"] * MS), [(0, 0)]),
    # Arc of Ruin: the aiming line from the cast to the hit, then the blast (played once over the line's life)
    "rw_beam": ("core", seq(range(6), [AIM / 3] * 3 + [(BEAM_LIFE - AIM) * k for k in (0.4, 0.35, 0.25)]), [(0, 0)]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "q_sp_hit": ("core", seq(range(3), [40, 60, 80]), [HIT]),
    "w_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "w_tick": ("core", seq(range(3), [40, 60, 80]), [HIT]),
    "rw_hit": ("core", seq(range(5), [40, 60, 80, 90, 100]), [HIT]),
    # the spread's ripple on the ground under the unit hit (a ViewEffect at the lob's landing)
    "q_spread": ("core", seq(range(4), [60, 70, 80, 90]), [SOLES]),
    # the bead spinning where it stopped, w_linger ticks
    "w_end": (("feet", 3), seq(range(6), [P["w_linger"] * MS * k for k in (0.16, 0.16, 0.16, 0.16, 0.18, 0.18)]), [SOLES]),
    # on her (following her): her feet on the cell's bottom row
    "q_burst": (("feet", 0), seq(range(5), [60, 80, 100, 120, 140]), [SOLES]),
    "rw_charge": (("feet", 0), seq(range(4), [100] * 4), [SOLES]),
    "e_cast": (("feet", 2), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "re_trail": (("feet", 0), seq(range(5), [(P["re_t"] + 2) * MS / 5] * 5), [SOLES]),
    "r_burst": (("feet", 0), seq(range(6), [60, 80, 100, 120, 140, 160]), [SOLES]),
    # buffs (looped while they last)
    "q_on": (("feet", 0), seq(range(4), [100] * 4), [SOLES]),
    "r_on": (("feet", 0), seq(range(4), [120] * 4), [SOLES]),
    "e_ms": (("feet", 0), seq(range(4), [100] * 4), [SOLES]),
    "w_slow0": ("core", seq(range(4), [100] * 4), [SOLES]),
    "rw_slow0": ("core", seq(range(4), [100] * 4), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", meta["file"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h, n = meta["frame_width"], meta["frame_height"], meta["frames"]
    if a.shape[1] != w * n or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {n} frames of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(n)]
    sym = SYM.get(name, "lr")
    for k, c in enumerate(out):
        ok = (c == c[:, ::-1]).all() if sym == "lr" else (c == c[::-1]).all()
        if not ok:
            sys.exit(f"{name} frame {k + 1} is not symmetric {sym}")
    if sym == "lr" and w % 2 == 0:
        # an even width puts the axis between two columns, half a square off the pivot's column: thin shapes (q_burst's
        # flames) then miss their mirror image by a square on the red side; the two middle columns are the same
        # (symmetric), so one goes and the axis is the pivot's column
        out = [np.delete(c, w // 2, axis=1) for c in out]
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def manifest():
    m = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    out = {}
    for e in m["effects"]:
        name = e["file"][len("yunara_fx_"):-len(".png")]
        out[name] = e
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = manifest()
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    for n, (kind, frames, _) in FX.items():
        if len(allc[n]) != len({k for k, _ in frames if k != EMPTY}):
            sys.exit(f"{n}: {len(allc[n])} frames delivered, the timing uses {len({k for k, _ in frames if k != EMPTY})}")
    tables = {"league_yunara_fx": {}, "league_yunara_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_yunara_big" if name in BIG else "league_yunara_fx"][name] = out
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
