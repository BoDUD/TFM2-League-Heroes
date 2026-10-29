#!/usr/bin/env python3
"""Taric's actions from Codex's pixel rig (assets/source/taric/hd/casts: tools/art/pack_taric_actions.py's pack,
delivered 2026-10-29, Documents/Codex/2026-10-29/new-chat-7/outputs/taric_actions_done.zip), rigged again and posed
on the old frames.

Codex drew no whole frames this time: after its generated tries broke his arms and the hammer (raw/rejected-ai, left
out), the user had it cut the approved design (hd/design.png) into parts - the head, the torso with the sash, the two
pauldrons, the cape, the gauntleted near arm, the bare far arm, the legs, the one hammer (casts/rig-parts) - and set
them frame by frame on joints (casts/source/pixel_rig.py, its poses in casts/rig-poses.json, its frames in
casts/logical): every part the design's own pixels, turned whole, never scaled. Its frames bent the knees backwards,
left the boots flat whatever the shins did, carried a ghost of the near thigh in the torso and hid the legs under a
cape drawn over the far one, turned the parts pixel by pixel (their edges broke), kept the Bravado smash and E's thrust
against his chest and stood ~6 squares left of the old frames (the user, 2026-10-29: 「怎么腿有点变形了 你好好改」).

So here: its parts cut again (each leg as thigh, shin with the knee guard and boot; each part its own pixels only;
_masks), turned RotSprite's way (Scale2x three times, turned and sampled back: x8, paste), the knees bending only
backwards and the lifted boots turning with the shins (render, chain), the cape behind both legs and swept back by
shear, the standing pose the design pixel for pixel (--check); and every frame posed again (POSES) on the old frame
laid under it (--tune). The frames come out on the design's squares: placed() gives each one's picture and top-left on
the design's grid, the design's pivot (his feet's middle, OLD_CENTRE right of it) on the old frame's pivot (its centre;
the soles OLD_SOLES under it).

    python tools/art/casts_taric_hd.py --check
    python tools/art/casts_taric_hd.py --review DIR    # every tag placed, at 2x, the design first
    python tools/art/casts_taric_hd.py --tune DIR [--tags run ...]   # each frame: the old at PPU | the new | both
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack_taric_actions as PK  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "taric", "hd")
TAGS = PK.TAGS
SRC = Image.open(os.path.join(HD, "design.png")).convert("RGBA")
D0 = np.asarray(SRC)
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1       # the row under the design's soles
PPU = D0.shape[0] / 40          # 62 rows over his 1x 40 (design_taric_hd)
OLD_CENTRE = 3.5                # the old idle: its frame's centre 3.5 pixels right of its feet's middle (23.5 / 20)
OLD = PK.old_frames(os.path.join(HD, "old", "sheet.png"), os.path.join(HD, "old", "anim.fanim"))


def shoes_mid(d):
    """The middle of his two shoes: the outer edges of what stands in the 3 rows over his lowest (casts_draven_hd's)."""
    op = d[..., 3] > 0
    low = int(np.nonzero(op.any(1))[0].max())
    xs = np.nonzero(op[low - 3:low + 1].any(0))[0]
    return (xs.min() + xs.max() + 1) / 2.0


# --- the parts ------------------------------------------------------------------------------------------------------
OX, OY = 40, 44                 # the canvas's design origin: room over his head and out both sides
SIZE = (48 + 2 * OX, GROUND + OY + 4)
NAVY = [(1, 22, 160), (4, 12, 107), (2, 17, 134), (12, 9, 74)]     # the cape's blues (the sash has them too)
ARR = np.array(SRC)
ARR[ARR[..., 3] == 0] = 0
YY, XX = np.mgrid[:ARR.shape[0], :ARR.shape[1]]
OPAQUE = ARR[..., 3] > 0
IS_NAVY = np.zeros(OPAQUE.shape, bool)
for _c in NAVY:
    IS_NAVY |= OPAQUE & (ARR[..., :3] == _c).all(-1) & (YY >= 25)       # (over row 25 they are the pauldrons' gems)
DARK = OPAQUE & (ARR[..., :3].max(-1) < 45)                             # the outline's colours
SASH = (YY >= 37) & (XX >= 25) & (XX <= 32)


def poly(points):
    m = Image.new("L", SRC.size)
    ImageDraw.Draw(m).polygon(points, fill=255)
    return np.array(m) > 0


def spans(rows):
    """A mask from {(first row, end row): (first x, end x)}."""
    m = np.zeros(OPAQUE.shape, bool)
    for (y0, y1), (x0, x1) in rows.items():
        m[y0:y1, x0:x1] = True
    return m


def _masks():
    """{part: mask}: Codex's polygons for the head, torso, pauldrons, arms and hammer, the legs cut by rows; the
    torso without what stands beside the sash under the belt, no part but the sash with the cape's navy; then each
    pixel left out (mostly outline) given to the part most of its 8 neighbours' COLOURS are in (the cape's navy
    counting for the cape), so an outline goes with what it outlines; one with outline round it alone, to the part
    most of its neighbours are in; what is still left to the cape."""
    hammer = spans({(38, 41): (9, 12), (41, 42): (3, 12), (42, 43): (2, 12), (43, 44): (1, 12), (44, 48): (0, 12),
                    (48, 54): (0, 14), (54, 55): (2, 13), (55, 56): (4, 13), (56, 57): (4, 12), (57, 58): (4, 11),
                    (58, 59): (4, 10), (59, 60): (4, 9), (60, 61): (4, 7)})
    m = {
        "head": poly([(24, 0), (30, 0), (34, 4), (37, 7), (35, 11), (35, 15), (32, 18), (29, 19), (25, 18), (23, 16),
                      (20, 17), (16, 15), (12, 16), (8, 16), (8, 13), (15, 10), (16, 6), (21, 2)]),
        "torso": poly([(20, 17), (27, 18), (32, 18), (37, 21), (38, 27), (36, 32), (37, 36), (33, 40), (32, 49),
                       (30, 56), (24, 57), (21, 51), (21, 43), (16, 39), (17, 31), (18, 25)])
        & ~((YY >= 37) & ~SASH),
        "near_shoulder": poly([(4, 21), (8, 17), (13, 15), (19, 16), (20, 18), (19, 21), (17, 24), (17, 25),
                               (14, 25), (12, 23), (8, 24), (5, 24)]),
        "far_shoulder": poly([(30, 16), (34, 15), (39, 16), (41, 18), (42, 20), (44, 23), (43, 25), (40, 26),
                              (38, 23), (35, 21), (33, 20), (31, 19)]),
        "near_upper": poly([(10, 23), (15, 23), (18, 26), (17, 29), (14, 32), (10, 33), (7, 31), (7, 28), (9, 26)]),
        "near_lower": poly([(8, 29), (13, 29), (15, 32), (14, 35), (12, 38), (12, 39), (8, 39), (6, 37), (7, 33)]),
        "near_hand": poly([(8, 36), (12, 36), (12, 39), (11, 41), (8, 41), (8, 39), (7, 38)]),
        "bare_upper": poly([(37, 27), (40, 27), (42, 29), (43, 33), (42, 35), (39, 35), (37, 32), (36, 30)]),
        "bare_lower": poly([(39, 32), (43, 32), (45, 36), (46, 39), (44, 41), (41, 39), (40, 36)]),
        "bare_hand": poly([(43, 38), (46, 38), (47, 40), (47, 43), (45, 45), (43, 45), (41, 43), (42, 41),
                           (42, 39)]),
        "near_thigh": spans({(37, 46): (16, 25)}),
        "near_shin": spans({(44, 53): (14, 25), (53, 55): (14, 23)}),
        "near_boot": spans({(53, 54): (15, 23), (54, 55): (14, 23), (55, 56): (13, 23), (56, 57): (12, 23),
                            (57, 58): (13, 23), (58, 59): (12, 23), (59, 62): (11, 23)}),
        "far_thigh": spans({(37, 47): (32, 38)}),
        "far_shin": spans({(45, 56): (32, 40)}),
        "far_boot": spans({(53, 57): (31, 40), (57, 62): (31, 43)}),
        "weapon": hammer,
    }
    for n in m:
        m[n] &= OPAQUE & ~(IS_NAVY & ~(SASH if n == "torso" else np.zeros_like(SASH)))
        if n != "weapon":
            m[n] &= ~hammer
    m["sash"] = m["torso"] & (YY >= 38)
    m["torso"] &= ~m["sash"]
    m["cape"] = IS_NAVY & ~SASH
    names = list(m)
    for colours in (True, False):
        while True:
            cov = np.zeros(OPAQUE.shape, bool)
            for v in m.values():
                cov |= v
            grown = 0
            for y, x in zip(*np.nonzero(OPAQUE & ~cov)):
                win = (slice(max(y - 1, 0), y + 2), slice(max(x - 1, 0), x + 2))
                votes = [int((m[n][win] & ~DARK[win]).sum() if colours else m[n][win].sum()) for n in names]
                if max(votes):
                    m[names[int(np.argmax(votes))]][y, x] = True
                    grown += 1
            if not grown:
                break
    cov = np.zeros(OPAQUE.shape, bool)
    for n, v in m.items():
        if n != "cape":
            cov |= v
    m["cape"] |= OPAQUE & ~cov
    return m


MASKS = _masks()


def _cape(own):
    """The cape whole behind him (Codex's contour of it: its outline, its navy; inside the design's outline) under its
    own pixels."""
    back = Image.new("RGBA", SRC.size)
    d = ImageDraw.Draw(back)
    d.polygon([(17, 26), (36, 26), (39, 35), (42, 43), (43, 49), (47, 55), (45, 57), (39, 56), (33, 56), (27, 57),
               (21, 56), (17, 53), (13, 47), (13, 39)], fill=(22, 2, 22, 255))
    d.polygon([(18, 27), (35, 27), (38, 36), (41, 44), (42, 50), (45, 55), (40, 55), (33, 55), (27, 56), (21, 55),
               (18, 52), (14, 46), (14, 39)], fill=(12, 9, 74, 255))
    a = np.array(back)
    a[~OPAQUE] = 0
    a[own] = ARR[own]
    return a


def _parts():
    """{part: RGBA}; Codex's head clean-up (the near pauldron's pixels under the hair, below row 14 left of 22) moves
    those pixels to the near pauldron."""
    out = {}
    for n, m in MASKS.items():
        a = np.zeros_like(ARR)
        a[m] = ARR[m]
        out[n] = a
    out["cape"] = _cape(MASKS["cape"])
    h = out["head"]
    for y in range(14, h.shape[0]):
        for x in range(22):
            r, g, b = map(int, h[y, x, :3])
            if h[y, x, 3] and not (max(r, g, b) < 45 or (r > g * 1.2 and r > b * .8)):
                out["near_shoulder"][y, x] = h[y, x]
                h[y, x] = 0
    return out


def scale2x(a):
    """Scale2x (EPX) of a uint32 picture."""
    p = np.pad(a, 1, mode="edge")
    up, rt, lf, dn = p[:-2, 1:-1], p[1:-1, 2:], p[1:-1, :-2], p[2:, 1:-1]
    out = np.empty((a.shape[0] * 2, a.shape[1] * 2), a.dtype)
    out[0::2, 0::2] = np.where((lf == up) & (lf != dn) & (up != rt), up, a)
    out[0::2, 1::2] = np.where((up == rt) & (up != lf) & (rt != dn), rt, a)
    out[1::2, 0::2] = np.where((dn == lf) & (dn != rt) & (lf != up), lf, a)
    out[1::2, 1::2] = np.where((rt == dn) & (rt != up) & (dn != lf), dn, a)
    return out


def x8(a):
    """The part at 8x by Scale2x three times (RotSprite's way): turned there and sampled back at 1x, its edges and
    lines stay whole."""
    u = np.ascontiguousarray(a).view(np.uint32)[..., 0]
    for _ in range(3):
        u = scale2x(u)
    return Image.fromarray(np.ascontiguousarray(u).view(np.uint8).reshape(u.shape + (4,)), "RGBA")


PARTS = _parts()
PARTS8 = {n: x8(a) for n, a in PARTS.items()}
# the design's pivot: his boots' middle (the hammer's foot, as low as they, left out: it put the middle 3.5 squares
# left and the frames as far right of the old ones), OLD_CENTRE right of it - where the design lies best over his old
# idle_base too (its overlap's peak, 0.88)
_BOOTS = D0.copy()
_BOOTS[MASKS["weapon"]] = 0
PIVOT = int(round(shoes_mid(_BOOTS) + OLD_CENTRE * PPU))

# --- the joints, on the design (pixel corners) ----------------------------------------------------------------------
NEAR_LEG = [(21.0, 38.0), (19.5, 46.5), (18.0, 54.0)]   # hip, knee (the guard's middle), ankle (the boot's top)
FAR_LEG = [(34.5, 38.0), (36.5, 47.5), (36.5, 54.5)]
NEAR_ARM = [(13, 24), (11, 31), (10, 38)]                 # shoulder, elbow, wrist (Codex's)
BARE_ARM = [(38, 27), (40, 33), (43, 38)]
PELVIS = (27, 36)
NECK = (27, 18)
CAPE_TOP = (27, 26)
SASH_TOP = (28.5, 38)            # the sash hangs from under the buckle
HIPS = 0.25                     # the share of the body's tilt the hips take (the rest is his back bending)
GRIP = (10, 40)                 # the hammer's grip in the design's near hand


def rot(v, angle):
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    return c * v[0] - s * v[1], s * v[0] + c * v[1]


def vadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def vsub(a, b):
    return a[0] - b[0], a[1] - b[1]


def bearing(v):
    return math.degrees(math.atan2(v[1], v[0]))


def endpoint(a, n, angle):
    return vadd(a, rot((n, 0), angle))


def rest(joints):
    return tuple(bearing(vsub(b, a)) for a, b in zip(joints, joints[1:]))


REST = {"near": rest(NEAR_ARM), "bare": rest(BARE_ARM), "near_leg": rest(NEAR_LEG), "far_leg": rest(FAR_LEG)}


def paste(can, name, anchor, dest, angle=0.0, mat=None, ground=None):
    """PARTS[name] turned by `angle` (degrees, clockwise on screen) or carried by the 2x2 `mat`, its `anchor` (design
    squares) on `dest` (the design's frame), sampled from its 8x picture; with `ground` (a design row) the cloth under
    it folded back over it."""
    if mat is None:
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        mat = ((c, -s), (s, c))
    (a, b), (c, d) = mat
    det = a * d - b * c
    inv = ((d / det, -b / det), (-c / det, a / det))
    dx, dy = dest[0] + OX, dest[1] + OY
    ax, ay = anchor
    coeff = [inv[0][0], inv[0][1], ax - inv[0][0] * dx - inv[0][1] * dy,
             inv[1][0], inv[1][1], ay - inv[1][0] * dx - inv[1][1] * dy]
    tile = PARTS8[name].transform(SIZE, Image.Transform.AFFINE, [8 * v for v in coeff],
                                  resample=Image.Resampling.NEAREST)
    if ground is not None:
        ta = np.array(tile)
        edge = int(round(ground)) + OY
        for yy in range(edge, ta.shape[0]):
            if 2 * edge - yy - 1 >= 0:
                m = ta[yy, :, 3] > 0
                ta[2 * edge - yy - 1, m] = ta[yy, m]
        ta[edge:] = 0
        tile = Image.fromarray(ta)
    can.alpha_composite(tile)


def limb_ends(joints, root, angles):
    """The knee/elbow and the ankle/wrist of a two-bone limb from `root`, its bones at their screen angles."""
    b1 = endpoint(root, math.hypot(*vsub(joints[1], joints[0])), angles[0])
    return b1, endpoint(b1, math.hypot(*vsub(joints[2], joints[1])), angles[1])


def chain(can, names, joints, root, angles, rest_, end=None):
    """A two-bone limb from `root`, each part on its joint at its screen angle (90 = down); `end` = (a third part on
    the last joint, its own turn or None to turn with the second). -> the last joint's place, the second's turn."""
    b1, c1 = limb_ends(joints, root, angles)
    t1 = angles[1] - rest_[1]
    paste(can, names[0], joints[0], root, angles[0] - rest_[0])
    paste(can, names[1], joints[1], b1, t1)
    if end is not None:
        paste(can, end[0], joints[2], c1, t1 if end[1] is None else end[1])
    return c1, t1


def swept(tilt, turn, shear, squash):
    """Cloth hung from its top edge: turned with the body and by its own turn, each row under the top carried back
    (left) by shear and the whole lifted by squash."""
    c, s = math.cos(math.radians(tilt + turn)), math.sin(math.radians(tilt + turn))
    return (c, -c * shear - s * squash), (s, -s * shear + c * squash)


def trunk(p, share=1.0):
    """The body's 2x2 about the pelvis: bent forward (each row over the pelvis carried forward by bend[0], the rows
    drawn together by bend[1] - a back bending toward us in his three-quarter view keeps his shoulders level), then
    turned by tilt; `share` of both for the hips."""
    k, sq = p["bend"]
    k, sq = k * share, 1 + (sq - 1) * share
    c, s = math.cos(math.radians(p["tilt"] * share)), math.sin(math.radians(p["tilt"] * share))
    return (c, -c * k - s * sq), (s, -s * k + c * sq)


def body(p, point, share=1.0):
    """A point of the standing design carried with the body (trunk), the pelvis moved."""
    (a, b), (c, d) = trunk(p, share)
    u, v = vsub(point, PELVIS)
    return vadd(p["pelvis"], (a * u + b * v, c * u + d * v))


def base_pose():
    """The design standing: the pelvis, the body's tilt and bend (trunk), the head's own turn over it, each limb's two
    screen angles (each leg's third: its boot's turn, None to turn with the shin), the hammer's turn, the cape (turn,
    shear, squash), the sash (turn, shear, squash; sash_back: blown back between the legs, behind them), the dropped
    hammer (its grip's x, y, its turn) or None and whether it lies on the ground (drop_ground), the far arm raised (its
    pauldron lifted), the near shoulder's reach forward, the hammer in front of the body, the grip's offset down the
    hand, what stands on the ground."""
    return dict(pelvis=PELVIS, tilt=0.0, head=0.0, near=REST["near"], bare=REST["bare"],
                legs=(REST["near_leg"] + (None,), REST["far_leg"] + (None,)), weapon=0.0, cape=(0.0, 0.0, 1.0),
                sash=(0.0, 0.0, 1.0), sash_back=False, bend=(0.0, 1.0), drop_ground=False,
                drop=None, raised=False, reach=0, front=False, grip=2, ground="feet")


def render(p):
    """The frame of pose p on the canvas (the design's (0, 0) at (OX, OY)), back to front: the cape (hung from its top
    edge, turned, its hem swept back by shear and lifted by squash), the far leg, the bare far arm, the near leg, the
    torso and the sash (hung from under the buckle, swept back by shear; behind the legs when blown back), the hammer
    (unless in front) and the gauntleted near arm, the pauldrons, the head, the hammer in front; then set down - its
    lowest boot (ground "feet") or its lowest pixel (ground "all") on the design's ground, a dropped hammer on its own -
    and its 1-6 pixel specks cleared."""
    can = Image.new("RGBA", SIZE)
    tilt = p["tilt"]
    nl, fl = p["legs"]
    nhip, fhip = body(p, NEAR_LEG[0], HIPS), body(p, FAR_LEG[0], HIPS)     # the hips stay near level as he bends
    feet = Image.new("RGBA", SIZE)
    for (th, sh, bt), hip, boot, joints, rs in ((nl, nhip, "near_boot", NEAR_LEG, REST["near_leg"]),
                                                (fl, fhip, "far_boot", FAR_LEG, REST["far_leg"])):
        _, an = limb_ends(joints, hip, (th, sh))
        paste(feet, boot, joints[2], an, sh - rs[1] if bt is None else bt)
    floor = feet.getbbox()[3] - OY if p["ground"] == "feet" else GROUND     # where the cloth folds
    paste(can, "cape", CAPE_TOP, body(p, CAPE_TOP), mat=swept(tilt, *p["cape"]), ground=floor)
    if p["sash_back"]:
        paste(can, "sash", SASH_TOP, body(p, SASH_TOP), mat=swept(tilt, *p["sash"]), ground=floor)
    chain(can, ("far_thigh", "far_shin"), FAR_LEG, fhip, fl[:2], REST["far_leg"], ("far_boot", fl[2]))
    root = body(p, (38, 17) if p["raised"] else BARE_ARM[0])
    chain(can, ("bare_upper", "bare_lower"), BARE_ARM, root, p["bare"], REST["bare"], ("bare_hand", None))
    chain(can, ("near_thigh", "near_shin"), NEAR_LEG, nhip, nl[:2], REST["near_leg"], ("near_boot", nl[2]))
    paste(can, "torso", PELVIS, p["pelvis"], mat=trunk(p), ground=floor)
    if not p["sash_back"]:
        paste(can, "sash", SASH_TOP, body(p, SASH_TOP), mat=swept(tilt, *p["sash"]), ground=floor)
    sx = NEAR_ARM[0][0] + p["reach"]
    wrist, na = chain(can, ("near_upper", "near_lower"), NEAR_ARM, body(p, (sx, NEAR_ARM[0][1])), p["near"],
                      REST["near"])
    grip = vadd(wrist, rot((0, p["grip"]), na))
    dropped = Image.new("RGBA", SIZE)
    if p["drop"] is not None:
        wx, wy, wa = p["drop"]
        paste(dropped, "weapon", GRIP, (wx, wy), wa)
    elif not p["front"]:
        paste(can, "weapon", GRIP, grip, p["weapon"])
    paste(can, "near_hand", NEAR_ARM[2], wrist, na)
    paste(can, "far_shoulder", (38, 23), body(p, (38, 17) if p["raised"] else (38, 23)), tilt)
    paste(can, "near_shoulder", (13, 21), body(p, (sx, 21)), tilt)
    paste(can, "head", NECK, body(p, NECK), tilt + p["head"])
    if p["front"] and p["drop"] is None:
        paste(can, "weapon", GRIP, grip, p["weapon"])
        paste(can, "near_hand", NEAR_ARM[2], wrist, na)
    a = np.array(can)
    if p["ground"]:
        op = (np.array(feet) if p["ground"] == "feet" else a)[..., 3] > 0
        a = drop_to(a, GROUND + OY - (int(np.nonzero(op.any(1))[0].max()) + 1))
    w = np.array(dropped)
    if p["drop"] is not None and p["drop_ground"]:
        w = drop_to(w, GROUND + OY - (int(np.nonzero((w[..., 3] > 0).any(1))[0].max()) + 1))
    out = Image.fromarray(a)
    out.alpha_composite(Image.fromarray(w))
    return Image.fromarray(despeck(np.array(out)))


def drop_to(a, dy):
    """The picture moved down dy rows (up if negative), nothing wrapping round."""
    a = np.roll(a, dy, axis=0)
    if dy > 0:
        a[:dy] = 0
    elif dy < 0:
        a[dy:] = 0
    return a


def despeck(a):
    """Codex's seam clean-up: every 8-connected piece of 6 pixels or fewer cleared."""
    lbl, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n:
        sizes = ndimage.sum(np.ones(lbl.shape), lbl, range(1, n + 1))
        for i in np.nonzero(sizes <= 6)[0]:
            a[lbl == i + 1] = 0
    return a


# --- the poses, on the old frames (--tune): {tag: [each frame's keys over base_pose]} -------------------------------
def _run():
    """The run (RUN_LEGS): the near leg planted ahead in 1 and 8, under him in 2, pushing off behind in 3, kicked up
    behind in 4, coming through knee first in 5-6 and reaching in 7; the far leg half a stride on. He leans in, the
    hammer trails low behind, each arm swinging against its leg, the cape streaming back."""
    near = [(72, 92, 0), (95, 102, 0), (122, 140, 30), (118, 172, None), (52, 118, None), (40, 106, None),
            (56, 74, -10), (72, 92, 0)]
    far = [(116, 170, None), (52, 116, None), (56, 72, -10), (68, 88, 0), (88, 96, 0), (100, 112, 0),
           (120, 138, 30), (120, 176, None)]
    swing = [12, 6, -6, -12, -8, 0, 8, 12]          # the near arm back (+) as the near leg goes ahead
    out = []
    for k in range(8):
        out.append(dict(tilt=9, head=-6, legs=(near[k], far[k]), near=(122 + swing[k], 128 + swing[k]),
                        weapon=30 + swing[k],
                        bare=[(50, 68), (45, 46), (58, 35), (75, 40), (87, 75), (73, 82), (60, 78), (50, 68)][k],
                        cape=(6, [0.95, 1.05, 1.15, 1.05] [k % 4], [0.68, 0.62, 0.58, 0.62][k % 4]),
                        sash=([14, 18, 22, 18][k % 4], 0.3, 0.85), sash_back=True))
    return out


STANCE = ((124, 118, 0), (52, 94, 0))       # feet apart: the near leg back, the far one forward, its knee bent


def _attack():
    """The attack: the hammer raised up behind his head (1), drawn back level behind him (2), swept out in front
    across his body at chest height (3), carried on down in front (4), back down by his side (5), settled (6); feet
    apart throughout, the bare fist out in front but in the sweep."""
    return [dict(tilt=-6, head=2, legs=STANCE, near=(232, 262), weapon=150, bare=(35, 5), cape=(0, 0.2, 0.95)),
            dict(tilt=-3, head=0, legs=STANCE, near=(178, 182), weapon=92, bare=(40, 10), cape=(0, 0.25, 0.95)),
            dict(tilt=4, head=-4, legs=STANCE, near=(6, 4), weapon=-86, bare=(95, 300), reach=10, front=True,
                 cape=(0, 0.45, 0.9), pelvis=(30, 36)),
            dict(tilt=8, head=-5, legs=STANCE, near=(30, 40), weapon=-52, bare=(85, 315), reach=10, front=True,
                 cape=(0, 0.4, 0.9), pelvis=(30, 36)),
            dict(tilt=3, head=-2, legs=STANCE, near=(118, 120), weapon=22, bare=(40, 10), cape=(0, 0.2, 0.95)),
            dict(tilt=0, legs=((106, 104, 0), (72, 90, 0)), near=(108, 102), weapon=4, bare=(60, 40))]


def _attack_p():
    """Bravado: the hammer lifted behind his shoulder (1) and straight up over his head (2), then he lunges low - the
    near leg stretched back, the far knee bent deep, his back near level - and smashes its head into the ground in
    front of him, the bare arm flung up behind (3, 4); he rises with it held back behind him (5) and settles (6)."""
    lunge = ((150, 152, 0), (14, 104, 0))
    return [dict(tilt=-4, legs=STANCE, near=(228, 252), weapon=140, bare=(35, 5), cape=(0, 0.2, 0.95)),
            dict(tilt=-2, legs=STANCE, near=(266, 272), weapon=180, bare=(45, 15), cape=(0, 0.15, 0.95)),
            dict(tilt=24, bend=(1.05, 0.78), head=-20, legs=lunge, near=(40, 40), weapon=-70, bare=(268, 240),
                 reach=10, front=True, cape=(14, 0.4, 0.8), sash=(16, 0.2, 0.9), pelvis=(17, 36)),
            dict(tilt=22, bend=(1.0, 0.8), head=-18, legs=lunge, near=(42, 42), weapon=-68, bare=(250, 225),
                 reach=10, front=True, cape=(12, 0.35, 0.82), sash=(14, 0.2, 0.9), pelvis=(17, 36)),
            dict(tilt=4, legs=STANCE, near=(172, 178), weapon=88, bare=(40, 10), cape=(0, 0.25, 0.95)),
            dict(tilt=0, legs=((106, 104, 0), (72, 90, 0)), near=(112, 106), weapon=6, bare=(60, 40))]


EASY = ((106, 104, 0), (72, 90, 0))          # standing easy, the feet a little apart
WIDE = ((118, 108, 0), (60, 92, 0))          # braced, the feet well apart


def _skill():
    """Dazzle (E): the hammer raised up behind his head (1), brought down in front (2), thrust straight out ahead at
    chest height, the bare hand raised up behind him (3, 4), drawn back up before his chest (5); settled (6)."""
    return [dict(tilt=-6, head=2, legs=STANCE, near=(232, 262), weapon=150, bare=(35, 5), cape=(0, 0.2, 0.95)),
            dict(tilt=4, head=-3, legs=STANCE, near=(40, 22), weapon=-72, bare=(100, 300), reach=8, front=True,
                 cape=(0, 0.3, 0.92)),
            dict(tilt=4, head=-4, legs=STANCE, near=(2, 0), weapon=-90, bare=(262, 250), raised=True, reach=10,
                 front=True, cape=(0, 0.45, 0.9), pelvis=(29, 36)),
            dict(tilt=5, head=-4, legs=STANCE, near=(4, 2), weapon=-88, bare=(258, 246), raised=True, reach=10,
                 front=True, cape=(0, 0.4, 0.9), pelvis=(29, 36)),
            dict(tilt=2, head=-2, legs=STANCE, near=(60, 350), weapon=215, bare=(90, 40), reach=12, front=True,
                 cape=(0, 0.25, 0.95)),
            dict(legs=EASY, near=(112, 106), weapon=6, bare=(64, 44))]


def _skill2():
    """Starlight's Touch (Q): the bare fist before his chest (1), the hand raised open ahead of him (2), straight up
    high over his head (3, 4), lowered ahead (5) and down (6); the hammer low in his near hand throughout."""
    bare = [(100, 228), (335, 305), (305, 290), (303, 286), (345, 318), (80, 66)]
    return [dict(legs=EASY, near=(110, 102), weapon=4, bare=b, raised=k in (2, 3), head=[0, -2, -4, -4, -2, 0][k])
            for k, b in enumerate(bare)]


def _ult():
    """Cosmic Radiance (R): standing (1), the hammer swung up across him (2), held high over his head, the bare hand
    open ahead of him, the cape spread (3-6), lowered (7)."""
    up = dict(legs=WIDE, near=(268, 272), weapon=180, bare=(18, 335), cape=(0, 0.15, 1.0))
    return [dict(legs=EASY, near=(112, 106), weapon=6, bare=(80, 50)),
            dict(legs=WIDE, near=(350, 330), weapon=215, bare=(85, 60), reach=12, front=True, head=-2),
            dict(up, head=-6), dict(up, head=-5, bare=(20, 338)), dict(up, head=-6, bare=(16, 333)),
            dict(up, head=-5, bare=(20, 338)),
            dict(legs=EASY, near=(112, 106), weapon=6, bare=(80, 50))]


def _hit():
    """Struck: jolted back, the bare fist flung out ahead (1); upright again (2)."""
    return [dict(tilt=-12, head=4, legs=((110, 100, 0), (66, 92, 0)), near=(126, 120), weapon=22, bare=(10, 350),
                 cape=(0, -0.2, 1.0)),
            dict(tilt=-3, legs=EASY, near=(110, 102), weapon=6, bare=(70, 55))]


def _dead():
    """Death: struck back (1); falling back, the hammer flung away up ahead of him (2, 3); down on his knees as it
    falls (4); slumping forward (5) and down on his face, the hammer on the ground before him (6-8)."""
    knees = ((62, 176, 90), (50, 172, 84))
    flat = ((176, 178, 90), (172, 176, 90))
    down = dict(drop=(52, 52, 270), drop_ground=True, ground="all")
    return [dict(tilt=-14, head=6, legs=((112, 100, 0), (62, 90, 0)), near=(130, 120), weapon=24, bare=(5, 345),
                 cape=(0, -0.2, 1.0)),
            dict(tilt=-24, head=8, legs=((104, 112, 0), (52, 100, 0)), near=(160, 170), bare=(350, 330),
                 drop=(54, 2, 150), cape=(0, -0.25, 1.0)),
            dict(tilt=-30, head=8, legs=((84, 132, 0), (40, 118, 0)), near=(150, 150), bare=(0, 340),
                 drop=(58, 14, 200), cape=(0, -0.25, 1.0)),
            dict(tilt=10, head=8, legs=knees, near=(100, 95), bare=(75, 60), drop=(58, 36, 245), ground="all",
                 cape=(16, 0.4, 0.85), sash=(-30, 0, 0.9)),
            dict(down, tilt=30, bend=(0.4, 0.9), head=-14, legs=knees, near=(80, 70), bare=(70, 80),
                 cape=(10, 0.2, 0.95), drop=(54, 52, 270)),
            dict(down, tilt=78, head=-6, legs=flat, near=(35, 20), bare=(10, 5), cape=(0, 0.1, 0.9)),
            dict(down, tilt=84, head=-4, legs=flat, near=(35, 20), bare=(10, 5), cape=(0, 0.05, 0.85)),
            dict(down, tilt=86, head=-2, legs=flat, near=(35, 20), bare=(10, 5), cape=(0, 0.05, 0.85))]


POSES = {"run": _run(), "attack": _attack(), "attack_p": _attack_p(), "skill": _skill(), "skill2": _skill2(),
         "ult": _ult(), "hit": _hit(), "dead": _dead()}


# each frame's body moved sideways where the old frame has it (the old frames step back and forth within the frame
# round a still pivot): the shift that lays the new frame's upper 60 % best over the old one's (shifts())
SHIFT = {"run": [5, 6, 7, 6, 6, 7, 6, 6], "attack": [-1, -5, 2, -15, 15, 1], "attack_p": [-3, -6, -19, -24, 1, 13],
         "skill": [-5, -4, -10, -12, -10, 0], "skill2": [-1, -2, -2, -2, 0, 0], "ult": [-1, -1, -3, -3, -6, -3, -4],
         "hit": [-17, 0], "dead": [-13, -7, -14, 8, -14, -17, -12, -14]}


def pose(tag, k, shift=True):
    p = base_pose()
    fr = POSES.get(tag, [])
    if k - 1 < len(fr):
        p.update(fr[k - 1])
    dx = SHIFT.get(tag, [0] * k)[k - 1] if shift else 0
    p["pelvis"] = (p["pelvis"][0] + dx, p["pelvis"][1])
    if p["drop"] is not None:
        p["drop"] = (p["drop"][0] + dx,) + tuple(p["drop"][1:])
    return p


def shifts():
    """{tag: [each frame's best shift]}: the new frame (unshifted) moved -24..24 squares over the old one, its upper
    60 % (his head and body, not where the long-handled old hammer swings low) overlapping most."""
    out = {}
    for tag in TAGS:
        out[tag] = []
        for k in range(1, len(OLD[tag]) + 1):
            o = np.array(old_on_grid(tag, k))[..., 3] > 0
            n = np.array(render(pose(tag, k, shift=False)))[..., 3] > 0
            ys = np.nonzero(o.any(1))[0]
            o, n = o[:ys.min() + int((ys.max() - ys.min()) * 0.6)], n[:ys.min() + int((ys.max() - ys.min()) * 0.6)]
            iou = [((o & np.roll(n, dx, 1)).sum() / max((o | np.roll(n, dx, 1)).sum(), 1), dx) for dx in range(-24, 25)]
            out[tag].append(max(iou)[1])
    return out


def placed():
    """{"<tag>_<frame>": (picture, x, y of its top-left on the design's grid)}."""
    out = {}
    for tag in TAGS:
        for k in range(1, len(OLD[tag]) + 1):
            a = np.asarray(render(pose(tag, k)))
            ys, xs = np.nonzero(a[..., 3] > 0)
            out[f"{tag}_{k}"] = (a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy(), int(xs.min()) - OX,
                                 int(ys.min()) - OY)
    return out


def old_on_grid(tag, k):
    """The old frame at PPU on the canvas, its pivot on the design's: (RGBA)."""
    fr, _, (pvx, pvy) = OLD[tag][k - 1]
    h, w = fr.shape[:2]
    im = Image.fromarray(fr).resize((round(w * PPU), round(h * PPU)), Image.NEAREST)
    can = Image.new("RGBA", SIZE)
    can.alpha_composite(im, (int(round(OX + PIVOT - pvx * PPU)), int(round(OY + GROUND - pvy * PPU))))
    return can


def check():
    """The standing pose is the design pixel for pixel; every frame only the design's colours."""
    a = np.asarray(render(base_pose()))
    d = np.zeros_like(a)
    d[OY:OY + D0.shape[0], OX:OX + D0.shape[1]] = D0
    d[d[..., 3] == 0] = 0
    bad = int((a != d).any(-1).sum())
    print("standing pose vs design: pixels differing", bad)
    pal = {tuple(c) for c in ARR[OPAQUE][:, :3].tolist()}
    for n, (pic, _, _) in placed().items():
        cols = {tuple(c) for c in pic[pic[..., 3] > 0][:, :3].tolist()}
        if cols - pal or set(np.unique(pic[..., 3])) - {0, 255}:
            print(n, "colours off the design:", len(cols - pal))
    return bad


def tune(out_dir, tags):
    """Per tag: each frame a row - the old frame at PPU | the new | the new over the old (the old faded), at 3x."""
    os.makedirs(out_dir, exist_ok=True)
    Z, (W, H) = 3, SIZE
    for tag in tags:
        n = len(OLD[tag])
        sheet = Image.new("RGB", (3 * W * Z + 8, n * H * Z), (30, 30, 30))
        for k in range(1, n + 1):
            old, new = old_on_grid(tag, k), render(pose(tag, k))
            ghost = np.array(old)
            ghost[..., 3] = (ghost[..., 3] > 0) * 110
            for i, layers in enumerate(([old], [new], [Image.fromarray(ghost), new])):
                t = Image.new("RGBA", SIZE, (95, 100, 95, 255))
                ImageDraw.Draw(t).line([(0, OY + GROUND), (W, OY + GROUND)], fill=(140, 140, 140, 255))
                for im in layers:
                    t.alpha_composite(im)
                sheet.paste(t.convert("RGB").resize((W * Z, H * Z), Image.NEAREST), (i * (W * Z + 4), (k - 1) * H * Z))
        sheet.save(os.path.join(out_dir, f"tune_{tag}.png"))
    print("written", out_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tune")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--shifts", action="store_true", help="SHIFT measured again")
    ap.add_argument("--tags", nargs="*", default=TAGS)
    a = ap.parse_args()
    if a.check:
        sys.exit(1 if check() else 0)
    if a.shifts:
        print(shifts())
        return
    if a.tune:
        tune(a.tune, a.tags)
        return
    fr = placed()
    print("frames", len(fr))
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    for t in TAGS:
        names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
        x0 = min(min(fr[n][1] for n in names), 0) - 2
        x1 = max(max(fr[n][1] + fr[n][0].shape[1] for n in names), D0.shape[1]) + 2
        y0 = min(min(fr[n][2] for n in names), 0) - 2
        y1 = max(GROUND, max(fr[n][2] + fr[n][0].shape[0] for n in names)) + 2
        Z, W, Hh = 2, x1 - x0, y1 - y0
        tiles = [("design", (D0, 0, 0))] + [(n, fr[n]) for n in names]
        can = Image.new("RGB", (len(tiles) * (W * Z + 4), Hh * Z), (40, 40, 40))
        for i, (n, (pic, x, y)) in enumerate(tiles):
            tile = Image.new("RGBA", (W, Hh), (150, 165, 150, 255))
            tile.alpha_composite(Image.fromarray(pic), (x - x0, y - y0))
            can.paste(tile.convert("RGB").resize((W * Z, Hh * Z), Image.NEAREST), (i * (W * Z + 4), 0))
        can.save(os.path.join(a.review, f"placed_{t}.png"))
    print("written", a.review)


if __name__ == "__main__":
    main()
