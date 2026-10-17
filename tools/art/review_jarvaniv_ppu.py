#!/usr/bin/env python3
"""Jarvan IV at several densities (the user, 2026-10-17: 「而且脸部太糊 要调整PPU了」): the rig's idle (tools/art/rig_jarvaniv.py,
posed at PPU 1.5) brought to each PPU by pixel_down.pixelate (nothing written), shown at one game size next to the pack's
heroes as the battlefield draws them, plus the head of each at its own pixels.

    python tools/art/review_jarvaniv_ppu.py --out DIR [--ppus 1.5,1.3,1.2,1.0] [--scale 4]

Writes <out>/jarvaniv_ppu_choices.png (per PPU the idle at game size, then Nasus / Tahm Kench (1.2), Pantheon (1.5),
Xin Zhao, Garen, feet on one line) and <out>/jarvaniv_ppu_faces.png (each PPU's head, 8 screen px a game px).
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
import pixel_down as PD  # noqa: E402
import ppu_hd  # noqa: E402
import rig_jarvaniv as J  # noqa: E402

CHAMPS = os.path.join(ROOT, "league", "champions")
PEERS = ["nasus", "tahmkench", "pantheon", "xinzhao", "garen"]
BG = (96, 112, 96)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def frame0(hero, tag="idle"):
    stem = os.path.join(CHAMPS, f"league_{hero}")
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    ppu = ppu_hd.PPU.get(hero)
    t = f"hd_{tag}" if ppu and f"hd_{tag}" in anims else tag
    f = anims[t]["frames"][0]["data"]
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    return im.crop(im.getbbox()), (ppu if t.startswith("hd_") else 1.0)


def shown(im, ppu, scale):
    k = scale / ppu
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ppus", default="1.5,1.3,1.2,1.0")
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    F = J.form()
    r = F.rig
    idle = r.finish(J.frames_all(F)["idle"][0])
    cells, faces = [], []
    for p in [float(x) for x in a.ppus.split(",")]:
        if abs(p - J.PPU) < 1e-6:
            im = idle
        else:
            im, _ = PD.pixelate(idle, p / J.PPU, (float(r.CX), float(r.GY)), F.D.outline)
        im = Image.fromarray(im)
        im = im.crop(im.getbbox())
        cells.append((f"Jarvan PPU {p}", shown(im, p, a.scale)))
        # the head: the helmet's top to the chin, a quarter of the body (design rows 13..28 of 73)
        h = im.height
        top = round(h * 13 / 73)
        head = im.crop((0, top, im.width, top + round(h * 17 / 73)))
        faces.append((f"PPU {p}: {im.width}x{im.height} squares", shown(head, p, 8)))
    for hero in PEERS:
        im, p = frame0(hero)
        cells.append((f"{hero} ({p})", shown(im, p, a.scale)))
    gap, top = 18, 22
    W = sum(c[1].width for c in cells) + gap * (len(cells) + 1)
    H = max(c[1].height for c in cells) + top + gap
    can = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(can)
    x = gap
    for lab, im in cells:
        can.paste(im, (x, H - gap - im.height), im)          # feet on one line (crops end at the soles)
        d.text((x, 4), lab, fill=(240, 240, 240))
        x += im.width + gap
    os.makedirs(a.out, exist_ok=True)
    can.save(os.path.join(a.out, "jarvaniv_ppu_choices.png"))
    W = sum(im.width + gap for _, im in faces) + gap
    H = max(im.height for _, im in faces) + top + gap
    can = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(can)
    x = gap
    for lab, im in faces:
        can.paste(im, (x, top), im)
        d.text((x, 4), lab, fill=(240, 240, 240))
        x += im.width + gap
    can.save(os.path.join(a.out, "jarvaniv_ppu_faces.png"))
    print("written", a.out)


if __name__ == "__main__":
    main()
