#!/usr/bin/env python3
"""Import Caitlyn's effects (assets/source/caitlyn/PROMPTS.md, 22 effects) as the game sheet.

    python tools/art/import_caitlyn.py --native <Codex's delivery folder>   # once: Codex's 1x strips -> native strips
    python tools/art/import_caitlyn.py                                      # native strips -> the effect sheet

The body comes from Codex's strips and tools/art/import_native.py. Codex delivered the effects finished at game size
(outputs/caitlyn-fx-q-larger-v2, 2026-10-01: Q's bolt, burst and hit redrawn about 30% larger - 32 x 14, 24 x 18,
22 x 22 - after the user found Q faint in game; the first import had also taken e_hit, hs_shot, r_hit, r_muzzle, w_trap,
w_fade, e_net and e_slow while Codex was still rewriting them, so the whole pack is re-imported; its HANDOFF, manifest
and bindings in assets/source/caitlyn/codex_fx): `game_size/
caitlyn_fx_<tag>.png` in the pack's palettes, binary alpha, every cell `assets[].game_size_px` big on the strip's
`grid` (columns, rows), an anchor per strip (`anchor_normalized`) and suggested ticks per frame. --native keeps every
pixel: each cell is cut by the grid and copied 1:1 into assets/source/caitlyn/caitlyn_fx_<tag>.png (8x), its anchor,
frame count and ticks into caitlyn_fx_anchors.json.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; a pixel's middle
on whole numbers) and times it:
- the muzzle flashes (anchored on their left edge's middle) just past the barrel's last pixel of her firing frames
  (the second design, tools/art/rig_caitlyn.py: the attack fires from the hip in frames 3-4, the Headshot in 4-5, E
  in 3, Q and R kneeling in 7 - the first design's Codex shots threw the barrel up and the bullets fell 12 degrees;
  MUZZLE below). A caster view follows her, not her sprite (champion-data
  "Projectiles that leave the muzzle"), so the fire burns only while the barrel stays where it was drawn, at base
  speed: the attack's shot comes 8 ticks in (133 ms) with the barrel still to 260 ms - Codex's 67 ms of fire; the
  Headshot's 10 ticks in (167 ms), still to 300 ms - 130 ms; E's 67 ms; Q's 100 ms (its whole 7th frame); R's 150 ms.
  The smoke after the fire stays where it was blown out;
- the projectiles on their middle. A TargetProjectile is lifted `5000 - y_offset` over her pivot (a LinearProjectile
  starts there), so the kit's `y_offset`s put each at its muzzle's height (5000 - 1000 x the height; checked against
  the kit below), but each still starts over her pivot: its view (`repeat: false`) starts empty for the ticks it needs
  to reach the muzzle at the kit's speed (also the tick a TargetProjectile's view points up), then loops about 0.4 s
  and holds a frame; the net opens over 8 ticks and stays open; the thrown trap tumbles after 2 empty ticks;
- the hits on the upper body; the net over a champion, the snapped trap, the slow's bits and the trap on the ground
  with their lowest row on the soles' row (11 px under the pivot), the crosshair on the chest;
- Codex's ticks, except where the kit sets a length: the landing holds its last frame until the first lying picture
  (30 ticks after it lands), a lying picture and the fading trap are the 15-tick link of the kit.
Writes league/effects/league_caitlyn_fx.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "caitlyn")
MOD = os.path.join(ROOT, "league")
KIT = os.path.join(MOD, "champion", "league_caitlyn.data_champion")
Z = 8
TICK = 1000 / 60
# the barrel's last pixel of each firing frame and the middle of the barrel's rows (.5: between two rows), measured on
# league/champions/league_caitlyn's sheet: the attack's 3rd-4th frames, the Headshot's 4th-5th, Q 7, E 3, R 7
MUZZLE = {"attack": (24, -7.5), "passive": (24, -7.5), "skill": (22, -7.5), "e": (24, -11.5), "ult": (22, -7.5)}
HIT = (0, -8)                          # a hit on the upper body of a 32-42 px unit
SOLES = 11                             # the soles' row under the pivot
# each projectile: the muzzle it leaves
LEAVES = {"bolt": "attack", "hs_bolt": "passive", "hs_trap_bolt": "passive", "e_net": "e", "q_bolt": "skill",
          "r_bullet": "ult", "r_laser": "ult"}
# projectiles that fly level from her standing height (y_offset 5000) instead of a muzzle's height
LEVEL = set()
MARK = (0, 0)                          # R's crosshair on his pivot, where the laser and the shot end



def tip(name):
    """The point just past the barrel's last pixel."""
    x, y = MUZZLE[name]
    return x + 0.5, y


