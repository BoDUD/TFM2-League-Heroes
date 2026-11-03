"""The Codex pack for league_aatrox's actions drawn whole at PPU 2.27 (assets/source/aatrox/ACTIONS_PROMPT_PPU.md): every
frame of his actions - his attack, Deathbringer Stance (attack_p), Q The Darkin Blade's three casts (skill, q2, q3), W
Infernal Chains (skill2), R World Ender (ult) and the same actions in World Ender's form with his wings spread (the _r
tags), run, hit and death - a new drawing of the approved design (hd/design.png: Codex's aatrox-A read on ~12-px
squares, 97 x 91 - the user, 2026-11-03: 「凯南1.81 梦魇1.8 剑魔2.27 丽桑卓1.81」) in the pose of his OLD sheet's same frame,
tools/art/pack_ryze_actions.py's way, one PR with the other seven.

    python tools/art/pack_aatrox_actions.py --out C:/t/aatrox_actions

The weapon and hands go where the old frame has them (WEAPONS); the old frames' baked effects are not drawn. The run's
legs change over (RUN_LEGS, named from the start).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from the actions), the
*_fx1 / *_fx2 / skill_fx3 copies of the Q casts and W with their dashes, slashes and chains
(assets/source/native/aatrox_bake.json lays them on again). Old frames that are another frame pixel for pixel are drawn
once (SAME). BAKED: eight old tags carry their slashes, fire and chains (aatrox_bake.json): their native body cells are
drawn (pack_akali_actions.py's way: assets/source/native/aatrox_cells.json, at 1x on their own pivots). Each template
sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame scaled to his height
(PPU squares a pixel, SQ px a square), faded, as the pose to follow, standing on the ground line at the standing point,
and a bar as tall as he stands. refs/design_picture.png is Codex's own aatrox-A, the picture the design was read from
(its fine detail). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "aatrox")
NATIVE = os.path.join(REPO, "assets", "source", "native")
TAGS = ["run", "attack", "attack_p", "skill", "q2", "q3", "skill2", "ult", "hit", "dead", "attack_r", "attack_p_r", "skill_r", "q2_r", "q3_r", "skill2_r"]
BAKED = ["attack_p", "attack_p_r", "q3", "q3_r", "q2", "q2_r", "skill_r", "skill2_r"]    # eight old tags carry their slashes, fire and chains (aatrox_bake.json): the native body cells
NAMES = {
    "run": ("running (his move loop): a heavy run, the greatsword held low, the LEGS CHANGING OVER"),
    "attack": ("attack: he swings the greatsword (frames 2-5)"),
    "attack_p": ("Deathbringer Stance (the empowered strike): he raises the sword and swings it in a wide arc, frame "
        "by frame as the pale figure"),
    "skill": ("The Darkin Blade, first cast (Q1): he lifts the sword over his head, leaps and slams it down (frames"
        " 1-8)"),
    "q2": ("The Darkin Blade, second cast (Q2): he winds up and sweeps the sword across low, frame by frame as "
        "the pale figure"),
    "q3": ("The Darkin Blade, third cast (Q3): he leaps high, the sword raised over his head, and slams it into "
        "the ground, frame by frame as the pale figure"),
    "skill2": ("Infernal Chains (W): he flings his free hand forward, throwing the chains (frames 2-4)"),
    "ult": ("World Ender (R): he spreads his WINGS wide and rises up (frames 1-8), the wings opening more frame "
        "by frame"),
    "hit": ("struck: jolted back"),
    "dead": ("death: struck (frames 2-3), he falls back and lies flat, the sword on the ground (frames 4-6)"),
    "attack_r": ("attack in World Ender's form (his WINGS SPREAD WIDE): he swings the greatsword (frames 1-5)"),
    "attack_p_r": ("Deathbringer Stance in World Ender's form (WINGS SPREAD WIDE): the wide sword arc, frame by frame as"
        " the pale figure"),
    "skill_r": ("Q1 in World Ender's form (WINGS SPREAD WIDE): the sword lifted, the leap and the slam, frame by "
        "frame as the pale figure"),
    "q2_r": ("Q2 in World Ender's form (WINGS SPREAD WIDE): the wind-up and the low sweep, frame by frame as the "
        "pale figure"),
    "q3_r": ("Q3 in World Ender's form (WINGS SPREAD WIDE): the high leap and the slam, frame by frame as the pale"
        " figure"),
    "skill2_r": ("Infernal Chains in World Ender's form (WINGS SPREAD WIDE): the free hand flung forward, frame by "
        "frame as the pale figure"),
}
ARMS = ("HIS HANDS AND THE GREATSWORD go where the pale figure has them, frame by frame (image 3 shows them in "
        "colour): the huge dark red greatsword, as long as in image 1, held, raised, swung or slammed as the pale "
        "figure holds it. HIS WINGS as the pale figure's: as in image 1 in his normal form, SPREAD WIDE in World "
        "Ender (the ult, and every action whose name ends in _r). The pale figure's fire, sparks, chains and "
        "eruptions are the old frame's effects: do NOT draw them. Only him: no fire, no blood mist, no afterimages; "
        "the red light stays in his chest core.")
WEAPONS = {t: ARMS for t in NAMES}
# The run's legs, frame by frame (Talon's first run kept one leg in front in every frame: 「走路没有换腿」;
# so did Codex's first run of Senna's: named here from the start); he runs to the right, "back" is the image's left
RUN_LEGS = {
    1: "SUPPORT ON THE NEAR LEG: the NEAR leg (the lighter one) planted straight down under his hips, its foot flat on "
       "the ground; the FAR leg (the darker one) kicked up and back behind him, bent, its foot high off the ground",
    2: "SUPPORT ON THE NEAR LEG: the near leg still planted under his hips, bending; the far leg swinging down from "
       "behind, its foot off the ground behind the planted one",
    3: "PASSING: both legs gathered under him, knees bent; the FAR leg passing forward close beside the planted near "
       "leg, its foot just off the ground",
    4: "STRIDE: the FAR leg reaching forward (image right) to land, its heel coming down; the NEAR leg behind (image "
       "left) pushing off, its toes on the ground",
    5: "SUPPORT ON THE FAR LEG: now the FAR leg (the darker one) planted straight down under his hips, its foot flat on "
       "the ground; the NEAR leg (the lighter one) kicked up and back behind him, bent, its foot high off the ground",
    6: "SUPPORT ON THE FAR LEG: the far leg still planted under his hips, bending; the near leg swinging down from "
       "behind, its foot off the ground behind the planted one",
    7: "PASSING: both legs gathered under him, knees bent; the NEAR leg passing forward close beside the planted far "
       "leg, its foot just off the ground",
    8: "STRIDE: the NEAR leg reaching forward (image right) to land, its heel coming down; the FAR leg behind (image "
       "left) pushing off, its toes on the ground",
}
RUN_SWAP = ("The two legs TAKE TURNS: in frames 1-4 the NEAR leg (the lighter one) carries him and the FAR leg comes "
            "forward, in frames 5-8 the FAR leg (the darker one) carries him and the NEAR leg comes forward - frames 1 "
            "and 5 must look different: a different leg planted, the other one kicked back. Never the same leg in "
            "front in every frame (Senna's first run did that, and Talon's: 「走路没有换腿」).")
# old frames that are another frame pixel for pixel (checked on the old sheet, cropped to the figure): drawn once,
# here (tag, frame), 1-based; DESIGN: her idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {"attack": {1: DESIGN, 6: DESIGN}, "attack_p": {6: DESIGN}, "q2": {8: ('skill', 8)}, "q3": {8: ('skill', 8)},
        "skill2": {1: DESIGN, 5: ('skill2', 4), 6: DESIGN}, "dead": {1: DESIGN, 7: ('dead', 6), 8: ('dead', 6)},
        "attack_r": {6: ('ult', 8)}, "attack_p_r": {6: ('ult', 8)}, "skill_r": {8: ('ult', 8)}, "q2_r": {8: ('ult', 8)},
        "q3_r": {8: ('ult', 8)}, "skill2_r": {1: ('attack_r', 1), 6: ('ult', 8)}}
SQ = 7                                   # px a design square in the templates (his 91 rows in the sheet)
SQ_OF = {"skill": 6, "q2": 6, "dead": 6, "skill_r": 6, "q2_r": 6, "q3": 5, "q3_r": 5}   # (the leaps and the
                                         # flung sword reach 940-1226 px over the ground at 7: smaller to stay in the sheet)
PPU = 91 / 40                            # design squares an old pixel (hd/design.png: 91 rows, his 1x 40)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 91                               # design rows from his highest point to his soles
OLD_SOLES = 11.5                         # old frames: the soles this many pixels under the frame's centre (its pivot)
CELL_SOLES = 12                          # native cells: their pivot is the frame's centre too, the soles 12 px under it
MARGIN = 30
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    """{tag: [(frame, ms, (pivot x, soles y))]}: the old sheet's frames (pivot: the frame's centre, the soles OLD_SOLES
    under it), BAKED tags from their native body cells at 1x (each cell's own pivot, aatrox_cells.json, the soles
    CELL_SOLES under it)."""
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    with open(os.path.join(NATIVE, "aatrox_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    out = {}
    for tag in TAGS:
        fr = []
        if tag in BAKED:
            strip = Image.open(PR.lp(os.path.join(NATIVE, f"aatrox_{tag}.png"))).convert("RGBA")
            cw, ch = (v * cells.get("scale", 8) for v in cells["cell"])   # (8 when the cells json leaves it out: kennen_cells.json)
            per_row = strip.width // cw
            for k, c in enumerate(cells["tags"][tag]):
                r, q = divmod(k, per_row)
                a = np.asarray(strip.crop((q * cw, r * ch, (q + 1) * cw, (r + 1) * ch))
                               .resize(tuple(cells["cell"]), Image.BOX)).copy()
                a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
                a[a[..., 3] == 0] = 0
                fr.append((a, c["ms"], (c["pivot"][0], c["pivot"][1] + CELL_SOLES)))
        else:
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
    """The old frame scaled to his height in a cell [x0, x0 + cw): its pivot on the standing point (the cell's middle),
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
        dr.text((bx + 8, GROUND - STAND * sq - 4), "his height standing (his highest point)",
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
    """His idle pose on the old sheet: idle_base 1."""
    px = np.asarray(Image.open(PR.lp(os.path.join(SRC, "hd", "old", "sheet.png"))).convert("RGBA"))
    with open(PR.lp(os.path.join(SRC, "hd", "old", "anim.fanim")), encoding="utf-8-sig") as f:
        d = json.load(f)["anims"]["idle_base"]["frames"][0]["data"]
    x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
    return px[y:y + h, x:x + w]


def check_same(old):
    """Every SAME pair is the same picture on the old sheet - a later edit of SAME must not join two poses."""
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
    ap.add_argument("--sheets", help="of those, only these sheets, comma-separated (the redo: run_1,...,skill_1)")
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/aatrox")
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
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "aatrox-A.png"))).convert("RGBA")
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
            if a.sheets and name not in a.sheets.split(","):
                continue
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
