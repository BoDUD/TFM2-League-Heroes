#!/usr/bin/env python3
"""Preview images for T-Hex (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_thex.py [--out docs/preview] [--only frames|effects|skills]

  tft_thex_frames.png    every animation's dense frames (hd_, PPU 1.9, as league.dll shows them)
  tft_thex_effects.png   every effect animation, 3x
  tft_thex_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                         (tools/kit/build_thex.py, 60 ticks a second) and as tft.dll plays its parts
                         (addons/tft/src/thex.rs), captioned in Chinese, 4x (preview_brock.py's way): the run; Gatling
                         Barrage (four attacks of four bullets each, the fourth's last bullet the crit); Homing Missiles
                         (the pods' launch flash, six missiles on Darius, Garen and Ashe); Rex Charge (the dash streak, the
                         bite, Darius knocked back and slowed); Hextech Arsenal (the shield, three lasers through the line,
                         each with four missiles); Pilot Eject (it falls, the mech bursts, the enemies near it knocked back).
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
from build_thex import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_thex")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_thex_fx", "tft_thex_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it attacks: the range
                                                # plus both units' collision radii
BITE = 42                        # game px to Darius when the charge's bite lands (its jaws on him)
SPOTS = ((24, -6), (40, 6))      # Garen behind Darius, Ashe further on (game px): in the laser's line
GUN = (9, -17)                   # the gatling's muzzle from its pivot (hd/idle.png's rings (72, 43) at PPU 1.9)
MOUTH = (18, -27)                # the jaws (the laser's start)
SEED = 3


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames; held() plays a tag with its first frame held (the charge)."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "thex", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        return self.play(fr, dur, loop)

    def held(self, tag, first):
        fr = list(dense(self.sp, tag, "thex", self.z))
        fr[0] = (fr[0][0], first)
        return self.play(fr, sum(ms for _, ms in fr), False)

    def play(self, fr, dur, loop):
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def scene(out, steps, gap, W=360, H=170, z=4, tail=900, x0=80):
    """One scene (a list of steps) written to `out`."""
    rnd = random.Random(SEED)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_thex_fx"], fx["tft_thex_big"]
    gy = H - 34
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    foes = (d,)
    if any(s in steps for s in ("q", "r", "p")):                   # two more enemies by Darius
        foes = (d,) + tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
        c.foes = foes[1:]
    c.wait(300)
    count = [0]

    def volley():
        """One attack: a_n bullets from the gatling a_gap ticks apart from atk_st, homing on Darius at a_speed; every
        fourth attack's last bullet the crit."""
        t = c.t
        count[0] += 1
        for k in range(P["a_n"]):
            at = t + tick(P["atk_st"] - 1 + k * P["a_gap"])
            x, y = me.pos(at)
            tx = d.pos(at)[0]
            fly = tick((tx - x - GUN[0]) * 1000 / P["a_speed"])
            c.fly("a_bullet", at, at + fly, x + GUN[0], tx, y + GUN[1])
            last = k == P["a_n"] - 1 and count[0] % 4 == 0
            c.on_foe(d, "a_crit" if last else "a_hit", at + fly)
            d.flinches.append(at + fly)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def missiles():
        """Homing Missiles: the pods' launch flash on q_st, q_n missiles q_gap ticks apart on random enemies."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        at = t + tick(P["q_st"] - 1)
        c.on_me("q_launch", at)
        end = at
        for k in range(P["q_n"]):
            f = rnd.choice(foes)
            mt = at + tick(k * P["q_gap"])
            x, y = f.pos(mt)
            c.at_spot("q_fall", mt, x, y, sheet=c.big, under=False)
            f.flinches.append(mt + 300)
            end = mt + 700
        return end

    def charge():
        """Rex Charge: the dash streak under it, running onto Darius at e_speed (the low charge frame held), the bite on
        arrival: Darius knocked back e_kb x e_kb_t and slowed for e_slow_t."""
        t = c.t
        x, y = me.pos(t)
        to = d.x - BITE
        run = tick((to - x) * 1000 / P["e_speed"])
        c.on_me("e_dash", t, under=True)
        me.moves.append((t, t + run, x, to))
        c.held("skill2", run)
        at = t + run
        c.on_foe(d, "e_hit", at)
        kb = P["e_kb"] * P["e_kb_t"] / 1000
        d.slides.append((at, at + tick(P["e_kb_t"]), kb))
        c.on_foe(d, "e_slow", at, until=at + tick(P["e_slow_t"]))
        d.flinches.append(at)
        return at + tick(P["e_slow_t"])

    def arsenal():
        """Hextech Arsenal: the shield, then r_n beats r_every apart from r_st: the laser bolt from the jaws through the
        line (r_hit on each enemy it passes) and r_m missiles on random enemies spread over the beat."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        c.on_me("r_shield", t, sheet=c.big, until=t + tick(P["r_sh_t"]))
        for k in range(P["r_n"]):
            at = t + tick(P["r_st"] - 1 + k * P["r_every"])
            x, y = me.pos(at)
            x1 = x + MOUTH[0] + P["r_len"] // 1000
            fly = tick((x1 - x - MOUTH[0]) * 1000 / 9000)
            c.fly("r_beam", at, at + fly, x + MOUTH[0], x1, y + MOUTH[1], sheet=c.big)
            for f in foes:
                fx_ = f.pos(at)[0]
                hit = at + tick((fx_ - x - MOUTH[0]) * 1000 / 9000)
                c.on_foe(f, "r_hit", hit)
                f.flinches.append(hit)
            for m in range(P["r_m"]):
                f = rnd.choice(foes)
                mt = at + tick(m * P["r_every"] // P["r_m"])
                fx_, fy = f.pos(mt)
                c.at_spot("q_fall", mt, fx_, fy, sheet=c.big, under=False)
        return t + tick(P["r_dur"]) + 300

    def eject():
        """Pilot Eject (tft.dll): it falls, and as it dies the mech bursts - every enemy within p_r knocked back
        p_kb x p_kb_t and stunned p_stun."""
        t = c.t
        c.a("dead", 1000)
        at = t + 100
        x, y = me.pos(at)
        c.at_spot("p_blast", at, x, y, sheet=c.big, under=False)
        kb = P["p_kb"] * P["p_kb_t"] / 1000
        for f in foes:
            if abs(f.pos(at)[0] - x) <= P["p_r"] / 1000 + 15:
                f.slides.append((at, at + tick(P["p_kb_t"]), kb))
                f.flinches.append(at)
        return at + tick(P["p_stun"])

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            for _ in range(4):
                volley()
        else:
            end = {"q": missiles, "e": charge, "r": arsenal, "p": eject}[step]()
            c.wait(max(0, end + 200 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：机械霸龙迈开鸟腿奔跑，两条腿轮流迈步", ["walk_in"], 200, 170),
          ("普攻 加特林弹幕：每次攻击连射4发子弹；每第四次攻击最后一发暴击加伤", ["attack"], REACH, 170),
          ("技能1 追踪导弹：背部导弹舱翻开，6枚导弹落在附近的敌人身上", ["q"], REACH, 200),
          ("技能2 霸龙冲撞：冲向目标一口咬住，击退并减速", ["e"], 110, 180),
          ("大招 海克斯军械库：获得护盾，每秒一道贯穿激光（每穿一人伤害递减）+ 4枚导弹", ["r"], REACH, 210),
          ("被动 驾驶员弹射：阵亡时机甲爆炸，附近敌人被击退并晕眩", ["p"], 30, 200)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_thex_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[9:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_thex_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_thex_skills.gif")))


if __name__ == "__main__":
    main()
