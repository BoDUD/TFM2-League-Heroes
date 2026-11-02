#!/usr/bin/env python3
"""Preview images for the Crimson Raptor (the tft pack), built from the exported game sprites (so they also prove the
sheets load).

    python tools/art/preview_raptor.py [--out docs/preview] [--only frames|effects|skills]

  tft_raptor_frames.png    every animation's dense frames (hd_, PPU 1.56, as league.dll shows them)
  tft_raptor_effects.png   every effect animation, 3x
  tft_raptor_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                           (tools/kit/build_raptor.py, 60 ticks a second) and as tft.dll plays its parts
                           (addons/tft/src/raptor.rs), captioned in Chinese, 4x (preview_sentinel.py's way): the walk;
                           Feather Shot (the feather, its hit, Orange Buff's cracked armour on the target); Feather Fan
                           (five blade feathers in a fan, each stopping at the first enemy on its line - the preview
                           draws them unturned, the game turns them with their flight); Startled Hop (the puff it hops
                           from, the frenzy round it, two quick attacks); Flock Family (the four Tiny Beaks round it,
                           each attack followed by their four pecks).
"""
import argparse
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows  # noqa: E402
from preview_garen import T, contact, frames_of, load  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me  # noqa: E402
import preview_zoe as Z  # noqa: E402
from preview_silco import Clip as SilcoClip, px_tick  # noqa: E402
from build_raptor import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_raptor")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_raptor_fx", "tft_raptor_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it attacks
SPOTS = ((22, -10), (34, 12))    # Garen and Ashe behind Darius (game px), off the middle line: the fan's outer feathers
MOUTH = (8, -12)                 # where its feathers leave (game px from its pivot: the beak)
UNIT_R = 10                      # a unit's own radius (game px) on top of a feather's half width


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "raptor", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        if dur and not loop and dur < sum(ms for _, ms in fr):   # a shorter play: every frame shorter alike
            k = dur / sum(ms for _, ms in fr)
            fr = [(f, ms * k) for f, ms in fr]
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def line(self, tag, t0, t1, x0, y0, x1, y1):
        """A projectile's picture from (x0, y0) to (x1, y1), unturned."""
        self.over.append(Anim(frames_of(self.small, tag), t0, int(x0), int(y0), loop=True, until=t1, x1=int(x1),
                              y1=int(y1)))


