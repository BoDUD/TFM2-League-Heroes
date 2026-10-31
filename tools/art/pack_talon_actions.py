"""The Codex pack for league_talon's actions drawn whole at PPU 2.21 (assets/source/talon/ACTIONS_PROMPT_PPU.md): every
frame of his run, attack, W Rake (skill), Q Noxian Diplomacy's leap (skill2) and close stab (skill2_stab), E Assassin's
Way (skill_e), R Shadow Assault (ult), hit and death a new drawing of the approved design (hd/design.png: Codex's
talon-A read on its own ~10.5-px squares, 105 x 86 - the user, 2026-10-31: 「用A PPU2.21吧」) in the pose of his OLD
sheet's same frame, tools/art/pack_briar_actions.py's way.

    python tools/art/pack_talon_actions.py --out C:/t/tl_actions

The wrist blade goes where the old frame has it: a long straight silver blade from his near fist where the pale figure
shows one, the bare fist (the design's) where it shows none; the rust-red cloak with its blade tips and the long spear
tip streams as the old frame's does. The run's legs follow the pale figures (RUN_LEGS).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from attack and
skill2_stab). No old body frame is another frame or his idle pose (SAME is empty: checked pixel for pixel), so 57 are
drawn. Nothing is baked. Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each
cell the old 1x frame scaled to his height (PPU squares a pixel, SQ px a square), faded, as the pose to follow,
standing on the ground line at the standing point, and a bar as tall as he stands. refs/design_picture.png is Codex's
own talon-A, the picture the design was read from (its fine face and blades). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "talon")
TAGS = ["run", "attack", "skill", "skill2", "skill2_stab", "skill_e", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into his body tags)
NAMES = {"run": "running (his move loop): a low, fast assassin's run, leaning far forward, the cloak streaming "
                "behind, the near arm and its blade held low ahead, the LEGS STEPPING IN TURN",
         "attack": "attack: he draws the near arm back, then STABS the wrist blade straight forward (frame 3, the "
                   "blade reaching far ahead to the right), and pulls it back to his crouch",
         "skill": "Rake (W): he winds up, then FLINGS his near arm forward and out (frame 3), throwing his blades "
                  "(the thrown blades are effects - not drawn), the cloak swirling, and recovers",
         "skill2": "Noxian Diplomacy's leap (Q): he springs UP (frames 1-2), FLIPS head over heels through the air "
                   "(frames 4-5: upside down, the cloak and its blades flung up), and lands in a deep lunge "
                   "(frame 6) and rises",
         "skill2_stab": "Noxian Diplomacy's stab (Q, close): he coils, then SLASHES and THRUSTS the blade far forward "
                        "(frames 2-3, stretched out), spins back round (frames 4-5) and settles",
         "skill_e": "Assassin's Way (E): he crouches and VAULTS - a tight SOMERSAULT through the air (frames 2-4: "
                    "tucked, upside down, turning), lands (frame 5) and runs on (frames 6-7)",
         "ult": "Shadow Assault (R): he crouches, then SPINS round, flinging both arms out with blades (frames 2-7: "
                "the body turning, the cloak and blades whirling out), and comes back to his crouch",
         "hit": "struck: jolted back, the head knocked back",
         "dead": "death: struck, he staggers back, rises on his toes, twists, falls and ends lying flat on the "
                 "ground on his front, the cloak and its long spear tip laid out behind him"}
BLADE = ("THE WRIST BLADE AND THE CLOAK go where the pale figure has them, frame by frame (image 3 shows them in "
         "colour): where the pale figure shows a long grey blade from his NEAR FIST, draw it there - one long, straight, "
         "single-edged SILVER BLADE held in the near hand, as long as his forearm, in the steel colours of the design; "
         "where it shows none, draw the bare blue-violet fist as the design. The rust-red CLOAK with its silver BLADE "
         "TIPS and the LONG SPEAR TIP at its lower end streams, swirls and lies as the pale figure's does. Only these: "
         "no thrown blades in the air, no blade trails.")
WEAPONS = {t: BLADE for t in NAMES}
WEAPONS["skill2"] = BLADE + " In frames 4-5 he is UPSIDE DOWN mid-flip, the hood at the bottom, as the pale figure."
WEAPONS["skill_e"] = BLADE + " In frames 2-4 he is tucked and turning in a somersault, as the pale figure."
# The run's legs, each frame following its pale figure
RUN_LEGS = {k: "the legs exactly as the pale figure: one foot planted, the other lifted or swinging" for k in range(1, 9)}
RUN_SWAP = ("The two legs TAKE TURNS frame by frame as the pale figures show - never the same leg pose in every frame, "
            "never both legs stretched apart in every frame; the body bobs with the steps.")
# old frames that are another frame pixel for pixel (checked on the old sheet / the native cells, cropped to the
# figure): drawn once, here (tag, frame), 1-based; DESIGN: his idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
_ID = {}                                 # (none: checked pixel for pixel on his old sheet)
SAME = {t: {k: DESIGN for k in ks} for t, ks in _ID.items()}
SQ = 8                                   # px a design square in the templates (his 86 rows in the sheet)
SQ_OF = {"skill2": 7, "ult": 7, "skill_e": 6}   # Q's flip, R's spin and E's vault rise high: smaller squares
PPU = 86 / 39                            # design squares an old pixel (hd/design.png: 86 rows, his 1x 39)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 86                               # design rows from the top of the hood to his soles
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
        dr.text((bx + 8, GROUND - STAND * sq - 4), "his height standing (the top of the hood)",
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/talon")
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
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "talon-A.png"))).convert("RGBA")
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
