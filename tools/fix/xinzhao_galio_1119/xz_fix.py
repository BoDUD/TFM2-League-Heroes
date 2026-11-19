"""Xin Zhao's spear to one length (the user, 2026-11-19: 「赵信我还发现个问题 武器大小各个动作帧不一样？」): the ready stance
(idle_base 0/2/4 = attack[5], q1[0] ... and the idle / bp reels' held frames, 92 px) and the low thrust (q2[3], ult[6],
85 px) slide their spear ends inward along the shaft (slide.py: the body, hands and head untouched) to ~77 px, the
length of the frames that show the whole spear (lying 74-76, overhead 76, horizontal 75).

The hd_ pictures are the master: every sheet rect (hd_ and lo_, which share them) holding an old picture gets the new
one; each 1x frame is pixel_down.pixelate(its hd_ frame, 1/1.5) placed on its 1x frame, as Codex's 1x frames are
(checked 100 %); the hd strips (assets/source/ppu/xinzhao_<tag>.png and orig/) get the new pictures in the cells that
held the old ones.
    python xz_fix.py <tree> <out dir>      # writes <out>/league_xinzhao#sheet.png (+ fanim copy), <out>/strips/..."""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TREE, OUT = sys.argv[1:3]
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TREE, "tools", "art"))
import pixel_down as D  # noqa: E402
import slide as S  # noqa: E402

BASE = os.path.join(TREE, "league", "champions", "league_xinzhao")
sheet = np.asarray(Image.open(BASE + "#sheet.png").convert("RGBA")).copy()
anims = json.loads(open(BASE + "#anim.fanim", "rb").read().decode("utf-8-sig"))["anims"]


def rect(t, k):
    d = anims[t]["frames"][k]["data"]
    return tuple(int(round(d[q])) for q in ("x", "y", "w", "h"))


def cell(t, k, src=None):
    x, y, w, h = rect(t, k)
    return (sheet if src is None else src)[y:y + h, x:x + w].copy()


ORIG = sheet.copy()


def stance_edit(c, oy=0):
    """Ready stance -> the attack frames' spear (redesign.py): the butt is band + silver tip (no silver ring, no gold
    ornament), slid in along the shaft; the blade has no crescent hook."""
    import redesign as RD
    return RD.hook(RD.butt(c, oy), oy, outline=(8, 10, 17))


def thrust_edit(c, ox=0):
    """Low thrust: the blade + collar slide 8 px back along the shaft to the front hand."""
    h, w = c.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    m = (c[..., 3] > 0) & (xs >= 84 + ox) & (ys >= 40) & (ys <= 53)
    return S.apply(c, m, (-8, -1))


edits = {}
for (t, k), fn in (((("hd_attack", 5)), lambda c: stance_edit(c)),
                   ((("hd_idle_base", 2)), lambda c: stance_edit(c)),
                   ((("hd_idle_base", 4)), lambda c: stance_edit(c, -1)),
                   ((("hd_q2", 3)), lambda c: thrust_edit(c)),
                   ((("hd_ult", 6)), lambda c: thrust_edit(c, -3))):
    old = cell(t, k)
    edits[old.tobytes() + bytes(old.shape)] = (f"{t}[{k}]", old, fn(old), fn)

# the run (8 frames, each drawn apart): run_redesign.py, frame by frame
import run_redesign as RR  # noqa: E402
for k in range(8):
    old = cell("hd_run", k)
    fn = (lambda kk: (lambda c: RR.edit(c, kk)[0]))(k)
    edits[old.tobytes() + bytes(old.shape)] = (f"hd_run[{k}]", old, fn(old), fn)


def key(a):
    return a.tobytes() + bytes(a.shape)


# hd_ and lo_ rects
written = set()
for t in anims:
    if not t.startswith(("hd_", "lo_")):
        continue
    for k in range(len(anims[t]["frames"])):
        c = cell(t, k, ORIG)
        e = edits.get(key(c))
        if e:
            x, y, w, h = rect(t, k)
            sheet[y:y + h, x:x + w] = e[2]
            written.add((t, k))
print(f"hd_/lo_ frames rewritten: {len(written)}")
# lo_ frames: ppu_hd.add_lo's own computation from the new hd_ frame (a replica checked to give all 134 lo_ frames of the
# tree sheet pixel for pixel); a lo_ frame that shared its rect with an hd_ frame and now differs gets a rect of its own
# below the sheet
import ppu_hd as P  # noqa: E402


def lo_of(one_shape, b):
    k = P.PPU["xinzhao"]
    size = D.sizes_of().get("xinzhao", 1.0)
    outline = D.edge_colour(b) if (b[..., 3] > 0).any() else (0, 0, 0)
    lo, (px, py) = D.pixelate(b, P.UI_PPU * size / k, (b.shape[1] / 2, b.shape[0] / 2), outline)
    W, H = P.lo_size(one_shape[1], one_shape[0])
    ys, xs = np.nonzero(lo[..., 3] > 0)
    while W / 2 < max(px - xs.min(), xs.max() + 1 - px):
        W += 2
    while H / 2 < max(py - ys.min(), ys.max() + 1 - py):
        H += 2
    f = np.zeros((H, W, 4), np.uint8)
    ox, oy = int(np.floor(W / 2 - px + 0.5)), int(np.floor(H / 2 - py + 0.5))
    ok = (ys + oy >= 0) & (ys + oy < H) & (xs + ox >= 0) & (xs + ox < W)
    f[ys[ok] + oy, xs[ok] + ox] = lo[ys[ok], xs[ok]]
    return f


