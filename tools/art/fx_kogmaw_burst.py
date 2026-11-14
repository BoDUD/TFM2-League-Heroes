#!/usr/bin/env python3
"""Kog'Maw's void form bursting (Icathian Surprise, the add-on league_kogmaw 0.1.0, 2026-11-14): league/effects/
league_kogmaw_burst#sheet.png + #anim.fanim, drawn by code at 1x and at PPU 2 (the density of his league_kogmaw_big, whose
p_boom it replaces: the user, after a GIF of the old comet, 「大嘴死了还是看不到炸人啊」 then 「按英雄联盟改」).

    python -I tools/art/fx_kogmaw_burst.py [--check] [--review <dir>]

The add-on plays `league_kogmaw_p_void` (its copy's view effect: this sheet's `burst`) where the form bursts, a
ViewEffect on that point - never turned, never mirrored (champion-data section 6), so it may have an up and a down.
Everything is shapes in game pixels (tools/art/unit_draw.py's Raster) sampled once a game pixel and twice: the same
drawing at both densities, hard edges, no blur, every hd_ frame exactly twice its 1x frame and both centred on the point
(the form's pivot; its feet and the ground ring GROUND game px under it). Outline-free, saturated, as the pack's effects.

  burst  8 frames, 0.51 s: a white-hot flash in the form's middle (0); a magenta ball of void light with rays and a ring
         on the ground (1); the ball at its biggest, a violet column of light rising out of it, sparks flying (2, 3); the
         ball caving in to a dark void with a magenta rim while the ring runs out to 30 game px (4, 5); a last dark speck,
         embers and smoke (6, 7).
The damage reaches p_r = 12000 (12 game px) plus a unit's radius round the point: the ring passes it by frame 2 and keeps
going - the picture is meant to be seen, not to measure. Today's p_boom (league_kogmaw_big) is 25 x 45 at most, 0.42 s;
this one is up to 65 x 77, a white core and three bright rings of colour.
  idle   one empty frame (the effects PPU table reads the density from idle and hd_idle: tools/art/fx_ppu_table.py).
--check: exit 1 when the sheet in the repo is not what this writes. --review: every frame at 3x (1x and dense rows), the
burst beside today's p_boom and beside the form, at game scale.
"""
import argparse
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_draw as U  # noqa: E402

NAME = "league_kogmaw_burst"
OUT_STEM = os.path.join(U.ROOT, "league", "effects", NAME)
PPU = 2
G = U.G
GROUND = 10.0                   # the form's feet under its pivot: his frames end 12-13 game px down (the ring's middle)
FLAT = 0.42                     # the ground's tilt: a ring on it is this much as tall as it is wide

WHITE = (255, 246, 255)
MAG = [(84, 6, 66), (150, 18, 116), (222, 46, 172), (255, 112, 214), (255, 206, 246)]
VIO = [(70, 26, 140), (122, 58, 214), (176, 112, 255), (222, 182, 255), (248, 236, 255)]
VOID = [(10, 2, 22), (34, 8, 62), (58, 18, 100)]

BURST_MS = (40, 50, 60, 60, 70, 70, 80, 80)
# sparks: the angle (degrees round the ball, 0 = right, 90 = down) and how fast it flies (game px a frame)
SPARKS = [(-80, 4.6), (-48, 5.2), (-20, 4.2), (8, 5.6), (34, 4.4), (62, 3.8), (118, 3.6), (148, 4.8), (172, 5.4),
          (200, 4.4), (228, 5.0), (256, 4.2)]


