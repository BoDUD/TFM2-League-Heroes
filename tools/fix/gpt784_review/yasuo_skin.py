"""league_yasuo: one skin colour in every frame - the sheathed / blade-out set's (the user, 2026-11-19, on a screenshot of
attack[0]: 「怎么压缩皮肤颜色还变了」「我要的是这个皮肤颜色吧」).

Yasuo's frames come from five generations. The sheathed set (attack[0] = skill[0] = q3[0]) and the blade-out set
(attack[1..5], skill[1..5], q3[1..5], eq[2..5], ult[5]) - REF here - have the stone-grey-brown skin of the screenshot
(mean skin colour (71, 51, 54)). The idle set (idle_base, hit and the idle frames that close an action), the run and the
cast set (skill2[1..4], eq[0, 1, 6], ult[0..4, 6], q3[6], dead[1..6]) have a purple-red one ((70, 41, 49), (78, 43, 56),
(75, 45, 51)): his arms, chest and boots change colour from one action to the next (the idle reel even mixes attack[0]
with hit[1]).

Here only the skin changes: a square is skin unless it is navy (hair, trousers, scabbard: blue above red), orange (the
glow and the blade's edge), tan (the sash, the mask's horns) or near-black. Those three sets also draw twice REF's dark
line work inside the body (13-15 % of the body's squares near-black against 6-7 %), so matching the skin colours alone
left them darker (body lightness 13-16 against REF's 21.5: the user, after the first pass: 「亚索的皮肤放完技能后还是会变颜色」).
For each set a map of its own is made from its dense frames: each skin colour it does not share with REF goes to the
lightness REF's body (skin and near-black squares two squares in from the outline) has at the colour's own quantile in
the set's body, raised by the one offset (0-10 Lab L, steps of 0.5) that brings the set's mean body lightness to REF's,
and there to the REF skin colour nearest in lightness (and a little in a*b*). It is applied to the set's hd_ and 1x
frames (a colour of a 1x frame not in the map takes the map of the nearest colour that is, when one is within 40), each
rect once (the idle and BP reels show the same rects); the lo_ frames are derived again from the dense ones as
yasuo_navy.py leaves them (tools/fix/xinzhao_galio_1119/sheetkit.py, ppu_hd.add_lo's replica); the strips
(assets/source/ppu[/orig]/yasuo_<tag>.png, the idle_base frames in yasuo_idle.png) are rewritten from the dense frames.
`--from REV` first puts REV's Yasuo sheet, anim and strips back (bc563ba4a: the purple-red sets as drawn).

The navy (hair, trousers, scabbard) is matched the same way, by itself: those sets' navy came out of yasuo_navy.py darker
than REF's (mean Lab L 19.9-22.2 against 24.9; hair and trousers are 45 % of his figure), so with the skin matched he
still went dark in the idle frames and light in attack[0] (the sheathed frame his idle reel plays between them): the
user, 「那为什么亚索看起来会一会儿亮的 一会儿黑的？」. Each set's navy colours not in REF's navy go to REF's navy lightness at
their own quantile, raised by the offset that brings the set's mean navy lightness to REF's, and there to the REF navy
colour nearest in lightness; every REF navy colour is yasuo_navy.py's hue, so its --check holds.

Once done every skin colour of those frames is one of REF's, so a second run maps nothing; --check also wants each
set's mean body lightness within 1.0 of REF's.

    python tools/fix/gpt784_review/yasuo_skin.py --from bc563ba4a
    python tools/fix/gpt784_review/yasuo_skin.py --check
"""
import json
import os
import subprocess
import sys
from collections import Counter

import numpy as np
from PIL import Image
from scipy import ndimage

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


def parts(p):
    p = np.asarray(p, int).reshape(-1, 3)
    r, g, b = p[:, 0], p[:, 1], p[:, 2]
    navy = (b > r + 8) & (b >= g)
    orange = (r > 150) & (r - b > 90)
    tan = (r > 120) & (g > 90) & (r - b > 40) & (r - b < 110) & ~orange
    return navy | orange | tan


def navy_px(c):
    """the navy squares (hair, trousers, scabbard): blue above red, not near-black"""
    p = c[c[..., 3] > 0][:, :3].astype(int)
    r, g, b = p[:, 0], p[:, 1], p[:, 2]
    return p[(b > r + 8) & (b >= g) & (p.max(1) >= 30)]


