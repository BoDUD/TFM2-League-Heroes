#!/usr/bin/env python3
"""World Ender keeps Aatrox in the air for its whole length (the user, 2026-10-04: 「剑魔的大招应该一直在天上的吧？」;
2026-11-14, on the list of differences from League: 「全改吧」): the hover frames league.dll's LOOKS row plays instead of
idle / run / hit / ult while `league_aatrox_r` is on him (addons/league_main/src/looks.rs), and his R casts kept off the
ground between them - all of it his own approved frames moved whole.

    python tools/art/hover_aatrox.py            # rewrite league/champions/league_aatrox#sheet.png and #anim.fanim
    python tools/art/hover_aatrox.py --check    # exit 1 when the sheet is not what this writes
    python tools/art/hero_reels.py --hero aatrox && python tools/art/hover_aatrox.py   # then: r_idle's reel, repacked

Why it was on the ground. tools/art/air_aatrox.py (2026-10-04) rebuilt the R casts airborne (League's ULT clips: the
feet 39-117 units over the floor, only the Q slams touching down), but the game plays idle / run / hit by name and the
kit could not swap them, so every cast took off from the ground and landed on it, and between casts he stood with the
wing loop `league_aatrox_r_look` drew behind him on his standing point (league_aatrox_big r_aura, 1x art).

The hover pose is REST, the last frame of every R cast: Codex's PPU redraw (2026-11-03, rig_aatrox_hd.py) of
air_aatrox's REST - his idle with the loop's wings spread at rest; its body the idle's own, square for square at the
same rows (the head's top, the chest core and the soles where the idle has them). Lifted HOVER_HD dense px (7.03 game
px, 16 at PPU 91/40): the airborne frames of his attacks fight 6-7.4 game px up (their chest core 17.5-20.0 game px over
the pivot against the idle's 12.6; REST lifted: 19.1). Every frame here is an existing frame moved whole by whole pixels
of its own density (1x, hd_, lo_: 7, 16 and 11 px for the hover) - nothing redrawn, turned or rescaled, so the body is
exactly the size it is everywhere else (「模型不要变大变小」).

- r_idle: REST lifted, held still (idle_base's timing; tools/art/hero_reels.json `"r_idle": []` makes r_idle the held
  frame 0 and keeps this drawn one as r_idle_base) - it hovers, it does not bob (「上下摆动全不要了啊」);
- r_run: REST lifted, still, at run's timing: he glides, the unit moving under him;
- r_hit: REST lifted and pushed back HIT_BACK game px, the first frame flashed as his own hit's first (ppu_rig.flash
  inside the outer band of his outline, which stays dark as there);
- the R casts: every frame of attack_r, attack_p_r and skill2_r lower than the hover raised to it (they took off and
  landed: he would dip to the ground at every attack); the Q casts (skill_r, q2_r, q3_r) only before the swing, frames
  1-2 (their copies with E's dash, *_r_fx*, start at 300 ms in frame 3 and are left alone) - the slam and the REST after
  it stay on the ground as drawn (League: only the Q slams touch down). Played only under R, they change in place.
- r_ult: the transformation rising as drawn and settling on the hover, frames 6-8, instead of landing. `ult` itself
  stays as drawn - the ban/pick card and the idle reel play it (it would end in the air and drop to the standing
  idle there); the LOOKS row swaps it for r_ult in game (`league_aatrox_r` comes on in the tick the kit plays `ult`,
  and frames 1-5 are the same frames).
- the wings: REST carries Codex's spread wings, so the kit's view of `league_aatrox_r_look` (the 1x wing loop on his
  standing point, 7 game px under the hovering shoulders and a second pair of wings) is gone from the main pack's
  league_aatrox.data_champion and league_aatrox_chain's copy; the buff stays (the attack tree that gives it is frozen).

A cast frame is raised to the hover by the lowest opaque row: the frame's soles line (its centre + FEET game px) to it,
against the idle's plus the hover, never lowered. The drawn hover idle is `r_idle_base` once hero_reels has made the
reel, else `r_idle`. The sheet is written packed with identical frames sharing their squares (strips.write_sheet share),
so a repack leaves no square behind.
"""
import argparse
import os
import sys

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402
import ppu_rig as R  # noqa: E402

HERO = "aatrox"
PPU = P.PPU[HERO]
DENSITY = {"": 1.0, P.PREFIX: PPU, P.LO: P.UI_PPU}           # pixels a game pixel: 1x, hd_, lo_
FEET = R.FEET                                                 # game px from a frame's centre down to the soles line
HOVER_HD = 16                                                 # dense px: 7.03 game px
HOVER = HOVER_HD / PPU
REST = ("attack_r", -1)                                       # the last frame of every R cast
LIFT_ALL = ("attack_r", "attack_p_r", "skill2_r")
LIFT_SOME = {"skill_r": (0, 1), "q2_r": (0, 1), "q3_r": (0, 1)}
ULT_SETTLE = (5, 6, 7)                                        # r_ult's frames on the hover (from 0)
HIT_BACK = (2.0, 1.0)                                         # game px r_hit's two frames are pushed back
# his outline colour and its outer band's depth in dense px (ppu_restyle's outline round the figure): his own hit's
# flash frame keeps that band dark and whitens what is inside it
OUTLINE = (11, 2, 13)
OUTLINE_HD = 3
# the hover tags and the tags whose timing they take; they go in after idle_base (the last plain tag)
NEW = {"r_idle": "idle_base", "r_run": "run", "r_hit": "hit", "r_ult": "ult"}
AFTER = "idle_base"


