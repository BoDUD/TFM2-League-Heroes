"""Build the step-0 pack for Codex (assets/source/gwen/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_gwen_picture.py --out D:/TFM2-Workshop/gwen_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..7 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/8..10 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground; the scissors drawn with the weapon map, the doll Isolde, the
needle and the scissors' smear card left out): League's idle 3/4 from the front facing right (mirrored), the same from
the front, a head-and-shoulders close-up, the back, the passive idle with the scissors up (version B) and a strip of
her snipping, the dash and the needle throw.
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
MESH = ["--hide-submesh", "Doll", "--hide-submesh", "Needle", "--hide-submesh", "Scissors_A_Smear",
        "--submesh-texture", "Scissors=Weapon"]
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_gwen_league_front": (["idle@0"], 30, True, 1000, 0.6, 0.92, 1.6, None),
    "2_gwen_league_frontal": (["idle@0"], 0, True, 1000, 0.6, 0.92, 1.6, None),
    "3_gwen_league_head": (["idle@0"], 20, True, 2000, 0.8, 0.92, 1.0, (0.30, 0.10, 0.70, 0.46)),
    "4_gwen_league_back": (["idle@0"], 150, True, 1000, 0.6, 0.92, 1.6, None),
    "6_gwen_league_passive": (["passive_idle@0"], 30, True, 1000, 0.6, 0.92, 1.2, None),
    "7_gwen_league_actions": (["attack1@250", "spell1@300", "spell3_dash@150", "spell4@300"], 30,
                              True, 600, 0.55, 0.88, 1.3, None),
}
STYLE = {
    "8_style_samira.png": os.path.join(SRC, "samira", "codex_picture", "samira-model-A.png"),
    "9_style_evelynn.png": os.path.join(SRC, "evelynn", "codex_picture", "evelynn-model-A.png"),
    "10_style_varus.png": os.path.join(SRC, "varus", "codex_picture", "varus-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Gwen", "--hq",
           "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground", str(ground),
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, *MESH]
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
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    os.makedirs(refs, exist_ok=True)
    os.makedirs(style, exist_ok=True)
    for name, spec in RENDERS.items():
        render(a.lol, name, spec, refs)
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Gwen.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("ASSETS/Characters/Gwen/Skins/Base/GwenLoadscreen_0.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_gwen_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "gwen", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
