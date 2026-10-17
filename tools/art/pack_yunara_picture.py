"""Build the step-0 pack for Codex (assets/source/yunara/PICTURE_PROMPT.md): League references, layout guides and style
pictures.

    python tools/art/pack_yunara_picture.py --out %TEMP%/yu_work/yunara_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..14 (this pack's PPU 1.4-1.5 heroes at their dense frames, 8x, cut
from their sheets), then <out>.zip. Render into a short folder (%TEMP%): pose_ref's saves under yu/dist pass MAX_PATH.
Yunara (the user's picks, 2026-10-17: bot ADC, add-on, R-form idle/run swap, PPU 1.5) is a slim Ionian martial artist:
lilac hair in two braids with golden horn-like ornaments, a navy cropped long-sleeved top, gold bracers, wide lavender
gauze trousers and wooden platform sandals. Eight bronze prayer beads and a violet crystal dragon-head bead (Dragon_Head
+ Tail) float round her; they are separate submeshes coloured by Yunara_Base_Weapon_TX_CM (pose_ref picks the body map
for every submesh unless told). A = League's idle (Idle_1@0, beads round her), B = her attack (attack1@300: the palm
strike, arms spread, the beads arcing over her head), W = the beads alone at A's scale (Body + Pants hidden).
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
IDLE = "Idle_1@0"
SHOT = "attack1@300"
PROPS = ["Dragon_Head", "Tail"] + [f"Bead_{i}" for i in range(1, 9)]
WEAPON = [a for p in PROPS for a in ("--submesh-texture", p + "=Weapon_TX_CM")]
NO_PROPS = [a for p in PROPS for a in ("--hide-submesh", p)]
NO_BODY = ["--hide-submesh", "Body", "--hide-submesh", "Pants"]
# name -> (frame, yaw, size, crop: "box" / (x0, y0, x1, y1) fractions of the full render, extra pose_ref args)
RENDERS = {
    "1_yunara_idle": (IDLE, 45, 1600, "box", WEAPON),
    "2_yunara_frontal": (IDLE, 0, 1600, "box", NO_PROPS),
    "3_yunara_head": (IDLE, 45, 3200, (0.38, 0.19, 0.62, 0.40), NO_PROPS),
    "4_yunara_back": (IDLE, 200, 1600, "box", NO_PROPS),
    "6_yunara_attack": (SHOT, 45, 1600, "box", WEAPON),
    "7_yunara_attack_side": (SHOT, 80, 1600, "box", WEAPON),
    "9_yunara_beads": (IDLE, 45, 1600, "box", WEAPON + NO_BODY),
    "10_yunara_dragon_bead": (IDLE, 45, 3200, "box", WEAPON + NO_BODY + [a for i in range(1, 9) for a in
                                                                        ("--hide-submesh", f"Bead_{i}")]),
}
# crown (hair, not the golden ornaments) to soles BODY_H px (72 squares of 11) on the 1536 square, soles on row SOLE;
# every render shares one camera size (--fit-all), so one scale for A, B and W
BODY_H = 792
SOLE = 1400
GUIDES = {
    "8a_layout_A.png": ("1_yunara_idle.png", "A: League's idle; crown to soles about 792 px (72 squares of 11); layout only"),
    "8b_layout_B.png": ("6_yunara_attack.png", "B: her palm strike; same scale; layout only"),
    "8c_layout_W.png": ("9_yunara_beads.png", "W: the beads alone at A's scale; spread them apart; layout only"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_katarina.png": ("katarina", "hd_idle"),
    "12_style_kalista.png": ("kalista", "hd_idle"),
    "13_style_nilah.png": ("nilah", "hd_idle"),
    "14_style_aphelios.png": ("aphelios", "hd_idle"),
}
FIT, GROUND = 0.62, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, crop, extra = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Yunara",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--fit-all", "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame] + extra
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    if crop == "box":
        x0, y0, x1, y1 = _keyed(path).getbbox()
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    else:
        fx0, fy0, fx1, fy1 = crop
        im = im.crop((round(fx0 * im.width), round(fy0 * im.height), round(fx1 * im.width), round(fy1 * im.height)))
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


def guide(refs, name, spec, k, centre=False):
    """The render scaled by k, its box bottom (the soles) on row SOLE, or centred on the canvas."""
    src, label = spec
    full = _keyed(os.path.join(refs, src))
    fig = full.crop(full.getbbox())
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0 = (1536 - fig.width) // 2
    y0 = (1536 - fig.height) // 2 if centre else SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, max(0, y0)))
    d = ImageDraw.Draw(can)
    if not centre:
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Yunara.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/yunara/skins/base/yunaraloadscreen_0.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_yunara_splash.png"))
    # the scale: the body alone (no beads), golden hair ornaments to soles
    body = _keyed(os.path.join(refs, "2_yunara_frontal.png"))
    k = BODY_H / body.crop(body.getbbox()).height
    # A and B: the soles are the lowest thing drawn (the beads float above them); W is a sheet, centred
    guide(refs, "8a_layout_A.png", GUIDES["8a_layout_A.png"], k)
    guide(refs, "8b_layout_B.png", GUIDES["8b_layout_B.png"], k)
    guide(refs, "8c_layout_W.png", GUIDES["8c_layout_W.png"], k, centre=True)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "yunara", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