def px(n, k):
    """`n` game px in pixels of density k (whole)."""
    return int(round(n * k))


def feet(a, k):
    """Pixels from the frame's soles line (its centre + FEET game px) up to under its lowest opaque row (negative:
    something hangs below the soles line)."""
    rows = np.nonzero((a[..., 3] > 0).any(1))[0]
    return a.shape[0] / 2.0 + FEET * k - (rows.max() + 1)


def lift(a, n):
    """The frame's picture n pixels higher about its centre (the pivot): n more rows at both ends, the picture at the top."""
    n = int(n)
    if n <= 0:
        return a
    out = np.zeros((a.shape[0] + 2 * n, a.shape[1], 4), np.uint8)
    out[:a.shape[0]] = a
    return out


def back(a, n):
    """The frame's picture n pixels further back (left: he faces right) about its centre."""
    n = int(n)
    if n <= 0:
        return a
    out = np.zeros((a.shape[0], a.shape[1] + 2 * n, 4), np.uint8)
    out[:, :a.shape[1]] = a
    return out


def flash_inside(a, k):
    """ppu_rig.flash (his hit's first frame) inside the outline: the outer band of his outline colour - OUTLINE_HD dense
    px, as many game px at the other densities - stays dark, as in his own hit's flash frame."""
    out = R.flash(a)
    op = a[..., 3] > 0
    depth = ndimage.distance_transform_cdt(np.pad(op, 1), metric="taxicab")[1:-1, 1:-1]
    keep = op & (depth <= max(1, px(OUTLINE_HD / PPU, k))) & (a[..., :3] == OUTLINE).all(-1)
    out[keep] = a[keep]
    return out


def build(sheet):
    """{tag: [(frame, ms)]} of the tags this writes (the lifted casts and the hover tags at every density) from `sheet`
    (ppu_hd.read_sheet)."""
    idle_tag = "r_idle_base" if "r_idle_base" in sheet else "r_idle"
    out = {}
    for pre, k in DENSITY.items():
        target = feet(sheet[pre + "idle_base"][0][0], k) + px(HOVER, k)
        for tag in LIFT_ALL + tuple(LIFT_SOME):
            frames = list(sheet[pre + tag])
            for i in (range(len(frames)) if tag in LIFT_ALL else LIFT_SOME[tag]):
                a, ms = frames[i]
                frames[i] = (lift(a, round(target - feet(a, k))), ms)
            out[pre + tag] = frames
        hover = out[pre + REST[0]][REST[1]][0]
        for tag, timing in NEW.items():
            ms = [m for _, m in sheet[timing]]
            if tag == "r_hit":
                out[pre + tag] = [(flash_inside(back(hover, px(HIT_BACK[0], k)), k), ms[0]),
                                  (back(hover, px(HIT_BACK[1], k)), ms[1])]
            elif tag == "r_ult":
                ult = sheet[pre + "ult"]
                out[pre + tag] = [(lift(a, round(target - feet(a, k))) if i in ULT_SETTLE else a, m)
                                  for i, (a, m) in enumerate(ult)]
            else:
                out[pre + (idle_tag if tag == "r_idle" else tag)] = [(hover, m) for m in ms]
    return out


def merged(sheet, made):
    """The sheet with `made` in: the tags it has in place, the new ones after idle_base / hd_idle_base / lo_idle_base."""
    out = {}
    for tag, frames in sheet.items():
        out[tag] = made.get(tag, frames)
        for pre in DENSITY:
            if tag == pre + AFTER:
                for new in made:
                    if new not in sheet and new.startswith(pre) and (pre or not new.startswith((P.PREFIX, P.LO))):
                        out[new] = made[new]
    missing = [t for t in made if t not in out]
    if missing:
        sys.exit(f"nowhere to put {missing}")
    return out


def same(a, b):
    return a.shape == b.shape and np.array_equal(a, b)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when the sheet differs")
    a = ap.parse_args()
    stem = P.stem_of(HERO)
    sheet = P.read_sheet(stem)
    made = build(sheet)
    if a.check:
        bad = []
        for tag, frames in made.items():
            have = sheet.get(tag)
            if have is None:
                bad.append(f"{tag}: not in the sheet")
            elif len(have) != len(frames) or any(not same(x, y) or abs(m - n) > 1e-6
                                                 for (x, m), (y, n) in zip(have, frames)):
                bad.append(f"{tag}: frames differ")
        print("\n".join(bad) if bad else f"league_{HERO}: the hover tags and the raised R casts are as written")
        sys.exit(1 if bad else 0)
    out = merged(sheet, made)
    w, h = P.G.write_sheet(stem, out, share=True)
    lifted = {t: [i + 1 for i, ((x, _), (y, _)) in enumerate(zip(sheet[t], made[t])) if not same(x, y)]
              for t in made if t in sheet and not t.startswith(("r_", P.PREFIX + "r_", P.LO + "r_"))}
    print(f"league_{HERO}#sheet.png {w}x{h}: hover {px(HOVER, 1)} / {HOVER_HD} / {px(HOVER, P.UI_PPU)} px (1x / hd_ / lo_); "
          + "; ".join(f"{t} raised {v}" for t, v in lifted.items() if v and not t.startswith((P.PREFIX, P.LO)))
          + "; " + ", ".join(t for t in made if t.startswith("r_")))


if __name__ == "__main__":
    main()
