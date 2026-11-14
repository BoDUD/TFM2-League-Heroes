#!/usr/bin/env python3
"""league_kayn redone at PPU 1.80 in his three forms (the user, 2026-11-05: 「凯隐本体 1.80 凯隐暗裔 1.79 凯隐影流 1.80」;
2026-11-06: 「Codex全都交付了 你做到完美后喊我review」): the designs are Codex's kayn-A, kayn_darkin-A and kayn_shadow-A read on
their own squares (tools/art/design_kayn_hd.py 73 x 72, design_kayn_darkin_hd.py 71 x 77, design_kayn_shadow_hd.py
104 x 72), every action Codex's whole-frame redraw of the old frame read onto its form's design
(tools/art/casts_kayn_hd.py and its two form wrappers), rig_jhin_hd.py's way (the baked effects laid on again by
rig.bake from assets/source/native/kayn_bake.json).

ONE SHEET, ONE PPU: the forms live in Kayn's own sheet (league/champions/league_kayn: rh_ the Darkin, sh_ the Shadow
Assassin, w_ / rw_ / hw_ their in-wall shadows - addons/league_kayn_form swaps the playing animation's name) and
league.dll draws a hero at one PPU (hd.rs HEROES), so all three are drawn at Kayn's 72 / 40 = 1.80. The Darkin's design
is 77 rows over his 43 (1.79): at 1.80 he shows 0.5% smaller than his design asked - under half a game pixel - and the
transformation keeps one density (design_kayn_hd.py: the three forms are read at one PPU). Each form's frames are moved
onto Kayn's grid by its pivot column and its ground row (casts' PIVOT / GROUND).

The tags, as tools/art/import_native.py made the 1x sheet:
- idle_base / rh_idle_base / sh_idle_base: each form's design held still; idle / rh_idle / sh_idle are hero_reels'
  reels (tools/art/hero_reels.json) - here the idle_base until hero_reels.py cuts them.
- the drawn actions: the frames Codex drew; pack_<form>_actions.SAME frames take that drawing (the design for DESIGN);
  the BAKED tags (skill, rh_skill, rh_skill2, sh_skill, sh_skill2) are their native body cells, on the cells' timings,
  and kayn_bake.json lays Q's dash and W's wind on again and makes skill2_fx1 / ult_fx1 (rig.bake).
- the R's dive (ult) also has an in-between made from Codex's leap: Rhaast turned a quarter about his fist (INB).
- the forms' tags with no drawing of their own (import_native FORM_REVERSED / FORM_RETIMED): rh_ult / rh_ult_fx1 the
  form's R exit played backwards on ult's / ult_fx1's timings, rh_transform the form's idle on transform's timings,
  rh_skill2_fx1 the form's W (baked) spread over skill2_fx1's timings; the same for sh_.
- the death's dissolve (pack DISSOLVE: rh_dead / sh_dead 6, 7, 8 = frame 6 with a quarter, a half, three quarters of
  its pixels gone in rig_kayn_forms.py's 4x4 ordered dither) and the in-wall shadows (import_native.shadow_frame of
  idle, run, hit, skill, idle_base of each form) and r_hidden (empty) are made by --finish on the finished sheet, after
  ppu_restyle grew the outline (a dither run through it would get an outline round every dot): the dither on whole
  game pixels at every density, the shadows on the 1x frames (their hd_ frames are those scaled: a shadow needs no
  detail).

    python tools/art/rig_kayn_hd.py --review DIR      # every tag at 3x + GIFs
    python tools/art/rig_kayn_hd.py                   # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero kayn && python tools/art/ppu_hd.py --hero kayn
    python tools/art/ppu_one.py --hero kayn && python tools/art/rig_kayn_hd.py --one-ground   # the 1x frames
    python tools/art/rig_kayn_hd.py --finish          # the dissolve, the in-wall shadows, r_hidden; hd_ / lo_ again
    python tools/art/hero_reels.py --hero kayn        # then: the idle / ban-pick reels
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_kayn_hd as CA  # noqa: E402
import inbetween as IB  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_rengar_hd as RG  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "kayn"
FORMS = {"": "kayn", "rh_": "kayn_darkin", "sh_": "kayn_shadow"}
BASE = CA.form("kayn")
PPU = BASE.PPU
DESIGN_ROWS = 72
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
NATIVE = os.path.join(R.ROOT, "assets", "source", "native")
FX_PAD = 50                     # squares round the canvas for the baked effects (rig.bake)
# import_native's forms (FORM_REVERSED, FORM_RETIMED) and in-wall sheets (WALL_INTO_BASE + idle_base)
FORM_REVERSED = {"ult": "ult_exit", "ult_fx1": "ult_exit"}
FORM_RETIMED = {"transform": "idle", "skill2_fx1": "skill2"}
WALL = {"": "w_", "rh_": "rw_", "sh_": "hw_"}
WALL_TAGS = ("idle", "run", "hit", "skill", "idle_base")
DISSOLVE = {"rh_dead": {6: 0.25, 7: 0.5, 8: 0.75}, "sh_dead": {6: 0.25, 7: 0.5, 8: 0.75}}
# rig_kayn_forms.py's 4x4 ordered-dither threshold: a pixel goes once the fade passes its cell's rank (0..15)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])
LATER = ("idle", "bp", "r_hidden")      # (hero_reels' reels; r_hidden is --finish's)
# The R's dive in four frames (2026-11-14, the user: 「有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): Codex drew
# three (crouch, leap with Rhaast hanging below, dive with it raised overhead); between the leap and the dive Rhaast swings
# up behind him - the leap's picture with the scythe (the piece below the fist, SCYTHE: the row it is cut at, a square of
# it) turned one exact quarter clockwise about the fist (GRIP, a square corner), behind the rest of him (inbetween.vary:
# everything else checked unchanged). On R's dive effect's own frames (r_dive 40 / 50 / 50 / 60 ms, kayn_bake.json),
# still 200 ms (12 ticks, nothing hits inside it): ult_fx1, what the kit shows, is then four pieces, a body frame under
# each effect frame (three frames cut it into six: 40 27 23 44 6 60), and the forms' rh_ult / sh_ult (+ _fx1), their
# exits played backwards on these timings, show four of their five exit drawings (stance, swing, crouch, leap) where
# they showed three, or six pieces with a 6-ms one and the stance again at the end. INB: tag -> ([(cast, quarter turns
# of the scythe)], ms) - the first frame stays 40 ms, as the effect's first frame is.
INB = {"ult": ([("ult_1", 0), ("ult_2", 0), ("ult_2", 1), ("ult_3", 0)], [40, 50, 50, 60])}
SCYTHE = {"ult_2": (48, (20, 60))}
GRIP = {"ult_2": (20, 44)}
VPAD = 34


def picture(d):
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(R.lp(os.path.join(HD, "picture.png")))


def design():
    d = np.asarray(Image.open(R.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    picture(d)
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != d.shape or (D.d != d).any():
        sys.exit("hd/picture.png does not read back as hd/design.png")
    D.d0 = D.d.copy()
    D.px = BASE.PIVOT
    return D


def sealed(can, outline):
    """Every edge of the figure outlined (rig_jhin_hd's)."""
    out = can.copy()
    four = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], bool)
    op = out[..., 3] > 0
    line = op & (out[..., :3] == outline).all(-1)
    edge = op & ~line & ndimage.binary_dilation(~op, structure=four)
    dark = edge & (out[..., :3].max(-1) < 40)
    out[dark, :3] = outline
    ring = ndimage.binary_dilation(edge & ~dark, structure=four) & ~op
    out[ring] = (*outline, 255)
    return out


