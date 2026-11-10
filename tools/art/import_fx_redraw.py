#!/usr/bin/env python3
"""Codex's effect redraws (the packs of tools/art/pack_fx_redraw.py) into the effect sheets' dense twins (the effects PPU,
2026-11-10, the user handing over the first delivery: 「第一个压缩包完成了 特效重做的 你继续处理」).

    python -I tools/art/import_fx_redraw.py --store DELIVERY PACK_MANIFEST   # keep a delivery in the repo
    python -I tools/art/import_fx_redraw.py [--hero h ...] [--review DIR] [--report JSON] [--dry]

--store: DELIVERY is Codex's outputs/fx_redraw_<n>/ (its manifest.json: one entry a delivered strip with the sheet and the
source_entry_index of PACK_MANIFEST, the pack's own manifest.json, whose entries hold the frames' distinct cells); every
delivered strip is copied to assets/source/<hero>/codex_fx_redraw/<sheet>/<tag>.png and listed in that folder's
manifest.json (sheet, tag, the guide's cells and cell size, symmetry, zoom, the pack it came in). Names repeat across a
hero's sheets (Ashe's arrow and hit in league_ashe_fx and league_ashe_r: the pack wrote one guide over the other, Codex
kept them apart by sheet), so the sheet is part of the path.

Without --store every stored strip of the heroes asked (default: every hero with one) gives its tag new hd_ frames. A
strip is the guide's size: its cells side by side, each the guide's cell (the tag's largest frame, odd sizes) 8 px a game
pixel, each distinct 1x frame centred in its cell (pack_fx_redraw.guide) - so the cell IS a raw on an exact grid and
needs no fit: game = raw / 8 - (ox, oy), (ox, oy) the frame's place in the cell. Each frame then goes through what a raw
does in densify_fx.py: the gate at 1x (F, colours), refine (the dense silhouette within one fine pixel of the 1x squares,
inner squares solid, each fine pixel coloured by a vote over the 1x frame's own colours - the tag's palette), outside
the squares only at their steps' inner corners (corners_only: a thin line or a dot never reads in thicker), mirrored
where the 1x frame is its own mirror, the read-back gate; a tag takes its redraw only when every drawn frame of it passes
(specks aside), else it keeps the hd_ frames it has (Scale2x). The tag's 1x frames must still be the ones the pack drew
from (same distinct cells, same cell size): a tag changed since is left alone (said in the log). A redraw wins over the
review blocklist (tools/art/fx_x2_tags.txt: those were kept off Codex's OLD raws); --review shows them like the rest.
What the review turns down (finer is not enough - the same effect: no thicker lines, no closed shapes, no blobs) goes
in tools/art/fx_redraw_rejects.txt (`sheet:tag  # why`): those tags keep their Scale2x frames.

The sheets are written back with every other tag as it was (strips.write_sheet, frames shared); league.dll / tft.dll
embed every dense sheet's .fanim (src/fx_ppu.rs), so a written sheet means a rebuilt pack DLL.
densify_fx.py ends a hero's run by applying that hero's stored redraws (apply()), so a rerun keeps them.
"""
import argparse
import glob
import hashlib
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import densify_fx as D  # noqa: E402

G = D.G
SCALE = 8                 # guide px a game pixel
PPU = 2
STORE = "codex_fx_redraw"


def hero_dir(hero):
    """assets/source/<hero> of a pack manifest's hero (TFT heroes come as tft_<hero>)"""
    return os.path.join(ROOT, "assets", "source", hero[4:] if hero.startswith("tft_") else hero)


def pack_of(sheet):
    return sheet.split("_", 1)[0]


