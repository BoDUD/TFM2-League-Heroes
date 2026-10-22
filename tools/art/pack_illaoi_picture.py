"""Build the step-0 pack for Codex (assets/source/illaoi/PICTURE_PROMPT.md): League references of Illaoi and her
tentacle, layout guides and style pictures.

    python tools/art/pack_illaoi_picture.py --out C:/t/il_work/illaoi_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders of Illaoi and a tentacle, the loading-screen art) and
<out>/refs/10a..10c (layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this pack's K'Sante,
Udyr, Nilah and Nami, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Illaoi (group H, top at the user's pick, 2026-10-22) is the Kraken Priestess: a tall broad-shouldered woman with dark
brown skin, black hair in a high bun with gold rings, green eyes and a gold nose ring; gold-and-teal plate on the
shoulders, the forearms and the shins, a teal wrap over the chest, a dark red loincloth, bare strong arms and thighs;
her golden Idol of Nagakabouros - a big round carved gold disc with a green spiral eye - rests on her near shoulder in
the idle. The tentacle (her passive, Q, W, R) is the character IllaoiMinion in Illaoi's WAD: a thick tentacle growing
out of the ground, dark green-teal with gold bands, its tip curled. It stands in the game as effect pictures on the
ground (league_zyra's plants), which the client never mirrors (the skill's rule "the client never mirrors an effect
picture"), so it is drawn from the front.
Three pictures: A = her idle 3/4 front facing right, SA = her side-on facing right, T = a tentacle from the front.
Illaoi about 58 squares of 11 px from the top of her hair bun to the soles, the tentacle about 50 (the same square
size). Her skin draws nothing extra in the idle: renders do NOT use --hide-submeshes (it hides her whole body). Yaw 0
front, 35 the 3/4 view, 75 the side.
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
HERO, TENT = "illaoi_idle1@0", "illaoiminion_idleangry@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_illaoi_idle": ("Illaoi", HERO, 35, 1600, 1.2, "box"),
    "2_illaoi_frontal": ("Illaoi", HERO, 0, 1600, 1.2, "box"),
    "3_illaoi_head": ("Illaoi", HERO, 35, 3200, 1.2, "head"),
    "4_illaoi_back": ("Illaoi", HERO, 200, 1600, 1.2, "box"),
    "6_illaoi_side": ("Illaoi", HERO, 75, 1600, 1.2, "box"),
    "7_tentacle_front": ("IllaoiMinion", TENT, 0, 1600, 1.2, "box"),
    "8_tentacle_34": ("IllaoiMinion", TENT, 35, 1600, 1.2, "box"),
    "9_tentacle_slam": ("IllaoiMinion", "illaoiminion_attack1@900", 75, 1600, 1.2, "box"),
    "full_illaoi": ("Illaoi", HERO, 35, 1600, 1.2, "none"),
    "full_illaoi_side": ("Illaoi", HERO, 75, 1600, 1.2, "none"),
    "full_tentacle": ("IllaoiMinion", TENT, 0, 1600, 1.2, "none"),
}
HEAD_CX = 0.62   # her head sits right of her box's centre (the idol on her shoulder widens it to the left)
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, squares tall, label)
    "10a_layout_illaoi.png": ("full_illaoi", 58, "A: Illaoi's idle, 3/4 front; top to soles ~640 px (58 squares of 11)"),
    "10b_layout_illaoi_side.png": ("full_illaoi_side", 58, "SA: Illaoi from the side, facing right; same size and ground"),
    "10c_layout_tentacle.png": ("full_tentacle", 50, "T: a tentacle from the front; curl top to base ~550 px (50 squares of 11)"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_ksante.png": ("ksante", "hd_idle"),
    "12_style_udyr.png": ("udyr", "hd_idle"),
    "13_style_nilah.png": ("nilah", "hd_idle"),
    "14_style_nami.png": ("nami", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Illaoi", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the bun, the face, the shoulders: the upper 30% of her, around the head
        h = y1 - y0
        cx = round(x0 + (x1 - x0) * HEAD_CX)
        im = im.crop((cx - round(h * 0.17), max(0, y0 - h // 30), cx + round(h * 0.17), y0 + round(h * 0.3)))
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Illaoi.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/illaoi/skins/base/illaoiloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_illaoi_splash.png"))
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "illaoi", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
