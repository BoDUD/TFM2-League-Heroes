#!/usr/bin/env python3
"""Pack league/ for the game and the Workshop: the same content, smaller and quicker to load.

The game reads every mod file except background music into memory when it starts (docs/perf.md), and on
2026-10-02 the installed league mod was 78 MB, 66 MB of it WAV clips. The repo keeps the editable sources
(pretty JSON, WAV clips, roomy sheets); this tool writes the copy that is installed or uploaded:

- WAV clips -> MP3 (VBR, LAME quality V0; mono 44.1 kHz stays), the format of the base game's own sound
  effects. The clip name does not change, so no .sound_info needs an edit. Clips that no .sound_info plays
  are left out. MP3 clips are copied as they are.
- Sprite sheets (#sheet.png + #anim.fanim) repacked: identical frames share one rect and the frames sit
  close together (1 px gap). Every frame keeps its size, its pixels and its duration; only x and y in the
  .fanim change.
- JSON files (.data_champion .fanim .i18n .champion_view .override_info .sound_info) minified: whitespace
  outside strings is dropped, the text of every value stays as it was.
- Everything else is copied as it is.

Every output is checked against its source: JSON equal after parsing, every frame pixel-identical, every
MP3 decoding to the WAV's length.

    python tools/package_mod.py                                # league/ -> dist/league, every hero
    python tools/package_mod.py --hero fiora --install         # one hero into <game>/mods/league
    python tools/package_mod.py --install                      # every hero (nobody else testing a hero)
    python tools/package_mod.py --out <folder>                 # e.g. the Workshop upload folder

--install merges the way the hero sessions' install scripts did: it writes the selected heroes' files,
replaces a clip's .wav with the .mp3 of the same name, refreshes only the selected heroes' keys in
text/champion.i18n, style/champion_view and mod.override_info, and keeps the higher mod_info version.
Every other hero's files stay as they are.

Needs Python 3.9+ with Pillow, numpy and soundfile (`pip install pillow numpy soundfile`; the libsndfile in
soundfile's wheel brings the LAME encoder). The audio is Riot's: it is never committed.
"""
import argparse
import concurrent.futures as cf
import copy
import hashlib
import io
import json
import os
import shutil
import sys
import time

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DIRS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Teamfight Manager2",
    r"C:\Program Files\Steam\steamapps\common\Teamfight Manager2",
    r"D:\steam\steamapps\common\Teamfight Manager2",
    r"D:\Steam\steamapps\common\Teamfight Manager2",
    r"D:\SteamLibrary\steamapps\common\Teamfight Manager2",
    r"E:\SteamLibrary\steamapps\common\Teamfight Manager2",
]
JSON_EXT = (".data_champion", ".fanim", ".i18n", ".champion_view", ".override_info", ".sound_info")
SHARED = ("text/champion.i18n", "style/champion_view.champion_view", "mod.override_info")
HERO_DIRS = ("champion", "champions", "effects", "icons", "sound/sfx")
AUDIO_EXT = (".wav", ".mp3")
MP3_QUALITY = 0.0          # libsndfile compression level for VBR MP3: 0.0 = LAME V0 (best), 1.0 = V9
MAX_SHEET = 2048           # repacked sheets stay within 2048 x 2048, like the sheets the mod ships today
GAP = 1                    # transparent pixels between packed frames


def lp(path):
    """Windows long-path form: the workspace sits under a long packaged-app path."""
    path = os.path.abspath(path)
    if os.name == "nt" and not path.startswith(chr(92) * 2):
        return chr(92) * 2 + "?" + chr(92) + path
    return path


def read(path):
    with open(lp(path), "rb") as f:
        return f.read()


def write(path, data):
    os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
    with open(lp(path), "wb") as f:
        f.write(data)


def parse_json(raw, where):
    def no_dupes(pairs):
        keys = [k for k, _ in pairs]
        if len(keys) != len(set(keys)):
            raise ValueError(f"{where}: duplicate key {sorted(k for k in keys if keys.count(k) > 1)[0]!r}")
        return dict(pairs)
    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=no_dupes)


def minify(raw):
    """Drop whitespace outside JSON strings. Numbers, strings and key order keep their exact text."""
    text = raw.decode("utf-8-sig")
    out = []
    in_str = esc = False
    start = 0
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch in " \t\r\n":
            out.append(text[start:i])
            start = i + 1
    out.append(text[start:])
    return "".join(out).encode("utf-8")


