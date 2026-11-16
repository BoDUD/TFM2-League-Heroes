#!/usr/bin/env python3
"""A hero's drawn run with life in the upper body: the legs exactly as drawn, the upper body one drawing that bobs
with the steps, the back hair (a cape, a tail) swinging after it as a chain, fists and weapons lagging it a square
(the user, on league_vi's and league_lux's runs re-posed from League's motion: 「拉克丝 蔚全都不合格 我让你改不是让你改原本的
走路的腿部的姿势 只是身体有点动画效果 看起来不要那么僵硬 你现在改的导致模型严重变形了」 - keep the drawn legs, give the body some
animation so it is less stiff - 「蔚先回复到main分支的模型再改」, then 「装好后处理别的英雄吧」 and 「之前修过节奏的也要修
都要给我review才行」: every hero, each one reviewed before it is installed).

    python tools/art/run_body_anim.py --hero vi               # run / hd_run / lo_run into the sheet (+ the strip)
    python tools/art/run_body_anim.py --hero vi --check       # exit 1 when the sheet's run tags are not what it makes
    python tools/art/run_body_anim.py --hero vi --dry         # make them, write nothing
    python tools/art/run_body_anim.py --check                 # every hero with a data file
    python tools/art/run_body_anim.py --init fiora [--drawn-from 858cbab94]
                                                              # a first data file from the hero's own frames
    python tools/art/run_body_anim.py --batch fiora zyra --out C:/t/par_work/run_body/batch1
                                                              # review sets (tools/art/run_body_review.py), nothing written
    python tools/art/run_body_anim.py --batch vi jinx --variants "base:v1,lively:活泼" --installed C:/t/inst_bv --out DIR
                                                              # a hero's variants side by side, the installed run first

Each hero's data is its own file, assets/source/<hero>/hd/<hero>_run_body.json (heroes are added on separate branches
without touching each other), its drawn run beside it (<hero>_run_drawn.png + .json: the dense frames the tool starts
from, kept apart so it can make them again; --init copies them from the sheet - with --drawn-from, from the sheet at a
git revision - and writes a first data file, tools/art/run_body_init.py). Every frame is made of:

- its legs, square for square as drawn: every square of the frame from its waist (`waist`: a row from its centre, a
  frame each) down, but the pieces of its upper body that hang below it. `below` finds those: either rects (frame
  rows and cols, a list a frame; in them, what its legs reach - 4-connected through its own squares that are not
  outline, from outside the rects - stays legs), or "match": the upper body is one drawing in every frame, only moved
  (league_fiora's, league_zyra's, league_jinx's) - the squares where frame `from`'s laid upper body sits in the frame,
  square for square alike, go (a leg drawn over it stays); `clear` adds rects (rows and cols from the centre) where
  all but the legs goes - a braid's end drawn swinging a column;
- one upper body - frame `from`'s: its head (one drawing, no frame's own head or ear any more), torso, arms and hands
  and what they hold - laid by whole squares where `bob` puts it: rows down from frame `from`'s drawn place, a frame
  each - two beats a cycle, low as each step lands, high as it pushes off - never sideways (`x`: columns off frame
  `from`'s place, the same in every frame);
- in it, `parts` that lag the body (`poly`: corners in frame `from`, its outline in; `skip`: colours inside it that
  are not its own; `behind`: laid behind the body and the legs, a cape; `lag` in frames; `range` of rows): their rows
  off the body are the body's own bob `lag` frames before minus now (the bob read as a periodic curve through the
  frames), rounded and held in the range - a fist that drops a square as she rises. A part by her face gets a range
  that never moves it towards it; a part with `lag` 0 is locked to the body (a gun in her hands);
- `chains` (hair, a braid: its `colours` on the `side` of a `root` column, between two `rows` - under the waist too -
  and the outline only they touch; `front`: laid over the body, a braid in front of what she carries on her back): every
  column lagging the body by more the farther it is from the root (`lag` frames at the tip, `whip` that much more swing
  there), the root staying on the body, neighbouring columns never more than a square apart; `hang` (with `poly` and
  `tip`): a chain hanging DOWN from a root ROW - every row shifted sideways by its share of `tip` (columns a frame, +
  right) by how far it is below the root, neighbouring rows never more than a square apart (league_camille's rear skirt
  panels, swung back and forth on League's path: a cloth panel, not a tail);
- `keep`: rects (rows and cols from the centre) whose squares stay the frame's own - a vine the drawing swings by
  itself and the hand on it, never the legs - in front, moved with the body (so it stays in its hand).
- `steps`: every drawn frame shown that many frames (2: 8 drawn frames, 16 frames), each 1 / `steps` of its time (or
  `cycle_ms` split evenly) - its legs as drawn on all of them, the upper body moving on every one: `bob` has a value a
  frame then (two beats: a quick dip as each step lands, a slower rise on the push-off) and the `lag`s count frames;
- a part's `rows` (a value a frame) instead of `lag` / `range`: a head that nods - a square lower on the frame of each
  landing's lowest, back the next; a chain's `with`: the part it hangs from, its rows on every column too (the back
  hair with that head); a square in two parts' corners is the first one's; a chain's `tip_lag` (with `tip`): frames
  the tip's path lags the root end by - each column takes the tip's path that much earlier by its share of the way out
  (league_belveth's hair ribbon: League's Hair4..Hair8 follow one another, a wave running out along it);
- `keep_gaps`: what was ground between the pieces of frame `from`'s drawing (by the body's rows; under its waist, away
  from the frame's legs) stays ground where the frame's own upper body was - without it a square shut in from both
  sides is filled, which closes the drawing's own gaps once the body sits further off its drawn place;
- `bare_ground`: what a moved part or chain bares at her outer edge - a square it left that reaches the ground round her
  through clear squares - stays ground instead of being joined (without it a lifted lock of hair leaves its old lower
  edge as outline); what it leaves shut in between her pieces is still joined;
- `variants`: {name: keys to change} (`base`: the variant it starts from; `parts` / `chains`: by name, keys to change
  or a whole new one) for review sets side by side (--batch --variants); the sheet carries the data without one until
  `use` names one.
- `add`: pieces of the hero's League design its drawing lacks (league_jax's topknot and cloak strips - the user: 「贾克斯
  可以补造型」), each a small picture in the hero's own colours and outline - `rows` of characters from the square `at`
  of frame `from`, `key` their colours - laid into frame `from`'s drawing (behind it, `under`, by default) for a chain or
  a part to cut out by its corners and move; a variant names them like `parts` (null: that one goes);
- `part_gaps`: a moved part or chain takes its own surroundings along: a square it left that is clear in frame `from`'s
  drawing where the moved piece puts it (the air beside a staff slid along itself, under a raised topknot) stays ground
  instead of a fill - what it bares of the drawing behind it is still filled.
- `open_pockets`: N - a pocket of more than N squares the moved layers shut off, at least half of it clear in the
  frame's own drawing (the sky between two spider legs whose tips swing together: league_elise), stays ground instead
  of being filled with outline as a pinhole.
- `match_search`: N (`below` "match") - how far round the frames' centres the drawn place of frame `from`'s upper body
  is looked for (7 squares by default): league_nilah's leaping frames are drawn on the same rows of a rect 23-27 rows
  taller, so their centres sit 12-14 rows under where her upper body is.
- `keep_lo`: like `keep_one` for the lo_ frames - they stay the drawn run's own (<hero>_run_lo.png), for a hero whose
  lo_run is not add_lo's from his dense frames (league_malzahar's timing-only run keeps every square of it).
- `frame_shift`: [rows, cols] a drawn frame - every square of that drawn frame moved by whole squares in its rect before
  anything else is made of it (down +, right +): a frame the artist drew off the others' place (league_soraka's frames
  3 and 6, her whole figure drawn 10-22 columns back: she lurched back and forth every step), re-registered; no square
  changes or goes (one that would leave the rect stops the tool: grow it with `pad`).
- `props` (with `lock` "head"): rigid props the artist redrew a little differently in every frame (league_sona's etwahl:
  「琴女的琴有点变形」) - one drawing each, laid on each frame's own drawn place: `squares` (a mask spec in its drawn frame
  `from` - the head's by default - its squares with their outline and what rests on it, the hands on its strings), `at`
  (rows / cols off its place in frame `from`, from the frames' centres, a frame each), `clear` (a mask spec a drawn frame,
  null: none - the frame's own drawing of it, exactly those squares go); laid in front, the gaps joined as the head's. A
  mask spec: (row, col) corners, or {"rows": [[row, first col, last col], ...]}, in the frame's own rows / cols.
- `head_chains` (with `lock` "head"): pieces of the laid head that swing on their own (league_tristana's long ears
  flopping on League's Ear02 paths on her locked head): each the head's squares in `poly` (corners in frame `from`) on
  the `side` of its `root` column, every column off the laid head by its share of `tip` (rows a frame) as a chain's,
  neighbouring columns at most a square apart - behind the rest (`front`: over it); the head's own edge it bares is
  closed with 2 squares of outline, the rest of what it leaves is ground. `head_search`: how far from the frames'
  centres the frame's own head is looked for (10 squares by default).
- `lock` "own": nothing is laid from frame `from` - every frame keeps its own drawing (a run drawn as whole key poses, the
  arms pumping as drawn: league_shyvana's Codex poses), its upper body (above its `waist`, with what `below`'s rects
  hold) moved `shift` rows down (never up: lowered over its own hips) and `shift_x` columns (+ right: a rigid lean,
  never a turn) over its own legs, the legs square for square as drawn (compose_own) - with `steps` 2 the body bobs on
  every frame while each drawn pose is shown twice; `upper` (a mask spec a drawn frame) names that upper body square
  for square where no waist row and rects can (a tail leaving the hip under the belt: everything but the legs, cut off
  at the hips).
- `shade`: which leg is near shown by its shade, as a run's legs cross (league_ambessa, both legs one dark armour:
  「安蓓萨感觉腿部没有交叉感 看的不是太明显」, then 「安蓓萨 你决定」) - in each drawn frame the `far` leg's squares (a mask
  spec a drawn frame) a step darker and the `near` leg's a step lighter along their colour's `ramps` (dark to light;
  `keep_dark`: never darker, `keep_light`: never lighter; another colour stays), laid on the drawn frame before it is
  composed - the drawing's shapes square for square, only the shade. Default: none.
Order, back to front: the chains, the parts `behind`, the legs, the body, the `front` chains, the other parts in their
order, the kept squares. Where the frame's own upper body was and nothing is laid, a square inside her is filled from
her legs' own colours round it, or with outline where only the laid body is round it; the rest is cleared; an edge that
bares is closed with 2 squares of outline; a pinhole none of the drawings has is outline. `fill` "between" (the
default): inside = shut in by her squares from both sides (within 3 where she was, 1 where a part moved off: a chain
takes its own outline along); "closing" (league_vi's, made first): closing her figure by 3. Last,
tools/art/thin_outline.py's pass with the hero's own settings (thin_outline.json), so CI's --check finds nothing to
change.
The 1x frames come from the dense ones as tools/art/ppu_one.py makes them (the drawn run's 1x sizes kept; squares that
do not fit are reported by --dry), the lo_ frames as tools/art/ppu_hd.py's add_lo does, thinned the same way. Frames
that keep their sizes and timing are written into their own rects (the fanim, which league.dll's hd.rs embeds, does not
change); when the drawn run differs from the sheet's (a run taken from another revision: league_jinx), the tags' old
squares are cleared and the frames put in free room, every other tag where it was - then league.dll is built again,
and a tag another tool makes from the run is made again (league_jinx's run_x: tools/art/jinx_excited_run.py, then
thin_outline.py --hero jinx). tools/art/ppu_restyle.py writes a hero's strip again from assets/source/ppu/orig/: run
this after it, as thin_outline.py runs after it.
"""
import argparse
import math
import glob
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import thin_outline as T  # noqa: E402

K8 = np.ones((3, 3), bool)
GAME_BOB = 1.6          # game px from low to high (the base game's runs bob a median 2 px; Vi's 3 squares = 1.64)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def short(hero):
    return hero.split("_", 1)[1] if hero.startswith(("league_", "tft_")) else hero


def data_file(hero):
    return os.path.join(ROOT, "assets", "source", short(hero), "hd", f"{short(hero)}_run_body.json")


def heroes_with_data():
    return sorted(os.path.basename(p)[:-len("_run_body.json")]
                  for p in glob.glob(os.path.join(ROOT, "assets", "source", "*", "hd", "*_run_body.json")))


def with_variant(cfg, name):
    """The data with variant `name` laid over it (`variants`: {name: keys to change} - `base`: the variant it starts
    from; `parts` / `chains`: {name: keys to change} for the ones there, whole new ones (a `poly` / `colours`) added)."""
    import copy
    v = cfg["variants"][name]
    out = with_variant(cfg, v["base"]) if v.get("base") else copy.deepcopy(cfg)
    for k, x in v.items():
        if k in ("base", "notes"):
            continue
        if k in ("parts", "chains") or (k == "add" and isinstance(x, dict)):   # (`add`'s pieces by name too)
            have = {item["name"]: item for item in out.get(k, [])}
            for nm, ch in x.items():
                if ch is None:                           # null: that one goes (a cape made a chain instead)
                    out[k] = [item for item in out.get(k, []) if item["name"] != nm]
                elif nm in have:
                    have[nm].update(copy.deepcopy(ch))
                else:
                    out.setdefault(k, []).append(dict(copy.deepcopy(ch), name=nm))
        else:
            out[k] = copy.deepcopy(x)
    out["variant"] = name
    return out


