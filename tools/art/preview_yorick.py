#!/usr/bin/env python3
"""Preview images for Yorick, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_yorick.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_yorick_frames.png    every animation's dense frames (hd_, PPU 1.75, as league.dll shows them)
  league_yorick_effects.png   every effect animation, 3x
  league_yorick_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_yorick.py, 60 ticks a
                              second): shovel blows; Last Rites (the heavy blow, his heal, a grave dug by Darius) three
                              times; with the graves full the next Q is the Awakening (the walkers clawing up and
                              gnawing at Darius, the ring of spirits caging him) and the cage brings Mourning Mist at
                              once (W -> E: the globule, its splash, the mark and the slow); the mist on a champion sends
                              the walkers pouncing and gives Q back (E -> Q); Eulogy of the Isles (the Maiden rising
                              behind him, two more walkers, her claws, his bonus hits) gives Q back too (R -> Q); he
                              falls; 3x.
  league_yorick_skills.gif    each skill and combo alone with its effects, captioned in Chinese, 4x (the user,
                              2026-10-24: 「带技能的gif图呢？」).
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
from build_yorick import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_yorick")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_yorick_fx", "league_yorick_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Yorick(Clip):
    """preview_gnar's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "yorick", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Darius (the walkers, the Maiden behind him, the mark over his head)."""
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: the grave, the wall, the mist's splash)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


# the fight's steps in order (showcase); skills() plays some of them alone
FIGHT = ["walk_in", "attack", "q", "q", "q", "awaken_e", "eq", "r", "kill"]


def showcase(out, z=3, steps=FIGHT, W=320, H=150, gap=150, tail=1500, graves=0):
    """The scripted fight (or some of its steps: skills() plays each skill alone) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_yorick_fx"], fx["league_yorick_big"]
    gy = H - 30
    x0 = 40
    far = x0 + gap                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Yorick(load(CHAMP), d, me, small, big)
    st = {"graves": graves, "walkers": -1.0, "maiden": -1.0}
    c.wait(300)

    def walkers(when, n):
        """Walkers clawing up round Darius, then gnawing a second at a time while they last, a bite each k_p."""
        c.on_foe("k_spawn", when, until=when + 460, under=True)
        end = when + tick(P["k_t"])
        c.on_foe("k_swarm", when + 460, until=end, under=True)
        t = when + tick(P["k_p"])
        while t < end:
            c.on("k_bite", t)
            d.flinches.append(t)
            t += tick(P["k_p"])
        st["walkers"] = end

    def blow():
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        b = t + tick(P["a_hit"] - 1)
        c.on("a_hit", b)
        if b < st["maiden"]:                            # the Maiden's target takes his bonus
            c.on("r_mark", b + tick(1))
        d.flinches.append(b)

    def rites():
        """Last Rites (or, with the graves full, the Awakening: the walkers and the wall, then E at once)."""
        t = c.t
        full = st["graves"] >= P["g_n"]
        c.a("awaken" if full else "skill", tick(P["q_dur"]))
        h = t + tick(P["q_hit"] - 1)
        c.on("q_hit", h)
        d.flinches.append(h)
        if full:
            st["graves"] = 0
            walkers(h + tick(1), P["k_n"])
            fx_ = h + tick(2)
            c.at("w_wall", fx_, d.pos(fx_)[0], gy, sheet=big, under=True)
            c.on("w_hit", fx_)
            return fx_
        st["graves"] += 1
        c.at("q_grave", h, d.pos(h)[0] + 14, gy, under=True, until=h + 6000)
        return None

    def mist():
        """Mourning Mist: the globule lobbed at Darius, its splash, the burst, the mark and the slow; the walkers pounce
        on him if they are up, and Q is back (E -> Q)."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        rel = t + tick(P["e_rel"] - 1)
        land = rel + tick(P["e_fly"])
        xs = me.pos(rel)[0] + 10
        c.fly("e_mist", rel, land, xs, d.pos(rel)[0], gy - 22)
        c.at("e_cloud", land, d.pos(land)[0], gy, sheet=big, under=True)
        c.on("e_hit", land)
        d.flinches.append(land)
        c.on_foe("e_mark", land, until=land + tick(P["e_t"]))
        c.on_foe("slow", land, until=land + tick(P["e_slow_t"]), under=True)
        if land < st["walkers"]:
            c.on("k_leap", land + tick(2))
        return land

    def eulogy():
        """Eulogy of the Isles: the Maiden rising behind Darius with two walkers, clawing while she stands."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        rise = t + tick(P["r_rel"] - 1)
        c.on_foe("r_spawn", rise, sheet=big, until=rise + 720, under=True)
        end = rise + tick(P["r_t"])
        c.on_foe("r_maiden", rise + 720, sheet=big, until=end, under=True)
        k = rise + tick(P["r_p"])
        while k < end:
            c.on("r_claw", k)
            d.flinches.append(k)
            k += tick(P["r_p"])
        walkers(rise + tick(2), P["r_n"])
        st["maiden"] = end
        return rise

    def walk(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    for step in steps:
        if step == "walk_in":
            walk(far - 34)
        elif step == "attack":          # two shovel blows
            blow()
            blow()
        elif step == "q":               # Last Rites: a grave each
            rites()
            c.wait(250)
        elif step == "awaken":          # the graves full: the Awakening alone
            rites()
            c.wait(1600)
        elif step == "awaken_e":        # the Awakening's cage brings Mourning Mist at once (W -> E)
            rites()
            mist()
            c.wait(200)
        elif step == "e":               # Mourning Mist alone
            mist()
            c.wait(900)
        elif step == "eq":              # the mist on a champion: the walkers pounce, Q at once (E -> Q)
            mist()
            rites()
            c.wait(400)
        elif step == "r":               # Eulogy alone: the Maiden, Q back at once (R -> Q), his bonus blows
            eulogy()
            rites()
            blow()
            c.wait(600)
        elif step == "r_only":
            eulogy()
            c.wait(1800)
        elif step == "kill":
            blow()
            d.death = c.t + 40
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height,
# graves already dug)
SCENES = [("移动：扛着铲子走", ["walk_in"], 150, 150, 0),
          ("普攻：抡铲子砸", ["attack"], 40, 150, 0),
          ("技能1 临终仪式：重重一铲 + 回血，挖出一座坟（攒到 3 座）", ["q"], 40, 150, 0),
          ("被动 唤醒（Q→雾行者 + 灵魂墙）：坟满 3 座，下一铲唤醒雾行者咬他，一圈灵魂墙困住英雄", ["awaken"], 40, 150, 3),
          ("连招 灵魂墙→黑雾：困住英雄的同时，哀伤之雾冷却刷新，立刻扔出", ["awaken_e"], 40, 150, 3),
          ("技能2 哀伤之雾：扔出黑雾，伤害、破甲（头上的印记）、减速", ["e"], 60, 150, 0),
          ("连招 黑雾→雾行者扑上去 + 临终仪式马上好", ["awaken", "eq"], 40, 150, 3),
          ("大招 海屿悼词：迷雾室女在他身后升起，带两只雾行者，跟着他抓", ["r_only"], 60, 160, 0),
          ("连招 R→Q：室女升起，临终仪式刷新；室女还在时普攻加伤（紫光）", ["r"], 40, 160, 0)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h, graves) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        showcase(path, z=z, steps=steps, W=220, H=h, gap=gap, tail=900, graves=graves)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_yorick_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_yorick_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_yorick_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_yorick_skills.gif")))


if __name__ == "__main__":
    main()
