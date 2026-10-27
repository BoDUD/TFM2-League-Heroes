"""The Codex pack for league_syndra's PPU redo (assets/source/syndra/PICTURE_PROMPT_PPU.md): one design picture on the
11-px grid at PPU 1.5, TRACED from her game sprite now (hovering, the near hand at her hip, the far hand out at her
waist, the silver hair down both sides), only denser - Rengar's way (tools/art/pack_rengar_ppu.py). The user,
2026-10-27: 「接下来可以重做辛德拉」.

    python tools/art/pack_syndra_ppu.py --out C:/t/sy_pack [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..3 (League renders through tools/lol/pose_ref.py, poses.json's camera and
chibi head, the spheres hidden: 1 = her idle, 2 = her head close up, 3 = from behind; Riot's, kept local, never
committed), refs/4 (the loading-screen art), refs/5 (her native design, assets/source/native/syndra_native.png - her
sprite at 8x), refs/6 (her game sprite now at 8x: THE picture to trace), refs/7 (the layout guide: her sprite now as a
flat silhouette at the new size) and <out>/style/8..10 (this pack's Morgana, Mel and Zoe at their PPU 1.5 hd_idle, 8x),
then <out>.zip.
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
IDLE = "Syndra_idle1@0"                              # League's idle (poses.json "design")
# name -> (yaw, size, width, crop "box" or fractions of the figure's box, frame); mirrored (poses.json camera)
RENDERS = {
    "1_syndra_idle": (30, 1000, 1.4, "box", IDLE),
    "2_syndra_head": (30, 2400, 1.2, (0.15, 0.0, 0.85, 0.40), IDLE),
    "3_syndra_back": (210, 1000, 1.4, "box", IDLE),
}
CANVAS = (1024, 1024)                                # 42 game px horn tips to toes now: 63 squares, 693 px
SOLE = 960                                           # the soles' row
SQ = 11
PPU = 1.5


def render(lol, name, spec, out):
    yaw, size, width, crop, frame = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Syndra",
           "--hq", "--head", "1.8", "--legs", "0.85", "--mirror", "--hide-submeshes", "--pitch", "20", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size),
           "--fit", "0.6", "--ground", "0.92", "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
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
    """Her sprite now as a flat silhouette at PPU 1.5 (each game pixel 16.5 px), toes on row SOLE, centred."""
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
    d.text((24, 24), f"horn tips to toes {full} px ({round(spr.height * PPU)} squares of {SQ}); layout only",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Syndra.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Syndra/Skins/Base/SyndraLoadScreen_0.tex".lower())) \
        .convert("RGB").save(os.path.join(refs, "4_syndra_splash.png"))
    first = Image.open(SP.lp(os.path.join(SRC, "native", "syndra_native.png"))).convert("RGBA")
    first = first.crop(first.getbbox())
    pad = Image.new("RGBA", (first.width + 32, first.height + 32), GREY + (255,))
    pad.alpha_composite(first, (16, 16))
    pad.convert("RGB").save(os.path.join(refs, "5_syndra_first_design.png"))
    now = SP.sheet_frame(os.path.join(CHAMPS, "league_syndra"), "idle")
    SP.sheet_frame(os.path.join(CHAMPS, "league_syndra"), "idle", 8).save(os.path.join(refs, "6_syndra_now.png"))
    guide(refs, now)
    for n, hero in (("8_style_morgana", "league_morgana"), ("9_style_mel", "league_mel"),
                    ("10_style_zoe", "league_zoe")):
        SP.sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(SP.lp(os.path.join(SRC, "syndra", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| her sprite now", now.size)


if __name__ == "__main__":
    main()
