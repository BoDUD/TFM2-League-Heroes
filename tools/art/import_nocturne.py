#!/usr/bin/env python3
"""Import Nocturne's effects (Codex's deliveries in assets/source/nocturne/codex_fx and codex_fx2) as game sheets.

    python tools/art/import_nocturne.py

The body comes from tools/art/import_native.py. Codex's effects round got the strips pack by mistake and drew 8 effects
of its own choice (codex_fx/HANDOFF.md); the 11 it skipped came in a second round from PROMPTS_FX2.md (codex_fx2). Both
come in one format: 4 frames in a 2x2 grid of 120x104-game-pixel cells, exact pixels, the 19 colours of the design
without the eyes' white, each frame's anchor (manifest.json `pivot_1x`) on the feet (tail tip) of the unit the effect
sits on, drawn round a 40-px hero standing there. So an effect on a unit (CasterViewEffect / ViewEffect, the frame's
middle on the unit's pivot) keeps its place by putting the anchor 11 rows under the frame's middle (the pivot is 11 px
over the feet). Three are projectiles, centred on themselves instead: the shadow blade (centred on its own box), the
dusk trail (88 px long, cut to the Q's 66 by dropping evenly spread columns, centred on its middle line - a projectile's
picture is turned with its flight, so it may not hang off-centre) and one 24-px link of the tether (the middle of
Codex's 52-px rope, the stretch where it is even, so the links join end to end).
Times follow the kit (60 ticks a second): the bursts 70/70/90/110 ms as Codex timed them, the loops (blade, trail,
chain, shroud, flight trail) 100 ms a frame repeated for as long as they last. Writes league/effects/league_nocturne_fx
and league_nocturne_big.
Colours: both rounds keep to the design's 19 colours and draw mostly in its three darkest navies, so the set came out
the darkest in the pack (mean luminance 36-42, the brightest tenth 72; even the dark heroes' effects - Fiddlesticks,
Morgana, Shaco - have highlights over 200) and the hits vanished on the champions they land on. LIFT keeps the three
darkest navies dark (one step up: the smoke's core) and turns the next tones into rims - blue, light blue, near white -
with the purples and crimsons two steps up (seven new tints): the small effects' mean 96 and brightest tenth 193, the
big ones (trail, landing, burst: mostly core) 81 / 141. One step up for every colour still lost the hits on Darius; two
to three steps for every colour turned the darkness pastel white.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nocturne")
MOD = os.path.join(ROOT, "league")
FEET = 11                      # the unit's pivot is 11 rows over the anchor (its feet)
Q_LEN = 66                     # the Q's line: 66000 units = 66 px
LINK = 24                      # one tether link (the kit's links fly 1600 a tick, spawned 12 ticks apart)
BURST = [70, 70, 90, 110]
LIFT = {  # Codex's colour -> the one drawn (new tints: #6F8CE0 #A9C1FF #F2F5FF #A774B8 #D2A6E0 #FF4D6A #FF8A9C)
    "#080611": "#171C43", "#101029": "#202952", "#171C43": "#30437B",                      # the dark core
    "#202952": "#6F8CE0", "#30437B": "#A9C1FF", "#284C85": "#A9C1FF", "#465DAC": "#F2F5FF",   # the rims
    "#888BA2": "#D3D7DC", "#D3D7DC": "#F2F5FF",
    "#342039": "#583262", "#583262": "#A774B8", "#794786": "#D2A6E0",
    "#560F27": "#9B1032", "#9B1032": "#FF4D6A", "#D3143E": "#FF8A9C",
    "#33323E": "#555160", "#555160": "#777680", "#777680": "#A1A3AA", "#A1A3AA": "#D3D7DC",
}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def lift(c):
    """The cell with every colour moved up its ramp (LIFT)."""
    out = c.copy()
    solid = c[..., 3] > 0
    for k, v in LIFT.items():
        out[solid & np.all(c[..., :3] == rgb(k), axis=-1), :3] = rgb(v)
    left = {tuple(x) for x in c[solid][:, :3]} - {rgb(k) for k in LIFT}
    assert not left, f"colours outside LIFT: {sorted(left)}"
    return out


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def frames(delivery, name, prefix="nocturne_fx"):
    """The delivered frames of one effect: [(cell RGBA, (anchor x, anchor y))]."""
    man = json.load(open(lp(os.path.join(SRC, delivery, "manifest.json")), encoding="utf-8"))
    eff = man["effects"][name]
    one = np.asarray(Image.open(lp(os.path.join(SRC, delivery, "effects_1x", f"{prefix}_{name}_1x.png"))).convert("RGBA"))
    out = []
    for fr in eff["frames"]:
        x, y, w, h = fr["cell_rect_1x"]
        c = one[y:y + h, x:x + w].copy()
        c[c[..., 3] < 128] = 0
        c[c[..., 3] > 0, 3] = 255
        out.append((lift(c), tuple(fr["pivot_1x"])))
    return out


def on_unit(cells):
    """Frames centred on the unit's pivot: the anchor (its feet) FEET rows under the middle."""
    return [G.centre_frame(c, -ax, -(ay - FEET)) for c, (ax, ay) in cells]


