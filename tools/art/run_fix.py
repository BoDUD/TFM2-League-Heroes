#!/usr/bin/env python3
"""The heroes' own run cycles mended in code - never a pose redrawn (the user, 2026-11-15, after cut-out redos of
Caitlyn, Jax and Ezreal failed: 「修旧跑步的硬伤」 - fix the old runs' measured faults).

    python tools/art/run_fix.py --audit [--hero caitlyn ...] [--json PATH]   # every dense hero of both packs
    python tools/art/run_fix.py --league [--lol D:\\WeGameApps\\lol]           # League's run clips -> run_fix_league.json
    python tools/art/run_fix.py --fix --hero caitlyn [--dry]                 # the fixes into the sheet (+ the strips)

The audit reads every run-type tag a kit plays (run, and its forms: r_run, b_run, run_x ...) on the dense frames
(hd_<tag>, each frame centred on the pivot; game px = squares x SIZES / PPU, as the battlefield draws them) and finds:
- cycle: the tag's time off its target by more than CYCLE_OFF - the target League's own run for the champion
  (run_fix_league.json: the clip `Run` plays at base move speed, tools/lol/anim_graph.py's graph followed through its
  parametric / condition / selector / sequence clips, its time over the strides its feet take in it; a cycle League's
  way outside LEAGUE_OK is a misread and not used), but never quicker than covering GROUND_MIN body heights of ground
  at the unit's move speed, held to CYCLE_MIN..CYCLE_MAX; a form's run (b_run, r_run) the run's target;
- dupes: neighbour frames that hardly differ - under CHANGE_DUP of the squares, and of the legs' (the lowest third)
  too (Lux's run holds her upper body while her legs step: 13 % of the frame, half of the legs);
- outliers: a frame whose top (the head), height or baseline (the feet) lies OUTLIER game px or more off the mean
  of its two neighbours, and as far off its twin in the other step (else it is the bob's top: Ezreal's passing
  frames) - Caitlyn's 6th frame drawn small, her head 7 px low;
- baseline: the frames' lowest row spread over more than BASE game px (feet not on one ground line);
- bob: the head's height over the feet without two lows a cycle (no bob, or one beat for a two-step cycle).

The fixes (`--fix`), each only by whole squares, every frame keeping its squares (outlines and all), the hd_ / 1x /
lo_ frames alike (the same frames dropped, swapped and moved; a frame put on the ground goes onto each tag's own
ground line - the 1x frames are not the dense ones' squares over PPU to the pixel):
(d) the feet of every frame FEET game px or more off the ground line (the standing frame's: idle_base) put on it;
    less is left - a square's lift can be the drawing's own bob (Jax's old run);
(c) an outlier (as found on the frames so placed) replaced by the neighbour nearer its pose (no shift fixes a frame
    drawn at another size);
(b) a hold - a near-duplicate and the neighbours as alike - one frame of it kept; with its twin in the other step
    both dropped, the time shared by all; alone (or made by (c)), its time goes to its own step's frames, so both
    steps still take half the cycle (the legs' alternation even, one step a frame short);
(e) a cycle with no bob (under BOB_MIN) given a two-beat one: the frames with the feet closest (passing) a square up;
(a) the cycle's time to its target where it is off it, the frames' times even (by step, after (b)).
A second run finds nothing to fix. Jinx's and Vi's v4 runs (tools/art/run_league.py) are left alone.
"""
import argparse
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import thin_outline as T  # noqa: E402

LEAGUE = os.path.join(HERE, "run_fix_league.json")
TICKS = 60              # game ticks a second (a unit moves move_speed / 1000 game px a tick)
UI_PPU = T.UI_PPU       # the lo_ frames' squares a game px
CHANGE_DUP = 0.15       # neighbour frames differing in less than this share of their squares: a near-duplicate
OUTLIER = 3.0           # game px: a frame's top / height / baseline this far off its neighbours' mean
BASE = 1.5              # game px: the frames' baselines spread over more than this: feet off one ground line
BOB_MIN = 0.75          # game px: a head moving less than this over the cycle has no bob
FEET = 0.8              # game px: a frame's feet this far or farther off the ground line are moved onto it (less is
                        # its own bob: league_jax's old run lifts a frame a square)
CYCLE_MIN, CYCLE_MAX = 0.75, 1.2    # s: the cycle's time held to this (League's own, else as it is)
CYCLE_OFF = 0.15        # a cycle this share or more off its target is set to it
GROUND_MIN = 1.1        # body heights of ground a cycle covers at least (oppi's hand-drawn runs 1.1 - 1.3; a quicker
                        # cycle takes small steps for the speed: the user on 0.55 s, 「太快，像小碎步」)
RUN = re.compile(r"^(?:hd_|lo_)?((?:\w+_)?run(?:_\w+)?)$")
SKIP = {"league_jinx": "v4 run (run_league.py; the user: 这个不错啊)", "league_vi": "v4 run (run_league.py)"}
DERIVED = {("league_jinx", "run_x"): "tools/art/jinx_excited_run.py makes it from run"}


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


