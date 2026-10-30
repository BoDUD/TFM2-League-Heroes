"""The Codex pack for league_leona's actions drawn whole at PPU 1.76 (assets/source/leona/ACTIONS_PROMPT_PPU.md):
every frame of her run, attack, Q Shield of Daybreak (skill), W Eclipse (skill2), E Zenith Blade's dash (e_dash), R
Solar Flare (ult), hit and death a new drawing of the approved design (hd/design.png: Codex's leona-A read as drawn,
69 x 72 squares - the user, 2026-10-30: 「通过，用 1.76」) in the pose of her OLD sheet's same frame,
tools/art/pack_taric_actions.py's way.

    python tools/art/pack_leona_actions.py --out C:/t/le_actions

The shield and the sword go where the old frame has them: the round gold shield on her near arm before her (pushed out
ahead in Q's bash), the sword in her far hand raised, thrust or swung; both dropped on the ground in the death from
frame 3. The run's legs follow the pale figures (RUN_LEGS: the old run's legs hide behind the shield and the skirt,
so they are not named one by one).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from skill2 and
skill). No old frame is another one's picture nor her idle pose itself (checked on the old sheet: SAME is empty), so
all 45 are drawn. Nothing is baked into her body tags (her sunlight, eclipse and flare are effect strips,
leona_fx_*). Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old
1x frame scaled to her height (PPU squares a pixel, SQ px a square), faded, as the pose to follow, standing on the
ground line at the standing point, and a bar as tall as she stands. Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "leona")
TAGS = ["run", "attack", "skill", "skill2", "e_dash", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into her body tags)
NAMES = {"run": "running (her move loop): a steady armoured run, the round shield held before her, the sword low "
                "in her far hand, the LEGS STEPPING IN TURN, the hair and the skirt swaying",
         "attack": "attack: she raises the sword, draws it back over her shoulder, thrusts it out ahead of her to the "
                   "right, lunges low slashing down ahead, and settles",
         "skill": "Shield of Daybreak (Q): she raises the sword behind her, braces behind the shield, then lunges and "
                  "BASHES the shield out ahead of her to the right, and draws it back before her",
         "skill2": "Eclipse (W): she raises the sword over her shoulder, swings it round behind her and over, sweeps "
                   "it down ahead of her and thrusts it out level, the shield before her",
         "e_dash": "Zenith Blade's dash (E): she lunges forward with the sword raised up ahead of her, then dashes "
                   "low with it pointing ahead",
         "ult": "Solar Flare (R): she thrusts the sword out level ahead, raises it up, holds it straight up over her "
                "head, and lowers it ahead of her",
         "hit": "struck: jolted back, the sword up",
         "dead": "death: struck, she drops the shield (frame 3: it falls to the ground on her left) and the sword (it "
                 "falls to the ground on her right), sinks to her knees and slumps forward onto the ground"}
ARMS = ("THE SHIELD AND THE SWORD go where the pale figure has them, frame by frame (image 3 shows them in "
        "colour): the ROUND GOLD SUN SHIELD on her NEAR arm (image left), before her unless she bashes it out "
        "ahead; the SWORD in her FAR hand (image right), its silver blade pointing where the pale figure's does. "
        "Only ONE shield and ONE sword, the design's.")
WEAPONS = {t: ARMS for t in NAMES}
WEAPONS["skill"] = ARMS + (" In frames 4-5 she pushes the shield out AHEAD of her to the right (the bash), as the pale "
                           "figure.")
WEAPONS["dead"] = ("As the pale figure: shield and sword in her hands in frames 1-2; from frame 3 on BOTH lie on the "
                   "ground apart from her - the round shield on her left, the sword on her right - drawn where the "
                   "pale figure has them, only one of each.")
# The run's legs: the old run's are hidden behind the shield and the skirt (both boots gold), so not named frame by
# frame - each frame follows its pale figure
RUN_LEGS = {k: "the legs exactly as the pale figure: one foot planted, the other lifted or swinging"
            for k in range(1, 9)}
RUN_SWAP = ("The two legs TAKE TURNS frame by frame as the pale figures show - never the same leg pose in every frame, "
            "never both legs stretched apart in every frame; the body bobs with the steps.")
# old frames that are another frame pixel for pixel (checked on the old sheet / the native cells, cropped to the
# figure): drawn once, here (tag, frame), 1-based; DESIGN: her idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {}                                # (none: every old frame is its own picture)
SQ = 8                                   # px a design square in the templates (two run frames a sheet)
PPU = 72 / 41                            # design squares an old pixel (hd/design.png: 72 rows, her 1x 41)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 72                               # design rows from the top of her crown to her soles
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
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height standing (the top of her crown)",
                fill=(120, 120, 120), font=PR.font(16))
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/leona")
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
