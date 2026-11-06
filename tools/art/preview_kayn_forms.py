#!/usr/bin/env python3
"""Showcase GIF of Kayn's full transform (the native add-on addons/league_kayn_form), built from the exported sheets.

    python tools/art/preview_kayn_forms.py [--out FILE.gif] [--z 3]

Three rows - Kayn, the Darkin, the Shadow Assassin - and five columns, each looping: idle, run, hit, dead, and in a
wall (the in-wall shade with the shroud wall_aura{,_d,_s} over it and the splash wall_burst{,_d,_s} as he goes in, from
league/effects/league_kayn_fx). All from his own sheet league/champions/league_kayn as the add-on plays them on game
0.6.4 and later (the forms' rh_ / sh_ tags, the shades' w_ / rw_ / hw_), drawn from their dense frames (hd_, PPU 1.8, as
league.dll shows them; the forms' own 1x sheets league_kayn_darkin / _shadow / *_wall serve game 0.6.2's renaming
only). Writes a GIF (one palette) and a key frame PNG beside it.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402
from preview_dense import dense, put  # noqa: E402

ARENA = T.ARENA_BG
LEAGUE = os.path.join(ROOT, "league")
CW, CH = 96, 84             # a cell
PX, PY = 48, 52             # the pivot in a cell
TOP, LEFT = 14, 54          # column titles, row titles
ROWS = [("Kayn", "", "w_", ""), ("Darkin", "rh_", "rw_", "_d"), ("Shadow", "sh_", "hw_", "_s")]   # form, wall shade, fx
COLS = ["idle", "run", "hit", "dead", "in wall"]
LOOP = 2400.0               # ms each cell loops over (dead holds its last frame, then starts again)


def frames_of(sp, tag):
    return [(sp.frames[i], sp.durations[i]) for i in sp.tag_frames(tag)]


def at(fr, t, hold=False):
    """The frame showing `t` ms into an animation (looping, or holding its last frame)."""
    total = sum(ms for _, ms in fr)
    if total <= 0:
        return None
    t = min(t, total - 1) if hold else t % total
    for f, ms in fr:
        if t < ms:
            return f
        t -= ms
    return fr[-1][0]


def place(img, f, x, y, z):
    if f is not None:
        put(img, f, int(x), int(y), z)


def showcase(out, z=3, step=40):
    fx = T.load_sprite(os.path.join(LEAGUE, "effects", "league_kayn_fx"))
    k = T.load_sprite(os.path.join(LEAGUE, "champions", "league_kayn"))
    rows = []
    for label, pre, wpre, suf in ROWS:
        body = {tag: dense(k, pre + tag, "kayn", z) for tag in ("idle", "run", "hit", "dead")}
        rows.append((label, body, dense(k, wpre + "idle", "kayn", z), frames_of(fx, "wall_aura" + suf),
                     frames_of(fx, "wall_burst" + suf)))
    W, H = LEFT + CW * len(COLS), TOP + CH * len(ROWS)
    ground = Image.new("RGBA", (W, H), ARENA)          # the titles and ground lines at 1x, scaled as before
    d = ImageDraw.Draw(ground)
    for c, name in enumerate(COLS):
        d.text((LEFT + c * CW + CW // 2 - 3 * len(name), 2), name, fill=(235, 235, 225, 255))
    for r, (label, *_) in enumerate(rows):
        y0 = TOP + r * CH
        d.text((4, y0 + PY - 6), label, fill=(235, 235, 225, 255))
        d.line([(LEFT, y0 + PY + 12), (W, y0 + PY + 12)], fill=(120, 132, 100, 255))
    ground = ground.resize((W * z, H * z), Image.NEAREST)
    frames = []
    t = 0.0
    while t < LOOP:
        img = ground.copy()
        for r, (label, body, wall, aura, burst) in enumerate(rows):
            y0 = TOP + r * CH
            for c, tag in enumerate(["idle", "run", "hit", "dead"]):
                hold = tag == "dead"
                place(img, at(body[tag], t if not hold else t % LOOP, hold), LEFT + c * CW + PX, y0 + PY, z)
            x = LEFT + 4 * CW + PX
            place(img, at(wall, t), x, y0 + PY, z)
            place(img, at(aura, t), x, y0 + PY, z)
            place(img, at(burst, t % 1200, hold=True) if t % 1200 < sum(ms for _, ms in burst) else None, x, y0 + PY, z)
        frames.append(img.convert("RGB"))
        t += step
    strip = Image.new("RGB", (W * z, H * z * 6))
    for i, f in enumerate(frames[::max(1, len(frames) // 6)][:6]):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0)
    frames[len(frames) // 3].save(T.long_path(out[:-4] + "_key.png"))
    return len(frames)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview", "league_kayn_forms.gif"))
    ap.add_argument("--z", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    print(a.out, showcase(a.out, a.z), "frames")


if __name__ == "__main__":
    main()
