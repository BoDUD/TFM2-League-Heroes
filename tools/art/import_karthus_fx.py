#!/usr/bin/env python3
"""Import Karthus's effects (assets/source/karthus/PROMPTS_FX.md, 14 pictures) as the game sheets league_karthus_fx and
league_karthus_big.

    python tools/art/import_karthus_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/karthus/codex_fx/karthus_fx: pixel_1x/karthus_fx_<name>.png, one row
of equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; the bolt drawn pointing right
and symmetric top to bottom, every other picture symmetric left to right - checked again here). Each frame is cut by
the manifest's frame size and placed as the kit plays it (import_chogath_fx.py's way): spots are game px from the pivot
(x forward, y down); a unit's soles are 11 under it (his 11.5), a point's ground too. Times follow
tools/kit/build_karthus.py: Lay Waste's mark lasts the lob's flight (q_delay), the wall its zone (w_t: frames 3-6
looped), Requiem's souls the channel (r_ch: looped); the buffs loop (e_on, w_slow, w_shred, p_spirit) and the bolt too;
the rest play once.
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
from build_karthus import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "karthus", "codex_fx", "karthus_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"q_mark", "q_boom", "e_on", "w_wall", "r_cast", "r_hit", "p_spirit"}
FLYING = {"a_bolt"}             # turned with its flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -31)             # over a unit's head (the mark 38-46 px over its soles)
FLIGHT = (0, 0)                 # a projectile's own point
# Requiem's souls round him as he hovers: his body (the staff left out) spans 19 px behind his standing point to 8 in
# front and 9-55 px over the ground in the ult's hover frames (its middle 5 back and 32 up); the oval's middle in its
# cell is 36 up, so the cell goes 5 back and 4 down (the user, 2026-10-20: 「这个盾没对齐啊」 - centred on his standing
# point it covered his staff and left his claw and book outside)
R_CAST = (-5, 15)
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def ticks_ms(t):
    return t * 1000 / 60


def spread(n, total):
    """n frames together lasting `total` ms (whole ms, the remainder on the first ones)."""
    base, extra = divmod(int(round(total)), n)
    return [base + (1 if k < extra else 0) for k in range(n)]


def wall_frames():
    """The wall's 8 frames over its zone's w_t ticks: rising (1, 2), frames 3-6 looped, fading (7, 8)."""
    total = ticks_ms(P["w_t"])
    rise, fade, step = [100, 100], [150, 150], 125
    loops = int((total - sum(rise) - sum(fade)) // (4 * step))
    left = total - sum(rise) - sum(fade) - loops * 4 * step
    fade = [fade[0] + left / 2, fade[1] + left / 2]
    ks = [0, 1] + [2, 3, 4, 5] * loops + [6, 7]
    ms = rise + [step] * (4 * loops) + fade
    return list(zip(ks, ms))


def channel_frames():
    """Requiem's souls looped over the channel (r_ch ticks): 6 frames of 125 ms."""
    total = ticks_ms(P["r_ch"])
    n = int(round(total / 750))
    ks = list(range(6)) * n
    return list(zip(ks, spread(len(ks), total)))


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # the attack's bolt (a homing projectile's picture, looped) and its hit
    "a_bolt": ("core", loop(4, 70), [FLIGHT]),
    "a_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    # Lay Waste: the mark on the landing point the whole flight (q_delay), the blast, the hit, the doubled hit
    "q_mark": (("feet", 7), list(zip(range(6), spread(6, ticks_ms(P["q_delay"])))), [SOLES]),
    "q_boom": (("feet", 7), seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    "q_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "q_lone": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    # Defile: the vortex under him (a buff, looped) and the burn on each enemy
    "e_on": (("feet", 9), loop(4, 120), [SOLES]),
    "e_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    # Wall of Pain: the wall on the point (its zone's w_t), the slow and the shred (buffs, looped)
    "w_wall": ("core", wall_frames(), [SOLES]),
    "w_slow": (("feet", 1), loop(2, 150), [SOLES]),
    "w_shred": ("core", loop(2, 150), [OVERHEAD]),
    # Requiem: the souls round him for the channel (r_ch), the beam on each enemy champion
    "r_cast": (("feet", 0), channel_frames(), [R_CAST]),
    "r_hit": (("feet", 0), seq(range(6), [60, 70, 80, 90, 100, 100]), [SOLES]),
    # the add-on's Death Defied: the spirit's glow (a buff, looped)
    "p_spirit": (("feet", 0), loop(4, 150), [SOLES]),
}
# made here from a delivered picture: Requiem's mark on every enemy champion while the channel holds (a buff's picture,
# looped; the user 2026-11-01: 「卡尔萨斯放大时候敌方英雄身上也没特效」) - the thin beam of r_hit's first frame, and every
# other row of it, so it flickers where the strike will land
DERIVED = {"r_mark": ("r_hit", ("feet", 0), [SOLES])}
BIG.add("r_mark")
# the pictures that must last as long as something in the kit: tag -> ticks
LASTS = {"q_mark": P["q_delay"], "w_wall": P["w_t"], "r_cast": P["r_ch"]}


def dashed(c):
    """Every other drawn row of a cell, the rest cleared."""
    out = c.copy()
    out[1::2] = 0
    return out
STRAY = {}


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for (nm, k), (r0, r1) in STRAY.items():
        if nm == name:
            out[k][r0:r1] = 0
    for k, c in enumerate(out):
        mirror = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def manifest(src):
    """{name: entry} from Codex's manifest.json, whichever way it lists them ("entries" / "effects" / "assets", each
    with "id" or "name", maybe prefixed karthus_fx_), with the 1x sheet's path relative to src."""
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    rows = man.get("entries") or man.get("effects") or man.get("assets") or []
    meta = {}
    for e in rows:
        name = (e.get("id") or e.get("name")).replace("karthus_fx_", "").replace(".png", "")
        meta[name] = dict(e, pixel_1x=e.get("pixel_1x") or os.path.join("pixel_1x", e["file"]))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC, help="Codex's delivery (the folder holding manifest.json and pixel_1x/)")
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    for tag, t in LASTS.items():
        ms = sum(m for _, m in FX[tag][1])
        if abs(ms - ticks_ms(t)) > 1:
            sys.exit(f"{tag} plays {ms} ms, the kit holds it {t} ticks ({ticks_ms(t):.0f} ms)")
    meta = manifest(a.src)
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n], a.src) for n in FX}
    tables = {"league_karthus_fx": {}, "league_karthus_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{name}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_karthus_big" if name in BIG else "league_karthus_fx"][name] = out
    for name, (src, kind, spots) in DERIVED.items():
        beam = allc[src][0]
        anc = anchor(beam, kind)
        tables["league_karthus_big"][name] = [(J.place(c, anc, spots), 90) for c in (beam, dashed(beam))]
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
