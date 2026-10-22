"""Build the step-0 pack for Codex (assets/source/hwei/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_hwei_picture.py --out C:/t/hw_work/hwei_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Sylas, Malzahar and Zoe, 8x, cut from their sheets),
then <out>.zip. Render into a short folder (C:/t).
Hwei (group G mid, 2026-10-22) is the Visionary, an Ionian painter: a slim young man with pale skin, messy dark
teal-navy hair falling over his eyes, a tired, brooding face, a dark choker; an off-shoulder indigo painter's coat with a
wide turquoise collar, gold trim and red-orange cuffs over a red-orange shirt and a brown vest; dark green cropped
trousers tied with teal ribbons at the calves, a pink bead anklet, brown loafers; a big paintbrush staff (dark shaft,
a red and navy brush head ending in a wooden point) slanting down to the ground in the hand on the image right; and a
floating crescent of painted strokes (navy with orange, teal and gold) curling over his back, dripping three ink drops.
Two pictures: A = League's idle (idle_base@0), 3/4 front facing right; SA = the same idle from the SIDE facing right.
Hair top to soles about 58 squares of 11 px (the crescent above his head, the brush inside the box). His model: yaw 0
is the front, 35 the 3/4 view, 75 the side.
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

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
IDLE = "idle_base@0"
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_hwei_idle": (IDLE, 35, 1600, 1.2, "box"),
    "2_hwei_frontal": (IDLE, 0, 1600, 1.2, "box"),
    "3_hwei_head": (IDLE, 35, 3200, 1.2, "head"),
    "4_hwei_back": (IDLE, 200, 1600, 1.2, "box"),
    "6_hwei_side": (IDLE, 75, 1600, 1.2, "box"),
    "full_idle": (IDLE, 35, 1600, 1.2, "none"),
    "full_side": (IDLE, 75, 1600, 1.2, "none"),
}
# whole figure (crescent top to soles) FIG_H px on the 1536 square, soles on row SOLE, centred on CX. The crescent
# rises ~12% of the figure above his hair: hair top to soles ~640 px = 58 squares of 11.
FIG_H = 720
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label)
    "8a_layout_front.png": ("full_idle", "A: League's idle, 3/4 front; hair top to soles ~640 px (58 squares of 11), "
                                         "the crescent above; the brush slants down on the image right"),
    "8b_layout_side.png": ("full_side", "SA: the same idle from the side, facing right; same size and ground line"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_sylas.png": ("sylas", "hd_idle"),
    "12_style_malzahar.png": ("malzahar", "hd_idle"),
    "13_style_zoe.png": ("zoe", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Hwei",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size),
           "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name,
           "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the hair, the face, the collar: below the crescent, around the head
        h = y1 - y0
        cx = (x0 + x1) // 2
        im = im.crop((cx - round(h * 0.13), y0 + round(h * 0.08), cx + round(h * 0.17), y0 + round(h * 0.36)))
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


def guide(src, name, label):
    """The whole figure scaled so its top to the soles is FIG_H, soles on SOLE, centred on CX."""
    full = _keyed(src)
    fig = full.crop(full.getbbox())
    k = FIG_H / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0, y0 = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - FIG_H), (1536, SOLE - FIG_H)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


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
    ap.add_argument("--splash", default="C:/t/hw_work/dd/Hwei_0_loading.jpg",
                    help="ddragon.leagueoflegends.com/cdn/img/champion/loading/Hwei_0.jpg")
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs")
    a = ap.parse_args()
    refs, style, work = os.path.join(a.out, "refs"), os.path.join(a.out, "style"), a.out + "_measure"
    for d in (refs, style, work):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, work if name.startswith("full_") else refs)
        # his skin folder has no loadscreen texture: Data Dragon's loading art (Hwei_0.jpg, 308x560)
        splash = Image.open(a.splash).convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_hwei_splash.png"))
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "hwei", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
