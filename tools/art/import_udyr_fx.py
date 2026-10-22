#!/usr/bin/env python3
"""Import Udyr's effects (assets/source/udyr/PROMPTS_FX.md, 24 pictures) as the game sheets league_udyr_fx and
league_udyr_big.

    python tools/art/import_udyr_fx.py [--review out.png]

The source is the step-3 delivery (assets/source/udyr/codex_fx/udyr_fx: pixel_1x/udyr_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json's effects (cell_1x); alpha 0 / 255). The lightning ball and the
released storm are projectiles (the game turns them to their flight: flying left they turn upside down, so they must be
symmetric top to bottom); the forward pictures q_swipe and e_trail sit in league_udyr_fx too but no view plays them: the
rig draws them into his own frames (assets/source/native/udyr_bake.json, ppu_rig.Rig.bake - they turn with him, the red
side included); every other picture is symmetric left to right (the client never mirrors it on the red side) - all
checked again here. A symmetric picture an even number of squares across gets its middle column (a projectile: its
middle row) twice (import_shyvana_fx.odd: the game mirrors and turns about the pivot's square, so only an odd width lies
even about it). Each frame is cut by the manifest's frame
size and placed as the kit plays it (import_naafiri_fx.py's way): spots are game px from the pivot (x forward, y down); a
unit's soles are 11 under it, a point's ground too. His own pictures are centred on his standing point (the middle of his
belt's plaque). Which sheet an effect goes to is read from the kit's own views (build_udyr.build), so the two never
disagree.
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
import build_udyr as K  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "udyr", "codex_fx", "udyr_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)
P = K.P


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"q_bolt", "r_rel"}             # projectiles: turned to their flight by the game
FORWARD = {"q_swipe", "e_trail"}     # drawn into his own frames (bake), no view
HIT = (0, -14)                       # a hit on the upper body of a 36-px unit
SOLES = (0, 11)                      # on the ground under a unit or a point
OVERHEAD = (0, -29)                  # over a 36-px unit's head
FLIGHT = (0, 0)                      # a projectile's own point
HIM = (0, 11)                        # his soles under his standing point
CHEST = (0, -14)                     # his chest
# over his head in each stance (the plain guard 40 game px tall, the bear 41, the ram 46 with its horns, the phoenix 49
# with its swept-up hair): the sigil's middle 9 px over his top
OVER_Q, OVER_E, OVER_R = (0, -39), (0, -44), (0, -47)
HALO_E = (0, -37)                    # just over the ram's head, under the horns' tops
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom row), frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    # the spirits' sigils over his head as he enters a stance; the awakenings round him (his feet 2 rows up the cell)
    "q_on": ("core", seq(range(5), [50, 60, 70, 80, 90]), [OVER_Q]),
    "e_on": ("core", seq(range(5), [50, 60, 70, 80, 90]), [OVER_E]),
    "r_on": ("core", seq(range(5), [50, 60, 70, 80, 90]), [OVER_R]),
    "q_wake": (("feet", 2), seq(range(6), [50, 60, 60, 70, 80, 90]), [HIM]),
    "e_wake": (("feet", 2), seq(range(6), [50, 60, 60, 70, 80, 90]), [HIM]),
    # the bear's claws and lightning
    "q_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "q_bolt": ("core", loop(4, 50), [FLIGHT]),
    "q_bolt_hit": (("feet", 3), seq(range(5), [40, 50, 60, 70, 80]), [SOLES]),
    # the ram's blow
    "e_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    # the phoenix's storm
    "r_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    "r_rel": ("core", loop(4, 70), [FLIGHT]),
    "r_rel_hit": ("core", seq(range(6), [50, 60, 70, 80, 90, 100]), [(0, -10)]),
    # Iron Mantle (the boar, in the passive): the shell closing round him, the heal on his chest
    "w_on": (("feet", 2), seq(range(6), [60, 70, 70, 80, 90, 100]), [HIM]),
    "w_heal": ("core", seq(range(4), [60, 70, 80, 90]), [CHEST]),
    # buffs, looped while they hold
    "q_as": ("core", loop(4, 110), [HIM]),
    "e_ms": ("core", loop(4, 100), [HIM]),
    "e_imm": ("core", loop(4, 120), [HALO_E]),
    "e_stun": ("core", loop(4, 110), [OVERHEAD]),
    "r_storm": (("feet", 4), loop(6, 80), [HIM]),
    "r_slow": ("core", loop(4, 120), [SOLES]),
    "w_sh": (("feet", 2), loop(4, 110), [HIM]),
    # drawn into his frames (udyr_bake.json): the bear's three claw streaks from his raking paw (the cell's left middle on
    # the paw's sweep, in front of his chest), the ram's fire trail lying behind his feet (the cell's bottom right on them)
    "q_swipe": (("pt", 0, 12), seq(range(3), [40, 50, 60]), [(17, -11)]),
    "e_trail": (("pt", 35, 17), loop(4, 110), [(2, 11)]),
}


def sheets_of_kit():
    """{effect: "league_udyr_fx" or "league_udyr_big"} as the kit's views name them (the baked ones in the small sheet)."""
    kit = K.build(dict(P))
    out = {}
    for group in ("view_projectiles", "view_effects", "view_buffs"):
        for v in kit[group]:
            out[v["tag"]] = v["anim"].rsplit("/", 1)[1]
    for name in FORWARD:
        out[name] = "league_udyr_fx"
    return out


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        if name not in FORWARD:
            mirror = c[::-1] if name in TB else c[:, ::-1]
            if not (c == mirror).all():
                sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in TB else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return [odd(c, name) for c in out]


def odd(c, name):
    """A symmetric picture an even number of squares across gets its middle column (a projectile: its middle row)
    twice (import_shyvana_fx.odd)."""
    if name in FORWARD:
        return c
    ax = 0 if name in TB else 1
    n_ = c.shape[ax]
    if n_ % 2:
        return c
    return np.insert(c, n_ // 2, np.take(c, n_ // 2, axis=ax), axis=ax)


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind[0] == "pt":
        return [kind[1], kind[2]]
    return [(w - 1) / 2, h - 1 - kind[1]]


def delivered():
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man["effects"]:
        name = os.path.basename(e["file"])[len("udyr_fx_"):-len(".png")]
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", os.path.basename(e["file"])))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = delivered()
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the importer's {sorted(FX)}")
    sheet_of = sheets_of_kit()
    if set(sheet_of) != set(FX):
        sys.exit(f"the kit's views {sorted(sheet_of)} against the importer's {sorted(FX)}")
    for name, (_, frames, _) in FX.items():
        if any(k >= meta[name]["frames"] for k, _ in frames if k != J.EMPTY):
            sys.exit(f"{name}: a frame past the delivered {meta[name]['frames']}")
    allc = {n: cells(n, meta[n]) for n in meta}
    tables = {"league_udyr_fx": {}, "league_udyr_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables[sheet_of[name]][name] = out
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
