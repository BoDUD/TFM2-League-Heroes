"""Build the step-0 pack for Codex (assets/source/powder/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_powder_picture.py --out %TEMP%/pw_work/powder_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (renders of TFT's own model and its HUD icon and the layout guides:
Riot's, kept local, never committed) and <out>/style/11..13 (this repo's Zoe, Poppy and Jinx, 8x, cut from their
sheets), then <out>.zip. Render into a short folder (%TEMP%).
Powder (the tft pack's first hero, 2026-10-19) is young Jinx from Arcane, a unit of Teamfight Tactics set 13 (Into the
Arcane). League has no Powder, but the League client carries TFT's units: her model is TFT13_Blue in
Game/DATA/FINAL/TFTSet13.wad.client (Violet is TFT13_Red), with clips Idle, Run, attack_1, attack_2, Spell, Death,
Celebration; pose_ref.py reads it with --wad-file. Its skin holds two prop submeshes (Bomb, Monkey) parked in her idle:
every render hides them. The look: a small girl, bright blue hair in a short messy bob with two thin braids hanging
behind, two big gold X-shaped hair clips (crossed bolts) on top, big blue-grey eyes, a teal tunic with short pink sleeves
over a pink shirt, dark brown fingerless arm wraps, a brown belt with a pouch of glowing blue bombs on her hip, purple
striped tights, brown laced boots. Two pictures of the same Powder: A = TFT's idle (3/4 front facing right, one hand
held out, the other at her chest), B = the same Powder standing straight, arms hanging at her sides (the base the
actions are posed from). Crown to soles about 60 squares of 11 px. Her yaw: 40 (mirrored) is the 3/4 view, 0 the
front, 90 the side.
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
WAD = "TFTSet13.wad.client"
CHAMP = "TFT13_Blue"
IDLE = "Idle@0"
PROPS = ["Bomb", "Monkey"]
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_powder_idle": (IDLE, 40, 1600, 1.0, "box"),
    "2_powder_frontal": (IDLE, 0, 1600, 1.0, "box"),
    "3_powder_head": (IDLE, 40, 3200, 1.0, "head"),
    "4_powder_back": (IDLE, 180, 1600, 1.0, "box"),
    "6_powder_head_front": (IDLE, 0, 3200, 1.0, "head"),
    "7_powder_side": (IDLE, 90, 1600, 1.0, "box"),
    "full_idle": (IDLE, 40, 1600, 1.0, "none"),
}
# crown to soles BODY_H px (60 squares of 11) on the 1536 square, soles on row SOLE, centred
BODY_H = 660
SOLE = 1390
GUIDES = {
    "8a_layout_A.png": "A: TFT's idle; crown to soles 660 px (60 squares of 11); layout only",
    "8b_layout_B.png": "B: same size and ground line; she STANDS STRAIGHT, arms down (see the text); size only",
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_zoe.png": ("zoe", "hd_idle"),
    "12_style_poppy.png": ("poppy", "hd_idle"),
    "13_style_jinx.png": ("jinx", "idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", CHAMP,
           "--wad-file", WAD, *[x for p in PROPS for x in ("--hide-submesh", p)],
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the hair clips, the face and the braids: the top 30% of the figure
        h = y1 - y0
        hx0, _, hx1, _ = _keyed(path).crop((0, y0, im.width, y0 + round(h * 0.30))).getbbox()
        m = (hx1 - hx0) // 8
        im = im.crop((hx0 - m, max(0, y0 - m), hx1 + m, y0 + round(h * 0.30)))
    elif crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    im.save(path)
    print(name, im.size)
    return path


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def guide(src, name, label, fade=False):
    """The whole figure scaled so crown to soles is BODY_H, soles on SOLE, centred (B: faded - size only)."""
    full = _keyed(src)
    fig = full.crop(full.getbbox())
    k = BODY_H / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    if fade:
        a = np.asarray(fig).copy()
        a[..., 3] = (a[..., 3] * 0.35).astype(np.uint8)
        fig = Image.fromarray(a)
    x0, y0 = round(768 - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - BODY_H), (1536, SOLE - BODY_H)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


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
    refs, style, work = os.path.join(a.out, "refs"), os.path.join(a.out, "style"), a.out + "_measure"
    for d in (refs, style, work):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, work if name.startswith("full_") else refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", WAD))
        icon = pose_ref.read_tex(wad.read_path("assets/characters/tft13_blue/hud/tft13_blue_square.tex")).convert("RGB")
        icon.resize((icon.width * 4, icon.height * 4), Image.LANCZOS).save(os.path.join(refs, "5_powder_icon.png"))
    full = os.path.join(work, "full_idle.png")
    for i, (name, label) in enumerate(GUIDES.items()):
        guide(full, os.path.join(refs, name), label, fade=i == 1)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "powder", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
