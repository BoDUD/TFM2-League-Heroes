#!/usr/bin/env python3
"""Preview images for Meepsie (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_meepsie.py [--out docs/preview] [--only frames|effects|skills]

  tft_meepsie_frames.png    every animation's dense frames (hd_, PPU 2.875, as league.dll shows them)
  tft_meepsie_effects.png   every effect animation, 3x
  tft_meepsie_skills.gif    each skill alone with its effects against Darius, Garen and Ashe (the meeps with Garen and
                            Braum on its side), timed like the kit (tools/kit/build_meepsie.py, 60 ticks a second) and
                            as tft.dll plays its parts (addons/tft/src/meepsie.rs), captioned in Chinese, 3x
                            (preview_idas.py's way): the walk; Moon-Rock Punch (the moon dust and the pilot's violet star
                            on every punch); Moon-Dust Quake (the dust wave along its line, the jolt and the drag on the
                            three in the cone); Healing Meeps (the meeps popping out of it, one flying to each ally, the
                            mending glow on them and on itself); The Big Bang (the leap to the group, the blast where it
                            lands, the three nearest knocked up).
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
from build_meepsie import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_meepsie")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_meepsie_fx", "tft_meepsie_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
ALLY = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_braum")]
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it punches
CONE = ((16, -8), (22, 9))       # Garen and Ashe beside Darius (game px): in the quake's cone
ALLIES = ((62, -6), (96, 6))     # Garen and Braum on its side, ahead of it (game px), facing right
WAVE_MID = P["q_len"] / 2000     # the dust wave's line middle ahead of it (game px)
GROUP = ((14, -8), (18, 9))      # Garen and Ashe round Darius: the Big Bang's landing among the three
LEAP = 40                        # game px the leap carries it toward them


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "meepsie", self.z))
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


def scene(out, steps, gap, W=330, H=170, z=3, tail=900, x0=70):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_meepsie_fx"], fx["tft_meepsie_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    foes = (d,)
    allies = ()
    if "e" in steps:   # its side only: Darius out of the picture
        d.x = W + 200
        allies = tuple(Foe(load(p), x0 + dx, gy + dy, mirror=False) for p, (dx, dy) in zip(ALLY, ALLIES))
        c.foes = allies
    elif any(s in steps for s in ("q", "r")):
        spots = GROUP if "r" in steps else CONE
        foes = (d,) + tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, spots))
        c.foes = foes[1:]
    c.wait(300)

    def punch():
        """One punch: the moon dust and the pilot's star on Darius on atk_st."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def quake():
        """Moon-Dust Quake: on q_st the fist hits the ground, the dust wave along its line; the three in the cone jolted
        and slowed (the drag at their feet, q_slow_t ticks)."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        at = t + tick(P["q_st"] - 1)
        c.looped("q_wave", at, at + 360, me.pos(at)[0] + WAVE_MID, gy, big)
        for f in foes:
            hit = at + int((f.pos(at)[0] - me.pos(at)[0]) * 4)
            f.flinches.append(hit)
            c.on_foe(f, "q_hit", hit)
            c.on_foe(f, "q_slow", hit + 300, until=hit + tick(P["q_slow_t"]))
        return at + tick(P["q_slow_t"])

    def meeps():
        """Healing Meeps: on e_st the meeps pop out of it; one flies to each ally (e_speed), the mending glow on him for
        e_t; its own glow at once (a slot to spare)."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_st"] - 1)
        c.on_me("e_cast", at, sheet=big)
        c.on_me("e_hot", at, until=at + tick(P["e_t"]))
        x, y = me.pos(at)
        end = at
        for f in allies:
            fx_ = f.pos(at)[0]
            land = at + tick((fx_ - x) * 1000.0 / P["e_speed"])
            c.fly("e_meep", at, land, x + 4, fx_, y - 20)
            c.on_foe(f, "e_hot", land, until=land + tick(P["e_t"]))
            end = max(end, land + tick(P["e_t"]))
        c.a("idle", max(0, end - c.t), loop=True)
        return end

    def bang():
        """The Big Bang: the leap (r_air ticks) toward the three, the blast where it lands, the nearest knocked up
        r_up ticks with the stars round them."""
        t = c.t
        xa = me.pos(t)[0]
        c.a("ult", tick(P["r_dur"]))
        land = t + tick(P["r_air"])
        me.moves.append((t + tick(4), land, xa, xa + LEAP))
        x, y = me.pos(land)
        c.at_spot("r_slam", land, x + 2, y + 3, sheet=c.big, under=True)
        for f in foes:
            f.hops.append((land, land + tick(P["r_up"]), 10))
            c.on_foe(f, "r_up", land)
        return land + tick(P["r_up"])

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            for _ in range(3):
                punch()
        elif step in ("q", "e", "r"):
            end = {"q": quake, "e": meeps, "r": bang}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：沉重地一步一步走（金铲铲原版的走法，两条腿轮流在前）", ["walk_in"], 200, 170),
          ("普攻 月岩重拳：一拳砸下；被动 木灵驾驶员：每一拳附带魔法伤害（紫色小星星）", ["attack"], REACH, 170),
          ("技能1 月尘震地：一拳砸地，月尘震波往前扇形推开，打中的敌人受伤并减速", ["q"], REACH, 180),
          ("技能2 治疗木灵：小木灵飞向生命比例最低的队友（名额有剩时也治疗自己），持续回血", ["e"], REACH, 180),
          ("大招 宇宙大爆炸：跳到敌人最多的地方砸地，离中心越远伤害越低，最近的三个敌人被击飞", ["r"], 60, 200)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_meepsie_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_meepsie_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_meepsie_skills.gif")))


if __name__ == "__main__":
    main()