class Painter:
    """one frame on a raster: shapes painted back to front"""

    def __init__(self, R):
        self.R = R
        self.c = R.blank()

    def put(self, mask, colour):
        self.c[mask, :3] = colour
        self.c[mask, 3] = 255

    def disc(self, cx, cy, r, colour, flat=1.0):
        m, _, _ = U.ellipse(self.R, cx, cy, r, r * flat)
        self.put(m, colour)
        return m

    def ring(self, cx, cy, rx, ry, width, colour, keep=None):
        """the squares between two ellipses `width` game px apart (thinner at the ends of the short axis, as on the
        ground); `keep`: angles (radians, 0 = right) that are drawn, as (from, to) - the rest are gaps"""
        outer, u, v = U.ellipse(self.R, cx, cy, rx, ry)
        inner, _, _ = U.ellipse(self.R, cx, cy, max(rx - width, 0.1), max(ry - width * FLAT, 0.1))
        m = outer & ~inner
        if keep is not None:
            ang = np.arctan2(v, u)
            ok = np.zeros_like(m)
            for a, b in keep:
                ok |= (ang >= a) & (ang <= b)
            m &= ok
        self.put(m, colour)

    def ray(self, cx, cy, deg, r0, r1, width, colour, flat=1.0):
        a = np.radians(deg)
        p = (cx + r0 * np.cos(a), cy + r0 * np.sin(a) * flat)
        q = (cx + r1 * np.cos(a), cy + r1 * np.sin(a) * flat)
        self.put(U.capsule(self.R, p, q, width), colour)

    def tongue(self, pts, r0, r1, colour):
        """a tongue of void fire along the polyline `pts`, tapering from r0 to r1"""
        n = len(pts) - 1
        m = self.R.none()
        for i, (p, q) in enumerate(zip(pts, pts[1:])):
            m |= U.capsule(self.R, p, q, r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n)
        self.put(m, colour)

    def flames(self, k, scale, outer, inner):
        """the tongues rising out of the ball: three, bending, each a darker sheath round a brighter core"""
        for dx, lean, h in ((-5.0, -4.5, 0.78), (0.5, 1.5, 1.0), (5.5, 5.0, 0.70)):
            top = -2.0 - (14.0 + 16.0 * scale) * h
            mid = (dx + lean * 0.35, -2.0 + (top + 2.0) * 0.55)
            pts = [(dx * 0.6, -4.0), mid, (dx + lean, top)]
            self.tongue(pts, 4.2 * (0.8 + 0.2 * scale), 1.0, outer)
            self.tongue(pts[:2] + [(dx + lean * 0.8, top + 5.0)], 2.2 * (0.8 + 0.2 * scale), 0.6, inner)

    def ball(self, r, colours, bumps=8, turn=0.0):
        """the ball of void light: discs from the outside in, its rim knobbly (bumps of uneven size round it)"""
        knob = (0.30, 0.20, 0.34, 0.24, 0.29, 0.18, 0.32, 0.22)
        for i, (frac, colour) in enumerate(colours):
            rr = r * frac
            self.disc(0, -2, rr, colour)
            if i == 0 and bumps:
                for j in range(bumps):
                    a = turn + (j + 0.17 * (j % 3)) * 2 * np.pi / bumps
                    s = knob[j % len(knob)]
                    self.disc((rr - s * rr * 0.3) * np.cos(a), -2 + (rr - s * rr * 0.3) * np.sin(a), rr * s, colour)

    def sparks(self, k, colour, hot, size=0.75):
        for i, (deg, v) in enumerate(SPARKS):
            r = 6.0 + v * k
            a = np.radians(deg)
            x, y = r * np.cos(a), -2.0 + r * np.sin(a) * 0.7 + 0.35 * k * k   # they fall a little as they fly
            self.put(U.ellipse(self.R, x, y, size, size)[0], hot if i % 3 == 0 else colour)


