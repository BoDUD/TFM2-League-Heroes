#!/usr/bin/env python3
"""Preview of Kayle's ascension (tools/fix/kayle_ascend.py, tools/art/import_kayle_ascend.py), from the game sheets.

    python tools/art/preview_kayle_ascend.py [--out docs/preview]

  league_kayle_ascend.gif   Kayle idling then running at level 1, 5, 8 and 12 side by side: no wings, then the wing
                            layers stacking behind her (each a view_buffs picture, z -1: under her sprite); 3x
  league_kayle_ascend.png   the level-12 effects beside the ones they replace (bolt, wave, Q sword, E starfire, their hits
                            and blasts), 3x
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from preview_garen import ARENA, T, frames_of, load  # noqa: E402

LEAGUE = os.path.join(ROOT, "league")
STAGES = [("Lv1", []), ("Lv5", ["wings1"]), ("Lv8", ["wings1", "wings2"]), ("Lv12", ["wings1", "wings2", "wings3"])]
PAIRS = [("bolt", "bolt_x", "fx"), ("wave", "wave_x", "fx"), ("q_sword", "q_sword_x", "fx"), ("e_bolt", "e_bolt_x", "fx"),
         ("bolt_hit", "bolt_hit_x", "fx"), ("e_hit", "e_hit_x", "fx"), ("q_blast", "q_blast_x", "big"),
         ("e_blast", "e_blast_x", "big")]


def at(fr, t):
    total = sum(ms for _, ms in fr)
    t %= total
    for f, ms in fr:
        if t < ms:
            return f
        t -= ms
    return fr[-1][0]


def stages_gif(out, z=3, step=50):
    me = load(os.path.join(LEAGUE, "champions", "league_kayle"))
    asc = load(os.path.join(LEAGUE, "effects", "league_kayle_ascend"))
    wings = {w: frames_of(asc, w) for w in ("wings1", "wings2", "wings3")}
    idle, run = frames_of(me, "idle"), frames_of(me, "run")
    cw, H = 100, 104
    gy = 74
    frames = []
    for k in range(int(4400 / step)):
        t = k * step
        body = idle if t < 2000 else run
        img = Image.new("RGBA", (cw * len(STAGES), H), ARENA)
        d = ImageDraw.Draw(img)
        for i, (label, layers) in enumerate(STAGES):
            cx = i * cw + cw // 2
            for w in layers:
                f = at(wings[w], t)
                img.alpha_composite(f, (cx - f.width // 2, gy - f.height // 2))
            f = at(body, t)
            img.alpha_composite(f, (cx - f.width // 2, gy - f.height // 2))
            d.text((i * cw + 4, 2), label, fill=(255, 255, 255, 255))
        frames.append(img.resize((img.width * z, img.height * z), Image.NEAREST).convert("RGB"))
    strip = Image.new("RGB", (frames[0].width, frames[0].height * 8))
    for i, f in enumerate(frames[::max(1, len(frames) // 8)][:8]):
        strip.paste(f, (0, i * frames[0].height))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(os.path.join(out, "league_kayle_ascend.gif")), save_all=True, append_images=q[1:],
              duration=step, loop=0)
    return len(frames)


def effects_png(out, z=3):
    sheets = {"fx": load(os.path.join(LEAGUE, "effects", "league_kayle_fx")),
              "big": load(os.path.join(LEAGUE, "effects", "league_kayle_big"))}
    asc = load(os.path.join(LEAGUE, "effects", "league_kayle_ascend"))
    rows = []
    for base, up, sheet in PAIRS:
        a = [f for f, _ in frames_of(sheets[sheet], base)]
        b = [f for f, _ in frames_of(asc, up)]
        rows.append((base, a, b))
    crop = lambda fs: [f.crop(f.getbbox()) for f in fs if f.getbbox()]
    W = max(sum(f.width + 4 for f in crop(a)) + sum(f.width + 4 for f in crop(b)) for _, a, b in rows) + 80
    H = sum(max(f.height for f in crop(a) + crop(b)) + 8 for _, a, b in rows) + 8
    img = Image.new("RGBA", (W, H), ARENA)
    d = ImageDraw.Draw(img)
    y = 4
    for name, a, b in rows:
        x = 4
        d.text((x, y), name, fill=(255, 255, 255, 255))
        x += 60
        h = max(f.height for f in crop(a) + crop(b))
        for f in crop(a):
            img.alpha_composite(f, (x, y + h - f.height))
            x += f.width + 4
        x += 16
        for f in crop(b):
            img.alpha_composite(f, (x, y + h - f.height))
            x += f.width + 4
        y += h + 8
    img.resize((W * z, H * z), Image.NEAREST).convert("RGB").save(
        T.long_path(os.path.join(out, "league_kayle_ascend.png")))
    return W, H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    a = ap.parse_args()
    print("stages gif frames", stages_gif(a.out))
    print("effects png", effects_png(a.out))


if __name__ == "__main__":
    main()
