#!/usr/bin/env python3
"""League's particle MOTION drawn as pixel-art VFX (Pixel-FX-Designer style): vfx_render.py's simulation gives when
each particle is born, where it goes, how big it is and how long it lives; every particle is then drawn as a solid
pixel primitive at PPU 2 - a round dot, a 4-point star, a streak along its motion, a thick ring, a shaded puff - in
painter's order, with no soft alpha, coloured from a ramp per effect (pale core -> saturated -> deep -> dark edge,
and an outline colour for smoke) that each particle walks by its life.

    from vfx_pixelfx import render_tag
    hd, x1 = render_tag(scene, intervals, vfxs)          # PPU 2 frames and their 1x twins, cropped round the anchor

What decides a particle's primitive (emitter by emitter, `kinds` in a scene overrides):
  - Beam emitters of a play: ONE composite beam - a white core, stepped glow bands as wide as League's beam layers
    (the widest the deepest colour), edges flickering a square, a star flare at each end.
  - Trails: a stepped polyline through the emitter's particles, thick and pale at the head, thin and deep at the tail.
  - Rays and quads whose texture is long and thin, or isDirectionOriented ones: streaks along their motion.
  - Ring textures (a hollow middle) and flat ring meshes: thick rings (at least 2 squares), pale inside, deep outside.
  - Spiky textures (flares, star filters): 4-point stars; soft radial glows: round dots with a stepped core.
  - Alpha-blended particles (League's smoke, fire clouds, rocks): puffs shaded in 3 tones with a dark outline, from
    the smoke ramp when dark, the light ramp when bright (a fireball); flat ones on the ground: dark ground marks.
  - Other meshes (Jinx's rocket): the textured model itself, alpha-cut and outlined.
Sizes are integers that step down with the particle's own League scale; a particle fades in 3 steps only (solid,
dithered 1 in 2, gone) and particles too faint to see are dropped.
"""
import math

import numpy as np

import vfx_pixel as X
import vfx_render as R

PPU = 2
# radius ladder (squares at PPU 2): sizes step, never slide
STEPS = np.array([0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0, 24.0, 28.0, 32.0,
                  40.0, 48.0, 56.0, 64.0])


def step(r):
    return float(STEPS[np.argmin(np.abs(STEPS - r))])


# ----------------------------------------------------------------------------- colours
def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float64) / 255.0


def _hsv(rgb):
    r, g, b = rgb
    mx, mn = max(r, g, b), min(r, g, b)
    v = mx
    s = 0.0 if mx <= 1e-9 else (mx - mn) / mx
    if mx - mn < 1e-9:
        h = 0.0
    elif mx == r:
        h = ((g - b) / (mx - mn)) % 6
    elif mx == g:
        h = (b - r) / (mx - mn) + 2
    else:
        h = (r - g) / (mx - mn) + 4
    return h * 60.0, s, v


def _rgb(h, s, v):
    h = (h % 360) / 60.0
    c = v * s
    x = c * (1 - abs(h % 2 - 1))
    m = v - c
    i = int(h) % 6
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][i]
    return np.array([r + m, g + m, b + m])


def ramp_from(base, n=6):
    """a ramp from one League colour: [core (near white), pale, saturated, deep, dark, outline]; the dark end turns its
    hue toward red-purple for warm colours and toward violet for cool ones, as pixel artists shade."""
    h, s, v = _hsv(np.clip(base, 0, 1))
    s = max(s, 0.55)
    warm = (h < 70 or h > 300)
    turn = -14 if warm else 18
    sat = _rgb(h, min(1.0, s * 1.1 + 0.1), 1.0)
    out = [0.15 * sat + 0.85, 0.5 * sat + 0.5, sat,
           _rgb(h + turn, min(1.0, s + 0.15), 0.8),
           _rgb(h + 2 * turn, min(1.0, s + 0.2), 0.55),
           _rgb(h + 3 * turn, 0.75, 0.25)]
    return [np.clip(c, 0, 1) for c in out[:n]]


def smoke_ramp(base=None):
    """grey-brown smoke: [highlight, light, body, shadow, deep shadow, outline]."""
    base = np.array([0.55, 0.5, 0.48]) if base is None else np.clip(base, 0, 1)
    h, s, v = _hsv(base)
    s = min(max(s, 0.08), 0.35)
    return [_rgb(h, s * 0.6, 0.86), _rgb(h, s * 0.8, 0.7), _rgb(h, s, 0.55), _rgb(h + 10, s + 0.08, 0.4),
            _rgb(h + 20, s + 0.12, 0.28), _rgb(h + 30, s + 0.15, 0.14)]


