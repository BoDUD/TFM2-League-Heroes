"""Build the step-0 pack for Codex (assets/source/kled/PICTURE_PROMPT.md): League references of Kled, layout guides
and style pictures.

    python tools/art/pack_kled_picture.py --out C:/t/kl_work/kled_pack0 [--lol D:\\WeGameApps\\lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders of Kled, the loading-screen art) and <out>/refs/9a..9b
(layout guides: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's Sejuani, Nunu & Willump, Ziggs
and Teemo, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Kled (group J, 2026-10-24) is the Cantankerous Cavalier: a grumpy yordle riding Skaarl, a big cowardly lizard - one
unit while mounted; when Skaarl's health runs out Kled fights on foot (the KledRider character in the same WAD).
Kled: big pointed ears, a teal and red hat with a steel spike, a cream-white beard and fur, a manic toothy grin, one
milky blind eye, a teal and green coat with a red sash, grey trousers, a two-bladed axe, a bear trap on a rope.
Skaarl: a tall amber-orange lizard with a purple belly, teal-blue spines on the head, a big green eye, a frilled neck,
long dark purple legs with leather straps and a gold star, clawed feet, a tail.
Two pictures: A = mounted idle 3/4 front facing right, B = Kled on foot (dismounted) at the SAME scale. About 50
squares of 11 px from the tip of his hat spike to Skaarl's claws in A. The models differ (Kled 196 units tall bind
pose, KledRider 150), so B renders at fit x 150.28/195.94 to keep one world scale (his head is the same size in both).
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
# the mounted model has one skin over both bodies: name each submesh's map, and leave the emote fish out
MOUNT = ["--submesh-texture", "KledRider_base_mat=KledRider_Base", "--submesh-texture", "KledMount_Base_Mat=KledMount_base",
         "--hide-submesh", "KledRider_base_fish_mat", "--hide-submesh", "KledRider_base_fish_cut_mat"]
RIDER_FIT = 150.28 / 195.94   # KledRider's bind height over Kled's: one world scale for both
IDLE = "kled_idle1@0"
RIDER = "rider_idle1@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / "head" / "rider_head" / "none")
RENDERS = {
    "1_kled_idle": ("Kled", IDLE, 35, 1600, 1.5, "box"),
    "2_kled_frontal": ("Kled", IDLE, 0, 1600, 1.5, "box"),
    "3_kled_heads": ("Kled", IDLE, 35, 3200, 1.5, "head"),
    "4_kled_back": ("Kled", IDLE, 200, 1600, 1.5, "box"),
    "6_kled_dismounted": ("KledRider", RIDER, 35, 1600, 1.5, "box"),
    "7_kled_dismounted_head": ("KledRider", RIDER, 35, 3200, 1.5, "rider_head"),
    "8_kled_trap": ("Kled", "kled_spell1@61", 35, 1600, 1.6, "box"),
    "8b_kled_charge": ("Kled", "kled_spell4_into@256", 35, 1600, 1.6, "box"),
    "full_kled": ("Kled", IDLE, 35, 1600, 1.5, "none"),
    "full_kled_dismounted": ("KledRider", RIDER, 35, 1600, 1.5, "none"),
}
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label); both at the scale that makes A's hat spike to claws ANCHOR squares
    "9a_layout_kled.png": ("full_kled", "A: mounted idle, 3/4 front; hat spike to Skaarl's claws ~550 px (50 squares of 11)"),
    "9b_layout_kled_dismounted.png": ("full_kled_dismounted", "B: Kled on foot; the SAME scale as A, boots on the grey line"),
}
ANCHOR = ("full_kled", 50)
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "10_style_sejuani.png": ("sejuani", "hd_idle"),
    "11_style_nunu.png": ("nunu", "hd_idle"),
    "12_style_ziggs.png": ("ziggs", "hd_idle"),
    "13_style_teemo.png": ("teemo", "idle"),
}
FIT, GROUND = 0.45, 0.82


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    fit = FIT * (RIDER_FIT if champ == "KledRider" else 1.0)
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ, "--wad", "Kled",
           "--fit-all", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame] + (MOUNT if champ == "Kled" else [])
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    h = y1 - y0
    if crop == "head":   # Kled's hat and face on top, Skaarl's head (spines, eye, mouth) below and to the right
        im = im.crop((x0, max(0, y0 - h // 30), x1, y0 + round(h * 0.55)))
    elif crop == "rider_head":
        im = im.crop((x0, max(0, y0 - h // 30), x1, y0 + round(h * 0.5)))
    elif crop == "box":
        m = max(x1 - x0, h) // 12
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
    """The render scaled by k (one scale for every guide), the lowest claw / boot on SOLE, centred on CX."""
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Kled.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/kled/skins/base/kledloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_kled_splash.png"))
    anchor = _keyed(os.path.join(work, ANCHOR[0] + ".png"))
    x0, y0, x1, y1 = anchor.getbbox()
    k = ANCHOR[1] * SQ / (y1 - y0)
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), k, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "kled", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
