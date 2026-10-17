"""Build the step-0 pack for Codex (assets/source/pyke/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_pyke_picture.py --out D:\\TFM2-Workshop\\pyke_pack0 [--lol D:\\WeGameApps\\lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..7 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/8..10 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground; the Nensi sea monster and the scroll submeshes left out, the
harpoon kept): League's idle (crouched, harpoon raised: version A) seen 3/4 from the front facing right (mirrored), the
same from the front, a head-and-shoulders close-up, the back (the coat tails), the idle-in pose standing with the
harpoon held low (version B) and a strip of his attack, Q stab, hook throw and run.
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
HEAD = (0.38, 0.25, 0.70, 0.57)   # head and shoulders in the 2000 px idle-in render
MESH = ["--hide-submesh", "Pyke_Base_Nensi_Mat", "--hide-submesh", "Pyke_Base_Scroll_Mat"]
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_pyke_league_front": (["pyke_idle1@0"], 30, True, 1000, 0.75, 0.92, 1.2, None),
    "2_pyke_league_frontal": (["pyke_idle1@0"], 0, True, 1000, 0.75, 0.92, 1.2, None),
    "3_pyke_league_head": (["pyke_idle_in@3000"], 20, True, 2000, 0.8, 0.92, 1.0, HEAD),
    "4_pyke_league_back": (["pyke_idle1@0"], 150, True, 1000, 0.75, 0.92, 1.2, None),
    "6_pyke_league_standing": (["pyke_idle_in@3000"], 30, True, 1000, 0.75, 0.92, 1.0, None),
    "7_pyke_league_actions": (["pyke_attack1@300", "pyke_spell1_short_hit@200", "pyke_spell1_long_hook@200", "pyke_run_base@200"],
                              30, True, 600, 0.6, 0.88, 1.1, None),
}
STYLE = {
    "8_style_samira.png": os.path.join(SRC, "samira", "codex_picture", "samira-model-A.png"),
    "9_style_jhin.png": os.path.join(SRC, "jhin", "codex_picture", "jhin-model-A.png"),
    "10_style_kayn.png": os.path.join(SRC, "kayn", "codex_picture", "kayn-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Pyke", "--hq",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Pyke.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("ASSETS/Characters/Pyke/Skins/Base/PykeLoadscreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_pyke_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "pyke", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
