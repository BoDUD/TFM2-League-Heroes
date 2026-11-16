#!/usr/bin/env python3
"""Parts of a hero's League design that its drawing lacked - added for its run (tools/art/run_body_anim.py `add`) -
laid into EVERY other animation of the hero too (the user, 2026-11-16, after Jax's, Camille's and Bel'Veth's runs:
「改了模型的那几个其他动作帧也要改吧 没影响吧 贾克斯 卡密尔 卑尔维斯之类的」): without them a part vanishes the moment the
hero stops running - it stands, attacks, casts or dies without its topknot.

    python tools/art/add_design_parts.py --hero jax                 # the tags into the sheet (+ strips), then hero_reels
    python tools/art/add_design_parts.py --check                    # every hero with a data file: exit 1 when a frame or
                                                                    # a strip is not what this makes (CI)
    python tools/art/add_design_parts.py --hero jax --dry --review DIR   # review pictures, nothing written
    python tools/art/add_design_parts.py --init jax [--from REV]    # the base frames: the tags as they are without parts
    python tools/art/add_design_parts.py --anchors jax              # each frame's anchor found again (scores printed)
    python tools/art/add_design_parts.py --motion jax [--lol DIR]   # each part's sway a frame, from League's clips

Each hero's data is its own file, assets/source/<hero>/hd/<hero>_parts.json, beside its run data; its base beside it
(<base>.png + .json: every tag's dense and 1x frames as they were before the parts, written by --init - the tool starts
from them every time, so it runs again over its own output; when a generator draws the hero's frames anew
(ppu_restyle.py, ppu_hd.py, the hero's rig), --init again from the new sheet, then run this). A frame is made of:

- the base frame, square for square: nothing of the hero's drawing moves or changes but where a part covers it;
- every part (`parts`), a small picture in the hero's own colours and outline - a run `add` piece by name (`run`: the
  same squares the run lays, from <hero>_run_body.json) or its own `rows` / `key` - set on the frame's ANCHOR: the
  hero's own drawn reference (the hood, the head, the hip; `anchor`: a rect of squares in a base frame) found in the
  frame (`frames` -> tag -> `hd` / `one`: [rows, cols, how] a frame, the anchor's place from its place in the anchor
  frame, how it is drawn there - "id", "h" mirrored, "r90" / "r180" / "r270" turned (np.rot90's quarter turns,
  counter-clockwise), "r90h" / "r270h" both; --anchors finds them, but for the places set by hand in `anchor` -> kind
  -> `fixed`: a flashed frame, a redrawn hip). A part keeps its place against the anchor as the
  run has it (`run_anchor`: the anchor's place in the run's frame `from`) or as its `at` says (the anchor frame's rows /
  cols); a mirrored or turned frame gets the part mirrored / turned the same way - lossless quarter turns only;
- `bend` (a part's `bend`: {"root": picture column, "side": "left" / "right"}; `frames` -> tag -> `bend` -> part: rows
  a frame, down +): the part as a chain - every column on `side` of its root moved that many rows times its share of
  the way out (run_body_anim's `tip`, neighbouring columns never more than a square apart), the root end staying on the
  anchor: hair or cloth swaying with the frame's motion (--motion: League's own sway, its tip against its root, seen
  through the camera of the poses spec the frames were rigged with - `poses`, default <hero>/poses.json); with
  "hang": true, `root` is a picture ROW and every row under it moves that many columns (+ right) by its share - a cloth
  panel hanging from a hip (run_body_anim's `hang`);
  `move` (part: [rows, cols] a frame): the whole part moved (a star on its orbit); `hide` (part: [frame indices]);
  `variant` (part: [name or null] a frame): another picture of the part (`variants`), drawn for a pose the main one
  cannot take (a part lying on the ground); `orient` (part: [how or null] a frame): the part drawn its own way
  instead of the frame's, its `pin` square (picture rows / cols) kept where the frame's way puts it;
- `layer` "under" (the default: only where the frame is clear - behind every square of the hero, as the run lays it)
  or "over" (on top, but never on `anchor` -> `hd` / `one` -> `protect`: a rect of the anchor frame, the face,
  carried to each frame as the anchor is); parts are laid in their order, an earlier one on top;
- `tint` (tag -> [frame or null]: [share, [r, g, b]]): a flashed frame's colours (a hit's white flash) - every colour of
  the part but the outline moved that share of the way to the colour;
- a pinhole the part closes (a clear pocket of at most 2 squares shut in by the part and the figure, clear in the base)
  is outline, as the drawing would close it.
A frame the parts reach past grows alike at both ends (the centre, the pivot, kept): the dense frame by what it needs,
its 1x frame by its own 1x part (`one`: the 1x picture, its `at` in the 1x anchor frame, its own `bend` root / `pin` -
a 1x frame is a drawing of its own, keep_one-style: only the part is added, bent its share of the dense rows; a 1x
frame redrawn a little differently each time takes its dense frame's anchor scaled, `anchor` -> `one` -> "from": "hd"),
both then grown together until tools/art/ppu_hd.py's check holds (hd_ at least PPU x the 1x size, a frame the idle reel
plays exactly PPU x as wide: the DLL's test). The lo_ frames are made from the dense ones as ppu_hd.add_lo makes them;
heroes in tools/art/thin_outline.json get its pass. Sizes changed, the fanim changes (league.dll embeds it: build it
again) - the whole sheet is packed again (shelves by height; the tags' new frames, every other tag's as they are, the
idle / bp reels pointed at their frames' new rects), then tools/art/hero_reels.py runs for the hero. The strips
tools/art/ppu_hd.py reads (assets/source/ppu/<hero>_<tag>.png, an idle_base's is <hero>_idle.png) are written with the
dense frames, so ppu_hd.py makes them again. Order: after ppu_restyle.py / ppu_hd.py / ppu_one.py / run_body_anim.py,
before hero_reels.py.

The check needs numpy and Pillow only (CI); the lo_ frames are made with tools/art/pixel_down.py, which needs scipy:
without it they are not compared (the dense and 1x frames and the strips are).
"""
import argparse
import glob
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import thin_outline as T  # noqa: E402  (numpy and Pillow only)

PIN_HOLE = 2                    # a clear pocket of at most this many squares shut in by a part becomes outline
TFS = ("id", "h", "r90", "r180", "r270", "r90h", "r270h")


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def short(hero):
    return hero.split("_", 1)[1] if hero.startswith(("league_", "tft_")) else hero


def data_file(hero):
    return os.path.join(ROOT, "assets", "source", short(hero), "hd", f"{short(hero)}_parts.json")


