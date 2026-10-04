#!/usr/bin/env python3
"""Sivir's action strips posed from the approved design's own parts (2026-10-04): the casting body = the idle's body.

    python tools/art/rig_sivir.py            # writes assets/source/native/sivir_<tag>.png (8x) + sivir_cells.json
    python tools/art/rig_sivir.py --review   # also Temp/sv_work/rig/review.png (every pose next to the idle, 6x)

Codex's step-2 strips (2026-10-04) drew a new, bigger body in every frame (+13-45% of the idle's area); scaled and
with the design's head pasted they still read 「人物释放技能时变胖 模型变形」. Every frame here is the design itself:

Parts (design canvas, 1x, pivot (64, 88), soles row 99):
- FRONT: the near arm under the pauldron (purple sleeve, gold bracer, brown open glove);
- UNIT: the crossblade with the far hand's glove and gold cuff (moved and turned as one);
- SLEEVE: the far arm's purple sleeve from the shoulder to the cuff (drawn per pose);
- BODY: everything else (head, hair, torso, legs), the squares the blade and the hand covered painted.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SV = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(SV, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import rig_nocturne as RN  # noqa: E402

DESIGN = os.path.join(SV, "assets", "source", "native", "sivir_native.png")
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "sv_work", "rig")
PIVOT = (64, 88)
OUT = (0x14, 0x10, 0x1A)

HAIR = {(0x1B, 0x22, 0x36), (0x1A, 0x24, 0x40), (0x2C, 0x3A, 0x58), (0x2C, 0x3E, 0x66)}


def design():
    return np.asarray(Image.open(DESIGN).convert("RGBA"))[4::8, 4::8].copy()


def is_out(c):
    return tuple(int(v) for v in c[:3]) == OUT


def masks(d):
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    front = np.zeros((H, W), bool)
    for y in range(77, 87):
        for x in range(74, 90):
            if op[y, x] and (y <= 83 or x >= 80):
                front[y, x] = True
    # the crossblade with the far glove and cuff: its squares that are not outline, by rows
    core = np.zeros((H, W), bool)
    lim = {}
    for y in range(67, 73):
        lim[y] = 51
    lim[73] = 57
    for y in range(74, 81):
        lim[y] = 59 if y in (76, 77) else 58
    for y in range(81, 86):
        lim[y] = 56
    for y in range(86, 90):
        lim[y] = 49
    for y, xm in lim.items():
        for x in range(36, xm + 1):
            c = d[y, x]
            if op[y, x] and not is_out(c) and tuple(int(v) for v in c[:3]) not in HAIR:
                core[y, x] = True
    # the sleeve between the cuff and the shoulder
    sleeve = np.zeros((H, W), bool)
    for x, y in ((59, 75), (60, 75), (60, 74), (60, 73)):
        sleeve[y, x] = True
    core &= ~sleeve
    # outline squares: the unit's when every non-outline 4-neighbour is the unit's (or a sleeve square)
    unit = core.copy()
    for y in range(66, 91):
        for x in range(36, 60):
            if op[y, x] and is_out(d[y, x]):
                nb = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                body_nb = [p for p in nb if op[p] and not is_out(d[p]) and not core[p] and not sleeve[p]]
                unit_nb = [p for p in nb if core[p]]
                if unit_nb and not body_nb:
                    unit[y, x] = True
    return front, unit, sleeve


def body_of(d, front, unit, sleeve):
    """The design without the moving parts; outline squares left with no drawn square beside them (8 ways) go."""
    body = d.copy()
    body[front | unit | sleeve] = 0
    op = body[..., 3] > 0
    H, W = op.shape
    for y in range(H):
        for x in range(W):
            if op[y, x] and is_out(body[y, x]):
                if not any(op[y + dy, x + dx] and not is_out(body[y + dy, x + dx])
                           for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx)):
                    body[y, x] = 0
    return drop_small(body, 4)


def drop_small(a, keep):
    """Pieces (8-connected) under `keep` squares go."""
    a = a.copy()
    op = a[..., 3] > 0
    H, W = op.shape
    seen = np.zeros((H, W), bool)
    for y in range(H):
        for x in range(W):
            if op[y, x] and not seen[y, x]:
                st, comp = [(y, x)], []
                seen[y, x] = True
                while st:
                    cy, cx = st.pop()
                    comp.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < H and 0 <= nx < W and op[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                st.append((ny, nx))
                if len(comp) < keep:
                    for cy, cx in comp:
                        a[cy, cx] = 0
    return a


def grid_img(a, x0, x1, y0, y1, z, name):
    sub = a[y0:y1 + 1, x0:x1 + 1]
    H, W = sub.shape[:2]
    img = Image.new("RGBA", (W * z + 30, H * z + 20), (92, 98, 86, 255))
    img.alpha_composite(Image.fromarray(sub).resize((W * z, H * z), Image.NEAREST), (30, 20))
    dr = ImageDraw.Draw(img)
    for c in range(W):
        dr.text((30 + c * z + 3, 4), str((c + x0) % 100), fill=(255, 255, 255))
    for r in range(H):
        dr.text((2, 20 + r * z + 4), str(r + y0), fill=(255, 255, 255))
    for c in range(W + 1):
        dr.line([(30 + c * z, 20), (30 + c * z, 20 + H * z)], fill=(0, 0, 0, 90))
    for r in range(H + 1):
        dr.line([(30, 20 + r * z), (30 + W * z, 20 + r * z)], fill=(0, 0, 0, 90))
    os.makedirs(TMP, exist_ok=True)
    img.save(os.path.join(TMP, name))


def show(arrs, name, z=12):
    tiles = []
    for t, a in arrs:
        ys, xs = np.nonzero(a[..., 3] > 0)
        if not len(ys):
            continue
        sub = a[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]
        im = Image.fromarray(sub).resize((sub.shape[1] * z, sub.shape[0] * z), Image.NEAREST)
        bg = Image.new("RGBA", (im.width, im.height + 18), (92, 98, 86, 255))
        bg.alpha_composite(im, (0, 18))
        ImageDraw.Draw(bg).text((3, 2), t, fill=(255, 255, 255, 255))
        tiles.append(bg)
    W = sum(t.width + 8 for t in tiles)
    H = max(t.height for t in tiles)
    out = Image.new("RGB", (W, H), (30, 30, 30))
    x = 0
    for t in tiles:
        out.paste(t.convert("RGB"), (x, 0))
        x += t.width + 8
    os.makedirs(TMP, exist_ok=True)
    out.save(os.path.join(TMP, name))
    return out.size


# ---------------------------------------------------------------------------------------------------------------
# posing

RING = (47.0, 80.0)          # the crossblade's ring middle (continuous canvas coordinates)
CUFF = (59.5, 76.0)          # where the far sleeve meets the cuff
SHOULDER_FAR = (61.0, 73.5)
SHOULDER_NEAR = (75.0, 77.0)
GLOVE_NEAR = (85.5, 83.0)    # the near glove's middle
SLEEVE = ((0x4E, 0x3F, 0x5E, 255), (0x2E, 0x24, 0x38, 255))     # lit, dark


def sprite_of(d, mask):
    ys, xs = np.nonzero(mask)
    y0, x0 = ys.min(), xs.min()
    s = np.zeros((ys.max() - y0 + 1, xs.max() - x0 + 1, 4), np.uint8)
    s[ys - y0, xs - x0] = d[ys, xs]
    return s, (x0, y0)


def rot_pt(p, c, deg):
    """p turned deg counter-clockwise on screen about c."""
    t = math.radians(deg)
    dx, dy = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * math.cos(t) + dy * math.sin(t), c[1] - dx * math.sin(t) + dy * math.cos(t))


def transform(s, origin, joint, deg, target):
    """{(x, y): rgba}: sprite s (top-left at origin) turned deg about joint, the joint moved onto target."""
    jx, jy = joint[0] - origin[0] - 0.5, joint[1] - origin[1] - 0.5
    if deg % 360 == 0:
        r, (rx, ry) = s, (jx, jy)
    elif deg % 90 == 0:
        r, (rx, ry) = RN.op(s, (jx, jy), ("rot", int(deg // 90) % 4))
    else:
        r, (rx, ry) = RN.rotsprite(s, (jx, jy), deg)
    ox = int(math.floor(target[0] - 0.5 - rx + 0.5))
    oy = int(math.floor(target[1] - 0.5 - ry + 0.5))
    return {(ox + x, oy + y): r[y, x].copy() for y, x in zip(*np.nonzero(r[..., 3]))}


ARM_REACH = 8.5             # shoulder -> cuff at most (the near arm: shoulder -> the bracer's end ~8)


def reach(shoulder, cuff):
    dx, dy = cuff[0] - shoulder[0], cuff[1] - shoulder[1]
    n = math.hypot(dx, dy)
    if n <= ARM_REACH:
        return cuff
    return (shoulder[0] + dx * ARM_REACH / n, shoulder[1] + dy * ARM_REACH / n)


def sleeve(a, b, half=1.3):
    """The far arm's sleeve from a to b: lit on its upper side, dark under, one outline ring."""
    cells = {}
    vx, vy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(vx, vy) or 1e-9
    for y in range(int(min(a[1], b[1])) - 3, int(max(a[1], b[1])) + 4):
        for x in range(int(min(a[0], b[0])) - 3, int(max(a[0], b[0])) + 4):
            px, py = x + 0.5, y + 0.5
            t = max(0.0, min(n, ((px - a[0]) * vx + (py - a[1]) * vy) / n))
            qx, qy = a[0] + vx / n * t, a[1] + vy / n * t
            if math.hypot(px - qx, py - qy) <= half:
                side = (px - qx) * (-vy / n) + (py - qy) * (vx / n)      # + = left of a->b
                up = side if vx >= 0 else -side
                cells[(x, y)] = np.array(SLEEVE[0] if (py < qy or (abs(py - qy) < 0.3 and up > 0)) else SLEEVE[1],
                                         np.uint8)
    ring = {}
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells:
                ring[q] = np.array(OUT + (255,), np.uint8)
    ring.update(cells)
    return ring


