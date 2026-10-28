#!/usr/bin/env python3
"""Preview images for Ao Shin (the tft pack), built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_aoshin.py [--out docs/preview] [--only frames|effects|skills]

  tft_aoshin_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_aoshin_effects.png   every effect animation, 3x
  tft_aoshin_skills.gif    each skill alone with its effects against Darius (and Garen), timed like the kit
                           (tools/kit/build_aoshin.py, 60 ticks a second) and as tft.dll plays its part
                           (addons/tft/src/aoshin.rs), captioned in Chinese, 4x: the flight; the ball lightning; Thunder
                           Breath (the bolt from his jaw along the line, the hit, the static over Darius's head); Cloud
                           Ride (the whirl where he took off, flying back, the storm shield held); Tempest Might (the
                           bolts from the sky on both enemies, then the crackle round him); Lightning Rain (the storm
                           cloud over him, the bolts falling on both enemies in turn).
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
from build_aoshin import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_aoshin")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_aoshin_fx", "tft_aoshin_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
REACH = 55                       # game px between his pivot and Darius's when he attacks (atk_range 55000)
JAW = (5000 - P["q_y"]) / 1000   # the breath's bolt over his pivot (5000 - y_offset)
BALL = (5000 - P["a_y"]) / 1000  # the ball lightning's


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "aoshin", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def scene(out, steps, gap, W=280, H=170, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_aoshin_fx"], fx["tft_aoshin_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "r" in steps or "p" in steps:              # a second enemy close by: the storms strike both
        c.foes = (Foe(load(GAREN), far + 24, gy),)
    c.wait(300)

    def ball():
        """The ball lightning: released on a_rel, homing on Darius at a_speed."""
        rel = c.t + tick(P["a_rel"] - 1)
        x0_, x1_ = me.pos(rel)[0], d.pos(rel)[0]
        hit = rel + tick((x1_ - x0_) * 1000.0 / P["a_speed"])
        c.fly("a_ball", rel, hit, x0_, x1_, gy - BALL)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def breath():
        """Thunder Breath: on q_rel the bolt (view only) flies from his jaw at q_speed to Darius; the line strikes
        q_at - 1 ticks after it appears: the hit and the static (q_sil) over his head."""
        rel = c.t + tick(P["q_rel"] - 1)
        x0_ = me.pos(rel)[0]
        x1_ = d.pos(rel)[0]                        # a Targeting cast's bolt is removed on the target's spot
        c.fly("q_beam", rel, rel + tick((x1_ - x0_) * 1000.0 / P["q_speed"]), x0_, x1_, gy - JAW)
        hit = rel + tick(P["q_at"] - 1)
        c.on_foe(d, "q_hit", hit)
        c.on_foe(d, "q_sil", hit, until=hit + tick(P["q_sil"]))
        d.flinches.append(hit)
        c.a("skill", tick(P["q_dur"]))
        c.wait(800)

    def ride():
        """Cloud Ride: on e_rel the whirl left where he took off, MoveBack e_back x e_back_t away from Darius, the
        shield held (cut short here) while he goes on attacking."""
        t = c.t + tick(P["e_rel"] - 1)
        x = me.pos(t)[0]
        c.at_spot("e_cast", t, x, gy, sheet=small)
        back = P["e_back"] * P["e_back_t"] / 1000
        me.moves.append((t, t + tick(P["e_back_t"]), x, x - back))
        c.on_me("e_shield", t, until=t + 2600)
        d.attacks += [t - 150]
        c.a("skill2", tick(P["e_dur"]))
        c.wait(200)
        ball()
        ball()

    def storm():
        """Tempest Might (tft.dll): the bolt on every enemy champion near (p_bolt, the stun p_stun), then the crackle
        round him while he deals more (cut short here), attacking."""
        t = c.t
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "p_bolt", t, sheet=big, until=t + 500)
            foe.flinches.append(t + 50)
        c.wait(tick(P["p_stun"]))
        c.on_me("p_storm", c.t, until=c.t + 2600)
        ball()
        ball()

    def rain():
        """Lightning Rain: the cloud over him for the whole action; from r_rel a bolt every r_gap ticks on a random
        enemy champion near (here Darius and Garen in turn): the strike and the static."""
        t = c.t
        dur = tick(P["r_rel"] + P["r_n"] * P["r_gap"] + 6)
        c.on_me("r_cloud", t, sheet=big, until=t + dur)
        foes = (d,) + tuple(c.foes)
        for k in range(P["r_n"]):
            when = t + tick(P["r_rel"] - 1 + k * P["r_gap"])
            foe = foes[k % len(foes)]
            c.on_foe(foe, "r_bolt", when, sheet=big)
            c.on_foe(foe, "q_sil", when + 60, until=when + 60 + tick(P["r_sil"]))
            foe.flinches.append(when + 60)
        c.a("ult", dur)

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            ball()
            ball()
        elif step == "q":
            breath()
        elif step == "e":
            ride()
        elif step == "p":
            storm()
        elif step == "r":
            rain()
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：驾着风飞行", ["walk_in"], 170, 170),
          ("普攻：吐出球状闪电", ["attack"], REACH, 170),
          ("技能1 雷息：从嘴里喷出一道闪电，打中的敌人头上冒电火花（沉默）", ["q"], REACH, 170),
          ("技能2 腾云：驾云向后飞开，身上裹着风暴护盾", ["e"], 40, 170),
          ("被动 风暴龙威：交战几秒后天雷劈中周围所有敌方英雄（眩晕），随后他身上电光缠绕（法强+）", ["p"], REACH, 200),
          ("大招 闪电暴雨：头顶召来雷云，闪电接连劈向周围的敌方英雄", ["r"], REACH, 200)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_aoshin_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_aoshin_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_aoshin_skills.gif")))


if __name__ == "__main__":
    main()
