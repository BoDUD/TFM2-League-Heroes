#!/usr/bin/env python3
"""Kayn's Darkin and Shadow Assassin bodies for the actions the game plays by name - idle, run, hit, dead - posed from
the approved form designs' own parts (tools/art/rig_kayn.py's cut and renderer), for the full transform of the native
add-on addons/league_kayn_form (the game draws a unit's body from "asset/base/aseprite_resources/champions/{name}"; the
add-on renames Kayn's view to league_kayd / league_kays when he transforms, and those names are sent to the sheets
league_kayn_darkin / league_kayn_shadow that import_native.py builds from these strips and Kayn's own).

    python tools/art/rig_kayn_forms.py [--review DIR]

Writes assets/source/native/kayn_{rh,sh}_{idle,run,hit,dead}.png (8x strips in Kayn's cells: the same cell, layout,
pivots and timings as his base idle / run / hit / dead, kayn_cells.json). The user: 「用造型像素摆」.
  idle  the design itself, six times (no breathing, as his base idle's slots);
  hit   pushed back 2 then 1 squares, the upper body a square further back (no shear anywhere: it bent the scythe);
  run   the design's own legs, each turned about its hip joint, one forward as the other goes back (their tops stay
        joined to the body), the body leaning forward and a row up as the legs pass, the arms swinging;
  dead  struck back, crouching, kneeling, bowing forward, then bowed down and dissolving (a quarter, a half, three
        quarters of the pixels gone in an ordered dither): the forms are wider than tall, and turned a quarter to lie
        down like his base death they stood on end.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_kayn as R  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
CELLS = os.path.join(NATIVE, "kayn_cells.json")
Z = 8
CW, CH = 128, 96
PREFIX = {"darkin": "rh_", "shadow": "sh_"}
HIPS = {"darkin": (62, 85), "shadow": (63, 86)}
BODY_TAGS = ("idle", "run", "hit", "dead")
# the run's legs moved toward each other (squares, near leg, far leg): the near hip (57 / 68) and the far (65 / 61)
PULL_IN = {"darkin": (3, -3), "shadow": (-3, 3)}


def legs(form, name, *ops):
    return [["sprite", f"legs_{name}", list(HIPS[form])], *ops]


def order_with_hips(form):
    """The form's drawing order with the leg pair ('hips') where the far leg was, both legs left out."""
    _, order, _ = R.load_parts(form)
    out = []
    for p in order:
        if p == "far_leg":
            out.append("hips")
        elif p != "near_leg":
            out.append(p)
    return out


def upper_at(dx, dy):
    """The upper body (head, hair, torso, arms, scythe) moved whole - a lean without shearing the scythe crooked
    (「武器看起来有点歪」)."""
    return {p: [["at", dx, dy]] for p in ("head", "hair", "torso", "near_arm", "far_arm", "scythe")}


def specs(form):
    """{tag: [frame spec for rig_kayn.render]}."""
    o = order_with_hips(form)
    # the run: the design's own two legs, each turned about its own hip joint (RotSprite), one forward while the other
    # goes back - their tops stay where the design joins them to the body (the first version's leg pairs, the tuck and
    # the hang drawn apart from the body, came loose at the hips: 「双腿那里做的不好 脱节的」); the body a row up on the
    # passing frames, the arms swinging against the legs
    # the legs drawn in to almost one hip and swung wide, so each foot passes the other (League's crossing steps; the
    # first rotation version kept the stance's hips 7-8 squares apart and its feet never crossed: 「走路没有交叉步」)
    swing = [36, 18, 0, -18, -36, -18, 0, 18]       # degrees, + = the near leg forward
    bob = [1, 0, -1, 0, 1, 0, -1, 0]
    near_x, far_x = PULL_IN[form]
    run = []
    # no shear: the lean sheared the scythe crooked (「武器看起来有点歪」); the upper body leans by moving a square ahead
    # whole (head, hair, torso, arms, scythe), the scythe as drawn
    upper = {p: [["at", 1, 0]] for p in ("head", "hair", "torso", "scythe")}
    for a, dy in zip(swing, bob):
        parts = dict(upper)
        parts.update({"near_leg": [["deg", a], ["at", near_x, 0]], "far_leg": [["deg", -a], ["at", far_x, 0]],
                      "near_arm": [["deg", -a * 0.5], ["at", 1, 0]], "far_arm": [["deg", a * 0.5], ["at", 1, 0]]})
        run.append({"move": [1, dy], "parts": parts})
    dead = [
        {"move": [-2, 0], "parts": upper_at(-1, 0)},
        {"order": o, "move": [-1, 4], "parts": {"hips": legs(form, "crouch")}},
        {"order": o, "move": [0, 5], "parts": {"hips": legs(form, "kneel"), **upper_at(1, 0)}},
        {"order": o, "move": [1, 5], "parts": {"hips": legs(form, "kneel"), **upper_at(2, 1)}},
        {"order": o, "move": [1, 5], "parts": {"hips": legs(form, "kneel"), **upper_at(3, 2)}},
        "fade", "fade", "fade",
    ]
    return {
        "idle": [{}] * 6,
        "hit": [{"move": [-2, 0], "parts": upper_at(-1, 0)}, {"move": [-1, 0], "parts": upper_at(-1, 0)}],
        "run": run,
        "dead": dead,
    }


