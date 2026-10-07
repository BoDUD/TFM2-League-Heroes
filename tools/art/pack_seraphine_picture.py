"""Build the step-0 pack for Codex (assets/source/seraphine/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_seraphine_picture.py --out dist/seraphine_packs/seraphine_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground): the skin's own hidden submeshes (microphone, the ult speakers,
the bar and the plane) left out, the hair drawn with its own map. League's Seraphine stands on her floating stage
whenever she moves or casts (idle_in, run, spells); she only sits on it in the long idle (idle2) - version A = standing
on the stage, version B = standing on the ground without it (the stage left to the effects).
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
MESH = ["--hide-submesh", "Mic", "--hide-submesh", "UltSpeaker", "--hide-submesh", "Bar", "--hide-submesh", "Plane",
        "--submesh-texture", "Hair=Hair"]
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_seraphine_league_front": (["seraphin_idlein@0"], 30, True, 1000, 0.75, 0.92, 1.1, None),
    "2_seraphine_league_frontal": (["seraphin_idlein@0"], 0, True, 1000, 0.75, 0.92, 1.1, None),
    "3_seraphine_league_head": (["seraphin_idlein@0"], 15, True, 2000, 0.65, 0.92, 1.0, (0.30, 0.10, 0.66, 0.42)),
    "4_seraphine_league_back": (["seraphin_idlein@0"], 150, True, 1000, 0.75, 0.92, 1.1, None),
    "6_seraphine_league_glide": (["seraphin_run@0", "seraphin_run@500"], 30, True, 800, 0.75, 0.92, 1.1, None),
    "7_seraphine_league_actions": (["seraphin_attack1@200", "seraphin_spell1@300", "seraphin_spell3@300",
                                    "seraphin_spell2@300", "seraphin_spell4_cast@300"], 30, True, 600, 0.5, 0.95,
                                   1.1, None),
    "8_seraphine_league_sit": (["seraphin_idle2@0"], 30, True, 800, 0.75, 0.92, 1.3, None),
}
STYLE = {
    "9_style_gwen.png": os.path.join(SRC, "gwen", "codex_picture", "gwen-model-A.png"),
    "10_style_samira.png": os.path.join(SRC, "samira", "codex_picture", "samira-model-A.png"),
    "11_style_evelynn.png": os.path.join(SRC, "evelynn", "codex_picture", "evelynn-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Seraphine",
           "--hq", "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground",
           str(ground), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, *MESH]
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Seraphine.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/seraphine/skins/base/seraphineloadscreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_seraphine_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "seraphine", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
