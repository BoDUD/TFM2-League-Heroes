#!/usr/bin/env python3
"""Preview images for Gromp (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_gromp.py [--out docs/preview] [--only frames|effects|skills]

  tft_gromp_frames.png    every animation's dense frames (hd_, PPU 1.69, as league.dll shows them)
  tft_gromp_effects.png   every effect animation, 3x
  tft_gromp_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_gromp.py,
                          60 ticks a second), captioned in Chinese, 4x (preview_murkwolf.py's way): the hop; Toxic Spit
                          (the glob flying, its splat, Purple Buff's rune over its back); Belchy Bubble (the bubble, its
                          pop on Darius, the burst and the poison bubbles on him); Slime Swamp (the glob lobbed, its
                          splash, the pool lying under him and the slime on his feet); Swamp Belch (the shockwave round
                          it, the blast and the choking fog on him, the fog lying on the spot). The growth (league.dll's
                          hd::FORMS) is not drawn here.
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
from preview_silco import Clip as SilcoClip, Lob, px_tick  # noqa: E402
from build_gromp import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_gromp")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_gromp_fx", "tft_gromp_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
REACH = P["atk_range"] // 1000                  # game px between its pivot and Darius's when it attacks
MOUTH = (30, -20)                               # its mouth from its pivot (game px)
SHOW = 2400                                     # how long the lying swamp and fog are shown (ms)


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "gromp", self.z))
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


def scene(out, steps, gap, W=380, H=180, z=4, tail=900, x0=80):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_gromp_fx"], fx["tft_gromp_big"]
    gy = H - 40
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    c.wait(300)

    def mouth(t):
        x, y = me.pos(t)
        return x + MOUTH[0], y + MOUTH[1]

    def fly(tag, rel, speed):
        """A straight shot from its mouth at Darius; returns its arrival."""
        x0_, y0_ = mouth(rel)
        x1 = d.pos(rel)[0]
        hit = rel + tick((x1 - x0_) * 1000.0 / speed)
        c.fly(tag, rel, hit, x0_, x1, y0_)
        return hit

    def spit():
        """One attack: the glob on a_rel, its splat on Darius."""
        hit = fly("a_spit", c.t + tick(P["a_rel"] - 1), P["a_speed"])
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def bubble():
        """Belchy Bubble: the bubble on q_rel, its pop on Darius (the first enemy it meets), the burst there and the
        poison bubbles on him for q_t."""
        t = c.t
        hit = fly("q_bubble", t + tick(P["q_rel"] - 1), P["q_speed"])
        c.a("skill", tick(P["q_dur"]))
        c.on_foe(d, "q_hit", hit)
        d.flinches.append(hit)
        x, y = d.pos(hit)
        c.at_spot("q_burst", hit, x, y, sheet=c.big, under=False)
        c.on_foe(d, "q_poison", hit, until=hit + tick(P["q_t"]))
        return hit + tick(P["q_t"])

    def swamp():
        """Slime Swamp: the glob lobbed on e_rel, its splash where Darius stood, the pool lying there (replayed every
        e_show ticks, shown SHOW ms) and the slime on his feet."""
        t = c.t
        rel = t + tick(P["e_rel"] - 1)
        land = rel + tick(P["e_travel"])
        x0_, y0_ = mouth(rel)
        x1, y1 = d.pos(rel)
        c.over.append(Lob(frames_of(c.small, "e_glob"), rel, int(x0_), int(y0_), loop=True, until=land, x1=int(x1),
                          y1=int(y1)))
        c.a("skill2", tick(P["e_dur"]))
        c.at_spot("e_land", land, x1, y1, sheet=c.big)
        for k in range(0, SHOW, round(tick(P["e_show"]))):
            c.at_spot("e_pool", land + k, x1, y1, sheet=c.big)
        c.on_foe(d, "e_slow", land, until=land + SHOW)
        return land + SHOW

    def belch():
        """Swamp Belch: the shockwave round it on r_rel, the blast and the choking fog on Darius, the fog lying on his
        spot (replayed every r_show ticks, shown SHOW ms)."""
        t = c.t
        rel = t + tick(P["r_rel"] - 1)
        c.a("ult", tick(P["r_dur"]))
        c.on_me("r_cast", rel, sheet=c.big)
        c.on_foe(d, "r_hit", rel)
        d.flinches.append(rel)
        c.on_foe(d, "r_slow", rel, until=rel + tick(P["r_hold"]))
        x, y = d.pos(rel)
        land = rel + tick(P["r_travel"])
        for k in range(0, SHOW, round(tick(P["r_show"]))):
            c.at_spot("r_fog", land + k, x, y, sheet=c.big, under=False)
        return land + SHOW

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            t0 = c.t
            spit()
            spit()
            c.on_me("p_ap", t0, until=c.t)            # tft.dll's Purple Buff stacks while it fights
        elif step == "q":
            end = bubble()
            c.wait(max(0, end + 200 - c.t))
        elif step == "e":
            end = swamp()
            c.wait(max(0, end + 200 - c.t))
        elif step == "r":
            end = belch()
            c.wait(max(0, end + 200 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：一下一下地蛙跳", ["walk_in"], 220, 170),
          ("普攻 毒涎吐射：吐毒口水；紫霸符：战斗里背上方的紫色符文（每 4 秒叠法强）", ["attack"], REACH, 180),
          ("技能1 打嗝泡泡：鼓肚子吐出毒泡泡，碰到第一个敌人破开，炸出毒圈，周围敌人冒毒泡（中毒）", ["q"], REACH, 180),
          ("技能2 黏液沼泽：往敌人脚下吐一团黏液，摊成一滩沼泽，站在里面的敌人被黏住减速", ["e"], REACH, 180),
          ("大招 毒沼大嗝：仰头鼓到最大（游戏里身体变大 30%），大嗝冲击波，前方毒雾伤害减速并留在地上", ["r"], REACH, 190)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_gromp_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[10:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_gromp_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_gromp_skills.gif")))


if __name__ == "__main__":
    main()
