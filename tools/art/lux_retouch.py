#!/usr/bin/env python3
"""Lux's retouch table (assets/source/native/lux_retouch.json): her whole staff and even eyes.

    python tools/art/lux_retouch.py [--preview DIR]     # then: python tools/art/import_native.py --hero lux

Two passes over the frames as import_native.py has cut them (before its retouch step, which applies the table this
writes), BROWS then STAFF.

BROWS (the user, 2026-10-05: 「眼睛统一统一 不对的地方就行修正」). The design draws each eye as one row of dark lid over a
white and a blue square, the forehead's skin over the lids (idle, the face the user picked on 2026-09-30). The face
was pasted into every frame on Codex's step-2 hair, and in 18 frames the bangs' outline (or a grey highlight) came
down onto a lid, so one eye looked twice as heavy as the other. Over every pair of eye blues (#2D6FB8, three
squares apart) the row above the lids - from the left white to the right blue - is skin again wherever it is dark
or grey.

STAFF (the user, 2026-10-05: 「拉克丝看起来好像法杖被截断？你查一查这个问题」). Lux's wand is a staff almost as tall as she
is, a finial at each end, held near the middle (League's model; assets/source/lux/PROMPTS.md asked for it, and
the round-1 strips had it). Codex's step-2 redraw (the strips in assets/source/native) kept only the part above
her hand: the upper finial on a short shaft, the hand at its end and nothing past it, so wherever the shaft
should go on past the hand it looks cut off there - most of all where she holds it up (idle, hit, Q, E, the R's
landing) and where the R's wand floats free with one bare end.

Each STAFF entry draws what is missing in one frame, on the frame as import_native.py has cut it (before its
retouch step, which applies the table this writes):
  ("line", (x0, y0), (x1, y1), layer)   the shaft from the hand on, in the line of the part above it: one square
                                        of SHAFT colours, an outline square on both sides, then the lower finial
                                        (FINIAL: a cross-bar of three and a tip) past (x1, y1). "front" draws over
                                        the body (a staff held in front of her, outlined against it); "back" only
                                        on clear squares (behind her: it shows where it comes out). The first
                                        square replaces the hand's outline, so the shaft comes out of the fist.
  ("paint", [(x, y, colour), ...])      single squares (a shaft Codex drew in outline colour, between the finial
                                        and the hand, made gold).
x, y count from the pivot (x right, y down), as in the retouch table. The lower part is about three quarters of
the part above the hand (League: the hand 55-60% of the way down) and keeps clear of the feet, where a gold end
once read as a gold foot (the run's retouch of 2026-09-27).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import import_native as N  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "native", "lux_retouch.json")
ABOUT = ("Written by tools/art/lux_retouch.py, do not edit by hand. BROWS: the row above both eye lids is the "
         "forehead's skin again where the bangs' outline or a grey highlight came down onto a lid (one eye looked "
         "twice as heavy). STAFF: the lower half of Lux's staff below her hand, which Codex's step-2 redraw left "
         "off (idle, run 4-8, attack 6, Q 1 and 7, E 2, 6 and 7, R 2-8, hit, death 1).")
OUTLINE = (0x13, 0x0C, 0x14)
GOLD = (0xF5, 0xC3, 0x51)          # the shaft (the upper shaft's middle gold)
SHADE = (0xCF, 0x90, 0x34)         # its shaded squares and the finial's sides
LIGHT = (0xFB, 0xD1, 0x61)         # the finial's bright middle
SHAFT = [SHADE, GOLD, GOLD]        # repeated down the shaft from the hand: a ribbon's turns
SKIN = {(0xFC, 0xD4, 0xAE), (0xD5, 0x89, 0x6E)}
FOREHEAD = (0xFC, 0xD4, 0xAE)
EYE = (0x2D, 0x6F, 0xB8)
GREY = {(0xD2, 0xCA, 0xCB), (0xB1, 0xA3, 0xAB)}

IDLE = [("line", (8, -2), (6, 2), "front")]
STAFF = {
    # idle (one drawing six times): the staff down across her skirt to the knee
    **{("idle", k): IDLE for k in range(6)},
    # run 4-8: held upright behind her; the end stops above the hip so it never meets the back leg
    ("run", 3): [("line", (-5, -4), (-5, -2), "back")],
    ("run", 4): [("line", (-6, -3), (-6, -1), "back")],
    ("run", 5): [("line", (-6, -2), (-6, 0), "back")],
    ("run", 6): [("line", (-6, -2), (-6, 0), "back")],
    ("run", 7): [("line", (-6, -3), (-6, -1), "back")],
    # attack 6: Codex drew three squares below the fist; the staff goes on to the skirt's edge
    ("attack", 5): [("line", (11, -3), (9, 0), "front")],
    # Q 1 and 7: held upright beside her
    ("skill", 0): [("line", (8, -4), (7, -2), "back")],
    ("skill", 6): [("line", (11, -3), (9, 0), "front")],
    # E 2 (raised behind her), 6 (the user's frame: upright at arm's length), 7
    ("skill2", 1): [("line", (-16, -10), (-14, -3), "back")],
    ("skill2", 5): [("line", (18, -6), (18, 1), "back")],
    ("skill2", 6): [("line", (8, 0), (6, 4), "front")],
    # R 2-7: the wand floating free had one bare end; R 8: caught and held upright
    ("ult", 1): [("line", (18, -3), (11, -1), "back")],
    ("ult", 2): [("line", (12, -3), (6, -1), "back")],
    ("ult", 3): [("line", (13, -2), (7, 0), "back")],
    ("ult", 4): [("line", (15, -5), (9, -3), "back")],
    ("ult", 5): [("line", (19, -1), (13, 1), "back")],
    ("ult", 6): [("line", (6, 1), (1, 3), "back")],
    ("ult", 7): [("line", (5, -3), (4, 0), "front")],
    # hit: the shaft between the finial and the hand was outline-dark in hit 1 and partly in hit 2
    ("hit", 0): [("paint", [(8, -12, GOLD), (7, -11, GOLD), (7, -10, SHADE), (7, -9, GOLD), (8, -9, OUTLINE)]),
                 ("line", (6, -4), (5, 0), "front")],
    ("hit", 1): [("paint", [(10, -9, GOLD), (9, -8, SHADE), (8, -8, OUTLINE)]),
                 ("line", (7, -2), (5, 2), "front")],
    # death 1: still in her hand, upright
    ("dead", 0): [("line", (4, -1), (3, 2), "front")],
}


def line(p0, p1):
    """Squares from p0 to p1 (Bresenham)."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x1 > x0 else -1), (1 if y1 > y0 else -1)
    err, out = dx + dy, []
    while True:
        out.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return out
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def unit_step(p0, p1):
    """The finial's way: along the main axis, or diagonal when the shaft is within about 37 degrees of it."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    if abs(dx) >= abs(dy):
        return (1 if dx > 0 else -1), (0 if abs(dy) < 0.75 * abs(dx) else (1 if dy > 0 else -1))
    return (0 if abs(dx) < 0.75 * abs(dy) else (1 if dx > 0 else -1)), (1 if dy > 0 else -1)


class Canvas:
    """A frame with squares addressed from its pivot; grows when drawn past its edge."""

    def __init__(self, a):
        self.a = a.copy()

    def _rc(self, x, y):
        h, w = self.a.shape[:2]
        return h // 2 + y, w // 2 + x

    def get(self, x, y):
        r, c = self._rc(x, y)
        h, w = self.a.shape[:2]
        if 0 <= r < h and 0 <= c < w:
            return self.a[r, c]
        return np.zeros(4, np.uint8)

    def put(self, x, y, rgb):
        r, c = self._rc(x, y)
        h, w = self.a.shape[:2]
        if not (0 <= r < h and 0 <= c < w):
            py = max(0, -r, r - h + 1)
            px = max(0, -c, c - w + 1)
            self.a = np.pad(self.a, ((py, py), (px, px), (0, 0)))
            r, c = self._rc(x, y)
        self.a[r, c] = tuple(rgb) + (255,)


def clear(p):
    return p[3] == 0


def dark(p):
    return p[3] and N.G.lum(np.array([p[:3]], float))[0] < 60


def draw_line(cv, p0, p1, layer, cap=True):
    pts = line(p0, p1)
    d = unit_step(p0, p1)
    tip1 = (p1[0] + d[0], p1[1] + d[1])
    tip2 = (p1[0] + 2 * d[0], p1[1] + 2 * d[1])
    side = (1, 0) if abs(d[1]) >= abs(d[0]) else (0, 1)          # the outline squares across the shaft
    if d[0] and d[1]:
        side = (d[0], -d[1])
    bar = [(tip1[0] + side[0], tip1[1] + side[1]), (tip1[0] - side[0], tip1[1] - side[1])]
    body = {}
    for i, q in enumerate(pts):
        body[q] = SHAFT[i % len(SHAFT)]
    if cap:
        body[tip1] = LIGHT
        for q in bar:
            body[q] = SHADE
        body[tip2] = GOLD
    filled = set(body)
    ring = set()
    for (x, y) in filled:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in filled:
                ring.add(q)
    first = pts[0]
    for q, rgb in body.items():
        p = cv.get(*q)
        if q == first or layer == "front" or clear(p):
            if layer == "front" and tuple(p[:3]) in SKIN and p[3] and q != first:
                continue                                    # the hand stays over the shaft
            cv.put(*q, rgb)
    for q in ring:
        p = cv.get(*q)
        if clear(p) or (layer == "front" and not dark(p) and tuple(p[:3]) not in SKIN):
            cv.put(*q, OUTLINE)


def brows(a):
    """The row above both lids skin again where it is dark or grey (module docstring)."""
    b = a.copy()
    ys, xs = np.nonzero((b[..., :3] == EYE).all(-1) & (b[..., 3] > 0))
    blue = set(zip(ys.tolist(), xs.tolist()))
    for y, x in sorted(blue):
        if (y, x + 3) not in blue or y < 2:
            continue
        for c in range(x - 1, x + 4):
            p = b[y - 2, c]
            if p[3] and (dark(p) or tuple(p[:3]) in GREY):
                b[y - 2, c] = FOREHEAD + (255,)
    return b


def apply(a, ops):
    cv = Canvas(brows(a))
    for op in ops:
        if op[0] == "line":
            draw_line(cv, op[1], op[2], op[3])
        elif op[0] == "paint":
            for x, y, rgb in op[1]:
                cv.put(x, y, rgb)
    return cv.a


def frames_before_retouch():
    os.chdir(ROOT)
    sheet, _ = N.build("lux")
    N.neck_up("lux", sheet)
    return sheet


def symbols(colours):
    keys = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return {c: keys[i] for i, c in enumerate(sorted(colours))}


def retouch(sheet):
    """{tag: [[x, y, was, now], ...] per frame], palette} for every frame STAFF changes."""
    changes, colours = {}, set()
    for tag, frames in sheet.items():
        for k, (a, _) in enumerate(frames):
            ops = STAFF.get((tag, k), [])
            b = apply(a, ops)
            if b.shape == a.shape and (b == a).all():
                continue
            # compare on b's canvas (it may have grown)
            ph, pw = (b.shape[0] - a.shape[0]) // 2, (b.shape[1] - a.shape[1]) // 2
            a2 = np.pad(a, ((ph, ph), (pw, pw), (0, 0)))
            hh, hw = b.shape[0] // 2, b.shape[1] // 2
            for r, c in zip(*np.nonzero((a2 != b).any(-1))):
                was, now = a2[r, c], b[r, c]
                if was[3]:
                    colours.add(tuple(int(v) for v in was[:3]))
                if now[3]:
                    colours.add(tuple(int(v) for v in now[:3]))
                changes.setdefault(tag, {}).setdefault(k, []).append(
                    (int(c - hw), int(r - hh), None if not was[3] else tuple(int(v) for v in was[:3]),
                     None if not now[3] else tuple(int(v) for v in now[:3])))
    sym = symbols(colours)
    pal = {s: "#%02x%02x%02x" % c for c, s in sym.items()}
    out = {}
    for tag, frames in sheet.items():
        if tag not in changes:
            continue
        out[tag] = [[[x, y, "." if w is None else sym[w], "." if n is None else sym[n]]
                     for x, y, w, n in sorted(changes[tag].get(k, []), key=lambda q: (q[1], q[0]))]
                    for k in range(len(frames))]
    return pal, out


def preview(sheet, out_dir, z=8):
    os.makedirs(out_dir, exist_ok=True)
    for tag, frames in sheet.items():
        ks = [k for k in range(len(frames)) if not np.array_equal(apply(frames[k][0], STAFF.get((tag, k), [])),
                                                                     frames[k][0])]
        if not ks:
            continue
        tiles = []
        for k in ks:
            a = frames[k][0]
            b = apply(a, STAFF.get((tag, k), []))
            H = max(a.shape[0], b.shape[0]) + 4
            W = max(a.shape[1], b.shape[1]) + 4
            for x in (a, b):
                c = np.zeros((H, W, 4), np.uint8)
                c[...] = (92, 104, 88, 255)
                y0, x0 = H // 2 - x.shape[0] // 2, W // 2 - x.shape[1] // 2
                m = x[..., 3] > 0
                sub = c[y0:y0 + x.shape[0], x0:x0 + x.shape[1]]
                sub[m] = x[m]
                tiles.append(Image.fromarray(c).resize((W * z, H * z), Image.NEAREST))
        width = sum(t.width + 6 for t in tiles)
        img = Image.new("RGBA", (width, max(t.height for t in tiles)), (34, 34, 38, 255))
        x = 0
        for t in tiles:
            img.paste(t, (x, 0))
            x += t.width + 6
        img.save(os.path.join(out_dir, f"lux_retouch_{tag}.png"))


def dump(spec):
    """The table with one frame's squares a line (as the other retouch tables)."""
    lines = ["{", '  "about": ' + json.dumps(spec["about"], ensure_ascii=False) + ",",
             '  "palette": ' + json.dumps(spec["palette"]) + ",", '  "frames": {']
    tags = list(spec["frames"].items())
    for i, (tag, frames) in enumerate(tags):
        lines.append("    " + json.dumps(tag) + ": [")
        for k, px in enumerate(frames):
            lines.append("      " + json.dumps(px) + ("," if k < len(frames) - 1 else ""))
        lines.append("    ]" + ("," if i < len(tags) - 1 else ""))
    lines += ["  }", "}"]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preview", help="write before / after pictures of the changed frames to this folder")
    args = ap.parse_args()
    sheet = frames_before_retouch()
    if args.preview:
        preview(sheet, args.preview)
        return
    pal, frames = retouch(sheet)
    spec = {"about": ABOUT, "palette": pal, "frames": frames}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(spec))
    n = sum(len(p) for fr in frames.values() for p in fr)
    print(f"assets/source/native/lux_retouch.json: {n} squares in "
          f"{sum(1 for fr in frames.values() for p in fr if p)} frames")


if __name__ == "__main__":
    main()
