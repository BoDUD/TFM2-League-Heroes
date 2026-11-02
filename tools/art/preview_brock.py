#!/usr/bin/env python3
"""Preview images for Brock (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_brock.py [--out docs/preview] [--only frames|effects|skills]

  tft_brock_frames.png    every animation's dense frames (hd_, PPU 1.16, as league.dll shows them)
  tft_brock_effects.png   every effect animation, 3x
  tft_brock_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                          (tools/kit/build_brock.py, 60 ticks a second) and as tft.dll plays its parts
                          (addons/tft/src/brock.rs), captioned in Chinese, 4x (preview_sentinel.py's way): the heavy walk;
                          Quake Fist (three blows: the burst, the quake ring round Darius, the third throws him up);
                          Boulder Toss (the boulder flying, its smash, the rubble on the slowed); Moss Grip (the roots
                          bursting under Darius and binding his legs, the mossy shell); Seismic Slam (the launch dust,
                          out of sight while he moves, the landing on Darius, the shockwave, everyone in reach thrown up,
                          the rocks falling on them).
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
from build_brock import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_brock")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_brock_fx", "tft_brock_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between his pivot and Darius's when he attacks: the range
                                                # plus both units' collision radii (his fists reach that far)
SPOTS = ((22, -4), (38, 6))      # Garen behind Darius, Ashe further on (game px): inside the slam's reach
LEAP = 70                        # game px to Darius for the ult (r_range 60000 + the bodies)


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames; part() plays some of a tag's frames (the ult's seen parts)."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "brock", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        if dur and not loop and dur < sum(ms for _, ms in fr):   # a shorter play: every frame shorter alike
            k = dur / sum(ms for _, ms in fr)
            fr = [(f, ms * k) for f, ms in fr]
        return self.play(fr, dur, loop)

    def part(self, tag, k0, k1):
        fr = list(dense(self.sp, tag, "brock", self.z))[k0:k1]
        return self.play(fr, sum(ms for _, ms in fr), False)

    def play(self, fr, dur, loop):
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def scene(out, steps, gap, W=360, H=170, z=4, tail=900, x0=80):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_brock_fx"], fx["tft_brock_big"]
    gy = H - 34
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    foes = (d,)
    if "r" in steps:                                               # two more enemies by Darius
        foes = (d,) + tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
        c.foes = foes[1:]
    c.wait(300)
    count = [0]

    def fist():
        """One attack: Quake Fist's blow on atk_st, the ring round Darius; every third blow throws him up."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        x, y = d.pos(hit)
        c.at_spot("a_quake", hit, x, y, under=True)
        d.flinches.append(hit)
        count[0] += 1
        if count[0] % 3 == 0:
            c.on_foe(d, "a_up", hit, until=hit + tick(P["a_up"]) + 100)
            d.hops.append((hit, hit + tick(P["a_up"]), 8))
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def toss():
        """Boulder Toss: the boulder thrown on q_st, flying to Darius at q_speed, the smash and the rubble."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        at = t + tick(P["q_st"] - 1)
        x, y = me.pos(at)
        tx = d.pos(at)[0]
        fly = tick((tx - x) * 1000 / P["q_speed"])
        c.fly("q_rock", at, at + fly, x + 6, tx, y - 14)
        c.on_foe(d, "q_hit", at + fly)
        c.on_foe(d, "q_slow", at + fly, until=at + fly + tick(P["q_slow_t"]))
        d.flinches.append(at + fly)
        return at + fly + tick(P["q_slow_t"])

    def grip():
        """Moss Grip: on e_st the roots burst under Darius and bind his legs e_root; his mossy shell for e_sh_t."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_st"] - 1)
        x, y = d.pos(at)
        c.at_spot("e_vine", at, x, y, under=False)
        c.on_foe(d, "e_root", at, until=at + tick(P["e_root"]))
        c.on_me("e_shield", at, sheet=c.big, until=at + tick(P["e_sh_t"]))
        d.flinches.append(at)
        return at + tick(P["e_sh_t"])

    def slam():
        """Seismic Slam: the crouch and spring (the launch dust where he stood), out of sight from r_go to r_at - 6
        while he moves onto Darius, falling and landing on r_at: the shockwave, every enemy within r_r thrown up r_up,
        then r_rocks rocks falling on them in turn."""
        t = c.t
        x0_, y = me.pos(t)
        c.part("ult", 0, 3)                                         # the crouch, the spring (to r_go)
        c.at_spot("r_jump", t + 200, x0_, y, sheet=c.big, under=True)
        c.t = t + tick(P["r_at"] - 6)                              # out of sight
        land = d.pos(c.t)[0] - 12
        me.moves.append((t + tick(P["r_at"] - 7), t + tick(P["r_at"] - 7) + 1, x0_, land))
        c.part("ult", 4, 8)                                         # falling, the landing, standing up
        at = t + tick(P["r_at"] - 1)
        c.at_spot("r_slam", at, land, y, sheet=c.big, under=True)
        for f in foes:
            if abs(f.pos(at)[0] - land) <= P["r_r"] / 1000 + 15:
                c.on_foe(f, "r_hit", at, until=at + tick(P["r_up"]))
                f.hops.append((at, at + tick(P["r_up"]), 14))
        for k in range(P["r_rocks"]):
            f = foes[k % len(foes)]
            rt = at + tick(P["r_rock_t"] + k * P["r_rock_gap"])
            fx_, fy = f.pos(rt)
            c.at_spot("r_rock", rt, fx_, fy, sheet=c.big, under=False)
        return at + tick(P["r_rock_t"] + P["r_rocks"] * P["r_rock_gap"]) + 700

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            fist()
            fist()
            fist()
        elif step == "q":
            end = toss()
            c.wait(max(0, end + 200 - c.t))
        elif step == "e":
            end = grip()
            c.wait(max(0, end + 200 - c.t))
        elif step == "r":
            end = slam()
            c.wait(max(0, end + 200 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：沉重地迈步，两只脚轮流抬起", ["walk_in"], 200, 170),
          ("普攻 震地拳：双拳砸下，目标周围一圈震波溅射；每第三下击飞目标。被动 岩心不动：免疫控制", ["attack"], REACH, 190),
          ("技能1 巨岩投掷：抡起大石头砸向目标，造成伤害并减速", ["q"], 110, 180),
          ("技能2 苔藤缠握：树根从目标脚下钻出定住他，自己套上苔石护盾", ["e"], REACH + 10, 200),
          ("大招 震地猛击：跃起砸向敌人，离落点越远伤害越低，第一次被砸中的击飞，随后天上落下碎石", ["r"], LEAP, 230)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_brock_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[10:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_brock_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_brock_skills.gif")))


if __name__ == "__main__":
    main()