def heroes_with_data():
    return sorted(os.path.basename(p)[:-len("_parts.json")]
                  for p in glob.glob(os.path.join(ROOT, "assets", "source", "*", "hd", "*_parts.json")))


# ------------------------------------------------------------------------------------------------- the data
def picture(rows, key):
    """`rows` of characters, `key` naming each one's colour ("." / " ": nothing) -> an RGBA array."""
    key = {k: tuple(int(x) for x in v) for k, v in key.items()}
    H, W = len(rows), max(len(r) for r in rows)
    out = np.zeros((H, W, 4), np.uint8)
    for y, line in enumerate(rows):
        for x, ch in enumerate(line):
            if ch in ". ":
                continue
            out[y, x, :3] = key[ch]
            out[y, x, 3] = 255
    return out


def run_pieces(hero):
    """The run's `add` pieces {name: (picture, (row, col) in the run's frame `from`, padded)} and the run's data."""
    with open(lp(os.path.join(ROOT, "assets", "source", short(hero), "hd", f"{short(hero)}_run_body.json")),
              encoding="utf-8") as f:
        rb = json.load(f)
    pr, pc = rb.get("pad", (0, 0))
    return {a["name"]: (picture(a["rows"], a["key"]), (a["at"][0] + pr, a["at"][1] + pc)) for a in rb.get("add", [])}, rb


def load(hero):
    with open(lp(data_file(hero)), encoding="utf-8") as f:
        cfg = json.load(f)
    run = None
    for p in cfg["parts"]:
        for kind in ("hd", "one"):
            spec = p.get(kind)
            if spec is None:
                continue
            if "run" in spec:                              # the run's own `add` piece, square for square
                if run is None:
                    run = run_pieces(hero)[0]
                pic, at = run[spec["run"]]
                ra = cfg.get("run_anchor")                 # the anchor's place in the run's frame `from` (--anchors)
                spec["pic"], spec["at"] = pic, (None if ra is None else (at[0] - ra[0], at[1] - ra[1]))
            else:
                spec["pic"] = picture(spec["rows"], spec["key"])
                spec["at"] = tuple(spec["at"])
            for v in spec.get("variants", {}).values():
                v["pic"] = picture(v["rows"], v["key"])
                v["at"] = tuple(v["at"])
    return cfg


def save(hero, cfg):
    """The data file: a key a line, each frame list on one line (pictures as rows)."""
    def dump(v, ind, key=None):
        one = json.dumps(v, ensure_ascii=False, separators=(", ", ": "))
        if len(one) + ind <= 118 and key != "rows":
            return one
        if isinstance(v, dict):
            if not v:
                return "{}"
            inner = ",\n".join(f'{" " * (ind + 2)}{json.dumps(k, ensure_ascii=False)}: {dump(x, ind + 2, k)}'
                               for k, x in v.items())
            return "{\n" + inner + "\n" + " " * ind + "}"
        if isinstance(v, list) and v and (key == "rows" or all(isinstance(x, (dict, list)) for x in v)):
            inner = ",\n".join(" " * (ind + 2) + dump(x, ind + 2) for x in v)
            return "[\n" + inner + "\n" + " " * ind + "]"
        return one
    clean = json.loads(json.dumps(cfg, default=lambda o: None))
    for p in clean["parts"]:                               # (the pictures made by load go)
        for kind in ("hd", "one"):
            s = p.get(kind) or {}
            s.pop("pic", None)
            if "run" in s:
                s.pop("at", None)
            for v in s.get("variants", {}).values():
                v.pop("pic", None)
    with open(lp(data_file(hero)), "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(clean, 0) + "\n")


def hero_row(hero):
    return T.resolve(short(hero), T.all_heroes())       # (id, pack, ppu, size)


# ------------------------------------------------------------------------------------------------- the sheet
def read_sheet(hid, pack, rev=None):
    """(anims, pixels) of the hero's sheet - the tree's, or at a git revision."""
    if rev is None:
        return T.read(hid, pack)
    import io
    rel = os.path.relpath(T.stem(hid, pack), ROOT).replace(os.sep, "/")
    env = dict(os.environ, MSYS_NO_PATHCONV="1")
    fan = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{rel}#anim.fanim"], capture_output=True, check=True, env=env)
    png = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{rel}#sheet.png"], capture_output=True, check=True, env=env)
    return json.loads(fan.stdout.decode("utf-8-sig"))["anims"], np.array(Image.open(io.BytesIO(png.stdout)).convert("RGBA"))


def rect(f):
    return tuple(int(round(f["data"][q])) for q in ("x", "y", "w", "h"))


def frames_of(anims, px, tag):
    out = []
    for f in anims[tag]["frames"]:
        x, y, w, h = rect(f)
        out.append((px[y:y + h, x:x + w].copy(), round(f["duration"] * 1000, 3)))
    return out


# ------------------------------------------------------------------------------------------------- the base
def base_files(cfg):
    return os.path.join(ROOT, cfg["base"] + ".png"), os.path.join(ROOT, cfg["base"] + ".json")


def read_base(cfg):
    """{tag: {"hd": [frame], "one": [frame], "ms": [ms]}} - the frames before the parts."""
    png, side = base_files(cfg)
    px = np.array(Image.open(lp(png)).convert("RGBA"))
    with open(lp(side), encoding="utf-8") as f:
        meta = json.load(f)
    out = {}
    for tag, m in meta["tags"].items():
        out[tag] = {k: [px[y:y + h, x:x + w].copy() for x, y, w, h in m[k]] for k in ("hd", "one")}
        out[tag]["ms"] = list(m["ms"])
    return out


def init(hero, rev=None):
    """The base from the sheet (at a revision): every tag of the data's `tags`, dense and 1x frames, a row each."""
    cfg = load(hero)
    hid, pack, _, _ = hero_row(hero)
    anims, px = read_sheet(hid, pack, rev)
    rows, meta = [], {"from": f"{rev or 'the tree'} {os.path.relpath(T.stem(hid, pack), ROOT).replace(os.sep, '/')}#sheet.png",
                      "tags": {}}
    for tag in cfg["tags"]:
        for kind, pre in (("hd", "hd_"), ("one", "")):
            fr = frames_of(anims, px, pre + tag)
            rows.append((tag, kind, [a for a, _ in fr]))
            if kind == "one":
                meta["tags"].setdefault(tag, {})["ms"] = [ms for _, ms in fr]
    W = max(sum(a.shape[1] + 1 for a in fr) for _, _, fr in rows)
    H = sum(max(a.shape[0] for a in fr) + 1 for _, _, fr in rows)
    out = np.zeros((H, W, 4), np.uint8)
    y = 0
    for tag, kind, fr in rows:
        x, rects = 0, []
        for a in fr:
            out[y:y + a.shape[0], x:x + a.shape[1]] = a
            rects.append([x, y, a.shape[1], a.shape[0]])
            x += a.shape[1] + 1
        meta["tags"][tag][kind] = rects
        y += max(a.shape[0] for a in fr) + 1
    png, side = base_files(cfg)
    os.makedirs(os.path.dirname(lp(png)), exist_ok=True)
    Image.fromarray(out, "RGBA").save(lp(png), optimize=True)
    with open(lp(side), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"from": meta["from"]}, ensure_ascii=False)[:-1] + ', "tags": {\n'
                + ",\n".join(f"  {json.dumps(t)}: {json.dumps(m, separators=(',', ':'))}" for t, m in meta["tags"].items())
                + "\n}}\n")
    print(f"{hid}: base of {len(cfg['tags'])} tags from {meta['from']} -> {os.path.relpath(png, ROOT)} ({W}x{H})")


