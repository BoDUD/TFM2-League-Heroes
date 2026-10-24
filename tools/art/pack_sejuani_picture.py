"""Build the step-0 pack for Codex (assets/source/sejuani/PICTURE_PROMPT.md): League references of Sejuani,
layout guides and style pictures.

    python tools/art/pack_sejuani_picture.py --out C:/t/se_work/sejuani_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders of Sejuani, the loading-screen art) and <out>/refs/9a..9b
(layout guides: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's Nunu & Willump, Braum, Hecarim
and Volibear, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Sejuani (group I, 2026-10-24) is the Winter's Wrath: a Freljord warrior woman riding her war boar Bristle - one unit.
Sejuani: a bronze-gold horned helm with blue ice horns, long pale hair, purple leather armour under bronze-gold plates
with glowing blue ice gems, white fur at the collar and shoulders, an ice flail on a long chain (a blue ice head).
Bristle: a big hunched pale blue-grey boar with a white bristly mane, two huge ivory tusks, a pink snout, glowing blue
eyes, dark hooves, green-bronze saddle armour with blue gems. One figure, so one design: the flail's frost, the ice
bola and the storm are effects for step 3.
Two pictures: A = the idle 3/4 front facing right, B = Arctic Assault (Q), Bristle charging, 3/4. About 52 squares of
11 px from the top of her helm's horns to Bristle's hooves in A; B on the same scale. Yaw 0 front, 35 the 3/4 view.
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
IDLE = "sejuani_2013_idle1@0"
CHARGE = "sejuani_2013_spell1@400"
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_sejuani_idle": (IDLE, 35, 1600, 1.5, "box"),
    "2_sejuani_frontal": (IDLE, 0, 1600, 1.5, "box"),
    "3_sejuani_heads": (IDLE, 35, 3200, 1.5, "head"),
    "4_sejuani_back": (IDLE, 200, 1600, 1.5, "box"),
    "6_sejuani_charge": (CHARGE, 35, 1600, 1.6, "box"),
    "7_sejuani_flail": ("sejuani_spell2_a_0@400", 35, 1600, 1.6, "box"),
    "8_sejuani_bola": ("sejuani_2013_spell4@330", 35, 1600, 1.5, "box"),
    "full_sejuani": (IDLE, 35, 1600, 1.5, "none"),
    "full_sejuani_charge": (CHARGE, 35, 1600, 1.6, "none"),
}
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label); both at the scale that makes A's horn tips to hooves ANCHOR squares
    "9a_layout_sejuani.png": ("full_sejuani", "A: idle, 3/4 front; helm horns to hooves ~572 px (52 squares of 11)"),
    "9b_layout_sejuani_charge.png": ("full_sejuani_charge", "B: Arctic Assault charge; the SAME scale as A, hooves on the grey line"),
}
ANCHOR = ("full_sejuani", 52)
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "10_style_nunu.png": ("nunu", "idle"),
    "11_style_braum.png": ("braum", "hd_idle"),
    "12_style_hecarim.png": ("hecarim", "idle"),
    "13_style_volibear.png": ("volibear", "hd_idle"),
}
FIT, GROUND = 0.45, 0.82


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Sejuani", "--fit-all",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # her helm and face above, Bristle's head (tusks, snout, eyes) below and to the right
        h = y1 - y0
        im = im.crop((x0 + round((x1 - x0) * 0.35), max(0, y0 - h // 30), x1, y0 + round(h * 0.9)))
    elif crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    im.save(path)
    print(name, im.size)
    return path


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def guide(src, name, k, label):
    """The render scaled by k (one scale for every guide), the lowest hoof on SOLE, centred on CX."""
    full = _keyed(src)
    fig = full.crop(full.getbbox())
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    px, py = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (px, py))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, py), (1536, py)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (px, py, px + fig.width, py + fig.height),
          "squares", round(fig.width / SQ, 1), "x", round(fig.height / SQ, 1))


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
    refs, style, work = os.path.join(a.out, "refs"), os.path.join(a.out, "style"), a.out + "_measure"
    for d in (refs, style, work):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, work if name.startswith("full_") else refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Sejuani.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/sejuani/skins/base/sejuaniloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_sejuani_splash.png"))
    anchor = _keyed(os.path.join(work, ANCHOR[0] + ".png"))
    x0, y0, x1, y1 = anchor.getbbox()
    k = ANCHOR[1] * SQ / (y1 - y0)
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), k, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "sejuani", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