class KaynRig(R.Rig):
    def finish(self, can):
        outline = tuple(int(v) for v in self.D.outline)
        return RG.trim_nubs(sealed(RG.drop_specks(super().finish(can)), outline), outline)


def casts():
    """{"<prefix><tag>_<frame>": (picture, x, y on Kayn's grid)} of all three forms, and {prefix: (design, x, y)}."""
    out, designs = {}, {}
    for pre, name in FORMS.items():
        F = CA.form(name)
        dx, dy = BASE.PIVOT - F.PIVOT, BASE.GROUND - F.GROUND
        for n, (pic, x, y) in F.placed().items():
            out[n] = (pic, x + dx, y + dy)
        designs[pre] = (F.D0, dx, dy)
    return out, designs


def pad_for(D, cs, designs):
    """(left, right, top, bottom) squares round the design that every cast and form design fits in, 4 to spare."""
    allp = list(cs.values()) + list(designs.values())
    left = max([0] + [-x for _, x, _ in allp]) + 4
    right = max([0] + [x + p.shape[1] - D.d.shape[1] for p, x, _ in allp]) + 4
    top = max([0] + [-y for _, _, y in allp]) + 4
    return left, right, top, 6


def form_of(tag):
    return "rh_" if tag.startswith("rh_") else "sh_" if tag.startswith("sh_") else ""