def centred(cells):
    """Frames centred on the middle of their common box (a projectile's picture)."""
    ys = [np.nonzero(c[..., 3])[0] for c, _ in cells]
    xs = [np.nonzero(c[..., 3])[1] for c, _ in cells]
    cy = (min(y.min() for y in ys) + max(y.max() for y in ys)) / 2
    cx = (min(x.min() for x in xs) + max(x.max() for x in xs)) / 2
    return [G.centre_frame(c, -int(round(cx)), -int(round(cy))) for c, _ in cells]


def trail(cells):
    """The dusk trail cut to Q_LEN columns (evenly spread columns dropped) and centred on its middle line."""
    ys = [np.nonzero(c[..., 3])[0] for c, _ in cells]
    xs = [np.nonzero(c[..., 3])[1] for c, _ in cells]
    y0, y1 = min(y.min() for y in ys), max(y.max() for y in ys)
    x0, x1 = min(x.min() for x in xs), max(x.max() for x in xs)
    n = x1 - x0 + 1
    keep = sorted({x0 + int(round(k * (n - 1) / (Q_LEN - 1))) for k in range(Q_LEN)})
    assert len(keep) == Q_LEN, len(keep)
    out = []
    for c, _ in cells:
        band = c[y0:y1 + 1][:, keep]
        out.append(G.centre_frame(band, -(Q_LEN // 2), -((y1 - y0) // 2)))
    return out


def link(cells):
    """One LINK-px piece out of the middle of the tether rope, centred on the rope's middle line."""
    xs = [np.nonzero(c[..., 3])[1] for c, _ in cells]
    x0 = max(x.min() for x in xs)
    x1 = min(x.max() for x in xs)
    mid = (x0 + x1) // 2
    out = []
    for c, _ in cells:
        piece = c[:, mid - LINK // 2:mid - LINK // 2 + LINK]
        py = np.nonzero(piece[..., 3].any(1))[0]
        out.append(G.centre_frame(piece, -(LINK // 2), -int(round((py.min() + py.max()) / 2))))
    return out


def loop(fr, n, ms=100):
    return [(fr[k % len(fr)], ms) for k in range(n)]


def burst(fr, ms=BURST):
    return list(zip(fr, ms))


def build():
    d1 = "codex_fx"
    swing = on_unit(frames(d1, "attack_slash"))
    cleave = on_unit(frames(d1, "passive_cleave"))
    blade = centred(frames(d1, "q_blade"))
    path = trail(frames(d1, "q_trail"))
    chain = link(frames(d1, "e_tether"))
    shroud = on_unit(frames(d1, "w_shroud"))
    flight = on_unit(frames(d1, "r_flight"))
    impact = on_unit(frames(d1, "r_impact"))
    fx = {
        "swing": burst(swing),                  # the attack's slash in front of him (a caster picture)
        "p_spin": burst(cleave),                # Umbra Blades' ring round him
        "q_blade": loop(blade, 4),              # the flying shadow blade (repeats while it flies)
        "e_chain": loop(chain, 4),              # one tether link (repeats while it flies back)
        "w_shroud": loop(shroud, 15),           # the shroud's 90 ticks
        "r_trail": loop(flight, 6),             # the dark trail behind his dive (the flight's ~37 ticks)
    }
    big = {
        "q_path": loop(path, 4),                # the dusk trail (repeats for the 300 ticks it lies there)
        "r_hit": burst(impact),                 # the landing strike on the champion
    }
    d2 = os.path.join(SRC, "codex_fx2", "manifest.json")
    if os.path.exists(lp(d2)):
        def two(name):
            return on_unit(frames("codex_fx2", name, "nocturne_fx2"))
        fx.update({
            "hit": burst(two("hit")),
            "p_hit": burst(two("p_hit")),
            "q_hit": burst(two("q_hit")),
            "q_dusk": loop(two("q_dusk"), 4),
            "e_grip": burst(two("e_grip")),
            "e_tick": burst(two("e_tick"), [50, 50, 60, 70]),
            "e_fear": loop(two("e_fear"), 13),   # the fear's 80 ticks
            "w_proc": burst(two("w_proc")),
            "r_veil": burst(two("r_veil"), [90, 100, 110, 120]),
            "r_dark_in": burst(two("r_dark")[:1], [100]),
            "r_dark": loop(two("r_dark"), 4),
            "r_dark_out": burst(two("r_dark")[3:], [100]),
        })
        big["r_burst"] = burst(two("r_burst"), [80, 90, 110, 140])
    return {"league_nocturne_fx": fx, "league_nocturne_big": big}


def main():
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
