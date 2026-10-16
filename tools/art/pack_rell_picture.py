"""Build the step-0 pack for Codex (assets/source/rell/PICTURE_PROMPT.md): League references, layout guides and style
pictures.

    python tools/art/pack_rell_picture.py --out %TEMP%/rl_work/rell_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders, the loading-screen art and the layout guides pasted
from renders: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's heroes at 8x: league_pantheon's
and league_katarina's hd_idle at PPU 1.5, league_kalista's hd_idle, league_hecarim's idle for a horse body at game
size), then <out>.zip. Render into a short folder (%TEMP%): pose_ref's saves under rl/dist pass MAX_PATH.
Rell is drawn as two pictures on 1536x1536 squares, at one scale: A = mounted (League's Idle: her iron horse, the
lance held level) and B = dismounted (Biped_Idle: the horse's metal worn as heavy armour, the lance in her hand). Her
mesh carries both looks: mounted renders hide the Armor_* submeshes and the joke horse, dismounted ones the Horse_*
submeshes and the joke horse; the horse and the lance have their own textures (--submesh-texture). Hair top to the
hooves of A about 72 squares of 11 px; B at the same scale.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
MOUNTED = "Idle@0"
BIPED = "Biped_Idle@0"
HORSE = ["Horse_Tail", "Horse_Backlegs", "Horse_Head", "Horse_Midsection", "Horse_FrontLegs", "Horse_Rear",
         "Horse_Saddle"]
ARMOUR = ["Armor_Chest", "Armor_Shoulder", "Armor_Foot", "Armor_Gauntlet", "Armor_Leg_Lower", "Armor_Leg_Mid",
          "Armor_Leg"]
JOKE = ["JokeHorsie", "JokeHorsie_Stand"]
TEX = [f"{s}=Rell_Base_Horse_TX_CM" for s in HORSE] + ["Lance=Rell_Lance_TX_CM", "LanceMetal=Rell_Lance_TX_CM"]
# name -> (frames, yaw, size, fit, ground, width, crop: "box" / "head", form: "m" mounted / "b" dismounted)
RENDERS = {
    "1_rell_mounted": ([MOUNTED], 45, 1000, 0.55, 0.85, 1.7, "box", "m"),
    "2_rell_mounted_front": ([MOUNTED], 0, 1000, 0.55, 0.85, 1.7, "box", "m"),
    "3_rell_mounted_back": ([MOUNTED], 215, 1000, 0.55, 0.85, 1.7, "box", "m"),
    "4_rell_head": ([BIPED], 25, 2400, 0.60, 0.85, 1.0, "head", "b"),
    "6_rell_dismounted": ([BIPED], 55, 1000, 0.60, 0.85, 1.2, "box", "b"),
    "7_rell_dismounted_front": ([BIPED], 0, 1000, 0.60, 0.85, 1.2, "box", "b"),
}
# the layout guides: A's hair top to hooves FIG_H px (72 squares of 11) on the 1536 square, soles on row SOLE, centred;
# B is scaled like A (one size for both: the same woman)
FIG_H = 792
SOLE = 1390
GUIDES = {
    "8a_layout_A.png": ("1_rell_mounted.png", "A: mounted (League's idle); hair top to hooves 792 px (72 squares of 11); layout only"),
    "8b_layout_B.png": ("6_rell_dismounted.png", "B: dismounted, same scale as A; layout only"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "10_style_pantheon.png": ("pantheon", "hd_idle"),
    "11_style_katarina.png": ("katarina", "hd_idle"),
    "12_style_kalista.png": ("kalista", "hd_idle"),
    "13_style_hecarim.png": ("hecarim", "idle"),
}


def render(lol, name, spec, out):
    frames, yaw, size, fit, ground, width, crop, form = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Rell",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--fit-all"]
    for s in JOKE + (ARMOUR if form == "m" else HORSE):
        cmd += ["--hide-submesh", s]
    for t in TEX:
        cmd += ["--submesh-texture", t]
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    key = _keyed(path)
    x0, y0, x1, y1 = key.getbbox()
    if crop == "head":  # the head: the top of the figure, round the hair's columns
        band = key.crop((0, y0, key.width, y0 + (y1 - y0) // 10))
        bx0, _, bx1, _ = band.getbbox()
        cx, s = (bx0 + bx1) // 2, (y1 - y0) // 7
        im.crop((max(0, cx - s), max(0, y0 - s // 8), min(im.width, cx + s), y0 + s + s // 2)).save(path)
    else:
        m = max(x1 - x0, y1 - y0) // 12
        im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m))).save(path)
    print(name, Image.open(path).size)


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if abs(r - GREY[0]) + abs(g - GREY[1]) + abs(b - GREY[2]) < 12:
                px[x, y] = (0, 0, 0, 0)
    return im


def guide(refs, name, spec, k):
    src, label = spec
    full = _keyed(os.path.join(refs, src))
    fig = full.crop(full.getbbox())
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0 = (1536 - fig.width) // 2
    y0 = SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, name))
    print(name, "figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


def cut(hero, tag, out):
    """Frame 0 of a sheet tag at 8x (one square = one pixel of that tag's density)."""
    anims = json.load(open(os.path.join(CHAMPS, f"league_{hero}#anim.fanim"), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(os.path.join(CHAMPS, f"league_{hero}#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))   # on grey like the other style pictures
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(out)
    print(os.path.basename(out), pad.size)


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Rell.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/rell/skins/base/rellloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(
            os.path.join(refs, "5_rell_splash.png"))
    mounted = _keyed(os.path.join(refs, "1_rell_mounted.png"))
    k = FIG_H / mounted.crop(mounted.getbbox()).height
    # B at A's scale: both renders came out of pose_ref at their own fit, so bring B to A's pixels per model unit
    # (fit x size / bind height is the same model for both: the ratio of their fit x size)
    kb = k * (RENDERS["1_rell_mounted"][3] * RENDERS["1_rell_mounted"][2]) / \
        (RENDERS["6_rell_dismounted"][3] * RENDERS["6_rell_dismounted"][2])
    guide(refs, "8a_layout_A.png", GUIDES["8a_layout_A.png"], k)
    guide(refs, "8b_layout_B.png", GUIDES["8b_layout_B.png"], kb)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "rell", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
