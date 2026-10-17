#!/usr/bin/env python3
"""Preview images for Swain, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_swain.py [--out docs/preview] [--only frames|effects|showcase]

  league_swain_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_swain_effects.png   every effect animation, 3x
  league_swain_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_swain.py, 60 ticks a
                             second), as the main pack shows it: raven bolts from the demon hand; Vision of Empire - the
                             eye opening under Darius, its burst and a Soul Fragment brought to Swain; Death's Hand's
                             fan; Nevermove - the hand out and back, the root, the pull and a fragment; Demonic
                             Ascension - the burst, the wings' aura, the drain, a demon's bolt and Demonflare; Darius
                             falls and the ravens bring the takedown's fragment; 3x
Projectiles fly as the kit flies them: lifted 5000 - y_offset over his pivot, turned to their way (champion-data
section 6). Main pack only: his idle stays Swain between the demon's casts (the add-on swaps the whole body).
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_kindred import Turned, fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_swain import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_swain")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_swain_fx", "league_swain_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_swain_fx"], fx["league_swain_big"]
    W, H = 300, 120
    gy = 84
    x0 = 112
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 50, gy)     # in his reach
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    lift = lambda y: (5000 - y) / 1000.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(dense(sp, tag, "swain", z), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        if ms > 0:
            a("idle", ms, loop=True)

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def on_me(tag, when, sheet=None, under_=False, until=None, frames=None):
        o = OnMe(frames or frames_of(sheet or small, tag), when, me, until=until)
        (under if under_ else over).append(o)

    def at_spot(tag, when, x, y, sheet=None, under_=False):
        an = Anim(frames_of(sheet or small, tag), when, int(x), int(y))
        (under if under_ else over).append(an)

    def bolt(rel):
        mx, my = me.pos(rel)
        dx, dy = d.pos(rel)
        arrive = rel + tick(max(1.0, abs(dx - mx) / (P["bolt_speed"] / 1000.0)))
        over.append(Turned(frames_of(small, "a_bolt"), rel, int(mx), int(my - lift(P["bolt_y"])), loop=False,
                           until=arrive, x1=dx, y1=dy))
        on(d, "a_hit", arrive)
        d.flinches.append(arrive)
        return arrive

    def attack(tag="attack"):
        rel = t + tick(P["a_rel"])
        arrive = bolt(rel)
        a(tag, tick(P["atk_dur"]))
        wait(tick(P["atk_cd"] - P["atk_dur"]))
        return arrive

    wait(400)
    attack()
    # Vision of Empire: the watch lobs the eye under Darius (w_travel ticks), it bursts w_delay later
    w0 = t + tick(P["w_travel"])
    ex, ey = d.pos(w0)
    at_spot("w_eye", w0, ex, ey, big, under_=True)
    burst = w0 + tick(P["w_delay"])
    attack()
    attack()
    on(d, "w_hit", burst)
    d.flinches.append(burst)
    on_me("p_frag", burst)
    wait(max(0.0, burst - t) + 200)
    # Death's Hand: the fan flies q_len, the hits flash as the bolts reach Darius
    rel = t + tick(P["q_rel"])
    mx, my = me.pos(rel)
    ly = int(my - lift(-2000))
    over.append(Turned(frames_of(small, "q_bolts"), rel, int(mx), ly, until=rel + tick(P["q_len"] / P["q_speed"]),
                       x1=int(mx + P["q_len"] / 1000), y1=ly))
    on(d, "q_hit", rel + tick(P["q_flash"]))
    d.flinches.append(rel + tick(P["q_flash"]))
    a("skill", tick(P["q_dur"]))
    wait(500)
    # Nevermove: the hand out to e_len, back to him; the root as it passes Darius, the pull e_pull_at later
    rel = t + tick(P["e_rel"])
    mx, my = me.pos(rel)
    ly = int(my - lift(-2000))
    turn = rel + tick(P["e_len"] / P["e_out"])
    far = mx + P["e_len"] / 1000
    over.append(Turned(frames_of(small, "e_out"), rel, int(mx), ly, loop=True, until=turn, x1=int(far), y1=ly))
    home = turn + tick((far - mx) / (P["e_back"] / 1000.0))
    over.append(Turned(frames_of(small, "e_back"), turn, int(far), ly, loop=True, until=home, x1=int(mx), y1=ly))
    dx, _ = d.pos(turn)
    caught = turn + tick((far - dx) / (P["e_back"] / 1000.0))
    on(d, "e_hit", caught, until=caught + tick(P["e_root"]))
    d.flinches.append(caught)
    pull = caught + tick(P["e_pull_at"])
    pull_t = tick(P["e_pull_d"] // P["e_pull_v"])
    d.slides.append((pull, pull + pull_t, -P["e_pull_d"] / 1000.0))
    on(d, "e_pull", pull)
    on_me("p_frag", pull)
    a("skill2", tick(P["e_dur"]))
    wait(max(0.0, pull + pull_t - t) + 300)
    # Demonic Ascension: the press opens the window, the watch raises the demon (two champions close here)
    a("idle", tick(3))
    rise = t
    at_spot("r_cast", rise, *me.pos(rise), big)
    on_t = rise + tick(P["r_wings_at"])
    end = on_t + tick(P["r_t0"] + P["r_keep"])
    on_me("r_wings", on_t, under_=True, until=end, frames=dense(sp, "r_wings", "swain", z))
    a("ult", tick(P["r_dur"]))
    pulses = [on_t + tick(P["r_pulse"] * k) for k in range(int((end - on_t) // tick(P["r_pulse"])) + 1)]
    flare_at = next(p for p in pulses if p >= rise + tick(P["r_wings_at"] + P["r_flare_at"]))
    death = flare_at + tick(P["r_fl_dur"]) + 160
    for pt in pulses:
        if pt < death:
            on(d, "r_drain", pt)
    wait(200)
    attack("r_attack")
    wait(max(0.0, flare_at - t))
    a("r_flare", tick(P["r_fl_dur"]))
    at_spot("r_flare", flare_at, *me.pos(flare_at), big, under_=True)
    on(d, "r_fl_hit", flare_at + 60)
    d.flinches.append(flare_at + 60)
    d.death = death
    on_me("p_frag", death + 300)
    wait(max(0.0, end - t))
    wait(600)
    end_all = t

    def place(img, f, px, py):
        put(img, f, px, py, z)

    frames, tt = [], 0.0
    while tt < end_all:
        img = Image.new("RGBA", (W * z, H * z), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((an.pos(tt)[1] + 0.5, f, an.pos(tt)))
                break
        for _, f, p in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *p)
        for an in over:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        frames.append(img.convert("RGB"))
        tt += step
    sample = frames[::6]
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q_ = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q_[0].save(T.long_path(out), save_all=True, append_images=q_[1:], duration=step, loop=0)
    return len(frames), round(end_all / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_swain_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_swain_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_swain_showcase.gif")))


if __name__ == "__main__":
    main()
