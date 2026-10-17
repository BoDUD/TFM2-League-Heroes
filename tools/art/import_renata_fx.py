#!/usr/bin/env python3
"""Import Renata's effects (assets/source/renata/PROMPTS_FX.md, 24 pictures) as the game sheets league_renata_fx and
league_renata_big.

    python tools/art/import_renata_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/renata/codex_fx: pixel_1x/renata_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255, the red side's symmetry
already exact - checked again here against the entry's `symmetry` - and no dark outline round the light). Each frame is
cut by the manifest's frame size and placed as the kit plays it (import_swain_fx.py's way): spots are game px from the
pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Times from the kit (build_renata.P, 60
ticks a second). a_flash is not a sheet tag: it is drawn on her own fine squares and rig_renata.py lays it into the
attack's shot frames at the muzzle.
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
from build_renata import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "renata", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


SYM = {"top_bottom": "tb", "left_right": "lr"}
BIG = {"r_cast", "r_wave"}
BAKED = {"a_flash"}             # rig_renata.py's: into her attack frames
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
HEAD = (0, -38)                 # over a champion's head
FACE = (0, -22)                 # a champion's head
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
# the pistol's bullet chases (twice its straight flight) and shows once past the muzzle (24 px at 6 a tick); the
# missiles and the hand leave the mechanical hand (14-17 px out at 4-4.5 a tick); the wave rolls out of the machine
SHOT_MS = P["atk_range"] / P["shot_speed"] * MS * 2
E_MS = P["e_len"] / P["e_speed"] * MS
Q_MS = P["q_len"] / P["q_speed"] * MS
R_MS = P["r_len"] / P["r_speed"] * MS
ROOT_MS = P["q_root"] * MS                                  # the hand's grip holds for the root
grip_k = (ROOT_MS - 40 - 60 - 80) / 9
loop4 = lambda ms: seq(range(4), [ms] * 4)
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # the flying pictures turn with their flight (drawn going right, symmetric top to bottom)
    "a_shot": ("core", flight(4, 60, SHOT_MS, lead=4), [(0, 0)]),
    "e_missile": ("core", flight(4, 60, E_MS, lead=3), [(0, 0)]),
    "q_hand": ("core", flight(4, 60, Q_MS, lead=3), [(0, 0)]),
    "r_wave": ("core", flight(4, 90, R_MS, lead=1), [(0, 0)]),
    # hits on a unit
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "e_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_crash_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "r_lash_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "p_pop": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "r_hit": ("core", seq(range(6), [40, 60, 70, 80, 90, 100]), [FACE]),
    # round a unit, standing on its soles
    "w_cast": (("feet", 3), seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES]),
    "w_save": (("feet", 3), seq(range(6), [50, 60, 70, 80, 90, 110]), [SOLES]),
    "e_shield": (("feet", 2), seq(range(6), [40, 60, 80, 120, 120, 100]), [SOLES]),
    # the grip closes, then holds for the root
    "q_hit": (("feet", 2), seq([0, 1, 2] + [3, 4, 5] * 3, [40, 60, 80] + [grip_k] * 9), [SOLES]),
    "q_fling": (("feet", 2), seq(range(4), [40, 60, 70, 80]), [SOLES]),
    # on the ground where a missile, a thrown unit or a lash lands (not following)
    "e_boom": (("feet", 5), seq(range(6), [40, 60, 70, 80, 90, 100]), [SOLES]),
    "q_land": (("feet", 5), seq(range(6), [40, 60, 80, 90, 100, 120]), [SOLES]),
    "r_lash": (("feet", 7), seq(range(6), [40, 50, 60, 70, 80, 90]), [SOLES]),
    # the machine's gas round her through the ult (r_anim, 40 ticks)
    "r_cast": (("feet", 6), seq(range(6), [100, 100, 120, 140, 120, 87]), [SOLES]),
    # buffs (looping as long as they last)
    "p_mark": ("core", loop4(150), [HEAD]),
    "r_berserk": ("core", loop4(110), [HEAD]),
    "w_buff": (("feet", 3), loop4(120), [SOLES]),
    "e_slow": (("feet", 3), loop4(130), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", meta["file"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    sym = SYM[meta["symmetry"]]
    for k, c in enumerate(out):
        ok = (c == c[:, ::-1]).all() if sym == "lr" else (c == c[::-1]).all()
        if not ok:
            sys.exit(f"{name} frame {k + 1} is not symmetric {sym}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def brightness(cs):
    """Mean and 90th-percentile luminance of a picture's squares (memory effects-match-league: a sheet under ~100 /
    ~170 reads dark on the arena)."""
    px = np.concatenate([c[c[..., 3] > 0][:, :3] for c in cs]).astype(float)
    lum = px @ np.array([0.299, 0.587, 0.114])
    return float(lum.mean()), float(np.percentile(lum, 90))


def flash_cells():
    """a_flash's frames (her fine squares) for rig_renata.py, or None before the delivery."""
    path = os.path.join(SRC, "manifest.json")
    if not os.path.isfile(lp(path)):
        return None
    meta = {e["name"]: e for e in json.load(open(lp(path), encoding="utf-8-sig"))["effects"]}
    return cells("a_flash", meta["a_flash"]) if "a_flash" in meta else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    ap.add_argument("--src", help="a delivery folder other than assets/source/renata/codex_fx (a test)")
    ap.add_argument("--mod", help="write the sheets under this folder instead of league/ (a test)")
    a = ap.parse_args()
    global SRC, MOD
    SRC, MOD = a.src or SRC, a.mod or MOD
    meta = {e["name"]: e for e in json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))["effects"]}
    if set(meta) != set(FX) | BAKED:
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(set(FX) | BAKED)}")
    allc = {n: cells(n, meta[n]) for n in list(FX) + sorted(BAKED)}
    tables = {"league_renata_fx": {}, "league_renata_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_renata_big" if name in BIG else "league_renata_fx"][name] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    print("brightness (mean / 90th pct): " + ", ".join(
        f"{n} {m:.0f}/{p:.0f}" for n, (m, p) in ((n, brightness(c)) for n, c in allc.items())))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name, cs in allc.items():
            W = sum(c.shape[1] + 2 for c in cs)
            H = max(c.shape[0] for c in cs)
            img = Image.new("RGBA", (W * Z, H * Z), (104, 112, 72, 255))
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
