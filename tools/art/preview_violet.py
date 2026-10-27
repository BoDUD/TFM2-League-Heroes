#!/usr/bin/env python3
"""Preview images for Violet (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_violet.py [--out docs/preview] [--only frames|effects|skills]

  tft_violet_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_violet_effects.png   every effect animation, 3x
  tft_violet_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_violet.py,
                           60 ticks a second) and as tft.dll plays its parts (addons/tft/src/violet.rs), captioned in
                           Chinese, 4x (preview_vander.py's way): the run; the punches; the 1-2-3 Combo (two jabs, the
                           uppercut throwing Darius up); Gauntlet Rush (the kick-off dust, the rush, the punch knocking
                           him back); the Pit Fighter's second wind (Darius hits her to half health: the green burst and
                           the heal over time); Undercity Fist (the leap, the slam's shockwave, Darius and Garen thrown up,
                           the fury's crackles while she punches faster).
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
from build_violet import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_violet")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_violet_fx", "tft_violet_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
REACH = 36                       # game px between her pivot and Darius's when she punches (her gauntlets reach 17 ahead)
FURY_AS = 1 + (P["r_as"]) / 100   # the fury's attack speed (no Family ally in the scene)


class Clip(SilcoClip):
    """preview_silco's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "violet", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        if dur and not loop and dur < sum(ms for _, ms in fr):   # a faster attack: every frame shorter alike
            k = dur / sum(ms for _, ms in fr)
            fr = [(f, ms * k) for f, ms in fr]
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def scene(out, steps, gap, W=280, H=150, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_violet_fx"], fx["tft_violet_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "r" in steps:                              # a second enemy close by: the slam takes both
        c.foes = (Foe(load(GAREN), far + 22, gy),)
    c.wait(300)

    def punch(speed=1.0):
        hit = c.t + tick(P["atk_st"] - 1) / speed
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]) / speed)
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) / speed)
        return hit

    def combo():
        """1-2-3 Combo: the jabs on q_j1 / q_j2, the uppercut on q_j3 throwing Darius up q_air ticks."""
        t = c.t
        for j in ("q_j1", "q_j2"):
            hit = t + tick(P[j] - 1)
            c.on_foe(d, "q_jab", hit)
            d.flinches.append(hit)
        up = t + tick(P["q_j3"] - 1)
        c.on_foe(d, "q_up", up)
        d.hops.append((up, up + tick(P["q_air"]), 9))
        c.a("skill", tick(P["q_dur"]))
        return up + tick(P["q_air"])

    def rush():
        """Gauntlet Rush: the dust where she starts, the rush onto Darius at e_speed, the punch knocking him back."""
        t = c.t
        c.at_spot("e_dash", t, me.pos(t)[0], gy, sheet=small)
        x_from = me.pos(t)[0]
        x_to = d.x - REACH
        land = t + (x_to - x_from) / px_tick(P["e_speed"])
        me.moves.append((t, land, x_from, x_to))
        c.a("skill2", land - t)
        c.a("punch", tick(P["e_hit_t"]))
        c.on_foe(d, "e_hit", land)
        d.flinches.append(land)
        d.slides.append((land, land + tick(P["e_kb_t"]) * 4, P["e_kb_speed"] * P["e_kb_t"] / 1000))
        return land + tick(P["e_hit_t"])

    def second_wind():
        """The Pit Fighter: Darius hits her down to half health; the burst and the heal over p_t ticks (tft.dll)."""
        t = c.t
        d.attacks += [t + 100, t + 900]
        wind = t + 1100
        c.on_me("p_burst", wind)
        c.on_me("p_wind", wind + 300, until=wind + tick(P["p_t"]))
        c.a("hit", 200)
        c.a("idle", wind + tick(P["p_t"]) + 300 - c.t)

    def undercity_fist():
        """Undercity Fist: the leap onto Darius at r_speed, on landing the slam: the shockwave at her feet, every enemy
        within r_r thrown up r_up ticks; then the fury r_t ticks while she punches faster."""
        t = c.t
        x_from = me.pos(t)[0]
        x_to = d.x - REACH
        land = t + (x_to - x_from) / px_tick(P["r_speed"])
        me.moves.append((t, land, x_from, x_to))
        c.a("ult", land - t)
        c.a("slam", tick(P["r_slam_t"]))
        c.at_spot("r_slam", land, x_to, gy, sheet=big)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "r_hit", land)
            foe.hops.append((land, land + tick(P["r_up"]), 10))
        end = land + tick(P["r_t"])
        c.on_me("r_fury", land + 100, until=end)
        c.wait(max(0, land + tick(P["r_up"]) - c.t))
        while c.t + tick(P["atk_cd"]) / FURY_AS < end:
            punch(FURY_AS)
        return end

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            punch()
            punch()
        elif step == "q":
            end = combo()
            c.wait(max(0, end + 500 - c.t))
        elif step == "e":
            end = rush()
            c.wait(max(0, end + 500 - c.t))
        elif step == "p":
            second_wind()
        elif step == "r":
            end = undercity_fist()
            c.wait(max(0, end + 200 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：举着拳套小跑", ["walk_in"], 160, 170),
          ("普攻：拳套直拳", ["attack"], REACH, 170),
          ("技能1 1-2-3连招：两记刺拳，再一记上勾拳把目标击飞0.5秒", ["q"], REACH, 180),
          ("技能2 冲拳：冲到敌人身上一拳打退", ["e"], 90, 170),
          ("被动 搏击手：命中附带真实伤害、全能吸血；第一次掉到半血时2秒内回复15%最大生命", ["p"], REACH, 170),
          ("大招 底城怒拳：跳进敌群双拳砸地，击飞周围敌人0.8秒，之后5秒攻速+40%、吸血+5%（家人越多攻速越高）", ["r"], 90, 190)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_violet_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[10:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_violet_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_violet_skills.gif")))


if __name__ == "__main__":
    main()
