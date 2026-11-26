#!/usr/bin/env python3
"""league_ksante: every black square his drawn frames hold beyond his outline cleared from every tag - the black between
his body, arms, legs and Ntofos, and the black that ties a Ntofo or an arm to his head (the user, 2026-11-17:
「跑步时右边武器也冒出来黑色阴影 处理干净点」「奎桑提和狼人有一样问题 莫名其妙的黑影 处理干净需要」, then on the first pass
「不对奎桑提其实还有点黑影没处理干净 武器连接着头部有黑影 狼人也没太处理干净 都重新再处理一遍」).

    python -I tools/art/ksante_strays.py                 # clear them: his sheet's frames (hd_, 1x, lo_), his strips and
                                                         # his run's sources
    python -I tools/art/ksante_strays.py --check         # exit 1 when a frame still holds one (CI)
    python -I tools/art/ksante_strays.py --review DIR    # each frame it changes: before / cleared (magenta) / after, x5,
                                                         # nothing written

The rule is tools/art/black_strays.py's: his outline colour (2, 1, 1) is an outline only within a square of another
colour on the dense and 1x frames; deeper, it is no part's outline and goes - left as ground, open or shut in (a gap
under an arm shows the ground as it does when the arm is away). A colour counts only if it is his own (his designs'
DESIGNS and their hit flash): the effects rig_ksante.py drew into his frames (league_ksante_fx / _big: the swing arcs,
Q's crack and burst, W's dust) have colours of their own and no outline, so black beside them alone goes too. What
stays is his hair: black dreadlocks, drawn as a black mass in many poses, so the depth alone cannot tell it from a
shadow. The first pass
kept every black piece reaching into a box round his head, so a black fill bridging a Ntofo or an arm into the head
was kept whole; now the hair is his own head's:
- the head: his idle head's silhouette (hair, face, beard: HEADS, cut from the idle frames of each density and form,
  hd_idle_base / hd_ao_idle_base / idle_base / ao_idle_base) laid on each frame at the eye row and the face's edge
  tools/art/ksante_eyes.py finds there - All Out's on All Out's frames and on the base ult's All Out head
  (ksante_eyes.ao_head) - and a zone round it (ZONE squares: the poses draw the hair a little larger or smaller);
- his head's colours: the 4-connected pieces of colour in the zone made only of his face's and hair's colours (skin,
  the eyes, the lid and shade browns, the hair and beard grey (44, 41, 40); ksante_eyes.CLS and their hit flash), or
  holding the face's skin; every other colour (a Ntofo, his armour, an arm, an effect - the Ntofos' own greys are pieces
  of blue-grey) is another part;
- hair: a black square of the zone at least GAP + 1 steps nearer his head's colours than any other part's (8-neighbour
  steps through what is not a colour): the black between the hair and a Ntofo is the other part's half or a tie and
  goes, the mass on his head stays; a square that would go but has no ground 4-connected to it through what goes stays
  too (no hole is opened inside his hair).
The lo_ frames follow their clean dense frame (black_strays.py: a black square of theirs more than a square from
every colour takes the dense square's value where that one went - between two parts, or deeper than their two-square
outline - and stays where it is still black: his hair). His eyes, mouth and beard are colours and the outline squares
round them: never touched. The run tags are tools/art/run_body_anim.py's: their sources are cleaned here (the drawn
run; the kept 1x and lo_ frames, ksante_run_one*.png / ksante_run_lo*.png), run_body_anim.py --hero ksante lays them in
and cleans each composed dense frame with this rule too (its run data's `strays`).
hero_reels' idle / bp reels are rects of these frames and need nothing. Order: after rig_ksante.py / ppu_restyle.py /
ppu_hd.py (they draw the black again) and tools/art/ksante_eyes.py (neither touches the other's squares), before
run_body_anim.py; thin_outline.py's pass runs inside (black_strays.clean), so thin_outline.py --check finds nothing
after it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import black_strays as B  # noqa: E402
import ksante_eyes as E  # noqa: E402
import thin_outline as T  # noqa: E402

HERO = E.HERO
SKIN = E.SKIN
HEADPAL = set(E.CLS) | {E.flash(c) for c in E.CLS}
ZONE = {"hd": 3, "one": 2}
DESIGNS = ("idle.png", "ao_idle.png")          # his designs (PPU 1.5): every colour of his own
GAP = 1
# his idle heads (hair, face, beard): the squares 4-connected to the face through his head's colours and outline, row by
# row from the top (first row, first column against the face's edge); '@' the face's edge on the eye row (ksante_eyes'
# (eye row, edge)), 'x' / '@' the head
HEADS = {
    ("hd", "base"): (-8, -13, [
        "..........xxx....",
        ".....xx..xxxxx...",
        ".xxxxxxxxxxxxxxx.",
        "xxxxxxxxxxxxxxxxx",
        ".xxxxxxxxxxxxxxxx",
        "..xxxxxxxxxxxxxxx",
        ".xxxxxxxxxxxxxxx.",
        ".xxxxxxxxxxxxx...",
        ".xxxxxxxxxxxx@...",
        "xxxxxxxxxxxxxxx..",
        ".xxx.xxxxxxxxx...",
        ".xxx.xxxxxxxxxxx.",
        "...xxxxxxxxxxxx..",
        ".....xxxxxxxxxx..",
        "......x.xxxxxxxx."]),
    ("hd", "ao"): (-10, -18, [
        ".....xxx....x.x.......",
        "....xxxxxxxxxxxx......",
        "....xxxxxxxxxxxxxx....",
        "...xxxxxxxxxxxxxxxxxx.",
        "...xxxxxxxxxxxxxxxxxxx",
        ".xxxxxxxxxxxxxxxxxxxxx",
        "xx.xxxxxxxxxxxxxxxxxxx",
        ".x.xxxxxxxxxxxxxxxxxx.",
        "..xxxxxxxxxxxxxxxxx...",
        "...xxxx.xxxxxxxxxx....",
        "...xxxxxxxxxxxxxxx@...",
        "...xxx.xxxxxxxxxxxx...",
        "...xxx.xxxxxxxxxxx....",
        "....xxxxxxxxxxxxxx....",
        "....x..xxxxxxxxxxx....",
        ".......xxxxxxxxxxx....",
        "...........xxxxxxx...."]),
    ("one", "base"): (-8, -11, [
        ".....xx.xxx.....",
        "..xxxxxxxxx.....",
        ".xxxxxxxxxxxx...",
        "xxxxxxxxxxxxxxx.",
        "xxxxxxxxxxxxxxx.",
        "xxxxxxxxxxxxx...",
        "xxxxxxxxxxxx....",
        "xxxxxxxxxxxx....",
        "xxxxxxxxxxx@....",
        "xxxxxxxxxxxx....",
        ".xxxxxxxxxxxxx..",
        "..xxxxxxxxxxxxx.",
        "....xxxxxxxx..xx",
        "....x..xxxxxx.x."]),
    ("one", "ao"): (-9, -18, [
        "...............xxx...",
        "..........xxx..xxx...",
        ".....xxxxxxxxxxxxxxx.",
        ".....xxxxxxxxxxxxxxxx",
        "....xxxxxxxxxxxxxxxxx",
        "....xxxxxxxxxxxxxxxxx",
        ".xxxxxxxxxxxxxxxxxxxx",
        "xx..x.xxxxxxxxxxxxxxx",
        "xx..x.xxxxxxxxxxxxx..",
        "..xxx.xxxxxxxxxxxx@..",
        "......xx.xxxxxxxxxxx.",
        ".......xxxxxxxxxxx...",
        "........xxxxxxxxxx...",
        ".........xxxxxxxxx...",
        ".............xxxxx..."]),
}


def head_at(shape, dens, form, ye, e):
    """His idle head (HEADS) laid with its face's edge on (ye, e) -> mask."""
    y0, x0, rows = HEADS[dens, form]
    m = np.zeros(shape, bool)
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            y, x = ye + y0 + r, e + x0 + c
            if ch != "." and 0 <= y < shape[0] and 0 <= x < shape[1]:
                m[y, x] = True
    return m


