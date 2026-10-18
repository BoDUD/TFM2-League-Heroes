"""Build the step-0 pack for Codex (assets/source/maokai/PICTURE_PROMPT.md): League references, layout guides and style
pictures.

    python tools/art/pack_maokai_picture.py --out %TEMP%/mko_work/maokai_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..14 (this pack's PPU 1.2-1.5 big heroes at their dense frames, 8x, cut
from their sheets), then <out>.zip. Render into a short folder (%TEMP%).
Maokai (the user's picks, 2026-10-18: support, layout A, add-on, PPU 1.2, pro combos - 「全按推荐做」) is the Twisted
Treant: a huge hunched tree - a dark-bark body under a mossy green crown, the face in the trunk (two glowing blue eyes,
a mossy beard), a branch over his back with a blue crystal lantern hanging from it, a HUGE near arm (League's left) of
pale wood with a carved face glowing blue on its fist, a smaller far claw, stumpy root legs and a violet loincloth.
Two pictures, both used: A = League's idle (maokai_idle1), C = his sapling (MaokaiSproutling, the E's trap) on the same
squares. A big creature (no chibi head, like oppi's big creatures): the face is where League puts it, in the trunk.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
IDLE = "maokai_idle1@0"
SAPLING = "MaokaiSapling_Aggro@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / (x0, y0, x1, y1) fractions of the figure's box)
RENDERS = {
    "1_maokai_idle": ("Maokai", IDLE, 35, 1600, 1.6, "box"),
    "2_maokai_frontal": ("Maokai", IDLE, 0, 1600, 1.6, "box"),
    "3_maokai_face": ("Maokai", IDLE, 25, 3200, 1.6, (0.30, 0.15, 0.80, 0.55)),
    "4_maokai_back": ("Maokai", IDLE, 200, 1600, 1.6, "box"),
    "5_maokai_side": ("Maokai", IDLE, 70, 1600, 1.6, "box"),
    "7_maokai_r_cast": ("Maokai", "maokai_spell4@833", 35, 1600, 1.6, "box"),
    "9_sapling": ("MaokaiSproutling", SAPLING, 35, 1200, 1.2, "box"),
}
# crown top to soles HEIGHT px (72 squares of 11) on the 1536 square, soles on row SOLE, centred
HEIGHT = 792
SOLE = 1390
SAPLING_H = 20 * 11     # the sapling: about 20 squares tall on the same grid
GUIDES = {
    "8_layout_A.png": ("1_maokai_idle.png", "A: League's idle; crown top to soles 792 px (72 squares of 11); layout only",
                       HEIGHT),
    "10_layout_C.png": ("9_sapling.png", "C: the sapling, the SAME squares; leaf tip to its foot ~220 px (20 squares); "
                        "layout only", SAPLING_H),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_tahmkench.png": ("tahmkench", "hd_idle"),
    "12_style_nasus.png": ("nasus", "hd_idle"),
    "13_style_urgot.png": ("urgot", "hd_idle"),
    "14_style_swain.png": ("swain", "hd_idle"),
}
FIT, GROUND = 0.62, 0.84


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Maokai", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size),
           "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name,
           "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    else:
        fx0, fy0, fx1, fy1 = crop
        w, h = x1 - x0, y1 - y0
        im = im.crop((round(x0 + fx0 * w), round(y0 + fy0 * h), round(x0 + fx1 * w), round(y0 + fy1 * h)))
    im.save(path)
    print(name, im.size)
    return path


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def guide(refs, name, spec):
    src, label, height = spec
    full = _keyed(os.path.join(refs, src))
    fig = full.crop(full.getbbox())
    k = height / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0 = (1536 - fig.width) // 2
    y0 = SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, max(0, y0)))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, y0), (1536, y0)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, name))
    print(name, "figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


def cut(hero, tag, out):
    """Frame 0 of a sheet tag at 8x (one square = one pixel of that tag's density)."""
    anims = json.load(open(os.path.join(CHAMPS, f"league_{hero}#anim.fanim"), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(os.path.join(CHAMPS, f"league_{hero}#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))   # on grey like the other style pictures
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(out)
    print(os.path.basename(out), pad.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Maokai.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/maokai/skins/base/maokailoadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "6_maokai_splash.png"))
    for name, spec in GUIDES.items():
        guide(refs, name, spec)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "maokai", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
