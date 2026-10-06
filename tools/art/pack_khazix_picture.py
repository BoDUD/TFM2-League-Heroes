"""Build the step-0 pack for Codex (assets/source/khazix/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_khazix_picture.py --out D:\\TFM2-Workshop\\khazix_pack0 [--lol D:\\WeGameApps\\lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground). Kha'Zix's evolved parts are one mesh with the rest, shown or
hidden by joint scales that League layers over every clip from Khazix_evo_overrides: --layer takes those joints from
it. BASE = all four parts unevolved (version A, League's idle); FINAL = the parts this port evolves - Reaper Claws
(Q, the hands), Wings (E) and Adaptive Cloaking (R, the back shell) - with the W spikes left unevolved (version B).
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
HEAD = (0.30, 0.18, 0.72, 0.60)   # head and shoulders in the 2000 px idle render
BASE = ["--layer", "Khazix_evo_overrides@0=Wing|_evo$|_base$|Spike|Shell"]
FINAL = ["--layer", r"Khazix_evo_overrides@0=Spikes|Spike\d"]
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None, layer)
RENDERS = {
    "1_khazix_league_front": (["khazix_idle1@0"], 30, True, 1000, 0.75, 0.92, 1.3, None, BASE),
    "2_khazix_league_side": (["khazix_idle1@0"], 70, True, 1000, 0.75, 0.92, 1.3, None, BASE),
    "3_khazix_league_head": (["khazix_idle1@0"], 40, True, 2000, 0.8, 0.92, 1.0, HEAD, BASE),
    "4_khazix_league_back": (["khazix_idle1@0"], 150, True, 1000, 0.75, 0.92, 1.3, None, BASE),
    "6_khazix_league_evolved": (["khazix_idle1@0"], 30, True, 1000, 0.75, 0.92, 1.3, None, FINAL),
    "7_khazix_league_evolved_side": (["khazix_idle1@0"], 70, True, 1000, 0.75, 0.92, 1.3, None, FINAL),
    "8_khazix_league_actions": (["khazix_attack1@383", "khazix_spell1@333", "khazix_spell2@333", "khazix_spell3@250",
                                 "khazix_run@250"], 30, True, 600, 0.6, 0.88, 1.2, None, BASE),
}
STYLE = {
    "9_style_pyke.png": os.path.join(SRC, "pyke", "codex_picture", "pyke-model-A.png"),
    "10_style_alistar.png": os.path.join(SRC, "alistar", "codex_picture", "alistar-model-A.png"),
    "11_style_kayn.png": os.path.join(SRC, "kayn", "codex_picture", "kayn-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop, layer = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Khazix", "--hq",
           "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground", str(ground),
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, *layer]
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Khazix.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("ASSETS/Characters/KhaZix/Skins/Base/KhazixLoadScreen.tex".lower()))
    splash.convert("RGB").save(os.path.join(refs, "5_khazix_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "khazix", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