def navy_counts(cells):
    n = Counter()
    for c in cells:
        n.update(map(tuple, navy_px(c).tolist()))
    return n


def navy_mean(cells):
    p = np.concatenate([q for q in (navy_px(c) for c in cells) if len(q)])
    return float(lab(p)[:, 0].mean())


def build_navy(src, own, ref, delta):
    fl, fq = quantiles(own)
    rl, rq = quantiles(ref)
    cand = list(ref)
    cl = lab(cand)
    f = {}
    for k in src:
        kl = lab(k)
        tl = np.interp(np.interp(kl[0], fl, fq), rq, rl) + delta
        d = (cl[:, 0] - tl) ** 2 + 0.2 * ((cl[:, 1] - kl[1]) ** 2 + (cl[:, 2] - kl[2]) ** 2)
        f[k] = tuple(int(v) for v in cand[int(np.argmin(d))])
    return f


def body(c):
    """the body's squares two in from the outline, not navy / orange / tan: skin and the dark line work inside it"""
    inner = ndimage.binary_erosion(c[..., 3] > 0, iterations=2)
    p = c[inner][:, :3].astype(int)
    return p[~parts(p)]


def body_counts(cells):
    n = Counter()
    for c in cells:
        n.update(map(tuple, body(c).tolist()))
    return n


def body_mean(cells):
    ps = [body(c) for c in cells]
    p = np.concatenate([q for q in ps if len(q)])
    return float(lab(p)[:, 0].mean())


def quantiles(n):
    ks = list(n)
    ls = np.array([lab(k)[0] for k in ks])
    w = np.array([n[k] for k in ks], float)
    o = np.argsort(ls)
    return ls[o], (np.cumsum(w[o]) - w[o] / 2) / w.sum()


def build(src, own_body, ref_body, ref_skin, delta, chroma=0.3):
    fl, fq = quantiles(own_body)
    rl, rq = quantiles(ref_body)
    cand = list(ref_skin)
    cl = lab(cand)
    f = {}
    for k in src:
        kl = lab(k)
        tl = np.interp(np.interp(kl[0], fl, fq), rq, rl) + delta
        d = (cl[:, 0] - tl) ** 2 + chroma * ((cl[:, 1] - kl[1]) ** 2 + (cl[:, 2] - kl[2]) ** 2)
        f[k] = tuple(int(v) for v in cand[int(np.argmin(d))])
    return f


def apply_map(c, f):
    """f on the squares whose colour is a key (vectorised; for the offset search)"""
    if not f:
        return c.copy()
    out = c.copy()
    key = (c[..., 0].astype(np.int64) << 16) | (c[..., 1].astype(np.int64) << 8) | c[..., 2].astype(np.int64)
    src = np.array([(k[0] << 16) | (k[1] << 8) | k[2] for k in f], np.int64)
    dst = np.array(list(f.values()), np.uint8)
    o = np.argsort(src)
    src, dst = src[o], dst[o]
    pos = np.clip(np.searchsorted(src, key), 0, len(src) - 1)
    hit = (src[pos] == key) & (c[..., 3] > 0)
    out[hit, :3] = dst[pos[hit]]
    return out


def is_navy(k):
    return k[2] > k[0] + 8 and k[2] >= k[1] and max(k) >= 30


def recolour(c, f, ref_all):
    """f on c; a colour not in f (a 1x frame's) takes the map of the nearest key of its own kind (skin / navy) within
    NEAR"""
    out = c.copy()
    kinds = {}
    for key in f:
        kinds.setdefault(is_navy(key), []).append(key)
    arrs = {kind: np.array(keys, float) for kind, keys in kinds.items()}
    cache = {}
    ys, xs = np.nonzero(c[..., 3] > 0)
    for y, x in zip(ys, xs):
        k = tuple(int(v) for v in c[y, x, :3])
        if k not in cache:
            cache[k] = k
            kind = is_navy(k)
            if k in f:
                cache[k] = f[k]
            elif k not in ref_all and lab(k)[0] >= DARK and (kind or skin([k])[0]) and kind in kinds:
                d = ((arrs[kind] - np.array(k, float)) ** 2).sum(1)
                j = int(np.argmin(d))
                if d[j] <= NEAR * NEAR:
                    cache[k] = f[kinds[kind][j]]
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


