#!/usr/bin/env python3
"""Shared rig for the 2026-10-16 PPU redo of eleven heroes from Codex's pictures (the user: 「帮我利用PPU重做一下娜美
莫甘娜 锐雯的模型吧 动作帧就不让codex做了 参照塔姆那样慢慢做就行了 特效还是老样子」, then Darius, Leona, LeBlanc, Xin Zhao,
Janna, Kayle, Jax and Fiora: 「一共11个英雄」).

league_tahmkench's way (tools/art/rig_tahmkench.py), made common:

* the picture (assets/source/<hero>/hd/picture.png, Codex's full-body pixel picture) is brought once to the hero's PPU
  at its current height (head top to soles = the 1x idle's) - the design (`Design`); a coarse picture (squares of 6 px
  or more) by pixel_down.pixelate on its own colours, a fine one (squares of 4-5 px: an illustration more than pixel
  art) by an alpha-weighted Lanczos and pixel_down.crisp (league_zeri's flat look);
* parts are cut from the design by polygons in design squares (`Design.part`), every square in at most one part;
* a frame is the parts put down in order, each only moved losslessly - whole squares, mirrored, quarter turns
  (memory no-deformation-lossless-poses) - except props and limbs held at another angle (a sword swung, an arm raised):
  those are drawn again from the picture itself turned at that angle and brought to the same grid (`Design.turned`),
  never turned on the coarse grid; the body and the head never turn;
* where a moved part uncovers the body, the body is filled from the squares round it (`fill_under`);
* the frames go out the way rig_tahmkench.export does: the dense frame PPU x its 1x frame about the pivot to
  assets/source/ppu/orig/<hero>_<tag>.png (+ .json sizes), the 1x frame (the commonest colour of each PPU x PPU block)
  to the hero's sheet; then tools/art/ppu_restyle.py (RESTYLE: edge 1, face point) and tools/art/ppu_hd.py.

The soles' bottom edge is 11.5 1x pixels under a frame's centre (every hero's sheet), so a dense frame's pivot is its
centre and the ground FEET x PPU under it.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import pixel_down as PD  # noqa: E402

MOD = os.path.join(ROOT, "league")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
FEET = 11.5                                  # 1x pixels from a frame's centre down to the soles' bottom edge
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


# ------------------------------------------------------------------------------------------------- the picture
def load_picture(hero, name="picture"):
    a = np.asarray(Image.open(lp(os.path.join(ROOT, "assets", "source", hero, "hd", f"{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def lanczos_down(pic, k, size=None):
    """Alpha-weighted Lanczos to k times the size (or `size` = (W, H)), alpha cut at one half."""
    H, W = pic.shape[:2]
    a = pic.astype(np.float32)
    al = a[..., 3:4] / 255
    pm = np.concatenate([a[..., :3] * al, al * 255], -1)
    size = size or (max(1, round(W * k)), max(1, round(H * k)))
    r = np.stack([np.asarray(Image.fromarray(pm[..., c]).resize(size, Image.LANCZOS)) for c in range(4)], -1)
    alpha = r[..., 3] / 255
    rgb = r[..., :3] / np.maximum(alpha[..., None], 1e-3)
    out = np.zeros(r.shape, np.uint8)
    m = alpha >= 0.5
    out[m, :3] = np.clip(rgb[m], 0, 255)
    out[m, 3] = 255
    return out


def kmeans_palette(px, n, seed=0):
    """n colours for the rgb rows `px` (k-means in Lab on a sample, each colour its members' mean)."""
    rng = np.random.default_rng(seed)
    s = px[rng.choice(len(px), min(len(px), 30000), replace=False)].astype(float)
    L = PD._lab(s)
    c = L[rng.choice(len(L), n, replace=False)]
    for _ in range(20):
        idx = ((L[:, None] - c[None]) ** 2).sum(-1).argmin(1)
        for j in range(n):
            if (idx == j).any():
                c[j] = L[idx == j].mean(0)
    idx = ((L[:, None] - c[None]) ** 2).sum(-1).argmin(1)
    return np.array([s[idx == j].mean(0) if (idx == j).any() else s[0] for j in range(n)])


def snap(a, pal):
    """Opaque squares snapped to the nearest palette colour (Lab)."""
    out = a.copy()
    m = a[..., 3] > 0
    if m.any():
        L = PD._lab(a[m][:, :3].astype(float))
        P = PD._lab(pal.astype(float))
        out[m, :3] = np.clip(pal[((L[:, None] - P[None]) ** 2).sum(-1).argmin(1)].round(), 0, 255).astype(np.uint8)
    return out


def inpaint(a, hole, iters=400):
    """hole pixels take the mean of their filled neighbours, ring by ring inward (alpha 255)."""
    out = a.astype(np.float32).copy()
    known = (a[..., 3] > 0) & ~hole
    todo = hole.copy()
    k = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], np.float32)
    for _ in range(iters):
        if not todo.any():
            break
        w = ndimage.convolve(known.astype(np.float32), k, mode="constant")
        ring = todo & (w > 0)
        if not ring.any():
            break
        for c in range(3):
            sm = ndimage.convolve(np.where(known, out[..., c], 0), k, mode="constant")
            out[..., c][ring] = sm[ring] / w[ring]
        out[..., 3][ring] = 255
        known |= ring
        todo &= ~ring
    return out.round().astype(np.uint8)