# ------------------------------------------------------------------------------------------------- the anchors
def tf_arr(a, how):
    if how in ("h", "r90h", "r270h"):
        a = a[:, ::-1]
    k = {"id": 0, "h": 0, "r90": 1, "r180": 2, "r270": 3, "r90h": 1, "r270h": 3}[how]
    return np.ascontiguousarray(np.rot90(a, k))


def tf_pt(u, v, th, tw, how):
    """A square (u, v) of a th x tw box -> its place in the box drawn `how` (tf_arr's)."""
    if how in ("h", "r90h", "r270h"):
        v = tw - 1 - v
    k = {"id": 0, "h": 0, "r90": 1, "r180": 2, "r270": 3, "r90h": 1, "r270h": 3}[how]
    for _ in range(k):                     # one counter-clockwise quarter turn of a th x tw box
        u, v, th, tw = tw - 1 - v, u, tw, th
    return u, v


def tf_vec(u, v, how):
    """An offset (rows, cols) as it points in a frame drawn `how`."""
    if how in ("h", "r90h", "r270h"):
        v = -v
    for _ in range({"id": 0, "h": 0, "r90": 1, "r180": 2, "r270": 3, "r90h": 1, "r270h": 3}[how]):
        u, v = -v, u
    return u, v


def template(cfg, base, kind):
    a = cfg["anchor"][kind]
    r0, r1, c0, c1 = a["rect"]
    f = base[a["tag"]][kind][a["frame"]]
    t = f[r0:r1, c0:c1].copy()
    return t, t[..., 3] > 0, (r0, c0)


def find(frame, tpl, mask, ways=TFS):
    """The template's best place in the frame: (share of its squares alike, how, row, col of its top-left)."""
    best = (-1.0, "id", 0, 0)
    for how in ways:
        t, m = tf_arr(tpl, how), tf_arr(mask, how)
        th, tw = m.shape
        H, W = frame.shape[:2]
        n = int(m.sum())
        F = np.zeros((H + 2 * th, W + 2 * tw, 4), np.uint8)
        F[th:th + H, tw:tw + W] = frame
        key = F[..., 0].astype(np.int64) << 24 | F[..., 1].astype(np.int64) << 16 | F[..., 2].astype(np.int64) << 8 \
            | (F[..., 3] > 0).astype(np.int64)
        tk = t[..., 0].astype(np.int64) << 24 | t[..., 1].astype(np.int64) << 16 | t[..., 2].astype(np.int64) << 8 | 1
        acc = np.zeros((H + th + 1, W + tw + 1), np.int32)
        for u, v in zip(*np.nonzero(m)):
            acc += (key[u:u + H + th + 1, v:v + W + tw + 1] == tk[u, v])
        y, x = np.unravel_index(int(acc.argmax()), acc.shape)
        s = acc[y, x] / float(n)
        if s > best[0] + 1e-9:
            best = (float(s), how, int(y) - th, int(x) - tw)
    return best


def find_near(frame, tpl, mask, how, y0, x0, r=2):
    """The template drawn `how` near (y0, x0) (its top-left, within r): the place where most of its box agrees with
    the frame - opaque where it is, clear where it is - and most of its squares have their colour (a 1x frame redrawn
    a little differently each time) -> (share alike, row, col)."""
    t, m = tf_arr(tpl, how), tf_arr(mask, how)
    th, tw = m.shape
    H, W = frame.shape[:2]
    best = None
    for y in range(y0 - r, y0 + r + 1):
        for x in range(x0 - r, x0 + r + 1):
            sub = np.zeros((th, tw, 4), np.uint8)
            ya, yb, xa, xb = max(0, y), min(H, y + th), max(0, x), min(W, x + tw)
            if yb > ya and xb > xa:
                sub[ya - y:yb - y, xa - x:xb - x] = frame[ya:yb, xa:xb]
            op = sub[..., 3] > 0
            s = (op == m).sum() + ((sub[..., :3] == t[..., :3]).all(-1) & m & op).sum()
            key = (int(s), -abs(y - y0) - abs(x - x0))
            if best is None or key > best[0]:
                best = (key, y, x)
    (s, _), y, x = best
    return s / float(th * tw + m.sum()), y, x