def anchor(f, dense):
    """(eye row, the face's edge on it) as tools/art/ksante_eyes.py finds them, or None."""
    g, flashed = E.classes(f)
    c = E.candidates(g, dense, flashed)
    if not c:
        return None
    _, ye, _, _, e = max(c, key=lambda t: (t[0], t[1]))
    return ye, e


def head_of(f, tag, dense):
    """His idle head laid on frame f of `tag` (dense: a hd_ frame or a strip's; else 1x) -> mask, or None (no face)."""
    found = anchor(f, dense)
    if found is None:
        return None
    form = "ao" if E.ao_head(tag, f, dense) else "base"
    return head_at(f.shape[:2], "hd" if dense else "one", form, *found)


class KSante(B.Hero):
    ink = E.OUT
    pocket = "ground"

    def __init__(self):
        super().__init__(HERO)
        pal = set()
        for name in DESIGNS:
            d = np.array(Image.open(B.lp(os.path.join(B.ROOT, "assets", "source", "ksante", "hd", name))).convert("RGBA"))
            pal |= {tuple(int(v) for v in c) for c in d[d[..., 3] > 0][:, :3]}
        pal |= {E.flash(c) for c in pal}
        self.own_keys = np.array([(r << 16) | (g << 8) | b for r, g, b in pal], np.int64)

    def own(self, a, col):
        """His own colours (his designs' and their hit flash): an effect drawn into his frames (league_ksante_fx / _big,
        rig_ksante.py: the swing arcs, Q's crack and burst, W's dust; colours of their own, never outlined) carries no
        outline - black beside it alone is no part's outline."""
        rgb = a[..., :3].reshape(-1, 3).astype(np.int64)
        keys = (rgb[:, 0] << 16) | (rgb[:, 1] << 8) | rgb[:, 2]
        return col & np.isin(keys, self.own_keys).reshape(col.shape)

    def ctx(self, tag, f, kind):
        """His head on frame f (a dense or 1x frame of `tag`)."""
        return head_of(f, tag, kind == "hd")

    def protect(self, a, kind, head):
        """The black of his hair (see the module's notes) -> mask."""
        if head is None:
            raise RuntimeError(f"{HERO}: a frame with no face (ksante_eyes finds none)")
        op = a[..., 3] > 0
        out, col, deep = B.deep_of(a, self.ink, B.KEEP[kind], self.own)
        if not deep.any():
            return deep
        zone = B.dil8(head, ZONE[kind])
        rgb = a[..., :3].reshape(-1, 3).astype(np.int64)
        keys = (rgb[:, 0] << 16) | (rgb[:, 1] << 8) | rgb[:, 2]
        pal_keys = np.array([(r << 16) | (g << 8) | b for r, g, b in HEADPAL], np.int64)
        pal = np.isin(keys, pal_keys).reshape(op.shape) & col
        skin = col & ((a[..., :3] == SKIN).all(-1) | (a[..., :3] == E.flash(SKIN)).all(-1))
        lab, n = B.label(col, eight=False)
        own = np.zeros_like(col)
        for j in np.unique(lab[zone & col]):
            b = lab == j
            if (b & ~pal).any() and not (b & skin & head).any():
                continue                                   # a piece of another part
            own |= b & pal & zone
        other = col & ~own
        dh = B.steps8(own, ~col)
        dn = B.steps8(other, ~col)
        hair = deep & zone & (dh + GAP < dn)
        cut = deep & ~hair
        hair |= cut & zone & ~B.reach4(~op, cut)          # no hole opened inside the hair
        return hair

    def run_sources(self):
        """The drawn run (dense), its kept 1x and lo_ frames (ksante_eyes.run_sources)."""
        out = []
        for path, fr, dens, idx in E.run_sources():
            sizes = [(w, h) for _, w, h in fr]
            out.append((path, sizes, dens, idx if dens == "lo" else {"hd": "hd_run", "one": "run"}[dens]))
        return out


def hero():
    """His settings (tools/art/run_body_anim.py's `strays`)."""
    return KSante()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", metavar="DIR")
    a = ap.parse_args()
    B.run(KSante(), a.check, a.review)


if __name__ == "__main__":
    main()
