"""league_yasuo: one skin colour in every frame - the sheathed / blade-out set's (the user, 2026-11-19, on a screenshot of
attack[0]: 「怎么压缩皮肤颜色还变了」「我要的是这个皮肤颜色吧」).

Yasuo's frames come from five generations. The sheathed set (attack[0] = skill[0] = q3[0]) and the blade-out set
(attack[1..5], skill[1..5], q3[1..5], eq[2..5], ult[5]) - REF here - have the stone-grey-brown skin of the screenshot
(mean skin colour (71, 51, 54)). The idle set (idle_base, hit and the idle frames that close an action), the run and the
cast set (skill2[1..4], eq[0, 1, 6], ult[0..4, 6], q3[6], dead[1..6]) have a purple-red one ((70, 41, 49), (78, 43, 56),
(75, 45, 51)): his arms, chest and boots change colour from one action to the next (the idle reel even mixes attack[0]
with hit[1]).

Here only the skin changes: a square is skin unless it is navy (hair, trousers, scabbard: blue above red), orange (the
glow and the blade's edge), tan (the sash, the mask's horns) or near-black. For each of the three sets a map of its own
is made from its dense frames: each skin colour it does not share with REF goes to the lightness the same share of
REF's skin squares has (quantile by quantile, weighted by how many squares show each colour; Lab L under 14 left
alone), and there to the REF skin colour nearest in that lightness and in a*b*. It is applied to the set's hd_ and 1x
frames (a colour of a 1x frame not in the map takes the map of the nearest colour that is, when one is within 40), each
rect once (the idle and BP reels show the same rects); the lo_ frames are derived again from the dense ones as
yasuo_navy.py leaves them (tools/fix/xinzhao_galio_1119/sheetkit.py, ppu_hd.add_lo's replica); the strips
(assets/source/ppu[/orig]/yasuo_<tag>.png, the idle_base frames in yasuo_idle.png) are rewritten from the dense frames.

Once done every skin colour of those frames is one of REF's, so a second run maps nothing (and --check says so).

    python tools/fix/gpt784_review/yasuo_skin.py
    python tools/fix/gpt784_review/yasuo_skin.py --check
"""
import json
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

REF = {"attack": [0, 1, 2, 3, 4, 5], "skill": [0, 1, 2, 3, 4, 5], "q3": [0, 1, 2, 3, 4, 5], "eq": [2, 3, 4, 5], "ult": [5]}
SETS = {
    "idle": {"idle_base": list(range(8)), "hit": [0, 1], "attack": [6], "skill": [6], "q3": [7], "eq": [7],
             "skill2": [0, 6], "ult": [7], "dead": [0]},
    "run": {"run": list(range(8)), "skill2": [5]},
    "cast": {"skill2": [1, 2, 3, 4], "eq": [0, 1, 6], "ult": [0, 1, 2, 3, 4, 6], "q3": [6], "dead": [1, 2, 3, 4, 5, 6]},
}
REELS = ("idle", "bp")
DARK = 14
NEAR = 40


