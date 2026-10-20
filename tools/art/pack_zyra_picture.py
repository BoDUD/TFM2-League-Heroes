"""Build the step-0 pack for Codex (assets/source/zyra/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_zyra_picture.py --out C:/t/zy_work/zyra_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..7 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Morgana, Elise and Nidalee, 8x, cut from their
sheets), then <out>.zip. Render into a short folder (C:/t).
Zyra (#140, 2026-10-20) is the Rise of the Thorns: a tall slender plant woman with a huge mane of crimson-magenta
petal-strand hair swept back, two yellow-green leaf horns on her head, pale cream-green skin, glowing amber eyes, a
dark purple choker with a pink gem, a green leaf bodice and leafy green shorts, long dark purple thorny legs with spiky
leaves down their outer side and clawed dark feet, magenta thorn spikes on her shoulders, dark purple vine gauntlets
studded with pink thorns, clawed hands and a thin magenta whip-vine with a spear tip curling from each wrist.
Her base texture sits beside the skins folder (ASSETS/Characters/Zyra/Zyra_base_TX_CM.tex): pose_ref finds it since
2026-10-20. Her plants (ZyraThornPlant = the Thorn Spitter, ZyraGraspingPlant = the Vine Lasher, ZyraSeed) are
characters of their own in Zyra.wad.client (--champ ZyraThornPlant --wad Zyra): step 3 (effects), not here.
Four pictures for the user to pick from: A = League's idle, 3/4 front facing right, League's full mane and long wrist
whips; B = the same with a tighter mane and short whips curled round her wrists; SA / SB = the same two seen from the
SIDE facing right (the base of the actions). Hair top to soles about 66 squares of 11 px. Yaw 0 front, 35 the 3/4
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
IDLE = "zyra_idle1@0"
HIDE = []  # one submesh (lambert2), nothing to hide
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_zyra_idle": (IDLE, 35, 1600, 1.4, "box"),
    "2_zyra_frontal": (IDLE, 0, 1600, 1.4, "box"),
    "3_zyra_head": (IDLE, 35, 3200, 1.4, "head"),
    "4_zyra_back": (IDLE, 200, 1600, 1.4, "box"),
    "6_zyra_side": (IDLE, 75, 1600, 1.4, "box"),
    "full_idle": (IDLE, 35, 1600, 1.4, "none"),
    "full_side": (IDLE, 75, 1600, 1.4, "none"),
}
# hair top to soles BODY_H px (66 squares of 11) on the 1536 square, soles on row SOLE, centred
BODY_H = 726
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label)
    "7a_layout_front.png": ("full_idle", "A / B: League's idle, 3/4 front; hair top to soles 726 px (66 squares of 11)"),
    "7b_layout_side.png": ("full_side", "SA / SB: the same idle from the side, facing right; same size and ground line"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_morgana.png": ("morgana", "hd_idle"),
    "12_style_elise.png": ("elise", "hd_idle"),
    "13_style_nidalee.png": ("nidalee", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Zyra", *HIDE,
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the mane, the leaf horns, the face, the choker: the top 30% of the figure, the arms cut off
        h = y1 - y0
        fx0, _, fx1, _ = _keyed(path).crop((0, y0 + round(h * 0.6), im.width, y1)).getbbox()   # the legs' span
        cx, half = (fx0 + fx1) // 2, round(h * 0.2)
        im = im.crop((cx - half, max(0, y0 - h // 30), cx + half, y0 + round(h * 0.3)))
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
    """The whole figure scaled so ear tips to soles is BODY_H, soles on SOLE, centred on CX."""
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Zyra.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/zyra/skins/base/zyraloadscreen.tex")).convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_zyra_splash.png"))
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "zyra", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
