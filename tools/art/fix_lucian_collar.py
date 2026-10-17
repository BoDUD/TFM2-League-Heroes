#!/usr/bin/env python3
"""Lucian: the collar between the redrawn back shoulder and his jaw (the user, 2026-10-01: "卢锡安开大时左边脸旁边有像素缺失").

    python tools/art/fix_lucian_collar.py [--check]

tools/art/lucian_shoulder.py put Codex's back shoulder into the 13 frames that aim both pistols forward (R 1-4,
Q 2-5, the double shot 2-6), but only where the shoulder is: between its top and the pasted head a crevice of empty
pixels stayed - a row under the jaw on the left of the face, two or three pixels between the shoulder's gold edge
and the cheek, and a pixel or two down the chest - so the background showed through beside his face. In the idle that
place is his coat's collar (its outline, the dark lining, the white collar, the gold trim down the chest). Every
pixel there that a frame leaves empty and the idle fills takes the idle's colour, placed by the iris like the head
(rows ROWS under the iris's lowest row, columns COLS from its middle; the raised arm further left in the idle is not
taken). The edits are written as assets/source/native/lucian_retouch.json (import_native.py applies it to the cut
frames, before the breathing seam and the outline: x, y from the pivot, the colour expected there and the new one; a
pixel that changed since stops the import), so this only needs running again if the strips change.
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

OUT = os.path.join(N.SRC, "lucian_retouch.json")
FRAMES = {"ult": range(0, 4), "skill": range(1, 5), "passive": range(1, 6)}   # the shoulder's 13 frames (0-based)
ROWS = range(1, 5)                                         # the jaw's last row to the chest
COLS = range(-9, -1)                                       # the collar's outline to the trim beside the jaw


def iris(a):
    m = (a[..., :3] == np.array(N.EYES["lucian"], np.uint8)).all(-1) & (a[..., 3] > 0)
    ys, xs = np.nonzero(m)
    return int(ys.max()), int(round(xs.mean()))


def key(p):
    return "#%02X%02X%02X" % tuple(int(v) for v in p[:3])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only say whether the file is what a run writes")
    o = ap.parse_args()
    sheet, _ = N.build("lucian")
    N.neck_up("lucian", sheet)
    idle = sheet["idle"][0][0]
    iy, ix = iris(idle)
    palette, spec = {}, {}
    for tag, ks in FRAMES.items():
        lists = []
        for k in range(max(ks) + 1):
            edits = []
            if k in ks:
                a = sheet[tag][k][0]
                y0, x0 = iris(a)
                hh, hw = a.shape[0] // 2, a.shape[1] // 2
                for dy in ROWS:
                    for dx in COLS:
                        p, q = a[y0 + dy, x0 + dx], idle[iy + dy, ix + dx]
                        if p[3] or not q[3]:
                            continue
                        palette[key(q)] = key(q)
                        edits.append([x0 + dx - hw, y0 + dy - hh, ".", key(q)])
            lists.append(edits)
        spec[tag] = lists
        print(f"{tag:8s} pixels a frame {[len(e) for e in lists]}")
    text = json.dumps({"palette": dict(sorted(palette.items())), "frames": spec}, indent=1) + "\n"
    if o.check:
        cur = open(G.lp(OUT), encoding="utf-8").read() if os.path.exists(G.lp(OUT)) else ""
        print("same" if cur == text else "DIFFERENT")
        sys.exit(0 if cur == text else 1)
    with open(G.lp(OUT), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(os.path.relpath(OUT, ROOT), sum(len(e) for v in spec.values() for e in v), "pixels")


if __name__ == "__main__":
    main()
