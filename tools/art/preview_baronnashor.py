#!/usr/bin/env python3
"""Preview images for Baron Nashor (the tft pack), built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_baronnashor.py [--out docs/preview] [--only frames|effects|skills]

  tft_baronnashor_frames.png    every animation's dense frames (hd_, PPU 2.04, as the tft add-on shows them)
  tft_baronnashor_effects.png   every effect animation, 3x
  tft_baronnashor_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                                (tools/kit/build_baronnashor.py, 60 ticks a second) and as tft.dll plays its part
                                (addons/tft/src/baronnashor.rs), captioned in Chinese, 4x (preview_thex.py's way): the run;
                                Corrosive Bite (the bite on Darius, the line on Garen behind him); Corrosive Breath (the
                                acid spray, the splashes, the corrosion on everyone in the cone); Burrow Strike (it dives,
                                travels under the ground, bursts out by Darius: the ground breaks, the enemies near knocked
                                up); Wrath of the Void (it rears, slams: the spike ring, then ten acid balls on random
                                enemies); Void Rift (a tentacle under a random enemy, knocked up, every few seconds); its
                                death.
"""
import argparse
import os
import random
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows  # noqa: E402
from preview_garen import T, contact, load  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me  # noqa: E402
import preview_zoe as Z  # noqa: E402
from preview_silco import Clip as SilcoClip, px_tick  # noqa: E402
from build_baronnashor import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_baronnashor")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_baronnashor_fx", "tft_baronnashor_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it attacks: the range
                                                # plus both units' collision radii
SPOTS = ((22, -5), (40, 6))      # Garen behind Darius (in the bite's line and the breath's cone), Ashe further on
MOUTH = (5, -27)                 # its mouth from its pivot (hd/idle.png's (47, 38) from (38, 94) at PPU 2.04)
UP = 10                          # game px a knock-up throws a unit (the picture's height, not the engine's)
SEED = 3


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "baronnashor", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        return self.play(fr, dur, loop)

    def play(self, fr, dur, loop):
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def scene(out, steps, gap, W=380, H=190, z=4, tail=900, x0=80):
    """One scene (a list of steps) written to `out`."""
    rnd = random.Random(SEED)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_baronnashor_fx"], fx["tft_baronnashor_big"]
    gy = H - 34
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    foes = (d,)
    if any(s in steps for s in ("attack", "q", "e", "r", "p")):    # two more enemies by Darius
        foes = (d,) + tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
        c.foes = foes[1:]
    c.wait(300)

    def up(f, at, ticks):
        f.hops.append((at, at + tick(ticks), UP))
        f.flinches.append(at)

    def bite():
        """Corrosive Bite: the bite lands on atk_st; the line through Darius hits Garen behind him too."""
        t = c.t
        at = t + tick(P["atk_st"] - 1)
        for f in foes[:2]:
            c.on_foe(f, "a_hit", at)
            f.flinches.append(at)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def breath():
        """Corrosive Breath: on q_st the spray flies from the mouth; everyone in the cone splashed and corroded q_t."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        at = t + tick(P["q_st"] - 1)
        x, y = me.pos(at)
        reach = P["q_r"] // 1000 + 15
        c.fly("q_spray", at, at + tick(reach * 1000 / 3000), x + MOUTH[0], x + MOUTH[0] + reach, y + MOUTH[1],
              sheet=c.big)
        for f in foes:
            fx_ = f.pos(at)[0]
            if fx_ - x <= reach + 15:
                hit = at + tick((fx_ - x) * 1000 / 3000)
                c.on_foe(f, "q_hit", hit)
                c.on_foe(f, "q_acid", hit, until=hit + tick(P["q_t"]))
                f.flinches.append(hit)
        return at + tick(P["q_t"])

    def burrow():
        """Burrow Strike: it dives on e_st, travels under the ground (the `dig` frames) at e_speed to Darius, bursts out
        (`rise`): the broken ground under it, everyone within e_r knocked up e_up."""
        t = c.t
        c.a("skill2", tick(P["e_st"]))
        x, y = me.pos(c.t)
        to = d.x - 20
        run = tick((to - x) * 1000 / P["e_speed"])
        me.moves.append((c.t, c.t + run, x, to))
        c.a("dig", run, loop=True)
        at = c.t
        c.at_spot("e_burst", at, to, y, sheet=c.big, under=True)
        c.a("rise", tick(P["e_rise"]))
        for f in foes:
            if abs(f.pos(at)[0] - to) <= P["e_r"] / 1000 + 15:
                c.on_foe(f, "e_hit", at)
                up(f, at, P["e_up"])
        return at + tick(P["e_up"]) + 400

    def wrath():
        """Wrath of the Void: it rears, slams on r_st - the spike ring round it, r_hit on everyone within r_r - then r_n
        acid balls r_every apart on random enemies within r_mr (each corrodes)."""
        t = c.t
        dur = P["r_st"] + P["r_n"] * P["r_every"] + 6
        c.a("ult", tick(dur))
        at = t + tick(P["r_st"] - 1)
        x, y = me.pos(at)
        c.at_spot("r_spikes", at, x, y, sheet=c.big, under=True)
        for f in foes:
            if abs(f.pos(at)[0] - x) <= P["r_r"] / 1000 + 15:
                c.on_foe(f, "r_hit", at)
                f.flinches.append(at)
        for k in range(P["r_n"]):
            f = rnd.choice(foes)
            mt = at + tick(k * P["r_every"])
            fx_, fy = f.pos(mt)
            c.at_spot("r_fall", mt, fx_, fy, sheet=c.big, under=False)
            hit = mt + 200
            c.on_foe(f, "q_acid", hit, until=hit + tick(P["q_t"]) // 2)
            f.flinches.append(hit)
        return t + tick(dur) + 300

    def rift():
        """Void Rift (tft.dll): in the fight a tentacle under a random enemy champion after p_first, then every p_every
        (shown twice): knocked up p_up."""
        t = c.t
        c.a("idle", tick(P["p_first"] + P["p_every"]) + 900)
        for k in range(2):
            at = t + tick(P["p_first"] + k * P["p_every"])
            f = rnd.choice(foes)
            fx_, fy = f.pos(at)
            c.at_spot("p_tent", at, fx_, fy, sheet=c.big, under=False)
            up(f, at + 150, P["p_up"])
        return c.t

    def death():
        c.a("dead", 1600)
        return c.t

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            for _ in range(3):
                bite()
        else:
            end = {"q": breath, "e": burrow, "r": wrath, "p": rift, "d": death}[step]()
            c.wait(max(0, end + 200 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：纳什男爵迈开两条短腿奔跑，两条腿轮流迈步", ["walk_in"], 200, 190),
          ("普攻 腐蚀撕咬：咬住目标，身后一条直线上的敌人也受伤", ["attack"], REACH, 190),
          ("技能1 腐蚀吐息：向前喷出扇形酸液，伤害并降低护甲和魔抗", ["q"], REACH, 190),
          ("技能2 钻地突袭：钻入地下冲到目标脚下破土而出，击飞周围敌人", ["e"], 150, 200),
          ("大招 虚空之怒：猛砸地面竖起尖刺环，然后连续吐出10团酸液", ["r"], REACH, 230),
          ("被动 虚空裂隙：战斗中每6秒，随机敌方英雄脚下冒出触手击飞", ["p"], REACH, 220),
          ("阵亡", ["d"], REACH, 190)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_baronnashor_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_baronnashor_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_baronnashor_skills.gif")))


if __name__ == "__main__":
    main()
