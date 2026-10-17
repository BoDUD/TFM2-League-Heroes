#!/usr/bin/env python3
"""Rell's effects from Codex's step-3 delivery (assets/source/rell/codex_fx, from rell_fx_pack_done.zip) as the game
sheets league_rell_fx / league_rell_big (the tags build_rell.py's views bind).

    python tools/art/import_rell_fx.py --prepare <delivery dir>   (once: copies what the import reads)
    python tools/art/import_rell_fx.py [--review DIR]

import_katarina_fx.py's way: Codex's read-backs (pixel_1x/rell_fx_<name>.png: each a row of equal frames, the frame size
in manifest.json) used as they are, checked for hard alpha and the symmetry the pack asked (q_line top to bottom: it
turns with the strike; every other one left to right: the client never mirrors an effect picture). Each frame is placed
by manifest.json's anchor_1x (Codex's: the middle of a hit, the ground line under a body or a ring) on a spot, game px
from the pivot (x forward, y down; a unit's soles are FEET under it):
  HIT   the hits on a unit's body;
  HEAD  the marks over a unit's head (stun stars, the cracked plate, Full Tilt's sigil over her);
  SOLES the pictures standing on the ground round her or a unit (rings, dust, shields, the scraps, the field);
  LINE  Shattering Strike's line: a LineRangeProjectile cast from her is drawn at the line's MIDDLE (champion-data 6),
        so the picture's middle is the projectile.
Frame times: the kit's (build_rell.P, 60 ticks a second) - Q's strike frame (4) starts at 0.38 s (q_at 24 ticks = 0.4 s:
the line hits on its tick 23) and the line stays q_tail ticks after so the strike plays out.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "rell")
CODEX = os.path.join(SRC, "codex_fx")
MOD = os.path.join(ROOT, "league")
FEET = 11                       # game px from the pivot down to the soles' row
HIT = (0, -8)                   # a hit on a unit's body (the pack's heroes 34-46 px)
HEAD = (0, -32)                 # over a unit's head
SOLES = (0, FEET)
LINE = (0, 0)
BIG = {"q_line", "w_jump", "w_crash", "r_cast", "r_on"}

# name -> (mirror, spot, frame times ms)
FX = {
    "a_hit": ("lr", HIT, [40, 50, 60, 70]),
    "p_shred": ("lr", (0, -37), [150] * 4),
    "q_line": ("ud", LINE, [127, 127, 126, 100, 80, 80]),
    "q_hit": ("lr", HIT, [40, 50, 60, 70, 80]),
    "q_stun": ("lr", HEAD, [100] * 4),
    "e_cast": ("lr", SOLES, [60, 70, 80, 90, 100]),
    "e_ms": ("lr", SOLES, [100] * 4),
    "e_ready": ("lr", (0, -39), [120] * 4),
    "e_boom": ("lr", HIT, [40, 50, 70, 80, 90]),
    "w_jump": ("lr", SOLES, [60, 70, 80, 90]),
    "w_crash": ("lr", SOLES, [60, 80, 100, 110, 120, 130]),
    "w_hit": ("lr", HIT, [40, 50, 60, 70]),
    "w_shield": ("lr", SOLES, [120] * 4),
    "foot": ("lr", SOLES, [150] * 4),
    "w2_mount": ("lr", SOLES, [60, 60, 70, 70, 73]),
    "w2_hit": ("lr", HIT, [40, 50, 60, 70, 80]),
    "r_cast": ("lr", SOLES, [60, 80, 90, 90, 90, 90]),
    "r_on": ("lr", SOLES, [83, 83, 84, 83, 83, 84]),
    "r_yank": ("lr", SOLES, [50, 60, 70, 80]),
    "r_hit": ("lr", HIT, [40, 50, 60]),
}


def load(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


def manifest():
    with open(os.path.join(CODEX, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)
    return {it["name"]: it for it in m["effects"]}


def frames_of(name, item):
    a = load(os.path.join(CODEX, "pixel_1x", f"rell_fx_{name}.png"))
    a[a[..., 3] < 128] = 0
    a[..., 3][a[..., 3] > 0] = 255
    w, h = item["frame_size_1x"]
    n = item["frames"]
    if a.shape[1] != n * w or a.shape[0] != h:
        sys.exit(f"{name}: pixel_1x is {a.shape[1]}x{a.shape[0]}, manifest says {n} frames of {w}x{h}")
    return [a[:, k * w:(k + 1) * w].copy() for k in range(n)]


def box(f):
    ys, xs = np.nonzero(f[..., 3] > 0)
    return (xs.min(), xs.max(), ys.min(), ys.max()) if len(xs) else None


def placed(name, item):
    mirror, spot, times = FX[name]
    cells = frames_of(name, item)
    if len(cells) != len(times):
        sys.exit(f"{name}: {len(cells)} frames, {len(times)} times")
    ax, ay = item["anchor_1x"]
    seq = []
    for c, ms in zip(cells, times):
        if box(c) is None:
            seq.append((np.zeros((3, 3, 4), np.uint8), float(ms)))
            continue
        # the anchor may sit on a pixel edge (a cell's middle): the frame's own middle column then lands on the spot
        seq.append((G.centre_frame(c, spot[0] - int(np.floor(ax)), spot[1] - int(round(ay))), float(ms)))
    return seq, cells


def check(cells):
    bad = []
    for name, cs in cells.items():
        mirror = FX[name][0]
        for k, c in enumerate(cs):
            if set(np.unique(c[..., 3])) - {0, 255}:
                bad.append(f"{name} {k + 1} soft alpha")
            if box(c) is None:
                bad.append(f"{name} {k + 1} empty")
                continue
            if mirror == "lr" and not (c == c[:, ::-1]).all():
                bad.append(f"{name} {k + 1} not symmetric left to right in its cell")
            if mirror == "ud" and not (c == c[::-1]).all():
                bad.append(f"{name} {k + 1} not symmetric top to bottom in its cell")
    return bad


def review(out_dir, e):
    from PIL import ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for name, seq in e.items():
        z = 3 if name in BIG else 6
        tiles = []
        for f, ms in seq:
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), (52, 60, 46, 255))
            bg.alpha_composite(Image.fromarray(f))
            d = ImageDraw.Draw(bg)
            cx, cy = f.shape[1] // 2, f.shape[0] // 2
            d.point((cx, cy), fill=(255, 0, 0, 255))
            tiles.append(bg.resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST))
        W = sum(t.width + 4 for t in tiles)
        H = max(t.height for t in tiles) + 14
        r = Image.new("RGB", (W, H), (16, 16, 16))
        ImageDraw.Draw(r).text((2, 1), f"{name} (red: the pivot)", fill=(255, 255, 0))
        x = 0
        for t in tiles:
            r.paste(t.convert("RGB"), (x, 14))
            x += t.width + 4
        rows.append(r)
    W = max(r.width for r in rows)
    sheet = Image.new("RGB", (W, sum(r.height + 4 for r in rows)), (0, 0, 0))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height + 4
    sheet.save(os.path.join(out_dir, "rell_fx_frames.png"))
    print(os.path.join(out_dir, "rell_fx_frames.png"), sheet.size)


def prepare(delivery):
    """The parts of Codex's delivery the import reads, into assets/source/rell/codex_fx (the raw pictures and the 8x
    previews stay in the delivery: the read-backs are good)."""
    os.makedirs(os.path.join(CODEX, "pixel_1x"), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(delivery, "pixel_1x"))):
        shutil.copy2(os.path.join(delivery, "pixel_1x", f), os.path.join(CODEX, "pixel_1x", f))
    for f in ("HANDOFF.md", "manifest.json", "generation-prompts.txt"):
        shutil.copy2(os.path.join(delivery, f), os.path.join(CODEX, f))
    print("prepared", CODEX)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", help="Codex's delivery folder (unzipped)")
    ap.add_argument("--review", help="write every effect's frames here")
    a = ap.parse_args()
    if a.prepare:
        prepare(a.prepare)
        return
    man = manifest()
    missing = set(FX) - set(man)
    if missing:
        sys.exit(f"not delivered: {sorted(missing)}")
    e, cells = {}, {}
    for name in FX:
        e[name], cells[name] = placed(name, man[name])
    bad = check(cells)
    if bad:
        sys.exit("\n".join(bad))
    tables = {"league_rell_fx": {}, "league_rell_big": {}}
    for name, seq in e.items():
        tables["league_rell_big" if name in BIG else "league_rell_fx"][name] = seq
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        review(a.review, e)


if __name__ == "__main__":
    main()
