"""The Codex pack for league_ahri's PPU redo (assets/source/ahri/PICTURE_PROMPT_PPU.md): two design pictures on the
11-px grid at PPU 1.5 - A in 3/4 view facing right, S side-on - her sprite's chibi proportions (40 game rows from the
ear tips to the soles, the nine tails in one bunch behind her), the way league_leblanc's pack asked
(tools/art/pack_leblanc_ppu.py); the actions are posed after League's clips afterwards (rig_leblanc_hd.py's way), the
effects stay.

    python tools/art/pack_ahri_ppu.py --out C:/t/ah_pack [--lol D:/WeGameApps/lol]

The user, 2026-10-19: 「接下来重做阿狸吧」 (after LeBlanc's PPU redo, PR #397). Her sprite was drawn by Claude from
League's model (restyle_native.py) and Codex only redrew the tails (TAILS_REDO2.md), so there is no dense picture of
her to start from: Codex draws one.
Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders of her idle with poses.json's chibi head, legs and
hair, through tools/lol/pose_ref.py: Riot's, kept local, never committed; 4 = her tails close up), refs/5 (the
loading-screen art), refs/6 (her game sprite now at 8x: the proportions, the tails' bunch and the facing), refs/7 (the
layout guide: her sprite now as a flat silhouette at the new size) and <out>/style/8..10 (this pack's LeBlanc, Fiora
and Kai'Sa at their PPU hd_idle, 8x), then <out>.zip. Render into a short folder.
"""
import argparse
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
sys.path.insert(0, HERE)
from pack_leblanc_ppu import GREY, keyed, lp, sheet_frame  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
IDLE = "Idle1@0"                                # poses.json design
# poses.json's chibi head, legs and hair; the tails with their own texture, the ult's large tail left out
CHIBI = ["--head", "2.0", "--legs", "0.8", "--hair", "0.5", "--submesh-texture", "Tails=Tails_TX",
         "--hide-submesh", "Tail_Large"]
# name -> (yaw, size, width, crop "box" or fractions of the figure's box); not mirrored (poses.json camera)
RENDERS = {
    "1_ahri_idle": (35, 1000, 1.3, "box"),
    "2_ahri_side": (90, 1000, 1.4, "box"),
    "3_ahri_head": (35, 2400, 1.3, (0.15, 0.0, 0.85, 0.45)),
    "4_ahri_tails": (35, 1800, 1.3, (0.0, 0.1, 0.75, 0.9)),
}
PPU, SQ = 1.5, 11                               # each game pixel 1.5 squares of 11 px
ROWS = 40                                       # her idle now: ear tips to soles
# ear tips to soles 40 game rows = 60 squares = FULL_H px, soles on row SOLE
CANVAS, SOLE, FULL_H = (1024, 1024), 960, 660


def render(lol, name, spec, out):
    yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Ahri", "--hq",
           *CHIBI, "--fit-all", "--pitch", "25", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size),
           "--fit", "0.6", "--ground", "0.92", "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", IDLE]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = keyed(path).getbbox()
    if crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m))).save(path)
    else:
        w, h = x1 - x0, y1 - y0
        im.crop((x0 + int(crop[0] * w), y0 + int(crop[1] * h), x0 + int(crop[2] * w), y0 + int(crop[3] * h))).save(path)
    print(name, Image.open(path).size)
    return path


def guide(refs):
    """Her sprite now as a flat silhouette at PPU 1.5 (each game pixel 16.5 px), soles on row SOLE, centred: the size
    and the place only."""
    spr = sheet_frame(os.path.join(CHAMPS, "league_ahri"), "idle")
    k = FULL_H / spr.height
    a = spr.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    a = a.resize((round(spr.width * k), FULL_H), Image.NEAREST)
    sil = Image.new("RGBA", a.size, (150, 160, 185, 255))
    sil.putalpha(a)
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    ox = (CANVAS[0] - a.width) // 2
    can.alpha_composite(sil, (ox, SOLE - FULL_H))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(110, 110, 110, 255), width=2)
    d.line([(0, SOLE - FULL_H), (CANVAS[0], SOLE - FULL_H)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), f"ear tips to soles {FULL_H} px (60 squares of 11); layout only", fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "7_layout.png"))
    print("layout", a.size, "at", ox, SOLE - FULL_H)


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
    from riot import Wad
    import pose_ref
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Ahri.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Ahri/Skins/Base/AhriLoadScreen_0.tex")) \
        .convert("RGB").save(os.path.join(refs, "5_ahri_splash.png"))
    sheet_frame(os.path.join(CHAMPS, "league_ahri"), "idle", 8).save(os.path.join(refs, "6_ahri_now.png"))
    guide(refs)
    for n, hero in (("8_style_leblanc", "league_leblanc"), ("9_style_fiora", "league_fiora"),
                    ("10_style_kaisa", "league_kaisa")):
        sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(lp(os.path.join(SRC, "ahri", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
