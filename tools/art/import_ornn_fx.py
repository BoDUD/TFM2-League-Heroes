#!/usr/bin/env python3
"""Import Ornn's effects (assets/source/ornn/PROMPTS_FX.md, 18 pictures) as the game sheets league_ornn_fx and
league_ornn_big.

    python tools/art/import_ornn_fx.py [--src DIR] [--review out.png]

The source is Codex's step-3 delivery (assets/source/ornn/codex_fx/ornn_fx: pixel_1x/ornn_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255) - import_graves_fx.py's way:
each frame cut by the manifest's frame size, checked for its symmetry (the projectiles q_fissure and r_ram drawn going
right and symmetric top to bottom; the breath w_fire going right - no check; every other picture symmetric left to
right: the client never mirrors an effect picture) and placed as the kit plays it: spots are game px from the pivot
(x forward, y down); a unit's soles are 11 under it, a point's ground too. Times follow tools/kit/build_ornn.py:
  * the pillar: q_rise lasts q_stamp ticks (its last frame the standing pillar), then q_pillar is stamped every q_stamp
    ticks while the pillar stands, so one play of q_pillar lasts q_stamp ticks too;
  * the projectiles (q_fissure, r_ram and r_ram2 - the headbutt's ram, the same picture) and the buffs (brittle, w_shown)
    loop; the rest play once;
  * the ram's three pictures (r_ram, r_rise, r_hit) are 1.5 times Codex's (the user, 2026-10-21: 「R的羊的效果范围和效果
    都要做大点」, then 「不重新生成 你在那个特效的基础上改」): Scale3x, then each 2x2 block of it one square (the colour most of
    it has), the symmetry made again from its source half - one square is still one game px, the curves stay clean
    (a plain 1.5x nearest makes lines one and two squares wide by turns);
  * three slips of the readback mended (STRAY, SETTLE, SHIFT): a solid line across the top of r_rise's frames 4 and 5
    (a cell border of the raw sheet), q_rise's frame 3 standing 3 rows over the ground over a 2-square speck, w_fire's
    frame 6 drawn 4 rows lower than the other five (its root under his mouth, a spark alone at the top: moved up);
  * w_fire is no view of the kit: tools/art/rig_ornn.py draws it into his breath frames (the client mirrors his frames,
    never an effect picture), its mouth (the cell's left edge, middle row) on the frame's centre.
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
from build_ornn import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ornn", "codex_fx", "ornn_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


# the kit's sheets (build_ornn.py views): everything on the ground or round him is big
BIG = {"w_fire", "q_slam", "q_fissure", "q_rise", "q_pillar", "e_quake", "r_call", "r_rise", "r_ram", "r_ram2", "r_butt"}
FLYING = {"q_fissure", "r_ram"}     # turned with their flight: drawn going right, symmetric top to bottom
BAKED = {"w_fire"}                  # drawn into his own frames by rig_ornn.py (going right)
HIT = (0, -14)                      # a hit on the upper body of a 34-46 px unit
HEAD = (0, -31)                     # over the head of a 40 px unit (Brittle's mark)
SOLES = (0, 11)                     # on the ground under a unit or a point
FLIGHT = (0, 0)                     # a projectile's own point
MOUTH = (0, 0)                      # the breath: its mouth (the cell's left edge) on the frame's centre
BUTT = (0, -18)                     # the headbutt's flash on his chest (it cannot sit ahead of him: never mirrored)
MS = 1000 / 60
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def spread(n, total, w=None):
    """n frames over total ms, weighted by w (the last ones longer); whole ms adding up to total."""
    w = w or [1] * n
    cuts = [round(total * sum(w[:k]) / sum(w)) for k in range(n + 1)]
    return seq(range(n), [b - a for a, b in zip(cuts, cuts[1:])])


STAMP_MS = P["q_stamp"] * MS          # q_rise and one play of q_pillar: one stamp's ticks
# effect -> (anchor: "core", "mouth" or ("feet", rows above the cell's bottom row on the ground), frames with ms, spots)
FX = {
    # the attack: the hammer's hit, Brittle broken, Brittle's mark (a buff, looped)
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "br_pop": ("core", seq(range(5), [40, 60, 70, 80, 90]), [HIT]),
    "brittle": ("core", loop(4, 130), [HEAD]),
    # W Bellows Breath: the fire (baked), each pulse's hit, the shield round him (a buff, looped)
    "w_fire": ("mouth", loop(6, 75), [MOUTH]),
    "w_hit": ("core", seq(range(3), [40, 60, 70]), [HIT]),
    "w_shown": (("feet", 2), loop(4, 110), [SOLES]),
    # Q Volcanic Rupture: the fist's slam under him, the fissure's head (looped), its hit, the pillar rising and standing
    "q_slam": (("feet", 3), seq(range(5), [50, 60, 70, 80, 100]), [SOLES]),
    "q_fissure": ("core", loop(3, 60), [FLIGHT]),
    "q_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "q_rise": (("feet", 1), spread(6, STAMP_MS, [1, 1, 1, 1, 1.2, 1.2]), [SOLES]),
    "q_pillar": (("feet", 1), spread(2, STAMP_MS), [SOLES]),
    # E Searing Charge: the quake round him (the pillar broken), the contact's hit
    "e_quake": (("feet", 4), seq(range(6), [50, 60, 70, 90, 110, 140]), [SOLES]),
    "e_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    # R Call of the Forge God: the call under him, the ram bursting up far away, the ram (looped, both ways), the
    # headbutt's flash, a ram's hit
    "r_call": (("feet", 3), seq(range(6), [60, 80, 100, 110, 120, 130]), [SOLES]),
    "r_rise": (("feet", 1), seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    "r_ram": ("core", loop(4, 70), [FLIGHT]),
    "r_ram2": ("core", loop(4, 70), [FLIGHT]),
    "r_butt": ("core", seq(range(4), [50, 60, 70, 90]), [BUTT]),
    "r_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
}
# tags drawn from another effect's cells
ALIAS = {"r_ram2": "r_ram"}
BIGGER = {"r_ram", "r_rise", "r_hit"}                  # drawn 1.5 times bigger (up15)
STRAY = {("r_rise", 3): (2, 3), ("r_rise", 4): (2, 3)}  # (picture, frame) -> rows cleared
SETTLE = {("q_rise", 2): 41}                            # (picture, frame) -> rows from here down cleared, then set down
SHIFT = {("w_fire", 5): -4}                             # (picture, frame) -> rows moved (what leaves the cell is dropped)


def pack(a):
    a = a.astype(np.uint32)
    return (a[..., 0] << 24) | (a[..., 1] << 16) | (a[..., 2] << 8) | a[..., 3]


def unpack(p):
    return np.stack([(p >> 24) & 255, (p >> 16) & 255, (p >> 8) & 255, p & 255], -1).astype(np.uint8)


def scale3x(p):
    """Scale3x (AdvMAME3x) of packed colours: each square three by three, a corner or an edge taking a neighbour's
    colour where two neighbours meet on a diagonal."""
    q = np.pad(p, 1)
    A, B, C = q[:-2, :-2], q[:-2, 1:-1], q[:-2, 2:]
    D, E, F = q[1:-1, :-2], q[1:-1, 1:-1], q[1:-1, 2:]
    G_, H, I = q[2:, :-2], q[2:, 1:-1], q[2:, 2:]
    c1 = (D == B) & (D != H) & (B != F)
    c2 = (B == F) & (B != D) & (F != H)
    c3 = (D == H) & (D != B) & (H != F)
    c4 = (H == F) & (H != D) & (F != B)
    e = [np.where(c1, D, E), np.where((c1 & (E != C)) | (c2 & (E != A)), B, E), np.where(c2, F, E),
         np.where((c1 & (E != G_)) | (c3 & (E != A)), D, E), E, np.where((c2 & (E != I)) | (c4 & (E != C)), F, E),
         np.where(c3, D, E), np.where((c3 & (E != I)) | (c4 & (E != G_)), H, E), np.where(c4, F, E)]
    out = np.zeros((p.shape[0] * 3, p.shape[1] * 3), np.uint32)
    for k in range(9):
        out[k // 3::3, k % 3::3] = e[k]
    return out


def up15(cell, flying):
    """The picture 1.5 times bigger: Scale3x, each 2x2 block one square - the colour most of the block has (a tie: the
    square a plain 1.5x nearest puts there if it is one of them) - and the symmetry made again from the top half
    (a projectile) or the left half (the others: the middle column of an odd width is its own mirror)."""
    h, w = cell.shape[:2]
    H, W = h * 3 // 2, w * 3 // 2
    big = scale3x(pack(cell))[:H * 2, :W * 2].reshape(H, 2, W, 2).transpose(0, 2, 1, 3).reshape(H, W, 4)
    yy = np.minimum(((np.arange(H) + 0.5) / 1.5).astype(int), h - 1)
    xx = np.minimum(((np.arange(W) + 0.5) / 1.5).astype(int), w - 1)
    near = pack(cell)[yy][:, xx]
    out = np.zeros((H, W), np.uint32)
    for y in range(H):
        for x in range(W):
            vals, cnt = np.unique(big[y, x], return_counts=True)
            top = vals[cnt == cnt.max()]
            out[y, x] = near[y, x] if near[y, x] in top else top[0]
    if flying:
        out[H - H // 2:] = out[:H // 2][::-1]
    else:
        out[:, W - W // 2:] = out[:, :W // 2][:, ::-1]
    return unpack(out)


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        if (name, k) in STRAY:
            r0, r1 = STRAY[name, k]
            c[r0:r1] = 0
        if (name, k) in SHIFT:
            dy = SHIFT[name, k]
            moved = np.zeros_like(c)
            if dy < 0:
                moved[:dy] = c[-dy:]
            else:
                moved[dy:] = c[:h - dy]
            out[k] = c = moved
        if (name, k) in SETTLE:
            c[SETTLE[name, k]:] = 0
            ys = np.nonzero(c[..., 3].any(1))[0]
            out[k] = c = np.roll(c, h - 1 - ys.max(), axis=0)
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
        if name in BAKED:
            continue
        how, mirror = ("top to bottom", c[::-1]) if name in FLYING else ("left to right", c[:, ::-1])
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {how}")
    if name in BIGGER:
        out = [up15(c, name in FLYING) for c in out]
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "mouth":
        return [-0.5, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def manifest(src):
    """{name: entry} from Codex's manifest.json ("effects" / "entries" / "assets", each with "name" or "id", maybe
    prefixed ornn_fx_), with the 1x sheet's path relative to src."""
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    rows = man.get("effects") or man.get("entries") or man.get("assets") or []
    meta = {}
    for e in rows:
        name = (e.get("name") or e.get("id")).replace("ornn_fx_", "").replace(".png", "")
        meta[name] = dict(e, pixel_1x=e.get("pixel_file") or os.path.join("pixel_1x", e["file"]))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC, help="Codex's delivery (the folder holding manifest.json and pixel_1x/)")
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    for tag in ("q_rise", "q_pillar"):
        ms = sum(m for _, m in FX[tag][1])
        if abs(ms - STAMP_MS) > 1:
            sys.exit(f"{tag} plays {ms} ms, one stamp is {P['q_stamp']} ticks ({STAMP_MS:.0f} ms)")
    meta = manifest(a.src)
    if set(meta) != set(FX) - set(ALIAS):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(set(FX) - set(ALIAS))}")
    allc = {n: cells(n, meta[n], a.src) for n in FX if n not in ALIAS}
    allc.update({n: allc[src] for n, src in ALIAS.items()})
    # the pillar rises into the standing one: q_rise's last frame is q_pillar's first (PROMPTS_FX.md)
    if not (allc["q_rise"][-1] == allc["q_pillar"][0]).all():
        print("note: q_rise's last frame differs from q_pillar's first", file=sys.stderr)
    tables = {"league_ornn_fx": {}, "league_ornn_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{name}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_ornn_big" if name in BIG else "league_ornn_fx"][name] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name, cs in allc.items():
            if name in ALIAS:
                continue
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
