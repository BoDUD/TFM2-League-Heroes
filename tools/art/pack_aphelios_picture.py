"""Build the step-0 pack for Codex (assets/source/aphelios/PICTURE_PROMPT.md): League references, layout guides,
the five weapons and style pictures.

    python tools/art/pack_aphelios_picture.py --out %TEMP%/ap_work/aphelios_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..14 (League renders, the loading-screen art, the layout guides and the
weapons: Riot's, kept local, never committed) and <out>/style/15..18 (this pack's PPU 1.4-1.5 heroes at their dense
frames, 8x, cut from their sheets), then <out>.zip. Render into a short folder (%TEMP%): pose_ref's saves under ap/dist
pass MAX_PATH.
Aphelios (the user's picks, 2026-10-16: bottom ADC, add-on, PPU 1.5) is drawn as two body pictures on 1536x1536 squares
(Calibrum is a rifle longer than he is tall) and one weapon sheet: A = League's Calibrum idle (aphelios_A_Idle1: the
long rifle resting on his shoulder), B = Calibrum's shot (aphelios_A_Attack1 at 300 ms: crouched, the rifle levelled),
W = the five weapons apart at the scale of A (the add-on paints each one in his hand). League's clips A..E are the
weapons in their order: A Calibrum, B Severum, C Gravitum, D Infernum, E Crescendum (only the held weapon's submesh is
shown, the skin hides all five). Hair top to soles about 72 squares of 11 px (~40 game rows at 1.8 squares a game
pixel; read back and brought to PPU 1.5 by the restyle).
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
WEAPONS = ["calibrum", "severum", "gravitum", "infernum", "crescendum"]
CLIP = dict(zip(WEAPONS, "ABCDE"))
IDLE = "aphelios_A_Idle1@0"
SHOT = "aphelios_A_Attack1@300"
PROPS = ["recall", "scarf_recall", "flower"]
BODY = ["Aphelios_Base_Mat", "scarf"]
# name -> (frames, shown weapon or None, hide the body, yaw, size, fit, ground, width, crop: "box" / "head")
RENDERS = {
    "1_aphelios_idle": ([IDLE], "calibrum", False, 45, 1600, 0.85, 0.85, 1.4, "box"),
    "2_aphelios_frontal": ([IDLE], "calibrum", False, 0, 1600, 0.85, 0.85, 1.4, "box"),
    "3_aphelios_head": (["aphelios_C_Idle1@0"], None, False, 20, 3200, 0.85, 0.85, 1.0, "head"),
    "4_aphelios_back": ([IDLE], "calibrum", False, 200, 1600, 0.85, 0.85, 1.4, "box"),
    "6_aphelios_shot": ([SHOT], "calibrum", False, 45, 1600, 0.85, 0.85, 1.6, "box"),
    "7_aphelios_shot_side": ([SHOT], "calibrum", False, 80, 1600, 0.85, 0.85, 1.6, "box"),
    "9_weapons_in_hand": ([f"aphelios_{CLIP[w]}_Idle1@0" for w in WEAPONS], "each", False, 45, 900, 0.85, 0.85, 1.0, None),
}
for _i, _w in enumerate(WEAPONS):
    RENDERS[f"{10 + _i}_weapon_{_w}"] = ([f"aphelios_{CLIP[_w]}_Idle1@0"], _w, True, 45, 2400, 1.0, 0.85, 1.4, "box")
RENDERS["12_weapon_gravitum"] = (["aphelios_C_Idle1@0"], "gravitum", True, 45, 2400, 1.0, 1.25, 1.4, "box")  # cut at 0.85
RENDERS["10_weapon_calibrum"] = ([IDLE], "calibrum", True, 90, 2400, 1.0, 1.25, 0.8, "box")  # yaw 45 shows it edge-on
# measured on a render without weapons (the rifle tops his hair): hair top to soles HAIR_H px (72 squares of 11) on
# the 1536 square, soles on row SOLE, centred; the shot is scaled like the idle (one size for both)
MEASURE = ([IDLE], None, False, 45, 1600, 0.85, 0.85, 1.4, "box")
HAIR_H = 792
SOLE = 1400
GUIDES = {
    "8a_layout_A.png": ("1_aphelios_idle.png", "A: League's Calibrum idle; hair top to soles 792 px (72 squares of 11); layout only"),
    "8b_layout_B.png": ("6_aphelios_shot.png", "B: Calibrum's shot; same scale; layout only"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "15_style_jayce.png": ("jayce", "hd_idle"),
    "16_style_kalista.png": ("kalista", "hd_idle"),
    "17_style_katarina.png": ("katarina", "hd_idle"),
    "18_style_pantheon.png": ("pantheon", "hd_idle"),
}


def render(lol, name, spec, out):
    frames, shown, no_body, yaw, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Aphelios",
           "--hq", "--fit-all", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(fit),
           "--ground", str(ground), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out]
    for w in WEAPONS:
        cmd += ["--submesh-texture", f"{w}=Guns_TX"]
    hide = PROPS + (BODY if no_body else [])  # --fit-all keeps the scale with the body hidden
    if shown != "each":
        hide += [w for w in WEAPONS if w != shown]
    for s in hide:
        cmd += ["--hide-submesh", s]
    if shown == "each":  # one strip, each frame with its own weapon: render them one by one and paste
        cells = []
        for w, f in zip(WEAPONS, frames):
            one = render(lol, f"{name}_{w}", ([f], w, no_body, yaw, size, fit, ground, width, None), out)
            cells.append(Image.open(one).convert("RGB"))
            os.remove(one)
        can = Image.new("RGB", (sum(c.width for c in cells), cells[0].height), GREY)
        x = 0
        for c in cells:
            can.paste(c, (x, 0))
            x += c.width
        path = os.path.join(out, name + ".png")
        can.save(path)
        print(name, can.size)
        return path
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    if crop is None:
        return path
    im = Image.open(path).convert("RGB")
    key = _keyed(path)
    x0, y0, x1, y1 = key.getbbox()
    if crop == "head":  # the head: the top 16% of the body (no weapon shown), the columns round the hair
        band = key.crop((0, y0, key.width, y0 + (y1 - y0) // 12))
        bx0, _, bx1, _ = band.getbbox()
        cx, s = (bx0 + bx1) // 2, (y1 - y0) * 16 // 100
        im.crop((max(0, cx - s), max(0, y0 - s // 8), min(im.width, cx + s), y0 + s)).save(path)
    else:
        m = max(x1 - x0, y1 - y0) // 12
        im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m))).save(path)
    print(name, Image.open(path).size)
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


def weapon_guide(refs, k):
    """8c: the five weapons at the body's scale (the weapon renders are WEAPON_ZOOM times the body's), shelf-packed on
    the 1536 square: Calibrum, Severum, Gravitum, Crescendum on the top row, the wide Infernum below."""
    zoom = (2400 * 1.0) / (1600 * 0.85)
    figs = {}
    for i, w in enumerate(WEAPONS):
        im = _keyed(os.path.join(refs, f"{10 + i}_weapon_{w}.png"))
        im = im.crop(im.getbbox())
        figs[w] = im.resize((round(im.width * k / zoom), round(im.height * k / zoom)), Image.LANCZOS)
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    d = ImageDraw.Draw(can)
    gap, x, y = 60, 80, 120
    top = ["calibrum", "severum", "gravitum", "crescendum"]
    row_h = max(figs[w].height for w in top)
    for w in top:
        can.alpha_composite(figs[w], (x, y + row_h - figs[w].height))
        d.text((x, y + row_h + 12), w, fill=(60, 60, 60, 255))
        x += figs[w].width + gap
    y += row_h + 80
    can.alpha_composite(figs["infernum"], (80, y))
    d.text((80, y + figs["infernum"].height + 12), "infernum", fill=(60, 60, 60, 255))
    d.text((24, 24), "W: the five weapons at the scale of A; layout only", fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "8c_layout_W.png"))
    print("8c_layout_W.png", {w: f.size for w, f in figs.items()})


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
    tmp = a.out + "_measure"
    for d in (refs, style, tmp):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        render(a.lol, "measure", MEASURE, tmp)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Aphelios.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/aphelios/skins/base/apheliosloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(
            os.path.join(refs, "5_aphelios_splash.png"))
    bare = _keyed(os.path.join(tmp, "measure.png"))
    k = HAIR_H / bare.crop(bare.getbbox()).height
    for name, spec in GUIDES.items():
        guide(refs, name, spec, k)  # same camera size, so one scale for both
    weapon_guide(refs, k)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "aphelios", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
