#!/usr/bin/env python3
"""Tahm Kench's effects, drawn square by square in code at game size (the user, 2026-10-16: Codex out of quota, 「你能画
吗？用点工具和技术」 - the strips were rigged the same way, tools/art/rig_tahmkench.py).

    python tools/art/fx_tahmkench.py [--review out.png]

Writes league/effects/league_tahmkench_fx and league_tahmkench_big (#sheet.png + #anim.fanim). Every frame is centred on
the unit's pivot (art-spec "Effect anchors": the soles 11 px under it, x forward, y down), one square a game pixel.
Colours: the tongue in the design's pinks, the river in murky teals, the stun in gold, the heal green, Thick Skin's
grey-health shield a pale steel blue. No outline on effects (art-spec), hard pixels, no transparency ramps. Pictures
that ride on him (CasterViewEffect: q_heal, e_shield, w_down, w_up, r_gulp) and every buff are left-right symmetric
(red side: the client never mirrors an effect picture); the tongue projectile is turned with its flight by the game and
is drawn symmetric top to bottom.
  q_tongue  projectile (repeat): the lashing tongue, 26 px long behind its tip, 2 frames
  a_hit     the slap: a pink splat, 3 frames          q_hit   the lash's hit: a bigger splat with drops, 4 frames
  q_stun    gold stars circling over the head, 4 x 300 ms (the 1.25 s stun)
  q_heal    green motes rising round him, 4 frames     e_shield  a steel bubble round him: in, hold, shimmer, out
  w_down    river water bursting up round his feet as he goes under, 4 frames (big sheet)
  w_warn    the spot he comes up: dark water churning with bubbles, 6 x 170 ms (his 1 s under; big sheet)
  w_up      a column of water as he bursts out, its splash ring, 4 frames (big sheet)
  w_hit     a splash under each unit thrown up, 3 frames
  r_gulp    the chomp: drool drops flung from his mouth both ways, 4 frames
  r_in      the swallowed unit pulled in: a dark swirl closing, 3 frames   r_spit  the spit: slime splash, 3 frames
  t_pip1-3  An Acquired Taste's stacks over a champion: one pink drop per slot (left, middle, right), 2 frames
  q_slow    a pink goo puddle at the feet (under), 2 frames   r_full  bubbles rising off him while he digests, 3 frames
  r_bubble  the swallowed unit's mark, 2 frames
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

MOD = os.path.join(ROOT, "league")


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


PINK = [hexc(c) for c in ("#FFE3D6", "#F0A28E", "#D4686A", "#A8344E", "#6E1534")]      # light .. dark
WATER = [hexc(c) for c in ("#E4FFF4", "#9EE6D2", "#4FB3A4", "#2A7A7A", "#174A52", "#0C2A33")]
GOLD = [hexc(c) for c in ("#FFF7C2", "#FFD84A", "#E39A1E", "#9E5A12")]
GREEN = [hexc(c) for c in ("#EFFFD8", "#9CF06A", "#42C24A", "#1E7A3A")]
STEEL = [hexc(c) for c in ("#F2FAFF", "#BFDCEF", "#7FA9C9", "#4D7699")]
DARK = [hexc(c) for c in ("#5A3A6E", "#2E1A40", "#140A1E")]


class Canvas:
    """A frame centred on the pivot: (2R + 1) square, pivot at (R, R); x forward, y down."""

    def __init__(self, r=40):
        self.r = r
        self.a = np.zeros((2 * r + 1, 2 * r + 1, 4), np.uint8)

    def dot(self, x, y, c):
        xi, yi = int(round(x)) + self.r, int(round(y)) + self.r
        if 0 <= xi < self.a.shape[1] and 0 <= yi < self.a.shape[0]:
            self.a[yi, xi] = (*c, 255)

    def disc(self, cx, cy, rad, c, ry=None):
        ry = rad if ry is None else ry
        for y in range(int(math.floor(cy - ry - 1)), int(math.ceil(cy + ry + 1)) + 1):
            for x in range(int(math.floor(cx - rad - 1)), int(math.ceil(cx + rad + 1)) + 1):
                if ((x - cx) / max(rad, 0.01)) ** 2 + ((y - cy) / max(ry, 0.01)) ** 2 <= 1.0:
                    self.dot(x, y, c)

    def ring(self, cx, cy, rx, ry, c, width=1.0, arc=None):
        for y in range(int(cy - ry - 2), int(cy + ry + 3)):
            for x in range(int(cx - rx - 2), int(cx + rx + 3)):
                d = math.hypot((x - cx) / max(rx, 0.01), (y - cy) / max(ry, 0.01))
                if abs(d - 1.0) * min(rx, ry) <= width / 2:
                    if arc is None or arc(math.atan2(y - cy, x - cx)):
                        self.dot(x, y, c)

    def star(self, cx, cy, c_core, c_edge):
        self.dot(cx, cy, c_core)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            self.dot(cx + dx, cy + dy, c_edge)

    def mirror_x(self):
        """Left-right symmetric: the fuller of each mirrored pair kept on both sides."""
        f = self.a[:, ::-1]
        take = (self.a[..., 3] == 0) & (f[..., 3] > 0)
        self.a[take] = f[take]
        return self

    def mirror_y(self):
        f = self.a[::-1]
        take = (self.a[..., 3] == 0) & (f[..., 3] > 0)
        self.a[take] = f[take]
        return self

    def done(self):
        """Cropped to the smallest box still centred on the pivot (odd sizes)."""
        ys, xs = np.nonzero(self.a[..., 3] > 0)
        if not len(ys):
            return np.zeros((3, 3, 4), np.uint8)
        r = self.r
        hw = int(max(abs(xs.min() - r), abs(xs.max() - r))) + 1
        hh = int(max(abs(ys.min() - r), abs(ys.max() - r))) + 1
        return self.a[r - hh:r + hh + 1, r - hw:r + hw + 1].copy()


# ------------------------------------------------------------------------------------------------- the effects
def splat(n, size, y0, cols, drops=4, seed=1):
    """A splat burst: a core blob shrinking, drops flying out and falling."""
    rng = np.random.default_rng(seed)
    angs = [(-math.pi / 2) + (k - (drops - 1) / 2) * (math.pi * 0.9 / max(drops - 1, 1)) for k in range(drops)]
    out = []
    for i in range(n):
        c = Canvas(size + 8)
        t = i / max(n - 1, 1)
        core = size * (0.55 - 0.35 * t)
        if core >= 1:
            c.disc(0, y0, core, cols[2])
            c.disc(-core * 0.25, y0 - core * 0.3, core * 0.55, cols[1])
            c.dot(-core * 0.4, y0 - core * 0.5, cols[0])
        for a in angs:
            r = size * (0.35 + 0.6 * t)
            x, y = math.cos(a) * r, y0 + math.sin(a) * r + 3 * t * t * size * 0.4
            c.disc(x, y, max(0.6, 1.4 - t), cols[1 if t < 0.5 else 2])
        out.append(c.mirror_x().done())
    return out


def tongue_proj():
    frames = []
    for k in range(2):
        c = Canvas(18)
        for x in range(-26, 1):
            t = (x + 26) / 26.0
            w = 1.6 + 1.2 * t
            wob = math.sin((x + 26) / 26 * math.pi * 2 + k * math.pi) * 0.8 * (1 - t)
            for y in range(-4, 5):
                d = y - wob
                if abs(d) <= w:
                    c.dot(x, y, PINK[1] if d < -w * 0.35 else PINK[3] if d > w * 0.45 else PINK[2])
        c.disc(1, 0, 2.6, PINK[2])
        c.dot(0, -1, PINK[0])
        c.dot(1, -1, PINK[1])
        frames.append(c.mirror_y().done())
    return frames


def stun():
    out = []
    for i in range(4):
        c = Canvas(30)
        for k in range(3):
            a = i * (math.pi * 2 / 12) + k * (math.pi * 2 / 3)
            x, y = math.cos(a) * 8, -27 + math.sin(a) * 2.5
            c.star(x, y, GOLD[0], GOLD[1] if math.sin(a) < 0.3 else GOLD[2])
        c.ring(0, -27, 8, 2.5, GOLD[3], 0.8, arc=lambda t: math.sin(t) > 0.2)
        out.append(c.done())
    return out


def heal():
    out = []
    pos = [(-12, 0), (11, -6), (-6, -14), (8, -18), (0, -4)]
    for i in range(4):
        c = Canvas(34)
        for k, (x, y) in enumerate(pos):
            yy = y - i * 4 - (k % 2) * 2
            col = GREEN[1] if i < 3 else GREEN[2]
            c.dot(x, yy, GREEN[0])
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c.dot(x + dx, yy + dy, col)
        out.append(c.mirror_x().done())
    return out


def shield():
    out = []
    for i, (scale, light) in enumerate([(0.6, 1), (1.0, 1), (1.0, 0), (1.04, 2)]):
        c = Canvas(34)
        rx, ry = 26 * scale, 25 * scale
        cy = -9
        c.ring(0, cy, rx, ry, STEEL[3] if light == 2 else STEEL[2], 1.2)
        if light < 2:
            c.ring(0, cy, rx - 1.3, ry - 1.3, STEEL[1], 0.7, arc=lambda t: t < -1.9 or (-1.2 < t < -0.4))
            c.disc(-rx * 0.45, cy - ry * 0.55, 1.2, STEEL[0])
        if light == 0:
            for a in (-2.4, -0.8, 0.6, 2.2):
                c.dot(math.cos(a) * rx, cy + math.sin(a) * ry, STEEL[0])
        out.append(c.mirror_x().done())
    return out


def water_burst(n, ground=11, width=18, height=22, ring=True):
    """Water thrown up round the feet: a ring on the ground and drops rising then falling."""
    out = []
    cols = [-width, -width * 0.6, -width * 0.25, 0]
    for i in range(n):
        c = Canvas(40)
        t = i / max(n - 1, 1)
        if ring:
            c.ring(0, ground - 1, width * (0.5 + 0.6 * t), 3 + 2 * t, WATER[3], 1.4)
            c.ring(0, ground - 2, width * (0.45 + 0.6 * t), 2.5 + 2 * t, WATER[2], 0.8,
                   arc=lambda a: math.sin(a) < 0)
        for k, x in enumerate(cols):
            h = height * (1 - (k / len(cols)) * 0.5)
            yy = ground - 2 - h * math.sin(math.pi * min(1.0, t * 1.1 + 0.15))
            r = 2.2 - 1.2 * t
            c.disc(x * (0.7 + 0.4 * t), yy, max(0.7, r), WATER[1])
            c.dot(x * (0.7 + 0.4 * t) - 0.5, yy - 1, WATER[0])
            if t < 0.6:
                for s in range(1, 4):
                    c.dot(x * (0.7 + 0.4 * t), yy + s * 2, WATER[2])
        out.append(c.mirror_x().done())
    return out


def warn():
    out = []
    bub = [(-9, 0), (-3, 2), (4, -1), (9, 1), (0, -2), (-6, 2), (6, 2)]
    for i in range(6):
        c = Canvas(24)
        c.disc(0, 9, 13, WATER[5], ry=4.5)
        c.disc(0, 9, 11, WATER[4], ry=3.5)
        c.ring(0, 9, 13 - (i % 3), 4.5 - (i % 3) * 0.4, WATER[3], 0.8)
        for k, (x, y) in enumerate(bub):
            ph = (i + k * 2) % 6
            if ph < 3:
                c.disc(x, 9 + y * 0.5 - ph, 0.6 + ph * 0.5, WATER[1])
                c.dot(x - (1 if ph else 0), 9 + y * 0.5 - ph - (1 if ph else 0), WATER[0])
        out.append(c.done())
    return out


def column():
    out = []
    for i in range(4):
        c = Canvas(44)
        t = i / 3
        top = -40 + 18 * t if i else -20
        w = 9 - 4 * t
        for y in range(int(top), 11):
            ww = w * (0.6 + 0.4 * (y - top) / max(11 - top, 1))
            for x in range(-int(ww), int(ww) + 1):
                d = abs(x) / max(ww, 1)
                c.dot(x, y, WATER[0] if d < 0.25 else WATER[1] if d < 0.6 else WATER[2])
        c.ring(0, 10, 16 + 8 * t, 3.5 + t, WATER[3], 1.3)
        for k in range(3):
            c.disc(6 + k * 5 + 6 * t, top + 6 + k * 7 + 8 * t, 1.6 - 0.3 * k, WATER[1])
        out.append(c.mirror_x().done())
    return out


def swirl():
    out = []
    for i in range(3):
        c = Canvas(20)
        r0 = 13 - i * 4
        for k in range(36):
            a = k / 36 * math.pi * 4 + i * 0.9
            r = r0 * (1 - k / 48)
            c.dot(math.cos(a) * r, -6 + math.sin(a) * r * 0.7, DARK[k % 2] if k < 30 else PINK[2])
        c.disc(0, -6, 2.5 - i * 0.6, DARK[2])
        out.append(c.done())
    return out


def gulp():
    out = []
    for i in range(4):
        c = Canvas(34)
        t = i / 3
        for k, (dx, dy) in enumerate([(14, -26), (18, -20), (11, -31)]):
            x, y = dx * (0.6 + 0.6 * t), dy + 14 * t * t
            c.disc(x, y, 1.6 - 0.5 * t, PINK[1])
            c.dot(x - 1, y - 1, PINK[0])
        if i < 2:
            c.ring(0, -22, 9 + 4 * i, 5 + 2 * i, PINK[0], 0.9, arc=lambda a: math.sin(a) < -0.3)
        out.append(c.mirror_x().done())
    return out


def pip(slot):
    out = []
    x = {1: -6, 2: 0, 3: 6}[slot]
    for k in range(2):
        c = Canvas(34)
        y = -31 - k
        c.disc(x, y, 1.6, PINK[2], ry=2.0)
        c.dot(x, y - 2, PINK[2])
        c.dot(x - 0.5, y - 0.5, PINK[0])
        c.dot(x + 1, y + 1, PINK[4])
        out.append(c.done())
    return out


def goo():
    out = []
    for k in range(2):
        c = Canvas(18)
        c.disc(0, 11, 10 + k, PINK[3], ry=2.6)
        c.disc(-1, 10.5, 7, PINK[2], ry=1.6)
        c.dot(-4 + k * 2, 10, PINK[1])
        c.dot(4 - k, 11, PINK[1])
        out.append(c.mirror_x().done())
    return out


def full():
    out = []
    pts = [(-10, -6), (9, -12), (-4, -18), (5, -3)]
    for i in range(3):
        c = Canvas(30)
        for k, (x, y) in enumerate(pts):
            yy = y - ((i + k) % 3) * 4
            c.ring(x, yy, 1.6, 1.6, PINK[1], 0.8)
            c.dot(x - 1, yy - 1, PINK[0])
        out.append(c.mirror_x().done())
    return out


def bubble():
    out = []
    for k in range(2):
        c = Canvas(20)
        c.ring(0, -6, 11 + k, 12 + k, PINK[2], 1.0)
        c.dot(-5, -13, PINK[0])
        out.append(c.mirror_x().done())
    return out


def build():
    ms = lambda frames, d: [(f, d) for f in frames]
    fx = {
        "league_tahmkench_a_hit": ms([np.roll(f, 0) for f in splat(3, 6, -6, PINK, drops=3, seed=2)], 70),
        "league_tahmkench_q_tongue": ms(tongue_proj(), 80),
        "league_tahmkench_q_hit": ms(splat(4, 9, -6, PINK, drops=5, seed=3), 70),
        "league_tahmkench_q_stun": ms(stun(), 300),
        "league_tahmkench_q_heal": ms(heal(), 120),
        "league_tahmkench_e_shield": [(f, d) for f, d in zip(shield(), (80, 600, 900, 100))],
        "league_tahmkench_w_hit": ms(water_burst(3, ground=11, width=8, height=10), 90),
        "league_tahmkench_r_gulp": ms(gulp(), 90),
        "league_tahmkench_r_in": ms(swirl(), 100),
        "league_tahmkench_r_spit": ms(splat(3, 8, -6, PINK, drops=4, seed=5), 90),
        "league_tahmkench_t_pip1": ms(pip(1), 400),
        "league_tahmkench_t_pip2": ms(pip(2), 400),
        "league_tahmkench_t_pip3": ms(pip(3), 400),
        "league_tahmkench_q_slow": ms(goo(), 300),
        "league_tahmkench_r_full": ms(full(), 200),
        "league_tahmkench_r_bubble": ms(bubble(), 300),
    }
    big = {
        "league_tahmkench_w_down": ms(water_burst(4, ground=11, width=18, height=22), 100),
        "league_tahmkench_w_warn": ms(warn(), 170),
        "league_tahmkench_w_up": ms(column(), 90),
    }
    return {"league_tahmkench_fx": fx, "league_tahmkench_big": big}


def review(sheets, path, z=6):
    from PIL import ImageDraw
    rows = []
    for tags in sheets.values():
        for name, frames in tags.items():
            W = sum(f.shape[1] + 3 for f, _ in frames)
            H = max(f.shape[0] for f, _ in frames)
            img = Image.new("RGBA", (W * z, H * z), (92, 98, 86, 255))
            x = 0
            for f, _ in frames:
                img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST),
                                    (x * z, (H - f.shape[0]) // 2 * z))
                x += f.shape[1] + 3
            rows.append((name.replace("league_tahmkench_", ""), img))
    W = max(r.width for _, r in rows) + 110
    Ht = sum(r.height + 8 for _, r in rows)
    out = Image.new("RGB", (W, Ht), (30, 32, 30))
    d = ImageDraw.Draw(out)
    y = 0
    for name, r in rows:
        d.text((4, y + 4), name, fill=(255, 255, 255))
        out.paste(r, (110, y), r)
        y += r.height + 8
    out.save(path)
    print(path, out.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    sheets = build()
    for sheet, tags in sheets.items():
        tags = {k.replace("league_tahmkench_", ""): v for k, v in tags.items()}
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(v)}" for t, v in tags.items()))
    if a.review:
        review(sheets, a.review)


if __name__ == "__main__":
    main()
