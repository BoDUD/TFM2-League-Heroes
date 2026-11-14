#!/usr/bin/env python3
"""The pixel-art pass for tools/lol/vfx_render.py's true-colour VFX renders: crisp effect frames that sit with our art.

    from vfx_pixel import pixelate
    hd, x1, palette = pixelate(renders, ppx=8, anchor=(48.5, 56.5))

Our effect sheets hold opaque pixels only (alpha 0 or 255) in 15-48 colours a tag, no outline (the art spec's VFX
rules). League's particles are soft, additive and layered, so the pass:
  1. box-filters each render (ppx canvas px a game px) to PPU 2 (2 px a game px) and to 1x;
  2. decides which pixels are drawn: coverage >= HI, or >= LO next to a strong core (a glow keeps a 1-2 px halo
     round its core instead of fading out), then drops lone specks that are not bright (sparkles stay);
  3. colours a drawn pixel by its own light with the faint ones darker and a little more saturated (a glow's edge
     on the ground), then snaps every frame of the tag to ONE palette: k-means in OKLab over the tag's drawn
     pixels (white kept when the core is white), or a given palette (the hero's present effect colours);
  4. cleans single-pixel colour noise (a pixel unlike all 8 neighbours takes their commonest colour) and pinholes;
  5. crops every frame round the anchor the game draws it at (the frame's centre): the 1x frame odd-sized with the
     anchor in its middle pixel, the PPU 2 twin exactly twice that (strips.write_sheet's hd_ pairs).
"""
import numpy as np

HI, LO, CORE = 0.34, 0.12, 0.6


def box(img, k, maxmix=0.0):
    """box-filter a straight RGBA float image by an integer factor (premultiplied) -> straight RGBA. maxmix pulls a
    block's coverage toward its densest pixel (a thin bright line - the E ring - keeps its strength at 1 px)."""
    H, W = img.shape[:2]
    H2, W2 = H // k, W // k
    a = img[:H2 * k, :W2 * k].astype(np.float64)
    pre = a.copy()
    pre[..., :3] *= pre[..., 3:4]
    blocks = pre.reshape(H2, k, W2, k, 4)
    pre = blocks.mean((1, 3))
    out = pre.copy()
    nz = pre[..., 3] > 1e-6
    out[nz, :3] = pre[nz, :3] / pre[nz, 3:4]
    if maxmix:
        amax = blocks[..., 3].max((1, 3))
        out[..., 3] = pre[..., 3] + maxmix * (amax - pre[..., 3])
    return out


def box_layers(matter, light, k, maxmix=0.0):
    """box-filter (matter premultiplied RGBA, light RGB) by k -> (matter straight RGBA, light RGB), maxmix pulling a
    block toward its densest / brightest pixel (thin rings and lines keep their strength at 1 px)."""
    H, W = light.shape[:2]
    H2, W2 = H // k, W // k
    mb = matter[:H2 * k, :W2 * k].astype(np.float64).reshape(H2, k, W2, k, 4)
    lb = light[:H2 * k, :W2 * k].astype(np.float64).reshape(H2, k, W2, k, 3)
    m = mb.mean((1, 3))
    li = lb.mean((1, 3))
    if maxmix:
        am = mb[..., 3].max((1, 3))
        m_a = m[..., 3] + maxmix * (am - m[..., 3])
        scale = np.where(m[..., 3] > 1e-6, m_a / np.maximum(m[..., 3], 1e-6), 0)
        m = m * scale[..., None]
        lv = li.max(-1)
        lmax = lb.max(-1).max((1, 3))
        lv2 = lv + maxmix * (lmax - lv)
        li = li * np.where(lv > 1e-6, lv2 / np.maximum(lv, 1e-6), 0)[..., None]
    out = np.zeros((H2, W2, 4))
    nz = m[..., 3] > 1e-6
    out[nz, :3] = m[nz, :3] / m[nz, 3:4]
    out[..., 3] = np.clip(m[..., 3], 0, 1)
    return out, li


