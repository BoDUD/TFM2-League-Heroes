"""The Codex pack for league_kayn_darkin's PPU redo (assets/source/kayn_darkin/PICTURE_PROMPT_PPU.md): one design
picture on the 6-px grid at PPU 3, TRACED from his game sprite now (Kayn as the Darkin, Rhaast's form: the crimson flesh
under blue-grey steel armour, the helm with its pair of huge curved horns and the two red eyes, the crimson scythe low
in front of him, the same sash, rope belt, trousers and boots as his base form), only denser - Evelynn's way
(tools/art/pack_evelynn_ppu.py), one PR with the others of the batch (the user, 2026-11-05: 「下面重做凯隐 维克托 永恩 泰坦」).

    python tools/art/pack_kayn_darkin_ppu.py --out C:/t/kd_pack [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1 (his darkin picture the user picked,
assets/source/kayn/codex_picture/kayn-darkin.png), refs/2 (its head close up), refs/3 (his base picture,
codex_picture/kayn-model-A.png: the sash, the rope belt, the trousers, the apron and the boots are the same in every
form; League's model hides the forms' armour and blades, so there is no render of the form), refs/4 (League's
loading-screen art), refs/5 (the draft his Darkin design was cut from,
assets/source/kayn/codex_model/kayn_darkin_A_raw.png - the user's pick A), refs/6 (his game sprite now at 8x: THE
picture to trace), refs/7 (the layout guide: his sprite now as a flat silhouette at the new size) and <out>/style/8..10
(this pack's Diana, Ryze and Master Yi at their hd_idle, 8x), then <out>.zip.
"""
import argparse
import os
import shutil
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack_samira_ppu as SP  # noqa: E402

REPO = SP.REPO
SRC, CHAMPS, GREY = SP.SRC, SP.CHAMPS, SP.GREY
PICTURE = os.path.join(SRC, "kayn", "codex_picture", "kayn-darkin.png")   # the form the user picked
BASE_PICTURE = os.path.join(SRC, "kayn", "codex_picture", "kayn-model-A.png")   # his base form
HEADBOX = (0.18, 0.0, 0.85, 0.3)                   # the head close up: fractions of the figure's box
CANVAS = (1024, 1024)                               # (the size: the horn tips to the soles, guide())
SOLE = 960                                          # the soles' row
SQ = 6
PPU = 3.0


def pictures(refs):
    """refs/1: the form's picture the user picked (on grey, cropped to the figure), refs/2: its head close up (HEADBOX:
    fractions of the figure's box), refs/3: his base picture (the parts every form shares)."""
    for name, path, box in (("1_kayn_darkin_picture", PICTURE, None), ("2_kayn_darkin_head", PICTURE, HEADBOX), ("3_kayn_darkin_base", BASE_PICTURE, None)):
        im = Image.open(SP.lp(path)).convert("RGBA")
        x0, y0, x1, y1 = im.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()
        if box is not None:
            w, h = x1 - x0, y1 - y0
            x0, y0, x1, y1 = (x0 + int(box[0] * w), y0 + int(box[1] * h), x0 + int(box[2] * w), y0 + int(box[3] * h))
            im = im.crop((x0, y0, x1, y1))
            im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
        else:
            m = max(x1 - x0, y1 - y0) // 20
            im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
        bg = Image.new("RGBA", im.size, GREY + (255,))
        bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(refs, name + ".png"))
        print(name, bg.size)

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
    d.text((24, 24), f"horn tips to the soles {full} px ({round(spr.height * PPU)} squares of {SQ}); layout only",
           fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "7_layout.png"))
    print("layout", a.size, "at", ox, SOLE - full)


def splash(lol, out):
    from riot import Wad
    import pose_ref
    wad = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", "Kayn.wad.client"))
    for tex in ("KaynLoadScreen.tex", "KaynLoadScreen_0.tex"):
        try:
            data = wad.read_path(f"ASSETS/Characters/Kayn/Skins/Base/{tex}".lower())
        except KeyError:
            continue
        pose_ref.read_tex(data).convert("RGB").save(out)
        return
    sys.exit("no loading-screen art in Kayn.wad.client")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    refs, style = (os.path.join(a.out, d) for d in ("refs", "style"))
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    pictures(refs)
    splash(a.lol, os.path.join(refs, "4_kayn_darkin_splash.png"))
    first = Image.open(SP.lp(os.path.join(SRC, "kayn", "codex_model", "kayn_darkin_A_raw.png"))).convert("RGBA")
    first.putalpha(first.getchannel("A").point(lambda v: 255 if v >= 128 else 0))   # (Codex's soft alpha: its figure)
    first = first.crop(first.getbbox())
    pad = Image.new("RGBA", (first.width + 32, first.height + 32), GREY + (255,))
    pad.alpha_composite(first, (16, 16))
    pad.convert("RGB").save(os.path.join(refs, "5_kayn_darkin_first_design.png"))
    now = SP.sheet_frame(os.path.join(CHAMPS, "league_kayn_darkin"), "idle_base")
    SP.sheet_frame(os.path.join(CHAMPS, "league_kayn_darkin"), "idle_base", 8).save(
        os.path.join(refs, "6_kayn_darkin_now.png"))
    guide(refs, now)
    for n, hero in (("8_style_diana", "league_diana"), ("9_style_ryze", "league_ryze"),
                    ("10_style_masteryi", "league_masteryi")):
        SP.sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(SP.lp(os.path.join(SRC, "kayn_darkin", "PICTURE_PROMPT_PPU.md")),
                    os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| his sprite now", now.size)


if __name__ == "__main__":
    main()
