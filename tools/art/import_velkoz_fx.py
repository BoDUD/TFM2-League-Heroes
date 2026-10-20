#!/usr/bin/env python3
"""Import Vel'Koz's effects (assets/source/velkoz/PROMPTS_FX.md, 17 pictures) as the game sheets league_velkoz_fx and
league_velkoz_big.

    python tools/art/import_velkoz_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/velkoz/codex_fx/velkoz_fx: pixel_1x/velkoz_fx_<name>.png, one row
of equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; the projectiles and lines
symmetric top to bottom, q_split both ways, the rest left to right - checked again here). Each frame is cut by the
manifest's frame size and placed as the kit plays it (import_zyra_fx.py's way): spots are game px from the pivot (x
forward, y down); a unit's soles are 11 under it, a point's ground too. Times from the kit (build_velkoz.P, 60 ticks a
second):
  * a_bolt / q_bolt: hidden their first 2 ticks (they leave his pivot, 7 px behind his eye: league_malzahar's link),
    then looped over twice their straight flight;
  * w_rift (the rift line's own picture: drawn at the line's middle, turned with it): its burst frame (6) on the
    detonation's tick w_det, the whole picture w_life ticks;
  * e_mark: the crack telegraph, played on the landing point while E's hidden lob flies (e_delay ticks), the eruption
    e_boom from the landing;
  * r_beam: built from Codex's four-frame beam strip, league_lucian Q's standing beam - each wave's homing projectile
    leaves his pivot lifted to his eye and creeps toward the champion 1 px a tick (r_bspeed), so its picture is one frame
    a tick: an empty first tick (its first move points it straight up), then r_p frames with the beam's flare held on his
    eye (BEAM_AHEAD px ahead of the pivot: each frame drawn 1 px further back than the last), then empty for the rest
    of its creep - the next wave's beam takes over on the next tick.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from build_velkoz import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "velkoz", "codex_fx", "velkoz_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"a_bolt", "q_bolt", "w_rift", "r_beam"}   # turned with their flight / direction: drawn going right
BOTH = {"q_split"}                               # the split's two bolts, up and down: symmetric both ways
BIG = {"q_split", "w_rift", "e_mark", "e_boom", "r_beam"}
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
HEAD = (0, -30)                 # over the head of a 36 px unit (the research mark)
SOLES = (0, 11)                 # on the ground under a unit or a point
SPLIT = (0, -6)                 # where Q's bolt stops on the unit it struck (it falls from his eye onto the pivot)
BEAM_AHEAD = 7                  # px from his pivot to his big eye along the beam (rig_velkoz: the eye 11 squares ahead)
BEAM_FLARE = 6                  # the beam strip's flare middle, px from the cell's left edge (the prompt)
seq = J.seq
flight = J.flight
MS = 1000 / 60
BOLT_MS = P["atk_range"] / P["a_speed"] * MS * 2                    # the homing bolt (twice its straight flight)
Q_MS = P["q_len"] / P["q_speed"] * MS                               # Plasma Fission's line, to its end


def loop(n, ms):
    return seq(range(n), [ms] * n)


def rift():
    """w_rift's 10 frames: the crack opening and glowing (frames 1-5) until the detonation's tick w_det, the burst
    (frame 6) on it, the spray and the fragments to the line's end of life w_life."""
    before = P["w_det"] * MS
    after = (P["w_life"] - P["w_det"]) * MS
    return seq(range(10), [before / 5] * 5 + [after / 5] * 5)