def dump_min(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


# ---------------------------------------------------------------- audio

def wav_to_mp3(raw, where):
    import soundfile as sf
    x, sr = sf.read(io.BytesIO(raw), dtype="float32")
    buf = io.BytesIO()
    sf.write(buf, x, sr, format="MP3", subtype="MPEG_LAYER_III", bitrate_mode="VARIABLE",
             compression_level=MP3_QUALITY)
    mp3 = buf.getvalue()
    y, sr2 = sf.read(io.BytesIO(mp3), dtype="float32")
    if sr2 != sr or len(y) != len(x):
        raise ValueError(f"{where}: MP3 decodes to {len(y)} samples at {sr2} Hz, the WAV has {len(x)} at {sr} Hz")
    return mp3, len(x) / sr


# ---------------------------------------------------------------- sprite sheets

def shelf_pack(sizes, width):
    """Place (w, h) boxes in rows no wider than `width`, tallest first. -> positions, used width, height."""
    order = sorted(range(len(sizes)), key=lambda i: (-sizes[i][1], -sizes[i][0], i))
    pos = [None] * len(sizes)
    x = y = row_h = used_w = 0
    for i in order:
        w, h = sizes[i]
        if x and x + w > width:
            y += row_h + GAP
            x = row_h = 0
        pos[i] = (x, y)
        used_w = max(used_w, x + w)
        x += w + GAP
        row_h = max(row_h, h)
    return pos, used_w, y + row_h


def repack(png_raw, anim, where):
    """-> (png bytes, fanim object, stats) with identical frames merged and packed tightly, or None to keep."""
    im = Image.open(io.BytesIO(png_raw))
    if im.mode != "RGBA":
        return None
    px = np.asarray(im)
    sheet_h, sheet_w = px.shape[:2]
    rects = []
    for tag, a in anim.get("anims", {}).items():
        for fr in a.get("frames", []):
            d = fr.get("data", {})
            r = tuple(d.get(k) for k in ("x", "y", "w", "h"))
            if any(not isinstance(v, (int, float)) or v != int(v) for v in r):
                return None                      # fractional or missing rect: leave this sheet alone
            x, y, w, h = (int(v) for v in r)
            if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > sheet_w or y + h > sheet_h:
                raise ValueError(f"{where}: frame of '{tag}' at {r} is outside the {sheet_w}x{sheet_h} sheet")
            rects.append((x, y, w, h))
    if not rects:
        return None
    content = {}                                 # pixel hash -> index into uniq
    uniq = []                                    # (w, h, pixels)
    slot_of_rect = {}
    for r in dict.fromkeys(rects):
        x, y, w, h = r
        crop = px[y:y + h, x:x + w]
        key = (w, h, hashlib.sha1(crop.tobytes()).hexdigest())
        if key not in content:
            content[key] = len(uniq)
            uniq.append(crop)
        slot_of_rect[r] = content[key]
    sizes = [(c.shape[1], c.shape[0]) for c in uniq]
    max_w = max(w for w, _ in sizes)
    best = None
    for width in sorted({max_w, 256, 384, 512, 768, 1024, 1536, MAX_SHEET}):
        if width < max_w or width > MAX_SHEET:
            continue
        pos, used_w, used_h = shelf_pack(sizes, width)
        if used_h > MAX_SHEET:
            continue
        cand = (used_w * used_h, max(used_w, used_h), pos, used_w, used_h)
        if best is None or cand[:2] < best[:2]:
            best = cand
    if best is None or best[0] >= sheet_w * sheet_h:
        return None
    _, _, pos, out_w, out_h = best
    out = np.zeros((out_h, out_w, 4), np.uint8)
    for i, crop in enumerate(uniq):
        x, y = pos[i]
        out[y:y + crop.shape[0], x:x + crop.shape[1]] = crop
    new_anim = copy.deepcopy(anim)
    for a in new_anim.get("anims", {}).values():
        for fr in a.get("frames", []):
            d = fr["data"]
            r = tuple(int(d[k]) for k in ("x", "y", "w", "h"))
            nx, ny = pos[slot_of_rect[r]]
            d["x"] = float(nx) if isinstance(d["x"], float) else nx
            d["y"] = float(ny) if isinstance(d["y"], float) else ny
    buf = io.BytesIO()
    Image.fromarray(out, "RGBA").save(buf, "PNG", optimize=True)
    png = buf.getvalue()
    check_frames(png_raw, anim, png, new_anim, where)
    return png, new_anim, (sheet_w * sheet_h, out_w * out_h, len(rects), len(uniq))


def frames_of(anim):
    for tag, a in anim.get("anims", {}).items():
        for i, fr in enumerate(a.get("frames", [])):
            yield tag, i, fr


def check_frames(png_a, anim_a, png_b, anim_b, where):
    pa = np.asarray(Image.open(io.BytesIO(png_a)).convert("RGBA"))
    pb = np.asarray(Image.open(io.BytesIO(png_b)).convert("RGBA"))
    fa, fb = list(frames_of(anim_a)), list(frames_of(anim_b))
    if [(t, i) for t, i, _ in fa] != [(t, i) for t, i, _ in fb]:
        raise ValueError(f"{where}: repacked .fanim lost or reordered frames")
    for (tag, i, a), (_, _, b) in zip(fa, fb):
        ra, rb = a["data"], b["data"]
        if (ra["w"], ra["h"]) != (rb["w"], rb["h"]) or {k: v for k, v in a.items() if k != "data"} != \
                {k: v for k, v in b.items() if k != "data"}:
            raise ValueError(f"{where}: frame {tag}[{i}] changed size or timing")
        xa, ya, xb, yb, w, h = (int(v) for v in (ra["x"], ra["y"], rb["x"], rb["y"], ra["w"], ra["h"]))
        if not np.array_equal(pa[ya:ya + h, xa:xa + w], pb[yb:yb + h, xb:xb + w]):
            raise ValueError(f"{where}: frame {tag}[{i}] pixels differ after repacking")
    strip = lambda d: {k: v for k, v in d.items() if k != "anims"}
    if strip(anim_a) != strip(anim_b) or {t: strip_frames(a) for t, a in anim_a["anims"].items()} != \
            {t: strip_frames(a) for t, a in anim_b["anims"].items()}:
        raise ValueError(f"{where}: repacked .fanim changed something besides frame positions")


def strip_frames(a):
    return {k: v for k, v in a.items() if k != "frames"}


# ---------------------------------------------------------------- the package

def hero_ids(src):
    return sorted(f[:-len(".data_champion")] for f in os.listdir(lp(os.path.join(src, "champion")))
                  if f.endswith(".data_champion"))


def belongs(name, hid):
    return name.startswith((hid + "_", hid + ".", hid + "#"))


def select_files(src, heroes, everything):
    """Relative paths (forward slashes) to package."""
    files = []
    for dp, dn, fn in os.walk(lp(src)):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), lp(src)).replace(os.sep, "/")
            sub = os.path.dirname(rel)
            if everything:
                files.append(rel)
            elif sub in HERO_DIRS and any(belongs(f, h) for h in heroes):
                files.append(rel)
            elif rel in SHARED or rel == "mod.mod_info":
                files.append(rel)
    return sorted(files)


