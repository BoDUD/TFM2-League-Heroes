#!/usr/bin/env python3
"""Tidy Codex's step-2 redraw of the 18 heroes (model_strips_18: every strip drawn from the approved design) into
the native strips.

    python tools/art/tidy_codex18.py <hero> <Codex's delivery folder>

Codex delivers <hero>_<tag>.png for every tag of assets/source/native/<hero>_cells.json, on the same cells, every
game pixel an 8x8 block, the design's palette and its head pasted into every frame. One thing is fixed here on the
game pixels before the strips are written to assets/source/native/: the doubled outline. A study of the LoL Reborn
pack (oppi) against ours found our designs use black as the shadow tone, so the ring just inside the 1-px outline
is black as well (inner-ring black 0.58 against oppi's 0.30 and the base game's 0.20), and hair, cloth and thin
props melt into the outline at game size. Per frame:
  - a near-black pixel on the silhouette's edge with at most one opaque 4-neighbour (an outline spur) goes;
    coloured pixels are never removed (chains, braids and wand tips are 1 px wide);
  - a near-black pixel just inside the edge takes the darkest of its lighter 8-neighbours (at least two of them):
    the material's own dark shade instead of a second ring of black;
  - a lone pixel inside an area (its colour on none of its four neighbours, three or four of which share one
    colour) takes that colour: the specks of noise (Fiddlesticks's red and grey dots in his dark wood). Lines stay:
    a pixel of a chain, a crack or an edge has at least two neighbours of its own colour or of different ones.
The face round the eyes (EYE_COLOURS) is left alone. Then run import_native.py --hero <hero>.
Fiddlesticks and Kayle (merged before the 18) are cleaned the same way in place: their own
assets/source/native folder is the delivery.
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
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
Z = 8
DARK = 40                       # luma under this is "black" (outline, black shadow)
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))
# the colours of each hero's eyes in Codex's delivery (Thresh's green glints are also on his hood flame and lantern:
# only the pixels round the eyes are kept, see protected())
EYE_COLOURS = {"thresh": [(13, 200, 78), (4, 71, 29)],
               # merged before the 18 (PRs #27 and #26), cleaned the same way in place: run with their own
               # assets/source/native folder as the delivery
               "fiddlesticks": [(200, 224, 96)], "kayle": [(226, 138, 8)],
               "leona": [(186, 88, 30)], "janna": [(3, 51, 207)],
               "ekko": [(213, 125, 34)], "darius": [(255, 247, 238)],
               "leesin": [(212, 34, 50)], "soraka": [(231, 174, 48)],
               # the new design (the user's moss-stone golem): his orange eyes
               "malphite": [(245, 166, 8), (184, 78, 5), (150, 76, 29)],
               "annie": [(51, 32, 63)],
               "amumu": [(243, 224, 80), (247, 214, 65), (204, 141, 33), (153, 88, 24), (87, 46, 21)],
               "jinx": [(209, 46, 128)], "yone": [(70, 52, 94)],
               "garen": [(31, 62, 200)], "ashe": [(59, 174, 240)], "ahri": [(233, 162, 34)],
               "lux": [(45, 111, 184)]}
# heroes whose delivered faces were drawn anew in every frame (Codex: "not a pixel copy of the head"): the design's
# face - eyes, brows, cheeks and the fringe right round them - goes back into every frame where the head is found.
# head: the design's head box on its 128x128 canvas (<hero>_native.png), matched in every frame by colour; patch: the
# face pasted there; iris: the eyes' colour and the eye-only shade it becomes in every frame (import_native.py's EYES
# steadies the head on it; the design's iris is also on the hair); hidden: frames (1-based, per strip) whose face is
# turned away or covered, where a face would be "found" on something else
FACES = {"leona": {"head": (42, 58, 66, 74), "patch": (53, 68, 61, 73), "iris": ((184, 86, 28), (186, 88, 30))},
         # Darius's eye white is already an eye-only shade in the design (#FFF7EE)
         "darius": {"head": (52, 55, 65, 66), "patch": (55, 60, 64, 65), "iris": ((255, 247, 238), (255, 247, 238))},
         # Lee Sin's eyes are under the blindfold: the skull top, the band across the face (its own red #D42232 in the
         # design) and the face under it go back; matched on that face alone (his braid knot changes every frame)
         "leesin": {"head": (57, 62, 69, 72), "patch": (57, 63, 69, 72), "iris": ((212, 34, 50), (212, 34, 50))},
         # Soraka: the approved design's face (the user went back to it from the face Codex refined), its amber eye the
         # marker in an eye-only shade (Codex's frames use the eye amber on her gold trim); matched on the face alone
         # (her white hair is drawn anew in every frame); in Wish's deep bow her hair covers the face
         "soraka": {"head": (58, 68, 65, 75), "patch": (59, 69, 65, 75), "iris": ((230, 172, 46), (231, 174, 48)),
                    "hidden": {"ult": (4, 5)}},
         # Annie: her face - the lids, the white-and-violet eyes (the pupils #33203F, an eye-only shade of #2A1A35
         # since the step-2 pack) and the cheeks - matched on the face alone (her hair is drawn anew every frame)
         "annie": {"head": (60, 72, 65, 77), "patch": (60, 72, 65, 76), "iris": ((51, 32, 63), (51, 32, 63))},
         # Amumu: the two yellow eyes in their dark sockets (his bandages are drawn anew every frame); the eye yellow
         # #F2DF4E becomes an eye-only shade (Codex's frames use it for their own, bigger eyes)
         "amumu": {"head": (70, 77, 82, 82), "patch": (71, 78, 81, 81), "iris": ((242, 223, 78), (243, 224, 80)),
                   # Codex's own eyes were bigger in some frames: their yellows left round the pasted face go
                   "scrub": {(242, 223, 78), (247, 214, 65), (204, 141, 33), (153, 88, 24), (87, 46, 21)},
                   # lying in the death strip: the face is on the ground (a "face" was found on his body)
                   "hidden": {"dead": (3, 4, 5, 6, 7)}},
         # Jinx: lids, the blue-and-pink eyes and the mouth; the pink iris #D02C7E becomes an eye-only shade
         # (Codex's frames use it on her guns); matched on the face alone (her hair and braids are drawn anew)
         "jinx": {"head": (55, 69, 63, 73), "patch": (56, 70, 62, 73), "iris": ((208, 44, 126), (209, 46, 128))},
         # Yone: no eyes (the mask's red V and a dark strand cover them) - the masked face with the purple hair
         # strand over it goes back; the strand's #45335C (Codex also uses it on the demon blade) becomes a
         # head-only shade to steady on
         "yone": {"head": (57, 61, 67, 72), "patch": (58, 62, 66, 72), "iris": ((69, 51, 92), (70, 52, 94)),
                  "hidden": {"q3": (5, 6), "dead": (1, 2, 3, 4, 5, 6, 7)}},  # the spin turns him away; he falls face down
         # Garen: the near eye's lid, white and blue iris, the one grey pixel of the far eye, cheeks; the iris
         # #1E3CC6 (the pack's eye-only shade, which Codex then used on his armour too) becomes #1F3EC8
         "garen": {"head": (59, 69, 66, 73), "patch": (59, 69, 66, 72), "iris": ((30, 60, 198), (31, 62, 200)),
                   "hidden": {"hit": (1,)}},  # the flinch turns his head
         # Ashe: dark pupils over cyan, cheeks and mouth; the cyan is also her crystal bow's, so the pasted
         # eyes get an eye-only shade
         "ashe": {"head": (58, 74, 63, 79), "patch": (58, 75, 62, 79), "iris": ((58, 172, 238), (59, 174, 240)),
                  "hidden": {"dead": (3, 4, 5, 6)}},  # falling: the head tilts
         # Ahri: white-and-amber eyes under brown lids, the blush; the amber is also on her outfit in Codex's
         # frames, so the pasted eyes get an eye-only shade
         "ahri": {"head": (65, 72, 70, 77), "patch": (65, 72, 70, 76), "iris": ((232, 160, 32), (233, 162, 34)),
                  "hidden": {"attack": (3,), "hit": (1,)}},  # a "face" found on her tails; the flinch
         # Lux: the eyes the user picked ("A": both lids over white and blue, the right eye one pixel in from
         # the face's edge - Codex drew it bulging out of the face); her blue in an eye-only shade, and
         # Codex's own blue eye pixels left round the face are scrubbed
         "lux": {"head": (63, 72, 70, 77), "patch": (64, 72, 70, 76), "iris": ((45, 111, 184), (45, 111, 184)),
                 "scrub": {(43, 109, 182)}, "hidden": {"dead": (2, 3, 4)}}}  # falling: the head tilts
FACE_OK = 120                   # mean colour distance over the head box above which a frame's head is not found
# deliveries whose frames Codex centred in their cells (its manifest's atlas pivot) instead of standing them on our
# pivots: every frame whose face is found goes sideways so that its eyes stand on League's head joint of that frame
# (the cells table's "head"), as in the design; a frame without a face keeps Codex's place round the atlas pivot,
# moved to ours. Up and down stay Codex's: the soles are on the feet line already.
PLACE_BY_HEAD = {"darius", "leesin", "soraka", "annie", "amumu", "jinx", "yone", "garen", "ashe", "ahri", "lux"}


def blocks(path):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    if a.shape[0] % Z or a.shape[1] % Z:
        sys.exit(f"{path}: {a.shape[1]}x{a.shape[0]} is not a multiple of {Z}")
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    out = b[:, 0, :, 0].copy()
    if not set(np.unique(out[..., 3])) <= {0, 255}:
        sys.exit(f"{path}: semi-transparent pixels")
    return out


def lum(rgb):
    rgb = rgb.astype(float)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def protected(a, colours):
    """The face: from 2 rows over the eyes to 4 rows under them, 3 columns either side (sockets, lashes, brows and
    the mouth - Kayle's mouth is one lone red pixel)."""
    op = a[..., 3] > 0
    m = np.zeros(op.shape, bool)
    for c in colours:
        m |= op & np.all(a[..., :3] == np.array(c, np.uint8), -1)
    grown = m.copy()
    for dy in range(-2, 5):
        for dx in range(-3, 4):
            grown |= shifted(m, dy, dx)
    return grown


def one_outline(a, colours=()):
    """One frame at game size: outline spurs off, the second ring of black turned into the material's dark shade."""
    a = a.copy()
    keep = protected(a, colours)
    for _ in range(2):
        op = a[..., 3] > 0
        cnt = sum(shifted(op, dy, dx).astype(int) for dy, dx in N4)
        a[op & (lum(a[..., :3]) < DARK) & (cnt <= 1) & ~keep] = 0
    op = a[..., 3] > 0
    L = lum(a[..., :3])
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    ring2 = np.zeros_like(op)
    for dy, dx in N4:
        ring2 |= shifted(edge, dy, dx)
    ring2 &= op & ~edge & (L < DARK) & ~keep
    H, W = op.shape
    out = a.copy()
    for y, x in zip(*np.nonzero(ring2)):
        cols = [tuple(int(v) for v in a[y + dy, x + dx]) for dy, dx in N8
                if 0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx] and L[y + dy, x + dx] >= DARK]
        if len(cols) >= 2:
            out[y, x] = min(cols, key=lambda c: (lum(np.array(c[:3])), -cols.count(c)))
    return despeckle(out, keep)