# ------------------------------------------------------------------------------------------------- the design
class Design:
    """The picture at `ppu` squares a game pixel, `rows_1x` game rows from `pic_top` (the head's top in picture pixels
    from the figure's top: wings, a raised lamp or spear tip above it are left out of the measure) to the soles.
    picture: the file's name in assets/source/<hero>/hd/ (a second form: league_swain's picture_b, the demon).
    coarse: pixelate on the picture's own colours; else Lanczos + crisp. foot_x: the picture column the hero stands on
    (default the soles' middle)."""

    def __init__(self, hero, ppu, rows_1x, pic_top=0, coarse=False, colours=24, foot_x=None, outline=None,
                 regrid=None, picture="picture"):
        self.hero, self.ppu, self.coarse, self.colours = hero, ppu, coarse, colours
        pic = load_picture(hero, picture)
        self.pic = pic
        self.k = rows_1x * ppu / (pic.shape[0] - pic_top)
        self.outline = tuple(outline) if outline else PD.edge_colour(pic)
        if foot_x is None:
            ys, xs = np.nonzero(pic[-max(4, pic.shape[0] // 40):, :, 3])
            foot_x = (xs.min() + xs.max() + 1) / 2
        self.foot_x = foot_x
        H0, W0 = pic.shape[:2]
        if regrid:
            # the picture's own squares (scripts/regrid.py), one design square each - when they come out at the PPU
            import regrid as RG
            d, _, (bx, by) = RG.regrid(pic, regrid)
            self.pal = kmeans_palette(pic[pic[..., 3] > 0][:, :3], 48)
            self.d = d
            self.coarse = True
            self.k = (len(by) - 1) / (by[-1] - by[0])
            self.gx0, self.gy0 = float(bx[0]), float(by[0])
            ys, xs = np.nonzero(d[..., 3])
            self.px = int(round((foot_x - self.gx0) * self.k))
        elif coarse:
            self.pal = kmeans_palette(pic[pic[..., 3] > 0][:, :3], 48)
            d, (nx0, ny0) = PD.pixelate(pic, self.k, (foot_x, H0), self.outline, self.pal)
            self.d = d
            # pixelate's grid runs through (foot_x, bottom): design square (c, r) covers picture x from
            # gx0 + c / k, y from gy0 + r / k
            self.gx0, self.gy0 = foot_x - nx0 / self.k, H0 - ny0 / self.k
            self.px = nx0
        else:
            Wd, Hd = max(1, round(W0 * self.k)), max(1, round(H0 * self.k))
            self.gx0, self.gy0 = 0.0, 0.0
            self._fit = self.grid_lanczos(pic, Wd, Hd)
            self.d = PD.crisp([self._fit], n=colours, keep="face", contrast=1.1)[0]
            self.px = int(round(foot_x * self.k))
            self.pal = None
        self.d0 = self.d.copy()                              # the whole design (props in)
        ys, xs = np.nonzero(self.d[..., 3])
        self.ground = ys.max() + 1                           # the first row under the soles
        self.H, self.W = self.d.shape[:2]
        self.parts = {}
        self.order = []
        self.polys = {}
        self.props = set()
        self.prop_masks = {}
        self.keep_out = None
        self.shafts = {}
        self._turned = {}

    # -------------------------------------------------------------------------------------------- parts
    def poly(self, pts):
        """Squares whose centre is inside the polygon pts [(x, y), ...] (design squares)."""
        img = Image.new("L", (self.W, self.H), 0)
        ImageDraw.Draw(img).polygon([(x - 0.5, y - 0.5) for x, y in pts], fill=1, outline=1)
        return np.asarray(img, bool) & (self.d[..., 3] > 0)

    def part(self, name, mask, take=True, poly=None):
        """Register `mask` as part `name`; with take, its squares leave every part registered before. poly: the
        polygon it was cut by (design squares), for turned(); a list of points as `mask` is that polygon."""
        if isinstance(mask, (list, tuple)):
            poly, mask = mask, self.poly(mask)
        mask = mask & (self.d[..., 3] > 0)
        if poly is not None:
            self.polys[name] = poly
        if take:
            for k in self.parts:
                self.parts[k] = self.parts[k] & ~mask
        self.parts[name] = mask
        if name not in self.order:
            self.order.append(name)
        return mask

    def rest(self):
        """Squares in no part."""
        m = self.d[..., 3] > 0
        for v in self.parts.values():
            m = m & ~v
        return m

    def layer(self, name):
        m = self.parts[name] if name != "rest" else self.rest()
        out = np.zeros_like(self.d)
        out[m] = self.d[m]
        return out

    # -------------------------------------------------------------------------------------------- turned props
    def cut_props(self, props, close=4, fills=(), keep_out=None, bare=()):
        """props {name: polygon (design squares)}: cut out of the picture, the body they hid filled from round it
        (inpaint, inside the body's outline closed over their width), and the design made again from what is left -
        so a prop swung away shows the body behind it. Each prop is drawn from the picture itself by turn(), at any
        angle (0 too). fills: polygons (design squares) of body the props hid where the body's outline does not close
        round it (a leg's edge behind a blade) - filled from round them too. keep_out: rgb -> mask of picture pixels
        never part of a prop (a cape behind an arm). A prop may also be given as a picture-sized mask (leg_masks); the
        props named in `bare` (legs) leave their place empty, never filled."""
        self.keep_out = keep_out
        H, W = self.pic.shape[:2]
        cut = np.zeros((H, W), bool)
        fill = np.zeros((H, W), bool)
        for poly in fills:
            img = Image.new("L", (W, H), 0)
            ImageDraw.Draw(img).polygon([self.d2p(x, y) for x, y in poly], fill=1)
            fill |= np.asarray(img, bool)
        bare_cut = np.zeros((H, W), bool)
        for name, poly in props.items():
            if isinstance(poly, np.ndarray):
                m = poly.copy()
                poly = None
            else:
                img = Image.new("L", (W, H), 0)
                ImageDraw.Draw(img).polygon([self.d2p(x, y) for x, y in poly], fill=1)
                m = np.asarray(img, bool)
            if keep_out is not None:
                m &= ~keep_out(self.pic[..., :3].astype(int))
            m &= ~cut                                     # a square belongs to the first prop that takes it
            cut |= m
            if name in bare:
                bare_cut |= m
            self.polys[name] = poly
            self.prop_masks[name] = m
            self.props.add(name)
        body = self.pic.copy()
        body[cut] = 0
        bop = body[..., 3] > 0
        # close > 0: the body's outline closed over the props' width (an arm across the body); 0: only gaps the body
        # itself encloses (a staff held beside her - closed over, its squares came back as a strip of body)
        closed = ndimage.binary_closing(bop, structure=np.ones((9, 9)), iterations=close) if close > 0 else bop
        hole = cut & (closed | ndimage.binary_fill_holes(bop) | fill) & ~bop & (self.pic[..., 3] > 0) & ~bare_cut
        self.pic_body = inpaint(body, hole)
        if self.coarse:
            d, (nx0, ny0) = PD.pixelate(self.pic_body, self.k, (self.gx0, self.gy0), self.outline, self.pal)
            out = np.zeros_like(self.d)
            sub = d[ny0:ny0 + self.H, nx0:nx0 + self.W]
            out[:sub.shape[0], :sub.shape[1]] = sub
        else:
            raw = self.grid_lanczos(self.pic_body, self.W, self.H)
            out = PD.crisp([raw], n=self.colours, keep="face", contrast=1.1, fit=[self._fit])[0]
        # what the cut left loose (a prop's outline squares outside its polygon): pieces under 3 % of the body go
        op = out[..., 3] > 0
        lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
        if n > 1:
            sz = ndimage.sum(op, lbl, range(1, n + 1))
            for j in range(1, n + 1):
                if sz[j - 1] < 0.03 * sz.max():
                    out[lbl == j] = 0
        self.d = out
        for k in self.parts:
            self.parts[k] &= self.d[..., 3] > 0

    def shaft(self, name, p0, p1, width=1.6, colour=None, keep=(), rim=None):
        """A thin straight shaft in prop `name` from p0 to p1 (design squares): drawn as a clean line of `width` squares
        in its own colour at every angle instead of brought down from the picture, where a one- or two-square post
        breaks up when turned (league_jax's lamp post; the user: 「枪别做歪了」). colour: the commonest colour of the
        design's squares along it, when not given. keep: polygons (design squares) the line runs under and that stay as
        drawn (the fist round the post). rim: squares of outline drawn round the line (a post the picture draws dark-edged:
        a one-square line alone broke into dashes at a shallow slope, league_jax)."""
        if colour is None:
            n = int(np.hypot(p1[0] - p0[0], p1[1] - p0[1]) * 2) + 2
            cols = []
            for t in np.linspace(0.45, 0.9, n):          # away from p0 (a grip: the hand's colours)
                x, y = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
                for dx in (-0.5, 0, 0.5):
                    xi, yi = int(np.floor(x + dx)), int(np.floor(y))
                    if 0 <= yi < self.H and 0 <= xi < self.W and self.d0[yi, xi, 3]:
                        cols.append(tuple(int(v) for v in self.d0[yi, xi, :3]))
            lit = [c for c in cols if sum(c) >= 70] or cols
            colour = max(set(lit), key=lit.count)
        self.shafts[name] = (tuple(p0), tuple(p1), width, tuple(colour), tuple(tuple(k) for k in keep), rim)

    def turn(self, name, angle, about, src=None):
        """turned() for a registered part, cached; angle 0 = the part itself (a prop is always drawn from the
        picture). src: another picture to draw it from (a recoloured blade), with its own cache."""
        if not angle and name not in self.props:
            return self.layer(name)
        key = (name, angle, about, id(src))
        if key not in self._turned:
            self._turned[key] = self.turned(self.polys[name], angle, about, src, shaft=self.shafts.get(name),
                                            mask=self.prop_masks.get(name))
        return self._turned[key]

    def d2p(self, x, y):
        """Design coordinates (square edges) -> picture pixels."""
        return self.gx0 + x / self.k, self.gy0 + y / self.k

    def grid_lanczos(self, pic, Wd, Hd, gx0=None, gy0=None):
        """pic sampled by an alpha-weighted Lanczos on the design's grid: Wd x Hd squares from (gx0, gy0)."""
        gx0 = self.gx0 if gx0 is None else gx0
        gy0 = self.gy0 if gy0 is None else gy0
        a = pic.astype(np.float32)
        al = a[..., 3:4] / 255
        pm = np.concatenate([a[..., :3] * al, al * 255], -1)
        box = (gx0, gy0, gx0 + Wd / self.k, gy0 + Hd / self.k)
        # PIL wants the box inside the picture: pad it (clear) far enough
        need_x, need_y = int(np.ceil(max(box[2] - pm.shape[1], 0))) + 2, int(np.ceil(max(box[3] - pm.shape[0], 0))) + 2
        pm = np.pad(pm, ((0, need_y), (0, need_x), (0, 0)))
        r = np.stack([np.asarray(Image.fromarray(pm[..., c]).resize((Wd, Hd), Image.LANCZOS, box=box))
                      for c in range(4)], -1)
        alpha = r[..., 3] / 255
        rgb = r[..., :3] / np.maximum(alpha[..., None], 1e-3)
        out = np.zeros(r.shape, np.uint8)
        m = alpha >= 0.5
        out[m, :3] = np.clip(rgb[m], 0, 255)
        out[m, 3] = 255
        return out

    TURN_PAD = 40                                   # design squares round the design a turned part may reach

    def turned(self, poly_pts, angle, about, src=None, shaft=None, mask=None):
        """The picture's pixels inside poly_pts (design squares) turned `angle` degrees counter-clockwise about
        `about` (design squares) and brought to the design's own grid, method and colours. -> RGBA covering the
        design plus TURN_PAD squares on every side (its (0, 0) is design (-TURN_PAD, -TURN_PAD))."""
        k, P = self.k, self.TURN_PAD
        H, W = self.pic.shape[:2]
        M = int(np.ceil(P / k)) + 2                     # picture pixels of padding
        big = np.zeros((H + 2 * M, W + 2 * M, 4), np.uint8)
        big[M:M + H, M:M + W] = self.pic if src is None else src
        img = Image.new("L", (W + 2 * M, H + 2 * M), 0)
        if mask is not None:                            # the prop's own picture pixels (cut_props)
            mm = np.zeros((H + 2 * M, W + 2 * M), np.uint8)
            mm[M:M + H, M:M + W] = mask * 255
            img = Image.fromarray(mm)
        else:
            ImageDraw.Draw(img).polygon([tuple(v + M for v in self.d2p(x, y)) for x, y in poly_pts], fill=255)
        if shaft is not None:                           # the shaft's middle is drawn as a line afterwards
            (x0, y0), (x1, y1), w, _, keep, rim = shaft
            L = max(1e-6, np.hypot(x1 - x0, y1 - y0))
            e = w / 2 + 0.7 + (rim or 0)
            nx, ny = -(y1 - y0) / L * e, (x1 - x0) / L * e
            band = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
            ImageDraw.Draw(img).polygon([tuple(v + M for v in self.d2p(x, y)) for x, y in band], fill=0)
            for kp in keep:
                ImageDraw.Draw(img).polygon([tuple(v + M for v in self.d2p(x, y)) for x, y in kp], fill=255)
        big[np.asarray(img) == 0] = 0
        if getattr(self, "keep_out", None) is not None:
            big[self.keep_out(big[..., :3].astype(int)) & (big[..., 3] > 0)] = 0
        cx, cy = (v + M for v in self.d2p(*about))
        rot = np.asarray(Image.fromarray(big).rotate(angle, resample=Image.BICUBIC, center=(cx, cy))).copy()
        rot[..., 3] = np.where(rot[..., 3] >= 128, 255, 0)
        rot[rot[..., 3] == 0] = 0
        Wd, Hd = self.W + 2 * P, self.H + 2 * P
        gx0, gy0 = self.gx0 + M - P / k, self.gy0 + M - P / k   # the padded grid's corner in `rot`
        if self.coarse:
            d, (nx0, ny0) = PD.pixelate(rot, k, (gx0, gy0), self.outline, self.pal)
            out = np.zeros((Hd, Wd, 4), np.uint8)
            sub = d[ny0:ny0 + Hd, nx0:nx0 + Wd]
            out[:sub.shape[0], :sub.shape[1]] = sub
        else:
            raw = self.grid_lanczos(rot, Wd, Hd, gx0, gy0)
            fit = [self._fit]
            if src is not None:                         # another picture (a recoloured blade): its colours count too
                fit.append(self.grid_lanczos(src, self.W, self.H))
            out = PD.crisp([raw], n=self.colours + (8 if src is not None else 0), keep="face", contrast=1.1,
                           fit=fit)[0]
        if shaft is not None:
            (x0, y0), (x1, y1), w, colour, _, rim = shaft
            th = np.radians(angle)
            ax_, ay_ = about

            def rot(x, y):
                return (ax_ + (x - ax_) * np.cos(th) + (y - ay_) * np.sin(th) + P,
                        ay_ - (x - ax_) * np.sin(th) + (y - ay_) * np.cos(th) + P)
            (X0, Y0), (X1, Y1) = rot(x0, y0), rot(x1, y1)
            yy, xx = np.mgrid[0:out.shape[0], 0:out.shape[1]]
            cx, cy = xx + 0.5, yy + 0.5
            dx_, dy_ = X1 - X0, Y1 - Y0
            L2 = max(1e-9, dx_ * dx_ + dy_ * dy_)
            t = np.clip(((cx - X0) * dx_ + (cy - Y0) * dy_) / L2, 0, 1)
            dist = np.hypot(cx - (X0 + t * dx_), cy - (Y0 + t * dy_))
            line = (dist <= w / 2) & (out[..., 3] == 0)
            out[line, :3] = colour
            out[line, 3] = 255
            if rim:
                edge = (dist <= w / 2 + rim) & (out[..., 3] == 0)
                out[edge, :3] = self.outline
                out[edge, 3] = 255
        # crumbs the turn left apart from the part (a thin curl or a cloth edge the polygon took: under 8 % of the
        # part's biggest piece) - nothing may float beside a swung prop
        op = out[..., 3] > 0
        lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
        if n > 1:
            sz = ndimage.sum(op, lbl, range(1, n + 1))
            for j in range(1, n + 1):
                if sz[j - 1] < max(4, 0.08 * sz.max()):
                    out[lbl == j] = 0
        return out

    # -------------------------------------------------------------------------------------------- review
    def ruler(self, path, z=8, show_parts=True):
        """The design at z x with a square grid every 5 and labels every 10, each part tinted."""
        H, W = self.H, self.W
        base = self.d.copy()
        img = Image.new("RGBA", ((W + 6) * z, (H + 6) * z), (96, 112, 96, 255))
        big = Image.fromarray(base).resize((W * z, H * z), Image.NEAREST)
        img.alpha_composite(big, (3 * z, 3 * z))
        dr = ImageDraw.Draw(img)
        if show_parts:
            tints = [(255, 0, 0), (0, 160, 255), (255, 200, 0), (0, 255, 120), (255, 0, 255), (0, 255, 255),
                     (255, 120, 0), (160, 80, 255), (120, 255, 0), (255, 255, 255)]
            ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            for i, name in enumerate(self.order):
                ys, xs = np.nonzero(self.parts[name])
                c = tints[i % len(tints)]
                for y, x in zip(ys, xs):
                    od.rectangle([(x + 3) * z, (y + 3) * z, (x + 4) * z - 1, (y + 4) * z - 1], fill=(*c, 90))
                if len(ys):
                    od.text(((xs.mean() + 3) * z, (ys.mean() + 3) * z), name, fill=(*c, 255))
            img.alpha_composite(ov)
        for x in range(0, W + 1, 5):
            dr.line([((x + 3) * z, 3 * z), ((x + 3) * z, (H + 3) * z)], fill=(255, 255, 255, 60 if x % 10 else 120))
            if x % 10 == 0:
                dr.text(((x + 3) * z + 2, 2), str(x), fill=(255, 255, 0))
        for y in range(0, H + 1, 5):
            dr.line([(3 * z, (y + 3) * z), ((W + 3) * z, (y + 3) * z)], fill=(255, 255, 255, 60 if y % 10 else 120))
            if y % 10 == 0:
                dr.text((2, (y + 3) * z + 2), str(y), fill=(255, 255, 0))
        dr.line([((self.px + 3) * z, 3 * z), ((self.px + 3) * z, (H + 3) * z)], fill=(255, 0, 0, 160))
        img.convert("RGB").save(lp(path))


# ------------------------------------------------------------------------------------------------- composing
def put(dst, src, mask=None, dx=0, dy=0, under=False, flip=False, rot=0, about=None):
    """src's squares (where mask, else where opaque) onto dst moved (dx, dy); flip mirrors them left-right about
    about[0] (else their own middle), rot = quarter turns counter-clockwise about `about` (design squares)."""
    m = (src[..., 3] > 0) if mask is None else (mask & (src[..., 3] > 0))
    ys, xs = np.nonzero(m)
    if not len(ys):
        return dst
    cols = src[ys, xs]
    fx, fy = xs.astype(float) + 0.5, ys.astype(float) + 0.5
    if about is None:
        about = ((xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2)
    ax, ay = about
    if flip:
        fx = 2 * ax - fx
    for _ in range(rot % 4):                  # counter-clockwise on screen (y down): (x, y) -> (y, -x) about the point
        fx, fy = ax + (fy - ay), ay - (fx - ax)
    tx = np.floor(fx + dx).astype(int)
    ty = np.floor(fy + dy).astype(int)
    ok = (ty >= 0) & (ty < dst.shape[0]) & (tx >= 0) & (tx < dst.shape[1])
    tx, ty, cols = tx[ok], ty[ok], cols[ok]
    if under:
        free = dst[ty, tx, 3] == 0
        tx, ty, cols = tx[free], ty[free], cols[free]
    dst[ty, tx] = cols
    return dst


def fill_under(frame, hole, src_mask=None, iters=12):
    """Squares of `hole` (clear in frame) inside the figure take the colour of their nearest opaque neighbour that is
    not outline, grown inward ring by ring (the body behind a part that moved away)."""
    out = frame.copy()
    todo = hole & (out[..., 3] == 0)
    dark = out[..., :3].astype(int).sum(-1) < 70
    for _ in range(iters):
        if not todo.any():
            break
        op = (out[..., 3] > 0) & ~dark
        grow = ndimage.binary_dilation(op, structure=CROSS) & todo
        if not grow.any():
            break
        ys, xs = np.nonzero(grow)
        for y, x in zip(ys, xs):
            for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < out.shape[0] and 0 <= xx < out.shape[1] and op[yy, xx]:
                    out[y, x] = out[yy, xx]
                    break
        todo &= ~grow
        dark = out[..., :3].astype(int).sum(-1) < 70
    return out


def tidy(a, outline, most_hole=6, speck=5):
    """The outline closed round moved edges, enclosed pinholes (up to most_hole squares) filled with their commonest
    neighbour, loose specks under `speck` squares off (rig_tahmkench.tidy)."""
    out = G.complete_outline(a, color=outline)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > most_hole:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[m, :3] = cols[cnt.argmax()]
        out[m, 3] = 255
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] < speck:
                out[lbl == k] = 0
    return out


# ------------------------------------------------------------------------------------------------- the game's frames
def sheet_of(hero):
    stem = os.path.join(MOD, "champions", f"league_{hero}")
    with open(lp(stem + "#anim.fanim"), encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    px = np.asarray(Image.open(lp(stem + "#sheet.png")).convert("RGBA"))
    out = {}
    for tag, a in anims.items():
        if tag.startswith(("hd_", "lo_")):              # (ppu_hd's copies: the 1x tags are the timing)
            continue
        fr = []
        for f_ in a["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000, 3)))
        out[tag] = fr
    return out


def one_of(can, px, py, hw, hh, ppu, need=0.5):
    """The 1x frame (2hw+1 x 2hh+1) about the pivot (px, py): each 1x square the commonest colour of the dense
    squares under it where `need` of them are drawn."""
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * ppu, py + (j - hh + 0.5) * ppu
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * ppu, px + (i - hw + 0.5) * ppu
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() < need * len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    return one


def crop_dense(can, px, py, W, H):
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, hx0), max(0, hy0)
    sub = can[sy0:min(can.shape[0], hy0 + H), sx0:min(can.shape[1], hx0 + W)]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return hd


class Rig:
    """A hero's frames on a canvas: the design placed so its pivot square (design.px, design.ground) lands on the
    canvas point (CX, CY); every frame a canvas of the same size."""

    def __init__(self, design, pad=(60, 60, 80, 30)):
        self.D = design
        left, right, top, bottom = pad
        self.CW = design.W + left + right
        self.CH = design.H + top + bottom
        self.ox, self.oy = left, top                       # where the design's (0, 0) goes standing
        self.CX = self.ox + design.px                      # canvas column of the pivot (the line the hero stands on)
        self.GY = self.oy + design.ground                  # canvas row under the soles

    def canvas(self):
        return np.zeros((self.CH, self.CW, 4), np.uint8)

    fill_rows = None                                    # (row0, row1) design rows where cracks a step opens are closed
    CRACK = 40
    CRACK_W = None                                      # squares from a crack's middle to its edge at most (None: any)

    def finish(self, can):
        """tidy() and, for a hero that walks (fill_rows), the cracks a step opens between the legs and the skirt closed
        with the outline (league_braum's walk_frame, gap-check): enclosed gaps of at most CRACK squares lying within
        fill_rows that the standing frame does not have (and, with CRACK_W, no wider than that from their middle to an edge:
        a thin crack, not the room a swung arm leaves between itself and the body - league_darius)."""
        out = tidy(can, self.D.outline)
        if not self.fill_rows:
            return out
        if getattr(self, "_ref", None) is None:
            self._ref = None
            ref = tidy(self.idle_canvas, self.D.outline) if hasattr(self, "idle_canvas") else None
            if ref is not None:
                rop = ref[..., 3] > 0
                self._ref = ndimage.binary_dilation(ndimage.binary_fill_holes(rop) & ~rop, iterations=2)
        op = out[..., 3] > 0
        lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
        r0, r1 = self.oy + self.fill_rows[0], self.oy + self.fill_rows[1]
        for j in range(1, n + 1):
            h = lbl == j
            ys = np.nonzero(h.any(1))[0]
            if h.sum() > self.CRACK or ys.min() < r0 or ys.max() > r1:
                continue
            if self._ref is not None and (h & self._ref).any():
                continue
            if self.CRACK_W is not None and ndimage.distance_transform_edt(h).max() > self.CRACK_W:
                continue
            out[h] = (*self.D.outline, 255)
        return out

    def at(self, x, y):
        """Design square -> canvas square (standing)."""
        return self.ox + x, self.oy + y

    def export(self, frames, review_dir=None, hero=None):
        """frames: {tag: [(canvas or {"body", "over", "under"}, ms)]} in the sheet's tag order -> orig strips + json
        (+ .over / .under strips for the effects a bake laid on: ppu_restyle RESTYLE fx puts them on after the
        outline), the 1x sheet (body and effects together)."""
        D = self.D
        hero = hero or D.hero
        ppu = D.ppu
        os.makedirs(lp(ORIG), exist_ok=True)
        sheet = {}
        for tag, fr in frames.items():
            ones, hds, overs, unders = [], [], [], []
            for can, ms in fr:
                lay = can if isinstance(can, dict) else {"body": can}
                body = self.finish(lay["body"])
                over, under = lay.get("over"), lay.get("under")
                full = body.copy()
                for fx_, top in ((under, False), (over, True)):
                    if fx_ is not None:
                        m = fx_[..., 3] > 0
                        if not top:
                            m &= full[..., 3] == 0
                        full[m] = fx_[m]
                px = float(self.CX)
                py = self.GY - FEET * ppu
                ys, xs = np.nonzero(full[..., 3] > 0)
                hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / ppu - 0.5))
                hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / ppu - 0.5))
                hh = max(hh, int(np.ceil(FEET)) + 1)
                one = G.complete_outline(one_of(body, px, py, hw, hh, ppu), color=D.outline)[0]
                for fx_, top in ((under, False), (over, True)):
                    if fx_ is not None and fx_[..., 3].any():
                        f1 = one_of(fx_, px, py, hw, hh, ppu)
                        m = f1[..., 3] > 0
                        if not top:
                            m &= one[..., 3] == 0
                        one[m] = f1[m]
                W, H = round((2 * hw + 1) * ppu), round((2 * hh + 1) * ppu)
                ones.append((one, float(ms)))
                hds.append(crop_dense(body, px, py, W, H))
                overs.append(None if over is None else crop_dense(over, px, py, W, H))
                unders.append(None if under is None else crop_dense(under, px, py, W, H))
            sheet[tag] = ones
            for suf, lst in (("", hds), (".over", overs), (".under", unders)):
                path = lp(os.path.join(ORIG, f"{hero}_{tag}{suf}.png"))
                if suf and all(v is None for v in lst):
                    if os.path.isfile(path):
                        os.remove(path)
                    continue
                lst = [np.zeros_like(h) if v is None else v for v, h in zip(lst, hds)]
                Hm = max(h.shape[0] for h in lst)
                strip = np.zeros((Hm, sum(h.shape[1] + 1 for h in lst) - 1, 4), np.uint8)
                x = 0
                for h in lst:
                    strip[:h.shape[0], x:x + h.shape[1]] = h
                    x += h.shape[1] + 1
                Image.fromarray(strip).save(path)
            with open(lp(os.path.join(ORIG, f"{hero}_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
                json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": ppu}, f)
        w, h = G.write_sheet(os.path.join(MOD, "champions", f"league_{hero}"), sheet)
        print(f"league/champions/league_{hero}#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))

    def bake(self, frames, hero=None):
        """assets/source/native/<hero>_bake.json applied to the rig's frames the way tools/art/import_native.bake
        applies it to a 1x sheet (the effects drawn into the old frames keep their timing: 「特效还是老样子」): each
        effect frame brought to PPU (nearest) and laid centred on the pivot into an "over" or "under" layer; an item's
        "side" ("left" / "right") keeps only that half of the picture (two things in one picture moved apart).
        frames {tag: [(canvas, ms)]} -> {tag: [({"body", "over", "under"}, ms)]}, the `from` copies made too."""
        import tfm2_ase
        hero = hero or self.D.hero
        with open(lp(os.path.join(ROOT, "assets", "source", "native", f"{hero}_bake.json")), encoding="utf-8") as f:
            cfg = json.load(f)
        ppu = self.D.ppu
        out = {t: [({"body": c, "over": None, "under": None}, ms) for c, ms in fr] for t, fr in frames.items()}
        src = {e["into"]: e["from"] for e in cfg["items"] if "from" in e}

        def depth(tag):
            return 0 if tag not in src else depth(src[tag]) + 1

        def sl(fr, start, length=None):
            total = sum(ms for _, ms in fr)
            length = total - start if length is None else length
            res, t, end = [], 0, start + length
            while t < end:
                for a, ms in fr:
                    lo, hi = max(t, start), min(t + ms, end)
                    if hi > lo:
                        res.append((dict(a), hi - lo))
                    t += ms
            return res

        def at(seq, tt, base=0):
            for k_, (_, ms) in enumerate(seq):
                if base <= tt < base + ms:
                    return k_
                base += ms
            return None
        sheets = {}
        px, py = self.CX, self.GY - FEET * ppu
        for e in sorted(cfg["items"], key=lambda e: depth(e["into"])):
            name = e.get("fx", cfg["fx"])
            if name not in sheets:
                sheets[name] = tfm2_ase.load_sprite(os.path.join(MOD, "effects", name + "#sheet.png"))
            fx = sheets[name]
            if "from" in e:
                if e["into"] not in out:
                    out[e["into"]] = sl(out[e["from"]], int(round(e["slice_ms"])), e.get("length_ms"))
            elif e.get("length_ms") and sum(ms for _, ms in out[e["into"]]) < e["length_ms"]:
                out[e["into"]] = sl(out[e["into"]], 0, e["length_ms"])
            pic = []
            for i in fx.tag_frames(e["tag"]):
                a = np.asarray(fx.frames[i])
                h, w = a.shape[:2]
                yy = np.minimum(((np.arange(round(h * ppu)) + 0.5) / ppu).astype(int), h - 1)
                xx = np.minimum(((np.arange(round(w * ppu)) + 0.5) / ppu).astype(int), w - 1)
                b = a[yy][:, xx].copy()
                if e.get("side") in ("left", "right"):
                    # one half of a picture that shows two things (league_kaisa's Q flash over each pod), moved apart
                    half = b.shape[1] // 2
                    if e["side"] == "left":
                        b[:, half:] = 0
                    else:
                        b[:, :half] = 0
                # sparks under 4 squares dropped (ppu_hd's check: no specks on a frame; ppu_restyle's scale_fx mote)
                lbl, n = ndimage.label(b[..., 3] > 0, structure=np.ones((3, 3)))
                if n:
                    sz = ndimage.sum(b[..., 3] > 0, lbl, range(1, n + 1))
                    for j in range(1, n + 1):
                        if sz[j - 1] < 4:
                            b[lbl == j] = 0
                pic.append((b, fx.durations[i]))
            dx, dy = e.get("dx", 0) * ppu, e.get("dy", 0) * ppu
            fr = out[e["into"]]
            total = sum(ms for _, ms in fr)
            t0 = int(round(e["at_ms"]))
            cuts, t = {0, total}, 0
            for _, ms in fr:
                t += ms
                cuts.add(t)
            t = t0
            for _, ms in pic:
                cuts.add(t)
                t += ms
            cuts.add(t)
            cuts = sorted(c for c in cuts if 0 <= c <= total)
            res = []
            key = "under" if e.get("under") else "over"
            for a_, b_ in zip(cuts, cuts[1:]):
                lay = dict(fr[at(fr, a_)][0])
                j = at(pic, a_, t0)
                if j is not None:
                    p_ = pic[j][0]
                    layer = np.zeros((self.CH, self.CW, 4), np.uint8) if lay[key] is None else lay[key].copy()
                    y0 = int(round(py + dy - p_.shape[0] / 2))
                    x0 = int(round(px + dx - p_.shape[1] / 2))
                    ys, xs = np.nonzero(p_[..., 3] > 0)
                    ok = (ys + y0 >= 0) & (ys + y0 < self.CH) & (xs + x0 >= 0) & (xs + x0 < self.CW)
                    layer[ys[ok] + y0, xs[ok] + x0] = p_[ys[ok], xs[ok]]
                    lay[key] = layer
                res.append((lay, b_ - a_))
            out[e["into"]] = res
        return out

    def review(self, frames, out_dir, z=3, name=None):
        """Each tag's canvases at z x (cropped to what any frame uses) + a GIF at 2x."""
        name = name or self.D.hero
        os.makedirs(lp(out_dir), exist_ok=True)

        def flat(c):
            if not isinstance(c, dict):
                return self.finish(c)
            full = self.finish(c["body"])
            for fx_, top in ((c.get("under"), False), (c.get("over"), True)):
                if fx_ is not None:
                    m = fx_[..., 3] > 0
                    if not top:
                        m &= full[..., 3] == 0
                    full[m] = fx_[m]
            return full
        frames = {t: [(flat(c), ms) for c, ms in fr] for t, fr in frames.items()}
        allc = np.concatenate([np.stack([f for f, _ in fr]) for fr in frames.values()])
        ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
        y0, y1, x0, x1 = max(0, ys.min() - 2), min(self.CH, max(ys.max() + 3, self.GY + 2)), max(0, xs.min() - 2), xs.max() + 3
        for tag, fr in frames.items():
            tiles = []
            for f, _ in fr:
                bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
                bg.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]))
                d = ImageDraw.Draw(bg)
                d.line([(self.CX - x0, self.GY - y0), (self.CX - x0, self.GY - y0 + 1)], fill=(255, 0, 0, 255))
                tiles.append(bg.convert("RGB"))
            sheet = Image.new("RGB", (len(tiles) * ((x1 - x0) * z + 6), (y1 - y0) * z), (60, 60, 60))
            for i, t in enumerate(tiles):
                sheet.paste(t.resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST), (i * ((x1 - x0) * z + 6), 0))
            sheet.save(lp(os.path.join(out_dir, f"{name}_{tag}.png")))
            small = [t.resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.NEAREST) for t in tiles]
            pal_src = Image.new("RGB", (small[0].width, small[0].height * len(small)))
            for i, t in enumerate(small):
                pal_src.paste(t, (0, i * t.height))
            pal = pal_src.quantize(255, dither=Image.Dither.NONE)
            q = [t.quantize(palette=pal, dither=Image.Dither.NONE) for t in small]
            q[0].save(lp(os.path.join(out_dir, f"{name}_{tag}.gif")), save_all=True, append_images=q[1:],
                      duration=[int(ms) for _, ms in fr], loop=0, optimize=False)


