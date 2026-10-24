#!/usr/bin/env python3
"""Preview images for Sejuani, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_sejuani.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_sejuani_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  league_sejuani_effects.png   every effect animation, 3x
  league_sejuani_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_sejuani.py, 60 ticks a
                               second, the add-on's League rules): out of combat she wears the Frost Armour; Arctic
                               Assault (the snow kicked up where she starts, the charge stopping on Darius, the tusk
                               impact, the knock-up, the glint) gives Winter's Wrath at once (Q -> W: the sweep's ring,
                               the ice line racing ahead, the bursts, the slow, a Frost stack each swing); her flail
                               brings the Frost to four and freezes him (W -> freeze); the next blow shatters him (stun
                               -> shatter); Glacial Prison (the bola, the prison, the ice storm) gives Arctic Assault
                               back and she charges him again (R -> Q); he falls; 3x.
  league_sejuani_skills.gif    each skill and combo alone with its effects, captioned in Chinese, 4x (the user,
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
from build_sejuani import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_sejuani")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_sejuani_fx", "league_sejuani_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Sejuani(Clip):
    """preview_gnar's clip with her own dense frames."""

    flip = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "sejuani", z))
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

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Darius (the frozen prison held, a Frost stack over his head)."""
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: the snow kick-up, the ice storm)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


# the fight's steps in order (showcase); skills() plays some of them alone
FIGHT = ["ride_in", "qw", "freeze", "shatter", "back", "rq", "kill"]


def showcase(out, z=3, steps=FIGHT, W=320, H=130, gap=150, tail=1500):
    """The scripted fight (or some of its steps: skills() plays each skill alone) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_sejuani_fx"], fx["league_sejuani_big"]
    gy = H - 30
    x0 = 40
    far = x0 + gap                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Sejuani(load(CHAMP), d, me, small, big)
    frost = {"n": 0}
    fight = {"from": None}
    c.wait(300)

    def stack(when):
        """A Frost stack on Darius (the add-on's snowflake over him); the fourth freezes him."""
        frost["n"] += 1
        if frost["n"] < P["f_n"]:
            c.on_foe("frost", when, until=when + tick(P["f_t"]))
            return None
        frost["n"] = 0
        c.on_foe("e_freeze", when, until=when + tick(P["e_stun"]))
        return when

    def combat():
        if fight["from"] is None:
            fight["from"] = c.t

    def ride(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    def charge():
        """Arctic Assault: the snow where she starts (q_go), the charge stopping on Darius (the add-on), the impact,
        the knock-up and the glint on him."""
        combat()
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        go = t + tick(P["q_go"] - 1)
        xa = me.pos(go)[0]
        c.at("q_dash", go, xa, gy, under=True)
        stop = d.pos(go)[0] - 24
        me.moves.append((go, go + tick(P["q_t"]), xa, stop))
        hit = go + tick(P["q_t"])
        c.on("q_hit", hit)
        c.on_foe("f_mark", hit)
        d.hops.append((hit, hit + tick(P["q_up"]), 12))
        return hit

    def wrath():
        """Winter's Wrath: the sweep round her on w_rel1, the slam's ice line on w_rel2; a burst, a slow and a Frost
        stack on Darius for each swing."""
        combat()
        t = c.t
        c.a("skill2", tick(P["w_dur"]))
        r1 = t + tick(P["w_rel1"] - 1)
        c.on_me("w_sweep", r1, sheet=big, under=True)
        c.on("w_hit", r1)
        d.flinches.append(r1)
        c.on_foe("slow", r1, until=r1 + tick(P["w_slow_t"]), under=True)
        first = stack(r1)
        r2 = t + tick(P["w_rel2"] - 1)
        x = me.pos(r2)[0]
        x_end = x + P["w_len"] / 1000.0
        c.fly("w_line", r2, r2 + abs(x_end - x) / px_ms(P["w_speed"]), x, x_end, gy - 11)
        hit = r2 + abs(d.pos(r2)[0] - x) / px_ms(P["w_speed"])
        c.on("w_hit", hit)
        d.flinches.append(hit)
        return first or stack(hit)

    def blow(shatter=False):
        combat()
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        b = t + tick(P["a_hit"] - 1)
        c.on("a_hit", b)
        d.flinches.append(b)
        if shatter:
            c.on("sh_hit", b + tick(1))
            return None
        return stack(b)

    def prison():
        """Glacial Prison: the bola, the prison held while he is stunned, the ice storm round him."""
        combat()
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        rel = t + tick(P["r_rel"] - 1)
        xs = me.pos(rel)[0]
        reach = rel + abs(d.pos(rel)[0] - xs) / px_ms(P["r_speed"])
        c.fly("r_bola", rel, reach, xs, d.pos(rel)[0], gy - 12)
        c.on_foe("r_hit", reach, until=reach + tick(P["r_stun"]))
        c.at("r_storm", reach, d.pos(reach)[0], gy, sheet=big, under=True, until=reach + tick(P["r_storm"]))
        c.on_foe("slow", reach, until=reach + tick(P["r_storm"]), under=True)
        return reach

    for step in steps:
        if step == "ride_in":           # out of combat: the Frost Armour on her as she rides in
            ride(far - 70)
        elif step == "armour":          # the Frost Armour out of combat, gone a moment after the first blow
            ride(far - 40)
            blow()
            c.wait(800)
        elif step == "attack":          # two flail blows, a Frost stack each
            blow()
            blow()
        elif step == "q":               # Arctic Assault alone
            charge()
            c.wait(400)
        elif step == "qw":              # Arctic Assault, Winter's Wrath at once (Q -> W)
            charge()
            wrath()
        elif step == "w":               # Winter's Wrath alone
            wrath()
            c.wait(300)
        elif step == "freeze":          # W, then blows until the fourth stack freezes him (W -> freeze)
            frozen = wrath() if frost["n"] == 0 else None
            while frozen is None:
                frozen = blow()
            c.wait(frozen + tick(10) - c.t)
        elif step == "shatter":         # the next blow on the frozen one shatters him (stun -> shatter)
            blow(shatter=True)
            c.wait(300)
        elif step == "back":            # she backs off
            c.wait(200)
            xb = me.pos(c.t)[0]
            me.moves.append((c.t, c.t + 500, xb, xb - 60))
            c.a("run", 500, loop=True)
        elif step == "r":               # Glacial Prison alone
            reach = prison()
            c.wait(reach + tick(P["r_stun"]) - c.t)
        elif step == "rq":              # Glacial Prison, Arctic Assault back at once (R -> Q)
            reach = prison()
            c.wait(reach + tick(2) - c.t)
            charge()
            c.wait(300)
        elif step == "kill":
            blow()
            d.death = c.t + 40
    c.wait(tail)
    if "ride_in" in steps or "armour" in steps:      # the Frost Armour until a moment after the fight starts
        start = fight["from"] if fight["from"] is not None else c.t
        c.on_me("fa_armour", 0, until=start + tick(P["fa_keep"]))
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：骑着钢鬃奔跑", ["ride_in"], 150, 130),
          ("被动 冰霜护甲：脱战时身上一层冰霜（附加包：免疫减速），一出手很快消失", ["armour"], 150, 130),
          ("普攻：冰锤链枷抽打，每下给敌方英雄叠一层霜冻（头上的雪花）", ["attack"], 60, 130),
          ("技能1 极寒突袭：钢鬃冲锋，撞到第一个敌方英雄停下（附加包），把它挑飞", ["q"], 110, 130),
          ("技能2 凛冬之怒：链枷先横扫一圈，再往前砸出一道冰；减速，每下叠霜冻", ["w"], 60, 130),
          ("连招 Q→W：冲锋撞飞英雄，立刻接凛冬之怒", ["qw"], 110, 130),
          ("被动 永冻领域：霜冻叠满 4 层，敌人被冻住（冰笼）", ["freeze"], 60, 130),
          ("连招 晕住→碎冰：打中被晕住的敌人（队友晕的也算，附加包），冰块炸开", ["freeze", "shatter"], 60, 130),
          ("大招 极冰寒狱：甩出冰套索，冻住第一个英雄，落点冰风暴减速周围敌人", ["r"], 120, 130),
          ("连招 R→Q：套索冻住英雄，极寒突袭冷却刷新，立刻冲过去", ["rq"], 120, 130)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        showcase(path, z=z, steps=steps, W=220, H=h, gap=gap, tail=900)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_sejuani_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_sejuani_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_sejuani_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_sejuani_skills.gif")))


if __name__ == "__main__":
    main()
