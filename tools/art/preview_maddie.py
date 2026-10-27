#!/usr/bin/env python3
"""Preview images for Maddie (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_maddie.py [--out docs/preview] [--only frames|effects|skills]

  tft_maddie_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  tft_maddie_effects.png   every effect animation, 3x
  tft_maddie_skills.gif    each skill alone with its effects against Darius (Garen in front of him where the bullets
                           would meet the first enemy), timed like the kit (tools/kit/build_maddie.py, 60 ticks a second)
                           and as tft.dll plays its parts (addons/tft/src/maddie.rs), captioned in Chinese, 4x: the run;
                           the rifle shots; Fan the Hammer's six bullets at the farthest enemy (Darius behind Garen: the
                           bullets stop on Garen, the first in their way); Wanted on Darius (the badge, the mark); the
                           bounty when he falls Wanted; the snipe (the scope closing on him while she aims, the round
                           punching through Garen and Darius).
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me  # noqa: E402
import preview_zoe as Z  # noqa: E402
from preview_silco import Clip as SilcoClip, px_tick  # noqa: E402
from build_maddie import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_maddie")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_maddie_fx", "tft_maddie_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
REACH = 68                       # game px between her pivot and Darius's when she attacks (atk_range 68000)
PIVOT = 11                       # game px from a unit's soles up to its pivot (the line bullets fly to)


class Clip(SilcoClip):
    """preview_silco's clip with her own dense frames and her bullets at the rifle's height."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "maddie", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def bullet(self, tag, hit_tag, rel, speed, foe, lift, sheet=None):
        """A bullet from her muzzle (`lift` units over her pivot, as the kit lifts it) to `foe`'s pivot at `speed` (game
        units a tick), its hit on him."""
        x0, x1 = self.me.pos(rel)[0] + 16, foe.pos(rel)[0]
        hit = rel + tick((x1 - x0) * 1000.0 / speed)
        y0, y1 = self.me.y - PIVOT - lift // 1000, foe.pos(rel)[1] - PIVOT
        self.over.append(Anim(frames_of(sheet or self.small, tag), rel, x0, y0, loop=True, until=hit, x1=x1, y1=y1))
        self.on_foe(foe, hit_tag, hit, sheet=sheet)
        foe.flinches.append(hit)
        return hit


def scene(out, steps, gap, W=280, H=150, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_maddie_fx"], fx["tft_maddie_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "q" in steps or "r" in steps:              # Garen in front of Darius: the first enemy in the bullets' way
        c.foes = (Foe(load(GAREN), far - 30, gy),)
    c.wait(300)

    def shot():
        rel = c.t + tick(P["a_rel"] - 1)
        c.bullet("a_bullet", "a_hit", rel, P["a_speed"], d, P["a_lift"])
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def fan():
        """Fan the Hammer: q_n bullets q_gap ticks apart from q_rel at the farthest enemy (Darius); each stops on the
        first enemy in its line (Garen, in front of him)."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        first = c.foes[0] if c.foes else d
        end = t
        for k in range(P["q_n"]):
            rel = t + tick(P["q_rel"] - 1 + k * P["q_gap"])
            end = c.bullet("q_bullet", "q_hit", rel, P["q_speed"], first, P["q_lift"])
        return end

    def wanted():
        """Wanted on Darius (the most health here): the badge slams down, the mark stays e_t ticks."""
        rel = c.t + tick(P["e_rel"] - 1)
        c.a("skill2", tick(P["e_dur"]))
        c.on_foe(d, "e_mark", rel)
        c.on_foe(d, "e_wanted", rel + 530, until=rel + 3000)
        return rel + 3000

    def bounty():
        """A Wanted enemy falls: the bounty bursts on her, the glow at her feet stays."""
        c.on_me("p_bounty", c.t)
        c.on_me("p_bounty_loop", c.t + 580, until=c.t + 3000)
        c.wait(3000)

    def snipe():
        """Enforcer's Snipe: the scope closes on Darius while she aims, the blast on r_rel, the round through Garen and
        Darius."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        c.on_foe(d, "r_sight", t, sheet=big)
        rel = t + tick(P["r_rel"] - 1)
        end = rel
        for foe in sorted((d,) + tuple(c.foes), key=lambda f: f.pos(rel)[0]):
            end = c.bullet("r_round", "r_hit", rel, P["r_speed"], foe, P["q_lift"], sheet=big)
        return end + 500

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            shot()
            shot()
        elif step == "q":
            end = fan()
            c.wait(end + 400 - c.t)
        elif step == "e":
            end = wanted()
            c.wait(end - c.t)
        elif step == "p":
            bounty()
        elif step == "r":
            end = snipe()
            c.wait(end + 300 - c.t)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：端着步枪低姿小跑", ["walk_in"], 160, 170),
          ("普攻：步枪射击，后坐力把枪口顶起来", ["attack"], REACH, 170),
          ("技能1 连拨击锤：半蹲朝最远的敌人连开6枪，每枪打中路上第一个敌人（这里是挡在前面的盖伦）", ["q"], 110, 170),
          ("技能2 通缉令：给附近血最多的敌方英雄砸下执法官徽章，通缉中受到的伤害提高", ["e"], REACH, 170),
          ("被动 狙神：越远伤害越高；被通缉的敌人阵亡时领一份赏金（攻速提高，脚下留金光）", ["p"], REACH, 170),
          ("大招 执法狙杀：准星锁定血量比例最低的敌人，一发穿透子弹打穿路上所有敌人", ["r"], 150, 170)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_maddie_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_maddie_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_maddie_skills.gif")))


if __name__ == "__main__":
    main()
