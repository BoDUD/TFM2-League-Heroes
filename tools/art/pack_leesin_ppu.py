"""The Codex pack for league_leesin's PPU redo (assets/source/leesin/PICTURE_PROMPT_PPU.md): one design picture on the
11-px grid at PPU 2.2, TRACED from his game sprite now (the guard stance: the far palm forward, the near fist back), only
denser - Draven's way (tools/art/pack_draven_ppu.py). The user, 2026-10-26: 「下一个英雄重做盲僧」.

    python tools/art/pack_leesin_ppu.py --out C:/t/ls_pack [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..3 (League renders through tools/lol/pose_ref.py with a chibi head, so
he faces right as the sprite does: 1 = his idle, 2 = his head close up, 3 = from behind; Riot's, kept local, never
committed), refs/4 (the loading-screen art), refs/5 (his native design, assets/source/native/leesin_native.png),
refs/6 (his game sprite now at 8x: THE picture to trace), refs/7 (the layout guide: his sprite now as a flat silhouette
at the new size) and <out>/style/8..10 (this pack's Jinx, Draven and Lux at their PPU 2.2 hd_idle, 8x), then <out>.zip.

Samira's and Draven's lessons are in the prompt: a sturdy build, the head drawn at the size every action keeps, the
face's features clear (his blindfold, mouth and jaw).
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
IDLE = "Idle_Active@0"                               # League's idle (poses.json "design")
# name -> (yaw, size, width, crop "box" or fractions of the figure's box, frame)
RENDERS = {
    "1_leesin_idle": (55, 1000, 1.8, "box", IDLE),
    "2_leesin_head": (55, 2400, 1.2, (0.25, 0.0, 0.75, 0.40), IDLE),
    "3_leesin_back": (235, 1000, 1.8, "box", IDLE),
}
CANVAS = (1024, 1536)                                # portrait: a compact stance, his braid high
SOLE = 1472                                          # the soles' row
SQ = 11
PPU = 2.2


def render(lol, name, spec, out):
    yaw, size, width, crop, frame = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "LeeSin",
           "--hq", "--head", "2.0", "--legs", "0.8", "--hair", "0.5", "--pitch", "25", "--mirror",
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
    """His sprite now as a flat silhouette at PPU 2.2 (each game pixel 24.2 px), soles on row SOLE, centred."""
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
    d.text((24, 24), f"top of the hair to soles {full} px ({round(spr.height * PPU)} squares of {SQ}); layout only",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "LeeSin.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/LeeSin/Skins/Base/LeeSinLoadScreen_0.tex".lower())) \
        .convert("RGB").save(os.path.join(refs, "4_leesin_splash.png"))
    first = Image.open(SP.lp(os.path.join(SRC, "native", "leesin_native.png"))).convert("RGBA")
    first = first.crop(first.getbbox())
    pad = Image.new("RGBA", (first.width + 32, first.height + 32), GREY + (255,))
    pad.alpha_composite(first, (16, 16))
    pad.convert("RGB").save(os.path.join(refs, "5_leesin_first_design.png"))
    now = SP.sheet_frame(os.path.join(CHAMPS, "league_leesin"), "idle_base")
    SP.sheet_frame(os.path.join(CHAMPS, "league_leesin"), "idle_base", 8).save(os.path.join(refs, "6_leesin_now.png"))
    guide(refs, now)
    for n, hero in (("8_style_jinx", "league_jinx"), ("9_style_draven", "league_draven"), ("10_style_lux", "league_lux")):
        SP.sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(SP.lp(os.path.join(SRC, "leesin", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| his sprite now", now.size)


if __name__ == "__main__":
    main()
