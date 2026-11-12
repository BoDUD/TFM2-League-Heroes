#!/usr/bin/env python3
"""Codex packs to redraw the effects that have no drawing to read a dense twin from (the effects PPU, 2026-11-09, the
user: 「继续完成别的英雄的技能特效的修复 在这个pr里面 如果要补图的也全都整理给我」).

    python tools/art/pack_fx_redraw.py --out DIR [--heroes h ...] [--per-pack 12] [--zoom-plan ult_zoom.json]

tools/art/densify_fx.py gives a tag its dense twin from Codex's raw drawing (or an older real drawing); a tag left with
squares (its hd_ frames its 1x squares scaled up, or a sheet never densified) has nothing finer behind it - its 1x
frames are all there is. This packs every such tag for Codex to redraw on a guide:

  guides/<hero>/<hero>_fx_<tag>.png   the tag's distinct 1x frames, each centred in an equal cell (one row, no gutters),
                                      8 px a game pixel (nearest) - the exact place and size each frame must keep
  guides/<hero>/_contact.png          every guide of the hero on a dark ground with its name, for reading
  refs/<hero>/hero.png                the hero's own dense idle (colours, scale) and, when some of its effects are dense
                                      already, refs/<hero>/dense.png (the style to match)
  manifest.json                       hero, tag, file, frames, distinct (the tag's frames -> the guide's cells), cell_1x,
                                      cell_8x, kind (effect / projectile / buff), symmetry, zoom
An ult's area picture drawn smaller than the area it hits (scratchpad ult_zoom_plan.py: radius + a 15000 body each side)
gets its guide drawn `zoom` times bigger (smooth) - Codex draws it that size.

What comes back (outputs/fx_redraw_<n>/<hero>/<hero>_fx_<tag>.png, the guide's size, each frame in its cell) is read by
densify_fx.py as a raw on an exact 8 px grid.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import densify_fx as D  # noqa: E402

SCALE = 8
CRATES = {"league": "league_main", "tft": "tft"}


def fx_dir(pack):
    return os.path.join(ROOT, pack, "effects")


def hd_effect_sheets(pack):
    """the pack DLL's hd.rs own EFFECTS rows (dense by their own tools: turrets, Daisy ...; the effects PPU's are in
    fx_ppu.rs)"""
    import re
    hd = open(os.path.join(ROOT, "addons", CRATES[pack], "src", "hd.rs"), encoding="utf-8").read()
    i = hd.index("pub const EFFECTS")
    return set(re.findall(r'\("(' + pack + r'_[a-z0-9_]+)", [0-9.]+, include_str!', hd[i:hd.index("];", i)]))


def kinds_of(hero, pack):
    """{(sheet, tag): kind} from the kit's views (effect / projectile / buff)"""
    p = os.path.join(ROOT, pack, "champion", f"{pack}_{hero}.data_champion")
    if not os.path.isfile(p):
        return {}
    d = json.load(open(p, encoding="utf-8-sig"))
    out = {}
    for sec, kind in (("view_effects", "effect"), ("view_projectiles", "projectile"), ("view_buffs", "buff")):
        for v in d.get(sec, []):
            if "anim" not in v:
                continue
            for t in (v.get("tag"), v.get("pre_tag"), v.get("loop_tag"), v.get("remove_tag")):
                if t:
                    out.setdefault((v["anim"].split("/")[-1], t), kind)
    return out


def needs(sheet_tags, tag):
    """True when no raw redrew the tag: no hd_ twin, or every hd_ frame its 1x frame scaled up (square for square, or
    Scale2x'd - densify_fx.py's frames no raw redraws faithfully)"""
    hd = sheet_tags.get("hd_" + tag)
    if hd is None:
        return True
    for (a, _), (b, _) in zip(sheet_tags[tag], hd):
        if not a[..., 3].any():
            continue
        k = b.shape[1] / a.shape[1]
        if abs(k - round(k)) > 1e-6 or b.shape[0] != a.shape[0] * round(k):
            return False
        k = int(round(k))
        if not (np.array_equal(np.repeat(np.repeat(a, k, 0), k, 1), b) or (k == 2 and np.array_equal(D.scale2x(a), b))):
            return False
    return True


