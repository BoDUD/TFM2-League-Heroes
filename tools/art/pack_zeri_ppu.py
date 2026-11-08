"""The Codex pack for league_zeri's PPU redo (assets/source/zeri/PICTURE_PROMPT_PPU.md): one design picture on the 6-px
grid at PPU 3, REDESIGNED from League's Zeri (the spark of Zaun: the two spiky green-and-yellow hair buns, the green
eyes, the teal jacket with its white fur collar, the yellow top with the lightning bolt, the maroon leggings and knee
pads, the brown boots, the green electric rifle) in the pose and at the size of her sprite now, whose look the user
rejected (the user, 2026-11-09: 「最后重做提莫 菲兹 泽丽吧 泽丽虽然是高清帧了 但是模型我不满意」, then 「照英雄联盟原版重新设计」).

    python tools/art/pack_zeri_ppu.py --out C:/t/zr_pack [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..3 (League renders through tools/lol/pose_ref.py, the camera yaw 30 pitch
20: 1 = her idle, 2 = her head close up, 3 = from behind, mirrored as poses.json's camera; Riot's, kept local, never
committed), refs/4 (League's loading-screen art), refs/5 (League's model rendered in this game's chibi proportions,
poses.json chibi: head 1.6, legs 0.9), refs/6 (her sprite now, hd_idle_base at 3x: THE POSE AND THE SIZE ONLY), refs/7
(the layout guide: her sprite now as a flat silhouette at the new size) and <out>/style/8..10 (this pack's Veigar,
Seraphine and Ezreal at their hd_idle, 8x), then <out>.zip.
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
IDLE = "Idle@0"                              # League's idle (poses.json "design")
HIDE = []                                           # (no submesh hidden by name)
SUBTEX = {}                                         # (no submesh textured apart)
FLAGS = []  # (poses.json hides nothing)
# name -> (yaw, size, width, crop "box" or fractions of the figure's box, frame); mirrored (poses.json camera)
RENDERS = {
    "1_zeri_idle": (30, 1000, 1.4, "box", IDLE),
    "2_zeri_head": (30, 2400, 1.2, (0.1, 0.0, 0.8, 0.28), IDLE),
    "3_zeri_back": (210, 1000, 1.4, "box", IDLE),
}
CANVAS = (1024, 1024)                               # (the size: the hair-bun tips to the soles, guide())
SOLE = 960                                          # the soles' row
SQ = 6
PPU = 3.0


def render(lol, name, spec, out, chibi=("1.0", "1.0")):
    yaw, size, width, crop, frame = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Zeri",
           "--hq", "--head", chibi[0], "--legs", chibi[1], "--mirror"] + FLAGS
    for m in HIDE:
        cmd += ["--hide-submesh", m]
    for m, t in SUBTEX.items():
        cmd += ["--submesh-texture", f"{m}={t}"]
    cmd += ["--pitch", "20", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", "0.6",
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
    """Her sprite now as a flat silhouette at PPU 3 (each game pixel 18 px), soles on row SOLE, centred."""
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
    d.text((24, 24), f"hair-bun tips to the soles {full} px ({round(spr.height * PPU)} squares of {SQ}); layout only",
           fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "7_layout.png"))
    print("layout", a.size, "at", ox, SOLE - full)


def splash(lol, out):
    from riot import Wad
    import pose_ref
    wad = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", "Zeri.wad.client"))
    for tex in ("ZeriLoadScreen.tex", "ZeriLoadScreen_0.tex"):
        try:
            data = wad.read_path(f"ASSETS/Characters/Zeri/Skins/Base/{tex}".lower())
        except KeyError:
            continue
        pose_ref.read_tex(data).convert("RGB").save(out)
        return
    sys.exit("no loading-screen art in Zeri.wad.client")


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
    splash(a.lol, os.path.join(refs, "4_zeri_splash.png"))
    render(a.lol, "5_zeri_chibi", (30, 1000, 1.4, "box", IDLE), refs, chibi=("1.6", "0.9"))   # (poses.json chibi)
    now = SP.sheet_frame(os.path.join(CHAMPS, "league_zeri"), "idle_base")
    SP.sheet_frame(os.path.join(CHAMPS, "league_zeri"), "hd_idle_base", 3).save(   # (the pose and the size only)
        os.path.join(refs, "6_zeri_now.png"))
    guide(refs, now)
    for n, hero in (("8_style_veigar", "league_veigar"), ("9_style_seraphine", "league_seraphine"),
                    ("10_style_ezreal", "league_ezreal")):
        SP.sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(SP.lp(os.path.join(SRC, "zeri", "PICTURE_PROMPT_PPU.md")),
                    os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| her sprite now", now.size)


if __name__ == "__main__":
    main()
