#!/usr/bin/env python3
"""LeBlanc's run legs drawn again: a crossing stride instead of Codex's one wide stance in all eight frames.

The user: "走路没有交叉步 平行走路？" - Codex's run kept the left leg behind and the right one ahead in every frame,
so she slid along. Here everything under the gown's hem in the legs' columns is cleared and two legs are drawn on
joints (hip, knee, ankle) per frame: 1 the near leg ahead and the far one behind, both on the ground; 2 the back foot
lifting; 3 passing - the near leg under her, the far one bent, its foot off the ground, crossing it; 4 the far leg
swinging ahead; 5-8 the same with the legs swapped. Both legs are one material, Codex's run boots (dark wine, a gold
band under the knee, the gold toe, the red heel), the near one drawn over the far one so its outline cuts it; feet at
most 12 squares apart (the stride rule for a 46-row hero). A library for fix_leblanc_strips.py.
"""
import numpy as np

OUTLINE = (0x06, 0x02, 0x12)
BOOT = (0x39, 0x0C, 0x20)
SHADE = (0x2B, 0x01, 0x0E)
GOLD = (0xB8, 0x66, 0x2B)
TOE = (0xF9, 0xB9, 0x54)
HEEL = (0x7F, 0x00, 0x15)
HEM = 60                         # the first row under the gown where the legs show (pivot row 56 + 4)
SOLES = 67                       # pivot + 11
CLEAR = (-14, 17)                # columns from the body's middle that are cleared under the hem
MID = -3                         # the body's middle under the gown: pivot column + MID
# per frame: (near leg, far leg), each (hip, knee, ankle) columns from the middle and how many rows the foot is lifted
POSES = [((1, 3, 5, 0), (-1, -3, -5, 0)),       # 1 contact: near ahead, far behind
         ((1, 2, 4, 0), (-1, -3, -5, 1)),       # 2 the back foot lifts
         ((1, 1, 1, 0), (-1, 1, -2, 3)),        # 3 passing: near under her, far bent, its foot up behind
         ((1, 0, -1, 0), (-1, 3, 3, 1)),        # 4 near pushes back, far swings ahead
         ((-1, -3, -5, 0), (1, 3, 5, 0)),       # 5 contact: far ahead, near behind
         ((-1, -3, -5, 1), (1, 2, 4, 0)),       # 6
         ((-1, 1, -2, 3), (1, 1, 1, 0)),        # 7 passing: near bent, far under her
         ((-1, 3, 3, 1), (1, 0, -1, 0))]        # 8
KNEE = 3                         # rows under the hem to the knee (straight leg)


def leg(canvas, mid, hip, knee, ankle, lift):
    """One leg on the canvas: a boot two squares wide in outline from the hem down to the ankle, bending at the
    knee, the foot (gold toe ahead, red heel) on the ankle, `lift` rows off the ground."""
    sole = SOLES - lift
    ay = sole - 1                                  # the foot's row
    ky = HEM + KNEE - (lift + 1) // 2
    pts = []
    for y in range(HEM, ay):
        if y <= ky:
            t = (y - HEM) / max(ky - HEM, 1)
            x = hip + (knee - hip) * t
        else:
            t = (y - ky) / max(ay - ky, 1)
            x = knee + (ankle - knee) * t
        pts.append((y, mid + int(round(x))))
    put = []
    for y, x in pts:
        put += [(y, x - 1, OUTLINE), (y, x, BOOT), (y, x + 1, SHADE), (y, x + 2, OUTLINE)]
    gy = ky + 1 if ky + 1 < ay else ky              # the gold band under the knee
    for y, x in pts:
        if y == gy:
            put += [(y, x, GOLD), (y, x + 1, GOLD)]
    x = pts[-1][1] if pts else mid + ankle
    put += [(ay, x - 1, OUTLINE), (ay, x, HEEL), (ay, x + 1, BOOT), (ay, x + 2, TOE), (ay, x + 3, OUTLINE),
            (sole, x - 1, OUTLINE), (sole, x, OUTLINE), (sole, x + 1, OUTLINE), (sole, x + 2, OUTLINE),
            (sole, x + 3, OUTLINE)]
    # the outline first, the colours over it: a slanted leg's rows overlap by a square
    for y, xx, c in sorted(put, key=lambda p: p[2] != OUTLINE):
        if 0 <= y < canvas.shape[0] and 0 <= xx < canvas.shape[1]:
            if c == OUTLINE and canvas[y, xx, 3] and tuple(int(v) for v in canvas[y, xx, :3]) != OUTLINE \
                    and (y, xx) in own:
                continue
            canvas[y, xx, :3] = c
            canvas[y, xx, 3] = 255
            if c != OUTLINE:
                own.add((y, xx))


own = set()


def redraw(f, pivot, k):
    """Frame k (1-based) of the run with its legs drawn again."""
    global own
    g = f.copy()
    mid = pivot[0] + MID
    g[HEM:SOLES + 1, max(0, mid + CLEAR[0]):mid + CLEAR[1] + 1] = 0
    near, far = POSES[k - 1]
    layer = np.zeros_like(g)
    own = set()
    leg(layer, mid, *far)
    far_layer = layer.copy()
    layer = np.zeros_like(g)
    own = set()
    leg(layer, mid, *near)
    m = far_layer[..., 3] > 0
    g[m] = far_layer[m]
    m = layer[..., 3] > 0
    g[m] = layer[m]
    return g
