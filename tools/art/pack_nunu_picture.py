"""Build the step-0 pack for Codex (assets/source/nunu/PICTURE_PROMPT.md): League references of Nunu & Willump,
layout guides and style pictures.

    python tools/art/pack_nunu_picture.py --out C:/t/nu_work/nunu_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..7 (League renders of Nunu & Willump, the loading-screen art) and
<out>/refs/8a..8b (layout guides: Riot's, kept local, never committed) and <out>/style/9..12 (this pack's Volibear,
Braum, Ornn and Gnar, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Nunu & Willump (group H, jungle at the user's pick, 2026-10-23) are one unit: Willump, a big round pale-blue yeti
with white fur on the head, the shoulders and the forearms, blue swirl marks, glowing blue eyes, a wide grin with
little tusks, red-pink ears, dark blue claws; and the boy Nunu riding on his head, holding on to Willump's two big
brown wooden antlers - a boy in a blue furry hood with pink-lined cat ears and a white pompom on top, an orange
cape with white fur, brown gloves and boots, a slingshot / satchel on the back. One figure, so one design: the
snowball (W), the snowball barrage (E) and the blizzard (R) are effects for step 3.
Two pictures: A = the idle 3/4 front facing right, SA = the side-on facing right. About 60 squares of 11 px from the
top of Nunu's pompom to Willump's soles. The skin hides some of the mesh until an animation shows it (the snowman
of R's recall, the long claws, the big and smiling teeth): renders hide those by name and colour Willump with his
own map (the bin's material override; the default colours the whole model with Nunu's). Yaw 0 front, 35 the 3/4
view, 75 the side.
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
IDLE = "nunu_idle01@0"
SKIN = ["--hide-submesh", "claws_long", "--hide-submesh", "teeth_big", "--hide-submesh", "snowman",
        "--hide-submesh", "teeth_smile", "--submesh-texture", "willump=Willump_Base",
        "--submesh-texture", "claws_short=Willump_Base", "--submesh-texture", "teeth_small=Willump_Base"]
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_nunu_idle": (IDLE, 35, 1600, 1.2, "box"),
    "2_nunu_frontal": (IDLE, 0, 1600, 1.2, "box"),
    "3_nunu_heads": (IDLE, 35, 3200, 1.2, "head"),
    "4_nunu_back": (IDLE, 200, 1600, 1.2, "box"),
    "6_nunu_side": (IDLE, 75, 1600, 1.2, "box"),
    "7_nunu_run": ("nunu_run01@300", 35, 1600, 1.2, "box"),
    "full_nunu": (IDLE, 35, 1600, 1.2, "none"),
    "full_nunu_side": (IDLE, 75, 1600, 1.2, "none"),
}
HEAD_FRAC = 0.55   # the head close-up: Nunu and Willump's face, the top 55% of the figure
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, squares tall, label)
    "8a_layout_nunu.png": ("full_nunu", 60, "A: Nunu & Willump's idle, 3/4 front; pompom to soles ~660 px (60 squares of 11)"),
    "8b_layout_nunu_side.png": ("full_nunu_side", 60, "SA: Nunu & Willump from the side, facing right; same size and ground"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "9_style_volibear.png": ("volibear", "hd_idle"),
    "10_style_braum.png": ("braum", "hd_idle"),
    "11_style_ornn.png": ("ornn", "hd_idle"),
    "12_style_gnar.png": ("gnar", "idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Nunu",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame] + SKIN
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # Nunu on top and Willump's face under him
        h = y1 - y0
        cx = (x0 + x1) // 2
        im = im.crop((cx - round(h * 0.33), max(0, y0 - h // 30), cx + round(h * 0.33), y0 + round(h * HEAD_FRAC)))
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


def guide(src, name, squares, label):
    """The whole figure scaled so its top to its soles is `squares` x SQ px, soles on SOLE, centred on CX."""
    full = _keyed(src)
    fig = full.crop(full.getbbox())
    k = squares * SQ / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0, y0 = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - squares * SQ), (1536, SOLE - squares * SQ)], fill=(190, 190, 190, 255), width=1)
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
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs")
    a = ap.parse_args()
    refs, style, work = os.path.join(a.out, "refs"), os.path.join(a.out, "style"), a.out + "_measure"
    for d in (refs, style, work):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, work if name.startswith("full_") else refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Nunu.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/nunu/skins/base/nunuloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_nunu_splash.png"))
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "nunu", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
