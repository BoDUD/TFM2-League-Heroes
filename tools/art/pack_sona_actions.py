"""The Codex pack for league_sona's actions drawn whole at PPU 3.88 (assets/source/sona/ACTIONS_PROMPT_PPU.md): every
frame of her run, attack, power chord (attack_p), skill, skill2, R Crescendo (ult), hit and death a new drawing of the
approved design (hd/design.png: the user's picture read on its 5.5-px squares, 117 x 155 squares - the user,
2026-10-30: 「通过，用 3.88」) in the pose of her OLD sheet's same frame, tools/art/pack_leona_actions.py's way.

    python tools/art/pack_sona_actions.py --out C:/t/so_actions

The etwahl goes where the old frame has it: level before her waist, both hands on it (her far hand lifted to pluck
the strings in the attacks, both arms swept wide over it in skill); in R's frames 3-5 it floats high over her head,
apart from her, while she stands beneath it with her arms raised; in the death it sinks with her and lies before her.
She glides: the gown hides her feet in every frame, so the run is a sway and bob of the gown, not steps (RUN_LEGS).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from skill and
attack_p). The old frames that are her idle pose itself (the first and last of run, the attacks and the skills, R 1
and 8, hit 2) are the design (SAME); R 6 is R 2. So 36 are drawn. Nothing is baked into her body tags. Each template
sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame scaled to her
height (PPU squares a pixel, SQ px a square - R's etwahl 57 px over her hem at SQ_OF's smaller squares), faded, as the pose to follow, standing on the ground line at the
standing point, and a bar as tall as she stands. refs/design_picture.png is the user's picture itself (the style the
user wants matched). Then <out>.zip.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import pack_riven_actions as PR  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "sona")
TAGS = ["run", "attack", "attack_p", "skill", "skill2", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into her body tags)
NAMES = {"run": "moving (her move loop): she GLIDES, the etwahl level before her waist, both hands on it, the gown "
                "swaying and the twin tails bobbing with each step hidden under the gown",
         "attack": "attack: she lifts her far hand over the etwahl's right end, plucks the strings and lowers it",
         "attack_p": "power chord (empowered attack): she lifts her far hand high over the etwahl's right end and "
                     "strikes the strings hard, then lowers it",
         "skill": "skill: she sweeps both arms out wide over the strings, from the middle to the etwahl's two ends, "
                  "and brings them back",
         "skill2": "skill 2: she lifts her far hand over the etwahl's right end and plucks a long note, then lowers it",
         "ult": "Crescendo (R): she lifts the etwahl (frame 2), flings it up to float high OVER HER HEAD, apart from "
                "her, while she stands beneath it with her arms raised, conducting (frames 3-5), and takes it back "
                "before her waist (frame 7)",
         "hit": "struck: jolted back, the etwahl still before her",
         "dead": "death: struck, she sinks down, her gown spreading over the ground, the etwahl sinking with her, and "
                 "ends lying face down behind the etwahl, only her head and the etwahl showing over the gown"}
HARP = ("THE ETWAHL AND THE HANDS go where the pale figure has them, frame by frame (image 3 shows them in colour): the "
        "GOLD ETWAHL level before her waist, its two curled gold ends out past her body, the strings in the middle; "
        "her hands on it, or lifted over it where the pale figure lifts them. Only ONE etwahl, the design's.")
WEAPONS = {t: HARP for t in NAMES}
WEAPONS["ult"] = HARP + (" In frames 3-5 the etwahl FLOATS HIGH OVER HER HEAD, apart from her (a gap between them), "
                         "drawn where the pale figure has it; she stands beneath it, her arms raised, her whole gown "
                         "showing.")
WEAPONS["dead"] = HARP + (" It sinks with her and lies before her as the pale figure; in the last frames only her head "
                          "and the etwahl show over the spread gown.")
# She glides: the old run has no legs (the gown hides them), so the frames are named by the gown's sway
RUN_LEGS = {k: "no legs: the gown hides them as in the pale figure; the gown's hem and the twin tails sway with the step"
            for k in range(1, 9)}
RUN_SWAP = ("The gown and the twin tails SWAY frame by frame as the pale figures show - never the same picture in "
            "every frame; the body bobs gently.")
# old frames that are another frame pixel for pixel (checked on the old sheet / the native cells, cropped to the
# figure): drawn once, here (tag, frame), 1-based; DESIGN: her idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
_ID = {"run": [1, 8], "attack": [1, 6], "attack_p": [1, 6], "skill": [1, 6], "skill2": [1, 6], "ult": [1, 8],
       "hit": [2]}
SAME = {t: {k: DESIGN for k in ks} for t, ks in _ID.items()}
SAME["ult"][6] = ("ult", 2)
SQ = 5                                   # px a design square in the templates (her 155 rows in the sheet)
SQ_OF = {"ult": 3.8}                     # R flings the etwahl 57 px over her hem: smaller squares to stay in the sheet
PPU = 155 / 40                           # design squares an old pixel (hd/design.png: 155 rows, her 1x 40)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 155                              # design rows from the top of her hair to the hem
OLD_SOLES = 11.5                         # old frames: the soles this many pixels under the frame's centre (its pivot)
MARGIN = 30
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    """{tag: [(frame, ms, (pivot x, soles y))]}: the old sheet's frames (pivot: the frame's centre, the soles OLD_SOLES
    under it)."""
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag in TAGS:
        fr = []
        for f_ in anims[tag]["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000), (w / 2, h / 2 + OLD_SOLES)))
        out[tag] = fr
    return out


def cell_fit(frame, sq):
    xs = np.nonzero(frame[0][..., 3].any(0))[0]
    return (xs.max() + 1 - xs.min()) * PPU * sq + 2 * MARGIN <= SHEET_W / 2


def placed(frame, x0, cw, sq):
    """The old frame scaled to her height in a cell [x0, x0 + cw): its pivot on the standing point (the cell's middle),
    its soles on the ground line, kept inside the cell. -> (RGBA image, left, top)."""
    a, _, (pvx, pvy) = frame
    k = PPU * sq
    h, w = a.shape[:2]
    im = Image.fromarray(a).resize((round(w * k), round(h * k)), Image.NEAREST)
    left = round(x0 + cw / 2 - pvx * k)
    top = round(GROUND - pvy * k)
    bb = im.getbbox()
    if bb:
        lo, hi = left + bb[0], left + bb[2]
        if lo < x0 + MARGIN:
            left += x0 + MARGIN - lo
        elif hi > x0 + cw - 14:
            left -= hi - (x0 + cw - 14)
        if top + bb[1] < 8:
            raise SystemExit(f"a frame reaches {8 - top - bb[1]} px over the template's top: lower SQ_OF")
    return im, left, top


def template(path, frames, nums, sq):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), (255, 255, 255, 255))
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw, sq)
        a = np.asarray(im).astype(float)
        faded = a.copy()
        faded[..., :3] = a[..., :3] * 0.35 + 255 * 0.65                  # a pale picture of the pose
        can.alpha_composite(Image.fromarray(faded.astype(np.uint8)), (left, top))
    dr = ImageDraw.Draw(can)
    for i in range(len(frames)):
        x0 = i * cw
        cx = x0 + cw / 2
        dr.rectangle([x0, 0, x0 + cw - 1, H - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + cw - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 16
        dr.line([(bx, GROUND), (bx, GROUND - STAND * sq)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * sq - 4), "her height standing (the top of her hair)",
                fill=(120, 120, 120), font=PR.font(16))
        dr.text((x0 + 14, 12), f"frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(path)


def old_ref(frames, nums, out, sq):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw, sq)
        can.alpha_composite(im, (left, top))
        dr.text((i * cw + 14, 12), f"old frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def groups(frs, skip, sq):
    """[([numbers], [frames])] of the frames to draw (none in `skip`): two to a sheet while both fit a half."""
    todo = [(k + 1, f) for k, f in enumerate(frs) if k + 1 not in skip]
    out, k = [], 0
    while k < len(todo):
        if k + 1 < len(todo) and cell_fit(todo[k][1], sq) and cell_fit(todo[k + 1][1], sq):
            pair = todo[k:k + 2]
            k += 2
        else:
            pair = todo[k:k + 1]
            k += 1
        out.append(([n for n, _ in pair], [f for _, f in pair]))
    return out


def figure(a):
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def idle_sheet():
    """Her idle pose on the old sheet: idle_base 1."""
    px = np.asarray(Image.open(PR.lp(os.path.join(SRC, "hd", "old", "sheet.png"))).convert("RGBA"))
    with open(PR.lp(os.path.join(SRC, "hd", "old", "anim.fanim")), encoding="utf-8-sig") as f:
        d = json.load(f)["anims"]["idle_base"]["frames"][0]["data"]
    x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
    return px[y:y + h, x:x + w]


def check_same(old):
    """Every SAME pair is the same picture on the old sheet (a later edit of SAME must not join two poses)."""
    for tag, m in SAME.items():
        for k, (t2, k2) in m.items():
            a = figure(old[tag][k - 1][0])
            bs = [figure(idle_sheet())] if (t2, k2) == DESIGN else [figure(old[t2][k2 - 1][0])]
            if not any(a.shape == b.shape and (a == b).all() for b in bs):
                sys.exit(f"SAME {tag} {k} = {t2} {k2}: not the same old frame")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-sheet", default=os.path.join(SRC, "hd", "old", "sheet.png"))
    ap.add_argument("--old-fanim", default=os.path.join(SRC, "hd", "old", "anim.fanim"))
    ap.add_argument("--only", help="tags to pack, comma-separated (the redo of one action: --only run)")
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/sona")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    old = old_frames(PR.lp(a.old_sheet), PR.lp(a.old_fanim))
    check_same(old)
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 6, bg.height * 6), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "sona-A.png"))).convert("RGBA")
    pic.putalpha(pic.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    pic = pic.crop(pic.getbbox())
    bg = Image.new("RGBA", (pic.width + 40, pic.height + 40), GREY + (255,))
    bg.alpha_composite(pic, (20, 20))
    bg.convert("RGB").save(os.path.join(refs, "design_picture.png"))
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    sheets = []
    for tag in (a.only.split(",") if a.only else TAGS):
        sq = SQ_OF.get(tag, SQ)
        for n, (nums, part) in enumerate(groups(old[tag], set(SAME.get(tag, {})), sq)):
            name = f"{tag}_{n + 1}"
            template(os.path.join(tpl, name + ".png"), part, nums, sq)
            old_ref(part, nums, os.path.join(refs, f"old_{name}.png"), sq)
            sheets.append(dict(tag=tag, name=name, frames=nums, cells=len(part), square=sq, action=NAMES[tag],
                               ms=[ms for _, ms, _ in part], weapons=WEAPONS[tag]))
            if tag == "run":
                sheets[-1]["legs"] = " ".join(f"Frame {k}: {RUN_LEGS[k]}." for k in nums) + " " + RUN_SWAP
    same = {t: {str(k): f"{t2} {k2}" for k, (t2, k2) in m.items()} for t, m in SAME.items()}
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "square_of": SQ_OF, "sheet": [SHEET_W, H], "ground": GROUND, "same": same, "baked_body_frames": BAKED,
                   "sheets": sheets}, f, indent=1, ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, a.prompt)), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
