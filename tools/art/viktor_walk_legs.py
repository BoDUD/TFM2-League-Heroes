#!/usr/bin/env python3
"""Viktor's walk legs, put together per frame from the design's own leg rows (run v14; the user, 2026-10-10, after
a dozen re-poses: 「我自己逐帧画腿」「有点审美啊」, then at the first drawn legs - limbs two squares wide drawn from
hip, knee and ankle points: 「这腿我怎么看的还这么抽象」).

The design's leg is twelve rows of one-row pieces: the hip plate (rows 88-90, gold-trimmed), the grey thigh (91-92),
the navy knee pad (93), a one-square dark shin (94), the orange-and-gold ankle band (95), the dark ankle and the
ten-square boot (96-99). Lines drawn between joints made thin sticks, and moving blocks of rows a column apart broke
the knee (the user's crop: 「你是看不到这里有问题吗」). Here every row is the design's own, whole, and a pose moves
them at the two places where the leg can bend without a step in its outline:

- the thigh and the knee move `s1` columns under the hip plate (the plate hangs over that joint, as in the idle);
- the shin, the band and the boot move a further `s2` (the one-square shin stays under the three-square knee pad);
- a foot `lift` rows up leaves out that many thigh rows (the thigh swings forward and shortens), the knee pushed a
  column forward; a body sunk a row (BOB) leaves out one more.

The far leg is the near one mirrored about its shin (toes outward, the user's pick B), in its own lane FAR_SHIN
(the user's pick C). Its foot keeps to -1..+2 (further back its shin goes behind the staff) and the near one to
-2..+3 (2026-10-21, the user: 「维克托的走路也可以改改」, of a bigger stride on these same rows or a redone PPU
Viktor 「在现有基础上加大步子」 - it had been -1..+1 and -1..+2, a shuffle beside Jarvan's and Jax's new runs); a foot
passing the other goes up 2 rows, so the boots meet only as one plants behind the other.
"""
import numpy as np

PLATE = (88, 89, 90)        # the hip plate: rides with the body
THIGH = (91, 92)            # left out from the top as the foot lifts / the body sinks
KNEE, SHIN, BAND = 93, 94, 95
BOOT = (96, 97, 98, 99)     # the dark ankle row, the boot and its sole
NEAR_SHIN, FAR_SHIN = 69, 59
# per phase (s1, s2, lift); frame k plays the near leg's phase k and the far leg's phase k + 4. The near foot lands
# three ahead and goes back 1-2 columns a frame to -2 (phases 0-3), comes up behind (4), passes two rows up with the knee
# forward (5, 6) and reaches (7); the far foot the same in -1..+2, landing at +1 (at +2 its boot met the near one
# lifted behind it - one slab of navy - in frame 5) and a frame still where it lands
NEAR = [(1, 2, 0), (1, 0, 0), (0, -1, 0), (0, -2, 0), (0, -2, 1), (0, -1, 2), (1, 0, 2), (1, 2, 1)]
FAR = [(1, 0, 0), (0, 1, 0), (0, 0, 0), (0, -1, 0), (0, -1, 1), (0, 0, 2), (1, 0, 2), (1, 1, 1)]
BOB = [1, 0, 0, 0, 1, 0, 0, 0]  # the body and the plates a row down as a foot lands


def far_part(near):
    """The near leg mirrored about its shin and set in the far lane: column x -> NEAR_SHIN + FAR_SHIN - x."""
    out = np.zeros_like(near)
    ys, xs = np.nonzero(near[..., 3])
    nx = NEAR_SHIN + FAR_SHIN - xs
    ok = (nx >= 0) & (nx < near.shape[1])
    out[ys[ok], nx[ok]] = near[ys[ok], xs[ok]]
    return out


def leg(part, pose, bob):
    """One leg alone on a canvas: the part's rows stacked down from the plate as `pose` = (s1, s2, lift) sets them."""
    s1, s2, lift = pose
    keep = len(THIGH) - bob - lift
    assert keep >= 0, (pose, bob)
    out = np.zeros_like(part)
    y = PLATE[0] + bob
    for r, dx in [(r, 0) for r in PLATE] + [(r, s1) for r in THIGH[len(THIGH) - keep:]] + [(KNEE, s1)] + \
            [(r, s1 + s2) for r in (SHIN, BAND) + BOOT]:
        row = np.roll(part[r], dx, axis=0)
        m = row[:, 3] > 0
        out[y][m] = row[m]
        y += 1
    assert y - 1 == BOOT[-1] - lift
    return out


def foot(side, k):
    """(columns forward, rows up) of a leg's foot in frame k."""
    s1, s2, lift = NEAR[k % 8] if side == "near" else FAR[(k + 4) % 8]
    return s1 + s2, lift
