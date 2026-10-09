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

SRC = os.path.join(ROOT, "assets", "source", "olaf", "codex_strips_v2")
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


def codex(tag):
    """Codex's frames of a tag on 128 canvases (pivot on PIVOT), their durations and Codex's eye estimates there."""
    man = json.load(open(K.lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))["animations"][tag]["frames"]
    out, ms, eyes = [], [], []
    for f in man:
        cell = np.asarray(Image.open(K.lp(os.path.join(SRC, "native", f"olaf_{tag}_{f['frame']:02d}.png")))
                          .convert("RGBA")).copy()
        cell[cell[..., 3] < 128] = 0
        c = np.zeros((128, 128, 4), np.uint8)
        ox, oy = PIVOT[0] - f["pivot"][0], PIVOT[1] - f["pivot"][1]
        K.put(c, cell, ox, oy)
        c[SOLES + 1:] = 0
        out.append(c)
        ms.append(f["ms"])
        h = f["head"]
        eyes.append(((h["eye_left"][0] + h["eye_right"][0]) / 2 + ox, h["eye_left"][1] + oy))
    return out, ms, eyes


def head_place(c, des, hm, guess):
    """(score, dx, dy): where the design's head piece sits best in c, searched round Codex's eye estimate. The helmet
    and horns should land on Codex's helmet (steel on steel; on the mane is fair, on the body or on nothing is wrong),
    the face on Codex's face or beard; where Codex drew eyes or a mouth, the design's go on them."""
    ys, xs = np.nonzero(hm)
    want = kind(des)[ys, xs]
    steel = (want == 2) | (want == 3)
    face = (want >= 5) & ~steel
    have = kind(c)
    ex = (EYES[0][1] + EYES[1][1]) / 2
    gx, gy = int(round(guess[0] - ex)), int(round(guess[1] - EYES[0][0]))
    best = (-9.0, gx, gy)
    for dy in range(gy - SEARCH, gy + SEARCH + 1):
        for dx in range(gx - SEARCH, gx + SEARCH + 1):
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


def build(P, tag, report=None):
    frames, ms, eyes = codex(tag)
    hm = head_piece(P)
    mid = face_spot(P.design)
    out = []
    for i, c in enumerate(frames):
        k = i + 1
        if (tag, k) in KEEP_HEAD:
            out.append(tidy(c))
            continue
        spot = face_spot(c)
        s, dx, dy = head_place(c, P.design, hm, eyes[i])
        if (tag, k) in HEAD_AT:
            s, (dx, dy) = None, HEAD_AT[(tag, k)]
        elif spot is not None:                          # the design's face on Codex's face, near the helmet's match
            fx, fy = int(round(spot[1] - mid[1])), int(round(spot[0] - mid[0]))
            if max(abs(fx - dx), abs(fy - dy)) <= FACE_OFF:
                s, dx, dy = "face", fx, fy
        if report is not None:
            report.append((tag, k, dx, dy, s if s is None or isinstance(s, str) else round(s, 2)))
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