def played_clips(src, files):
    clips = set()
    for rel in files:
        if rel.endswith(".sound_info"):
            name = os.path.basename(rel)[:-len(".sound_info")]
            for p in parse_json(read(os.path.join(src, rel)), rel).get("plays", []):
                if p.get("clip") == name:        # the game then finds no sound by that name (2026-10-07 log)
                    sys.exit(f"{rel}: plays a clip of its own name; give the clip another name (league_<id>_sfx_...)")
                clips.add(p.get("clip"))
    return clips


def build(src, heroes, everything, workers):
    """-> dict rel -> bytes, plus a report."""
    files = select_files(src, heroes, everything)
    clips = played_clips(src, files)
    out, report = {}, {"before": {}, "after": {}, "dropped": [], "sheets": [], "audio_s": 0.0}

    def count(side, rel, n):
        ext = os.path.splitext(rel)[1] or rel
        report[side][ext] = report[side].get(ext, 0) + n

    stems = {}
    for rel in files:
        stem, ext = os.path.splitext(rel)
        if ext in AUDIO_EXT:
            stems.setdefault(stem, []).append(ext)
    jobs = []
    for rel in files:
        raw_len = os.path.getsize(lp(os.path.join(src, rel)))
        count("before", rel, raw_len)
        stem, ext = os.path.splitext(rel)
        if ext in AUDIO_EXT:
            if os.path.basename(stem) not in clips:
                report["dropped"].append(rel)
                continue
            if ext == ".wav" and ".mp3" in stems[stem]:
                report["dropped"].append(rel + " (an .mp3 of the same clip is there)")
                continue
            jobs.append(("audio", rel))
        elif rel.endswith("#sheet.png") and os.path.isfile(lp(os.path.join(src, rel[:-len("#sheet.png")] + "#anim.fanim"))):
            jobs.append(("sheet", rel))
        elif rel.endswith("#anim.fanim") and os.path.isfile(lp(os.path.join(src, rel[:-len("#anim.fanim")] + "#sheet.png"))):
            continue                             # written with its sheet
        elif ext in JSON_EXT:
            jobs.append(("json", rel))
        else:
            jobs.append(("copy", rel))

    def run(job):
        kind, rel = job
        path = os.path.join(src, rel)
        if kind == "copy":
            return [(rel, read(path))], None
        if kind == "json":
            raw = read(path)
            small = minify(raw)
            if parse_json(small, rel) != parse_json(raw, rel):
                raise ValueError(f"{rel}: minified JSON parses differently")
            return [(rel, small)], None
        if kind == "audio":
            raw = read(path)
            if rel.endswith(".mp3"):
                return [(rel, raw)], None
            mp3, secs = wav_to_mp3(raw, rel)
            return [(rel[:-4] + ".mp3", mp3)], ("audio", secs)
        base = rel[:-len("#sheet.png")]
        png, fanim_raw = read(path), read(os.path.join(src, base + "#anim.fanim"))
        anim = parse_json(fanim_raw, base + "#anim.fanim")
        res = repack(png, anim, base)
        if res is None:
            return [(rel, png), (base + "#anim.fanim", minify(fanim_raw))], None
        new_png, new_anim, st = res
        return [(rel, new_png), (base + "#anim.fanim", dump_min(new_anim))], ("sheet", (base,) + st)

    with cf.ThreadPoolExecutor(workers) as ex:
        for written, extra in ex.map(run, jobs):
            for rel, data in written:
                out[rel] = data
                count("after", rel, len(data))
            if extra and extra[0] == "audio":
                report["audio_s"] += extra[1]
            elif extra:
                report["sheets"].append(extra[1])
    return out, report


