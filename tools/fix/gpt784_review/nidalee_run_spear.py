"""league_nidalee's run, the spear on her near shoulder in every frame (the user, 2026-11-19: 「豹女跑步保持这个姿势就行了
我指出的问题是枪看起来在脸的另外一边」). GPT's shoulder-carry run (0be7fa6ab, kept on #784 until bdbda7d47 swapped it for a
spear held out in front - not wanted) draws the shaft across her neck in front in frames 0-3, but in frames 4-7 a span
of 5-9 squares right of her gripping hand is covered by her fur collar and hair: the shaft seems to pass behind her
head. Here:

1. `--from REV` puts that run back: the run's hd_, 1x and lo_ frames of REV's sheet in the sheet (rects of their own);
2. in each dense frame, on each shaft row (the rows where a long brown run lies left of her hand), the covered span
   between her hand's right edge and where the shaft shows again is painted with that row's first shaft colour past the
   span, and a light square just over / under it takes the darkest colour beside it (the shaft's own outline, as over
   her neck in frames 0-3);
3. 1x and lo_ derived again from the dense frames (tools/fix/xinzhao_galio_1119/sheetkit.py), the strips rewritten.

    python tools/fix/gpt784_review/nidalee_run_spear.py --from 02b3aa862
    python tools/fix/gpt784_review/nidalee_run_spear.py --check
"""
import io
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

STEM = "league/champions/league_nidalee"


def shaft_px(p):
    r, g, b = int(p[0]), int(p[1]), int(p[2])
    return p[3] > 0 and r > 90 and r < 215 and r - b > 50 and g < 130


def skin_px(p):
    r, g, b = int(p[0]), int(p[1]), int(p[2])
    return p[3] > 0 and r > 200 and 120 <= g <= 195 and 70 <= b <= 165 and 45 <= r - b <= 150


# the covered span right of her hand, per dense run frame (read off the 0be7fa6ab frames on a grid: her hand's skin ends
# at the first column, the shaft shows clean again after the last); frames 0-3 draw it across her neck already
SPANS = {4: (60, 74), 5: (57, 62), 6: (61, 67), 7: (57, 61)}


def shaft_rows(c):
    h = c.shape[0]
    return [r for r in range(20, min(h, 45)) if sum(shaft_px(c[r, x]) for x in range(18, 36)) >= 6]


def spans(c, i):
    """[(row, x0, x1, colour)]: on each shaft row, the span to paint and the row's commonest shaft colour just past it"""
    if i not in SPANS:
        return [], []
    x0, x1 = SPANS[i]
    rows = shaft_rows(c)
    out = []
    for r in rows:
        if all(shaft_px(c[r, x]) for x in range(x0, x1 + 1)):
            continue
        cols = [tuple(int(v) for v in c[r, x]) for x in range(x1 + 1, min(c.shape[1], x1 + 12)) if shaft_px(c[r, x])]
        if not cols:
            continue
        col = max(set(cols), key=cols.count)
        out.append((r, x0, x1, np.array(col, np.uint8)))
    return out, rows


def paint(c, i):
    new = c.copy()
    sp, rows = spans(c, i)
    for r, x0, x1, col in sp:
        for x in range(x0, x1 + 1):
            new[r, x] = col
    if sp:
        top, bot = min(s[0] for s in sp), max(s[0] for s in sp)
        for r in (top - 1, bot + 1):
            for _, x0, x1, _ in sp:
                for x in range(x0, x1 + 1):
                    p = new[r, x]
                    if p[3] > 0 and int(p[0]) + int(p[1]) + int(p[2]) > 360:
                        nb = [new[rr, xx] for rr in (r - 1, r, r + 1) for xx in (x - 1, x, x + 1)
                              if (rr, xx) != (r, x) and new[rr, xx, 3] > 0]
                        new[r, x] = min(nb, key=lambda q: int(q[0]) + int(q[1]) + int(q[2]))
    return new, sp


def restore(k, rev):
    def show(path):
        return subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout
    sheet = np.asarray(Image.open(io.BytesIO(show(STEM + "#sheet.png"))).convert("RGBA"))
    an = json.loads(show(STEM + "#anim.fanim").decode("utf-8-sig"))["anims"]
    for pre in ("hd_", "", "lo_"):
        for i, f in enumerate(an[pre + "run"]["frames"]):
            d = f["data"]
            x, y, w, h = (int(round(d[q])) for q in ("x", "y", "w", "h"))
            k.put(pre + "run", i, sheet[y:y + h, x:x + w].copy())
    k.save()


def main():
    k = Kit(ROOT, "league", "nidalee")
    n = len(k.anims["hd_run"]["frames"])
    if "--check" in sys.argv:
        bad = sum(1 for i in range(n) if spans(k.cell("hd_run", i), i)[0])
        bad += sum(1 for i in range(n) if not np.array_equal(k.lo_of(k.cell("run", i).shape[:2], k.cell("hd_run", i)), k.cell("lo_run", i)))
        print("nidalee run spear: OK" if not bad else f"nidalee run spear: {bad} frames not as this tool leaves them")
        sys.exit(1 if bad else 0)
    if "--from" in sys.argv:
        restore(k, sys.argv[sys.argv.index("--from") + 1])
        k = Kit(ROOT, "league", "nidalee")
    for i in range(n):
        new, sp = paint(k.cell("hd_run", i), i)
        print(f"run[{i}]: " + (", ".join(f"row {r} x {a}-{b}" for r, a, b, _ in sp) or "shaft already in front"))
        k.put("hd_run", i, new)
    for i in range(n):
        k.derive("run", i)
    k.save()
    k.strip("run")


if __name__ == "__main__":
    main()
