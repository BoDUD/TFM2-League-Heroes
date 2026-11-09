"""The Codex pack for league_milio's PPU redo (assets/source/milio/PICTURE_PROMPT_PPU.md): one design picture on the
6-px grid at about PPU 3 - the boy of his sprite now WITH League's backpack, which his sprite lacks (the user,
2026-11-09: 「再补一个吧 米利欧 现在我们做的背后没有葫芦」): the gentle flame: the boy as he is now - the fluffy dark indigo curls, the big
amber eyes and the grin, the red tunic with the golden shoulder pads and cream tassels, the teal sash, the magenta kilt,
the sandals, his round fire spirit - WITH League's BIG GOURD-SHAPED BACKPACK (cream canvas with teal scale bands and
gold trims under a teal cap, wound with a thick purple rope whose two ends he holds at his chest, on a wooden frame).

    python tools/art/pack_milio_ppu.py --out C:/t/ml_pack [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..3 (League renders through tools/lol/pose_ref.py, the camera yaw 65 pitch
20: 1 = his idle, 2 = his head close up, 3 = from behind, not mirrored; Riot's, kept local, never committed), refs/4
(League's loading-screen art), refs/5 (League's model WITH the backpack in this game's chibi proportions, poses.json
chibi: head 1.35, legs 0.9), refs/6 (the front design his sprite was made from, assets/source/milio/hd/front.png at 6x -
one square 6 px, this pack's grid: the boy's look, his fire spirit, the pose and the size), refs/7 (the layout guide:
the boy alone, hd/front_boy.png, as a flat silhouette at that size) and <out>/style/8..10 (this pack's Veigar, Seraphine
and Ezreal at their hd_idle, 8x), then <out>.zip. The renders hide by name (HIDE) the bin's own initialSubmeshToHide
(the spirit buddies BuddyA / BuddyB and their eyes) and the fire buddy's face in the backpack's back window (FireBuddy
eyes and mouth: shown in League, but flipbook maps pose_ref would draw as a whole atlas), and give the backpack its own
map (SUBTEX): poses.json's hide_submeshes (pose_ref --hide-submeshes) hid the backpack too - pose_ref.hidden_submeshes
takes every bin string made only of submesh names, and the material override naming the Backpack alone is one.
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
IDLE = "spell4_idle_in@600"                              # League's idle (poses.json "design")
HIDE = ["BuddyA", "BuddyB", "BuddyA_Eyes", "BuddyB_Eyes", "FireBuddy_Eye_Left", "FireBuddy_Eye_Right",
        "FireBuddy_Mouth"]   # (the bin's initialSubmeshToHide, BuddyA/B, + the fire buddy's flipbook face)
SUBTEX = {"Backpack": "Milio_Base_Backpack_TX_CM"}   # (the backpack's own map, not the body's)
FLAGS = []  # (the bin's own hide list by name: HIDE; --hide-submeshes hid the backpack too)
# name -> (yaw, size, width, crop "box" or fractions of the figure's box, frame); not mirrored (the camera)
RENDERS = {
    "1_milio_idle": (65, 1000, 1.4, "box", IDLE),
    "2_milio_head": (65, 2400, 1.2, (0.42, 0.0, 1.0, 0.38), IDLE),
    "3_milio_back": (245, 1000, 1.4, "box", IDLE),
}
CANVAS = (1024, 1024)                               # (the size: the hair top to the soles, guide())
SOLE = 960                                          # the soles' row
SQ = 6
PPU = 3.0


def render(lol, name, spec, out, chibi=("1.0", "1.0", "1.0")):
    yaw, size, width, crop, frame = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Milio",
           "--hq", "--head", chibi[0], "--legs", chibi[1], "--hair", chibi[2]] + FLAGS
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
    """The boy now as a flat silhouette on this pack's grid, soles on row SOLE: his front design without the spirit
    (boy()), one square 6 px - as tall as refs/6 - a quarter of his width right of centre (the backpack goes on his
    left). `spr` (his 1x sprite now) for the rows only."""
    shape = boy()
    full = shape.height * SQ
    a = shape.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    a = a.resize((shape.width * SQ, full), Image.NEAREST)
    sil = Image.new("RGBA", a.size, (150, 160, 185, 255))
    sil.putalpha(a)
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    ox = (CANVAS[0] - a.width) // 2 + a.width // 4          # (room for the backpack on his left)
    can.alpha_composite(sil, (ox, SOLE - full))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(110, 110, 110, 255), width=2)
    d.line([(0, SOLE - full), (CANVAS[0], SOLE - full)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), f"hair top to the soles {full} px ({shape.height} squares of {SQ}, his {spr.height} rows); "
           "layout only: the boy without his spirit; the backpack goes on his left",
           fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "7_layout.png"))
    print("layout", a.size, "at", ox, SOLE - full)


def design_now(out):
    """The front design his sprite was made from (hd/front.png: the idle's boy and his fire spirit on Codex's own grid,
    one square a pixel) at 6x on grey - the look on this pack's 6-px grid."""
    im = Image.open(SP.lp(os.path.join(SRC, "milio", "hd", "front.png"))).convert("RGBA")
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * SQ, pad.height * SQ), Image.NEAREST).save(out)
    print("design now", im.size)


def boy():
    """The boy alone as his idle has him (hd/front_boy.png: the front design without the spirit, a layer of its own)."""
    im = Image.open(SP.lp(os.path.join(SRC, "milio", "hd", "front_boy.png"))).convert("RGBA")
    return im.crop(im.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox())


def splash(lol, out):
    from riot import Wad
    import pose_ref
    wad = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", "Milio.wad.client"))
    for tex in ("MilioLoadScreen.tex", "MilioLoadScreen_0.tex"):
        try:
            data = wad.read_path(f"ASSETS/Characters/Milio/Skins/Base/{tex}".lower())
        except KeyError:
            continue
        pose_ref.read_tex(data).convert("RGB").save(out)
        return
    sys.exit("no loading-screen art in Milio.wad.client")


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
    splash(a.lol, os.path.join(refs, "4_milio_splash.png"))
    render(a.lol, "5_milio_chibi", (65, 1000, 1.4, "box", IDLE), refs,
           chibi=("1.35", "0.9", "1.0"))   # (this game's chibi proportions)
    now = SP.sheet_frame(os.path.join(CHAMPS, "league_milio"), "idle_base")
    design_now(os.path.join(refs, "6_milio_now.png"))   # (the boy's look, his spirit, the pose and the size)
    guide(refs, now)
    for n, hero in (("8_style_veigar", "league_veigar"), ("9_style_seraphine", "league_seraphine"),
                    ("10_style_ezreal", "league_ezreal")):
        SP.sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(SP.lp(os.path.join(SRC, "milio", "PICTURE_PROMPT_PPU.md")),
                    os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| his sprite now", now.size)


if __name__ == "__main__":
    main()
