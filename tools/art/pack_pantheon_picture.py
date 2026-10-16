"""Build the step-0 pack for Codex (assets/source/pantheon/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_pantheon_picture.py --out %TEMP%/pn_work/pantheon_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guides pasted
from renders: Riot's, kept local, never committed) and <out>/style/9..12 (this pack's armoured heroes at their dense
frames, 8x: league_galio's hd_idle and league_braum's lo_idle from assets/source/bard/style_ref, league_garen's and
league_elise's hd_idle cut from their sheets), then <out>.zip. Render into a short folder (%TEMP%): pose_ref's saves
under pn/dist pass MAX_PATH.
Pantheon (the user's picks, 2026-10-16: top, add-on, PPU 1.5) is drawn as two pictures on 1536x1536 squares (the
spear, the shield and the cape reach far out): A = League's idle (Pantheon_Idle1: the spear held low in the near hand,
its blade forward and down, the round shield on the far arm, the cape flying back) and B = Comet Spear's wind-up
(Pantheon_spell1_nomove at 1000 ms: the spear raised over his shoulder to throw, the shield held out before him).
Helmet top to soles about 76 squares of 11 px (~42 game rows at 1.8 squares a game pixel; read back and brought to
PPU 1.5 by the restyle). The skin hides its spear, shield, cape and both heads until an animation shows them: the
renders hide the comet, recall and joke props, the bare head and the one-armed variant instead (HIDE), the cape takes
its own map.
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
IDLE = "Pantheon_Idle1@0"
THROW = "Pantheon_spell1_nomove@1000"
HIDE = ["Recall", "Comet", "Joke", "L_Arm_Only", "Head", "HeadHelmet"]
# name -> (frames, yaw, size, fit, ground, width, crop: "box" / fractions of the figure's box)
RENDERS = {
    "1_pantheon_idle": ([IDLE], 45, 1000, 0.60, 0.80, 1.6, "box"),
    "2_pantheon_frontal": ([IDLE], 0, 1000, 0.60, 0.80, 1.6, "box"),
    "3_pantheon_head": ([IDLE], 40, 2400, 0.60, 0.80, 1.6, "head"),
    "4_pantheon_back": ([IDLE], 200, 1000, 0.60, 0.80, 1.6, "box"),
    "6_pantheon_throw": ([THROW], 45, 1000, 0.60, 0.80, 1.6, "box"),
    "7_pantheon_throw_side": ([THROW], 80, 1000, 0.60, 0.80, 1.6, "box"),
}
# the layout guides: the render's helmet top to soles HELM_H px (76 squares of 11) on the 1536 square, soles on row
# SOLE, centred; the throw is scaled like the idle (one size for both)
HELM_H = 836
SOLE = 1390
GUIDES = {
    "8a_layout_A.png": ("1_pantheon_idle.png", "A: League's idle; helmet top to soles 836 px (76 squares of 11); layout only"),
    "8b_layout_B.png": ("6_pantheon_throw.png", "B: the spear raised to throw; same scale; layout only"),
}
STYLE = {
    "9_style_galio.png": os.path.join(SRC, "bard", "style_ref", "galio_hd_idle_x8.png"),
    "10_style_braum.png": os.path.join(SRC, "bard", "style_ref", "braum_lo_idle_x8.png"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_garen.png": ("garen", "hd_idle"),
    "12_style_elise.png": ("elise", "hd_idle"),
}


def render(lol, name, spec, out):
    frames, yaw, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Pantheon",
           "--submesh-texture", "Cape=Cape_TX", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out]
    for s in HIDE:
        cmd += ["--hide-submesh", s]
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    key = _keyed(path)
    x0, y0, x1, y1 = key.getbbox()
    if crop == "head":  # the helmet: the top of the body, the columns round the helmet's crest
        band = key.crop((0, y0, key.width, y0 + (y1 - y0) // 10))
        bx0, _, bx1, _ = band.getbbox()
        cx, s = (bx0 + bx1) // 2, (y1 - y0) // 5
        im.crop((max(0, cx - s), max(0, y0 - s // 8), min(im.width, cx + s), y0 + s + s // 4)).save(path)
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


def helm_height(fig):
    """Helmet top to soles of a keyed figure: the topmost row whose drawn run is wider than a crest spike (the crest
    rises a little above the helmet) down to the lowest drawn row."""
    a = fig.split()[3].load()
    for y in range(fig.height):
        n = sum(1 for x in range(fig.width) if a[x, y])
        if n > fig.width // 40:
            return fig.height - y
    return fig.height


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Pantheon.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/pantheon/skins/base/pantheonloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(
            os.path.join(refs, "5_pantheon_splash.png"))
    idle = _keyed(os.path.join(refs, "1_pantheon_idle.png"))
    k = HELM_H / helm_height(idle.crop(idle.getbbox()))
    for name, spec in GUIDES.items():
        guide(refs, name, spec, k)
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "pantheon", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
