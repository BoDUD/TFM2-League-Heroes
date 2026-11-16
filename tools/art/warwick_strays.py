#!/usr/bin/env python3
"""league_warwick: every black square his drawn frames hold beyond his outline cleared from every tag (the user,
2026-11-16: 「狼人怎么有阴影冒出来好奇怪」, then 「狼人还是有冒出来的黑边啊」; 2026-11-17, on the first pass:
「狼人也没太处理干净 都重新再处理一遍」).

    python -I tools/art/warwick_strays.py                 # clear them: his sheet's frames (hd_, 1x, lo_), his strips and
                                                          # his run's sources
    python -I tools/art/warwick_strays.py --check         # exit 1 when a frame still holds one (CI)
    python -I tools/art/warwick_strays.py --review DIR    # each frame it changes: before / cleared (magenta) and filled
                                                          # (cyan) / after, x5, nothing written

His frames came from image-model poses (tools/art/rig_warwick.py, ppu_restyle.py, Codex's redrawn run): in some frames
of a tag, and not in the next, they hold black that is no part of his design (tools/art/design_warwick_model.py; his
prompts: no shadow, no effect) - read in the game as shadows popping in and out: a chain-like curve from his far hand's
claws to the ground, blots under his feet and claws, tufts round the tank on his back, specks on the ground, and black
filling the gaps between his parts - between his bracer arm and his body, his thighs, his far arm and his leg.
The first pass took only black two or more squares from every colour in pieces of some size at his edge, and kept the
gap by his bracer arm and the 1x frames' chain; now the rule is tools/art/black_strays.py's, the same at every density:
his outline colour (9, 1, 11) is an outline only within a square of another colour (dense and 1x frames; the lo_ frames
follow their clean dense frame); every square of it deeper goes, but the open mouth's inside (black with his gums or
tongue and his teeth both within two squares, MOUTH). What goes leaves ground where it is open to the ground round him,
and his fur where his pieces shut it in (a pocket inside his body: the design draws his body's fur behind the bracer
arm) - one shade a pocket, the commonest of his body's fur shades (FUR) within three squares of it, else the shadow
shade. On the 1x frames this leaves his outline one square (one game pixel) round every part, as on his dense frames,
where the drawing had two or three. The run tags are tools/art/run_body_anim.py's: their sources are cleaned here (the
drawn run, the kept 1x frames), run_body_anim.py --hero warwick lays them in and cleans each composed dense frame with
this rule too (its run data's `strays`: the laid tail closing a gap against the drawing left a square of black at its
apex). hero_reels' idle / bp reels are rects of these frames and need nothing; tools/art/illaoi_souls.py makes his
spirit from his idle again. Order: after rig_warwick.py / ppu_restyle.py / ppu_hd.py (they draw the black again),
before run_body_anim.py; thin_outline.py's pass runs inside (black_strays.clean), so thin_outline.py --check finds
nothing after it.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import black_strays as B  # noqa: E402

HERO = "league_warwick"
OUT = (9, 1, 11)
GUMS = [(249, 99, 118), (191, 61, 78), (160, 47, 62), (168, 57, 81)]      # his gums / tongue (his inner ears too)
TEETH = [(249, 250, 251)]                                                  # (his chest fur's highlight too)
MOUTH = 2
# his body's fur, darkest first (design_warwick_model.py's blues; the chest's pale ones left out): a pocket's shade
FUR = [(27, 27, 69), (40, 44, 107), (64, 77, 164), (87, 115, 216)]
SHADOW = (40, 44, 107)


class Warwick(B.Hero):
    ink = OUT
    pocket = "fill"

    def __init__(self):
        super().__init__(HERO)

    def protect(self, a, kind, ctx):
        """The open mouth's inside: black with his gums / tongue and his teeth both within MOUTH squares."""
        g, t = B.colour_mask(a, GUMS), B.colour_mask(a, TEETH)
        if not g.any() or not t.any():
            return np.zeros(a.shape[:2], bool)
        return B.dil8(g, MOUTH) & B.dil8(t, MOUTH)

    def fill_colour(self, a, pocket):
        """The commonest of his body's fur shades within three squares of the pocket (the darker on a tie), else the
        shadow shade."""
        near = B.dil8(pocket, 3)
        best, n_best = SHADOW, 0
        for c in FUR:
            n = int((B.colour_mask(a, [c]) & near).sum())
            if n > n_best:
                best, n_best = c, n
        return best

    def run_sources(self):
        """The drawn run (dense) and the 1x run it keeps (keep_one: each 1x frame `steps` times)."""
        base = os.path.join(B.ROOT, "assets", "source", "warwick", "hd")
        with open(B.lp(os.path.join(base, "warwick_run_drawn.json")), encoding="utf-8") as f:
            meta = json.load(f)
        with open(B.lp(os.path.join(base, "warwick_run_body.json")), encoding="utf-8") as f:
            steps = int(json.load(f).get("steps", 1))
        return [(os.path.join(base, "warwick_run_drawn.png"), meta["sizes"], "hd", "hd_run"),
                (os.path.join(base, "warwick_run_one.png"), [v for v in meta["one_sizes"] for _ in range(steps)], "one",
                 "run")]


def hero():
    """His settings (tools/art/run_body_anim.py's `strays`)."""
    return Warwick()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", metavar="DIR")
    a = ap.parse_args()
    B.run(Warwick(), a.check, a.review)


if __name__ == "__main__":
    main()
