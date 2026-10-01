#!/usr/bin/env python3
"""Lee Sin's head: the idle's in every run frame, and no black line in front of the mouth (the user, 2026-10-01:
"盲僧走路时发现头上有残影", "这里不还是有残影？", "嘴巴前面还有黑线？").

    python tools/art/fix_leesin_head.py [--check]

The mouth: under the blindfold the design's face has a near-black pixel between the brown mouth and the outline, and
one more under it at the chin's front - with the outline a black line two pixels thick in front of the mouth, in every
frame that shows the face. They take the skin's colours (the lit skin in front of the mouth, the skin's shadow under
it, like their neighbours), in every frame where the face is the design's around them (MOUTH: what must be there).

The run: Codex pasted the design's face into every run frame (the blindfold and everything under it are the same pixels), but
over his own drawing of the head, which sat a pixel or two off in most frames and was never cleared: past the face's
front edge a strip of it stayed - a column of skin, the blindfold's red and a second outline in frames 2, 3 and 7, a
doubled outline in 1, 4, 6 and 8 - and behind the back of the skull one- and two-pixel specks of outline and dark red,
different in every frame. The four rows of bald crown over the blindfold were drawn anew in each frame too: the braid's
gold or brown clasp sat on the left of the crown in one frame and on its top in the next, dark specks and the braid's
hair crossed it. At the run's 115 ms a frame the head's edges flickered like an afterimage. So, in every run frame,
placed on that frame's blindfold:
  - the crown: the idle's (rows 2-5 over the blindfold: skin, its outline and the clasp, not the idle's braid hanging
    behind); a clasp the frame drew over it or behind it takes the braid's dark hair (it would be a second clasp);
  - the front: from the crown to the chin, whatever lies past the idle head's front edge goes (REACH columns);
  - the back: from the crown under the braid's knot to the jaw, the two columns behind the skull's back edge (the
    edge all eight frames share) are cleared.
The braid itself keeps swinging as drawn, and the shoulders under the jaw stay. After this the head, from the crown
to the chin, is the same pixels in all eight frames.
The edits are written as assets/source/native/leesin_retouch.json (import_native.py applies it to the cut frames,
before the breathing seam and the outline: x, y from the pivot, the colour expected there and the new one; a pixel
that changed since stops the import), so this only needs running again if the run strip changes.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import import_native as N  # noqa: E402
import strips as G  # noqa: E402

OUT = os.path.join(N.SRC, "leesin_retouch.json")
BAND = (0xD4, 0x22, 0x32)                                   # the blindfold's red: the face's place in every frame
SKULL = [(0xF3, 0xB2, 0x7C), (0xD7, 0x92, 0x60), (0x01, 0x00, 0x00), (0x03, 0x01, 0x06),   # skin, its outline
         (0xAB, 0x6F, 0x25), (0x7D, 0x4B, 0x23), (0xE0, 0xA5, 0x2F)]                          # the clasp's gold
CLASP = [(0xAB, 0x6F, 0x25), (0x7D, 0x4B, 0x23), (0xE0, 0xA5, 0x2F)]
HAIR = (0x32, 0x25, 0x2A)                                   # the braid's dark hair
ROWS = range(-5, -1)                                       # the crown: rows 5..2 over the blindfold's top row
COLS = range(-1, 11)                                       # from the blindfold's left column (the braid is further left)
KNOT = (range(-7, -3), range(-4, 6))                       # rows, columns where the frame's own clasp may sit
FRONT = range(-4, 6)                                       # the crown's second row to the chin
BACK = range(-4, 5)                                        # the crown under the knot to the jaw (the shoulders below)
REACH = 4                                                  # columns past the front edge (2 at most in the strip)
SKIN, SHADE, INK, LINE = (0xF3, 0xB2, 0x7C), (0xD7, 0x92, 0x60), (0x03, 0x01, 0x06), (0x01, 0x00, 0x00)
MOUTH = {(4, 5): (0xB3, 0x65, 0x3D), (4, 6): (0x7D, 0x4B, 0x23), (4, 8): LINE,      # (row, column) from the
         (5, 5): SHADE, (5, 7): LINE, (6, 5): INK}                                  # blindfold: the face around them
INKED = {(4, 7): SKIN, (5, 6): SHADE}                                              # the black line: its new colours


def band_at(a):
    m = (a[..., :3] == np.array(BAND, np.uint8)).all(-1) & (a[..., 3] > 0)
    ys, xs = np.nonzero(m)
    return (int(ys.min()), int(xs.min())) if len(ys) else (None, None)


def key(c):
    return "#%02X%02X%02X" % tuple(int(v) for v in c[:3])


def rgb(p):
    return tuple(int(v) for v in p[:3])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only say whether the file is what a run writes")
    o = ap.parse_args()
    sheet, _ = N.build("leesin")
    N.neck_up("leesin", sheet)
    idle = sheet["idle"][0][0]
    iy, ix = band_at(idle)
    crown = {}
    for dy in ROWS:
        for dx in COLS:
            p = idle[iy + dy, ix + dx]
            if p[3] and rgb(p) in SKULL:
                crown[dy, dx] = rgb(p)
    front = {dy: int(np.nonzero(idle[iy + dy, :, 3] > 0)[0].max()) - ix for dy in FRONT}
    work = {tag: [(a, a.copy(), *band_at(a), {}) for a, _ in frames] for tag, frames in sheet.items()}
    runs = work["run"]

    def put(run, dy, dx, new):
        a, b, y0, x0, edits = run
        r, c = y0 + dy, x0 + dx
        if not (0 <= r < b.shape[0] and 0 <= c < b.shape[1]):
            return
        now = (0, 0, 0, 0) if new is None else new + (255,)
        if tuple(int(v) for v in b[r, c]) == now or (new is None and not b[r, c, 3]):
            return
        b[r, c] = now
        edits[r, c] = True

    def opaque(run, dy, dx):
        _, b, y0, x0, _ = run
        r, c = y0 + dy, x0 + dx
        return 0 <= r < b.shape[0] and 0 <= c < b.shape[1] and b[r, c, 3] > 0

    for run in runs:
        for (dy, dx), c in crown.items():
            put(run, dy, dx, c)
        for dy in KNOT[0]:                                 # a clasp of the frame's own beside the idle's: dark hair
            for dx in KNOT[1]:
                if (dy, dx) in crown or not opaque(run, dy, dx):
                    continue
                b, y0, x0 = run[1], run[2], run[3]
                if rgb(b[y0 + dy, x0 + dx]) in CLASP:
                    put(run, dy, dx, HAIR)
        for dy in FRONT:                                   # past the idle head's front edge
            for dx in range(front[dy] + 1, front[dy] + REACH + 1):
                put(run, dy, dx, None)
            assert not any(opaque(run, dy, dx) for dx in range(front[dy] + REACH + 1, front[dy] + REACH + 3)), dy
    back = {}
    for dy in BACK:                                        # the skull's back edge: the span all eight frames share
        dx = 4
        while all(opaque(run, dy, dx - 1) for run in runs):
            dx -= 1
        back[dy] = dx
    for run in runs:
        for dy in BACK:
            for dx in (back[dy] - 2, back[dy] - 1):
                put(run, dy, dx, None)
    print("front edge", front, "back edge", back)
    for tag, frames in work.items():                       # the black line in front of the mouth, in every frame
        marks = ""
        for run in frames:
            b, y0, x0 = run[1], run[2], run[3]

            def at(dy, dx):
                r, c = y0 + dy, x0 + dx
                ok = 0 <= r < b.shape[0] and 0 <= c < b.shape[1] and b[r, c, 3] > 0
                return rgb(b[r, c]) if ok else None
            if y0 is None:
                marks += "-"                               # no face: turned away, lying
            elif all(at(*p) == c for p, c in MOUTH.items()) and all(at(*p) == INK for p in INKED):
                for (dy, dx), c in INKED.items():
                    put(run, dy, dx, c)
                marks += "+"
            else:
                marks += "?"
        print(f"mouth {tag:7s} {marks}")
    palette, spec_frames = {}, {}
    for tag, frames in work.items():
        lists = []
        for a, b, y0, x0, edits in frames:
            hh, hw = a.shape[0] // 2, a.shape[1] // 2
            out = []
            for r, c in sorted(edits):
                was = "." if not a[r, c, 3] else key(a[r, c])
                now = "." if not b[r, c, 3] else key(b[r, c])
                if was == now:
                    continue
                for s in (was, now):
                    if s != ".":
                        palette[s] = s
                out.append([c - hw, r - hh, was, now])
            lists.append(out)
        while lists and not lists[-1]:
            lists.pop()
        if lists:
            spec_frames[tag] = lists
            print(f"{tag:7s} pixels a frame {[len(x) for x in lists]}")
    frames = [x for lists in spec_frames.values() for x in lists]
    spec = {"palette": {k: k for k in sorted(palette)}, "frames": spec_frames}
    text = json.dumps(spec, indent=1) + "\n"
    if o.check:
        cur = open(G.lp(OUT), encoding="utf-8").read() if os.path.exists(G.lp(OUT)) else ""
        print("same" if cur == text else "DIFFERENT")
        sys.exit(0 if cur == text else 1)
    with open(G.lp(OUT), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(os.path.relpath(OUT, ROOT), sum(len(f) for f in frames), "pixels")


if __name__ == "__main__":
    main()
