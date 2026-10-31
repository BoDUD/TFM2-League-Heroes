#!/usr/bin/env python3
"""Preview images for the Elder Dragon (the tft pack), built from the exported game sprites (so they also prove the
sheets load).

    python tools/art/preview_elderdragon.py [--out docs/preview] [--only frames|effects|skills]

  tft_elderdragon_frames.png    every animation's dense frames (hd_, PPU 2.84, as league.dll shows them)
  tft_elderdragon_effects.png   every effect animation, 3x
  tft_elderdragon_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                                (tools/kit/build_elderdragon.py, 60 ticks a second) and as tft.dll plays its parts
                                (addons/tft/src/elderdragon.rs), captioned in Chinese, 3x (preview_raptor.py's way): the
                                low flight; Dragonfire Bite (the jaws' mark, the splash's sparks on the two beside its
                                target, the Elder buff's execution on the last bite); Flame Breath (the fire along the line
                                through the three, each burst and Ignited); Wing Storm (the gust round it, the crystal
                                guard on it, the three knocked back and slowed); Heat Without Equal (up into the sky, the
                                slam's ring where it lands, the three dazed and Ignited, its hunger, the breath at once).
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
from preview_garen import T, contact, frames_of, load  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me  # noqa: E402
import preview_zoe as Z  # noqa: E402
from preview_silco import Clip as SilcoClip, px_tick  # noqa: E402
from build_elderdragon import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_elderdragon")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_elderdragon_fx", "tft_elderdragon_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it bites
SPLASH = ((14, -9), (16, 9))     # Garen and Ashe beside Darius (game px): within the bite's splash
LINE = ((26, 2), (50, -2))       # Garen and Ashe behind Darius on the breath's line
MOUTH = (18, -9)                 # where its fire leaves (game px from its pivot: elderdragon.rs JAWS, 9 north)


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "elderdragon", self.z))
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


def scene(out, steps, gap, W=330, H=190, z=3, tail=900, x0=80):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_elderdragon_fx"], fx["tft_elderdragon_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    spots = LINE if ("q" in steps or "r" in steps) else SPLASH
    foes = (d,)
    if any(s in steps for s in ("attack", "q", "e", "r")):
        foes = (d,) + tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, spots))
        c.foes = foes[1:]
    c.wait(300)

    def ignite(f, at):
        c.on_foe(f, "ig", at, until=at + tick(P["ig_t"]))

    def bite(execute=False):
        """One bite: the jaws' mark on Darius on atk_st, the splash's sparks on the two beside him; the Elder buff's
        execution on the last."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        for f in foes[1:]:
            c.on_foe(f, "a_splash", hit)
            f.flinches.append(hit)
        if execute:
            c.on_foe(d, "p_exec", hit + 40)
            d.death = hit + 400
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def breath(at):
        """Flame Breath: on `at` the fire leaves its jaws along the line and burns each one as it reaches him."""
        x, y = me.pos(at)
        ox = x + MOUTH[0]
        end = ox + P["q_len"] / 1000
        c.fly("q_fire", at, at + tick(P["q_len"] / P["q_speed"]), ox, end, y + MOUTH[1])
        for f in foes:
            fx_ = f.pos(at)[0]
            t = at + tick((fx_ - ox) * 1000.0 / P["q_speed"])
            c.on_foe(f, "q_hit", t)
            f.flinches.append(t)
            ignite(f, t)
        return at + tick(P["q_len"] / P["q_speed"])

    def storm():
        """Wing Storm: on e_st the gust round it, its guard for e_t, the three knocked back (e_kb x e_kb_t) and slowed."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_st"] - 1)
        c.on_me("e_cast", at, sheet=c.big)
        c.on_me("e_guard", at, sheet=c.big, until=at + tick(P["e_t"]))
        back = P["e_kb"] * P["e_kb_t"] / 1000
        for f in foes:
            f.slides.append((at, at + tick(P["e_kb_t"]), back))
            f.flinches.append(at)
            c.on_foe(f, "e_slow", at + tick(P["e_kb_t"]), until=at + tick(P["e_t"]))
        return at + tick(P["e_t"])

    def heat():
        """Heat Without Equal: up into the sky for r_air, the slam's ring where it lands, the three dazed and Ignited,
        its hunger for r_vamp_t (shown 1.6 s), the breath on r_air + q_st."""
        t = c.t
        c.a("ult", tick(P["r_air"] + P["q_st"] + 4))
        land = t + tick(P["r_air"] - 1)
        x, y = me.pos(land)
        c.at_spot("r_slam", land, x + 3, y + 3, sheet=c.big, under=True)
        for f in foes:
            c.on_foe(f, "r_stun", land, until=land + tick(P["r_stun"]))
            f.flinches.append(land)
            ignite(f, land)
        c.on_me("r_vamp", land, sheet=c.big, until=land + 1600)
        return max(breath(t + tick(P["r_air"] + P["q_st"] - 1)), land + 1600)

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            bite()
            bite(execute=True)
        elif step == "q":
            t = c.t
            c.a("skill", tick(P["q_dur"]))
            end = breath(t + tick(P["q_st"] - 1))
            c.wait(max(0, end + 600 - c.t))
        elif step == "e":
            end = storm()
            c.wait(max(0, end + 200 - c.t))
        elif step == "r":
            end = heat()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：低空飞行，翅膀一下下扇", ["walk_in"], 200, 170),
          ("普攻 龙焰撕咬：咬目标，身边的敌人被溅射；被动 远古巨龙霸符：残血的敌方英雄被处决", ["attack"], REACH, 170),
          ("技能1 烈焰吐息：朝敌人最多的直线喷龙焰，逐个递减，并【引燃】", ["q"], REACH, 170),
          ("技能2 龙翼风暴：立起身猛拍双翼，击退并减速身边的敌人，自己减伤", ["e"], REACH, 170),
          ("大招 绝伦火热：无敌飞上天空再砸落，晕眩并【引燃】，全能吸血，立刻再喷一口吐息", ["r"], REACH, 260)]


def skills(out, z=3):
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_elderdragon_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_elderdragon_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_elderdragon_skills.gif")))


if __name__ == "__main__":
    main()
