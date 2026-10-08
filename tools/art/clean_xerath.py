"""(tools/art/import_native.py TIDY; the user, 2026-10-08: 「顺便把泽拉斯脚上的黑边清理干净」)
Xerath's (league_xerath) leg tips: the near spike trailed a 1-square stalk of bare outline two or three rows under
its last coloured square, the far one a 2-square block of outline beside its tip. Near the soles an outline square
with no coloured square beside it (4 ways) goes, again until none is left; every tip then ends on one outline square
right under it. Nothing moves: his body, the baked effects and the kit's offsets keep their places (the spikes now end
two rows over the ground - he floats, as in League).

    tidy_shrunk(tag, k, frame) -> frame   (import_native, after SHRINK: the approved shrink's lines stay as they were,
                                           and no removed row can take a tip's cap afterwards)
        frame: HxWx4 uint8, odd size, pivot = centre pixel, soles row = centre + 11.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402

ZONE = 10            # rows above the soles row the clean-up looks at (his legs)
OUTLINE = (0x04, 0x02, 0x08)
STANDING = 24        # a figure at least this many rows tall stands on his tips


def _ink(a):
    return (a[..., 3] > 0) & (a[..., :3] == OUTLINE).all(-1)


def _clean(a, soles):
    zone = np.zeros(a.shape[:2], bool)
    zone[max(0, soles - ZONE):soles + 1] = True
    while True:
        op = a[..., 3] > 0
        ink = _ink(a)
        col = op & ~ink
        near = np.zeros_like(col)
        near[1:] |= col[:-1]
        near[:-1] |= col[1:]
        near[:, 1:] |= col[:, :-1]
        near[:, :-1] |= col[:, 1:]
        gone = ink & ~near & zone
        if not gone.any():
            break
        a[gone] = 0
    closed, _, _ = strips.complete_outline(a.copy(), color=OUTLINE, feet=soles)
    a[zone] = closed[zone]                       # only by the feet: the rest of the frame stays as it was
    # complete_outline leaves a dark tip open (the far spike's block sat beside its tip, not under it): one outline
    # square under every coloured square that has nothing under it
    op = a[..., 3] > 0
    tip = op & ~_ink(a) & zone
    for y, x in zip(*np.nonzero(tip)):
        if y + 1 <= soles and not op[y + 1, x]:
            a[y + 1, x] = OUTLINE + (255,)
    return a


def tidy_shrunk(tag, k, frame):
    a = frame.copy()
    op = a[..., 3] > 0
    if not op.any():
        return a
    ys = np.nonzero(op.any(1))[0]
    if ys.max() - ys.min() < STANDING:            # lying (his death): the whole body is by the ground, nothing done
        return a
    return _clean(a, a.shape[0] // 2 + 11)
