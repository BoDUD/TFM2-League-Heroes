#!/usr/bin/env python3
"""Preview images for Sy'fen (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_syfen.py [--out docs/preview] [--only frames|effects|skills]

  tft_syfen_frames.png    every animation's dense frames (hd_, PPU 2.52, as league.dll shows them)
  tft_syfen_effects.png   every effect animation, 3x
  tft_syfen_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                          (tools/kit/build_syfen.py, 60 ticks a second) and as tft.dll plays its parts
                          (addons/tft/src/syfen.rs), captioned in Chinese, 4x (preview_daeja.py's way): the run on all
                          fours; the wing claw and the tail lash, Darius shrunk by the first and the fury lit by the
                          second; Bite (the lunge, the jaws on Darius); Wing Sweep (the crescents round him, the cuts and
                          the slow on the two near him); Rampage (the roar, the charge at the farthest - Ashe - ramming
                          Darius and Garen on the way, the great bite on her).
"""
import argparse
import os
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
from build_syfen import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_syfen")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_syfen_fx", "tft_syfen_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = P["atk_range"] // 1000   # game px between his pivot and Darius's when he attacks
SPOTS = ((24, -3), (50, 3))      # Garen and Ashe behind Darius (game px): Ashe the farthest
TOUCH = 22                       # tft.dll stops the charge this far in front of the one he charges at


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "syfen", self.z))
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


def scene(out, steps, gap, W=320, H=150, z=4, tail=900, x0=60):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_syfen_fx"], fx["tft_syfen_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if any(s in steps for s in ("e", "r")):                    # two more enemies by Darius
        c.foes = tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
    foes = (d,) + tuple(c.foes)
    c.wait(300)

    def swing(tag, first):
        """One attack: the blow on atk_st; the first shrinks Darius (p, p_shrink for p_t), the next (on him shrunk)
        lights the fury on Sy'fen."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        if first:
            c.on_foe(d, "p", hit)
            c.on_foe(d, "p_shrink", hit, until=hit + tick(P["p_t"]))
        else:
            c.on_me("p_rage", hit, sheet=big, until=hit + tick(P["p_stack_t"]), under=True)
        c.a(tag, tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def bite():
        """Bite: the rear, the lunge on q_st onto Darius, the jaws on him."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        go = t + tick(P["q_st"] - 1)
        x = me.pos(go)[0]
        to = d.pos(go)[0] - REACH
        land = go + tick(abs(to - x) * 1000.0 / P["q_speed"])
        me.moves.append((go, land, x, to))
        c.on_foe(d, "q_bite", land)
        d.flinches.append(land)
        return land + 400

    def sweep():
        """Wing Sweep: the crescents round him on e_st, every enemy within e_r cut and slowed."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_st"] - 1)
        c.on_me("e_sweep", at, sheet=big)
        x = me.pos(at)[0]
        for foe in foes:
            if abs(foe.pos(at)[0] - x) <= P["e_r"] / 1000:
                c.on_foe(foe, "e_hit", at)
                c.on_foe(foe, "e_slow", at, until=at + tick(P["e_slow_t"]))
                foe.flinches.append(at)
        return at + tick(P["e_slow_t"])

    def rampage():
        """Rampage: the roar; on r_go the kick-off dust and the charge at the farthest (Ashe), r_speed a tick, every
        enemy passed rammed; on r_bite_t the great bite on her."""
        t = c.t
        c.on_me("r", t, sheet=big)
        c.a("ult", tick(P["r_dur"]))
        go = t + tick(P["r_go"] - 1)
        x = me.pos(go)[0]
        target = max(foes, key=lambda f: f.pos(go)[0])
        to = target.pos(go)[0] - TOUCH
        speed = P["r_speed"] / 1000                          # game px a tick
        arrive = go + tick(max(1, round(abs(to - x) / speed)))
        c.at_spot("r_dash", go, x, me.y, sheet=small)
        me.moves.append((go, arrive, x, to))
        w = P["r_w"] / 1000
        for foe in foes:
            fx_ = foe.pos(go)[0]
            if x - w <= fx_ <= to + w or foe is target:
                th = go + tick(max(0, round((min(fx_, to) - x) / speed)))
                c.on_foe(foe, "r_hit", th)
                foe.flinches.append(th)
        bite_at = t + tick(P["r_bite_t"] - 1)
        c.on_foe(target, "r_bite", bite_at, sheet=big)
        target.flinches.append(bite_at)
        return max(bite_at + 500, c.t)

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            swing("attack", True)
            swing("attack2", False)
            swing("attack", False)
        elif step in ("q", "e", "r"):
            end = {"q": bite, "e": sweep, "r": rampage}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：四肢着地奔跑，两条后腿轮流往前迈", ["walk_in"], 170, 160),
          ("普攻 + 被动 幽影低语：翼爪、甩尾交替；伤害让敌人缩小（护甲魔抗降低），打缩小的敌人叠怒气", ["attack"], REACH, 160),
          ("技能1 噬咬：后仰后扑上去狠咬一口，无视部分护甲并回血", ["q"], 50, 160),
          ("技能2 翼刃横扫：张开双翼横扫身边，扫中的敌人受伤并减速", ["e"], 32, 160),
          ("大招 暴走：龙吼后冲向最远的敌人，路上的敌人被撞晕，冲到后猛咬一口", ["r"], 34, 200)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_syfen_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[8:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_syfen_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_syfen_skills.gif")))


if __name__ == "__main__":
    main()
