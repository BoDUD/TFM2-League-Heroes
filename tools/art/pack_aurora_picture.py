"""Build the step-0 pack for Codex (assets/source/aurora/PICTURE_PROMPT.md): League references of Aurora, layout guides
and style pictures.

    python tools/art/pack_aurora_picture.py --out C:/t/au_work/aurora_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..6 (League renders of Aurora, the loading-screen art) and <out>/refs/10a..10b
(layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this pack's Neeko, Zoe, Yuumi and Hwei, 8x,
cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Aurora (group H, mid at the user's pick, 2026-10-23) is the Witch Between Worlds, a Vastayan bunny girl: curly copper-red
hair in two short braids, round gold glasses over violet-blue eyes, a wide-brimmed teal witch hat with two LONG RABBIT
EARS (orange-red fur, pale inside) standing up through it and red feathers at its band; a cream cable-knit high collar,
a pale blue-white fur-trimmed shawl over a cream coat with long tails, a teal tunic panel with gold runes, a brown
braided belt, an orange fluffy tail, dark brown thigh-high stockings and fur-trimmed boots; a slim wand in one hand.
No summon: her spirits (passive) are effects for step 3.
Two pictures: A = her idle 3/4 front facing right, SA = her side-on facing right. Aurora about 54 squares of 11 px from
the top of her hat (not the ears) to the soles, the ears rising about 12 squares more. Her idle draws nothing extra: renders
do not use --hide-submeshes. Yaw 0 front, 35 the 3/4 view, 75 the side.
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
HERO = "idle@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_aurora_idle": ("Aurora", HERO, 35, 1600, 1.2, "box"),
    "2_aurora_frontal": ("Aurora", HERO, 0, 1600, 1.2, "box"),
    "3_aurora_head": ("Aurora", HERO, 35, 3200, 1.2, "head"),
    "4_aurora_back": ("Aurora", HERO, 200, 1600, 1.2, "box"),
    "6_aurora_side": ("Aurora", HERO, 75, 1600, 1.2, "box"),
    "full_aurora": ("Aurora", HERO, 35, 1600, 1.2, "none"),
    "full_aurora_side": ("Aurora", HERO, 75, 1600, 1.2, "none"),
}
HEAD_TOP, HEAD_H = 0.12, 0.30   # her face sits below the ears: the head crop starts 12% down the figure, 30% tall
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, squares tall ear tips to soles, label)
    "10a_layout_aurora.png": ("full_aurora", 66, "A: Aurora's idle, 3/4 front; hat top to soles ~595 px (54 squares of 11), ears ~12 squares more"),
    "10b_layout_aurora_side.png": ("full_aurora_side", 66, "SA: Aurora from the side, facing right; same size and ground"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_neeko.png": ("neeko", "hd_idle"),
    "12_style_zoe.png": ("zoe", "hd_idle"),
    "13_style_yuumi.png": ("yuumi", "hd_idle"),
    "14_style_hwei.png": ("hwei", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Aurora", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the hat brim, the glasses, the face: below the ears, around the head
        h = y1 - y0
        top = y0 + round(h * HEAD_TOP)
        a = np.asarray(_keyed(path))[top:top + round(h * HEAD_H), :, 3] > 0
        cols = np.nonzero(a.any(axis=0))[0]
        cx = (cols[0] + cols[-1]) // 2
        im = im.crop((cx - round(h * 0.17), top, cx + round(h * 0.17), top + round(h * HEAD_H)))
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
    """The whole figure scaled so its top (the ear tips) to its soles is `squares` x SQ px, soles on SOLE, centred on CX."""
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
    d.line([(0, SOLE - 54 * SQ), (1536, SOLE - 54 * SQ)], fill=(205, 205, 205, 255), width=1)
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Aurora.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/aurora/skins/base/auroraloadscreen_0.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_aurora_splash.png"))
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "aurora", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
