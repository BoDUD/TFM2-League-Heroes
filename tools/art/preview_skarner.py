#!/usr/bin/env python3
"""Preview images for Skarner, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_skarner.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_skarner_frames.png    every animation's dense frames (hd_, PPU 1.75, as league.dll shows them)
  league_skarner_effects.png   every effect animation, 3x
  league_skarner_showcase.gif  a scripted fight with Darius, timed like the kit, 3x: Ixtal's Impact from afar (the
                               charge, the carry, the slam, Seismic Bastion) gives the boulder at once (E -> Q); a
                               splashing blows; Darius runs for it: Impale with the boulder up throws Upheaval first (R ->
                               Upheaval), the stingers catch him down the line, drag him back and set him quaking at
                               once (R -> Quaking); blows, Darius swings back and runs again;
                               the throw brought Ixtal's Impact back within 4 s (Q -> E): it catches him, he falls.
  league_skarner_skills.gif    each skill and combo alone with its effects against Darius, timed like the kit
                               (tools/kit/build_skarner.py, 60 ticks a second), captioned in Chinese, 4x: the scuttle;
                               stinger blows; Shattered Earth (the boulder dug up and held over his back, three blows
                               splashing, the third slowing); Upheaval (held too long: thrown); Ixtal's Impact (the
                               charge, the carry, the slam and stun, Seismic Bastion's bounce, quake and shield); E -> Q
                               (the boulder at once after the carry); Impale (the three stingers down the line, the
                               suppression and the drag, his haste, Quaking at full); R with the boulder up (Upheaval
                               thrown first); Quaking (three hits: the tremor and the burning ground).
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
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_skarner import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_skarner")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_skarner_fx", "league_skarner_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
REACH = 25                       # game px between his pivot and Darius's when he strikes (atk_range 25000)


def px_tick(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


class Arc(Anim):
    """A lobbed picture: from (x, y) to (x1, y1) in a parabola `h` px high."""

    def __init__(self, fr, t0, x, y, x1, t1, h=18):
        super().__init__(fr, t0, x, y, loop=True, until=t1, x1=x1, y1=y)
        self.h = h

    def pos(self, t):
        x, y = super().pos(t)
        u = min(1.0, max(0.0, (t - self.t0) / (self.until - self.t0)))
        return x, int(round(y - 4 * self.h * u * (1 - u)))


class Skarner(Clip):
    """preview_gnar's clip with his own dense frames, effects on him, on Darius, left on the ground, flying."""

    z = 4                                               # the clip's zoom: his dense frames drawn at it

    def a(self, tag, dur=None, loop=False):
        fr = list(dense(self.sp, tag, "skarner", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def on_him(self, tag, when, sheet=None, until=None, under=False):
        (self.under if under else self.over).append(OnMe(frames_of(sheet or self.small, tag), when, self.me,
                                                         until=until))

    def at(self, tag, when, x, y, sheet=None, under=False):
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y))

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y, loop=True, until=t1, x1=x1, y1=y))

    def lob(self, tag, t0, t1, x0, x1, y, sheet=None):
        self.over.append(Arc(frames_of(sheet or self.small, tag), t0, x0, y, x1, t1))


