#!/usr/bin/env python3
"""Elise's step-2 delivery (Codex, assets/source/elise/codex_strips: 65 frames, one dense square a pixel on the pack's
219 x 146 canvas) made into her action frames: assets/source/elise/frames/<tag>_<n>.png + frames.json.

    python tools/art/import_elise_strips.py [--review DIR]

import_nidalee_strips.py's way. Codex's handoff (2026-10-15) says the frames are on the grid and in the 40 colours but
the heads and carapaces are redrawn per frame and the sizes drift; reading them back, the huntress is 10-20 % under
the design (99-114 rows against 124) and her size jumps inside a tag, the spider about the design's size.
  1. size: every frame's face is found by matching the design's face (skimage match_template on the colours) on the
     frame shrunk by 1/s for s in SCALES; each tag takes the median s of its frames that matched (one size through a
     tag, no wobble) and the frame is brought to the design's size by 1/s, nearest neighbour, round the standing point
     (the frames go down to 1.5 squares a game pixel later, so this costs nothing that step keeps);
  2. ground: the lowest opaque row on the toes' row SOLE (AIR frames - the bite's leap, Rappel's rise, the drop - keep
     their height above it);
  3. one face: in every upright frame the design's face (HEAD box, its opaque squares) is pasted where the face matched
     at s = 1; lying, curled or flipped frames keep Codex's (NO_HEAD).
The idles (the designs) and hit come later with the breathing (rig step).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from skimage.feature import match_template

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ppu_restyle import Warp  # noqa: E402
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "elise")
CODEX = os.path.join(SRC, "codex_strips")
OUT = os.path.join(SRC, "frames")
COLS, ROWS, SOLE = 219, 146, 138
FORMS = {
    # design, where it sits on the canvas (x0, y0), standing point column; the face matched (rows, cols in the design)
    # and the head pasted (rows, cols): the face with its side hair (the hair horns and the crown sit among the back
    # legs, which move from frame to frame), the spider's front with its eyes and fangs
    "human": {"design": "human.png", "at": (52, 15), "piv": 105, "face": (36, 56, 44, 62), "head": (34, 56, 43, 63)},
    "spider": {"design": "spider.png", "at": (42, 67), "piv": 110, "face": (36, 56, 63, 80), "head": (35, 56, 63, 81)},
}
SCALES = np.round(np.arange(0.76, 1.36, 0.02), 2)
MATCH_MIN = 0.55                 # a face found below this score does not count (lying, turned, covered)
AIR = {("c_skill", 2), ("c_skill", 3), ("c_skill2", 2), ("c_skill2", 3), ("c_skill2", 4), ("c_land", 1)}
NO_HEAD = {"c_dead", "c_transform"}
# the huntress's frames that do not stand: lying on her back, the head on the image right (the "lie" warp along x),
# curled in her legs (scaled evenly); E / W's thrust frames are Codex's thin, stretched back legs (its own handoff):
# Neurotoxin's thrust frames stand in for them (both spells leave her hands)
EVEN = {("dead", 2): 1.15, ("dead", 3): 1.15, ("dead", 4): 1.15, ("dead", 5): 1.15, ("dead", 6): 1.15, ("transform", 3): 1.25}   # scaled evenly (lying / curled)
SAME = {("skill2", 2): ("skill", 3), ("skill2", 3): ("skill", 4)}
F_DEFAULT = 0.66
DRIFT = 0.05
PASTE_MIN = 0.38                 # an upright frame's face at the tag's size: found well enough to paste the design's
                                 # (attack 4's arm crosses its head, 0.40, the match right where the face is drawn)
LIFT = {("c_skill2", 2): 15, ("c_skill2", 3): 45}   # Rappel's rise: Codex drew these near the ground
ALIGN = {"run"}                   # loops held by the head: each frame moved across to the loop's median face column
FACE_AT = {}
OFFSET = {}                       # (tag, frame) -> Codex's warped face minus the pasted one (dx, dy, score), the review                     # (tag, frame) -> where the design's face box went (its top-left), for the review


def lp(path):
    """The workspace sits under a long path: the extended-length prefix for Windows file calls (python-long-paths)."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def rgba(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


