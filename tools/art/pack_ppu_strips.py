#!/usr/bin/env python3
"""Codex packs for dense (PPU) action strips drawn from a dense design: every action frame redrawn at the design's grid.

The user, 2026-10-12: 「接下来使用PPU修复吸血鬼和卡尔玛和艾希 做到所有动作帧一致 待机一致」, chose 「Codex 按设计图逐帧重画」
and 「保持现在的身高」. The design (a Codex picture read back on its own grid, one pixel per drawn square) is the hero's
dense idle; PPU = its height in squares / the 1x idle's height in pixels, so the hero stands as tall as now. Every other
1x frame is scaled by PPU (nearest) into a cell of round(PPU x its size) squares - the SKELETON: the pose, the place and
the size - and Codex draws the design's character over it at the design's own square size (the 「骨架 + 皮囊」 way).
tools/art/import_ppu_strips.py reads the delivery back into assets/source/ppu/<hero>_<tag>.png (ppu_hd.py's drawn strips).

    python tools/art/pack_ppu_strips.py --hero vladimir --design assets/source/ppu/vladimir_codex.png --px 6

Writes dist/ppu_packs/<hero>/ (and <hero>_ppu_strips.zip):
  design/<hero>_design.png        the design at --px per square (transparent), design/<hero>_design_1x.png 1 px / square
  design/<hero>_palette.png       its colours (at most --colours)
  now/<hero>_<tag>_<n>.png        the skeleton images: the 1x frames x PPU, --px per square, frames packed in cells
  guide/<hero>_<tag>_<n>.png      the same with each cell's border (grey), standing point (blue) and feet line (red)
  cells.json                      every image: its cells (tag, frame, rect in squares, standing point, feet row, ms)
  PROMPTS.md                      what to give Codex and the prompts
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import regrid as RG  # noqa: E402
import ppu_hd as P  # noqa: E402

MAX_PX = 1536            # Codex's largest image side
# tags left out of a pack: copies of another tag with an effect drawn in (tools/fix/bake_caster_fx.py) - the importer
# makes their dense frames from the base tag's dense frames and the 1x effect pixels
SKIP = {"riven": ("skill_fx1", "skill_fx2", "skill2_fx1", "skill2_fx2", "ult_fx1", "r_slash_fx1")}
GAP = 2                  # squares between cells

# what each action is, for the prompts (the skeleton shows the motion; these name it)
ACTIONS = {
    "vladimir": {
        "run": "running to the right (8-frame loop)",
        "attack": "basic attack: a quick claw swipe throwing a blood bolt to the right",
        "skill": "Q Transfusion: a reaching claw grab to the right, drawing blood",
        "skill2": "E Tides of Blood: charging, the coat flaring as he gathers blood, then releasing it all around",
        "skill_w": "W Sanguine Pool: he sinks into a pool of blood and rises again (the long frames are the pool)",
        "ult": "R Hemoplague: a raised claw casting a blood curse to the right",
        "hit": "taking a hit, recoiling",
        "dead": "dying: collapsing to the ground",
    },
    "karma": {
        "run": "running to the right (8-frame loop)",
        "attack": "basic attack: a palm strike throwing a spirit bolt to the right",
        "skill": "Q Inner Flame: thrusting both palms to the right to fire a spirit flame",
        "skill2": "W Focused Resolve: a pointing hand tethering an enemy to the right",
        "skill_e": "E Inspire: lifting a hand to shield an ally",
        "ult": "R Mantra: a sweeping empowering gesture, the jade ring glowing",
        "hit": "taking a hit, recoiling",
        "dead": "dying: collapsing to the ground",
    },
    "yasuo": {
        "run": "running to the right, the sword held low behind him (8-frame loop)",
        "attack": "basic attack: a quick sword slash to the right",
        "skill": "Q Steel Tempest: a straight sword thrust to the right",
        "q3": "Q3: a rising sword sweep that sends a whirlwind to the right",
        "eq": "E-Q: a spinning sword slash in a full circle while dashing",
        "skill2": "E Sweeping Blade: a low dash to the right through an enemy, sword trailing",
        "ult": "R Last Breath: a leap up and a flurry of strikes on an airborne enemy, landing with the sword sheathed",
        "hit": "taking a hit, recoiling",
        "dead": "dying: collapsing to the ground",
    },
    "riven": {
        "run": "running to the right with the broken sword (8-frame loop)",
        "attack": "basic attack: a broken-sword slash to the right",
        "skill": "Q Broken Wings, first cast: a lunging slash to the right",
        "q2": "Q Broken Wings, second cast: another lunging slash, the other way round",
        "q3": "Q Broken Wings, third cast: a leap and a slam of the sword into the ground",
        "skill2": "E Valor: a quick dash to the right, the sword raised as a shield, then Ki Burst around her",
        "ult": "R Blade of the Exile: she reforges the sword, its broken pieces joined by a green rune blade",
        "r_slash": "R Wind Slash: a big sweeping slash sending a wave to the right (the reforged green blade)",
        "hit": "taking a hit, recoiling",
        "dead": "dying: collapsing to the ground",
        "attack_r": "basic attack while R is on: the same slash, the sword reforged with its glowing green rune blade",
        "skill_r": "Q first cast while R is on: the reforged green blade",
        "q2_r": "Q second cast while R is on: the reforged green blade",
        "q3_r": "Q third cast while R is on: the reforged green blade",
        "skill2_r": "E Valor while R is on: the reforged green blade",
    },
    "soraka": {
        "run": "running to the right holding the staff (8-frame loop)",
        "attack": "basic attack: a staff swing throwing a star bolt to the right",
        "skill": "Q Starcall: raising the staff high to call a falling star to the right",
        "skill2": "E Equinox: thrusting the staff forward to set a silence circle to the right",
        "ult": "R Wish: both arms raised high, praying, the staff upright",
        "hit": "taking a hit, recoiling",
        "dead": "dying: collapsing to the ground",
    },
    "ashe": {
        "run": "running to the right with the bow (8-frame loop)",
        "attack": "basic attack: drawing the bow and shooting an arrow to the right",
        "q_attack": "Ranger's Focus attack: a rapid flurry shot to the right",
        "skill": "W Volley: drawing the bow and firing a fan of arrows to the right",
        "skill2": "E Hawkshot: raising the bow and loosing a hawk spirit up to the right",
        "ult": "R Enchanted Crystal Arrow: a full draw, then loosing the big crystal arrow to the right",
        "hit": "taking a hit, recoiling",
        "dead": "dying: collapsing to the ground",
    },
}

LOOKS = {
    "vladimir": "a pale vampire mage: tall spiky white-pink hair, red eyes, a long blood-red high-collared coat with gold "
                "trim, silver spikes on the shoulders and clawed silver gauntlets, three silver clasps down the chest, "
                "red trousers and red boots with silver caps",
    "karma": "a spiritual mage: dark skin, short dark hair with a gold-and-jade circlet, a big jade dragon ring floating "
             "above her head, two cream-and-jade spirit blades floating beside her shoulders, a purple-and-gold top, a "
             "long purple-to-magenta skirt split at the front, jade tattoos on the bare leg, purple heeled boots",
    "garen": "Garen, the Might of Demacia (League of Legends): a Demacian knight in heavy silver plate armour with gold "
             "trim and blue accents, a blue cape, short brown hair, blue eyes, a big silver greatsword",
    "yasuo": "a wandering swordsman: a long brown ponytail tied with a gold band, a handsome stubbled face with thick "
             "brows, a blue scarf, a big silver shoulder plate on the far shoulder, a bare chest under brown straps, "
             "silver forearm guards, a gold sash, dark blue wide trousers, grey wrapped boots, and a long thin "
             "katana",
    "riven": "a fierce exiled warrior: short spiky white hair, green eyes, a dark olive-green sleeveless tunic with a "
             "torn, jagged skirt, bandages wrapped over her chest, brown leather straps and belts with a round bronze "
             "buckle and a hanging brown sash, a big olive-green metal pauldron and gauntlet on her sword arm, a "
             "bandaged other forearm with a leather bracer, bandaged legs, tall brown boots, and a huge broken runic "
             "sword: a grey stone-like blade snapped into jagged pieces with glowing green runes, a dark hilt",
    "soraka": "a gentle celestial healer: blue-violet skin with light swirl markings on her arms, long white-silver "
              "hair in a thick low ponytail down her back, one curved golden horn on her forehead, big pointed ears "
              "(blue-violet outside, red inside), golden eyes, a golden-yellow top with a teal gem pendant, a red cape, "
              "a brown belt with a round orange gem and a long orange-red cloth hanging in front, pale wraps on her "
              "lower legs, dark goat hooves, and a long golden staff with a big crescent moon on top and an orange orb "
              "at the bottom",
    "ashe": "a chibi frost archer: a black hood with a gold crest, long silver-white hair, big blue eyes, black-and-gold "
            "armour, a dark blue cape, a quiver of ice-blue arrows on the back, and a big ice-crystal bow with gold "
            "fittings in her near hand",
}


def clean_design(raw, colours):
    """The design read back on its own grid, its colours cut to `colours` (no dithering), alpha 0/255."""
    a = np.asarray(Image.open(raw).convert("RGBA")).copy()
    if a[..., 3].min() == 255:
        # a white or green ground: only the ground joined to the image's edge goes (white hair or cloth inside the
        # outline stays)
        from scipy import ndimage
        rgb = a[..., :3].astype(int)
        near = np.abs(rgb - rgb[0, 0]).max(axis=2) <= 40
        lab, _ = ndimage.label(near)
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        a[..., 3] = np.where(np.isin(lab, list(edge)), 0, 255)
    d = RG.regrid(a)[0]
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    op = op[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    img = Image.fromarray(d[..., :3].astype(np.uint8), "RGB")
    q = img.quantize(colors=colours, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    out = np.zeros(d.shape[:2] + (4,), np.uint8)
    out[..., :3] = np.asarray(q)
    out[..., 3] = np.where(op, 255, 0)
    return out


def scale_nearest(a, k):
    """`a` scaled by k (any k > 0) with every target pixel the source pixel under its centre."""
    h, w = a.shape[:2]
    H, W = max(1, round(h * k)), max(1, round(w * k))
    ys = np.minimum(((np.arange(H) + 0.5) / k).astype(int), h - 1)
    xs = np.minimum(((np.arange(W) + 0.5) / k).astype(int), w - 1)
    return a[ys][:, xs]


def feet_offset(frame):
    """Rows from the frame's centre (its pivot) down to its lowest opaque row."""
    ys = np.nonzero(frame[..., 3] > 0)[0]
    return ys.max() + 0.5 - frame.shape[0] / 2


