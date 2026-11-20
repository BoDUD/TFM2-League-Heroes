"""league_braum's run frames 0-3 after GPT's smaller shield (bdbda7d47): the outline round the cuts.

The old run[0..3] held a shield ~15 % bigger than run[4..7] and the idle; bdbda7d47 drew the smaller one in its place,
and where the big one had covered him his body now ends in a straight cut with no outline: the underside of his
forearm (a flat light row from the shoulder to the hand), the side of his chest under the arm (a flat light column), the
shield's own top-left bevel and a few squares round the gripping hand - 44-52 light squares on the edge of each frame,
where run[4..7], the idle and the attack have 0-1.

Here every such square (light, with a clear square beside it, not one the frame already had before bdbda7d47) gets the
hero's outline round it: the clear squares within KEEP (league_braum's hd_ outline: 2, tools/art/thin_outline.json) of
it take the outline colour, so the body keeps every square it had and shows the 2-square outline every other edge of his
has. The gap between his chest and the shield stays (in run[0..3] he holds the shield out further than in run[4..7]).

Under the shield's bottom-left corner each of those frames also kept a hook of the old shield's outline (the user:
「布隆盾牌下面有个黑边没处理干净」): a dark square one row under the left end of the bottom outline and a 4-square dash
to the left of it, hanging in the air (run[4..7] have none). HOOKS lists them; they are cleared. So are STRAYS (the user
then: 「腿上好像也有」): one-square-wide dark strokes run[4..7] and the frames before bdbda7d47 do not have - a 3-square
piece of the old shield's left edge standing beside his trousers in run[2], single squares on the shield's top outline
and its top-left bevel, a spur on run[0]'s boot toe; FILLS closes the notch that spur left in the toe's outline, and a
clear square with the figure on all four sides that bdbda7d47 left (a pinhole in the outline band under his forearm)
takes the darkest colour beside it.

The 1x and lo_ frames are not made anew (#784's own 1x frames are not pixel_down's: ~8 % of their squares differ from
it, so a fresh one would differ from run[4..7] all over): each is derived from the dense frame before and after
(tools/fix/xinzhao_galio_1119/sheetkit.py) and only the squares that differ between the two are written into it - the
outline at that scale. The strips are rewritten from the dense frames. Then
`python -I tools/art/thin_outline.py --hero league_braum` evens the lo_ outline as on every other frame.

    python tools/fix/gpt784_review/braum_run_outline.py
    python -I tools/art/thin_outline.py --hero league_braum
    python tools/fix/gpt784_review/braum_run_outline.py --check
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

FRAMES = (0, 1, 2, 3)
# light edge squares each frame had before bdbda7d47 (its own drawing: a hair-thin highlight on the head's outline):
# left as they are
OLD = {0: {(12, 63), (13, 81)}, 1: {(15, 57), (17, 84), (19, 40), (41, 86), (83, 66)}, 2: {(11, 66)},
       3: {(9, 60), (11, 78), (14, 93), (14, 94), (19, 108)}}


# the old shield's outline hanging under the new one's bottom-left corner: (x, y) per frame, all outline-dark
HOOKS = {0: [(100, 81), (97, 82), (98, 82), (99, 82), (100, 82)], 1: [(97, 82), (94, 83), (95, 83), (96, 83), (97, 83)],
         2: [(105, 80), (102, 81), (103, 81), (104, 81), (105, 81)], 3: [(97, 79), (94, 80), (95, 80), (96, 80), (97, 80)]}


# one-square-wide dark strokes left of the old shield / grown at the new one's bevel: (x, y) per frame, all outline-dark
STRAYS = {0: [(95, 30), (88, 79)], 1: [(126, 26), (92, 31)], 2: [(134, 24), (100, 29), (90, 52), (90, 53), (90, 54)],
          3: [(126, 23), (92, 28)]}
# outline squares to add: the toe's outline joined to the boot's once its spur is gone
FILLS = {0: [(87, 80)]}

def unhook(c, i):
    out = c.copy()
    for x, y in list(HOOKS.get(i, [])) + list(STRAYS.get(i, [])):
        if out[y, x, 3] > 0:
            if int(out[y, x, :3].max()) >= 40:
                sys.exit(f"run[{i}] ({x}, {y}) is not outline-dark: {out[y, x].tolist()}")
            out[y, x] = 0
    for x, y in FILLS.get(i, ()):
        if out[y, x, 3] == 0:
            out[y, x] = OUTLINE
    for y, x in np.argwhere(pinholes(out)):
        nb = [out[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))]
        out[y, x] = min(nb, key=lambda q: int(q[0]) + int(q[1]) + int(q[2]))
    return out


def pinholes(c):
    a = c[..., 3] > 0
    pad = np.pad(a, 1)
    return ~a & pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]


def outline_of():
    t = json.load(open(os.path.join(ROOT, "tools", "art", "thin_outline.json"), encoding="utf-8"))["league_braum"]
    return np.array(list(t["grow"]) + [255], np.uint8), int(t["hd"]["keep"])


OUTLINE = outline_of()[0]


def clear_beside(a):
    pad = np.pad(a, 1)
    return ~pad[:-2, 1:-1] | ~pad[2:, 1:-1] | ~pad[1:-1, :-2] | ~pad[1:-1, 2:]


def cuts(c, i):
    a = c[..., 3] > 0
    m = a & clear_beside(a) & (c[..., :3].astype(int).sum(-1) > 150)
    for y, x in OLD.get(i, ()):
        m[y, x] = False
    return m


def outline(c, i, colour, keep):
    out = c.copy()
    front = cuts(c, i)
    for _ in range(keep):
        pad = np.pad(front, 1)
        near = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
        new = near & ~(out[..., 3] > 0)
        out[new] = colour
        front = new
    return out


def main():
    k = Kit(ROOT, "league", "braum")
    if "--check" in sys.argv:
        bad = [i for i in FRAMES if cuts(k.cell("hd_run", i), i).any()]
        bad += [i for i in FRAMES if any(k.cell("hd_run", i)[y, x, 3] > 0 for x, y in HOOKS[i] + STRAYS[i])]
        bad += [i for i in FRAMES if any(k.cell("hd_run", i)[y, x, 3] == 0 for x, y in FILLS.get(i, ()))]
        bad += [i for i in FRAMES if pinholes(k.cell("hd_run", i)).any()]
        print("braum run outline: OK" if not bad else f"braum run outline: frames {sorted(set(bad))} still cut / hooked")
        sys.exit(1 if bad else 0)
    colour, keep = outline_of()
    for i in FRAMES:
        c = k.cell("hd_run", i)
        n = int(cuts(c, i).sum())
        new = unhook(outline(c, i, colour, keep), i)
        shape = k.cell("run", i).shape[:2]
        moved = []
        for pre, make in (("", k.one_of), ("lo_", k.lo_of)):
            old, a, b = k.cell(pre + "run", i), make(shape, c), make(shape, new)
            if a.shape != old.shape or b.shape != old.shape:
                sys.exit(f"run[{i}] {pre or '1x'}: derived {a.shape} / {b.shape} vs the sheet's {old.shape}")
            diff = (a != b).any(-1)
            old[diff] = b[diff]
            k.put(pre + "run", i, old)
            moved.append(f"{pre or '1x '}{int(diff.sum())}")
        print(f"run[{i}]: {n} cut squares, {int((new[..., 3] > 0).sum() - (c[..., 3] > 0).sum())} squares added (outline - hook)"
              f" (squares written: {', '.join(moved)})")
        k.put("hd_run", i, new)
    k.save()
    k.strip("run")


if __name__ == "__main__":
    main()