def restore(rev):
    def show(path):
        return subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout
    for path in ("league/champions/league_yasuo#sheet.png", "league/champions/league_yasuo#anim.fanim"):
        open(os.path.join(ROOT, path), "wb").write(show(path))
    for sub in ("", "orig/"):
        for t in ("idle", "run", "attack", "skill", "q3", "eq", "skill2", "ult", "hit", "dead"):
            for ext in (".png", ".json"):
                path = f"assets/source/ppu/{sub}yasuo_{t}{ext}"
                if os.path.isfile(os.path.join(ROOT, path)):
                    open(os.path.join(ROOT, path), "wb").write(show(path))


def main():
    if "--from" in sys.argv:
        restore(sys.argv[sys.argv.index("--from") + 1])
    k = Kit(ROOT, "league", "yasuo")
    # every dense frame is in REF or one set
    named = {(t, i) for sel in [REF] + list(SETS.values()) for t, ii in sel.items() for i in ii}
    missing = [f"{t}[{i}]" for t in k.anims if t.startswith("hd_") and t[3:] not in REELS
               for i in range(len(k.anims[t]["frames"])) if (t[3:], i) not in named]
    if missing:
        sys.exit("frames in no set: " + ", ".join(missing))
    refc = [k.cell("hd_" + t, i) for t, ii in REF.items() for i in ii]
    ref_skin, ref_all = skin_counts(refc), all_colours(refc)
    ref_body, ref_mean = body_counts(refc), body_mean(refc)
    ref_navy, ref_navy_mean = navy_counts(refc), navy_mean(refc)
    check = "--check" in sys.argv
    bad = 0
    done = set()
    touched = set()
    for name, sel in SETS.items():
        cells = [k.cell("hd_" + t, i) for t, ii in sel.items() for i in ii]
        own = skin_counts(cells)
        src = Counter({c: v for c, v in own.items() if c not in ref_all and lab(c)[0] >= DARK})
        n = sum(src.values())
        mean = body_mean(cells)
        nmean = navy_mean(cells)
        nn = sum(v for c, v in navy_counts(cells).items() if c not in ref_navy)
        if check or (not src and not nn):
            far = abs(mean - ref_mean) > 1.0 or abs(nmean - ref_navy_mean) > 1.0
            print(f"yasuo {name}: {n} skin / {nn} navy squares not in the sheathed / blade-out colours; body lightness"
                  f" {mean:.1f} (REF {ref_mean:.1f}), navy {nmean:.1f} (REF {ref_navy_mean:.1f})" + (" - apart" if far else ""))
            bad += n + nn + int(far)
            continue
        own_body = body_counts(cells)
        best = None
        for delta in np.arange(0.0, 10.5, 0.5):
            f = build(src, own_body, ref_body, ref_skin, float(delta))
            m = body_mean([apply_map(c, f) for c in cells])
            if best is None or abs(m - ref_mean) < abs(best[1] - ref_mean):
                best = (float(delta), m, f)
        delta, m, f = best
        # the navy, by itself
        ncells = [apply_map(c, f) for c in cells]
        own_navy = navy_counts(ncells)
        nsrc = [c for c in own_navy if c not in ref_navy]
        nbest = None
        for nd in np.arange(-4.0, 10.5, 0.5):
            g = build_navy(nsrc, own_navy, ref_navy, float(nd))
            nm = navy_mean([apply_map(c, g) for c in ncells])
            if nbest is None or abs(nm - ref_navy_mean) < abs(nbest[1] - ref_navy_mean):
                nbest = (float(nd), nm, g)
        f = {**f, **{k: v for k, v in nbest[2].items()}}
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
        print(f"yasuo {name}: {len(f)} colours mapped (skin offset {delta:+.1f} L, navy {nbest[0]:+.1f} L), body lightness"
              f" {mean:.1f} -> {m:.1f} (REF {ref_mean:.1f}), navy {nmean:.1f} -> {nbest[1]:.1f} (REF {ref_navy_mean:.1f}),"
              f" {moved} squares recoloured")
    if check:
        print("yasuo skin: OK" if not bad else "yasuo skin: run tools/fix/gpt784_review/yasuo_skin.py")
        sys.exit(1 if bad else 0)
    k.save()
    for t in sorted(touched):
        write_strip(k, t)


if __name__ == "__main__":
    main()