def merge_layers(matter, light, gain, m_cut=0.45):
    """(matter straight RGBA, light RGB) -> straight RGBA for the drawn-pixel decision: light exposed by `gain` and
    laid over matter; matter counts only where it is dense (a faint dark mark under League's beam - Lux R's Burnt,
    Q's dark trail - would otherwise turn into an opaque brown band)."""
    v = light.max(-1)
    if gain:
        V = (1 - np.exp(-gain * v)) / (1 - np.exp(-gain))
    else:
        V = np.clip(v, 0, 1)
    hue = np.where(v[..., None] > 1e-6, light / np.maximum(v[..., None], 1e-6), 0)
    hue = np.clip(hue, 0, 1)
    # the light's colour bands follow its own strength, not the exposed coverage (a soft disk lifted to full
    # coverage keeps its white core): the faint edge its hue at full saturation, lighter inward, white where it
    # burns past 1 - a glow drawn the pixel-art way (saturated rim, pale core), never a darker, muddier shade
    mn = hue.min(-1, keepdims=True)
    sat = np.clip((hue - mn) / np.maximum(hue.max(-1, keepdims=True) - mn, 1e-6), 0, 1)
    sat = np.where((hue.max(-1, keepdims=True) - mn) > 0.08, 0.35 * sat + 0.65 * hue, hue)
    t = np.clip((v - 0.15) / 1.1, 0, 1)[..., None]
    lit = sat * (1 - t ** 1.5) + t ** 1.5
    am = np.where(matter[..., 3] >= m_cut, matter[..., 3], 0)
    a = 1 - (1 - V) * (1 - am)
    mix = lit * V[..., None] + matter[..., :3] * am[..., None] * (1 - V[..., None])
    rgb = np.where(a[..., None] > 1e-6, mix / np.maximum(a[..., None], 1e-6), 0)
    return np.concatenate([np.clip(rgb, 0, 1), a[..., None]], -1)


def expose(img, gain):
    """lift faint light: coverage a -> (1 - e^(-gain a)) / (1 - e^-gain) (1 stays 1). League tunes its additive glows
    for its dark map; drawn opaque on our lighter grass the faint layers would otherwise drop out."""
    if not gain:
        return img
    out = img.copy()
    out[..., 3] = (1 - np.exp(-gain * img[..., 3])) / (1 - np.exp(-gain))
    return out


