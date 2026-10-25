#!/usr/bin/env python3
"""Import Trundle's effects (assets/source/trundle/PROMPTS_FX.md, 15 pictures) as the game sheets league_trundle_fx and
league_trundle_big.

    python tools/art/import_trundle_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/trundle/codex_fx/trundle_fx, Codex 2026-10-25/new-chat-5:
pixel_1x/trundle_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json (a list: cell_1x,
frames, symmetry); alpha 0 / 255; every one symmetric left to right - checked again here, then made an odd number of
squares across the symmetric way). import_yorick_fx.py's way.
Each frame is placed as the kit plays it: spots are game px from the pivot (x forward, y down); a unit's soles are 11
under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's middle), "bottom" (the lowest
drawn row of all its frames). The pillar stands e_t ticks (4 s, tools/kit/build_trundle.py) from ONE play: its standing
frame (the 6th) is held for the rest; the frozen ground under him, the slows, the marks over heads loop while their buffs
last; the drain's shackles loop a second (the kit's AddCasted plays them every 60 ticks); `w_field` (the add-on's frozen
field where it froze, played again every 60 ticks) is the domain's last two frames, a second long; the rest play once.
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
from import_hwei_fx import anchor, lp, odd  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "trundle", "codex_fx", "trundle_fx")
# the redraws (the domain made big, 80 x 26: 「那gif图的冰面那么小？」, Codex 2026-10-25/new-chat-5), read in place of SRC's
REDO = os.path.join(ROOT, "assets", "source", "trundle", "codex_fx", "trundle_fx_redo")
MOD = os.path.join(ROOT, "league")

BIG = {"w_domain", "e_pillar"}
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
OVER = (0, -28)                 # over a unit's head
OVER_HIM = (0, -33)             # over Trundle's mane (42.5 game px)
GROUND = (0, 12)                # a picture's lowest row on the ground line
FEETRING = (0, 11)              # the middle of a ring drawn round a unit's feet
PILLAR_T = 4000                 # ms the pillar stands: the kit's e_t 240 ticks


seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


_RISE, _FALL = [60, 70, 80, 90, 100], [120, 150]
# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the ice club's blow
    "a_hit": ("a_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    # King's Tribute: green wisps round him as a unit falls near him
    "p_heal": ("p_heal", "bottom", seq(range(5), [80, 90, 100, 110, 120]), [GROUND]),
    # Chomp: the bite, his strength over his head, the bitten one's weakness over its head, the slow at its feet
    "q_hit": ("q_hit", "core", seq(range(4), [50, 60, 80, 100]), [HIT]),
    "q_buff": ("q_buff", "bottom", loop(4, 150), [OVER_HIM]),
    "q_sap": ("q_sap", "bottom", loop(4, 150), [OVER]),
    "slow": ("slow", "core", loop(4, 110), [FEETRING]),
    # the Frozen Domain: the landing's frost ring, the ground freezing over, the frozen patch under him while it lasts;
    # the add-on's frozen field where it froze (the domain's last two frames, a second)
    "w_hop": ("w_hop", "core", seq(range(4), [50, 60, 80, 100]), [FEETRING]),
    "w_domain": ("w_domain", "core", seq(range(8), [60, 70, 80, 90, 100, 110, 120, 170]), [FEETRING]),
    "w_aura": ("w_aura", "core", loop(6, 120), [FEETRING]),
    "w_field": ("w_domain", "core", seq([6, 7], [500, 500]), [FEETRING]),
    # Pillar of Ice: rising, standing (the 6th frame held), falling - 4 s from one play; the spikes at a champion's feet
    "e_pillar": ("e_pillar", "bottom", seq(range(8), _RISE + [PILLAR_T - sum(_RISE) - sum(_FALL)] + _FALL), [GROUND]),
    "e_hit": ("e_hit", "bottom", seq(range(4), [50, 70, 90, 110]), [GROUND]),
    # Subjugate: the seizing, every drain, the shackles while it drains, the broken shield over its head
    "r_hit": ("r_hit", "bottom", seq(range(5), [50, 60, 80, 100, 120]), [GROUND]),
    "r_tick": ("r_tick", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "r_chain": ("r_chain", "bottom", loop(6, 167), [GROUND]),
    "r_sap": ("r_sap", "bottom", loop(4, 150), [OVER]),
}


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        if not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return [odd(c, name) for c in out]


def manifest(src, redo=REDO):
    """{name: its manifest entry, pixel_1x = its picture}: the delivery's, the redraws' (REDO) in place of theirs."""
    meta = {}
    for folder in (src, redo):
        if not os.path.isfile(lp(os.path.join(folder, "manifest.json"))):
            continue
        man = json.load(open(lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig"))
        if isinstance(man, dict):                 # a delivery shaped {"schema_version", ..., "effects": [...]}
            man = man.get("effects") or man.get("items")
        for e in man:
            f = os.path.basename(e["file"])
            name = f[:-4].replace("trundle_fx_", "")
            meta[name] = dict(e, pixel_1x=os.path.join(folder, "pixel_1x", f))
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
    tables = {"league_trundle_fx": {}, "league_trundle_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_trundle_big" if tag in BIG else "league_trundle_fx"][tag] = out
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