def scene(out, steps, gap, W=360, H=170, z=4, tail=900, x0=90):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_raptor_fx"], fx["tft_raptor_big"]
    gy = H - 40
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    foes = (d,)
    if "q" in steps:                                               # two more enemies on the fan's outer lines
        foes = (d,) + tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
        c.foes = foes[1:]
    c.wait(300)
    flock = {"until": -1}

    def shred(f, at):
        """Orange Buff: the cracked armour over the struck, p_t long."""
        c.on_foe(f, "p_shred", at, until=at + tick(P["p_t"]))

    def shot(cd=None):
        """One attack: the feather on a_rel, homing to Darius at a_speed; the Tiny Beaks' pecks after it while the
        flock is out."""
        rel = c.t + tick(P["a_rel"] - 1)
        x, y = me.pos(rel)
        x0_, x1_ = x + MOUTH[0], d.pos(rel)[0]
        hit = rel + tick((x1_ - x0_) * 1000.0 / P["a_speed"])
        c.fly("a_bolt", rel, hit, x0_, x1_, y + MOUTH[1])
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        shred(d, hit)
        if rel < flock["until"]:
            for k in range(1, P["r_n"] + 1):
                t = rel + tick(k * P["r_gap"])
                h = t + tick((x1_ - x0_) * 1000.0 / P["r_speed"])
                dy = (-6, 4, -2, 8)[k - 1]                         # the chicks dive from round it
                c.line("r_peck", t, h, x0_ - 6, y + MOUTH[1] + dy, x1_, y - 14)
                c.on_foe(d, "r_peck_hit", h)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick((cd or P["atk_cd"]) - P["atk_dur"]))

    def fan():
        """Feather Fan: on q_rel, q_n feathers q_spread degrees apart toward Darius, each to the first enemy within its
        half width (and a unit's radius) of its line, else to q_len."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        at = t + tick(P["q_rel"] - 1)
        x, y = me.pos(at)
        ox, oy = x + MOUTH[0], y + MOUTH[1]
        reach = P["q_len"] / 1000
        for k in range(P["q_n"]):
            a = math.radians((k - (P["q_n"] - 1) / 2) * P["q_spread"])
            dx, dy = math.cos(a), math.sin(a)
            best = None
            for f in foes:
                fx_, fy_ = f.pos(at)[0] - ox, (f.pos(at)[1] - 14) - oy
                along, off = fx_ * dx + fy_ * dy, abs(fx_ * dy - fy_ * dx)
                if 0 <= along <= reach and off <= P["q_w"] / 1000 + UNIT_R and (best is None or along < best[0]):
                    best = (along, f)
            dist = best[0] if best else reach
            end = at + tick(dist * 1000.0 / P["q_speed"])
            c.line("q_feather", at, end, ox, oy, ox + dx * dist, oy + dy * dist)
            if best:
                c.on_foe(best[1], "q_hit", end)
                best[1].flinches.append(end)
                shred(best[1], end)
        return at + tick(reach * 1000.0 / P["q_speed"])

    def hop():
        """Startled Hop: on e_rel the puff where it stood and the hop straight back (e_back x e_back_t), then the frenzy
        for e_t (shown 1.6 s) with two quick attacks."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_rel"] - 1)
        x, y = me.pos(at)
        c.at_spot("e_jump", at, x, y, sheet=c.small, under=True)
        back = P["e_back"] * P["e_back_t"] / 1000
        me.moves.append((at, at + tick(P["e_back_t"]), x, x - back))
        rush = at + tick(P["e_back_t"])
        c.on_me("e_rush", rush, until=rush + 1600)
        cd = P["atk_cd"] * 100 / (100 + P["e_as"])
        shot(cd)
        shot(cd)
        return rush + 1600

    def call():
        """Flock Family: on r_rel the four Tiny Beaks round it for r_t (shown 2.6 s), two attacks with their pecks."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        at = t + tick(P["r_rel"] - 1)
        flock["until"] = at + 2600
        c.on_me("r_flock", at, sheet=c.big, until=flock["until"])
        shot()
        shot()
        return flock["until"]

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            shot()
            shot()
        elif step == "q":
            end = fan()
            c.wait(max(0, end + 300 - c.t))
        elif step == "e":
            end = hop()
            c.wait(max(0, end + 200 - c.t))
        elif step == "r":
            end = call()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：小步快跳，两条腿轮流迈", ["walk_in"], 200, 160),
          ("普攻 锋羽射击：甩出一根锋羽；被动 橙霸符：物理伤害减护甲（头顶裂开的橙盾）", ["attack"], REACH, 160),
          ("技能1 羽刃扇射：张开翅膀，扇形甩出五根羽刃，每根命中第一个敌人", ["q"], REACH, 190),
          ("技能2 惊飞跃退：受惊往后一跳（起跳的尘土），之后攻速大涨（身边的速度线）", ["e"], REACH, 160),
          ("大招 鸟群之家：召唤四只小锋喙鸟围在身边，每次普攻它们一起扑上去啄同一个敌人", ["r"], REACH, 170)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        scene(path, steps, gap, H=h, z=z)
        for f in ImageSequence.Iterator(Image.open(path)):
            frames.append((cap, f.convert("RGB").copy(), f.info.get("duration", 40)))
    W = max(f.width for _, f, _ in frames)
    H = max(f.height for _, f, _ in frames) + 26
    out_frames = []
    for cap, f, ms in frames:
        img = Image.new("RGB", (W, H), (40, 40, 40))
        img.paste(f, (0, 26 + H - 26 - f.height))
        ImageDraw.Draw(img).text((6, 3), cap, fill=(240, 240, 240), font=font)
        out_frames.append((img, ms))
    sample = Image.new("RGB", (W, H * 8))
    for i, (img, _) in enumerate(out_frames[::max(1, len(out_frames) // 8)][:8]):
        sample.paste(img, (0, i * H))
    pal = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [img.quantize(palette=pal, dither=Image.Dither.NONE) for img, _ in out_frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in out_frames], loop=0)
    return len(q), round(sum(ms for _, ms in out_frames) / 1000, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "skills"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_raptor_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_raptor_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_raptor_skills.gif")))


if __name__ == "__main__":
    main()
