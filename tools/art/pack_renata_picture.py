"""Build the step-0 pack for Codex (assets/source/renata/PICTURE_PROMPT.md): League references, layout guides and style
pictures.

    python tools/art/pack_renata_picture.py --out %TEMP%/rn_work/renata_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..14 (this pack's PPU 1.5 heroes at their dense frames, 8x, cut from
their sheets), then <out>.zip. Render into a short folder (%TEMP%): pose_ref's saves under rn/dist pass MAX_PATH.
Renata Glasc (the user's picks, 2026-10-17: support, Util, add-on, PPU 1.5) is a tall chem-baroness: long black-violet
hair with a silver streak, a silver respirator mask over mouth and nose, a white cape-jacket over the shoulders with
gold trim and grey ornament, a dark navy vest with gold clasps, a magenta shirt and tie, white high-waisted flared
trousers with buttons, black ankle boots with gold toes and heels, a GOLD-AND-MAGENTA MECHANICAL RIGHT ARM (the near
arm of a right-facing sprite) with claw fingers, a dark pistol in the black-gloved far hand. The skin hides Q_Arm,
Q_Arm_Tubes, Recall_Jacket, Wing_Folded and Wing until a spell shows them; Weapon / Weapon_Glass / Canisters /
Canister_Glass are the chemtech machine on her back that only R (Spell4) unfolds (the idle leaves it in the bind pose
over her head). A = Weapon_Idle1@0 (pistol raised by her shoulder), B = Attack1@200 (the shot, arm stretched),
C = Spell4@889 (R: the far arm raised, the machine with its blade-wings and cape spread behind her).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
IDLE = "Weapon_Idle1@0"
SHOT = "Attack1@200"
ULT = "Spell4@889"
SPELL_PARTS = ["Recall_Jacket", "Pocket", "Potion", "Q_Arm", "Q_Arm_Tubes", "Wing_Folded"]
MACHINE = ["Wing", "Weapon", "Weapon_Glass", "Canisters", "Canister_Glass"]
BODY = ["Body", "Arm", "Jacket", "Gun"]
hide = lambda names: [a for n in names for a in ("--hide-submesh", n)]
BASE = hide(SPELL_PARTS + MACHINE)
R_ALL = hide(SPELL_PARTS)
R_MACHINE = hide(SPELL_PARTS + BODY)
# name -> (frame, yaw, size, crop: "box" / (x0, y0, x1, y1) fractions of the full render, extra pose_ref args)
RENDERS = {
    "1_renata_idle": (IDLE, 45, 1600, "box", BASE),
    "2_renata_frontal": (IDLE, 0, 1600, "box", BASE),
    "3_renata_head": (IDLE, 45, 3200, "head", BASE),
    "4_renata_back": (IDLE, 200, 1600, "box", BASE),
    "6_renata_attack": (SHOT, 45, 1600, "box", BASE),
    "7_renata_attack_side": (SHOT, 80, 1600, "box", BASE),
    "9_renata_ult": (ULT, 45, 1600, "box", R_ALL),
    "10_renata_ult_machine": (ULT, 45, 1600, "box", R_MACHINE),
    "ult_body": (ULT, 45, 1600, None, BASE),   # only for the guide: where her own soles are in C
}
# hair top to soles BODY_H px (72 squares of 11) on the 1536 square, soles on row SOLE; every render shares one camera
# size (--fit-all), so one scale for A, B and C
BODY_H = 792
SOLE = 1400
GUIDES = {
    "8a_layout_A.png": ("1_renata_idle.png", "A: League's idle, pistol up; hair top to soles about 792 px (72 squares of 11); layout only"),
    "8b_layout_B.png": ("6_renata_attack.png", "B: the shot; same scale; layout only"),
    "8c_layout_C.png": ("raw/9_renata_ult.png", "C: Hostile Takeover, the machine behind her; same scale; layout only"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_katarina.png": ("katarina", "hd_idle"),
    "12_style_kalista.png": ("kalista", "hd_idle"),
    "13_style_yunara.png": ("yunara", "hd_idle"),
    "14_style_aphelios.png": ("aphelios", "hd_idle"),
}
FIT, GROUND = 0.62, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, crop, extra = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Renata",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--fit-all", "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame] + extra
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    raw = os.path.join(os.path.dirname(out), "raw")
    os.makedirs(raw, exist_ok=True)
    shutil.copyfile(path, os.path.join(raw, name + ".png"))
    if crop is None:
        os.remove(path)
        return None
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    elif crop == "head":   # the top fifth of the figure, a square round the head
        h = (y1 - y0) // 8
        cx = _head_x(_keyed(path), y0, h, x0 + (x1 - x0) * 0.55)
        im = im.crop((cx - h, y0 - h // 4, cx + h, y0 + 2 * h - h // 4))
    else:
        fx0, fy0, fx1, fy1 = crop
        im = im.crop((round(fx0 * im.width), round(fy0 * im.height), round(fx1 * im.width), round(fy1 * im.height)))
    im.save(path)
    print(name, im.size)
    return path


def _head_x(keyed, y0, h, right):
    """Centre column of the drawn pixels in the figure's top rows left of `right` (the head; the raised pistol in the
    far hand reaches as high, right of it)."""
    xs = [x for y in range(y0, y0 + h) for x in range(int(right)) if keyed.getpixel((x, y))[3]]
    return (min(xs) + max(xs)) // 2


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if abs(r - GREY[0]) + abs(g - GREY[1]) + abs(b - GREY[2]) < 12:
                px[x, y] = (0, 0, 0, 0)
    return im


def guide(refs, name, spec, k, soles=None):
    """The render scaled by k, its box bottom (the soles) on row SOLE; with `soles` (an uncropped render of her body
    alone in the same frame) her own soles go on SOLE and whatever reaches below them is cut off."""
    src, label = spec
    full = _keyed(os.path.join(refs, src))
    box = full.getbbox()
    sole = _keyed(soles).getbbox()[3] if soles else box[3]
    fig = full.crop((box[0], box[1], box[2], sole))
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Renata.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/renata/skins/base/renataloadscreen_0.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_renata_splash.png"))
    # the scale: hair top to soles in the frontal idle (no machine)
    body = _keyed(os.path.join(refs, "2_renata_frontal.png"))
    k = BODY_H / body.crop(body.getbbox()).height
    raw = os.path.join(a.out, "raw")
    for name, spec in GUIDES.items():
        soles = os.path.join(raw, "ult_body.png") if name.startswith("8c") else None
        guide(refs, name, (spec[0].replace("raw/", "../raw/"), spec[1]), k, soles)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "renata", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = a.out + ".zip"   # refs/, style/ and the prompt; raw/ (uncropped renders for the guides) stays out
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(a.out, "PICTURE_PROMPT.md"), "PICTURE_PROMPT.md")
        for sub in ("refs", "style"):
            for f in sorted(os.listdir(os.path.join(a.out, sub))):
                z.write(os.path.join(a.out, sub, f), f"{sub}/{f}")
    print("written", zp)


if __name__ == "__main__":
    main()
