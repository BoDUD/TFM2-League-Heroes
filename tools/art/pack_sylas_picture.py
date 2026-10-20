"""Build the step-0 pack for Codex (assets/source/sylas/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_sylas_picture.py --out C:/t/sy_work/sylas_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guide: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Darius, Graves and Jayce, 8x, cut from their
sheets), then <out>.zip. Render into a short folder (C:/t).
Sylas (#143, 2026-10-20) is the Unshackled: a lean, muscular mage-revolutionary, bare-chested and scarred, long dark
hair swept back and tied, a short dark beard; a dark teal scarf / collar wrapped high round his neck with a brass
clasp; dark teal-green trousers, a wide brown belt, brown boots; on both forearms huge petricite manacles (pale
pinkish-tan stone with dark violet-black bands) from which heavy petricite chains hang to the ground.
Two pictures for the user to pick from, both 3/4 front facing right (the user, 2026-10-20: 3/4 only, no side view, the
actions are posed on the 3/4 design): A = League's idle, the chains hanging from the manacles down to the ground and
trailing a few links behind him as in League; B = the same Sylas with the chains SHORTER (wound once round each
manacle, the ends hanging to his knees, never on the ground - the sprite compact). Hair top to soles about 68 squares
of 11 px. His model: yaw 0 is the front, 35 the 3/4 view, 75 the side.
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
IDLE = "sylas_idle@0"
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_sylas_idle": (IDLE, 35, 1600, 1.4, "box"),
    "2_sylas_frontal": (IDLE, 0, 1600, 1.4, "box"),
    "3_sylas_head": (IDLE, 30, 3200, 1.4, "head"),
    "4_sylas_back": (IDLE, 200, 1600, 1.4, "box"),
    "6_sylas_attack": ("sylas_attack_01@200", 35, 1600, 1.6, "box"),
    "full_idle": (IDLE, 35, 1600, 1.6, "none"),
}
# hair top to soles BODY_H px (68 squares of 11) on the 1536 square, soles on row SOLE, the box (chains included)
# centred on CX
BODY_H = 748
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label)
    "8a_layout_front.png": ("full_idle", "A / B: League's idle, 3/4 front; hair top to soles 748 px (68 squares of 11); "
                                         "B: the chains shorter, off the ground"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_darius.png": ("darius", "hd_idle"),
    "12_style_graves.png": ("graves", "hd_idle"),
    "13_style_jayce.png": ("jayce", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84
# the manacles and chains are their own submeshes with their own maps (pose_ref's default map is the body's: it drew
# them skin-pink with bits of his face on them)
SUBTEX = ["gauntlet_left=Shackles_TX_CM", "gauntlet_right=Shackles_TX_CM", "chain_left=Shackles_TX_CM",
          "chain_right=Shackles_TX_CM"]
# the two big U-shaped stone locks (Sylas_Base_ChainLock_Mat) stand on the ground in his attack clip - an effect prop,
# not him: left out


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Sylas",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame] + [x for t in SUBTEX for x in ("--submesh-texture", t)] + [
               "--hide-submesh", "Sylas_Base_ChainLock_Mat"]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the hair, the face, the scarf and the chest: from the top down 40% of the body
        top = y0
        h = y1 - top
        hx0, _, hx1, _ = _keyed(path).crop((0, top, im.width, top + round(h * 0.40))).getbbox()
        m = (hx1 - hx0) // 10
        im = im.crop((hx0 - m, max(0, top - m), hx1 + m, top + round(h * 0.40)))
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
    """The whole figure scaled so spike top to soles is BODY_H, soles on SOLE, its box (tail included) centred on CX."""
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Sylas.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/sylas/skins/base/sylasloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_sylas_splash.png"))
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "sylas", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
