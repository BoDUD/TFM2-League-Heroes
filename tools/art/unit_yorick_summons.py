#!/usr/bin/env python3
"""Yorick's summons as units of their own: league/champions/league_yorick_walker and league_yorick_maiden
(#sheet.png + #anim.fanim each).

    python tools/art/unit_yorick_summons.py [--check] [--preview <dir>]

The add-on league_yorick spawns the Mist Walkers (the Awakening's, and the Maiden's escort) and the Maiden of the Mist
through the mod API's spawn_unit under these names; the game draws a unit of a name from asset/base/aseprite_resources/
champions/<name> (the add-on's mod.override_info sends that here) with the tags a champion has - the engine's own summons
(base `ghoul`) carry idle, run, attack, hit and dead, so those five. Every frame is the effect sheets' own pixels
(league/effects/league_yorick_fx and league_yorick_big, their plain 1x frames: a square a game pixel, the size the
pictures have on screen today; the dense hd_ twins are left out, so the units need no league.dll row):

  walker  one of the two mirrored walkers of the swarm picture (k_swarm: the left one, facing right - the way a sheet
          faces), moved WALKER_DX columns right onto the unit's pivot and WALKER_DY rows (its mist's last row on a unit's
          ground row, FEET under the pivot):
            idle    the swarm's crouched frames 0, 1, 5, 3 (167 ms: the swarm's own timing);
            run     a bound: crouched (0), the lunge (4) two rows up, crouched (5), the lunge a row up (110 ms each);
            attack  crouched (0), rearing (2), the lunge with the jaws wide (4) - the bite, WALKER_BITE_MS in - and down
                    again (5);
            hit     the crouched frame a pixel back;
            dead    its rise out of the grave (k_spawn's left walker, moved alike) backwards - it sinks into the mound -
                    and an empty frame;
  maiden  the Maiden of r_maiden (she faces the viewer: no side to turn), moved MAIDEN_DY rows down (the last row of her
          mist lies on the effect's pivot row, which the riding picture puts 11 squares above the champion's feet; a
          unit's ground row is FEET under its pivot):
            idle    her floating loop, r_maiden 0-5 (167 ms);
            run     arms lowered, 2 and 3, the second and fourth a row higher - a gliding bob (120 ms each);
            attack  arms up (1, 0), then down (2: the claws, MAIDEN_CLAW_MS in) and (3);
            hit     arms lowered (2) a pixel back;
            dead    her rising out of the mist (r_spawn, moved alike) backwards - she sinks back into it - and an empty
                    frame.
The add-on's unit attacks land on the frames above (league_yorick src/lib.rs: WALK_LANDS / WALK_ACT, MAID_LANDS /
MAID_ACT; checked by its make_override.py against this sheet's .fanim).
--check: exit 1 when a sheet in the repo is not what this writes. --preview DIR: each sheet's frames at 8x on the ground
line (<DIR>/league_yorick_walker.png, ...).
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

FX = os.path.join(ROOT, "league", "effects", "league_yorick_fx")
BIG = os.path.join(ROOT, "league", "effects", "league_yorick_big")
OUT = os.path.join(ROOT, "league", "champions")
S = 160                 # the working canvas; its centre (C, C) is the frame's pivot
C = S // 2
FEET = 11               # a unit's ground row under the pivot (every hero's soles)
WALKER_DX = 18          # the swarm's left walker stands 18 columns left of the effect's pivot (its middle, cols -27..-9)
WALKER_DY = -1          # its mist's last row is the effect's row 12
MAIDEN_DY = 11          # her mist's last row is the effect's pivot row
SWARM_MS = 167
WALKER_RUN_MS = 110
WALKER_ATTACK_MS = (70, 100, 120, 90)
WALKER_BITE_MS = sum(WALKER_ATTACK_MS[:2])
HIT_MS = 100
SINK_MS = 80
MAIDEN_RUN_MS = 120
MAIDEN_ATTACK_MS = (80, 100, 120, 100)
MAIDEN_CLAW_MS = sum(MAIDEN_ATTACK_MS[:2])
BLANK_MS = 100


def frames_of(stem, tag):
    """the tag's 1x frames, each on an S x S canvas with its pivot at (C, C)"""
    sheet = np.array(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA"))
    with open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig") as fh:
        anim = json.load(fh)["anims"]
    out = []
    for f in anim[tag]["frames"]:
        d = f["data"]
        x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
        c = np.zeros((S, S, 4), np.uint8)
        cx, cy = (w - 1) // 2, (h - 1) // 2
        c[C - cy:C - cy + h, C - cx:C - cx + w] = sheet[y:y + h, x:x + w]
        out.append(c)
    return out


def shift(f, dx, dy):
    out = np.zeros_like(f)
    ys, xs = np.nonzero(f[..., 3])
    ok = (ys + dy >= 0) & (ys + dy < S) & (xs + dx >= 0) & (xs + dx < S)
    out[ys[ok] + dy, xs[ok] + dx] = f[ys[ok], xs[ok]]
    return out


def left_half(f):
    """the walker left of the effect's pivot (the right one is its mirror image)"""
    out = f.copy()
    out[:, C:] = 0
    return out


def walker(f):
    return shift(left_half(f), WALKER_DX, WALKER_DY)


def lowest(f):
    return int(np.nonzero(f[..., 3])[0].max()) - C


def build_walker():
    swarm = [walker(f) for f in frames_of(FX, "k_swarm")]
    rise = [walker(f) for f in frames_of(FX, "k_spawn")]
    # the swarm's frames are the two walkers mirrored about the pivot: check that the left one is all there is to take
    for k, f in enumerate(frames_of(FX, "k_swarm")):
        if not np.array_equal(f[:, 1:C][:, ::-1], f[:, C + 1:2 * C]):
            sys.exit(f"k_swarm {k}: the two walkers are no longer mirror images: read the picture again")
    for k, f in enumerate(swarm):
        if lowest(f) != FEET:
            sys.exit(f"k_swarm {k}: the walker's lowest row is {lowest(f)}, not {FEET}: read the picture again")
    blank = np.zeros((S, S, 4), np.uint8)
    tags = {
        "idle": [(swarm[k], SWARM_MS) for k in (0, 1, 5, 3)],
        "run": [(swarm[0], WALKER_RUN_MS), (shift(swarm[4], 0, -2), WALKER_RUN_MS), (swarm[5], WALKER_RUN_MS),
                (shift(swarm[4], 0, -1), WALKER_RUN_MS)],
        "attack": list(zip([swarm[0], swarm[2], swarm[4], swarm[5]], WALKER_ATTACK_MS)),
        "hit": [(shift(swarm[0], -1, 0), HIT_MS)],
        "dead": [(f, SINK_MS) for f in rise[::-1]] + [(blank, BLANK_MS)],
    }
    return tags


def build_maiden():
    loop = [shift(f, 0, MAIDEN_DY) for f in frames_of(BIG, "r_maiden")]
    rise = [shift(f, 0, MAIDEN_DY) for f in frames_of(BIG, "r_spawn")]
    for k, f in enumerate(loop):
        if lowest(f) != FEET:
            sys.exit(f"r_maiden {k}: her lowest row is {lowest(f)}, not {FEET}: read the picture again")
    blank = np.zeros((S, S, 4), np.uint8)
    tags = {
        "idle": [(f, SWARM_MS) for f in loop],
        "run": [(loop[2], MAIDEN_RUN_MS), (shift(loop[3], 0, -1), MAIDEN_RUN_MS), (loop[2], MAIDEN_RUN_MS),
                (shift(loop[3], 0, -1), MAIDEN_RUN_MS)],
        "attack": list(zip([loop[1], loop[0], loop[2], loop[3]], MAIDEN_ATTACK_MS)),
        "hit": [(shift(loop[2], -1, 0), HIT_MS)],
        "dead": [(f, SINK_MS) for f in rise[::-1]] + [(blank, BLANK_MS)],
    }
    return tags


SHEETS = {"league_yorick_walker": build_walker, "league_yorick_maiden": build_maiden}


def centred(tags):
    """every frame trimmed to an odd size round the pivot (the exported-sheet convention); an empty one 3 x 3"""
    out = {}
    for tag, frames in tags.items():
        out[tag] = [(G.centre_frame(f, -C, -C) if f[..., 3].any() else np.zeros((3, 3, 4), np.uint8), ms)
                    for f, ms in frames]
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


def read(stem):
    with open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig") as fh:
        return np.array(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA")), json.load(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview")
    a = ap.parse_args()
    stale = []
    for name, build in SHEETS.items():
        tags = build()
        if a.preview:
            os.makedirs(a.preview, exist_ok=True)
            preview(tags, os.path.join(a.preview, name + ".png"))
        out = centred(tags)
        stem = os.path.join(OUT, name)
        if a.check:
            import tempfile
            tmp = os.path.join(tempfile.mkdtemp(prefix="yorick_units_"), name)
            G.write_sheet(tmp, out)
            same = False
            if os.path.exists(G.lp(stem + "#sheet.png")) and os.path.exists(G.lp(stem + "#anim.fanim")):
                (px, an), (px2, an2) = read(stem), read(tmp)
                same = an == an2 and px.shape == px2.shape and bool((px == px2).all())
            print(name + ":", "up to date" if same else "stale")
            if not same:
                stale.append(name)
            continue
        w, h = G.write_sheet(stem, out)
        print("wrote %s#sheet.png (%d x %d) and #anim.fanim: %s" % (
            os.path.relpath(stem, ROOT), w, h,
            ", ".join("%s %d frames %.2f s" % (t, len(fr), sum(ms for _, ms in fr) / 1000.0) for t, fr in out.items())))
    if a.check:
        sys.exit(1 if stale else 0)


if __name__ == "__main__":
    main()