def scene(out, steps, gap, W=260, H=150, z=4, tail=900, x0=70):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_skarner_fx"], fx["league_skarner_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Skarner(load(CHAMP), d, me, small, big)
    c.z = z
    st = {"qk": 0, "quaking": -1.0, "rock": None, "thrown": 0}
    c.wait(300)

    def quake_hit(when, full=False):
        """Quaking: a champion hit climbs the stacks (his), the third - or Impale - sets Darius quaking."""
        if when < st["quaking"]:
            return
        st["qk"] = 3 if full else st["qk"] + 1
        if st["qk"] >= 3:
            st["qk"] = 0
            st["quaking"] = when + tick(P["p_t"])
            c.on_foe("p_burst", when)
            c.on_foe("p_quake", when, until=st["quaking"], under=True)

    def rock_shown(t0):
        """The boulder over his back from the pickup's end until it is spent (the kit's rock_v)."""
        st["rock"] = t0 + tick(P["q_dur"])

    def rock_spent(when):
        if st["rock"] is not None:
            c.on_him("q_held", st["rock"], sheet=big, until=when)
            st["rock"] = None

    def blow(k=None):
        """A stinger blow; holding the boulder (k = its 1st, 2nd, 3rd) the claw strikes instead (attack_rock: the tails
        keep it up) and it splashes, the third slowing and spending it."""
        t = c.t
        dur = P["atk_dur"]
        c.a("attack_rock" if k is not None else "attack", tick(dur))
        b = t + tick(P["a_hit"] - 1)
        c.on("a_hit", b)
        d.flinches.append(b)
        if k is not None:
            c.on("q_hit", b + 20)
            if k == 3:
                c.on_foe("slow", b, until=b + tick(P["q_slow_t"]), under=True)
                rock_spent(b)
        quake_hit(b)
        cd = P["atk_cd"] / (1 + P["q_as"] / 100) if st["rock"] is not None else P["atk_cd"]
        c.wait(tick(cd - dur))

    def pickup():
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        rock_shown(t)

    def toss():
        """Upheaval: the boulder high, thrown on the throw frame, lobbed onto Darius."""
        t = c.t
        rock_spent(t)
        c.a("skill_toss", tick(P["q_toss"]))
        rel = t + tick(P["q_toss_rel"] - 1)
        land = rel + tick(P["q_travel"])
        x, y = me.pos(rel)
        c.lob("q_rock", rel, land, x + 10, d.pos(land)[0], y - 20)
        c.at("q_land", land, d.pos(land)[0], gy)
        c.on("q_hit", land)
        d.flinches.append(land)
        c.on_foe("slow", land, until=land + tick(P["q_slow_t"]), under=True)
        quake_hit(land)

    def walk(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_tick(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    def impact(kill=False):
        """Ixtal's Impact: the charge while he runs in, the grab and the carry from the contact, the slam and stun (or
        Darius falling: kill); Seismic Bastion's bounce, quake and shield at the carry's end."""
        t = c.t
        xa = me.pos(t)[0]
        xc = d.pos(t)[0] - REACH
        reach_t = t + abs(xc - xa) / px_tick(P["e_speed"])
        me.moves.append((t, reach_t, xa, xc))
        c.a("skill2", reach_t - t, loop=True)
        c.on("e_hit", reach_t)
        carry = px_tick(P["e_kb_speed"]) * tick(P["e_kb_t"])
        c.a("grab", tick(P["e_kb_t"]))
        end = c.t
        d.slides.append((reach_t, end, carry))
        me.moves.append((reach_t, end, xc, xc + carry))
        c.on("e_slam", end)
        if kill:
            d.death = end
        else:
            d.flinches.append(end)
            c.on_foe("stun", end, until=end + tick(P["e_stun"]))
        t = c.t
        c.a("w", tick(P["w_dur"]))
        q = t + tick(P["w_rel"] - 1)
        x = me.pos(q)[0]
        c.at("w_quake", q, x, gy, sheet=big, under=True)
        c.on("w_hit", q + 20)
        c.on_foe("slow", q, until=q + tick(P["w_slow_t"]), under=True)
        c.on_him("w_shield", q, until=q + tick(P["w_sh_t"]))

    def stop_run(when):
        """Darius caught while running for it: his run (and the slide that carries it) cut at `when`."""
        for k, (t0, t1) in enumerate(d.runs):
            if t0 <= when < t1:
                d.runs[k] = (t0, when)
                for j, (s0, s1, dx) in enumerate(d.slides):
                    if s0 == t0 and s1 == t1:
                        d.slides[j] = (s0, when, dx * (when - s0) / (s1 - s0))

    def impale():
        """Impale: the stingers down the line (catching Darius where he is by then, running or not), the suppression
        and the drag toward him, his haste, Quaking full; with the boulder up, Upheaval first."""
        t = c.t
        rock_up = st["rock"] is not None
        c.a("ult", tick(P["r_dur"]))
        rel = t + tick(P["r_rel"] - 1)
        x, y = me.pos(rel)
        sp = px_tick(P["r_speed"])
        hit = rel
        while x + 8 + (hit - rel) * sp < d.pos(hit)[0] - 8:
            hit += 5
        stop_run(hit)
        stop = rel + P["r_len"] / 1000.0 / sp
        c.fly("r_spike", rel, stop, x + 8, x + 8 + P["r_len"] / 1000.0, y - 8, sheet=big)
        c.on("r_hit", hit)
        d.flinches.append(hit)
        held = hit + tick(P["r_sup"])
        c.on_foe("r_held", hit, until=held)
        pull = d.pos(hit)[0] - (me.pos(hit)[0] + REACH)
        if pull > 0:
            d.slides.append((hit, hit + pull / px_tick(P["r_grab"]) * (P["r_drag"] / 2.0), -pull))
        if rock_up:                                     # Upheaval thrown first, as he starts the lash
            rock_spent(t)
            land = t + tick(P["q_travel"])
            x0, y0 = me.pos(t)
            c.lob("q_rock", t, land, x0 + 10, d.pos(land)[0], y0 - 20)
            c.at("q_land", land, d.pos(land)[0], gy)
            c.on("q_hit", land)
            d.flinches.append(land)
            quake_hit(land)
            st["thrown"] = land
        quake_hit(hit, full=True)
        c.on_him("r_haste", hit, until=hit + tick(P["r_ms_t"]), under=True)
        return held

    for step in steps:
        if step == "walk_in":
            walk(far - REACH)
        elif step == "attack":
            blow()
            blow()
        elif step == "q3":                  # the boulder and its three splashing blows
            pickup()
            for k in (1, 2, 3):
                blow(k)
        elif step == "q_toss":              # held past q_hold: thrown
            pickup()
            c.wait(tick(P["q_hold"] - P["q_dur"]))
            toss()
            c.wait(600)
        elif step == "e":
            impact()
            c.wait(700)
        elif step == "e_q":                 # the carry's end gives the boulder at once (E -> Q)
            impact()
            pickup()
            blow(1)
        elif step == "r":
            impale()
            c.wait(800)
        elif step == "q_r":                 # R with the boulder up: Upheaval first
            pickup()
            c.wait(200)
            impale()
            c.wait(800)
        elif step == "fight":               # the showcase: every combo in one fight
            impact()                        # the engage from afar: charge, carry, slam, bastion
            pickup()                        # E -> Q: the boulder at once
            blow(1)
            blow(2)
            t0 = c.t + 100                  # Darius runs for it
            d.runs.append((t0, t0 + 1500))
            d.slides.append((t0, t0 + 1500, 90))
            c.wait(t0 + 450 - c.t)
            free = impale()                 # R with the boulder up: Upheaval first; the stingers catch him, drag him
            c.wait(max(0, free - c.t))      # back; Quaking full
            blow()
            d.attacks.append(c.t + 60)      # free again: he swings back
            blow()
            t0 = c.t + 150                  # and runs again
            d.runs.append((t0, t0 + 750))
            d.slides.append((t0, t0 + 750, 42))
            # the throw on a champion brought Ixtal's Impact back within e_cut ticks: it catches him
            c.wait(max(t0 + 750, st["thrown"] + tick(P["e_cut"])) - c.t)
            impact(kill=True)
            print("fight: E again", round(c.t / 1000, 2), "s; ready from", round((st["thrown"] + tick(P["e_cut"])) / 1000, 2))
        elif step == "quake":               # three blows: the third sets him quaking
            for _ in range(3):
                blow()
            c.wait(1200)
    rock_spent(c.t + tail)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


def showcase(out):
    """The scripted fight (every combo in play), 3x."""
    return scene(out, ["fight"], 90, W=320, H=160, z=3, tail=1500, x0=30)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：六条腿爬行，三根尾巴竖在背上", ["walk_in"], 150, 150),
          ("普攻：三根尾巴的水晶毒刺往前扎", ["attack"], REACH, 150),
          ("技能1 撼地：从地里掘出巨石举在背上，接下来 3 下普攻带溅射，第 3 下打最大生命值并减速", ["q3"], REACH, 170),
          ("技能1 擎天：举着巨石太久就把它扔出去，砸中的地方溅射、减速", ["q_toss"], 90, 170),
          ("技能2 以绪塔尔冲击：冲锋撞上英雄拖着走，停下砸晕；被动 震地壁垒：跳起砸地，护盾 + 地震波减速", ["e"], 110, 170),
          ("连招 冲锋拖完人 → 撼地马上转好", ["e_q"], 110, 170),
          ("大招 毒刺贯体：三根毒刺往前扎，压制并拖到身边，自己加速；被扎中的人战栗直接叠满", ["r"], 60, 170),
          ("连招 举着巨石放大招 → 先扔出擎天", ["q_r"], 60, 170),
          ("被动 战栗：普攻、巨石、毒刺打中英雄叠层，满 3 层脚下地面开裂、每秒掉最大生命值", ["quake"], REACH, 150)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_skarner_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_skarner_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_skarner_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_skarner_skills.gif")))


if __name__ == "__main__":
    main()
