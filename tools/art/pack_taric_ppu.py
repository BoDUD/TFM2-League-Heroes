"""The Codex pack for league_taric's PPU redo (assets/source/taric/PICTURE_PROMPT_PPU.md): one design picture on the
11-px grid at PPU 1.5, TRACED from his game sprite now (the long brown hair, the silver pauldrons set with blue gems,
the dark coat and the blue cape, the gem-headed hammer low in his near hand, the bare far arm), only denser - Zed's way
(tools/art/pack_zed_ppu.py). The user, 2026-10-29: 「下一个英雄重做塔里克」.

    python tools/art/pack_taric_ppu.py --out C:/t/ta_pack [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..3 (League renders through tools/lol/pose_ref.py, poses.json's camera:
1 = his idle, 2 = his head close up, 3 = from behind; Riot's, kept local, never committed), refs/4 (the loading-screen
art), refs/5 (his native design, assets/source/native/taric_native.png - his sprite at 8x), refs/6 (his game sprite
now at 8x: THE picture to trace), refs/7 (the layout guide: his sprite now as a flat silhouette at the new size) and
<out>/style/8..10 (this pack's Lee Sin, Pantheon and Riven at their PPU 1.5 hd_idle, 8x), then <out>.zip.
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
IDLE = "taric_idle1@0"                              # League's idle (poses.json "design")
HIDE = []                                           # (poses.json hides no submesh)
# name -> (yaw, size, width, crop "box" or fractions of the figure's box, frame); not mirrored (poses.json camera)
RENDERS = {
    "1_taric_idle": (40, 1000, 1.4, "box", IDLE),
    "2_taric_head": (40, 2400, 1.2, (0.20, 0.0, 0.80, 0.30), IDLE),
    "3_taric_back": (220, 1000, 1.4, "box", IDLE),
}
CANVAS = (1024, 1024)                               # 40 game px hair top to soles now: 60 squares, 660 px
SOLE = 960                                          # the soles' row
SQ = 11
PPU = 1.5


def render(lol, name, spec, out):
    yaw, size, width, crop, frame = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Taric",
           "--hq", "--head", "1.0", "--legs", "1.0"]
    for m in HIDE:
        cmd += ["--hide-submesh", m]
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
    """His sprite now as a flat silhouette at PPU 1.5 (each game pixel 16.5 px), soles on row SOLE, centred."""
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
    d.text((24, 24), f"hair top to soles {full} px ({round(spr.height * PPU)} squares of {SQ}); layout only",
           fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "7_layout.png"))
    print("layout", a.size, "at", ox, SOLE - full)


def splash(lol, out):
    from riot import Wad
    import pose_ref
    wad = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", "Taric.wad.client"))
    for tex in ("TaricLoadScreen.tex", "TaricLoadScreen_0.tex"):
        try:
            data = wad.read_path(f"ASSETS/Characters/Taric/Skins/Base/{tex}".lower())
        except KeyError:
            continue
        pose_ref.read_tex(data).convert("RGB").save(out)
        return
    sys.exit("no loading-screen art in Taric.wad.client")


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
    splash(a.lol, os.path.join(refs, "4_taric_splash.png"))
    first = Image.open(SP.lp(os.path.join(SRC, "native", "taric_native.png"))).convert("RGBA")
    first = first.crop(first.getbbox())
    pad = Image.new("RGBA", (first.width + 32, first.height + 32), GREY + (255,))
    pad.alpha_composite(first, (16, 16))
    pad.convert("RGB").save(os.path.join(refs, "5_taric_first_design.png"))
    now = SP.sheet_frame(os.path.join(CHAMPS, "league_taric"), "idle_base")
    SP.sheet_frame(os.path.join(CHAMPS, "league_taric"), "idle_base", 8).save(
        os.path.join(refs, "6_taric_now.png"))
    guide(refs, now)
    for n, hero in (("8_style_leesin", "league_leesin"), ("9_style_pantheon", "league_pantheon"),
                    ("10_style_riven", "league_riven")):
        SP.sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(SP.lp(os.path.join(SRC, "taric", "PICTURE_PROMPT_PPU.md")),
                    os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| his sprite now", now.size)


if __name__ == "__main__":
    main()
