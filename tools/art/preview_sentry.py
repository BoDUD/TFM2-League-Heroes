#!/usr/bin/env python3
"""Preview images for the Sentry (the tft pack), built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_sentry.py [--out docs/preview] [--only frames|effects|skills]

  tft_sentry_frames.png    every animation's dense frames (hd_, PPU 1.29, as league.dll shows them)
  tft_sentry_effects.png   every effect animation, 3x
  tft_sentry_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_sentry.py,
                           60 ticks a second), captioned in Chinese, 4x (preview_gromp.py's way): the glide; Shard Bolt
                           (the bolt from its core, its burst); Azure Laser (q_t of waves: the laser held on the core
                           every q_p, the burn and the cracked shield on Darius, the channel's loop frames); Rift Leap
                           (the split flash, the shard ring left where it was, the blink back, the slowed); Prism Sweep
                           (the charge round its core, the swept beam, the blast and the shattered shield on Darius).
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
from build_sentry import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_sentry")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_sentry_fx", "tft_sentry_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
REACH = P["atk_range"] // 1000                  # game px between its pivot and Darius's when it attacks
CORE = (0, (5000 - P["q_by"]) // 1000)          # its core over its pivot (game px): where the bolts and beams leave


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "sentry", self.z))
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
    small, big = fx["tft_sentry_fx"], fx["tft_sentry_big"]
    gy = H - 40
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    c.wait(300)

    def core(t):
        x, y = me.pos(t)
        return x + CORE[0], y - CORE[1]

    def creep(tag, when, x, y, n):
        """A beam picture riding its projectile as in the game: it creeps 1 px a tick toward Darius (the importer drew
        each tick's frame back by as much, so the flare holds on the core)."""
        c.over.append(Anim(frames_of(c.big, tag), when, int(x), int(y), until=when + tick(n + 1), x1=int(x) + n + 1,
                           y1=int(y)))

    def bolt():
        """One attack: the bolt from its core on a_rel, its burst on Darius."""
        rel = c.t + tick(P["a_rel"] - 1)
        x0_, y0_ = core(rel)
        x1 = d.pos(rel)[0]
        hit = rel + tick((x1 - x0_) * 1000.0 / P["a_speed"])
        c.fly("a_bolt", rel, hit, x0_, x1, y0_)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def laser():
        """Azure Laser: from q_rel, every q_p a wave - the laser held on the core (its picture creeps 1 px a tick and is
        drawn back by as much), the zap's burn and the cracked shield on Darius; skill, then skill_loop for the rest."""
        t = c.t
        t0 = t + tick(P["q_rel"] - 1)
        waves = P["q_t"] // P["q_p"]
        for k in range(waves):
            w = t0 + tick(k * P["q_p"])
            x, y = core(w)
            creep("q_beam", w, x, y, P["q_p"])
            c.on_foe(d, "q_hit", w + tick(2))
            d.flinches.append(w + tick(2))
        c.on_foe(d, "q_shred", t0, until=t0 + tick(P["q_t"] + P["q_hold"]))
        c.a("skill", tick(P["q_anim"]))
        c.a("skill_loop", t0 + tick(P["q_t"]) - c.t, loop=True)
        return c.t

    def leap():
        """Rift Leap: the split flash on it and the shard ring where it stands, the slowed Darius, the blink back on
        e_rel (MoveBack e_back x e_back_t)."""
        t = c.t
        x, y = me.pos(t)
        c.on_me("e_split", t)
        c.at_spot("e_ring", t, x, y + 11, sheet=c.big)
        c.on_foe(d, "e_slow", t, until=t + tick(P["e_hold"]))
        b0 = t + tick(P["e_rel"] - 1)
        b1 = b0 + tick(P["e_back_t"])
        me.moves.append((b0, b1, x, x - P["e_back"] * P["e_back_t"] / 1000))
        c.a("skill2", tick(P["e_dur"]))
        return t + tick(P["e_hold"])

    def sweep():
        """Prism Sweep: the charge round its core, the swept beam on r_rel (held on the core), the blast and the
        shattered shield on Darius."""
        t = c.t
        rel = t + tick(P["r_rel"] - 1)
        c.on_me("r_open", t, sheet=c.big)
        x, y = core(rel)
        creep("r_sweep", rel, x, y, 20)
        c.on_foe(d, "r_hit", rel + tick(6))
        d.flinches.append(rel + tick(6))
        c.on_foe(d, "r_shred", rel + tick(6), until=rel + tick(6 + P["r_hold"]))
        c.a("ult", tick(P["r_dur"]))
        return rel + tick(6 + P["r_hold"])

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
            end = laser()
            c.wait(max(0, end + 300 - c.t))
        elif step == "e":
            end = leap()
            c.wait(max(0, end + 200 - c.t))
        elif step == "r":
            end = sweep()
            c.wait(max(0, end + 200 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：两块石头前倾着飘过去", ["walk_in"], 220, 170),
          ("普攻 碎光弹：往上一抬、往前一倾，蓝核射出光弹", ["attack"], REACH, 180),
          ("技能1 蔚蓝激光：引导 2.5 秒激光，每 0.25 秒一下伤害，敌人头上裂开的护盾 = 魔抗被削（青霸符：引导时大招冷却缩短）",
           ["q"], REACH, 180),
          ("技能2 裂石跃迁：两块石头裂开，原地留一圈碎水晶减速敌人，自己往后闪开", ["e"], 40, 180),
          ("大招 棱镜扫射：两块石头张成 V 字，蓝核蓄力，光柱从上往下扫过前方，魔抗大降", ["r"], REACH, 200)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        scene(path, steps, gap, H=h, z=z, x0=80 if "e" not in steps else 140)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_sentry_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_sentry_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_sentry_skills.gif")))


if __name__ == "__main__":
    main()
