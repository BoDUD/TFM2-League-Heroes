#!/usr/bin/env python3
"""Preview images for Aphelios, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_aphelios.py [--out docs/preview] [--only frames|effects|showcase]

  league_aphelios_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_aphelios_effects.png   every effect animation, 3x
  league_aphelios_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_aphelios.py, 60
                                ticks a second), the five weapons in the main pack's order: Calibrum's shots and
                                Moonshot (the line, the mark, the pop from afar); W to Severum - its shots and Onslaught
                                (the ring under him, the bolts of both hands); the magazine empty, Gravitum - its shots
                                slow and mark, Binding Eclipse roots; Infernum - its shots, Duskwave and the off-hand
                                shot; Crescendum - its chakrams and the Sentry; Moonlight Vigil; 3x
The muzzle flashes are in his own shot frames (tools/art/rig_aphelios.py). Projectiles fly as the kit flies them: lifted 5000 - y_offset over his pivot, at the target's pivot, turned to their
way (champion-data section 6). A picture not delivered yet is left out (tools/art/import_aphelios_fx.py --partial).
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
from build_aphelios import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_aphelios")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_aphelios_fx", "league_aphelios_big")}
Q_SPEED = 20000                     # the pop, Severum's bolts, the off-hand shots (build_aphelios)


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_aphelios_fx"], fx["league_aphelios_big"]
    have = {t["name"]: s for s in (small, big) for t in s.tags}
    W, H = 260, 110
    gy = 76
    x0 = 70
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 52, gy)     # in his reach
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    lift = (5000 - P["a_y"]) / 1000.0

    def fr(tag):
        return frames_of(have[tag], tag)

    def a(tag, dur=None, loop=False):
        nonlocal t
        frames = dense(sp, tag, "aphelios", z)
        total = sum(ms for _, ms in frames)
        if dur and not loop and dur > total + 1:
            # a strip shorter than its action (the attacks: 350 ms in a 400 ms swing): the idle for the rest - not
            # nothing (the first showcase lost him for 50 ms after every shot)
            a(tag, total)
            return a("idle", dur - total, loop=True)
        an = Anim(frames, t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def on(unit, tag, when, under_=False, until=None):
        if tag in have:
            (under if under_ else over).append(OnFoe(fr(tag), when, unit, until=until))

    def on_me(tag, when, under_=False, until=None):
        if tag in have:
            (under if under_ else over).append(OnMe(fr(tag), when, me, until=until))

    def at_spot(tag, when, x, y, under_=False):
        if tag in have:
            (under if under_ else over).append(Anim(fr(tag), when, int(x), int(y)))

    def fly(tag, when, speed, src=None):
        """A projectile from over his pivot (or src) to Darius's pivot; returns the arrival time."""
        sx, sy = src if src else me.pos(when)
        sy = sy - (lift if src is None else 0)
        dx, dy = d.pos(when)
        arrive = when + tick(max(1.0, abs(dx - sx) / (speed / 1000.0)))
        if tag in have:
            over.append(Turned(fr(tag), when, int(sx), int(round(sy)), until=arrive, x1=dx, y1=dy))
        return arrive

    def hit(when, tag="a_hit"):
        on(d, tag, when)
        d.flinches.append(when)

    aura = []

    def weapon(w):
        """The main hand's aura under him from now (mw_<w>, a buff's loop)."""
        if aura:
            aura[-1].until = t
        if f"mw_{w}" in have:
            o = OnMe(fr(f"mw_{w}"), t, me, until=10 ** 9)
            under.append(o)
            aura.append(o)

    def shoot(w, n):
        for _ in range(n):
            s0 = t
            rel = s0 + tick(P["a_st"])
            arrive = fly(f"a_{w}", rel, P["a_speed"])
            hit(arrive)
            if w == "grav":
                on(d, "g_slow", arrive, under_=True, until=arrive + tick(P["grav_slow_t"]))
            if w == "inf":
                # the splash: from the target to those near it (here: none) - the picture alone, a step past him
                dx, dy = d.pos(arrive)
                if "a_inf_s" in have:
                    over.append(Turned(fr("a_inf_s"), arrive, dx, dy - 2, until=arrive + tick(2), x1=dx + 14, y1=dy - 2))
            if w == "cre":
                on_me("cre", arrive, until=arrive + tick(P["cre_t"]))
            a(f"a_{w}", tick(P["atk_dur"]))
            wait(tick(P["atk_cd"] - P["atk_dur"]))

    def swap(anim=None):
        on_me("swap", t)
        if anim:
            a(anim, tick(P["w_anim"]))

    # Calibrum (his start): two shots, Moonshot - aimed q_c_lock ticks, the line hits Darius, the pop from afar
    weapon("cal")
    wait(400)
    shoot("cal", 2)
    q0 = t
    rel = q0 + tick(P["q_c_lock"])
    mx, my = me.pos(rel)
    arrive = fly("q_c_shot", rel, P["q_c_speed"], src=(mx, my + P["q_c_y"] / 1000.0 - 5))
    hit(arrive, "q_c_hit")
    pop = arrive + tick(P["q_c_pop"])
    back = fly("q_c_pop", pop, Q_SPEED)
    hit(back, "q_c_pop_b")
    a("q_cal", tick(P["q_c_anim"]))
    wait(300)
    # W: Severum to the main hand
    swap("skill2")
    weapon("sev")
    wait(200)
    shoot("sev", 2)
    # Onslaught: the ring under him, the bolts of both hands every per ticks
    q0 = t
    on_me("q_s_on", q0, under_=True)
    on_me("q_s_haste", q0, under_=True, until=q0 + tick(P["q_s_t"]))
    per = P["q_s_t"] // P["q_s_n"]
    for k in range(P["q_s_n"]):
        arrive = fly("q_s_bolt" if k % 2 == 0 else "off_bolt", q0 + tick(k * per), Q_SPEED)
        hit(arrive, "q_s_hit")
    a("q_sev", tick(P["q_s_anim"]))
    a("idle", tick(P["q_s_t"] - P["q_s_anim"]), loop=True)
    # the magazine empty: the cycle's next, Gravitum (its shots slow and mark), Binding Eclipse
    swap()
    weapon("grav")
    wait(200)
    shoot("grav", 2)
    q0 = t
    on_me("q_g_cast", q0, under_=True)
    bind = q0 + tick(P["q_g_at"])
    on(d, "q_g_hit", bind)
    d.flinches.append(bind)
    a("q_grav", tick(P["q_g_anim"]))
    wait(500)
    # Infernum: its shots, Duskwave (at his spot as it starts, not following) and the off-hand shot from the wave
    swap()
    weapon("inf")
    wait(200)
    shoot("inf", 2)
    q0 = t
    wave = q0 + tick(P["q_i_at"])
    mx, my = me.pos(wave)
    if "q_i_wave" in have:              # on its view-only projectile: lifted to the gun, crawling toward Darius
        lift_w = (5000 - P["q_i_wy"]) / 1000.0
        crawl = P["q_i_wv"] * P["q_i_wt"] / 1000.0
        over.append(Turned(fr("q_i_wave"), wave, mx, int(round(my - lift_w)), until=wave + tick(P["q_i_wt"]),
                           x1=int(round(mx + crawl)), y1=int(round(my - lift_w))))
    hit(wave, "q_i_hit")
    arrive = fly("off_bolt", wave + tick(1), Q_SPEED)
    hit(arrive)
    a("q_inf", tick(P["q_i_anim"]))
    wait(400)
    # Crescendum: the chakrams (each hit adds one), the Sentry on Darius's spot shooting him every q_r_per ticks
    swap()
    weapon("cre")
    wait(200)
    shoot("cre", 2)
    q0 = t
    drop = q0 + tick(P["q_r_at"])
    dx, dy = d.pos(drop)
    sentry_until = drop + 2200          # (the sentry stands q_r_t ticks; the clip moves on sooner)
    if "q_r_turret" in have:
        under.append(Anim(fr("q_r_turret"), drop, dx, dy, loop=True, until=sentry_until))
    k = drop + tick(P["q_r_per"])
    while k < sentry_until:
        hit(k, "q_r_hit")
        k += tick(P["q_r_per"])
    a("q_cre", tick(P["q_r_anim"]))
    a("idle", sentry_until - t, loop=True)
    # Moonlight Vigil: the cast, the moonlight on r_at, its burst on Darius - he falls
    r0 = t
    on_me("r_cast", r0, under_=True)
    rel = r0 + tick(P["r_at"])
    arrive = fly("r_moon", rel, P["r_speed"])
    dx, dy = d.pos(arrive)
    at_spot("r_boom", arrive, dx, dy)
    hit(arrive, "r_hit")
    d.death = arrive + tick(3)
    a("ult", tick(P["r_anim"]))
    wait(1300)
    end = t
    if aura:
        aura[-1].until = end

    def place(img, f, px, py):
        put(img, f, px, py, z)

    frames, tt = [], 0.0
    while tt < end:
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
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_aphelios_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_aphelios_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_aphelios_showcase.gif")))


if __name__ == "__main__":
    main()