hd_rects = {rect(t, k) for t in anims if t.startswith("hd_") for k in range(len(anims[t]["frames"]))}
extra, nlo = [], 0
for t in list(anims):
    if not t.startswith("lo_"):
        continue
    for k in range(len(anims[t]["frames"])):
        if np.array_equal(cell("hd_" + t[3:], k, ORIG), cell("hd_" + t[3:], k)):
            continue
        f = lo_of(cell(t[3:], k, ORIG).shape, cell("hd_" + t[3:], k))
        x, y, w, h = rect(t, k)
        if (x, y, w, h) in hd_rects and f.shape[:2] == (h, w) and np.array_equal(f, sheet[y:y + h, x:x + w]):
            continue
        if (x, y, w, h) not in hd_rects and f.shape[:2] == (h, w):
            sheet[y:y + h, x:x + w] = f
            nlo += 1
            continue
        extra.append((t, k, f))
if extra:
    top = sheet.shape[0] + 1
    H = top + sum(f.shape[0] + 1 for _, _, f in extra)
    W = max(sheet.shape[1], max(f.shape[1] for _, _, f in extra))
    big = np.zeros((H, W, 4), np.uint8)
    big[:sheet.shape[0], :sheet.shape[1]] = sheet
    y0 = top
    for t, k, f in extra:
        big[y0:y0 + f.shape[0], :f.shape[1]] = f
        anims[t]["frames"][k]["data"] = {"x": 0.0, "y": float(y0), "w": float(f.shape[1]), "h": float(f.shape[0])}
        print(f"  {t}[{k}]: own rect at y {y0} ({f.shape[1]}x{f.shape[0]})")
        y0 += f.shape[0] + 1
    sheet = big
print(f"lo_ frames regenerated in their own rects: {nlo}, given new rects: {len(extra)}")
# 1x frames: pixelate the hd frame of the same tag / index
n1 = 0
for t in anims:
    if t.startswith(("hd_", "lo_")):
        continue
    for k in range(len(anims[t]["frames"])):
        hd_old = cell("hd_" + t, k, ORIG)
        e = edits.get(key(hd_old))
        if not e:
            continue
        one = cell(t, k, ORIG)
        H, W = one.shape[:2]

        def place(b):
            outline = D.edge_colour(b)
            lo, (px, py) = D.pixelate(b, 1 / 1.5, (b.shape[1] / 2, b.shape[0] / 2), outline)
            f = np.zeros((H, W, 4), np.uint8)
            ox, oy = int(np.floor(W / 2 - px + 0.5)), int(np.floor(H / 2 - py + 0.5))
            yy, xx = np.nonzero(lo[..., 3] > 0)
            ok = (yy + oy >= 0) & (yy + oy < H) & (xx + ox >= 0) & (xx + ox < W)
            f[yy[ok] + oy, xx[ok] + ox] = lo[yy[ok], xx[ok]]
            return f
        if not np.array_equal(place(hd_old), one):
            sys.exit(f"{t}[{k}]: the 1x frame is not the pixelated hd frame - stop")
        x, y, w, h = rect(t, k)
        sheet[y:y + h, x:x + w] = place(e[2])
        n1 += 1
print(f"1x frames rewritten: {n1}")
os.makedirs(os.path.join(OUT, "strips", "orig"), exist_ok=True)
Image.fromarray(sheet).save(os.path.join(OUT, "league_xinzhao#sheet.png"))
open(os.path.join(OUT, "league_xinzhao#anim.fanim"), "wb").write(json.dumps({"anims": anims}, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
# strips
ns = 0
main_cells = {}
for sub in ("", "orig"):
    folder = os.path.join(TREE, "assets", "source", "ppu", sub)
    for f in sorted(os.listdir(folder)):
        if not (f.startswith("xinzhao_") and f.endswith(".png")) or not os.path.isfile(os.path.join(folder, f[:-4] + ".json")):
            continue
        st = np.asarray(Image.open(os.path.join(folder, f)).convert("RGBA")).copy()
        sizes = json.load(open(os.path.join(folder, f[:-4] + ".json")))["sizes"]
        x0, hit = 0, 0
        for i, (w, h) in enumerate(sizes):
            c = np.ascontiguousarray(st[:h, x0:x0 + w])
            e = edits.get(key(c))
            if sub == "" and e:
                main_cells[(f, i)] = e
            if not e and sub == "orig" and (f, i) in main_cells:
                # the frame as drawn before its effect overlay (orig/<tag>.over.png): the same edit when it changes the
                # same pixels the same way
                name, old, new, fn = main_cells[(f, i)]
                if c.shape == old.shape:
                    cand = fn(c)
                    changed = np.any(new != old, axis=2)
                    if np.array_equal(np.any(cand != c, axis=2), changed) and np.array_equal(cand[changed], new[changed]):
                        st[:h, x0:x0 + w] = cand
                        hit += 1
                        print(f"    orig/{f}[{i}]: {name}'s edit on the overlay-free frame")
                    else:
                        print(f"    orig/{f}[{i}]: unlike the main strip's {name} and the edit does not carry over - LEFT")
            if e:
                st[:h, x0:x0 + w] = e[2]
                hit += 1
            x0 += w + 1
        if hit:
            Image.fromarray(st).save(os.path.join(OUT, "strips", sub, f))
            ns += hit
            print(f"  strip {sub + '/' if sub else ''}{f}: {hit} cells")
print(f"strip cells rewritten: {ns}")
for _, (name, old, new, _fn) in edits.items():
    Image.fromarray(np.concatenate([old, new], 1)).save(os.path.join(OUT, f"pair_{name.replace('[', '_').replace(']', '')}.png"))
