"""Build the step-0 pack for Codex (assets/source/reksai/PICTURE_PROMPT.md): League references, layout guides and style
pictures.

    python tools/art/pack_reksai_picture.py --out %TEMP%/rk_work/reksai_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..14 (this pack's PPU 1.5-1.8 creatures at their dense frames, 8x, cut
from their sheets, + Kha'Zix at 1x for the Void colours), then <out>.zip. Render into a short folder (%TEMP%).
Rek'Sai (the user's picks, 2026-10-17: jungle, add-on, PPU 1.5) is a blind Void burrower: a crouched armoured beast on
four clawed limbs, a magenta fin crest on her back, a long spiked tail. Both pictures are needed (not a pick): A = League's
idle on the surface (RekSai_idle01), B = burrowed (RekSai_idle01_burrowed: crest, back and head out of a dirt mound) for
the add-on's underground body and the dive casts. Crest top to claw tips about 66 squares of 11 px; B on the same scale.
One submesh, one colour map (RekSai_Base_TX_CM).
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
IDLE = "RekSai_idle01@0"
BUR = "RekSai_idle01_burrowed@0"
# name -> (frame, yaw, size, crop: "box" / (x0, y0, x1, y1) fractions of the figure's box)
RENDERS = {
    "1_reksai_idle": (IDLE, 45, 1600, "box"),
    "2_reksai_frontal": (IDLE, 0, 1600, "box"),
    "3_reksai_head": (IDLE, 40, 3200, (0.62, 0.18, 1.0, 0.66)),
    "4_reksai_back": (IDLE, 200, 1600, "box"),
    "6_reksai_burrowed": (BUR, 45, 1600, "box"),
    "7_reksai_burrowed_side": (BUR, 80, 1600, "box"),
    "9_reksai_claws": (IDLE, 45, 3200, (0.15, 0.55, 1.0, 1.0)),
}
# crest top to claw tips CREST_H px (66 squares of 11) on the 1536 square, claw tips on row SOLE, centred; the burrowed
# pose is scaled like the idle (one size for both)
CREST_H = 726
SOLE = 1400
GUIDES = {
    "8a_layout_A.png": ("1_reksai_idle.png", "A: League's idle; crest top to claw tips 726 px (66 squares of 11); layout only"),
    "8b_layout_B.png": ("6_reksai_burrowed.png", "B: burrowed; same scale; the grey line = the ground; layout only"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_smolder.png": ("smolder", "hd_idle"),
    "12_style_rell.png": ("rell", "hd_idle"),
    "13_style_elise_spider.png": ("elise", "hd_c_idle"),
    "14_style_khazix.png": ("khazix", "idle"),
}
SIZE_W = 1.8    # cell width as a fraction of the size: her tail makes her much wider than tall
FIT, GROUND = 0.62, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "RekSai",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(SIZE_W), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    if frame == BUR:   # burrowed: what lies under the ground line is underground - not drawn
        g = round(size * GROUND)
        ImageDraw.Draw(im).rectangle((0, g, im.width, im.height), fill=GREY)
        im.save(path)
    if crop == "box":
        x0, y0, x1, y1 = _keyed(path).getbbox()
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    else:   # fractions of the figure's box (her cell is much wider than she is)
        x0, y0, x1, y1 = _keyed(path).getbbox()
        fx0, fy0, fx1, fy1 = crop
        w, h = x1 - x0, y1 - y0
        im = im.crop((round(x0 + fx0 * w), round(y0 + fy0 * h), round(x0 + fx1 * w), round(y0 + fy1 * h)))
    im.save(path)
    print(name, im.size)
    return path


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
    can.alpha_composite(fig, (x0, max(0, y0)))
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
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "RekSai.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/reksai/skins/base/reksailoadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_reksai_splash.png"))
    idle = _keyed(os.path.join(refs, "1_reksai_idle.png"))
    k = CREST_H / idle.crop(idle.getbbox()).height
    for name, spec in GUIDES.items():
        guide(refs, name, spec, k)  # same camera size, so one scale for both
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "reksai", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
