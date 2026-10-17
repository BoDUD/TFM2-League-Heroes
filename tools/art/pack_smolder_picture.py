"""Build the step-0 pack for Codex (assets/source/smolder/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_smolder_picture.py --out dist/smolder_packs/smolder_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/10..13 (this pack's heroes at the density Smolder gets, 1.5 squares a game pixel:
league_galio's hd_idle and the lo_idle of braum, zeri and nidalee at 8x, the same style pictures as
assets/source/bard/style_ref), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground) of the base skin: a small dragon fledgling - an orange-tan
scaly body with a cream belly, a big head with big teal eyes and a toothy grin, a crimson crest with teal fins, two
cream horns with flame-orange tips, folded wings worn like a dark navy-to-crimson cape, dark red forelegs and hind
legs with claws, a long pink-crimson tail. Smolder's model faces image right at yaw 30-80 WITHOUT --mirror; the
submesh VFX_Meshes (flat flame cards on the horns and a stray card behind him) is left out of every render. Version A = League's idle (sitting up on his haunches, wings
folded as a cape), version B = standing on all four legs (League's run stance) - the same dragon. His tail lies on
the ground in League; here it curls up behind him, off the ground (memory tail-off-ground). Side-on comes in step 1.
The look: the user's pick for Smolder, PPU 1.5: horn tips to soles about 51 squares of 12 px (34 game rows).
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
    "1_smolder_league_front": (["Idle2@0"], 30, False, 1000, 0.70, 0.94, 1.6, None),
    "2_smolder_league_frontal": (["Idle2@0"], 10, False, 1000, 0.70, 0.94, 1.6, None),
    "3_smolder_league_head": (["Idle2@0"], 25, False, 2400, 0.80, 0.94, 1.0, (0.25, 0.05, 0.80, 0.45)),
    "4_smolder_league_back": (["Idle2@0"], 160, False, 1000, 0.70, 0.94, 1.6, None),
    "6_smolder_league_run": (["run_collar@0", "run_collar@167", "run_collar@333", "run_collar@500"],
                             70, False, 700, 0.60, 0.94, 1.5, None),
    "7_smolder_league_actions": (["attack_H_1@150", "Spell2_A@250", "Spell3_0@1500", "Spell4_A@200"],
                                 70, False, 800, 0.55, 0.94, 1.6, None),
    "8_smolder_league_stand": (["run_collar@167"], 30, False, 1000, 0.65, 0.94, 1.8, None),
    "9_smolder_league_side": (["Idle2@0"], 80, False, 1000, 0.70, 0.94, 1.6, None),
}
# PPU 1.5 (the user's pick): heroes of this pack at that density, 8x (one square = one dense pixel)
STYLE = {
    "10_style_galio.png": os.path.join(SRC, "bard", "style_ref", "galio_hd_idle_x8.png"),
    "11_style_braum.png": os.path.join(SRC, "bard", "style_ref", "braum_lo_idle_x8.png"),
    "12_style_zeri.png": os.path.join(SRC, "bard", "style_ref", "zeri_lo_idle_x8.png"),
    "13_style_nidalee.png": os.path.join(SRC, "bard", "style_ref", "nidalee_lo_idle_x8.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Smolder",
           "--hq", "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground",
           str(ground), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--hide-submesh", "VFX_Meshes"]
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Smolder.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/smolder/skins/base/smolderloadscreen_0.tex"))
        splash.convert("RGB").save(os.path.join(refs, "5_smolder_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "smolder", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