def anchors(hero, rev_run=True):
    """Every frame's anchor found by its drawn squares (the best place of the anchor rect, mirrored and turned too).
    `anchor` -> `one` -> "from": "hd": a 1x frame redrawn each time (no square-for-square anchor) gets its dense
    frame's place and way, scaled by 1 / PPU about the frames' centres, then the best place within 2 squares.
    `anchor` -> kind -> `fixed` ({tag: {frame: [rows, cols, how]}}): places set by hand, kept as they are."""
    cfg = load(hero)
    base = read_base(cfg)
    ways = cfg["anchor"].get("ways", list(TFS))
    ppu = hero_row(hero)[2]
    for kind in ("hd", "one"):
        if kind not in cfg["anchor"]:
            continue
        tpl, mask, (r0, c0) = template(cfg, base, kind)
        from_hd = kind == "one" and cfg["anchor"]["one"].get("from") == "hd"
        if from_hd:
            a_hd, a1 = cfg["anchor"]["hd"], cfg["anchor"]["one"]
            hb, ob = base[a_hd["tag"]]["hd"][a_hd["frame"]], base[a1["tag"]]["one"][a1["frame"]]
            R0, R1, C0, C1 = a_hd["rect"]
            # (the two boxes' centres from their frames' centres, the 1x box's from the dense one's scaled)
            q0 = np.array([(R0 + R1) / 2.0 - hb.shape[0] / 2.0, (C0 + C1) / 2.0 - hb.shape[1] / 2.0])
            q1 = np.array([(r0 + a1["rect"][1]) / 2.0 - ob.shape[0] / 2.0, (c0 + a1["rect"][3]) / 2.0 - ob.shape[1] / 2.0])
            e = q1 - q0 / ppu
        fixed = cfg["anchor"][kind].get("fixed", {})       # (places set by hand: a flashed frame, a redrawn hip)
        for tag in cfg["tags"]:
            out, scores = [], []
            for i, f in enumerate(base[tag][kind]):
                if str(i) in fixed.get(tag, {}):
                    out.append(list(fixed[tag][str(i)]))
                    scores.append("fixed")
                    continue
                if from_hd:
                    dy, dx, how = cfg["frames"][tag]["hd"][i]
                    hf = base[tag]["hd"][i]
                    th, tw = tf_arr(base[a_hd["tag"]]["hd"][a_hd["frame"]][R0:R1, C0:C1, 3], how).shape
                    qF = np.array([R0 + dy + th / 2.0 - hf.shape[0] / 2.0, C0 + dx + tw / 2.0 - hf.shape[1] / 2.0])
                    eu, ev = tf_vec(e[0], e[1], how)
                    t1h, t1w = tf_arr(mask, how).shape
                    yc = f.shape[0] / 2.0 + qF[0] / ppu + eu
                    xc = f.shape[1] / 2.0 + qF[1] / ppu + ev
                    s, y, x = find_near(f, tpl, mask, how, int(round(yc - t1h / 2.0)), int(round(xc - t1w / 2.0)))
                else:
                    s, how, y, x = find(f, tpl, mask, ways)
                out.append([y - r0, x - c0, how])
                scores.append(f"{s:.2f}{'' if how == 'id' else how}")
            fr = cfg.setdefault("frames", {}).setdefault(tag, {})
            fr[kind] = out
            print(f"{kind:3s} {tag:14s} " + " ".join(scores))
    if any("run" in (p.get("hd") or {}) for p in cfg["parts"]) and rev_run:
        # the anchor's place in the run's frame `from` (its parts' `at` are there)
        _, rb = run_pieces(hero)
        d = rb["drawn"]
        s = np.array(Image.open(lp(os.path.join(ROOT, d + ".png"))).convert("RGBA"))
        with open(lp(os.path.join(ROOT, d + ".json")), encoding="utf-8") as f:
            meta = json.load(f)
        x = sum(w + 1 for w, _ in meta["sizes"][:rb["from"]])
        w, h = meta["sizes"][rb["from"]]
        pr, pc = rb.get("pad", (0, 0))
        ref = np.pad(s[:h, x:x + w], ((pr, pr), (pc, pc), (0, 0)))
        tpl, mask, (r0, c0) = template(cfg, base, "hd")
        sc, how, y, x = find(ref, tpl, mask, ("id",))
        cfg["run_anchor"] = [y - r0, x - c0]
        print(f"run frame {rb['from']}: anchor at {cfg['run_anchor']} ({sc:.2f})")
    save(hero, cfg)


# ------------------------------------------------------------------------------------------------- one frame
def per_frame(cfg, tag, key, part, i, default=None):
    v = cfg.get("frames", {}).get(tag, {}).get(key, {})
    v = v.get(part) if isinstance(v, dict) else None
    if v is None:
        return default
    if len(v) <= i:
        sys.exit(f"{tag}: `{key}` of {part} has {len(v)} values, frame {i} wanted")
    return default if v[i] is None else v[i]


def bent(pic, spec, rows):
    """The picture as a chain bent `rows` at its tip: every column on `side` of `root` ("left" / "right") moved that
    many rows times its share of the way out - or, `hang` (a cloth panel hanging from a root ROW), every row below
    `root` moved that many columns (+ right) times its share - neighbours never more than a square apart (as
    run_body_anim's `tip` / `hang`) -> (picture, (rows it grew above, columns it grew to the left))."""
    if not rows or not spec:
        return pic, (0, 0)
    root, m = spec["root"], abs(rows)
    if spec.get("hang"):
        lines = [y for y in range(pic.shape[0]) if y > root and pic[y, :, 3].any()]
        if not lines:
            return pic, (0, 0)
        span = max(y - root for y in lines)
        out = np.zeros((pic.shape[0], pic.shape[1] + 2 * m, 4), np.uint8)
        keep = [y for y in range(pic.shape[0]) if y not in lines]
        out[keep, m:m + pic.shape[1]] = pic[keep]
        prev = 0
        for y in sorted(lines):
            v = int(round(rows * (y - root) / float(span)))
            v = max(prev - 1, min(prev + 1, v))
            prev = v
            out[y, m + v:m + v + pic.shape[1]] = pic[y]
        return out, (0, m)
    side = spec.get("side", "left")
    cols = [x for x in range(pic.shape[1]) if (x < root if side == "left" else x > root) and pic[:, x, 3].any()]
    if not cols:
        return pic, (0, 0)
    span = max(abs(root - x) for x in cols)
    out = np.zeros((pic.shape[0] + 2 * m, pic.shape[1], 4), np.uint8)
    keep = [x for x in range(pic.shape[1]) if x not in cols]
    out[m:m + pic.shape[0], keep] = pic[:, keep]
    prev = 0
    for x in sorted(cols, key=lambda c: abs(root - c)):
        v = int(round(rows * abs(root - x) / float(span)))
        v = max(prev - 1, min(prev + 1, v))
        prev = v
        out[m + v:m + v + pic.shape[0], x] = pic[:, x]
    return out, (m, 0)


def tinted(pic, tint, outline):
    if not tint:
        return pic
    share, to = tint
    out = pic.copy()
    op = out[..., 3] > 0
    ink = (out[..., :3] == np.array(outline)).all(-1)
    c = out[..., :3].astype(float)
    # (as tools/art/ppu_rig.py flash() makes a hit frame: c (1 - share) + to x share, rounded down)
    new = np.clip(np.floor(c * (1.0 - share) + np.array(to, float) * share + 1e-9), 0, 255).astype(np.uint8)
    out[..., :3] = np.where((op & ~ink)[..., None], new, out[..., :3])
    return out


