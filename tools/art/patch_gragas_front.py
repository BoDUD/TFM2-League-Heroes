"""Gragas front: the hand patches on the 2:1 first pass (design/front_auto.txt -> design/front.txt): the face (brows, eyes
with a white and a pupil, nose, mouth), the keg lid (iron ring, wood, the square cork), the X scar, one hole, the beard
tips on the silhouette, then single beard squares unlike all four neighbours take their neighbours' colour."""
import sys
sys.path.insert(0, r"D:\TFM2-Workshop\repo\.claude\worktrees\magical-wescoff-894eec\tools\art")
import numpy as np
import trace_gragas as T
D = T.DESIGN  # tools/art/trace_gragas.py --auto writes front_auto.txt; this writes front.txt
rows = [list(r) for r in open(D + "/front_auto.txt").read().split("\n") if r]
EDITS = [
    (5, 14, "kicvtiddtddimd.."),
    (6, 14, "qmctrtxatxarci.."),
    (7, 14, "miqqmitvwrtrqd.."),
    (8, 14, "cqqmmmqmtrmqqqq."),
    (9, 14, "ciimmqqqdaadqdid"),
    (10, 14, "prrdmqqirrqdiqd."),
    # the keg's lid: outline, iron ring, wood, the square cork in the middle
    (4, 0, "..aannn"),
    (5, 0, ".anjhhn"),
    (6, 0, "anjklln"),
    (7, 0, "anhkupn"),
    (8, 0, "anhkvun"),
    (9, 0, "anjklln"),
    (10, 0, "anjhkhn"),
    (11, 0, ".anjhjn"),
    (12, 0, ".annnna"),
    (13, 0, "..aaaaa"),
    (14, 0, "....aaa"),
    (34, 8, "a"),  # a hole between the shorts and the near thigh
    (5, 26, "i"),
    (8, 28, "d"),  # beard tips on the silhouette get a dark edge
    # the X scar on the belly
    (23, 17, "v"),
    (24, 17, "ovo"),
    (25, 17, "vov"),
    (26, 17, "ovo"),
]
for r, c, s in EDITS:
    for k, ch in enumerate(s):
        rows[r][c + k] = ch
BEARD = set("cdimq")
def despeckle(rows, r0, r1, c0, c1):
    n = 0
    for _ in range(2):
        g = [row[:] for row in rows]
        for r in range(r0, r1):
            for c in range(c0, c1):
                ch = g[r][c]
                if ch not in BEARD:
                    continue
                nb = [g[r + dy][c + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                if all(x in BEARD for x in nb) and ch not in nb:
                    vals = [x for x in nb]
                    best = max(set(vals), key=vals.count)
                    rows[r][c] = best; n += 1
    return n
print("despeckled", despeckle(rows, 10, 23, 14, 32))
open(D + "/front.txt", "w", newline="\n").write("\n".join("".join(r) for r in rows) + "\n")
