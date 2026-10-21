#!/usr/bin/env python3
"""league_naafiri's action frames: her approved 3/4 design and Codex's key poses after League's clips, with her pack
drawn into every frame (the user, 2026-10-21: 「做附加包啊 4也做」 - the packmates follow her; no add-on draws a sprite of
its own beside a unit, so they are part of her frames and turn, stand and run with her).

    python tools/art/rig_naafiri.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_naafiri.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (PPU 1.5, one palette; tools/art/design_naafiri_model.py and design_naafiri_poses.py):
  hd/idle.png         her, 3/4 front facing right, 77 x 45 (30 game px): the idle, the hit;
  hd/pack.png         a packmate, 49 x 24 (16 game px): the pack standing;
  hd/pose_<name>.png  Codex's key poses read back at the design's size (assets/source/naafiri/POSE_PROMPTS.md): hers
                      crouch rear lunge fling flare dash rise howl lie run1-4 (the design's head pasted on all but the
                      crouch, the rear, the rise and the howl), the packmate's p_run1-4 p_bite.
Placing a pose: one with the design's head (its json's head_at) keeps the head box where the idle has it, moved dx -
the head steady and the body moving behind it, as a hound runs; one without (NOHEAD) keeps its hind paws (the leftmost
square of its two bottom rows) where the idle's are - the hind legs planted as it rears or howls; both stand with their
lowest square on the ground, or `lift` squares over it.
The pack: two packmates trail her (PACK: the far one higher and behind her, drawn first; the near one lower, drawn over
her hind legs), standing, galloping half a stride apart, diving in with her bite; the p4_* tags (The Call of the Pack,
the add-on's view hook) have four (PACK4). They go when she dies (League's packmates vanish with her).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "naafiri"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "naafiri", "hd")
STAND = 40                     # the idle's standing column: under the body's middle, between the hind and fore legs
HEAD = (49, 17)                # the head box's top-left square in hd/idle.png (design_naafiri_poses.DESIGN)
P_HEAD = (33, 4)               # the packmate's in hd/pack.png
P_STAND = 24                   # the packmate's middle column
NOHEAD = {"crouch", "rear", "rise", "howl"}
# the pack: (column of the packmate's middle from her standing column, rows its ground lies under hers (negative: higher,
# farther), drawn over her) - two, and four in The Call of the Pack
# (the near one's head ends just behind her hind legs, the far one higher and farther back, only her tail over it: on
# top of her the three reds ran into one mass, the first review; 8 rows apart the two packmates read as one with two
# heads, the second)
PACK = [(-60, -12, False), (-44, 2, True)]
PACK4 = [(-84, -9, False), (-60, -13, False), (-44, 2, True), (-70, 5, True)]
RUN_BACK = 12                  # her gallop and lunge are longer behind her head than the idle: the pack that much farther
DASH_BACK = 24                 # her flat dash longer still (105 squares): the pack running that far behind her


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def head_at(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["head_at"]


def hind_x(a):
    """The leftmost square of the figure's two bottom rows (the hind paws)."""
    ys, xs = np.nonzero(a[..., 3] > 0)
    bottom = ys.max()
    return int(xs[ys >= bottom - 1].min())


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        self.pack = load("pack.png")
        self.poses = {n[5:-4]: load(n) for n in sorted(os.listdir(lp(SRC))) if n.startswith("pose_") and n.endswith(".png")}
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(110, 40, 50, 12))    # room for the pack behind her, the rear and the howl above
        self.outline = D.outline
        self.idle_hind = hind_x(d)

    def blank(self):
        return self.rig.canvas()

    def stamp(self, can, a, x0, y0):
        ys, xs = np.nonzero(a[..., 3] > 0)
        ty, tx = ys + y0, xs + x0
        ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
        can[ty[ok], tx[ok]] = a[ys[ok], xs[ok]]
        return can

    def her_at(self, name, dx=0, lift=0, breath=0):
        """(picture, its top-left canvas square) for her design ('idle') or a pose."""
        CX, GY = self.rig.CX, self.rig.GY
        if name == "idle":
            a = self.d
            if breath:                                   # the rows above the legs set down `breath` rows (Mel's rule)
                a = breathe(a, breath)
            x0 = CX - STAND + dx
        else:
            a = self.poses[name]
            if name in NOHEAD:
                x0 = CX - STAND + self.idle_hind - hind_x(a) + dx
            else:
                hx, _ = head_at(name)
                x0 = CX - STAND + HEAD[0] - hx + dx
        ys = np.nonzero(a[..., 3] > 0)[0]
        y0 = GY - 1 - ys.max() - lift
        return a, x0, y0

    def mate_at(self, name, slot, dx=0, lift=0, breath=0):
        """A packmate: the design ('pack', `breath` rows set down onto its legs) or a pose, at its slot (column from her
        standing point, rows under her ground)."""
        CX, GY = self.rig.CX, self.rig.GY
        sx, sy, _ = slot
        if name == "pack":
            a = breathe(self.pack, breath, P_LEG_TOP) if breath else self.pack
            x0 = CX + sx - P_STAND + dx
        else:
            a = self.poses[name]
            hx, _ = head_at(name)
            x0 = CX + sx - P_STAND + P_HEAD[0] - hx + dx
        ys = np.nonzero(a[..., 3] > 0)[0]
        y0 = GY - 1 - ys.max() + sy - lift
        return a, x0, y0

    def frame(self, her, mates=(), slots=PACK, flash=False):
        """her = (name, dx, lift, breath); mates = one (name, dx, lift[, breath]) per slot (None: not drawn)."""
        can = self.blank()
        front = []
        for slot, m in zip(slots, mates):
            if m is None:
                continue
            a, x0, y0 = self.mate_at(m[0], slot, *m[1:])
            if slot[2]:
                front.append((a, x0, y0))
            else:
                self.stamp(can, a, x0, y0)
        a, x0, y0 = self.her_at(*her)
        self.stamp(can, a, x0, y0)
        for a, x0, y0 in front:
            self.stamp(can, a, x0, y0)
        return hit_white(can) if flash else can


