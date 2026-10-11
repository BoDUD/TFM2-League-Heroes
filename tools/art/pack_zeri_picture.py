"""Build the step-0 pack for Codex (assets/source/zeri/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_zeri_picture.py --out dist/zeri_packs/zeri_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right): the base skin - the two spiky
lime-and-teal hair buns, the oversized teal jacket with metal buttons and the glowing tube on its chest, the yellow tank
top with a magenta-green lightning print, the maroon leggings with a knee pad, the brown ankle boots with orange socks,
the fingerless maroon glove and her lime-and-orange electric rifle (the backpack battery behind her). Version A =
League's Idle at 0 ms (the rifle held up beside her head, barrel up, the far arm hanging), version B = Spell1 at 427 ms
(Burst Fire: the rifle held level at her hip, barrel forward, legs apart: the shooting stance).
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
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {  # clips: Idle 2.7 s, Idle_Var1, Run 0.85 s, Attack1, Spell1 (Burst Fire), Spell2 (W), Spell3, Spell4_Activate
    "1_zeri_league_front": (["Idle@0"], 30, True, 1000, 0.8, 0.92, 1.1, None),
    "2_zeri_league_frontal": (["Idle@0"], 0, True, 1000, 0.8, 0.92, 1.1, None),
    "3_zeri_league_head": (["Idle@0"], 15, True, 2000, 0.8, 0.92, 1.0, (0.36, 0.08, 0.70, 0.36)),
    "4_zeri_league_back": (["Idle@0"], 150, True, 1000, 0.8, 0.92, 1.1, None),
    "6_zeri_league_run": (["Run@0", "Run@213", "Run@427"], 30, True, 800, 0.8, 0.92, 1.2, None),
    "7_zeri_league_actions": (["Attack1@150", "Spell1@427", "Spell2@200", "Spell3@150", "Spell4_Activate@207"], 30, True,
                              700, 0.75, 0.92, 1.3, None),
    "8_zeri_league_shooting": (["Spell1@427"], 30, True, 1000, 0.8, 0.92, 1.1, None),
}
STYLE = {
    "9_style_seraphine.png": os.path.join(SRC, "seraphine", "codex_picture", "seraphine-model-A.png"),
    "10_style_samira.png": os.path.join(SRC, "samira", "codex_picture", "samira-model-A.png"),
    "11_style_syndra.png": os.path.join(SRC, "syndra", "codex_picture", "syndra-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Zeri",
           "--hq", "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground",
           str(ground), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out]
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Zeri.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/zeri/skins/base/zeriloadscreen_0.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_zeri_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "zeri", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
