#!/usr/bin/env python3
"""A hero's drawn run with life in the upper body: the legs exactly as drawn, the upper body one drawing that bobs
with the steps, the back hair swinging after it as a chain, the fists lagging it a square (the user, on league_vi's
and league_lux's runs re-posed from League's motion: 「拉克丝 蔚全都不合格 我让你改不是让你改原本的走路的腿部的姿势
只是身体有点动画效果 看起来不要那么僵硬 你现在改的导致模型严重变形了」 - keep the drawn legs, give the body some animation so it
is less stiff - and 「蔚先回复到main分支的模型再改」).

    python tools/art/run_body_anim.py --hero vi             # run / hd_run / lo_run into the sheet (+ the strip)
    python tools/art/run_body_anim.py --hero vi --check     # exit 1 when the sheet's run tags are not what it makes
    python tools/art/run_body_anim.py --hero vi --dry       # make them, write nothing

HEROES holds each hero's data; nothing in the code is one hero's. From the hero's drawn run (`drawn`: the dense
frames as main had them, kept apart so the tool can make them again), every frame is made of:

- its legs, square for square as drawn: every square of the frame from its waist (`waist`, rows from its centre)
  down, but the pieces of its upper body that hang below it (`below`: rects where the fists hang; in them, what its
  legs reach - 4-connected through its own squares that are not outline, from outside the rects - stays legs);
- one upper body - frame `from`'s: its head (the face, the goggles, the hair on top: one drawing, no frame's own head
  or ear any more), its torso, arms and fists, its back hair - laid by whole squares where `bob` puts it: `bob` is
  rows down from frame `from`'s drawn place, a frame each - two beats a cycle, low as each step lands, high as it
  pushes off - never sideways;
- in it, parts that lag the body (`parts`: a polygon in frame `from` each, a lag in frames, a range of rows): their
  rows off the body are the body's own bob some frames before minus now (the bob read as a periodic curve through
  the frames), rounded and held in the range - a fist that drops a square as she rises and rises as she lands;
- the back hair (`hair`: its colours left of the root column, and the outline only it touches): a chain, every column
  of it lagging the body by more the farther it is from the root (`lag` frames at its tip, `whip`: that much more
  swing there), so its tips move as the body did a frame before; the root stays on the head, neighbouring columns
  never more than a square apart.
Order, back to front: the hair, the legs, the body, then the parts (`parts` in order). Where the frame's own upper
body was and nothing is laid, a square inside her (closing her figure by 3) is filled from her legs' own colours round
it, or with outline where only the laid body is round it; the rest is cleared; an edge that bares is closed with 2
squares of outline; a pinhole the parts shut in is outline. Last, tools/art/thin_outline.py's pass with the hero's own
settings (thin_outline.json), so CI's --check finds nothing to change.
The 1x frames come from the dense ones as tools/art/ppu_one.py makes them (the 1x sizes kept where the drawing fits;
squares that do not fit are reported by --dry), the lo_ frames as tools/art/ppu_hd.py's add_lo does, thinned the same
way. Every frame keeps its size and its timing, so the sheet's rects and the fanim (league.dll's hd.rs embeds it) do
not change. tools/art/ppu_restyle.py writes the hero's strip again from assets/source/ppu/orig/ (the run as drawn):
run this after it, as tools/art/thin_outline.py runs after it.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import thin_outline as T  # noqa: E402

PINKS = [(232, 54, 124), (249, 100, 164), (141, 19, 67), (116, 16, 56), (170, 27, 83), (205, 40, 105), (91, 17, 47),
         (176, 60, 102)]
REDS = [(153, 16, 35), (97, 29, 43), (198, 26, 48), (124, 25, 39), (63, 18, 30), (159, 36, 58)]
HEROES = {
    "vi": {
        "tag": "run",
        "drawn": "assets/source/vi/hd/vi_run_drawn",      # main 858cbab94's hd_run, 8 frames of 105 ms
        "from": 0,
        "outline": (26, 12, 16),
        # each frame's first row of its legs, from its centre: the top of her belt
        "waist": [-15, -16, -16, -16, -15, -15, -15, -16],
        # rows down from frame `from`'s drawn place, a frame each: two beats a cycle, 3 squares (1.6 game px; the
        # base game's runs bob a median 2 px, low at each step). Her legs: contacts at frames 3 and 7 (both feet
        # down, the widest stride), the down after them at 0 and 4 (the planted knee bent, the rear foot kicked up),
        # passings at 1 and 5, up at 2 and 6 (the swinging knee driven forward by the straight standing leg): the
        # body lowest at the downs, highest at the ups. Her drawn head sits a row under each rect's top (frame 3's at
        # it): one row higher and the 1x frame made from it loses its top row, so the ups are at frame 0's drawn place
        "bob": [3, 2, 0, 1, 3, 2, 0, 1],
        # frame rows (rect: top row, last row, first col, last col; top None = the waist) where her fists hang below
        # her waist: the near gauntlet at her hip, the far one in front of her
        "below": [[(None, 54, 0, 24), (None, 47, 34, 58)], [(None, 52, 0, 23), (None, 47, 34, 58)],
                  [(None, 51, 0, 23), (None, 47, 34, 58)], [(None, 50, 0, 22), (None, 45, 34, 58)],
                  [(None, 53, 0, 23), (None, 47, 34, 58)], [(None, 53, 0, 23), (None, 47, 34, 58)],
                  [(None, 50, 0, 23), (None, 47, 34, 58)], [(None, 50, 0, 23), (None, 47, 34, 58)]],
        "parts": {
            # (row, col) corners in frame `from`, its outline in; skip: colours in the polygon that are not its own
            # (her hip strap's end, her scarf's)
            "near gauntlet": {"poly": [(30, 3), (30, 13), (32, 17), (32, 24), (36, 25), (46, 25), (49, 24), (53, 23),
                                       (54, 21), (54, 8), (51, 3), (46, 0), (35, 0)],
                              "lag": 1.0, "range": (-1, 1), "skip": PINKS + REDS},
            # never up: its top is by her chin
            "far gauntlet": {"poly": [(18, 40), (18, 50), (22, 54), (24, 56), (36, 56), (40, 52), (44, 48), (44, 40),
                                      (41, 36), (24, 35), (21, 37)],
                             "lag": 0.5, "range": (0, 1), "skip": PINKS + REDS},
        },
        "hair": {"colours": PINKS, "root": 19, "bottom": 31, "lag": 1.0, "whip": 0.2},
    },
}


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def colour_mask(a, cols):
    m = np.zeros(a.shape[:2], bool)
    for c in cols:
        m |= (a[..., :3] == np.array(c)).all(-1)
    return m & (a[..., 3] > 0)


def poly_mask(poly, shape):
    """The squares whose centres lie inside a polygon of (row, col) corners."""
    H, W = shape[:2]
    Y, X = np.mgrid[0:H, 0:W]
    y, x = Y + 0.5, X + 0.5
    m = np.zeros((H, W), bool)
    for k in range(len(poly)):
        (y1, x1), (y2, x2) = poly[k], poly[(k + 1) % len(poly)]
        if y1 == y2:
            continue
        m ^= ((y1 > y) != (y2 > y)) & (x < x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    return m


def disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return (y * y + x * x) <= r * r + 0.5


K8 = np.ones((3, 3), bool)


def drawn(cfg):
    """-> [(frame, ms)] of the hero's drawn run."""
    s = np.array(Image.open(lp(os.path.join(ROOT, cfg["drawn"] + ".png"))).convert("RGBA"))
    with open(lp(os.path.join(ROOT, cfg["drawn"] + ".json")), encoding="utf-8") as f:
        meta = json.load(f)
    out, x = [], 0
    for (w, h), ms in zip(meta["sizes"], meta["ms"]):
        out.append((s[:h, x:x + w].copy(), ms))
        x += w + 1
    return out