# ----------------------------------------------------------------------------- colour
def srgb_to_lin(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def oklab(rgb):
    lin = srgb_to_lin(rgb)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    lms = np.cbrt(lin @ M1.T)
    return lms @ M2.T


def kmeans(x, w, k, iters=30, seed=3):
    """weighted k-means (rows of x) -> centres."""
    rng = np.random.default_rng(seed)
    n = len(x)
    if n <= k:
        return x.copy()
    p = w / w.sum()
    c = [x[rng.choice(n, p=p)]]
    for _ in range(k - 1):                                   # k-means++ seeding
        d = np.min(((x[:, None] - np.array(c)[None]) ** 2).sum(-1), 1)
        q = d * w
        c.append(x[rng.choice(n, p=q / q.sum())] if q.sum() > 0 else x[rng.integers(n)])
    c = np.array(c)
    for _ in range(iters):
        lab = np.argmin(((x[:, None] - c[None]) ** 2).sum(-1), 1)
        for j in range(k):
            m = lab == j
            if m.any():
                c[j] = (x[m] * w[m, None]).sum(0) / w[m].sum()
    return c


def shade(rgb, a):
    """a drawn pixel's colour from its straight colour and coverage: faint = darker, a little more saturated."""
    s = np.clip((a - LO) / (0.85 - LO), 0, 1)[..., None]
    mx = rgb.max(-1, keepdims=True)
    mn = rgb.min(-1, keepdims=True)
    sat_push = (rgb - mn) * (0.25 * (1 - s))                  # away from grey in the faint parts
    out = (rgb + sat_push) * (0.62 + 0.38 * s)
    return np.clip(out, 0, 1), mx


# ----------------------------------------------------------------------------- the pass
def _drawn(a):
    """which pixels are drawn: strong ones, and faint ones within 2 px of a core."""
    strong = a >= HI
    core = a >= CORE
    near = np.zeros_like(core)
    H, W = a.shape
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx * dx + dy * dy > 5:
                continue
            sh = np.zeros_like(core)
            ys, yd = (slice(max(dy, 0), H), slice(0, H - max(dy, 0))) if dy >= 0 else (slice(0, H + dy), slice(-dy, H))
            xs, xd = (slice(max(dx, 0), W), slice(0, W - max(dx, 0))) if dx >= 0 else (slice(0, W + dx), slice(-dx, W))
            sh[ys, xs] = core[yd, xd]
            near |= sh
    return strong | ((a >= LO) & near)


def _neigh(m):
    """count of drawn 8-neighbours."""
    p = np.pad(m.astype(np.int32), 1)
    H, W = m.shape
    return sum(p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)


def _clean(idx, drawn, lum):
    """lone specks out (unless bright), pinholes filled, single-pixel colour noise smoothed."""
    n8 = _neigh(drawn)
    drawn = drawn & ((n8 > 0) | (lum > 0.72))
    H, W = idx.shape
    p = np.pad(drawn.astype(np.int32), 1)
    n4 = p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
    hole = ~drawn & (n4 >= 3)
    pi = np.pad(idx, 1, constant_values=-1)
    pd = np.pad(drawn, 1)
    out = idx.copy()
    for y, x in zip(*np.nonzero(hole | drawn)):
        nb = [pi[y + 1 + dy, x + 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
              if (dy or dx) and pd[y + 1 + dy, x + 1 + dx]]
        if not nb:
            continue
        if hole[y, x] or (drawn[y, x] and idx[y, x] not in nb and len(nb) >= 5):
            vals, cnt = np.unique(nb, return_counts=True)
            out[y, x] = vals[np.argmax(cnt)]
    return out, drawn | hole


def _majority(idx, drawn, passes=1):
    """hue noise out: a drawn pixel whose colour at most one drawn neighbour shares takes the colour most of its
    drawn neighbours have (4 or more of 8) - Lux's rainbow multiplier otherwise speckles every glow."""
    H, W = idx.shape
    for _ in range(passes):
        pi = np.pad(idx, 1, constant_values=-1)
        pd = np.pad(drawn, 1)
        out = idx.copy()
        for y, x in zip(*np.nonzero(drawn)):
            nb = [pi[y + 1 + dy, x + 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                  if (dy or dx) and pd[y + 1 + dy, x + 1 + dx]]
            if len(nb) < 4:
                continue
            vals, cnt = np.unique(nb, return_counts=True)
            own = cnt[vals == idx[y, x]].sum()
            j = np.argmax(cnt)
            if own <= 1 and cnt[j] >= 4:
                out[y, x] = vals[j]
        idx = out
    return idx


def pixelate(renders, ppx, anchor, k=16, palette=None, ppu=2, keep_white=True, min_half=(1, 1), gain=0.0,
             maxmix=0.0, majority=1):
    """renders: straight RGBA float arrays (H, W, 4) - or (matter, light) layer pairs (vfx_render layers=True) - at
    `ppx` canvas px a game px, the anchor at game px `anchor`
    (x, y: the centre of a 1x pixel, k + 0.5). Returns (hd frames, 1x frames, palette (n, 3) uint8) - frames as
    uint8 RGBA arrays cropped round the anchor, all hd frames exactly twice their 1x twin."""
    assert ppx % ppu == 0, "ppx must be a multiple of the PPU"
    if renders and isinstance(renders[0], tuple):            # (matter, light) layers: light exposed, faint matter out
        hds = [merge_layers(*box_layers(m, li, ppx // ppu, maxmix), gain) for m, li in renders]
        ones = [merge_layers(*box_layers(m, li, ppx, maxmix), gain) for m, li in renders]
    else:
        hds = [expose(box(r, ppx // ppu, maxmix), gain) for r in renders]
        ones = [expose(box(r, ppx, maxmix), gain) for r in renders]
    # 1. drawn pixels and their colours (PPU 2 decides the palette)
    layered = bool(renders) and isinstance(renders[0], tuple)
    data = []
    for f in hds:
        a = f[..., 3]
        d = _drawn(a)
        col = f[..., :3] if layered else shade(f[..., :3], a)[0]
        data.append((d, col))
    if palette is None:
        pts = np.concatenate([c[d] for d, c in data]) if any(d.any() for d, _ in data) else np.zeros((0, 3))
        wts = np.concatenate([f[..., 3][d] for (d, _), f in zip(data, hds)]) if len(pts) else np.zeros(0)
        if len(pts) > 40000:
            sel = np.random.default_rng(5).choice(len(pts), 40000, replace=False)
            pts, wts = pts[sel], wts[sel]
        if len(pts):
            cen = kmeans(oklab(pts), wts + 0.05, min(k, len(pts)))
            # back to RGB: the mean colour of each cluster
            lab = np.argmin(((oklab(pts)[:, None] - cen[None]) ** 2).sum(-1), 1)
            pal = np.array([pts[lab == j].mean(0) if (lab == j).any() else np.zeros(3) for j in range(len(cen))])
            if keep_white and (pts.min(1) > 0.93).sum() > 3:
                pal[np.argmax(pal.sum(1))] = 1.0
        else:
            pal = np.ones((1, 3))
    else:
        pal = np.asarray(palette, np.float64) / 255.0
    pal_lab = oklab(pal)

    def quant(f, d, col):
        lab = oklab(col.reshape(-1, 3))
        idx = np.argmin(((lab[:, None] - pal_lab[None]) ** 2).sum(-1), 1).reshape(d.shape)
        lum = col.max(-1)
        idx, d = _clean(idx, d, lum)
        if majority:
            idx = _majority(idx, d, majority)
        out = np.zeros(d.shape + (4,), np.uint8)
        out[d, :3] = (pal[idx[d]] * 255 + 0.5).astype(np.uint8)
        out[d, 3] = 255
        return out

    hd_q = [quant(f, d, c) for f, (d, c) in zip(hds, data)]
    one_q = []
    for f in ones:
        a = f[..., 3]
        d = _drawn(a)
        col = f[..., :3] if layered else shade(f[..., :3], a)[0]
        one_q.append(quant(f, d, col))
    # 2. crop round the anchor: one half-extent per frame (in game px), odd 1x sizes, hd twice that
    ax, ay = anchor
    cx1, cy1 = int(np.floor(ax)), int(np.floor(ay))           # the 1x pixel holding the anchor
    hd_out, one_out = [], []
    for hq, oq in zip(hd_q, one_q):
        m = hq[..., 3] > 0
        if m.any():
            ys, xs = np.nonzero(m)
            ex = int(np.ceil(max(abs(xs.min() / ppu - ax), abs((xs.max() + 1) / ppu - ax)) - 0.5))
            ey = int(np.ceil(max(abs(ys.min() / ppu - ay), abs((ys.max() + 1) / ppu - ay)) - 0.5))
        else:
            ex, ey = 0, 0
        ex, ey = max(ex, min_half[0] - 1), max(ey, min_half[1] - 1)
        x0, y0 = cx1 - ex, cy1 - ey                            # 1x crop (2ex+1) x (2ey+1)
        one_out.append(_crop(oq, x0, y0, 2 * ex + 1, 2 * ey + 1))
        hd_out.append(_crop(hq, x0 * ppu, y0 * ppu, (2 * ex + 1) * ppu, (2 * ey + 1) * ppu))
    return hd_out, one_out, (pal * 255 + 0.5).astype(np.uint8)


def _crop(img, x0, y0, w, h):
    out = np.zeros((h, w, 4), np.uint8)
    H, W = img.shape[:2]
    sx0, sy0 = max(x0, 0), max(y0, 0)
    sx1, sy1 = min(x0 + w, W), min(y0 + h, H)
    if sx1 > sx0 and sy1 > sy0:
        out[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = img[sy0:sy1, sx0:sx1]
    return out
