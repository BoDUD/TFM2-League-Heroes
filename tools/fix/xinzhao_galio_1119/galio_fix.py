"""league_galio (the user, 2026-11-19: 「接下来改加里奥吧 走路时翅膀不动 待机也是」, then 「这里腿部像素缺失没处理？还有走路
会出来不干净的黑边也没清理」): his 8 run frames get wings that flap (wings.py: the one wing pair all 8 frames carry,
lifted and turned +-4 deg about its root behind the shoulder by RotSprite, back behind the body) and their legs cleaned
(legclean.clean2: specks, the porous inner thigh filled or cleared by the 3 x 3 fill, outline closed, black on the
silhouette <= 2 squares from the stone; legs and feet only - the tail and the wings are left as drawn); a new tag idle_loop (+ hd_ / lo_) = the stance with its
own wings turning +-3 deg in 8 frames of 0.15 s, which hero_reels.py plays through the idle's holds ("hold"). 1x / lo_
frames and the strips as the pipeline makes them (sheetkit.py). One-off: refuses a sheet that has idle_loop.
    python -I galio_fix.py <repo>"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import legclean as LC  # noqa: E402
import sheetkit  # noqa: E402
import wings as WG  # noqa: E402

REPO = sys.argv[1]
k = sheetkit.Kit(REPO, "league", "galio")
if "idle_loop" in k.anims:
    sys.exit("league_galio already has idle_loop: this edit was made")


def polys(ox, oy):
    L = [(56, 26), (94, 26), (94, 56), (92, 56), (92, 64), (78, 64), (77, 70), (76, 92), (56, 92)]
    R = [(101, 26), (134, 26), (134, 92), (117, 92), (116, 70), (114, 64), (103, 64), (103, 56), (101, 56)]
    sh = lambda P: [(x + ox, y + oy) for x, y in P]
    return {"left": (sh(L), (86.0 + ox, 72.0 + oy)), "right": (sh(R), (108.0 + ox, 72.0 + oy))}


ref = k.cell("hd_run", 0)
T = WG.template(ref, polys(0, 0))
OFFS = [(0, 0), (0, -1), (0, -1), (0, -1), (0, 2), (0, 0), (0, -2), (0, -3)]
LEGS = (86, 88, 132, 124)        # from the left foot right: the tail (x 58-85: gold tip, grey stone under the thigh) is not touched
for i in range(8):
    c = k.cell("hd_run", i)
    ang = 4.0 * np.sin(2 * np.pi * i / 8)
    f = WG.flap(c, T, OFFS[i], {"left": -ang, "right": ang}, ref)
    g, info = LC.clean2(f, LEGS)
    # rows 88-91 right of the legs hold the right wing's lowest feathers: those stay as the flap left them
    for y in range(88, 92):
        for x in range(117, 133):
            g[y, x] = f[y, x]
    k.put("hd_run", i, g)
    print(f"run[{i}] wings {ang:+.1f} deg, legs {info}")
for i in range(8):
    k.derive("run", i)
k.strip("run")
st = k.cell("hd_idle_base", 0)
TS = WG.template(st, polys(1, -1))
loop = [(WG.flap(st, TS, (0, 0), {"left": -3.0 * np.sin(2 * np.pi * p / 8), "right": 3.0 * np.sin(2 * np.pi * p / 8)}, st), 0.15)
        for p in range(8)]
assert np.array_equal(loop[0][0], st), "the loop's frame 0 must be the stance"
k.add_tag("idle_loop", loop, k.cell("idle_base", 0).shape)
k.save()
k2 = sheetkit.Kit(REPO, "league", "galio")
k2.strip("idle_loop")
print("league_galio written:", {t: len(k2.anims[t]["frames"]) for t in ("hd_run", "hd_idle_loop", "idle_loop", "lo_idle_loop")})