def load(hero, variant=None):
    """The hero's data - with `use`'s variant (the one its sheet carries) laid over it, or `variant`'s ("base": none)."""
    with open(lp(data_file(hero)), encoding="utf-8") as f:
        cfg = json.load(f)
    use = cfg.get("use") if variant is None else variant
    if use and use != "base":
        cfg = with_variant(cfg, use)
    cfg["outline"] = tuple(cfg["outline"])
    cfg.setdefault("below", [])
    if cfg["below"] != "match":
        cfg["below"] = [[tuple(r) for r in rs] for rs in cfg["below"]]
    for p in cfg.get("parts", []):
        p["poly"] = [tuple(v) for v in p["poly"]]
        if "range" in p:
            p["range"] = tuple(p["range"])
        p["skip"] = [tuple(c) for c in p.get("skip", [])]
    for c in cfg.get("chains", []):
        c["colours"] = [tuple(v) for v in c.get("colours", [])]
        if c.get("poly"):
            c["poly"] = [tuple(v) for v in c["poly"]]
    pr, pc = cfg.get("pad", (0, 0))
    if pr or pc:
        # frames grown by `pad`: what is given in a frame's own rows / cols (corners, a chain's root and rows, `below`'s
        # rects, the head and chin) moves with its squares; what is given from the centre does not
        for p in cfg.get("parts", []):
            p["poly"] = [(r + pr, c + pc) for r, c in p["poly"]]
        for c in cfg.get("chains", []):
            c["root"] += pr if c.get("hang") else pc     # (`hang`: the root is a row)
            if "rows" in c:
                c["rows"] = [c["rows"][0] + pr, c["rows"][1] + pr]
            if c.get("poly"):
                c["poly"] = [(r + pr, q + pc) for r, q in c["poly"]]
        if cfg.get("head"):
            cfg["head"] = [[r + pr, c + pc] for r, c in cfg["head"]]
            cfg["chin"] += pr
        if cfg.get("chin_rows"):
            cfg["chin_rows"] = [r + pr for r in cfg["chin_rows"]]
        if cfg["below"] != "match":
            cfg["below"] = [[(None if r0 is None else r0 + pr, r1 + pr, c0 + pc, c1 + pc) for r0, r1, c0, c1 in rs]
                            for rs in cfg["below"]]
        for a in cfg.get("add", []):
            a["at"] = [a["at"][0] + pr, a["at"][1] + pc]
        for key in ("head_clear", "own_clear", "upper", "shift_parts"):
            if cfg.get(key):
                cfg[key] = [None if q is None else
                            {"rows": [[r + pr, c0 + pc, c1 + pc] for r, c0, c1 in q["rows"]]} if isinstance(q, dict)
                            else [[r + pr, c + pc] for r, c in q] for q in cfg[key]]
        for key in ("far", "near"):
            if cfg.get("shade") and cfg["shade"].get(key):
                cfg["shade"][key] = [None if q is None else
                                     {"rows": [[r + pr, c0 + pc, c1 + pc] for r, c0, c1 in q["rows"]]}
                                     if isinstance(q, dict) else [[r + pr, c + pc] for r, c in q]
                                     for q in cfg["shade"][key]]
        for pr_ in cfg.get("props", []):
            # (`props`: its squares in its frame `from` and each frame's `clear` are in the frames' own rows / cols)
            pr_["squares"] = shift_spec(pr_["squares"], pr, pc)
            pr_["clear"] = [None if q is None else shift_spec(q, pr, pc) for q in pr_["clear"]]
        if cfg.get("own_paint"):
            cfg["own_paint"] = [None if not q else
                                [dict(d, rows=[[r + pr, c0 + pc, c1 + pc] for r, c0, c1 in d["rows"]])
                                 for d in (q if isinstance(q, list) else [q])] for q in cfg["own_paint"]]
    return cfg


def added(src, cfg):
    """Frame `from`'s drawing with `add`'s pieces in it: parts of the hero's League design the drawing lacks (the user,
    on league_jax: 「贾克斯可以补造型」 - his topknot, the cloth strips of his cloak), each a small picture in the
    hero's own colours and outline - `rows` of characters from its top-left square `at` (frame `from`'s rows and
    columns), `key` naming each character's colour, "." nothing - laid behind the drawing (`under`, the default:
    only where it is clear) or over it. A chain or a part then cuts them out of it by its corners and moves them on the
    hero's League paths; the frames' own drawings never get them."""
    if not cfg.get("add"):
        return src
    out = src.copy()
    for a in cfg["add"]:
        key = {k: tuple(int(x) for x in v) for k, v in a["key"].items()}
        r0, c0 = a["at"]
        for dr, line in enumerate(a["rows"]):
            for dc, ch in enumerate(line):
                if ch in ". ":
                    continue
                y, x = r0 + dr, c0 + dc
                if not (0 <= y < out.shape[0] and 0 <= x < out.shape[1]):
                    sys.exit(f"add {a.get('name')}: square ({y}, {x}) off frame `from` ({out.shape[1]}x{out.shape[0]}):"
                             f" grow it (`pad`)")
                if a.get("under", True) and out[y, x, 3] > 0:
                    continue
                out[y, x, :3] = key[ch]
                out[y, x, 3] = 255
    return out


def save(hero, cfg):
    """The data file, a key a line (lists kept on one line each)."""
    lines = []
    for k, v in cfg.items():
        if k in ("parts", "chains", "below") and v and not isinstance(v, str):
            inner = ",\n".join("    " + json.dumps(x, ensure_ascii=False) for x in v)
            lines.append(f'  "{k}": [\n{inner}\n  ]')
        elif k == "notes":
            inner = ",\n".join(f"    {json.dumps(a, ensure_ascii=False)}: {json.dumps(b, ensure_ascii=False)}"
                               for a, b in v.items())
            lines.append(f'  "{k}": {{\n{inner}\n  }}')
        else:
            lines.append(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}")
    os.makedirs(os.path.dirname(lp(data_file(hero))), exist_ok=True)
    with open(lp(data_file(hero)), "w", encoding="utf-8", newline="\n") as f:
        f.write("{\n" + ",\n".join(lines) + "\n}\n")


def colour_mask(a, cols):
    m = np.zeros(a.shape[:2], bool)
    for c in cols:
        m |= (a[..., :3] == np.array(c)).all(-1)
    return m & (a[..., 3] > 0)


