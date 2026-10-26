"""The Codex pack for league_vayne's PPU redo (assets/source/vayne/PICTURE_PROMPT_PPU.md): one design picture on the
11-px grid at PPU 2.2, TRACED from her game sprite now (standing, the wrist crossbow on the near forearm, the big
crossbow over her back, the red cape behind), only denser - Lee Sin's way (tools/art/pack_leesin_ppu.py). The user,
2026-10-26: 「下一个英雄重做薇恩」.

    python tools/art/pack_vayne_ppu.py --out C:/t/vn_pack [--lol D:/WeGameApps/lol] [--redo]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..3 (League renders through tools/lol/pose_ref.py with a chibi head, so
she faces right as the sprite does: 1 = her idle, 2 = her head close up, 3 = from behind; Riot's, kept local, never
committed), refs/4 (the loading-screen art), refs/5 (her native design, assets/source/native/vayne_native.png),
refs/6 (her game sprite now at 8x: THE picture to trace), refs/7 (the layout guide: her sprite now as a flat silhouette
at the new size) and <out>/style/8..10 (this pack's Jinx, Draven and Lux at their PPU 2.2 hd_idle, 8x), then <out>.zip.

--redo (the user, 2026-10-26, on Codex's first take - drawn on ~8-px squares = PPU 3.5, a small adult head, a new
stance: 「Q 版大头（约 1/3），姿势照现在的精灵，直接按 PPU 1.5 画（约 60 格，每格 16 像素）」): PPU 1.5 on 16-px
squares, the layout guide with her chin's row, refs/5 = that first take (costume detail only), style = this pack's
Riven, Katarina and Lee Sin at PPU 1.5, prompt assets/source/vayne/PICTURE_PROMPT_REDO.md.

Samira's, Draven's and Lee Sin's lessons are in the prompt: not a thin build, the head drawn at the size every action
keeps, the face's features clear (her red glasses, mouth and chin).
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
IDLE = "Vayne_idle1@0"                               # League's idle (poses.json "design")
# name -> (yaw, size, width, crop "box" or fractions of the figure's box, frame)
RENDERS = {
    "1_vayne_idle": (40, 1000, 1.8, "box", IDLE),
    "2_vayne_head": (40, 2400, 1.2, (0.4, 0.04, 0.95, 0.4), IDLE),
    "3_vayne_back": (220, 1000, 1.8, "box", IDLE),
}
CANVAS = (1024, 1536)                                # portrait: standing, her ponytail and the big crossbow high
SOLE = 1472                                          # the soles' row
SQ = 11
PPU = 2.2


def render(lol, name, spec, out):
    yaw, size, width, crop, frame = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Vayne",
           "--hq", "--head", "2.3", "--legs", "0.8", "--hair", "0.6", "--pitch", "25",
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


CHIN = 16                                            # her sprite's chin row (0 = its top): the head 0-16 of 40


def guide(refs, spr, chin=False):
    """Her sprite now as a flat silhouette at PPU (each game pixel PPU x SQ px), soles on row SOLE, centred; with
    `chin` her chin's row marked too (red)."""
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
    if chin:
        cy = SOLE - full + round(CHIN * k)
        d.line([(0, cy), (CANVAS[0], cy)], fill=(200, 60, 60, 255), width=2)
        d.text((24, cy - 18), f"chin: the head from the top line to here = {round(CHIN * PPU)} squares", fill=(200, 60, 60, 255))
    d.text((24, 24), f"top of the figure to soles {full} px ({round(spr.height * PPU)} squares of {SQ}); layout only",
           fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "7_layout.png"))
    print("layout", a.size, "at", ox, SOLE - full)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    global PPU, SQ
    if a.redo:
        PPU, SQ = 1.5, 16
    refs, style = (os.path.join(a.out, d) for d in ("refs", "style"))
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    for name, spec in RENDERS.items():
        render(a.lol, name, spec, refs)
    from riot import Wad
    import pose_ref
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Vayne.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Vayne/Skins/Base/VayneLoadScreen.tex".lower())) \
        .convert("RGB").save(os.path.join(refs, "4_vayne_splash.png"))
    if a.redo:
        first = Image.open(SP.lp(os.path.join(SRC, "vayne", "hd", "raw", "vayne-A.png"))).convert("RGBA")
        first.putalpha(first.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    else:
        first = Image.open(SP.lp(os.path.join(SRC, "native", "vayne_native.png"))).convert("RGBA")
    first = first.crop(first.getbbox())
    pad = Image.new("RGBA", (first.width + 32, first.height + 32), GREY + (255,))
    pad.alpha_composite(first, (16, 16))
    pad.convert("RGB").save(os.path.join(refs, "5_vayne_first_take.png" if a.redo else "5_vayne_first_design.png"))
    now = SP.sheet_frame(os.path.join(CHAMPS, "league_vayne"), "idle_base")
    SP.sheet_frame(os.path.join(CHAMPS, "league_vayne"), "idle_base", 8).save(os.path.join(refs, "6_vayne_now.png"))
    guide(refs, now, chin=a.redo)
    styles = ((("8_style_riven", "league_riven"), ("9_style_katarina", "league_katarina"), ("10_style_leesin", "league_leesin"))
              if a.redo else (("8_style_jinx", "league_jinx"), ("9_style_draven", "league_draven"), ("10_style_lux", "league_lux")))
    for n, hero in styles:
        SP.sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(SP.lp(os.path.join(SRC, "vayne", "PICTURE_PROMPT_REDO.md" if a.redo else "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| her sprite now", now.size)


if __name__ == "__main__":
    main()