def telegraph():
    """e_mark's 6 frames over E's hidden lob (e_delay ticks): the cracks spreading, the last and brightest the longest."""
    total = P["e_delay"] * MS
    w = [1, 1, 1, 1, 1.2, 1.5]
    return seq(range(6), [total * k / sum(w) for k in w])


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom row), frames with ms, spots)
FX = {
    "a_bolt": ("core", flight(4, 60, BOLT_MS, lead=2), [(0, 0)]),
    "a_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "q_bolt": ("core", flight(4, 60, Q_MS * 1.2, lead=2), [(0, 0)]),
    "q_hit": ("core", seq(range(5), [40, 60, 70, 80, 90]), [HIT]),
    "q_split": ("core", seq(range(6), [50, 50, 50, 60, 70, 80]), [SPLIT]),
    "q_split_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "q_slow": (("feet", 3), loop(4, 110), [SOLES]),
    "w_rift": ("core", rift(), [(0, 0)]),
    "w_hit": ("core", seq(range(3), [40, 60, 70]), [HIT]),
    "e_mark": ("core", telegraph(), [SOLES]),
    "e_boom": (("feet", 4), seq(range(7), [50, 60, 80, 90, 100, 110, 120]), [SOLES]),
    "e_hit": ("core", seq(range(3), [40, 60, 70]), [HIT]),
    "r_beam": ("beam", None, None),                 # beam_tag
    "r_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "p_s1": ("core", seq(range(4), [60, 160, 160, 120]), [HEAD]),
    "p_s2": ("core", seq(range(4), [60, 160, 160, 120]), [HEAD]),
    "p_full": ("core", seq(range(6), [50, 60, 70, 80, 90, 100]), [HIT]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
        mirrors = [c[::-1]] if name in TB else [c[:, ::-1], c[::-1]] if name in BOTH else [c[:, ::-1]]
        for mirror in mirrors:
            off = int(((c != mirror).any(axis=2) & ((c[..., 3] > 0) | (mirror[..., 3] > 0))).sum())
            if off:
                sys.exit(f"{name} frame {k + 1} is not symmetric "
                         f"{'top to bottom' if name in TB else 'both ways' if name in BOTH else 'left to right'} ({off} squares)")
    return out


def beam_tag(cs):
    """r_beam: an empty tick, r_p frames each the beam strip's frame (t % 4) with its flare on his eye - BEAM_AHEAD - t px
    from the projectile (it creeps 1 px a tick toward the target), then empty for the rest of the creep."""
    h, w = cs[0].shape[:2]
    period = P["r_p"]
    reach = BEAM_AHEAD + w - BEAM_FLARE                 # the farthest pixel from the projectile on the first frame
    W = 2 * (reach + 2) + 1
    cx, cy = W // 2, h // 2
    out = [(np.zeros((3, 3, 4), np.uint8), MS)]
    for t in range(1, period + 1):
        canvas = np.zeros((h, W, 4), np.uint8)
        left = cx + BEAM_AHEAD - t - BEAM_FLARE          # the strip's left edge
        c = cs[t % len(cs)]
        x0, x1 = max(0, left), min(W, left + w)
        sub = c[:, x0 - left:x1 - left]
        m = sub[..., 3] > 0
        canvas[:, x0:x1][m] = sub[m]
        assert cy == (h - 1) // 2 or h % 2 == 0
        out.append((canvas, MS))
    out.append((np.zeros((3, 3, 4), np.uint8), 4000))
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def read_manifest():
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    items = man.get("effects") or man.get("assets") or man.get("entries") or man.get("files") or man
    if isinstance(items, dict):
        items = [dict(v, name=k) for k, v in items.items()]
    for e in items:
        name = e.get("name") or e.get("id") or e["file"][len("velkoz_fx_"):-len(".png")]
        name = name.replace("velkoz_fx_", "")
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", e.get("file", f"velkoz_fx_{name}.png")))
        meta[name].setdefault("cell_1x", e.get("cell") or e.get("cell_size"))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = read_manifest()
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_velkoz_fx": {}, "league_velkoz_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        if kind == "beam":
            out = [(c if c.shape[0] > 3 else c, ms) for c, ms in beam_tag(cs)]
        else:
            anc = anchor(cs[0], kind)
            out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_velkoz_big" if name in BIG else "league_velkoz_fx"][name] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name, cs in allc.items():
            W = sum(c.shape[1] + 2 for c in cs)
            H = max(c.shape[0] for c in cs)
            img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
            x = 0
            for c in cs:
                img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                    (x * Z, (H - c.shape[0]) * Z))
                x += c.shape[1] + 2
            rows.append((name, img))
        W = max(r.width for _, r in rows) + 120
        Ht = sum(r.height + 10 for _, r in rows)
        sheet = Image.new("RGB", (W, Ht), (20, 20, 26))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.paste(r.convert("RGB"), (120, y))
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += r.height + 10
        sheet.save(lp(a.review))
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