def frame(R, k):
    """burst frame k on raster R"""
    P = Painter(R)
    gy = GROUND
    if k == 0:
        P.ring(0, -2, 7.5, 7.5, 1.6, MAG[3])
        for deg in (0, 90, 180, 270):
            P.ray(0, -2, deg, 6.0, 10.0, 0.6, VIO[4])
        P.disc(0, -2, 4.6, WHITE)
    elif k == 1:
        P.ring(0, gy, 13, 13 * FLAT, 1.6, VIO[3])
        for deg in range(0, 360, 45):
            P.ray(0, -2, deg + 22.5, 9.5, 15.5, 0.55, MAG[3])
        P.ball(8.5, [(1.0, MAG[3]), (0.75, MAG[4]), (0.52, WHITE)])
        P.sparks(1, VIO[4], WHITE)
    elif k == 2:
        P.ring(0, gy, 19, 19 * FLAT, 1.8, VIO[3])
        P.ring(0, gy, 15, 15 * FLAT, 1.0, MAG[2])
        P.flames(2, 0.6, VIO[2], VIO[4])
        P.ball(11.5, [(1.0, MAG[2]), (0.76, MAG[4]), (0.48, WHITE)], turn=0.3)
        P.sparks(2, MAG[3], VIO[4])
    elif k == 3:
        P.ring(0, gy, 24, 24 * FLAT, 1.6, VIO[2])
        P.ring(0, gy, 20, 20 * FLAT, 1.0, MAG[2])
        P.flames(3, 1.0, VIO[1], VIO[3])
        P.ball(12.5, [(1.0, MAG[1]), (0.8, MAG[2]), (0.48, MAG[3])], turn=0.7)
        P.sparks(3, MAG[3], VIO[4])
    elif k == 4:
        gaps = [(-3.0, -1.9), (-1.6, -0.2), (0.1, 1.5), (1.8, 3.1)]
        P.ring(0, gy, 27.5, 27.5 * FLAT, 1.4, VIO[1], keep=gaps)
        P.ring(0, gy, 23, 23 * FLAT, 0.9, MAG[1], keep=gaps)
        for x, y0, y1 in ((-7.0, -20.0, -29.0), (1.5, -25.0, -38.0), (8.0, -19.0, -27.0)):
            P.tongue([(x, y0), (x + 0.8, (y0 + y1) / 2), (x + 2.0, y1)], 2.4, 0.7, VIO[1])
        P.ball(11.0, [(1.0, MAG[2]), (0.8, VOID[2]), (0.6, VOID[1])], bumps=6, turn=0.2)
        P.sparks(4, MAG[2], VIO[3])
    elif k == 5:
        gaps = [(-2.8, -2.2), (-1.3, -0.6), (0.4, 1.0), (2.0, 2.7)]
        P.ring(0, gy, 30, 30 * FLAT, 1.2, VIO[1], keep=gaps)
        for x, y, r in ((-6, -16, 2.6), (5, -21, 2.2), (-1, -27, 1.8)):
            P.disc(x, y, r, VOID[2])
        P.disc(0, -2, 7.4, VIO[1])
        P.disc(0, -2, 5.6, VOID[1])
        P.disc(0, -2, 3.6, VOID[0])
        P.sparks(5, VIO[2], MAG[3], size=0.6)
    elif k == 6:
        for x, y, r in ((-7, -21, 2.2), (6, -26, 1.8), (0, -31, 1.4)):
            P.disc(x, y, r, VOID[1])
        P.disc(0, -2, 3.4, VIO[0])
        P.disc(0, -2, 2.0, VOID[0])
        P.sparks(6, VIO[1], MAG[2], size=0.55)
    else:
        for x, y in ((-12, -6), (14, 0), (-3, -24), (9, 7)):
            P.put(U.ellipse(R, x, y, 0.55, 0.55)[0], VIO[1])
        P.disc(0, -2, 1.4, VIO[0])
    return P.c


def build():
    out = []
    for d in (1, PPU):
        R = U.Raster(d, half=36, up=42, down=24)
        out.append((R, [frame(R, k) for k in range(len(BURST_MS))]))
    (R1, f1), (Rd, fd) = out
    burst, hd_burst = [], []
    for a, b, ms in zip(f1, fd, BURST_MS):
        p1, pd = U.frame_pair(a, R1, b, Rd)
        burst.append((p1, ms))
        hd_burst.append((pd, ms))
    blank1, blankd = np.zeros((3, 3, 4), np.uint8), np.zeros((3 * PPU, 3 * PPU, 4), np.uint8)
    return {"idle": [(blank1, 100)], "burst": burst, "hd_idle": [(blankd, 100)], "hd_burst": hd_burst}