def scythe_runs(d, row, seed):
    """The scythe of a cast as row runs (boxes): the 8-connected piece of its squares below `row` holding `seed`."""
    low = d[..., 3] > 0
    low[:row] = False
    lab, _ = ndimage.label(low, structure=np.ones((3, 3)))
    m = lab == lab[seed[1], seed[0]]
    runs = []
    for y in range(m.shape[0]):
        xs = np.nonzero(m[y])[0]
        for run in np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1) if len(xs) else []:
            runs.append((int(run[0]), y, int(run[-1]), y))
    return runs


def inb_frame(rig, cs, name, quarters):
    """A cast on the grid, its scythe turned `quarters` clockwise about the fist (INB)."""
    d, x, y = cs[name]
    if quarters:
        row, seed = SCYTHE[name]
        d = IB.vary(d, {"scythe": scythe_runs(d, row, seed)}, tuple(int(v) for v in rig.D.outline),
                    turns=[("scythe", GRIP[name], quarters, "under")], pad=VPAD, name=f"{name} scythe {quarters}")
        x, y = x - VPAD, y - VPAD
    return RG.on_grid(rig, d, x, y)


def body_timing(tag, sheet):
    """The frames' durations before the bake: a baked tag's native cells', else the sheet's (rig_akali_hd's)."""
    if tag in INB:
        return list(INB[tag][1])
    PK = CA.form(FORMS[form_of(tag)]).PK
    if tag in PK.BAKED:
        with open(R.lp(os.path.join(NATIVE, "kayn_cells.json")), encoding="utf-8") as f:
            return [c["ms"] for c in json.load(f)["tags"][tag]]
    return [m for _, m in sheet[tag]]


def derived(sheet):
    """The form tags made from others (prefix + import_native FORM_REVERSED / FORM_RETIMED, and the form idles)."""
    out = {}
    for pre in ("rh_", "sh_"):
        for t in FORM_REVERSED:
            out[pre + t] = ("reversed", pre + FORM_REVERSED[t], t)
        for t in FORM_RETIMED:
            src = pre + ("idle_base" if FORM_RETIMED[t] == "idle" else FORM_RETIMED[t])
            out[pre + t] = ("retimed", src, t)
    return {t: v for t, v in out.items() if t in sheet}


