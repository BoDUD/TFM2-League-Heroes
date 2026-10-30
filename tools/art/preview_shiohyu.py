#!/usr/bin/env python3
"""Preview images for Shi Oh Yu (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_shiohyu.py [--out docs/preview] [--only frames|effects|skills]

  tft_shiohyu_frames.png    every animation's dense frames (hd_, PPU 2.46, as league.dll shows them)
  tft_shiohyu_effects.png   every effect animation, 3x
  tft_shiohyu_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                            (tools/kit/build_shiohyu.py, 60 ticks a second) and as tft.dll plays its part
                            (addons/tft/src/shiohyu.rs), captioned in Chinese, 4x (preview_daeja.py's way): the run; the
                            three claw swipes; the jade skin; Jade Fist Barrage (the rush and four punches); Earthshaker
                            (the slam, the three knocked up and slowed); Jade Form (the stance, then its three blows:
                            the stun, the true damage, the wave down the line through the three).
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
from build_shiohyu import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_shiohyu")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_shiohyu_fx", "tft_shiohyu_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = P["atk_range"] // 1000   # game px between his pivot and Darius's when he attacks
SPOTS = ((22, -3), (44, 3))      # Garen and Ashe behind Darius, on the line (game px)


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "shiohyu", self.z))
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


def scene(out, steps, gap, W=300, H=150, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_shiohyu_fx"], fx["tft_shiohyu_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if any(s in steps for s in ("e", "r")):                   # two more enemies by Darius
        c.foes = tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
    foes = (d,) + tuple(c.foes)
    c.wait(300)

    def swipe(tag, hit_tag="a_hit", sheet=None):
        """One attack (a swipe or a Jade Form blow): the claw lands on atk_st."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on(hit_tag, hit, sheet=sheet)
        d.flinches.append(hit)
        c.a(tag, tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))
        return hit

    def barrage():
        """Jade Fist Barrage: the rush at Darius (q_speed), then q_n punches q_gap apart from q_first."""
        t = c.t
        xa = me.pos(t)[0]
        x1 = d.x - REACH
        t1 = t + tick(max(1, (x1 - xa) * 1000.0 / P["q_speed"]))
        me.moves.append((t, t1, xa, x1))
        c.a("dash", t1 - t)
        flurry = P["q_first"] + P["q_n"] * P["q_gap"]
        for k in range(P["q_n"]):
            hit = t1 + tick(P["q_first"] + k * P["q_gap"])
            c.on("q_hit", hit)
            d.flinches.append(hit)
        c.a("skill", tick(flurry), loop=True)
        return c.t

    def slam():
        """Earthshaker: the fist into the ground on e_st, every enemy within e_r knocked up e_up and slowed."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_st"] - 1)
        x, y = me.pos(at)
        c.at_spot("e_slam", at, x, y, sheet=big, under=True)
        for foe in foes:
            if abs(foe.pos(at)[0] - x) <= P["e_r"] / 1000 + 15:
                c.on_foe(foe, "e_hit", at)
                c.on_foe(foe, "e_slow", at, until=at + tick(P["e_slow_t"]))
                foe.hops.append((at, at + tick(P["e_up"]), 10))
        return at + tick(P["e_slow_t"])

    def skin():
        """Jade Skin (tft.dll): the flash as his skin turns, the aura for p_t."""
        t = c.t
        c.on_me("p", t, sheet=big)
        c.on_me("p_skin", t, sheet=big, until=t + tick(P["p_t"]), under=True)
        swipe("attack")
        swipe("attack2")
        return t + tick(P["p_t"])

    def jade_form():
        """Jade Form: the stance (its flash and aura), then the three blows: the stun, the true damage, the wave."""
        t = c.t
        c.on_me("r", t, sheet=big)
        c.a("ult", tick(P["r_dur"]))
        aura_end = t + tick(P["r_dur"]) + tick(P["atk_cd"]) * 3
        c.on_me("r_jade", t, sheet=big, until=aura_end, under=True)
        swipe("attack", "r1_hit")
        swipe("attack2", "r2_hit")
        at = c.t
        x, y = me.pos(at)
        show = at + tick(P["atk_st"] - 1)
        c.at_spot("r3_wave", show, x + P["r3_len"] / 2000, y, sheet=big, under=False)
        hit = show + tick(P["r3_delay"])
        for foe in foes:
            if 0 <= foe.pos(hit)[0] - x <= P["r3_len"] / 1000:
                c.on_foe(foe, "r3_hit", hit)
                foe.flinches.append(hit)
        c.a("r_wave", tick(P["atk_dur"]))
        return max(hit + 400, c.t)

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            swipe("attack")
            swipe("attack2")
            swipe("attack3")
        elif step in ("p", "q", "e", "r"):
            end = {"p": skin, "q": barrage, "e": slam, "r": jade_form}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：金铲铲的跑步，两条腿轮流迈步", ["walk_in"], 160, 170),
          ("普攻 龙爪三连：左右爪交替挥，第三下更重", ["attack"], REACH, 170),
          ("被动 玉石之肤：半血以下全身化作玉石，几秒内大幅减伤", ["p"], REACH, 170),
          ("技能1 玉拳连打：冲到目标面前连打四拳", ["q"], 70, 170),
          ("技能2 震地：一拳砸地，周围敌人被震飞并减速", ["e"], REACH, 170),
          ("大招 玉龙形态：减伤免控，接下来三击：晕眩 / 真实伤害 / 直线玉石冲击波", ["r"], REACH, 170)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_shiohyu_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_shiohyu_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_shiohyu_skills.gif")))


if __name__ == "__main__":
    main()
