"""Minimal lossless pixel rig primitives from the local rigkit."""
import math
import numpy as np

def mask_rows(spec, shape=(128, 128)):
    """{row: (first, last)} or {row: [cols]} -> bool mask."""
    m = np.zeros(shape, bool)
    for r, cols in spec.items():
        if isinstance(cols, tuple) and len(cols) == 2:
            m[r, cols[0]:cols[1] + 1] = True
        else:
            m[r, list(cols)] = True
    return m

class Part:
    """A sprite (RGBA, cropped) with a joint in sprite coordinates (pixel centres = integer + 0.5)."""

    def __init__(self, s, joint):
        self.s = s
        self.j = joint

    @classmethod
    def from_canvas(cls, a, mask, joint):
        ys, xs = np.nonzero(mask & (a[..., 3] > 0))
        y0, x0 = ys.min(), xs.min()
        s = np.zeros((ys.max() - y0 + 1, xs.max() - x0 + 1, 4), np.uint8)
        s[ys - y0, xs - x0] = a[ys, xs]
        return cls(s, (joint[0] - x0, joint[1] - y0))

    def flip_h(self):
        return Part(self.s[:, ::-1].copy(), (self.s.shape[1] - self.j[0], self.j[1]))

    def flip_v(self):
        return Part(self.s[::-1].copy(), (self.j[0], self.s.shape[0] - self.j[1]))

    def transpose(self):
        return Part(self.s.transpose(1, 0, 2).copy(), (self.j[1], self.j[0]))

def put(dst, src, ox, oy, under=False):
    """src's opaque squares onto dst at top-left (ox, oy); under=True only where dst is clear."""
    ys, xs = np.nonzero(src[..., 3])
    cy, cx = ys + oy, xs + ox
    ok = (cy >= 0) & (cy < dst.shape[0]) & (cx >= 0) & (cx < dst.shape[1])
    ys, xs, cy, cx = ys[ok], xs[ok], cy[ok], cx[ok]
    if under:
        free = dst[cy, cx, 3] == 0
        ys, xs, cy, cx = ys[free], xs[free], cy[free], cx[free]
    dst[cy, cx] = src[ys, xs]
    return dst

def place(dst, part, at, under=False):
    """The part with its joint on the canvas point `at` (continuous)."""
    return put(dst, part.s, int(math.floor(at[0] - part.j[0] + 1e-9)), int(math.floor(at[1] - part.j[1] + 1e-9)), under)

def rot90(part, k):
    """The part turned k quarter turns clockwise on screen about its joint - lossless, and unlike a mirror it keeps
    a curved blade's shape (which edge is serrated, which way it bends)."""
    s, (jx, jy) = part.s, part.j
    for _ in range(k % 4):
        H = s.shape[0]
        s = np.rot90(s, -1)                  # clockwise: (x, y) -> (H - y, x)
        jx, jy = H - jy, jx
    return Part(s.copy(), (jx, jy))