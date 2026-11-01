#!/usr/bin/env python3
"""Preview images for the Scuttle Crab (the tft pack), built from the exported game sprites (so they also prove the
sheets load).

    python tools/art/preview_scuttlecrab.py [--out docs/preview] [--only frames|effects|skills]

  tft_scuttlecrab_frames.png    every animation's dense frames (hd_, PPU 2.667, as league.dll shows them)
  tft_scuttlecrab_effects.png   every effect animation, 3x
  tft_scuttlecrab_skills.gif    each skill alone with its effects against Darius and Garen (the Green Buff with Garen and
                                Braum on its side), timed like the kit (tools/kit/build_scuttlecrab.py, 60 ticks a
                                second) and as tft.dll plays its parts (addons/tft/src/scuttlecrab.rs), captioned in
                                Chinese, 3x (preview_meepsie.py's way): the scuttle; Crab Dance (the splash on both
                                beside it); Green Buff (the heal on an ally gone low); Speed Shrine (the ring at its
                                feet, the splash's slow on the two, its own haste); Shell Shield (the dome, the burst
                                when it runs out, the stun and the wet ground on the two); Can You Dig It? (dug in under
                                the mound, the burst out, the two knocked up).
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
from build_scuttlecrab import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_scuttlecrab")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_scuttlecrab_fx", "tft_scuttlecrab_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
ALLY = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_braum")]
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it dances
BESIDE = (8, 10)                 # Garen beside Darius (game px): in the dance's and the splash's reach
ALLIES = ((40, -6), (64, 6))     # Garen and Braum on its side, ahead of it (game px), facing right


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "scuttlecrab", self.z))
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


def scene(out, steps, gap, W=330, H=170, z=3, tail=900, x0=70):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_scuttlecrab_fx"], fx["tft_scuttlecrab_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    foes = (d,)
    allies = ()
    if "p" in steps:   # its side only: Darius out of the picture
        d.x = W + 200
        allies = tuple(Foe(load(p), x0 + dx, gy + dy, mirror=False) for p, (dx, dy) in zip(ALLY, ALLIES))
        c.foes = allies
    elif steps != ["walk_in"]:
        foes = (d, Foe(load(GAREN), far + BESIDE[0], gy + BESIDE[1]))
        c.foes = foes[1:]
    c.wait(300)

    def dance():
        """One dance: the splash on both beside it on atk_st."""
        hit = c.t + tick(P["atk_st"] - 1)
        for f in foes:
            c.on_foe(f, "a_hit", hit)
            f.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def green():
        """Green Buff: an ally falls under p_low% (tft.dll): the heal rises round him."""
        c.a("idle", 400, loop=True)
        c.on_foe(allies[0], "p_heal", c.t - 200)
        c.a("idle", 1400, loop=True)
        return c.t

    def shrine():
        """Speed Shrine: on q_st the ring at its feet for q_t, the splash slows the two (q_slow_t, the wet ground), it
        stands in its own shrine hasted."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        at = t + tick(P["q_st"] - 1)
        x, y = me.pos(at)
        c.at_spot("q_shrine", at, x, y + 11, sheet=c.big, under=True)
        for f in foes:
            f.flinches.append(at)
            c.on_foe(f, "e_slow", at, until=at + tick(P["q_slow_t"]))
        c.on_me("q_haste", at, until=at + tick(P["q_t"]))
        end = at + tick(P["q_t"])
        c.a("idle", max(0, end - c.t), loop=True)
        return end

    def shell():
        """Shell Shield: on e_st the dome while the shield holds (it runs out here, e_t), then the burst: the two stunned
        e_stun and on wet ground e_slow_t."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_st"] - 1)
        out_ = at + tick(P["e_t"])
        c.on_me("e_shell", at, until=out_)
        c.a("idle", max(0, out_ - c.t), loop=True)
        c.on_me("e_burst", out_, sheet=c.big)
        for f in foes:
            f.flinches.append(out_)
            c.on_foe(f, "e_slow", out_, until=out_ + tick(P["e_slow_t"]))
        c.a("idle", 900, loop=True)
        return c.t

    def dig():
        """Can You Dig It?: the mound for r_t while it hides under the earth, then the burst out, the two knocked up r_up
        with the clods under them."""
        t = c.t
        c.a("ult", tick(P["r_t"] + P["r_out"]))
        x, y = me.pos(t)
        c.at_spot("r_dig", t, x + 1, y + 2, sheet=c.big, under=True)
        out_ = t + tick(P["r_t"] - 1)
        c.on_me("r_burst", out_, sheet=c.big)
        for f in foes:
            f.hops.append((out_, out_ + tick(P["r_up"]), 10))
            c.on_foe(f, "r_up", out_)
        return out_ + tick(P["r_up"])

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            for _ in range(3):
                dance()
        elif step in ("p", "q", "e", "r"):
            end = {"p": green, "q": shrine, "e": shell, "r": dig}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：小短腿飞快地横着倒腾", ["walk_in"], 200, 170),
          ("普攻 螃蟹舞：跳一段舞，踩中身边所有敌人（河水溅开）", ["attack"], REACH, 170),
          ("被动 绿霸符：附近的队友掉到40%血以下时回复12%最大生命（每人10秒一次）", ["p"], REACH, 180),
          ("技能1 疾行神龛：脚下放一个河水神龛，水花伤害并减速周围敌人，神龛里的队友加移速攻速", ["q"], REACH, 180),
          ("技能2 蟹壳护盾：缩进壳里得到护盾；护盾打光或到时间时蟹壳碎裂，周围敌人受伤、眩晕并减速", ["e"], REACH, 180),
          ("大招 你挖得动吗？：钻进地下减伤、免控、回血，然后钻出来击飞身边的敌人", ["r"], REACH, 190)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_scuttlecrab_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_scuttlecrab_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_scuttlecrab_skills.gif")))


if __name__ == "__main__":
    main()