def print_report(report, seconds):
    exts = sorted(set(report["before"]) | set(report["after"]),
                  key=lambda e: -max(report["before"].get(e, 0), report["after"].get(e, 0)))
    tb, ta = sum(report["before"].values()), sum(report["after"].values())
    print(f"{'':16s} {'before':>10s} {'after':>10s}")
    for e in exts:
        b, a = report["before"].get(e, 0), report["after"].get(e, 0)
        print(f"{e:16s} {b / 1e6:9.2f}M {a / 1e6:9.2f}M")
    print(f"{'total':16s} {tb / 1e6:9.2f}M {ta / 1e6:9.2f}M  ({100 * ta / max(tb, 1):.0f}%)")
    if report["sheets"]:
        before = sum(s[1] for s in report["sheets"])
        after = sum(s[2] for s in report["sheets"])
        frames = sum(s[3] for s in report["sheets"])
        uniq = sum(s[4] for s in report["sheets"])
        print(f"sheets repacked: {len(report['sheets'])}, {before / 1e6:.1f}M -> {after / 1e6:.1f}M pixels "
              f"({4 * before / 1e6:.0f} -> {4 * after / 1e6:.0f} MB once decoded), {frames} frame rects -> {uniq} unique")
    if report["audio_s"]:
        print(f"audio encoded: {report['audio_s']:.0f} s of WAV -> MP3")
    for d in report["dropped"]:
        print("left out:", d)
    print(f"built in {seconds:.1f} s")


# ---------------------------------------------------------------- install

def find_game(explicit):
    for c in [explicit, os.environ.get("TFM2_GAME_DIR")] + GAME_DIRS:
        if c and os.path.isfile(os.path.join(c, "bundle.game_data")):
            return c
    sys.exit("Teamfight Manager2 not found: pass --game <folder> or set TFM2_GAME_DIR")


