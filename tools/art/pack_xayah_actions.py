"""The Codex pack for league_xayah's actions drawn whole at PPU 1.80 (assets/source/xayah/ACTIONS_PROMPT_PPU.md): every
frame of her actions - her attack, Q Double Daggers (skill), E Bladecaller (skill_e), W Deadly Plumage (skill2), R
Featherstorm (ult), run, hit and death - most of them her idle pose itself on the old sheet - a new drawing of the
approved design (hd/design.png: Codex's xayah-A read on ~14.25-px squares, 57 x 79 - the user, 2026-11-07: 「1.8 for all
four」（四位都用 1.8）) in the pose of the OLD sheet's same frame, tools/art/pack_ryze_actions.py's way
(pack_blitzcrank_actions.py's latest), one PR with the rest of batch 6 (霞 / 洛 / 稻草人 / 璐璐).

    python tools/art/pack_xayah_actions.py --out C:/t/xayah_actions

The weapon and hands go where the old frame has them (WEAPONS); the old frames' baked effects are not drawn. The run's
legs change over (RUN_LEGS: named frame by frame from the start - deferred to the pale figure, Codex's runs kept the
same legs in all 8 frames).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from the actions). Old
frames that are another frame pixel for pixel are drawn once (SAME). Nothing is baked. Each template sheet
(templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame scaled to her height (PPU
squares a pixel, SQ px a square), faded, as the pose to follow, standing on the ground line at the standing point, and a
bar as tall as her standing height. refs/design_picture.png is Codex's own xayah-A, the picture the design was read from
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

SRC = os.path.join(REPO, "assets", "source", "xayah")
OLD_SRC = os.path.join(REPO, "assets", "source", "xayah")   # the old sheet (hd/old)
NATIVE = os.path.join(REPO, "assets", "source", "native")
NATIVE_HERO = "xayah"                    # the native cells of BAKED tags: <hero>_<tag>.png, <hero>_cells.json
DESIGN_TAG = "idle_base"                  # the old sheet's idle pose (the design): its first frame
RUN_TAG = "run"
TAGS = ["run", "attack", "skill", "skill_e", "skill2", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into the body tags)
NAMES = {
    "run": ("running (her move loop): darting forward, the magenta feather blade low in her near hand, the great "
        "feather cloak trailing behind her as in image 1, the LEGS CHANGING OVER as written for each frame"),
    "attack": ("attack (a flung feather): she flicks her near hand forward, the arm straight out to the picture's "
        "right at chest height, the feather leaving her fingers (frame 3); frames 1-2 and 5-6 are the design,"
        " frame 4 = frame 3"),
    "skill": ("Double Daggers (Q): every frame is another one's (the design, attack 3)"),
    "skill_e": ("Bladecaller (E): she pulls her near hand back in to her hip, the feather blade low, calling her "
        "feathers home (frame 2); frame 1 = attack 3, frames 3-4 are the design"),
    "skill2": ("Deadly Plumage (W): she sweeps the magenta feather blade forward and low at arm's length, pointing "
        "it at the foe (frame 2); frames 1, 3 and 4 are the design"),
    "ult": ("Featherstorm (R): every frame is another one's (the design, attack 3, skill_e 2)"),
    "hit": ("struck: both frames are the design"),
    "dead": ("death: she has collapsed forward onto the ground and lies low, her head to the picture's right, the "
        "great feather cloak spread out over her (frame 4); frames 1-3 are the design, frames 5-8 = frame 4"),
}
ARMS = ("THE FEATHER BLADE goes where the pale figure has it, frame by frame (image 3 shows it in colour): the "
        "magenta feather blade in her near hand, as big as in image 1; her far hand empty. Her great feather cloak as"
        " big as in image 1, where the pale figure has it. Only her: no flying feathers, no glow, no trails.")
WEAPONS = {t: ARMS for t in NAMES}
# The run's legs frame by frame, named from the start (the Blitzcrank redo's way, 2026-11-05: deferred to the pale
# figure, Codex drew the same legs in all 8 frames - the user on Talon, 2026-10-31: 「走路没有换腿」): support, swing, passing,
# stride, the other leg from frame 5 (Lulu's 7-frame run: from frame 4); the run goes to the right, "back" is the
# picture's left
RUN_LEGS = {
    1: "SUPPORT ON THE NEAR LEG: the NEAR leg (the lighter one) straight down under her hips, her bird-claw foot "
       "flat on the ground line; the FAR leg (the darker one) bent and kicked back behind her, its foot off the "
       "ground",
    2: "SUPPORT ON THE NEAR LEG: the near leg still planted under her hips, bending; the far leg swinging down from "
       "behind, its foot low, just off the ground behind the planted one",
    3: "PASSING: the FAR leg passing forward right beside the planted near leg, its foot just off the ground - the "
       "two feet side by side",
    4: "STRIDE: the FAR leg reaching forward (the picture's right), its foot about to land; the NEAR leg behind (the"
       " picture's left) pushing off, its toes on the ground - the feet wide apart",
    5: "SUPPORT ON THE FAR LEG: now the FAR leg (the darker one) straight down under her hips, its foot flat on the "
       "ground line; the NEAR leg (the lighter one) bent and kicked back behind her, its foot off the ground",
    6: "SUPPORT ON THE FAR LEG: the far leg still planted under her hips, bending; the near leg swinging down from "
       "behind, its foot low, just off the ground behind the planted one",
    7: "PASSING: the NEAR leg passing forward right beside the planted far leg, its foot just off the ground - the "
       "two feet side by side",
    8: "STRIDE: the NEAR leg reaching forward (the picture's right), its foot about to land; the FAR leg behind (the"
       " picture's left) pushing off, its toes on the ground - the feet wide apart",
}
RUN_SWAP = ("The two legs TAKE TURNS: in frames 1-4 the NEAR leg (the lighter one) carries her and the FAR leg comes "
            "forward, in frames 5-8 the FAR leg (the darker one) carries her and the NEAR leg comes forward - frames "
            "1 and 5 must show a different leg planted. Draw the legs AS WRITTEN for each frame, not the pale "
            "figure's (the old 1x legs are too small to read; runs drawn after them kept the same legs in all 8 "
            "frames: 「走路没有换腿」). The body, the hood, the cloak and the feather blade follow the pale figure. The cloak"
            " trails low behind her but is NOT a leg: her two striped legs carry her.")
# old frames that are another frame pixel for pixel (checked on the old sheet, cropped to the figure): drawn once, here
# (tag, frame), 1-based; DESIGN: her idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {"attack": {1: DESIGN, 2: DESIGN, 4: ('attack', 3), 5: DESIGN, 6: DESIGN}, "skill": {1: DESIGN, 2: DESIGN, 3:
        ('attack', 3), 4: DESIGN}, "skill_e": {1: ('attack', 3), 3: DESIGN, 4: DESIGN}, "skill2": {1: DESIGN, 3:
        DESIGN, 4: DESIGN}, "ult": {1: DESIGN, 2: DESIGN, 3: DESIGN, 4: DESIGN, 5: DESIGN, 6: ('attack', 3), 7:
        ('skill_e', 2), 8: DESIGN}, "hit": {1: DESIGN, 2: DESIGN}, "dead": {1: DESIGN, 2: DESIGN, 3: DESIGN, 5:
        ('dead', 4), 6: ('dead', 4), 7: ('dead', 4), 8: ('dead', 4)}}
DISSOLVE = {}
SOLID = set()
SQ = 9                                    # px a design square in the templates (her 79 rows in the sheet)
SQ_OF = {}                               # (tags drawn at smaller squares)
PPU = 79 / 44                            # design squares an old pixel (hd/design.png: 79 rows, her 1x 44)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 79                               # design rows from the tips of her feather ears to her soles
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
        dr.text((bx + 8, GROUND - STAND * sq - 4), "her height standing (the tips of her feather ears)",
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
    """Her idle pose on the old sheet: DESIGN_TAG 1."""
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/xayah")
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
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "xayah-A.png"))).convert("RGBA")
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
