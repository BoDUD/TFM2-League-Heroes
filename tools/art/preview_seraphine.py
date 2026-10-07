#!/usr/bin/env python3
"""Preview images for Seraphine, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_seraphine.py [--out docs/preview] [--only frames|effects|showcase]

  league_seraphine_frames.png    every animation, frame by frame, 3x on the arena colour
  league_seraphine_effects.png   every effect animation, 3x
  league_seraphine_showcase.gif  a scripted fight beside Jinx against Darius with Garen behind him, timed like the kit
                                 (tools/kit/build_seraphine.py, 60 ticks a second): two notes over her, the charged
                                 note on Darius; Q - the high note lobbed onto them, the ring and the hits; E -> W - the
                                 wave through both (slowed), the echo and its second wave (rooted), the song's ring,
                                 the shield bubbles on her and Jinx, then the heal; she glides past them, turns round -
                                 facing left from here, as on the red side - and casts R: the spotlight, the great wave
                                 through both, the charm's hearts, then Beat Drop stuns Darius; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_annie import Held  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_seraphine import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_seraphine")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_seraphine_fx", "league_seraphine_big")}
HAND = 21                                        # her hand at the release, px ahead of the pivot
NOTE_Y = P["bolt_y"] // 1000                     # the notes fly this far over the pivot
NOTE = P["bolt_speed"] / 1000                    # px a tick
WAVE = P["e_speed"] / 1000
RWAVE = P["r_speed"] / 1000
HEAL_SHOWN = 900                                 # W's heal comes w_heal_delay (2.5 s) later; the showcase cuts it short


def flipped(fr):
    return [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in fr]


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_seraphine_fx"], fx["league_seraphine_big"]
    W, H = 420, 160
    gy = 116
    x0 = 120
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 60, gy)       # her attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 92, gy)        # behind Darius, in line
    jinx = Held(load(os.path.join(LEAGUE, "champions", "league_jinx")), x0 - 34, gy)      # her ally, behind her
    jinx.mirrored = False                                                                 # facing the foes
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    face = [False]

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        fr = frames_of(sp, tag)
        an = Anim(fr, t, x, y, loop=loop, until=(t + dur) if dur else None, flip=face[0])
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def wave(tag, when, speed, y, foes, last):
        """A line from her hand past the last foe; the hits as it reaches each."""
        sx = me.pos(when)[0] + (-HAND if face[0] else HAND)
        tx = last.pos(when)[0] + (-30 if face[0] else 30)
        arrive = when + tick(max(1, abs(tx - sx) / speed))
        fr = frames_of(big, tag)
        over.append(Anim(flipped(fr) if face[0] else fr, when, sx, gy - y, until=arrive, x1=tx, y1=gy - y))
        return [(foe, when + tick(max(1, abs(foe.pos(when)[0] - sx) / speed))) for foe in foes]

    # two notes over her; the charged note on Darius (the notes are spent)
    notes = OnMe(frames_of(small, "n2"), t, me, until=t + 1500)
    over.append(notes)
    a("idle", 600, loop=True)
    rel = t + tick(P["a_st"])
    sx = me.pos(rel)[0] + HAND
    arrive = rel + tick(max(1, (d.pos(rel)[0] - sx) / NOTE))
    over.append(Anim(frames_of(small, "a_note"), rel, sx, gy - NOTE_Y, until=arrive, x1=d.pos(rel)[0], y1=gy - NOTE_Y))
    notes.until = rel
    hit(d, "a_note_hit", arrive)
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # Q: the high note lobbed onto them, the ring on the ground and the hits; a note for her
    rel = t + tick(P["q_rel"])
    land = rel + tick(P["q_travel"])
    hx, cx = me.pos(rel)[0] + 20, (d.pos(rel)[0] + g.pos(rel)[0]) // 2
    up = (hx + cx) // 2
    over.append(Anim(frames_of(small, "q_note"), rel, hx, gy - 36, until=(rel + land) / 2, x1=up, y1=gy - 52))
    over.append(Anim(frames_of(small, "q_note"), (rel + land) / 2, up, gy - 52, until=land, x1=cx, y1=gy - 4))
    under.append(Anim(frames_of(big, "q_land"), land, cx, gy + 9))
    for foe in (d, g):
        hit(foe, "q_hit", land)
    over.append(OnMe(frames_of(small, "n1"), land, me, until=land + 2600))
    a("skill", tick(P["q_anim"]))
    a("idle", 400, loop=True)
    # E -> W: the wave through both (slowed); the echo's second wave roots them; the song, the bubbles, the heal
    e0 = t
    rel = e0 + tick(P["e_rel"])
    for foe, when in wave("e_wave", rel, WAVE, 0, (d, g), g):
        hit(foe, "e_hit", when)
        under.append(OnFoe(frames_of(small, "e_slow"), when, foe, until=when + 1000))
    echo = rel + tick(P["echo_delay"])
    over.append(OnMe(frames_of(small, "echo"), echo, me))
    for foe, when in wave("e_wave", echo, WAVE, 0, (d, g), g):
        hit(foe, "e_hit", when)
        under.append(OnFoe(frames_of(small, "e_root"), when + 70, foe))
    song = e0 + tick(P["w_rel"])
    under.append(OnMe(frames_of(big, "w_cast"), song, me))
    for who in (me, jinx):
        mk = OnMe if who is me else OnFoe
        over.append(mk(frames_of(small, "w_on"), song, who, until=song + 1700))
        over.append(mk(frames_of(small, "w_heal"), song + HEAL_SHOWN, who))
    over.append(OnMe(frames_of(small, "n3"), song, me, until=song + 3000))
    a("skill2", tick(P["e_anim"]))
    a("idle", 1200, loop=True)
    # she glides past them and turns round (the red side's facing): R - the spotlight, the great wave, the charm, then
    # Beat Drop stuns the charmed Darius
    walk_to = g.pos(t)[0] + 70
    me.moves.append((t, t + 900, me.pos(t)[0], walk_to))
    a("run", 900, loop=True)
    face[0] = True
    r0 = t
    over.append(OnMe(frames_of(big, "r_cast"), r0 + tick(P["r_rel"]) - 120, me))
    for foe, when in wave("r_wave", r0 + tick(P["r_rel"]), RWAVE, 0, (g, d), d):
        hit(foe, "r_hit", when)
    a("ult", tick(P["r_anim"]))
    a("idle", tick(P["rc_wait"]), loop=True)
    e0 = t
    for foe, when in wave("e_wave", e0 + tick(P["e_rel"]), WAVE, 0, (g, d), d):
        hit(foe, "e_hit", when)
        if foe is d:
            over.append(OnFoe(frames_of(small, "e_stun"), when, foe))
    a("skill2", tick(P["e_anim"]))
    over.append(OnMe(frames_of(small, "echo_ready"), t, me, until=t + 1600))
    a("idle", 1600, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt)) for u in (g, d, jinx)]
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
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
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
        print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                                os.path.join(args.out, "league_seraphine_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[17:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_seraphine_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_seraphine_showcase.gif")))


if __name__ == "__main__":
    main()
