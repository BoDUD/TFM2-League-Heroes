#!/usr/bin/env python3
"""Lillia's Swirlseed rolling on the ground (the add-on league_lillia, 2026-11-14: the user's 「全改吧」, kit round S4).

    python -I tools/art/fx_lillia_roll.py                  # add e_roll / e_roll_l (+ hd_) to league/effects/league_lillia_fx
    python -I tools/art/fx_lillia_roll.py --check          # the sheet holds what this script draws (tests)
    python -I tools/art/fx_lillia_roll.py --review out.png [--gif out.gif]

League: "Lillia lobs a seed at the target location that rolls forward indefinitely", detonating on an enemy or on
terrain. The add-on rolls it (addons/league_lillia src/roll.rs: a projectile of its own from the landing point); this
draws its picture from her own flying seed and nothing else (no Codex, no outside art): the seed of `e_seed`'s first
frame - its round body (8 x 8 squares, the same outline turned any quarter) turned a quarter at a time about its own
middle, the two swirl wisps behind it kept where they are. The frame keeps `e_seed`'s 11 x 9 canvas, so the rolling
seed sits on its point exactly where the flying one did and is never bigger or smaller.

The game turns a projectile's picture to its direction (a picture going left is this one turned half round), and a
turn keeps a spin's sense: one tag spinning clockwise would roll backwards going left. So there are two, and the
add-on picks by the roll's sideways sign - `e_roll` clockwise (rolling right: the top goes forward) and `e_roll_l`
counter-clockwise (rolling left, after the game's half turn).

Both get `hd_` twins the way every tag of this sheet has them: tools/art/densify_fx.py's scale2x of the 1x frames (the
seed's own hd_e_seed is exactly that). The sheet keeps every other tag and frame where it was (strips.write_sheet packs
in order; the new tags go last, into the free end of the hd shelf), so league.dll's table (fx_ppu.rs include_str!s
the .fanim) only learns the two tags when it is rebuilt.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import densify_fx as D  # noqa: E402
import strips as G  # noqa: E402

STEM = os.path.join(ROOT, "league", "effects", "league_lillia_fx")
HERO = os.path.join(ROOT, "league", "champions", "league_lillia")
SOURCE = ("e_seed", 1)          # the flying seed's first full frame (frame 0 is a 1-tick blank)
WISPS = {(168, 176, 255), (106, 106, 232)}   # the swirl wisps behind the seed: they stay put
STEP_MS = 50                    # a quarter turn (a turn every 0.2 s: the seed is 8 squares across, it rolls ~2.3 a tick)
TAGS = ("e_roll", "e_roll_l")


def load(stem):
    anims = json.load(open(G.lp(stem + "#anim.fanim"), encoding="utf-8"))["anims"]
    sheet = np.asarray(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA"))
    return anims, sheet


def frames_of(anims, sheet, tag):
    out = []
    for f in anims[tag]["frames"]:
        d = f["data"]
        x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
        out.append((sheet[y:y + h, x:x + w].copy(), f["duration"] * 1000))
    return out


def split(frame):
    """The seed's body (every drawn square that is no wisp) and its square box: (body mask, y0, x0, side)."""
    rgb = [tuple(int(c) for c in p[:3]) for p in frame.reshape(-1, 4)]
    wisp = np.array([c in WISPS for c in rgb]).reshape(frame.shape[:2])
    body = (frame[..., 3] > 0) & ~wisp
    ys, xs = np.nonzero(body)
    y0, x0, h, w = ys.min(), xs.min(), ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
    if h != w:
        sys.exit(f"the seed's body is {w} x {h}, not square: update this script")
    box = body[y0:y0 + h, x0:x0 + w]
    if not all(np.array_equal(box, np.rot90(box, k)) for k in (1, 2, 3)):
        sys.exit("the seed's outline is not the same turned a quarter: update this script")
    return body, y0, x0, h


def rolled(frame, k):
    """The frame with its body turned k quarters (numpy's sense: k > 0 counter-clockwise on screen), wisps unmoved."""
    body, y0, x0, s = split(frame)
    out = frame.copy()
    out[body] = 0
    patch = np.rot90(frame[y0:y0 + s, x0:x0 + s].copy(), k)
    mask = np.rot90(body[y0:y0 + s, x0:x0 + s], k)
    region = out[y0:y0 + s, x0:x0 + s]
    region[mask] = patch[mask]
    return out


def roll_tags(anims, sheet):
    """{tag: [(1x frame, ms)]} for e_roll (clockwise) and e_roll_l (counter-clockwise), with their hd_ twins."""
    src = frames_of(anims, sheet, SOURCE[0])[SOURCE[1]][0]
    cw = [(rolled(src, -k), STEP_MS) for k in range(4)]
    ccw = [(rolled(src, k), STEP_MS) for k in range(4)]
    out = {"e_roll": cw, "e_roll_l": ccw}
    for t in TAGS:
        out["hd_" + t] = [(D.scale2x(a), ms) for a, ms in out[t]]
    return out


def sheet_tags(anims, sheet, new):
    """Every tag of the sheet as it is, in its order, then the roll's (1x first, then hd_)."""
    tags = {t: frames_of(anims, sheet, t) for t in anims if t not in new}
    for t in TAGS:
        tags[t] = new[t]
    for t in TAGS:
        tags["hd_" + t] = new["hd_" + t]
    return tags


