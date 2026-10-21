"""Build the step-0 pack for Codex (assets/source/heimerdinger/PICTURE_PROMPT.md): League references of Heimerdinger and
his two turrets, layout guides and style pictures.

    python tools/art/pack_heimerdinger_picture.py --out C:/t/hd_work/heimerdinger_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders of Heimerdinger and his turrets, the loading-screen art)
and <out>/refs/10a..10d (layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this pack's Ziggs,
Corki, Poppy and Jayce's cannon, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Heimerdinger (group F bot stand-in, 2026-10-21) is the Revered Inventor, a yordle professor:
  a huge spiky mane of golden-yellow hair swept back, big pointed orange ears, red-rimmed goggles with glowing cyan
  lenses, a bushy white moustache and beard, a magnifying monocle on a stalk over his hair; a dark green-grey academy
  coat with a brass belt buckle, black boots; an orange hextech multitool in one hand and a green wrench in the other.
  Turret (H-28G Evolution Turret, Q) - a small grey cannon box on a short tripod, a pale green gear on its back, a red
  muzzle ring, a red knob on a stalk; in the WAD it is the character HeimerTBlue (clips HeimerTurret_Mega_*).
  Apex turret (UPGRADE!!! Q) - a big grey block on four splayed red-footed legs, two pale green exhaust stacks, a big red
  muzzle; the character HeimerTYellow (clips HeimerTurret_*). The names cross the looks: the renders decide.
Four pictures: A = his idle 3/4 front facing right, SA = his side-on facing right, T = the turret from the front, X = the
apex turret from the front. The turrets stand in the game as effect pictures, which the client never mirrors (the skill's
rule "the client never mirrors an effect picture"): a turret seen from the front (the muzzle toward the viewer) looks
right on both sides. Heimerdinger about 36 squares of 11 px from the hair's top to the soles, the turret about 20, the
apex turret about 30 (the same square size). Yaw 0 front, 35 the 3/4 view, 75 the side.
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
HERO, TUR, APEX = "heimerdinger_base_idle1@0", "heimerturret_mega_idle1@0", "heimerturret_idle1@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_heimer_idle": ("Heimerdinger", HERO, 35, 1600, 1.4, "box"),
    "2_heimer_frontal": ("Heimerdinger", HERO, 0, 1600, 1.4, "box"),
    "3_heimer_head": ("Heimerdinger", HERO, 35, 3200, 1.4, "head"),
    "4_heimer_side": ("Heimerdinger", HERO, 75, 1600, 1.4, "box"),
    "5_turret_34": ("HeimerTBlue", TUR, 35, 1600, 1.2, "box"),
    "6_turret_front": ("HeimerTBlue", TUR, 0, 1600, 1.2, "box"),
    "7_apex_34": ("HeimerTYellow", APEX, 35, 1600, 1.2, "box"),
    "8_apex_front": ("HeimerTYellow", APEX, 0, 1600, 1.2, "box"),
    "full_heimer": ("Heimerdinger", HERO, 35, 1600, 1.4, "none"),
    "full_heimer_side": ("Heimerdinger", HERO, 75, 1600, 1.4, "none"),
    "full_turret": ("HeimerTBlue", TUR, 0, 1600, 1.2, "none"),
    "full_apex": ("HeimerTYellow", APEX, 0, 1600, 1.2, "none"),
}
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, squares tall, label)
    "10a_layout_heimer.png": ("full_heimer", 36, "A: Heimerdinger's idle, 3/4 front; hair top to soles 396 px (36 squares of 11)"),
    "10b_layout_heimer_side.png": ("full_heimer_side", 36, "SA: Heimerdinger from the side, facing right; same size and ground"),
    "10c_layout_turret.png": ("full_turret", 20, "T: the turret from the front; top to feet 220 px (20 squares of 11)"),
    "10d_layout_apex.png": ("full_apex", 30, "X: the apex turret from the front; top to feet 330 px (30 squares of 11)"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_ziggs.png": ("ziggs", "hd_idle"),
    "12_style_corki.png": ("corki", "hd_idle"),
    "13_style_poppy.png": ("poppy", "hd_idle"),
    "14_style_jayce_cannon.png": ("jayce", "hd_c_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Heimerdinger", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the big mane and the goggles: the upper 62% of him, the tools left out
        w, h = x1 - x0, y1 - y0
        im = im.crop((x0 + w // 12, max(0, y0 - h // 30), x1 - w // 12, y0 + round(h * 0.62)))
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


def guide(src, name, squares, label):
    """The whole figure scaled so its top to its soles is `squares` x SQ px, soles on SOLE, centred on CX."""
    full = _keyed(src)
    fig = full.crop(full.getbbox())
    k = squares * SQ / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0, y0 = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - squares * SQ), (1536, SOLE - squares * SQ)], fill=(190, 190, 190, 255), width=1)
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Heimerdinger.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/heimerdinger/skins/base/heimerdingerloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "9_heimer_splash.png"))
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "heimerdinger", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