def despeckle(a, keep):
    """Lone pixels inside an area take the colour of the area (3 or 4 of the 4 neighbours share it)."""
    op = a[..., 3] > 0
    H, W = op.shape
    out = a.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not op[y, x] or keep[y, x]:
                continue
            nb = [tuple(int(v) for v in a[y + dy, x + dx]) for dy, dx in N4]
            me = tuple(int(v) for v in a[y, x])
            if me in nb or any(n[3] == 0 for n in nb):
                continue
            best = max(set(nb), key=nb.count)
            if nb.count(best) >= 3:
                out[y, x] = best
    return out


def find_head(frame, head, guess, reach=(16, 14)):
    """(mean colour distance, x, y) of the best place for the design's head box in the frame near guess (x, y)."""
    m = head[..., 3] > 0
    hh, hw = head.shape[:2]
    H, W = frame.shape[:2]
    best = (1e9, 0, 0)
    for y in range(max(0, guess[1] - reach[1]), min(H - hh, guess[1] + reach[1]) + 1):
        for x in range(max(0, guess[0] - reach[0]), min(W - hw, guess[0] + reach[0]) + 1):
            win = frame[y:y + hh, x:x + hw]
            d = np.sqrt(((win[..., :3].astype(float) - head[..., :3]) ** 2).sum(-1))
            d[win[..., 3] == 0] = 255
            s = float(d[m].mean())
            if s < best[0]:
                best = (s, x, y)
    return best