def part_squares(cfg, kind, tag, i):
    """[(row, col, rgba, part)] of every part in frame i of `tag` (its `kind` frame), in the frame's rows / cols."""
    fr = cfg.get("frames", {}).get(tag, {})
    place = fr.get(kind)
    if place is None:
        sys.exit(f"{tag}: no {kind} anchors (--anchors)")
    dy, dx, how = place[i]
    tpl_rect = cfg["anchor"][kind]["rect"]
    th, tw = tpl_rect[1] - tpl_rect[0], tpl_rect[3] - tpl_rect[2]
    r0, c0 = tpl_rect[0], tpl_rect[2]
    # the template's top-left in this frame, drawn `how` (dy, dx: from its place in the anchor frame)
    ty, tx = r0 + dy, c0 + dx
    tint = (fr.get("tint") or [None] * (i + 1))[i] if fr.get("tint") else None
    k1 = 1.0 if kind == "hd" else 1.0 / hero_row(cfg["hero"])[2]
    out = []
    for p in cfg["parts"]:
        spec = p.get(kind)
        if spec is None:
            continue
        name = p["name"]
        if i in (fr.get("hide", {}).get(name) or []):
            continue
        var = per_frame(cfg, tag, "variant", name, i)
        pic, at = (spec["pic"], spec["at"]) if var is None else (spec["variants"][var]["pic"], spec["variants"][var]["at"])
        b = per_frame(cfg, tag, "bend", name, i, 0)
        if kind == "one":
            b = int(round(b * k1))                   # (the 1x part bends its share of the dense rows)
        bspec = (spec.get("bend") or p.get("bend")) if var is None else spec["variants"][var].get("bend")
        pic, (up, left) = bent(pic, bspec, b)
        pic = tinted(pic, tint, cfg["outline"])
        mv = per_frame(cfg, tag, "move", name, i, [0, 0])
        if kind == "one":
            mv = [int(round(mv[0] * k1)), int(round(mv[1] * k1))]
        own = per_frame(cfg, tag, "orient", name, i)
        ph, pw = pic.shape[:2]
        if own is None:
            # every square of the part through the frame's way (`at`: in the anchor frame; u, v: from the template's
            # top-left there)
            ys, xs = np.nonzero(pic[..., 3])
            for y, x in zip(ys.tolist(), xs.tolist()):
                u, v = at[0] - r0 - up + y + mv[0], at[1] - c0 - left + x + mv[1]
                uu, vv = tf_pt(u, v, th, tw, how) if how != "id" else (u, v)
                out.append((ty + uu, tx + vv, pic[y, x], name, p.get("layer", "under")))
        else:
            # drawn its own way, its pin square where the frame's way puts it
            pin = spec.get("pin") if var is None else spec["variants"][var].get("pin")
            pu, pv = at[0] - r0 + pin[0] + mv[0], at[1] - c0 + pin[1] + mv[1]
            fu, fv = tf_pt(pu, pv, th, tw, how) if how != "id" else (pu, pv)
            q = tf_arr(pic, own)
            qy, qx = tf_pt(pin[0] + up, pin[1] + left, ph, pw, own)
            ys, xs = np.nonzero(q[..., 3])
            for y, x in zip(ys.tolist(), xs.tolist()):
                out.append((ty + fu + (y - qy), tx + fv + (x - qx), q[y, x], name, p.get("layer", "under")))
    return out


def protected(cfg, kind, tag, i, shape):
    """The squares an "over" part never covers in frame i (`anchor` -> kind -> `protect`: a rect [r0, r1, c0, c1] of the
    anchor frame - the face -, carried to the frame as its anchor is) -> mask, or None."""
    rect_ = cfg["anchor"][kind].get("protect")
    if not rect_:
        return None
    dy, dx, how = cfg["frames"][tag][kind][i]
    R0, R1, C0, C1 = cfg["anchor"][kind]["rect"]
    th, tw = R1 - R0, C1 - C0
    pts = [tf_pt(r - R0, c - C0, th, tw, how) for r in (rect_[0], rect_[1] - 1) for c in (rect_[2], rect_[3] - 1)]
    ys, xs = [R0 + dy + u for u, _ in pts], [C0 + dx + v for _, v in pts]
    m = np.zeros(shape[:2], bool)
    m[max(0, min(ys)):max(0, max(ys) + 1), max(0, min(xs)):max(0, max(xs) + 1)] = True
    return m


