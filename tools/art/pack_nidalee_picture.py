"""Build the step-0 pack for Codex (assets/source/nidalee/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_nidalee_picture.py --out dist/nidalee_packs/nidalee_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/11..13 (this pack's approved Codex pictures), then <out>.zip.
Nidalee has two forms, so the pack asks for four pictures: the huntress (3/4 front, A the javelin upright at her side,
B the javelin level over her shoulder, ready to throw) and the cougar (side-on facing right, A standing, B crouched to
pounce). Renders (tools/lol/pose_ref.py --hq, light grey ground): the base skin - a tan, red-brown huntress with white
tribal paint, a huge black ponytail tied with red, green eyes, a bone-tooth necklace, a fur-trimmed leather top, fur
bracers, a fringed leather loincloth with tusks at the belt, big brown fur leg wraps bound with green cords, a wooden
javelin with red bands, a white feather and a pale stone blade - and her cougar: golden-orange fur with white stripes,
a white belly and muzzle, sabre fangs, green eyes, a spiky mane, a dark leather collar hung with bone tusks, dark-brown
paws and tail tip.
"""
import argparse
import os
import shutil
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
H, C = "Nidalee", "NidaleeCougar"
# name -> (champ, frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_nidalee_league_front": (H, ["nidalee_2012_idle1@0"], 30, True, 1000, 0.62, 0.92, 1.2, None),
    "2_nidalee_league_side": (H, ["nidalee_2012_idle1@0"], 70, True, 1000, 0.62, 0.92, 1.2, None),
    "3_nidalee_league_head": (H, ["nidalee_2012_idle1@0"], -20, True, 2600, 0.62, 0.92, 1.0, (0.36, 0.50, 0.60, 0.70)),
    "4_nidalee_league_body": (H, ["nidalee_2012_idle1@0"], 30, False, 1000, 0.62, 0.92, 1.2, None),
    "6_nidalee_league_actions": (H, ["nidalee_2012_spell1@0", "nidalee_2012_attack1@300", "nidalee_2012_spell3@300",
                                     "nidalee_2012_run@0", "nidalee_2012_run@500"], 80, True, 700, 0.6, 0.92, 1.4,
                                 None),
    "7_cougar_league_side": (C, ["NidaleeCougar_Idle1@0"], 90, False, 800, 0.5, 0.92, 1.8, None),
    "8_cougar_league_34": (C, ["NidaleeCougar_Idle1@0"], 40, True, 800, 0.5, 0.92, 1.8, None),
    "9_cougar_league_head": (C, ["NidaleeCougar_Idle1@0"], 60, True, 2400, 0.5, 0.92, 1.4, (0.50, 0.50, 0.75, 0.80)),
    "10_cougar_league_actions": (C, ["NidaleeCougar_Spell2_short@80", "NidaleeCougar_Spell2_short@160",
                                     "NidaleeCougar_Spell3@250", "NidaleeCougar_Attack1@300", "NidaleeCougar_Run1@0",
                                     "NidaleeCougar_Run1@500"], 90, False, 600, 0.5, 0.88, 1.8, None),
}
STYLE = {
    "11_style_braum.png": os.path.join(SRC, "braum", "codex_picture", "braum-model-A.png"),
    "12_style_kassadin.png": os.path.join(SRC, "kassadin", "codex_picture", "kassadin-model-A.png"),
    "13_style_corki.png": os.path.join(SRC, "corki", "user_picture", "corki-picture-2.png"),
}


def render(lol, name, spec, out):
    champ, frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", H, "--hq", "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit),
           "--ground", str(ground), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out]
    for f in frames:
        cmd += ["--frame", f]
    if mirror:
        cmd.append("--mirror")
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    if crop:
        im = Image.open(path)
        w, h = im.size
        im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h))).save(path)
    print(name, Image.open(path).size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--only", nargs="*", help="render only these names (checking crops)")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    os.makedirs(refs, exist_ok=True)
    os.makedirs(style, exist_ok=True)
    for name, spec in RENDERS.items():
        if not a.only or name in a.only:
            render(a.lol, name, spec, refs)
    if a.only:
        return
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Nidalee.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/nidalee/skins/base/nidaleeloadscreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_nidalee_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "nidalee", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
