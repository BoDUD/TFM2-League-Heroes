#!/usr/bin/env python3
"""Naafiri's packmate as a unit of its own: league/champions/league_naafiri_packmate#sheet.png + #anim.fanim.

    python tools/art/unit_naafiri_packmate.py [--check] [--preview <png>]

The add-on league_naafiri spawns her packmates through the mod API's spawn_unit under this name (and plays her solo_*
tags while they are units: tools/art/rig_naafiri.py); the game draws a unit of a name from
asset/base/aseprite_resources/champions/<name> (the add-on's mod.override_info sends that here) with the tags a champion
has - idle, run, attack, hit and dead (base `ghoul`'s). Nothing is drawn anew: the frames are made by rig_naafiri.py's
own pieces - the packmate's design (assets/source/naafiri/hd/pack.png, 49 x 24 squares at her PPU 1.5) and Codex's
packmate poses (hd/pose_p_run1-4, pose_p_bite) - each placed on her rig's canvas the way her frames place a packmate
(Canvas.mate_at: its middle on the pivot's column, its lowest square on the ground row), then brought to 1x the way the
rig brings her own frames (ppu_rig.Rig.finish, one_of, strips.complete_outline in her outline colour): the size the
painted packmates have in her frames (16 game px). Plain 1x frames, no hd_ twins: a unit sheet league.dll has no row for
(the row it would take: ("league_naafiri_packmate", 1.5, ...) with hd_ twins - see the add-on's README).

  idle    the design breathing as her idle's packmates do (rows above the legs set down 0 0 1 1 1 1 0 0, 150 ms);
  run     the gallop p_run1-4 (150 ms, her own run's pace);
  attack  standing, the leap (p_run4 two squares up), the bite (p_bite) - BITE_MS in - held, standing (her attack's
          70 100 100 90 60 ms);
  hit     struck white two squares back, then a square back (her hit's way);
  dead    struck white, then gone (League's packmates vanish).
--check: exit 1 when the sheet in the repo is not what this writes. --preview: the frames at 8x on the ground line.
Needs scipy (ppu_rig), so it runs as `python`, not `python -I`.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import ppu_rig as R  # noqa: E402
import rig_naafiri as RN  # noqa: E402
import strips as G  # noqa: E402

OUT = os.path.join(ROOT, "league", "champions", "league_naafiri_packmate")
FEET = 11
ATTACK_MS = (70, 100, 100, 90, 60)
BITE_MS = sum(ATTACK_MS[:2])
BREATHS = (0, 0, 1, 1, 1, 1, 0, 0)


def canvases():
    """{tag: [(rig canvas or None for an empty frame, ms)]}"""
    C = RN.Canvas()

    def mate(name, dx=0, lift=0, breath=0, flash=False):
        can = C.blank()
        a, x0, y0 = C.mate_at(name, (0, 0, False), dx, lift, breath)
        C.stamp(can, a, x0, y0)
        return RN.hit_white(can) if flash else can

    tags = {
        "idle": [(mate("pack", breath=b), 150) for b in BREATHS],
        "run": [(mate("p_run%d" % k), 150) for k in (1, 2, 3, 4)],
        "attack": list(zip([mate("pack"), mate("p_run4", lift=2), mate("p_bite", dx=4), mate("p_bite", dx=3), mate("pack")],
                           ATTACK_MS)),
        "hit": [(mate("pack", dx=-2, flash=True), 100), (mate("pack", dx=-1), 100)],
        "dead": [(mate("pack", flash=True), 120), (None, 100)],
    }
    return C, tags


def one_x(C, can):
    """the rig canvas brought to 1x as ppu_rig.Rig.export brings a frame (odd size round the pivot)"""
    if can is None:
        return np.zeros((3, 3, 4), np.uint8)
    ppu = RN.PPU
    body = C.rig.finish(can)
    px, py = float(C.rig.CX), C.rig.GY - R.FEET * ppu
    ys, xs = np.nonzero(body[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / ppu - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / ppu - 0.5))
    hh = max(hh, int(np.ceil(R.FEET)) + 1)
    return G.complete_outline(R.one_of(body, px, py, hw, hh, ppu), color=C.outline)[0]


def build():
    C, tags = canvases()
    out = {tag: [(one_x(C, can), ms) for can, ms in frames] for tag, frames in tags.items()}
    # every standing frame on the ground row, like a hero's feet
    for tag in ("idle", "attack"):
        f = out[tag][0][0]
        low = int(np.nonzero(f[..., 3])[0].max()) - (f.shape[0] - 1) // 2
        if low != FEET:
            sys.exit(f"{tag}: the packmate's lowest row is {low}, not {FEET}: read the rig again")
    return out


def preview(tags, path, zoom=8):
    S, C0 = 81, 40
    cells = [(tag, i, f) for tag, frames in tags.items() for i, (f, _) in enumerate(frames)]
    half_w, up, down = 30, 30, 14
    per_row = 7
    cw, ch = (2 * half_w + 1) * zoom, (up + down + 1) * zoom + 14
    rows = (len(cells) + per_row - 1) // per_row
    img = Image.new("RGBA", (per_row * cw, rows * ch), (58, 58, 70, 255))
    dr = ImageDraw.Draw(img)
    for n, (tag, i, f) in enumerate(cells):
        can = np.zeros((S, S, 4), np.uint8)
        h, w = f.shape[:2]
        can[C0 - (h - 1) // 2:C0 - (h - 1) // 2 + h, C0 - (w - 1) // 2:C0 - (w - 1) // 2 + w] = f
        ox, oy = (n % per_row) * cw, (n // per_row) * ch + 14
        crop = Image.fromarray(can[C0 - up:C0 + down + 1, C0 - half_w:C0 + half_w + 1], "RGBA")
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
    out = build()
    if a.preview:
        preview(out, a.preview)
        print("preview", a.preview)
    if a.check:
        import tempfile
        tmp = os.path.join(tempfile.mkdtemp(prefix="packmate_"), "league_naafiri_packmate")
        G.write_sheet(tmp, out)

        def read(stem):
            with open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig") as fh:
                return np.array(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA")), json.load(fh)

        same = False
        if os.path.exists(G.lp(OUT + "#sheet.png")) and os.path.exists(G.lp(OUT + "#anim.fanim")):
            (px, an), (px2, an2) = read(OUT), read(tmp)
            same = an == an2 and px.shape == px2.shape and bool((px == px2).all())
        print("league_naafiri_packmate:", "up to date" if same else "stale")
        sys.exit(0 if same else 1)
    w, h = G.write_sheet(OUT, out)
    print("wrote %s#sheet.png (%d x %d) and #anim.fanim: %s" % (
        os.path.relpath(OUT, ROOT), w, h,
        ", ".join("%s %d frames %.2f s" % (t, len(fr), sum(ms for _, ms in fr) / 1000.0) for t, fr in out.items())))


if __name__ == "__main__":
    main()
