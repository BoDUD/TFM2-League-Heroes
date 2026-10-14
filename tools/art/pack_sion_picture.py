"""Build the step-0 pack for Codex (assets/source/sion/PICTURE_PROMPT.md): League references, style and size guides.

    python tools/art/pack_sion_picture.py --out dist/sion_packs/sion_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders and the loading-screen art: Riot's, kept local, never
committed), <out>/style/10..14 (this pack's 1x heavy heroes' idle at 8x, assets/source/sion/style_ref, and oppi's
cf_sion idle from Workshop 3774304166 at 8x) and <out>/guide/15_size_guide.png (the 1536x1024 canvas on its 18-px grid,
the ground row and Darius / Nautilus drawn square for square beside a free space, for the size only), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right) of the base skin: the undead juggernaut -
pale grey-lilac stitched skin, a small bald head with red glowing eyes and an iron jaw cage with spikes, a red ribbon on a
pin, a huge spiked iron pauldron on the far shoulder, an iron gauntlet, a glowing red furnace in his belly under an iron
belt, brown-and-plum trousers, a short olive loin cloth, iron boots; the great axe (a long leather-wrapped haft, a broad
curved steel blade). Version A = League's idle (the axe hanging in his near hand, blade down beside his near leg),
version B = the same figure with the axe resting on his near shoulder, the blade behind his back.
The look: the user's pick for Sion, 1x frames (no PPU): crown to soles about 44 squares (Darius 42, Nautilus 51).
"""
import argparse
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
sys.path.insert(0, os.path.join(REPO, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pose_ref  # noqa: E402
import tfm2_ase  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
OPPI = r"D:\steam\steamapps\workshop\content\3009300\3774304166\champions\cf_sion.aseprite"
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_sion_league_front": (["Sion_Idle1@0"], 30, True, 1000, 1.15, 0.95, 1.2, None),
    "2_sion_league_frontal": (["Sion_Idle1@0"], 0, True, 1000, 1.15, 0.95, 1.2, None),
    "3_sion_league_head": (["Sion_Idle1@0"], 20, True, 2400, 1.15, 0.95, 1.0, (0.36, 0.06, 0.66, 0.30)),
    "4_sion_league_back": (["Sion_Idle1@0"], 160, True, 1000, 1.15, 0.95, 1.2, None),
    "6_sion_league_run": (["Sion_Run@0", "Sion_Run@300", "Sion_Run@600"], 60, True, 800, 0.9, 0.95, 1.3, None),
    "7_sion_league_actions": (["Sion_Attack1@400", "Sion_Spell1_CHRG@500", "Sion_Spell1_Hit2@200", "Sion_Spell3@300",
                               "Sion_Spell4_Run@200"], 60, True, 700, 0.85, 0.95, 1.5, None),
    "8_sion_league_axe": (["Sion_Spell1_CHRG@500"], 30, True, 1200, 1.0, 0.95, 1.4, None),
    "9_sion_league_side": (["Sion_Idle1@0"], 85, True, 1000, 1.15, 0.95, 1.3, None),
}
# 1x heavy heroes of this pack (the user's pick: 1x frames), first idle frame at 8x
STYLE = {
    "10_style_nautilus.png": os.path.join(SRC, "sion", "style_ref", "nautilus_idle_x8.png"),
    "11_style_alistar.png": os.path.join(SRC, "sion", "style_ref", "alistar_idle_x8.png"),
    "12_style_darius.png": os.path.join(SRC, "sion", "style_ref", "darius_idle_x8.png"),
    "13_style_renekton.png": os.path.join(SRC, "sion", "style_ref", "renekton_idle_x8.png"),
}
SQ = 18                     # canvas px per square (one square = one game pixel)
GRID_W, GRID_H = 1536 // SQ, 1024 // SQ   # 85 x 56
SOLE_ROW = 52               # the soles' square row
CROWN_ROW = SOLE_ROW - 43   # 44 squares crown (top of the bald head) to soles


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Sion",
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


def first_idle(path):
    sp = tfm2_ase.load_sprite(path)
    im = sp.frames[sp.tag_frames("idle")[0]]
    return im.crop(im.getbbox())


def x8(im, pad=2):
    w, h = im.size
    out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    out.paste(im, (pad, pad))
    return out.resize((out.width * 8, out.height * 8), Image.NEAREST)


def size_guide(path):
    """The 1536x1024 canvas: an 18-px grid, the soles row (green) and the crown row (red) marked, Darius (42 rows)
    drawn square for square on the ground at the right edge - the free space on the left is where Sion stands."""
    im = Image.new("RGBA", (1536, 1024), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    for c in range(GRID_W + 1):
        d.line([(c * SQ, 0), (c * SQ, 1024)], fill=(225, 225, 225), width=1)
    for r in range(GRID_H + 1):
        d.line([(0, r * SQ), (1536, r * SQ)], fill=(225, 225, 225), width=1)
    ground = (SOLE_ROW + 1) * SQ
    d.line([(0, ground), (1536, ground)], fill=(40, 160, 40), width=3)
    d.line([(0, CROWN_ROW * SQ), (1536, CROWN_ROW * SQ)], fill=(220, 40, 40), width=3)
    fig = first_idle(os.path.join(REPO, "league", "champions", "league_darius#sheet.png"))
    big = fig.resize((fig.width * SQ, fig.height * SQ), Image.NEAREST)
    im.alpha_composite(big, (1536 - 2 * SQ - big.width, ground - big.height))
    im.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs")
    a = ap.parse_args()
    refs, style, guide = (os.path.join(a.out, k) for k in ("refs", "style", "guide"))
    for p in (refs, style, guide):
        os.makedirs(p, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Sion.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/sion/skins/base/sionloadscreen.tex"))
        splash.convert("RGB").save(os.path.join(refs, "5_sion_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    x8(first_idle(OPPI)).save(os.path.join(style, "14_other_artist_sion.png"))
    size_guide(os.path.join(guide, "15_size_guide.png"))
    shutil.copyfile(os.path.join(SRC, "sion", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
