"""Build the step-0 pack for Codex (assets/source/viego/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_viego_picture.py --out dist/viego_packs/viego_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right): the base skin - white hair, the teal-green
thorn crown, the pale face and bare chest, the long navy coat, the spiky navy armour and the glowing green greatsword
(the Blade of the Ruined King) with its big cross guard. His mesh carries a "Wraith" submesh (the black mist shell of
his soul form) that the renders leave out, and the sword and crown take the Crown_Sword map. Version A = League's idle
(the sword on his shoulder, the blade pointing forward over his head), version B = his second idle (the sword trailing
low behind him, the hilt at his hip).
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
RENDERS = {
    "1_viego_league_front": (["Viego_idle1@0"], 30, True, 1000, 0.62, 0.92, 1.4, None),
    "2_viego_league_frontal": (["Viego_idle1@0"], 0, True, 1000, 0.62, 0.92, 1.4, None),
    "3_viego_league_head": (["Viego_idle1@0"], 15, True, 2400, 0.62, 0.92, 1.0, (0.38, 0.46, 0.60, 0.68)),
    "4_viego_league_back": (["Viego_idle1@0"], 150, True, 1000, 0.62, 0.92, 1.4, None),
    "6_viego_league_run": (["Viego_run@0", "Viego_run@250", "Viego_run@500"], 30, True, 800, 0.62, 0.92, 1.4, None),
    "7_viego_league_actions": (["Viego_attack1@250", "Viego_spell1@200", "Viego_Spell2_Charge@400",
                                "Viego_Spell4@300"], 30, True, 700, 0.6, 0.92, 1.5, None),
    "8_viego_league_idle2": (["Viego_idle2@1500"], 30, True, 1000, 0.62, 0.92, 1.4, None),
}
SUBMESH = ["--hide-submesh", "Wraith", "--submesh-texture", "Sword=Crown_Sword", "--submesh-texture", "Crown=Crown_Sword"]
STYLE = {
    "9_style_talon.png": os.path.join(SRC, "talon", "picture", "talon-model-A.png"),
    "10_style_renekton.png": os.path.join(SRC, "renekton", "codex_picture", "renekton-model-A.png"),
    "11_style_xinzhao.png": os.path.join(SRC, "xinzhao", "codex_picture", "xinzhao-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Viego",
           "--hq", "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground",
           str(ground), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out] + SUBMESH
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Viego.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/viego/skins/base/viegoloadscreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_viego_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "viego", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
