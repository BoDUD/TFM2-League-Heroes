#!/usr/bin/env python3
"""league_ksante: the black his drawn frames fill the gaps between his body, arms, legs and Ntofos with, cleared from
every tag (the user, 2026-11-17: 「跑步时右边武器也冒出来黑色阴影 处理干净点」「奎桑提和狼人有一样问题 莫名其妙的黑影 处理干净需要」).

    python -I tools/art/ksante_strays.py                 # clear them: his sheet's frames (hd_, 1x, lo_), his strips and
                                                         # his run's sources
    python -I tools/art/ksante_strays.py --check         # exit 1 when a frame still holds one (CI)
    python -I tools/art/ksante_strays.py --review DIR    # each frame it changes: before / cleared (magenta) / after, x6,
                                                         # nothing written

His frames came from Codex's poses (tools/art/rig_ksante.py, ppu_restyle.py): where an arm, a leg or his body comes near
a Ntofo, the gap between them is drawn black - two to five squares deep and a different shape in every frame - and spikes
of black stand out of his outline; on the battlefield they read as shadows popping in and out (the user saw them by the
right Ntofo in the run). tools/art/thin_outline.py keeps them: black between two parts, or deeper than its band (a dark
part of a design, as his hair).
What goes: outline-coloured squares (2, 1, 1) more than `keep` squares (chessboard) from every other colour - the outline
of no part (each part keeps its own `keep` squares: 1 on the dense and 1x frames, 2 on the lo_ ones, as thin_outline.json
has them). What they leave is ground, open or shut in (a gap under an arm shows the ground as it does when the arm is
away). What stays: his hair, black dreadlocks - the head (from the eye row tools/art/ksante_eyes.py finds on each frame:
the rows over it, round the face) and every deep piece that reaches into it are never touched - so are his eyes, mouth
and beard; every square of another colour; every outline square beside a colour.
The lo_ frames are cleaned on their own (their outline is two squares, the dense frames' as they were before
thin_outline.py: ppu_hd.add_lo's frames were made then), their head mapped from their dense frame. The run tags are
tools/art/run_body_anim.py's: their sources are cleaned here (the drawn run; the kept 1x and lo_ frames,
ksante_run_one*.png / ksante_run_lo*.png), run_body_anim.py --hero ksante lays them in. hero_reels' idle / bp reels are
rects of these frames and need nothing. Order: after rig_ksante.py / ppu_restyle.py / ppu_hd.py (they draw the black
again), with tools/art/ksante_eyes.py (neither touches the other's squares), before thin_outline.py (with the gaps open
it clears a square or two more a frame: outline only a corner away from a part, now reached from the ground) and
run_body_anim.py.
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
import ksante_eyes as E  # noqa: E402
import thin_outline as T  # noqa: E402

HERO = E.HERO
OUT = E.OUT
# per density: the outline's own depth, and the head round the eye row (rows over / under it, columns left of / right of
# the face's edge on it) - his hair 11 dense rows over his eyes, 8 at 1x
DENSE = dict(keep=1, head=(13, 3, 18, 5))
ONE = dict(keep=1, head=(11, 3, 15, 4))
LO = dict(keep=2)


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


def eye_row(f, dense):
    """(eye row, the face's edge on it) as tools/art/ksante_eyes.py finds them, or None."""
    g, flashed = E.classes(f)
    c = E.candidates(g, dense, flashed)
    if not c:
        return None
    _, ye, _, _, e = max(c, key=lambda t: (t[0], t[1]))
    return ye, e


def head_box(f, k):
    """The head's squares on frame f (density k, DENSE or ONE) -> mask, or None when no face is found."""
    found = eye_row(f, k is DENSE)
    if found is None:
        return None
    ye, e = found
    up, down, left, right = k["head"]
    m = np.zeros(f.shape[:2], bool)
    m[max(0, ye - up):max(0, ye + down), max(0, e - left):max(0, e + right)] = True
    return m


def lo_head(hd_box, hd_shape, lo_shape, grow):
    """The dense frame's head on its lo_ frame (ppu_hd.add_lo's grow, ksante_eyes.grow_src)."""
    ry, rx = E.grow_src(hd_shape, lo_shape, grow)
    m = np.zeros(lo_shape, bool)
    ys, xs = np.nonzero(hd_box)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    m[np.ix_((ry >= y0) & (ry < y1), (rx >= x0) & (rx < x1))] = True
    return m


def strays(f, keep, head):
    """-> the squares to clear: outline colour more than `keep` from every other colour, its pieces reaching into the
    head left alone."""
    op = f[..., 3] > 0
    ink = op & (f[..., :3] == OUT).all(-1)
    deep = ink & ~dil8(op & ~ink, keep)
    if not deep.any():
        return deep
    lab, n = label8(deep)
    for j in np.unique(lab[deep & head]):
        deep[lab == j] = False
    return deep


def clean(f, keep, head):
    """-> (frame cleaned, squares cleared)."""
    m = strays(f, keep, head)
    b = f.copy()
    b[m] = 0
    return b, m


def run(check, review=None):
    hid, pack, ppu, size = T.resolve(HERO, T.all_heroes())
    grow = E.UI_PPU * size / ppu
    an, px = T.read(hid, pack)
    px2 = px.copy()
    bad, log, pics = [], [], []
    heads = {}
    # dense and 1x frames: their own heads
    for tag, i, (x, y, w, h) in E.frames_of(an):
        if tag.startswith("lo_"):
            continue
        f = px[y:y + h, x:x + w]
        k = DENSE if tag.startswith("hd_") else ONE
        head = head_box(f, k)
        if head is None:
            bad.append(f"{tag} {i}: no face found")
            continue
        if k is DENSE:
            heads[E.plain(tag), i] = (head, f.shape[:2])
        b, m = clean(f, k["keep"], head)
        n = int(m.sum())
        log.append(f"{tag} {i}: {n} squares")
        if n:
            px2[y:y + h, x:x + w] = b
            pics.append((f"{tag} {i}", f, m, b))
    # lo_ frames: their own outline, the head of their dense frame
    for tag, i, (x, y, w, h) in E.frames_of(an):
        if not tag.startswith("lo_"):
            continue
        if (E.plain(tag), i) not in heads:
            bad.append(f"{tag} {i}: no dense frame")
            continue
        hb, hs = heads[E.plain(tag), i]
        f = px[y:y + h, x:x + w]
        b, m = clean(f, LO["keep"], lo_head(hb, hs, f.shape[:2], grow))
        n = int(m.sum())
        log.append(f"{tag} {i}: {n} squares")
        if n:
            px2[y:y + h, x:x + w] = b
            pics.append((f"{tag} {i}", f, m, b))
    changed = int((px2 != px).any(-1).sum())
    if changed:
        bad.append(f"sheet: {changed} squares")
    # his strips (assets/source/ppu/ksante_<tag>.png, the dense frames ppu_hd.py reads)
    for path in sorted(glob.glob(os.path.join(T.STRIPS, "ksante_*.png"))):
        tag = os.path.basename(path)[len("ksante_"):-4]
        if "." in tag or tag == "run":
            continue
        with open(E.lp(path[:-4] + ".json"), encoding="utf-8") as fh:
            sizes = json.load(fh)["sizes"]
        s, fr = E.strip_frames(path, sizes)
        s2 = s.copy()
        for x, w, h in fr:
            f = s[:h, x:x + w]
            head = head_box(f, DENSE)
            if head is None:
                bad.append(f"{os.path.basename(path)}: a frame with no face")
                continue
            s2[:h, x:x + w] = clean(f, DENSE["keep"], head)[0]
        n = int((s2 != s).any(-1).sum())
        if n:
            bad.append(f"{os.path.relpath(path, ROOT)}: {n} squares")
            if not check and review is None:
                Image.fromarray(s2, "RGBA").save(E.lp(path), optimize=True)
    # the run's sources: the drawn run (dense), its kept 1x and lo_ frames
    drawn = []
    for path, fr, dens, idx in E.run_sources():
        s = np.array(Image.open(E.lp(path)).convert("RGBA"))
        s2 = s.copy()
        for j, (x, w, h) in enumerate(fr):
            f = s[:h, x:x + w]
            if dens == "lo":
                hb, hs = drawn[idx[j]]
                b, m = clean(f, LO["keep"], lo_head(hb, hs, f.shape[:2], grow))
            else:
                k = DENSE if dens == "hd" else ONE
                head = head_box(f, k)
                if head is None:
                    bad.append(f"{os.path.basename(path)} {j}: no face found")
                    continue
                if dens == "hd":
                    drawn.append((head, f.shape[:2]))
                b, m = clean(f, k["keep"], head)
            n = int(m.sum())
            log.append(f"{os.path.basename(path)} {j}: {n} squares")
            if n:
                s2[:h, x:x + w] = b
                pics.append((f"{os.path.basename(path)[:-4]} {j}", f, m, b))
        n = int((s2 != s).any(-1).sum())
        if n:
            bad.append(f"{os.path.relpath(path, ROOT)}: {n} squares")
            if not check and review is None:
                Image.fromarray(s2, "RGBA").save(E.lp(path), optimize=True)
    if review is not None:
        write_review(review, pics, log)
        print(f"{HERO}: {len(pics)} frames would change - {review}")
        return
    if check:
        if bad:
            print("\n".join(bad))
            sys.exit(f"{HERO}: black strays left - run tools/art/ksante_strays.py, then tools/art/thin_outline.py --hero "
                     f"ksante and tools/art/run_body_anim.py --hero ksante")
        print(f"ok: {HERO} holds no black strays")
        return
    if changed:
        Image.fromarray(px2, "RGBA").save(E.lp(T.stem(hid, pack) + "#sheet.png"), optimize=True)
    print(f"{HERO}: " + ("; ".join(bad) if bad else "nothing to change"))


def write_review(out_dir, pics, log):
    from PIL import ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "ksante_strays.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    S, BG = 6, (150, 170, 140)

    def show(a, m=None):
        img = np.zeros(a.shape[:2] + (3,), np.uint8)
        img[:] = BG
        op = a[..., 3] > 0
        img[op] = a[op][:, :3]
        if m is not None:
            img[m] = (255, 0, 255)
        return np.repeat(np.repeat(img, S, 0), S, 1)
    for k in range(0, len(pics), 6):
        part = pics[k:k + 6]
        cells = []
        for name, a, m, b in part:
            gap = np.full((a.shape[0] * S, 4, 3), 30, np.uint8)
            cells.append((f"{name}: {int(m.sum())}", np.concatenate([show(a), gap, show(a, m), gap, show(b)], 1)))
        W = max(c.shape[1] for _, c in cells)
        H = sum(c.shape[0] + 18 for _, c in cells)
        sheet = Image.new("RGB", (W, H), (20, 20, 20))
        dr = ImageDraw.Draw(sheet)
        y = 0
        for name, c in cells:
            dr.text((2, y + 2), name, fill=(255, 255, 0))
            sheet.paste(Image.fromarray(c), (0, y + 16))
            y += c.shape[0] + 18
        sheet.save(os.path.join(out_dir, f"ksante_strays_{k // 6:02d}.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", metavar="DIR")
    a = ap.parse_args()
    run(a.check, a.review)


if __name__ == "__main__":
    main()