def design(form):
    return rgba(os.path.join(SRC, "hd", FORMS[form]["design"]))


def as_float(a):
    """Colours for matching: transparent squares a fixed mid grey."""
    f = a[..., :3].astype(float) / 255.0
    f[a[..., 3] == 0] = 0.4
    return f


def find_face(frame, form):
    """(score, s, x, y): the design's face found in the frame shrunk by 1/s; (x, y) the face box's top-left in the
    frame's own squares."""
    r0, r1, c0, c1 = FORMS[form]["face"]
    t = as_float(design(form)[r0:r1, c0:c1])
    best = (-1.0, 1.0, 0, 0)
    for s in SCALES:
        w, h = max(1, round(COLS / s)), max(1, round(ROWS / s))
        f = as_float(np.asarray(Image.fromarray(frame).resize((w, h), Image.NEAREST)))
        if f.shape[0] < t.shape[0] or f.shape[1] < t.shape[1]:
            continue
        sc = np.mean([match_template(f[..., k], t[..., k]) for k in range(3)], axis=0)
        y, x = np.unravel_index(np.argmax(sc), sc.shape)
        if sc[y, x] > best[0]:
            best = (float(sc[y, x]), float(s), int(round(x * s)), int(round(y * s)))
    return best


def rescale(frame, s, piv):
    """The frame brought to the design's size: shrunk (or grown) by 1/s round (piv, the toes' bottom edge)."""
    if abs(s - 1.0) < 1e-6:
        return frame.copy()
    H, W = frame.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    sx = np.round((xx + 0.5 - (piv + 0.5)) * s + (piv + 0.5) - 0.5).astype(int)
    sy = np.round((yy + 0.5 - (SOLE + 1)) * s + (SOLE + 1) - 0.5).astype(int)
    ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    out = np.zeros_like(frame)
    out[ok] = frame[sy[ok], sx[ok]]
    return out


def ground(frame):
    ys = np.nonzero((frame[..., 3] > 0).any(1))[0]
    return np.roll(frame, SOLE - int(ys.max()), axis=0) if len(ys) else frame


# the huntress's whole head (hair, crown, horns, face) as an ellipse on the design (row, column, half height, half
# width): pasting only the face left Codex's own crown and hair, scaled with its head, beside it - a second head (the
# user: 「我怎么看到动作帧里面有两个头？」, Neurotoxin 4). Inside the ellipse above the face (HEAD_CLEAR rows) the design's
# clear squares clear the frame too, so no crown of Codex's shows between the design's spikes
HEAD_ELLIPSE = (40, 51, 17, 12.5)
HEAD_CLEAR = 36


def head_mask(form):
    """(rows, cols, clear) of the design's head: every square of the human's ellipse (the spider's HEAD box), and
    whether a clear one there clears the frame."""
    d = design(form)
    if form == "human":
        cr, cc, hr, hc = HEAD_ELLIPSE
        yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
        m = ((yy - cr) / hr) ** 2 + ((xx - cc) / hc) ** 2 <= 1.0
        ys, xs = np.nonzero(m)
        return ys, xs, ys < HEAD_CLEAR
    r0, r1, c0, c1 = FORMS[form]["head"]
    yy, xx = np.mgrid[r0:r1, c0:c1]
    return yy.ravel(), xx.ravel(), np.zeros(yy.size, bool)


def paste_head(frame, form, x, y):
    """The design's head pasted with its face box at (x, y) of the frame."""
    fr0, _, fc0, _ = FORMS[form]["face"]
    d = design(form)
    ys, xs, clear = head_mask(form)
    ox, oy = x - fc0, y - fr0
    out = frame.copy()
    ty, tx = ys + oy, xs + ox
    ok = (ty >= 0) & (ty < ROWS) & (tx >= 0) & (tx < COLS)
    op = d[ys, xs, 3] > 0
    m = ok & op
    out[ty[m], tx[m]] = d[ys[m], xs[m]]
    m = ok & ~op & clear
    out[ty[m], tx[m]] = 0
    return out