def zoom_crop(a, path, box, z=16, origin=(0, 0)):
    """a[y0:y1, x0:x1] at z x with every square's grid and its design coordinates every 2 (labels from origin)."""
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1]
    H, W = sub.shape[:2]
    img = Image.new("RGBA", ((W + 3) * z, (H + 3) * z), (96, 112, 96, 255))
    img.alpha_composite(Image.fromarray(sub).resize((W * z, H * z), Image.NEAREST), (3 * z, 3 * z))
    dr = ImageDraw.Draw(img)
    for i in range(W + 1):
        dr.line([((i + 3) * z, 3 * z), ((i + 3) * z, (H + 3) * z)], fill=(255, 255, 255, 50 if (x0 + i) % 5 else 140))
        if (x0 + i) % 2 == 0 and i < W:
            dr.text(((i + 3) * z + 1, z), str(x0 + i - origin[0]), fill=(255, 255, 0))
    for j in range(H + 1):
        dr.line([(3 * z, (j + 3) * z), ((W + 3) * z, (j + 3) * z)], fill=(255, 255, 255, 50 if (y0 + j) % 5 else 140))
        if (y0 + j) % 2 == 0 and j < H:
            dr.text((2, (j + 3) * z + 2), str(y0 + j - origin[1]), fill=(255, 255, 0))
    img.convert("RGB").save(lp(path))


