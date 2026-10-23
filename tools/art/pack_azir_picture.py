"""Build the step-0 pack for Codex (assets/source/azir/PICTURE_PROMPT.md): League references of Azir, his sand soldier,
his Imperial Guard and his Sun Disc, layout guides and style pictures.

    python tools/art/pack_azir_picture.py --out C:/t/az_work/azir_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..13 (League renders of Azir and his three summons, the loading-screen art) and
<out>/refs/14a..14f (layout guides: Riot's, kept local, never committed) and <out>/style/15..18 (this pack's Xerath, Nasus,
Malzahar and K'Sante, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Azir (group H, mid at the user's pick, 2026-10-23) is the Emperor of the Sands: a tall slim figure in a FALCON-HEADED
gold helmet (a beak in front, a crest on top, cheek wings), gold armour with teal gems, a deep purple robe and cape whose
long ribbons trail far behind him (kept short in the picture: the sprite's width), grey-blue legs and gold greaves, and
a long gold sceptre with a split head, taller than he is. His summons live in Azir.wad.client as characters of their
own: AzirSoldier (the sand soldier of the passive, Q and E: a dark-skinned soldier in a gold falcon helmet with a spear),
AzirUltSoldier (R's Imperial Guard: the same soldier behind a tall gold tower shield) and AzirSunDisc (the passive's
Sun Disc: a gold spire holding up a round purple-and-gold sun emblem). The summons stand in the game as effect pictures,
never mirrored (the skill's rule), so the soldier, the guard and the disc are drawn from the FRONT; the guard also from
the side (R's wall charging) to decide later.
Six pictures: A = Azir's idle 3/4 front facing right, SA = his side facing right, T = the soldier from the front, U = the
guard from the front, US = the guard from the side facing right, D = the disc from the front. Squares of 11 px; Azir
about 56 squares from the top of his helmet's crest to the soles (the sceptre higher), the soldier 48, the guard 52 (shield
top), the disc 66. Yaw 0 front, 35 the 3/4 view, 75 the side.
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
HERO, SOLD, GUARD, DISC = "azir_idle1@0", "azirsoldier_idle1@0", "azirultsoldier_idle1@0", "azirsundisc_idle1@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_azir_idle": ("Azir", HERO, 35, 1600, 1.2, "box"),
    "2_azir_frontal": ("Azir", HERO, 0, 1600, 1.2, "box"),
    "3_azir_head": ("Azir", HERO, 35, 3200, 1.2, "head"),
    "4_azir_back": ("Azir", HERO, 200, 1600, 1.2, "box"),
    "6_azir_side": ("Azir", HERO, 75, 1600, 1.2, "box"),
    "7_soldier_front": ("AzirSoldier", SOLD, 0, 1600, 1.2, "box"),
    "8_soldier_34": ("AzirSoldier", SOLD, 35, 1600, 1.2, "box"),
    "9_soldier_stab": ("AzirSoldier", "azirsoldier_attack1@300", 75, 1600, 1.2, "box"),
    "10_guard_front": ("AzirUltSoldier", GUARD, 0, 1600, 1.2, "box"),
    "11_guard_34": ("AzirUltSoldier", GUARD, 60, 1600, 1.2, "box"),
    "12_disc_front": ("AzirSunDisc", DISC, 0, 1600, 1.2, "box"),
    "13_disc_34": ("AzirSunDisc", DISC, 35, 1600, 1.2, "box"),
    "full_azir": ("Azir", HERO, 35, 1600, 1.2, "none"),
    "full_azir_side": ("Azir", HERO, 75, 1600, 1.2, "none"),
    "full_soldier": ("AzirSoldier", SOLD, 0, 1600, 1.2, "none"),
    "full_guard": ("AzirUltSoldier", GUARD, 0, 1600, 1.2, "none"),
    "full_guard_side": ("AzirUltSoldier", GUARD, 90, 1600, 1.2, "none"),
    "full_disc": ("AzirSunDisc", DISC, 0, 1600, 1.2, "none"),
}
HEAD_TOP, HEAD_H = 0.28, 0.26   # the sceptre rises far above him: the head crop starts 28% down the figure, 26% tall
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, squares tall top to soles, label)
    "14a_layout_azir.png": ("full_azir", 80, "A: Azir's idle, 3/4 front; crest top to soles ~616 px (56 squares of 11), the sceptre higher"),
    "14b_layout_azir_side.png": ("full_azir_side", 80, "SA: Azir from the side, facing right; same size and ground"),
    "14c_layout_soldier.png": ("full_soldier", 48, "T: the sand soldier from the front; crest top to soles ~528 px (48 squares of 11)"),
    "14d_layout_guard.png": ("full_guard", 52, "U: the Imperial Guard from the front; shield top to the ground ~572 px (52 squares)"),
    "14e_layout_guard_side.png": ("full_guard_side", 52, "US: the Imperial Guard from the side, facing right; same size"),
    "14f_layout_disc.png": ("full_disc", 66, "D: the Sun Disc from the front; top to base ~726 px (66 squares of 11)"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "15_style_xerath.png": ("xerath", "hd_idle"),
    "16_style_nasus.png": ("nasus", "hd_idle"),
    "17_style_malzahar.png": ("malzahar", "hd_idle"),
    "18_style_ksante.png": ("ksante", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Azir", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the falcon helmet and the shoulders: below the sceptre's head, around the widest run of columns
        h = y1 - y0
        top = y0 + round(h * HEAD_TOP)
        a = np.asarray(_keyed(path))[top:top + round(h * HEAD_H), :, 3] > 0
        cols = np.nonzero(a.sum(axis=0) > a.shape[0] // 4)[0]   # the sceptre's thin shaft drops out
        runs = np.split(cols, np.nonzero(np.diff(cols) > 4)[0] + 1)
        run = max(runs, key=len)
        cx = (run[0] + run[-1]) // 2
        im = im.crop((cx - round(h * 0.15), top, cx + round(h * 0.15), top + round(h * HEAD_H)))
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
    can.alpha_composite(fig, (max(0, x0), y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - squares * SQ), (1536, SOLE - squares * SQ)], fill=(190, 190, 190, 255), width=1)
    if name.endswith(("_azir.png", "_azir_side.png")):   # the crest line: 56 squares
        d.line([(0, SOLE - 56 * SQ), (1536, SOLE - 56 * SQ)], fill=(205, 205, 205, 255), width=1)
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Azir.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/azir/skins/base/azirloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_azir_splash.png"))
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "azir", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
