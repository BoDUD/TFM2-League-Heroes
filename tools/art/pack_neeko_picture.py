"""Build the step-0 pack for Codex (assets/source/neeko/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_neeko_picture.py --out C:/t/nk_work/neeko_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Zoe, Zyra and Vex, 8x, cut from their sheets), then
<out>.zip. Render into a short folder (C:/t).
Neeko (group F mid, 2026-10-21) is the Curious Chameleon: a lizard-like girl with green-teal scaled skin, a mop of
violet-blue hair with a coral-pink flower at the temple, a crest of long magenta-violet quills rising from the head,
big yellow eyes, a coral-orange woven top and loincloth with a brown belt of white shell beads, pale peach legs with
violet swirl markings, ankle wraps, bare clawed feet and a long tail. Her skin hides the R bloom's petals and the
disguise model until a spell shows them (--hide-submeshes). Two pictures: A = League's idle, 3/4 front facing right;
SA = the same idle seen from the SIDE facing right (the base of the actions). Quill tips to soles about 60 squares of
11 px. Her model: yaw 0 is the front, 35 the 3/4 view, 75 the side.
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
IDLE = "neeko_idle1@0"
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_neeko_idle": (IDLE, 35, 1600, 1.4, "box"),
    "2_neeko_frontal": (IDLE, 0, 1600, 1.4, "box"),
    "3_neeko_head": (IDLE, 35, 3200, 1.4, "head"),
    "4_neeko_back": (IDLE, 200, 1600, 1.4, "box"),
    "6_neeko_side": (IDLE, 75, 1600, 1.4, "box"),
    "full_idle": (IDLE, 35, 1600, 1.4, "none"),
    "full_side": (IDLE, 75, 1600, 1.4, "none"),
}
# quill tips to soles BODY_H px (60 squares of 11) on the 1536 square, soles on row SOLE, centred on CX
BODY_H = 660
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label)
    "8a_layout_front.png": ("full_idle", "A: League's idle, 3/4 front; quill tips to soles 660 px (60 squares of 11); "
                                         "the tail curls up behind her, off the ground"),
    "8b_layout_side.png": ("full_side", "SA: the same idle from the side, facing right; same size and ground line"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_zoe.png": ("zoe", "hd_idle"),
    "12_style_zyra.png": ("zyra", "hd_idle"),
    "13_style_vex.png": ("vex", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Neeko",
           "--hide-submeshes", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size),
           "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name,
           "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the quills, the hair with its flower, the face: the top 38% of the figure
        h = y1 - y0
        hx0, _, hx1, _ = _keyed(path).crop((0, y0, im.width, y0 + round(h * 0.38))).getbbox()
        m = (hx1 - hx0) // 10
        im = im.crop((hx0 - m, max(0, y0 - m), hx1 + m, y0 + round(h * 0.38)))
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
    """The whole figure scaled so quill tips to soles is BODY_H, soles on SOLE, centred on CX."""
    full = _keyed(src)
    fig = full.crop(full.getbbox())
    k = BODY_H / fig.height
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Neeko.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/neeko/skins/base/neekoloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_neeko_splash.png"))
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "neeko", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