def skin_blobs(frame, skin, least=8):
    """(size, centre x, centre y) of every 4-connected patch of the skin colours with at least `least` pixels."""
    m = (frame[..., 3] > 0) & np.isin(frame[..., :3].astype(np.int32) @ np.array([65536, 256, 1]),
                                      [r * 65536 + g * 256 + b for r, g, b in skin])
    seen = np.zeros_like(m)
    H, W = m.shape
    out = []
    for sy, sx in zip(*np.nonzero(m)):
        if seen[sy, sx]:
            continue
        stack, pts = [(sy, sx)], []
        seen[sy, sx] = True
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for dy, dx in N4:
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        if len(pts) >= least:
            ys, xs = zip(*pts)
            out.append((len(pts), sum(xs) / len(xs), sum(ys) / len(ys)))
    return out


def locate(frame, design, face, head, guess):
    """(score, x, y) of the head box in the frame. With "skin" in the hero's FACES entry the face is the frame's
    largest patch of skin (at least `skin_least` pixels; hands and arms are smaller) and the colour search only looks
    `reach` round it: Codex's faces drift too far from the pose for a wide search, which then settles on hair or
    armour, and they differ too much from the design for its distance to judge them - the skin patch is the
    evidence, so a frame without one is "not found" and one with it is found whatever the distance."""
    if not face.get("skin"):
        return find_head(frame, head, guess)
    x0, y0 = face["head"][:2]
    if "_off" not in face:
        own = min(skin_blobs(design, face["skin"]), key=lambda b: abs(b[1] - x0) + abs(b[2] - y0))
        face["_off"] = (x0 - own[1], y0 - own[2])
    ox, oy = face["_off"]
    blobs = [b for b in skin_blobs(frame, face["skin"]) if b[0] >= face.get("skin_least", 12)]
    if not blobs:
        return (1e9, 0, 0)
    big = max(blobs)
    s, x, y = find_head(frame, head, (round(big[1] + ox), round(big[2] + oy)), face.get("reach", (2, 2)))
    return (min(s, FACE_OK), x, y)


