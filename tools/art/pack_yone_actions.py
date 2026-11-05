"""The Codex pack for league_yone's actions drawn whole at PPU 2.20 (assets/source/yone/ACTIONS_PROMPT_PPU.md): every
frame of his actions - his two attacks (attack: the steel katana, attack2: the demon blade), Q Mortal Steel (skill) and
its third cast's dash (q3), W Spirit Cleave (skill2), E Soul Unbound's spirit dash (e_dash) and the body it leaves
(e_body), R Fate Sealed (ult), walk, hit and death - a new drawing of the approved design (hd/design.png: Codex's yone-A
read on ~12.5-px squares, 96 x 90 - the user, 2026-11-05: 「凯隐本体 1.80 凯隐暗裔 1.79 凯隐影流 1.80 维克托 1.81 永恩2.20 泰坦1.80」) in the
pose of the OLD sheet's same frame, tools/art/pack_ryze_actions.py's way (pack_blitzcrank_actions.py's latest), one PR
with the rest of batch 5.

    python tools/art/pack_yone_actions.py --out C:/t/yone_actions

The weapon and hands go where the old frame has them (WEAPONS); the old frames' baked effects are not drawn. The run's
legs change over (RUN_LEGS: named frame by frame from the start - deferred to the pale figure, Codex's runs kept the
same legs in all 8 frames).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from the actions),
skill2_fx1 / e_dash_fx1 (copies of skill2 / e_dash with E's cast: assets/source/native/yone_bake.json lays them on
again). Old frames that are another frame pixel for pixel are drawn once (SAME). Nothing is baked. Each template sheet
(templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame scaled to his height (PPU
squares a pixel, SQ px a square), faded, as the pose to follow, standing on the ground line at the standing point, and a
bar as tall as he stands. refs/design_picture.png is Codex's own yone-A, the picture the design was read from (its fine
detail). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "yone")
OLD_SRC = os.path.join(REPO, "assets", "source", "yone")   # the old sheet (hd/old)
NATIVE = os.path.join(REPO, "assets", "source", "native")
NATIVE_HERO = "yone"                    # the native cells of BAKED tags: <hero>_<tag>.png, <hero>_cells.json
DESIGN_TAG = "idle_base"                  # the old sheet's idle pose (the design): its first frame
RUN_TAG = "run"
TAGS = ["run", "attack", "attack2", "skill", "q3", "skill2", "e_dash", "ult", "e_body", "hit", "dead"]
BAKED = []                              # (nothing baked into the body tags)
NAMES = {
    "run": ("walking (his move loop, League's walk): striding forward, the red demon blade low behind him, the white"
        " katana low before him, the LEGS CHANGING OVER as written for each frame"),
    "attack": ("attack (the steel katana): he stands ready (frame 1), raises the white katana high over his head "
        "(frame 2), cuts down across (frames 3-4) and follows through in a low lunge, both blades swept low "
        "and forward (frames 5-7)"),
    "attack2": ("attack (the demon blade): he stands ready (frame 1), swings the red blade up behind him (frames "
        "2-3), raises it straight up over his head (frame 4) and brings it down, back into his stance "
        "(frames 5-7)"),
    "skill": ("Mortal Steel (Q): he thrusts the white katana straight forward, level, in a lunge (frame 1), draws it"
        " back (frames 2-3) and thrusts again in a long low lunge, the katana level before him (frames 4-7)"),
    "q3": ("Mortal Steel's third cast (Q3): he raises the white katana upright (frame 1), levels it (frame 2), "
        "raises it over his shoulder (frame 3), dashes forward low, almost lying along the ground, the blades "
        "trailing (frames 4-6), rises (frame 7) and stands ready (frame 8)"),
    "skill2": ("Spirit Cleave (W): he crouches low, both blades out (frame 1), swings the red blade up and over his "
        "head (frames 2-5), leaps, the red blade raised high (frame 6), and comes down cutting (frame 7)"),
    "e_dash": ("Soul Unbound, the spirit's dash (E): he lunges forward low, both blades back (frames 1-2), rises "
        "upright, both blades held upright before him (frames 3-4), and thrusts the red blade straight "
        "forward, level (frame 5)"),
    "ult": ("Fate Sealed (R): he stands ready, the katana pointed forward (frame 1), raises both blades upright "
        "(frame 2), crouches into a low lunge, the white katana up, the red blade back (frames 3-4), spreads "
        "both blades - the red blade level behind him, the white katana up before him (frames 5-7), crouches low"
        " (frame 8) and stands ready (frame 9)"),
    "e_body": ("the body left behind (E): he stands upright, both blades held upright before him, still (frames 1-2)"),
    "hit": ("struck: jolted back, the blades swung out (frames 1-2)"),
    "dead": ("death: struck, he staggers (frames 1-2) and sinks to his knees, the red blade planted upright beside "
        "him (frames 3-7)"),
}
ARMS = ("HIS TWO BLADES go where the pale figure has them, frame by frame (image 3 shows them in colour): the RED "
        "DEMON BLADE and the WHITE STEEL KATANA, as long as in image 1 - each in its own hand, raised, swung, thrust "
        "or held low as the pale figure holds them; the red horned mask stays on the side of his head. Only him: no "
        "spirit flames, no wind, no slash arcs, no trails, no glow; the eye's red stays inside the eye.")
WEAPONS = {t: ARMS for t in NAMES}
# The run's legs frame by frame, named from the start (the Blitzcrank redo's way, 2026-11-05: deferred to the pale
# figure, Codex drew the same legs in all 8 frames - the user on Talon, 2026-10-31: 「走路没有换腿」): support, swing, passing,
# stride, the other leg from frame 5; he runs to the right, "back" is the picture's left
RUN_LEGS = {
    1: "SUPPORT ON THE NEAR LEG: the NEAR leg (the lighter one) straight down under his hips, his black sandal flat "
       "on the ground line; the FAR leg (the darker one) bent and kicked back behind him, its foot off the ground",
    2: "SUPPORT ON THE NEAR LEG: the near leg still planted under his hips, bending; the far leg swinging down from "
       "behind, its foot low, just off the ground behind the planted one",
    3: "PASSING: the FAR leg passing forward right beside the planted near leg, its foot just off the ground - the "
       "two feet side by side",
    4: "STRIDE: the FAR leg reaching forward (the picture's right), its foot about to land; the NEAR leg behind (the"
       " picture's left) pushing off, its toes on the ground - the feet wide apart",
    5: "SUPPORT ON THE FAR LEG: now the FAR leg (the darker one) straight down under his hips, its foot flat on the "
       "ground line; the NEAR leg (the lighter one) bent and kicked back behind him, its foot off the ground",
    6: "SUPPORT ON THE FAR LEG: the far leg still planted under his hips, bending; the near leg swinging down from "
       "behind, its foot low, just off the ground behind the planted one",
    7: "PASSING: the NEAR leg passing forward right beside the planted far leg, its foot just off the ground - the "
       "two feet side by side",
    8: "STRIDE: the NEAR leg reaching forward (the picture's right), its foot about to land; the FAR leg behind (the"
       " picture's left) pushing off, its toes on the ground - the feet wide apart",
}
RUN_SWAP = ("The two legs TAKE TURNS: in frames 1-4 the NEAR leg (the lighter one) carries him and the FAR leg comes "
            "forward, in frames 5-8 the FAR leg (the darker one) carries him and the NEAR leg comes forward - frames "
            "1 and 5 must show a different leg planted. Draw the legs AS WRITTEN for each frame, not the pale "
            "figure's (the old 1x legs are too small to read; runs drawn after them kept the same legs in all 8 "
            "frames: 「走路没有换腿」). The body, the head, the hair, the arms and the blades follow the pale figure. The "
            "wide hakama swings with the legs: show each leg's shape through it, the sandals under its hems; the "
            "blades' tips hang near the ground but are NOT legs.")
# old frames that are another frame pixel for pixel (checked on the old sheet, cropped to the figure): drawn once, here
# (tag, frame), 1-based; DESIGN: his idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {}
DISSOLVE = {}
SOLID = set()
SQ = 8                                    # px a design square in the templates (his 90 rows in the sheet)
SQ_OF = {"attack": 7, "attack2": 7, "skill2": 7}   # (his two attacks lift a blade 56-58 old px and W 59 over his soles)
PPU = 90 / 41                            # design squares an old pixel (hd/design.png: 90 rows, his 1x 41)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 90                               # design rows from the top of his hair to his soles
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
        dr.text((bx + 8, GROUND - STAND * sq - 4), "his height standing (the top of his hair)",
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/yone")
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
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "yone-A.png"))).convert("RGBA")
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
