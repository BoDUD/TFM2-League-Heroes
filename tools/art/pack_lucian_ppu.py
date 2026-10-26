"""The Codex pack for league_lucian's PPU redo (assets/source/lucian/PICTURE_PROMPT_PPU.md): one design picture on the
9-px grid at PPU 2.2, in his game sprite's pose and chibi proportions (standing, a pistol in each hand) but drawn
after LEAGUE's Lucian - the user, 2026-10-26: 「下一个英雄重做卢锡安 模型要和英雄联盟像一点」 - Vayne's way
(tools/art/pack_vayne_ppu.py), with League's renders as the look's reference rather than the old sprite's colours.

    python tools/art/pack_lucian_ppu.py --out C:/t/lu_pack [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders through tools/lol/pose_ref.py, facing right as the
sprite does: 1 = his idle with the chibi head the sprite has, 2 = his head close up, 3 = from behind, 4 = his idle at
League's own proportions - the costume undistorted; Riot's, kept local, never committed), refs/5 (the loading-screen
art), refs/6 (his game sprite now at 8x: the pose and the proportions), refs/7 (the layout guide: his sprite now as a
flat silhouette at the new size) and <out>/style/8..10 (this pack's Jinx, Draven and Vayne at their PPU 2.2 hd_idle,
8x), then <out>.zip.
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
IDLE = "Lucian_idle_ready@0"                         # League's idle (poses.json "design")
# name -> (yaw, size, width, crop "box" or fractions of the figure's box, frame, head scale)
RENDERS = {
    "1_lucian_idle": (45, 1000, 1.8, "box", IDLE, 2.3),
    "2_lucian_head": (45, 2400, 1.2, (0.30, 0.0, 0.85, 0.40), IDLE, 2.3),
    "3_lucian_back": (225, 1000, 1.8, "box", IDLE, 2.3),
    "4_lucian_league": (45, 1000, 1.8, "box", IDLE, 1.0),
}
CANVAS = (1536, 1024)                                # LANDSCAPE: his guns held wide (the sprite is 47 x 46)
SOLE = 980                                           # the soles' row
SQ = 9                                               # 47 x 2.2 x 11 = 1137 px would not fit 1024; at 9: 930 x 909
PPU = 2.2


def render(lol, name, spec, out):
    yaw, size, width, crop, frame, head = spec
    legs = "0.75" if head > 1 else "1.0"
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Lucian",
           "--hq", "--head", str(head), "--legs", legs, "--hair", "0.45" if head > 1 else "1.0", "--pitch", "25",
           "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", "0.6", "--ground", "0.92",
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, "--frame", frame]
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
    """His sprite now as a flat silhouette at PPU (each game pixel PPU x SQ px), soles on row SOLE, centred."""
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
    d.text((24, 24), f"top of the figure to soles {full} px ({round(spr.height * PPU)} squares of {SQ}); layout only",
           fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "7_layout.png"))
    print("layout", a.size, "at", ox, SOLE - full)


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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Lucian.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Lucian/Skins/Base/LucianLoadScreen.tex".lower())) \
        .convert("RGB").save(os.path.join(refs, "5_lucian_splash.png"))
    now = SP.sheet_frame(os.path.join(CHAMPS, "league_lucian"), "idle_base")
    SP.sheet_frame(os.path.join(CHAMPS, "league_lucian"), "idle_base", 8).save(os.path.join(refs, "6_lucian_now.png"))
    guide(refs, now)
    for n, hero in (("8_style_jinx", "league_jinx"), ("9_style_draven", "league_draven"), ("10_style_vayne", "league_vayne")):
        SP.sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(SP.lp(os.path.join(SRC, "lucian", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| his sprite now", now.size)


if __name__ == "__main__":
    main()
