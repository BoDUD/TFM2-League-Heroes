#!/usr/bin/env python3
"""league_warwick: the black shapes his drawn frames scatter round his outline, cleared from every tag (the user,
2026-11-16: 「狼人怎么有阴影冒出来好奇怪」, then 「狼人还是有冒出来的黑边啊」).

    python -I tools/art/warwick_strays.py            # clear them: his sheet's frames (hd_, 1x, lo_) and his strips
    python -I tools/art/warwick_strays.py --check    # exit 1 when a frame still holds one (CI)

His frames came from image-model poses (tools/art/rig_warwick.py, ppu_restyle.py, Codex's redrawn run): in some frames
of a tag, and not in the next, they hold black that is no part of his design (tools/art/design_warwick_model.py; his
prompts: no shadow, no effect) - read in the game as shadows popping in and out:
- a black chain-like curve from his far hand's claws down to the ground, a ball at its end (idle_base frames 2-5 ...);
- black blots under his feet and claws, and black tufts round the tank on his back;
- detached black specks of a few squares out on the ground beside him.
What goes: outline-coloured squares more than a square from any other colour (pure black, two or more deep) that touch
the ground round him, in pieces of a few squares or more, in his figure's top band or bottom rows, or by his far hand
(below the wrist, right of the body); and detached pieces of outline colour alone out on the ground. A hand's, a claw's
or a foot's own outline (next to its colours) stays, so does black his pieces close in (a mouth, a gap under an arm).
What they leave is ground. The run tags are tools/art/run_body_anim.py's (its `own_clear` takes the same squares,
_a6_work strayseg rules); this tool leaves them alone. Order: after rig_warwick.py / ppu_restyle.py / ppu_hd.py, before
thin_outline.py (its pass closes any edge left one square short) and run_body_anim.py; hero_reels' idle / bp reels are
rects of these frames and need nothing.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import thin_outline as T  # noqa: E402

HERO = "league_warwick"
OUT = (9, 1, 11)
K8 = np.ones((3, 3), bool)
RUN = ("run", "hd_run", "lo_run")
REELS = ("idle", "bp", "hd_idle", "hd_bp", "lo_idle", "lo_bp")
# per density (squares a game px against the dense frames' 1.2): sizes in squares
DENSE = dict(scale=1.0, keep=1)
ONE = dict(scale=1.0 / 1.2, keep=3)
LO = dict(scale=1.5 / 1.2 / 1.2, keep=2)


def dil8(m, n=1):
    """m grown by n squares (8-neighbours)."""
    m = m.copy()
    for _ in range(n):
        p = np.pad(m, 1)
        g = np.zeros_like(m)
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                g |= p[dy:dy + m.shape[0], dx:dx + m.shape[1]]
        m = g
    return m


def label8(m):
    """(labels, count) of m's 8-connected pieces (numpy only: CI runs python -I without scipy)."""
    H, W = m.shape
    lab = np.zeros((H, W), np.int32)
    n = 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        stack = [(y0, x0)]
        while stack:
            y, x = stack.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        stack.append((yy, xx))
    return lab, n


def away(src, cap):
    """Squares more than cap squares (chessboard) from any src square."""
    return ~dil8(src, cap)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


GUMS = [(249, 99, 118), (191, 61, 78), (160, 47, 62), (168, 57, 81)]      # his gums / tongue (his inner ears too)
TEETH = [(249, 250, 251)]                                                  # (his chest fur's highlight too)


def cmask(a, cols):
    m = np.zeros(a.shape[:2], bool)
    for c in cols:
        m |= (a[..., :3] == np.array(c)).all(-1)
    return m & (a[..., 3] > 0)


