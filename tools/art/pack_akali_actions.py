"""The Codex pack for league_akali's actions drawn whole at PPU 1.8 (assets/source/akali/ACTIONS_PROMPT_PPU.md): every
frame of her run, attack, empowered attack (attack_p), Q (skill), E throw (skill2), E recast dash (skill2_dash), R
(ult), R recast (ult2), hit and death a new drawing of the approved design (hd/design.png: Codex's fourth take read as
drawn, 71 x 72 squares - the user, 2026-10-27: 「设计图通过，就用 1.8，继续做阿卡丽的动作包」) in the pose of her OLD
sheet's same frame, tools/art/pack_rengar_actions.py's way.

    python tools/art/pack_akali_actions.py --out C:/t/ak_actions
    python tools/art/pack_akali_actions.py --out C:/t/ak_run --only run --prompt RUN_REDO_PROMPT_PPU.md   # the run again

Her weapons are the design's, not the old sprite's (「就用这张，不用照旧精灵的手」): the hooked kama in the near hand, the
long straight blade in the far hand; the old frames hold them the other way round, so the prompt takes only their arms.

Not drawn: idle_base (the design breathing: the old frames are its first one sunk 0-2 rows over its feet - the rig
sinks the design), idle and bp (tools/art/hero_reels.json cuts them from attack 1-2), ult2_fx1 (R's recast with its
dash picture: assets/source/native/akali_bake.json lays it on ult2 again). A frame that is another frame pixel for
pixel (SAME, across tags: the recovery pose attack 6 ends seven of them) takes that frame's drawing. skill2_dash and ult
carry the dash pictures baked in, sliced to the effect's timing (10 and 13 frames); their BODY frames (5 and 6, the
native cells assets/source/native/akali_<tag>.png at 1x, on their own pivots) are the poses to draw, and the rig bakes
the effects on again. Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell
the old 1x frame scaled to her height (PPU squares a pixel, SQ px a square), faded, as the pose to follow, standing on
the ground line at the standing point, and a bar as tall as she stands. Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "akali")
NATIVE = os.path.join(REPO, "assets", "source", "native")
TAGS = ["run", "attack", "attack_p", "skill", "skill2", "skill2_dash", "ult", "ult2", "hit", "dead"]
BAKED = ["skill2_dash", "ult"]          # the old frames carry the dash pictures: the native body cells are drawn
NAMES = {"run": "running (her move loop): a fast, low run, the LEGS SWAPPING every half cycle (left foot forward, then "
                "right foot forward), the body bobbing with each stride, the arms swinging as the pale figure's",
         "attack": "attack: a quick slash forward, then back to her stance",
         "attack_p": "empowered attack: a long lunging slash, reaching far forward, then back to her stance",
         "skill": "Five Point Strike (Q): a sweep of her arm flinging a fan of kunai forward, then back to her stance",
         "skill2": "Shuriken Flip (E): she flips back and hurls a shuriken forward, then lands in her stance",
         "skill2_dash": "Shuriken Flip recast: she dashes forward low and strikes, then stands",
         "ult": "Perfect Execution (R): she dashes forward through her target, blades out, and turns to stand",
         "ult2": "Perfect Execution recast: a second dash, low and fast, then back to her stance",
         "hit": "struck, flinching back",
         "dead": "death: she staggers, falls and lies on the ground"}
HANDS = ("Her NEAR hand (image left) always holds the HOOKED kama and her FAR hand (image right) the long STRAIGHT "
         "blade, as in image 1. The old frames hold them the other way round: follow the pale figure's ARMS - where each "
         "hand is, raised, swung, thrust or lowered - but put image 1's weapon in each hand.")
WEAPONS = {t: HANDS for t in NAMES}
WEAPONS["skill"] = HANDS + " Do not draw the kunai (they are an effect)."
WEAPONS["skill2"] = HANDS + " Do not draw the shuriken (it is an effect)."
WEAPONS["dead"] = ("Lying on the ground as the pale figure: the hooked kama and the straight blade where the pale "
                   "figure's hands have them (dropped beside her in the last frames).")
# The run's legs frame by frame, read off the old run (the pale figures): Codex's first run kept both legs stretched
# apart, the back foot up, in all 8 frames - it hopped, the legs never passed (Rengar's 「走路两个腿不交换的」) - so the
# redo (--only run) names each frame's legs; she runs to the right, "back" is the picture's left
RUN_LEGS = {
    1: "STRIDE: both feet on the ground, wide apart - the back foot far behind (left), the front foot far ahead (right)",
    2: "PASSING: the back foot has pushed off and is planted right under her hips; the other knee swings up and "
       "forward, its foot off the ground under her belly",
    3: "PASSING: one foot planted under her hips; the other knee raised high in front, its foot tucked under it",
    4: "FLIGHT: the back leg stretched far behind, its foot up off the ground at knee height; the front foot reaching "
       "forward to land (right)",
    5: "PASSING, THE OTHER LEG: the foot that landed is now planted under her hips; the leg that was behind comes "
       "through bent, its knee forward, its foot off the ground",
    6: "FLIGHT, THE OTHER LEG: the other leg now stretched far behind and lifted, the other foot reaching forward to "
       "land",
    7: "PASSING: one foot planted under her hips, the other knee lifted in front",
    8: "PASSING: both legs gathered under her, one foot planted right under her hips, the other tucked up beside it",
}
RUN_SWAP = ("The two legs TAKE TURNS: in frames 1-4 the NEAR leg (the lighter one) is the one that ends in front, in "
            "frames 5-8 the FAR leg (the darker one). Follow the pale figure's LEGS exactly - only frames 1, 4 and 6 "
            "have them stretched apart; in the others a foot is planted under her hips and the other leg comes through "
            "under her.")
# old frames that are another frame pixel for pixel (checked on the old sheet; a BAKED body cell against the old
# frames cropped to the figure - the cells are the very pictures the sheet's frames were cut from): drawn once, here
# (tag, frame), 1-based
SAME = {"attack_p": {6: ("attack", 6)},
        "skill": {3: ("skill", 2), 5: ("skill", 4), 6: ("attack", 6)},
        "skill2": {3: ("skill2", 1), 5: ("skill", 4), 6: ("attack", 6)},
        "skill2_dash": {3: ("skill2_dash", 1), 4: ("skill", 2), 5: ("attack", 6)},
        "ult": {1: ("skill2", 1), 2: ("skill2_dash", 2), 4: ("attack_p", 1), 5: ("skill2_dash", 1), 6: ("attack", 6)},
        "ult2": {5: ("attack", 6)},
        "hit": {2: ("attack", 6)}}
SQ = 8                                   # px a design square in the templates
PPU = 72 / 40                            # design squares an old pixel (hd/design.png: 72 rows, her 1x 40)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 72                               # design rows from the top of her ponytail to her soles
OLD_SOLES = 11.5                         # old frames: the soles this many pixels under the frame's centre (its pivot)
CELL_SOLES = 12                          # native cells: their pivot is the frame's centre too, the soles 12 px under it
MARGIN = 30
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    """{tag: [(frame, ms, (pivot x, soles y))]}: the old sheet's frames (pivot: the frame's centre, the soles OLD_SOLES
    under it), BAKED tags from their native body cells at 1x (each cell's own pivot, akali_cells.json, the soles
    CELL_SOLES under it: row 82 of every cell)."""
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    with open(os.path.join(NATIVE, "akali_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    out = {}
    for tag in TAGS:
        fr = []
        if tag in BAKED:
            strip = Image.open(PR.lp(os.path.join(NATIVE, f"akali_{tag}.png"))).convert("RGBA")
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
            for f_ in anims[tag]["frames"]:
                d = f_["data"]
                x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
                fr.append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000), (w / 2, h / 2 + OLD_SOLES)))
        out[tag] = fr
    return out


def cell_fit(frame):
    xs = np.nonzero(frame[0][..., 3].any(0))[0]
    return (xs.max() + 1 - xs.min()) * PPU * SQ + 2 * MARGIN <= SHEET_W / 2


def placed(frame, x0, cw):
    """The old frame scaled to her height in a cell [x0, x0 + cw): its pivot on the standing point (the cell's middle),
    its soles on the ground line, kept inside the cell. -> (RGBA image, left, top)."""
    a, _, (pvx, pvy) = frame
    k = PPU * SQ
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
            raise SystemExit(f"a frame reaches {8 - top - bb[1]} px over the template's top: lower SQ")
    return im, left, top


def template(path, frames, nums):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), (255, 255, 255, 255))
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
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
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height standing (top of the ponytail)", fill=(120, 120, 120),
                font=PR.font(16))
        dr.text((x0 + 14, 12), f"frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(path)


def old_ref(frames, nums, out):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        can.alpha_composite(im, (left, top))
        dr.text((i * cw + 14, 12), f"old frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def groups(frs, skip):
    """[([numbers], [frames])] of the frames to draw (none in `skip`): two to a sheet while both fit a half."""
    todo = [(k + 1, f) for k, f in enumerate(frs) if k + 1 not in skip]
    out, k = [], 0
    while k < len(todo):
        if k + 1 < len(todo) and cell_fit(todo[k][1]) and cell_fit(todo[k + 1][1]):
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


def check_same(old):
    """Every SAME pair is the same picture on the old sheet (a later edit of SAME must not join two poses)."""
    for tag, m in SAME.items():
        for k, (t2, k2) in m.items():
            a, b = figure(old[tag][k - 1][0]), figure(old[t2][k2 - 1][0])
            if a.shape != b.shape or (a != b).any():
                sys.exit(f"SAME {tag} {k} = {t2} {k2}: not the same old frame")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-sheet", default=os.path.join(SRC, "hd", "old", "sheet.png"))
    ap.add_argument("--old-fanim", default=os.path.join(SRC, "hd", "old", "anim.fanim"))
    ap.add_argument("--only", help="tags to pack, comma-separated (the redo of one action: --only run)")
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/akali")
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
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    sheets = []
    for tag in (a.only.split(",") if a.only else TAGS):
        for n, (nums, part) in enumerate(groups(old[tag], set(SAME.get(tag, {})))):
            name = f"{tag}_{n + 1}"
            template(os.path.join(tpl, name + ".png"), part, nums)
            old_ref(part, nums, os.path.join(refs, f"old_{name}.png"))
            sheets.append(dict(tag=tag, name=name, frames=nums, cells=len(part), action=NAMES[tag],
                               ms=[ms for _, ms, _ in part], weapons=WEAPONS[tag]))
            if tag == "run":
                sheets[-1]["legs"] = " ".join(f"Frame {k}: {RUN_LEGS[k]}." for k in nums) + " " + RUN_SWAP
    same = {t: {str(k): f"{t2} {k2}" for k, (t2, k2) in m.items()} for t, m in SAME.items()}
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "sheet": [SHEET_W, H], "ground": GROUND, "same": same, "baked_body_frames": BAKED,
                   "sheets": sheets}, f, indent=1, ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, a.prompt)), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
