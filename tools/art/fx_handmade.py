#!/usr/bin/env python3
"""Effect tags redrawn by our own code (tools/art/fx_vector.py), kept in the repo and put into the sheets' hd_ frames
(the user, 2026-11-14: 「所有英雄你觉得特效模糊的 不是太清晰的 你也改改 改成高清一点的 我说的动画和特效都不依赖codex全部交给你来完成」
「反正不合格的特效和动画你可以手搓」).

    python -I tools/art/fx_handmade.py --redraw SHEET:TAG [SHEET:TAG ...] [--note TEXT]   # draw, store, apply
    python -I tools/art/fx_handmade.py [--hero h ...] [--dry]                              # apply what is stored
    python -I tools/art/fx_handmade.py --check                                             # the sheets hold what is stored
    python -I tools/art/fx_handmade.py --drop SHEET:TAG [...]                              # forget a stored tag

--redraw: every 1x frame of the tag is redrawn PPU 2 by fx_vector.redraw_tag (the same drawing, its boundaries traced and
smoothed inside the corridor its pixels leave them: fx_vector.py's notes), laid over the Scale2x twin densify_fx.py
gives it (draw_tag: a game pixel the redraw leaves as its plain square is that twin's), and kept as
assets/source/<hero>/fx_handmade/<sheet>/<tag>.png - the tag's distinct dense frames side by side, each centred in a cell
twice the tag's largest 1x frame - with an entry in that folder's manifest.json: the frames' order, each distinct frame's
1x size, and a hash of the tag's 1x frames. What is stored is the PICTURE, not the recipe: a later change of fx_vector.py
does not change an accepted tag (redraw it again to take the new code).

Applying: each stored tag whose 1x frames are still the ones it was drawn from (the hash) gets its hd_ frames from its
strip; a tag changed since is left alone and said so. Nothing else of the sheet changes: the 1x tags, the frame counts,
the durations and the frames' sizes stay as they are (strips.write_sheet, frames shared).

tools/art/densify_fx.py ends a hero's run by applying that hero's stored handmade tags, after Codex's redraws
(import_fx_redraw.apply): a handmade tag wins over both. A tag is only stored after its review page was looked at: the
bar is the user's (2026-11-09 「别给我整的更差了 我要的是质量更好的」; 2026-11-10 on a Scale2x-like twin 「我看不出有啥区别啊」) -
never worse than what is in the game, the same design, a difference one can see.
"""
import argparse
import glob
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import densify_fx as D  # noqa: E402
import fx_vector as V  # noqa: E402

G = D.G
PPU = 2
STORE = "fx_handmade"
BY = "fx_vector 4"          # what drew a stored tag (raise the number when the redraw's rules change)


def hero_of(sheet):
    """the hero folder of a sheet: league_<hero>_..., tft_<hero>_..."""
    return sheet.split("_")[1]


def pack_of(sheet):
    return sheet.split("_", 1)[0]


def store_dir(hero):
    return os.path.join(ROOT, "assets", "source", hero, STORE)


def entries(hero):
    p = os.path.join(store_dir(hero), "manifest.json")
    return json.load(open(G.lp(p), encoding="utf-8"))["items"] if os.path.isfile(p) else []


