#!/usr/bin/env python3
"""Preview images for Sevika (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_sevika.py [--out docs/preview] [--only frames|effects|skills]

  tft_sevika_frames.png    every animation's dense frames (hd_, PPU 1.8, as league.dll shows them)
  tft_sevika_effects.png   every effect animation, 3x
  tft_sevika_skills.gif    each skill alone with its effects against Darius (and Garen), timed like the kit
                           (tools/kit/build_sevika.py, 60 ticks a second) and as tft.dll plays its parts
                           (addons/tft/src/sevika.rs), captioned in Chinese, 4x (preview_renni.py's way): the run; the
                           punches and the clamp; High Roller (the slot machine's four outcomes: rockets, shield,
                           shimmer, the jackpot); the Flamethrower (five waves into Darius and Garen, burning); the
                           Extendo-Punch (Darius knocked into Garen, both stunned); Chomp (the dash, two bites, the
                           bleed, Darius executed and the re-dash to Garen).
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
from build_sevika import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_sevika")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_sevika_fx", "tft_sevika_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
REACH = 38                       # game px between her pivot and Darius's when she punches (her claws reach ~28 ahead)
BEHIND = 30                      # Garen behind Darius (game px)
FLAME_MID = P["q_len"] / 2000    # the flame line's middle ahead of her (game px)
ROCKET_LIFT, FIST_LIFT = 16, 8   # sevika.rs: where the rockets and the fist leave her


class Clip(SilcoClip):
    """preview_silco's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "sevika", self.z))
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


def scene(out, steps, gap, W=300, H=150, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_sevika_fx"], fx["tft_sevika_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    garen = Foe(load(GAREN), far + BEHIND, gy)
    if any(s in steps for s in ("p", "q", "e", "r")):              # a second enemy behind Darius
        c.foes = (garen,)
    c.wait(300)

    def punch(clamp=False):
        """One attack: a punch (every third the claws clamp, its own frames)."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a2_hit" if clamp else "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack2" if clamp else "attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def roll(mod):
        """The slot machine over her head, and what it paid out (tft.dll's Roll)."""
        t = c.t
        c.on_me("p", t)
        if mod == "rockets":
            for k in range(P["p_rk_n"]):
                t0 = t + tick(k * P["p_rk_gap"] + 1)
                foe = (d, garen)[k % 2]
                x0_, x1_ = me.pos(t0)[0], foe.x
                t1 = t0 + abs(x1_ - x0_) / px_tick(P["p_rk_speed"])
                c.fly("p_rocket", t0, t1, x0_, x1_, gy - ROCKET_LIFT)
                c.on_foe(foe, "p_rocket_hit", t1)
                foe.flinches.append(t1)
        elif mod == "shield":
            c.on_me("p_shield", t + 50)
            d.attacks += [t + 300, t + 1100]
        elif mod == "shimmer":
            c.on_me("p_shimmer", t, until=t + tick(P["p_as_t"]))
        else:
            c.on_me("p_jackpot", t + 300, sheet=big)
            c.on_me("p_triple", t + 900, until=t + 2400)
        c.a("idle", 1400 if mod != "jackpot" else 2400, loop=True)

    def flame():
        """Flamethrower: q_n waves q_gap apart from q_st into the cone; the flame on its line the whole time."""
        t = c.t
        c.a("skill", tick(1))
        c.a("flame", tick(P["q_dur"] - 1))
        x = me.pos(t)[0] + FLAME_MID
        c.looped("q_flame", t + tick(P["q_st"] - 1), t + tick(P["q_dur"]), x, gy, big)
        for k in range(P["q_n"]):
            th = t + tick(P["q_st"] - 1 + k * P["q_gap"])
            for foe in (d, garen):
                foe.flinches.append(th)
        for foe in (d, garen):
            c.on_foe(foe, "q_burn", t + tick(P["q_st"]), until=t + tick(P["q_dur"] + P["q_burn_t"]))
        return t + tick(P["q_dur"])

    def extendo():
        """Extendo-Punch: the fist flies at Darius from e_st, knocks him back into Garen: both stunned."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        t0 = t + tick(P["e_st"] - 1)
        x0_ = me.pos(t0)[0] + 10
        t1 = t0 + max(1, d.x - x0_) / px_tick(P["e_speed"])
        c.fly("e_fist", t0, t1, x0_, d.x, gy - FIST_LIFT)
        c.on_foe(d, "e_hit", t1)
        d.flinches.append(t1)
        slide = BEHIND - 12
        land = t1 + tick(P["e_kb_t"])
        d.slides.append((t1, land, slide))
        c.on_foe(garen, "e_hit", land)
        garen.flinches.append(land)
        for foe in (d, garen):
            c.on_foe(foe, "e_stun", land, until=land + tick(P["e_stun"]))
        return land + tick(P["e_stun"])

    def chomp():
        """Chomp: the dash at Darius, two bites (the first stuns), the bleed; Darius under the line executed, then the
        re-dash to Garen and two bites more at r_fall%."""
        t = c.t
        x_from, x_to = me.pos(t)[0], d.x - REACH
        land = t + max(1, x_to - x_from) / px_tick(P["r_speed"])
        me.moves.append((t, land, x_from, x_to))
        c.a("ult", tick(1))
        c.a("dash", land - c.t)

        def bites(foe, at):
            c.a("chomp", tick(P["r_chomp_t"]))
            last = at
            for k in range(P["r_n"]):
                last = at + tick(P["r_first"] + k * P["r_gap"])
                c.on_foe(foe, "r_hit", last)
                foe.flinches.append(last)
            c.on_foe(foe, "r_bleed", at + tick(P["r_first"]), until=at + tick(P["r_first"]) + 2500)
            return last
        last = bites(d, land)
        c.on_foe(d, "r_kill", last, sheet=big)
        d.death = last + 120
        # the re-dash: on to Garen, HOP_GAP short of him
        t2 = c.t
        x2 = garen.x - REACH
        me.moves.append((t2, t2 + 1, me.pos(t2)[0], x2))
        last2 = bites(garen, t2)
        return last2 + 600

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
            punch(clamp=True)
        elif step == "p":
            for mod in ("rockets", "shield", "shimmer", "jackpot"):
                roll(mod)
        elif step in ("q", "e", "r"):
            end = {"q": flame, "e": extendo, "r": chomp}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：往前跑，机械臂甩在身侧", ["walk_in"], 160, 170),
          ("普攻 机械铁拳：铁拳重击，每第三下爪钳钳击", ["attack"], REACH, 170),
          ("被动 百变铁手：每次放技能摇老虎机——火箭 / 护盾 / 微光攻速 / 头奖（本次技能强化）", ["p"], 70, 190),
          ("技能1 喷火器：前方扇形喷火 1.2 秒，五段伤害并灼烧，自己减伤 30%", ["q"], 50, 170),
          ("技能2 伸缩拳：铁拳打中达瑞斯并击退，撞上身后的盖伦，两人都眩晕", ["e"], 70, 170),
          ("大招 嚼一嚼：冲上去连咬两口（眩晕+流血），低血直接咬死，再冲向下一个", ["r"], 90, 170)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_sevika_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[8:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_sevika_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_sevika_skills.gif")))


if __name__ == "__main__":
    main()