def symmetric(frames):
    lr = all(np.array_equal(f, f[:, ::-1]) for f in frames)
    tb = all(np.array_equal(f, f[::-1]) for f in frames)
    return "left-right" if lr else ("top-bottom" if tb else "none")


def zoomed(f, z):
    """a 1x frame z times bigger, smooth (the redraw's size), odd sizes kept round the middle"""
    h, w = f.shape[:2]
    H, W = int(round(h * z)) | 1, int(round(w * z)) | 1
    return np.asarray(Image.fromarray(f).resize((W, H), Image.LANCZOS))


def tags_to_redraw(hero, pack, skip, zplan):
    out = []
    kinds = kinds_of(hero, pack)
    for fn in sorted(os.listdir(fx_dir(pack))):
        if not (fn.startswith(f"{pack}_{hero}_") and fn.endswith("#anim.fanim")):
            continue
        sheet = fn[:-len("#anim.fanim")]
        if sheet in skip:
            continue
        tags = D.load_sheet(os.path.join(fx_dir(pack), sheet))
        for tag, frames in tags.items():
            if tag.startswith(("hd_", "lo_")) or tag == "idle" or not any(a[..., 3].any() for a, _ in frames):
                continue
            z = zplan.get(f"{sheet}:{tag}", {}).get("zoom")
            if not needs(tags, tag) and not z:
                continue
            if z and not needs(tags, tag):
                continue            # it has a raw: densify_fx.py --zoom redraws it from that
            distinct, index = [], []
            for a, _ in frames:
                k = next((i for i, d in enumerate(distinct) if d.shape == a.shape and np.array_equal(d, a)), None)
                if k is None:
                    distinct.append(a)
                    k = len(distinct) - 1
                index.append(k)
            out.append({"hero": hero if pack == "league" else f"{pack}_{hero}", "pack": pack, "sheet": sheet,
                        "tag": tag, "frames": len(frames), "distinct": index,
                        "cells": distinct, "kind": kinds.get((sheet, tag), "effect"), "zoom": z,
                        "symmetry": symmetric([d for d in distinct if d[..., 3].any()])})
    return out


def guide(cells, z):
    """the guide strip at 1x (each cell the largest frame's size, every frame centred) and at SCALE"""
    if z:
        cells = [zoomed(c, z) for c in cells]
    h = max(c.shape[0] for c in cells) | 1
    w = max(c.shape[1] for c in cells) | 1
    strip = np.zeros((h, w * len(cells), 4), np.uint8)
    for k, c in enumerate(cells):
        strip[:, k * w:(k + 1) * w] = D.centre_pad(c, h, w)
    big = np.repeat(np.repeat(strip, SCALE, 0), SCALE, 1)
    return strip, big, (w, h)


def contact(hero, items, path):
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22) if os.path.isfile("C:/Windows/Fonts/msyh.ttc") else None
    rows = []
    for it in items:
        im = Image.fromarray(it["big"])
        if im.width > 2400:
            im = im.resize((2400, max(1, int(im.height * 2400 / im.width))), Image.NEAREST)
        rows.append((f"{it['tag']}  ({it['kind']}, {len(it['cells'])} frames, cell {it['cell_1x'][0]}x{it['cell_1x'][1]} game px"
                     + (f", ZOOM x{it['zoom']}" if it["zoom"] else "") + ")", im))
    W = max(r[1].width for r in rows) + 20
    H = sum(r[1].height + 44 for r in rows) + 10
    can = Image.new("RGB", (W, H), (32, 36, 44))
    d = ImageDraw.Draw(can)
    y = 6
    for label, im in rows:
        d.text((10, y), f"{hero}  {label}", fill=(255, 220, 120), font=font)
        y += 32
        bg = Image.new("RGBA", im.size, (58, 64, 74, 255))
        bg.alpha_composite(im.convert("RGBA"))
        can.paste(bg.convert("RGB"), (10, y))
        y += im.height + 12
    can.save(G.lp(path))


