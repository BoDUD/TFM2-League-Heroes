"""Build the step-0 pack for Codex (assets/source/naafiri/PICTURE_PROMPT.md): League references of Naafiri and her
packmate, layout guides and style pictures.

    python tools/art/pack_naafiri_picture.py --out C:/t/nf_work/naafiri_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders of Naafiri and a packmate, the loading-screen art) and
<out>/refs/10a..10d (layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this pack's Nidalee
cougar, Kindred, Warwick and Volibear, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Naafiri (group F mid, 2026-10-21) is the Hound of a Hundred Bites, a darkin dagger that took a pack of desert hounds:
  Naafiri - a big lean hound on four legs: a crimson-red wolf head with a white blaze down the snout and pointed ears,
  yellow eyes, a grinning mouth of white fangs, a slate blue-teal armoured hide over the back and the shoulders with
  crimson veins, a fan of big curved dark-purple blades rimmed in mint green rising from her neck and shoulders like a
  mane, a row of short teal spikes down the spine, crimson legs with black claws, a long whip tail red at the end.
  Packmate - a smaller crimson hound: lean red body, a slate-grey bony helmet with a blade jutting forward over the
  snout, short grey spikes on the neck, one yellow eye, black claws, a long thin tail.
Both are characters in Naafiri.wad.client (--champ NaafiriPackmate --wad Naafiri). Skin scales 1.3 and 0.95: a packmate
stands about half as tall as she does. Naafiri's skin has a hidden 'Hand' submesh (a prop floating above her in the
bind pose): renders use --hide-submeshes. Four pictures: A = her idle 3/4 front facing right, SA = her side-on facing
right, P = a packmate's idle 3/4 front facing right, SP = a packmate side-on facing right. Naafiri about 36 squares of
11 px from the top blade tip to the paws, a packmate about 20 (the same square size: they keep their sizes against
each other). Yaw 0 front, 35 the 3/4 view, 75 the side.
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
HERO, PACK = "idle@0", "idle1@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_naafiri_idle": ("Naafiri", HERO, 35, 1600, 1.6, "box"),
    "2_naafiri_frontal": ("Naafiri", HERO, 0, 1600, 1.6, "box"),
    "3_naafiri_head": ("Naafiri", HERO, 35, 3200, 1.6, "head"),
    "4_naafiri_side": ("Naafiri", HERO, 75, 1600, 1.6, "box"),
    "5_packmate_idle": ("NaafiriPackmate", PACK, 35, 1600, 1.8, "box"),
    "6_packmate_head": ("NaafiriPackmate", PACK, 35, 3200, 1.8, "head"),
    "7_packmate_side": ("NaafiriPackmate", PACK, 75, 1600, 1.8, "box"),
    "full_naafiri": ("Naafiri", HERO, 35, 1600, 1.6, "none"),
    "full_naafiri_side": ("Naafiri", HERO, 75, 1600, 1.6, "none"),
    "full_packmate": ("NaafiriPackmate", PACK, 35, 1600, 1.8, "none"),
    "full_packmate_side": ("NaafiriPackmate", PACK, 75, 1600, 1.8, "none"),
}
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, squares tall, label)
    "10a_layout_naafiri.png": ("full_naafiri", 36, "A: Naafiri's idle, 3/4 front; top blade tip to paws 396 px (36 squares of 11)"),
    "10b_layout_naafiri_side.png": ("full_naafiri_side", 36, "SA: Naafiri from the side, facing right; same size and ground"),
    "10c_layout_packmate.png": ("full_packmate", 20, "P: a packmate's idle, 3/4 front; top to paws 220 px (20 squares of 11)"),
    "10d_layout_packmate_side.png": ("full_packmate_side", 20, "SP: a packmate from the side, facing right; same size and ground"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_nidalee_cougar.png": ("nidalee", "hd_c_idle"),
    "12_style_kindred.png": ("kindred", "hd_idle"),
    "13_style_warwick.png": ("warwick", "hd_idle"),
    "14_style_volibear.png": ("volibear", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Naafiri", "--hq", "--mirror", "--hide-submeshes", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # both hounds hold the head at the front (image right): hers low under the blades, his high
        w, h = x1 - x0, y1 - y0
        top, bottom = (0.3, 0.95) if champ == "Naafiri" else (-0.05, 0.75)
        im = im.crop((x0 + round(w * 0.58), max(0, y0 + round(h * top)), min(im.width, x1 + w // 30),
                      min(im.height, y0 + round(h * bottom))))
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
    """The whole figure scaled so its top to its paws is `squares` x SQ px, paws on SOLE, centred on CX."""
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Naafiri.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/naafiri/skins/base/naafiriloadscreen_0.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "8_naafiri_splash.png"))
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "naafiri", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
