"""The Codex pack for league_briar's actions drawn whole at PPU 2.94 (assets/source/briar/ACTIONS_PROMPT_PPU.md): every
frame of her run, attack, Q Head Rush (skill), W Blood Frenzy (skill2), E Chilling Scream (skill2_scream), R Certain
Death (ult, ult_fly, ult_land), hit, death and the Snack bite (attack_fx1: a body animation the kit plays on her, not an
effect) a new drawing of the approved design (hd/design.png: Codex's briar-A read on ~8.5-px squares, 110 x 135 - the
user, 2026-10-30: 「算了用2.94吧」) in the pose of her OLD sheet's same frame, tools/art/pack_sona_actions.py's way.

    python tools/art/pack_briar_actions.py --out C:/t/br_actions

The pillory goes where the old frame has it: locked round her neck with both wrists in its two ends, the hands sticking
out, always one pillory; it leads her head first through Head Rush's leap and R's flight. The run's legs follow the
pale figures (RUN_LEGS).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from skill2_scream and
skill2). The old frames that are her idle pose itself (the last of attack, skill, skill2_scream, ult and ult_land, hit
2) are the design (SAME). So 56 are drawn. Nothing is baked but the Snack's few blood drops at her mouth. Each template
sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame scaled to her
height (PPU squares a pixel, SQ px a square - Head Rush's flat leap, 99 px wide, at SQ_OF's smaller squares), faded, as
the pose to follow, standing on the ground line at the standing point, and a bar as tall as she stands.
refs/design_picture.png is Codex's own briar-A, the picture the design was read from (its fine eyes and studs). Then
<out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "briar")
TAGS = ["run", "attack", "skill", "skill2", "skill2_scream", "ult", "ult_fly", "ult_land", "hit", "dead", "attack_fx1"]
BAKED = []                              # (nothing baked into her body tags)
NAMES = {"run": "running (her move loop): a wild, eager run, the pillory on her shoulders, her locked hands out to "
                "the sides, the LEGS STEPPING IN TURN, the hair bouncing",
         "attack": "attack: she crouches, LEAPS forward low and bites ahead of her to the right (frames 3-4: stretched "
                   "out in the air, the far leg kicked back), then lands and stands",
         "skill": "Head Rush (Q): she crouches, leaps HEAD FIRST through the air stretched out FLAT, the pillory "
                  "leading (frames 3-5), and lands",
         "skill2": "Blood Frenzy (W): she crouches low, then rises into a wide, wild stance, swaying, ready to pounce",
         "skill2_scream": "Chilling Scream (E): she braces and SCREAMS, leaning forward with her mouth wide open "
                          "(frames 2-3), and straightens",
         "ult": "Certain Death (R): she lifts a knee and KICKS high forward (frame 3), stamps down and crouches, "
                "ready to fly",
         "ult_fly": "Certain Death's flight (R): she FLIES forward to the right, stretched out FLAT in the air, the "
                    "pillory leading, the legs trailing behind",
         "ult_land": "Certain Death's landing (R): she lands from the flight crouching low, then rises to stand",
         "hit": "struck: jolted back, her eyes squeezed shut",
         "dead": "death: struck, she staggers, sinks to her knees, falls forward and ends lying flat on the ground, "
                 "the pillory still on her",
         "attack_fx1": "the Snack (her healing bite): she LUNGES forward stretched out and bites, a few RED BLOOD "
                       "drops at her mouth (frames 1-3), then lands and stands, blood on her chin (frames 4-7)"}
PILLORY = ("THE PILLORY AND THE HANDS go where the pale figure has them, frame by frame (image 3 shows them in "
           "colour): the DARK IRON PILLORY always locked round her neck, BOTH WRISTS locked in its two ends, the hands "
           "sticking out; it tilts and turns with her as the pale figure's does. Only ONE pillory, the design's.")
WEAPONS = {t: PILLORY for t in NAMES}
WEAPONS["skill"] = PILLORY + (" In frames 3-5 she flies HEAD FIRST, stretched out flat, the pillory ahead of her "
                              "body, as the pale figure.")
WEAPONS["ult_fly"] = PILLORY + " She flies stretched out flat, the pillory ahead of her body, as the pale figure."
# The run's legs, each frame following its pale figure
RUN_LEGS = {k: "the legs exactly as the pale figure: one foot planted, the other lifted or swinging" for k in range(1, 9)}
RUN_SWAP = ("The two legs TAKE TURNS frame by frame as the pale figures show - never the same leg pose in every frame, "
            "never both legs stretched apart in every frame; the body bobs with the steps.")
# old frames that are another frame pixel for pixel (checked on the old sheet / the native cells, cropped to the
# figure): drawn once, here (tag, frame), 1-based; DESIGN: her idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
_ID = {"attack": [6], "skill": [6], "skill2_scream": [4], "ult": [6], "ult_land": [5], "hit": [2]}
SAME = {t: {k: DESIGN for k in ks} for t, ks in _ID.items()}
SQ = 6                                   # px a design square in the templates (her 135 rows in the sheet)
SQ_OF = {"skill": 5}                     # Head Rush flies 99 px wide: smaller squares to stay in the sheet
PPU = 135 / 46                           # design squares an old pixel (hd/design.png: 135 rows, her 1x 46)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 135                              # design rows from the top of the pillory to her soles
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
        dr.text((bx + 8, GROUND - STAND * sq - 4), "her height standing (the top of the pillory)",
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/briar")
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
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "briar-A.png"))).convert("RGBA")
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
