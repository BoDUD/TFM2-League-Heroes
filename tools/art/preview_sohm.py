#!/usr/bin/env python3
"""Preview images for Sohm (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_sohm.py [--out docs/preview] [--only frames|effects|skills]

  tft_sohm_frames.png    every animation's dense frames (hd_, PPU 1.8, as league.dll shows them)
  tft_sohm_effects.png   every effect animation, 3x
  tft_sohm_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                         (tools/kit/build_sohm.py, 60 ticks a second) and as tft.dll plays its parts
                         (addons/tft/src/sohm.rs), captioned in Chinese, 4x (preview_daeja.py's way): the swim; the water
                         bolts; Tideblossom (the wave through Darius and Garen at Ashe, the water flower over her, the tide
                         behind Sohm); Tidecaller's Guard (the ripple, the bubble on the weakest - herself here); Tidal
                         Bloom (the lotus bursting on every flower: Darius's and Ashe's from two Tideblossoms, the petals
                         on everyone round them).
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
from build_sohm import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_sohm")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_sohm_fx", "tft_sohm_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = P["atk_range"] // 1000   # game px between her pivot and Darius's when she attacks
SPOTS = ((22, -3), (46, 3))      # Garen and Ashe behind Darius, on the line (game px)
OVERSHOOT = 8                    # tft.dll flies the wave this far past its target (sohm.rs OVERSHOOT 8000)


class Clip(SilcoClip):
    """preview_silco's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "sohm", self.z))
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


def scene(out, steps, gap, W=300, H=170, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_sohm_fx"], fx["tft_sohm_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if any(s in steps for s in ("q", "r")):                   # two more enemies behind Darius
        c.foes = tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
    foes = (d,) + tuple(c.foes)
    flowers = []
    c.wait(300)

    def tide(at):
        """Lagoon Power: a cast lights her tide behind her for p_t."""
        c.on_me("p_glow", at, sheet=big, until=at + tick(P["p_t"]), under=True)

    def bolt():
        """One attack: the water bolt on a_rel (homing), its splash on Darius."""
        rel = c.t + tick(P["a_rel"] - 1)
        c.shot("a_bolt", "a_hit", rel, P["a_speed"])
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def wave(target):
        """Tideblossom: the rise, the S-thrust on q_rel: the wave at `target` (the nearest without a flower), through
        everyone on its way and OVERSHOOT past it, the water flower over the target."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        rel = t + tick(P["q_rel"] - 1)
        tide(rel)
        x0_ = me.pos(rel)[0] + 4
        x1 = target.pos(rel)[0] + OVERSHOOT
        t1 = rel + tick((x1 - x0_) * 1000.0 / P["q_speed"])
        c.fly("q_wave", rel, t1, x0_, x1, me.y - 14, sheet=big)
        for foe in foes:
            fx_ = foe.pos(rel)[0]
            if x0_ <= fx_ <= x1:
                th = rel + tick((fx_ - x0_) * 1000.0 / P["q_speed"])
                c.on_foe(foe, "q_hit", th)
                foe.flinches.append(th)
                if foe is target:
                    flowers.append((foe, th))
        return t1 + 200

    def guard():
        """Tidecaller's Guard: the gather, the push on e_rel: the ripple at her, the bubble on the weakest ally in e_ar
        (no ally here: herself) for e_sh_t."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_rel"] - 1)
        tide(at)
        c.on_me("e", at)
        c.on_me("e_shield", at, until=at + tick(P["e_sh_t"]))
        return at + tick(P["e_sh_t"])

    def bloom():
        """Tidal Bloom: the coil, the rise; on r_rel every flower bursts - the lotus on each flowered one, the petals
        on everyone within r_r of it (once each); the flowers gone."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        at = t + tick(P["r_rel"] - 1)
        tide(at)
        hit = set()
        for foe, _ in flowers:
            x, y = foe.pos(at)
            c.at_spot("r_bloom", at, x, y, sheet=big, under=False)
            for f in foes:
                fx_, fy = f.pos(at)
                if f not in hit and (fx_ - x) ** 2 + (fy - y) ** 2 <= (P["r_r"] / 1000) ** 2:
                    hit.add(f)
                    c.on_foe(f, "r_hit", at + 80)
                    f.flinches.append(at + 80)
        return at + 800

    def flowers_on(*who):
        """Flowers already standing (from earlier Tideblossoms) over these, till the bloom."""
        for foe in who:
            flowers.append((foe, c.t))

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
        elif step == "q":
            end = wave(foes[-1])
            c.wait(max(0, end + 300 - c.t))
            end = wave(d)
            c.wait(max(0, end + 600 - c.t))
        elif step == "e":
            end = guard()
            c.wait(max(0, end + 300 - c.t))
        elif step == "r":
            flowers_on(d, foes[-1])
            c.wait(300)
            end = bloom()
            c.wait(max(0, end + 300 - c.t))
    for foe, t0 in flowers:   # every flower over its one till the bloom (or the scene's end)
        c.on_foe(foe, "q_flower", t0, until=(c.t if "r" not in steps else t0 + 300 + tick(P["r_rel"])))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：平着身子在空中游，波浪从鬃毛后一路传到尾鳍", ["walk_in"], 180, 170),
          ("普攻 水泡弹：吐出水弹打向目标", ["attack"], REACH, 170),
          ("技能1 潮涌 + 被动：潮涌穿过沿途敌人，目标头顶开出水之花；每次施法身后潮水涌起（叠法强和攻速）", ["q"], 40, 170),
          ("技能2 海潮护佑：小爪一推，给生命比例最低的队友套上水盾（这里没有队友，套在自己身上）", ["e"], REACH, 170),
          ("大招 潮汐绽放：所有水之花一齐绽放，周围的敌人被花瓣水花打中", ["r"], 40, 200)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_sohm_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[8:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_sohm_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_sohm_skills.gif")))


if __name__ == "__main__":
    main()
