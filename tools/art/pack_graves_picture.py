"""Build the step-0 pack for Codex (assets/source/graves/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_graves_picture.py --out C:/t/gv_work/graves_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Malzahar, Swain and Xerath, 8x, cut from their
sheets), then <out>.zip. Render into a short folder (C:/t).
Graves (#139, 2026-10-20) is the Outlaw: a burly gunslinger with slicked-back black hair, a full black beard, thick
brows; a ragged crimson scarf / short poncho over his shoulders and down his back; a brown
leather vest and a big brown leather pauldron with brass trim on his near shoulder, a dark navy shirt, leather bracers
and gloves, a wide belt with shell pouches; loose dark grey trousers bunched over brown boots; and his shotgun
"Destiny": a huge double-barrelled gun of black steel and polished brass/gold, held level at his hip with both hands,
the barrels pointing right.
Four pictures for the user to pick from: A = League's idle, 3/4 front facing right, the shotgun at League's length;
B = the same idle with the shotgun SHORTER (barrels cut so the gun stays within a few squares of his front, the sprite
compact); SA / SB = A and B seen from the SIDE facing right (the base of the actions). Hair top to soles about 68
squares of 11 px. His model: yaw 0 is the front, 35 the 3/4 view, 75 the side.
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
IDLE = "graves_idle1@0"
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_graves_idle": (IDLE, 35, 1600, 1.4, "box"),
    "2_graves_frontal": (IDLE, 0, 1600, 1.4, "box"),
    "3_graves_head": (IDLE, 30, 3200, 1.4, "head"),
    "4_graves_back": (IDLE, 200, 1600, 1.4, "box"),
    "6_graves_attack": ("graves_attack1@100", 75, 1600, 1.6, "box"),
    "7_graves_side": (IDLE, 75, 1600, 1.6, "box"),
    "full_idle": (IDLE, 35, 1600, 1.6, "none"),
    "full_side": (IDLE, 75, 1600, 1.6, "none"),
}
# hair top to soles BODY_H px (68 squares of 11) on the 1536 square, soles on row SOLE, the box centred on CX
# the middle: the shotgun reaches out to the right)
BODY_H = 748
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label)
    "8a_layout_front.png": ("full_idle", "A / B: League's idle, 3/4 front; hair top to soles 748 px (68 squares of 11); "
                                         "B: the shotgun shorter"),
    "8b_layout_side.png": ("full_side", "SA / SB: the same idle from the side, facing right; same size and ground line; "
                                        "SB: the shotgun shortened as in B"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_gangplank.png": ("gangplank", "hd_idle"),
    "12_style_akshan.png": ("akshan", "hd_idle"),
    "13_style_darius.png": ("darius", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Graves",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the hair, the face, the scarf and the pauldron: from the hair top down 20% of the body
        top = y0
        h = y1 - top
        hx0, _, hx1, _ = _keyed(path).crop((0, top, im.width, top + round(h * 0.2))).getbbox()
        m = (hx1 - hx0) // 10
        im = im.crop((hx0 - m, max(0, top - m), hx1 + m, top + round(h * 0.2)))
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
    """The whole figure scaled so hair top to soles is BODY_H, soles on SOLE, its box (gun included) centred on CX."""
    full = _keyed(src)
    box = full.getbbox()
    fig = full.crop(box)
    k = BODY_H / (box[3] - box[1])
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0, y0 = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - BODY_H), (1536, SOLE - BODY_H)], fill=(190, 190, 190, 255), width=1)
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Graves.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/graves/skins/base/gravesloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_graves_splash.png"))
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "graves", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
