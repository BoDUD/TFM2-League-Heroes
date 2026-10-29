#!/usr/bin/env python3
"""Preview images for Renni (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_renni.py [--out docs/preview] [--only frames|effects|skills]

  tft_renni_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_renni_effects.png   every effect animation, 3x
  tft_renni_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_renni.py,
                          60 ticks a second) and as tft.dll plays its parts (addons/tft/src/renni.rs), captioned in
                          Chinese, 4x (preview_scar.py's way): the run; the saw's three bites; Shimmer Frenzy (hurt
                          under the line, the shot, the rush while she grinds); the Chainsaw Charge (at Darius, the cone
                          ground three times, Darius and Garen slowed); the Saw Guard (the shield while Darius hits);
                          Mudrunner Slam (Darius heaved up and held, then slammed down by Garen).
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
from build_renni import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_renni")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_renni_fx", "tft_renni_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
REACH = 40                       # game px between her pivot and Darius's when she grinds (the saw reaches ~28 ahead)
LIFT = 26                        # game px Darius hangs over the ground on her saw


class Clip(SilcoClip):
    """preview_silco's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "renni", self.z))
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
    small, big = fx["tft_renni_fx"], fx["tft_renni_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "q" in steps or "r" in steps:              # a second enemy close by
        c.foes = (Foe(load(GAREN), far + 22, gy),)
    c.wait(300)

    def grind():
        """One attack: the saw bites three times."""
        for k in range(3):
            hit = c.t + tick(P["atk_st"] - 1 + k * P["a_gap"])
            c.on_foe(d, "a_hit", hit)
            d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def shimmer():
        """Shimmer Frenzy: Darius has her under the line; tft.dll's shot, then the rush while she grinds."""
        d.attacks += [c.t + 100, c.t + 400]
        c.a("hit", 200)
        c.wait(400)
        t = c.t
        c.on_me("p", t)
        end = t + tick(P["p_t"])
        c.on_me("p_rush", t + 100, until=end)
        while c.t + tick(P["atk_cd"]) * 0.6 < end:
            grind()
        return end

    def charge():
        """Chainsaw Charge: at Darius at q_speed, then the cone ground q_n times q_gap apart, everyone in it slowed."""
        t = c.t
        x_from = me.pos(t)[0]
        x_to = d.x - REACH
        land = t + max(1, x_to - x_from) / px_tick(P["q_speed"])
        me.moves.append((t, land, x_from, x_to))
        c.a("charge", land - t)
        c.a("grind", tick(P["q_grind_t"]))
        for k in range(P["q_n"]):
            th = land + tick(k * P["q_gap"])
            for foe in (d,) + tuple(c.foes):
                c.on_foe(foe, "q_hit", th)
                foe.flinches.append(th)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "q_slow", land, until=land + tick(P["q_slow_t"]))
        return land + tick(P["q_slow_t"])

    def guard():
        """Saw Guard: the flash and the shield while Darius swings at her."""
        t = c.t
        c.on_me("e", t)
        end = t + tick(P["e_t"])
        c.on_me("e_guard", t + 200, until=end)
        d.attacks += [t + 300, t + 1100, t + 1900]
        c.a("skill2", tick(P["e_dur"]))
        c.wait(max(0, end - c.t - 600))
        return end

    def slam():
        """Mudrunner Slam: on r_st Darius heaved up and held r_up ticks (stunned), on r_slam slammed down: the crack
        under him, every enemy there hit."""
        t = c.t
        lift = t + tick(P["r_st"] - 1)
        down = t + tick(P["r_slam"] - 1)
        c.on_foe(d, "r_hit", lift)
        d.flinches.append(lift)
        d.hops.append((lift, lift + tick(P["r_up"]), LIFT))
        c.on_foe(d, "r_up", lift, until=down)
        c.a("ult", down - t)
        c.a("slam", tick(P["r_slam_t"]))
        c.at_spot("r_slam", down, d.x, gy, sheet=big)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "r_hit", down)
            foe.flinches.append(down)
        return down + 900

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            grind()
            grind()
        elif step in ("p", "q", "e", "r"):
            end = {"p": shimmer, "q": charge, "e": guard, "r": slam}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：弓着身子跑，链锯拎在身侧", ["walk_in"], 160, 170),
          ("普攻 链锯研磨：链锯往前一顶，一次锯三下", ["attack"], REACH, 170),
          ("被动 微光狂热：生命低于40%时打一针微光，4秒内攻速+40%，回复20%最大生命（30秒一次）", ["p"], REACH, 170),
          ("技能1 链锯冲撞：冲到目标面前，前方扇形连锯三下，减速30%", ["q"], 110, 170),
          ("技能2 锯刃格挡：竖起链锯，护盾+减伤20%，持续2.5秒", ["e"], REACH, 170),
          ("大招 泥奔者重击：把目标挑起举过头顶（击飞1.1秒，自己回复15%最大生命），再砸到地上", ["r"], REACH, 210)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_renni_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[8:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_renni_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_renni_skills.gif")))


if __name__ == "__main__":
    main()
