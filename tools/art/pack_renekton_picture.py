"""Build the step-0 pack for Codex (assets/source/renekton/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_renekton_picture.py --out D:\\TFM2-Workshop\\renekton_pack0 [--lol D:\\WeGameApps\\lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground). Version A = League's idle (Renekton_Idle1: hunched forward, the
crescent blade trailing low behind him in the near hand, the tail on the ground behind); version B = the blade raised
over his shoulder (Renekton_Spell2 at 880 ms: Ruthless Predator's wind-up, the blade held up behind his head).
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
HEAD = (0.40, 0.10, 0.88, 0.50)   # head and shoulders in the 2000 px idle render
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_renekton_league_idle": (["renekton_idle1@0"], 30, True, 1000, 0.75, 0.92, 1.3, None),
    "2_renekton_league_side": (["renekton_idle1@0"], 70, True, 1000, 0.75, 0.92, 1.3, None),
    "3_renekton_league_head": (["renekton_idle1@0"], 40, True, 2000, 0.8, 0.92, 1.0, HEAD),
    "4_renekton_league_back": (["renekton_idle1@0"], 150, True, 1000, 0.75, 0.92, 1.3, None),
    "6_renekton_league_raised": (["renekton_spell2@880"], 30, True, 1000, 0.75, 0.92, 1.3, None),
    "7_renekton_league_raised_side": (["renekton_spell2@880"], 70, True, 1000, 0.75, 0.92, 1.3, None),
    "8_renekton_league_actions": (["renekton_attack1_60fps@660", "renekton_spell1@335", "renekton_spell3@387",
                                   "renekton_run@200", "renekton_run@580"], 30, True, 600, 0.6, 0.88, 1.2, None),
}
STYLE = {
    "9_style_twitch.png": os.path.join(SRC, "twitch", "codex_picture", "twitch-model-B.png"),
    "10_style_tryndamere.png": os.path.join(SRC, "tryndamere", "codex_picture", "tryndamere-model-A.png"),
    "11_style_khazix.png": os.path.join(SRC, "khazix", "codex_picture", "khazix-model-B.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Renekton", "--hq",
           "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground", str(ground),
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out]
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Renekton.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("ASSETS/Characters/Renekton/Skins/Base/RenektonLoadScreen.tex".lower()))
    splash.convert("RGB").save(os.path.join(refs, "5_renekton_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "renekton", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