# the huntress's proportions: Codex followed League's skeleton (a head about 0.6 of the design's, a slim body, long
# legs), so each upright frame is warped round its neck (ppu_restyle.Warp, the Zeri way): above the neck x 1/f (f the
# found face's size against the design's), below it SHORT so the neck-to-toes height is the design's, WIDE times wider
# within REACH squares of the standing point (an arm or a back leg thrown further keeps its length)
FACE_F = np.round(np.arange(0.44, 0.92, 0.02), 2)
DESIGN_NECK = 15 + 57            # the design's neck row on the canvas (its chin on design row 56, the design at y 15)
FACE_NECK = 21                   # design rows from the face box's top to the neck
FACE_MID = 9                     # design columns from the face box's left to the face's middle
WIDE, REACH, BAND = 1.35, 20, 3


HEAD_HALF = 13                   # design columns each side of the face's middle that scale with the head


class HeadWarp(Warp):
    """Warp whose head part scales only within HEAD_HALF design columns of the neck: an arm or a back leg held out at
    the neck's height keeps its own length beyond that (the plain warp smeared Neurotoxin's level arm into a bar)."""

    def across(self, v, u):
        w = self.w(u)
        d = v - self.nx
        r = HEAD_HALF / self.s                          # source columns
        ad = np.abs(d)
        head = self.nx2 + np.sign(d) * (self.s * np.minimum(ad, r) + np.maximum(ad - r, 0))
        body = self.px + self.g(v - self.px)
        return w * head + (1 - w) * body


def find_small_face(frame, sizes=FACE_F):
    """(score, f, x, y): the design's face shrunk by f found in the frame; (x, y) its top-left."""
    r0, r1, c0, c1 = FORMS["human"]["face"]
    full = design("human")[r0:r1, c0:c1]
    F = as_float(frame)
    best = (-1.0, 1.0, 0, 0)
    for f in sizes:
        t = as_float(np.asarray(Image.fromarray(full).resize((max(2, round(full.shape[1] * f)),
                                                              max(2, round(full.shape[0] * f))), Image.NEAREST)))
        sc = np.mean([match_template(F[..., k], t[..., k]) for k in range(3)], axis=0)
        y, x = np.unravel_index(np.argmax(sc), sc.shape)
        if sc[y, x] > best[0]:
            best = (float(sc[y, x]), float(f), int(x), int(y))
    return best


def warp_human(frame, f, x, y, piv, short):
    """The frame warped to the design's proportions round its neck (x, y: the small face's top-left; `short` the tag's
    one squash, so a crouch stays lower than a stand and the run keeps its bob) -> (frame, short, where the design's
    face box goes: its top-left (x, y) in the warped frame)."""
    nx, ny = x + FACE_MID * f, y + FACE_NECK * f
    w = HeadWarp("up", None, nx, ny, piv + 0.5, SOLE + 1, 1.0 / f, WIDE, short, BAND, reach=REACH)
    fx, fy = w.nx2 + (x - nx) / f, w.ny2 + (y - ny) / f
    return w.render(frame, (ROWS, COLS), (0, 0)), short, (int(round(fx)), int(round(fy)))


def skin_head(frame, f):
    """For a tilted head the design's face does not match: the topmost blob of the design's skin colours (min SKIN_MIN
    squares) stands for the face -> the small face box's top-left (x, y) the warp needs, or None."""
    from scipy import ndimage
    r0, r1, c0, c1 = FORMS["human"]["face"]
    face = design("human")[r0:r1, c0:c1]
    cols = face[face[..., 3] > 0][:, :3].astype(int)
    skin = {tuple(c) for c in cols if c.sum() > 480}           # the pale skin shades
    m = np.zeros(frame.shape[:2], bool)
    for c in skin:
        m |= (frame[..., :3] == c).all(-1) & (frame[..., 3] > 0)
    lab, n = ndimage.label(m)
    best = None
    for j in range(1, n + 1):
        ys, xs = np.nonzero(lab == j)
        if len(ys) >= 8 and (best is None or ys.min() < best[0]):
            best = (ys.min(), ys.max(), xs.mean())
    if best is None:
        return None
    _, y1, cx = best
    return int(round(cx - FACE_MID * f)), int(round(y1 + 2 - FACE_NECK * f))