def clean(a, scale=1.0, keep=1):
    """-> (frame cleaned, squares cleared, squares filled). keep: the outline's own depth (1 on the dense and 1x frames,
    2 on the lo_ ones: thin_outline.json) - black deeper than that is not his outline."""
    a = a.copy()
    H, W = a.shape[:2]
    op = a[..., 3] > 0
    cleared = np.zeros((H, W), bool)
    filled = np.zeros((H, W), bool)
    if not op.any():
        return a, cleared, filled
    s = lambda v: max(1, int(round(v * scale)))  # noqa: E731
    ink = cmask(a, [OUT])
    # detached pieces of outline colour alone (out on the ground, or floating in a gap his pieces close)
    lab, n = label8(op)
    if n > 1:
        sizes = np.bincount(lab.ravel())[1:]
        big = int(np.argmax(sizes)) + 1
        for j in range(1, n + 1):
            b = lab == j
            if j != big and b.sum() <= s(12) and not (b & ~ink).any():
                cleared |= b
    a[cleared] = 0
    op = a[..., 3] > 0
    ink = cmask(a, [OUT])
    solid = op & ~ink
    # black more than `keep` squares from any other colour: not his outline
    deep = ink & away(solid, keep)
    core = ink & away(solid, keep + 1)
    # the ground round him: clear squares reached from the frame's edge (4-connected)
    clear = ~op
    out = np.zeros((H, W), bool)
    out[0], out[-1], out[:, 0], out[:, -1] = clear[0], clear[-1], clear[:, 0], clear[:, -1]
    while True:
        p = np.pad(out, 1)
        g = (p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & clear
        if (g == out).all():
            break
        out = g
    by_out = dil8(out)
    # the open mouth: black with both his gums / tongue and his teeth beside it (the inner ears have the pink alone,
    # the chest the white alone)
    gums, teeth = cmask(a, GUMS), cmask(a, TEETH)
    lab, n = label8(deep)
    fill = np.zeros((H, W), bool)
    for j in range(1, n + 1):
        b = lab == j
        near = dil8(b, 2)
        if (near & gums).any() and (near & teeth).any():
            continue                                  # the open mouth's inside
        if not (b & core).any():
            continue                                  # his outline a square deeper here: not a blob
        if (b & by_out).any():
            cleared |= b                              # out at his edge: ground (his outline stays round it)
        else:
            fill |= b                                 # shut in by his pieces: his fur round it
    a[cleared] = 0
    # fill: ring by ring, the commonest colour of the solid squares round each (his fur shades)
    voter = (a[..., 3] > 0) & ~cmask(a, [OUT])
    todo = fill.copy()
    key = (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2]
    while todo.any():
        step = []
        for y, x in zip(*np.nonzero(todo)):
            votes = {}
            for vy in (-1, 0, 1):
                for vx in (-1, 0, 1):
                    yy, xx = y + vy, x + vx
                    if (vy or vx) and 0 <= yy < H and 0 <= xx < W and voter[yy, xx]:
                        k_ = int(key[yy, xx])
                        votes[k_] = votes.get(k_, 0) + (1.0 if vy == 0 or vx == 0 else 0.7)
            if votes:
                step.append((y, x, max(votes, key=lambda q: (votes[q], -q))))
        if not step:
            break
        for y, x, k_ in step:
            a[y, x] = ((k_ >> 16) & 255, (k_ >> 8) & 255, k_ & 255, 255)
            key[y, x] = k_
            voter[y, x] = True
            todo[y, x] = False
            filled[y, x] = True
    return a, cleared, filled


def clean_all(a, scale=1.0, keep=1):
    """clean() until it changes nothing (a filled blob can leave another one to close)."""
    cleared = np.zeros(a.shape[:2], bool)
    filled = np.zeros(a.shape[:2], bool)
    for _ in range(4):
        a, c, f = clean(a, scale, keep)
        if not (c | f).any():
            break
        cleared |= c
        filled |= f
    return a, cleared & (a[..., 3] == 0), filled


def mask(a, scale=1.0, keep=1):
    """The squares clean() would change."""
    b, c, f = clean(a, scale, keep)
    return c | f


def kind(tag):
    return LO if tag.startswith("lo_") else DENSE if tag.startswith("hd_") else ONE


def sheet_rects(anims):
    """{(x, y, w, h): kind} of every frame the tool looks after (the run tags and the reels left out)."""
    out = {}
    for tag, an in anims.items():
        if tag in RUN or tag in REELS:
            continue
        for f in an["frames"]:
            r = tuple(int(round(f["data"][q])) for q in ("x", "y", "w", "h"))
            out[r] = kind(tag)
    return out


def strips():
    """[(path, tag)] of his dense strips (assets/source/ppu/warwick_<tag>.png), the run's left out."""
    out = []
    for p in sorted(glob.glob(os.path.join(T.STRIPS, "warwick_*.png"))):
        tag = os.path.basename(p)[len("warwick_"):-4]
        if tag != "run":
            out.append((p, tag))
    return out


def strip_frames(path):
    side = path[:-4] + ".json"
    with open(lp(side), encoding="utf-8") as f:
        sizes = json.load(f)["sizes"]
    s = np.array(Image.open(lp(path)).convert("RGBA"))
    out, x = [], 0
    for w, h in sizes:
        out.append((x, w, h))
        x += w + 1
    return s, out


def drawn_run():
    """[(path, [(x, w, h)], params)] of the run's own sources run_body_anim.py reads: the drawn run (dense) and the 1x run
    it keeps (keep_one)."""
    base = os.path.join(ROOT, "assets", "source", "warwick", "hd")
    with open(lp(os.path.join(base, "warwick_run_drawn.json")), encoding="utf-8") as f:
        meta = json.load(f)
    with open(lp(os.path.join(base, "warwick_run_body.json")), encoding="utf-8") as f:
        steps = int(json.load(f).get("steps", 1))
    out = []
    x, fr = 0, []
    for w, h in meta["sizes"]:
        fr.append((x, w, h)); x += w + 1
    out.append((os.path.join(base, "warwick_run_drawn.png"), fr, DENSE))
    x, fr = 0, []
    for w, h in [v for v in meta["one_sizes"] for _ in range(steps)]:
        fr.append((x, w, h)); x += w + 1
    out.append((os.path.join(base, "warwick_run_one.png"), fr, ONE))
    return out


def clean_strip(path, frames, k, check, bad):
    s = np.array(Image.open(lp(path)).convert("RGBA"))
    s2 = s.copy()
    n = 0
    for x, w, h in frames:
        b, c, f = clean_all(s[:h, x:x + w], k["scale"], k["keep"])
        if (c | f).any():
            s2[:h, x:x + w] = b
            n += int((c | f).sum())
    if n:
        bad.append(f"{os.path.relpath(path, ROOT)}: {n} squares")
        if not check:
            Image.fromarray(s2, "RGBA").save(lp(path), optimize=True)
    return n


def run(check):
    hid, pack, _, _ = T.resolve(HERO, T.all_heroes())
    an, px = T.read(hid, pack)
    bad, changed = [], 0
    px2 = px.copy()
    for (x, y, w, h), k in sorted(sheet_rects(an).items()):
        b, c, f = clean_all(px[y:y + h, x:x + w], k["scale"], k["keep"])
        if (c | f).any():
            bad.append(f"sheet frame at {x},{y}: {int((c | f).sum())} squares")
            px2[y:y + h, x:x + w] = b
            changed += int((c | f).sum())
    for path, tag in strips():
        _, fr = strip_frames(path)
        clean_strip(path, fr, DENSE, check, bad)
    for path, fr, k in drawn_run():
        clean_strip(path, fr, k, check, bad)
    if check:
        if bad:
            print("\n".join(bad))
            sys.exit(f"{HERO}: black strays left - run tools/art/warwick_strays.py, then tools/art/thin_outline.py --hero "
                     f"warwick and tools/art/run_body_anim.py --hero warwick")
        print(f"ok: {HERO} holds no black strays")
        return
    if changed:
        Image.fromarray(px2, "RGBA").save(lp(T.stem(hid, pack) + "#sheet.png"), optimize=True)
    print(f"{HERO}: {changed} sheet squares changed; " + "; ".join(b for b in bad if not b.startswith("sheet")))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    run(a.check)


if __name__ == "__main__":
    main()
