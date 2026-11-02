#!/usr/bin/env python3
"""Preview images for the Rift Herald (the tft pack), built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_riftherald.py [--out docs/preview] [--only frames|effects|skills]

  tft_riftherald_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_riftherald_effects.png   every effect animation, 3x
  tft_riftherald_skills.gif    each skill alone with its effects against Darius and Garen, timed like the kit
                               (tools/kit/build_riftherald.py, 60 ticks a second), captioned in Chinese, 4x (preview_brock.py's
                               way): the scuttle; Rending Pincer (three strikes, the gash on Darius); Spin Sweep (the
                               ground ring, both swept and slowed); Void Charge (reared up, the flip and the charge through
                               Garen, knocked aside, onto Darius: the crash, the stun); Warp Armor (the roar, the slam ahead,
                               the floating armour). The void shell is tft.dll's and has no picture; the body's growth is
                               league.dll's (hd::FORMS) and is not drawn here.
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
from build_riftherald import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_riftherald")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_riftherald_fx", "tft_riftherald_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it attacks: the range
                                                # plus both units' collision radii


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames; part() plays some of a tag's frames (the ult's seen parts)."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "riftherald", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        if dur and not loop and dur < sum(ms for _, ms in fr):   # a shorter play: every frame shorter alike
            k = dur / sum(ms for _, ms in fr)
            fr = [(f, ms * k) for f, ms in fr]
        return self.play(fr, dur, loop)

    def part(self, tag, k0, k1):
        fr = list(dense(self.sp, tag, "riftherald", self.z))[k0:k1]
        return self.play(fr, sum(ms for _, ms in fr), False)

    def play(self, fr, dur, loop):
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def scene(out, steps, gap, W=380, H=170, z=4, tail=900, x0=80):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_riftherald_fx"], fx["tft_riftherald_big"]
    gy = H - 34
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    foes = (d,)
    if "q" in steps or "r" in steps:                              # Garen beside Darius, inside the sweep and the slam
        foes = (d, Foe(load(OTHERS[0]), far + 16, gy + 4))
        c.foes = foes[1:]
    if "e" in steps:                                               # Garen on the charge's way
        foes = (d, Foe(load(OTHERS[0]), x0 + gap // 2, gy - 3))
        c.foes = foes[1:]
    c.wait(300)

    def pincer():
        """One attack: the pincer comes down on atk_st, the gash on Darius."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def sweep():
        """Spin Sweep: on q_st the ground ring round it, every enemy within q_r swept and slowed q_slow_t."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        at = t + tick(P["q_st"] - 1)
        x, y = me.pos(at)
        c.at_spot("q_spin", at, x, y, sheet=c.big, under=True)
        for f in foes:
            if abs(f.pos(at)[0] - x) <= P["q_r"] / 1000 + 15:
                c.on_foe(f, "q_hit", at)
                c.on_foe(f, "q_slow", at, until=at + tick(P["q_slow_t"]))
                f.flinches.append(at)
        return at + tick(P["q_slow_t"])

    def charge():
        """Void Charge: reared up e_wind ticks (unstoppable), then the flip and the charge onto Darius at e_speed (the
        kit's CasterAnimation `charge`): Garen on the way knocked aside, Darius rammed and stunned e_stun, the crash."""
        t = c.t
        c.part("skill2", 0, 1)                                      # reared up
        c.t = t + tick(P["e_wind"])
        x, y = me.pos(c.t)
        land = d.pos(c.t)[0] - REACH
        run = tick((land - x) * 1000 / P["e_speed"])
        me.moves.append((c.t, c.t + run, x, land))
        for f in foes[1:]:                                          # on the way: the line's hit at the start of the run
            c.on_foe(f, "e_hit", c.t + run * 0.5)
            f.hops.append((c.t + run * 0.5, c.t + run * 0.5 + tick(P["e_up"]), 6))
        c.a("charge", max(run, 300))
        at = t + tick(P["e_wind"]) + run
        c.at_spot("e_crash", at, land + 10, y, sheet=c.big, under=True)
        c.on_foe(d, "e_hit", at)
        c.on_foe(d, "e_stun", at, until=at + tick(P["e_stun"]))
        d.flinches.append(at)
        return at + tick(P["e_stun"])

    def warp():
        """Warp Armor: the roar round it (its body grown - league.dll's FORMS row, not drawn here), the slam on r_st in
        front of it, every enemy within r_r of the point r_off ahead struck, then the armour r_t."""
        t = c.t
        c.on_me("r_roar", t + 250, sheet=c.big)
        c.a("ult", tick(P["r_dur"]))
        at = t + tick(P["r_st"] - 1)
        x, y = me.pos(at)
        sx = x + P["r_off"] // 1000
        c.at_spot("r_slam", at, sx, y, sheet=c.big, under=True)
        for f in foes:
            if abs(f.pos(at)[0] - sx) <= P["r_r"] / 1000 + 15:
                c.on_foe(f, "q_hit", at)
                f.flinches.append(at)
        c.on_me("r_armor", at, sheet=c.big, until=at + tick(P["r_t"]))
        return at + tick(P["r_t"])

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            pincer()
            pincer()
            pincer()
        elif step == "q":
            end = sweep()
            c.wait(max(0, end + 200 - c.t))
        elif step == "e":
            end = charge()
            c.wait(max(0, end + 200 - c.t))
        elif step == "r":
            end = warp()
            c.wait(max(0, end + 200 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：弓着背小跑，两条后腿轮流迈步", ["walk_in"], 200, 170),
          ("普攻 裂钳：钳爪举起砸下。被动 虚空甲壳：身边敌方英雄越多，受到的伤害越少", ["attack"], REACH, 190),
          ("技能1 回旋横扫：原地转一圈，扫中身边一圈的敌人并减速", ["q"], REACH, 190),
          ("技能2 虚空冲锋：直立蓄力，翻身用甲壳冲撞，沿途敌人被撞开，撞到的英雄晕眩", ["e"], 150, 200),
          ("大招 扭曲护甲：长啸变大（游戏里体型变大 25%），猛击前方地面，之后几秒伤害减免", ["r"], REACH, 230)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_riftherald_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[10:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_riftherald_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_riftherald_skills.gif")))


if __name__ == "__main__":
    main()
