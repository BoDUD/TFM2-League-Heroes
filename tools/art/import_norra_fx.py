#!/usr/bin/env python3
"""Import Norra's effects (Wild Rift's kit: tools/kit/build_norra.py's views, the add-on's copy's too) as the game
sheets tft_norra_fx and tft_norra_big, and her three skill icons.

    python tools/art/process_norra_fx.py               # the two deliveries' pictures the kit plays -> fx_1x/
    python tools/art/import_norra_fx.py [--review out.png]

The source is assets/source/norra/fx_1x (process_norra_fx.py: one row of equal frames each at game size, frame sizes in
its manifest.json; alpha 0 / 255; the bolt and the ball flying right and symmetric top to bottom, every other one left
to right - checked again here, then made an odd number of squares across the symmetric way). import_locke_fx.py's way.
Each frame is placed as the kit plays it: spots are game px from the pivot (x forward, y down); a unit's soles are 11
under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's middle), "bottom" (the lowest
drawn row of all the picture's frames), (0, k) (the row k over the cell's last).
Timings follow the kit: the trinkets' field and the rift are played again every p_show / r_show ticks (one loop each);
Journey to Nowhere's portal turns where the unit stood for the whole banish (the Banish plays w_lock once, w_t ticks);
Threads of Homecoming's portals open while the hidden lob flies (e_delay 18 ticks: the threads cross at 300 ms).
Her kit (tft.dll: addons/tft/src/norra.rs) plays two pictures cut from these: each trinket on its own (p_trinket_l / _c / _r:
the field's left crystal, teacup and right crystal, each with its bottom middle on its trinket's spot) and one yarn ball
in flight (r_ball: the left ball of r_yarn's first three frames, going right, its ball - not its tail - on the
projectile's point).
Icons: codex_fx2's icons/norra_icon_<slot>.png (64 x 64) -> tft/icons/tft_norra_<slot>.png.
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
from import_hwei_fx import anchor, lp, rows_drawn  # noqa: E402
import build_norra as kit  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "norra", "fx_1x")
ICONS = os.path.join(ROOT, "assets", "source", "norra", "codex_fx2", "norra_fx2", "icons")
MOD = os.path.join(ROOT, "tft")

FLYING = {"a_bolt", "q_ball"}       # turned with their flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                      # a hit on the upper body of a 32-46 px unit
GROUND = (0, 12)                    # a picture's lowest row on the ground line
FEETRING = (0, 11)                  # the middle of a ring drawn round a unit's feet
LINE = (0, 0)                       # a projectile's point
# the yarn ball: the left ball of r_yarn's frames 0-2 (x0 in each frame, rows), the ball's middle in the crop
BALL_X0, BALL_ROWS, BALL_CORE = (0, 12, 24), (25, 31), (8.5, 2.5)

seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# tag -> (picture, anchor, frames with ms, spots, sheet)
FX = {
    # the attack: a star bolt off her finger, its hit
    "a_bolt": ("a_bolt", "core", loop(4, 60), [LINE], "fx"),
    "a_hit": ("a_hit", "core", seq(range(3), [40, 60, 80]), [HIT], "fx"),
    # Beloved Trinkets: the field where a ready Q / E lands (played again every p_show = 60 ticks), a trinket flying
    # onto a champion and bursting
    "p_trinkets": ("p_trinkets", "bottom", loop(4, 250), [GROUND], "big"),
    "p_burst": ("p_burst", "core", seq(range(5), [70, 70, 60, 80, 100]), [HIT], "fx"),
    # Journey to Nowhere: the portal swallowing him, turning where he stood (the whole w_t = 90 ticks), spitting him out
    "w_in": ("w_in", "bottom", seq(range(5), [70, 80, 110, 100, 90]), [GROUND], "fx"),
    "w_lock": ("w_lock", "core", seq(list(range(4)) * 2, [190, 190, 185, 185] * 2), [FEETRING], "fx"),
    "w_out": ("w_out", "bottom", seq(range(4), [70, 100, 120, 90]), [GROUND], "fx"),
    # Memory Surge: the memory bolt (q_travel 20 ticks), its blast on the ground, its hit
    "q_bolt": ("q_ball", "core", loop(4, 70), [LINE], "fx"),
    "q_blast": ("q_blast", "bottom", seq(range(7), [50, 60, 70, 80, 90, 100, 110]), [GROUND], "big"),
    "q_hit": ("q_hit", "core", seq(range(3), [40, 60, 80]), [HIT], "fx"),
    # Threads of Homecoming: the two portals and the threads between them (on the target's spot the tick it is cast:
    # the threads meet at 300 ms, when the hidden lob lands), a thread's hit, the Threads on a unit (a buff)
    "e_threads": ("e_threads", "bottom", seq(range(6), [100, 100, 100, 100, 90, 110]), [GROUND], "big"),
    "t_hit": ("t_hit", "core", seq(range(3), [40, 60, 80]), [HIT], "fx"),
    "t_mark": ("t_mark", "bottom", loop(6, 110), [GROUND], "fx"),
    # Portalpalooza!: the rift on the ground (played again every r_show = 30 ticks), a volley of yarn balls crossing it
    # at a unit's waist, a ball's hit, its slow (a buff)
    "r_rift": ("r_rift", "core", seq(range(6), [83, 83, 83, 83, 84, 84]), [FEETRING], "big"),
    "r_yarn": ("r_yarn", (0, 0), seq(range(6), [70, 70, 70, 60, 80, 100]), [GROUND], "big"),
    "r_hit": ("r_hit", "core", seq(range(4), [50, 60, 80, 100]), [HIT], "fx"),
    "r_slow": ("r_slow", "core", loop(4, 120), [FEETRING], "fx"),
}


def sym_of(name):
    return "top-bottom" if name in FLYING else "left-right"


def odd(c, name):
    """A symmetric picture an even number of squares across gets its middle column (top to bottom for a projectile: its
    middle row) twice: the game mirrors and turns about the pivot's square, so only an odd width lies even about it."""
    ax = 0 if sym_of(name) == "top-bottom" else 1
    n = c.shape[ax]
    if not n % 2:
        c = np.insert(c, n // 2, np.take(c, n // 2, axis=ax), axis=ax)
    return c


def raw_cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        s = sym_of(name)
        if not {"top-bottom": (c == c[::-1]).all(), "left-right": (c == c[:, ::-1]).all()}[s]:
            sys.exit(f"{name} frame {k + 1} is not symmetric {s}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def pieces(cs):
    """p_trinket_l / _c / _r: the three runs of columns the field is drawn in (over all its frames, a clear column
    between them), each with its bottom middle on its trinket's spot (the lowest row the whole field is drawn to)."""
    drawn = np.any([c[..., 3].any(0) for c in cs], axis=0)
    edges = np.flatnonzero(np.diff(np.concatenate([[0], drawn.astype(int), [0]])))
    runs = list(zip(edges[::2], edges[1::2]))
    if len(runs) != 3:
        sys.exit(f"p_trinkets is drawn in {len(runs)} runs of columns, not the three trinkets")
    bottom = rows_drawn(cs)[1]
    out = {}
    for s, (x0, x1) in zip("lcr", runs):
        crop = [c[:, x0:x1].copy() for c in cs]
        if s == "c":
            crop = [odd(c, "p_trinkets") for c in crop]
        anc = [(crop[0].shape[1] - 1) / 2, float(bottom)]
        out[f"p_trinket_{s}"] = [(J.place(c, anc, [GROUND]), 250) for c in crop]
    return out


def ball(cs):
    """r_ball: the left ball of r_yarn's frames 0-2 (going right, its yarn tail behind), its ball on the point."""
    y0, y1 = BALL_ROWS
    out = []
    for k, x0 in enumerate(BALL_X0):
        c = cs[k][y0:y1, x0:x0 + 12].copy()
        if np.any(cs[k][y0:y1, x0 + 12:38, 3]) or np.any(cs[k][:y0, :38, 3]) or np.any(cs[k][y1:, :38, 3]):
            sys.exit(f"r_yarn frame {k + 1}: the left ball is not inside its crop")
        out.append((J.place(c, BALL_CORE, [LINE]), 80))
    return out


def kit_tags():
    """Every view the kit and the add-on's copy play: {sheet: {tag}}."""
    need = {"tft_norra_fx": set(), "tft_norra_big": set()}
    for native in (False, True):
        k = kit.build(dict(kit.P), native)
        for v in k["view_projectiles"] + k["view_effects"] + k["view_buffs"]:
            need[v["anim"].rsplit("/", 1)[1]].add(v["tag"])
    return need


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's frames as the game draws them at 6x here")
    a = ap.parse_args()
    meta = {e["id"]: e for e in json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))["items"]}
    pics = {v[0] for v in FX.values()}
    if set(meta) != pics:
        sys.exit(f"fx_1x holds {sorted(meta)} against the kit's {sorted(pics)}")
    raw = {n: raw_cells(n, meta[n]) for n in pics}
    allc = {n: [odd(c, n) for c in cs] for n, cs in raw.items()}
    tables = {"tft_norra_fx": {}, "tft_norra_big": {}}
    for tag, (pic, kind, frames, spots, sheet) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        tables["tft_norra_" + sheet][tag] = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
    tables["tft_norra_fx"].update(pieces(raw["p_trinkets"]))
    tables["tft_norra_fx"]["r_ball"] = ball(raw["r_yarn"])
    need = kit_tags()
    for sheet, tags in need.items():
        if tags != set(tables[sheet]):
            sys.exit(f"{sheet}: the kit plays {sorted(tags - set(tables[sheet]))} not made, made "
                     f"{sorted(set(tables[sheet]) - tags)} not played")
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    for old in ("tft_norra_yuumi#sheet.png", "tft_norra_yuumi#anim.fanim"):   # TFT's Yuumi went with TFT's kit
        if os.path.isfile(lp(os.path.join(MOD, "effects", old))):
            os.remove(lp(os.path.join(MOD, "effects", old)))
            print("removed tft/effects/" + old)
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for slot in ("skill", "skill2", "ult"):
        im = Image.open(lp(os.path.join(ICONS, f"norra_icon_{slot}.png"))).convert("RGBA")
        if im.size != (64, 64):
            sys.exit(f"norra_icon_{slot}.png is {im.size}, not 64 x 64")
        im.save(lp(os.path.join(MOD, "icons", f"tft_norra_{slot}.png")))
        print(f"tft/icons/tft_norra_{slot}.png")
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for sheet, tags in tables.items():
            for tag, frames in tags.items():
                H = max(f.shape[0] for f, _ in frames)
                W = sum(f.shape[1] + 2 for f, _ in frames)
                img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
                x = 0
                for f, _ in frames:
                    img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST),
                                        (x * Z, (H - f.shape[0]) // 2 * Z))
                    x += f.shape[1] + 2
                rows.append((f"{tag} ({sheet[10:]})", img))
        W = min(max(r.width for _, r in rows) + 150, 4000)
        out = Image.new("RGB", (W, sum(r.height + 10 for _, r in rows)), (20, 20, 26))
        d = ImageDraw.Draw(out)
        y = 0
        for name, r in rows:
            out.paste(r.convert("RGB"), (150, y))
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += r.height + 10
        out.save(lp(a.review))
        print("review", a.review, out.size)


if __name__ == "__main__":
    main()