def lab(rgb):
    c = np.asarray(rgb, float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def skin(p):
    p = np.asarray(p, int).reshape(-1, 3)
    r, g, b = p[:, 0], p[:, 1], p[:, 2]
    navy = (b > r + 8) & (b >= g)
    orange = (r > 150) & (r - b > 90)
    tan = (r > 120) & (g > 90) & (r - b > 40) & (r - b < 110) & ~orange
    dark = p.max(1) < 30
    return ~(navy | orange | tan | dark)


def skin_counts(cells):
    n = Counter()
    for c in cells:
        p = c[c[..., 3] > 0][:, :3]
        n.update(map(tuple, p[skin(p)].tolist()))
    return n


def all_colours(cells):
    s = set()
    for c in cells:
        s |= set(map(tuple, c[c[..., 3] > 0][:, :3].tolist()))
    return s


def build(src, ref, window=10.0, chroma=0.5):
    nc, mc = list(src), list(ref)
    nl = np.array([lab(c)[0] for c in nc])
    nw = np.array([src[c] for c in nc], float)
    ml = np.array([lab(c)[0] for c in mc])
    mw = np.array([ref[c] for c in mc], float)
    o = np.argsort(nl)
    q = np.empty(len(nc))
    q[o] = (np.cumsum(nw[o]) - nw[o] / 2) / nw.sum()
    om = np.argsort(ml)
    target = np.interp(q, (np.cumsum(mw[om]) - mw[om] / 2) / mw.sum(), ml[om])
    mlab = lab(mc)
    f = {}
    for j, c in enumerate(nc):
        cl = lab(c)
        d = (mlab[:, 0] - target[j]) ** 2 + chroma * ((mlab[:, 1] - cl[1]) ** 2 + (mlab[:, 2] - cl[2]) ** 2)
        d = d + np.where(np.abs(mlab[:, 0] - target[j]) > window, 1e6, 0)
        f[c] = tuple(int(v) for v in mc[int(np.argmin(d))])
    return f


def recolour(c, f, ref_all):
    out = c.copy()
    keys = list(f)
    karr = np.array(keys, float)
    cache = {}
    ys, xs = np.nonzero(c[..., 3] > 0)
    for y, x in zip(ys, xs):
        k = tuple(int(v) for v in c[y, x, :3])
        if k not in cache:
            cache[k] = k
            if k in f:
                cache[k] = f[k]
            elif k not in ref_all and skin([k])[0] and lab(k)[0] >= DARK:
                d = ((karr - np.array(k, float)) ** 2).sum(1)
                j = int(np.argmin(d))
                if d[j] <= NEAR * NEAR:
                    cache[k] = f[keys[j]]
        out[y, x, :3] = cache[k]
    return out


def strip_name(t):
    return "idle" if t == "idle_base" else t


def write_strip(k, t):
    n = len(k.anims["hd_" + t]["frames"])
    pics = [k.cell("hd_" + t, i) for i in range(n)]
    H = max(p.shape[0] for p in pics)
    W = sum(p.shape[1] for p in pics) + len(pics) - 1
    st = np.zeros((H, W, 4), np.uint8)
    x = 0
    for p in pics:
        st[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1] + 1
    for sub in ("", "orig"):
        d = os.path.join(ROOT, "assets", "source", "ppu", sub)
        js = os.path.join(d, f"yasuo_{strip_name(t)}.json")
        meta = json.load(open(js))
        meta["sizes"] = [[p.shape[1], p.shape[0]] for p in pics]
        Image.fromarray(st).save(os.path.join(d, f"yasuo_{strip_name(t)}.png"))
        json.dump(meta, open(js, "w"))


def main():
    k = Kit(ROOT, "league", "yasuo")
    # every dense frame is in REF or one set
    named = {(t, i) for sel in [REF] + list(SETS.values()) for t, ii in sel.items() for i in ii}
    missing = [f"{t}[{i}]" for t in k.anims if t.startswith("hd_") and t[3:] not in REELS
               for i in range(len(k.anims[t]["frames"])) if (t[3:], i) not in named]
    if missing:
        sys.exit("frames in no set: " + ", ".join(missing))
    refc = [k.cell("hd_" + t, i) for t, ii in REF.items() for i in ii]
    ref_skin, ref_all = skin_counts(refc), all_colours(refc)
    check = "--check" in sys.argv
    bad = 0
    done = set()
    touched = set()
    for name, sel in SETS.items():
        cells = [k.cell("hd_" + t, i) for t, ii in sel.items() for i in ii]
        own = skin_counts(cells)
        src = Counter({c: v for c, v in own.items() if c not in ref_all and lab(c)[0] >= DARK})
        n = sum(src.values())
        if check or not src:
            print(f"yasuo {name}: {n} skin squares not in the sheathed / blade-out colours")
            bad += n
            continue
        f = build(src, ref_skin)
        moved = 0
        for t, ii in sel.items():
            for pre in ("hd_", ""):
                for i in ii:
                    r = k.rect(pre + t, i)
                    if r in done:
                        continue
                    done.add(r)
                    c = k.cell(pre + t, i)
                    new = recolour(c, f, ref_all)
                    moved += int((new != c).any(-1).sum())
                    k.put(pre + t, i, new)
            touched.add(t)
        for t, ii in sel.items():
            for i in ii:
                r = k.rect("lo_" + t, i)
                if r in done:
                    continue
                done.add(r)
                k.put("lo_" + t, i, k.lo_of(k.cell(t, i).shape[:2], k.cell("hd_" + t, i)))
        print(f"yasuo {name}: {len(f)} skin colours mapped, {moved} squares recoloured")
    if check:
        print("yasuo skin: OK" if not bad else "yasuo skin: run tools/fix/gpt784_review/yasuo_skin.py")
        sys.exit(1 if bad else 0)
    k.save()
    for t in sorted(touched):
        write_strip(k, t)


if __name__ == "__main__":
    main()