def write_entries(hero, items):
    base = store_dir(hero)
    p = os.path.join(base, "manifest.json")
    if not items:
        if os.path.isfile(p):
            os.remove(G.lp(p))
        return
    os.makedirs(base, exist_ok=True)
    out = {"about": "Effect tags redrawn by tools/art/fx_vector.py (kept by tools/art/fx_handmade.py): each strip holds "
                    "its tag's distinct hd_ frames (PPU 2), centred in cells twice the tag's largest 1x frame",
           "items": sorted(items, key=lambda e: (e["sheet"], e["tag"]))}
    with open(G.lp(p), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")


def distinct_of(frames):
    """the tag's distinct frames and each frame's index among them"""
    distinct, index = [], []
    for a, _ in frames:
        k = next((i for i, d in enumerate(distinct) if d.shape == a.shape and np.array_equal(d, a)), None)
        if k is None:
            distinct.append(a)
            k = len(distinct) - 1
        index.append(k)
    return distinct, index


def hash_1x(frames):
    """a hash of a tag's 1x frames (sizes, pixels, durations): the tag a stored strip was drawn from"""
    h = hashlib.sha256()
    for a, ms in frames:
        h.update(f"{a.shape[1]}x{a.shape[0]}@{ms:g};".encode())
        h.update(a.tobytes())
    return h.hexdigest()


def strip_of(dense, P=PPU):
    """the distinct dense frames side by side, each centred in a cell as large as the largest"""
    H = max(g.shape[0] for g in dense)
    W = max(g.shape[1] for g in dense)
    out = np.zeros((H, W * len(dense), 4), np.uint8)
    for k, g in enumerate(dense):
        oy, ox = (H - g.shape[0]) // 2, (W - g.shape[1]) // 2
        out[oy:oy + g.shape[0], k * W + ox:k * W + ox + g.shape[1]] = g
    return out


def frames_of(strip, entry, P=PPU):
    """the tag's dense frames from its strip, or None when the strip is not the entry's size"""
    sizes = entry["sizes"]
    W = max(s[0] for s in sizes) * P
    H = max(s[1] for s in sizes) * P
    if strip.shape[:2] != (H, W * len(sizes)):
        return None
    dense = []
    for k, (w, h) in enumerate(sizes):
        oy, ox = (H - h * P) // 2, (W - w * P) // 2
        dense.append(strip[oy:oy + h * P, k * W + ox:k * W + ox + w * P].copy())
    return [dense[k] for k in entry["distinct"]]


def checks(frames, dense, P=PPU):
    """What the redraw must hold whatever it looks like (the review judges the rest): every frame P times its 1x frame's
    size, an empty frame empty, no colour the tag's 1x frames have not, and no drawn 1x pixel whose colour is nowhere in
    its square (a mark lost). -> a list of what is wrong (empty: fine)"""
    bad = []
    pal = {tuple(c) for a, _ in frames for c in a[a[..., 3] > 0]}
    grid = [V.block_grid(a)[0] for a, _ in frames]
    for i, ((a, _), g) in enumerate(zip(frames, dense)):
        h, w = a.shape[:2]
        if g.shape[:2] != (h * P, w * P):
            bad.append(f"frame {i + 1}: {g.shape[1]}x{g.shape[0]}, not {P} times {w}x{h}")
            continue
        if not a[..., 3].any():
            if g[..., 3].any():
                bad.append(f"frame {i + 1}: drawn where the 1x frame is empty")
            continue
        new = {tuple(c) for c in g[g[..., 3] > 0]}
        if not new <= pal:
            bad.append(f"frame {i + 1}: {len(new - pal)} colour(s) the 1x frames have not")
        if ((g[..., 3] > 0) & (g[..., 3] < 255)).any() and not ((a[..., 3] > 0) & (a[..., 3] < 255)).any():
            bad.append(f"frame {i + 1}: half-transparent pixels the 1x frame has not")
        if grid[i] == 1:        # (a picture enlarged before it became the frame is judged on its source grid)
            same = (g.reshape(h, P, w, P, 4) == a[:, None, :, None, :]).all(-1).any(axis=(1, 3))
            lost = int((~same & (a[..., 3] > 0)).sum())
            if lost:
                bad.append(f"frame {i + 1}: {lost} drawn 1x pixel(s) whose colour is nowhere in their square")
    return bad


# ------------------------------------------------------------------ drawing and keeping
def draw_tag(sheet, tag, frames, **kw):
    """A tag's frames redrawn (fx_vector.redraw_tag) - and, wherever the redraw left a game pixel as its plain square,
    that pixel as the twin densify_fx.py gives it (Scale2x: a small dot's corners cut, a solid area's steps halved - what
    is in the game now; its squares for a tag fx_x2_tags.txt keeps square). The redraw is a layer over that twin: a
    pixel it has nothing to say about is never squarer than it was."""
    how = D.x2_tags().get((sheet, tag))
    new = V.redraw_tag([a for a, _ in frames], PPU, **kw)
    out = []
    for (a, _), g in zip(frames, new):
        h, w = a.shape[:2]
        base = D.square(a, PPU) if how == "square" else D.finer(a, PPU)
        plain = (g.reshape(h, PPU, w, PPU, 4) == a[:, None, :, None, :]).all(-1).all(axis=(1, 3))
        m = np.repeat(np.repeat(plain, PPU, 0), PPU, 1)
        g = g.copy()
        g[m] = base[m]
        out.append(g)
    return out


def redraw(keys, note="", log=print, **kw):
    """draw the tags (sheet:tag), keep their strips and manifest entries; -> the heroes touched"""
    heroes = set()
    for key in keys:
        sheet, tag = key.split(":", 1)
        stem = os.path.join(ROOT, pack_of(sheet), "effects", sheet)
        tags = D.load_sheet(stem)
        if tag not in tags or "hd_" + tag not in tags:
            sys.exit(f"{key}: no such tag (or no hd_ twin) in the sheet")
        frames = tags[tag]
        dense = draw_tag(sheet, tag, frames, **kw)
        wrong = checks(frames, dense)
        if wrong:
            sys.exit(f"{key}: not stored - " + "; ".join(wrong))
        distinct, index = distinct_of(frames)
        firsts = [index.index(k) for k in range(len(distinct))]
        hero = hero_of(sheet)
        rel = f"{sheet}/{tag}.png"
        dst = os.path.join(store_dir(hero), rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        Image.fromarray(strip_of([dense[i] for i in firsts]), "RGBA").save(G.lp(dst), optimize=True)
        e = {"sheet": sheet, "tag": tag, "file": rel, "ppu": PPU, "frames": len(frames), "distinct": index,
             "sizes": [[int(d.shape[1]), int(d.shape[0])] for d in distinct], "of_1x": hash_1x(frames), "by": BY,
             "sha256": hashlib.sha256(open(G.lp(dst), "rb").read()).hexdigest()}
        if kw:
            e["options"] = {k: v for k, v in sorted(kw.items())}
        if note:
            e["note"] = note
        items = [x for x in entries(hero) if (x["sheet"], x["tag"]) != (sheet, tag)] + [e]
        write_entries(hero, items)
        heroes.add(hero)
        log(f"  {key}: {len(distinct)} distinct frame(s) kept in {os.path.relpath(dst, ROOT)}")
    return heroes


def drop(keys, log=print):
    for key in keys:
        sheet, tag = key.split(":", 1)
        hero = hero_of(sheet)
        items = entries(hero)
        keep = [x for x in items if (x["sheet"], x["tag"]) != (sheet, tag)]
        if len(keep) == len(items):
            log(f"  {key}: not stored")
            continue
        p = os.path.join(store_dir(hero), f"{sheet}/{tag}.png")
        if os.path.isfile(p):
            os.remove(G.lp(p))
        write_entries(hero, keep)
        log(f"  {key}: dropped (rerun tools/art/densify_fx.py --hero {hero} to give the tag its other frames back)")


# ------------------------------------------------------------------ into the sheets
def apply(hero, dry=False, log=print):
    """the hero's stored tags into its sheets' hd_ frames; -> {sheet:tag: {"used", "why", "changed"}}"""
    res = {}
    by_sheet = {}
    for e in entries(hero):
        by_sheet.setdefault(e["sheet"], []).append(e)
    for sheet, es in sorted(by_sheet.items()):
        stem = os.path.join(ROOT, pack_of(sheet), "effects", sheet)
        if not os.path.isfile(stem + "#anim.fanim"):
            log(f"  {sheet}: no such sheet - skipped")
            continue
        tags = D.load_sheet(stem)
        changed = False
        for e in es:
            key = f"{sheet}:{e['tag']}"
            frames = tags.get(e["tag"])

            def no(why):
                res[key] = {"used": False, "why": why, "changed": False}
                log(f"  {key}: handmade frames not used - {why}")
            if frames is None or "hd_" + e["tag"] not in tags:
                no("no such tag (or no hd_ twin) in the sheet")
                continue
            if hash_1x(frames) != e["of_1x"]:
                no("its 1x frames changed since it was drawn (python -I tools/art/fx_handmade.py --redraw " + key + ")")
                continue
            strip = np.asarray(Image.open(G.lp(os.path.join(store_dir(hero), e["file"]))).convert("RGBA"))
            dense = frames_of(strip, e)
            if dense is None:
                no("the strip is not the size its entry says")
                continue
            wrong = checks(frames, dense)
            if wrong:
                no("; ".join(wrong))
                continue
            old = tags["hd_" + e["tag"]]
            diff = any(not np.array_equal(g, o[0]) for g, o in zip(dense, old))
            res[key] = {"used": True, "why": None, "changed": diff}
            if diff:
                tags["hd_" + e["tag"]] = [(g, ms) for g, (_, ms) in zip(dense, frames)]
                changed = True
            log(f"  {key}: handmade frames {'put in' if diff else 'already in'} ({len(e['sizes'])} distinct)")
        if changed and not dry:
            G.write_sheet(G.lp(stem), tags, share=True)
            log(f"  {sheet}: written")
    return res


def stored_heroes():
    return sorted({os.path.basename(os.path.dirname(os.path.dirname(p)))
                   for p in glob.glob(os.path.join(ROOT, "assets", "source", "*", STORE, "manifest.json"))})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--redraw", nargs="+", metavar="SHEET:TAG")
    ap.add_argument("--drop", nargs="+", metavar="SHEET:TAG")
    ap.add_argument("--note", default="", help="kept in the redrawn tags' manifest entries")
    ap.add_argument("--hero", nargs="*")
    ap.add_argument("--dry", action="store_true", help="read and judge, write no sheet")
    ap.add_argument("--check", action="store_true", help="exit 1 unless every stored tag is in its sheet as stored")
    a = ap.parse_args()
    if a.drop:
        drop(a.drop)
        return
    heroes = a.hero
    if a.redraw:
        heroes = sorted(redraw(a.redraw, a.note))
    heroes = heroes or stored_heroes()
    report = {}
    for hero in heroes:
        print(f"{hero}:")
        report.update(apply(hero, a.dry or a.check, log=(lambda s: None) if a.check else print))
    used = sum(1 for r in report.values() if r["used"])
    if a.check:
        off = sorted(k for k, r in report.items() if not r["used"] or r["changed"])
        for k in off:
            print(f"{k}: {'not in its sheet as stored' if report[k]['used'] else report[k]['why']}")
        print(f"{len(report) - len(off)} of {len(report)} handmade tags in their sheets as stored")
        sys.exit(1 if off else 0)
    print(f"{used} of {len(report)} handmade tags in their sheets")


if __name__ == "__main__":
    main()
