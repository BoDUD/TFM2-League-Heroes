"""Build the step-0 pack for Codex (assets/source/nilah/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_nilah_picture.py --out dist/nilah_packs/nilah_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/10..12 (this pack's restyled PPU heroes: zeri, nidalee, karma hd_idle at 8x,
assets/source/nilah/style_ref), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right) of the base skin: a joyful melee
fighter with deep brown skin, very long blue-black hair in a low ponytail down to the back of her knees, a bright
yellow one-shouldered top, plum harem trousers wrapped in teal-bronze armour, a purple-teal sash, a caged orb at her
hip, flat black slippers, and the whip-blade: a segmented blade (dark red-purple segments, teal edges) that in the
idle is drawn up into one short straight blade. Version A = League's idle (the blade raised beside her in the back
hand), version B = the same figure with the blade held low and forward in the front hand - a more compact silhouette.
Side-on comes in step 1 (memory side-view-design).
The look: the PPU heroes' one look of 2026-10-13 (league_zeri's: stocky, about 2.2 squares a game pixel, a thick
outline): crown to soles about 84 squares of 8 px.
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
    "1_nilah_league_front": (["Idle1@0"], 30, True, 1000, 0.80, 0.94, 1.0, None),
    "2_nilah_league_frontal": (["Idle1@0"], 0, True, 1000, 0.80, 0.94, 1.0, None),
    "3_nilah_league_head": (["Idle1@0"], 25, True, 2400, 0.80, 0.94, 0.9, (0.30, 0.12, 0.70, 0.45)),
    "4_nilah_league_back": (["Idle1@0"], 160, True, 1000, 0.80, 0.94, 1.0, None),
    "6_nilah_league_run": (["Run@0", "Run@467", "Run@933"], 60, True, 800, 0.70, 0.94, 1.2, None),
    "7_nilah_league_actions": (["Attack1b@222", "Spell1b@167", "Spell3a@117", "Spell4@533"],
                               60, True, 800, 0.55, 0.95, 1.6, None),
    "8_nilah_league_weapon": (["Idle1@0"], 30, True, 2400, 0.80, 0.94, 0.9, (0.18, 0.15, 0.42, 0.50)),
    "9_nilah_league_side": (["Idle1@0"], 85, True, 1000, 0.80, 0.94, 1.0, None),
}
# the 2026-10-13 one look of the PPU heroes (league_zeri's, PR #249 ppu-chunky, tools/art/ppu_restyle.py): their
# restyled hd_idle frames at 8x (one square = one dense pixel), assets/source/nilah/style_ref
STYLE = {
    "10_style_zeri.png": os.path.join(SRC, "nilah", "style_ref", "zeri_hd_idle_x8.png"),
    "11_style_nidalee.png": os.path.join(SRC, "nilah", "style_ref", "nidalee_hd_idle_x8.png"),
    "12_style_karma.png": os.path.join(SRC, "nilah", "style_ref", "karma_hd_idle_x8.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Nilah",
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Nilah.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/nilah/skins/base/nilahloadscreen_0.tex"))
        splash.convert("RGB").save(os.path.join(refs, "5_nilah_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "nilah", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