def write(tags, check):
    if check:
        tmp = os.path.join(tempfile.mkdtemp(prefix="fx_"), NAME)
        G.write_sheet(tmp, tags)
        same = False
        if os.path.exists(G.lp(OUT_STEM + "#sheet.png")) and os.path.exists(G.lp(OUT_STEM + "#anim.fanim")):
            (a, b), (c, d) = U.read_sheet(OUT_STEM), U.read_sheet(tmp)
            same = b == d and a.shape == c.shape and bool((a == c).all())
        print(f"{NAME}:", "up to date" if same else "stale")
        sys.exit(0 if same else 1)
    w, h = G.write_sheet(OUT_STEM, tags)
    print("wrote %s#sheet.png (%d x %d) and #anim.fanim: %s" % (
        os.path.relpath(OUT_STEM, U.ROOT), w, h,
        ", ".join("%s %d frames %.2f s" % (t, len(fr), sum(ms for _, ms in fr) / 1000.0) for t, fr in tags.items())))


def review(tags, folder):
    """every frame at 3x (1x and dense rows), and the burst beside today's p_boom and the form at game scale"""
    from PIL import Image, ImageDraw
    os.makedirs(folder, exist_ok=True)
    boom = U.sheet_frames(os.path.join(U.ROOT, "league", "effects", "league_kogmaw_big"), "p_boom")
    hd_boom = U.sheet_frames(os.path.join(U.ROOT, "league", "effects", "league_kogmaw_big"), "hd_p_boom")
    rows = [("p_boom today 1x", boom, 1.0), ("hd_p_boom today", hd_boom, 0.5),
            ("burst 1x", tags["burst"], 1.0), ("hd_burst", tags["hd_burst"], 0.5)]
    zoom = 3
    cell = 80 * zoom
    img = Image.new("RGBA", (180 + 8 * (cell + 6), len(rows) * (cell + 24) + 6), (74, 92, 70, 255))
    dr = ImageDraw.Draw(img)
    y = 6
    for label, fr, s in rows:
        dr.text((6, y + cell // 2), label, fill=(255, 255, 0, 255))
        x = 180
        for i, (f, ms) in enumerate(fr):
            w, h = max(1, int(round(f.shape[1] * s * zoom))), max(1, int(round(f.shape[0] * s * zoom)))
            im = Image.fromarray(f, "RGBA").resize((w, h), Image.NEAREST)
            img.alpha_composite(im, (x + (cell - w) // 2, y + 14 + (cell - h) // 2))
            dr.text((x + 2, y), "%d  %d ms  %dx%d" % (i, ms, f.shape[1], f.shape[0]), fill=(255, 255, 255, 255))
            x += cell + 6
        y += cell + 24
    path = os.path.join(folder, "kogmaw_burst_frames.png")
    img.save(path)
    print("review", path)
    form = U.sheet_frames(os.path.join(U.CHAMPIONS, "league_kogmaw_void"), "hd_idle")[0][0]
    figs = [("the form", form, 1.0 / 1.794), ("p_boom 2", hd_boom[2][0], 0.5), ("p_boom 3", hd_boom[3][0], 0.5),
            ("burst 1", tags["hd_burst"][1][0], 0.5), ("burst 2", tags["hd_burst"][2][0], 0.5),
            ("burst 3", tags["hd_burst"][3][0], 0.5), ("burst 4", tags["hd_burst"][4][0], 0.5),
            ("burst 5", tags["hd_burst"][5][0], 0.5)]
    print("review", U.beside(figs, os.path.join(folder, "kogmaw_burst_beside_boom.png"), scale=3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    a = ap.parse_args()
    tags = build()
    if a.review:
        review(tags, a.review)
    write(tags, a.check)


if __name__ == "__main__":
    main()