def breathe(a, k, leg_top=None):
    """Everything above the leg tops (LEG_TOP, the packmate's P_LEG_TOP) set down k rows onto the legs; the legs
    untouched."""
    leg_top = LEG_TOP if leg_top is None else leg_top
    out = a.copy()
    top = a.copy()
    top[leg_top:] = 0
    out[:leg_top] = 0
    sh = np.zeros_like(top)
    sh[k:] = top[:top.shape[0] - k]
    m = sh[..., 3] > 0
    out[m] = sh[m]
    return out


LEG_TOP = 31                   # hd/idle.png's first row of legs under the belly
P_LEG_TOP = 15                 # hd/pack.png's


def hit_white(can, k=0.45):
    """ppu_rig.flash keeping the outline dark (rig_shyvana.hit_white)."""
    import strips
    out = can.copy()
    m = (out[..., 3] > 0) & (strips.lum(out[..., :3]) >= 70)
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_naafiri.py) come from these (a frame's start in ticks = ms x 0.06)
# (attack: the lunge, the bite, starts at 170 ms = tick 10.2 -> a_hit 11, 25 ticks in all = atk_dur; skill and the
# second dagger: the fling from 90 ms = tick 5.4, the dagger let go mid-leap -> q_rel / q2_rel 7, 25 ticks = q_dur /
# q2_dur; skill2: 30 ticks = e_dur, the rise (the first shred) from tick 10.8; ult: 400 ms = r_roar 24; ult_b: 28 ticks
# = r_dur, the bite from 250 ms)
MS = {"idle": [150] * 8, "run": [110] * 4, "attack": [70, 100, 100, 90, 60], "hit": [100, 100],
      "dead": [120, 220, 260, 600], "skill": [90, 120, 110, 100], "skill2": [90, 90, 110, 110, 100],
      "ult": [80, 160, 160], "ult_b": [70, 90, 90, 110, 100]}


def actions(C, slots):
    """{tag: [canvas]} with the pack in `slots`."""
    n = len(slots)
    back = [(x - RUN_BACK, y, front) for x, y, front in slots]
    f = lambda her, mates, **k: C.frame(her, mates, slots, **k)
    g = lambda her, mates, **k: C.frame(her, mates, back, **k)      # the stretched poses: the pack farther back
    far = [(x - DASH_BACK, y, front) for x, y, front in slots]
    h = lambda her, mates, **k: C.frame(her, mates, far, **k)       # the dash: the pack left behind
    breaths = (0, 0, 1, 1, 1, 1, 0, 0)
    # the packmates breathe too, each a quarter of the cycle after the one before (her phase + 2 + 2i)
    idle_m = lambda k: [("pack", 0, 0, breaths[(k + 2 + 2 * i) % 8]) for i in range(n)]
    run_m = lambda k: [(f"p_run{(k + 2 * i) % 4 + 1}", 0, 0) for i in range(n)]
    bite_m = [("p_bite", 0, 0)] * n
    out = {}
    # idle (League's Idle: she stands low, breathing; the pack beside her)
    out["idle"] = [f(("idle", 0, 0, b), idle_m(k)) for k, b in enumerate(breaths)]
    # run (League's Run: the four phases of the gallop; the pack galloping half a stride apart)
    out["run"] = [g((f"run{k + 1}", 0, 2 if k == 3 else 0, 0), run_m(k)) for k in range(4)]
    # attack (League's attack1: gathered, rearing with the jaws wide, the lunge and bite - the hit - held, back)
    out["attack"] = [f(("crouch", 0, 0, 0), idle_m(0)), f(("rear", -2, 0, 0), idle_m(0)),
                     g(("lunge", 6, 0, 0), bite_m), g(("lunge", 5, 0, 0), bite_m), f(("idle", 0, 0, 0), idle_m(0))]
    out["hit"] = [f(("idle", -2, 0, 0), idle_m(0), flash=True), f(("idle", -1, 0, 0), idle_m(0))]
    # death (League's Death: the howl, falling onto her side; the pack gone with her)
    out["dead"] = [f(("howl", -2, 0, 0), idle_m(0), flash=True), f(("howl", -2, 0, 0), [None] * n),
                   f(("lie", 0, 0, 0), [None] * n), f(("lie", 0, 0, 0), [None] * n)]
    # Q Darkin Daggers (League's Spell1: gathering, leaping up with the head whipped down to fling the dagger - the
    # release - landing gathered, back)
    out["skill"] = [f(("crouch", 0, 0, 0), idle_m(0)), f(("fling", 2, 10, 0), run_m(0)),
                    f(("flare", 2, 0, 0), run_m(1)), f(("idle", 0, 0, 0), idle_m(0))]
    # E Eviscerate (League's Spell3: the dash onto the target, rearing to shred, the second shred, back)
    out["skill2"] = [h(("dash", 4, 3, 0), run_m(0)), h(("dash", 6, 2, 0), run_m(1)), f(("rise", 2, 0, 0), run_m(2)),
                     g(("lunge", 4, 0, 0), bite_m), f(("idle", 0, 0, 0), idle_m(0))]
    # R opened by W: The Call of the Pack (the howl; the add-on doubles the pack from here on)
    out["ult"] = [f(("crouch", 0, 0, 0), idle_m(0)), f(("howl", 0, 0, 0), idle_m(0)), f(("howl", 0, 1, 0), idle_m(0))]
    # Hounds' Pursuit (League's Spell2: pressed low with the blades fanned, the flat dash, the bite on landing, back)
    out["ult_b"] = [g(("flare", 0, 0, 0), idle_m(0)), h(("dash", 6, 4, 0), run_m(0)), h(("dash", 8, 2, 0), run_m(1)),
                    g(("lunge", 8, 0, 0), bite_m), f(("idle", 0, 0, 0), idle_m(0))]
    return out


def frames(C, tags=None):
    out = {}
    for prefix, slots in (("", PACK), ("p4_", PACK4)):
        for tag, cans in actions(C, slots).items():
            name = prefix + tag
            if tags and name not in tags:
                continue
            ms = MS[tag]
            if len(cans) != len(ms):
                sys.exit(f"{name}: {len(cans)} frames for {len(ms)}")
            out[name] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()