def sway(layer, x0, x1, k, attach="right"):
    """Whole columns of `layer` between x0 and x1 (design squares) lifted up to k rows (negative: lowered), nothing at
    the attached end and k at the free one (a tail, a train, a ribbon)."""
    out = layer.copy()
    if not k:
        return out
    n = max(1, x1 - x0)
    for x in range(x0, x1 + 1):
        t = (x1 - x) / n if attach == "right" else (x - x0) / n
        d = int(round(k * t))
        if not d:
            continue
        col = layer[:, x].copy()
        out[:, x] = 0
        if d > 0:
            out[:-d, x] = col[d:]
        else:
            out[-d:, x] = col[:d]
    return out


def compose(rig, layers, fill=()):
    """One frame: layers back to front, each (name or RGBA design-sized array, opts) with opts dx, dy (canvas move
    from standing), angle + about (turned from the picture, Design.turn), flip (+ about), rot (quarter turns, + about),
    sway (x0, x1, k[, attach]). fill: names whose original squares, moved by the given (dx, dy), may be filled from
    the squares round them where the frame left them clear inside its outline. -> canvas."""
    D = rig.D
    can = rig.canvas()
    for name, o in layers:
        off = 0
        if isinstance(name, str):
            if o.get("angle") or name in D.props:
                img, off = D.turn(name, o.get("angle", 0), o["about"], o.get("src")), D.TURN_PAD
            else:
                img = D.layer(name)
        else:
            img = name
            off = (img.shape[0] - D.H) // 2
        if o.get("sway"):
            img = sway(img, *o["sway"])
        about = o.get("about")
        if about is not None:
            about = (about[0] + rig.ox, about[1] + rig.oy)
        big = np.zeros((rig.CH, rig.CW, 4), np.uint8)
        y0, x0 = rig.oy - off, rig.ox - off
        sy0, sx0 = max(0, -y0), max(0, -x0)
        sub = img[sy0:sy0 + rig.CH - max(0, y0), sx0:sx0 + rig.CW - max(0, x0)]
        big[max(0, y0):max(0, y0) + sub.shape[0], max(0, x0):max(0, x0) + sub.shape[1]] = sub
        put(can, big, dx=o.get("dx", 0), dy=o.get("dy", 0), flip=o.get("flip", False),
            rot=o.get("rot", 0), about=about if (o.get("flip") or o.get("rot")) else None, under=o.get("under", False))
    if fill:
        op = can[..., 3] > 0
        inside = ndimage.binary_fill_holes(op)
        allow = np.zeros_like(op)
        for name, (dx, dy) in fill:
            m = np.zeros_like(op)
            m[rig.oy:rig.oy + D.H, rig.ox:rig.ox + D.W] = D.parts[name]
            allow |= np.roll(np.roll(m, dy, 0), dx, 1)
        can = fill_under(can, allow & inside & ~op)
    return can


