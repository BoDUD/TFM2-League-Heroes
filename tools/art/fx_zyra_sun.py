#!/usr/bin/env python3
"""Zyra's plants one size bigger in Leona's sunlight (the user's easter egg, 2026-11-05: 「植物大战僵尸」 - 「蕾欧娜的技能命中
婕拉的植物会让植物模型变大一号（光合作用）」).

    python tools/art/fx_zyra_sun.py [--review out.png]

The add-on league_zyra draws a plant Leona's sunlight landed on one size bigger for the rest of its life. The plant's own
picture (the main pack's t_plant / v_plant in league_zyra_big: grow 29 ticks, four 60-tick sway cycles, a shake and the
wither, 300 ticks in all) keeps playing - a data plant's is a ViewEffect, a seed plant's one play - so the add-on plays the
big one over it in step: the rest of the current cycle from its next frame (`<k>_big<j>`: cycle frames j..4), then a
whole cycle at every cycle start (`<k>_big0`) and the shake and wither at the end (`<k>_big_end`); a later play is drawn
over an earlier one, so the big plant covers the small one under it. Every segment holds its last frame HOLD ms longer
so two segments overlap instead of leaving a gap. The big frames are the plant's own frames x SCALE about the base of
the stalk (the ground, 11 rows under the pivot): Scale2x first (rounder bulbs and stems than plain nearest-neighbour
at 1.5), then sampled back to x SCALE. `sun_pop` is the moment it grows: a ray of Leona's gold light on the plant and
sparkles rising (her imported effects' colours), symmetric left to right (the client never mirrors an effect).
Written as addons/league_zyra/effects/league_zyra_sun (the add-on's own sheet: only its copy of Zyra binds the views).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "league", "effects", "league_zyra_big")
OUT = os.path.join(ROOT, "addons", "league_zyra", "effects", "league_zyra_sun")
SCALE = 1.5
GROUND = 11                  # the stalk's base under the pivot (every plant frame's lowest row)
HOLD = 2 * 1000.0 / 60       # ms each segment's last frame is held over into the next segment
CYCLE = slice(4, 9)          # one sway cycle in the plant's 30 frames (four of them: 4-8, 9-13, 14-18, 19-23)
END = slice(24, 30)          # the shake and the wither


def hexc(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# Leona's gold (league_leona_fx's sunlight mark)
WHITE, PALE, GOLD, AMBER = map(hexc, ["#FFFFFF", "#FFF6C8", "#FFE066", "#FFB627"])


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def plant_frames(kind):
    """The plant's frames as (array, ms), pivot at each array's centre."""
    an = json.load(open(lp(SRC + "#anim.fanim"), encoding="utf-8"))["anims"][kind]["frames"]
    sheet = np.array(Image.open(lp(SRC + "#sheet.png")).convert("RGBA"))
    out = []
    for f in an:
        d = f["data"]
        x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
        out.append((sheet[y:y + h, x:x + w].copy(), f["duration"] * 1000.0))
    assert len(out) == 30, f"{kind}: {len(out)} frames, the add-on's timeline expects 30"
    cyc = [o[0].tobytes() for o in out[CYCLE]]
    for k in range(1, 4):
        nxt = out[CYCLE.start + 5 * k:CYCLE.stop + 5 * k]
        assert [o[0].tobytes() for o in nxt] == cyc, f"{kind}: cycle {k + 1} differs from the first"
    for arr, _ in out:
        ys, _ = np.nonzero(arr[..., 3])
        assert ys.max() - arr.shape[0] // 2 == GROUND, f"{kind}: a frame's base is not {GROUND} under the pivot"
    return out


def scale2x(a):
    """EPX / Scale2x on an RGBA array."""
    h, w = a.shape[:2]
    pad = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode="edge")
    P = pad[1:-1, 1:-1]
    A, B, C, D = pad[:-2, 1:-1], pad[1:-1, 2:], pad[1:-1, :-2], pad[2:, 1:-1]
    eq = lambda u, v: (u == v).all(axis=-1)
    out = np.zeros((2 * h, 2 * w, 4), np.uint8)
    e0 = np.where((eq(C, A) & ~eq(C, D) & ~eq(A, B))[..., None], A, P)
    e1 = np.where((eq(A, B) & ~eq(A, C) & ~eq(B, D))[..., None], B, P)
    e2 = np.where((eq(D, C) & ~eq(D, B) & ~eq(C, A))[..., None], C, P)
    e3 = np.where((eq(B, D) & ~eq(B, A) & ~eq(D, C))[..., None], D, P)
    out[0::2, 0::2], out[0::2, 1::2], out[1::2, 0::2], out[1::2, 1::2] = e0, e1, e2, e3
    return out


def bigger(a):
    """The frame x SCALE about the base of the stalk (0, GROUND), pivot-relative, as (array, u0, r0)."""
    h, w = a.shape[:2]
    cy, cx = h // 2, w // 2
    src = scale2x(a)
    ys, xs = np.nonzero(a[..., 3])
    top = int(np.floor(GROUND + (ys.min() - cy - GROUND) * SCALE)) - 1
    half = int(np.ceil(max(cx, w - 1 - cx) * SCALE)) + 1
    out = np.zeros((GROUND + 1 - top, 2 * half + 1, 4), np.uint8)
    for oy in range(out.shape[0]):
        Y = oy + top
        sy = GROUND + (Y - GROUND) / SCALE
        py = int(np.floor((sy + cy) * 2 + 1))
        if not 0 <= py < src.shape[0]:
            continue
        for ox in range(out.shape[1]):
            sx = (ox - half) / SCALE
            px = int(np.floor((sx + cx) * 2 + 1))
            if 0 <= px < src.shape[1]:
                out[oy, ox] = src[py, px]
    out[..., 3] = np.where(out[..., 3] > 0, 255, 0)
    return out, -half, top


def big_tags(kind, short):
    fr = plant_frames(kind)
    cells = [(G.centre_frame(*bigger(a)), ms) for a, ms in fr]
    cyc, end = cells[CYCLE], cells[END]
    tags = {}
    for j in range(5):
        seg = list(cyc[j:])
        seg[-1] = (seg[-1][0], seg[-1][1] + HOLD)
        tags[f"{short}_big{j}"] = seg
    seg = list(end)
    seg[-1] = (seg[-1][0], seg[-1][1] + HOLD)
    tags[f"{short}_big_end"] = seg
    return tags


class Pop:
    """A sparkle frame round the plant: x, y pivot-relative; mirrored left to right."""
    HALF, TOP, BOTTOM = 14, -40, 12

    def __init__(self):
        self.a = np.zeros((self.BOTTOM - self.TOP + 1, 2 * self.HALF + 1, 4), np.uint8)

    def put(self, x, y, c):
        for xx in {x, -x}:
            u, r = xx + self.HALF, y - self.TOP
            if 0 <= u < self.a.shape[1] and 0 <= r < self.a.shape[0]:
                self.a[r, u] = (*c, 255)

    def star(self, x, y, core=WHITE, arm=GOLD, size=1):
        self.put(x, y, core)
        for d in range(1, size + 1):
            for dx, dy in [(d, 0), (-d, 0), (0, d), (0, -d)]:
                self.put(x + dx, y + dy, arm)

    def ray(self, y0, y1, width, c):
        for y in range(y0, y1 + 1):
            for x in range(0, width + 1):
                self.put(x, y, c)


def pop_tag():
    """The plant drinking in the sun: a thin ray of gold coming down on it, then sparkles rising off it."""
    out = []
    f = Pop()
    f.ray(-40, -14, 0, PALE)
    f.star(0, -14, size=2)
    out.append(f)
    f = Pop()
    f.ray(-40, -10, 1, GOLD)
    f.ray(-40, -10, 0, WHITE)
    f.star(5, -18, size=1)
    f.star(8, -6, core=PALE, arm=AMBER, size=1)
    out.append(f)
    f = Pop()
    f.ray(-36, -14, 0, GOLD)
    f.star(6, -24, size=2)
    f.star(10, -12, core=PALE, arm=AMBER, size=1)
    f.star(0, -30, core=PALE, size=1)
    out.append(f)
    f = Pop()
    f.star(7, -30, size=1)
    f.star(11, -18, core=GOLD, arm=AMBER, size=1)
    f.star(0, -36, core=PALE, arm=GOLD, size=1)
    out.append(f)
    f = Pop()
    f.put(8, -34, PALE)
    f.put(12, -24, GOLD)
    f.put(0, -39, GOLD)
    out.append(f)
    ticks = [4, 5, 6, 6, 6]
    cells = []
    for k, (p, t) in enumerate(zip(out, ticks)):
        assert (p.a == p.a[:, ::-1]).all(), f"pop frame {k + 1} is not symmetric"
        cells.append((G.centre_frame(p.a, -Pop.HALF, Pop.TOP), t * 1000.0 / 60))
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the small and the big cycles side by side at 6x here")
    a = ap.parse_args()
    tags = {}
    tags.update(big_tags("t_plant", "t"))
    tags.update(big_tags("v_plant", "v"))
    tags["sun_pop"] = pop_tag()
    w, h = G.write_sheet(OUT, tags, share=True)
    print(f"addons/league_zyra/effects/league_zyra_sun#sheet.png {w}x{h}: " +
          ", ".join(f"{t} {len(c)}f {sum(m for _, m in c):.0f}ms" for t, c in tags.items()))
    if a.review:
        Z = 6
        rows = []
        for kind, short in (("t_plant", "t"), ("v_plant", "v")):
            small = [arr for arr, _ in plant_frames(kind)[CYCLE]] + [arr for arr, _ in plant_frames(kind)[END]]
            big = [arr for arr, _ in tags[f"{short}_big0"]] + [arr for arr, _ in tags[f"{short}_big_end"]]
            rows.append((small, big))
        cw = max(arr.shape[1] for s, b in rows for arr in s + b) + 2
        ch = max(arr.shape[0] for s, b in rows for arr in s + b) + 2
        n = max(len(s) for s, _ in rows)
        img = Image.new("RGBA", (cw * Z * n, ch * Z * 4), (90, 140, 90, 255))
        for r, (s, b) in enumerate(rows):
            for line, arrs in ((2 * r, s), (2 * r + 1, b)):
                for k, arr in enumerate(arrs):
                    # centred on the pivot, the pivot at the same spot in every cell
                    im = Image.fromarray(arr).resize((arr.shape[1] * Z, arr.shape[0] * Z), Image.NEAREST)
                    px, py = (k * cw + cw // 2) * Z, (line * ch + ch // 2) * Z
                    img.alpha_composite(im, (px - im.width // 2, py - im.height // 2))
        img.convert("RGB").save(a.review)
        print("review", a.review)


if __name__ == "__main__":
    main()