def paste_face(frame, design, face, guess):
    """The design's face patch pasted where the head is found, the iris in its eye-only shade; (score, x, y) or
    None when the head is not found (turned away, lying)."""
    x0, y0, x1, y1 = face["head"]
    px0, py0, px1, py1 = face["patch"]
    head = design[y0:y1 + 1, x0:x1 + 1]
    s, x, y = locate(frame, design, face, head, guess)
    if s > FACE_OK:
        return None
    patch = design[py0:py1 + 1, px0:px1 + 1].copy()
    iris, shade = face["iris"]
    patch[np.all(patch[..., :3] == np.array(iris, np.uint8), -1) & (patch[..., 3] > 0), :3] = shade
    ox, oy = x + px0 - x0, y + py0 - y0
    win = frame[oy:oy + patch.shape[0], ox:ox + patch.shape[1]]
    m = patch[..., 3] > 0
    win[m] = patch[m]
    if face.get("scrub"):
        scrub(frame, (ox, oy, ox + patch.shape[1] - 1, oy + patch.shape[0] - 1), face["scrub"])
    return s, x, y


def scrub(frame, box, colours, margin=3):
    """The frame's own eyes where they stuck out of the pasted face: their colours (eye-only in the design) within
    `margin` of the patch box take the commonest other colour round them."""
    x0, y0, x1, y1 = box
    H, W = frame.shape[:2]
    bad = lambda p: p[3] > 0 and tuple(int(v) for v in p[:3]) in colours  # noqa: E731
    for _ in range(2):
        for y in range(max(0, y0 - margin), min(H, y1 + margin + 1)):
            for x in range(max(0, x0 - margin), min(W, x1 + margin + 1)):
                if x0 <= x <= x1 and y0 <= y <= y1 or not bad(frame[y, x]):
                    continue
                nb = [tuple(int(v) for v in frame[y + dy, x + dx]) for dy, dx in N8
                      if 0 <= y + dy < H and 0 <= x + dx < W and frame[y + dy, x + dx, 3] > 0
                      and not bad(frame[y + dy, x + dx])]
                if nb:
                    frame[y, x] = max(set(nb), key=nb.count)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hero")
    ap.add_argument("delivery")
    a = ap.parse_args()
    h = a.hero
    with open(G.lp(os.path.join(SRC, f"{h}_cells.json")), encoding="utf-8") as f:
        spec = json.load(f)
    cw, ch = spec["cell"]
    colours = EYE_COLOURS.get(h, [])
    face = FACES.get(h)
    if face:
        design = blocks(os.path.join(SRC, f"{h}_native.png"))
        idle = blocks(os.path.join(a.delivery, f"{h}_idle.png"))[:ch, :cw]
        x0, y0, x1, y1 = face["head"]
        s, hx, hy = find_head(idle, design[y0:y1 + 1, x0:x1 + 1], (cw // 2, ch // 2), (cw // 2, ch // 2))
        p0 = spec["tags"]["idle"][0]["pivot"]
        off = (hx - p0[0], hy - p0[1])          # the head box's corner from the standing point in the design
        print(f"{h}: design head in idle frame 1 at {hx},{hy} (distance {s:.1f})")
    place = h in PLACE_BY_HEAD
    if place:
        shade = np.array(face["iris"][1], np.uint8)
        first = idle.copy()                   # the design's face (and its eye shade) pasted, as in every frame
        paste_face(first, design, face, (p0[0] + off[0], p0[1] + off[1]))
        eye_k = eye_x(first, shade) - spec["tags"]["idle"][0]["head"][0]   # the eyes from League's head joint
    for tag, frames in spec["tags"].items():
        new = blocks(os.path.join(a.delivery, f"{h}_{tag}.png"))
        old = blocks(os.path.join(SRC, f"{h}_{tag}.png"))
        if new.shape != old.shape:
            sys.exit(f"{h}_{tag}.png: {new.shape[1]}x{new.shape[0]} game pixels, the cells need "
                     f"{old.shape[1]}x{old.shape[0]}")
        atlas = atlas_pivots(a.delivery, h, tag) if place else None
        out = new.copy()
        cols = new.shape[1] // cw
        found, moved = [], []
        for k, fr in enumerate(frames):
            y, x = (k // cols) * ch, (k % cols) * cw
            cell = out[y:y + ch, x:x + cw]
            if face:
                ap = atlas[k] if atlas else fr["pivot"]
                hidden = k + 1 in face.get("hidden", {}).get(tag, ())
                r = None if hidden else paste_face(cell, design, face, (ap[0] + off[0], ap[1] + off[1]))
                found.append("-" if r is None else f"{r[0]:.0f}")
                if place and tag != "idle":
                    # a cells frame without "head" (Garen's round-1 table: his head is not found in a spin
                    # seen from behind or a fall) goes by the pivot like a frame without a face
                    ex = eye_x(cell, shade) if r is not None and "head" in fr else None
                    dx = (round(fr["head"][0] + eye_k - ex) if ex is not None
                          else fr["pivot"][0] - (ap[0] if atlas else fr["pivot"][0]))
                    cell[:], dx = slide(cell, dx), dx
                    moved.append(f"{dx:+d}")
            out[y:y + ch, x:x + cw] = one_outline(cell, colours)
        n = int((out != new).any(-1).sum())
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1)).save(G.lp(os.path.join(SRC, f"{h}_{tag}.png")))
        print(f"{h}_{tag}.png: {n} pixels changed" + (f"; face pasted (head distance per frame, - = not found): "
                                                     f"{' '.join(found)}" if face else "")
              + (f"; moved sideways {' '.join(moved)}" if moved else ""))


def eye_x(frame, shade):
    """The middle column of the eye-only shade in a frame, or None."""
    m = (frame[..., 3] > 0) & np.all(frame[..., :3] == shade, -1)
    xs = np.nonzero(m)[1]
    return float(xs.mean()) if len(xs) else None


def atlas_pivots(delivery, h, tag):
    """The per-frame pivots Codex's manifest gives for its centred frames, or None."""
    p = os.path.join(delivery, f"{h}_{tag}_manifest.json")
    if not os.path.exists(p):
        return None
    m = json.load(open(p, encoding="utf-8-sig"))
    if not isinstance(m, dict):             # a plain list of frames: drawn at our pivots already (Darius's redo)
        return None
    return [f["pivot"] for f in m.get("atlas", {}).get("frames", [])] or None


def slide(cell, dx):
    """The cell's content moved dx columns (no further than keeps it inside the cell)."""
    xs = np.nonzero(cell[..., 3].any(0))[0]
    if not len(xs):
        return cell.copy()
    dx = max(-int(xs[0]), min(int(dx), cell.shape[1] - 1 - int(xs[-1])))
    out = np.zeros_like(cell)
    if dx >= 0:
        out[:, dx:] = cell[:, :cell.shape[1] - dx]
    else:
        out[:, :dx] = cell[:, -dx:]
    return out


if __name__ == "__main__":
    main()