def from_native(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8") as f:
        assets = json.load(f)["assets"]
    anchors = {}
    for a in assets:
        tag = a["tag"]
        w, h = a["game_size_px"]
        cols, rows = a["grid"]
        img = np.asarray(Image.open(G.lp(os.path.join(folder, a["game_size_file"]))).convert("RGBA"))
        if img.shape[:2] != (rows * h, cols * w):
            sys.exit(f"{a['game_size_file']}: {img.shape[1]}x{img.shape[0]}, not {cols}x{rows} cells of {w}x{h}")
        if set(np.unique(img[..., 3]).tolist()) - {0, 255}:
            sys.exit(f"{a['game_size_file']}: soft alpha")
        cells = [img[r * h:(r + 1) * h, c * w:(c + 1) * w] for r in range(rows) for c in range(cols)]
        cells = cells[:a["frame_count"]]
        out = np.concatenate(cells, 1)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"caitlyn_fx_{tag}.png")))
        ax, ay = a["anchor_normalized"]
        anchors[tag] = {"cell": [w, h], "anchor": [round(ax * w, 2), round(ay * h, 2)], "frames": len(cells),
                        "ticks": [f["duration_ticks"] for f in a["frames"]]}
        print(f"caitlyn_fx_{tag}.png  {len(cells)} cells of {w}x{h}, anchor {anchors[tag]['anchor']}, "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "caitlyn_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"caitlyn_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"caitlyn_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def kit_projectiles():
    """{name: (speed, y_offset)} of the kit's projectiles."""
    with open(G.lp(KIT), encoding="utf-8") as f:
        kit = json.load(f)
    found = {}

    def walk(o):
        if isinstance(o, dict):
            if "speed" in o and str(o.get("name", "")).startswith("league_caitlyn_"):
                found[o["name"][len("league_caitlyn_"):]] = (o["speed"], o.get("y_offset", 0))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(kit)
    return found


def lead(name, speeds):
    """Ticks a projectile needs from over her pivot to its muzzle."""
    return math.ceil(MUZZLE[LEAVES[name]][0] / (speeds[name][0] / 1000))


def check_kit(speeds):
    for name, muzzle in LEAVES.items():
        want = 5000 if name in LEVEL else 5000 - round(-MUZZLE[muzzle][1] * 1000)
        speed, y = speeds[name]
        state = "ok" if y == want else f"MISMATCH (the muzzle wants {want})"
        print(f"  {name}: speed {speed}, y_offset {y} {state}, {lead(name, speeds)} empty ticks")


def ticks(t):
    return [round(k * TICK) for k in t]


def flight(n_ticks, frames, per, loop_ms=400):
    """A projectile's view: empty for n_ticks, its frames looped about loop_ms, then its first frame held."""
    out = [(None, round(n_ticks * TICK))]
    while sum(m for _, m in out[1:]) < loop_ms:
        out += [(k, per) for k in frames]
    return out + [(frames[0], 3000)]


def build():
    with open(G.lp(os.path.join(SRC, "caitlyn_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    speeds = kit_projectiles()
    check_kit(speeds)

    def own(name, used=None):
        t = anchors[name]["ticks"]
        used = range(len(t)) if used is None else used
        return list(zip(used, ticks([t[k] for k in used])))

    proj = {name: flight(lead(name, speeds), [0, 1, 2, 3], round(anchors[tag]["ticks"][0] * TICK))
            for name, tag in (("bolt", "bolt"), ("hs_bolt", "hs_bolt"), ("q_bolt", "q_bolt"),
                              ("r_bullet", "r_bullet"))}
    net = [(None, round(lead("e_net", speeds) * TICK))] + [(k, 33) for k in range(3)] + [(3, 3000)]
    throw = flight(2, [0, 1, 2, 3], 50)
    # (strip, [(frame or None, ms)], spot, how): "point" puts the anchor on the spot, "ground" the strip's lowest row
    # on the soles' row (the anchor's x on the spot's)
    fx = {
        "bolt": [("bolt", proj["bolt"], (0, 0), "point")],
        "hs_bolt": [("hs_bolt", proj["hs_bolt"], (0, 0), "point")],
        "q_bolt": [("q_bolt", proj["q_bolt"], (0, 0), "point")],
        "r_bullet": [("r_bullet", proj["r_bullet"], (0, 0), "point")],
        # R's laser sight (tools/art/caitlyn_r_laser.py): a dash's head on its projectile, hidden until it is past the
        # rifle, 4 px for a tick, then 8 px (6 px apart: one a tick at 6 px a tick) until it reaches him
        "r_laser": [("r_laser", [(None, round(lead("r_laser", speeds) * TICK)), (0, round(TICK)), (1, 3000)],
                     (0, 0), "point")],
        "e_net": [("e_net", net, (0, 0), "point")],
        "w_throw": [("w_throw", throw, (0, 0), "point")],
        "shot": [("shot", own("shot"), tip("attack"), "point")],
        "hs_shot": [("hs_shot", [(0, 30), (1, 30), (2, 33), (3, 40), (4, 50)], tip("passive"), "point")],
        "e_shot": [("e_shot", [(0, 30), (1, 37), (2, 50), (3, 60)], tip("e"), "point")],
        "q_muzzle": [("q_muzzle", [(k, 20) for k in range(5)], tip("skill"), "point")],
        "r_muzzle": [("r_muzzle", [(0, 30), (1, 40), (2, 40), (3, 40), (4, 70), (5, 80)], tip("ult"), "point")],
        "hit": [("hit", own("hit"), HIT, "point")],
        "hs_hit": [("hs_hit", own("hs_hit"), HIT, "point")],
        "q_hit": [("q_hit", own("q_hit"), HIT, "point")],
        "r_hit": [("r_hit", own("r_hit"), HIT, "point")],
        "r_mark": [("r_mark", [(k, 100) for k in range(4)], MARK, "point")],
        "e_hit": [("e_hit", own("e_hit"), (0, 0), "ground")],
        "e_slow": [("e_slow", [(k, 100) for k in range(4)], (0, 0), "ground")],
        "w_land": [("w_land", [(0, 50), (1, 50), (2, 50), (3, 50), (4, 300)], (0, 0), "ground")],
        "w_trap": [("w_trap", [(0, 117), (1, 133)], (0, 0), "ground")],
        "w_fade": [("w_fade", [(0, 100), (1, 75), (2, 75)], (0, 0), "ground")],
        "w_snap": [("w_snap", own("w_snap"), (0, 0), "ground")],
    }
    out = {}
    for tag, parts in fx.items():
        out[tag] = []
        for src, frames, (sx, sy), how in parts:
            ax, ay = anchors[src]["anchor"]
            strip = cells(src, anchors[src]["frames"])
            u0 = math.floor(1 - ax + sx)
            if how == "ground":
                low = max(int(np.nonzero(c[..., 3].any(1))[0].max()) for c in strip)
                r0 = SOLES - low
            else:
                r0 = math.floor(1 - ay + sy)
            for k, ms in frames:
                if k is None:
                    out[tag].append((np.zeros((1, 1, 4), np.uint8), ms))
                else:
                    out[tag].append((G.centre_frame(strip[k], u0, r0), ms))
    return {"league_caitlyn_fx": out}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--native", help="Codex's delivery folder: rebuild the native strips from its 1x strips first")
    args = ap.parse_args()
    if args.native:
        from_native(args.native)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
