#!/usr/bin/env python3
"""Olaf's action strips from Codex's whole-figure redraw (2026-10-09, assets/source/olaf/codex_strips_v2).

    python tools/art/fix_olaf_strips.py [--check] [--review DIR] [--no-write] [--heads]

The user on the rig's strips (rig_olaf.py: the design's parts, only the arms moving): 「身体太奇怪了吧。。。和英雄联盟也
不一样啊」; the pick: 「Codex 照英雄联盟逐帧重画」 (MODEL_STRIPS_v2.md, the way Karma's strips passed). Codex drew every
frame whole from League's poses; its heads differ from frame to frame (the helmet's shape, the horns, the face mostly
lost in its grid export), so every upright frame gets the approved design's head at the place Codex drew its head -
the head stays where the body puts it:
1. Codex's frame on the 128 canvas, its standing point on the design's (64, 88);
2. the head's place: where Codex drew eyes and a mouth, the design's face goes on them (face_spot); else the design's
   head piece (head_piece: the horns, the helmet with its brim, the hair crest on top and the face - not the mane, the
   beard or the shoulder fur, which stay Codex's) slid over the frame round where Codex says its eyes are, its helmet
   on Codex's helmet (head_place); HEAD_AT overrides both;
3. Codex's own helmet goes: the squares under the piece, and round it every small piece of steel squares left over (a
   horn tip, a rim) - an axe is bigger and stays; Codex's eyes or mouth left beside the design's face take the colour
   round them;
4. the design's head on top, except where Codex drew something in front of it (FRONT boxes: the axes crossed before
   the face in Ragnarok);
5. Codex's dark leather mapped to the outline colour (thick near-black blobs: the boots, the vest's shade) gets the
   design's dark leather inside; pinholes up to 4 squares filled, one-square nicks closed with outline (they would
   be pinholes after import_native's outline pass), stray outline specks dropped.
KEEP_HEAD frames keep Codex's own head (Ragnarok's roar behind the crossed axes - axes and helmet drawn as one
there; kneeling with the head thrown back or bowed; lying on his front).
The idle is rig_olaf's (the design breathing over its boots). Writes assets/source/native/olaf_<tag>.png (8x, 112x96
cells, soles on cell row 81) and olaf_cells.json; then tools/art/import_native.py.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402
import strips as G  # noqa: E402
import rig_olaf as RO  # noqa: E402

# Codex's League-driven redraw (approved with the design's head 2026-10-09): where every frame's head goes
SRC_V2 = os.path.join(ROOT, "assets", "source", "olaf", "codex_strips_v2")
# the same frames redrawn with the slimmer, more muscular body (「奥拉夫稍微瘦一点 肌肉明显点」, design B): the frames
SRC_SLIM = os.path.join(ROOT, "assets", "source", "olaf", "codex_strips_slim")
# every action redrawn at the slim idle's size and a calm run (the user: 「跑动时为什么变大一圈」「跑动姿势太浮夸了吧」,
# then 「新版做完了 奇怪的地方你帮我调吧」): the frames
SRC = os.path.join(ROOT, "assets", "source", "olaf", "codex_strips_size")
# ... except the hit: Codex redrew it thin (narrow limbs and torso, its own head smaller), a big head on a small body
# once the design's head is on it - the approved slim hit instead, made smaller in import_native (SHRINK_TAGS)
# ... and the run: Codex's cross-step on the guide (codex_run_cross: 「你看看对吗 交叉步都没有？」, then 「Codex 重画跑步」)
SRC_CROSS = os.path.join(ROOT, "assets", "source", "olaf", "codex_run_cross")
TAG_SRC = {"hit": SRC_SLIM, "run": SRC_CROSS}
RUN_DROP = {6}                     # Codex's cross-step frames left out (1-based)
REFINE = 7                        # squares the head may move from its approved place (the bodies shrank: heads sit lower)
NEW_POSE = {"run"}                 # tags drawn anew (the calm run): the head goes where Codex drew it
RUN_AT, RUN_SEARCH = (0, 1), 3     # ... found within RUN_SEARCH squares of RUN_AT (the design's head, a row down)
# Codex's calm run keeps its image-right boot planted in all 8 frames and steps on the spot with the other (kicked
# back in 1/5, down in 3/4/7/8): no boot moves back under the walking body, so he slid over the ground (the user:
# 「走路对吗？ 感觉像在平移」). Its legs are redrawn on a step cycle (run_steps), both from Codex's frame 3 (both boots
# down): a planted boot slides back 2 columns a frame for 4 frames, then lifts and swings forward for 4, the legs half
# a cycle apart and landing on the frames where Codex's body dips (4 and 8); each leg leans with its boot (sheared
# from the hip), the boot moves whole and covers the greave's lowest rows when it lifts or the body dips (lossless).
# The legs stay apart under the wide 3/4 body: brought in to cross like a side view, they stood on one post.
RUN_BASE = 2                                   # Codex's frame 3
RUN_HIP = 86                                   # the legs' top row there
RUN_LEGS = {"L": [(86, 86, 55, 60), (87, 89, 51, 60), (90, 98, 47, 58)],     # (row0, row1, col0, col1) boxes
            "R": [(86, 89, 66, 71), (90, 98, 62, 74)]}
RUN_ANKLES = {"L": 94, "R": 95}                # each leg's first boot row there
RUN_FLAP = (86, 89, 60, 65)                    # the loincloth's flap between the thighs
RUN_SINK = 1                                   # every frame a row lower: frame 3's legs (13 rows) reach the ground
RUN_UP = [0, 0, 0, 1, 0, 0, 0, 0]              # frame 4 dips 3 rows, frame 8 two: frame 4's body lifted 1
RUN_DIP = [0, 0, 0, 2, 0, 0, 0, 2]             # the body's dip per frame (the legs' top follows it)
# a boot's place on its cycle: (columns from its frame-3 place, + = forward; rows off the ground) - planted 4 frames
# sliding back, then toe-off, through, reach. The image-right boot steps ahead of its frame-3 place and the image-left
# one behind (Codex's front and back legs): one cycle for both, the near one meeting the far one's heel at the pass,
# put the two boots side by side in one dark block (frames 7-8)
RUN_CYCLE = {"R": [(4, 0), (2, 0), (0, 0), (-1, 0), (-1, 2), (1, 3), (3, 3), (4, 1)],
             "L": [(1, 0), (0, 0), (-2, 0), (-4, 0), (-4, 2), (-2, 3), (0, 3), (1, 1)]}
RUN_LAND = {"R": 3, "L": 7}                    # the frame (0-based) each leg lands on
# Codex's own legs go: every square from the legs' top row down in columns up to RUN_CLEAR[0], and from row
# RUN_CLEAR[2] in columns up to RUN_CLEAR[1] (the image-right boot's toe) - not the axe held low at the right; the
# left fist hanging into the dipped frames' cut stays (RUN_KEEP boxes, on the frame as shifted)
RUN_CLEAR = (72, 75, 91)
RUN_KEEP = {3: [(85, 89, 48, 55)], 7: [(84, 90, 48, 56)]}
NATIVE = RO.NATIVE
C = RO.C
OUT = RO.OUT
PIVOT = RO.PIVOT
SOLES = RO.SOLES
CELL = RO.CELL
CELL_PIVOT = RO.CELL_PIVOT
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
CODEX_TAGS = TAGS[1:]
STEEL = set("dgGhwW")
ORANGE = set("rRoO")
FACE = set("KSkeEmtpbB")
EYES = ((71, 68), (71, 70))        # the design's eyes on the canvas
SEARCH = 7                         # squares round Codex's own eye estimate
FACE_OFF = 9                       # Codex's face is trusted this near the helmet's match
LEFTOVER = 14                      # a steel piece this small round the pasted head is Codex's helmet, it goes
KEEP_HEAD = {("ult", 3), ("ult", 4), ("dead", 3), ("dead", 5), ("dead", 6), ("dead", 7), ("dead", 8)}
HEAD_AT = {}                       # (tag, frame): (dx, dy) of the design's head on the canvas, where the match misses
# the run's heads ride its torsos: frame 3's head place (0, 2) moved as each torso (rows 66-86) sits against frame 3's -
# searched per frame, the head rose a row alone in frame 6 and slid a column against the body in 1, 2 and 7
if "run" not in TAG_SRC:         # (the stepping run's torsos only; Codex's cross-step heads are searched)
    for _k, _at in enumerate([(2, 2), (0, 2), (0, 2), (0, 4), (0, 2), (0, 2), (1, 2), (0, 4)], 1):
        HEAD_AT[("run", _k)] = _at
FRONT = {}                         # (tag, frame): [(row0, row1, col0, col1)] boxes where Codex's squares stay on top


def head_piece(P):
    """The design's head (canvas mask): the horns, the helmet and its brim, the crest on top, the face; plus the outline
    squares round them."""
    keep = set()
    for (y, x), c in P.g.items():
        if 58 <= y <= 69 and x >= 57 and c in STEEL:
            keep.add((y, x))
        elif 58 <= y <= 64 and 61 <= x <= 67 and c in ORANGE:
            keep.add((y, x))
        elif 70 <= y <= 75 and 63 <= x <= 72 and c != "0" and c not in ORANGE:
            keep.add((y, x))
    ring = set()
    for (y, x), c in P.g.items():
        if c == "0" and 57 <= y <= 76 and any((y + dy, x + dx) in keep for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            ring.add((y, x))
    m = np.zeros((128, 128), bool)
    for y, x in keep | ring:
        m[y, x] = True
    return m


def kind(a):
    """Each square's kind of colour: 0 clear, 1 outline, 2 dark steel, 3 light steel, 4 orange, 5 skin, 6 leather,
    7 face-only."""
    k = np.zeros(a.shape[:2], np.int8)
    groups = [("0", 1), ("dg", 2), ("GhwW", 3), ("rRoO", 4), ("kKS", 5), ("bBn", 6), ("eEmtp", 7)]
    for letters, v in groups:
        for ch in letters:
            k[(a[..., :3] == np.array(C[ch], np.uint8)).all(-1) & (a[..., 3] > 0)] = v
    return k


def codex(tag, src=None):
    """Codex's frames of a tag on 128 canvases (pivot on PIVOT), their durations and Codex's eye estimates there (the
    eyes' middle, else 3 rows over the mouth, else None)."""
    src = src or SRC
    man = json.load(open(K.lp(os.path.join(src, "manifest.json")), encoding="utf-8"))["animations"][tag]["frames"]
    out, ms, eyes = [], [], []
    for f in man:
        cell = np.asarray(Image.open(K.lp(os.path.join(src, "native", f"olaf_{tag}_{f['frame']:02d}.png")))
                          .convert("RGBA")).copy()
        cell[cell[..., 3] < 128] = 0
        c = np.zeros((128, 128, 4), np.uint8)
        ox, oy = PIVOT[0] - f["pivot"][0], PIVOT[1] - f["pivot"][1]
        K.put(c, cell, ox, oy)
        c[SOLES + 1:] = 0
        out.append(c)
        ms.append(f["ms"])
        h = f["head"]
        if h.get("eye_left") and h.get("eye_right"):
            eyes.append(((h["eye_left"][0] + h["eye_right"][0]) / 2 + ox, h["eye_left"][1] + oy))
        elif h.get("mouth"):
            eyes.append((h["mouth"][0] + ox, h["mouth"][1] - 3 + oy))
        else:
            eyes.append(None)
    return out, ms, eyes


def head_place(c, des, hm, guess, at=None, search=None):
    """(score, dx, dy): where the design's head piece sits best in c, searched round Codex's eye estimate. The helmet
    and horns should land on Codex's helmet (steel on steel; on the mane is fair, on the body or on nothing is wrong),
    the face on Codex's face or beard; where Codex drew eyes or a mouth, the design's go on them."""
    ys, xs = np.nonzero(hm)
    want = kind(des)[ys, xs]
    steel = (want == 2) | (want == 3)
    face = (want >= 5) & ~steel
    have = kind(c)
    ex = (EYES[0][1] + EYES[1][1]) / 2
    if at is not None:                  # round a known place (the approved frame's head)
        gx, gy = at
    else:
        gx, gy = int(round(guess[0] - ex)), int(round(guess[1] - EYES[0][0]))
    r = SEARCH if search is None else search
    best = (-9.0, gx, gy)
    for dy in range(gy - r, gy + r + 1):
        for dx in range(gx - r, gx + r + 1):
            yy, xx = ys + dy, xs + dx
            ok = (yy >= 0) & (yy < 128) & (xx >= 0) & (xx < 128)
            h = np.zeros(len(ys), np.int8)
            h[ok] = have[yy[ok], xx[ok]]
            hs = (h == 2) | (h == 3)
            s = (1.0 * (steel & hs).sum() + 0.3 * (steel & (h == 4)).sum() - 0.6 * (steel & ((h == 5) | (h == 6))).sum()
                 - 0.4 * (steel & (h == 0)).sum() + 0.5 * (face & ((h >= 4) | (h == 1))).sum()
                 - 0.6 * (face & (h == 0)).sum() + 0.2 * ((want == 1) & (h == 1)).sum()
                 + 3.0 * ((want == 7) & (h == 7)).sum())
            s /= len(ys)
            if s > best[0]:
                best = (float(s), dx, dy)
    return best


def face_spot(c, least=3):
    """The middle of Codex's own face, or None: the face-only squares round the one with the most of them within 4
    squares, when they hold an eye (blue) and a mouth (red) - Codex's export left lone ones on the axes and the boots."""
    k = kind(c)
    ys, xs = np.nonzero(k == 7)
    if len(ys) < least:
        return None
    pts = np.stack([ys, xs], 1)
    near = (np.abs(pts[:, None, :] - pts[None, :, :]).max(-1) <= 4)
    best = near.sum(1).argmax()
    grp = pts[near[best]]
    blue = sum(1 for y, x in grp if tuple(c[y, x, :3]) in (C["e"], C["E"]))
    red = sum(1 for y, x in grp if tuple(c[y, x, :3]) in (C["m"], C["p"]))
    if len(grp) < least or not blue or not red:
        return None
    return grp.mean(0)


def with_head(P, c, hm, at, front=()):
    """c with Codex's helmet swapped for the design's head piece at offset `at`."""
    dx, dy = at
    piece = K.shifted(np.where(hm[..., None], P.design, 0).astype(np.uint8), dx, dy)
    put = piece[..., 3] > 0
    ys, xs = np.nonzero(put)
    box = np.zeros((128, 128), bool)
    box[max(0, ys.min() - 3):ys.max() + 4, max(0, xs.min() - 3):xs.max() + 4] = True
    out = c.copy()
    keep_front = np.zeros((128, 128), bool)
    for r0, r1, c0, c1 in front:
        keep_front[r0:r1 + 1, c0:c1 + 1] = True
    keep_front &= c[..., 3] > 0
    out[put & ~keep_front] = 0
    # Codex's helmet left round the piece: small pieces of steel and outline squares
    kd = kind(out)
    rest = out.copy()
    rest[~box] = 0
    for comp in K.pieces(rest):
        steel = sum(1 for y, x in comp if kd[y, x] in (1, 2, 3))
        if len(comp) <= LEFTOVER and steel == len(comp):
            for y, x in comp:
                out[y, x] = 0
    # Codex's own eyes and mouth left beside the design's face (a second face): the colour round them
    kd = kind(out)
    for y, x in zip(*np.nonzero(box & ~put & (kd == 7))):
        nb = [tuple(int(v) for v in out[y + dy, x + dx]) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if out[y + dy, x + dx, 3] and kd[y + dy, x + dx] not in (1, 7)]
        if nb:
            out[y, x] = max(set(nb), key=nb.count)
        else:
            out[y, x, :3] = OUT
    m = put & ~keep_front
    out[m] = piece[m]
    return out


def leather(f):
    """Codex mapped its dark leather (the boots, the vest's shade) to the outline colour: blobs of outline squares two
    or more thick. Their squares with no clear square round them take the design's dark leather (b); one-square lines
    and the silhouette's edge stay outline."""
    op = f[..., 3] > 0
    ink = op & (f[..., :3] == np.array(OUT, np.uint8)).all(-1)
    thick = np.zeros_like(ink)
    for dy in (0, -1):
        for dx in (0, -1):
            blk = ink.copy()
            for a_, b_ in ((0, 1), (1, 0), (1, 1)):
                blk &= np.roll(np.roll(ink, -a_, 0), -b_, 1)
            thick |= np.roll(np.roll(blk, -dy, 0), -dx, 1)
    inside = op.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            inside &= np.roll(np.roll(op, dy, 0), dx, 1)
    out = f.copy()
    out[thick & ink & inside, :3] = C["b"]
    return out


def notches(f, rounds=2):
    """Clear squares with three or four of their four neighbours filled (the seams where the design's head meets
    Codex's body, Codex's own one-square nicks) become outline: import_native's outline pass would close them into
    see-through pinholes."""
    out = f.copy()
    for _ in range(rounds):
        op = out[..., 3] > 0
        n = np.zeros(op.shape, np.int8)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n += np.roll(np.roll(op, dy, 0), dx, 1)
        m = ~op & (n >= 3)
        m[SOLES + 1:] = False
        if not m.any():
            break
        out[m, :3] = OUT
        out[m, 3] = 255
    return out


def run_leg(base, m, ankle, dip, dx, lift):
    """One leg of the base frame posed: the rows above its ankle dropped with the body (dip + RUN_SINK) and shifted in
    proportion to dx from the hip, the boot moved dx whole with its sole on the ground row less `lift`."""
    shin = np.zeros_like(base)
    boot = np.zeros_like(base)
    sole = np.nonzero(m.any(1))[0].max()
    for r, c in zip(*np.nonzero(m)):
        if r < ankle:
            sh = int(np.floor(dx * max(0, r - RUN_HIP) / max(1, ankle - RUN_HIP) + 0.5))
            rr, tgt = r + dip + RUN_SINK, shin
        else:
            sh = dx
            rr, tgt = r + (SOLES - sole) - lift, boot
        if 0 <= rr <= SOLES and 0 <= c + sh < base.shape[1]:
            tgt[rr, c + sh] = base[r, c]
    return K.put(shin, boot, 0, 0)


def run_steps(frames):
    """Codex's run frames with the legs on the step cycle (RUN_CYCLE), drawn from its frame 3: the far (image-right)
    leg, the flap, the near (image-left) leg over them."""
    base = frames[RUN_BASE]
    op = base[..., 3] > 0
    parts = {}
    for name, boxes in RUN_LEGS.items():
        m = np.zeros(op.shape, bool)
        for r0, r1, c0, c1 in boxes:
            m[r0:r1 + 1, c0:c1 + 1] = True
        parts[name] = m & op
    r0, r1, c0, c1 = RUN_FLAP
    flap = np.zeros(op.shape, bool)
    flap[r0:r1 + 1, c0:c1 + 1] = True
    flap = np.where((flap & op)[..., None], base, 0).astype(np.uint8)
    out = []
    for i, c in enumerate(frames):
        body = K.shifted(c, 0, RUN_SINK - RUN_UP[i])
        cut = RUN_HIP + RUN_DIP[i] + RUN_SINK
        gone = np.zeros(op.shape, bool)
        gone[cut:, :RUN_CLEAR[0] + 1] = True
        gone[RUN_CLEAR[2]:, :RUN_CLEAR[1] + 1] = True
        for k0, k1, j0, j1 in RUN_KEEP.get(i, ()):
            gone[k0:k1 + 1, j0:j1 + 1] = False
        body[gone] = 0
        for name in ("R", "flap", "L"):
            if name == "flap":
                body = K.put(body, K.shifted(flap, 0, RUN_DIP[i] + RUN_SINK), 0, 0)
                continue
            dx, lift = RUN_CYCLE[name][(i - RUN_LAND[name]) % 8]
            body = K.put(body, run_leg(base, parts[name], RUN_ANKLES[name], RUN_DIP[i], dx, lift), 0, 0)
        out.append(body)
    return out


def tidy(f):
    """Leather, pinholes, nicks; then the outline closed here as import_native's COMPLETE pass would (strips.
    complete_outline) and the pinholes that closing makes filled, so the import finds nothing left to close."""
    f = notches(K.fill_pinholes(leather(f), 4, OUT))
    f, _, _ = G.complete_outline(f, color=OUT, dark=70, feet=SOLES)
    return drop_orphans(K.fill_pinholes(f, 4, OUT))


def drop_orphans(f):
    """Specks: outline-coloured pieces (8-connected among themselves) of at most 3 squares with no coloured square
    round them. Codex's boots are near-black blobs of outline squares joined to the greaves - they stay."""
    op = f[..., 3] > 0
    ink = op & (f[..., :3] == np.array(OUT, np.uint8)).all(-1)
    col = op & ~ink
    near = np.zeros_like(col)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            near |= np.roll(np.roll(col, dy, 0), dx, 1)
    only = np.where(ink[..., None], f, 0).astype(np.uint8)
    out = f.copy()
    for comp in K.pieces(only):
        if len(comp) <= 3 and not any(near[y, x] for y, x in comp):
            for y, x in comp:
                out[y, x] = 0
    return out


def places(P, tag, src=None):
    """Where the design's head went on the approved frames (Codex's v2 redraw, or `src`): (dx, dy) per frame, None
    where the frame keeps Codex's own head."""
    frames, ms, eyes = codex(tag, src or SRC_V2)
    hm = head_piece(P)
    mid = face_spot(P.design)
    out = []
    for i, c in enumerate(frames):
        k = i + 1
        if (tag, k) in KEEP_HEAD:
            out.append(None)
            continue
        spot = face_spot(c)
        if eyes[i] is None:                             # Codex found no eye or mouth: the frame's middle top
            ys, xs = np.nonzero(c[..., 3] > 0)
            eyes[i] = ((xs.min() + xs.max()) / 2, ys.min() + 13)
        s, dx, dy = head_place(c, P.design, hm, eyes[i])
        if (tag, k) in HEAD_AT:
            dx, dy = HEAD_AT[(tag, k)]
        elif spot is not None:                          # the design's face on Codex's face, near the helmet's match
            fx, fy = int(round(spot[1] - mid[1])), int(round(spot[0] - mid[0]))
            if max(abs(fx - dx), abs(fy - dy)) <= FACE_OFF:
                dx, dy = fx, fy
        out.append((dx, dy))
    return out


def build(P, tag, report=None):
    """The slim frames with the design's head where the approved frame had it, moved at most REFINE squares to sit on
    the slim body's own helmet."""
    new = tag in NEW_POSE
    # the calm run is upright: Codex's head sits near the design's place, bobbing - searched round it (a free search
    # took the mane beside the helmet for the helmet and left two heads)
    frames, ms, _ = codex(tag, TAG_SRC.get(tag))
    if tag == "run" and "run" not in TAG_SRC:
        frames = run_steps(frames)
    elif tag == "run":
        # Codex's cross-step stood frames 5-8 two rows off the ground (its own frame calibration); one boot is down
        # in every frame of the cycle, so each frame's lowest square goes on the soles' row
        frames = [K.shifted(c, 0, SOLES - int(np.nonzero((c[..., 3] > 0).any(1))[0].max())) for c in frames]
        # its frame 6 lifts the boot that landed in 4 to the knee and puts the other one down early, then frame 7 has
        # them back (a hop): frame 7 is what 6 should be, so 6 goes - the planted boot slides +8.5, +6.5, +4 over
        # frames 4, 5 and 7, the other passes and lands in 8
        frames = [c for k, c in enumerate(frames) if k + 1 not in RUN_DROP]
        ms = [m for k, m in enumerate(ms) if k + 1 not in RUN_DROP]
    at = [None if (tag, i + 1) in KEEP_HEAD else RUN_AT for i in range(len(frames))] if new else places(P, tag)
    hm = head_piece(P)
    mid = face_spot(P.design)
    out = []
    for i, c in enumerate(frames):
        k = i + 1
        if at[i] is None:
            out.append(tidy(c))
            continue
        s, dx, dy = head_place(c, P.design, hm, None, at=at[i], search=RUN_SEARCH if new else REFINE)
        spot = None if new else face_spot(c)
        if spot is not None:                            # Codex drew eyes and a mouth: the design's face on them
            fx, fy = int(round(spot[1] - mid[1])), int(round(spot[0] - mid[0]))
            if max(abs(fx - at[i][0]), abs(fy - at[i][1])) <= REFINE + 2:
                s, dx, dy = "face", fx, fy
        if (tag, k) in HEAD_AT:
            s, (dx, dy) = None, HEAD_AT[(tag, k)]
        if report is not None:
            report.append((tag, k, at[i], (dx, dy), s if s is None or isinstance(s, str) else round(s, 2)))
        out.append(tidy(with_head(P, c, hm, (dx, dy), FRONT.get((tag, k), ()))))
    return out, ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a review sheet and GIF into this folder")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--heads", action="store_true", help="print where each frame's head went")
    a = ap.parse_args()
    P = RO.Parts()                     # the design now: the idle breathes it
    H = RO.Parts(RO.FINAL_42)          # the head pasted on every frame is the first approved design's (unchanged)
    built = {"idle": [RO.breath(P, n) for n in RO.BREATH]}
    ms = {"idle": RO.ms_of("idle")}
    report = []
    for tag in CODEX_TAGS:
        built[tag], ms[tag] = build(H, tag, report)
    if a.heads:
        for r in report:
            print(r)
    for tag in TAGS:
        rows = K.audit(built[tag], P.design, OUT, SOLES)
        print(f"{tag:8s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}" for r in rows))
    if not a.no_write:
        bad = K.write_strips("olaf", built, ms, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        if a.check:
            print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "olaf_fix_review.png"), z=4, soles=SOLES)
        K.review_gif([(t, built[t]) for t in TAGS], ms, os.path.join(a.review, "olaf_fix_review.gif"), z=4)
    return built


if __name__ == "__main__":
    main()
