"""Build the step-0 pack for Codex (assets/source/shyvana/PICTURE_PROMPT.md): League references of both forms, layout
guides and style pictures.

    python tools/art/pack_shyvana_picture.py --out C:/t/sv_work/shyvana_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders of Shyvana and her dragon, the loading-screen art and
the layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this pack's Smolder, Volibear, Zyra and
Nidalee, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Shyvana (group F jungle, 2026-10-21; League 16.20's rework) is the Half-Dragon, two forms:
  Human - a tall half-dragon warrior woman: pale lavender skin, a mane of golden-orange hair, a crown of crimson dragon
  horns with black tips sweeping back, a teal-silver scale breastplate trimmed in gold, crimson cloth wraps on the
  forearms, dark plum leggings with silver-gold scale knee guards, clawed dragon feet, a long crimson scaly tail with a
  golden tip, small gold spikes on the shoulders.
  Dragon - a big crimson dragon on four clawed legs: crimson scales, two large bat wings raised (crimson membrane, darker
  inside, gold horn claws at the joints), a blazing orange-yellow flame mane on the head and neck, dark curved horns,
  ivory spikes along the spine and elbows, a teal armour plate on the chest, black claws, a gold-tipped tail.
Both are characters in Shyvana.wad.client: Shyvana and ShyvanaDragon (--champ ShyvanaDragon --wad Shyvana; the dragon's
skin scale 0.45: in League it stands about as tall as she does with its wings up, and 1.5 times her height long). Four
pictures: A = her idle 3/4 front facing right, SA = her side-on facing right, D = the dragon's idle 3/4 front facing
right, SD = the dragon side-on facing right. Human about 44 squares of 11 px from the horn tips to the soles, the dragon
about 52 from the highest wing tip to the claws (both forms on the same square size, so they keep their sizes against
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
HUMAN, DRAGON = "idle1@0", "idle2@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_human_idle": ("Shyvana", HUMAN, 35, 1600, 1.0, "box"),
    "2_human_frontal": ("Shyvana", HUMAN, 0, 1600, 1.0, "box"),
    "3_human_head": ("Shyvana", HUMAN, 35, 3200, 1.0, "head"),
    "4_human_side": ("Shyvana", HUMAN, 75, 1600, 1.0, "box"),
    "5_dragon_idle": ("ShyvanaDragon", DRAGON, 35, 1600, 1.6, "box"),
    "6_dragon_frontal": ("ShyvanaDragon", DRAGON, 0, 1600, 1.6, "box"),
    "7_dragon_head": ("ShyvanaDragon", DRAGON, 35, 3200, 1.6, "head"),
    "8_dragon_side": ("ShyvanaDragon", DRAGON, 75, 1600, 1.6, "box"),
    "full_human": ("Shyvana", HUMAN, 35, 1600, 1.0, "none"),
    "full_human_side": ("Shyvana", HUMAN, 75, 1600, 1.0, "none"),
    "full_dragon": ("ShyvanaDragon", DRAGON, 35, 1600, 1.6, "none"),
    "full_dragon_side": ("ShyvanaDragon", DRAGON, 75, 1600, 1.6, "none"),
}
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, squares tall, label)
    "10a_layout_human.png": ("full_human", 44, "A: Shyvana's idle, 3/4 front; horn tips to soles 484 px (44 squares of 11)"),
    "10b_layout_human_side.png": ("full_human_side", 44, "SA: Shyvana from the side, facing right; same size and ground"),
    "10c_layout_dragon.png": ("full_dragon", 52, "D: the dragon's idle, 3/4 front; wing tip to claws 572 px (52 squares of 11)"),
    "10d_layout_dragon_side.png": ("full_dragon_side", 52, "SD: the dragon from the side, facing right; same size and ground"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_smolder.png": ("smolder", "hd_idle"),
    "12_style_volibear.png": ("volibear", "hd_idle"),
    "13_style_zyra.png": ("zyra", "hd_idle"),
    "14_style_nidalee.png": ("nidalee", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Shyvana", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size),
           "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name,
           "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":
        w, h = x1 - x0, y1 - y0
        if champ == "ShyvanaDragon":   # the head sits at the front (image right) under the raised wing: mane, horns, jaw
            im = im.crop((x0 + round(w * 0.45), y0 + round(h * 0.3), min(im.width, x1 + w // 30), y0 + round(h * 0.8)))
        else:                          # the horn crown, the hair, the face: the top of her
            half = round(max(w * 0.4, h * 0.16))
            cx = (x0 + x1) // 2
            im = im.crop((max(0, cx - half), max(0, y0 - h // 40), min(im.width, cx + half), y0 + round(h * 0.3)))
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Shyvana.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/shyvana/skins/base/shyvanaloadscreen_0.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "9_shyvana_splash.png"))
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "shyvana", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