# ----------------------------------------------------------------------------- textures
_TEX = {}


def tex_kind(tex):
    """what a particle texture is, as a pixel artist would draw it: ring / star / streak / glow / blob / empty, with its
    mean colour (energy-weighted) and the radius (fraction of the half-quad) holding most of its energy."""
    key = id(tex)
    if key in _TEX:
        return _TEX[key]
    a = tex[..., 3] * tex[..., :3].max(-1)
    h, w = a.shape
    tot = a.sum()
    if tot < 1e-6:
        _TEX[key] = ("empty", np.ones(3), 0.5)
        return _TEX[key]
    mean = (tex[..., :3] * a[..., None]).sum((0, 1)) / tot
    yy, xx = np.mgrid[:h, :w]
    nx, ny = (xx - w / 2 + 0.5) / (w / 2), (yy - h / 2 + 0.5) / (h / 2)
    r = np.hypot(nx, ny)
    ang = np.arctan2(ny, nx)
    prof = np.array([a[(r >= k / 10) & (r < (k + 1) / 10)].mean() if ((r >= k / 10) & (r < (k + 1) / 10)).any() else 0
                     for k in range(10)])
    cum = np.cumsum([a[(r >= k / 10) & (r < (k + 1) / 10)].sum() for k in range(10)])
    r80 = (np.searchsorted(cum, 0.8 * cum[-1]) + 1) / 10.0
    cx, cy = (a * nx).sum() / tot, (a * ny).sum() / tot
    sxx, syy = (a * (nx - cx) ** 2).sum() / tot, (a * (ny - cy) ** 2).sum() / tot
    elong = max(sxx, syy) / max(min(sxx, syy), 1e-6)
    band = (r > 0.25) & (r < 0.8)
    spiky = 0.0
    if band.any():
        bins = ((ang[band] + math.pi) / (2 * math.pi) * 24).astype(int) % 24
        sums = np.bincount(bins, weights=a[band], minlength=24)
        spiky = sums.std() / max(sums.mean(), 1e-6)
    peak = int(np.argmax(prof))
    if max(h, w) / min(h, w) >= 4 or elong > 6:
        kind = "streak"
    elif peak >= 3 and prof[peak] > 2.2 * prof[0]:
        kind = "ring"
    elif spiky > 0.55:
        kind = "star"
    elif prof[0] > 1e-6 and prof[6] < 0.35 * prof[0]:
        kind = "glow"
    else:
        kind = "blob"
    _TEX[key] = (kind, mean, r80)
    return _TEX[key]


