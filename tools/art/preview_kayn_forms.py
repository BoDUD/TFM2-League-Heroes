#!/usr/bin/env python3
"""Showcase GIF of Kayn's full transform (the native add-on addons/league_kayn_form), built from the exported sheets.

    python tools/art/preview_kayn_forms.py [--out FILE.gif] [--z 3]

Three rows - Kayn, the Darkin, the Shadow Assassin (league/champions/league_kayn, league_kayn_darkin,
league_kayn_shadow) - and five columns, each looping: idle, run, hit, dead, and in a wall (the in-wall shadow sheet
league_kayn{,_darkin,_shadow}_wall with the shroud wall_aura{,_d,_s} over it and the splash wall_burst{,_d,_s} as he
goes in, from league/effects/league_kayn_fx). Writes a GIF (one palette) and a key frame PNG beside it.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402

ARENA = T.ARENA_BG
LEAGUE = os.path.join(ROOT, "league")
CW, CH = 96, 84             # a cell
PX, PY = 48, 52             # the pivot in a cell
TOP, LEFT = 14, 54          # column titles, row titles
ROWS = [("Kayn", "league_kayn", ""), ("Darkin", "league_kayn_darkin", "_d"), ("Shadow", "league_kayn_shadow", "_s")]
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


def place(img, f, x, y):
    if f is not None:
        img.alpha_composite(f, (int(x - f.width // 2), int(y - f.height // 2)))


def showcase(out, z=3, step=40):
    fx = T.load_sprite(os.path.join(LEAGUE, "effects", "league_kayn_fx"))
    rows = []
    for label, sheet, suf in ROWS:
        body = T.load_sprite(os.path.join(LEAGUE, "champions", sheet))
        wall = T.load_sprite(os.path.join(LEAGUE, "champions", sheet + "_wall"))
        rows.append((label, body, wall, frames_of(fx, "wall_aura" + suf), frames_of(fx, "wall_burst" + suf)))
    W, H = LEFT + CW * len(COLS), TOP + CH * len(ROWS)
    frames = []
    t = 0.0
    while t < LOOP:
        img = Image.new("RGBA", (W, H), ARENA)
        d = ImageDraw.Draw(img)
        for c, name in enumerate(COLS):
            d.text((LEFT + c * CW + CW // 2 - 3 * len(name), 2), name, fill=(235, 235, 225, 255))
        for r, (label, body, wall, aura, burst) in enumerate(rows):
            y0 = TOP + r * CH
            d.text((4, y0 + PY - 6), label, fill=(235, 235, 225, 255))
            d.line([(LEFT, y0 + PY + 12), (W, y0 + PY + 12)], fill=(120, 132, 100, 255))
            for c, tag in enumerate(["idle", "run", "hit", "dead"]):
                hold = tag == "dead"
                place(img, at(frames_of(body, tag), t if not hold else t % LOOP, hold), LEFT + c * CW + PX, y0 + PY)
            x = LEFT + 4 * CW + PX
            place(img, at(frames_of(wall, "idle"), t), x, y0 + PY)
            place(img, at(aura, t), x, y0 + PY)
            place(img, at(burst, t % 1200, hold=True) if t % 1200 < sum(ms for _, ms in burst) else None, x, y0 + PY)
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
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
