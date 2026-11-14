"""Shared helpers of the unit sheets cut by code from a hero's existing effect frames (tools/art/unit_*.py, round 2 of
"summons as real units", 2026-11-14; the user: 「召唤物的全做啊 剩下的一批英雄也做了啊」).

A unit spawned through the mod API's spawn_unit under a name is drawn like a champion from
asset/base/aseprite_resources/champions/<name> (its add-on's mod.override_info sends that to the main pack's
league/champions/<name>) with the tags a summon plays: idle, run, attack, hit and dead (the engine's own summons, base
`ghoul`). Every frame here is pixels the effect sheet already holds - moved, mirrored or cut, never drawn. A frame is
worked on an S x S canvas whose centre (C, C) is its pivot; a unit's ground row is FEET rows under the pivot.

    frames_of(stem, tag)   the tag's frames on canvases (pivot = the frame's centre, the exported-sheet convention)
    shift / over / lowest / blank / centred / preview
    run(name, out_stem, build, feet=FEET)   the scripts' main: write the sheet, or --check it, or --preview it at 8x
"""
import argparse
import json
import os
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

S = 200                 # the working canvas; its centre (C, C) is the frame's pivot
C = S // 2
FEET = 11               # a unit's ground row under the pivot (a champion's)
CHAMPIONS = os.path.join(ROOT, "league", "champions")
EFFECTS = os.path.join(ROOT, "league", "effects")


def frames_of(stem, tag):
    """[(canvas, ms)] of the tag: each frame on an S x S canvas with its pivot (the frame's centre) at (C, C)."""
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
        out.append((c, round(f.get("duration", d.get("duration", 0.1)) * 1000)))
    return out


def shift(f, dx, dy):
    out = np.zeros_like(f)
    ys, xs = np.nonzero(f[..., 3])
    ok = (ys + dy >= 0) & (ys + dy < S) & (xs + dx >= 0) & (xs + dx < S)
    out[ys[ok] + dy, xs[ok] + dx] = f[ys[ok], xs[ok]]
    return out


def over(under, top):
    out = under.copy()
    m = top[..., 3] > 0
    out[m] = top[m]
    return out


def mirror(f):
    """left and right swapped about the pivot column"""
    return np.roll(f[:, ::-1], 1, axis=1)          # column x takes column 2C - x


def lowest(f):
    """the lowest opaque row, pivot-relative"""
    return int(np.nonzero(f[..., 3])[0].max()) - C


def blank():
    return np.zeros((S, S, 4), np.uint8)


def to_feet(f, feet=FEET):
    """f moved up or down so its lowest row is the unit's ground row (an empty frame as it is)"""
    return shift(f, 0, feet - lowest(f)) if f[..., 3].any() else f


def centred(tags):
    """every frame trimmed to an odd size round the pivot (the exported-sheet convention); an empty one 3 x 3"""
    return {tag: [(G.centre_frame(f, -C, -C) if f[..., 3].any() else np.zeros((3, 3, 4), np.uint8), ms) for f, ms in frames]
            for tag, frames in tags.items()}


def preview(tags, path, feet=FEET, zoom=8, per_row=8):
    """the frames at zoom on the ground line (cyan), the pivot (magenta), the tag and index over each"""
    cells = [(tag, i, f) for tag, frames in tags.items() for i, (f, _) in enumerate(frames)]
    boxes = [np.nonzero(f[..., 3]) for _, _, f in cells]
    xs = [int(abs(b[1] - C).max()) for b in boxes if len(b[1])] or [4]
    ys_up = [int(C - b[0].min()) for b in boxes if len(b[0])] or [4]
    half_w, up, down = max(xs) + 2, max(ys_up) + 2, feet + 3
    cw, ch = (2 * half_w + 1) * zoom, (up + down + 1) * zoom + 14
    rows = (len(cells) + per_row - 1) // per_row
    img = Image.new("RGBA", (per_row * cw, rows * ch), (58, 58, 70, 255))
    dr = ImageDraw.Draw(img)
    for n, (tag, i, f) in enumerate(cells):
        ox, oy = (n % per_row) * cw, (n // per_row) * ch + 14
        crop = Image.fromarray(f[C - up:C + down + 1, C - half_w:C + half_w + 1], "RGBA")
        img.alpha_composite(crop.resize((crop.width * zoom, crop.height * zoom), Image.NEAREST), (ox, oy))
        gy = oy + (up + feet + 1) * zoom
        dr.line([(ox, gy), (ox + cw - 2, gy)], fill=(0, 255, 255, 255))
        px, py = ox + half_w * zoom, oy + up * zoom
        dr.rectangle([px, py, px + zoom - 1, py + zoom - 1], outline=(255, 0, 255, 255))
        dr.text((ox + 3, oy - 13), "%s %d" % (tag, i), fill=(255, 255, 0, 255))
    img.save(path)


def read_sheet(stem):
    with open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig") as fh:
        return np.array(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA")), json.load(fh)


def run(name, out_stem, build, feet=FEET):
    """The command line of a unit sheet script: write `out_stem`#sheet.png / #anim.fanim from `build()` (tags of
    [(canvas, ms)]), or --check it (exit 1 when the repo's is not what this writes), or --preview <png> at 8x."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview")
    a = ap.parse_args()
    tags = build()
    for tag in ("idle", "run", "attack", "hit", "dead"):
        if not tags.get(tag):
            sys.exit(f"{name}: no {tag} frames")
    if a.preview:
        preview(tags, a.preview, feet)
        print("preview", a.preview)
    out = centred(tags)
    if a.check:
        tmp = os.path.join(tempfile.mkdtemp(prefix="unit_"), name)
        G.write_sheet(tmp, out)
        same = False
        if os.path.exists(G.lp(out_stem + "#sheet.png")) and os.path.exists(G.lp(out_stem + "#anim.fanim")):
            (px, an), (px2, an2) = read_sheet(out_stem), read_sheet(tmp)
            same = an == an2 and px.shape == px2.shape and bool((px == px2).all())
        print(f"{name}:", "up to date" if same else "stale")
        sys.exit(0 if same else 1)
    w, h = G.write_sheet(out_stem, out)
    print("wrote %s#sheet.png (%d x %d) and #anim.fanim: %s" % (
        os.path.relpath(out_stem, ROOT), w, h,
        ", ".join("%s %d frames %.2f s" % (t, len(fr), sum(ms for _, ms in fr) / 1000.0) for t, fr in out.items())))