def flash(can, k=0.45):
    out = can.copy()
    m = out[..., 3] > 0
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


def lie(rig, can, k=1, dx=0, sink=0):
    """The whole frame turned k quarter turns counter-clockwise (lossless), its lowest row `sink` rows under the
    ground line's top, centred dx squares from the standing point (a body lying)."""
    ys, xs = np.nonzero(can[..., 3] > 0)
    sub = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    t = np.rot90(sub, k).copy()
    h, w = t.shape[:2]
    out = rig.canvas()
    top = rig.GY - h + sink
    left = int(round(rig.CX - w / 2)) + dx
    y0, x0 = max(0, top), max(0, left)
    y1, x1 = min(rig.CH, top + h), min(rig.CW, left + w)
    out[y0:y1, x0:x1] = t[y0 - top:y1 - top, x0 - left:x1 - left]
    out[rig.GY + sink:] = 0
    return out


def row_shift(layer, y0, y1, dx):
    """Whole rows y0..y1 of a design-sized layer moved dx columns (a hem swinging)."""
    out = layer.copy()
    if dx:
        out[y0:y1 + 1] = np.roll(layer[y0:y1 + 1], dx, axis=1)
    return out


# ------------------------------------------------------------------------------------------------- polygons
def band(p0, p1, hw0, hw1=None):
    """A polygon hugging the segment p0 -> p1, hw0 wide at p0 and hw1 at p1 (design squares)."""
    hw1 = hw0 if hw1 is None else hw1
    (x0, y0), (x1, y1) = p0, p1
    L = max(1e-6, np.hypot(x1 - x0, y1 - y0))
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    return [(x0 + nx * hw0, y0 + ny * hw0), (x1 + nx * hw1, y1 + ny * hw1), (x1 - nx * hw1, y1 - ny * hw1),
            (x0 - nx * hw0, y0 - ny * hw0)]


