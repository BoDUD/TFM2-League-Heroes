"""The Codex pack for league_hecarim's actions drawn whole at PPU 1.80 (assets/source/hecarim/ACTIONS_PROMPT_PPU.md):
every frame of his actions - his attack, Q Rampage (skill), E Devastating Charge's gallop and its blow (skill2,
skill2_hit), R Onslaught of Shadows (ult), run, hit and death - a new drawing of the approved design (hd/design.png:
Codex's hecarim-A read on ~10.75-px squares, 131 x 81 - the user, 2026-11-08: 「伊泽瑞尔2.19 其他都1.8」) in the pose of the OLD
sheet's same frame, tools/art/pack_ryze_actions.py's way (pack_blitzcrank_actions.py's latest), one PR with the rest of
batch 7 (奥拉夫 / 伊泽瑞尔 / 赫卡里姆 / 雷克顿).

    python tools/art/pack_hecarim_actions.py --out C:/t/hecarim_actions

The weapon and hands go where the old frame has them (WEAPONS); the old frames' baked effects are not drawn. The run's
four legs follow the pale figure frame by frame (RUN_LEGS, pack_lillia_actions.py's way: in each pair the near and the
far leg change over).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from the actions). Old
frames that are another frame pixel for pixel are drawn once (SAME). Nothing is baked. Each template sheet
(templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame scaled to his height (PPU
squares a pixel, SQ px a square), faded, as the pose to follow, standing on the ground line at the standing point, and a
bar as tall as his standing height. refs/design_picture.png is Codex's own hecarim-A, the picture the design was read
from (its fine detail). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "hecarim")
OLD_SRC = os.path.join(REPO, "assets", "source", "hecarim")   # the old sheet (hd/old)
NATIVE = os.path.join(REPO, "assets", "source", "native")
NATIVE_HERO = "hecarim"                    # the native cells of BAKED tags: <hero>_<tag>.png, <hero>_cells.json
DESIGN_TAG = "idle_base"                  # the old sheet's idle pose (the design): its first frame
RUN_TAG = "run"
TAGS = ["run", "attack", "skill", "skill2", "skill2_hit", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into the body tags)
NAMES = {
    "run": ("running (his move loop): a gallop on his four armoured legs, the halberd held up in front of him with "
        "its blade at the picture's upper right, the cyan ghost-fire tail streaming behind, the FOUR LEGS as the"
        " pale figure has them, frame by frame"),
    "attack": ("attack (the halberd chop): he raises the halberd in front of him, the blade high at the picture's "
        "upper right (frame 1), lifts it straight up over his head (frame 2), swings it back over his head, "
        "the shaft level, the blade pointing back to the picture's left (frame 3), lunges forward, the whole "
        "body stretched low and long, chopping the halberd down to the lower right with its blade near the "
        "ground far in front of him, the tail flying up behind (frame 4), gathers up low, the halberd back "
        "over his shoulder (frame 5), and stands, the halberd up in front of him (frame 6)"),
    "skill": ("Rampage (Q): he spins the halberd round him - swung back over his shoulder, the blade at the upper "
        "left (frame 1), held out level behind him to the picture's left (frames 2-3), swept round in front of"
        " him level to the picture's right (frame 4), swung up to the upper right (frame 5), back over his "
        "head, the blade at the upper left (frame 6) - and stands, the halberd upright at his side (frame 7)"),
    "skill2": ("Devastating Charge, the gallop (E): a long low charge, his body stretched forward, the halberd held "
        "level in front of him like a lance, its blade at the picture's right, the tail streaming behind, the"
        " four legs galloping as the pale figure has them, frame by frame"),
    "skill2_hit": ("Devastating Charge, the blow (E): he rears up, the halberd raised back over his head (frame 1), "
        "rears higher on his hind legs, the front hooves up, the halberd held level overhead (frame 2), "
        "crashes down forward, thrusting the halberd down to the lower right (frame 3), and stands, the "
        "halberd pointing down in front of him (frame 4)"),
    "ult": ("Onslaught of Shadows (R): he crouches, the halberd held low in front, its blade near the ground at the "
        "picture's right (frames 1-2), rears up tall on his hind legs, the halberd thrust straight up over his "
        "head (frame 3), and charges forward, galloping, the halberd level in front of him, the tail streaming "
        "(frames 4-7)"),
    "hit": ("struck: jolted back a little (frame 1; frame 2 = frame 1)"),
    "dead": ("death: his halberd stands planted upright in the ground beside him while he sags (frame 1), rears up "
        "in pain, the arms flung up (frame 2) and rears higher, the head thrown back (frame 3); the halberd "
        "falls flat on the ground in front of him as he stumbles (frame 4), he sinks down, the legs folding "
        "(frame 5) and lies collapsed on the ground, the legs folded under him, the halberd beside him (frame "
        "6; frames 7-8 = frame 6)"),
}
ARMS = ("THE HALBERD goes where the pale figure has it, frame by frame (image 3 shows it in colour): the long dark "
        "shaft and the curved silver blade, as long as in image 1, in his near hand - held up, swung, spun, thrust, "
        "raised overhead or lying on the ground as the pale figure has it. THE CYAN GHOST-FIRE TAIL and the dark "
        "crimson cloth where the pale figure has them. Only him: no ghost riders, no shadows, no slashes, no dust; "
        "the cyan light stays inside his armour's seams and his eyes.")
WEAPONS = {t: ARMS for t in NAMES}
# The run's legs frame by frame, named from the start (the Blitzcrank redo's way, 2026-11-05: deferred to the pale
# figure, Codex drew the same legs in all 8 frames - the user on Talon, 2026-10-31: 「走路没有换腿」): support, swing, passing,
# stride, the other leg from frame 5 (Olaf's 7-frame run: from frame 4; Hecarim's four legs: as the pale figure has
# them, Lillia's way); the run goes to the right, "back" is the picture's left
RUN_LEGS = {
    1: "his FOUR ARMOURED LEGS exactly as the pale figure has them in this frame: in the front pair and in the hind "
       "pair, which leg is in front and which behind, which hooves are on the ground line and which are lifted "
       "(image 3: the near legs lighter, the far legs darker)",
    2: "his FOUR ARMOURED LEGS exactly as the pale figure has them in this frame: in the front pair and in the hind "
       "pair, which leg is in front and which behind, which hooves are on the ground line and which are lifted "
       "(image 3: the near legs lighter, the far legs darker)",
    3: "his FOUR ARMOURED LEGS exactly as the pale figure has them in this frame: in the front pair and in the hind "
       "pair, which leg is in front and which behind, which hooves are on the ground line and which are lifted "
       "(image 3: the near legs lighter, the far legs darker)",
    4: "his FOUR ARMOURED LEGS exactly as the pale figure has them in this frame: in the front pair and in the hind "
       "pair, which leg is in front and which behind, which hooves are on the ground line and which are lifted "
       "(image 3: the near legs lighter, the far legs darker)",
    5: "his FOUR ARMOURED LEGS exactly as the pale figure has them in this frame: in the front pair and in the hind "
       "pair, which leg is in front and which behind, which hooves are on the ground line and which are lifted "
       "(image 3: the near legs lighter, the far legs darker)",
    6: "his FOUR ARMOURED LEGS exactly as the pale figure has them in this frame: in the front pair and in the hind "
       "pair, which leg is in front and which behind, which hooves are on the ground line and which are lifted "
       "(image 3: the near legs lighter, the far legs darker)",
    7: "his FOUR ARMOURED LEGS exactly as the pale figure has them in this frame: in the front pair and in the hind "
       "pair, which leg is in front and which behind, which hooves are on the ground line and which are lifted "
       "(image 3: the near legs lighter, the far legs darker)",
    8: "his FOUR ARMOURED LEGS exactly as the pale figure has them in this frame: in the front pair and in the hind "
       "pair, which leg is in front and which behind, which hooves are on the ground line and which are lifted "
       "(image 3: the near legs lighter, the far legs darker)",
}
RUN_SWAP = ("His four legs TAKE TURNS as in the old run: in the front pair and in the hind pair the near and the far "
            "leg change over during the 8 frames - never the same legs forward in every frame; all four legs armoured"
            " and as long and as thick as in image 1, the dark hooves on them. The body, the helmet, the arms, the "
            "halberd and the tail follow the pale figure.")
# old frames that are another frame pixel for pixel (checked on the old sheet, cropped to the figure): drawn once, here
# (tag, frame), 1-based; DESIGN: his idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {"hit": {2: ('hit', 1)}, "dead": {7: ('dead', 6), 8: ('dead', 6)}}
DISSOLVE = {}
SOLID = set()
SQ = 9                                    # px a design square in the templates (his 81 rows in the sheet)
# tags drawn at smaller squares to stay in the sheet: the halberd raised overhead reaches 80-83 old px over his hooves,
# the charge stretches him 92 old px long
SQ_OF = {"attack": 6, "skill": 7, "skill2": 8, "skill2_hit": 8, "ult": 6}
PPU = 81 / 45                            # design squares an old pixel (hd/design.png: 81 rows, his 1x 45)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 81                               # design rows from the tips of his helmet's horns to his soles
OLD_SOLES = 11.5                         # old frames: the soles this many pixels under the frame's centre (its pivot)
CELL_SOLES = 12                          # native cells: the soles 12 px under the cell's pivot
MARGIN = 30
GREY = (225, 225, 225)


def solid(a):
    """A dissolving old frame (an ordered dither took pixels out: tools/art/rig_kayn_forms.py's death) made whole for
    the template: the holes inside its closed shape take the colour of the nearest pixel left."""
    from scipy import ndimage
    op = a[..., 3] > 0
    shut = ndimage.binary_fill_holes(ndimage.binary_closing(op, structure=np.ones((3, 3)), iterations=2) | op)
    _, (iy, ix) = ndimage.distance_transform_edt(~op, return_indices=True)
    out = a.copy()
    hole = shut & ~op
    out[hole] = a[iy[hole], ix[hole]]
    return out


def old_frames(sheet_png, fanim):
    """{tag: [(frame, ms, (pivot x, soles y))]}: the old sheet's frames (pivot: the frame's centre, the soles OLD_SOLES
    under it), BAKED tags from their native body cells at 1x (each cell's own pivot, NATIVE_HERO's cells, the soles
    CELL_SOLES under it), SOLID frames made whole."""
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    cells = None
    if BAKED:
        with open(os.path.join(NATIVE, f"{NATIVE_HERO}_cells.json"), encoding="utf-8") as f:
            cells = json.load(f)
    out = {}
    for tag in TAGS:
        fr = []
        if tag in BAKED:
            strip = Image.open(PR.lp(os.path.join(NATIVE, f"{NATIVE_HERO}_{tag}.png"))).convert("RGBA")
            cw, ch = (v * cells["scale"] for v in cells["cell"])
            per_row = strip.width // cw
            for k, c in enumerate(cells["tags"][tag]):
                r, q = divmod(k, per_row)
                a = np.asarray(strip.crop((q * cw, r * ch, (q + 1) * cw, (r + 1) * ch))
                               .resize(tuple(cells["cell"]), Image.BOX)).copy()
                a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
                a[a[..., 3] == 0] = 0
                fr.append((a, c["ms"], (c["pivot"][0], c["pivot"][1] + CELL_SOLES)))
        else:
            for k, f_ in enumerate(anims[tag]["frames"], 1):
                d = f_["data"]
                x, y, w, h = (int(d[q]) for q in ("x", "y", "w", "h"))
                a = px[y:y + h, x:x + w].copy()
                if (tag, k) in SOLID:
                    a = solid(a)
                fr.append((a, round(f_["duration"] * 1000), (w / 2, h / 2 + OLD_SOLES)))
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
    if bb and top + bb[3] > GROUND + 2:      # (Ezreal's casts dip 2-5 old px under his soles: shown on the
        top = GROUND - bb[3]                 # ground line, where casts_*_hd.placed() puts every frame)
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
        dr.text((bx + 8, GROUND - STAND * sq - 4), "his height standing (the tips of his helmet's horns)",
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
    """His idle pose on the old sheet: DESIGN_TAG 1."""
    px = np.asarray(Image.open(PR.lp(os.path.join(OLD_SRC, "hd", "old", "sheet.png"))).convert("RGBA"))
    with open(PR.lp(os.path.join(OLD_SRC, "hd", "old", "anim.fanim")), encoding="utf-8-sig") as f:
        d = json.load(f)["anims"][DESIGN_TAG]["frames"][0]["data"]
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
    ap.add_argument("--old-sheet", default=os.path.join(OLD_SRC, "hd", "old", "sheet.png"))
    ap.add_argument("--old-fanim", default=os.path.join(OLD_SRC, "hd", "old", "anim.fanim"))
    ap.add_argument("--only", help="tags to pack, comma-separated (the redo of one action: --only run)")
    ap.add_argument("--sheets", help="of those, only these sheets, comma-separated (the redo: run_1,...,skill_1)")
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/hecarim")
    ap.add_argument("--style", help="a delivered sheet (hd/casts/<name>.png) shown as the view and size to match: "
                                    "refs/style.png (a redo of one sheet)")
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
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "hecarim-A.png"))).convert("RGBA")
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
        skip = set(SAME.get(tag, {})) | {k for k, (src, _) in DISSOLVE.get(tag, {}).items() if src != k}
        for n, (nums, part) in enumerate(groups(old[tag], skip, sq)):
            name = f"{tag}_{n + 1}"
            if a.sheets and name not in a.sheets.split(","):
                continue
            template(os.path.join(tpl, name + ".png"), part, nums, sq)
            old_ref(part, nums, os.path.join(refs, f"old_{name}.png"), sq)
            sheets.append(dict(tag=tag, name=name, frames=nums, cells=len(part), square=sq, action=NAMES[tag],
                               ms=[ms for _, ms, _ in part], weapons=WEAPONS[tag]))
            if tag == RUN_TAG:
                sheets[-1]["legs"] = " ".join(f"Frame {k}: {RUN_LEGS[k]}." for k in nums) + " " + RUN_SWAP
    same = {t: {str(k): f"{t2} {k2}" for k, (t2, k2) in m.items()} for t, m in SAME.items()}
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "square_of": SQ_OF, "sheet": [SHEET_W, H], "ground": GROUND, "same": same,
                   "dissolve": {t: {str(k): list(v) for k, v in m.items()} for t, m in DISSOLVE.items()},
                   "baked_body_frames": BAKED, "sheets": sheets}, f, indent=1, ensure_ascii=False)
    if a.style:
        shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "casts", a.style + ".png")), os.path.join(refs, "style.png"))
    shutil.copyfile(PR.lp(os.path.join(SRC, a.prompt)), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
