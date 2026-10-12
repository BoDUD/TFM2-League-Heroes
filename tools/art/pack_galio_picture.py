"""Build the step-0 pack for Codex (assets/source/galio/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_galio_picture.py --out dist/galio_packs/galio_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/10..12 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right) of the base skin: a towering winged
colossus of pale green-grey petricite stone, gold trim on every edge, a gold crested helm-crown over a stern stone face
with glowing blue eyes, a gold winged emblem on the chest, huge stone fists, two tall gold-feathered wings rising high
behind him, a stone tail ending in a gold arrowhead, digitigrade clawed stone feet. Version A = League's idle with the
wings raised high (as in the game), version B = the same figure with the wings half folded (tips a little above the
crown) - a more compact silhouette for the game's small frames. Side-on comes in step 1 (memory side-view-design).
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
    "1_galio_league_front": (["galio_idle01@0"], 30, True, 1000, 0.80, 0.94, 1.0, None),
    "2_galio_league_frontal": (["galio_idle01@0"], 0, True, 1000, 0.80, 0.94, 1.0, None),
    "3_galio_league_head": (["galio_idle01@0"], 25, True, 2600, 0.80, 0.94, 1.0, (0.32, 0.22, 0.68, 0.52)),
    "4_galio_league_back": (["galio_idle01@0"], 160, True, 1000, 0.80, 0.94, 1.0, None),
    "6_galio_league_run": (["galio_run@0", "galio_run@330", "galio_run@660"], 60, True, 800, 0.70, 0.94, 1.2, None),
    "7_galio_league_actions": (["galio_attack01@330", "galio_spell1@400", "galio_spell3@250", "galio_spell2_idle@0"],
                               60, True, 800, 0.60, 0.95, 1.5, None),
    "8_galio_league_side_b": (["galio_idle01@0"], 60, True, 1000, 0.80, 0.94, 1.0, None),
    "9_galio_league_side": (["galio_idle01@0"], 85, True, 1000, 0.80, 0.94, 1.0, None),
}
SUBMESH = []
STYLE = {
    "10_style_mordekaiser.png": os.path.join(SRC, "mordekaiser", "codex_picture", "mordekaiser-model-A.png"),
    "11_style_braum.png": os.path.join(SRC, "braum", "codex_picture", "braum-model-A.png"),
    "12_style_kassadin.png": os.path.join(SRC, "kassadin", "codex_picture", "kassadin-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Galio",
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
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    os.makedirs(refs, exist_ok=True)
    os.makedirs(style, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Galio.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/galio/skins/base/galioloadscreen.tex"))
        splash.convert("RGB").save(os.path.join(refs, "5_galio_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "galio", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