def check(anims, sheet, new):
    for t, frames in new.items():
        got = frames_of(anims, sheet, t) if t in anims else []
        if len(got) != len(frames) or any(not np.array_equal(a, b) or abs(ma - mb) > 0.5
                                          for (a, ma), (b, mb) in zip(got, frames)):
            sys.exit(f"{t}: the sheet is not this script's drawing: python -I tools/art/fx_lillia_roll.py")
    print("league_lillia_fx: e_roll / e_roll_l up to date")


# ------------------------------------------------------------------ review
def zoom(a, z):
    return Image.fromarray(a).resize((a.shape[1] * z, a.shape[0] * z), Image.NEAREST)


def review(path, gif, anims, sheet, new):
    """3x contact sheet: her idle beside the flying seed and the rolling seed (1x row, then the hd row at the same game
    size), and the roll as the game turns it (right, left, down-right, up) over grass and dirt; --gif: the seed rolling."""
    h_anims, h_sheet = load(HERO)
    idle = frames_of(h_anims, h_sheet, "idle")[0][0]
    hd_idle = frames_of(h_anims, h_sheet, "hd_idle")[0][0]
    seed = [a for a, _ in frames_of(anims, sheet, "e_seed")[1:5]]
    hd_seed = [a for a, _ in frames_of(anims, sheet, "hd_e_seed")[1:5]]
    rows = [
        ("1x x3: her idle, the flying seed (e_seed 1-4), e_roll, e_roll_l", 3,
         [idle] + seed + [a for a, _ in new["e_roll"]] + [a for a, _ in new["e_roll_l"]]),
        ("PPU 2 x3 (same game size as above x2): hd_idle, hd_e_seed 1-4, hd_e_roll, hd_e_roll_l", 3,
         [hd_idle] + hd_seed + [a for a, _ in new["hd_e_roll"]] + [a for a, _ in new["hd_e_roll_l"]]),
    ]
    pad = 12
    ims = []
    for title, z, frames in rows:
        tiles = [zoom(f, z) for f in frames]
        w = sum(t.width for t in tiles) + pad * (len(tiles) + 1)
        h = max(t.height for t in tiles) + 2 * pad
        can = Image.new("RGBA", (w, h), (52, 58, 64, 255))
        x = pad
        for t in tiles:
            can.alpha_composite(t, (x, h - pad - t.height))
            x += t.width + pad
        ims.append(can)
    # the roll as the game draws it: the hd frames (x3 = 6x game size) turned to the direction, over grass and dirt -
    # rolling right (e_roll), left (e_roll_l turned half round), down-right and up-left
    ground = Image.new("RGBA", (720, 300), (86, 120, 62, 255))
    ground.paste((140, 112, 76, 255), (0, 150, 720, 300))
    for gy, frames, ang in ((40, new["hd_e_roll"], 0), (110, new["hd_e_roll_l"], 180), (190, new["hd_e_roll"], -35),
                            (260, new["hd_e_roll_l"], 145)):
        for i in range(8):
            im = zoom(frames[i % 4][0], 3).rotate(ang, resample=Image.NEAREST, expand=True)
            ground.alpha_composite(im, (50 + i * 85 - im.width // 2, gy - im.height // 2))
    ims.append(ground)
    W = max(i.width for i in ims)
    H = sum(i.height for i in ims) + 10 * len(ims)
    out = Image.new("RGBA", (W, H), (30, 30, 34, 255))
    y = 0
    for i in ims:
        out.alpha_composite(i, (0, y))
        y += i.height + 10
    out.save(path)
    print("review:", path, out.size)
    if gif:
        # a tick a GIF frame (17 ms), the frames changing every STEP_MS, the seed moving ~2.3 game px a tick (the hd
        # frames x3 = 6x game size: 14 px a tick)
        frames = []
        per = max(1, round(STEP_MS / 1000 * 60))
        for t in range(32):
            can = Image.new("RGBA", (520, 120), (86, 120, 62, 255))
            can.paste((140, 112, 76, 255), (0, 60, 520, 120))
            ra = zoom(new["hd_e_roll"][(t // per) % 4][0], 3)
            rb = zoom(new["hd_e_roll_l"][(t // per) % 4][0], 3).rotate(180, resample=Image.NEAREST, expand=True)
            can.alpha_composite(ra, (10 + t * 14, 30 - ra.height // 2))
            can.alpha_composite(rb, (510 - t * 14 - rb.width, 90 - rb.height // 2))
            frames.append(can.convert("P", palette=Image.ADAPTIVE))
        frames[0].save(gif, save_all=True, append_images=frames[1:], duration=17, loop=0)
        print("gif:", gif)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    ap.add_argument("--gif")
    a = ap.parse_args()
    anims, sheet = load(STEM)
    new = roll_tags(anims, sheet)
    if a.check:
        check(anims, sheet, new)
        return
    if a.review:
        review(a.review, a.gif, anims, sheet, new)
        return
    tags = sheet_tags(anims, sheet, new)
    before = {t: v for t, v in anims.items() if t not in new}
    w, h = G.write_sheet(STEM, tags, share=True)
    after = json.load(open(G.lp(STEM + "#anim.fanim"), encoding="utf-8"))["anims"]
    moved = [t for t, v in before.items() if after.get(t) != v]
    if moved:
        sys.exit(f"tags moved on the sheet: {moved}")
    print(f"wrote league/effects/league_lillia_fx#sheet.png ({w}x{h}): " +
          ", ".join(f"{t}:{len(new[t])}" for t in new) + " (every other tag where it was)")


if __name__ == "__main__":
    main()