# ----------------------------------------------------------------------------- the canvas
class Pix:
    """an RGBA uint8 canvas at PPU 2; later draws cover earlier ones (painter's order)."""

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.img = np.zeros((H, W, 4), np.uint8)
        self.yy, self.xx = np.mgrid[:H, :W]

    def paint(self, mask, col, dither=0):
        if dither:
            mask = mask & (((self.xx + self.yy) % 2) == 0)
        c = (np.clip(col, 0, 1) * 255 + 0.5).astype(np.uint8)
        self.img[mask, :3] = c
        self.img[mask, 3] = 255

    def _box(self, cx, cy, rx, ry):
        x0, x1 = max(int(cx - rx - 1), 0), min(int(cx + rx + 2), self.W)
        y0, y1 = max(int(cy - ry - 1), 0), min(int(cy + ry + 2), self.H)
        return x0, x1, y0, y1

    def ellipse_mask(self, cx, cy, rx, ry):
        """pixels whose centres lie in the ellipse (rx, ry squares; 0 = the one pixel under the centre)."""
        m = np.zeros((self.H, self.W), bool)
        x0, x1, y0, y1 = self._box(cx, cy, rx, ry)
        if x1 <= x0 or y1 <= y0:
            return m
        gx = self.xx[y0:y1, x0:x1] + 0.5 - cx
        gy = self.yy[y0:y1, x0:x1] + 0.5 - cy
        if rx < 0.6 and ry < 0.6:
            m[int(np.clip(cy, 0, self.H - 1)), int(np.clip(cx, 0, self.W - 1))] = True
            return m
        m[y0:y1, x0:x1] = (gx / max(rx, 0.5)) ** 2 + (gy / max(ry, 0.5)) ** 2 <= 1.0
        return m

    def dot(self, cx, cy, r, cols, dither=0, squash=1.0):
        """a round dot of radius r (squares) stepped inward: cols[0] outside, then each next colour at half the
        radius before."""
        rr = r
        for c in cols:
            if rr < 0:
                break
            self.paint(self.ellipse_mask(cx, cy, rr, rr * squash), c, dither)
            rr = step(rr * 0.5) if rr >= 2 else (rr - 1.5 if rr >= 1 else -1)

    def star(self, cx, cy, r, cols, dither=0):
        """a 4-point star: arms r squares long (1 square wide, 3 near the middle on big ones), a dot in the middle,
        and short diagonal arms on big stars."""
        r = max(1.0, r)
        ix, iy = int(math.floor(cx)), int(math.floor(cy))
        m = np.zeros((self.H, self.W), bool)
        L = int(round(r))
        for k in range(-L, L + 1):
            for x, y in ((ix + k, iy), (ix, iy + k)):
                if 0 <= x < self.W and 0 <= y < self.H:
                    m[y, x] = True
        if L >= 5:
            for k in range(-L // 2, L // 2 + 1):
                for x, y in ((ix + k, iy - 1), (ix + k, iy + 1), (ix - 1, iy + k), (ix + 1, iy + k)):
                    if 0 <= x < self.W and 0 <= y < self.H and abs(k) <= L // 3:
                        m[y, x] = True
            D = max(1, L // 3)
            for k in range(-D, D + 1):
                for x, y in ((ix + k, iy + k), (ix + k, iy - k)):
                    if 0 <= x < self.W and 0 <= y < self.H:
                        m[y, x] = True
        self.paint(m, cols[min(1, len(cols) - 1)], dither)
        self.dot(cx, cy, step(max(0.0, r * 0.28)), cols[min(1, len(cols) - 1):][:1] + cols[:1], dither)

    def line(self, p0, p1, w, cols, dither=0):
        """a streak from p0 (tail) to p1 (head) w squares wide: the colours step from cols[-1] at the tail to cols[0]
        at the head."""
        p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
        L = max(1.0, float(np.hypot(*(p1 - p0))))
        n = max(2, int(L * 2) + 1)
        for k in range(n):
            t = k / (n - 1)
            c = cols[min(len(cols) - 1, int((1 - t) * len(cols)))]
            q = p0 + (p1 - p0) * t
            self.paint(self.ellipse_mask(q[0], q[1], w / 2, w / 2), c, dither)

    def ring(self, cx, cy, rx, ry, th, cols, dither=0):
        """a ring th squares thick (measured along each ray from the centre, so the flattened top and bottom keep it)
        round the ellipse (rx, ry): cols from the inside out in equal bands."""
        th = max(2.0, th)
        x0, x1, y0, y1 = self._box(cx, cy, rx + th, ry + th)
        if x1 <= x0 or y1 <= y0:
            return
        gx = self.xx[y0:y1, x0:x1] + 0.5 - cx
        gy = self.yy[y0:y1, x0:x1] + 0.5 - cy
        q = np.sqrt((gx / max(rx, 0.5)) ** 2 + (gy / max(ry, 0.5)) ** 2)
        d = np.hypot(gx, gy) * (q - 1) / np.maximum(q, 1e-6)
        nb = len(cols)
        for i, c in enumerate(cols):
            lo = -th / 2 + i * th / nb
            m = np.zeros((self.H, self.W), bool)
            m[y0:y1, x0:x1] = (d >= lo) & (d < lo + th / nb)
            self.paint(m, c, dither)

    def puff(self, cx, cy, r, ramp, outline=True, dither=0):
        """a cartoon puff: body, a highlight up-left, a shadow down-right, a dark outline."""
        r = max(1.0, r)
        body = self.ellipse_mask(cx, cy, r, r * 0.9)
        if outline:
            ring = self.ellipse_mask(cx, cy, r + 1, r * 0.9 + 1) & ~body
            self.paint(ring, ramp[5], dither)
        self.paint(body, ramp[2], dither)
        sh = body & ~self.ellipse_mask(cx - r * 0.25, cy - r * 0.25, r, r * 0.9)
        self.paint(sh, ramp[3], dither)
        if r >= 2:
            hl = self.ellipse_mask(cx - r * 0.3, cy - r * 0.32, r * 0.45, r * 0.4) & body
            self.paint(hl, ramp[1], dither)
        if r >= 5:
            hl2 = self.ellipse_mask(cx - r * 0.38, cy - r * 0.4, r * 0.18, r * 0.16) & body
            self.paint(hl2, ramp[0], dither)

    def outline(self, mask, col):
        """a 1-square outline round mask (4-neighbours), drawn under nothing: only on empty pixels."""
        p = np.pad(mask, 1)
        ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~mask & (self.img[..., 3] == 0)
        self.paint(ring, col)


# ----------------------------------------------------------------------------- particles -> primitives
def emitter_colour(em):
    """an emitter's own colour: its texture's (energy-weighted) times its birth colour times its colour at mid-life."""
    tc = tex_kind(em.tex)[1] if em.tex is not None else np.ones(3)
    c = em.bcolor.at(0.0)[:3] * em.color.at(0.4)[:3] * tc
    if em.palette is not None:
        row = (np.floor(em.palette["sel"].at(0.0)[0]) % em.palette["count"] + 0.5) / em.palette["count"]
        pal = R.sample(em.palette["tex"], np.array([0.8]), np.array([row]), wrap=False)[0, :3]
        c = pal * em.bcolor.at(0.0)[:3]
    return c


def kind_of(em, kinds):
    if em.name in kinds:
        return kinds[em.name]
    if em.prim == "Beam":
        return "beam"
    if em.prim in ("CameraTrail", "ArbitraryTrail"):
        return "trail"
    if em.prim == "Mesh":
        v = em.mesh[0]
        ext = v.max(0) - v.min(0)
        r = np.hypot(v[:, 0], v[:, 2])
        if ext[1] < 0.05 * max(ext[0], ext[2]):
            return "ring" if r.min() > 0.4 * r.max() else "disc"
        if ext[1] > 0.6 * max(ext[0], ext[2]) and r.min() > 0.8 * r.max():
            return "pillar"
        return "model"
    if em.prim == "Ray":
        return "streak"
    if em.tex is None:
        return "skip"
    tk = tex_kind(em.tex)[0]
    if em.blend == R.BLEND_ALPHA:
        if em.prim == "ArbitraryQuad" and em.ground:
            return "mark"
        lum = float(np.max(emitter_colour(em)))
        return "fire" if lum > 0.55 and tk in ("glow", "blob") else "puff" if tk != "streak" else "streak"
    if em.dir_oriented or tk == "streak":
        return "streak"
    return {"ring": "ring", "star": "star", "glow": "dot", "blob": "dot", "empty": "skip"}[tk]


class Look:
    """per scene (its "pixelfx" entry): named colour ramps and, when given, the emitters drawn ("keep": emitter ->
    {"kind", "ramp", "size", "cut"}) - League's motion, our art direction. Without "keep" every emitter is drawn by
    kind_of() with a ramp from its own colour."""

    def __init__(self, scene, plays):
        px = scene.get("pixelfx", {})
        self.kinds = px.get("kinds", {})
        self.keep = px.get("keep")
        self.size = px.get("size", 1.0)
        self.cut = px.get("cut", 0.12)
        self.outline = px.get("outline", True)
        self.ramps = {}
        for name, spec in px.get("ramps", {}).items():
            if isinstance(spec, list):
                r = [hexrgb(h) for h in spec]
                r = (r + r[-1:] * 6)[:6]
            elif name.startswith("smoke"):
                r = smoke_ramp(hexrgb(spec))
            else:
                r = ramp_from(hexrgb(spec))
            self.ramps[name] = r
        if "smoke" not in self.ramps:
            self.ramps["smoke"] = smoke_ramp()
        self.smoke = self.ramps["smoke"]
        if not any(k != "smoke" for k in self.ramps):     # League's strongest saturated light colour
            cols = []
            for pl in plays:
                for em in pl.emitters:
                    if em.hidden or em.blend == R.BLEND_ALPHA:
                        continue
                    c = emitter_colour(em)
                    h, s_, v = _hsv(np.clip(c / max(c.max(), 1e-6), 0, 1))
                    if s_ > 0.2:
                        cols.append((h, s_ * float(c.max())))
            base = _rgb(max(cols, key=lambda x: x[1])[0], 0.8, 1.0) if cols else np.array([1.0, 0.85, 0.4])
            self.ramps["light"] = ramp_from(base)
        self.default = next(k for k in self.ramps if k != "smoke")

    def spec(self, em):
        if self.keep is not None:
            return self.keep.get(em.name)
        return {}

    def ramp(self, em, spec=None):
        spec = spec or {}
        if spec.get("ramp"):
            return self.ramps[spec["ramp"]]
        return self.ramps[self.default]


def _strength(em, p, age, t):
    """how visible a particle is (0..1): its alpha times its colour's brightness for light, its alpha for matter."""
    col = R.particle_colour(em, p, age, t)
    tk = tex_kind(em.tex) if em.tex is not None else ("glow", np.ones(3), 0.5)
    a = float(np.clip(col[3], 0, 1))
    if em.blend == R.BLEND_ALPHA:
        return a, col
    return float(np.clip(a * max(col[:3].max(), 0.0) * max(tk[1].max(), 0.35) * 1.6, 0, 1)), col


def draw_frame(sim, cam, look, pix):
    """every live particle of the scene as a pixel primitive (painter's order: ground first, then pass, far to near)."""
    groups = {}
    for pl, em, p, age, pos in sim.snapshot():
        groups.setdefault((id(pl), id(em)), (pl, em, []))[2].append((p, age, pos))
    order = []
    for pl, em, parts in groups.values():
        spec = look.spec(em)
        if spec is None:
            continue
        depth = float(np.mean([cam.project(pos)[1] for _, _, pos in parts]))
        layer = spec.get("layer", 0 if em.ground else 1)
        order.append((layer, spec.get("pass", em.pass_), depth, pl, em, parts, spec))
    order.sort(key=lambda x: (x[0], x[1], x[2]))
    ppu = cam.s * cam.ppx                      # squares a League unit
    beams = {}
    for _g, _ps, _d, pl, em, parts, spec in order:
        kind = spec.get("kind") or kind_of(em, look.kinds)
        if kind == "skip":
            continue
        ramp = look.ramp(em, spec)
        cut = spec.get("cut", look.cut)
        k_size = spec.get("size", 1.0) * look.size
        if kind == "beam":
            beams.setdefault(id(pl), (pl, []))[1].append((em, parts, ramp, k_size))
            continue
        if kind == "trail":
            _trail(pix, cam, em, parts, ramp, cut, ppu * k_size)
            continue
        for p, age, pos in sorted(parts, key=lambda x: cam.project(x[2])[1]):
            t = min(1.0, age / max(p.life, 1e-6))
            a, col = _strength(em, p, age, t)
            if a < cut:
                continue
            dither = 1 if a < max(0.3, cut * 1.8) else 0
            sc = p.scale * em.scale.at(t)
            if em.uniform:
                sc = np.full(3, sc[0])
            size = float(abs(sc[0])) * ppu * k_size              # the quad's width in squares
            if em.prim == "Mesh":                                # a mesh's scale multiplies its own radius
                size *= 2.0 * float(np.max(np.hypot(em.mesh[0][:, 0], em.mesh[0][:, 2])))
                if kind in ("ring", "disc", "pillar", "model"):
                    _mesh(pix, cam, pl, em, p, age, t, pos, sc, ramp, int(np.clip(round(0.6 + 2.6 * t - 1.2 * (a - 0.5))
                                                                                     + spec.get("shift", 0), 0, 4)),
                          kind, look, dither if size < 16 else 0, spec)
                    continue
            if size > 14:
                dither = 0                                       # big shapes never dither: they step and go
            (cx, cy), _ = cam.project(pos)
            # walk the ramp by life: young and strong near the core colour, old toward the deep end
            idx = int(np.clip(round(0.6 + 2.6 * t - 1.2 * (a - 0.5)) + spec.get("shift", 0), 0, 4))
            cols = [ramp[min(4, idx + 2)], ramp[min(4, idx + 1)], ramp[idx]]
            r80 = tex_kind(em.tex)[2] if em.tex is not None else 0.6
            if kind == "dot":
                pix.dot(cx, cy, step(max(0.0, size * 0.5 * r80 * 0.75)), cols, dither)
            elif kind == "star":
                pix.star(cx, cy, step(max(1.0, size * 0.5 * r80 * 0.9)), [ramp[max(0, idx - 1)], ramp[min(4, idx + 1)]],
                         dither)
            elif kind == "burst":
                _burst(pix, cx, cy, size * 0.5 * 0.55, ramp, t, dither)
            elif kind == "ring":
                rx = step(max(1.0, size * 0.5 * 0.72))
                flat = cam.sp if (em.ground or em.prim == "ArbitraryQuad") else 1.0
                pix.ring(cx, cy, rx, rx * flat, float(spec.get("px", max(2.0, step(size * 0.08)))),
                         [ramp[max(0, idx)], ramp[min(4, idx + 1)], ramp[min(4, idx + 2)]], dither)
            elif kind == "streak":
                _streak(pix, cam, em, p, age, t, pos, size, sc, ramp, idx, dither, spec.get("max_len", 40.0))
            elif kind == "spark":
                _streak(pix, cam, em, p, age, t, pos, size, sc, ramp, max(0, idx - 1), dither, spec.get("max_len", 6.0))
            elif kind == "chunk":
                r = step(max(1.0, size * 0.5 * 0.5))
                body = pix.ellipse_mask(cx, cy, r, r)
                pix.outline(body, look.smoke[5])
                pix.paint(body, look.smoke[3])
                pix.paint(pix.ellipse_mask(cx - 0.5, cy - 0.5, max(0.0, r - 1), max(0.0, r - 1)), look.smoke[1])
            elif kind in ("puff", "fireball"):
                r = step(max(1.0, size * 0.5 * 0.62))
                if kind == "fireball":
                    rp = ramp if t < spec.get("smoke_at", 0.55) else look.smoke
                    if t >= spec.get("smoke_at", 0.55) * 0.7 and rp is ramp:
                        rp = ramp[1:] + ramp[-1:]                 # darker on its way to smoke
                else:
                    rp = look.smoke
                pix.puff(cx, cy, r, rp, look.outline, dither)
            elif kind == "decal":
                _decal(pix, cam, pl, em, p, age, pos, ramp if spec.get("ramp") else look.smoke, look, dither)
            elif kind == "mark":
                r = max(1.0, size * 0.5 * 0.7)
                pix.paint(pix.ellipse_mask(cx, cy, r, r * cam.sp), look.smoke[4], dither)
                pix.paint(pix.ellipse_mask(cx, cy, r * 0.6, r * 0.6 * cam.sp), look.smoke[5], dither)
    for pl, items in beams.values():
        _beam(pix, cam, pl, items, look, ppu)


def _burst(pix, cx, cy, r, ramp, t, dither):
    """an explosion's flash: a stepped disc (saturated rim, pale, white core) and 8 rays that shrink after the peak."""
    r = step(max(2.0, r))
    arms = step(r * (1.7 - 0.8 * t))
    pix.star(cx, cy, arms, [ramp[0], ramp[2]], dither)
    pix.dot(cx, cy, r, [ramp[2], ramp[1], ramp[0]], dither)


def _decal(pix, cam, pl, em, p, age, pos, ramp, look, dither):
    """a particle's own picture (Jinx's smiling smoke cloud), alpha-cut, its light and dark parts mapped onto the ramp
    in 4 tones, outlined."""
    cv = R.Canvas(pix.W, pix.H, None)
    R.draw_particle(cv, cam, pl, em, p, age, pos)
    out = cv.rgba()
    m = out[..., 3] > 0.45
    if not m.any():
        return
    lum = out[..., :3].max(-1)
    lv = lum[m]
    lo, hi = np.percentile(lv, 5), np.percentile(lv, 95)
    k = np.clip((lum - lo) / max(hi - lo, 1e-6), 0, 1)
    tone = np.clip((3.99 * (1 - k)).astype(int), 0, 3)       # 0 = lightest
    if look.outline:
        pix.outline(m, ramp[5])
    for i in range(4):
        pix.paint(m & (tone == i), ramp[min(4, i + 1)], dither)


def _streak(pix, cam, em, p, age, t, pos, size, sc, ramp, idx, dither, max_len=40.0):
    """a ray (from the particle out along its turned up axis) or a spark smeared along its motion: pale head, deep
    tail."""
    (hx, hy), _ = cam.project(pos)
    head = np.array([hx, hy])
    if em.prim == "Ray":
        Rr = R.rot_matrix(p.rot + p.rotv * age + em.rot.at(t))
        axis = Rr @ np.array([0, 1.0, 0])
        tip = cam.project(pos + axis * abs(sc[1]))[0]
        dv = tip - head
        n = float(np.hypot(*dv))
        if n > max_len:
            tip = head + dv / n * max_len
        w = 1.0 if abs(sc[0]) * cam.s * cam.ppx < 6 else 2.0
        pix.line(tip, head, w, [ramp[max(0, idx)], ramp[min(4, idx + 1)], ramp[min(4, idx + 2)]], dither)
        return
    v2 = cam.project(pos + p.vel * 0.02)[0] - head
    n = float(np.hypot(*v2))
    d = v2 / n if n > 1e-6 else np.array([1.0, 0.0])
    stretch = 1 + float(np.linalg.norm(p.vel)) * em.dir_scale
    length = max(2.0, min(max(abs(sc[1]), abs(sc[0])) * cam.s * cam.ppx * 0.5 * stretch, max_len))
    w = 1.0 if abs(sc[0]) * cam.s * cam.ppx < 8 else 2.0
    pix.line(head - d * length, head, w, [ramp[max(0, idx - 1)], ramp[min(4, idx)], ramp[min(4, idx + 1)],
                                          ramp[min(4, idx + 2)]], dither)


def _trail(pix, cam, em, parts, ramp, cut, ppu):
    """a stepped polyline through the trail's points: wide and pale at the head, thin and deep at the tail."""
    parts = sorted(parts, key=lambda x: x[0].seq)
    if len(parts) < 2:
        return
    pts = np.array([cam.project(pos)[0] for _, _, pos in parts])
    for k in range(len(parts) - 1):
        p, age, _ = parts[k]
        t = min(1.0, age / max(p.life, 1e-6))
        a, _col = _strength(em, p, age, t)
        if a < cut:
            continue
        sc = p.scale * em.scale.at(t)
        w = step(max(1.0, abs(sc[0]) * ppu * 0.45))
        idx = int(np.clip(round(0.5 + 3.2 * t), 0, 4))
        pix.line(pts[k], pts[k + 1], w, [ramp[idx]], 0)          # a trail steps its colour, it never dithers


def _beam(pix, cam, pl, items, look, ppu):
    """the play's beam layers as one stepped beam: bands as wide as the layers, white core, flickering edges, flares."""
    layers = []
    src = tgt = None
    for em, parts, ramp, k_size in items:
        for p, age, pos in parts:
            t = min(1.0, age / max(p.life, 1e-6))
            a, col = _strength(em, p, age, t)
            if a < look.cut:
                continue
            sc = p.scale * em.scale.at(t)
            bd = em.prim_data.get("mBeam") or {}
            off = bd.get("mLocalSpaceSourceOffset")
            s_off = R._vec(off, 3) if off is not None else np.zeros(3)
            a_w = pos + pl.M @ s_off
            b_w = pl.target if pl.target is not None else pos
            layers.append((abs(sc[0]) * ppu * k_size, a, ramp))
            if src is None:
                src, tgt = cam.project(a_w)[0], cam.project(b_w)[0]
    if not layers or src is None:
        return
    layers.sort(key=lambda x: -x[0])
    d = tgt - src
    L = float(np.hypot(*d))
    if L < 1:
        return
    u = d / L
    nrm = np.array([-u[1], u[0]])
    gx = pix.xx + 0.5 - src[0]
    gy = pix.yy + 0.5 - src[1]
    along = gx * u[0] + gy * u[1]
    across = np.abs(gx * nrm[0] + gy * nrm[1])
    inside = (along >= 0) & (along <= L)
    rng = np.random.default_rng(int(L * 7 + len(layers) * 13 + layers[0][0] * 3))
    wobble = rng.integers(-1, 2, size=int(L) + 4)
    wob = wobble[np.clip(along.astype(int), 0, len(wobble) - 1)]
    widest = layers[0][0]
    strong = max(a for _, a, _ in layers)
    ramp = layers[0][2]
    # bands: the widest layer's half width split into 4 steps (outer rim deep, then saturated, pale, white core)
    hw = max(2.0, widest * 0.5 * (0.55 + 0.45 * strong))
    bands = [(hw, ramp[3]), (hw * 0.72, ramp[2]), (hw * 0.45, ramp[1]), (max(1.0, hw * 0.22), ramp[0])]
    for wdt, c in bands:
        m = inside & (across <= wdt + (wob if wdt > 2 else 0))
        pix.paint(m, c, 1 if strong < 0.3 else 0)
    if strong >= 0.45:
        pix.star(src[0], src[1], step(hw * 1.5), [ramp[0], ramp[2]])
        pix.star(tgt[0] - u[0] * 2, tgt[1] - u[1] * 2, step(hw * 0.9), [ramp[0], ramp[2]])


def _mesh(pix, cam, pl, em, p, age, t, pos, sc, ramp, idx, kind, look, dither, spec=None):
    verts = em.mesh[0]
    if em.ground:
        sc = np.full(3, sc[0])
    rot = p.rot + p.rotv * age + em.rot.at(t)
    Rm = pl.M @ R.rot_matrix(rot)
    wv = (verts * sc) @ Rm.T + pos
    pts, _ = cam.project(wv)
    if kind == "ring":
        c = cam.project(pos)[0]
        r_out = float(np.max(np.hypot(*(pts - c).T)))
        ext = pts.max(0) - pts.min(0)
        th = float((spec or {}).get("px", 3.0))                 # a drawn ring is a few squares thick, whatever the mesh
        rx = max(1.0, r_out - th / 2)
        ry = rx * (ext[1] / max(ext[0], 1e-6))
        pix.ring(c[0], c[1], rx, ry, th, [ramp[max(0, idx - 1)], ramp[min(4, idx)], ramp[min(4, idx + 1)]], dither)
    elif kind == "pillar":
        x0, x1 = pts[:, 0].min(), pts[:, 0].max()
        y0, y1 = pts[:, 1].min(), pts[:, 1].max()
        cxm = (x0 + x1) / 2
        hw = (x1 - x0) / 2
        for frac, c in ((1.0, ramp[min(4, idx + 1)]), (0.6, ramp[max(0, idx)]), (0.25, ramp[0])):
            m = (np.abs(pix.xx + 0.5 - cxm) <= hw * frac) & (pix.yy + 0.5 >= y0) & (pix.yy + 0.5 <= y1)
            pix.paint(m, c, 1)
    elif kind == "disc":
        c = cam.project(pos)[0]
        ext = pts.max(0) - pts.min(0)
        pix.dot(c[0], c[1], step(ext[0] / 2), [ramp[min(4, idx + 1)], ramp[idx], ramp[max(0, idx - 1)]], dither,
                squash=ext[1] / max(ext[0], 1e-6))
    else:                                                # a model: the textured mesh itself, alpha-cut, outlined
        cv = R.Canvas(pix.W, pix.H, None)
        R.draw_particle(cv, cam, pl, em, p, age, pos)
        out = cv.rgba()
        m = out[..., 3] > 0.5
        if m.any():
            pix.outline(m, look.smoke[5])
            c = (np.clip(out[..., :3], 0, 1) * 255 + 0.5).astype(np.uint8)
            pix.img[m, :3] = c[m]
            pix.img[m, 3] = 255


# ----------------------------------------------------------------------------- tags
def half_bright(img):
    """PPU 2 -> 1x: each 2x2 block keeps its brightest drawn pixel (a 1-square line survives)."""
    H, W = img.shape[:2]
    H2, W2 = H // 2, W // 2
    a = img[:H2 * 2, :W2 * 2]
    lum = np.where(a[..., 3] > 0, a[..., :3].astype(int).sum(-1) + 1, 0)
    blocks = lum.reshape(H2, 2, W2, 2).transpose(0, 2, 1, 3).reshape(H2, W2, 4)
    k = np.argmax(blocks, -1)
    yy, xx = np.mgrid[:H2, :W2]
    return a[yy * 2 + k // 2, xx * 2 + k % 2]


def render_tag(scene, intervals, vfxs=None, sample=0.45):
    """our tag's frames (our-time intervals) drawn from the scene's simulation: (hd frames, 1x frames, palette).
    Each frame shows the moment `sample` of the way through its interval (a pose, not a blur)."""
    if vfxs is None:
        vfxs = {}
    for ps in [scene] + scene["plays"]:
        c = ps.get("champ")
        if c and c not in vfxs:
            vfxs[c] = R.Vfx(c)
    plays = R.build_plays(vfxs, scene)
    sim = R.Sim(plays, dt=scene.get("dt", 1.0 / 120))
    look = Look(scene, plays)
    warp = R.warp_fn(scene)
    cam_d = scene["camera"]
    follow = scene.get("follow")
    W, H = int(cam_d["size"][0] * PPU), int(cam_d["size"][1] * PPU)
    hd = []
    for t0, t1 in intervals:
        t = warp(t0 + sample * (t1 - t0))
        sim.run_to(t)
        cam = R.Camera(cam_d["s"], cam_d.get("pitch", 35.0), cam_d.get("ground_px", 11.5), PPU, tuple(cam_d["size"]),
                       tuple(cam_d["center"]) if cam_d.get("center") else None)
        if follow is not None:
            pl = plays[follow]
            o = pl.pos_at((t - pl.t_start) * pl.speed)
            cam.center = (cam.center[0] - o[0] * cam.s, cam.center[1] - o[2] * cam.s * cam.sp)
        pix = Pix(W, H)
        draw_frame(sim, cam, look, pix)
        hd.append(pix.img)
    center = cam_d.get("center") or [cam_d["size"][0] // 2 + 0.5, cam_d["size"][1] // 2 + 0.5]
    anchor = scene.get("anchor") or center
    ones = [half_bright(f) for f in hd]
    hd_c, one_c = X._crop_all(hd, ones, tuple(anchor), PPU, (1, 1))
    cols = np.concatenate([f[..., :3][f[..., 3] > 0] for f in hd]) if any((f[..., 3] > 0).any() for f in hd) \
        else np.zeros((0, 3), np.uint8)
    pal = np.unique(cols, axis=0) if len(cols) else np.zeros((0, 3), np.uint8)
    return hd_c, one_c, pal