def poly_mask(poly, shape):
    """The squares whose centres lie inside a polygon of (row, col) corners."""
    H, W = shape[:2]
    Y, X = np.mgrid[0:H, 0:W]
    y, x = Y + 0.5, X + 0.5
    m = np.zeros((H, W), bool)
    for k in range(len(poly)):
        (y1, x1), (y2, x2) = poly[k], poly[(k + 1) % len(poly)]
        if y1 == y2:
            continue
        m ^= ((y1 > y) != (y2 > y)) & (x < x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    return m


def disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return (y * y + x * x) <= r * r + 0.5


# ------------------------------------------------------------------------------------------------- the frames
def sheet(hid, pack, rev=None):
    """(anims, pixels) of the hero's sheet - the tree's, or at a git revision."""
    if rev is None:
        return T.read(hid, pack)
    rel = os.path.relpath(T.stem(hid, pack), ROOT).replace(os.sep, "/")
    env = dict(os.environ, MSYS_NO_PATHCONV="1")
    fan = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{rel}#anim.fanim"], capture_output=True, check=True, env=env)
    png = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{rel}#sheet.png"], capture_output=True, check=True, env=env)
    import io
    anims = json.loads(fan.stdout.decode("utf-8-sig"))["anims"]
    return anims, np.array(Image.open(io.BytesIO(png.stdout)).convert("RGBA"))


def frames_of(anims, px, tag):
    out = []
    for f in anims[tag]["frames"]:
        x, y, w, h = (int(round(f["data"][q])) for q in ("x", "y", "w", "h"))
        out.append((px[y:y + h, x:x + w].copy(), int(round(f["duration"] * 1000))))
    return out


def drawn(cfg):
    """-> ([(frame, ms)] of the hero's drawn run, its meta: sizes, ms, and the 1x / lo_ sizes when kept)."""
    s = np.array(Image.open(lp(os.path.join(ROOT, cfg["drawn"] + ".png"))).convert("RGBA"))
    with open(lp(os.path.join(ROOT, cfg["drawn"] + ".json")), encoding="utf-8") as f:
        meta = json.load(f)
    out, x = [], 0
    pr, pc = cfg.get("pad", (0, 0))                  # `pad`: room grown round every frame (rows, cols a side)
    for (w, h), ms in zip(meta["sizes"], meta["ms"]):
        f = s[:h, x:x + w].copy()
        if pr or pc:
            f = np.pad(f, ((pr, pr), (pc, pc), (0, 0)))
        out.append((f, ms))
        x += w + 1
    return out, meta


def keep_drawn(hero, frames, one_sizes, lo_sizes, origin):
    """The drawn run as the tool's source: <hero>_run_drawn.png (the frames left to right, a square apart) + .json."""
    base = os.path.join("assets", "source", short(hero), "hd", f"{short(hero)}_run_drawn")
    H = max(a.shape[0] for a, _ in frames)
    s = np.zeros((H, sum(a.shape[1] + 1 for a, _ in frames) - 1, 4), np.uint8)
    x = 0
    for a, _ in frames:
        s[:a.shape[0], x:x + a.shape[1]] = a
        x += a.shape[1] + 1
    os.makedirs(os.path.dirname(lp(os.path.join(ROOT, base))), exist_ok=True)
    Image.fromarray(s, "RGBA").save(lp(os.path.join(ROOT, base + ".png")), optimize=True)
    meta = {"from": origin, "sizes": [[a.shape[1], a.shape[0]] for a, _ in frames], "ms": [m for _, m in frames],
            "one_sizes": one_sizes, "lo_sizes": lo_sizes}
    with open(lp(os.path.join(ROOT, base + ".json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f)
    return base.replace(os.sep, "/")


# ------------------------------------------------------------------------------------------------- the motion
def curve(vals):
    """The periodic curve through vals (one a frame): its value at any (fractional) frame."""
    n = len(vals)
    X = np.fft.rfft(np.asarray(vals, float))

    def at(t):
        out = X[0].real / n
        for k in range(1, len(X)):
            w = 1.0 if (n % 2 == 0 and k == n // 2) else 2.0
            out += w / n * (X[k] * np.exp(2j * np.pi * k * t / n)).real
        return out
    return at


def lagged(at, i, lag, gain=1.0):
    """Rows a part lagging the body by `lag` frames sits off it at frame i (down +)."""
    return gain * (at(i - lag) - at(i))


def chain_offsets(at, n, c, cols):
    """{col: rows} per frame for a chain over cols (its root column's side)."""
    root = c["root"]
    span = max(1, max(abs(root - x) for x in cols)) if cols else 1
    order = sorted(cols, key=lambda x: abs(root - x))
    rows = []
    for i in range(n):
        d, prev = {}, 0
        for x in order:
            u = abs(root - x) / float(span)
            v = int(round(lagged(at, i, c["lag"] * u, 1.0 + c.get("whip", 0.0) * u)))
            v = max(prev - 1, min(prev + 1, v))          # neighbouring columns at most a square apart
            d[x] = v
            prev = v
        rows.append(d)
    return rows


def motion(cfg, n, chain_cols):
    """-> {"body": [rows], part name: [rows], chain name: [{col: rows}]} per frame."""
    bob = cfg["bob"]
    at = curve(bob)
    out = {"body": list(bob)}
    for p in cfg.get("parts", []):
        if p.get("path") is not None:                    # (rows, columns) a frame: a gauntlet on League's swing
            if len(p["path"]) != n:
                sys.exit(f"part {p['name']}: {len(p['path'])} steps for {n} frames")
            out[p["name"]] = [(int(v[0]), int(v[1])) for v in p["path"]]
            continue
        if p.get("rows") is not None:                    # rows given a frame (a head that nods)
            if len(p["rows"]) != n:
                sys.exit(f"part {p['name']}: {len(p['rows'])} rows for {n} frames")
            out[p["name"]] = [int(v) for v in p["rows"]]
            continue
        lo, hi = p["range"]
        out[p["name"]] = [int(min(hi, max(lo, round(lagged(at, i, p["lag"]))))) for i in range(n)]
    for c in cfg.get("chains", []):
        if c.get("tip") is not None:
            # `tip`: the tip's rows a frame (League's hair end against the chest): each column that share of it by
            # how far it is from the root, neighbouring columns never more than a square apart
            cols = chain_cols[c["name"]]
            root = c["root"]
            span = max(1, max(abs(root - x) for x in cols)) if cols else 1
            order = sorted(cols, key=lambda x: abs(root - x))
            # `tip_lag`: frames the tip's path lags the chain's root end by (a ribbon's wave running out along it, as
            # League's hair joints follow one another): a column that share of the way out takes the tip's path that
            # much earlier (the periodic curve through the `tip` rows), scaled by its share - the tip keeps `tip`
            tip_at = curve(c["tip"]) if c.get("tip_lag") else None
            rows_ = []
            for i in range(n):
                d, prev = {}, 0
                for x in order:
                    if tip_at is None:
                        v = int(round(c["tip"][i] * abs(root - x) / float(span)))
                    else:
                        u = abs(root - x) / float(span)
                        v = int(round(tip_at(i + float(c["tip_lag"]) * (1.0 - u)) * u))
                    v = max(prev - 1, min(prev + 1, v))
                    d[x] = v
                    prev = v
                rows_.append(d)
            out[c["name"]] = rows_
        else:
            out[c["name"]] = chain_offsets(at, n, c, chain_cols[c["name"]])
        if c.get("with"):                                # hanging from a part: its rows on every column too
            w = out[c["with"]]
            out[c["name"]] = [{x: v + w[i] for x, v in d.items()} for i, d in enumerate(out[c["name"]])]
    return out


# ------------------------------------------------------------------------------------------------- the layers
def pieces(src, cfg, i_src):
    """Frame `from`'s upper body cut into its layers -> {"body", chain names, part names: mask}, each with the outline
    that is its own (the outline a square deep against the other layers, two against the ground)."""
    H, W = src.shape[:2]
    op = src[..., 3] > 0
    ink = colour_mask(src, [cfg["outline"]])
    cy = H // 2
    upper = np.zeros((H, W), bool)
    upper[:cy + cfg["waist"][i_src]] = True
    parts, had = {}, np.zeros((H, W), bool)
    for p in cfg.get("parts", []):                       # (a square in two parts' corners: the first one's)
        if p.get("late"):
            continue                                     # (cut from the body after the chains: below)
        parts[p["name"]] = poly_mask(p["poly"], src.shape) & op & ~colour_mask(src, p.get("skip", [])) & ~had
        had |= parts[p["name"]]
    every = (upper & op)
    for m in parts.values():
        every |= m
    kept = keep_mask(src, cfg, i_src)
    every &= ~kept
    for name in parts:
        parts[name] &= ~kept
    out, taken = {}, np.zeros((H, W), bool)
    for m in parts.values():
        taken |= m
    for c in cfg.get("chains", []):
        side = np.zeros((H, W), bool)
        if c.get("hang"):
            side[:] = True                               # (a hanging chain: its corners say where it is)
        elif c.get("side", "left") == "left":
            side[:, :c["root"]] = True
        else:
            side[:, c["root"] + 1:] = True
        rows = np.zeros((H, W), bool)
        r0, r1 = c.get("rows", (0, H))
        rows[r0:r1] = True
        if c.get("poly"):
            # a chain cut by its corners (a cape: every square in them, its outline too) - not by colours
            m = poly_mask(c["poly"], src.shape) & op & side & rows & ~taken & ~kept
            out[c["name"]] = m
            taken |= m
            every |= m
            continue
        # (a chain may hang under the waist: a whip, a braid - its rows say how far)
        m = colour_mask(src, c["colours"]) & (every | (op & rows & ~upper)) & side & rows & ~taken & ~kept
        lab, n = ndimage.label(m, structure=K8)
        if n:
            sz = ndimage.sum(m, lab, range(1, n + 1))
            m = np.isin(lab, [j + 1 for j in range(n) if sz[j] >= c.get("min", 12)])
        solid_rest = every & ~ink & ~m & ~taken
        # its outline: what touches it and no other solid square of hers, on its side of the root
        cink = ink & (every | (op & rows & ~upper)) & side & ndimage.binary_dilation(m, structure=K8) & \
            ~ndimage.binary_dilation(solid_rest, structure=K8) & ~taken & ~kept
        out[c["name"]] = m | cink
        taken |= out[c["name"]]
        every |= out[c["name"]]
    out["body"] = every & ~taken
    out.update(parts)
    for p in cfg.get("parts", []):
        if p.get("late"):
            # `late`: the body's squares in its corners once the chains and the other parts have theirs (a head that
            # nods: a box round it, the hair chain keeping its own)
            m = poly_mask(p["poly"], src.shape) & out["body"] & ~colour_mask(src, p.get("skip", []))
            out[p["name"]] = m
            out["body"] &= ~m
    return out


def keep_mask(a, cfg, i):
    """`keep`: rects (rows, cols from the frame's centre: first row, last row, first col, last col) whose squares stay
    the frame's own - a vine swinging in the drawing, a hand that holds it - one list for every frame or one a frame."""
    H, W = a.shape[:2]
    m = np.zeros((H, W), bool)
    k = cfg.get("keep") or []
    rs = k[i] if k and isinstance(k[0][0], list) else k
    for r0, r1, c0, c1 in rs:
        m[max(0, H // 2 + r0):max(0, H // 2 + r1 + 1), max(0, W // 2 + c0):max(0, W // 2 + c1 + 1)] = True
    if not m.any():
        return m
    # never her legs: what her feet reach under the waist (4-connected through her squares that are not outline)
    op = a[..., 3] > 0
    ink = colour_mask(a, [cfg["outline"]])
    low = np.zeros((H, W), bool)
    low[H // 2 + cfg["waist"][i]:] = True
    through = op & ~ink & low
    lab, _ = ndimage.label(through)
    ys = np.nonzero(op.any(1))[0]
    feet = np.zeros((H, W), bool)
    feet[ys.max() - 2:ys.max() + 1] = True
    hit = np.unique(lab[through & feet])
    legs = np.isin(lab, hit[hit > 0])
    legs |= ink & low & ndimage.binary_dilation(legs, structure=K8)
    return m & op & ~legs


def own_clear_mask(a, cfg, i):
    """`own_clear`: a drawn frame's own drawing of a part laid anew from frame `from` (a chain on League's path) - a list a
    drawn frame (null: none) of corners in the frame's own rows / cols, or {"rows": [[row, first col, last col], ...]}:
    exactly those squares of it go, whatever the waist (league_rengar's tail, drawn a little differently in every
    frame: none of it may stay beside the one laid). What they leave counts as bared by a moved part: with `bare_ground`
    it is ground where it reaches the ground round her, else joined as any gap."""
    H, W = a.shape[:2]
    m = np.zeros((H, W), bool)
    q = (cfg.get("own_clear") or [None] * (i + 1))[i]
    if not q:
        return m
    if isinstance(q, dict):
        for r, c0, c1 in q["rows"]:
            if 0 <= r < H:
                m[r, max(0, c0):min(W, c1 + 1)] = True
    else:
        m = poly_mask([tuple(p) for p in q], a.shape)
    return m & (a[..., 3] > 0)


def own_paint(b, cfg, i):
    """`own_paint`: squares of a drawn frame's own drawing painted anew once `own_clear` has cleared what it clears - a
    list a drawn frame (null: none) of {"rows": [[row, first col, last col], ...], "colour": [R, G, B] (the outline by
    default)}, one or a list of them, in the frame's own rows / cols. They are the frame's own drawing from then on (not
    gaps to fill): the outline of league_irelia's hair where a blade drawn over its edge is cleared and laid anew behind
    it - the hair keeps an edge when the blade floats off. -> the squares (painted into b)."""
    H, W = b.shape[:2]
    m = np.zeros((H, W), bool)
    q = (cfg.get("own_paint") or [None] * (i + 1))[i]
    if not q:
        return m
    for d in (q if isinstance(q, list) else [q]):
        col = tuple(int(v) for v in d.get("colour", cfg["outline"]))
        for r, c0, c1 in d["rows"]:
            if 0 <= r < H and c1 >= max(0, c0):
                sl = slice(max(0, c0), min(W, c1 + 1))
                b[r, sl, :3] = col
                b[r, sl, 3] = 255
                m[r, sl] = True
    return m


def shift_spec(q, pr, pc):
    """A mask given as corners or {"rows": [[row, first col, last col], ...]}, moved `pad`'s (rows, cols)."""
    if isinstance(q, dict):
        return {"rows": [[r + pr, c0 + pc, c1 + pc] for r, c0, c1 in q["rows"]]}
    return [[r + pr, c + pc] for r, c in q]


def shade_legs(a, cfg, i):
    """`shade`: drawn frame i with its `far` leg a ramp step darker and its `near` leg a step lighter (a copy; frame i as
    it is without `shade`)."""
    sh = cfg.get("shade")
    if not sh:
        return a
    ramps = [[tuple(c) for c in r] for r in sh["ramps"]]
    keep = {-1: {tuple(c) for c in sh.get("keep_dark", [])}, 1: {tuple(c) for c in sh.get("keep_light", [])}}
    b = a.copy()
    op = a[..., 3] > 0
    for key, step in (("far", -1), ("near", 1)):
        q = (sh.get(key) or [None] * (i + 1))[i]
        for y, x in zip(*np.nonzero(spec_mask(q, a.shape) & op)):
            c = tuple(int(v) for v in a[y, x, :3])
            for r in ramps:
                if c in r:
                    j = r.index(c) + step
                    if 0 <= j < len(r) and c not in keep[step]:
                        b[y, x, :3] = r[j]
                    break
    return b


def spec_mask(q, shape):
    """The squares a mask spec names: {"rows": [[row, first col, last col], ...]} (several runs a row) or a polygon of
    (row, col) corners - in a frame's own rows / cols."""
    H, W = shape[:2]
    m = np.zeros((H, W), bool)
    if not q:
        return m
    if isinstance(q, dict):
        for r, c0, c1 in q["rows"]:
            if 0 <= r < H and c1 >= max(0, c0):
                m[r, max(0, c0):min(W, c1 + 1)] = True
        return m
    return poly_mask([tuple(v) for v in q], shape)


def prop_layers(frames, cfg):
    """`props` (`lock` "head"): rigid props the artist redrew a little differently in every frame (league_sona's etwahl:
    「琴女的琴有点变形」) - each one drawing, its drawn frame `from`'s (the head's `from` by default): `squares` (its
    squares there, with its outline and what rests on it - the hands on the strings) -> [(prop, its frame, its mask)]."""
    out = []
    for pr in cfg.get("props", []):
        j = int(pr.get("from", cfg["from"]))
        psrc = frames[j][0]
        out.append((pr, psrc, spec_mask(pr["squares"], psrc.shape) & (psrc[..., 3] > 0)))
    return out


def own_upper(a, cfg, i, match=None):
    """Frame i's own upper body: everything above its waist and, under it, either what `below`'s rects hold that its
    legs do not reach, or (`below` "match": the upper body is one drawing in every frame, only moved) the squares of
    frame `from`'s laid upper body where it sits in frame i, square for square alike (a leg drawn over it stays).
    `upper` (`lock` "own"; a mask spec a drawn frame, null: the waist / `below` rule): exactly those squares of the
    frame - a pose whose tail, hair or hanging fist reaches under any one waist row (league_shyvana's tail from the hip):
    everything but the legs, the legs cut off at the hips by hand."""
    H, W = a.shape[:2]
    op = a[..., 3] > 0
    if cfg.get("upper") and cfg["upper"][i]:
        return spec_mask(cfg["upper"][i], a.shape) & op
    ink = colour_mask(a, [cfg["outline"]])
    cy = H // 2
    wr = cy + cfg["waist"][i]
    up = np.zeros((H, W), bool)
    up[:wr] = True
    low = ~up
    if cfg["below"] == "match":
        src, union, (dy, dx) = match
        ys, xs = np.nonzero(union)
        ty, tx = ys + dy, xs + dx
        ok = (ty >= 0) & (ty < H) & (tx >= 0) & (tx < W)
        ys, xs, ty, tx = ys[ok], xs[ok], ty[ok], tx[ok]
        same = (a[ty, tx] == src[ys, xs]).all(-1) & op[ty, tx]
        hang = np.zeros((H, W), bool)
        hang[ty[same], tx[same]] = True
        # `clear`: rects (from the frame's centre) under the waist where the frame's own pieces of the upper body are
        # drawn a little differently each frame (a braid's swinging end): all of it but what the legs reach goes
        rect = np.zeros((H, W), bool)
        for r0, r1, c0, c1 in cfg.get("clear", []):
            rect[max(0, cy + r0):max(0, cy + r1 + 1), max(0, W // 2 + c0):max(0, W // 2 + c1 + 1)] = True
        if rect.any():
            through = op & ~ink & low
            lab, _ = ndimage.label(through)
            hit = np.unique(lab[through & ~rect])
            legs = np.isin(lab, hit[hit > 0])
            hang |= rect & low & op & ~legs & ~(ink & ndimage.binary_dilation(legs, structure=K8))
        return (up & op) | (hang & low)
    rect = np.zeros((H, W), bool)
    for r0, r1, c0, c1 in (cfg["below"][i] if cfg["below"] else []):
        rect[(wr if r0 is None else r0):r1 + 1, c0:c1 + 1] = True
    through = op & ~ink & low
    lab, _ = ndimage.label(through)
    hit = np.unique(lab[through & ~rect])
    legs = np.isin(lab, hit[hit > 0])
    hang = rect & low & op & ~ink & ~legs
    if cfg.get("hang_outline") == "nearest" and hang.any():
        # `hang_outline` "nearest": a hanging piece's outline is every outline square in its rects nearer to it than to
        # her legs (8-neighbour steps, within 3) - its outline two squares deep goes with it (league_gangplank's coat
        # tails swung on League's path: the outer row left behind stood alone), the legs' own outline stays theirs
        far = np.full((H, W), 99, np.int32)
        dh = ndimage.distance_transform_cdt(~hang, metric="chessboard")
        dl = ndimage.distance_transform_cdt(~legs, metric="chessboard") if legs.any() else far
        hang |= rect & low & ink & (dh < dl) & (dh <= 3)
        return (up & op) | hang
    # the hanging pieces' outline: what touches them and not her legs
    hang |= rect & low & ink & ndimage.binary_dilation(hang, structure=K8) & ~ndimage.binary_dilation(legs, structure=K8)
    return (up & op) | hang


def drawn_shift(src, a, union, search=7):
    """Where frame `from`'s upper body (union) sits in frame a: the whole-square shift (from the centres) that puts the
    most of its squares on alike squares -> ((dy, dx), share alike)."""
    ys, xs = np.nonzero(union)
    cdy, cdx = a.shape[0] // 2 - src.shape[0] // 2, a.shape[1] // 2 - src.shape[1] // 2
    best = ((cdy, cdx), -1)
    for dy in range(cdy - search, cdy + search + 1):
        for dx in range(cdx - search, cdx + search + 1):
            ty, tx = ys + dy, xs + dx
            ok = (ty >= 0) & (ty < a.shape[0]) & (tx >= 0) & (tx < a.shape[1])
            n = int((a[ty[ok], tx[ok]] == src[ys[ok], xs[ok]]).all(-1).sum())
            if n > best[1]:
                best = ((dy, dx), n)
    return best[0], best[1] / float(max(1, len(ys)))


# ------------------------------------------------------------------------------------------------- the frame
def fill_in(b, inside, voters):
    """The inside squares filled from the voters' colours round them, ring by ring (the commonest of the 8 neighbours,
    across counted above diagonals); a square no voter reaches stays clear."""
    key = (b[..., 0].astype(np.int64) << 16) | (b[..., 1].astype(np.int64) << 8) | b[..., 2]
    voter = voters.copy()
    todo = inside.copy()
    while todo.any():
        step = []
        for y, x in zip(*np.nonzero(todo)):
            votes = {}
            for vy in (-1, 0, 1):
                for vx in (-1, 0, 1):
                    yy, xx = y + vy, x + vx
                    if (vy or vx) and 0 <= yy < b.shape[0] and 0 <= xx < b.shape[1] and voter[yy, xx]:
                        k = int(key[yy, xx])
                        votes[k] = votes.get(k, 0) + (1.0 if vy == 0 or vx == 0 else 0.7)
            if votes:
                step.append((y, x, max(votes, key=lambda q: (votes[q], -q))))
        if not step:
            break
        for y, x, k in step:
            b[y, x] = ((k >> 16) & 255, (k >> 8) & 255, k & 255, 255)
            key[y, x] = k
            voter[y, x] = True
            todo[y, x] = False


def pockets(a):
    """The clear squares the figure shuts in (not reaching the frame's edge)."""
    lab, n = ndimage.label(a[..., 3] == 0)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    return (lab > 0) & ~np.isin(lab, edge)


def lay(b, src, m, dy, dx, cols=None, under=False, rows=None):
    """src's squares in m into b moved (dy, dx) (cols: {col: extra rows} per source column; rows: {row: extra cols} per
    source row - a `hang` chain); under: only where b is clear. -> (the squares laid, the squares that would leave the
    frame)."""
    ys, xs = np.nonzero(m)
    ty = ys + dy + (np.array([cols.get(int(x), 0) for x in xs], int) if cols else 0)
    tx = xs + dx + (np.array([rows.get(int(y), 0) for y in ys], int) if rows else 0)
    ok = (ty >= 0) & (ty < b.shape[0]) & (tx >= 0) & (tx < b.shape[1])
    lost = int((~ok).sum())
    if under:
        ok &= np.where(ok, b[np.clip(ty, 0, b.shape[0] - 1), np.clip(tx, 0, b.shape[1] - 1), 3] == 0, False)
    b[ty[ok], tx[ok]] = src[ys[ok], xs[ok]]
    put = np.zeros(b.shape[:2], bool)
    put[ty[ok], tx[ok]] = True
    return put, lost


def x_at(cfg, i):
    """`x`: columns off frame `from`'s place - one for every frame, or one a frame (a body on each frame's own hips)."""
    x = cfg.get("x", 0)
    return int(x[i]) if isinstance(x, list) else int(x)


def off_of(v):
    """A part's offset a frame: rows, or (rows, columns) for one on a path."""
    return (int(v[0]), int(v[1])) if isinstance(v, (tuple, list)) else (int(v), 0)


def layer_names(cfg):
    """Back to front: the chains, the parts behind the body (a cape), the body, the parts in front (fists, a weapon);
    `lock` "head": the head alone; `lock` "own": none (every frame its own drawing)."""
    if cfg.get("lock") == "head":
        return ["head"]
    if cfg.get("lock") == "own":
        return []
    parts, chains = cfg.get("parts", []), cfg.get("chains", [])
    return ([c["name"] for c in chains if not c.get("front")] + [p["name"] for p in parts if p.get("behind")] + ["body"]
            + [c["name"] for c in chains if c.get("front")] + [p["name"] for p in parts if not p.get("behind")])


def compose(a, i, src, cy0, cx0, layers, mov, cfg, match=None, pose=None):
    """Frame i made: its legs (drawn frame `pose`'s: i's own unless `steps` shows a drawn frame more than once), frame
    `from`'s upper body laid as `mov` says, the gaps joined. -> (frame, info)."""
    pose = i if pose is None else pose
    out_c = cfg["outline"]
    H, W = a.shape[:2]
    cy, cx = H // 2, W // 2
    kept = keep_mask(a, cfg, pose)
    own = own_upper(a, cfg, pose, match) & ~kept
    oc_ = own_clear_mask(a, cfg, pose) & ~kept
    own |= oc_
    b = a.copy()
    b[own] = 0
    painted = own_paint(b, cfg, pose)                    # (`own_paint`: the frame's own squares painted anew)
    legs = b[..., 3] > 0
    dy = cy - cy0 + mov["body"][i]
    dx = cx - cx0 + x_at(cfg, i)
    info = {"own": own, "legs": legs & ~painted, "at": (dy, dx), "lost": 0, "painted": painted}
    names = layer_names(cfg)
    base = np.zeros((H, W, 4), np.uint8)                 # every layer at the body's place (no lag): what they cover
    for name in names:
        lay(base, src, layers[name], dy, dx)
    for c in [c for c in cfg.get("chains", []) if not c.get("front")]:
        info[c["name"]], lost = lay(b, src, layers[c["name"]], dy, dx, under=True,
                                    **{"rows" if c.get("hang") else "cols": mov[c["name"]][i]})
        info["lost"] += lost
    for p in [p for p in cfg.get("parts", []) if p.get("behind")]:
        oy, ox = off_of(mov[p["name"]][i])
        info[p["name"]], lost = lay(b, src, layers[p["name"]], dy + oy, dx + ox, under=True)
        info["lost"] += lost
    info["body"], lost = lay(b, src, layers["body"], dy, dx)
    info["lost"] += lost
    for c in [c for c in cfg.get("chains", []) if c.get("front")]:
        info[c["name"]], lost = lay(b, src, layers[c["name"]], dy, dx,
                                    **{"rows" if c.get("hang") else "cols": mov[c["name"]][i]})
        info["lost"] += lost
    for p in [p for p in cfg.get("parts", []) if not p.get("behind")]:
        oy, ox = off_of(mov[p["name"]][i])
        info[p["name"]], lost = lay(b, src, layers[p["name"]], dy + oy, dx + ox)
        info["lost"] += lost
    # kept squares in front, the frame's own - moved with the body by as many rows as it sits off the frame's drawn
    # upper body (`below` "match" finds where that is)
    ky = 0 if match is None else dy - match[2][0]
    if ky:
        moved = np.zeros_like(kept)
        ys, xs = np.nonzero(kept)
        ok = (ys + ky >= 0) & (ys + ky < H)
        b[ys[ok] + ky, xs[ok]] = a[ys[ok], xs[ok]]
        moved[ys[ok] + ky, xs[ok]] = True
        kept = moved
    else:
        b[kept] = a[kept]
    for name in names:
        info[name] &= ~kept
    info["kept"] = kept
    put = np.zeros((H, W), bool)
    for name in names:
        info[name] &= b[..., 3] > 0
        put |= info[name]
    clear = b[..., 3] == 0
    gone = (a[..., 3] > 0) & clear                       # hers before, nothing laid on it
    revealed = (base[..., 3] > 0) & clear                # covered had the parts not moved off the body
    revealed |= oc_ & clear                              # (`own_clear`: the frame's own drawing of a part laid anew)
    # inside her: `fill` "closing" (league_vi's): where she was or a part moved off, closing her figure by 3; else
    # ("between") only squares her squares shut in from both sides - within 3 where she was, 1 where a part moved off
    # (a thin chain or part takes its own outline along: what it bares at its edge is ground, not outline)
    if cfg.get("fill", "between") == "closing":
        inside = (gone | revealed) & ndimage.binary_closing(put | legs, structure=disk(3))
    else:
        inside = (gone & T.between(put | legs, 3)) | (revealed & T.between(put | legs, 1))
    if cfg.get("keep_gaps"):
        # the laid drawing's own gaps stay ground: a square whose place in frame `from` (by the body's rows) is clear,
        # above its waist or away from the frame's legs - between the launcher's tip and her hair, between two braids
        # (by her legs a square stays inside: what a braid's end drawn over a leg hid is the leg)
        sy, sx = np.mgrid[0:H, 0:W]
        ty, tx = sy - dy, sx - dx
        ok = (ty >= 0) & (ty < src.shape[0]) & (tx >= 0) & (tx < src.shape[1])
        by_legs = ndimage.binary_dilation(legs, structure=K8, iterations=2)
        gap = np.zeros((H, W), bool)
        gap[ok] = (src[ty[ok], tx[ok], 3] == 0) & ((ty[ok] < src.shape[0] // 2 + cfg["waist"][cfg["from"]])
                                                   | ~by_legs[ok])
        inside &= ~gap
    pg = part_gaps(src, layers, mov, cfg, i, dy, dx, b) if cfg.get("part_gaps") else np.zeros((H, W), bool)
    inside &= ~pg
    open_ = np.zeros((H, W), bool)
    if cfg.get("bare_ground"):
        # `bare_ground`: what a moved layer (a part off its place, a chain's columns) bares at her outer edge stays
        # ground - a square it left that reaches the ground round her through clear squares is neither filled nor
        # outlined; the between-fill still closes the gaps shut in (a lifted hair's old lower edge stays open sky, the
        # squares between it and her shoulder are joined)
        lab, _ = ndimage.label(clear)
        edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
        open_ = revealed & np.isin(lab, edge[edge > 0])
        inside &= ~open_
    keep_open = np.zeros((H, W), bool)
    if cfg.get("own_clear_ground"):
        # `own_clear_ground`: what `own_clear` leaves stays ground even where her pieces shut it in (the gap a lifted
        # tail leaves between her claws and her paws is air, not a fill) - but for a pinhole of 1-2 squares
        lab_, n_ = ndimage.label(clear & oc_)
        if n_:
            size_ = ndimage.sum(np.ones((H, W)), lab_, range(1, n_ + 1))
            keep_open = np.isin(lab_, [j + 1 for j in range(n_) if size_[j] > 2])
        inside &= ~keep_open
    # inside her: from her legs' own colours where they are round it, else outline (between the laid layers)
    near_legs = inside & ndimage.binary_dilation(legs, structure=K8, iterations=2)
    fill_in(b, near_legs, legs & ~colour_mask(b, [out_c]))
    rest = inside & (b[..., 3] == 0)
    b[rest, :3] = out_c
    b[rest, 3] = 255
    # an edge that bares where she was: 2 squares of outline on the bared side (in "between": an edge of her own
    # squares, her legs' - the laid layers bring their outline with them)
    clear = b[..., 3] == 0
    was = gone & clear
    solid = (b[..., 3] > 0) & ~colour_mask(b, [out_c])
    if cfg.get("fill", "between") != "closing":
        solid &= ~put
    d = T.steps_from(solid, np.ones((H, W), bool), 2)
    bare = was & (d <= 2) & ndimage.binary_dilation(solid & ndimage.binary_dilation(was, structure=K8), structure=K8,
                                                    iterations=2) & ~pg & ~open_
    b[bare, :3] = out_c
    b[bare, 3] = 255
    if cfg.get("fill", "between") == "closing":
        shut = pockets(b) & ~pockets(a)
    else:
        # a pinhole none of the drawings has where it is now: the frame `from`'s own (laid with its layers) and the
        # frame's own under the waist are the drawing's
        laid = np.zeros((H, W), bool)
        ps = pockets(src)
        hangs = {c["name"] for c in cfg.get("chains", []) if c.get("hang")}
        for name in names:
            ys, xs = np.nonzero(ps & ndimage.binary_dilation(layers[name], structure=K8))
            if not len(ys):
                continue
            off, offx = dy, 0                            # (the body's own rows are in dy)
            if name != "body" and isinstance(mov[name][i], dict) and name in hangs:
                offx = np.array([mov[name][i].get(int(y), 0) for y in ys], int)
            elif name != "body" and isinstance(mov[name][i], dict):
                off = dy + np.array([mov[name][i].get(int(x), 0) for x in xs], int)
            elif name != "body":
                oy, offx = off_of(mov[name][i])
                off = dy + oy
            ty, tx = ys + off, xs + dx + offx
            ok = (ty >= 0) & (ty < H) & (tx >= 0) & (tx < W)
            laid[ty[ok], tx[ok]] = True
        own_low = pockets(a) & ~own_upper(a, cfg, pose, match)
        shut = pockets(b) & ~laid & ~ndimage.binary_dilation(own_low, structure=K8)
    if keep_open.any():
        # (`own_clear_ground`: a pocket holding what it left open stays open)
        lab_, n_ = ndimage.label(pockets(b))
        hit_ = np.unique(lab_[keep_open & (b[..., 3] == 0)])
        shut &= ~np.isin(lab_, hit_[hit_ > 0])
    if cfg.get("open_pockets"):
        # `open_pockets`: N - a pocket of more than N squares the moved layers shut off, at least half of it clear in
        # the frame's own drawing (the sky between two spider legs whose tips swing together: league_elise), stays
        # ground instead of being filled with outline as a pinhole
        lab_, n_ = ndimage.label(pockets(b))
        for j in range(1, n_ + 1):
            m_ = lab_ == j
            if m_.sum() > int(cfg["open_pockets"]) and (a[..., 3][m_] == 0).mean() >= 0.5:
                shut &= ~m_
    b[shut, :3] = out_c
    b[shut, 3] = 255
    info["joined"] = ((near_legs | rest | bare | shut) & (b[..., 3] > 0)) & ~put
    return b, info


def part_gaps(src, layers, mov, cfg, i, dy, dx, b):
    """`part_gaps`: a part or chain moved off its place takes its own surroundings along - a square it left that is clear
    in frame `from`'s drawing where the moved piece puts it (beside the piece, in the air) stays ground, never a fill (a
    staff slid along itself: its ends, the air round its hands; a topknot whipped up: the air under it). What it bared
    of the drawing behind it (a hand that slid off the robe it covered) is still filled. -> the squares."""
    H, W = b.shape[:2]
    out = np.zeros((H, W), bool)
    clear = b[..., 3] == 0
    chain_names = {c["name"] for c in cfg.get("chains", [])}
    hangs = {c["name"] for c in cfg.get("chains", []) if c.get("hang")}
    for name in layer_names(cfg):
        if name == "body" or name not in mov:
            continue
        ys, xs = np.nonzero(layers[name])
        hy, hx = ys + dy, xs + dx                           # its own place (no offset)
        ok = (hy >= 0) & (hy < H) & (hx >= 0) & (hx < W)
        home = np.zeros((H, W), bool)
        home[hy[ok], hx[ok]] = True
        vy, vx = np.nonzero(home & clear)
        if not len(vy):
            continue
        if name in hangs:                                   # (a hanging chain: columns off by its rows)
            oy = 0
            ox = np.array([mov[name][i].get(int(y - dy), 0) for y in vy], int)
        elif name in chain_names:
            oy = np.array([mov[name][i].get(int(x - dx), 0) for x in vx], int)
            ox = 0
        else:
            oy, ox = off_of(mov[name][i])
        sy, sx = vy - dy - oy, vx - dx - ox                 # where the moved piece's drawing puts the square
        inb = (sy >= 0) & (sy < src.shape[0]) & (sx >= 0) & (sx < src.shape[1])
        ground = ~inb
        ground[inb] = src[sy[inb], sx[inb], 3] == 0
        out[vy[ground], vx[ground]] = True
    return out


# ------------------------------------------------------------------------------------------------- the head alone
def head_of(src, cfg):
    """Frame `from`'s head (`lock` "head"): its squares inside `head` (corners in frame `from`), the piece of them joined
    to its biggest run (8-connected)."""
    m = poly_mask(cfg["head"], src.shape) & (src[..., 3] > 0)
    lab, n = ndimage.label(m, structure=K8)
    if n > 1:
        m = lab == 1 + int(np.argmax(ndimage.sum(m, lab, range(1, n + 1))))
    return m


def find_head(src, a, head, search=10):
    """Where the frame's own head sits: the shift (from the centres) putting frame `from`'s head on the most alike
    squares of frame a - a square alike in colour counts 2, opaque on opaque 1, opaque on clear -1 -> (dy, dx)."""
    ys, xs = np.nonzero(head)
    cdy, cdx = a.shape[0] // 2 - src.shape[0] // 2, a.shape[1] // 2 - src.shape[1] // 2
    best = None
    for dy in range(cdy - search, cdy + search + 1):
        for dx in range(cdx - search, cdx + search + 1):
            ty, tx = ys + dy, xs + dx
            ok = (ty >= 0) & (ty < a.shape[0]) & (tx >= 0) & (tx < a.shape[1])
            if ok.mean() < 0.95:
                continue
            on = a[ty[ok], tx[ok]]
            opq = on[:, 3] > 0
            same = opq & (on[:, :3] == src[ys[ok], xs[ok], :3]).all(-1)
            sc = 2 * int(same.sum()) + int(opq.sum()) - int((~opq).sum())
            if best is None or sc > best[0]:
                best = (sc, dy, dx)
    return best[1], best[2]


def head_chain_masks(src, cfg, head):
    """`head_chains` (with `lock` "head"): pieces of the laid head that swing on their own, the way `chains` with `tip` do
    (league_tristana's long ears flopping on League's Ear02 paths on her locked head) - each its squares of the head in
    `poly` (corners in frame `from`) on the `side` of its `root` column; {name: mask}, in their order."""
    out, taken = {}, np.zeros(head.shape, bool)
    for c in cfg["head_chains"]:
        side = np.zeros(head.shape, bool)
        if c.get("side", "left") == "left":
            side[:, :c["root"]] = True
        else:
            side[:, c["root"] + 1:] = True
        m = poly_mask([tuple(v) for v in c["poly"]], src.shape) & head & side & ~taken
        out[c["name"]] = m
        taken |= m
    return out


def compose_head(a, i, src, head, mov, cfg, pose=None, props=None, hchains=None):
    """Frame i (drawn frame `pose`'s) with frame `from`'s head on its own head's place (rows `bob`, columns `x` off it): the
    frame's own head cleared round it - its own head colours (`head_colours`, frame `from`'s head's by default) within 2
    squares, above its chin (`chin`: frame `from`'s first row of the neck) - the rest of the frame square for square its
    own; the gaps the clearing leaves inside her filled from her own colours round them, bared edges closed with 2
    squares of outline, a pinhole none of the drawings has filled with outline. -> (frame, info)."""
    pose = i if pose is None else pose
    out_c = cfg["outline"]
    H, W = a.shape[:2]
    torso, legs_only, sh_joined = None, None, None
    sh = cfg["shift"][i] if cfg.get("shift") else 0
    if sh:
        a, torso, legs_only, sh_joined = shifted_upper(a, cfg, pose, sh)
    # `head_match_colours`: the head is put where the frame's own head's squares of these colours are (goggles, eyes):
    # matched on them alone, the rest of a redrawn head (hair spikes, a longer face) does not pull it off
    tmpl = head & colour_mask(src, [tuple(c) for c in cfg["head_match_colours"]]) if cfg.get("head_match_colours") \
        else head
    # `head_search`: how far (squares from the frames' centres) the frame's own head is looked for - 10 by default;
    # league_kayle hovers, her figure rising and falling 20-odd squares in her frames, so her face is looked for further
    my, mx = find_head(src, a, tmpl, int(cfg.get("head_search", 10)))
    dy, dx = my + mov["body"][i], mx + x_at(cfg, i)
    same = pose == cfg["from"] or (a.shape == src.shape and np.array_equal(a, src))
    props = props or []
    # (`props`: a frame whose own prop is cleared, or that gets one laid from another frame, is made)
    prop_here = any(pr["clear"][pose] or int(pr.get("from", cfg["from"])) != pose or any(pr["at"][i])
                    for pr, _, _ in props)
    hchains = hchains or {}
    chain_here = any(any(mov[nm][i].values()) for nm in hchains)  # (`head_chains` off their place this frame)
    if same and (dy, dx) == (my, mx) == (0, 0) and not sh and not prop_here and not chain_here:
        # frame `from` keeps its own head where it is: nothing to change (nor in a frame drawn the same as frame `from`:
        # a 4-frame drawing shown twice)
        z = np.zeros(a.shape[:2], bool)
        return a.copy(), {"own": z, "legs": a[..., 3] > 0, "at": (0, 0), "lost": 0, "drawn_at": (0, 0),
                          "head": head & (a[..., 3] > 0), "joined": z, "kept": z}
    ys, xs = np.nonzero(head)
    at_match = np.zeros((H, W), bool)
    ok = (ys + my >= 0) & (ys + my < H) & (xs + mx >= 0) & (xs + mx < W)
    at_match[ys[ok] + my, xs[ok] + mx] = True
    cols = [tuple(c) for c in cfg.get("head_colours", [])] or \
        sorted({tuple(int(v) for v in c) for c in src[head][:, :3]})
    cols = cols + [tuple(c) for c in cfg.get("clear_colours", [])]   # (the frame's own head's that frame `from`'s lacks)
    chin = cfg["chin"] + my                            # the frame's own neck starts here
    # `clear_grow`: how far round frame `from`'s head the frame's own is cleared (2 squares by default)
    zone = ndimage.binary_dilation(at_match, structure=K8, iterations=int(cfg.get("clear_grow", 2)))
    if cfg.get("clear_poly"):
        # `clear_poly`: corners in frame `from`, placed where the frame's own head is found - the clearing never goes
        # outside them (a shoulder plate in the head's own colours right under it keeps every square)
        zone &= poly_mask([(r + my, c + mx) for r, c in cfg["clear_poly"]], a.shape)
    hc = cfg.get("head_clear")
    if hc and hc[pose]:
        # `head_clear`: the frame's own head by hand - corners in the frame's own rows / cols, a polygon a drawn frame
        # (null: the zone as above): exactly its squares are cleared, never what is drawn beside it (a fist, a staff, a
        # shoulder pad, a scarf up by the face stays the frame's own, square for square); or {"rows": [[row, first col,
        # last col], ...]}: its squares row by row, several runs a row (a throat between a mane and a jaw stays)
        q = hc[pose]
        if isinstance(q, dict):
            zone = np.zeros((H, W), bool)
            for r, c0, c1 in q["rows"]:
                zone[r, c0:c1 + 1] = True
        else:
            zone = poly_mask([tuple(p) for p in q], a.shape)
    if cfg.get("clear_all"):
        # `clear_all`: every square of the frame's own head goes - all its colours but `keep_colours` (a collar, a
        # scarf round the neck), down to its own chin: the lowest of its face's `skin` squares, and the outline under it
        sk = zone & colour_mask(a, [tuple(c) for c in cfg.get("skin", [])])
        own_chin = int(np.nonzero(sk.any(1))[0].max()) + 2 if sk.any() else chin
        rows_at = cfg.get("chin_rows")
        if rows_at:
            # `chin_rows`: each drawn frame's own chin (its face's lowest row, read off the frame) where the skin runs on
            # down a bare neck and the lowest skin square is not the chin (league_sivir): the clearing stops under it
            own_chin = int(rows_at[pose]) + 2
        zone[max(0, own_chin if rows_at else max(chin, own_chin)):] = False
        fsk = head & colour_mask(src, [tuple(c) for c in cfg.get("skin", [])])
        if cfg.get("head_align") == "chin" and rows_at and not (pose == cfg["from"] and not sh):
            # (with `chin_rows`: frame `from`'s chin - its own `chin_rows` value - laid on the frame's)
            dy = int(rows_at[pose]) - int(rows_at[cfg["from"]]) + mov["body"][i]
        elif cfg.get("head_align") == "chin" and sk.any() and fsk.any() and not (pose == cfg["from"] and not sh):
            # `head_align` "chin": the laid chin on the frame's own drawn chin, so the neck under it is the drawing's
            # (a redrawn head a few rows longer than frame `from`'s: the columns stay where the goggles / eyes put them)
            dy = (own_chin - 2) - int(np.nonzero(fsk.any(1))[0].max()) + mov["body"][i]
        # a collar / scarf (`keep_colours`) stays under the laid chin and behind the laid face (its first skin column);
        # beside the face it is the frame's own bigger head's collar edge and goes with the head
        face_left = (int(np.nonzero(fsk.any(0))[0].min()) + dx) if fsk.any() else W
        rows_, cols_ = np.mgrid[0:H, 0:W]
        # (`keep_above`: from this many rows over the laid chin - 1 by default; league_sivir's shoulder piece, whose top
        # reaches the jaw's rows beside it, keeps its gold from 4 rows up)
        keep_c = colour_mask(a, [tuple(c) for c in cfg.get("keep_colours", [])]) & \
            ((rows_ >= cfg["chin"] + dy - int(cfg.get("keep_above", 1))) | (cols_ < face_left))
        own = zone & (a[..., 3] > 0) & ~keep_c & ~keep_mask(a, cfg, pose)
    else:
        zone[max(0, chin):] = False
        own = zone & colour_mask(a, cols) & ~keep_mask(a, cfg, pose)
    # `head_carry`: what hangs on the frame's own head (a ponytail and its tie: corners in frame `from`, placed where the
    # frame's own head is found) moves with the laid head - as many squares as the laid head sits off the frame's own
    # (`head_align` "chin"'s rows) - as drawn, under the head and behind the rest of the frame (a shoulder it reaches
    # stays over it); the clearing never takes it (its `keep_colours` squares - a shoulder pad reaching into the corners
    # - stay where they are). What it leaves is ground where it reaches the ground round her, else joined as the head's
    # gaps are
    # `carry_colours`: only these (the hair's, the tie's) are carried, with the outline that closes them (within 2 of
    # them, not next to anything else: a sword or a shoulder pad keeps its own outline)
    carry = np.zeros((H, W), bool)
    if cfg.get("head_carry"):
        carry = poly_mask([(r + my, c + mx) for r, c in cfg["head_carry"]], a.shape)
        carry &= (a[..., 3] > 0) & ~colour_mask(a, [tuple(c) for c in cfg.get("keep_colours", [])])
        if cfg.get("carry_colours"):
            hair = carry & colour_mask(a, [tuple(c) for c in cfg["carry_colours"]])
            ink = colour_mask(a, [out_c])
            other = (a[..., 3] > 0) & ~colour_mask(a, [tuple(c) for c in cfg["carry_colours"]]) & ~ink
            # (its outline: reached from the hair through outline squares, a thick tip's too, never one by the rest)
            own_ink = carry & ink & ~ndimage.binary_dilation(other, structure=K8)
            reach = ndimage.binary_dilation(hair, structure=K8) & own_ink
            for _ in range(4):
                reach = ndimage.binary_dilation(reach, structure=K8) & own_ink
            carry &= hair | reach
        own &= ~carry
    # `props`: each frame's own drawing of a prop (`clear`: a mask spec a drawn frame, null: none) goes - exactly those
    # squares - and the prop's one drawing is laid on the frame's own drawn place (`at`: rows / cols off its place in
    # its frame `from`, from the frames' centres, a frame each), in front; the gaps it leaves are joined as the head's
    pclear = np.zeros((H, W), bool)
    for pr, _, _ in props:
        pclear |= spec_mask(pr["clear"][pose], a.shape)
    pclear &= (a[..., 3] > 0) & ~keep_mask(a, cfg, pose) & ~own & ~carry
    b = a.copy()
    b[own] = 0
    b[carry] = 0
    b[pclear] = 0
    legs = b[..., 3] > 0
    info = {"own": own, "legs": legs, "at": (dy, dx), "lost": 0, "drawn_at": (my, mx)}
    carried = np.zeros((H, W), bool)
    if carry.any():
        carried, info["lost"] = lay(b, a, carry, dy - my, dx - mx, under=True)
    hbody = head
    for m_ in hchains.values():
        hbody = hbody & ~m_                              # (`head_chains`: laid on their own, below)
    if cfg.get("head_under"):
        # `head_under`: corners in frame `from` - the head's squares in them are laid only where the frame has nothing
        # left (the hood's lower edge behind the frame's own shoulder plate, which stays over it)
        low = hbody & poly_mask(cfg["head_under"], src.shape)
        info["head"], lost = lay(b, src, hbody & ~low, dy, dx)
        under_put, lost2 = lay(b, src, low, dy, dx, under=True)
        info["head"] |= under_put
        lost += lost2
    else:
        info["head"], lost = lay(b, src, hbody, dy, dx)
    info["lost"] += lost
    cput = np.zeros((H, W), bool)
    for c in (cfg.get("head_chains", []) if hchains else []):
        # `head_chains`: each column of the piece off the laid head by its rows this frame (`tip`, as a chain's), behind
        # the head and whatever of the frame is left (`front`: over them) - the root's columns stay on the head
        c_put, lost = lay(b, src, hchains[c["name"]], dy, dx, cols=mov[c["name"]][i], under=not c.get("front"))
        info[c["name"]] = c_put
        cput |= c_put
        info["lost"] += lost
    pput = np.zeros((H, W), bool)
    for pr, psrc, pm in props:
        ady, adx = (int(v) for v in pr["at"][i])
        p_put, lost = lay(b, psrc, pm, H // 2 - psrc.shape[0] // 2 + ady, W // 2 - psrc.shape[1] // 2 + adx)
        pput |= p_put
        info["lost"] += lost
    put = (info["head"] | cput | pput) & (b[..., 3] > 0)
    info["head"] = put & ~pput
    if props:
        info["props"] = pput & (b[..., 3] > 0)
        info["prop_own"] = pclear
        info["legs"] = legs & ~pput                      # (the laid props are not her own squares changed)
    carried &= ~put
    gone = (a[..., 3] > 0) & (b[..., 3] == 0)
    inside = gone & T.between(put | carried | legs, 3)
    open_ = np.zeros((H, W), bool)
    if carry.any():
        # what the carried squares leave at her outer edge (reaching the ground round her through clear squares) is ground
        lab, _ = ndimage.label(b[..., 3] == 0)
        edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
        open_ = carry & gone & np.isin(lab, edge[edge > 0])
        inside &= ~open_
    if cfg.get("beside_head") == "ground":
        # what the frame's own (bigger) head leaves beside frame `from`'s is ground, not filled from the colours round
        # it (a goggle strap's grey, a collar's teal run into it): only under the laid chin is a gap filled
        inside &= np.arange(H)[:, None] >= cfg["chin"] + dy - 1
    elif cfg.get("beside_head") == "outline":
        # "outline": nothing it leaves is filled from the colours round it, under the chin either (a face at her
        # outer edge with only the outline under its jaw: a hood's blue would run in under it) - what is shut in or
        # by her squares is closed with outline, the rest is ground
        inside[:] = False
    elif cfg.get("beside_head") == "front":
        # "front": that only in front of the laid face (from its first `skin` column on) - a shoulder's gem run into
        # the gap by the jaw; behind it, where the back hair runs on into the frame's own (league_sivir), a gap is
        # filled from the hair round it as without the key
        fsk_ = head & colour_mask(src, [tuple(c) for c in cfg.get("skin", [])])
        front = (int(np.nonzero(fsk_.any(0))[0].min()) + dx) if fsk_.any() else W
        inside &= (np.arange(H)[:, None] >= cfg["chin"] + dy - 1) | (np.arange(W)[None, :] < front)
    voters = legs & ~colour_mask(b, [out_c])
    if cfg.get("fill_skip"):
        # `fill_skip`: colours a gap the clearing leaves is never filled with (they do not vote) - a collar's gold or a
        # neck's skin right under a shorter laid lock of hair (league_leona): such a gap is filled from the other colours
        # round it, else closed with outline as one no colour reaches
        voters &= ~colour_mask(b, [tuple(c) for c in cfg["fill_skip"]])
    fill_in(b, inside, voters)
    rest = inside & (b[..., 3] == 0)
    b[rest, :3] = out_c
    b[rest, 3] = 255
    clear = b[..., 3] == 0
    was = gone & clear
    solid = (b[..., 3] > 0) & ~colour_mask(b, [out_c]) & ~put & ~carried
    d = T.steps_from(solid, np.ones((H, W), bool), 2)
    bare = was & (d <= 2) & ndimage.binary_dilation(solid & ndimage.binary_dilation(was, structure=K8), structure=K8,
                                                    iterations=2) & ~open_
    b[bare, :3] = out_c
    b[bare, 3] = 255
    # a pinhole: neither frame `from`'s head's (laid with it) nor the frame's own (outside the cleared squares; the
    # carried squares' own where they are carried)
    laid = np.zeros((H, W), bool)
    ps = pockets(src) & ndimage.binary_dilation(head, structure=K8)
    py, px_ = np.nonzero(ps)
    okp = (py + dy >= 0) & (py + dy < H) & (px_ + dx >= 0) & (px_ + dx < W)
    laid[py[okp] + dy, px_[okp] + dx] = True
    for pr, psrc, pm in props:
        # (a prop's own pinholes are its drawing's)
        py, px_ = np.nonzero(pockets(psrc) & ndimage.binary_dilation(pm, structure=K8))
        ady, adx = (int(v) for v in pr["at"][i])
        py, px_ = py + H // 2 - psrc.shape[0] // 2 + ady, px_ + W // 2 - psrc.shape[1] // 2 + adx
        okp = (py >= 0) & (py < H) & (px_ >= 0) & (px_ < W)
        laid[py[okp], px_[okp]] = True
    for c in (cfg.get("head_chains", []) if hchains else []):
        # (a swung piece's own pinholes: the drawing's, where its columns put them)
        py, px_ = np.nonzero(pockets(src) & ndimage.binary_dilation(hchains[c["name"]], structure=K8))
        py = py + dy + np.array([mov[c["name"]][i].get(int(x), 0) for x in px_], int)
        px_ = px_ + dx
        okp = (py >= 0) & (py < H) & (px_ >= 0) & (px_ < W)
        laid[py[okp], px_[okp]] = True
    own_p = pockets(a) & ~ndimage.binary_dilation(own | carry | pclear, structure=K8)
    if carry.any():
        py, px_ = np.nonzero(pockets(a) & ndimage.binary_dilation(carry, structure=K8))
        py, px_ = py + dy - my, px_ + dx - mx
        okp = (py >= 0) & (py < H) & (px_ >= 0) & (px_ < W)
        own_p[py[okp], px_[okp]] = True
    shut = pockets(b) & ~laid & ~own_p
    if props:
        # (ground the frame drew open that a laid prop shuts off - more than a slit (12 squares), by the prop, at least
        # half of it clear in the frame's own drawing: the gap between a horn, the hair and an arm - stays ground)
        lab_, n_ = ndimage.label(pockets(b))
        near_ = ndimage.binary_dilation(info["props"], structure=K8)
        for j in range(1, n_ + 1):
            m_ = lab_ == j
            if m_.sum() > 12 and (m_ & near_).any() and (a[..., 3][m_] == 0).mean() >= 0.5:
                shut &= ~m_
    b[shut, :3] = out_c
    b[shut, 3] = 255
    if hchains and cput.any():
        # `head_chains`: the head's own edge a swung piece bares (the hair under a lifted ear shared its outline with the
        # ear) is closed with outline, 2 squares deep as drawn - a square the piece left at its home that is clear now,
        # within 2 of the laid head's own colours; the rest of what it leaves is ground
        home = np.zeros((H, W), bool)
        for m_ in hchains.values():
            ys_, xs_ = np.nonzero(m_)
            ok_ = (ys_ + dy >= 0) & (ys_ + dy < H) & (xs_ + dx >= 0) & (xs_ + dx < W)
            home[ys_[ok_] + dy, xs_[ok_] + dx] = True
        body_solid = info["head"] & ~cput & (b[..., 3] > 0) & ~colour_mask(b, [out_c])
        edge = home & (b[..., 3] == 0) & (T.steps_from(body_solid, np.ones((H, W), bool), 2) <= 2)
        b[edge, :3] = out_c
        b[edge, 3] = 255
        info["chain_edge"] = edge
    if cfg.get("clear_specks"):
        # `clear_specks`: a piece of at most that many squares the clearing cut off from her (the last row of outline
        # under the frame's own longer jaw) goes - one by the cleared squares that no drawing has as a piece of its own
        lab, n = ndimage.label(b[..., 3] > 0, structure=K8)
        if n:
            size = ndimage.sum(np.ones((H, W)), lab, range(1, n + 1))
            by = ndimage.binary_dilation(own, structure=K8, iterations=2)
            lab_a, _ = ndimage.label(a[..., 3] > 0, structure=K8)
            for j in np.nonzero(size <= int(cfg["clear_specks"]))[0]:
                m = lab == j + 1
                if (m & by).any() and not (m & (put | carried)).any() and \
                        not (np.unique(lab_a[m]).size == 1 and (lab_a == lab_a[m][0]).sum() == m.sum()):
                    b[m] = 0
    info["carry"] = carried & (b[..., 3] > 0)
    info["joined"] = ((inside | bare | shut) & (b[..., 3] > 0)) & ~put & ~carried
    info["kept"] = np.zeros((H, W), bool)
    if sh:
        # the frame's own upper body moved: its legs are what is left under the waist (the rest is laid, as drawn)
        info["torso"] = torso & (b[..., 3] > 0) & ~put
        info["legs"] = legs_only & (b[..., 3] > 0) & ~put & ~info["torso"]
        info["joined"] |= sh_joined & (b[..., 3] > 0) & ~put
    info["shift"] = sh
    return b, info


def shifted_upper(a, cfg, pose, sh):
    """`shift` (head lock): the frame's own upper body - above its `waist`, with what `below`'s rects hold - moved `sh`
    rows (down +) over its legs, as drawn; a gap it opens over them filled from their colours (outline where they are
    not round it). `shift_fill` "waist": only a gap opened at its waist is a gap (a body lifted: the rows from the
    waist `sh` rows up to a row under it; a body sunk over its legs opens none) - what the moved body leaves anywhere
    else is the drawing's own ground moved with it (the air between a raised hand and the hair, by a skirt's flared
    hem: league_annie's whole upper body sinking over her legs on each step's contact) and stays ground; without it
    ("between", the default) every square it leaves that its moved squares shut in from both sides within `sh` + 1 is
    filled. `shift_parts`: a mask spec a drawn frame (null: none; corners or {"rows": ...} in the frame's own rows /
    cols) of squares under the waist that move with it whatever touches them - a cloth flap hanging from the belt
    over the thighs (league_neeko's: drawn touching her legs, it stayed with them and the sinking belt hid its top, the
    flap shrinking and growing every step: 「妮蔻可以再调整一下 感觉身体不太自然」). -> (frame, the moved squares, the
    legs' squares, the squares filled)."""
    H, W = a.shape[:2]
    out_c = cfg["outline"]
    own = own_upper(a, cfg, pose)
    sp = (cfg.get("shift_parts") or [None] * (pose + 1))[pose]
    if sp:
        own = own | (spec_mask(sp, a.shape) & (a[..., 3] > 0))
    b = a.copy()
    b[own] = 0
    legs = b[..., 3] > 0
    ys, xs = np.nonzero(own)
    ty = ys + sh
    ok = (ty >= 0) & (ty < H)
    if (~ok).any():
        sys.exit(f"shift {sh}: the upper body leaves frame {pose}")
    b[ty[ok], xs[ok]] = a[ys[ok], xs[ok]]
    put = np.zeros((H, W), bool)
    put[ty[ok], xs[ok]] = True
    gone = (a[..., 3] > 0) & (b[..., 3] == 0)
    inside = gone & T.between(put | legs, abs(sh) + 1)
    if cfg.get("shift_fill", "between") == "waist":
        wr = H // 2 + cfg["waist"][pose]
        band = np.zeros((H, W), bool)
        if sh < 0:
            band[max(0, wr + sh - 1):min(H, wr + 2)] = True
        inside &= band
    near_legs = inside & ndimage.binary_dilation(legs, structure=K8, iterations=2)
    fill_in(b, near_legs, legs & ~colour_mask(b, [out_c]))
    rest = inside & (b[..., 3] == 0)
    b[rest, :3] = out_c
    b[rest, 3] = 255
    return b, put, legs & ~put, inside & (b[..., 3] > 0)


def compose_own(a, i, cfg, pose):
    """`lock` "own": frame i is drawn frame `pose`'s own drawing - nothing laid from frame `from`, every drawn frame its
    own upper body (a run whose poses are drawn whole, the arms pumping as drawn: league_shyvana's Codex key poses) -
    with that upper body (above its `waist`, with what `below`'s rects hold; `upper`: exactly its squares) moved `shift`
    rows DOWN (never up: lowered over its own hips, no gap to fill) and `shift_x` columns (+ right; a rigid lean, never a
    turn) over its own legs as drawn, laid over them; what it leaves is ground (the top edge of the hair, a horn, the
    tail; the gaps between its own feathers moved with it), but a leg's colour square it bares gets outline and a
    pinhole of 1-2 squares none of the drawings has is outline - the legs square for square as drawn. With
    `steps` 2 the body bobs on every frame while each drawn pose is shown twice. -> (frame, info)."""
    sh = int(cfg["shift"][i]) if cfg.get("shift") else 0
    sx = int(cfg["shift_x"][i]) if cfg.get("shift_x") else 0
    z = np.zeros(a.shape[:2], bool)
    if not sh and not sx:
        return a.copy(), {"own": z, "legs": a[..., 3] > 0, "torso": z, "at": (0, 0), "lost": 0, "drawn_at": (0, 0),
                          "head": z, "joined": z, "kept": z, "shift": 0, "shift_x": 0}
    if sh < 0:
        sys.exit(f"`lock` \"own\": shift {sh} at frame {i} - the body is only lowered over its hips (down +)")
    H, W = a.shape[:2]
    out_c = cfg["outline"]
    op0 = a[..., 3] > 0
    own = own_upper(a, cfg, pose)
    b = a.copy()
    b[own] = 0
    legs = b[..., 3] > 0
    ys, xs = np.nonzero(own)
    ty, tx = ys + sh, xs + sx
    if ((ty < 0) | (ty >= H) | (tx < 0) | (tx >= W)).any():
        sys.exit(f"shift {sh}, {sx}: the upper body leaves frame {pose}")
    b[ty, tx] = a[ys, xs]
    put = np.zeros((H, W), bool)
    put[ty, tx] = True
    vacated = (b[..., 3] == 0) & op0
    # a leg's colour square the body bares to the ground (a fist that hung by the thigh moved down) gets outline
    leg_col = legs & ~put & ~colour_mask(b, [out_c])
    bare = vacated & ndimage.binary_dilation(leg_col, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
    b[bare, :3] = out_c
    b[bare, 3] = 255
    # what else it leaves is ground - the gaps between its own feathers, arms and tail move with it, shut in or not -
    # but a pinhole of 1-2 squares none of the drawings has (no pocket of the frame's own moved there) is outline
    moved_pk = np.zeros((H, W), bool)
    py, px_ = np.nonzero(pockets(a) & ndimage.binary_dilation(own, structure=K8))
    okp = (py + sh < H) & (px_ + sx >= 0) & (px_ + sx < W)
    moved_pk[py[okp] + sh, px_[okp] + sx] = True
    lab, n = ndimage.label(b[..., 3] == 0)
    outer = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    pin = np.zeros((H, W), bool)
    for j in range(1, n + 1):
        m_ = lab == j
        if j not in outer and m_.sum() <= 2 and (m_ & vacated).any() and not (m_ & moved_pk).any():
            pin |= m_
    b[pin, :3] = out_c
    b[pin, 3] = 255
    op = b[..., 3] > 0
    joined = (bare | pin) & op
    return b, {"own": z, "legs": legs & op & ~put, "torso": put & op, "at": (sh, sx), "lost": 0, "drawn_at": (0, 0),
               "head": z, "joined": joined, "kept": z, "shift": sh, "shift_x": sx}


def shifted_frames(frames, shifts, hero):
    """`frame_shift`: each drawn frame's squares moved [rows, cols] in its own rect (a frame drawn off the others' place
    re-registered) - every square kept as drawn; one that would leave the rect stops the tool."""
    if len(shifts) != len(frames):
        sys.exit(f"{hero}: `frame_shift` has {len(shifts)} values for {len(frames)} drawn frames")
    out = []
    for i, ((a, ms), (dy, dx)) in enumerate(zip(frames, shifts)):
        dy, dx = int(dy), int(dx)
        if not (dy or dx):
            out.append((a, ms))
            continue
        H, W = a.shape[:2]
        ys, xs = np.nonzero(a[..., 3] > 0)
        if ys.min() + dy < 0 or ys.max() + dy >= H or xs.min() + dx < 0 or xs.max() + dx >= W:
            sys.exit(f"{hero}: `frame_shift` {dy}, {dx} moves drawn frame {i} off its {W}x{H} rect: grow it (`pad`)")
        b = np.zeros_like(a)
        b[ys + dy, xs + dx] = a[ys, xs]
        out.append((b, ms))
    return out


def make(hero, cfg=None):
    """-> ({"hd_<tag>", "<tag>", "lo_<tag>": [(frame, ms)]}, per-frame info, motion)."""
    import ppu_hd as P
    import ppu_one as O
    cfg = cfg or load(hero)
    hid, pack, ppu, size = T.resolve(hero, T.all_heroes())
    frames, meta = drawn(cfg)
    if cfg.get("frame_shift"):
        frames = shifted_frames(frames, cfg["frame_shift"], hero)
    n = len(frames)
    i0 = cfg["from"]
    src = added(frames[i0][0], cfg)                     # (`add`: pieces the drawing lacks, in frame `from`'s drawing)
    cy0, cx0 = src.shape[0] // 2, src.shape[1] // 2
    head_only = cfg.get("lock") == "head"
    own_only = cfg.get("lock") == "own"                 # (`lock` "own": nothing laid - compose_own)
    layers = {"head": head_of(src, cfg)} if head_only else {} if own_only else pieces(src, cfg, i0)
    props = prop_layers(frames, cfg) if head_only else []
    hchains = head_chain_masks(src, cfg, layers["head"]) if head_only and cfg.get("head_chains") else {}
    # (a `hang` chain's are its rows: it hangs from a root row, every row shifted sideways)
    chain_cols = {c["name"]: sorted(set(np.nonzero(layers[c["name"]])[0 if c.get("hang") else 1].tolist()))
                  for c in cfg.get("chains", [])}
    # `steps`: frames a drawn frame (its legs shown that many frames, the upper body moving on every one), each
    # 1 / `steps` of its time - or `cycle_ms` / the frames
    steps = int(cfg.get("steps", 1))
    N = n * steps
    if len(cfg["bob"]) != N:
        sys.exit(f"{hid}: `bob` has {len(cfg['bob'])} values for {N} frames ({n} drawn x `steps` {steps})")
    mov = motion(cfg, N, chain_cols)
    if hchains:
        # (`head_chains`: each one's columns off the laid head by their share of its `tip`, as `chains` with `tip` are)
        hcols = {nm: sorted(set(np.nonzero(m)[1].tolist())) for nm, m in hchains.items()}
        mov.update({k: v for k, v in motion({"bob": cfg["bob"], "chains": cfg["head_chains"]}, N, hcols).items()
                    if k != "body"})
    tp = T.load_state().get(hid)                         # (a hero thin_outline.json does not list: no pass)
    if tp is not None and tp.get("skip"):
        tp = None

    def thin(f, kind):
        return f if tp is None else T.change_fixed(f, tp[kind], tp["outline"], tp["grow"])[0]
    union = np.zeros(src.shape[:2], bool)
    for name in layer_names(cfg):
        union |= layers[name]
    dense, info, shifts = [], [], {}
    for i in range(N):
        p = i // steps
        a, ms = frames[p]
        a = shade_legs(a, cfg, p)                       # (`shade`: the near leg lighter, the far one darker)
        if cfg.get("cycle_ms"):
            ms = cfg["cycle_ms"] / float(N)
        elif steps > 1:
            ms = ms / float(steps)
        match, alike = None, None
        if own_only:
            b, inf = compose_own(a, i, cfg, p)
        elif head_only:
            b, inf = compose_head(a, i, src, layers["head"], mov, cfg, p, props, hchains)
        else:
            if cfg["below"] == "match":
                if p not in shifts:
                    shifts[p] = drawn_shift(src, a, union, int(cfg.get("match_search", 7)))
                shift, alike = shifts[p]
                match = (src, union, shift)
            b, inf = compose(a, i, src, cy0, cx0, layers, mov, cfg, match, p)
        inf["pose"] = p
        inf["drawn_alike"] = alike
        b2 = thin(b, "hd")
        inf["thinned"] = (b2 != b).any(-1)
        dense.append((b2, ms))
        info.append(inf)
    # the 1x frames from the dense ones (ppu_one), the lo_ ones (ppu_hd.add_lo), on the drawn run's own sizes
    tag = cfg["tag"]
    if meta.get("one_sizes"):
        one_sz, lo_sz = [tuple(v) for v in meta["one_sizes"]], [tuple(v) for v in meta["lo_sizes"]]
    else:
        an, _ = T.read(hid, pack)
        one_sz = [(int(f["data"]["w"]), int(f["data"]["h"])) for f in an[tag]["frames"]]
        lo_sz = [(int(f["data"]["w"]), int(f["data"]["h"])) for f in an["lo_" + tag]["frames"]]
    if len(one_sz) != N:                                 # a drawn frame's sizes on each of its frames
        one_sz, lo_sz = [one_sz[i // steps] for i in range(N)], [lo_sz[i // steps] for i in range(N)]
    k = P.PPU[short(hero)]
    pr, pc = cfg.get("pad", (0, 0))
    if pr or pc:                                     # (grown frames: the lo_ side bounds the 1x side - grown alike)
        gl = lambda v, p_: v + 2 * int(math.ceil(p_ * P.UI_PPU / k))  # noqa: E731
        lo_sz = [(gl(lw, pc), gl(lh, pr)) for lw, lh in lo_sz]
    shown = k / min(1.0, O.sizes().get(short(hero), 1.0))
    one, lost = [], []
    for (b, ms), (w, h), (lw, lh) in zip(dense, one_sz, lo_sz):
        ws = O.lengths(w, k, b.shape[1], lw, False)
        hs = O.lengths(h, k, b.shape[0], lh, False)
        f, off = O.one_frame(b, w, h, 1.0 / shown, ws, hs)
        lost.append(off)
        one.append((f, ms))
    if cfg.get("keep_one"):
        # `keep_one`: the 1x frames stay the drawn run's own, kept beside it (<hero>_run_one.png: the frames left to
        # right, a square apart) - a hero whose 1x run is a drawing of its own, not ppu_one's from the dense frames:
        # remade, every square of it would change; the lo_ frames are made from the dense ones anyway
        s1 = np.array(Image.open(lp(os.path.join(ROOT, cfg["keep_one"] + ".png"))).convert("RGBA"))
        kept1, x1 = [], 0
        for k1, (f, _) in enumerate(one):
            h1, w1 = f.shape[:2]
            if pr or pc or cfg.get("keep_lo"):
                # (with `pad` the made 1x frames grow: the kept ones keep their own sizes, the drawn run's 1x ones -
                # league_camille's added coat tails are in her dense and lo_ frames only; with `keep_lo` - a run kept
                # as drawn at every density, league_malzahar's - too: ppu_one would pick a taller rect for some)
                w1, h1 = one_sz[k1]
            kept1.append(s1[:h1, x1:x1 + w1].copy())
            x1 += w1 + 1
        one = [(f1, ms) for f1, (_, ms) in zip(kept1, one)]
    mini = {tag: one, "hd_" + tag: dense}
    if cfg.get("lo_size") is not None:
        # `lo_size`: the size the lo_ frames are made at in place of the hero's SIZES size (addons/league_main hd.rs, which
        # tools/art/pixel_down.py's sizes_of reads) - league_yuumi: every lo_ tag of hers is her hd_ frames at full size
        # (made before her 0.75 was in that table); add_lo at 1.0 makes her installed lo_run square for square, at 0.75
        # the run alone would come out a quarter smaller than every other lo_ tag of hers
        import pixel_down as D_
        sizes_of = D_.sizes_of
        D_.sizes_of = lambda: dict(sizes_of(), **{short(hero): float(cfg["lo_size"])})
        try:
            P.add_lo(short(hero), mini)
        finally:
            D_.sizes_of = sizes_of
    else:
        P.add_lo(short(hero), mini)
    lo = []
    for (f, ms), (lw, lh) in zip(mini["lo_" + tag], lo_sz):
        f2 = thin(f, "lo")
        if f2.shape[1] < lw or f2.shape[0] < lh:         # on the run's own rect: grown alike at both ends, centre kept
            g = np.zeros((max(lh, f2.shape[0]), max(lw, f2.shape[1]), 4), np.uint8)
            oy, ox = (g.shape[0] - f2.shape[0]) // 2, (g.shape[1] - f2.shape[1]) // 2
            g[oy:oy + f2.shape[0], ox:ox + f2.shape[1]] = f2
            # (thinned again in its rect: a frame whose figure touched its edge gets its outline where it had no room -
            # league_irelia's lo_run frame 7, 94 rows in a 98-row rect; a frame that had the room is as it was)
            f2 = thin(g, "lo")
        lo.append((f2, ms))
    if cfg.get("lo_grow") and tp is not None:
        # `lo_grow`: the lo_ frames' outline measured on them and grown to the hero's thin_outline `keep` where it is
        # thinner (league_poppy: her dense frames keep a 1-square outline, her lo_ tags 2 - add_lo grows her dense
        # frames, PPU 1.2 under the UI's 1.5, and keeps the one square; remade without it, her lo_run would be the only
        # lo_ tag drawn thin)
        oc_ = [tuple(c) for c in tp["outline"]]
        P = T.kind_params([f for f, _ in lo], oc_, tp["lo"]["keep"])
        if T.mode(P) == "grow":
            lo = [(T.change_fixed(f, P, tp["outline"], tp["grow"])[0], ms) for f, ms in lo]
    if cfg.get("keep_lo"):
        # `keep_lo`: the lo_ frames stay the drawn run's own, kept beside it (<hero>_run_lo.png: the frames left to
        # right, a square apart, on the drawn run's lo_ sizes) - a hero whose lo_run is not add_lo's from his dense
        # frames (league_malzahar: 173-195 squares a frame off), so a timing-only run keeps every square of it
        s2 = np.array(Image.open(lp(os.path.join(ROOT, cfg["keep_lo"] + ".png"))).convert("RGBA"))
        kept2, x2 = [], 0
        for (_, ms), (lw, lh) in zip(lo, lo_sz):
            kept2.append((s2[:lh, x2:x2 + lw].copy(), ms))
            x2 += lw + 1
        lo = kept2
    for inf, n_ in zip(info, lost):
        inf["one_lost"] = n_
    off = [inf["lost"] for inf in info]
    if any(off):
        sys.exit(f"{hid}: the laid upper body leaves the dense frames ({off} squares a frame): bob / parts too far")
    return {"hd_" + tag: dense, tag: one, "lo_" + tag: lo}, info, mov


# ------------------------------------------------------------------------------------------------- writing
def place(px, anims, drop, new):
    """The sheet with the tags in `drop` taken off (their squares cleared where no other tag uses them) and `new` put in
    the free room - top-left first, 1 clear square between frames, no wider than the sheet; every other tag's frames
    where they are. -> (sheet, anims)."""
    def rect(f):
        return tuple(int(round(f["data"][q])) for q in ("x", "y", "w", "h"))
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
    out = np.zeros((total_h, Ws, 4), np.uint8)
    out[:px.shape[0]] = px
    anims = dict(anims)
    for tag, fr in new.items():
        rows = []
        for f, ms in fr:
            h, w = f.shape[:2]
            ii = np.pad(np.cumsum(np.cumsum(occ.astype(np.int32), 0), 1), ((1, 0), (1, 0)))
            s_ = ii[h:, w:] - ii[:-h, w:] - ii[h:, :-w] + ii[:-h, :-w]
            free = np.argwhere(s_ == 0)
            if not len(free):
                sys.exit(f"{tag}: no room for a {w}x{h} frame")
            y, x = free[0]
            out[y:y + h, x:x + w] = f
            occ[max(0, y - 1):y + h + 1, max(0, x - 1):x + w + 1] = True
            rows.append({"duration": round(ms / 1000.0, 6),
                         "data": {"x": float(x), "y": float(y), "w": float(w), "h": float(h)}})
        anims[tag] = {"frames": rows}
    used = [rect(f) for a in anims.values() for f in a["frames"]]
    return out[:max(y + h for x, y, w, h in used), :max(x + w for x, y, w, h in used)], anims


def write(hero, new, cfg=None):
    """The tags' frames into the sheet (their own rects when every frame keeps its size and timing; else placed anew,
    the fanim written too) and the dense frames into the strip tools/art/ppu_hd.py reads. -> fanim changed?"""
    cfg = cfg or load(hero)
    hid, pack, ppu, size = T.resolve(hero, T.all_heroes())
    stem = T.stem(hid, pack)
    with open(lp(stem + "#anim.fanim"), encoding="utf-8-sig") as f:
        doc = json.load(f)
    an = doc["anims"]
    px = np.array(Image.open(lp(stem + "#sheet.png")).convert("RGBA"))
    same = all(len(an[t]["frames"]) == len(fr) and all(
        (int(round(r["data"]["w"])), int(round(r["data"]["h"]))) == (a.shape[1], a.shape[0])
        and abs(r["duration"] * 1000 - ms) <= 0.5 for r, (a, ms) in zip(an[t]["frames"], fr)) for t, fr in new.items())
    if same:
        for t, fr in new.items():
            for r, (a, _) in zip(an[t]["frames"], fr):
                x, y, w, h = (int(round(r["data"][q])) for q in ("x", "y", "w", "h"))
                px[y:y + h, x:x + w] = a
    else:
        order = list(an)
        px, anims = place(px, an, tuple(new), new)
        doc["anims"] = {t: anims[t] for t in order}
        with open(lp(stem + "#anim.fanim"), "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
    Image.fromarray(px, "RGBA").save(lp(stem + "#sheet.png"), optimize=True)
    tag = cfg["tag"]
    dense = [a for a, _ in new["hd_" + tag]]
    H = max(a.shape[0] for a in dense)
    s = np.zeros((H, sum(a.shape[1] + 1 for a in dense) - 1, 4), np.uint8)
    x = 0
    for a in dense:
        s[:a.shape[0], x:x + a.shape[1]] = a
        x += a.shape[1] + 1
    Image.fromarray(s, "RGBA").save(lp(os.path.join(T.STRIPS, f"{T.strip_name(hid)}_{tag}.png")), optimize=True)
    side = os.path.join(T.STRIPS, f"{T.strip_name(hid)}_{tag}.json")
    meta = {}
    if os.path.isfile(lp(side)):
        with open(lp(side), encoding="utf-8") as f:
            meta = json.load(f)
    if meta.get("sizes") != [[a.shape[1], a.shape[0]] for a in dense]:
        meta["sizes"] = [[a.shape[1], a.shape[0]] for a in dense]
        with open(lp(side), "w", encoding="utf-8", newline="\n") as f:
            json.dump(meta, f)
    return not same


def check(hero):
    """-> problems (the sheet's run tags and the strip against what the tool makes)."""
    cfg = load(hero)
    new, _, _ = make(hero, cfg)
    hid, pack, _, _ = T.resolve(hero, T.all_heroes())
    an, px = T.read(hid, pack)
    bad = []
    for t, fr in new.items():
        if len(an[t]["frames"]) != len(fr):
            bad.append(t)
            continue
        for f, (b, ms) in zip(an[t]["frames"], fr):
            x, y, w, h = (int(round(f["data"][q])) for q in ("x", "y", "w", "h"))
            if (w, h) != (b.shape[1], b.shape[0]) or not np.array_equal(px[y:y + h, x:x + w], b):
                bad.append(t)
                break
    tag = cfg["tag"]
    strip = np.array(Image.open(lp(os.path.join(T.STRIPS, f"{T.strip_name(hid)}_{tag}.png"))).convert("RGBA"))
    x = 0
    for b, _ in new["hd_" + tag]:
        if not np.array_equal(strip[:b.shape[0], x:x + b.shape[1]], b):
            bad.append(f"assets/source/ppu/{T.strip_name(hid)}_{tag}.png")
            break
        x += b.shape[1] + 1
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--init", metavar="HERO")
    ap.add_argument("--drawn-from", metavar="REV", help="--init: the drawn run from the sheet at this git revision")
    ap.add_argument("--force", action="store_true", help="--init: write the data file again")
    ap.add_argument("--batch", nargs="+", metavar="HERO")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "run_body"))
    ap.add_argument("--variants", help="--batch: the data's variants side by side, 'name:label,...' (base: none)")
    ap.add_argument("--installed", help="--batch --variants: the checkout the game was installed from (its run first)")
    ap.add_argument("--variant", help="--dry: this variant (base: none) instead of `use`'s")
    a = ap.parse_args()
    if a.init:
        import run_body_init as I
        I.init(a.init, rev=a.drawn_from, force=a.force)
        return
    if a.batch:
        import run_body_review as V
        if a.variants:
            V.variants(a.batch, a.out, [tuple(x.split(":", 1)) for x in a.variants.split(",")], a.installed)
        else:
            V.batch(a.batch, a.out)
        return
    if a.check and not a.hero:
        bad = []
        for h in heroes_with_data():
            p = check(h)
            print(f"{'ok' if not p else 'FAIL'}: {h}" + (f" - {', '.join(p)}" if p else ""))
            bad += p
        sys.exit(1 if bad else 0)
    if not a.hero:
        ap.error("--hero, --check, --init or --batch")
    if a.check:
        p = check(a.hero)
        if p:
            sys.exit(f"{a.hero}: {', '.join(p)} not as tools/art/run_body_anim.py makes them")
        print(f"ok: {a.hero} run tags as made")
        return
    new, info, _ = make(a.hero, load(a.hero, a.variant) if a.variant else None)
    if a.dry:
        hid, pack, _, _ = T.resolve(a.hero, T.all_heroes())
        an, _ = T.read(hid, pack)
        for t, fr in new.items():
            print(t, [f"{b.shape[1]}x{b.shape[0]}" + ("" if t in an and i < len(an[t]["frames"]) and
                                                    (int(an[t]["frames"][i]["data"]["w"]),
                                                     int(an[t]["frames"][i]["data"]["h"])) == (b.shape[1], b.shape[0])
                                                    else " (sheet differs)") for i, (b, _) in enumerate(fr)])
        print("1x squares off the rect:", [inf["one_lost"] for inf in info],
              "| dense squares off the frame:", [inf["lost"] for inf in info])
        return
    changed = write(a.hero, new)
    print(f"{a.hero}: {', '.join(new)} written ({len(next(iter(new.values())))} frames)"
          + (" - NEW RECTS: the fanim changed, build league.dll again" if changed else ""))


if __name__ == "__main__":
    main()
