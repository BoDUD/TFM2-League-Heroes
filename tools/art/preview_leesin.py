#!/usr/bin/env python3
"""Preview images for Lee Sin, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_leesin.py [--out docs/preview]

  league_leesin_frames.png    every animation, frame by frame, 3x on the arena colour
  league_leesin_effects.png   every effect animation, 3x
  league_leesin_showcase.gif  a scripted fight, timed like the kit: an enemy Darius keeps hitting an
                              allied Garen; Lee Sin runs in and casts Q Sonic Wave, and at its end
                              Safeguard (W) shields him and Garen on the same tick and dashes him to
                              Garen; Resonating Strike takes him to the marked enemy, two Flurry punches;
                              Dragon's Rage (R): nobody stands behind the fleeing enemy, so he rushes
                              through it and kicks it from behind, back toward Garen, who finishes it;
                              then a second scene: an enemy Yasuo with Jinx on the line behind him - the
                              forward kick: he dashes to Yasuo's front and kicks him into Jinx, and the
                              dragon trailing him knocks her up; 3x
  league_leesin_combos.gif    the combos (tools/kit/leesin_combos.py), labelled: Q, Q2, the punch and E (QQAE),
                              then R with Q on cooldown: the insec kick and the chase (QRQ); a cut; R with Q ready
                              against Yasuo with Jinx behind: the forward kick, the palm, the homing wave that meets
                              him in the air and the dash (RQQ); 3x
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_leesin")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_leesin_fx", "league_leesin_r")}


class Foe:
    """A unit standing at x (mirrored to face left unless mirror=False): idle, attacks, flinches, a
    knock-back slide, a knock-up hop, death."""

    def __init__(self, sprite, x, y, mirror=True):
        self.idle, self.hit, self.dead = frames_of(sprite, "idle"), frames_of(sprite, "hit"), frames_of(sprite, "dead")
        self.attack = frames_of(sprite, "attack")
        self.run = frames_of(sprite, "run")
        self.x, self.y, self.mirrored = x, y, mirror
        self.flinches, self.slides, self.hops, self.attacks, self.death = [], [], [], [], None
        self.runs = []                                # (t0, t1): running away to the right, unmirrored
        self.mirror = {}

    def flip(self, f):
        if not self.mirrored:
            return f
        if id(f) not in self.mirror:
            self.mirror[id(f)] = f.transpose(Image.FLIP_LEFT_RIGHT)
        return self.mirror[id(f)]

    def pos(self, t):
        x, y = self.x, self.y
        for t0, t1, dx in self.slides:
            if t >= t0:
                x += dx * min(1.0, (t - t0) / (t1 - t0))
        for t0, t1, h in self.hops:
            if t0 <= t < t1:
                u = (t - t0) / (t1 - t0)
                y -= 4 * h * u * (1 - u)
        return int(round(x)), int(round(y))

    @staticmethod
    def pick(fr, dt, hold=False):
        for f, ms in fr:
            if dt < ms:
                return f
            dt -= ms
        return fr[-1][0] if hold else None

    def frame(self, t):
        if self.death is not None and t >= self.death:
            return self.flip(self.pick(self.dead, t - self.death, hold=True))
        for t0, t1 in self.runs:
            if t0 <= t < t1:
                return self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
        for t0, t1, _ in self.slides + self.hops:
            if t0 <= t < t1:
                return self.flip(self.hit[0][0])
        for t0 in self.flinches:
            f = self.pick(self.hit, t - t0) if t >= t0 else None
            if f is not None:
                return self.flip(f)
        for t0 in self.attacks:
            f = self.pick(self.attack, t - t0) if t >= t0 else None
            if f is not None:
                return self.flip(f)
        return self.flip(self.pick(self.idle, t % sum(ms for _, ms in self.idle)))


class Follow2(Anim):
    """An effect played on a foe wherever it is (a knock-up marker rides the hop)."""

    def __init__(self, fr, t0, foe, z=1):
        super().__init__(fr, t0, 0, 0, z=z)
        self.foe = foe

    def pos(self, t):
        return self.foe.pos(t)


def skip(fr, ms):
    """The frames of an animation after its first ms milliseconds."""
    out = []
    for f, d in fr:
        if ms >= d:
            ms -= d
            continue
        out.append((f, d - ms))
        ms = 0
    return out or fr[-1:]


def showcase(out, z=3, step=40):
    lee = load(CHAMP)
    garen = load(os.path.join(LEAGUE, "champions", "league_garen"))
    darius = load(os.path.join(LEAGUE, "champions", "league_darius"))
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 320, 104
    gy = 62                                           # pivot row
    ally = Foe(garen, 66, gy - 10, mirror=False)      # Garen, facing right, a step further back on the field
    foe = Foe(darius, 100, gy)                        # the enemy (Darius) hitting him, facing left
    body, effects, shots = [], [], []
    t = 0.0
    x = 12                                            # Lee Sin's x

    def a(tag, dur=None, loop=False, x1=None, flip=False):
        nonlocal t, x
        an = Anim(frames_of(lee, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=x1, flip=flip)
        body.append(an)
        t = an.until
        if x1 is not None:
            x = x1

    def fx_at(tag, at, fx_x, fy=None, sprite="league_leesin_fx", z_=1):
        effects.append(Anim(frames_of(fx[sprite], tag), at, fx_x, gy if fy is None else fy, z=z_))

    # the enemy keeps hitting Garen: an attack every 700 ms, Garen flinches on the hit (tick 12)
    for k in range(4):
        t0 = 150 + k * 700
        foe.attacks.append(t0)
        ally.flinches.append(t0 + tick(12))
    # Lee Sin runs in (move_speed 1100 ~ 1.1 px a tick)
    body.append(Anim(frames_of(lee, "run"), t, x - 50, gy, loop=True, until=t + 760, x1=x))
    t += 760
    a("idle", 200, loop=True)
    # Q: the wave leaves at tick 16 (4500/tick). Safeguard's check runs with Q: Garen has an enemy champion
    # on him, so both get the shield on that tick and Lee Sin dashes to him (q2 pose, 5000/tick)
    start = t
    a("skill")
    at = start + tick(16)
    arrive = at + tick((foe.x - 6 - (x + 10)) / 4.5)
    shots.append(Anim(frames_of(fx["league_leesin_fx"], "q_wave"), at, x + 10, gy - 2, loop=True,
                      until=arrive, x1=foe.x - 6, y1=gy - 2, z=1))
    fx_at("q_mark", arrive, foe.x)
    foe.flinches.append(arrive)
    fx_at("shield", at, ally.x, fy=ally.y)
    wdest = ally.x - 12                               # right behind Garen
    land = at + tick((wdest - x) / 5.0)
    shield = frames_of(fx["league_leesin_fx"], "shield")   # his own shield rides the dash with him
    effects.append(Anim(shield, at, x, gy, until=land, x1=wdest, z=1))
    effects.append(Anim(skip(shield, land - at), land, wdest, gy, z=1))
    body[-1].until = at                               # the dash cuts Q's pose short
    body.append(Anim(frames_of(lee, "q2"), at, x, gy, until=at + tick(20), x1=wdest))
    body[-1].until_move = land
    t, x = at + tick(20), wdest
    # Resonating Strike: 12 ticks after the wave hits, the dash to the marked enemy
    dash0 = max(t, arrive + tick(12))
    if t < dash0:
        a("idle", dash0 - t, loop=True)
    dest = foe.x - 22                                 # melee range
    body.append(Anim(frames_of(lee, "q2"), dash0, x, gy, until=dash0 + tick(31), x1=dest))
    body[-1].until_move = dash0 + tick(max(1, (dest - x) / 5.0))
    fx_at("q2_hit", body[-1].until_move, foe.x)
    foe.flinches.append(body[-1].until_move)
    t, x = dash0 + tick(31), dest

    def punch():
        nonlocal t
        start = t
        a("attack")
        fx_at("hit", start + tick(12), foe.x - 4, gy - 4)
        foe.flinches.append(start + tick(12))
        a("idle", tick(36 - 20), loop=True)           # Flurry: 50-tick cooldown, 40% faster

    punch()
    punch()
    # the enemy runs away to the right (44 px in 40 ticks)
    flee0, flee1 = t, t + tick(40)
    foe.runs.append((flee0, flee1))
    foe.slides.append((flee0, flee1, 44))
    a("idle", tick(40), loop=True)
    fx_ = foe.x + 44
    # R, the insec: at tick 7 he rushes through the target (8000/tick) and stops 15 px behind it; the kick
    # at tick 19 sends it back the way he came, 54 px in 18 ticks, toward Garen; the dragon follows 4 ticks
    # later at 2500/tick for 35 px. Facing left from the rush on.
    start = t
    behind = fx_ + 15
    body.append(Anim(frames_of(lee, "ult"), start, x, gy, until=start + tick(7)))
    rush0, rush1 = start + tick(7), start + tick(7) + tick((behind - x) / 8.0)
    ult = Anim(frames_of(lee, "ult"), start, x, gy, until=start + tick(44), x1=behind, flip=True)
    ult.until_move, ult.move0 = rush1, rush0
    body.append(ult)
    kick = start + tick(19)
    fx_at("kick", kick, fx_, gy - 4, sprite="league_leesin_r")
    foe.slides.append((kick, kick + tick(18), -54))
    foe.flinches.append(kick)
    dragon = [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in frames_of(fx["league_leesin_r"], "dragon")]
    shots.append(Anim(dragon, kick + tick(4), behind, gy - 2, loop=True, until=kick + tick(4) + tick(35 / 2.5),
                      x1=behind - 35, y1=gy - 2, z=1))
    # Garen finishes it where it lands
    land = kick + tick(18)
    ally.attacks.append(land + 60)
    fx_at("hit", land + 60 + tick(12), fx_ - 54 - 4, gy - 4)
    foe.death = land + 60 + tick(12)
    t, x = start + tick(44), behind
    a("idle", 1500, loop=True, flip=True)
    # second scene (a cut): the forward kick. Yasuo stands in front with Jinx on the line behind him, so the probe
    # counts two champions: at tick 7 he dashes to Yasuo's front (8000/tick), the kick at tick 19 sends Yasuo 54 px
    # on, and the dragon trails him from Lee's foot at the kick's speed (3000/tick for 63000), knocking Jinx up
    # (0.75 s) as it reaches her
    cut = t
    yasuo = Foe(load(os.path.join(LEAGUE, "champions", "league_yasuo")), 138, gy)
    jinx = Foe(load(os.path.join(LEAGUE, "champions", "league_jinx")), 180, gy - 10)   # a step back: Yasuo flies past
    t, x = cut + 160, 70
    a("idle", 500, loop=True)
    start = t
    front = yasuo.x - 22
    body.append(Anim(frames_of(lee, "ult"), start, x, gy, until=start + tick(7)))
    ult = Anim(frames_of(lee, "ult"), start, x, gy, until=start + tick(44), x1=front)
    ult.until_move, ult.move0 = start + tick(7) + tick((front - x) / 8.0), start + tick(7)
    body.append(ult)
    kick = start + tick(19)
    fx_at("kick", kick, yasuo.x, gy - 4, sprite="league_leesin_r")
    yasuo.slides.append((kick, kick + tick(18), 54))
    yasuo.flinches.append(kick)
    shots.append(Anim(frames_of(fx["league_leesin_r"], "dragon"), kick, front, gy - 2, loop=True,
                      until=kick + tick(63 / 3.0), x1=front + 63, y1=gy - 2, z=1))
    reach = kick + tick(max(0.0, (jinx.x - 20 - front) / 3.0))   # the dragon's circle (14000) on her body
    jinx.hops.append((reach, reach + tick(45), 10))
    jinx.flinches.append(reach)
    effects.append(Follow2(frames_of(fx["league_leesin_fx"], "knockup"), reach, jinx))
    t, x = start + tick(44), front
    a("idle", 1200, loop=True)
    return film(out, W, H, t, body, effects, shots, lambda tt: (ally, foe) if tt < cut else (jinx, yasuo),
                cut=(cut, cut + 160), z=z, step=step)


def combos(out, z=3, step=40):
    """The combos (tools/kit/leesin_combos.py), timed as the simulation logs them: Q, Q2, then E in Q2's window (QQAE:
    the punch, the stomp), then R with Q on cooldown (QRQ: nobody behind the enemy, so the insec kick, and the chase
    while it flies); a cut; R with Q ready against Yasuo with Jinx behind him (RQQ: the forward kick, the palm, the
    homing wave that meets him in the air, the dash)."""
    lee = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H, gy = 320, 104, 62
    body, effects, shots, labels = [], [], [], []
    knockup = frames_of(fx["league_leesin_fx"], "knockup")
    dragon = frames_of(fx["league_leesin_r"], "dragon")

    def anim(tag, t0, x, dur=None, x1=None, move=None, flip=False, loop=False):
        an = Anim(frames_of(lee, tag), t0, x, gy, loop=loop, until=None if dur is None else t0 + dur, x1=x1, flip=flip)
        if move is not None:
            an.move0, an.until_move = move
        body.append(an)
        return an.until

    def fx_at(tag, at, x=0, y=None, sprite="league_leesin_fx", z_=1, on=None):
        fr = frames_of(fx[sprite], tag)
        effects.append(Follow2(fr, at, on, z=z_) if on else Anim(fr, at, x, gy if y is None else y, z=z_))

    def chase(t0, x, speed, foe, side):
        """A homing dash from x at speed px a tick: (arrival, where it stops) at side px from the moving foe."""
        k = 0
        while True:
            k += 1
            goal = foe.pos(t0 + tick(k))[0] + side
            x = max(goal, x - speed) if x > goal else min(goal, x + speed)
            if x == goal:
                return t0 + tick(k), x

    # ---- scene 1: Q, Q2, QQAE, QRQ against Darius
    darius = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), 120, gy)
    x = 40
    q0 = anim("idle", 0, x, dur=400, loop=True)
    anim("skill", q0, x)
    w0 = q0 + tick(16)
    w1 = w0 + tick((darius.x - 6 - (x + 10)) / 4.5)
    shots.append(Anim(frames_of(fx["league_leesin_fx"], "q_wave"), w0, x + 10, gy - 2, loop=True, until=w1,
                      x1=darius.x - 6, y1=gy - 2, z=1))
    fx_at("q_mark", w1, on=darius, z_=2)
    darius.flinches.append(w1)
    d0 = w1 + tick(12)                                # Q2: 12 ticks after the hit, 5000 a tick
    body[-1].until = min(body[-1].until, d0)
    dest = darius.x - 22
    d1 = d0 + tick((dest - x) / 5.0)
    t = anim("q2", d0, x, dur=tick(31), x1=dest, move=(d0, d1))
    fx_at("q2_hit", d1, on=darius)
    darius.flinches.append(d1)
    x = dest
    e0 = t + tick(4)                                  # E inside the window: the punch first
    anim("idle", t, x, dur=e0 - t, loop=True)
    anim("attack", e0, x, dur=tick(20))
    fx_at("hit", e0 + tick(12), darius.x - 4, gy - 4)
    darius.flinches.append(e0 + tick(12))
    anim("skill2", e0 + tick(21), x, dur=tick(40))
    fx_at("e_wave", e0 + tick(38), x, gy, z_=-1)
    darius.flinches.append(e0 + tick(38))
    t = e0 + tick(61)
    r0 = t + tick(6)                                  # R, Q still on cooldown: QRQ
    anim("idle", t, x, dur=r0 - t, loop=True)
    behind = darius.x + 15                            # nobody behind him: the insec, rushing through at 8000
    body.append(Anim(frames_of(lee, "ult"), r0, x, gy, until=r0 + tick(7)))
    ult = Anim(frames_of(lee, "ult"), r0, x, gy, until=r0 + tick(27), x1=behind, flip=True)
    ult.move0, ult.until_move = r0 + tick(7), r0 + tick(7) + tick((behind - x) / 8.0)
    body.append(ult)
    kick = r0 + tick(19)
    fx_at("kick", kick, darius.x, gy - 4, sprite="league_leesin_r")
    darius.slides.append((kick, kick + tick(18), -54))
    darius.flinches.append(kick)
    back = [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in dragon]
    shots.append(Anim(back, kick + tick(4), behind, gy - 2, loop=True, until=kick + tick(4) + tick(35 / 2.5),
                      x1=behind - 35, y1=gy - 2, z=1))
    up = r0 + tick(25)                                # the dragon passes him: knocked up as he flies
    darius.hops.append((up, up + tick(45), 8))
    effects.append(Follow2(knockup, up, darius))
    c0 = r0 + tick(27)                                # the chase: q2's pose, 7000 a tick, homing
    c1, cx = chase(c0, behind, 7.0, darius, 22)
    anim("q2", c0, behind, dur=tick(31), x1=cx, move=(c0, c1), flip=True)
    fx_at("q2_hit", c1, on=darius)
    darius.flinches.append(c1)
    t = c0 + tick(31)
    anim("idle", t, cx, dur=900, loop=True, flip=True)
    labels += [(q0, e0, "Q > Q2"), (e0, r0, "Q Q A E"), (r0, t + 900, "Q R Q")]
    cut = t + 900

    # ---- scene 2: RQQ against Yasuo, Jinx behind him
    yasuo = Foe(load(os.path.join(LEAGUE, "champions", "league_yasuo")), 112, gy)
    jinx = Foe(load(os.path.join(LEAGUE, "champions", "league_jinx")), 178, gy - 10)
    x, t = 70, cut + 160
    r0 = anim("idle", t, x, dur=500, loop=True)
    front = yasuo.x - 22                              # Jinx behind him: the forward kick
    body.append(Anim(frames_of(lee, "ult"), r0, x, gy, until=r0 + tick(7)))
    ult = Anim(frames_of(lee, "ult"), r0, x, gy, until=r0 + tick(24), x1=front)
    ult.move0, ult.until_move = r0 + tick(7), r0 + tick(7) + tick((front - x) / 8.0)
    body.append(ult)
    kick = r0 + tick(19)
    fx_at("kick", kick, yasuo.x, gy - 4, sprite="league_leesin_r")
    yasuo.slides.append((kick, kick + tick(18), 54))
    yasuo.flinches.append(kick)
    yasuo.hops.append((kick, kick + tick(45), 8))
    effects.append(Follow2(knockup, kick, yasuo))
    shots.append(Anim(dragon, kick, front, gy - 2, loop=True, until=kick + tick(63 / 3.0), x1=front + 63, y1=gy - 2,
                      z=1))
    reach = kick + tick(max(0.0, (jinx.x - 20 - front) / 3.0))
    jinx.hops.append((reach, reach + tick(45), 10))
    jinx.flinches.append(reach)
    effects.append(Follow2(knockup, reach, jinx))
    p0 = r0 + tick(24)                                # the palm, the wave on tick 28 (8000 a tick, homing)
    anim("q_throw", p0, front, dur=tick(20))
    w0 = r0 + tick(28)
    w1, wx = chase(w0, front + 10, 8.0, yasuo, -6)
    shots.append(Anim(frames_of(fx["league_leesin_fx"], "q_wave"), w0, front + 10, gy - 2, loop=True, until=w1,
                      x1=wx, y1=gy - 2, z=1))
    fx_at("q_mark", w1, on=yasuo, z_=2)
    yasuo.flinches.append(w1)
    d0 = w1 + tick(8)                                 # the dash 8 ticks after the hit
    if d0 > p0 + tick(20):
        anim("idle", p0 + tick(20), front, dur=d0 - p0 - tick(20), loop=True)
    d1, dx = chase(d0, front, 7.0, yasuo, -22)
    t = anim("q2", d0, front, dur=tick(31), x1=dx, move=(d0, d1))
    fx_at("q2_hit", d1, on=yasuo)
    yasuo.flinches.append(d1)
    anim("idle", t, dx, dur=1200, loop=True)
    labels.append((r0, t + 1200, "R Q Q"))
    return film(out, W, H, t + 1200, body, effects, shots, lambda tt: (darius,) if tt < cut else (jinx, yasuo),
                cut=(cut, cut + 160), labels=labels, z=z, step=step)


def place(img, f, px, py):
    img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))


def body_pos(an, tt):
    if getattr(an, "until_move", None) is None:
        return an.pos(tt)
    m0 = getattr(an, "move0", an.t0)                  # the R rush starts 7 ticks into the cast
    u = min(1.0, max(0.0, (tt - m0) / max(1e-6, an.until_move - m0)))
    return int(round(an.x + (an.x1 - an.x) * u)), an.y


def film(out, W, H, end, body, effects, shots, foes, cut=None, labels=(), z=3, step=40):
    """Draw the clip: ground effects, the foes (foes(tt)), Lee Sin's first playing animation, the other effects and
    projectiles; cut = (t0, t1) of an empty arena between scenes; labels = [(t0, t1, text)] in a corner."""
    font = ImageFont.load_default(size=8 * z) if labels else None
    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in effects:                            # ground effects under the units
            f = an.frame(tt)
            if f is not None and an.z < 0:
                place(img, f, *an.pos(tt))
        if cut and cut[0] <= tt < cut[1]:             # the cut: an empty arena between the scenes
            frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
            tt += step
            continue
        for fo in foes(tt):
            place(img, fo.frame(tt), *fo.pos(tt))
        for an in body:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *body_pos(an, tt))
                break
        for an in effects + shots:
            f = an.frame(tt)
            if f is not None and an.z >= 0:
                place(img, f, *an.pos(tt))
        img = img.resize((W * z, H * z), Image.NEAREST).convert("RGB")
        for t0, t1, text in labels:
            if t0 <= tt < t1:
                ImageDraw.Draw(img).text((4 * z, 2 * z), text, font=font, fill=(255, 236, 160),
                                         stroke_width=z // 2 + 1, stroke_fill=(24, 20, 16))
        frames.append(img)
        tt += step
    sample = frames[::6]                              # one palette for the whole clip
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_leesin_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_leesin_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_leesin_showcase.gif")))
    print("combos frames/seconds", combos(os.path.join(args.out, "league_leesin_combos.gif")))


if __name__ == "__main__":
    main()