# a 4x4 ordered-dither threshold: a pixel goes once the fade passes its cell's rank (0..15)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])


def dissolving(form, cache, pivot, k):
    """The death's end (k = 0, 1, 2): bowed down on his knees, dissolving - a quarter, a half, three quarters of the
    pixels gone in an ordered dither (the forms are wider than they are tall with their arms, horns, robe and scythe:
    turned a quarter to lie down they stood on end)."""
    o = order_with_hips(form)
    bow = {"order": o, "move": [1, 5], "parts": {"hips": legs(form, "kneel"), **upper_at(4, 3)}}
    f = R.K.outlined(R.render(form, bow, pivot, cache))      # outlined before the dither (import_native leaves these
    gone = (k + 1) * 4                                         # strips as they are: an outline round every dot)
    ys, xs = np.mgrid[0:f.shape[0], 0:f.shape[1]]
    f[BAYER[ys % 4, xs % 4] < gone] = 0
    return f


def build(form):
    with open(CELLS, encoding="utf-8") as f:
        cells = json.load(f)["tags"]
    cache = R.load_parts(form)
    out = {}
    for tag, fl in specs(form).items():
        frames = []
        for k, fs in enumerate(fl):
            piv = tuple(cells[tag][k]["pivot"])
            if fs == "fade":
                frames.append(dissolving(form, cache, piv, k - 5))
            else:
                frames.append(R.K.outlined(R.render(form, fs, piv, cache)))
        if len(frames) != len(cells[tag]):
            sys.exit(f"{form} {tag}: {len(frames)} frames, Kayn's {tag} has {len(cells[tag])}")
        out[tag] = frames
    return out


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def save_strip(path, frames):
    cols, rows = layout(len(frames))
    a = np.zeros((rows * CH, cols * CW, 4), np.uint8)
    for k, f in enumerate(frames):
        f = f.copy()
        f[f[..., 3] < 128] = 0
        f[f[..., 3] > 0, 3] = 255
        a[(k // cols) * CH:(k // cols + 1) * CH, (k % cols) * CW:(k % cols + 1) * CW] = f
    Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1)).save(R.lp(path))


def review(built, path, z=4):
    rows = []
    for form, tags in built.items():
        for tag, frames in tags.items():
            rows.append((f"{form} {tag}", frames))
    x0, x1, y0, y1 = 4, 124, 16, 84
    w, h = (x1 - x0) * z, (y1 - y0) * z
    img = Image.new("RGB", (8 * (w + 4) + 110, len(rows) * (h + 4)), (40, 40, 40))
    d = ImageDraw.Draw(img)
    for r, (label, frames) in enumerate(rows):
        d.text((4, r * (h + 4) + 4), label, fill=(255, 255, 255))
        for k, f in enumerate(frames):
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (110, 130, 110, 255))
            bg.alpha_composite(Image.fromarray(np.ascontiguousarray(R.K.outlined(f)[y0:y1, x0:x1])))
            img.paste(bg.resize((w, h), Image.NEAREST), (110 + k * (w + 4), r * (h + 4)))
    img.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", help="write the posed frames to this folder (form_bodies.png) and nothing else")
    a = ap.parse_args()
    built = {form: build(form) for form in PREFIX}
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        review(built, os.path.join(a.review, "form_bodies.png"))
        print(os.path.join(a.review, "form_bodies.png"))
        return
    for form, tags in built.items():
        for tag, frames in tags.items():
            path = os.path.join(NATIVE, f"kayn_{PREFIX[form]}{tag}.png")
            save_strip(path, frames)
            print(os.path.relpath(path, ROOT), len(frames), "frames")


if __name__ == "__main__":
    main()