def merge_keys(inst, pkg, match):
    """Copy pkg's keys that `match` into inst (recursing into dicts whose key does not match)."""
    changed = 0
    for k, v in pkg.items():
        if match(k):
            if inst.get(k) != v:
                inst[k] = v
                changed += 1
        elif isinstance(v, dict):
            if not isinstance(inst.get(k), dict):
                inst[k] = {}
            changed += merge_keys(inst[k], v, match)
        elif k not in inst:
            inst[k] = v
            changed += 1
    return changed


def version(v):
    return tuple(int(x) for x in v.split("."))


def install(pkg, heroes, target, dry):
    wrote = removed = 0
    for rel, data in sorted(pkg.items()):
        if rel in SHARED or rel == "mod.mod_info":
            continue
        dst = os.path.join(target, rel)
        stem, ext = os.path.splitext(dst)
        if ext in AUDIO_EXT:
            for other in AUDIO_EXT:
                if other != ext and os.path.isfile(lp(stem + other)):
                    removed += 1
                    if not dry:
                        os.remove(lp(stem + other))
        if os.path.isfile(lp(dst)) and read(dst) == data:
            continue
        wrote += 1
        if not dry:
            write(dst, data)
    print(f"{wrote} files written, {removed} clips of the other format removed" + (" (dry run)" if dry else ""))
    match = lambda k: any(h in k for h in heroes)
    for rel in SHARED:
        if rel not in pkg:
            continue
        dst = os.path.join(target, rel)
        inst = parse_json(read(dst), rel) if os.path.isfile(lp(dst)) else {}
        n = merge_keys(inst, parse_json(pkg[rel], rel), match)
        print(f"{rel}: {n} keys refreshed")
        if not dry and (n or not os.path.isfile(lp(dst))):
            write(dst, dump_min(inst))
    if "mod.mod_info" in pkg:
        dst = os.path.join(target, "mod.mod_info")
        new = parse_json(pkg["mod.mod_info"], "mod.mod_info")
        if os.path.isfile(lp(dst)):
            inst = parse_json(read(dst), "mod.mod_info")
            if version(new["version"]) >= version(inst["version"]) and len(heroes) > 1:
                inst = new                       # a full install of a newer version brings its hero list
            else:
                inst["version"] = max(inst["version"], new["version"], key=version)
                inst["last_updated"] = max(inst["last_updated"], new["last_updated"])
        else:
            inst = new
        print(f"mod.mod_info: version {inst['version']}")
        if not dry:
            write(dst, (json.dumps(inst, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=os.path.join(REPO, "league"), help="the mod folder to pack (default: league/)")
    ap.add_argument("--out", help="write the whole package here (default: dist/league when not installing)")
    ap.add_argument("--hero", action="append", help="only this hero (league_<id> or <id>); repeatable")
    ap.add_argument("--install", action="store_true", help="merge the package into <game>/mods/league")
    ap.add_argument("--game", help="Teamfight Manager2 folder (default: TFM2_GAME_DIR or the usual Steam paths)")
    ap.add_argument("--target", help="install into this mod folder instead of <game>/mods/league")
    ap.add_argument("--dry", action="store_true", help="with --install: report, write nothing")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    t0 = time.time()
    all_heroes = hero_ids(a.src)
    if a.hero:
        heroes = []
        for h in a.hero:
            h = h if h.startswith("league_") else "league_" + h
            if h not in all_heroes:
                sys.exit(f"{h}: no champion/{h}.data_champion in {a.src}")
            heroes.append(h)
    else:
        heroes = all_heroes
    pkg, report = build(a.src, heroes, everything=not a.hero, workers=a.workers)
    print_report(report, time.time() - t0)
    out = a.out or (None if a.install else os.path.join(REPO, "dist", "league"))
    if out:
        if a.hero:
            sys.exit("--out writes a whole package; leave out --hero")
        if os.path.isdir(lp(out)):
            if not os.path.isfile(lp(os.path.join(out, "mod.mod_info"))):
                sys.exit(f"{out} exists and is not a mod folder; not replacing it")
            shutil.rmtree(lp(out))
        for rel, data in sorted(pkg.items()):    # the order the game reads them: one pass on a hard disk
            write(os.path.join(out, rel), data)
        print("package:", out)
    if a.install:
        target = a.target or os.path.join(find_game(a.game), "mods", "league")
        print("install:", target, "-", "every hero" if not a.hero else ", ".join(heroes))
        install(pkg, heroes, target, a.dry)


if __name__ == "__main__":
    main()
