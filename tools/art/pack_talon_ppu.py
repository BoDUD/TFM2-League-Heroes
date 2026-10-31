"""The Codex pack for league_talon's PPU redo (assets/source/talon/PICTURE_PROMPT_PPU.md): one design picture on the
6-px grid at PPU 3, TRACED from his game sprite now (the blue-violet hood with its silver V brow guard, the tanned
face under it, the layered silver pauldron, the rust-red cloak with its hanging blade tips and the long spear tip
behind him, the long wrist blade, the teal and gold sash, the gunmetal greaves, the low ready crouch), only denser -
Briar's way (tools/art/pack_briar_ppu.py), straight at the density the user took for her (2.94). The user, 2026-10-31: 「下一个英雄重做泰隆」.

    python tools/art/pack_talon_ppu.py --out C:/t/tl_pack [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..3 (League renders through tools/lol/pose_ref.py, poses.json's camera:
1 = his idle, 2 = his head close up, 3 = from behind; Riot's, kept local, never committed), refs/4 (the loading-screen
art), refs/5 (his native design, assets/source/native/talon_native.png - his sprite at 8x), refs/6 (his game sprite
now at 8x: THE picture to trace), refs/7 (the layout guide: his sprite now as a flat silhouette at the new size) and
<out>/style/8..10 (this pack's Jinx, Sona and Briar at their hd_idle, 8x), then <out>.zip.
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
IDLE = "talon_idle1@0"                              # League's idle (poses.json "design")
HIDE = []                                           # (poses.json hides no submesh)
# name -> (yaw, size, width, crop "box" or fractions of the figure's box, frame); not mirrored (poses.json camera)
RENDERS = {
    "1_talon_idle": (45, 1000, 1.4, "box", IDLE),
    "2_talon_head": (45, 2400, 1.2, (0.2, 0.0, 0.8, 0.36), IDLE),
    "3_talon_back": (225, 1000, 1.4, "box", IDLE),
}
CANVAS = (1024, 1024)                               # (the size: hood top to the soles, guide())
SOLE = 960                                          # the soles' row
SQ = 6
PPU = 3.0


def render(lol, name, spec, out):
    yaw, size, width, crop, frame = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Talon",
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
    d.text((24, 24), f"hood top to the soles {full} px ({round(spr.height * PPU)} squares of {SQ}); layout only",
           fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "7_layout.png"))
    print("layout", a.size, "at", ox, SOLE - full)


def splash(lol, out):
    from riot import Wad
    import pose_ref
    wad = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", "Talon.wad.client"))
    for tex in ("TalonLoadScreen.tex", "TalonLoadScreen_0.tex"):
        try:
            data = wad.read_path(f"ASSETS/Characters/Talon/Skins/Base/{tex}".lower())
        except KeyError:
            continue
        pose_ref.read_tex(data).convert("RGB").save(out)
        return
    sys.exit("no loading-screen art in Talon.wad.client")


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
    splash(a.lol, os.path.join(refs, "4_talon_splash.png"))
    first = Image.open(SP.lp(os.path.join(SRC, "native", "talon_native.png"))).convert("RGBA")
    first = first.crop(first.getbbox())
    pad = Image.new("RGBA", (first.width + 32, first.height + 32), GREY + (255,))
    pad.alpha_composite(first, (16, 16))
    pad.convert("RGB").save(os.path.join(refs, "5_talon_first_design.png"))
    now = SP.sheet_frame(os.path.join(CHAMPS, "league_talon"), "idle_base")
    SP.sheet_frame(os.path.join(CHAMPS, "league_talon"), "idle_base", 8).save(
        os.path.join(refs, "6_talon_now.png"))
    guide(refs, now)
    for n, hero in (("8_style_jinx", "league_jinx"), ("9_style_sona", "league_sona"),
                    ("10_style_briar", "league_briar")):
        SP.sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(SP.lp(os.path.join(SRC, "talon", "PICTURE_PROMPT_PPU.md")),
                    os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| his sprite now", now.size)


if __name__ == "__main__":
    main()
