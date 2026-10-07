"""Build the step-0 pack for Codex (assets/source/lillia/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_lillia_picture.py --out dist/lillia_packs/lillia_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground; her skin also carries a pheasant, a smear and the R bloom on her
head - hidden: --hide-submesh Bird / Smear / Head_Bloom, the bud stays). Version A = League's idle (Lillia_Idle2 at 0:
the fawn body standing, her bough held upright in both hands, the dream lantern hanging from its tip high over her head);
version B = the bough held forward low (Lillia_Idle2 at 3000 ms: the lantern hanging in front of her at chest height -
a shorter figure for the 40-42-row sprite).
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
HEAD = (0.30, 0.05, 0.85, 0.55)   # head and torso in the 2000 px idle render
HIDE = ["Bird", "Smear", "Head_Bloom"]
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_lillia_league_idle": (["lillia_idle2@0"], 30, True, 1000, 0.7, 0.92, 1.3, None),
    "2_lillia_league_side": (["lillia_idle2@0"], 70, True, 1000, 0.7, 0.92, 1.3, None),
    "3_lillia_league_head": (["lillia_idle2@0"], 30, True, 2000, 0.8, 0.92, 1.0, HEAD),
    "4_lillia_league_back": (["lillia_idle2@0"], 150, True, 1000, 0.7, 0.92, 1.3, None),
    "6_lillia_league_low": (["lillia_idle2@3000"], 30, True, 1000, 0.7, 0.92, 1.3, None),
    "7_lillia_league_low_side": (["lillia_idle2@3000"], 70, True, 1000, 0.7, 0.92, 1.3, None),
    "8_lillia_league_actions": (["lillia_attack1@250", "lillia_spell2b@500", "lillia_spell3@300", "lillia_run2_0@300",
                                 "lillia_run2_0@600"], 30, True, 600, 0.55, 0.88, 1.2, None),
}
STYLE = {
    "9_style_seraphine.png": os.path.join(SRC, "seraphine", "codex_picture", "seraphine-model-A.png"),
    "10_style_gwen.png": os.path.join(SRC, "gwen", "codex_picture", "gwen-model-A.png"),
    "11_style_renekton.png": os.path.join(SRC, "renekton", "codex_picture", "renekton-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Lillia", "--hq",
           "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground", str(ground),
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out]
    for f in frames:
        cmd += ["--frame", f]
    for h in HIDE:
        cmd += ["--hide-submesh", h]
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Lillia.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("ASSETS/Characters/Lillia/Skins/Base/LilliaLoadScreen.tex".lower()))
    splash.convert("RGB").save(os.path.join(refs, "5_lillia_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "lillia", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
