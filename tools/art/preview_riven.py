#!/usr/bin/env python3
"""Preview images for Riven, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_riven.py [--out docs/preview]

  league_riven_frames.png    every animation, frame by frame, 3x on the arena colour
  league_riven_effects.png   every effect animation, 3x
  league_riven_showcase.gif  a scripted fight against Darius, timed like the kit (60 ticks a second): Riven runs in
                             and chops (the plain hit); Broken Wings' first strike hops onto him (the slash and the
                             hit on tick 13), an attack spends its rune (the runic X), the second strike and an
                             attack, the third leaps and slams (tick 15) and knocks him up (the dust swirl); Valor
                             dashes in under its shield sweep and keeps the rune shards round her waist, Ki Burst's
                             ring stuns him (tick 13, the rune ring over his head); two attacks spend E and W's
                             runes; Blade of the Exile wraps the blade in green energy and reforges it (the aura
                             under her from then on): an attack and Broken Wings with the reforged sword; Garen
                             walks up behind him and Wind Slash's crescent flies through both (released on tick 8,
                             a hit on each); Darius falls. The glyphs over her head count her runes; 3x
The first delivery's effects are drawn on her own strips (tools/art/import_riven.py): the back layer under the
units, the front layer over them, both following her from the action's first tick.
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held, OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow, Walker  # noqa: E402
from preview_yone import Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_riven")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_riven_fx", "league_riven_big")}
WAVE_LIFT = 15                        # px: the wave's y_offset -15000
WAVE_SPEED = 4                        # px a tick (4000 units)
WAVE_LEN = 70                         # px (70000 units)
SHIELD = 1500                         # ms: the shield's 90 ticks


def showcase(out, z=3, step=40):
    riven = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_riven_fx"], fx["league_riven_big"]
    W, H = 260, 150
    gy = 96                                           # the pivot row
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 186, gy)
    g = Walker(load(os.path.join(LEAGUE, "champions", "league_garen")), 290, gy)
    body, under, over = [], [], []
    runes = []                                        # (ms, +1 gained / -1 spent)
    t = 0.0
    x = 30
    r_on = None                                       # when Blade of the Exile started

    def a(tag, dur=None, loop=False, way=None):
        nonlocal t
        an = Path(frames_of(riven, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def reforged(tag):
        return f"{tag}_r" if r_on is not None else tag

    def overlay(sheet, name, t0):
        """Codex's effect drawn on her strip: the back layer under the units, the front layer over them."""
        under.append(Follow(frames_of(sheet, f"{name}_back"), t0, x, gy, on=body, z=-1))
        if f"{name}_front" in [tg["name"] for tg in sheet.tags]:
            over.append(Follow(frames_of(sheet, f"{name}_front"), t0, x, gy, on=body, z=2))

    def count(at):
        """The runes she holds at a moment: gains stop at three, attacks spend one."""
        n = 0
        for tt, dn in sorted(runes):
            if tt > at:
                break
            n = max(0, min(3, n + dn))
        return n

    def hop(tag, name, ticks, to, hit_tick, stun=0):
        """A Q strike: the hop over the jump frames (ticks 3-9), the slash and the hit on its tick."""
        nonlocal x
        start = t
        overlay(small, name, start)
        runes.append((start, 1))
        a(reforged(tag), tick(ticks), way=[(start + tick(3), x), (start + tick(9), to)])
        x = to
        hit = start + tick(hit_tick)
        d.flinches.append(hit)
        over.append(OnFoe(frames_of(small, "q_hit"), hit, d, z=3))
        if stun:
            d.holds.append((hit, hit + tick(stun)))
            over.append(OnFoe(frames_of(small, "knockup"), hit, d, z=3))

    def attack():
        start = t
        hit = start + tick(11)
        if count(hit) > 0:
            over.append(OnFoe(frames_of(small, "rune_hit"), hit, d, z=3))
            runes.append((hit, -1))
        else:
            over.append(OnFoe(frames_of(small, "hit"), hit, d, z=3))
        d.flinches.append(hit)
        a(reforged("attack"), tick(26))
        a("idle", tick(14), loop=True)

    # she runs in (move speed 1050: 63 px a second) and chops without a rune
    a("run", 1300, loop=True, way=[(0, x), (1300, 150)])
    x = 150
    attack()
    # Broken Wings: the first strike hops onto him, an attack spends its rune, the second, an attack, the third leaps
    # and slams him into the air
    hop("skill", "q1", 28, 154, 13)
    attack()
    hop("q2", "q2", 28, 156, 13)
    attack()
    hop("q3", "q3", 31, 158, 15, stun=45)
    attack()
    a("idle", 300, loop=True)
    # Valor + Ki Burst: the dash under the shield sweep, the shield held for 1.5 s, the ring stuns him (tick 13)
    start = t
    overlay(big, "e", start)
    overlay(big, "w", start)
    runes.append((start, 1))
    shield_in = frames_of(big, "shield_in")
    t_in = sum(ms for _, ms in shield_in)
    over.append(Follow(shield_in, start, x, gy, on=body, z=2))
    over.append(Follow(frames_of(big, "shield"), start + t_in, x, gy, loop=True, until=start + SHIELD, on=body, z=2))
    over.append(Follow(frames_of(big, "shield_out"), start + SHIELD, x, gy, on=body, z=2))
    a("skill2", tick(33), way=[(start + tick(2), x), (start + tick(8), 152)])
    x = 152
    hit = start + tick(13)
    runes.append((hit, 1))
    d.flinches.append(hit)
    d.holds.append((hit, hit + tick(45)))
    over.append(OnFoe(frames_of(small, "stun"), hit, d, z=3))
    attack()
    attack()
    # Blade of the Exile: the blade wrapped in green energy and reforged, the aura under her from then on; an attack
    # and Broken Wings with the reforged sword
    start = t
    overlay(big, "r_on", start)
    runes.append((start, 1))
    aura = Follow(frames_of(big, "r_aura"), start, x, gy, loop=True, until=None, on=body, z=-2)
    under.append(aura)
    a("ult", tick(31))
    r_on = start
    a("idle", 200, loop=True)
    attack()
    hop("skill", "q1", 28, 154, 13)
    attack()
    # Garen walks up behind Darius; Wind Slash: the crescent leaves on tick 8 and flies through both
    g.walks.append((t - 900, t + 300, -64))
    a("idle", 400, loop=True)
    start = t
    under.append(Follow(frames_of(small, "r_slash_back"), start, x, gy, on=body, z=-1))
    a("r_slash", tick(29))
    launch = start + tick(8)
    x1 = x + WAVE_LEN
    over.append(Anim(frames_of(small, "r_wave"), launch, x, gy - WAVE_LIFT, loop=True,
                     until=launch + tick(WAVE_LEN / WAVE_SPEED), x1=x1, y1=gy - WAVE_LIFT, z=3))
    for foe in (d, g):
        fx_ = foe.pos(launch)[0]
        hit = launch + tick(max(0.0, (fx_ - x - 16) / WAVE_SPEED))
        foe.flinches.append(hit)
        over.append(OnFoe(frames_of(small, "r_hit"), hit, foe, z=3))
    d.death = launch + tick((d.pos(launch)[0] - x - 16) / WAVE_SPEED) + 60
    a("idle", 1600, loop=True)
    end = t
    aura.until = end
    # the glyphs over her head: one for each rune she holds
    marks = sorted({tt for tt, _ in runes} | {0.0, end})
    for k in (1, 2, 3):
        on_ = None
        for tt in marks:
            held = count(tt) >= k
            if held and on_ is None:
                on_ = tt
            elif not held and on_ is not None:
                over.append(Follow(frames_of(small, f"rune_{k}"), on_, x, gy, loop=True, until=tt, on=body, z=4))
                on_ = None
        if on_ is not None:
            over.append(Follow(frames_of(small, f"rune_{k}"), on_, x, gy, loop=True, until=end, on=body, z=4))

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px) - f.width // 2, int(py) - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in sorted(under, key=lambda o: o.z):
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(1, d.frame(tt), d.pos(tt)), (2, g.frame(tt), g.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((0, f, an.pos(tt)))
                break
        for _, f, p in sorted(units, key=lambda u: -u[2][0]):      # the farther right, the further back
            if f is not None:
                place(img, f, *p)
        for an in sorted(over, key=lambda o: o.z):
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
        tt += step
    sample = frames[::6]                              # one palette for the whole clip
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0, optimize=False)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_riven_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_riven_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_riven_showcase.gif")))


if __name__ == "__main__":
    main()