# ------------------------------------------------------------------ keeping a delivery
def store(delivery, pack_manifest):
    ours = json.load(open(G.lp(pack_manifest), encoding="utf-8-sig"))
    theirs = json.load(open(G.lp(os.path.join(delivery, "manifest.json")), encoding="utf-8-sig"))
    by_hero = {}
    for it in theirs["items"]:
        if it.get("status", "delivered") != "delivered":
            continue
        o = ours["items"][it["source_entry_index"]]
        if (o["sheet"], o["tag"]) != (it["sheet"], it["tag"]):
            sys.exit(f"{it['file']}: entry {it['source_entry_index']} of the pack is {o['sheet']}:{o['tag']}, the delivery "
                     f"says {it['sheet']}:{it['tag']}")
        src = os.path.join(delivery, it["file"])
        im = Image.open(G.lp(src))
        if list(im.size) != list(o["guide_size"]):
            sys.exit(f"{it['file']}: {im.size[0]}x{im.size[1]}, its guide is {o['guide_size'][0]}x{o['guide_size'][1]}")
        by_hero.setdefault(o["hero"], []).append((o, it, src))
    for hero, items in sorted(by_hero.items()):
        base = os.path.join(hero_dir(hero), STORE)
        mpath = os.path.join(base, "manifest.json")
        old = json.load(open(G.lp(mpath), encoding="utf-8")) if os.path.isfile(mpath) else {"items": []}
        keep = {(e["sheet"], e["tag"]): e for e in old["items"]}
        for o, it, src in items:
            rel = f"{o['sheet']}/{o['tag']}.png"
            dst = os.path.join(base, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(G.lp(src), G.lp(dst))
            keep[(o["sheet"], o["tag"])] = {
                "sheet": o["sheet"], "tag": o["tag"], "file": rel, "pack": ours.get("pack"),
                "source_entry_index": it["source_entry_index"], "kind": o["kind"], "frames": o["frames"],
                "distinct": o["distinct"], "cell_1x": o["cell_1x"], "cell_8x": o["cell_8x"],
                "guide_size": o["guide_size"], "symmetry": o["symmetry"], "zoom": o["zoom"],
                "sha256": hashlib.sha256(open(G.lp(dst), "rb").read()).hexdigest()}
        out = {"about": "Codex's redraws of this hero's effects on pack_fx_redraw.py's guides (8 px a game pixel, the "
                        "guide's cells); tools/art/import_fx_redraw.py reads them into the sheets' hd_ frames",
               "items": [keep[k] for k in sorted(keep)]}
        with open(G.lp(mpath), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(f"{hero}: {len(items)} strips kept in {os.path.relpath(base, ROOT)} ({len(out['items'])} in all)")


# ------------------------------------------------------------------ reading them back
def distinct_of(frames):
    """the tag's distinct 1x frames and each frame's index among them (pack_fx_redraw.tags_to_redraw's way)"""
    distinct, index = [], []
    for a, _ in frames:
        k = next((i for i, d in enumerate(distinct) if d.shape == a.shape and np.array_equal(d, a)), None)
        if k is None:
            distinct.append(a)
            k = len(distinct) - 1
        index.append(k)
    return distinct, index


def corners_only(g, arr, P=PPU):
    """the dense frame g drawn outside arr's squares only at the inner corners of arr's steps - the fine pixel of an
    empty square whose two neighbours on that corner's sides are both drawn, where Scale2x itself may draw: a thin line,
    a ring or a speck never reads in thicker than its squares. refine() lets a fine pixel within one of the squares be
    drawn where a quarter of it is covered, and Codex's strokes and dots are soft-edged and a little wide (review of the
    2026-11-10 delivery after the first: Akali's and Akshan's dots read in as crosses, their thin slashes, rings and
    sights twice as thick)"""
    t = arr[..., 3] > 0
    pad = np.pad(t, 1)
    above, below, left, right = pad[:-2, 1:-1], pad[2:, 1:-1], pad[1:-1, :-2], pad[1:-1, 2:]
    ok = np.repeat(np.repeat(t, P, 0), P, 1)
    for fy, ny in ((0, above), (P - 1, below)):
        for fx, nx in ((0, left), (P - 1, right)):
            ok[fy::P, fx::P] |= ~t & ny & nx
    out = g.copy()
    out[~ok] = 0
    return out


def redraw_tag(entry, frames, strip):
    """(dense frames or None, per-frame measures, why not): the tag's frames from its stored strip"""
    distinct, index = distinct_of(frames)
    if entry.get("zoom"):
        return None, [], "a zoomed guide (its 1x frames would have to be zoomed too): not read yet"
    h = max(c.shape[0] for c in distinct) | 1
    w = max(c.shape[1] for c in distinct) | 1
    if index != entry["distinct"] or [w, h] != list(entry["cell_1x"]):
        return None, [], (f"its 1x frames changed since the pack (distinct {index} vs {entry['distinct']}, cell {w}x{h} vs "
                          f"{entry['cell_1x'][0]}x{entry['cell_1x'][1]})")
    if strip.shape[:2] != (h * SCALE, w * SCALE * len(distinct)):
        return None, [], f"the strip is {strip.shape[1]}x{strip.shape[0]}, the guide {w * SCALE * len(distinct)}x{h * SCALE}"
    pal = np.unique(np.concatenate([a[a[..., 3] > 0][:, :3] for a, _ in frames if a[..., 3].any()]), axis=0)
    out, measures, short = [], [], []
    for i, (arr, _) in enumerate(frames):
        fh, fw = arr.shape[:2]
        if not arr[..., 3].any():
            out.append(np.zeros((fh * PPU, fw * PPU, 4), np.uint8))
            measures.append(None)
            continue
        k = index[i]
        cell = strip[:, k * w * SCALE:(k + 1) * w * SCALE].astype(np.float64) / 255.0
        raw = D.Raw(cell)
        oy, ox = (h - fh) // 2, (w - fw) // 2
        s, ty, tx = 1.0 / SCALE, -float(oy), -float(ox)
        if raw.box is None:
            measures.append({"empty": True})
            short.append(i)
            out.append(None)
            continue
        fq, iou, gap = D.fidelity(raw, arr, s, ty, tx)
        g = corners_only(D.refine(arr, raw, s, ty, tx, PPU, pal), arr)
        for axis in (1, 0):
            if D.symmetric(arr, axis):
                g = D.symmetrize(g, axis)
        rt, outside = D.readback(arr, g, PPU)
        tv = D.balance(arr, g, pal)
        m = {"f": round(fq, 3), "iou": round(iou, 3), "gap": round(gap, 3), "rt": round(rt, 3), "out": round(outside, 3),
             "tv": round(tv, 3), "squares": int((arr[..., 3] > 0).sum())}
        measures.append(m)
        bad = (fq < D.GATE_F or gap > D.GATE_GAP or rt > D.GATE_RT or outside > D.GATE_OUT or tv > D.GATE_TV)
        if bad and m["squares"] >= D.SPECK:
            short.append(i)
        out.append(None if bad else g)
    if short:
        return None, measures, "frame(s) " + ", ".join(str(i + 1) for i in short) + " failed the gate"
    # a speck that failed keeps its Scale2x frame inside an otherwise redrawn tag
    return out, measures, None


def entries(hero):
    p = os.path.join(hero_dir(hero), STORE, "manifest.json")
    return json.load(open(G.lp(p), encoding="utf-8"))["items"] if os.path.isfile(p) else []


REJECTS = os.path.join(HERE, "fx_redraw_rejects.txt")


def rejected(path=REJECTS):
    """{sheet:tag: why} the review kept off their redraws (tools/art/fx_redraw_rejects.txt)"""
    out = {}
    if os.path.isfile(path):
        for line in open(path, encoding="utf-8"):
            key, _, why = line.partition("#")
            key = key.strip()
            if ":" in key:
                out[key] = why.strip()
    return out


def apply(hero, dry=False, log=print, review=None):
    """the hero's stored redraws into its sheets' hd_ frames; -> {sheet:tag: result}"""
    res = {}
    by_sheet = {}
    off = rejected()
    for e in entries(hero):
        key = f"{e['sheet']}:{e['tag']}"
        if key in off:
            res[key] = {"used": False, "why": f"rejected by the review: {off[key]}"}
            log(f"  {key}: kept its Scale2x frames - rejected by the review ({off[key]})")
            continue
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
            if frames is None or "hd_" + e["tag"] not in tags:
                res[key] = {"used": False, "why": "no such tag (or no hd_ twin) in the sheet"}
                log(f"  {key}: {res[key]['why']}")
                continue
            strip = np.asarray(Image.open(G.lp(os.path.join(hero_dir(hero), STORE, e["file"]))).convert("RGBA"))
            dense, measures, why = redraw_tag(e, frames, strip)
            old = tags["hd_" + e["tag"]]
            res[key] = {"used": dense is not None, "why": why, "measures": measures}
            if dense is None:
                log(f"  {key}: kept its Scale2x frames - {why}")
                continue
            new = [(g if g is not None else o[0], ms) for g, o, (_, ms) in zip(dense, old, frames)]
            if review is not None:
                review.append((sheet, e["tag"], frames, old, new, strip, e))
            if any(not np.array_equal(a[0], b[0]) for a, b in zip(new, old)):
                tags["hd_" + e["tag"]] = new
                changed = True
            log(f"  {key}: redrawn ({sum(1 for g in dense if g is not None)} of {len(frames)} frames from the strip)")
        if changed and not dry:
            G.write_sheet(G.lp(stem), tags, share=True)
            log(f"  {sheet}: written")
    return res


# ------------------------------------------------------------------ review
def review_pages(items, out_dir, M=4):
    """a page a tag: each distinct frame - its 1x squares, the dense frame it had (Scale2x), the redraw read in, the strip's
    cell - at the same size (M screen px a game pixel), on the game's grass and on black"""
    os.makedirs(out_dir, exist_ok=True)
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    except OSError:
        font = None
    for sheet, tag, frames, old, new, strip, e in items:
        distinct, index = distinct_of(frames)
        firsts = [index.index(k) for k in range(len(distinct))]
        h = max(c.shape[0] for c in distinct) | 1
        w = max(c.shape[1] for c in distinct) | 1
        cw, ch = w * M, h * M
        cols = 4
        can = Image.new("RGB", (cols * (cw + 12) + 12, 40 + len(firsts) * (ch * 2 + 22)), (24, 26, 30))
        d = ImageDraw.Draw(can)
        d.text((10, 8), f"{sheet}:{tag}  ({len(frames)} frames, {len(distinct)} distinct; columns: 1x | Scale2x | redraw "
                        f"read in | Codex strip)", fill=(255, 220, 120), font=font)
        y = 40
        for k, i in enumerate(firsts):
            arr = frames[i][0]
            fh, fw = arr.shape[:2]
            oy, ox = (h - fh) // 2, (w - fw) // 2
            pics = [Image.fromarray(arr).resize((fw * M, fh * M), Image.NEAREST),
                    Image.fromarray(old[i][0]).resize((fw * M, fh * M), Image.NEAREST),
                    Image.fromarray(new[i][0]).resize((fw * M, fh * M), Image.NEAREST)]
            cell = Image.fromarray(strip[:, k * w * SCALE:(k + 1) * w * SCALE]).resize((cw, ch), Image.LANCZOS)
            for row, bg in enumerate(((66, 92, 60, 255), (0, 0, 0, 255))):
                for c, im in enumerate(pics + [cell]):
                    x0 = 12 + c * (cw + 12)
                    y0 = y + row * (ch + 6)
                    tile = Image.new("RGBA", (cw, ch), bg)
                    tile.alpha_composite(im.convert("RGBA"), (0, 0) if c == 3 else (ox * M, oy * M))
                    can.paste(tile.convert("RGB"), (x0, y0))
            y += ch * 2 + 22
        can.save(G.lp(os.path.join(out_dir, f"{sheet}__{tag}.png")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", nargs=2, metavar=("DELIVERY", "PACK_MANIFEST"))
    ap.add_argument("--hero", nargs="*")
    ap.add_argument("--review", help="a review page a redrawn tag here")
    ap.add_argument("--report", help="every tag's result here (JSON)")
    ap.add_argument("--dry", action="store_true", help="read and judge, write no sheet")
    a = ap.parse_args()
    if a.store:
        store(*a.store)
        return
    heroes = a.hero or sorted({os.path.basename(os.path.dirname(os.path.dirname(p)))
                               for p in glob.glob(os.path.join(ROOT, "assets", "source", "*", STORE, "manifest.json"))})
    report, items = {}, [] if a.review else None
    for hero in heroes:
        print(f"{hero}:")
        report.update(apply(hero, a.dry, review=items))
    if a.review:
        review_pages(items, a.review)
        print(f"review: {len(items)} pages in {a.review}")
    if a.report:
        with open(G.lp(a.report), "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
    used = sum(1 for r in report.values() if r["used"])
    print(f"{used} of {len(report)} redrawn tags taken")


if __name__ == "__main__":
    main()