# ------------------------------------------------------------------------------------------------- the motion
def curve(vals):
    """The periodic curve through vals (one a frame): its value at any (fractional) frame."""
    n = len(vals)
    X = np.fft.rfft(np.asarray(vals, float))

    def at(t):
        out = X[0].real / n
        for k in range(1, len(X)):
            w = 1.0 if (n % 2 == 0 and k == n // 2) else 2.0
            out += w / n * (X[k] * np.exp(2j * np.pi * k * t / n)).real
        return out
    return at


def lagged(at, i, lag, gain=1.0):
    """Rows a part lagging the body by `lag` frames sits off it at frame i (down +)."""
    return gain * (at(i - lag) - at(i))


def motion(cfg, n, hair_cols):
    """-> {"body": [rows], part name: [rows], "hair": [{col: rows}]} per frame."""
    bob = cfg["bob"]
    at = curve(bob)
    out = {"body": list(bob)}
    for name, p in cfg["parts"].items():
        lo, hi = p["range"]
        out[name] = [int(min(hi, max(lo, round(lagged(at, i, p["lag"]))))) for i in range(n)]
    h = cfg["hair"]
    root = h["root"]
    span = max(1, root - min(hair_cols)) if hair_cols else 1
    rows = []
    for i in range(n):
        d = {}
        prev = 0
        for c in range(root - 1, min(hair_cols) - 1 if hair_cols else root - 1, -1):
            u = (root - c) / float(span)
            v = int(round(lagged(at, i, h["lag"] * u, 1.0 + h["whip"] * u)))
            v = max(prev - 1, min(prev + 1, v))          # neighbouring columns at most a square apart
            d[c] = v
            prev = v
        rows.append(d)
    out["hair"] = rows
    return out


# ------------------------------------------------------------------------------------------------- the parts
def pieces(src, cfg, i_src):
    """Frame `from`'s upper body cut into its layers -> {"body", "hair", part name: mask}, each with the outline that
    is its own (the outline a square deep against the other layers, two against the ground)."""
    H, W = src.shape[:2]
    op = src[..., 3] > 0
    ink = colour_mask(src, [cfg["outline"]])
    cy = H // 2
    upper = np.zeros((H, W), bool)
    upper[:cy + cfg["waist"][i_src]] = True
    parts = {name: poly_mask(p["poly"], src.shape) & op & ~colour_mask(src, p.get("skip", []))
             for name, p in cfg["parts"].items()}
    every = (upper & op) | np.logical_or.reduce(list(parts.values()))
    h = cfg["hair"]
    hair = colour_mask(src, h["colours"]) & every
    hair[:, h["root"]:] = False
    hair[h["bottom"]:] = False
    for m in parts.values():
        hair &= ~m
    lab, n = ndimage.label(hair, structure=K8)
    if n:
        sz = ndimage.sum(hair, lab, range(1, n + 1))
        hair = np.isin(lab, [j + 1 for j in range(n) if sz[j] >= 12])
    body = every & ~ink
    for m in parts.values():
        body &= ~m
    body_solid = body & ~hair
    # the hair's outline: what touches the hair and no other solid square of hers, left of the root
    hink = ink & every & ndimage.binary_dilation(hair, structure=K8) & ~ndimage.binary_dilation(body_solid, structure=K8)
    hink[:, h["root"]:] = False
    for m in parts.values():
        hink &= ~m
    out = {"hair": hair | hink}
    out["body"] = every & ~out["hair"]
    for name, m in parts.items():
        out["body"] &= ~m
        out[name] = m
    return out


def own_upper(a, cfg, i):
    """Frame i's own upper body: everything above its waist, and in `below`'s rects what its legs do not reach."""
    H, W = a.shape[:2]
    op = a[..., 3] > 0
    ink = colour_mask(a, [cfg["outline"]])
    cy = H // 2
    wr = cy + cfg["waist"][i]
    up = np.zeros((H, W), bool)
    up[:wr] = True
    rect = np.zeros((H, W), bool)
    for r0, r1, c0, c1 in cfg["below"][i]:
        rect[(wr if r0 is None else r0):r1 + 1, c0:c1 + 1] = True
    low = ~up
    through = op & ~ink & low
    lab, _ = ndimage.label(through)
    hit = np.unique(lab[through & ~rect])
    legs = np.isin(lab, hit[hit > 0])
    hang = rect & low & op & ~ink & ~legs
    # the hanging pieces' outline: what touches them and not her legs
    hang |= rect & low & ink & ndimage.binary_dilation(hang, structure=K8) & ~ndimage.binary_dilation(legs, structure=K8)
    return (up & op) | hang


# ------------------------------------------------------------------------------------------------- the frame
def fill_in(b, inside, voters):
    """The inside squares filled from the voters' colours round them, ring by ring (the commonest of the 8 neighbours,
    across counted above diagonals); a square no voter reaches stays clear."""
    key = (b[..., 0].astype(np.int64) << 16) | (b[..., 1].astype(np.int64) << 8) | b[..., 2]
    voter = voters.copy()
    todo = inside.copy()
    while todo.any():
        step = []
        for y, x in zip(*np.nonzero(todo)):
            votes = {}
            for vy in (-1, 0, 1):
                for vx in (-1, 0, 1):
                    yy, xx = y + vy, x + vx
                    if (vy or vx) and 0 <= yy < b.shape[0] and 0 <= xx < b.shape[1] and voter[yy, xx]:
                        k = int(key[yy, xx])
                        votes[k] = votes.get(k, 0) + (1.0 if vy == 0 or vx == 0 else 0.7)
            if votes:
                step.append((y, x, max(votes, key=lambda q: (votes[q], -q))))
        if not step:
            break
        for y, x, k in step:
            b[y, x] = ((k >> 16) & 255, (k >> 8) & 255, k & 255, 255)
            key[y, x] = k
            voter[y, x] = True
            todo[y, x] = False


def pockets(a):
    """The clear squares the figure shuts in (not reaching the frame's edge)."""
    lab, n = ndimage.label(a[..., 3] == 0)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    return (lab > 0) & ~np.isin(lab, edge)


def lay(b, src, m, dy, dx, cols=None, under=False):
    """src's squares in m into b moved (dy, dx) (cols: {col: extra rows} per source column); under: only where b is
    clear. -> the squares laid."""
    ys, xs = np.nonzero(m)
    ty = ys + dy + (np.array([cols.get(int(x), 0) for x in xs]) if cols else 0)
    tx = xs + dx
    ok = (ty >= 0) & (ty < b.shape[0]) & (tx >= 0) & (tx < b.shape[1])
    if not ok.all():
        sys.exit(f"run_body_anim: {int((~ok).sum())} squares of a part leave the frame")
    if under:
        ok &= b[ty, tx, 3] == 0
    b[ty[ok], tx[ok]] = src[ys[ok], xs[ok]]
    put = np.zeros(b.shape[:2], bool)
    put[ty[ok], tx[ok]] = True
    return put


def compose(a, i, src, cy0, cx0, layers, mov, cfg):
    """Frame i made: its legs, frame `from`'s upper body laid as `mov` says, the gaps joined. -> (frame, info)."""
    out_c = cfg["outline"]
    H, W = a.shape[:2]
    cy, cx = H // 2, W // 2
    own = own_upper(a, cfg, i)
    b = a.copy()
    b[own] = 0
    legs = b[..., 3] > 0
    dy = cy - cy0 + mov["body"][i]
    dx = cx - cx0
    info = {"own": own, "legs": legs, "at": (dy, dx)}
    names = ["hair", "body"] + list(cfg["parts"])
    base = np.zeros((H, W, 4), np.uint8)                 # every layer at the body's place (no lag): what they cover
    for name in names:
        lay(base, src, layers[name], dy, dx)
    info["hair"] = lay(b, src, layers["hair"], dy, dx, cols=mov["hair"][i], under=True)
    info["body"] = lay(b, src, layers["body"], dy, dx)
    for name in cfg["parts"]:
        info[name] = lay(b, src, layers[name], dy + mov[name][i], dx)
    put = np.zeros((H, W), bool)
    for name in names:
        info[name] &= b[..., 3] > 0
        put |= info[name]
    clear = b[..., 3] == 0
    gone = (a[..., 3] > 0) & clear                       # hers before, nothing laid on it
    revealed = (base[..., 3] > 0) & clear                # covered had the parts not moved off the body
    inside = (gone | revealed) & ndimage.binary_closing(put | legs, structure=disk(3))
    # inside her: from her legs' own colours where they are round it, else outline (between the laid layers)
    near_legs = inside & ndimage.binary_dilation(legs, structure=K8, iterations=2)
    fill_in(b, near_legs, legs & ~colour_mask(b, [out_c]))
    rest = inside & (b[..., 3] == 0)
    b[rest, :3] = out_c
    b[rest, 3] = 255
    # an edge that bares where she was: 2 squares of outline on the bared side
    clear = b[..., 3] == 0
    was = gone & clear
    solid = (b[..., 3] > 0) & ~colour_mask(b, [out_c])
    d = T.steps_from(solid, np.ones((H, W), bool), 2)
    bare = was & (d <= 2) & ndimage.binary_dilation(solid & ndimage.binary_dilation(was, structure=K8), structure=K8,
                                                    iterations=2)
    b[bare, :3] = out_c
    b[bare, 3] = 255
    shut = pockets(b) & ~pockets(a)
    b[shut, :3] = out_c
    b[shut, 3] = 255
    info["joined"] = ((near_legs | rest | bare | shut) & (b[..., 3] > 0)) & ~put
    return b, info


def make(hero):
    """-> ({"hd_<tag>", "<tag>", "lo_<tag>": [(frame, ms)]}, per-frame info, motion)."""
    import ppu_hd as P
    import ppu_one as O
    cfg = HEROES[hero]
    hid, pack, ppu, size = T.resolve(hero, T.all_heroes())
    frames = drawn(cfg)
    n = len(frames)
    i0 = cfg["from"]
    src = frames[i0][0]
    cy0, cx0 = src.shape[0] // 2, src.shape[1] // 2
    layers = pieces(src, cfg, i0)
    hair_cols = sorted(set(np.nonzero(layers["hair"])[1].tolist()))
    mov = motion(cfg, n, hair_cols)
    state = T.load_state()
    tp = state[hid]
    dense, info = [], []
    for i, (a, ms) in enumerate(frames):
        b, inf = compose(a, i, src, cy0, cx0, layers, mov, cfg)
        b2, _ = T.change_fixed(b, tp["hd"], tp["outline"], tp["grow"])
        inf["thinned"] = (b2 != b).any(-1)
        dense.append((b2, ms))
        info.append(inf)
    # the 1x frames from the dense ones (ppu_one), the lo_ ones (ppu_hd.add_lo), on the sheet's own rects
    an, px = T.read(hid, pack)
    tag = cfg["tag"]
    one_now = [px[int(f["data"]["y"]):int(f["data"]["y"]) + int(f["data"]["h"]),
                  int(f["data"]["x"]):int(f["data"]["x"]) + int(f["data"]["w"])] for f in an[tag]["frames"]]
    lo_now = [(int(f["data"]["w"]), int(f["data"]["h"])) for f in an["lo_" + tag]["frames"]]
    k = P.PPU[hero]
    sizes = O.sizes()
    shown = k / min(1.0, sizes.get(hero, 1.0))
    one, lost = [], []
    for (b, ms), o, (lw, lh) in zip(dense, one_now, lo_now):
        h, w = o.shape[:2]
        ws = O.lengths(w, k, b.shape[1], lw, False)
        hs = O.lengths(h, k, b.shape[0], lh, False)
        f, off = O.one_frame(b, w, h, 1.0 / shown, ws, hs)
        lost.append(off)
        one.append((f, ms))
    mini = {tag: one, "hd_" + tag: dense}
    P.add_lo(hero, mini)
    lo = []
    for (f, ms), (lw, lh) in zip(mini["lo_" + tag], lo_now):
        f2, _ = T.change_fixed(f, tp["lo"], tp["outline"], tp["grow"])
        if f2.shape[1] < lw or f2.shape[0] < lh:         # on the sheet's rect: grown alike at both ends, centre kept
            g = np.zeros((max(lh, f2.shape[0]), max(lw, f2.shape[1]), 4), np.uint8)
            oy, ox = (g.shape[0] - f2.shape[0]) // 2, (g.shape[1] - f2.shape[1]) // 2
            g[oy:oy + f2.shape[0], ox:ox + f2.shape[1]] = f2
            f2 = g
        lo.append((f2, ms))
    for inf, n_ in zip(info, lost):
        inf["one_lost"] = n_
    return {"hd_" + tag: dense, tag: one, "lo_" + tag: lo}, info, mov


def write(hero, new):
    """The tags' frames into the sheet's own rects (each frame keeps its size: the fanim does not change), the dense
    frames into the strip tools/art/ppu_hd.py reads (assets/source/ppu/<hero>_<tag>.png)."""
    hid, pack, ppu, size = T.resolve(hero, T.all_heroes())
    an, px = T.read(hid, pack)
    px = px.copy()
    for t, fr in new.items():
        rects = an[t]["frames"]
        if len(rects) != len(fr):
            sys.exit(f"{hid}: {t} has {len(rects)} frames, made {len(fr)}")
        for f, (a, ms) in zip(rects, fr):
            x, y, w, h = (int(round(f["data"][q])) for q in ("x", "y", "w", "h"))
            if (w, h) != (a.shape[1], a.shape[0]) or abs(f["duration"] * 1000 - ms) > 0.5:
                sys.exit(f"{hid}: {t} frame {w}x{h} / {f['duration']} s, made {a.shape[1]}x{a.shape[0]} / {ms} ms")
            px[y:y + h, x:x + w] = a
    Image.fromarray(px, "RGBA").save(lp(T.stem(hid, pack) + "#sheet.png"), optimize=True)
    tag = HEROES[hero]["tag"]
    dense = [a for a, _ in new["hd_" + tag]]
    H = max(a.shape[0] for a in dense)
    s = np.zeros((H, sum(a.shape[1] + 1 for a in dense) - 1, 4), np.uint8)
    x = 0
    for a in dense:
        s[:a.shape[0], x:x + a.shape[1]] = a
        x += a.shape[1] + 1
    Image.fromarray(s, "RGBA").save(lp(os.path.join(T.STRIPS, f"{T.strip_name(hid)}_{tag}.png")), optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True, choices=sorted(HEROES))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    new, info, _ = make(a.hero)
    hid, pack, _, _ = T.resolve(a.hero, T.all_heroes())
    if a.check:
        an, px = T.read(hid, pack)
        bad = []
        for t, fr in new.items():
            for f, (b, ms) in zip(an[t]["frames"], fr):
                x, y, w, h = (int(round(f["data"][q])) for q in ("x", "y", "w", "h"))
                if (w, h) != (b.shape[1], b.shape[0]) or not np.array_equal(px[y:y + h, x:x + w], b):
                    bad.append(t)
                    break
        tag = HEROES[a.hero]["tag"]
        strip = np.array(Image.open(lp(os.path.join(T.STRIPS, f"{T.strip_name(hid)}_{tag}.png"))).convert("RGBA"))
        x = 0
        for b, _ in new["hd_" + tag]:
            if not np.array_equal(strip[:b.shape[0], x:x + b.shape[1]], b):
                bad.append(f"assets/source/ppu/{T.strip_name(hid)}_{tag}.png")
                break
            x += b.shape[1] + 1
        if bad:
            sys.exit(f"{hid}: {', '.join(bad)} not as tools/art/run_body_anim.py makes them")
        print(f"ok: {hid} {tag} tags as made")
        return
    if a.dry:
        an, _ = T.read(hid, pack)
        for t, fr in new.items():
            print(t, [f"{b.shape[1]}x{b.shape[0]}" + ("" if (int(r["data"]["w"]), int(r["data"]["h"])) == (b.shape[1], b.shape[0])
                                                    else f" (sheet {int(r['data']['w'])}x{int(r['data']['h'])})")
                      for r, (b, _) in zip(an[t]["frames"], fr)])
        print("1x squares off the rect:", [inf["one_lost"] for inf in info])
        return
    write(a.hero, new)
    print(f"{hid}: {', '.join(new)} written ({len(next(iter(new.values())))} frames)")


if __name__ == "__main__":
    main()
