"""Build the step-0 pack for Codex (assets/source/mordekaiser/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_mordekaiser_picture.py --out dist/mordekaiser_packs/mordekaiser_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/10..12 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right) of the base skin with the joke and
recall parts hidden (his Guitar, the Shadow Isles poro and the Crown are submeshes of the same mesh; the Mace has its
own map): a towering revenant in spiked black iron armour, ghost-green light seeping from the gaps, a horned crowned
helm with two green eyes in the visor, a tattered maroon cloth hanging from the belt, and his huge spiked mace
Nightfall resting on the shoulder. Version A = League's idle at 3/4 front, version B = the same figure side-on facing
right (the base of every action, memory side-view-design).
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
    "1_mordekaiser_league_front": (["idle@0"], 30, True, 1000, 0.78, 0.94, 1.0, None),
    "2_mordekaiser_league_frontal": (["idle@0"], 0, True, 1000, 0.78, 0.94, 1.0, None),
    "3_mordekaiser_league_head": (["idle@0"], 20, True, 2600, 0.78, 0.94, 1.0, (0.3, 0.1, 0.7, 0.42)),
    "4_mordekaiser_league_back": (["idle@0"], 160, True, 1000, 0.78, 0.94, 1.0, None),
    "6_mordekaiser_league_run": (["run@0", "run@300", "run@600"], 60, True, 800, 0.66, 0.92, 1.2, None),
    "7_mordekaiser_league_actions": (["autoattack1@494", "spell_1@578", "spell3_cast@1333", "spell_4_cast@250"], 60,
                                     True, 800, 0.55, 0.95, 1.5, None),
    "8_mordekaiser_league_side_b": (["idle@0"], 60, True, 1000, 0.78, 0.94, 1.0, None),
    "9_mordekaiser_league_side": (["idle@0"], 85, True, 1000, 0.78, 0.94, 1.0, None),
}
SUBMESH = ["--hide-submesh", "Guitar", "--hide-submesh", "Poro_ShadowIsles_Mat", "--hide-submesh", "Crown",
           "--submesh-texture", "Mace=Mace"]
STYLE = {
    "10_style_kassadin.png": os.path.join(SRC, "kassadin", "codex_picture", "kassadin-model-A.png"),
    "11_style_nautilus.png": os.path.join(SRC, "nautilus", "codex_picture", "nautilus-model-A.png"),
    "12_style_gragas.png": os.path.join(SRC, "gragas", "codex_picture", "gragas-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Mordekaiser",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Mordekaiser.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/mordekaiser/skins/base/mordekaiserloadscreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_mordekaiser_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "mordekaiser", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
