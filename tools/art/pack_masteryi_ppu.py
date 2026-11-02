"""The Codex pack for league_masteryi's PPU redo (assets/source/masteryi/PICTURE_PROMPT_PPU.md): one design picture on the
6-px grid at PPU 2.5 (PPU 3 would not fit his raised sword in the canvas), TRACED from his game sprite now (the round
helmet with its gold-rimmed visor lens, the grey steel armour, the green-bladed sword raised behind him, the low lunging
stance), only denser - Evelynn's way (tools/art/pack_evelynn_ppu.py), one PR with the other two (the user, 2026-11-02:
「接下来可以重做 戴安娜 易大师 瑞兹」).

    python tools/art/pack_masteryi_ppu.py --out C:/t/ma_pack [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..3 (League renders through tools/lol/pose_ref.py, poses.json's camera: 1 =
his idle, 2 = his head close up, 3 = from behind; Riot's, kept local, never committed), refs/4 (the loading-screen art),
no refs/5 (his sprite was posed after League's renders, no design picture of its own), refs/6 (his game sprite now at
8x: THE picture to trace), refs/7 (the layout guide: his sprite now as a flat silhouette at the new size) and
<out>/style/8..10 (this pack's Jinx, Viego and Talon at their hd_idle, 8x), then <out>.zip.
"""
import argparse
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack_samira_ppu as SP  # noqa: E402

REPO = SP.REPO
SRC, CHAMPS, GREY = SP.SRC, SP.CHAMPS, SP.GREY
IDLE = "masteryi_2013_idle1@0"                              # League's idle (poses.json "design")
HIDE = []                                           # (no submesh hidden by name)
SUBTEX = {}                                         # (no submesh textured apart)
FLAGS = ["--hide-joints", "^[lr]_sword$"]  # (poses.json hide: the two spare swords on his back)
# name -> (yaw, size, width, crop "box" or fractions of the figure's box, frame); not mirrored (poses.json camera)
RENDERS = {
    "1_masteryi_idle": (40, 1000, 1.4, "box", IDLE),
    "2_masteryi_head": (40, 2400, 1.2, (0.3, 0.38, 0.8, 0.72), IDLE),
    "3_masteryi_back": (220, 1000, 1.4, "box", IDLE),
}
CANVAS = (1024, 1024)                               # (the size: the sword tip to the soles, guide())
SOLE = 960                                          # the soles' row
SQ = 6
PPU = 2.5                                           # (his sword raised behind him: 56 game px tall, 3 would not fit)


def render(lol, name, spec, out):
    yaw, size, width, crop, frame = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "MasterYi",
           "--hq", "--head", "1.0", "--legs", "1.0"] + FLAGS
    for m in HIDE:
        cmd += ["--hide-submesh", m]
    for m, t in SUBTEX.items():
        cmd += ["--submesh-texture", f"{m}={t}"]
    cmd += ["--pitch", "25", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", "0.6",
            "--ground", "0.92", "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
            "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = SP.keyed(path).getbbox()
    if crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m))).save(path)
    else:
        w, h = x1 - x0, y1 - y0
        im.crop((x0 + int(crop[0] * w), y0 + int(crop[1] * h), x0 + int(crop[2] * w), y0 + int(crop[3] * h))).save(path)
    print(name, Image.open(path).size)
    return path


def guide(refs, spr):
    """His sprite now as a flat silhouette at PPU 3 (each game pixel 18 px), soles on row SOLE, centred."""
    full = round(spr.height * PPU * SQ)
    k = full / spr.height
    a = spr.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    a = a.resize((round(spr.width * k), full), Image.NEAREST)
    sil = Image.new("RGBA", a.size, (150, 160, 185, 255))
    sil.putalpha(a)
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    ox = (CANVAS[0] - a.width) // 2
    can.alpha_composite(sil, (ox, SOLE - full))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(110, 110, 110, 255), width=2)
    d.line([(0, SOLE - full), (CANVAS[0], SOLE - full)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), f"sword tip to the soles {full} px ({round(spr.height * PPU)} squares of {SQ}); layout only",
           fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "7_layout.png"))
    print("layout", a.size, "at", ox, SOLE - full)


def splash(lol, out):
    from riot import Wad
    import pose_ref
    wad = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", "MasterYi.wad.client"))
    for tex in ("MasterYiLoadScreen.tex", "MasterYiLoadScreen_0.tex"):
        try:
            data = wad.read_path(f"ASSETS/Characters/MasterYi/Skins/Base/{tex}".lower())
        except KeyError:
            continue
        pose_ref.read_tex(data).convert("RGB").save(out)
        return
    sys.exit("no loading-screen art in MasterYi.wad.client")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    refs, style = (os.path.join(a.out, d) for d in ("refs", "style"))
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    for name, spec in RENDERS.items():
        render(a.lol, name, spec, refs)
    splash(a.lol, os.path.join(refs, "4_masteryi_splash.png"))
    now = SP.sheet_frame(os.path.join(CHAMPS, "league_masteryi"), "idle_base")
    SP.sheet_frame(os.path.join(CHAMPS, "league_masteryi"), "idle_base", 8).save(
        os.path.join(refs, "6_masteryi_now.png"))
    guide(refs, now)
    for n, hero in (("8_style_jinx", "league_jinx"), ("9_style_viego", "league_viego"),
                    ("10_style_talon", "league_talon")):
        SP.sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(SP.lp(os.path.join(SRC, "masteryi", "PICTURE_PROMPT_PPU.md")),
                    os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| his sprite now", now.size)


if __name__ == "__main__":
    main()
