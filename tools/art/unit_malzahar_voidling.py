#!/usr/bin/env python3
"""Malzahar's voidling as a unit of its own: league/champions/league_malzahar_voidling#sheet.png + #anim.fanim.

    python tools/art/unit_malzahar_voidling.py [--check] [--preview <png>]

The add-on league_malzahar spawns the voidlings of Void Swarm (his E's) through the mod API's spawn_unit under this name;
the game draws a unit of a name from asset/base/aseprite_resources/champions/<name> (the add-on's mod.override_info sends
that here) with the tags a champion has - idle, run, attack, hit and dead (the engine's own summons, base `ghoul`).
Every frame is the effect sheet's own pixels (league/effects/league_malzahar_fx, its plain 1x frames: a square a game
pixel, the size the swarm has on screen today; the dense hd_ twins are left out, so the unit needs no league.dll row):
one of the two mirrored voidlings of the swarm picture (w_swarm: the left one, facing right - the way a sheet faces; the
script checks the two are mirror images), moved DX columns right onto the unit's pivot (its middle; its feet already on
the effect's row 11, a unit's ground row):

  idle    the swarm's standing frames 0 and 3 (250 ms: the swarm's own timing);
  run     a scuttling hop: standing (0), the leap with the legs dangling (1), standing (3), the leap (125 ms each);
  attack  standing (0), rearing (1), the bite with its sparks (2) - BITE_MS in - and standing again (3);
  hit     the standing frame a pixel back;
  dead    it drops into the void: standing in the open rift of the swarm's arrival (w_spawn 2, moved up PORTAL_DY rows
          onto the ground row), the open rift alone, the rift closing (3), and an empty frame.
The add-on's unit attack lands on the bite (league_malzahar src/lib.rs: VOID_ACT / VOID_LANDS, checked by its
make_override.py against this sheet's .fanim).
--check: exit 1 when the sheet in the repo is not what this writes. --preview: the frames at 8x on the ground line.
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

FX = os.path.join(ROOT, "league", "effects", "league_malzahar_fx")
OUT = os.path.join(ROOT, "league", "champions", "league_malzahar_voidling")
S = 120                 # the working canvas; its centre (C, C) is the frame's pivot
C = S // 2
FEET = 11               # a unit's ground row under the pivot
DX = 14                 # the swarm's left voidling stands 14 columns left of the effect's pivot (cols -22..-6)
PORTAL_DY = -2          # the rift's last row is the effect's row 13 (its open frame's 14)
SWARM_MS = 250
RUN_MS = 125
ATTACK_MS = (80, 100, 120, 100)
BITE_MS = sum(ATTACK_MS[:2])
HIT_MS = 100
DEAD_MS = (100, 90, 90, 100)


def frames_of(tag):
    """the tag's 1x frames, each on an S x S canvas with its pivot at (C, C)"""
    sheet = np.array(Image.open(G.lp(FX + "#sheet.png")).convert("RGBA"))
    with open(G.lp(FX + "#anim.fanim"), encoding="utf-8-sig") as fh:
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


def over(under, top):
    out = under.copy()
    m = top[..., 3] > 0
    out[m] = top[m]
    return out


def voidling(f):
    out = f.copy()
    out[:, C:] = 0
    return shift(out, DX, 0)


def lowest(f):
    return int(np.nonzero(f[..., 3])[0].max()) - C


def build():
    raw = frames_of("w_swarm")
    for k, f in enumerate(raw):
        if not np.array_equal(f[:, 1:C][:, ::-1], f[:, C + 1:2 * C]):
            sys.exit(f"w_swarm {k}: the two voidlings are no longer mirror images: read the picture again")
    swarm = [voidling(f) for f in raw]
    for k in (0, 2, 3):
        if lowest(swarm[k]) != FEET:
            sys.exit(f"w_swarm {k}: the voidling's lowest row is {lowest(swarm[k])}, not {FEET}: read the picture again")
    rift = [shift(f, 0, PORTAL_DY) for f in frames_of("w_spawn")]
    blank = np.zeros((S, S, 4), np.uint8)
    tags = {
        "idle": [(swarm[0], SWARM_MS), (swarm[3], SWARM_MS)],
        "run": [(swarm[k], RUN_MS) for k in (0, 1, 3, 1)],
        "attack": list(zip([swarm[0], swarm[1], swarm[2], swarm[3]], ATTACK_MS)),
        "hit": [(shift(swarm[0], -1, 0), HIT_MS)],
        "dead": list(zip([over(rift[2], swarm[0]), rift[2], rift[3], blank], DEAD_MS)),
    }
    return tags


def centred(tags):
    """every frame trimmed to an odd size round the pivot (the exported-sheet convention); an empty one 3 x 3"""
    return {tag: [(G.centre_frame(f, -C, -C) if f[..., 3].any() else np.zeros((3, 3, 4), np.uint8), ms) for f, ms in frames]
            for tag, frames in tags.items()}


def preview(tags, path, zoom=8):
    cells = [(tag, i, f) for tag, frames in tags.items() for i, (f, _) in enumerate(frames)]
    half_w, up, down = 20, 30, 14
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
    tags = build()
    if a.preview:
        preview(tags, a.preview)
        print("preview", a.preview)
    out = centred(tags)
    if a.check:
        import tempfile
        tmp = os.path.join(tempfile.mkdtemp(prefix="voidling_"), "league_malzahar_voidling")
        G.write_sheet(tmp, out)

        def read(stem):
            with open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig") as fh:
                return np.array(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA")), json.load(fh)

        same = False
        if os.path.exists(G.lp(OUT + "#sheet.png")) and os.path.exists(G.lp(OUT + "#anim.fanim")):
            (px, an), (px2, an2) = read(OUT), read(tmp)
            same = an == an2 and px.shape == px2.shape and bool((px == px2).all())
        print("league_malzahar_voidling:", "up to date" if same else "stale")
        sys.exit(0 if same else 1)
    w, h = G.write_sheet(OUT, out)
    print("wrote %s#sheet.png (%d x %d) and #anim.fanim: %s" % (
        os.path.relpath(OUT, ROOT), w, h,
        ", ".join("%s %d frames %.2f s" % (t, len(fr), sum(ms for _, ms in fr) / 1000.0) for t, fr in out.items())))


if __name__ == "__main__":
    main()
