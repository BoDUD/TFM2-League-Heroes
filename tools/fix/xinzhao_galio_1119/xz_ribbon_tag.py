"""league_xinzhao's hair ribbons flutter while he stands (the user, 2026-11-19: 「发带能动吗 动画效果」): a new tag idle_loop
(+ hd_ / lo_) = the ready stance with its two ribbon tails waved (ribbon.py: whole columns moved, root still, 2 px at the
tips) in 6 frames of 0.15 s; hero_reels.py plays it through the idle's holds ("hold"). One-off: refuses a sheet that
has idle_loop. Run after the spear edit (the stance it waves is the edited one).
    python -I xz_ribbon_tag.py <repo>"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ribbon as RB  # noqa: E402
import sheetkit  # noqa: E402

REPO = sys.argv[1]
k = sheetkit.Kit(REPO, "league", "xinzhao")
if "idle_loop" in k.anims:
    sys.exit("league_xinzhao already has idle_loop: this edit was made")
st = k.cell("hd_idle_base", 0)
loop = [(RB.wave(st, p, 6), 0.15) for p in range(6)]
k.add_tag("idle_loop", loop, k.cell("idle_base", 0).shape)
k.save()
k2 = sheetkit.Kit(REPO, "league", "xinzhao")
k2.strip("idle_loop")
print("league_xinzhao written:", {t: len(k2.anims[t]["frames"]) for t in ("hd_idle_loop", "idle_loop", "lo_idle_loop")})