def hero_refs(hero, pack, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(ROOT, pack, "champions", f"{pack}_{hero}")
    if os.path.isfile(stem + "#anim.fanim"):
        tags = D.load_sheet(stem)
        idle = (tags.get("hd_idle") or tags.get("idle") or [[None]])[0][0]
        if idle is not None:
            Image.fromarray(idle).resize((idle.shape[1] * 4, idle.shape[0] * 4), Image.NEAREST).save(
                G.lp(os.path.join(out_dir, "hero.png")))
    # the hero's effects dense already (the style to match): a few of them
    shown = []
    for fn in sorted(os.listdir(fx_dir(pack))):
        if fn.startswith(f"{pack}_{hero}_") and fn.endswith("#anim.fanim"):
            tags = D.load_sheet(os.path.join(fx_dir(pack), fn[:-len("#anim.fanim")]))
            for t, fr in tags.items():
                if t.startswith("hd_") and t != "hd_idle" and not needs(tags, t[3:]):
                    a = max((f for f, _ in fr), key=lambda f: (f[..., 3] > 0).sum())
                    shown.append(a)
    if shown:
        shown = shown[:8]
        h = max(a.shape[0] for a in shown)
        can = Image.new("RGBA", (sum(a.shape[1] + 8 for a in shown) * 3, h * 3), (58, 64, 74, 255))
        x = 0
        for a in shown:
            im = Image.fromarray(a).resize((a.shape[1] * 3, a.shape[0] * 3), Image.NEAREST)
            can.alpha_composite(im, (x, (h * 3 - im.height) // 2))
            x += im.width + 24
        can.convert("RGB").save(G.lp(os.path.join(out_dir, "dense.png")))


PROMPT_ZH = """# 特效补画包 {n}（共 {total} 个包）：{heroes_zh}

这些特效现在游戏里只是把 1 倍小图平滑放大（Scale2x）：要么当初只有 1 倍小图，要么 Codex 原图和现在的样子对不上（小特效
当初在 1 倍下重新设计过），读不出忠实的高清版。请把整个压缩包 `fx_redraw_{n}.zip` 和这份说明一起交给
Codex（在同一个对话里），让它按下面英文部分逐张重画；完成后它会给出 `outputs/fx_redraw_{n}_done.zip`，你告诉我
「codex交付了」并给我这个压缩包，我读回来接进游戏。

- 本包：{n_heroes} 个英雄，{n_tags} 个特效动画，共要画 {n_frames} 帧。
- 底稿是游戏里现在的样子，每个游戏像素放大成 8×8 的方块：画的位置和大小必须对准底稿（游戏里的大小不变）。
- 这次只要「同一个特效、画得更细」：上一轮 Codex 有不少特效画成了别的样子（少了星芒、多了光圈和碎点、毛边、对称没了、颜色变暗），都被退回用了平滑放大。英文部分逐条写了禁止项，画完我会逐帧和底稿对比，不像的照样不用。
- 标了 ZOOM 的是大招范围图：底稿已经按实际判定范围放大好了，照底稿的大小画。

---

"""

PROMPT_EN = """## Task: redraw {n_tags} game effect animations at high resolution ({n_frames} frames, {n_heroes} heroes)

You are redrawing the skill effects (VFX) of champions in a 2D pixel-art auto-battler. Each effect exists today only as a
tiny pixel animation; we need a detailed, clean, high-resolution drawing of every frame, **at exactly the same place and
size**, so the game can show it finer without changing how big it looks.

### Inputs (in fx_redraw_{n}.zip)
- `guides/<hero>/<hero>_fx_<tag>.png` - one effect animation: its frames side by side in equal cells (no gutters), each
  game pixel drawn as an 8 x 8 block. **The guide is the in-game footprint**: what you draw in a cell must cover the
  same coloured blocks (within one block), centred the same, no bigger and no smaller.
- `guides/<hero>/_contact.png` - all of that hero's guides with their names, to read them easily.
- `refs/<hero>/hero.png` - the champion (colours, scale); `refs/<hero>/dense.png` (when present) - this champion's
  effects that were already redrawn: match that style.
- `manifest.json` - per item: hero, tag, file, cells (frames to draw), cell_1x / cell_8x (cell size in game px / in
  guide px), kind (effect = a hit, burst or area played at a point or on a unit; projectile = flies, drawn pointing
  right, the game turns it; buff = loops on a unit), symmetry (left-right / top-bottom / none), zoom.

### What to draw - THE SAME EFFECT, ONLY FINER
This is a fidelity job, not a redesign. A reviewer compares every frame you draw with its guide frame side by side, and
any frame that looks different from the guide (not just finer) is thrown away and the old blocky one kept.
1. Read each guide frame by frame: every shape, its colours, its brightest parts, and how it changes between frames.
2. Draw each frame as the same picture at a higher resolution: the same shapes in the same places, each edge smoother,
   each curve rounder, gradients and highlights a little richer inside the shapes the guide already has. Clean
   pixel-art-like rendering with flat, deliberate colour areas; no painterly texture.
3. Keep EVERY part of the guide, at its size and count: every ring, arc, line, star or cross sparkle (keep a '+' a crisp
   '+', a 4-point star a 4-point star), symbol, crown, notch, dot pattern, chunk and shard. Nothing goes missing.
4. Add NOTHING the guide does not have: no extra rings, flares, wings, splashes, outlines, glows, sparks, specks or
   debris; no new crack patterns or swirls inside a shape.
5. Same thickness: a line or ring is as thick as the guide's (not thinner, not thicker); a solid area stays solid; a
   sparse frame stays as sparse, a dense one as dense.
6. Same colours: the guide's hues and brightness; no new dark blotches, no shift to another hue, no greyed or dimmed
   copies of bright parts.
7. Clean: no speckle, dither, stipple, noise, stray single dots, hatching, scribbles or hairy/ragged edges. Edges are
   smooth and continuous where the guide's are continuous.
8. Symmetry: when the guide frame is left-right (or top-bottom) symmetric, yours is exactly mirror-symmetric too
   (draw one half, mirror it). Projectiles keep pointing right.
9. Small effects (a few game pixels): keep the guide's exact shape - just smoother edges; do not reinterpret them.
10. Keep every frame exactly in its cell: same centre, same footprint as the guide's blocks (± 1 block). Do not move
    anything into a neighbouring cell. Empty cells stay empty. Frames keep the same size from one to the next unless
    the guide's do change.
11. Items with `zoom` set are area pictures already enlarged to the area the skill really hits: keep the guide's size.
12. Background fully transparent (alpha 0). The game reads pixels with alpha >= 50 %.

### Deliverables
- `outputs/fx_redraw_{n}/<hero>/<hero>_fx_<tag>.png` - RGBA, **exactly the guide's pixel size**, frames in the guide's
  cells, one file per guide (same names).
- `outputs/fx_redraw_{n}/manifest.json` - every file delivered: hero, tag, size, cells; and any item you could not do,
  with why.
- `outputs/fx_redraw_{n}/check/<hero>.png` - each delivered strip laid over its guide at 50 % (placement check).
- Zip everything as `outputs/fx_redraw_{n}_done.zip`.

### Checks before you finish
- Every output has its guide's exact size; every non-empty guide cell has a drawing; nothing crosses a cell border.
- Each drawing's opaque area lines up with the guide's blocks (± 8 px); symmetric items are symmetric.
- Colours stay in the guide's colour family; nothing is left of a checkerboard or a background.

### This pack
{table}
"""


def write_prompt(root, n, total, group, man):
    heroes_zh = "、".join(group)
    lines = ["| hero | tags (frames) |", "|---|---|"]
    for h in group:
        items = [m for m in man if m["hero"] == h]
        lines.append(f"| {h} | " + ", ".join(f"{m['tag']} ({m['cells']}{', ZOOM x' + str(m['zoom']) if m['zoom'] else ''})"
                                             for m in items) + " |")
    n_frames = sum(m["cells"] for m in man)
    text = (PROMPT_ZH.format(n=n, total=total, heroes_zh=heroes_zh, n_heroes=len(group), n_tags=len(man),
                             n_frames=n_frames)
            + PROMPT_EN.format(n=n, n_tags=len(man), n_frames=n_frames, n_heroes=len(group), table="\n".join(lines)))
    path = os.path.join(os.path.dirname(root), f"FX_REDRAW_PROMPT_{n}.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--heroes", nargs="*")
    ap.add_argument("--per-pack", type=int, default=12, help="heroes in each pack")
    ap.add_argument("--zoom-plan", help="ult_zoom_plan.py's JSON: {hero: {sheet:tag: {zoom ...}}} (tft heroes as "
                                        "tft_<hero>)")
    ap.add_argument("--packs", nargs="*", default=["league", "tft"], help="the mod packs whose heroes are packed")
    a = ap.parse_args()
    zp = json.load(open(a.zoom_plan, encoding="utf-8")) if a.zoom_plan else {}
    todo, packs_of = {}, {}
    for pack in a.packs:
        skip = hd_effect_sheets(pack)
        ch = os.path.join(ROOT, pack, "champion")
        heroes = sorted(f[len(pack) + 1:-len(".data_champion")] for f in os.listdir(ch) if f.endswith(".data_champion"))
        if a.heroes:
            heroes = [h for h in heroes if h in a.heroes or f"{pack}_{h}" in a.heroes]
        for h in heroes:
            key = h if pack == "league" else f"{pack}_{h}"
            items = tags_to_redraw(h, pack, skip, zp.get(key, {}))
            if items:
                todo[key] = items
                packs_of[key] = (pack, h)
    names = sorted(todo)
    packs = [names[i:i + a.per_pack] for i in range(0, len(names), a.per_pack)]
    summary = []
    for n, group in enumerate(packs, 1):
        root = os.path.join(a.out, f"fx_redraw_{n}")
        if os.path.isdir(root):
            shutil.rmtree(root)
        man = []
        for h in group:
            gdir = os.path.join(root, "guides", h)
            os.makedirs(gdir, exist_ok=True)
            for it in todo[h]:
                strip, big, (w, hgt) = guide(it["cells"], it["zoom"])
                it["big"] = big
                it["cell_1x"] = [w, hgt]
                file = f"{h}_fx_{it['tag']}.png"
                Image.fromarray(big).save(G.lp(os.path.join(gdir, file)))
                man.append({"hero": h, "sheet": it["sheet"], "tag": it["tag"], "file": f"guides/{h}/{file}",
                            "kind": it["kind"], "frames": it["frames"], "cells": len(it["cells"]),
                            "distinct": it["distinct"], "cell_1x": [w, hgt], "cell_8x": [w * SCALE, hgt * SCALE],
                            "guide_size": [big.shape[1], big.shape[0]], "symmetry": it["symmetry"], "zoom": it["zoom"]})
            contact(h, todo[h], os.path.join(gdir, "_contact.png"))
            hero_refs(packs_of[h][1], packs_of[h][0], os.path.join(root, "refs", h))
        with open(os.path.join(root, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump({"scale": SCALE, "pack": n, "heroes": group, "items": man}, f, ensure_ascii=False, indent=1)
        cells = sum(m["cells"] for m in man)
        summary.append((n, group, len(man), cells))
        prompt = write_prompt(root, n, len(packs), group, man)
        zpath = shutil.make_archive(root, "zip", os.path.dirname(root), os.path.basename(root))
        print(f"fx_redraw_{n}: {len(group)} heroes, {len(man)} tags, {cells} frames to draw: {' '.join(group)} "
              f"-> {zpath} ({os.path.getsize(zpath) / 1e6:.1f} MB), {prompt}")
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump([{"pack": n, "heroes": g, "tags": t, "frames": c} for n, g, t, c in summary], f, indent=1)


if __name__ == "__main__":
    main()
