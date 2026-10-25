#!/usr/bin/env python3
"""Import Ambessa's effects (assets/source/ambessa/PROMPTS_FX.md, 20 pictures) as the game sheets league_ambessa_fx and
league_ambessa_big (import_sejuani_fx.py's way).

    python tools/art/import_ambessa_fx.py [--review out.png]

Two deliveries, half each (the user, 2026-10-25: 「特效是包含gemini的十张和codex的十张 你一起处理 反正是每人做了一半」):
  assets/source/ambessa/gemini_fx   the first ten (a_hit pw_hit pw_aura st_dash st_land q_sweep q_hit q_tip q2_crack
                                    q2_hit), Gemini's JPEGs read back by tools/art/read_ambessa_gemini.py into pixel_1x/
                                    + manifest.json (a list);
  assets/source/ambessa/codex_fx/ambessa_fx   the other ten (e_lash e_hit slow w_brace w_slam w_hit w_crit r_blink r_pin
                                    r_crash), Codex 2026-10-25/new-chat-3: pixel_1x/ambessa_fx_<name>.png, one row of
                                    equal frames each at game size, frame sizes in manifest.json ({"items": [...]}).
Every frame is checked again: alpha 0 / 255, not empty, the red side's symmetry (q2_crack top to bottom: the line zone
turns with the cast; every other one left to right), then made an odd number of squares across the symmetric way.
q_sweep and st_dash point forward: they are drawn into her own frames (tools/art/rig_ambessa.py BAKE), not here.
Each frame is placed as the kit plays it: spots are game px from the pivot (x forward, y down); a unit's soles are 11
under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's middle), "bottom" (the lowest
drawn row of all its frames). The buffs loop (tools/kit/build_ambessa.py: the empowered attack's stir pw_aura, the
slow), the suppression mark r_pin plays its loop over the pin (r_sup), the brace's shell over the brace (w_brace); the
rest play once.
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
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from import_hwei_fx import anchor, lp, odd  # noqa: E402
from build_ambessa import P  # noqa: E402

GEMINI = os.path.join(ROOT, "assets", "source", "ambessa", "gemini_fx")
CODEX = os.path.join(ROOT, "assets", "source", "ambessa", "codex_fx", "ambessa_fx")
MOD = os.path.join(ROOT, "league")

BIG = {"q2_crack", "e_lash", "w_slam", "r_blink", "r_crash"}
FLYING = {"q2_crack"}           # turned with the cast: drawn going right, symmetric top to bottom
FORWARD = {"q_sweep", "st_dash"}   # drawn into her frames (rig_ambessa BAKE)
HIT = (0, -14)                  # a hit on the upper body of a 32-48 px unit
GROUND = (0, 12)                # a picture's lowest row on the ground line
LINE = (0, 0)                   # a projectile's point


seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


T = lambda ticks: ticks * 1000 / 60     # noqa: E731

# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the twin blades' cut, the empowered cleave after Drakehound's Step, its amber stir round her feet, the dust where
    # the dash stops
    "a_hit": ("a_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "pw_hit": ("pw_hit", "core", seq(range(3), [40, 70, 90]), [HIT]),
    "pw_aura": ("pw_aura", "bottom", loop(4, 120), [GROUND]),
    "st_land": ("st_land", "bottom", seq(range(3), [50, 70, 90]), [GROUND]),
    # Cunning Sweep's cut on each one swept, the blade's edge (add-on); Sundering Slam's rift and its hit
    "q_hit": ("q_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "q_tip": ("q_tip", "core", seq(range(3), [40, 70, 90]), [HIT]),
    "q2_crack": ("q2_crack", "core", loop(4, 50), [LINE]),
    "q2_hit": ("q2_hit", "bottom", seq(range(3), [50, 70, 90]), [GROUND]),
    # Lacerate: the whirl of chained blades round her, the cut, the slow
    "e_lash": ("e_lash", "bottom", seq(range(5), [40, 60, 80, 80, 90]), [GROUND]),
    "e_hit": ("e_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "slow": ("slow", "bottom", loop(4, 110), [GROUND]),
    # Repudiation: the shell over the brace, the slam's shockwave round her, its hit, the struck brace's burst (add-on)
    "w_brace": ("w_brace", "bottom", seq(range(4), [60, 100, 120, round(T(P["w_brace"])) - 280]), [GROUND]),
    "w_slam": ("w_slam", "bottom", seq(range(5), [50, 60, 70, 80, 100]), [GROUND]),
    "w_hit": ("w_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "w_crit": ("w_crit", "core", seq(range(4), [40, 60, 70, 90]), [HIT]),
    # Public Execution: the smoke where she was, the suppression mark over the pin, the crater
    "r_blink": ("r_blink", "bottom", seq(range(4), [60, 80, 100, 120]), [GROUND]),
    "r_pin": ("r_pin", "bottom", seq([k % 4 for k in range(8)], [round(T(P["r_sup"]) / 8)] * 8), [GROUND]),
    "r_crash": ("r_crash", "bottom", seq(range(6), [50, 60, 70, 90, 100, 130]), [GROUND]),
}


def manifest():
    """name -> its entry (cell_1x, frames, symmetry) and the pixel_1x file, from both deliveries."""
    meta = {}
    for src in (GEMINI, CODEX):
        man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
        if isinstance(man, dict):                 # Codex's {"scope", ..., "items": [...]}
            man = man.get("items") or man.get("effects")
        for e in man:
            f = os.path.basename(e["file"])
            name = f[:-4].replace("ambessa_fx_", "")
            if name in meta:
                sys.exit(f"{name} delivered twice")
            meta[name] = dict(e, path=os.path.join(src, "pixel_1x", f))
    return meta


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["path"])).convert("RGBA")).copy()
    if not np.isin(a[..., 3], (0, 255)).all():
        sys.exit(f"{name}: alpha other than 0 / 255")
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        m = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == m).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return [odd_(c, name) for c in out]


def odd_(c, name):
    """import_hwei_fx.odd with this hero's line zone (its middle row doubled when even)."""
    if name in FLYING:
        n = c.shape[0]
        return c if n % 2 else np.insert(c, n // 2, c[n // 2], axis=0)
    return odd(c, name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = manifest()
    pics = {v[0] for v in FX.values()}
    if set(meta) - FORWARD != pics:
        sys.exit(f"delivered {sorted(set(meta) - FORWARD)} against the kit's {sorted(pics)}")
    allc = {n: cells(n, meta[n]) for n in pics}
    tables = {"league_ambessa_fx": {}, "league_ambessa_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_ambessa_big" if tag in BIG else "league_ambessa_fx"][tag] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name in sorted(allc):
            cs = allc[name]
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
        sheet = Image.new("RGB", (W, sum(r.height + 10 for _, r in rows)), (20, 20, 26))
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