def lie_human(frame, f, piv):
    """A lying frame (head on the image right): the head x 1/f round the neck along x, the body as long as the design's
    neck-to-toes and WIDE times as thick up from the ground."""
    op = frame[..., 3] > 0
    xs = np.nonzero(op.any(0))[0]
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    nx = x1 - 22 * f                                     # the head about 22 design rows long, shrunk by f
    short = (SOLE + 1 - DESIGN_NECK) / max(nx - x0, 1)
    w = Warp("lie", "r", nx, SOLE + 1, piv + 0.5, SOLE + 1, 1.0 / f, WIDE, short, BAND)
    return w.render(frame, (ROWS, COLS), (0, 0))


def even(frame, k, piv):
    return rescale(frame, 1.0 / k, piv)


def review(before, after, path, scale=3):
    """Codex's frames over ours, a tag per sheet."""
    n = len(before)
    sheet = Image.new("RGBA", (COLS * n * scale, ROWS * 2 * scale), (200, 200, 200, 255))
    for i, (b, a) in enumerate(zip(before, after)):
        for j, im in enumerate((b, a)):
            sheet.alpha_composite(Image.fromarray(im).resize((COLS * scale, ROWS * scale), Image.NEAREST),
                                  (i * COLS * scale, j * ROWS * scale))
    sheet.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write a before / after sheet per tag here")
    a = ap.parse_args()
    cells = json.load(open(lp(os.path.join(CODEX, "cells.json")), encoding="utf-8"))
    by_tag = {}
    for f in cells["frames"]:
        by_tag.setdefault(f["tag"], []).append(f)
    os.makedirs(lp(OUT), exist_ok=True)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
    table, report = {}, []
    for tag, frames in by_tag.items():
        form = frames[0]["form"]
        piv = FORMS[form]["piv"]
        raw = [rgba(os.path.join(CODEX, f["file"].replace(".png", "_1x.png"))) for f in frames]
        if form == "human":
            table[tag], outs = [], []
            # one head size through a tag (the median of the frames that matched well), the face found again at it
            first = [find_small_face(r) for r in raw]
            ok = [m[1] for m in first if m[0] >= 0.62]
            ftag = float(np.median(ok)) if ok else F_DEFAULT
            # a loop's frame Codex drew bigger or smaller than the rest (its height off the loop's median by DRIFT or
            # more; run 2 is 7 % taller): brought back to the loop's size first, round the standing point (other tags'
            # poses differ in height by themselves)
            if tag in ALIGN:
                hs = [np.ptp(np.nonzero((r[..., 3] > 0).any(1))[0]) + 1 for r in raw]
                med = float(np.median(hs))
                raw = [rescale(r, h_ / med, piv) if abs(h_ / med - 1) >= DRIFT else r for r, h_ in zip(raw, hs)]
            small = [find_small_face(r, [ftag]) for r in raw]
            # the tag's one squash: its highest neck (among the frames whose face matched) on the design's neck row
            necks = [m[3] + FACE_NECK * ftag for i_, m in enumerate(small)
                     if m[0] >= MATCH_MIN and (tag, i_ + 1) not in EVEN]
            short_tag = (SOLE + 1 - DESIGN_NECK) / max(SOLE + 1 - min(necks), 1) if necks else 1.0
            for i, (r, f, m) in enumerate(zip(raw, frames, small)):
                short = 0.0
                if (tag, i + 1) in EVEN:
                    o = ground(even(r, EVEN[(tag, i + 1)], piv))
                else:
                    tilted = m[0] < PASTE_MIN
                    x, y = (skin_head(r, ftag) or (m[2], m[3])) if tilted else (m[2], m[3])
                    o, short, (fx, fy) = warp_human(r, ftag, x, y, piv, short_tag)
                    ys = np.nonzero((o[..., 3] > 0).any(1))[0]
                    dy = SOLE - int(ys.max())
                    o = np.roll(o, dy, axis=0)
                    if not tilted:
                        # where Codex's own face is after the warp (the design's face at full size matched on it)
                        cm = find_small_face(o, [1.0])
                        OFFSET[(tag, i + 1)] = (cm[2] - fx, cm[3] - (fy + dy), round(cm[0], 2))
                        o = paste_head(o, form, fx, fy + dy)
                        FACE_AT[(tag, i + 1)] = (fx, fy + dy)
                name = f"{tag}_{i + 1}.png"
                Image.fromarray(o).save(lp(os.path.join(OUT, name)))
                outs.append(o)
                table[tag].append([name, f["ms"]])
                report.append(f"{tag:12s} {i + 1}: face {m[0]:.2f} at the tag's f {ftag:.2f}, short {short:.2f}")
            if tag in ALIGN:
                xs_ = [FACE_AT[(tag, j + 1)][0] for j in range(len(outs)) if (tag, j + 1) in FACE_AT]
                mid = int(round(np.median(xs_)))
                for j in range(len(outs)):
                    if (tag, j + 1) in FACE_AT:
                        outs[j] = np.roll(outs[j], mid - FACE_AT[(tag, j + 1)][0], axis=1)
                        Image.fromarray(outs[j]).save(lp(os.path.join(OUT, f"{tag}_{j + 1}.png")))
            if a.review:
                review(raw, outs, os.path.join(a.review, f"{tag}.png"))
            continue
        found = [find_face(r, form) for r in raw]
        good = [m[1] for m in found if m[0] >= MATCH_MIN]
        s = float(np.median(good)) if good else 1.0
        table[tag], outs = [], []
        for i, (r, f, m) in enumerate(zip(raw, frames, found)):
            o = rescale(r, s, piv)
            if (tag, i + 1) not in AIR:
                o = ground(o)
            if (tag, i + 1) in LIFT:
                o = np.roll(ground(o), -LIFT[(tag, i + 1)], axis=0)
            pasted = False
            if tag not in NO_HEAD and m[0] >= MATCH_MIN:
                sc, s1, x, y = find_face(o, form)
                if sc >= MATCH_MIN and abs(s1 - 1.0) <= 0.04:
                    o = paste_head(o, form, x, y)
                    pasted = True
            name = f"{tag}_{i + 1}.png"
            Image.fromarray(o).save(lp(os.path.join(OUT, name)))
            outs.append(o)
            table[tag].append([name, f["ms"]])
            report.append(f"{tag:12s} {i + 1}: face {m[0]:.2f} at s {m[1]:.2f} -> tag s {s:.2f}{' head' if pasted else ''}")
        if a.review:
            review(raw, outs, os.path.join(a.review, f"{tag}.png"))
    for (tag, i), (src, j) in SAME.items():
        Image.open(lp(os.path.join(OUT, f"{src}_{j}.png"))).save(lp(os.path.join(OUT, f"{tag}_{i}.png")))
        report.append(f"{tag:12s} {i}: = {src} {j}")
    report.append("offsets: " + " ".join(f"{t}{i}:{d[0]},{d[1]}({d[2]})" for (t, i), d in sorted(OFFSET.items())))
    report.append("faces: " + " ".join(f"{t}{i}:{x},{y}" for (t, i), (x, y) in FACE_AT.items() if t == "run"))
    # where the design's face went in each frame (rig_elise.py pastes the face brought down once there)
    with open(lp(os.path.join(OUT, "faces.json")), "w", encoding="utf-8", newline=chr(10)) as fh:
        json.dump({f"{t}_{i}": [x, y] for (t, i), (x, y) in sorted(FACE_AT.items())}, fh, indent=1)
    with open(lp(os.path.join(OUT, "frames.json")), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(table, fh, indent=1)
    print("\n".join(report))


if __name__ == "__main__":
    main()
