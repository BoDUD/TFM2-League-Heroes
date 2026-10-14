"""Build the step-0 pack for Codex (assets/source/bard/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_bard_picture.py --out dist/bard_packs/bard_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/10..13 (this pack's PPU heroes at the density Bard gets, 1.5 squares a game pixel:
league_galio's hd_idle and the lo_idle of zeri, nidalee and braum at 8x, assets/source/bard/style_ref), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right) of the base skin: a big gentle
wanderer with a pale green mane round a small bronze mask (three glowing golden holes), sage-green skin, a red tabard,
maroon trousers on short iron peg feet, and his instrument: a long curved ivory horn wrapped in leather bands, small
golden bells under it, a golden bell-mouth with a glowing teal orb at one end. Version A = League's idle (the
instrument over his near shoulder), version B = the same figure with the instrument held low in the near hand, the
horn hanging down beside his leg - a more compact silhouette. Side-on comes in step 1 (memory side-view-design).
The look: the user's pick for Bard, PPU 1.5 (league_galio's way): crown to soles about 60 squares of 12 px.
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
    "1_bard_league_front": (["Bard_Idle01@0"], 30, True, 1000, 0.80, 0.94, 1.0, None),
    "2_bard_league_frontal": (["Bard_Idle01@0"], 0, True, 1000, 0.80, 0.94, 1.0, None),
    "3_bard_league_head": (["Bard_Idle01@0"], 25, True, 2400, 0.80, 0.94, 1.0, (0.30, 0.10, 0.75, 0.45)),
    "4_bard_league_back": (["Bard_Idle01@0"], 160, True, 1000, 0.80, 0.94, 1.0, None),
    "6_bard_league_run": (["Bard_Run01@0", "Bard_Run01@358", "Bard_Run01@717"], 60, True, 800, 0.70, 0.94, 1.2, None),
    "7_bard_league_actions": (["Bard_Attack01@700", "Bard_Spell1@317", "Bard_Spell3@467", "Bard_Spell4@375"],
                              60, True, 800, 0.42, 0.95, 1.6, None),
    "8_bard_league_instrument": (["Bard_Idle01@0"], 70, True, 2000, 0.80, 0.94, 1.4, (0.0, 0.05, 1.0, 0.45)),
    "9_bard_league_side": (["Bard_Idle01@0"], 85, True, 1000, 0.80, 0.94, 1.2, None),
}
# PPU 1.5 (the user's pick, league_galio's way): heroes of this pack at that density, 8x (one square = one dense pixel)
STYLE = {
    "10_style_galio.png": os.path.join(SRC, "bard", "style_ref", "galio_hd_idle_x8.png"),
    "11_style_braum.png": os.path.join(SRC, "bard", "style_ref", "braum_lo_idle_x8.png"),
    "12_style_zeri.png": os.path.join(SRC, "bard", "style_ref", "zeri_lo_idle_x8.png"),
    "13_style_nidalee.png": os.path.join(SRC, "bard", "style_ref", "nidalee_lo_idle_x8.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Bard",
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Bard.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/bard/skins/base/bardloadscreen.tex"))
        splash.convert("RGB").save(os.path.join(refs, "5_bard_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "bard", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
