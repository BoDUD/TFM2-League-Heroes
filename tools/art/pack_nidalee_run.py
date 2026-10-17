#!/usr/bin/env python3
"""Nidalee's run redraw pack for Codex (assets/source/nidalee/RUN_FIX.md): the huntress's 8 run frames redrawn the way
she runs in League - leaning forward, long crossing strides, the javelin carried level at her side.

    python tools/art/pack_nidalee_run.py [--out dist/nidalee_packs/nidalee_run_fix]

The user, 2026-10-13: 「奈德丽走路有点问题 跑动姿势不像LOL的」 - the run in game was league_braum's walk on her standing
design (import_nidalee_strips.py: Codex's step-2 run kept the same leg in front in all 8 frames). Picked 「让 Codex 重画
跑步 8 帧」. Only the run; every other tag stays as it is.
Writes <out>/ (and <out>.zip): RUN_FIX.md, now/nidalee_run_<k>.png (League's run at the frame's moment, the step-2
pack's skeleton: same 1536 x 1024 canvas, 5 px a square, the design's size), guide/ (the same with the ground line and
the standing point), design/ (the design at 5 px, on the canvas, 1x, its head alone, the palette), refs/ (League's run
as a contact sheet - local only; league_caitlyn's and league_zeri's approved runs at 6x; Codex's previous run, 1x x 3).
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import import_nidalee_strips as I  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nidalee")
DOC = os.path.join(SRC, "RUN_FIX.md")
STRIPS = os.path.join(ROOT, "dist", "nidalee_packs", "nidalee_strips_pack")
LEAGUE_RUN = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "nd_work", "ref", "strip8", "nidalee_2012_run.png")
PX = 5


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def lines(img, piv):
    dr = ImageDraw.Draw(img)
    for c in range(0, I.COLS + 1, 10):
        dr.line([(c * PX, 0), (c * PX, 1024)], fill=(200, 200, 200, 90))
    for r in range(0, I.ROWS + 1, 10):
        dr.line([(0, r * PX), (1536, r * PX)], fill=(200, 200, 200, 90))
    dr.line([(0, (I.SOLE + 1) * PX), (1536, (I.SOLE + 1) * PX)], fill=(255, 40, 40, 255), width=2)
    cx, cy = (piv + 0.5) * PX, (I.SOLE + 1) * PX
    dr.line([(cx - 18, cy), (cx + 18, cy)], fill=(40, 90, 255, 255), width=3)
    dr.line([(cx, cy - 18), (cx, cy + 18)], fill=(40, 90, 255, 255), width=3)
    return img


def approved_run(hero, path, Z=6):
    """A pack hero's run in game (its 1x tag), frames side by side at Z."""
    import tfm2_ase as T
    from preview_garen import frames_of
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{hero}"))
    tiles = [f.crop(f.getchannel("A").getbbox()) for f, _ in frames_of(sp, "run")]
    w = max(t.width for t in tiles)
    h = max(t.height for t in tiles)
    can = Image.new("RGBA", (w * Z * len(tiles), h * Z + 20), (96, 112, 96, 255))
    d = ImageDraw.Draw(can)
    for i, t in enumerate(tiles):
        can.alpha_composite(t.resize((t.width * Z, t.height * Z), Image.NEAREST), (i * w * Z, 20 + (h - t.height) * Z))
        d.text((i * w * Z + 4, 4), f"frame {i + 1}", fill=(255, 255, 255, 255))
    can.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "nidalee_packs", "nidalee_run_fix"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("now", "guide", "design", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    piv = I.FORMS["human"]["piv"]
    for k in range(1, 9):
        sk = Image.open(os.path.join(STRIPS, "now", f"nidalee_run_{k}.png")).convert("RGBA")
        sk.save(os.path.join(out, "now", f"nidalee_run_{k}.png"))
        lines(sk.copy(), piv).save(os.path.join(out, "guide", f"nidalee_run_{k}.png"))
    d = I.design("human")
    Image.fromarray(up(d, PX)).save(os.path.join(out, "design", "nidalee_human_design.png"))
    Image.fromarray(d).save(os.path.join(out, "design", "nidalee_human_design_1x.png"))
    can = I.canvas("human")
    big = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
    big.paste(Image.fromarray(up(can, PX)), (0, 0))
    big.save(os.path.join(out, "design", "nidalee_human_design_on_canvas.png"))
    r0, r1, c0, c1 = I.FORMS["human"]["head"]
    Image.fromarray(up(d[r0:r1, c0:c1], PX)).save(os.path.join(out, "design", "nidalee_head.png"))
    cols = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols[np.argsort(cols.astype(int).sum(1))], 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "nidalee_palette.png"))
    approved_run("caitlyn", os.path.join(out, "refs", "caitlyn_run.png"))
    approved_run("zeri", os.path.join(out, "refs", "zeri_run.png"))
    if os.path.isfile(LEAGUE_RUN):
        shutil.copyfile(LEAGUE_RUN, os.path.join(out, "refs", "league_run.png"))
    tiles = [Image.open(os.path.join(I.CODEX, f"nidalee_run_{k}_1x.png")).convert("RGBA") for k in range(1, 9)]
    sheet = Image.new("RGBA", (8 * 160 * 3, 204 * 3), (96, 112, 96, 255))
    for k, t in enumerate(tiles):
        sheet.alpha_composite(t.crop((70, 0, 230, 204)).resize((480, 612), Image.NEAREST), (k * 480, 0))
    sheet.save(os.path.join(out, "refs", "previous_run_wrong.png"))
    shutil.copyfile(DOC, os.path.join(out, "RUN_FIX.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
