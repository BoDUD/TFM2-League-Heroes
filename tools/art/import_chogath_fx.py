#!/usr/bin/env python3
"""Import Cho'Gath's effects (assets/source/chogath/PROMPTS_FX.md, 15 pictures) as the game sheets league_chogath_fx and
league_chogath_big.

    python tools/art/import_chogath_fx.py [--src DIR] [--review out.png]

The source is Codex's step-3 delivery (assets/source/chogath/codex_fx: pixel_1x/chogath_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; the two pictures on picture-only lines
(e_pic, w_wave) drawn pointing right and symmetric top to bottom, every other one symmetric left to right - checked
again here). Each frame is cut by the manifest's frame size and placed as the kit plays it (import_volibear_fx.py's
way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it (his 11.5), a point's ground
too. A line's picture is drawn on the line's middle at pivot height. Times follow tools/kit/build_chogath.py: the
volley and the scream last as long as their lines (e_pic_t, w_pic_t), the cracks until the spikes burst (q_delay);
the buffs loop (e_slow, q_slow, w_sil); the rest play once.
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
from build_chogath import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "chogath", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"q_crack", "q_spikes", "w_wave", "r_hit", "r_grow"}
FLYING = {"e_pic", "w_wave"}    # on picture-only lines, turned with them: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -29)             # over a 36-px unit's head (the mark 36-44 px over its soles)
LINE = (0, 0)                   # a line's middle, at pivot height
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def ticks_ms(t):
    return t * 1000 / 60


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # the attack's slam on the target; Carnivore's heal on him when the attack kills
    "a_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "p_heal": (("feet", 0), seq(range(4), [80, 90, 100, 110]), [SOLES]),
    # Vorpal Spikes: armed (on him), the volley (its line's e_pic_t), the hit, the slow (a buff)
    "e_arm": (("feet", 0), seq(range(4), [60, 70, 80, 90]), [SOLES]),
    "e_pic": ("core", seq(range(4), [60, 60, 60, 70]), [LINE]),
    "e_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "e_slow": (("feet", 0), loop(2, 150), [SOLES]),
    # Rupture: the cracks on the point until the spikes burst (q_delay), the spikes, the hit, the slow (a buff)
    "q_crack": (("feet", 9), seq(range(6), [100] * 6), [SOLES]),
    "q_spikes": (("feet", 8), seq(range(6), [50, 60, 80, 90, 90, 100]), [SOLES]),
    "q_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "q_slow": (("feet", 0), loop(2, 150), [SOLES]),
    # Feral Scream: the cone (its line's w_pic_t), the hit, the silence (a buff)
    "w_wave": ("core", seq(range(5), [60, 70, 80, 90, 100]), [LINE]),
    "w_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "w_sil": ("core", loop(4, 120), [OVERHEAD]),
    # Feast: the bite on the target, the surge round him when it eats
    "r_hit": (("feet", 0), seq(range(5), [60, 60, 70, 80, 90]), [SOLES]),
    "r_grow": (("feet", 0), seq(range(5), [70, 80, 90, 100, 110]), [SOLES]),
}
# the pictures that must last as long as something in the kit: tag -> ticks
LASTS = {"e_pic": P["e_pic_t"], "w_wave": P["w_pic_t"], "q_crack": P["q_delay"]}
STRAY = {}


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for (nm, k), (r0, r1) in STRAY.items():
        if nm == name:
            out[k][r0:r1] = 0
    for k, c in enumerate(out):
        mirror = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def manifest(src):
    """{name: entry} from Codex's manifest.json, whichever way it lists them ("entries" / "effects" / "assets", each
    with "id" or "name", maybe prefixed chogath_fx_), with the 1x sheet's path relative to src."""
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    rows = man.get("entries") or man.get("effects") or man.get("assets") or []
    meta = {}
    for e in rows:
        name = (e.get("id") or e.get("name")).replace("chogath_fx_", "")
        meta[name] = dict(e, pixel_1x=e.get("pixel_1x") or os.path.join("pixel_1x", e["file"]))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC, help="Codex's delivery (the folder holding manifest.json and pixel_1x/)")
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    for tag, t in LASTS.items():
        ms = sum(m for _, m in FX[tag][1])
        if abs(ms - ticks_ms(t)) > 1:
            sys.exit(f"{tag} plays {ms} ms, the kit holds it {t} ticks ({ticks_ms(t):.0f} ms)")
    meta = manifest(a.src)
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n], a.src) for n in FX}
    tables = {"league_chogath_fx": {}, "league_chogath_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{name}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_chogath_big" if name in BIG else "league_chogath_fx"][name] = out
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
