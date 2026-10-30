#!/usr/bin/env python3
"""Preview images for the Blue Sentinel (the tft pack), built from the exported game sprites (so they also prove the
sheets load).

    python tools/art/preview_sentinel.py [--out docs/preview] [--only frames|effects|skills]

  tft_sentinel_frames.png    every animation's dense frames (hd_, PPU 1.7, as league.dll shows them)
  tft_sentinel_effects.png   every effect animation, 3x
  tft_sentinel_skills.gif    each skill alone with its effects against Darius, Garen and Ashe (Lux at its back for the
                             Blue Buff), timed like the kit (tools/kit/build_sentinel.py, 60 ticks a second) and as
                             tft.dll plays its parts (addons/tft/src/sentinel.rs), captioned in Chinese, 4x
                             (preview_terra.py's way): the heavy walk; Rock Fist; Twin Slam (the cracked ring round it,
                             the stone shackles on the slowed, the Blue Buff on Lux); Carved Skin (the rune flare, the
                             stone shell, the taunt marks); Azure Shockwave (the shell, both fists smashing the ground,
                             the fissure running toward the enemies, the spikes and knock-up under everyone it reaches,
                             the cracked rune over the reaved champions and the seal when their next skill comes ready).
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
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me  # noqa: E402
import preview_zoe as Z  # noqa: E402
from preview_silco import Clip as SilcoClip, px_tick  # noqa: E402
from build_sentinel import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_sentinel")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_sentinel_fx", "tft_sentinel_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
ALLY = os.path.join(ROOT, "league", "champions", "league_lux")
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it attacks: the range
                                                # plus both units' collision radii (its fists reach that far)
SPOTS = ((24, -4), (46, 6))      # Garen behind Darius, Ashe further on (game px): the fissure's line
ALLY_AT = -30                    # Lux at its back (game px)


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "sentinel", self.z))
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


def scene(out, steps, gap, W=360, H=170, z=4, tail=900, x0=80):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_sentinel_fx"], fx["tft_sentinel_big"]
    gy = H - 34
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    foes = (d,)
    ally = None
    if any(s in steps for s in ("q", "e", "r")):                   # two more enemies on, Lux at its back
        foes = (d,) + tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
        ally = Foe(load(ALLY), x0 + ALLY_AT, gy - 6, mirror=False)
        c.foes = foes[1:] + (ally,)
    c.wait(300)

    def blue(at):
        """Blue Buff: the glow on the ally within p_r."""
        if ally is not None and abs(ally.pos(at)[0] - me.pos(at)[0]) <= P["p_r"] / 1000:
            c.on_foe(ally, "p_blue", at, until=at + tick(P["p_glow"]))

    def fist():
        """One attack: Rock Fist's blow on atk_st."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def slam():
        """Twin Slam: the ring round it on q_st, magic and the shackles on every enemy within q_r."""
        t = c.t
        blue(t)
        c.a("skill", tick(P["q_dur"]))
        at = t + tick(P["q_st"] - 1)
        x, y = me.pos(at)
        c.at_spot("q_hit", at, x, y, sheet=c.big, under=True)
        for f in foes:
            if abs(f.pos(at)[0] - x) <= P["q_r"] / 1000:
                c.on_foe(f, "q_slow", at, until=at + tick(P["q_slow_t"]))
                f.flinches.append(at)
        return at + tick(P["q_slow_t"])

    def skin():
        """Carved Skin: the rune flare, the shell for e_sh_t (2 s shown), the taunt mark over every enemy in e_r."""
        t = c.t
        blue(t)
        c.a("skill2", tick(P["e_dur"]))
        c.on_me("e_cast", t, sheet=c.big)
        at = t + tick(P["e_st"] - 1)
        c.on_me("e_shield", at, sheet=c.big, until=at + 2000)
        for f in foes:
            if abs(f.pos(at)[0] - me.pos(at)[0]) <= P["e_r"] / 1000:
                c.on_foe(f, "e_taunt", at, until=at + tick(P["e_taunt"]))
        return at + 2000

    def shockwave():
        """Azure Shockwave: the shell at once; the smash on r_st, the fissure running r_len toward the enemies at
        r_speed, the spikes and the knock-up under each as it reaches them, the cracked rune over the champions, the
        seal when their next skill comes ready (shown 1 s later)."""
        t = c.t
        blue(t)
        c.a("ult", tick(P["r_dur"]))
        c.on_me("e_shield", t, sheet=c.big, until=t + 2400)
        at = t + tick(P["r_st"] - 1)
        x, y = me.pos(at)
        c.at_spot("r_slam", at, x + 14, y, sheet=c.big, under=True)
        run = tick(P["r_len"] / P["r_speed"])
        c.fly("r_crack", at, at + run, x, x + P["r_len"] / 1000, y, sheet=c.big)
        for f in foes:
            fx_ = f.pos(at)[0]
            if 0 <= fx_ - x <= P["r_len"] / 1000:
                reach = at + run * (fx_ - x) / (P["r_len"] / 1000)
                c.on_foe(f, "r_hit", reach)
                f.hops.append((reach, reach + tick(P["r_up"]), 14))
                c.on_foe(f, "r_reave", reach + tick(P["r_up"]), until=reach + tick(P["r_up"]) + 1000)
                c.on_foe(f, "r_seal", reach + tick(P["r_up"]) + 1000, until=reach + tick(P["r_up"]) + 1000 +
                         tick(P["r_reave"]))
        return at + run + tick(P["r_up"]) + 1000 + tick(P["r_reave"])

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            fist()
            fist()
        elif step == "q":
            end = slam()
            c.wait(max(0, end + 200 - c.t))
        elif step == "e":
            end = skin()
            c.wait(max(0, end + 200 - c.t))
        elif step == "r":
            end = shockwave()
            c.wait(max(0, end + 400 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：沉重地迈步，两只巨拳前后摆", ["walk_in"], 200, 170),
          ("普攻 岩拳猛击：单拳举过头顶砸下", ["attack"], REACH, 180),
          ("技能1 双拳重砸：双拳砸地，周围敌人受魔法伤害并被石块拖住减速；被动 蓝霸符：身后友军技能冷却缩短（脚下青光）", ["q"], REACH, 190),
          ("技能2 雕纹石肤：符文亮起，套上刻纹石板护盾，嘲讽周围敌人（头顶独眼符文）", ["e"], REACH, 200),
          ("大招 蔚蓝冲击波：护盾，双拳过顶猛砸，朝敌人最多的方向裂开裂隙：石刺击飞、魔法伤害、破法（下一个技能被封）", ["r"], REACH, 210)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_sentinel_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_sentinel_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_sentinel_skills.gif")))


if __name__ == "__main__":
    main()
