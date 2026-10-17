"""Build the step-0 pack for Codex (assets/source/malzahar/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_malzahar_picture.py --out dist/malzahar_packs/malzahar_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/10..13 (this pack's heroes at the density Malzahar gets, 1.5 squares a game pixel:
league_galio's hd_idle and the lo_idle of braum, zeri and nidalee at 8x, assets/source/malzahar/style_ref = bard's), then
<out>.zip. Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right) of the base skin: a lean
void prophet who FLOATS - a magenta hood with glowing pale-blue diamond marks over a shadowed face with two glowing eyes,
a magenta scarf, an open royal-blue robe over a bare chest, lilac-grey metal pauldrons and bracers, big dark gloved
hands, a curved golden-hilted dagger at the belt, puffy blue trousers and pointed dark magenta boots hanging toes-down.
Version A = the user's pick (a long robe covering the legs, its hem floating above the ground), version B = League's own
float (the legs hang below the robe, toes pointing down, never stepping). Side-on comes in step 1 (memory
side-view-design). The look: the user's pick for Malzahar, PPU 1.5: crown to the lowest point about 54 squares of 12 px.
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
    "1_malzahar_league_front": (["Malzahar_Idle1@0"], 30, True, 1000, 0.80, 0.94, 1.0, None),
    "2_malzahar_league_frontal": (["Malzahar_Idle1@0"], 0, True, 1000, 0.80, 0.94, 1.0, None),
    "3_malzahar_league_head": (["Malzahar_Idle1@0"], 25, True, 2400, 0.80, 0.94, 1.0, (0.30, 0.02, 0.72, 0.40)),
    "4_malzahar_league_back": (["Malzahar_Idle1@0"], 160, True, 1000, 0.80, 0.94, 1.0, None),
    "6_malzahar_league_run": (["Malzahar_Run@0", "Malzahar_Run@667", "Malzahar_Run@1333"], 60, True, 800, 0.70, 0.94, 1.2, None),
    "7_malzahar_league_actions": (["Malzahar_Attack1@450", "Malzahar_Spell1@450", "Malzahar_Spell3@400", "Malzahar_Spell4@900"],
                                  60, True, 800, 0.42, 0.95, 1.6, None),
    "8_malzahar_league_hands": (["Malzahar_Idle1@0"], 30, True, 2000, 0.80, 0.94, 1.4, (0.0, 0.18, 1.0, 0.62)),
    "9_malzahar_league_side": (["Malzahar_Idle1@0"], 85, True, 1000, 0.80, 0.94, 1.2, None),
}
# PPU 1.5 (the user's pick): heroes of this pack at that density, 8x (one square = one dense pixel); bard's style_ref
STYLE = {
    "10_style_galio.png": os.path.join(SRC, "malzahar", "style_ref", "galio_hd_idle_x8.png"),
    "11_style_braum.png": os.path.join(SRC, "malzahar", "style_ref", "braum_lo_idle_x8.png"),
    "12_style_zeri.png": os.path.join(SRC, "malzahar", "style_ref", "zeri_lo_idle_x8.png"),
    "13_style_nidalee.png": os.path.join(SRC, "malzahar", "style_ref", "nidalee_lo_idle_x8.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Malzahar",
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
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    os.makedirs(refs, exist_ok=True)
    os.makedirs(style, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Malzahar.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/malzahar/skins/base/malzaharloadscreen.tex"))
        splash.convert("RGB").save(os.path.join(refs, "5_malzahar_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "malzahar", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
