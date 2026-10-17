"""Build the step-0 pack for Codex (assets/source/anivia/PICTURE_PROMPT.md): League references, layout guides and style
pictures.

    python tools/art/pack_anivia_picture.py --out C:/t/av_work/anivia_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..14 (this pack's heroes at their dense frames, 8x, cut from their
sheets), then <out>.zip. Render into a short folder.
Anivia (the user's picks, 2026-10-17: mid, W folded into Q, add-on with the real egg / real wall / per-target Iced mark,
PPU 1.2 - 「全按推荐」) is the Cryophoenix: a big bird of blue ice-crystal feathers, a crest of ice spikes, magenta eyes,
dark-blue talons. Both pictures are needed (not a pick): A = League's idle (anivia_idle1), B = her Rebirth egg
(League's own AniviaEgg model: a frosted egg sitting in a ring of ice crystals) for the passive. League hovers her
34 units over the ground; here her lowest feather touches the ground line (a hovering sprite sits too high in the
collection screen, the Nami lesson). Crest to lowest feather about 64 squares of 11 px (A); the egg on its nest about
0.55 of that (B), the same squares.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
IDLE = "anivia_idle1@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / (x0, y0, x1, y1) fractions of the figure's box)
RENDERS = {
    "1_anivia_idle": ("Anivia", IDLE, 25, 1600, 1.8, "box"),
    "2_anivia_frontal": ("Anivia", IDLE, 0, 1600, 1.8, "box"),
    "3_anivia_head": ("Anivia", IDLE, 25, 4000, 1.8, (0.30, 0.0, 0.70, 0.55)),
    "4_anivia_back": ("Anivia", IDLE, 205, 1600, 1.8, "box"),
    "6_anivia_flight": ("Anivia", "anivia_run@300", 25, 1600, 1.8, "box"),
    "7_anivia_q_cast": ("Anivia", "anivia_spell1@250", 25, 1600, 1.8, "box"),
    "8_anivia_egg": ("AniviaEgg", "RebirthEgg_Idle1@0", 25, 1400, 1.3, "box"),
    "9_anivia_egg_side": ("AniviaEgg", "RebirthEgg_Idle1@0", 90, 1400, 1.3, "box"),
}
# crest top to the lowest feather A_H px (64 squares of 11) on the 1536 square, the lowest feather on row SOLE
A_H = 704
B_SHARE = 0.55
SOLE = 1390
GUIDES = {
    "10a_layout_A.png": ("1_anivia_idle.png", "A: League's idle; crest to the lowest feather 704 px (64 squares of 11), "
                         "the lowest feather ON the ground line; layout only", 1.0),
    "10b_layout_B.png": ("8_anivia_egg.png", "B: the Rebirth egg on its ice nest, the SAME squares: ~387 px tall "
                         "(~35 squares); layout only", B_SHARE),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_tahmkench.png": ("tahmkench", "hd_idle"),
    "12_style_nasus.png": ("nasus", "hd_idle"),
    "13_style_swain.png": ("swain", "hd_idle"),
    "14_style_lissandra.png": ("lissandra", "idle"),
}
FIT, GROUND = 0.62, 0.84


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Anivia", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size),
           "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name,
           "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    else:
        fx0, fy0, fx1, fy1 = crop
        w, h = x1 - x0, y1 - y0
        im = im.crop((round(x0 + fx0 * w), round(y0 + fy0 * h), round(x0 + fx1 * w), round(y0 + fy1 * h)))
    im.save(path)
    print(name, im.size)
    return path


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def guide(refs, name, spec):
    src, label, share = spec
    full = _keyed(os.path.join(refs, src))
    fig = full.crop(full.getbbox())
    k = A_H * share / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0 = (1536 - fig.width) // 2
    y0 = SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, max(0, y0)))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, y0), (1536, y0)], fill=(190, 190, 190, 255), width=1)
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Anivia.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/anivia/skins/base/anivialoadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_anivia_splash.png"))
    for name, spec in GUIDES.items():
        guide(refs, name, spec)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "anivia", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
