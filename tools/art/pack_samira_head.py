"""The Codex pack that redraws Samira's v2 picture with a smaller head (the user, 2026-10-25, on her PPU 2.84 design:
「这头怎么这么大」): her crown to chin is 32 % of her crown to soles, the target 26 % (Annie's 27 %); the same
picture otherwise - pose, sword, costume, colours, square size and total height - the freed rows going to her torso and
legs. A proportion change is a drawing job (a head cut row by row breaks the sword and the braid behind it).

    python tools/art/pack_samira_head.py --out C:/t/sm_head [--refs C:/t/sm_pack/refs]

<out>/PICTURE_PROMPT.md (assets/source/samira/PICTURE_PROMPT_HEAD.md), refs/1 her v2 picture (hd/raw/
samira-lol-refined.png: THE picture), refs/2 the guide (the picture with its crown, chin now, chin wanted and soles
lines), refs/3-4 League's idle render and head close-up from the design pack (Riot's, kept local), then <out>.zip.
"""
import argparse
import os
import shutil

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(HERE)), "assets", "source", "samira")
CROWN, CHIN, SOLES = 424, 775, 1519          # her v2 picture's rows (alpha >= 128; the chin by eye on the picture)
SHARE = 0.26                                 # crown to chin wanted, of crown to soles


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--refs", default="C:/t/sm_pack/refs")
    a = ap.parse_args()
    refs = os.path.join(a.out, "refs")
    os.makedirs(refs, exist_ok=True)
    pic = Image.open(lp(os.path.join(SRC, "hd", "raw", "samira-lol-refined.png"))).convert("RGBA")
    pic.save(os.path.join(refs, "1_samira_v2.png"))
    want = round(CROWN + SHARE * (SOLES - CROWN))
    g = Image.new("RGBA", pic.size, (225, 225, 225, 255))
    g.alpha_composite(pic)
    d = ImageDraw.Draw(g)
    for y, col, text in ((CROWN, (60, 60, 60), "crown (keep)"), (CHIN, (220, 40, 40), "chin NOW (head too big)"),
                         (want, (30, 160, 60), "chin WANTED (smaller head)"), (SOLES, (60, 60, 60), "soles (keep)")):
        d.line([(0, y), (pic.width, y)], fill=col + (255,), width=3)
        d.text((8, y + 4), text, fill=col + (255,))
    g.convert("RGB").save(os.path.join(refs, "2_guide.png"))
    for n, src in (("3_samira_league_idle.png", "1_samira_idle.png"), ("4_samira_league_head.png", "2_samira_head.png")):
        shutil.copyfile(os.path.join(a.refs, src), os.path.join(refs, n))
    shutil.copyfile(lp(os.path.join(SRC, "PICTURE_PROMPT_HEAD.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    print("chin", CHIN, "->", want, "| written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()
