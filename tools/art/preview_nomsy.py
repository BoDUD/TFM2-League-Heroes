#!/usr/bin/env python3
"""Preview images for Nomsy (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_nomsy.py [--out docs/preview] [--only frames|effects|skills]

  tft_nomsy_frames.png    every animation's dense frames (hd_, PPU 2.6, as league.dll shows them)
  tft_nomsy_effects.png   every effect animation, 3x
  tft_nomsy_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                          (tools/kit/build_nomsy.py, 60 ticks a second) and as tft.dll plays its parts
                          (addons/tft/src/nomsy.rs), captioned in Chinese, 4x (preview_sevika.py's way): the walk; the
                          fire bolts; Dragon Body (the low-health heal each second); Fireballs! (the big fireball lobbed
                          at Darius, its explosion, the two small ones bouncing on to Garen and Ashe); Dragon Breath (the
                          cone over the three, burning); Dragon Ascension (the take-off, the hover, ten fireballs falling,
                          the landing and the ascended aura).
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
from preview_silco import Clip as SilcoClip, Lob, px_tick  # noqa: E402
from build_nomsy import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_nomsy")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_nomsy_fx", "tft_nomsy_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = P["atk_range"] // 1000   # game px between her pivot and Darius's when she attacks
BREATH_MID = P["e_len"] / 2000   # the breath line's middle ahead of her (game px)
SPOTS = ((28, -10), (22, 12))    # Garen and Ashe from Darius (game px)


class Clip(SilcoClip):
    """preview_silco's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "nomsy", self.z))
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
    small, big = fx["tft_nomsy_fx"], fx["tft_nomsy_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if any(s in steps for s in ("q", "e", "r")):              # two more enemies by Darius
        c.foes = tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
    foes = (d,) + tuple(c.foes)
    c.wait(300)

    def bolt():
        """One attack: the fire bolt spat on a_rel (homing), its hit."""
        rel = c.t + tick(P["a_rel"] - 1)
        c.shot("a_bolt", "a_hit", rel, P["a_speed"])
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def mend():
        """Dragon Body: under p_low% health a heal every p_every ticks (tft.dll's p_heal buff on her); Darius hits her."""
        t = c.t
        for k in range(3):
            c.on_me("p_heal", t + tick(k * P["p_every"]), until=t + tick(k * P["p_every"] + 40))
        d.attacks += [t + 100, t + 900, t + 1700]
        c.a("idle", tick(3 * P["p_every"]), loop=True)

    def fireballs():
        """Fireballs!: the rise, the leap throwing the big one at Darius (q_fall ticks), the blast, two small ones on."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        rel = t + tick(P["q_rel"] - 1)
        land = rel + tick(P["q_fall"])
        x0_, y0_ = me.pos(rel)[0] + 10, me.y - 14
        x1, y1 = d.pos(rel)
        c.over.append(Lob(frames_of(big, "q_ball"), rel, int(x0_), int(y0_), loop=True, until=land, x1=int(x1),
                          y1=int(y1)))
        c.on_foe(d, "q_hit", land, sheet=big)
        d.flinches.append(land)
        for foe in c.foes:
            fx_, fy_ = foe.pos(land)
            t1 = land + max(1, abs(fx_ - x1)) / px_tick(P["q_speed"])
            c.fly("q_bounce", land, t1, x1, fx_, fy_)
            c.on_foe(foe, "q_bounce_hit", t1)
            foe.flinches.append(t1)
        return land + 600

    def breath():
        """Dragon Breath: the inhale, then the cone from her mouth over the three; each one burning."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_rel"] - 1)
        c.looped("e_flame", at, t + tick(P["e_dur"]), me.pos(at)[0] + BREATH_MID, gy, big)
        for foe in foes:
            foe.flinches.append(at)
            c.on_foe(foe, "e_burn", at, until=at + tick(P["e_burn_t"]))
        return at + tick(P["e_burn_t"])

    def ascension():
        """Dragon Ascension: up she goes (r_fly glowing under her), r_n fireballs falling on the three in turn every
        r_gap ticks from r_rel, each hitting r_fall_t later; she lands ascended (r_up)."""
        t = c.t
        air = P["r_rel"] + P["r_n"] * P["r_gap"] + P["r_fall_t"]
        c.on_me("r_fly", t, until=t + tick(air), under=True)
        for k in range(P["r_n"]):
            foe = foes[k % len(foes)]
            t0 = t + tick(P["r_rel"] - 1 + k * P["r_gap"])
            c.on_foe(foe, "r_fall", t0, sheet=big)
            c.on_foe(foe, "r_hit", t0 + tick(P["r_fall_t"]), sheet=big)
            foe.flinches.append(t0 + tick(P["r_fall_t"]))
        c.a("ult", tick(air + P["r_land"]))
        c.on_me("r_up", c.t, until=c.t + 1500, under=True)
        c.a("idle", 1500, loop=True)
        return c.t

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            bolt()
            bolt()
        elif step == "p":
            mend()
        elif step in ("q", "e", "r"):
            end = {"q": fireballs, "e": breath, "r": ascension}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：摇摇摆摆地往前蹦", ["walk_in"], 160, 170),
          ("普攻：张嘴吐出小火团", ["attack"], REACH, 170),
          ("被动 龙神之躯：生命值低于 40% 时每秒回复 3% 最大生命值", ["p"], 40, 170),
          ("技能1 火球！：抛出大火球，落地爆炸，再弹出两颗小火球打附近的敌人", ["q"], 60, 170),
          ("技能2 龙息：向前喷出扇形火焰，灼烧并降低魔抗", ["e"], 42, 170),
          ("大招 龙神飞升：飞上天盘旋，十颗火球砸向敌人，落地后攻速法强提升", ["r"], 60, 200)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_nomsy_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[8:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_nomsy_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_nomsy_skills.gif")))


if __name__ == "__main__":
    main()
