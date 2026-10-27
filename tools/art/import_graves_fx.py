#!/usr/bin/env python3
"""Import Graves's effects (assets/source/graves/PROMPTS_FX.md, 16 pictures) as the game sheets league_graves_fx and
league_graves_big.

    python tools/art/import_graves_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/graves/codex_fx/graves_fx: pixel_1x/graves_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255) - import_karthus_fx.py's way:
each frame cut by the manifest's frame size, checked for its symmetry (the projectiles a_shot, q_shell, r_shell drawn
pointing right and symmetric top to bottom; the canister w_can both ways; the three muzzle blasts a_flash, q_flash,
r_flash pointing right - no check; every other picture symmetric left to right) and placed as the kit plays it: spots
are game px from the pivot (x forward, y down); a unit's soles are 11 under it (his 11.5), a point's ground too. Times
follow tools/kit/build_graves.py: Q's bomb waits the fuse (q_fuse) on its first five frames and blows up on the sixth,
the smoke lasts its cloud (w_cloud: frames 3-7 looped); the buffs loop (e_grit, w_slow) and the projectiles too; the
rest play once. The muzzle blasts go into league_graves_fx as tags with their muzzle (the cell's left edge, middle
row) on the frame's centre: tools/art/rig_graves.py lays them on his shot frames (the kit binds no view to them).
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
from build_graves import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "graves", "codex_fx", "graves_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"q_blast", "q_blast_w", "w_smoke", "r_blast"}
FLYING = {"a_shot", "q_shell", "r_shell"}       # turned with their flight: drawn going right, symmetric top to bottom
BOTH = {"w_can"}                                # a tumbling canister: symmetric both ways
BAKED = {"a_flash", "q_flash", "r_flash"}       # drawn into his own frames by rig_graves.py (pointing right)
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
FLIGHT = (0, 0)                 # a projectile's own point
MUZZLE = (0, 0)                 # a muzzle blast: its muzzle (the cell's left edge) on the frame's centre
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def ticks_ms(t):
    return t * 1000 / 60


def spread(n, total):
    """n frames together lasting `total` ms (whole ms, the remainder on the first ones)."""
    base, extra = divmod(int(round(total)), n)
    return [base + (1 if k < extra else 0) for k in range(n)]


def bomb_frames():
    """Q's bomb: frames 1-5 over the fuse (q_fuse ticks: its red light blinking), the blast from frame 6 on."""
    return list(zip(range(5), spread(5, ticks_ms(P["q_fuse"])))) + list(zip(range(5, 9), [60, 90, 120, 150]))


def smoke_frames():
    """The smoke screen's 8 frames over its cloud's w_cloud ticks: the burst (1, 2), frames 3-7 looped, thinning (8)."""
    total = ticks_ms(P["w_cloud"])
    rise, fade, step = [120, 150], [300], 180
    loops = int((total - sum(rise) - sum(fade)) // (5 * step))
    left = total - sum(rise) - sum(fade) - loops * 5 * step
    fade = [fade[0] + left]
    ks = [0, 1] + [2, 3, 4, 5, 6] * loops + [7]
    ms = rise + [step] * (5 * loops) + fade
    return list(zip(ks, ms))


# effect -> (anchor: "core", "muzzle" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # the shotgun: its muzzle blast (baked), the pellet (a homing projectile's picture, looped) and its hit
    "a_flash": ("muzzle", seq(range(3), [40, 50, 60]), [MUZZLE]),
    "a_shot": ("core", loop(2, 60), [FLIGHT]),
    "a_hit": ("core", seq(range(3), [40, 50, 60]), [HIT]),
    # End of the Line: the cannon blast (baked), the shell, its hit, the bomb waiting and blowing up
    "q_flash": ("muzzle", seq(range(4), [40, 50, 60, 70]), [MUZZLE]),
    "q_shell": ("core", loop(2, 60), [FLIGHT]),
    "q_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "q_blast": (("feet", 1), bomb_frames(), [SOLES]),      # the cells are cropped to the drawing: the bomb on the ground
    # the add-on's bomb stopped by a wall (addons/league_graves shell.rs): its light once for q_wall, then the blast
    "q_blast_w": (("feet", 1), list(zip(range(1), [round(ticks_ms(P["q_wall"]))])) + list(zip(range(5, 9), [60, 90, 120, 150])),
                  [SOLES]),
    # Smoke Screen: the canister (a lob's picture, looped), the cloud on the point (w_cloud), the slowed (a buff)
    "w_can": ("core", loop(2, 70), [FLIGHT]),
    "w_smoke": (("feet", 0), smoke_frames(), [SOLES]),
    "w_slow": (("feet", 0), loop(2, 150), [SOLES]),
    # Quickdraw: the dust where he set off, True Grit's ring (a buff, looped)
    "e_dust": (("feet", 0), seq(range(4), [60, 70, 80, 90]), [SOLES]),
    "e_grit": (("feet", 4), loop(2, 200), [SOLES]),
    # Collateral Damage: the muzzle blast (baked), the shell, the hit on the champion, the blast round him
    "r_flash": ("muzzle", seq(range(4), [40, 50, 60, 70]), [MUZZLE]),
    "r_shell": ("core", loop(2, 60), [FLIGHT]),
    "r_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "r_blast": (("feet", 2), seq(range(5), [60, 80, 100, 120, 140]), [SOLES]),
}
# tags drawn from another effect's cells
ALIAS = {"q_blast_w": "q_blast"}
# the pictures that must last as long as something in the kit: tag -> (frames counted, ticks)
LASTS = {"q_blast": (5, P["q_fuse"]), "w_smoke": (None, P["w_cloud"])}
STRAY = {}
# cells whose embers are put out (0-based): the bomb's sparks fly out with the fireball (cell 6) and are gone in the
# smoke - cell 7 had a few back between the pillars, at the sides and in the smoke (the user, 2026-10-27: 「男枪Q的特效
# 好像有点问题？最后爆的那一下 火星乱弹」)
EMBERS_OUT = {("q_blast", 7)}


