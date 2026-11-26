"""league_nasus: the frames GPT drew again in bdbda7d47 (n_cast in n_hit's build: skill[0], skill2, skill_w, ult[0, 1, 2,
4, 5], dead and their b_ twins) put in the colours of the rest of his sheet.

Those frames came out of a new generation brighter and browner than the frames they play between (idle, attack, hit,
skill[1..5], ult[3]: the n_hit set): median lightness 50 against 36, a grey-brown (108, 78, 71) as the commonest body
colour where the rest is a dark red (90, 31, 33), the lava cracks orange all over - side by side the two read as two
skins. Their shapes are right (n_hit's build, the staff held across as in the idle), so only the colours change:

- the map is made once from the dense frames: each colour of the new frames (lighter than Lab L 14: the outline and the
  near-blacks stay) goes to the lightness the same share of the n_hit set's squares has (quantile by quantile, weighted
  by how many squares show each colour), and there to the n_hit colour nearest in that lightness and in a*b* (so a crack
  stays a crack, a dark red stays a dark red); the b_ (R form) frames get a map of their own from the b_ n_hit frames;
- it is applied to the hd_, 1x and lo_ frames (a colour of a small frame not in the map takes the map of the nearest
  colour that is), each rect once - the BP reel's frames show the same rects;
- the strips (assets/source/ppu[/orig]/nasus_<tag>.png) are rewritten from the dense frames.

GPT drew them in the n_hit set's own 79 colours, just in other shares: what tells the two apart is the lightness. Once
done the redrawn frames' lightness quartiles (Lab L of the squares lighter than 14, weighted) are the n_hit set's within
SAME, so a second run finds nothing to do (and --check says so).

    python tools/fix/gpt784_review/nasus_cast_colours.py
    python tools/fix/gpt784_review/nasus_cast_colours.py --check
"""
import os
import sys
from collections import Counter

import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

NEW = {"skill": [0], "skill2": [0, 1, 2, 3, 4], "skill_w": [0, 1, 2, 3], "ult": [0, 1, 2, 4, 5], "dead": list(range(8))}
NEW_B = {"b_skill": [0], "b_skill2": [0, 1, 2, 3, 4], "b_skill_w": [0, 1, 2, 3]}
DARK = 14


def main_set(k, b):
    tags = ["b_idle_base", "b_attack", "b_hit"] if b else ["idle_base", "attack", "hit"]
    out = {t: list(range(len(k.anims["hd_" + t]["frames"]))) for t in tags}
    out["b_skill" if b else "skill"] = [1, 2, 3, 4, 5]
    if not b:
        out["ult"] = [3]
    return out


def lab(rgb):
    c = np.asarray(rgb, float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def counts(cells):
    n = Counter()
    for c in cells:
        n.update(map(tuple, c[c[..., 3] > 0][:, :3].tolist()))
    return Counter({c: v for c, v in n.items() if lab(c)[0] >= DARK})


def build(new, main, window=6.0, chroma=0.35):
    nc, mc = list(new), list(main)
    nl = np.array([lab(c)[0] for c in nc])
    nw = np.array([new[c] for c in nc], float)
    ml = np.array([lab(c)[0] for c in mc])
    mw = np.array([main[c] for c in mc], float)
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


def recolour(c, f):
    out = c.copy()
    keys = list(f)
    karr = np.array(keys, float)
    cache = {}
    ys, xs = np.nonzero(c[..., 3] > 0)
    for y, x in zip(ys, xs):
        k = tuple(int(v) for v in c[y, x, :3])
        if k not in cache:
            if k in f:
                cache[k] = f[k]
            elif lab(k)[0] < DARK:
                cache[k] = k
            else:
                cache[k] = f[keys[int(np.argmin(((karr - np.array(k, float)) ** 2).sum(1)))]]
        out[y, x, :3] = cache[k]
    return out


SAME = 2.5


def quartiles(n):
    cs = list(n)
    ls = np.array([lab(c)[0] for c in cs])
    w = np.array([n[c] for c in cs], float)
    o = np.argsort(ls)
    cum = np.cumsum(w[o]) / w.sum()
    return np.array([ls[o][np.searchsorted(cum, q)] for q in (0.25, 0.5, 0.75)])


def apart(k, new, b):
    main = counts([k.cell("hd_" + t, i) for t, ii in main_set(k, b).items() for i in ii])
    have = counts([k.cell("hd_" + t, i) for t, ii in new.items() for i in ii])
    qm, qn = quartiles(main), quartiles(have)
    return main, have, qm, qn, float(np.abs(qm - qn).max())


def main():
    k = Kit(ROOT, "league", "nasus")
    check = "--check" in sys.argv
    bad = 0
    done = set()
    for b, new in ((False, NEW), (True, NEW_B)):
        main_c, new_c, qm, qn, gap = apart(k, new, b)
        name = "R form" if b else "base"
        far = gap > SAME
        print(f"nasus {name}: lightness quartiles of the redrawn frames {qn.round(1).tolist()}, of the n_hit set"
              f" {qm.round(1).tolist()}" + (" - apart" if far else " - the same"))
        if check or not far:
            bad += int(far)
            continue
        f = build(new_c, main_c)
        moved = 0
        for t, ii in new.items():
            for pre in ("hd_", "", "lo_"):
                for i in ii:
                    r = k.rect(pre + t, i)
                    if r in done:
                        continue
                    done.add(r)
                    c = k.cell(pre + t, i)
                    n = recolour(c, f)
                    moved += int((n != c).any(-1).sum())
                    k.put(pre + t, i, n)
        print(f"nasus {name}: {len(f)} colours mapped, {moved} squares recoloured")
    if check:
        print("nasus cast colours: OK" if not bad else "nasus cast colours: run tools/fix/gpt784_review/nasus_cast_colours.py")
        sys.exit(1 if bad else 0)
    k.save()
    for t in list(NEW) + list(NEW_B):
        k.strip(t)


if __name__ == "__main__":
    main()