def pack_cells(sizes, px, max_px=MAX_PX):
    """Frames (w, h in squares) into images of at most max_px: rows left to right. -> [[(x, y)...] per image]."""
    images, cur, x, y, row_h = [], [], 0, 0, 0
    for w, h in sizes:
        if x and (x + w) * px > max_px:
            x, y, row_h = 0, y + row_h + GAP, 0
        if cur and (y + h) * px > max_px:
            images.append(cur)
            cur, x, y, row_h = [], 0, 0, 0
        cur.append((x, y))
        x += w + GAP
        row_h = max(row_h, h)
    if cur:
        images.append(cur)
    return images


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--design", help="the Codex picture (any size; read back on its own grid); without it (a hero "
                    "whose design is drawn in the same pack's step 1: tools/art/pack_ppu_model.py) --ppu is needed and "
                    "the prompts point at that step's design")
    ap.add_argument("--px", type=int, default=6, help="pixels per square in the pack's images")
    ap.add_argument("--colours", type=int, default=48)
    ap.add_argument("--model-ref", help="with no --design: the picture the design is redrawn from in step 1 (the "
                    "user: 「索拉卡整体模型也重做 帮我整理 包括模型」「直接一步到位」「两个合一起」 - one pack, the design "
                    "first, then every action on it without stopping)")
    ap.add_argument("--px-model", type=int, default=8, help="pixels per square of the step-1 design")
    ap.add_argument("--model-only", action="store_true",
                    help="with --model-ref: a pack of step 1 alone - Codex draws the design and stops for the user to "
                         "see it; the actions follow in a pack of their own (--design <the delivery>). garen: the user "
                         "turned the model read from his original pictures down for its big head (「头这么大？」)")
    ap.add_argument("--ppu", type=float, help="squares per 1x pixel (default: the design's height / the 1x idle's); "
                    "yasuo: 1.5 - his game sheet is PPU 3 with the design's squares 2 x 2 (the face the user took); "
                    "karma: 3 - her head to her soles against the 1x one's (the big jade ring above her head is not "
                    "measured: by the whole height her body came out a quarter smaller)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "ppu_packs"))
    ap.add_argument("--only", action="append", default=[], metavar="TAG:I,J",
                    help="a completion pack: only these frames (yasuo eq:5 ult:0,1,2 dead:0,1,2,3,4,5,6 - Codex's image "
                         "service stopped half way through his pack)")
    ap.add_argument("--name", help="the pack's folder and zip name (default: the hero's; a completion pack: <hero>_fix)")
    ap.add_argument("--refs", nargs="*", default=[],
                    help="earlier deliveries' images copied into refs/ for Codex to match (a completion pack)")
    a = ap.parse_args()
    hero, px = a.hero, a.px
    sheet = P.read_sheet(os.path.join(ROOT, "league", "champions", f"league_{hero}"))
    design = clean_design(a.design, a.colours) if a.design else None
    if design is None and not a.ppu:
        sys.exit("without --design, --ppu is needed")
    idle = sheet["idle"][0][0]
    ys = np.nonzero(idle[..., 3] > 0)[0]
    ppu = a.ppu or design.shape[0] / (ys.max() - ys.min() + 1)
    pack_name = a.name or hero
    only = set()
    for spec in a.only:
        t, ids = spec.split(":")
        only |= {(t, int(v)) for v in ids.split(",")}
    out = os.path.join(a.out, pack_name)
    if os.path.isdir(out):
        shutil.rmtree(out)
    if a.model_only:
        if not a.model_ref:
            sys.exit("--model-only needs --model-ref")
        os.makedirs(out)
        write_model_step(out, hero, ppu, a.px_model, idle, a.model_ref, px, stop=True)
        readme = [f"# {hero}：只画造型", "",
                  f"按 `MODEL.md` 画一张造型，交付 `outputs/{hero}-ppu-model/`（最好打成 `{hero}_ppu_model_done.zip`），"
                  f"**画完就停**：用户先看造型，满意了再另发动作的包。", ""]
        with open(os.path.join(out, "README.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(chr(10).join(readme))
        shutil.make_archive(os.path.join(a.out, f"{pack_name}_ppu_model"), "zip", out)
        print(f"{hero}: the design step alone, PPU {ppu:g} -> {a.out}/{pack_name}_ppu_model.zip")
        return
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub))
    up = lambda img, k: np.repeat(np.repeat(img, k, axis=0), k, axis=1)
    if design is not None:
        shutil.copyfile(a.design, os.path.join(out, "refs", f"{hero}_design_raw.png"))
        Image.fromarray(design).save(os.path.join(out, "design", f"{hero}_design_1x.png"))
        Image.fromarray(up(design, px)).save(os.path.join(out, "design", f"{hero}_design.png"))
        cols = np.unique(design[design[..., 3] > 0][:, :3], axis=0)
        cols = cols[np.argsort(cols.sum(axis=1))]
        pal = np.zeros((1, len(cols), 4), np.uint8)
        pal[0, :, :3], pal[0, :, 3] = cols, 255
        Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", f"{hero}_palette.png"))
        hexes = " ".join("#%02X%02X%02X" % tuple(int(v) for v in c) for c in cols)
        extra = max(0, round(design.shape[0] - ppu * (ys.max() - ys.min() + 1)))
    else:
        cols, hexes, extra = [], "", 0
        os.rmdir(os.path.join(out, "design"))
    feet = feet_offset(idle)                        # 1x rows from the pivot to the soles

    manifest = {"hero": hero, "ppu": round(ppu, 4), "px_per_square": px, "skipped": list(SKIP.get(hero, ())),
                "design_squares": list(design.shape[1::-1]) if design is not None else None,
                "colours": len(cols), "images": []}
    rows_md = []
    for tag, frames in sheet.items():
        if tag.startswith(P.PREFIX) or tag == "idle" or tag in SKIP.get(hero, ()):
            continue
        if only and not any(t == tag for t, _ in only):
            continue
        cells = []
        for i, (f, ms) in enumerate(frames):
            if only and (tag, i) not in only:
                continue
            full = scale_nearest(f, ppu)
            # the cell: from 4 squares over the figure to the feet line (nothing may be drawn below it; the frame's
            # empty half under the pivot would only make the images bigger)
            feet_rel = min(full.shape[0] - 1, round(full.shape[0] / 2 + feet * ppu - 0.5))
            ys_ = np.nonzero(full[..., 3] > 0)[0]
            # never above the frame's own lowest pixel: the soles' last rows (the rounding above cut 1-2 of them) and
            # what a frame has under the standing feet line (a lying body, a sword's tip: yasuo dead 6 lost 371 px)
            if len(ys_):
                feet_rel = max(feet_rel, int(ys_.max()))
            # room over the head: 4 squares, plus what the design stands taller than the skeleton (karma's jade ring
            # rises ~25 squares over the 1x halo); a cell may start above the frame (frame_top < 0: the importer
            # grows the frame by as much at the top and the bottom, the pivot staying its centre)
            top = int((ys_.min() if len(ys_) else 0) - 4 - extra)
            sk = full[max(0, top):feet_rel + 1]
            if top < 0:
                sk = np.concatenate([np.zeros((-top,) + sk.shape[1:], np.uint8), sk])
            # across: the figure and 4 squares each side, not the frame's whole width (frame_left: where the cell
            # starts in the frame)
            xs_ = np.nonzero(full[..., 3].any(axis=0))[0]
            left = max(0, int(xs_.min()) - 4) if len(xs_) else 0
            right = min(full.shape[1], int(xs_.max()) + 5) if len(xs_) else full.shape[1]
            sk = sk[:, left:right]
            cells.append((tag, i, sk, ms, top, full.shape[1::-1], left))
        places = pack_cells([(c[2].shape[1], c[2].shape[0]) for c in cells], px)
        k = 0
        for n, img_places in enumerate(places):
            chunk = cells[k:k + len(img_places)]
            k += len(img_places)
            W = max(x + c[2].shape[1] for (x, _), c in zip(img_places, chunk))
            H = max(y + c[2].shape[0] for (_, y), c in zip(img_places, chunk))
            now = np.zeros((H, W, 4), np.uint8)
            meta = []
            for (x, y), (t, i, sk, ms, top, (fw, fh), left) in zip(img_places, chunk):
                h, w = sk.shape[:2]
                now[y:y + h, x:x + w] = sk
                # the pivot is the full frame's centre: the cell starts `top` rows and `left` columns into the frame
                cx, cy = x - left + fw / 2, y - top + fh / 2
                meta.append({"tag": t, "frame": i, "rect": [x, y, w, h], "pivot": [cx, cy],
                             "feet_row": y + h - 1, "ms": ms, "frame_size": [int(fw), int(fh)], "frame_top": top,
                             "frame_left": left})
            name = f"{hero}_{tag}_{n + 1}"
            big = up(now, px)
            Image.fromarray(big).save(os.path.join(out, "now", name + ".png"))
            g = Image.fromarray(big).convert("RGBA")
            dr = ImageDraw.Draw(g)
            for m in meta:
                x, y, w, h = m["rect"]
                dr.rectangle([x * px, y * px, (x + w) * px - 1, (y + h) * px - 1], outline=(128, 128, 128, 255))
                fy = (m["feet_row"] + 1) * px - 2
                dr.line([x * px, fy, (x + w) * px - 1, fy], fill=(255, 0, 0, 255), width=2)
                px0, py0 = m["pivot"][0] * px, m["pivot"][1] * px
                dr.line([px0 - 6, py0, px0 + 6, py0], fill=(0, 0, 255, 255), width=2)
                dr.line([px0, py0 - 6, px0, py0 + 6], fill=(0, 0, 255, 255), width=2)
            g.save(os.path.join(out, "guide", name + ".png"))
            manifest["images"].append({"file": name + ".png", "tag": tag, "size_px": [W * px, H * px],
                                       "squares": [W, H], "cells": meta})
            rows_md.append((name, tag, len(meta), W * px, H * px, ACTIONS.get(hero, {}).get(tag, tag)))
    with open(os.path.join(out, "cells.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    # earlier deliveries' images, named apart from this pack's skeletons (both would be yasuo_eq_1.png)
    for r in a.refs:
        shutil.copyfile(r, os.path.join(out, "refs", "delivered_" + os.path.basename(r)))
    write_prompts(out, hero, px, design, len(cols), hexes, rows_md, ppu, pack_name, sorted(only),
                  ["delivered_" + os.path.basename(r) for r in a.refs])
    if design is None and a.model_ref:
        write_model_step(out, hero, ppu, a.px_model, idle, a.model_ref, px)
        readme = [f"# {hero}：一个包两步，一次做完", "",
                  f"1. 先按 `MODEL.md` 画造型（交付 `outputs/{hero}-ppu-model/`）。",
                  f"2. 画完不用等确认，直接按 `PROMPTS.md` 画全部动作，附图2 用第 1 步的造型"
                  f"（交付 `outputs/{hero}-ppu-strips/`）。", "",
                  f"两步都交付后打成一个 zip：`{hero}_ppu_done.zip`。", ""]
        with open(os.path.join(out, "README.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(chr(10).join(readme))
    shutil.make_archive(os.path.join(a.out, f"{pack_name}_ppu_strips"), "zip", out)
    print(f"{hero}: design " + (f"{design.shape[1]}x{design.shape[0]} squares, {len(cols)} colours"
                                 if design is not None else "from step 1") + f", PPU {ppu:.3f}; "
          f"{len(rows_md)} images, {sum(r[2] for r in rows_md)} frames -> {a.out}/{pack_name}_ppu_strips.zip")


# the one-shot design step's words per hero: who asked, the top and bottom of the figure, the pose
MODEL_STEP = {
    "yasuo": {"asked": "「亚索的也可以帮我重做一下整体」「做亚索」"},     # (only the request: his design was already drawn)
    "garen": {
        "asked": "「盖伦游戏里还是老模型 ... 你参考亚索那些怎么弄的啊」；看了按原稿读回的那版后「还是变形 修不好了？模型都变形了 "
                 "还有模型尺寸太大 头这么大？」，选了「照亚索：新造型 + Codex 重画」，又说「盖伦的造型可以换」",
        "ref_note": "上一版按 GPT 原稿读回的高清造型，只是参考：它的头太大、身子太宽，用户说造型可以换",
        "top": "头发最高处", "bottom": "靴底", "top_en": "the top of the hair", "bottom_en": "the soles of the boots",
        "feet_en": "the boot soles",
        "pose": "**造型可以换**（用户：「盖伦的造型可以换」）：照英雄联盟的盖伦重新设计，盔甲细节和配色不必照参考图。"
                "**比例照 `model/style_yasuo.png`（亚索）**：头（头顶到下巴）只占身高的三成左右，**不要 Q 版大头**，"
                "身形结实但不要比亚索宽太多；**站姿照 `model/garen_size_now.png`（现在游戏里的待机）**：3/4 侧前方朝右，"
                "双脚分开站稳，大剑握在身前、剑尖朝右下方。",
        "pose_en": "You may redesign him (the user: his look can change): League of Legends' Garen, the armour details "
                   "and colours need not follow the reference, which is only the previous version. Use the proportions "
                   "of the image named style_yasuo - the head (top of the hair to the chin) only about 30% of the "
                   "height, NO big chibi head, a solid build but not much wider than that design - and the POSE of the "
                   "image named garen_size_now (the hero's current standing pose): 3/4 view facing right, feet apart, "
                   "the greatsword held low in front of him with its tip pointing down to the right.",
    },
    "soraka": {
        "asked": "「索拉卡整体模型也重做 帮我整理 包括模型」「直接一步到位」「两个合一起」",
        "ref_note": "你 10 月 9 日画的那张",
        "top": "角尖", "bottom": "蹄底", "top_en": "the tip of the horn", "bottom_en": "the bottom of the hooves",
        "feet_en": "the hooves",
        "pose": "长相、配色、姿势照参考图：3/4 侧前方朝右，自然站立，法杖竖在身前。",
        "pose_en": "Keep the reference's look, colours, proportions and pose (3/4 view facing right, standing, the staff "
                   "upright in front of her).",
    },
    "riven": {
        "asked": "「锐雯也重做 帮我打包一份个codex」",
        "ref_note": "用户发来的这张",
        "top": "头发最高的发梢", "bottom": "鞋底", "top_en": "the highest spike of the hair",
        "bottom_en": "the soles of the boots", "feet_en": "the boot soles",
        "pose": "长相、配色、比例照参考图；**姿势照 `model/riven_size_now.png`（现在游戏里的待机）**：3/4 侧前方朝右，"
                "双脚分开站稳，断剑握在身前、剑尖朝右下方——不要照参考图把剑拖在身后：第二步的动作都是照现在的骨架画的，"
                "剑多数在身前，待机的剑要和动作接得上。",
        "pose_en": "Keep the reference's look, colours and proportions, but take the POSE of the image named "
                   "riven_size_now (the hero's current standing pose): 3/4 view facing right, feet apart, the broken "
                   "sword held low in front of her with its tip pointing down to the right - not trailing behind her as "
                   "in the reference.",
    },
}


def write_model_step(out, hero, ppu, mpx, idle, ref, px, stop=False):
    """Step 1 of a one-shot pack: the design redrawn from `ref` on a clean grid at the hero's height x PPU (`stop`: a
    pack of this step alone - Codex delivers the design and stops)."""
    os.makedirs(os.path.join(out, "model"), exist_ok=True)
    shutil.copyfile(ref, os.path.join(out, "model", f"{hero}_reference.png"))
    for other in ("vladimir", "karma", "ashe", "yasuo"):
        src = os.path.join(ROOT, "assets", "source", "ppu", f"{other}_codex.png")
        if os.path.isfile(src):
            shutil.copyfile(src, os.path.join(out, "model", f"style_{other}.png"))
    ys, xs = np.nonzero(idle[..., 3] > 0)
    rows = round((ys.max() - ys.min() + 1) * ppu)
    # the guide: a 1024 x 1536 canvas of mpx squares, the 1x idle x PPU standing on the feet line, its top line
    W, H = 1024 // mpx, 1536 // mpx
    sk = scale_nearest(idle[ys.min():ys.max() + 1, xs.min():xs.max() + 1], ppu)
    feet_row = H - 8
    top_row = feet_row - rows + 1
    canvas = np.zeros((H, W, 4), np.uint8)
    x0 = (W - sk.shape[1]) // 2
    canvas[top_row:top_row + sk.shape[0], x0:x0 + sk.shape[1]] = sk[:H - top_row]
    big = np.repeat(np.repeat(canvas, mpx, axis=0), mpx, axis=1)
    Image.fromarray(big).save(os.path.join(out, "model", f"{hero}_size_now.png"))
    g = Image.fromarray(big).convert("RGBA")
    dr = ImageDraw.Draw(g)
    dr.line([0, top_row * mpx, W * mpx, top_row * mpx], fill=(0, 0, 255, 255), width=2)
    dr.line([0, (feet_row + 1) * mpx - 2, W * mpx, (feet_row + 1) * mpx - 2], fill=(255, 0, 0, 255), width=2)
    g.save(os.path.join(out, "model", f"{hero}_size_guide.png"))
    look = LOOKS.get(hero, hero)
    m = MODEL_STEP[hero]
    head = (f"# 造型（{hero}，画完就停，等用户确认）" if stop else f"# 第一步：造型（{hero}，画完不要停，直接做第二步）")
    then = ("画完交付就停：用户先看造型，满意了再另发动作的包。" if stop
            else "画完**直接用它做第二步**（`PROMPTS.md` 里的动作），中间不用等确认。")
    step = f"""{head}

> 用户：{m["asked"]}。先照 `model/{hero}_reference.png`（{m["ref_note"]}）重画一张**干净的高清造型**，{then}

- **大小**：从{m["top"]}到{m["bottom"]}正好 **{rows} 格**（游戏里现在的 {hero} 高 {ys.max() - ys.min() + 1} 像素，乘 {ppu:g}），每格 **{mpx}×{mpx} 像素**；画布 1024×1536，{m["bottom"]}在第 {feet_row} 行（从上往下数，`model/{hero}_size_guide.png` 的红线），{m["top"]}在蓝线（第 {top_row} 行），人站在画布中间。`model/{hero}_size_now.png` 是现在游戏里的样子按同样的大小放大——看大小和站位，长相照参考图。
- **{look}**。{m["pose"]}
- **画法照 `model/style_*.png`**（同一套英雄的高清造型）：干净的像素画，每格一个纯色方块，同一个网格，1 格深色外描边，每种材质 2-4 个色阶，不要抖动、渐变、噪点、抗锯齿、半透明；整张最多 48 色。
- 交付 `outputs/{hero}-ppu-model/{hero}_design.png`（{mpx} 倍放大，透明底）和 `{hero}_design_1x.png`（1 像素 1 格），生图原稿放 `raw/`。

```text
Redraw the attached reference character (FIRST image) as a clean, final pixel-art design: {look}. Exactly {rows} squares tall from {m["top_en"]} to {m["bottom_en"]}, every pixel one crisp {mpx}x{mpx} square on a single grid, on a 1024x1536 canvas with {m["feet_en"]} on square row {feet_row} and the character centered. {m["pose_en"]} Match the pixel style of the other attached designs: a 1-square dark outline, 2-4 flat shades per material, no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency, at most 48 colours. Transparent background (if not possible: solid #00FF00 green). No text, no grid lines.
```

""" + ("" if stop else f"""然后打开 `PROMPTS.md` 做第二步：**附图2 一律用这一步画好的 `{hero}_design.png`**，每格 {px}×{px} 像素——第二步骨架的格子按 {px} 像素一格算，**和这一步的 {mpx} 像素不同时，把造型缩放成 {px} 像素一格再当附图2**（按格子整格缩放，不要插值）。
""")
    with open(os.path.join(out, "MODEL.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(step)


# what of the skeleton's effects is drawn after all, per hero: (Chinese, English)
FX_KEEP = {
    "riven": ("例外：R 期间的动作（`*_r`）和 `ult`、`r_slash` 里，剑是**重铸**的——断片之间接上一道发光的绿色符文刃，"
              "这是剑本身，要画；骨架里画在身上的**绿色刀光**（剑挥过的绿弧）也照骨架画上，用造型图的绿色。"
              "别的特效照样不画。",
              "Exception: in the R-form frames (*_r), ult and r_slash the sword is REFORGED - a glowing green rune blade "
              "joins its broken pieces: that is the sword itself, draw it; and where Image 1 shows a green sword trail "
              "(the arc the swing leaves) draw it too, in Image 2's greens. No other effects."),
}


def write_prompts(out, hero, px, design, ncol, hexes, rows, ppu, name=None, only=(), refs=()):
    look = LOOKS.get(hero, hero)
    asked = MODEL_STEP.get(hero, {}).get("asked", "「接下来使用PPU修复吸血鬼和卡尔玛和艾希 做到所有动作帧一致 待机一致」")
    name = name or hero
    fix = ""
    if only:
        frames = "、".join(f"{t} 第 {i + 1} 帧" for t, i in only)
        fix = (f"> **补画包**：上次的包没画完（生图服务中途断了），这里只有缺的 {len(only)} 帧：{frames}。"
               f"其余的已经交付，不用再画。")
        if refs:
            fix += (f"`refs/` 里是上次交付的 {len(refs)} 张（{'、'.join(f'`{r}`' for r in refs)}）："
                    f"这次画的人要和它们**一样大、一样的画法和细节**，同一个动作里接得上。")
        fix += "\n>\n"
    fx_cn, fx_en = FX_KEEP.get(hero, ("", ""))
    if design is None:
        # the design is drawn in step 1 of the same pack (model/): every reference to it points there
        dfile = f"outputs/{hero}-ppu-model/{hero}_design.png"
        dsize = "第一步定稿的大小"
        colours_rule = "only the colours of Image 2 (no new colours)"
    else:
        dfile = f"design/{hero}_design.png"
        dsize = f"{design.shape[1]}×{design.shape[0]} 格、{ncol} 色"
        colours_rule = f"ONLY Image 2's colours: {hexes}"
    table = "\n".join(f"| `{n}.png` | {t} | {c} | {w}×{h} | {d} |" for n, t, c, w, h, d in rows)
    md = f"""# {hero}：按高清造型逐帧重画全部动作（PPU {ppu:.2f}，给 Codex 的提示词）

{fix}> 用户：{asked}。**造型就是 `{dfile}`**（{dsize}，这里每格 {px}×{px} 像素）。待机不用画（就是造型图）。其余每个动作都要画成**这个造型**，像素大小和造型图一模一样。
> - 每张 `now/{hero}_<动作>_<n>.png` 是**骨架**：现在游戏里的动作帧按同样的格子放大，告诉你每帧的姿势、在格子里的位置和人有多高。你画的人**脚底和骨架在同一行同一列、头顶到脚底一样高**，姿势照骨架；**比例（头的大小、身材、四肢）、长相、配色、细节全部照造型图**——骨架是旧的粗画法，头比造型图大，不要照它的比例（「骨架 + 皮囊」）。
> - `guide/` 是同一张图加了格子边框（灰）、站位点（蓝十字）和脚底线（红线）——对位用，**不要画进图里**。`cells.json` 里有每格的位置。
> - **每格 {px}×{px} 像素一个纯色方块**，所有格子对齐同一个网格；只用造型图的颜色；没有抗锯齿、模糊、半透明。
> - **头每帧都是造型图的头**（发型、脸、眼睛逐格一样，只平移），衣服、武器、配饰的形状和颜色每帧都和造型图一样；出招一律朝图的右边；不画背影；**脚底线以下什么都不能有**；不画特效（血、光、箭的轨迹、冲击波），只画人。{fx_cn}
> - 每张交回同名文件（`{hero}_<动作>_<n>.png`，和骨架同样大小、同样的格子），放到 `outputs/{name}-ppu-strips/`；附 `HANDOFF.md`（最后写：每张用了哪条提示词、哪里没做到）和生图原稿 `raw/`（不要重采样）；最好打成一个 zip（`{name}_ppu_strips_done.zip`）。
> - 你的生图工具一次画不好整张时，**一帧一帧单独生成**（每帧一张图，按 `cells.json` 拼回格子）；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**。

## 要画的图

| 骨架 | 动作 | 帧数 | 图片大小 | 动作内容 |
|---|---|---|---|---|
{table}

## 提示词（每张图：附图1 = `now/` 里那张骨架，附图2 = `{dfile}`）

```text
Image 1 is a sprite sheet of an animation: frames in cells, read left to right, top to bottom. Image 2 is the approved, final pixel-art design of the character. Redraw every frame of Image 1 as the character of Image 2.
1. Keep from Image 1: every frame's cell, where the character stands (the soles on the same row and the same column), the height from the soles to the top of the head, and the pose (where the arms, the weapon, the body and the legs go). Do NOT copy Image 1's proportions or look: Image 1's figure is an older, rougher drawing with a bigger head - the head size, the body, the limbs and every detail are Image 2's. Every cast goes to the RIGHT of the image; never draw the character from the back.
2. Replace the look completely with Image 2: {look}. The head (hair, face, eyes) is Image 2's head in every frame, copied square for square and only moved; the clothes, armour, weapon and ornaments keep Image 2's shapes and colours in every frame.
3. Pixel art at EXACTLY Image 2's pixel size: every pixel one crisp {px}x{px} square on a single grid, nothing smaller, no anti-aliasing, no blur, no semi-transparency. {colours_rule}. A 1-square dark outline around the silhouette, Image 2's shading, no dithering, no noise.
4. Nothing below each frame's feet (the soles stay where Image 1's soles are). Do not draw any effect (blood, glow, arrows in flight, trails, shockwaves): only the character. {fx_en}
5. The animation: [动作内容].
Same image size and the same cells as Image 1. Transparent background (if not possible: solid #00FF00 green). No grid lines, borders, labels or guide marks.
```

短提示词（生图画不准时用；附图同上）：

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 {px}×{px} 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作和站位（脚底同一行同一列、头顶到脚底一样高）；比例照图2，不照图1的大头；出招都朝图的右边，不画背影。
3. 长相、配色、细节全部换成图2，头每一帧都和图2一模一样。
4. 动作：[动作内容]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的"动作骨架"，只是换了"皮囊"。
```

## 交回前自查

- 每个方块 {px}×{px}、同一个网格；只用造型图的颜色；
- 每帧的人和骨架一样大、站在一样的位置，脚底在红线上；
- 头每帧都是造型图的头；衣服、武器、配饰每帧和造型图一样；
- 没有散落的碎块、多余的黑格；脚底线以下是空的；没有背影；
- 同名文件、同样大小、同样的格子。
"""
    with open(os.path.join(out, "PROMPTS.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(md)


if __name__ == "__main__":
    main()
