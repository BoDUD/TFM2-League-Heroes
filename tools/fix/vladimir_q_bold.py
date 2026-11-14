#!/usr/bin/env python3
"""Vladimir's Transfusion (Q) pictures drawn bolder (the user, 2026-11-14: 「吸血鬼的Q技能特效几乎看不出 要加粗点吧」).

    python -I tools/fix/vladimir_q_bold.py           # make the Q tags bold (only from the frames it knows)
    python -I tools/fix/vladimir_q_bold.py --check   # fail unless the sheet holds the bold frames

league/effects/league_vladimir_fx: the Q tags - q1 (the splash where it lands), q_drain (on the target), q_orb (the blood
coming back to him), q_heal (on him), q_rush (the empowered one) - and their hd_ twins. They were 1x drawings with lines a
pixel thick: q_orb is 17 x 7 game px, a red streak on the green grass, 「几乎看不出」. Now each 1x frame grows a pixel on
every side and its shape a pixel outward (4-neighbour: a 1-px line becomes 3 px wide), the new ring in the darkest colour
the tag already has (no colour made up: q1 / q_drain / q_orb / q_rush their dark crimson 120,6,20 - which also edges the
red against the grass - q_heal its own red 240,24,40); the frame's own pixels stay on top. The hd_ frames are the bold
1x frames Scale2x'd (densify_fx.scale2x, what every effect tag no redraw replaced is), so a later densify run gives the
same hd_ frames back. Every other tag of the sheet, every duration and every frame count stays as it is; the frames
grow symmetrically, so they stay centred where they are drawn. league.dll embeds the fanim (league_main/src/fx_ppu.rs):
rebuild it with the sheet.

The script knows the original frames by hash: the originals -> written; already bold -> nothing; anything else -> it
stops (redo by hand). --check is the CI kind.
"""
import argparse
import hashlib
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "art"))
import densify_fx as D  # noqa: E402

STEM = os.path.join(ROOT, "league", "effects", "league_vladimir_fx")
TAGS = ("q1", "q_drain", "q_orb", "q_heal", "q_rush")


def digest(frames):
    h = hashlib.sha256()
    for a, ms in frames:
        h.update(repr((a.shape, ms)).encode())
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:16]


def darkest(frames):
    """the tag's darkest opaque colour (by luminance)"""
    cols = {tuple(int(v) for v in px) for a, _ in frames for px in a.reshape(-1, 4) if px[3] == 255}
    return min(cols, key=lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2])


def bold(a, ring):
    """a 1x frame a pixel bigger on every side, its shape a pixel thicker (4-neighbour), the new pixels `ring`"""
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    m = p[:, :, 3] > 0
    grown = m.copy()
    grown[1:, :] |= m[:-1, :]
    grown[:-1, :] |= m[1:, :]
    grown[:, 1:] |= m[:, :-1]
    grown[:, :-1] |= m[:, 1:]
    out = p.copy()
    new = grown & ~m
    out[new] = np.array(ring, np.uint8)
    return out


def bold_tags(tags):
    """{tag: frames} for the Q tags and their hd_ twins, made bold from the given (original) 1x frames"""
    out = {}
    for t in TAGS:
        ring = darkest(tags[t])
        b = [(bold(a, ring), ms) for a, ms in tags[t]]
        out[t] = b
        old_hd = tags["hd_" + t]
        assert len(old_hd) == len(b), t
        out["hd_" + t] = [(D.scale2x(a), ms) for (a, _), (_, ms) in zip(b, old_hd)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    tags = D.load_sheet(STEM)
    now = {t: digest(tags[t]) for t in TAGS}
    if all(now[t] == BOLD.get(t) for t in TAGS):
        print("league_vladimir_fx: the Q tags are bold already")
        return
    if a.check:
        sys.exit(f"league_vladimir_fx: the Q tags are not the bold ones ({now}) - run tools/fix/vladimir_q_bold.py")
    if any(now[t] != ORIGINAL[t] for t in TAGS):
        sys.exit(f"league_vladimir_fx: the Q tags are neither the originals nor the bold ones ({now}) - redo by hand")
    new = bold_tags(tags)
    for t, frames in new.items():
        tags[t] = frames
    D.G.write_sheet(D.G.lp(STEM), tags, share=True)
    print("league_vladimir_fx: Q tags made bold:", {t: [f[0].shape[:2] for f in new[t]][:2] for t in TAGS})
    print("bold digests:", {t: digest(new[t]) for t in TAGS})


# the 1x frames (shape, duration, pixels) the script starts from, and what it makes of them
ORIGINAL = {"q1": "e7f3c242f675991f", "q_drain": "956746b1f2985c91", "q_orb": "6ec757e763a05e0b", "q_heal": "fad12b810d51a78a", "q_rush": "96015de7c4af7f49"}
BOLD = {"q1": "b67907bacda0f8f1", "q_drain": "ba03f26c8f21399b", "q_orb": "ad33392937cfc6d0", "q_heal": "017141e089a28e8c", "q_rush": "c2637d458caf3b21"}

if __name__ == "__main__":
    main()
