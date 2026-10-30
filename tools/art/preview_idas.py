#!/usr/bin/env python3
"""Preview images for Idas (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_idas.py [--out docs/preview] [--only frames|effects|skills]

  tft_idas_frames.png    every animation's dense frames (hd_, PPU 2.45, as league.dll shows them)
  tft_idas_effects.png   every effect animation, 3x
  tft_idas_skills.gif    each skill alone with its effects against Darius (and Ashe by him), with Garen and Braum behind
                         her as her allies, timed like the kit (tools/kit/build_idas.py, 60 ticks a second) and as
                         tft.dll plays its part (addons/tft/src/idas.rs), captioned in Chinese, 4x (preview_steb.py's
                         way): the run (TFT's low bound); the claws; Guardian's Vow (Darius's blows take her under half:
                         the flash and the shields on her and the nearest ally); Golden Breath (the molten-gold plume
                         from her jaws over Darius and Ashe, their armour melting); Dragon's Roar (the shockwave, the
                         slow at the enemies' feet, the light shields on her allies); Golden Scales (the shell while
                         her wings close, the burst, her heal, the allies' shields).
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
from preview_leesin import Foe, frames_of  # noqa: E402
from preview_pyke import Me  # noqa: E402
import preview_zoe as Z  # noqa: E402
from preview_silco import Clip as SilcoClip, px_tick  # noqa: E402
from build_idas import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_idas")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_idas_fx", "tft_idas_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
ASHE = os.path.join(ROOT, "league", "champions", "league_ashe")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
BRAUM = os.path.join(ROOT, "league", "champions", "league_braum")
REACH = 34                       # game px between her pivot and Darius's when she claws (atk_range 25000 + bodies)
ALLIES = (40, 76)                # her allies behind her (game px), facing right
ASHE_AT = (22, 10)               # Ashe beside Darius (game px from him)
BREATH_MID = P["q_len"] / 2000   # the breath line's middle ahead of her (game px)


class Clip(SilcoClip):
    """preview_silco's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "idas", self.z))
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

    def looped(self, tag, t0, t1, x, y, sheet):
        self.over.append(Anim(frames_of(sheet, tag), t0, int(x), int(y), loop=True, until=t1))


def scene(out, steps, gap, W=360, H=150, z=4, tail=900, x0=130):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_idas_fx"], fx["tft_idas_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    allies = (Foe(load(GAREN), x0 - ALLIES[0], gy, mirror=False), Foe(load(BRAUM), x0 - ALLIES[1], gy, mirror=False))
    ashe = Foe(load(ASHE), far + ASHE_AT[0], gy + ASHE_AT[1])
    enemies = (d,)
    if any(s in steps for s in ("p", "q", "e", "r")):
        c.foes = allies
    if any(s in steps for s in ("q", "e")):
        c.foes = allies + (ashe,)
        enemies = (d, ashe)
    c.wait(300)

    def claw():
        """One attack: the claw lands on atk_st."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def vow():
        """Guardian's Vow: Darius's blows take her under p_low%; tft.dll's flash and shield on her and on Garen, the
        nearest ally, for p_t ticks."""
        t = c.t
        d.attacks += [t + 100, t + 700]
        tv = t + 900
        c.on_me("p_burst", tv)
        c.on_foe(allies[0], "p_burst", tv)
        c.on_me("p_shield", tv + 360, until=tv + 360 + 1600)
        c.on_foe(allies[0], "p_shield", tv + 360, until=tv + 360 + 1600)
        c.a("idle", tv + 360 + 1600 - c.t, loop=True)
        return c.t

    def breath():
        """Golden Breath: the inhale, then on q_rel the plume from her jaws over Darius and Ashe; their armour melts."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        at = t + tick(P["q_rel"] - 1)
        c.looped("q_breath", at, t + tick(P["q_dur"]), me.pos(at)[0] + BREATH_MID, gy, big)
        for foe in enemies:
            foe.flinches.append(at + 60)
            c.on_foe(foe, "q_shred", at + 60, until=at + 60 + 1800)
        return at + 1900

    def roar():
        """Dragon's Roar: on e_st the shockwave round her; the enemies stunned and slowed (the slow at their feet), the
        light shields on her allies."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_st"] - 1)
        c.on_me("e_roar", at, sheet=big)
        for foe in enemies:
            foe.flinches.append(at + 80)
            c.on_foe(foe, "e_slow", at + 80, until=at + 80 + tick(P["e_slow_t"]))
        for ally in allies:
            c.on_foe(ally, "e_shield", at + 80, until=at + 80 + tick(P["e_sh_t"]))
        end = at + 80 + tick(P["e_sh_t"])
        c.a("idle", end - c.t, loop=True)
        return end

    def scales():
        """Golden Scales: the shell while her wings close (r_t ticks; Darius strikes the shell), then the burst, her
        heal and the allies' shields (shown 1.6 s of their r_sh_t)."""
        t = c.t
        c.on_me("r_wrap", t, until=t + tick(P["r_t"]))
        d.attacks += [t + 400, t + 1300]
        c.a("ult", tick(P["r_t"] + P["r_out"]))
        tb = t + tick(P["r_t"] - 1)
        c.on_me("r_burst", tb, sheet=big)
        c.on_me("r_heal", tb + 120)
        for ally in allies:
            c.on_foe(ally, "r_shield", tb + 120, until=tb + 120 + 1600)
        end = tb + 120 + 1600
        c.a("idle", end - c.t, loop=True)
        return end

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            for _ in range(3):
                claw()
        elif step in ("p", "q", "e", "r"):
            end = {"p": vow, "q": breath, "e": roar, "r": scales}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：低身往前扑跑（金铲铲原版的跑法，两条腿轮流在前）", ["walk_in"], 180, 170),
          ("普攻 龙爪：往前一扑一爪", ["attack"], REACH, 170),
          ("被动 护卫之誓：生命值低于 50% 时，她和最近的友军各得最大生命值 18% 的护盾", ["p"], REACH, 170),
          ("技能1 黄金龙息：向前喷出扇形熔金龙息，护甲降低 35%", ["q"], 46, 170),
          ("技能2 龙威振翅：振翅一吼，敌人眩晕并减速，友军得到护盾", ["e"], 46, 180),
          ("大招 黄金龙鳞：双翼裹身减伤，然后回血、给友军护盾（护盾在时攻速 +30%）", ["r"], REACH, 180)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_idas_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[8:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_idas_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_idas_skills.gif")))


if __name__ == "__main__":
    main()