def put(canvas, cells, under=False):
    for (x, y), c in cells.items():
        if 0 <= y < canvas.shape[0] and 0 <= x < canvas.shape[1]:
            if under and canvas[y, x, 3]:
                continue
            canvas[y, x] = c


import strips as G  # noqa: E402

HAIR_FILL = ((0x2C, 0x3A, 0x58, 255), (0x1B, 0x22, 0x36, 255))   # the hair's mid navy, its dark navy at the edges
BACK_ZONE = (48, 62, 70, 86)                                     # x0, x1, y0, y1: behind her back, by the far arm


def holes_of(a):
    """Enclosed clear components (4-connected), as lists of (x, y)."""
    from collections import deque
    op = a[..., 3] > 0
    H, W = op.shape
    seen = np.zeros((H, W), bool)
    q = deque()
    for y in range(H):
        for x in range(W):
            if (y in (0, H - 1) or x in (0, W - 1)) and not op[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and not op[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    hole = ~op & ~seen
    lab = np.zeros((H, W), int)
    comps = []
    for y, x in zip(*np.nonzero(hole)):
        if lab[y, x]:
            continue
        lab[y, x] = len(comps) + 1
        st, pts = [(y, x)], []
        while st:
            cy, cx = st.pop()
            pts.append((cx, cy))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if hole[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = len(comps) + 1
                    st.append((ny, nx))
        comps.append(pts)
    return comps


def fill_flat(a, keep=(), below=128):
    """Every enclosed gap (but those touching a `keep` square) takes the commonest colour round it that is not the
    outline - the specks a whole-figure RotSprite opens between the parts."""
    a = a.copy()
    for pts in holes_of(a):
        if any(abs(x - kx) <= 2.5 and abs(y - ky) <= 2.5 for x, y in pts for kx, ky in keep):
            continue
        if min(y for _, y in pts) >= below:
            continue
        from collections import Counter
        ps = set(pts)
        nb = Counter()
        for x, y in pts:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in ps and a[q[1], q[0], 3] and tuple(int(v) for v in a[q[1], q[0], :3]) != OUT:
                    nb[tuple(int(v) for v in a[q[1], q[0]])] += 1
        # a pocket walled by outline only takes the outline
        col = np.array(nb.most_common(1)[0][0] if nb else OUT + (255,), np.uint8)
        for x, y in pts:
            a[y, x] = col
    return a


def fill_back(a, shift=0, vshift=0, keep=()):
    """The gaps the far arm leaves behind her back (enclosed, mostly inside BACK_ZONE moved by the lean) take the long
    hair falling there: mid navy, dark navy where they touch the outline."""
    x0, x1, y0, y1 = BACK_ZONE
    a = a.copy()
    for pts in holes_of(a):
        inside = sum(1 for x, y in pts if x0 + shift <= x <= x1 + shift and y0 + vshift <= y <= y1 + vshift)
        if inside * 2 < len(pts):
            continue
        if any(abs(x - kx) <= 2.5 and abs(y - ky) <= 2.5 for x, y in pts for kx, ky in keep):
            continue                                 # the crossblade's ring stays open
        ps = set(pts)
        for x, y in pts:
            edge = any((x + dx, y + dy) not in ps and tuple(int(v) for v in a[y + dy, x + dx, :3]) == OUT
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            a[y, x] = HAIR_FILL[1] if edge else HAIR_FILL[0]
    return a


class Parts:
    def __init__(self):
        d = design()
        front, unit, slv = masks(d)
        self.d = d
        self.body = body_of(d, front, unit, slv)
        hand = np.zeros_like(unit)
        for y in range(74, 80):
            for x in range(54, 61):
                if unit[y, x] and not (y == 74 and x <= 55):
                    hand[y, x] = True
        self.unit = sprite_of(d, unit)
        self.hand = sprite_of(d, hand)
        self.blade = sprite_of(d, unit & ~hand)
        self.front = sprite_of(d, front)
        nu, nb, fu, fb = leg_masks(d)
        self.legs = (sprite_of(d, nu), sprite_of(d, nb), sprite_of(d, fu), sprite_of(d, fb))
        nl = self.body.copy()
        nl[nu | nb | fu | fb] = 0
        self.body_nolegs = drop_small(nl, 6)


HIP_ROW = 86                 # the lean bends the body over this row (the belt's bottom)
HEAD_ROWS = (59, 72)         # the head moves whole with the lean (never sheared: square eyes go diagonal)


def lean_shift(y, k):
    """Columns row y moves for a lean k (+ = the top to the left, back)."""
    if y >= HIP_ROW:
        return 0
    if HEAD_ROWS[0] <= y <= HEAD_ROWS[1]:
        y = 70
    return -int(math.floor((HIP_ROW - y) * k + 0.5))


def compose(P, pose):
    """One frame (128 x 128 RGBA, the design's canvas) from a pose:
    unit: (ring x, ring y, deg, z) - the crossblade in the far hand; hand: (cuff x, cuff y, deg) - the far hand empty;
    near: deg (the near arm turned about its shoulder, + up/forward); held: the crossblade in the near hand (deg);
    lean: the upper body sheared back over the hips (+ = head to the left); the parts move with their shoulders."""
    k = pose.get("lean", 0.0)
    sh_far = lean_shift(int(SHOULDER_FAR[1]), k)
    sh_near = lean_shift(int(SHOULDER_NEAR[1]), k)
    can = np.zeros((128, 128, 4), np.uint8)
    back, front = {}, {}
    cuff = None
    shoulder = (SHOULDER_FAR[0] + sh_far, SHOULDER_FAR[1])
    rings = []
    if pose.get("unit"):
        cx, cy, deg, z = pose["unit"]
        cuff = reach(shoulder, (cx + sh_far, cy))
        cells = transform(*P.unit, CUFF, deg, cuff)
        r_ = rot_pt(RING, CUFF, deg)
        rings.append((r_[0] - CUFF[0] + cuff[0], r_[1] - CUFF[1] + cuff[1]))
        (back if z == "back" else front).update(cells)
    elif pose.get("hand"):
        cx, cy, deg = pose["hand"]
        cuff = reach(shoulder, (cx + sh_far, cy))
        front.update(transform(*P.hand, CUFF, deg, cuff))
    if pose.get("blade"):                       # the crossblade alone, the far hand hidden behind it
        bx, by, deg = pose["blade"]
        front.update(transform(*P.blade, RING, deg, (bx + sh_far, by)))
        rings.append((bx + sh_far, by))
    if cuff is not None:
        sl = sleeve(shoulder, cuff)
        layer = back if pose.get("sleeve_z", "front") == "back" else front
        for kk, v in sl.items():
            layer.setdefault(kk, v)
    put(can, back)
    body = P.body
    cells = {}
    for y, x in zip(*np.nonzero(body[..., 3])):
        cells[(x + lean_shift(y, k), y)] = body[y, x]
    put(can, cells)
    put(can, front)
    nd = pose.get("near", 0)
    sn = (SHOULDER_NEAR[0] + sh_near, SHOULDER_NEAR[1])
    put(can, transform(*P.front, SHOULDER_NEAR, nd, sn))
    if pose.get("held") is not None:
        g = rot_pt(GLOVE_NEAR, SHOULDER_NEAR, nd)
        g = (g[0] + sh_near, g[1])
        put(can, transform(*P.blade, RING, pose["held"], (g[0] + 4, g[1] - 2)), under=True)
        rings.append((g[0] + 4, g[1] - 2))
    can = drop_small(can, 4)
    keep = [(int(round(x - 0.5)), int(round(y - 0.5))) for x, y in rings]
    return settle(can, keep, lean_shift(80, k), 0, 128)


def settle(can, keep, shift=0, vshift=0, below=128):
    """Outline closed, the gaps filled (the back's with hair, any other speck with its neighbours' colour; the ring
    stays open), again until closing the outline walls in nothing new - the import closes it once more."""
    for _ in range(6):
        can, _, _ = G.complete_outline(can, color=OUT, feet=99)
        before = can.copy()
        can = fill_back(can, shift, vshift, keep)
        can = fill_flat(can, keep=keep, below=below)
        if (can == before).all():
            break
    return can


IDLE = {"base": "idle"}


def frame(P, pose):
    if pose.get("base") == "idle":
        return P.d.copy()
    return compose(P, pose)


# every frame, in the cells table's order (design coordinates; the ring middle of the idle's blade is (47, 80))
# the unit is placed by its cuff (the far hand) and turned about it: deg + swings the ring down, - up (the idle's ring
# is 12.5 left of the cuff and 4 lower); the cuff stays within ARM_REACH of the far shoulder (61, 73.5)
POSES = {
    "attack": [{"unit": (58.0, 76.5, 0, "front")},                         # 1 the blade drawn back a little
               {"unit": (55.0, 78.0, -10, "front")},                       # 2 wound back
               {"hand": (55.0, 79.0, 0), "near": 35, "held": 0},           # 3 flung out of the near hand (release)
               {"hand": (55.0, 79.0, 0), "near": 40},                      # 4 follow-through, both hands empty
               {"hand": (57.0, 78.0, 0), "near": 15},                      # 5 recovering
               IDLE],                                                      # 6 the blade back at the hip
    "skill": [{"unit": (55.5, 79.0, 20, "front")},                         # 1 low behind
              {"unit": (54.0, 70.0, -45, "front")},                        # 2 back and up
              {"unit": (56.0, 66.0, -75, "front")},                        # 3 up behind her head
              {"hand": (55.0, 79.0, 0), "near": 35}],                      # 4 thrown (release)
    "skill_wait": [{"hand": (54.0, 79.0, 10), "near": 20},
                   {"hand": (54.0, 79.5, 5), "near": 17}],
    "skill_catch": [{"hand": (56.0, 80.0, 0), "near": 80, "held": 0},     # 1 caught overhead in the near hand
                    {"unit": (58.0, 75.0, -10, "front"), "near": 10},    # 2 brought down to the hip
                    IDLE],
    # E: the crossblade raised beside her as League's Spell Shield raises it (held before her it hid the whole body),
    # the near hand up casting; the shield's bubble is the effect round her
    "skill2": [{"unit": (58.0, 74.0, -15, "front"), "near": 15},
               {"unit": (56.0, 70.0, -30, "front"), "near": 30},
               {"unit": (56.0, 69.5, -32, "front"), "near": 30},
               IDLE],
    "ult": [{"unit": (57.5, 79.5, 10, "front")},
            {"unit": (55.5, 67.5, -60, "front")},
            {"unit": (61.5, 65.0, -90, "front")},                          # 3-4 raised over her head
            {"unit": (61.5, 65.0, -95, "front")},
            {"unit": (57.5, 79.0, 5, "front")}],
    "hit": [{"unit": (59.5, 76.0, 0, "front"), "lean": 0.07, "near": 20},
            {"unit": (59.5, 76.0, 0, "front"), "lean": 0.035, "near": 10}],
}


# ---------------------------------------------------------------------------------------------------------------
# the run: the idle's own legs turned about their hips, the boots laid flat on the turned ankles

def leg_masks(d):
    """(near upper, near boot, far upper, far boot) masks of the design's legs (outline squares included)."""
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    near = np.zeros((H, W), bool)
    far = np.zeros((H, W), bool)
    # rows -> the columns of each leg (the loincloth between them stays with the body)
    NEAR = {84: (69, 72), 85: (69, 73), 86: (69, 77), 87: (70, 77), 88: (71, 78), 89: (73, 79), 90: (73, 78),
            91: (73, 78), 92: (74, 80), 93: (75, 81), 94: (77, 83), 95: (77, 84), 96: (77, 84), 97: (77, 85),
            98: (77, 86), 99: (77, 86)}
    FAR = {83: (57, 62), 84: (56, 63), 85: (56, 62), 86: (50, 61), 87: (50, 60), 88: (50, 59), 89: (50, 58),
           90: (48, 57), 91: (47, 56), 92: (46, 52), 93: (45, 51), 94: (44, 51), 95: (42, 51), 96: (41, 51),
           97: (41, 50), 98: (40, 50), 99: (40, 50)}
    for y, (a, b) in NEAR.items():
        near[y, a:b + 1] = op[y, a:b + 1]
    for y, (a, b) in FAR.items():
        far[y, a:b + 1] = op[y, a:b + 1]
    rows = np.arange(H)[:, None] * np.ones((1, W), int)
    near_boot = near & (rows >= 95)
    far_boot = far & (rows >= 94)
    return near & ~near_boot, near_boot, far & ~far_boot, far_boot


NEAR_HIP = (71.5, 84.5)
FAR_HIP = (60.0, 84.0)
NEAR_ANKLE = (80.5, 95.0)
FAR_ANKLE = (48.0, 94.0)


NEAR_LEG_DEG = 43.5          # the idle's legs from straight down (+ = forward, to the right)
FAR_LEG_DEG = -52.8
# per frame: (near angle, near lift, far angle, far lift) - angles from straight down, + = the foot ahead; each foot
# planted ahead (contact), drawn back under the body, off the toe, swung through lifted, reaching ahead; the far leg
# half a cycle behind the near one
RUN = [(25, 0, -25, 1), (13, 0, -9, 3), (-5, 0, 15, 2), (-20, 0, 25, 1),
       (-25, 1, 25, 0), (-5, 3, 10, 0), (15, 2, -5, 0), (25, 1, -20, 0)]
RUN_HIPS = (69.0, 62.5)      # the hips' columns in the run (the idle's 71.5 / 60: the feet must cross)
# the near arm hangs and swings against the near leg (back when the leg is ahead): a straight arm held out ahead
# while running read as a zombie's (Ryze: 「像个僵尸一样」)
RUN_NEAR_ARM = [int(round(-55 - 0.8 * a)) for a, _, _, _ in RUN]
RUN_UNIT = [(59.5, 76.0, 3), (59.5, 76.0, 0), (59.5, 76.5, -3), (59.5, 76.5, -5),
            (59.5, 76.0, -3), (59.5, 76.0, 0), (59.5, 75.5, 3), (59.5, 75.5, 5)]


def run_frame(P, i):
    return stand(P, RUN[i], RUN_UNIT[i], RUN_NEAR_ARM[i])


def stand(P, legs_pose, unit_pose, near_deg, hand=None, blade=True):
    """The design's upper body on its own legs turned to legs_pose (near angle, near lift, far angle, far lift), the
    planted foot on the soles' row; the blade in the far hand (unit_pose: cuff x, cuff y, deg) or the far hand empty
    (hand: cuff x, cuff y, deg), the near arm turned near_deg."""
    nu, nb, fu, fb = P.legs
    na, nl, fa, fl = legs_pose
    can = np.zeros((128, 128, 4), np.uint8)
    legs = {}
    for side, upper, boot, hip0, ankle0, deg0, ang, lift, hx in (
            ("far", fu, fb, FAR_HIP, FAR_ANKLE, FAR_LEG_DEG, fa, fl, RUN_HIPS[1]),
            ("near", nu, nb, NEAR_HIP, NEAR_ANKLE, NEAR_LEG_DEG, na, nl, RUN_HIPS[0])):
        deg = ang - deg0                       # counter-clockwise turn that brings the leg to `ang` (+ forward)
        hip = (hx, hip0[1])
        cells = transform(*upper, hip0, deg, hip)
        ank = rot_pt(ankle0, hip0, deg)
        ank = (ank[0] - hip0[0] + hip[0], ank[1] - hip0[1] + hip[1])
        bs, bo = boot
        if side == "far":                      # the far boot turned toe-forward (mirrored about its ankle)
            bs = bs[:, ::-1].copy()
            bo = (2 * ankle0[0] - (bo[0] + bs.shape[1]), bo[1])
        cells.update({k: v for k, v in transform(bs, bo, ankle0, 0, ank).items()})
        legs[side] = ({(x, y - lift): c for (x, y), c in cells.items()}, lift)
    # the body sits on the planted foot: its lowest square on the soles' row
    planted = [legs[k][0] for k in ("near", "far") if legs[k][1] == 0]
    low = max(y for cells in planted for (_, y) in cells)
    dy = 99 - low
    body = P.body_nolegs
    put(can, {(x, y + dy): c for (x, y), c in legs["far"][0].items()})
    put(can, {(x, y + dy): c for (x, y), c in legs["near"][0].items()})
    # the upper body (the design without its legs), the blade at the back, the near arm swinging
    up = {}
    cx = cy = ud = None
    if blade:
        cx, cy, ud = unit_pose
        up.update(transform(*P.unit, CUFF, ud, (cx, cy)))
    elif hand:
        cx, cy, ud = hand
        up.update(transform(*P.hand, CUFF, ud, (cx, cy)))
    if cx is not None:
        for k, v in sleeve(SHOULDER_FAR, (cx, cy)).items():
            up.setdefault(k, v)
    for yy, xx in zip(*np.nonzero(body[..., 3])):
        up.setdefault((xx, yy), body[yy, xx])
    for k, v in transform(*P.front, SHOULDER_NEAR, near_deg, SHOULDER_NEAR).items():
        up[k] = v
    put(can, {(x, y + dy): c for (x, y), c in up.items()})
    can = drop_small(can, 4)
    ring = (CUFF[0] + (RING[0] - CUFF[0]), CUFF[1] + (RING[1] - CUFF[1]))
    if blade:
        r_ = rot_pt(RING, CUFF, ud)
        ring = (r_[0] - CUFF[0] + cx, r_[1] - CUFF[1] + cy + dy)
        keep = [(int(round(ring[0] - 0.5)), int(round(ring[1] - 0.5)))]
    else:
        keep = []
    return settle(can, keep, 0, dy, 86 + dy)


# ---------------------------------------------------------------------------------------------------------------
# the death: hit, then the whole figure (legs together, the hands empty) falls back and lies on its back; the blade
# drops out of the far hand and lies on the ground behind her

FALL_LEGS = (4, 0, -4, 0)
FALL_HAND = (58.0, 80.0, 0)
FALL_NEAR = -20


def turned(a, deg, joint):
    """The whole frame turned deg (counter-clockwise, + = the head back to the left) about joint; quarter turns exact."""
    ys, xs = np.nonzero(a[..., 3] > 0)
    x0, y0 = xs.min(), ys.min()
    s_ = a[y0:ys.max() + 1, x0:xs.max() + 1]
    cells = transform(s_, (x0, y0), joint, deg, joint)
    out = np.zeros_like(a)
    put(out, cells)
    return out


def on_ground(a, dx=0):
    """The frame moved down (or up) so its lowest square is on the soles' row, and dx columns across."""
    ys, xs = np.nonzero(a[..., 3] > 0)
    dy = 99 - ys.max()
    out = np.zeros_like(a)
    for y, x in zip(ys, xs):
        if 0 <= y + dy < 128 and 0 <= x + dx < 128:
            out[y + dy, x + dx] = a[y, x]
    return out


# the head as the strips paste it (rows -> columns), the same squares as fix_strips_sv.HEAD
HEAD = {60: (65, 73), 61: (60, 74), 62: (60, 75), 63: (58, 75), 64: (55, 75), 65: (54, 75), 66: (53, 75),
        67: (56, 75), 68: (55, 75), 69: (53, 75), 70: (53, 75), 71: (53, 75), 72: (53, 73)}


def head_mask(shape):
    m = np.zeros(shape[:2], bool)
    for r, (c0, c1) in HEAD.items():
        m[r, c0:c1 + 1] = True
    return m


def lying(P):
    """Sivir on her back (the accepted Kennen/Tristana death: the design's whole figure turned a quarter): the upright
    figure with the legs together, the near arm along the body and the far hand under her, turned counter-clockwise
    (the head to the left, the face up, the boots' toes up at the right)."""
    fig = stand(P, (2, 0, -2, 0), None, -55, hand=None, blade=False)    # the far arm lies under her
    fig = drop_small(fig, 6)
    ys, xs = np.nonzero(fig[..., 3] > 0)
    sub = fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rot = np.rot90(sub, 1).copy()
    out = np.zeros((128, 128, 4), np.uint8)
    h, w = rot.shape[:2]
    x0 = 64 - w // 2 + 2
    y0 = 99 - h + 1
    out[y0:y0 + h, x0:x0 + w] = rot
    return out


def squash(a, keep_every=2.5):
    """A sprite seen from above at a low angle: rows kept every keep_every (the crossblade lying flat)."""
    rows = sorted({int(round(k * keep_every)) for k in range(int(a.shape[0] / keep_every) + 1)
                   if int(round(k * keep_every)) < a.shape[0]})
    return a[rows]


# per frame: what the death shows
DEAD = ["hit", "knocked", ("tilt", 45), ("lying", 1), ("lying", 0), ("lying", 0), ("lying", 0), ("lying", 0)]
DEAD_BLADE_AT = (30.0, 99)     # the crossblade lying flat on the ground behind her head: its middle column, lowest row


def dead_frame(P, i):
    what = DEAD[i]
    if what == "hit":
        return compose(P, POSES["hit"][0])
    if what == "knocked":
        return compose(P, {"hand": (57.0, 79.0, 0), "lean": 0.11, "near": 35, "blade": (44.0, 88.0, 25)})
    out = np.zeros((128, 128, 4), np.uint8)
    if what[0] == "tilt":                       # falling back: the standing figure turned half way, in the air
        fig = stand(P, (2, 0, -2, 0), None, -50, hand=(58.0, 81.0, 0), blade=False)
        fig = turned(fig, what[1], (60.0, 99.0))
        fig = on_ground(fig, -4)
        fig = np.roll(fig, -3, 0)
        put(out, transform(*P.blade, RING, 60, (40.0, 89.0)))
        put(out, {(x, y): fig[y, x] for y, x in zip(*np.nonzero(fig[..., 3]))})
        out, _, _ = G.complete_outline(out, color=OUT, feet=99)
        out = fill_flat(out, keep=[(40, 89)])
    else:
        _, lift = what
        bs, bo = P.blade
        flat = squash(bs)
        ys, xs = np.nonzero(flat[..., 3] > 0)
        bx = int(round(DEAD_BLADE_AT[0] - (xs.min() + xs.max()) / 2))
        by = DEAD_BLADE_AT[1] - ys.max()
        for y, x in zip(ys, xs):
            out[by + y, bx + x] = flat[y, x]
        body = lying(P)
        if lift:
            body = np.roll(body, -lift, 0)
        put(out, {(x, y): body[y, x] for y, x in zip(*np.nonzero(body[..., 3]))})
    out = drop_small(out, 4)
    # the lying legs lie together: no gap between the shins and the boots (the blade's ring on the ground stays)
    for _ in range(6):
        out, _, _ = G.complete_outline(out, color=OUT, feet=99)
        before = out.copy()
        ring_keep = [(int(DEAD_BLADE_AT[0]) + dx, y) for dx in range(-3, 4) for y in range(90, 100)]
        out = fill_flat(out, keep=ring_keep)
        if (out == before).all():
            break
    return out


def review(P, tags, name, z=6):
    imgs = []
    for t in tags:
        r = [("idle", P.d)] + [(f"{t} {i + 1}", frame(P, p)) for i, p in enumerate(POSES[t])]
        ims = []
        for lab, a in r:
            sub = a[38:102, 30:106]
            im = Image.fromarray(sub).resize((sub.shape[1] * z, sub.shape[0] * z), Image.NEAREST)
            bg = Image.new("RGBA", (im.width, im.height + 18), (92, 98, 86, 255))
            bg.alpha_composite(im, (0, 18))
            dr = ImageDraw.Draw(bg)
            dr.text((3, 2), lab, fill=(255, 255, 255, 255))
            dr.line([(0, 18 + (99 - 38 + 1) * z), (bg.width, 18 + (99 - 38 + 1) * z)], fill=(220, 40, 40, 255))
            ims.append(bg)
        imgs.append(ims)
    W = max(sum(i.width + 6 for i in r) for r in imgs)
    H = sum(max(i.height for i in r) + 6 for r in imgs)
    out = Image.new("RGB", (W, H), (30, 30, 30))
    y = 0
    for r in imgs:
        x = 0
        for i in r:
            out.paste(i.convert("RGB"), (x, y))
            x += i.width + 6
        y += max(i.height for i in r) + 6
    os.makedirs(TMP, exist_ok=True)
    out.save(os.path.join(TMP, name))
    return out.size


CELLS_JSON = os.path.join(SV, "assets", "source", "native", "sivir_cells.json")
OUT_DIR = os.path.join(SV, "assets", "source", "native")
PIV = (57, 56)
Z = 8


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def frames_of(P, tag, n):
    if tag == "run":                    # the run v2 (League's run, drawn legs): tools/art/rig_sivir_run.py
        import rig_sivir_run
        return [rig_sivir_run.run_frame(P, i) for i in range(n)]
    if tag == "dead":
        return [dead_frame(P, i) for i in range(n)]
    return [frame(P, p) for p in POSES[tag]]


def build():
    cells = json.load(open(CELLS_JSON, encoding="utf-8"))
    CW, CH = cells["cell"]
    P = Parts()
    os.makedirs(OUT_DIR, exist_ok=True)
    idle_head = cells["tags"]["idle"][0]["head"]
    for tag, rows in cells["tags"].items():
        if tag == "idle":
            continue
        fr = frames_of(P, tag, len(rows))
        assert len(fr) == len(rows), (tag, len(fr), len(rows))
        c, r = layout(len(fr))
        sheet = np.zeros((r * CH, c * CW, 4), np.uint8)
        for i, a in enumerate(fr):
            ys, xs = np.nonzero(a[..., 3] > 0)
            ox, oy = PIV[0] - 64, PIV[1] - 88
            if xs.min() + ox < 0 or xs.max() + ox >= CW or ys.min() + oy < 0 or ys.max() + oy >= CH:
                print("OUT OF CELL", tag, i + 1, xs.min() + ox, xs.max() + ox, ys.min() + oy, ys.max() + oy)
            X0, Y0 = (i % c) * CW, (i // c) * CH
            for y, x in zip(ys, xs):
                ty, tx = y + oy, x + ox
                if 0 <= ty < CH and 0 <= tx < CW:
                    sheet[Y0 + ty, X0 + tx] = a[y, x]
            rows[i]["pivot"] = list(PIV)
            rows[i]["head"] = idle_head
        Image.fromarray(np.repeat(np.repeat(sheet, Z, 0), Z, 1)).save(os.path.join(OUT_DIR, f"sivir_{tag}.png"))
        print(tag, len(fr), "frames")
    with open(CELLS_JSON, "w", encoding="utf-8") as f:
        json.dump(cells, f, indent=1)



if __name__ == "__main__":
    import json  # noqa: E402
    build()
    if "--review" in sys.argv:
        print(review(Parts(), ["attack", "skill", "skill_wait", "skill_catch", "skill2", "ult", "hit"], "review.png"))
