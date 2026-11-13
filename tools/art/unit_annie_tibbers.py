#!/usr/bin/env python3
"""Tibbers as a unit of his own: league/champions/league_annie_tibbers#sheet.png + #anim.fanim.

    python tools/art/unit_annie_tibbers.py [--check] [--preview <png>]

The add-on league_annie_q spawns Tibbers through the mod API's spawn_unit under the name league_annie_tibbers; the game
draws a unit of that name from asset/base/aseprite_resources/champions/league_annie_tibbers (the add-on's
mod.override_info sends that here) with the tags a champion has. The engine's own summons (base `ghoul`) carry idle, run,
attack, hit and dead, so those five:

  idle    his first standing frame six times: frames 3-5 everything above the knees a row lower (the heroes' breath),
          and on every other frame the flames on his back a pixel taller;
  attack  his swipe as Codex drew it - frames 2-6 of the standing loop (the paw up, the claws down, round again) -
          0.45 s; the claws come down 0.17 s in (the add-on's unit attack lands at tick 10 of 27);
  run     no such drawing exists: six frames made here from the standing frame by whole-pixel moves - each shin and
          foot slides back on the ground, is lifted two rows and set down in front (never both feet up), the body a row
          lower on the two frames both feet stand, the arms a row up and down against the legs, the flames flickering;
          the outline is closed again where a move opened it;
  hit     the standing frame, the body above the knees a pixel back;
  dead    his vanishing into smoke (the six frames of tibbers_vanish) and an empty frame, as base's dead tags end.

Every frame is the effect sheet's own pixels (league/effects/league_annie_big: tags tibbers, tibbers_vanish - plain 1x
frames, 42 px ears to feet, no dense twin; the unit is no row of league.dll's tables and is drawn a square a game pixel,
the size he has on screen today), moved 10 rows down: on the effect his feet are a row under the frame's centre (he
stands 9 px behind the champion he rides on), a unit's are 11 rows under it like every hero's.
--check: exit 1 when the sheet in the repo is not what this writes. --preview: the frames at 8x on their ground line.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "league", "effects", "league_annie_big")
OUT = os.path.join(ROOT, "league", "champions", "league_annie_tibbers")
S = 160                 # the working canvas; its centre (C, C) is the frame's pivot
C = S // 2
FEET = 11               # a unit's soles: this many rows under the pivot
DOWN = 10               # the effect's frames stand with their soles a row under the pivot
# The standing frame's parts, read off its pixels (rows as on the effect sheet, before the move down; columns from the
# pivot; all inclusive). The shins with their feet from the knee row down, the stance's gap between them:
KNEE = -3
LEG_L = (-12, -1)
LEG_R = (3, 13)
# the near forearm with its claws: the rows it hangs over and, row by row, the column it reaches to (the dark line
# between it and the body stays with the body); its lowest row lies on the knee row, left of the shin
ARM_L = {-13: -9, -12: -9, -11: -9, -10: -9, -9: -9, -8: -9, -7: -9, -6: -10, -5: -10, -4: -10, KNEE: -11}
# the far forearm: free of the body on these rows, from this column on
ARM_R_ROWS = (-11, -5)
ARM_R = 14
IDLE_MS = 140
RUN_MS = 110
ATTACK_MS = (70, 100, 110, 100, 70)
HIT_MS = 100
VANISH_MS = 85


def frames_of(sheet, anim, tag):
    out = []
    for f in anim[tag]["frames"]:
        d = f["data"]
        x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
        c = np.zeros((S, S, 4), np.uint8)
        cx, cy = (w - 1) // 2, (h - 1) // 2
        c[C - cy + DOWN:C - cy + DOWN + h, C - cx:C - cx + w] = sheet[y:y + h, x:x + w]
        out.append(c)
    return out


def flames(f):
    """his fire: saturated orange and yellow on his back and his head (not the belly's dull orange: left of the chest
    or above the shoulders)"""
    rgb = f[..., :3].astype(int)
    hot = (f[..., 3] > 0) & (rgb[..., 0] > 150) & (rgb[..., 0] - rgb[..., 2] > 90)
    ys, xs = np.nonzero(hot)
    keep = np.zeros_like(hot)
    for y, x in zip(ys, xs):
        if x - C <= -7 and y - C <= -20 + DOWN or y - C <= -35 + DOWN and x - C <= 3:
            keep[y, x] = True
    return keep


def taller_flames(f):
    """every flame tongue a pixel taller: its tip repeated above it where nothing is drawn"""
    out = f.copy()
    fl = flames(f)
    ys, xs = np.nonzero(fl)
    for x in sorted(set(xs)):
        top = ys[xs == x].min()
        if f[top - 1, x, 3] == 0:
            out[top - 1, x] = f[top, x]
    return out


def shift(part, dx, dy):
    out = np.zeros_like(part)
    h, w = part.shape[:2]
    ys, xs = np.nonzero(part[..., 3])
    out[np.clip(ys + dy, 0, h - 1), np.clip(xs + dx, 0, w - 1)] = part[ys, xs]
    return out


def over(under, top):
    out = under.copy()
    m = top[..., 3] > 0
    out[m] = top[m]
    return out


def grid():
    rows = np.arange(S)[:, None] - C + np.zeros((1, S), int)
    cols = np.arange(S)[None, :] - C + np.zeros((S, 1), int)
    return rows, cols


def cut(f, mask):
    p = np.zeros_like(f)
    p[mask] = f[mask]
    return p


def masks(stand):
    """(left shin, right shin, left forearm, right forearm) of the standing frame, checked against its pixels"""
    rows, cols = grid()
    rows = rows - DOWN                  # as on the effect sheet
    op = stand[..., 3] > 0
    arm_l = np.zeros_like(op)
    for r, c in ARM_L.items():
        arm_l |= op & (rows == r) & (cols <= c)
    arm_r = op & (rows >= ARM_R_ROWS[0]) & (rows <= ARM_R_ROWS[1]) & (cols >= ARM_R)
    leg_l = op & (rows >= KNEE) & (cols >= LEG_L[0]) & (cols <= LEG_L[1]) & ~arm_l
    leg_r = op & (rows >= KNEE) & (cols >= LEG_R[0]) & (cols <= LEG_R[1])
    # from the knee row down there is nothing but the two shins and the near hand's lowest row
    if (op & (rows >= KNEE) & ~leg_l & ~leg_r & ~arm_l).any():
        sys.exit("the standing frame has pixels under the knees outside LEG_L / LEG_R: read the frame again")
    # the far forearm hangs free: a clear column left of it on each of its rows
    for r in range(ARM_R_ROWS[0], ARM_R_ROWS[1] + 1):
        xs = np.nonzero(arm_r[r + DOWN + C])[0]
        if len(xs) and op[r + DOWN + C, xs.min() - 1]:
            sys.exit("the far forearm touches the body on row %d: read the frame again" % r)
    return leg_l, leg_r, arm_l, arm_r


def parts(stand):
    """the standing frame as (left shin, right shin, left forearm, right forearm, the rest)"""
    leg_l, leg_r, arm_l, arm_r = masks(stand)
    rest = (stand[..., 3] > 0) & ~leg_l & ~leg_r & ~arm_l & ~arm_r
    return cut(stand, leg_l), cut(stand, leg_r), cut(stand, arm_l), cut(stand, arm_r), cut(stand, rest)


def with_arm(body, arm, dy):
    """the forearm back on the body `dy` rows lower (1: a row longer at the elbow; -1: a row shorter, its old lowest
    pixels left clear)"""
    if dy > 0:
        body = over(body, arm)          # the elbow's row stays where it was
    return over(body, shift(arm, 0, dy))


def close(f):
    """the outline closed where a move opened it; his fire and the light toes on the ground row stay as drawn"""
    rows, _ = grid()
    light = (f[..., 3] > 0) & (G.lum(f[..., :3]) >= 70)
    keep = flames(f) | light & (rows >= FEET)
    out, added, darkened = G.complete_outline(f, feet=C + FEET, keep=keep)
    return out, added + darkened


# a shin's place through the stride: (columns forward, rows up); the far one half a stride on
STRIDE = [(2, 0), (0, 0), (-2, 0), (-1, 2), (1, 2), (2, 1)]
# rows the near forearm hangs lower than the body (the far one the other way), frame by frame
SWING = [0, -1, 0, 0, 1, 0]


def run_frame(stand, k):
    """frame k (0-5) of the lumbering walk"""
    leg_l, leg_r, arm_l, arm_r, body = parts(stand)
    (lx, ly), (rx, ry) = STRIDE[k], STRIDE[(k + 3) % 6]
    sink = 1 if k in (0, 3) else 0              # both feet down: the knees give a row
    upper = with_arm(with_arm(body, arm_l, SWING[k]), arm_r, -SWING[k])
    f = np.zeros_like(stand)
    # the shins first, the far one under the near one, both under the body: a lifted one tucks up into the thigh
    for leg, dx, dy in ((leg_r, rx, ry), (leg_l, lx, ly)):
        f = over(f, shift(leg, dx, -dy))
    f = over(f, shift(upper, 0, sink))
    if k % 2:
        f = taller_flames(f)
    f[C + FEET + 1:] = 0                        # nothing under the ground row
    return close(f)


def above_knees(stand):
    leg_l, leg_r, _, _ = masks(stand)
    return (stand[..., 3] > 0) & ~leg_l & ~leg_r


def idle_frame(stand, k):
    """frame k (0-5) of the breath: frames 3-5 everything above the knees a row lower"""
    f = stand
    if k in (3, 4, 5):
        m = above_knees(stand)
        f = over(cut(stand, (stand[..., 3] > 0) & ~m), shift(cut(stand, m), 0, 1))
    if k % 2:
        f = taller_flames(f)
    return f


def hit_frame(stand):
    """the body above the knees a pixel back"""
    m = above_knees(stand)
    return close(over(cut(stand, (stand[..., 3] > 0) & ~m), shift(cut(stand, m), -1, 0)))


def build():
    sheet = np.array(Image.open(G.lp(SRC + "#sheet.png")).convert("RGBA"))
    with open(G.lp(SRC + "#anim.fanim"), encoding="utf-8-sig") as fh:
        anim = json.load(fh)["anims"]
    loop = frames_of(sheet, anim, "tibbers")
    vanish = frames_of(sheet, anim, "tibbers_vanish")
    stand = loop[0]
    if close(stand)[1]:
        sys.exit("the standing frame's outline is not closed as drawn: the outline pass would repaint him")
    report = []
    idle = [idle_frame(stand, k) for k in range(6)]
    run = []
    for k in range(6):
        f, fixed = run_frame(stand, k)
        report.append(("run %d" % k, fixed))
        run.append(f)
    hit, fixed = hit_frame(stand)
    report.append(("hit", fixed))
    attack = [loop[i] for i in (2, 3, 4, 5, 6)]
    blank = np.zeros((S, S, 4), np.uint8)
    tags = {
        "idle": [(f, IDLE_MS) for f in idle],
        "run": [(f, RUN_MS) for f in run],
        "attack": list(zip(attack, ATTACK_MS)),
        "hit": [(hit, HIT_MS)],
        "dead": [(f, VANISH_MS) for f in vanish] + [(blank, 100)],
    }
    return tags, report


def centred(tags):
    """every frame trimmed to an odd size round the pivot (the exported-sheet convention); an empty one 3 x 3"""
    out = {}
    for tag, frames in tags.items():
        row = []
        for f, ms in frames:
            c = G.centre_frame(f, -C, -C) if f[..., 3].any() else np.zeros((3, 3, 4), np.uint8)
            row.append((c, ms))
        out[tag] = row
    return out


def preview(tags, path, zoom=8):
    cells = [(tag, i, f) for tag, frames in tags.items() for i, (f, _) in enumerate(frames)]
    half_w, up, down = 30, 52, 14
    per_row = 7
    cw, ch = (2 * half_w + 1) * zoom, (up + down + 1) * zoom + 14
    rows = (len(cells) + per_row - 1) // per_row
    img = Image.new("RGBA", (per_row * cw, rows * ch), (58, 58, 70, 255))
    dr = ImageDraw.Draw(img)
    for n, (tag, i, f) in enumerate(cells):
        ox, oy = (n % per_row) * cw, (n // per_row) * ch + 14
        crop = Image.fromarray(f[C - up:C + down + 1, C - half_w:C + half_w + 1], "RGBA")
        img.alpha_composite(crop.resize((crop.width * zoom, crop.height * zoom), Image.NEAREST), (ox, oy))
        gy = oy + (up + FEET + 1) * zoom
        dr.line([(ox, gy), (ox + cw - 2, gy)], fill=(0, 255, 255, 255))
        px, py = ox + half_w * zoom, oy + up * zoom
        dr.rectangle([px, py, px + zoom - 1, py + zoom - 1], outline=(255, 0, 255, 255))
        dr.text((ox + 3, oy - 13), "%s %d" % (tag, i), fill=(255, 255, 0, 255))
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview")
    a = ap.parse_args()
    tags, report = build()
    if a.preview:
        preview(tags, a.preview)
        print("preview", a.preview)
    out = centred(tags)
    if a.check:
        import tempfile
        tmp = os.path.join(tempfile.mkdtemp(prefix="tibbers_"), "league_annie_tibbers")
        G.write_sheet(tmp, out)

        def read(stem):
            with open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig") as fh:
                return np.array(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA")), json.load(fh)

        same = False
        if os.path.exists(G.lp(OUT + "#sheet.png")) and os.path.exists(G.lp(OUT + "#anim.fanim")):
            (px, an), (px2, an2) = read(OUT), read(tmp)
            same = an == an2 and px.shape == px2.shape and bool((px == px2).all())
        print("league_annie_tibbers:", "up to date" if same else "stale")
        sys.exit(0 if same else 1)
    w, h = G.write_sheet(OUT, out)
    print("wrote %s#sheet.png (%d x %d) and #anim.fanim: %s" % (
        os.path.relpath(OUT, ROOT), w, h, ", ".join("%s %d frames %.2f s" % (t, len(fr), sum(ms for _, ms in fr) / 1000.0)
                                                    for t, fr in out.items())))
    print("outline pixels closed after the moves: " + ", ".join("%s %d" % r for r in report))


if __name__ == "__main__":
    main()
