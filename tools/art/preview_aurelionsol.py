#!/usr/bin/env python3
"""Preview images for Aurelion Sol, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_aurelionsol.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_aurelionsol_frames.png    every animation's dense frames (hd_, PPU 1.75, as league.dll shows them)
  league_aurelionsol_effects.png   every effect animation, 3x
  league_aurelionsol_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_aurelionsol.py, 60
                                   ticks a second): Aurelion Sol flies in and throws two stars; Singularity (the seed
                                   flying, the black hole on the ground, the core crushing Darius, the slow) and at
                                   once the breath on him (E -> Q: Breath of Light, the beam's segments every q_p
                                   ticks, the sear on him, stardust drawn in); Falling Star (the star called over his
                                   head, the star coming down, the impact and the stun) and the black hole on the
                                   same spot (R -> E); the stardust full (the Skies charged, the stars over his
                                   head); The Skies Descend (the giant star, Darius knocked up, the shockwave); Darius
                                   falls and he takes flight (takedown -> Astral Flight: the lift, the stardust
                                   stream); 3x.
  league_aurelionsol_skills.gif    each skill and combo alone with its effects, captioned in Chinese, 4x (the user,
                                   2026-10-24: 「带技能的gif图呢？」)
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows  # noqa: E402
from preview_garen import T, contact, frames_of, load  # noqa: E402
from preview_gnar import Clip  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe  # noqa: E402
from build_aurelionsol import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_aurelionsol")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_aurelionsol_fx", "league_aurelionsol_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Sol(Clip):
    """preview_gnar's clip with his own dense frames, facing left after he turns (flip)."""

    flip = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "aurelionsol", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None, flip=self.flip)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def fly(self, tag, t0, t1, x0, x1, y0, y1=None, sheet=None):
        """A projectile's picture flying from (x0, y0) to (x1, y1) (drawn flying right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y0, loop=True, until=t1, x1=x1,
                              y1=y0 if y1 is None else y1, flip=x1 < x0))

    def on_ground(self, tag, when, sheet=None, until=None):
        """A picture on the ground under Darius (under the units)."""
        self.under.append(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: the black hole, the star, the impact)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


# the fight's steps in order (showcase); skills() plays some of them alone
FIGHT = ["fly_in", "attack", "eq", "re", "sky", "kill"]


def showcase(out, z=3, steps=FIGHT, W=300, H=150, gap=150, tail=1200):
    """The scripted fight (or some of its steps: skills() plays each skill alone) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_aurelionsol_fx"], fx["league_aurelionsol_big"]
    gy = H - 32
    x0 = 30
    far = x0 + gap                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Sol(load(CHAMP), d, me, small, big)
    c.wait(300)
    state = {}

    def flight(x1, haste=0):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / (px_ms(P["ms"]) * (1 + haste / 100))
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    def gain(when):
        c.on_me("d_gain", when)

    def stars(n):
        for _ in range(n):
            t = c.t
            c.a("attack", tick(P["atk_dur"]))
            rel = t + tick(P["a_rel"] - 1)
            x = me.pos(rel)[0]
            hit = rel + abs(d.pos(rel)[0] - x) / px_ms(P["a_speed"])
            c.fly("a_bolt", rel, hit, x + 8, d.pos(rel)[0], gy + P["a_y"] / 1000)
            c.on("a_hit", hit)
            d.flinches.append(hit)

    def breath(ticks=None):
        """Breath of Light: the channel (q_t, or q_t_f in flight), a beam segment every q_p ticks from q_rel, the sear."""
        ticks = ticks or P["q_t"]
        t = c.t
        c.a("skill", tick(ticks), loop=ticks > P["q_t"])
        x = me.pos(t)[0]
        y = gy + P["q_y"] / 1000
        for k in range(0, ticks - P["q_rel"], P["q_p"]):
            go = t + tick(P["q_rel"] - 1 + k)
            end = go + P["q_len"] / 1000 / px_ms(P["q_speed"])
            c.fly("q_beam", go, end, x, x + P["q_len"] / 1000, y)
            hit = go + abs(d.pos(go)[0] - x) / px_ms(P["q_speed"])
            if d.death is None or hit < d.death:
                c.on("q_hit", hit)
                d.flinches.append(hit)
            if k == 0:
                gain(hit)

    def hole(when, x):
        """The black hole on the ground at x for e_t: the core on him every e_cp, the slow while he is in it."""
        c.at("e_hole", when, x, gy, sheet=big, under=True)
        for k in range(P["e_cp"], P["e_t"], P["e_cp"]):
            c.on("e_core", when + tick(k))
        c.on_ground("slow", when, until=when + tick(P["e_t"]))
        gain(when + tick(60))

    def singularity():
        """Singularity: the seed lobbed onto him, the black hole there (-> its landing time)."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        rel = t + tick(P["e_rel"] - 1)
        land = rel + tick(P["e_fly"])
        c.fly("e_orb", rel, land, me.pos(rel)[0] + 8, d.pos(rel)[0], gy - 12, gy)
        hole(land, d.pos(land)[0])
        return land

    def star(skies=False):
        """Falling Star (or The Skies Descend): the call over his head, the star coming down on him, the impact (->
        the landing time and spot)."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        rel = t + tick(P["r_rel"] - 1)
        c.on_me("r_call", rel)
        spot = d.pos(rel)[0]
        c.at("r_fall", rel, spot, gy, sheet=big)
        land = rel + tick(P["r_fall"])
        c.on("r_hit", land)
        if skies:
            c.at("r_sky", land, spot, gy, sheet=big, under=True)
            d.hops.append((land, land + tick(P["r_up"]), 12))
            wave = land + tick(P["r_wave_at"])
            c.at("r_wave", wave, spot, gy, sheet=big, under=True)
            c.on_ground("slow", wave, until=wave + tick(P["r_wslow_t"]))
        else:
            c.at("r_impact", land, spot, gy, sheet=big, under=True)
            d.flinches += [land + k * 100 for k in range(int(tick(P["r_stun"]) // 100))]
        gain(land + 100)
        return land, spot, rel

    for step in steps:
        if step == "fly_in":            # he flies in (his run: League's flight)
            flight(me.pos(c.t)[0] + 70)
        elif step == "attack":          # two stars flung
            stars(2)
        elif step == "q":               # Breath of Light alone
            breath()
        elif step == "e":               # Singularity alone
            land = singularity()
            c.wait(max(0, land + tick(P["e_t"]) - c.t - 2000))
        elif step == "eq":              # Singularity, then the breath on the one caught at once (E -> Q)
            land = singularity()
            c.t = max(c.t, land + tick(3))
            breath()
        elif step == "r":               # Falling Star alone
            land, _, _ = star()
            c.t = max(c.t, land + tick(P["r_stun"]))
        elif step == "re":              # Falling Star, then the black hole on its spot at once (R -> E)
            land, spot, _ = star()
            hole(land + tick(1), spot)
            c.t = max(c.t, land + tick(P["r_stun"]))
            c.wait(600)
        elif step == "sky":             # the stardust full: the Skies charged, the stars over his head; The Skies Descend
            t_sky = c.t
            c.on_me("sky_ready", t_sky)
            c.wait(700)
            glow = c.t - 300
            _, _, rel = star(skies=True)
            c.on_me("sky_glow", glow, until=rel)
            c.wait(400)
        elif step == "kill":            # a takedown lifts him into flight (the lift, the stardust stream, the breath
            d.death = c.t + 60          # without cooldown in it)
            c.wait(300)
            t = c.t
            c.on_me("w_lift", t)
            c.flip = True
            flight(me.pos(c.t)[0] - 40, haste=P["w_ms"])
            c.on_me("w_trail", t, under=True, until=c.t)
            c.flip = False
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：悬浮飞行（英雄联盟里他一直是飞着走的）", ["fly_in"], 150, 150),
          ("普攻：爪子一挥甩出一颗星星", ["attack"], 70, 150),
          ("技能1 星河冲荡：引导龙息 1.5 秒，一段段连成光流，命中英雄收集星尘", ["q"], 70, 150),
          ("技能2 星芒凝汇：黑洞种子落地张开黑洞，持续伤害、往中心拉、减速，中心吞噬", ["e"], 75, 150),
          ("连招 E→Q：黑洞一困住英雄，立刻对他喷龙息（被拉住的吃更多伤害）", ["eq"], 75, 150),
          ("大招 星落：头顶聚起星座，星星笔直坠下砸中目标，眩晕 1 秒", ["r"], 90, 230),
          ("连招 R→E：星落砸下，落点立刻张开黑洞，先晕后拉", ["re"], 90, 230),
          ("连招 星尘满→天瀑：星环亮起、头顶绕着小星星；巨星砸地击飞，外圈冲击波减速", ["sky"], 90, 230),
          ("连招 击杀→飞行：敌方英雄阵亡，他起飞加速，身下拖着星尘", ["kill"], 70, 150)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        showcase(path, z=z, steps=steps, W=200, H=h, gap=gap, tail=900)
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
    sample = Image.new("RGB", (W, H * 6))
    for i, (img, _) in enumerate(out_frames[::max(1, len(out_frames) // 6)][:6]):
        sample.paste(img, (0, i * H))
    pal = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [img.quantize(palette=pal, dither=Image.Dither.NONE) for img, _ in out_frames]
    q[0].save(out, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in out_frames], loop=0)
    return len(q), round(sum(ms for _, ms in out_frames) / 1000, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase", "skills"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_aurelionsol_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[19:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_aurelionsol_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_aurelionsol_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_aurelionsol_skills.gif")))


if __name__ == "__main__":
    main()