# ================================================================================================== League's runs
def league_champs():
    """{hero id: League's champion folder} for the league pack: the hero's poses.json `champ`, else its id matched
    to a champion WAD by name."""
    folder = None
    out = {}
    for hid, pack, _p, _s in T.all_heroes():
        if pack != "league":
            continue
        name = hid.split("_", 1)[1]
        pj = os.path.join(ROOT, "assets", "source", name, "poses.json")
        if os.path.exists(lp(pj)):
            with open(lp(pj), encoding="utf-8") as f:
                c = json.load(f).get("champ")
            if c:
                out[hid] = c
                continue
        out[hid] = name                                 # matched against the WADs when read
    return out


def league_run(lol, champ):
    """League's run for a champion: the clip `Run` plays at base move speed -> {clip, clip_s, strides, cycle_s}."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
    import anim_graph as AG
    import pose_ref as P
    from riot import Wad
    base = os.path.join(lol, "Game", "DATA", "FINAL", "Champions")
    wads = {os.path.splitext(os.path.splitext(f)[0])[0].lower(): os.path.splitext(os.path.splitext(f)[0])[0]
            for f in os.listdir(base) if f.endswith(".wad.client") and "." not in f[:-11]}
    champ = wads.get(champ.lower(), champ)
    w = Wad(os.path.join(base, f"{champ}.wad.client"))
    b = w.read_path(f"data/characters/{champ.lower()}/animations/skin0.bin")
    clips = {}
    for _cls, fields in AG.parse_prop(b):
        for key, clip in fields.get("mClipDataMap") or []:
            clips[key] = clip or {}

    def follow(key, depth=0):
        c = clips.get(key)
        if c is None or depth > 10:
            return None
        res = c.get("mAnimationResourceData")
        if isinstance(res, dict) and res.get("mAnimationFilePath"):
            return res["mAnimationFilePath"], c.get("mTickDuration")
        if c.get("mParametricPairDataList"):        # by move speed: the child for base speed (<= 345)
            pairs = [(p.get("mValue", 0.0), p.get("mClipName")) for p in c["mParametricPairDataList"]
                     if isinstance(p, dict)]
            low = [p for p in pairs if p[0] <= 345]
            return follow((max(low) if low else min(pairs))[1], depth + 1)
        if c.get("mConditionFloatPairDataList"):
            pairs = [(p.get("mValue", 0.0), p.get("mClipName")) for p in c["mConditionFloatPairDataList"]
                     if isinstance(p, dict)]
            return follow(min(pairs)[1], depth + 1)
        if "mFalseConditionClipName" in c or "mTrueConditionClipName" in c:
            return follow(c.get("mFalseConditionClipName") or c.get("mTrueConditionClipName"), depth + 1)
        if c.get("mSelectorPairDataList"):           # the likeliest
            pairs = [(p.get("mProbability", 0.0), p.get("mClipName")) for p in c["mSelectorPairDataList"]
                     if isinstance(p, dict)]
            return follow(max(pairs)[1], depth + 1)
        if c.get("mClipNameList"):                   # a sequence: its loop is the last (the first an intro)
            return follow(c["mClipNameList"][-1], depth + 1)
        return None

    got = follow(AG.fnv1a("Run"))
    if not got:
        return None
    path, tick = got
    anim = P.read_anim(w.read_path(path.lower()))
    frames = round(anim["duration"] * anim["fps"])
    clip_s = (tick or 1.0 / anim["fps"]) * frames
    strides = None
    try:                                             # each foot's landings over the clip (the skeleton posed)
        skin = w.read_path(f"data/characters/{champ.lower()}/skins/skin0.bin")
        skl = P.base_mesh(sorted(set(m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/.\-]+\.skl", skin))))
        joints, _ = P.read_skl(w.read_path(skl.lower()))
        feet = {}
        for i, j in enumerate(joints):
            n = j["name"].lower()
            if ("foot" in n or "ankle" in n) and n[:2] in ("l_", "r_"):
                feet.setdefault(n[0], i)
        if len(feet) == 2:
            N = 96
            ys = {k: [] for k in feet}
            for s in range(N):
                g = P.pose(joints, anim, anim["duration"] * s / N)
                for k, i in feet.items():
                    ys[k].append(g[i][1, 3])
            counts = []
            for y in ys.values():
                y = np.array(y)
                down = y < y.min() + 0.25 * (y.max() - y.min())
                counts.append(sum(1 for i in range(N) if down[i] and not down[i - 1]))
            strides = max(1, int(round(float(np.mean(counts)))))
    except Exception:  # noqa: BLE001 - a champion without foot joints: the clip taken as one stride
        strides = None
    k = strides or 1
    return {"champ": champ, "clip": os.path.basename(path), "clip_s": round(clip_s, 4), "strides": k,
            "cycle_s": round(clip_s / k, 4)}


# Champions whose clip the foot count misreads (Lulu skips: two hops a stride; the pilot read her clip by hand)
LEAGUE_FIX = {"league_lulu": 0.75}


LEAGUE_OK = (0.55, 1.5)      # s: a stride cycle League's way outside this is a misread (a floating champion's drift, a
                             # turn clip, feet that hop) and not used


def league_table():
    """{hero id: League's run} with a usable cycle (`cycle_s` within LEAGUE_OK, the clip a run)."""
    if not os.path.exists(lp(LEAGUE)):
        return {}
    with open(lp(LEAGUE), encoding="utf-8") as f:
        t = json.load(f)
    for hid, s in LEAGUE_FIX.items():
        if hid in t:
            t[hid]["cycle_s"] = s
    return {h: v for h, v in t.items() if LEAGUE_OK[0] <= v["cycle_s"] <= LEAGUE_OK[1]
            and "turn" not in v["clip"].lower()}


def write_league(lol):
    out = {}
    for hid, champ in league_champs().items():
        try:
            r = league_run(lol, champ)
        except Exception as e:  # noqa: BLE001
            print(f"{hid}: {champ}: {e}")
            continue
        if r:
            out[hid] = r
            print(f"{hid:24s} {r['champ']:14s} {r['clip']:30s} {r['clip_s']:.3f} s / {r['strides']} = {r['cycle_s']:.3f} s")
    with open(lp(LEAGUE), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=0, sort_keys=True)
    print(f"{len(out)} champions -> {os.path.relpath(LEAGUE, ROOT)}")


# ================================================================================================== the frames
def stem(hid, pack):
    return os.path.join(ROOT, pack, "champions", hid)


def read_sheet(hid, pack):
    with open(lp(stem(hid, pack) + "#anim.fanim"), encoding="utf-8-sig") as f:
        an = json.load(f)
    px = np.array(Image.open(lp(stem(hid, pack) + "#sheet.png")).convert("RGBA"))
    return an, px


def rect(f):
    return tuple(int(round(f["data"][k])) for k in ("x", "y", "w", "h"))


def frames_of(an, px, tag):
    """[(picture, ms)] of a tag."""
    out = []
    for f in an["anims"][tag]["frames"]:
        x, y, w, h = rect(f)
        out.append((px[y:y + h, x:x + w].copy(), int(round(f["duration"] * 1000))))
    return out


def move_speed(hid, pack):
    p = os.path.join(ROOT, pack, "champion", hid + ".data_champion")
    if not os.path.exists(lp(p)):
        return None
    with open(lp(p), encoding="utf-8-sig") as f:
        return float(json.load(f).get("stat", {}).get("move_speed") or 0) or None


def change(a, b, legs=False):
    """The share of squares that differ between two frames (centred on one another); legs: of the lowest third of
    their rows only (Lux's run keeps her upper body still while her legs step: 13 % of the frame, half of the legs)."""
    if a.shape != b.shape:
        h, w = max(a.shape[0], b.shape[0]), max(a.shape[1], b.shape[1])

        def pad(x):
            out = np.zeros((h, w, 4), np.uint8)
            y0, x0 = (h - x.shape[0]) // 2, (w - x.shape[1]) // 2
            out[y0:y0 + x.shape[0], x0:x0 + x.shape[1]] = x
            return out
        a, b = pad(a), pad(b)
    if legs:
        rows = np.nonzero(((a[..., 3] > 0) | (b[..., 3] > 0)).any(1))[0]
        if len(rows):
            t = rows[-1] - (rows[-1] - rows[0]) // 3
            a, b = a[t:], b[t:]
    oa, ob = a[..., 3] > 0, b[..., 3] > 0
    diff = (oa != ob) | (oa & ob & (np.abs(a[..., :3].astype(int) - b[..., :3].astype(int)).sum(-1) > 30))
    return float(diff.sum()) / max(1, int((oa | ob).sum()))


def same(a, b):
    """Two frames as one pose: hardly a square changed, the legs' neither."""
    return change(a, b) < CHANGE_DUP and change(a, b, legs=True) < CHANGE_DUP


def measure(a):
    """A frame's top (its first row three squares wide: the head, not a hair's tip), bottom edge (the feet) and
    middle column, in squares from its centre (the pivot), down +."""
    op = a[..., 3] > 0
    rows = np.nonzero(op.sum(1) >= 3)[0]
    allr = np.nonzero(op.any(1))[0]
    if not len(allr):
        return None
    cy = a.shape[0] / 2.0
    cols = np.nonzero(op.any(0))[0]
    return {"top": float((rows[0] if len(rows) else allr[0]) - cy), "bottom": float(allr[-1] + 1 - cy),
            "mid": float((cols[0] + cols[-1] + 1) / 2.0 - a.shape[1] / 2.0)}


def lows(v):
    """How many separate lows (a run of values within a third of the range of the lowest, round the loop) v has."""
    v = np.asarray(v, float)
    if v.max() - v.min() < 1e-9:
        return 0
    low = v >= v.max() - (v.max() - v.min()) / 3.0       # (down +: a low of the head is a high value)
    return sum(1 for i in range(len(v)) if low[i] and not low[i - 1]) or 1


def run_tags(an):
    """{base tag: {"hd": tag, "one": tag, "lo": tag}} of the run-type tags a kit plays."""
    out = {}
    for t in an["anims"]:
        m = RUN.match(t)
        if not m:
            continue
        base = m.group(1)
        kind = "hd" if t.startswith("hd_") else "lo" if t.startswith("lo_") else "one"
        out.setdefault(base, {})[kind] = t
    return out


def target_cycle(now, league_s, speed, height):
    """The time a run's cycle should take: League's own for the champion (else its own), but not so quick that it
    covers less than GROUND_MIN body heights of ground at the unit's move speed, held to CYCLE_MIN..CYCLE_MAX."""
    t = league_s or now
    if speed and height:
        t = max(t, GROUND_MIN * height / (speed / 1000.0 * TICKS))
    return min(CYCLE_MAX, max(CYCLE_MIN, t))


def audit_frames(fr, k, league_s=None, speed=None):
    """The numbers of a run's frames [(dense picture, ms)], k game px a square -> dict."""
    n = len(fr)
    ms = [m for _, m in fr]
    cyc = sum(ms) / 1000.0
    M = [measure(a) for a, _ in fr]
    empty = [i for i, m in enumerate(M) if m is None]
    if empty:                                           # (an empty frame: measured as its neighbour)
        for i in empty:
            M[i] = next((M[(i + d) % n] for d in range(1, n) if M[(i + d) % n] is not None),
                        {"top": 0.0, "bottom": 0.0, "mid": 0.0})
    top = np.array([m["top"] for m in M]) * k
    bot = np.array([m["bottom"] for m in M]) * k
    hgt = bot - top
    ch = [change(fr[i][0], fr[(i + 1) % n][0]) for i in range(n)]
    out = {"frames": n, "cycle_s": round(cyc, 3), "ms": ms, "league_s": league_s}
    if speed:
        out["ground_heights"] = round(speed / 1000.0 * TICKS * cyc / max(1e-6, float(np.median(hgt))), 2)
    out["height_px"] = round(float(np.median(hgt)), 1)
    target = target_cycle(cyc, league_s, speed, float(np.median(hgt)))
    out["target_s"] = round(target, 3)
    out["dupes"] = [i for i in range(n) if ch[i] < CHANGE_DUP and same(fr[i][0], fr[(i + 1) % n][0])]
    outl = []
    for i in range(n if n >= 3 else 0):
        for name, v_ in (("top", top), ("height", hgt), ("baseline", bot)):
            d = v_[i] - (v_[i - 1] + v_[(i + 1) % n]) / 2.0
            twin = v_[i] - v_[(i + n // 2) % n] if n % 2 == 0 else d     # (its twin in the other step as far
            if abs(d) >= OUTLIER and abs(twin) >= OUTLIER:              # out: the bob's top, not a fault)
                outl.append((i, name, round(float(d), 1)))
    out["outliers"] = outl
    out["baseline_px"] = round(float(bot.max() - bot.min()), 1)
    rel = bot - top                                     # the head over the feet
    out["bob_px"] = round(float(rel.max() - rel.min()), 1)
    out["bob_lows"] = lows(-rel) if out["bob_px"] >= BOB_MIN else 0
    out["top_px"] = [round(float(v), 1) for v in top]
    out["bottom_px"] = [round(float(v), 1) for v in bot]
    out["change"] = [round(c, 2) for c in ch]
    faults = []
    if abs(cyc / target - 1.0) > CYCLE_OFF:
        faults.append("cycle")
    if out["dupes"]:
        faults.append("dupes")
    if outl:
        faults.append("outliers")
    if out["baseline_px"] > BASE:
        faults.append("baseline")
    if n >= 4 and out["bob_lows"] < 2:
        faults.append("bob")
    if empty:
        out["empty"] = empty
        faults.append("empty")
    out["faults"] = faults
    return out


def audit_tag(hid, pack, ppu, size, an, px, base, tags, league):
    """The numbers of one run tag (its dense frames, else its 1x ones) -> dict."""
    dense = "hd" in tags
    fr = frames_of(an, px, tags.get("hd") or tags.get("one"))
    lg = league.get(hid)
    out = {"hero": hid, "pack": pack, "tag": base}
    out.update(audit_frames(fr, (size / ppu) if dense else size, lg["cycle_s"] if lg else None,
                            move_speed(hid, pack)))
    return out


def audit(heroes, league):
    rows = []
    for hid, pack, ppu, size in heroes:
        an, px = read_sheet(hid, pack)
        for base, tags in sorted(run_tags(an).items()):
            rows.append(audit_tag(hid, pack, ppu, size, an, px, base, tags, league))
    return rows


def print_audit(rows):
    for r in rows:
        lg = f"{r['league_s']:.3f}" if r["league_s"] else "  -  "
        print(f"{r['hero']:26s} {r['tag']:10s} n={r['frames']:2d} {r['cycle_s']:.3f}s (League {lg}, target "
              f"{r['target_s']:.3f}) "
              f"ground {r.get('ground_heights', '-')} h {r['height_px']}px base {r['baseline_px']}px "
              f"bob {r['bob_px']}px/{r['bob_lows']} dupes {r['dupes']} out {r['outliers']}"
              f"  {'+'.join(r['faults']) or 'ok'}")
    kinds = ["cycle", "dupes", "outliers", "baseline", "bob", "empty"]
    tags = len(rows)
    heroes = sorted({r["hero"] for r in rows})
    print(f"\n{len(heroes)} heroes, {tags} run tags")
    for k in kinds:
        hs = sorted({r["hero"] for r in rows if k in r["faults"]})
        print(f"  {k:9s} {len([r for r in rows if k in r['faults']]):4d} tags, {len(hs):4d} heroes")
    clean = sorted(set(heroes) - {r["hero"] for r in rows if r["faults"]})
    print(f"  no fault: {len(clean)} heroes")


# ================================================================================================== the fixes
CHANGE_HOLD = 0.20      # neighbours of a near-duplicate this alike hold the same pose too (one hold, one frame kept)


def trim(a):
    """Clear rows and columns taken off alike at both ends (the centre - the pivot - stays)."""
    op = a[..., 3] > 0
    rows, cols = np.nonzero(op.any(1))[0], np.nonzero(op.any(0))[0]
    if not len(rows):
        return a
    t, l_ = min(rows[0], a.shape[0] - 1 - rows[-1]), min(cols[0], a.shape[1] - 1 - cols[-1])
    return a[t:a.shape[0] - t, l_:a.shape[1] - l_].copy()


def shifted(a, dy):
    """A frame's squares dy rows down (up -), every square kept, its centre (the pivot) where it was."""
    if not dy:
        return a.copy()
    h = a.shape[0]
    out = np.zeros((h + 2 * abs(dy),) + a.shape[1:], np.uint8)
    out[dy + abs(dy):dy + abs(dy) + h] = a
    return trim(out)


def spread(a):
    """How wide the feet stand: the opaque columns of the frame's lowest rows (a sixth of its height)."""
    op = a[..., 3] > 0
    rows = np.nonzero(op.any(1))[0]
    if not len(rows):
        return 0
    band = op[max(rows[0], rows[-1] - max(3, (rows[-1] - rows[0]) // 6)):rows[-1] + 1].any(0)
    cols = np.nonzero(band)[0]
    return int(cols[-1] - cols[0] + 1)


def plan(fr, k, ground, target, keep=(), league_s=None):
    """The fixes for a run's dense frames [(picture, ms)] (k game px a square; ground: the standing frame's feet,
    squares under the centre) -> {"order": the source frame of each new frame, "dy": its rows down, "cycle_s",
    "notes"}. `keep`: fixes not to make (judged by eye: "outliers", "dupes", "bob", "baseline", "cycle")."""
    n = len(fr)
    notes = []
    M = [measure(a) for a, _ in fr]
    if any(m is None for m in M):
        return None
    # (d) the feet of every frame on the ground line
    if "baseline" in keep:
        dy = [0] * n
        feet = [False] * n
    else:                                               # (a square or two is a frame's own bob: left)
        dy = [int(round(ground - m["bottom"])) if abs(ground - m["bottom"]) * k >= FEET else 0 for m in M]
        feet = [bool(d) for d in dy]                    # (the frames put on the ground: each tag on its own line)
        moved = [(i, d) for i, d in enumerate(dy) if d]
        if moved:
            notes.append("feet onto the ground line: " + ", ".join(f"{i} {d:+d}" for i, d in moved))
    order = list(range(n))
    weights = [1.0] * n
    # (c) a frame whose head still lies OUTLIER px off its neighbours' (drawn at another size): the neighbour nearer
    #     its pose instead
    if n >= 4 and "outliers" not in keep:
        top = [M[i]["top"] + dy[i] for i in range(n)]
        for i in range(n):
            dev = (top[i] - (top[i - 1] + top[(i + 1) % n]) / 2.0) * k
            twin = (top[i] - top[(i + n // 2) % n]) * k if n % 2 == 0 else dev
            if abs(dev) >= OUTLIER and abs(twin) >= OUTLIER:      # (its own step's twin as high: the bob's top)
                j = min(((i - 1) % n, (i + 1) % n), key=lambda j: change(fr[i][0], fr[j][0]))
                order[i], dy[i], feet[i] = j, dy[j], feet[j]
                notes.append(f"frame {i} (head {dev:+.1f} px off its neighbours', drawn at another size) -> frame {j}")
    # (b) holds: a near-duplicate and the neighbours as alike - one frame kept (in both steps of an even cycle alike)
    if "dupes" not in keep:
        cur = [shifted(fr[order[i]][0], dy[i]) for i in range(n)]
        ch = [change(cur[i], cur[(i + 1) % n]) if same(cur[i], cur[(i + 1) % n]) else 1.0 for i in range(n)]
        groups, seen = [], set()
        for i in range(n):
            if ch[i] < CHANGE_DUP and i not in seen:
                g = [i, (i + 1) % n]
                while ch[(g[0] - 1) % n] < CHANGE_HOLD and (g[0] - 1) % n not in g:
                    g.insert(0, (g[0] - 1) % n)
                while ch[g[-1]] < CHANGE_HOLD and (g[-1] + 1) % n not in g:
                    g.append((g[-1] + 1) % n)
                seen.update(g)
                groups.append(g)
        drop, alone = set(), set()
        for g in groups:
            made = any(order[i] != i for i in g)            # a hold a replacement made
            twin = [(i + n // 2) % n for i in g] if n % 2 == 0 else None
            paired = twin is not None and any(len(set(twin) & set(h)) >= 2 for h in groups if h is not g)
            drop.update(g[1:])
            if not paired and n % 2 == 0:
                alone.update(g[1:])
            notes.append(f"hold {g}: frame {g[0]} kept" + (" (the hold the replacement made)" if made else
                                                          " (its twin in the other step alike)" if paired else
                         " (no twin: its time to its own step's frames - both steps as long, one a frame short)"))
        if drop:
            # each frame's share of the cycle: a frame dropped with its twin, its time shared by all; one dropped
            # alone, by the frames of its own step (half the cycle), so both steps keep half the cycle
            w = {i: 1.0 for i in range(n)}
            for i in sorted(alone):
                half = range(0, n // 2) if i < n // 2 else range(n // 2, n)
                rest = [j for j in half if j not in drop]
                for j in rest:
                    w[j] += w[i] / len(rest)
                w[i] = 0.0
            keep_i = [i for i in range(n) if i not in drop]
            order = [order[i] for i in keep_i]
            dy = [dy[i] for i in keep_i]
            feet = [feet[i] for i in keep_i]
            weights = [w[i] for i in keep_i]
    # (e) no bob: the frames between the landings (the feet closest together) a square up
    m2 = len(order)
    if len(weights) != m2:
        weights = [1.0] * m2
    lift = [0] * m2
    cur = [shifted(fr[order[i]][0], dy[i]) for i in range(m2)]
    MM = [measure(a) for a in cur]
    rel = [(mm["bottom"] - mm["top"]) * k for mm in MM]
    if "bob" not in keep and m2 >= 4 and max(rel) - min(rel) < BOB_MIN:
        sp = [spread(a) for a in cur]
        med = float(np.median(sp))
        up = [i for i in range(m2) if sp[i] < med]
        if 0 < len(up) < m2:
            for i in up:
                dy[i] -= 1
                lift[i] = -1
            notes.append(f"no bob ({max(rel) - min(rel):.1f} px): frames {up} a square up (the feet passing)")
    # (a) the cycle's time: League's (held to CYCLE_MIN..CYCLE_MAX) where it is off it by more than CYCLE_OFF, the
    #     frames' times even (a step's share kept where (b) dropped a frame alone)
    now = sum(m for _, m in fr) / 1000.0
    want = now
    if target and abs(now / target - 1.0) > CYCLE_OFF and "cycle" not in keep:
        want = target
    even = even_steps([m for _, m in fr])
    if abs(want - now) > 0.005 or len(order) != n or not even:
        notes.append(f"cycle {now:.3f} s ({n} frames{'' if even else ', uneven'}) -> {want:.3f} s "
                     f"({len(order)} frames)" + (f", League {league_s:.3f} s" if league_s else ""))
    total = int(round(want * 1000))
    ms = [total * w / sum(weights) for w in weights]
    ms_i = [int(math.floor(v)) for v in ms]
    for j in sorted(range(m2), key=lambda j: ms_i[j] - ms[j])[:total - sum(ms_i)]:
        ms_i[j] += 1
    changed = any(dy) or order != list(range(n)) or ms_i != [m for _, m in fr]
    return {"order": order, "dy": dy, "feet": feet, "lift": lift, "ms": ms_i, "cycle_s": want, "notes": notes,
            "changed": changed}


def even_steps(ms):
    """Frame times even - or even within each of two steps that take as long (a step a frame short, (b))."""
    if max(ms) - min(ms) <= 1:
        return True
    for k in range(1, len(ms)):
        a, b = ms[:k], ms[k:]
        if max(a) - min(a) <= 1 and max(b) - min(b) <= 1 and abs(sum(a) - sum(b)) <= 2:
            return True
    return False


def even_ms(total_s, n):
    """n frame times (ms) adding up to total_s, as even as whole ms go."""
    total = int(round(total_s * 1000))
    base = total // n
    out = [base] * n
    extra = total - base * n
    for i in range(extra):
        out[(i * n) // extra] += 1
    return out


def apply(fr, p, scale=None, ground=None):
    """The plan on a tag's frames. The dense tag: its rows as planned. Another (the 1x, lo_): a frame the plan put on
    the ground put on this tag's own ground line (its own squares - the 1x frames are not the dense ones' squares
    over PPU to the pixel), the bob's square lift `scale` of this tag's squares a dense one."""
    if scale is None:
        return [(shifted(fr[j][0], d), m) for j, d, m in zip(p["order"], p["dy"], p["ms"])]
    out = []
    for j, f, lf, m in zip(p["order"], p["feet"], p["lift"], p["ms"]):
        d = int(round(ground - measure(fr[j][0])["bottom"])) if f else 0
        out.append((shifted(fr[j][0], d + int(round(lf * scale))), m))
    return out


# Fixes not made for a hero's tag, judged by eye on its frames (plan()'s `keep`): {(hero, tag): (fixes, why)}
KEEP = {}


def ground_of(an, px, tag):
    """The standing frame's feet (squares under its centre) in the tag's density (hd_idle_base, else hd_idle)."""
    pre = "hd_" if tag.startswith("hd_") else "lo_" if tag.startswith("lo_") else ""
    for t in (pre + "idle_base", pre + "idle"):
        if t in an["anims"]:
            m = measure(frames_of(an, px, t)[0][0])
            if m:
                return m["bottom"]
    return None


def fix_hero(row, league, dry=False):
    """Every run tag of a hero fixed -> [(tag, plan, before, after)]; the sheet (and the strips) written unless dry."""
    hid, pack, ppu, size = row
    an, px = read_sheet(hid, pack)
    lg = league.get(hid)
    ls = lg["cycle_s"] if lg else None
    out, new, retime = [], {}, {}
    for base, tags in sorted(run_tags(an).items()):
        if hid in SKIP or (hid, base) in DERIVED or "hd" not in tags:
            continue
        fr = frames_of(an, px, tags["hd"])
        ground = ground_of(an, px, tags["hd"])
        kp = KEEP.get((hid, base), ((), ""))[0]
        before = audit_frames(fr, size / ppu, ls, move_speed(hid, pack))
        if base != "run" and "run" in run_tags(an) and "hd" in run_tags(an)["run"]:
            # a form's run (Swain's b_run, Lucian's r_run) keeps the cadence of the run: the target the run's
            base_fr = frames_of(an, px, run_tags(an)["run"]["hd"])
            before["target_s"] = audit_frames(base_fr, size / ppu, ls, move_speed(hid, pack))["target_s"]
        p = plan(fr, size / ppu, ground if ground is not None else measure(fr[0][0])["bottom"], before["target_s"],
                 kp, ls)
        if p is None:
            continue
        nf = apply(fr, p)
        after = audit_frames(nf, size / ppu, ls, move_speed(hid, pack))
        out.append((base, p, before, after))
        if not p["changed"]:
            continue
        if not any(p["dy"]) and p["order"] == list(range(n_ := len(fr))):
            retime.update({tags[k]: p["ms"] for k in ("hd", "one", "lo") if k in tags})   # (only the times)
            continue
        new[tags["hd"]] = nf
        if "one" in tags:
            new[tags["one"]] = apply(frames_of(an, px, tags["one"]), p, 1.0 / ppu, ground_of(an, px, tags["one"]))
        if "lo" in tags:
            new[tags["lo"]] = apply(frames_of(an, px, tags["lo"]), p, UI_PPU / ppu, ground_of(an, px, tags["lo"]))
    if (new or retime) and not dry:
        tag_frames = {t: len(an["anims"][t]["frames"]) for t in new}
        for t, ms in retime.items():
            for f, m in zip(an["anims"][t]["frames"], ms):
                f["duration"] = round(m / 1000.0, 6)
        write(hid, pack, an, px, new)
        strips(hid, tag_frames, new, out)
    return out


def place(px, anims, drop, new):
    """The sheet with the tags in `drop` taken off (their squares cleared where no other tag uses them) and `new`
    ({tag: [(frame, ms)]}) put in the free room - top-left first, 1 clear square between frames, no wider than the
    sheet; every other tag's frames stay exactly where they are. -> (sheet, anims)."""
    keep = {rect(f) for t, a in anims.items() if t not in drop for f in a["frames"]}
    gone = {rect(f) for t in drop if t in anims for f in anims[t]["frames"]} - keep
    px = px.copy()
    for x, y, w, h in gone:
        px[y:y + h, x:x + w] = 0
    Ws = px.shape[1]
    total_h = px.shape[0] + sum(f.shape[0] + 1 for fr in new.values() for f, _ in fr)
    occ = np.zeros((total_h, Ws), bool)
    for x, y, w, h in keep:
        occ[max(0, y - 1):y + h + 1, max(0, x - 1):x + w + 1] = True
    out_px = np.zeros((total_h, Ws, 4), np.uint8)
    out_px[:px.shape[0]] = px
    anims = {t: a for t, a in anims.items()}
    for tag, fr in new.items():
        rows = []
        for f, ms in fr:
            h, w = f.shape[:2]
            ii = np.pad(np.cumsum(np.cumsum(occ.astype(np.int32), 0), 1), ((1, 0), (1, 0)))
            s_ = ii[h:, w:] - ii[:-h, w:] - ii[h:, :-w] + ii[:-h, :-w]       # occupied squares in each h x w box
            free = np.argwhere(s_ == 0)
            if not len(free):
                sys.exit(f"{tag}: no room for a {w}x{h} frame")
            y, x = free[0]
            out_px[y:y + h, x:x + w] = f
            occ[max(0, y - 1):y + h + 1, max(0, x - 1):x + w + 1] = True
            rows.append({"duration": round(ms / 1000.0, 6), "data": {"x": float(x), "y": float(y), "w": float(w),
                                                                     "h": float(h)}})
        anims[tag] = {"frames": rows}
    used = [rect(f) for a in anims.values() for f in a["frames"]]
    H = max(y + h for x, y, w, h in used)
    W = max(x + w for x, y, w, h in used)
    return out_px[:H, :W], anims


def write(hid, pack, an, px, new):
    """The changed tags into the hero's sheet: their old squares cleared, the frames put in the free room, every other
    tag where it was (place, as tools/art/run_league.py's); the fanim keeps its tags' order."""
    order = list(an["anims"])
    if new:
        sheet, anims = place(px, an["anims"], tuple(new), new)
        an["anims"] = {t: anims[t] for t in order}
        Image.fromarray(sheet, "RGBA").save(lp(stem(hid, pack) + "#sheet.png"), optimize=True)
    with open(lp(stem(hid, pack) + "#anim.fanim"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(an, ensure_ascii=False, separators=(",", ":")))


def strips(hid, counts, new, done):
    """assets/source/ppu/<name>_<tag>.png (the strip tools/art/ppu_hd.py makes hd_<tag> from) and its orig/ twin
    (tools/art/ppu_restyle.py's source): the same frames dropped and moved, where the strip holds the tag's frames."""
    name = hid.split("_", 1)[1]
    for base, p, _b, _a in done:
        if "hd_" + base not in new:
            continue
        for folder in (os.path.join(ROOT, "assets", "source", "ppu"),
                       os.path.join(ROOT, "assets", "source", "ppu", "orig")):
            png, js = (os.path.join(folder, f"{name}_{base}.{e}") for e in ("png", "json"))
            if not (os.path.exists(lp(png)) and os.path.exists(lp(js))):
                continue
            with open(lp(js), encoding="utf-8") as f:
                meta = json.load(f)
            sizes = meta["sizes"]
            if len(sizes) != counts["hd_" + base]:
                print(f"{hid}: {os.path.relpath(png, ROOT)} holds {len(sizes)} frames, not the tag's: left as it is")
                continue
            img = np.asarray(Image.open(lp(png)).convert("RGBA"))
            fr, x = [], 0
            for w, h in sizes:
                fr.append((img[:h, x:x + w].copy(), 0))
                x += w + 1
            nf = [a for a, _ in apply(fr, p)]
            H = max(a.shape[0] for a in nf)
            out = np.zeros((H, sum(a.shape[1] + 1 for a in nf) - 1, 4), np.uint8)
            x = 0
            for a in nf:
                out[:a.shape[0], x:x + a.shape[1]] = a
                x += a.shape[1] + 1
            Image.fromarray(out, "RGBA").save(lp(png), optimize=True)
            meta["sizes"] = [[a.shape[1], a.shape[0]] for a in nf]
            with open(lp(js), "w", encoding="utf-8", newline="\n") as f:
                json.dump(meta, f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--league", action="store_true", help="read League's run clips into run_fix_league.json")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--hero", action="append", default=[])
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--tree", help="--audit: read the sheets of this tree instead (another checkout, as installed)")
    a = ap.parse_args()
    global ROOT
    if a.tree:
        ROOT = os.path.abspath(a.tree)
    if a.league:
        write_league(a.lol)
        return
    heroes = T.all_heroes()
    if a.hero:
        heroes = [T.resolve(n, heroes) for h in a.hero for n in h.split(",") if n]
    league = league_table()
    if a.audit:
        rows = audit(heroes, league)
        print_audit(rows)
        if a.json:
            with open(a.json, "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=1)
        return
    if a.fix:
        for row in heroes:
            for base, p, before, after in fix_hero(row, league, a.dry):
                print(f"{row[0]} {base}: " + ("; ".join(p["notes"]) or "nothing to fix"))
                for label, r in (("before", before), ("after", after)):
                    print(f"    {label:6s} n={r['frames']} {r['cycle_s']:.3f}s base {r['baseline_px']}px "
                          f"bob {r['bob_px']}px/{r['bob_lows']} dupes {r['dupes']} out {r['outliers']} "
                          f"{'+'.join(r['faults']) or 'ok'}")
        return
    ap.error("--audit, --league or --fix")


if __name__ == "__main__":
    main()
