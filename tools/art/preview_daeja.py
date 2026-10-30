#!/usr/bin/env python3
"""Preview images for Daeja (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_daeja.py [--out docs/preview] [--only frames|effects|skills]

  tft_daeja_frames.png    every animation's dense frames (hd_, PPU 1.72, as league.dll shows them)
  tft_daeja_effects.png   every effect animation, 3x
  tft_daeja_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                          (tools/kit/build_daeja.py, 60 ticks a second) and as tft.dll plays its parts
                          (addons/tft/src/daeja.rs), captioned in Chinese, 4x (preview_nomsy.py's way): the walk; the
                          wind bolt and the three barrage bolts after it, the broken ward on Darius; Windblast (the wave
                          down the line through the three); Wingbeat Retreat (the gust at Darius, his slow, the hop
                          back); Sky Gale (the take-off, three big waves through the three from the air, the landing).
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
from build_daeja import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_daeja")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_daeja_fx", "tft_daeja_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = P["atk_range"] // 1000   # game px between his pivot and Darius's when he attacks
GUST_MID = P["e_len"] / 2000     # the gust line's middle ahead of him (game px)
SPOTS = ((26, -3), (52, 3))      # Garen and Ashe behind Darius, on the line (game px)


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "daeja", self.z))
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
    small, big = fx["tft_daeja_fx"], fx["tft_daeja_big"]
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
        """One attack: the wind bolt on a_rel (homing), then the p_n barrage bolts p_gap ticks apart, each breaking
        Darius's ward a little more (p_shred, p_mr_t ticks each)."""
        rel = c.t + tick(P["a_rel"] - 1)
        c.shot("a_bolt", "a_hit", rel, P["a_speed"])
        for k in range(1, P["p_n"] + 1):
            hit = c.shot("p_bolt", "p_hit", rel + tick(k * P["p_gap"]), P["p_speed"])
            c.on_foe(d, "p_shred", hit, until=hit + tick(P["p_mr_t"]))
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def wave(tag, hit_tag, rel, speed, length):
        """A penetrating wave from him along the line through the three (tft.dll's): every one it passes is hit."""
        x0 = me.pos(rel)[0] + 4
        x1 = x0 + length
        t1 = rel + tick(length * 1000.0 / speed)
        c.fly(tag, rel, t1, x0, x1, me.y - 14, sheet=big)
        for foe in foes:
            fx_ = foe.pos(rel)[0]
            if x0 <= fx_ <= x1:
                th = rel + tick((fx_ - x0) * 1000.0 / speed)
                c.on_foe(foe, hit_tag, th, sheet=big if hit_tag == "r_hit" else small)
                foe.flinches.append(th)
        return t1

    def windblast():
        """Windblast: the wings raised back, swept forward on q_rel: the wave down the line through the three."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        return wave("q_wave", "q_hit", t + tick(P["q_rel"] - 1), P["q_speed"], P["q_len"] / 1000) + 200

    def wingbeat():
        """Wingbeat Retreat: one beat on e_rel, the gust on its line at Darius (slowed), the hop back e_back x e_back_t."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_rel"] - 1)
        x = me.pos(at)[0]
        c.looped("e_gust", at, at + tick(12), x + GUST_MID, me.y - 3, big)
        c.on_foe(d, "e_slow", at, until=at + tick(P["e_slow_t"]))
        d.flinches.append(at)
        back = P["e_back"] * P["e_back_t"] / 1000
        me.moves.append((at, at + tick(P["e_back_t"]), x, x - back))
        return at + tick(P["e_slow_t"])

    def skygale():
        """Sky Gale: up he goes (the downdraft under him), r_n big waves r_gap ticks apart from r_rise, the landing."""
        t = c.t
        air = P["r_rise"] + P["r_n"] * P["r_gap"]
        c.on_me("r_fly", t, until=t + tick(air), under=True)
        end = t
        for k in range(P["r_n"]):
            end = wave("r_wave", "r_hit", t + tick(P["r_rise"] - 1 + k * P["r_gap"]), P["r_speed"], P["r_len"] / 1000)
        c.a("ult", tick(air + P["r_land"]))
        return max(end, c.t)

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
        elif step in ("q", "e", "r"):
            end = {"q": windblast, "e": wingbeat, "r": skygale}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：两条腿轮流迈步往前走", ["walk_in"], 160, 170),
          ("普攻 + 被动 三连弹幕：推出风弹，再追加三颗小风弹，每颗削减目标魔抗（可叠加）", ["attack"], REACH, 170),
          ("技能1 罡风轰击：双翼前扫，朝敌人最多的直线轰出穿透的风波", ["q"], 40, 170),
          ("技能2 振翼退风：振翅扇风减速身边的敌人，自己借风后跳", ["e"], 30, 170),
          ("大招 苍穹罡风：展翅飞起，朝敌人最多的直线连续轰出三道大冲击波，然后落地", ["r"], 40, 200)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_daeja_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[8:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_daeja_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_daeja_skills.gif")))


if __name__ == "__main__":
    main()