def frames(rig, cs, designs):
    sheet = R.sheet_of(HERO)
    with open(R.lp(os.path.join(NATIVE, f"{HERO}_bake.json")), encoding="utf-8") as f:
        cfg = json.load(f)
    copies = {e["into"] for e in cfg["items"] if "from" in e}
    der = derived(sheet)
    walls = {w + t for w in WALL.values() for t in WALL_TAGS}
    out = {}
    for tag in sheet:
        if tag in LATER or tag in copies or tag in der or tag in walls or tag in ("rh_idle", "sh_idle"):
            continue
        pre = form_of(tag)
        PK = CA.form(FORMS[pre]).PK
        base = tag[len(pre):]
        des = RG.on_grid(rig, *designs[pre]) if pre else RG.on_grid(rig, rig.D.d0, 0, 0)
        ms = body_timing(tag, sheet)
        if base == "idle_base":
            fr = [des.copy() for _ in ms]                              # (held still: the form's design)
        elif tag in INB:
            fr = [inb_frame(rig, cs, n, q) for n, q in INB[tag][0]]
        else:
            fr = []
            for k in range(1, len(ms) + 1):
                if PK.SAME.get(tag, {}).get(k) == PK.DESIGN:
                    fr.append(des.copy())                              # (the idle pose: the design itself)
                elif k in DISSOLVE.get(tag, {}) and k != min(DISSOLVE[tag]):
                    fr.append(RG.on_grid(rig, *cs[f"{tag}_{min(DISSOLVE[tag])}"]))   # (--finish dithers 6-8)
                else:
                    fr.append(RG.on_grid(rig, *cs[f"{tag}_{k}"]))
            if base == "hit":
                fr[0] = R.flash(rig.finish(fr[0]))      # (the struck frame flashes, as every rig's)
        if len(fr) != len(ms):
            sys.exit(f"{tag}: {len(fr)} frames for {len(ms)}")
        out[tag] = list(zip(fr, ms))
    acts = rig.bake(out, cfg=cfg)
    for pre in ("", "rh_", "sh_"):
        acts[pre + "idle"] = list(acts[pre + "idle_base"])
    for tag, (how, src, timing) in der.items():
        pics = [a for a, _ in acts[src]]
        ms = [m for _, m in acts[timing]] if timing in acts else [m for _, m in sheet[tag]]
        if how == "reversed":
            back = pics[::-1]
            acts[tag] = [(dict(back[k % len(back)]), m) for k, m in enumerate(ms)]
        else:
            acts[tag] = [(dict(pics[k * len(pics) // len(ms)]), m) for k, m in enumerate(ms)]
    # (the INB tags, the bake's copies of them and the forms' tags on their timings have their own frames now)
    fed = set(INB) | {e["into"] for e in cfg["items"] if e.get("from") in INB}
    fed |= {t for t, (_, _, timing) in der.items() if timing in fed}
    for t in sheet:
        if t in LATER or t in walls or t in fed or t.endswith("idle") and t != "idle_base":
            continue
        if t not in acts or [round(m) for _, m in acts[t]] != [round(m) for _, m in sheet[t]]:
            sys.exit(f"{t}: frames or timing differ from the sheet: "
                     f"{[round(m) for _, m in acts.get(t, [])]} vs {[round(m) for _, m in sheet[t]]}")
    return {t: acts[t] for t in sheet if t in acts}


# ===================== --finish: the dissolve, the in-wall shadows, r_hidden =====================

WALL_SMOKE = [(0x2C, 0x22, 0x50), (0x46, 0x3A, 0x74), (0x6A, 0x5C, 0x9E), (0x9A, 0x8E, 0xC8)]
WALL_GLOW = (0xFF, 0x40, 0x58)


def shadow_frame(a):
    """One frame as the see-through in-wall shadow: tools/art/import_native.shadow_frame's, copied (import_native
    loads every hero's tables) - the outline stays, the body takes the smoke violets by its brightness with every
    other inside pixel left out (a checker), bright saturated pixels (his eyes, the scythe's eye) glow crimson."""
    out = np.zeros_like(a)
    op = a[..., 3] > 0
    if not op.any():
        return out
    rgb = a[..., :3].astype(np.int32)
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    pad = np.pad(op, 1)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    keep = op & (edge | ((xs + ys) % 2 == 0))
    shade = np.clip((lum / 255.0 * len(WALL_SMOKE)).astype(int), 0, len(WALL_SMOKE) - 1)
    out[keep, :3] = np.array(WALL_SMOKE, np.uint8)[shade[keep]]
    dark = op & (lum < 40)
    out[dark & keep, :3] = a[dark & keep, :3]            # the outline as it was
    glow = op & (sat > 0.55) & (mx > 200)
    out[glow, :3] = WALL_GLOW
    out[keep | glow, 3] = 255
    return out


def dissolve(a, gone, cell):
    """The frame with gone (0.25 / 0.5 / 0.75) of its game pixels taken out in the 4x4 ordered dither, on whole game
    pixels (cell: px a game pixel; the frame's centre on a pixel's centre - the frames are centred on their pivots)."""
    h, w = a.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    gy = np.floor((ys + 0.5 - h / 2) / cell + 0.5).astype(int)
    gx = np.floor((xs + 0.5 - w / 2) / cell + 0.5).astype(int)
    out = a.copy()
    out[BAYER[gy % 4, gx % 4] < int(round(gone * 16))] = 0
    return out


def finish():
    """On the finished sheet (after ppu_restyle, ppu_hd, ppu_one and --one-ground): rh_dead / sh_dead 6-8 dissolving,
    their strips too (ppu_hd's drawn hd frames); the in-wall shadows of every form; r_hidden empty; then ppu_hd's hd_ /
    lo_ tags again and the sheet written in the old sheet's tag order."""
    import ppu_hd as H
    import strips as G
    stem = H.stem_of(HERO)
    sheet = H.read_sheet(stem)
    old_order = list(R.sheet_of(HERO))
    with open(R.lp(os.path.join(HD, "old", "anim.fanim")), encoding="utf-8-sig") as f:
        old_tags = list(json.load(f)["anims"])
    plain = {t: v for t, v in sheet.items() if H.plain(t)}
    k = H.PPU[HERO]
    for tag, steps in DISSOLVE.items():
        src = os.path.join(H.SRC, f"{HERO}_{tag}.png")
        drawn = H.drawn_strip(HERO, tag, [(a.shape[1], a.shape[0]) for a, _ in plain[tag]], k)
        for i, gone in steps.items():
            plain[tag][i - 1] = (dissolve(plain[tag][min(steps) - 1][0], gone, 1.0), plain[tag][i - 1][1])
            if drawn is not None:
                drawn[i - 1] = dissolve(drawn[min(steps) - 1], gone, k)
        if drawn is not None:
            Hm = max(d.shape[0] for d in drawn)
            strip = np.zeros((Hm, sum(d.shape[1] + 1 for d in drawn) - 1, 4), np.uint8)
            x = 0
            for d in drawn:
                strip[:d.shape[0], x:x + d.shape[1]] = d
                x += d.shape[1] + 1
            Image.fromarray(strip).save(R.lp(src))
    with open(R.lp(os.path.join(HD, "old", "anim.fanim")), encoding="utf-8-sig") as f:
        old = json.load(f)["anims"]
    for pre, wpre in WALL.items():
        for t in WALL_TAGS:
            if pre + t in plain and wpre + t in old:
                fr = plain[pre + t]
                if t == "idle":                     # (one frame, as before: hero_reels' w_idle reel is empty)
                    fr = [(fr[0][0], round(old[wpre + t]["frames"][0]["duration"] * 1000))]
                if len(fr) != len(old[wpre + t]["frames"]):
                    sys.exit(f"{wpre + t}: {len(fr)} frames, the old sheet's {len(old[wpre + t]['frames'])}")
                plain[wpre + t] = [(shadow_frame(a), ms) for a, ms in fr]
    plain["r_hidden"] = [(np.zeros((1, 1, 4), np.uint8), round(old["r_hidden"]["frames"][0]["duration"] * 1000))]
    order = [t for t in old_tags if t in plain] + [t for t in plain if t not in old_tags]
    plain = {t: plain[t] for t in order}
    made = H.add_hd(HERO, plain)
    w, h = G.write_sheet(stem, plain)
    print(f"league_{HERO}#sheet.png {w}x{h}: {len(order)} tags (+ hd_ / lo_); drawn {len(made['drawn'])}, "
          f"scaled {', '.join(made['scaled'])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--one-ground", action="store_true", help="after ppu_one.py: trim the 1x frames along the ground")
    ap.add_argument("--finish", action="store_true", help="after --one-ground: the dissolve, the walls, r_hidden")
    a = ap.parse_args()
    if a.one_ground:
        RG.HERO = HERO                                  # (rig_rengar_hd's trim along the ground, on his sheet)
        RG.one_ground()
        return
    if a.finish:
        finish()
        return
    D = design()
    cs, designs = casts()
    left, right, top, bottom = pad_for(D, cs, designs)
    rig = KaynRig(D, pad=(left + FX_PAD, right + FX_PAD, top + FX_PAD, bottom + FX_PAD))
    acts = frames(rig, cs, designs)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
