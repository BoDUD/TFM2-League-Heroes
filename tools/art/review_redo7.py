#!/usr/bin/env python3
"""Before / after of the 2026-10-16 PPU redo at game size (tools/art/rig_<hero>_hd.py): for each hero every tag, the
frames on main (the 1x sheet, or its hd_ frames) over the new hd_ frames, all at Z x a game pixel, and one GIF of every
action in turn (new frames only).

    python tools/art/review_redo7.py --out dist/ppu_review [--hero nami ...] [--z 3]
"""
import argparse
import io
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402

HEROES = ["morgana", "nami", "janna"]
BG = (96, 112, 96, 255)


def sheet_from(png, fanim):
    px = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"))
    anims = json.loads(fanim.decode("utf-8-sig"))["anims"]
    out = {}
    for tag, a in anims.items():
        fr = []
        for f in a["frames"]:
            d = f["data"]
            x, y, w, h = (int(d[k]) for k in "xywh")
            fr.append((px[y:y + h, x:x + w].copy(), f["duration"] * 1000))
        out[tag] = fr
    return out


def git_show(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, check=True).stdout


def shown(a, k):
    im = Image.fromarray(a)
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--hero", action="append")
    ap.add_argument("--z", type=float, default=3)
    ap.add_argument("--base", default="origin/main")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for hero in a.hero or HEROES:
        stem = f"league/champions/league_{hero}"
        old = sheet_from(git_show(a.base, stem + "#sheet.png"), git_show(a.base, stem + "#anim.fanim"))
        with open(os.path.join(ROOT, stem + "#sheet.png"), "rb") as f:
            png = f.read()
        with open(os.path.join(ROOT, stem + "#anim.fanim"), "rb") as f:
            new = sheet_from(png, f.read())
        z, k = a.z, P.PPU[hero]
        rows, gif = [], []
        for tag in [t for t in new if P.plain(t)]:
            o_ppu = None
            if P.PREFIX + tag in old:
                o = old[P.PREFIX + tag]
                o_ppu = 1
                import re
                src = git_show(a.base, "tools/art/ppu_hd.py").decode("utf-8")
                m = re.search(r'"%s":\s*([0-9.]+)' % hero, src)
                o_ppu = float(m.group(1)) if m else 1
            else:
                o = old.get(tag, [])
            before = [shown(f, z / (o_ppu or 1)) for f, _ in o]
            after = [shown(f, z / k) for f, _ in new[P.PREFIX + tag]]
            cw = max(im.width for im in before + after) + 6
            ch = max(im.height for im in before + after)
            im = Image.new("RGBA", (90 + cw * max(len(before), len(after)), 2 * ch + 24), BG)
            d = ImageDraw.Draw(im)
            d.text((2, 4), tag, fill=(255, 255, 255))
            d.text((2, ch // 2 + 10), "main", fill=(220, 220, 220))
            d.text((2, ch + ch // 2 + 18), "new", fill=(255, 255, 0))
            for i, b in enumerate(before):
                im.alpha_composite(b, (90 + i * cw + (cw - b.width) // 2, ch - b.height))
            for i, n in enumerate(after):
                im.alpha_composite(n, (90 + i * cw + (cw - n.width) // 2, 2 * ch + 18 - n.height))
            rows.append(im)
            gif += [(f, ms) for (f, _), (_, ms) in zip(new[P.PREFIX + tag], new[tag])]
        W = max(r.width for r in rows)
        can = Image.new("RGB", (W, sum(r.height + 2 for r in rows)), (50, 50, 50))
        y = 0
        for r in rows:
            can.paste(r.convert("RGB"), (0, y))
            y += r.height + 2
        can.save(os.path.join(a.out, f"redo7_{hero}_frames.png"))
        # GIF: every action in turn, centred frames on one canvas, 2 x game size
        zz = 2 / k
        fr = [shown(f, zz) for f, _ in gif]
        cw = max(f.width for f in fr)
        ch = max(f.height for f in fr)
        imgs = []
        for f in fr:
            c = Image.new("RGBA", (cw, ch), BG)
            c.alpha_composite(f, ((cw - f.width) // 2, (ch - f.height) // 2))
            imgs.append(c.convert("RGB"))
        pal = imgs[0].quantize(255, dither=Image.Dither.NONE)
        q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in imgs]
        q[0].save(os.path.join(a.out, f"redo7_{hero}.gif"), save_all=True, append_images=q[1:],
                  duration=[max(20, int(round(ms))) for _, ms in gif], loop=0)
        print(hero, can.size, len(gif), "GIF frames")


if __name__ == "__main__":
    main()