def warm(p):
    return int(p[0]) > int(p[1]) + 40


def put_out(c):
    """The warm pixels (red over green by 40) of a cell: one with 3 or 4 opaque cool neighbours takes their commonest
    colour (an ember in the smoke), the others are cleared."""
    h, w = c.shape[:2]
    out = c.copy()
    for y in range(h):
        for x in range(w):
            if not c[y, x, 3] or not warm(c[y, x]):
                continue
            near = [tuple(c[v, u]) for v, u in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                    if 0 <= v < h and 0 <= u < w and c[v, u, 3] and not warm(c[v, u])]
            out[y, x] = max(set(near), key=near.count) if len(near) >= 3 else 0
    return out


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
    for nm, k in EMBERS_OUT:
        if nm == name:
            out[k] = put_out(out[k])
    for k, c in enumerate(out):
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
        if name in BAKED:
            continue
        checks = [("top to bottom", c[::-1])] if name in FLYING else [("left to right", c[:, ::-1])]
        if name in BOTH:
            checks.append(("top to bottom", c[::-1]))
        for how, mirror in checks:
            if not (c == mirror).all():
                sys.exit(f"{name} frame {k + 1} is not symmetric {how}")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "muzzle":
        return [-0.5, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def manifest(src):
    """{name: entry} from Codex's manifest.json, whichever way it lists them ("entries" / "effects" / "assets", each
    with "id" or "name", maybe prefixed graves_fx_), with the 1x sheet's path relative to src."""
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    rows = man.get("entries") or man.get("effects") or man.get("assets") or []
    meta = {}
    for e in rows:
        name = (e.get("id") or e.get("name")).replace("graves_fx_", "").replace(".png", "")
        meta[name] = dict(e, pixel_1x=e.get("pixel_1x") or os.path.join("pixel_1x", e["file"]))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC, help="Codex's delivery (the folder holding manifest.json and pixel_1x/)")
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    for tag, (n, t) in LASTS.items():
        fr = FX[tag][1] if n is None else FX[tag][1][:n]
        ms = sum(m for _, m in fr)
        if abs(ms - ticks_ms(t)) > 1:
            sys.exit(f"{tag} plays {ms} ms, the kit holds it {t} ticks ({ticks_ms(t):.0f} ms)")
    meta = manifest(a.src)
    if set(meta) != set(FX) - set(ALIAS):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n], a.src) for n in FX if n not in ALIAS}
    allc.update({n: allc[src] for n, src in ALIAS.items()})
    tables = {"league_graves_fx": {}, "league_graves_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{name}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_graves_big" if name in BIG else "league_graves_fx"][name] = out
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
