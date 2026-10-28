"""The Codex pack for league_sivir's actions drawn whole at PPU 2.25 (assets/source/sivir/ACTIONS_PROMPT_PPU.md): every
frame of her run, attack, Q throw (skill), Q in flight (skill_wait), Q catch (skill_catch), E (skill2), R (ult), hit
and death a new drawing of the approved design (hd/design.png: Codex's picture read as drawn, 98 x 81 squares - the
user, 2026-10-28: 「通过，用 2.25」) in the pose of her OLD sheet's same frame, tools/art/pack_akali_actions.py's way.

    python tools/art/pack_sivir_actions.py --out C:/t/sv_actions
    python tools/art/pack_sivir_actions.py --out C:/t/sv_run --only run --prompt <a redo prompt>   # one action again

The Chakram is where the old frame has it: in her near hand, raised, swung or caught - and not drawn at all while it
flies (the attack's 4-5, Q in flight: an effect). The run's legs are named frame by frame from the start (RUN_LEGS:
Akali's first run never passed a leg under her).

Not drawn: idle_base (one still frame: the design itself), idle and bp (tools/art/hero_reels.json cuts them from
skill_catch and attack), attack_fx1 / skill_catch_fx1 (copies with W's ricochet cast and the Q catch pictures:
assets/source/native/sivir_bake.json lays them on again). A frame that is another frame pixel for pixel (SAME) takes
that frame's drawing. skill_wait carries the Q throw's picture baked in, sliced to its timing (11 frames); its BODY
frames (2, the native cells assets/source/native/sivir_skill_wait.png at 1x, on their own pivots) are the poses to
draw, and the rig bakes the effect on again. Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or
TWO frames: in each cell the old 1x frame scaled to her height (PPU squares a pixel, SQ px a square), faded, as the
pose to follow, standing on the ground line at the standing point, and a bar as tall as she stands. Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "sivir")
NATIVE = os.path.join(REPO, "assets", "source", "native")
TAGS = ["run", "attack", "skill", "skill_wait", "skill_catch", "skill2", "ult", "hit", "dead"]
BAKED = ["skill_wait"]                  # the old frames carry the Q throw's picture: the native body cells are drawn
NAMES = {"run": "running (her move loop): a quick run, the Chakram carried in her near hand, the LEGS SWAPPING every "
                "half cycle, the body bobbing with each stride, the far arm swinging as the pale figure's",
         "attack": "attack: she swings her arm and hurls the Chakram forward, it flies off, then it is back in her hand",
         "skill": "Boomerang Blade (Q): she raises the Chakram over her head and hurls it forward",
         "skill_wait": "Boomerang Blade in flight: she waits in her stance, the far hand out, ready to catch it",
         "skill_catch": "Boomerang Blade returning: she catches the Chakram with her far hand and brings it back to her "
                        "near hand",
         "skill2": "Spell Shield (E): she raises the Chakram behind her head as the shield goes up",
         "ult": "On The Hunt (R): she raises the Chakram high over her head, rallying her team",
         "hit": "struck, flinching back",
         "dead": "death: she staggers, falls and lies on the ground, the Chakram dropped beside her"}
HANDS = ("THE CHAKRAM goes where the pale figure has it, frame by frame (image 3 shows it in colour): normally upright "
         "in her NEAR hand (image left) by her hip; raised over her head, swung forward or caught in a hand when the "
         "pale figure does it; and NOT DRAWN AT ALL when the pale figure's hands are empty (it is flying - an effect). "
         "Only ONE Chakram, never two. Her FAR hand (image right) keeps its brown glove.")
WEAPONS = {t: HANDS for t in NAMES}
WEAPONS["skill_wait"] = ("The Chakram is AWAY (thrown): her hands are empty, the far hand open and out in its brown "
                         "glove, as the pale figure. Do not draw the Chakram or any light.")
WEAPONS["dead"] = ("Lying on the ground as the pale figure; the Chakram where the pale figure has it (dropped on the "
                   "ground beside her in the last frames).")
# The run's legs frame by frame, read off the old run (the pale figures) - named from the start (Akali's first run kept
# the legs stretched apart in every frame and had to be drawn again); she runs to the right, "back" is the left
RUN_LEGS = {
    1: "PASSING: both feet together under her hips, one planted, the other just lifting off",
    2: "STRIDE: the front foot planted ahead (right), the back leg bent behind her, its foot lifting off the ground",
    3: "KICK-BACK: the back leg swung up high behind her, almost level, its foot well off the ground; the front foot "
       "planted under her",
    4: "RECOVERY: the back leg coming through, knee bent, its foot low behind; the front foot under her hips",
    5: "PASSING, THE OTHER LEG: both feet together under her hips again, the other foot planted",
    6: "STRIDE, THE OTHER LEG: the other foot planted ahead, the first leg bent behind her, lifting off",
    7: "KICK-BACK, THE OTHER LEG: that leg swung up high behind her, the other foot planted under her",
    8: "RECOVERY, THE OTHER LEG: it comes through, knee bent, foot low behind; the other foot under her hips",
}
RUN_SWAP = ("The two legs TAKE TURNS: in frames 1-4 the NEAR leg (the lighter one) is the one that ends in front, in "
            "frames 5-8 the FAR leg (the darker one). Follow the pale figure's LEGS exactly - frames 1 and 5 have both "
            "feet under her; never both legs stretched apart in every frame.")
# old frames that are another frame pixel for pixel (checked on the old sheet, cropped to the figure): drawn once,
# here (tag, frame), 1-based
SAME = {"dead": {6: ("dead", 5), 7: ("dead", 5), 8: ("dead", 5)}}
SQ = 6                                   # px a design square in the templates (her wide Chakram stance: two frames a sheet)
PPU = 81 / 36                            # design squares an old pixel (hd/design.png: 81 rows, her 1x 36)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 81                               # design rows from the top of her hair to her soles
OLD_SOLES = 11.5                         # old frames: the soles this many pixels under the frame's centre (its pivot)
CELL_SOLES = 12                          # native cells: their pivot is the frame's centre too, the soles 12 px under it
MARGIN = 30
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    """{tag: [(frame, ms, (pivot x, soles y))]}: the old sheet's frames (pivot: the frame's centre, the soles OLD_SOLES
    under it), BAKED tags from their native body cells at 1x (each cell's own pivot, sivir_cells.json, the soles
    CELL_SOLES under it: row 68 of every cell)."""
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    with open(os.path.join(NATIVE, "sivir_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    out = {}
    for tag in TAGS:
        fr = []
        if tag in BAKED:
            strip = Image.open(PR.lp(os.path.join(NATIVE, f"sivir_{tag}.png"))).convert("RGBA")
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
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height standing (top of her hair)", fill=(120, 120, 120),
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/sivir")
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