# ------------------------------------------------------------------------------------------------- jointed legs
def leg_masks(D, area, hip, knee, keep_out=None, over_knee=1.6, under_knee=1.8, extend=2.0):
    """A leg cut from the picture in two for League-driven poses (tools/lol/league_joints.py): the leg's own pixels
    inside `area` (design squares; keep_out: rgb -> mask of pixels that are not leg, a skirt or a robe), the thigh down
    to over_knee squares past the knee and the shin from under_knee above it (they overlap over the knee, so the joint
    never opens), the thigh's top row carried on up along the thigh to `extend` squares above the hip into D.leg_src
    (the picture the leg props are drawn from: hidden under the skirt, it keeps a turned thigh from opening a gap).
    -> (thigh mask, shin mask) in picture pixels."""
    pic = D.pic
    H, W = pic.shape[:2]
    img = Image.new("L", (W, H), 0)
    ImageDraw.Draw(img).polygon([D.d2p(x, y) for x, y in area], fill=1)
    leg = np.asarray(img, bool) & (pic[..., 3] > 0)
    if keep_out is not None:
        leg &= ~keep_out(pic[..., :3].astype(int))
    lbl, n = ndimage.label(leg, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(leg, lbl, range(1, n + 1))
        leg = lbl == (1 + int(np.argmax(sz)))
    leg = ndimage.binary_fill_holes(leg) & (pic[..., 3] > 0)
    yy, xx = np.mgrid[0:H, 0:W]
    hp, kp = np.array(D.d2p(*hip)), np.array(D.d2p(*knee))
    u = (kp - hp) / np.hypot(*(kp - hp))
    along = (xx - kp[0]) * u[0] + (yy - kp[1]) * u[1]
    sq = 1 / D.k
    thigh = leg & (along <= over_knee * sq)
    shin = leg & (along >= -under_knee * sq)
    if getattr(D, "leg_src", None) is None:
        D.leg_src = pic.copy()
    rows = np.nonzero(thigh.any(1))[0]
    if len(rows):
        top = min(rows.min() + 2, rows.max())
        ref = np.nonzero(thigh[top])[0]
        for y in range(max(0, int(hp[1] - extend * sq)), top):
            dx = int(round((y - top) * u[0] / u[1])) if abs(u[1]) > 1e-6 else 0
            xs = ref + dx
            ok = (xs >= 0) & (xs < W)
            D.leg_src[y, xs[ok]] = pic[top, ref[ok]]
            thigh[y, xs[ok]] = True
    return thigh, shin


def heading(v):
    """Screen angle of a design / game-pixel vector (y down), degrees counter-clockwise from +x."""
    return float(np.degrees(np.arctan2(-v[1], v[0])))


def turn_pt(p, about, deg):
    """p turned deg counter-clockwise on screen about `about`."""
    th = np.radians(deg)
    ax, ay = about
    return np.array((ax + (p[0] - ax) * np.cos(th) + (p[1] - ay) * np.sin(th),
                     ay - (p[0] - ax) * np.sin(th) + (p[1] - ay) * np.cos(th)))


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


class Driver:
    """The design's parts posed after League's skeleton, frame by frame (tools/lol/league_joints.py's json): the
    whole figure moved with League's pelvis (`lunge` of its way forward kept, as tools/lol/native_pose.py does), the
    legs - thigh and shin props each (leg_masks) - turned by the change of League's thigh and shin angles from its
    design pose (at most `leg_max` degrees), the figure set so the lower sole stands as high above the ground as
    League's lower foot; the weapon arm turned with League's shoulder-to-hand, the weapon with League's weapon, the
    upper body leaning `lean` of League's chest-over-pelvis shift. Nothing of the body itself turns (memory
    no-deformation-lossless-poses: a turned torso read as deformed).
    legs: [dict(name, hip, knee, sole, side "near" | "far", rigid)] - "near" takes League's leg nearer the camera; rigid:
    a short leg - the thigh stays, the shin swings about the knee by League's thigh turn.
    arm: dict(name, shoulder, hand, over_weapon, relative, short, league_hand) or None - turned to League's own
    direction on screen (absolute: League's idle often holds the arm unlike the design), or by the change from League's
    design pose (relative: a design drawn after League's idle, league_jax / league_darius); short: League's arm seen
    shorter than `short` of ours (pointing at or away from the camera) turns only that share of the way; dead: a relative
    turn of at most that many degrees is none; league_hand:
    League's weapon hand when its grip joint misleads; over_weapon: the fist drawn over the hilt.
    weapons: [dict(name, grip, tip, league=(joint, joint), relative, aim, chest, floor, on_arm, always_front, rest_back,
    back_when_back, src)] -
    turned about the grip (carried by the arm's turn) to League's direction from its first joint to the second (the end
    matching our `tip`), absolute or relative as the arm; aim: aimed instead from our grip at where League's end is
    against its chest (our `chest` point), since a short chibi arm cannot lift the grip as high; floor: never more than
    that many squares into the ground, on the side it points to.
    attach: [dict(name, anchor, league joint, turn=(joint, joint), max_turn, max_move, always_front)] - props carried
    by a League joint (moved as it moves against the chest, max_move squares at most, turned at most max_turn).
    A part goes behind the body when League's went back from where it is in the design pose by depth_margin (world
    units) - the pictures draw arms and weapons in front. A frame override `keep` holds the arm and the weapons as drawn
    (an idle drawn unlike League's); `walk` (hx, dy) -> leg layers drawn instead of the turned legs, the figure then on
    the design's ground moved by dy alone; the others: dx, dy, lean, arm, weapon (degrees added), rise, extra(j, ux, dy)
    -> (back, front), after. Pieces under `crumb` squares left apart from the figure go. max_lean: columns the upper
    body may lean off the hips (league_kaisa: her bare hip plates sit on the thighs, 1 is all they cover)."""

    def __init__(self, rig, joints, spec_height, rows, legs=(), arm=None, weapons=(), upper="upper", lunge=0.7,
                 lean=0.8, src=None, depth_margin=15.0, attach=(), leg_max=None, crumb=12, max_lean=5):
        self.rig, self.D = rig, rig.D
        self.J = joints
        self.s = self.D.ppu * rows / spec_height              # design squares per League game px
        self.legs, self.arm, self.weapons, self.upper = list(legs), arm, list(weapons), upper
        self.lunge, self.lean, self.src, self.margin = lunge, lean, src, depth_margin
        self.attach = list(attach)
        self.leg_max, self.crumb, self.max_lean = leg_max, crumb, max_lean
        d = joints["design"]
        self.d = d
        # League's near leg: the nearer hip in the design pose
        near_l = d["l_hip"][2] >= d["r_hip"][2] if "l_hip" in d else True
        self.side = {"near": "l" if near_l else "r", "far": "r" if near_l else "l"}
        # the weapon hand: League's hand nearer the weapon's grip (or the arm's league_hand: league_nami's weapon joint
        # sits mid-staff, nearer her other hand)
        if arm is not None and arm.get("league_hand"):
            self.hand = arm["league_hand"]
        elif "weapon" in d and "l_hand" in d:
            dl = np.hypot(d["l_hand"][0] - d["weapon"][0], d["l_hand"][1] - d["weapon"][1])
            dr = np.hypot(d["r_hand"][0] - d["weapon"][0], d["r_hand"][1] - d["weapon"][1])
            self.hand = "l" if dl <= dr else "r"
        else:
            self.hand = "r"

    def ang(self, j, a, b):
        return heading((j[b][0] - j[a][0], j[b][1] - j[a][1]))

    def delta(self, j, a, b):
        return wrap(self.ang(j, a, b) - self.ang(self.d, a, b))

    def frame(self, j, overrides=None):
        o = overrides or {}
        s, d = self.s, self.d
        dx = (j["pelvis"][0] - d["pelvis"][0]) * s * self.lunge + o.get("dx", 0)
        lean = ((j["chest"][0] - j["pelvis"][0]) - (d["chest"][0] - d["pelvis"][0])) * s * self.lean
        layers_legs, soles = [], []
        hx = int(round(dx))
        ux = hx + int(round(max(-self.max_lean, min(self.max_lean, lean)))) + o.get("lean", 0)
        for lg in self.legs:
            sd = self.side[lg["side"]]
            hip, knee, sole = (np.array(v, float) for v in (lg["hip"], lg["knee"], lg["sole"]))
            if f"{sd}_hip" in j:
                r1 = round(self.delta(j, f"{sd}_hip", f"{sd}_knee") / 2) * 2
                r2 = round(self.delta(j, f"{sd}_knee", f"{sd}_foot") / 2) * 2
                if lg.get("rigid"):
                    # a short leg: the stub of thigh stays under the robe and the shin (greave and boot, one piece)
                    # swings about the knee as League's thigh turns (league_jax: turned at a knee cut through the greave
                    # it broke the greave and twisted the boot; turned whole about the hip, the trousers stuck out)
                    r1, r2 = 0, r1
                if self.leg_max is not None:
                    # a body that never turns cannot cross its legs as League's spin does (league_riven's attack: the
                    # legs crossed under a front-facing body read as broken): each piece turned at most leg_max
                    r1 = max(-self.leg_max, min(self.leg_max, r1))
                    r2 = max(-self.leg_max, min(self.leg_max, r2))
            else:
                r1 = r2 = 0
            lx = ux if lg.get("rigid") else hx         # a stub of thigh under the robe moves with the body
            k_at = turn_pt(knee, hip, r1) + (lx, 0)
            kx, ky = int(round(k_at[0] - knee[0])), int(round(k_at[1] - knee[1]))
            s_at = turn_pt(sole, knee, r2) + (kx, ky)
            soles.append(s_at)
            layers_legs.append([(lg["name"] + "_shin", dict(dx=kx, dy=ky, angle=r2, about=tuple(knee), src=self.src)),
                                (lg["name"] + "_thigh", dict(dx=lx, dy=0, angle=r1, about=tuple(hip), src=self.src))])
        # ground: the lower sole raised as much as League's lower foot joint is above where it is in the design pose
        # (the joint is the ankle, never on the floor itself)
        if soles:
            feet = [j[f"{x}_foot"][1] for x in "lr" if f"{x}_foot" in j]
            feet0 = [d[f"{x}_foot"][1] for x in "lr" if f"{x}_foot" in d]
            h = (max(feet0) - max(feet)) if feet else 0.0
            ground = max(lg["sole"][1] for lg in self.legs)
            dy = int(round(ground - max(0.0, h) * s * o.get("rise", 1.0) - max(p[1] for p in soles)))
        else:
            dy = int(round((j["pelvis"][1] - d["pelvis"][1]) * s * o.get("rise", 1.0)))
        dy += o.get("dy", 0)
        if o.get("walk") is not None:
            # the legs the caller draws (a walk: the design's own legs stepped, never turned - league_jax's run), the
            # figure on the design's ground moved only by the caller's dy (its rise)
            dy = o.get("dy", 0)
            layers = list(o["walk"](hx, dy))
        else:
            layers = []
            order = sorted(range(len(self.legs)), key=lambda i: self.legs[i]["side"] != "far")   # the far leg first
            for i in order:
                for name, opt in layers_legs[i]:
                    opt = dict(opt)
                    opt["dy"] += dy
                    layers.append((name, opt))
        front, back = [], []
        chest_z = j["chest"][2]

        def behind(z, z0):
            # behind the body only when League's part went back from its place in the design pose by more than the
            # margin (world units, 5 to a game px): the pictures draw the arm and the weapon in front, though League's
            # design pose often has them a little behind its chest joint (league_darius's axe hid behind him)
            return (z - chest_z) < (z0 - d["chest"][2]) - self.margin
        arm_r = 0
        arm_layer = None
        # a design that turns its limbs and props only losslessly (league_xinzhao: mirrored / quarter-turned, the
        # RotSprite turns read as 「武器变形」) snaps each angle to the nearest one it can draw: D.snap(name, angle)
        snap = getattr(self.D, "snap", None)
        if self.arm is not None:
            h_ = self.hand
            if o.get("keep"):
                arm_r = o.get("arm", 0)
            elif self.arm.get("relative"):
                arm_r = round(self.delta(j, f"{h_}_shoulder", f"{h_}_hand") / 2) * 2
                if abs(arm_r) <= self.arm.get("dead", 0):
                    # a small turn from the idle only opened a slit between the arm and the body (league_darius's
                    # wind-up): the arm stays as drawn
                    arm_r = 0
                arm_r += o.get("arm", 0)
            else:
                v_arm = np.array(self.arm["hand"], float) - np.array(self.arm["shoulder"], float)
                ours = heading(v_arm)
                turn_ = wrap(self.ang(j, f"{h_}_shoulder", f"{h_}_hand") - ours)
                if self.arm.get("short"):
                    # League's arm pointing at or away from the camera shows short on screen and its direction there
                    # means little (league_riven's idle: 3 px, the fist pulled straight out to it): turned only that
                    # share of the way, the rest of it kept as drawn
                    seen = np.hypot(j[f"{h_}_hand"][0] - j[f"{h_}_shoulder"][0],
                                    j[f"{h_}_hand"][1] - j[f"{h_}_shoulder"][1]) * s
                    turn_ *= min(1.0, seen / (self.arm["short"] * float(np.hypot(*v_arm))))
                arm_r = round(turn_ / 2) * 2 + o.get("arm", 0)
            if snap is not None:
                arm_r = snap(self.arm["name"], arm_r)
            arm_layer = (back if behind(j[f"{h_}_hand"][2], d[f"{h_}_hand"][2]) else front,
                         (self.arm["name"], dict(dx=ux, dy=dy, angle=arm_r, about=tuple(self.arm["shoulder"]))))
            if not self.arm.get("over_weapon"):
                arm_layer[0].append(arm_layer[1])
        for w in self.weapons:
            grip = np.array(w["grip"], float)
            g = turn_pt(grip, self.arm["shoulder"], arm_r) if (w.get("on_arm", True) and self.arm) else grip
            gx, gy = int(round(g[0] - grip[0])), int(round(g[1] - grip[1]))
            want = None                                  # the direction League's weapon points on screen
            if o.get("keep"):
                wr = o.get("weapon", 0)
            elif w.get("aim"):
                # aimed from our grip at where League's weapon end is against its chest (w["chest"]: ours): a short
                # chibi arm cannot lift the grip as high as League's, so League's own direction would put the end
                # elsewhere (league_jax's lamp raised over his head pointed down-left from his shoulder); turned by
                # the change of that aim from the design pose (the picture is drawn after League's idle)
                a_, b_ = w["league"]
                span = float(np.hypot(*(np.array(w["tip"], float) - grip)))

                def aim(jj, at):
                    t = np.array(w["chest"], float) + (np.array(jj[b_][:2]) - np.array(jj["chest"][:2])) * s
                    v = t - at
                    own = self.ang(jj, a_, b_)
                    f = min(1.0, float(np.hypot(*v)) / (0.5 * span))   # near the grip the aim is unsteady
                    return own + wrap(heading(v) - own) * f
                want = aim(j, g)
                if w.get("relative"):
                    wr = round(wrap(want - aim(d, grip)) / 2) * 2 + o.get("weapon", 0)
                else:
                    ours = heading(np.array(w["tip"], float) - np.array(w.get("ref", w["grip"]), float))
                    wr = round(wrap(want - ours) / 2) * 2 + o.get("weapon", 0)
            elif w.get("relative"):
                want = self.ang(j, *w.get("league", ("weapon_b", "weapon_a")))
                wr = round(self.delta(j, *w.get("league", ("weapon_b", "weapon_a"))) / 2) * 2 + o.get("weapon", 0)
            else:
                a_, b_ = w.get("league", ("weapon_b", "weapon_a"))
                want = self.ang(j, a_, b_)
                ours = heading(np.array(w["tip"], float) - np.array(w.get("ref", w["grip"]), float))
                wr = round(wrap(want - ours) / 2) * 2 + o.get("weapon", 0)

            if snap is not None:
                wr = snap(w["name"], wr)

            def slide_at(a_ang):
                """(dx, dy) the weapon slides through the hand along its own line at angle a_ang: as League's hand
                moves along League's weapon (league_xinzhao: League holds the spear by the butt to thrust, the picture
                near the blade - turned alone, the blade stayed by his fist and the long butt stuck out behind him);
                still one rigid weapon."""
                if not w.get("slide") or o.get("keep"):
                    return 0.0, 0.0
                sl = w["slide"]
                unit = self.J.get("unit", 1.0)

                def frac(jj):
                    a3, b3, h3 = (np.array(jj[k], float) for k in (w["league"][0], w["league"][1], f"{self.hand}_hand"))
                    for v in (a3, b3, h3):
                        v[2] *= unit
                    ab = b3 - a3
                    return float(np.dot(h3 - a3, ab) / max(1e-9, np.dot(ab, ab)))
                blade = np.array(sl["blade"], float)
                tip_ = np.array(w["tip"], float)
                L = float(np.hypot(*(tip_ - blade)))
                f0 = float(np.hypot(*(grip - blade))) / L
                f1 = max(sl.get("lo", 0.1), min(sl.get("hi", 0.9), f0 + frac(j) - frac(d)))
                u = turn_pt(tip_, grip, a_ang) - turn_pt(blade, grip, a_ang)
                u /= max(1e-9, float(np.hypot(*u)))
                return -(f1 - f0) * L * u[0], -(f1 - f0) * L * u[1]
            if w.get("floor") is not None and self.legs and not o.get("keep"):
                # never more than `floor` squares into the ground: the nearest angle that keeps the weapon's polygon
                # above that, on the side League's points to (a lamp slammed down to his left lies on the ground to his
                # left - not the side a relative turn leans it to: league_jax's picture holds the lamp 23 degrees
                # flatter than League's idle, and a slam down-left came out straight down, then fell right)
                pts = np.array(self.D.polys[w["name"]], float)
                lim = max(lg["sole"][1] for lg in self.legs) + w["floor"] - (dy + gy)
                h0 = heading(np.array(w["tip"], float) - grip)
                side = np.sign(np.cos(np.radians(want if want is not None else h0 + wr))) or 1.0

                def low(a):
                    return max(turn_pt(p, grip, a)[1] for p in pts) + slide_at(a)[1]
                if low(wr) > lim:
                    best = None
                    for k in range(2, 182, 2):
                        cand = (wr + k, wr - k) if snap is None else (snap(w["name"], wr + k), snap(w["name"], wr - k))
                        ok = [a for a in cand if low(a) <= lim]
                        same = [a for a in ok if np.sign(np.cos(np.radians(h0 + a))) == side]
                        if same:
                            best = same[0]
                            break
                        if ok and best is None:
                            best = ok[0]
                    if best is not None:
                        wr = best
            wz = (j["weapon_a"][2] + j["weapon_b"][2]) / 2
            wz0 = (d["weapon_a"][2] + d["weapon_b"][2]) / 2
            in_back = behind(wz, wz0) and not w.get("always_front")
            if w.get("back_when_back") and not o.get("keep") and                     (np.cos(np.radians(heading(np.array(w["tip"], float) - grip) + wr)) < -0.1 or abs(wrap(arm_r)) > 135):
                # pointing back, or held by an arm turned back, a weapon in front lay across the whole body
                # (league_fiora's rapier through her chest in the attack's follow-through, out of her chest in the W):
                # behind it, only the part past the body shows
                in_back = True
            if w.get("rest_back"):
                # a weapon the picture draws behind the body (league_xinzhao's spear across his back): in front only
                # when League's came forward from its place in the design pose by more than the margin
                in_back = not ((wz - chest_z) > (wz0 - d["chest"][2]) + self.margin)
            if w.get("face") and not in_back and not o.get("keep"):
                # a long weapon in front of the body never across the face (league_xinzhao's spear over his eyes): the
                # next angle it can take nearest League's that keeps `face` (x, y, r: design squares, moving with the
                # upper body) r clear of its line and stays out of the ground; none within `face_turn` degrees - behind
                fx_, fy_, fr_ = w["face"]
                blade_ = np.array(w["slide"]["blade"] if w.get("slide") else w["grip"], float)
                tip0 = np.array(w["tip"], float)
                lim_ = (max(lg["sole"][1] for lg in self.legs) + w.get("floor", 99) - (dy + gy)) if self.legs else 1e9

                def face_ok(a):
                    sx2, sy2 = slide_at(a)
                    p0 = turn_pt(blade_, grip, a) + (sx2, sy2)
                    p1 = turn_pt(tip0, grip, a) + (sx2, sy2)
                    q = np.array((fx_, fy_), float) - (gx, gy)        # the face against the weapon's own frame
                    v = p1 - p0
                    t = float(np.clip(np.dot(q - p0, v) / max(1e-9, np.dot(v, v)), 0, 1))
                    return float(np.hypot(*(q - (p0 + t * v)))) > fr_

                def low_ok(a):
                    if w.get("floor") is None or not self.legs:
                        return True
                    pts_ = np.array(self.D.polys[w["name"]], float)
                    return max(turn_pt(p_, grip, a)[1] for p_ in pts_) + slide_at(a)[1] <= lim_
                if not face_ok(wr):
                    target = wr
                    cands = sorted({(snap(w["name"], wr + k) if snap is not None else wr + k) for k in range(-180, 181, 2)},
                                   key=lambda a: abs(wrap(a - target)))
                    pick = next((a for a in cands if abs(wrap(a - target)) <= w.get("face_turn", 70)
                                 and face_ok(a) and low_ok(a)), None)
                    if pick is None:
                        in_back = True
                    else:
                        wr = pick
            sx_, sy_ = slide_at(wr)
            gx, gy = gx + int(round(sx_)), gy + int(round(sy_))
            wlist = back if in_back else front
            wlist.append((w["name"], dict(dx=ux + gx, dy=dy + gy, angle=wr, about=tuple(grip), src=w.get("src"))))
            if arm_layer is not None and self.arm.get("with_weapon"):
                # the fist on the same side of the body as the weapon it holds (league_xinzhao: the spear came in front
                # while League's hand went behind him - a spear in front of his face with no hand on it)
                arm_layer = (wlist, arm_layer[1])
        if arm_layer is not None and self.arm.get("over_weapon"):
            arm_layer[0].append(arm_layer[1])          # the fist over the hilt
        for at in self.attach:
            # a prop carried by a joint of League's (Leona's shield on its own joint): moved as that joint moves
            # against the chest, turned as League's joint pair turns
            jn = at["league"]
            mx_ = ((j[jn][0] - j["chest"][0]) - (d[jn][0] - d["chest"][0])) * s
            my_ = ((j[jn][1] - j["chest"][1]) - (d[jn][1] - d["chest"][1])) * s
            if at.get("max_move") is not None:
                mv = float(np.hypot(mx_, my_))
                if mv > at["max_move"]:
                    mx_, my_ = mx_ * at["max_move"] / mv, my_ * at["max_move"] / mv
            rot_ = round(self.delta(j, *at["turn"]) / 2) * 2 if at.get("turn") else 0
            rot_ = max(-at.get("max_turn", 30), min(at.get("max_turn", 30), rot_))
            if o.get("keep"):
                # held as drawn with the arm (league_kaisa's R landing: League's arms swing back behind a body bent
                # double, which the upright figure cannot show)
                mx_ = my_ = rot_ = 0
            z_ = j[jn][2]
            (back if behind(z_, d[jn][2]) and not at.get("always_front") else front).append(
                (at["name"], dict(dx=ux + int(round(mx_)), dy=dy + int(round(my_)), angle=rot_,
                                  about=tuple(at["anchor"]))))
        if "extra" in o:
            ex_back, ex_front = o["extra"](j, ux, dy)
            back += ex_back
            front += ex_front
        layers = back + layers + [(self.upper, dict(dx=ux, dy=dy))] + front + o.get("after", [])
        can = compose(self.rig, layers)
        # a few squares of a part left peeking out alone where the rest of it went behind the body (league_jax's far
        # boot under his robe): pieces under `crumb` squares apart from the figure go
        op = can[..., 3] > 0
        lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
        if n > 1:
            sz = ndimage.sum(op, lbl, range(1, n + 1))
            for k in range(1, n + 1):
                if sz[k - 1] < self.crumb:
                    can[lbl == k] = 0
        return can


def fit_rows(rows, n):
    """League's frames of a tag spread over n frames (the sheet's count: League's idle has 6 where the sheet has 8):
    frame i takes League's frame at the same share of the clip."""
    if len(rows) == n:
        return rows
    return [rows[min(len(rows) - 1, int(i * len(rows) / n))] for i in range(n)]