def flood_clear(op):
    """Labels of the clear squares' 4-connected pockets (0: reaches the edge) -> (labels, sizes)."""
    H, W = op.shape
    lab = np.zeros((H, W), np.int32)
    sizes = [0]
    n = 0
    for sy in range(H):
        for sx in range(W):
            if op[sy, sx] or lab[sy, sx]:
                continue
            n += 1
            stack, cnt, edge = [(sy, sx)], 0, False
            lab[sy, sx] = n
            while stack:
                y, x = stack.pop()
                cnt += 1
                if y in (0, H - 1) or x in (0, W - 1):
                    edge = True
                for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= yy < H and 0 <= xx < W and not op[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        stack.append((yy, xx))
            sizes.append(-1 if edge else cnt)
    return lab, sizes


def compose(base, squares, outline, protect=None):
    """The base frame with the part squares laid in, grown alike at both ends to hold them -> (frame, (rows, cols)
    grown a side, pinholes closed)."""
    H, W = base.shape[:2]
    if not squares:
        return base.copy(), (0, 0), 0
    rs = [s[0] for s in squares]
    cs = [s[1] for s in squares]
    gr = max(0, -min(rs), max(rs) - (H - 1))
    gc = max(0, -min(cs), max(cs) - (W - 1))
    out = np.zeros((H + 2 * gr, W + 2 * gc, 4), np.uint8)
    out[gr:gr + H, gc:gc + W] = base
    had = out[..., 3] > 0
    taken = np.zeros_like(had)                           # (parts laid in order: an earlier one stays on top, as the
    for y, x, v, _, layer in squares:                    # run's `add` pieces are laid)
        Y, X = y + gr, x + gc
        if layer == "over":
            if protect is not None and 0 <= y < H and 0 <= x < W and protect[y, x]:
                continue
        elif had[Y, X] or taken[Y, X]:
            continue
        out[Y, X] = v
        taken[Y, X] = True
    # pinholes the parts closed: clear pockets of at most PIN_HOLE squares, clear and open in the grown base
    op = out[..., 3] > 0
    lab, sizes = flood_clear(op)
    lab0, sizes0 = flood_clear(had)
    holes = 0
    for k in range(1, len(sizes)):
        if 0 < sizes[k] <= PIN_HOLE:
            m = lab == k
            if any(sizes0[j] == -1 or sizes0[j] > PIN_HOLE for j in np.unique(lab0[m]).tolist() if j):
                out[m, :3] = outline
                out[m, 3] = 255
                holes += int(m.sum())
    return out, (gr, gc), holes


def grow_to(a, rows, cols):
    """`a` on a rows x cols frame, alike at both ends (the centre kept)."""
    H, W = a.shape[:2]
    if (rows, cols) == (H, W):
        return a
    out = np.zeros((rows, cols, 4), np.uint8)
    oy, ox = (rows - H) // 2, (cols - W) // 2
    out[oy:oy + H, ox:ox + W] = a
    return out


def sizes_for(hd, one, k, exact_w):
    """(hd rows, hd cols, 1x rows, 1x cols) grown alike from the made ones until ppu_hd.check holds: hd_ at least
    round(PPU x the 1x size) (exactly as wide where `exact_w`: a frame the idle reel plays, the DLL's test)."""
    H, W = hd
    h, w = one
    while round(h * k) > H:
        H += 2
    if exact_w:
        while round(w * k) != W:
            if round(w * k) < W:
                w += 2
            else:
                W += 2
    else:
        while round(w * k) > W:
            W += 2
    return H, W, h, w


def make(hero, cfg=None, lo=True):
    """-> ({tag, hd_tag, lo_tag: [(frame, ms)]}, info per tag) from the base."""
    cfg = cfg or load(hero)
    hid, pack, ppu, _ = hero_row(hero)
    base = read_base(cfg)
    anims, _ = T.read(hid, pack)
    # frames the idle reels play must keep hd_ exactly round(PPU x 1x) wide (ppu_hd.check, the DLL)
    exact = set()
    for t, a in anims.items():
        if t.endswith("idle") and not t.startswith(("hd_", "lo_")):
            rects_ = {rect(f) for f in a["frames"]}
            for t2 in cfg["tags"]:
                if t2 in anims:
                    exact |= {(t2, j) for j, f in enumerate(anims[t2]["frames"]) if rect(f) in rects_}
    new, info = {}, {}
    for tag in cfg["tags"]:
        b = base[tag]
        hd_out, one_out, inf = [], [], []
        for i, (bh, bo, ms) in enumerate(zip(b["hd"], b["one"], b["ms"])):
            sq = part_squares(cfg, "hd", tag, i)
            f, g, holes = compose(bh, sq, cfg["outline"], protected(cfg, "hd", tag, i, bh.shape))
            sq1 = part_squares(cfg, "one", tag, i) if any(p.get("one") for p in cfg["parts"]) else []
            f1, g1, holes1 = compose(bo, sq1, cfg["outline"], protected(cfg, "one", tag, i, bo.shape))
            H, W, h1, w1 = sizes_for(f.shape[:2], f1.shape[:2], ppu, (tag, i) in exact)
            f, f1 = grow_to(f, H, W), grow_to(f1, h1, w1)
            hd_out.append((f, ms))
            one_out.append((f1, ms))
            inf.append({"grown": [list(g), list(g1)], "size": [list(bh.shape[:2]), [H, W], list(bo.shape[:2]), [h1, w1]],
                        "holes": [holes, holes1],
                        "part_squares": int(((f[..., 3] > 0) & (grow_to(bh, H, W)[..., 3] == 0)).sum())})
        new[tag], new["hd_" + tag] = one_out, hd_out
        info[tag] = inf
    tp = T.load_state().get(hid)
    if tp is not None and tp.get("skip"):
        tp = None
    if tp is not None:
        for tag in cfg["tags"]:
            new["hd_" + tag] = [(T.change_fixed(f, tp["hd"], tp["outline"], tp["grow"])[0], ms) for f, ms in new["hd_" + tag]]
    if lo:
        import ppu_hd as P                                # (scipy: pixel_down)
        mini = {t: v for t, v in new.items()}
        P.add_lo(short(hero), mini)
        for tag in cfg["tags"]:
            fr = mini["lo_" + tag]
            if tp is not None:
                fr = [(T.change_fixed(f, tp["lo"], tp["outline"], tp["grow"])[0], ms) for f, ms in fr]
            new["lo_" + tag] = fr
    return new, info


# ------------------------------------------------------------------------------------------------- writing
def strip_paths(hid, tag):
    """The strip ppu_hd.py reads for a tag's dense frames (an idle_base's: the idle's, its breathing loop)."""
    name = T.strip_name(hid)
    t = "idle" if tag == "idle_base" else tag
    return os.path.join(T.STRIPS, f"{name}_{t}.png"), os.path.join(T.STRIPS, f"{name}_{t}.json")


def strip_of(frames):
    H = max(a.shape[0] for a in frames)
    s = np.zeros((H, sum(a.shape[1] + 1 for a in frames) - 1, 4), np.uint8)
    x = 0
    for a in frames:
        s[:a.shape[0], x:x + a.shape[1]] = a
        x += a.shape[1] + 1
    return s


def repack(an, px, new, max_w=2048):
    """The whole sheet packed again: every frame that owns its squares (the tags made here with their new frames, the
    rest as they are) in shelves by height, 1 square apart, at most max_w wide; a frame that is another tag's rect
    (the idle / bp reels and their hd_ / lo_: hero_reels.py's) points at that tag's frame again. -> (sheet, anims)."""
    by_rect = {}
    for t, a in an.items():
        for i, f in enumerate(a["frames"]):
            by_rect.setdefault(rect(f), []).append((t, i))
    shared = {t for t, a in an.items() if all(len(by_rect[rect(f)]) > 1 for f in a["frames"])}
    owner = {}
    for r, refs in by_rect.items():
        own = [q for q in refs if q[0] in new] or [q for q in refs if q[0] not in shared] or refs
        owner[r] = own[0]
    pics = {}
    for t, a in an.items():
        for i, f in enumerate(a["frames"]):
            if t in new:
                pics[(t, i)] = new[t][i][0]               # (a frame made here: its own squares, always)
            elif owner[rect(f)] == (t, i):
                x, y, w, h = rect(f)
                pics[(t, i)] = px[y:y + h, x:x + w]
    order = {q: k for k, q in enumerate(pics)}
    rects, x, y, shelf = {}, 0, 0, 0
    for q in sorted(pics, key=lambda q: (-pics[q].shape[0], order[q])):
        h, w = pics[q].shape[:2]
        if x and x + w > max_w:
            x, y, shelf = 0, y + shelf + 1, 0
        rects[q] = (x, y, w, h)
        x += w + 1
        shelf = max(shelf, h)
    W = max(r[0] + r[2] for r in rects.values())
    H = max(r[1] + r[3] for r in rects.values())
    out = np.zeros((H, W, 4), np.uint8)
    for q, (x, y, w, h) in rects.items():
        out[y:y + h, x:x + w] = pics[q]
    anims = {}
    for t, a in an.items():
        fr = []
        for i, f in enumerate(a["frames"]):
            q = (t, i) if t in new else owner[rect(f)]
            x, y, w, h = rects[q]
            ms = new[t][i][1] if t in new else f["duration"] * 1000.0
            fr.append({"duration": round(ms / 1000.0, 6), "data": {"x": float(x), "y": float(y), "w": float(w), "h": float(h)}})
        anims[t] = {"frames": fr}
    return out, anims


def write(hero, new, cfg):
    """The tags' frames into the sheet (their own rects when every frame keeps its size; else put in the free room, the
    reels pointed at them) and their dense frames into the strips. -> fanim changed?"""
    hid, pack, ppu, _ = hero_row(hero)
    stem = T.stem(hid, pack)
    with open(lp(stem + "#anim.fanim"), encoding="utf-8-sig") as f:
        doc = json.load(f)
    an = doc["anims"]
    px = np.array(Image.open(lp(stem + "#sheet.png")).convert("RGBA"))
    same = all(len(an[t]["frames"]) == len(fr) and all(
        (rect(r)[2], rect(r)[3]) == (a.shape[1], a.shape[0]) and abs(r["duration"] * 1000 - ms) <= 0.5
        for r, (a, ms) in zip(an[t]["frames"], fr)) for t, fr in new.items())
    if same:
        for t, fr in new.items():
            for r, (a, _) in zip(an[t]["frames"], fr):
                x, y, w, h = rect(r)
                px[y:y + h, x:x + w] = a
    else:
        order = list(an)
        px, anims = repack(an, px, new)
        doc["anims"] = {t: anims[t] for t in order}
        with open(lp(stem + "#anim.fanim"), "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
    Image.fromarray(px, "RGBA").save(lp(stem + "#sheet.png"), optimize=True)
    for tag in cfg["tags"]:
        png, side = strip_paths(hid, tag)
        if not os.path.isfile(lp(png)):
            continue
        dense = [a for a, _ in new["hd_" + tag]]
        Image.fromarray(strip_of(dense), "RGBA").save(lp(png), optimize=True)
        k = ppu
        one = [a for a, _ in new[tag]]
        sizes = [[a.shape[1], a.shape[0]] for a in dense]
        if os.path.isfile(lp(side)) or any((round(o.shape[1] * k), round(o.shape[0] * k)) != tuple(s)
                                           for o, s in zip(one, sizes)):
            with open(lp(side), "w", encoding="utf-8", newline="\n") as f:
                json.dump({"sizes": sizes}, f)
    return not same


# ------------------------------------------------------------------------------------------------- checking
def check(hero):
    """-> problems: a made frame unlike the sheet's, a strip unlike the dense frames."""
    cfg = load(hero)
    hid, pack, _, _ = hero_row(hero)
    try:
        import scipy  # noqa: F401
        lo = True
    except ImportError:
        lo = False
    new, _ = make(hero, cfg, lo=lo)
    anims, px = T.read(hid, pack)
    bad = []
    for t, fr in new.items():
        have = frames_of(anims, px, t)
        if len(have) != len(fr):
            bad.append(f"{t}: {len(have)} frames, made {len(fr)}")
            continue
        for i, ((a, ms), (b, ms2)) in enumerate(zip(fr, have)):
            if a.shape != b.shape:
                bad.append(f"{t}[{i}]: {b.shape[1]}x{b.shape[0]} in the sheet, made {a.shape[1]}x{a.shape[0]}")
            elif (a != b).any():
                bad.append(f"{t}[{i}]: {int((a != b).any(-1).sum())} squares unlike what this makes")
            elif abs(ms - ms2) > 0.5:
                bad.append(f"{t}[{i}]: {ms2} ms, made {ms}")
    for tag in cfg["tags"]:
        png, _ = strip_paths(hid, tag)
        if os.path.isfile(lp(png)):
            s = np.array(Image.open(lp(png)).convert("RGBA"))
            want = strip_of([a for a, _ in new["hd_" + tag]])
            if s.shape != want.shape or (s != want).any():
                bad.append(f"{os.path.basename(png)}: not the dense {tag} frames (ppu_hd.py would make them without parts)")
    if not lo:
        print(f"{hid}: lo_ frames not compared (no scipy: tools/art/pixel_down.py makes them)")
    return bad


# ------------------------------------------------------------------------------------------------- League's sway
def motion(hero, lol):
    """`bend` a frame per part from League's clips: each part's League chain (`lol`: {"root", "tip"} joints) seen
    through the camera of the poses spec the hero's frames were posed with (`poses`: default its poses.json), its tip's
    rows against its root (a `hang` part: its columns, + right) - from the mean of the run clip's, where the run's
    picture is drawn - times `gain`, capped at `cap` (a picture bent further breaks into a saw)."""
    cfg = load(hero)
    sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
    import native_pose as N
    poses = cfg.get("poses") or os.path.join("assets", "source", short(hero), "poses.json")
    with open(lp(os.path.join(ROOT, poses)), encoding="utf-8") as f:
        spec = json.load(f)
    chibi = dict(spec["chibi"])
    keep = chibi.pop("keep", None)
    ch = N.Champ(lol, spec["champ"], keep, spec.get("weapon", r"^weapon$"), spec.get("hide", ()),
                 spec.get("hair_part", False), spec.get("crown"), spec.get("parts", ()),
                 spec.get("hide_submeshes", False), spec.get("submesh_textures"), spec.get("glue"), spec.get("legs"),
                 spec.get("head_joint", "head"), spec.get("opaque", False), spec.get("wad"))
    cam = spec["camera"]
    rot = N.camera(cam)
    sign = -1.0 if cam.get("mirror") else 1.0
    pv, _, _ = ch.posed(spec["design"], chibi)
    cv = pv @ rot.T
    unit = spec["height"] / (cv[ch.headv, 1].max() - cv[ch.legv, 1].min())
    by = {j["name"].lower(): k for k, j in enumerate(ch.joints)}
    _, _, ppu, _ = hero_row(hero)

    def at(g, name):
        p = rot @ g[by[name.lower()]][:3, 3]
        return np.array([sign * p[0], -p[1]]) * unit * ppu      # dense squares: right +, down +

    def pose(fs, tagspec):
        return ch.posed(fs, chibi, tagspec.get("turn", 0.0), tagspec.get("head_like"))[1]

    lolp = {p["name"]: p["lol"] for p in cfg["parts"] if p.get("lol")}
    axis = {p["name"]: 0 if (p.get("bend") or {}).get("hang") else 1 for p in cfg["parts"]}
    ref = {}
    for name, L in lolp.items():
        t = spec["tags"][L.get("ref", "run")]
        v = [at(g, L["tip"]) - at(g, L["root"]) for g in (pose(f[0], t) for f in t["frames"])]
        ref[name] = np.mean(v, axis=0)
    base = read_base(cfg)
    for tag in cfg["tags"]:
        t = spec["tags"]["idle" if tag == "idle_base" else tag]
        fr = cfg.setdefault("frames", {}).setdefault(tag, {})
        bends = fr.setdefault("bend", {})
        n = len(base[tag]["hd"])
        specs = [f[0] for f in t["frames"]]
        if len(specs) != n:
            # (a tag redrawn with another frame count since it was posed - an idle loop of 8 for League's 6: each
            # frame takes the pose at its share of the way through)
            print(f"{tag}: {len(specs)} poses for {n} frames - spread")
            specs = [specs[int(round(i * (len(specs) - 1) / float(max(1, n - 1))))] for i in range(n)]
        gs = [pose(f, t) for f in specs]
        places = fr.get("hd") or [[0, 0, "id"]] * len(gs)
        for name, L in lolp.items():
            out, had = [], list(bends.get(name) or [])
            for i, (g, (_, _, how)) in enumerate(zip(gs, places)):
                if per_frame(cfg, tag, "orient", name, i) is not None and i < len(had):
                    out.append(had[i])                  # (a part drawn its own way there: its bend set by hand)
                    continue
                d = at(g, L["tip"]) - at(g, L["root"]) - ref[name]
                # (a turned frame: the sway in the figure's own rows - a quarter turn back)
                for _ in range((4 - {"id": 0, "h": 0, "r90": 1, "r180": 2, "r270": 3, "r90h": 1, "r270h": 3}[how]) % 4):
                    d = np.array([d[1], -d[0]])         # (one counter-clockwise quarter turn on the screen)
                if how in ("h", "r90h", "r270h"):
                    d = np.array([-d[0], d[1]])         # (tf_arr mirrors first, then turns: undone the other way)
                out.append(int(max(-L["cap"], min(L["cap"], round(d[axis[name]] * L["gain"])))))
            bends[name] = out
        print(f"{tag:14s} " + "  ".join(f"{n} {bends[n]}" for n in lolp))
    save(hero, cfg)


# ------------------------------------------------------------------------------------------------- review
def review(hero, new, info, out_dir, installed=None):
    """Per tag: every frame, installed | new, at game size x3 (dense squares at 3 / PPU); the base's 1x frames | new at
    x3 below; a note of each frame's growth."""
    cfg = load(hero)
    hid, pack, ppu, _ = hero_row(hero)
    os.makedirs(out_dir, exist_ok=True)
    root = installed or ROOT
    sys.path.insert(0, HERE)
    anims_i = json.load(open(lp(os.path.join(root, pack, "champions", hid + "#anim.fanim")), encoding="utf-8-sig"))["anims"]
    px_i = np.array(Image.open(lp(os.path.join(root, pack, "champions", hid + "#sheet.png"))).convert("RGBA"))
    ground = np.array([96, 128, 72, 255], np.uint8)

    def game(a, z):
        """`a` (dense) at game size x z: each game px z screen px (nearest)."""
        k = z / ppu
        H, W = a.shape[:2]
        h, w = max(1, round(H * k)), max(1, round(W * k))
        ys = np.minimum(((np.arange(h) + 0.5) / k).astype(int), H - 1)
        xs = np.minimum(((np.arange(w) + 0.5) / k).astype(int), W - 1)
        return a[ys][:, xs]

    def row_of(frames, gap=6):
        h = max(a.shape[0] for a in frames)
        cells = []
        for a in frames:
            c = np.zeros((h, a.shape[1], 4), np.uint8)
            oy = (h - a.shape[0]) // 2
            c[oy:oy + a.shape[0]] = a
            c = np.where(c[..., 3:] > 0, c, ground)
            cells.append(np.pad(c, ((0, 0), (0, gap), (0, 0)), constant_values=255))
        return np.concatenate(cells, 1)

    paths = []
    for tag in cfg["tags"]:
        old = [a for a, _ in frames_of(anims_i, px_i, "hd_" + tag)]
        nw = [a for a, _ in new["hd_" + tag]]
        old1 = [a for a, _ in frames_of(anims_i, px_i, tag)]
        nw1 = [a for a, _ in new[tag]]
        rows = [row_of([game(a, 3) for a in old]), row_of([game(a, 3) for a in nw]),
                row_of([np.repeat(np.repeat(a, 3, 0), 3, 1) for a in old1]),
                row_of([np.repeat(np.repeat(a, 3, 0), 3, 1) for a in nw1])]
        W = max(r.shape[1] for r in rows)
        img = np.concatenate([np.pad(r, ((0, 8), (0, W - r.shape[1]), (0, 0)), constant_values=255) for r in rows])
        p = os.path.join(out_dir, f"{short(hero)}_{tag}_game_x3.png")
        Image.fromarray(img).save(p)
        paths.append(p)
    with open(os.path.join(out_dir, f"{short(hero)}_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=0)
    return paths


# ------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", action="append", help="default (with --check): every hero with a data file")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry", action="store_true", help="make the frames, write nothing")
    ap.add_argument("--review", help="review pictures into this folder")
    ap.add_argument("--installed", help="the installed tree, for the review's 'installed' rows (default: this one)")
    ap.add_argument("--init", help="write HERO's base from its sheet")
    ap.add_argument("--from", dest="rev", help="--init: the sheet at this git revision")
    ap.add_argument("--anchors", help="find HERO's anchors again (writes the data file)")
    ap.add_argument("--motion", help="HERO's bends from League's clips (writes the data file)")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol", help="League install folder (--motion)")
    a = ap.parse_args()
    if a.init:
        init(a.init, a.rev)
        return
    if a.anchors:
        anchors(a.anchors)
        return
    if a.motion:
        motion(a.motion, a.lol)
        return
    heroes = a.hero or (heroes_with_data() if a.check else None)
    if not heroes:
        if a.check:
            print("ok: no hero has a data file (assets/source/<hero>/hd/<hero>_parts.json)")
            return
        ap.error("--hero, or --check for every hero")
    bad = 0
    for hero in heroes:
        if a.check:
            problems = check(hero)
            for p in problems:
                print(f"{hero}: {p}")
            bad += len(problems)
            if not problems:
                print(f"ok: {hero}'s design parts in every tag as made")
            continue
        cfg = load(hero)
        new, info = make(hero, cfg)
        if a.review:
            for p in review(hero, new, info, a.review, a.installed):
                print("wrote", p)
        if a.dry:
            continue
        changed = write(hero, new, cfg)
        hid = hero_row(hero)[0]
        r = subprocess.run([sys.executable, os.path.join(HERE, "hero_reels.py"), "--hero", hid], capture_output=True,
                           text=True)
        print(f"{hid}: {len(cfg['tags'])} tags with their parts; fanim {'CHANGED (build league.dll again)' if changed else 'unchanged'}"
              f"; hero_reels: {r.stdout.strip() or r.stderr.strip()}")
    if a.check:
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
