"""Build the step-0 pack for Codex (assets/source/zac/PICTURE_PROMPT.md): League references of Zac, layout guides and
style pictures.

    python tools/art/pack_zac_picture.py --out C:/t/za_work/zac_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders of Zac, the loading-screen art) and <out>/refs/9a..9b
(layout guides: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's Cho'Gath, Dr. Mundo, Gragas and
Volibear, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Zac (group H, jungle at the user's pick, 2026-10-23) is the Secret Weapon, a hulking man of living green goo: a broad
hunched body of translucent bright green slime with darker veins and organs showing inside, huge long arms with big
three-fingered hands, short thick legs, a small head sunk between the shoulders with glowing yellow eyes and a wide grin,
and a dark curling tendril (a stalk with a knob) rising from the top of his head. No summon: his bloblets (passive), the
stretched arms (Q), the slingshot (E) and the bounce (R) are frames and effects for later steps.
Two pictures: A = his idle 3/4 front facing right, SA = his side-on facing right. About 50 squares of 11 px from the top of
his head (not the tendril) to the soles, the tendril rising about 8 squares more. The skin hides a puddle and a bloblet
until an animation shows them: renders use --hide-submeshes. Yaw 0 front, 35 the 3/4 view, 75 the side.
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
IDLE = "zac_idle1@0"
SKIN = ["--hide-submeshes"]
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_zac_idle": (IDLE, 35, 1600, 1.2, "box"),
    "2_zac_frontal": (IDLE, 0, 1600, 1.2, "box"),
    "3_zac_head": (IDLE, 35, 3200, 1.2, "head"),
    "4_zac_back": (IDLE, 200, 1600, 1.2, "box"),
    "6_zac_side": (IDLE, 75, 1600, 1.2, "box"),
    "7_zac_run": ("zac_run_slow@300", 35, 1600, 1.2, "box"),
    "8_zac_stretch": ("zac_spell1_max@500", 35, 1600, 1.2, "box"),
    "full_zac": (IDLE, 35, 1600, 1.2, "none"),
    "full_zac_side": (IDLE, 75, 1600, 1.2, "none"),
}
HEAD_FRAC = 0.45   # the head close-up: his small head sunk between the shoulders, the top 45% of the figure
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, squares tall, label)
    "9a_layout_zac.png": ("full_zac", 58, "A: Zac's idle, 3/4 front; head top to soles ~550 px (50 squares of 11), tendril ~8 squares more"),
    "9b_layout_zac_side.png": ("full_zac_side", 58, "SA: Zac from the side, facing right; same size and ground"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "10_style_chogath.png": ("chogath", "hd_idle"),
    "11_style_drmundo.png": ("drmundo", "hd_idle"),
    "12_style_gragas.png": ("gragas", "hd_idle"),
    "13_style_volibear.png": ("volibear", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Zac",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame] + SKIN
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the head and the tendril, between the shoulders
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Zac.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/zac/skins/base/zacloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_zac_splash.png"))
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "zac", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
