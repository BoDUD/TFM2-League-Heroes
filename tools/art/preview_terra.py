#!/usr/bin/env python3
"""Preview images for Terra (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_terra.py [--out docs/preview] [--only frames|effects|skills]

  tft_terra_frames.png    every animation's dense frames (hd_, PPU 1.45, as league.dll shows them)
  tft_terra_effects.png   every effect animation, 3x
  tft_terra_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                          (tools/kit/build_terra.py, 60 ticks a second) and as tft.dll plays its parts
                          (addons/tft/src/terra.rs), captioned in Chinese, 4x (preview_sohm.py's way): the low flight;
                          Rock Claw; Rending Bite (the crouch, the pounce onto Darius, the stone jaws, the cracked ground
                          under him); Dragon's Roar (the sound waves, the taunt marks, her rock slabs); Earthquake (three
                          stomps, a quake ring each and the rock spikes under everyone in it, her stone armour after).
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
from build_terra import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_terra")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_terra_fx", "tft_terra_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = P["atk_range"] // 1000   # game px between her pivot and Darius's when she attacks
SPOTS = ((20, -4), (-2, 8))      # Garen behind Darius, Ashe beside him (game px)


class Clip(SilcoClip):
    """preview_silco's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "terra", self.z))
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


def scene(out, steps, gap, W=320, H=170, z=4, tail=900, x0=70):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_terra_fx"], fx["tft_terra_big"]
    gy = H - 34
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if any(s in steps for s in ("e", "r")):                   # two more enemies round Darius
        c.foes = tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
    foes = (d,) + tuple(c.foes)
    c.wait(300)

    def claw():
        """One attack: Rock Claw's strike on atk_st."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def bite():
        """Rending Bite: the crouch, the pounce on q_st (MoveToTarget q_speed onto Darius), the stone jaws as she lands,
        the cracked ground under him for q_slow_t."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        go = t + tick(P["q_st"] - 1)
        xa, xb = me.pos(go)[0], d.pos(go)[0] - REACH
        land = go + tick(max(1, (xb - xa)) * 1000.0 / P["q_speed"])
        me.moves.append((go, land, xa, xb))
        c.on_foe(d, "q_hit", land)
        c.on_foe(d, "q_slow", land, until=land + tick(P["q_slow_t"]))
        d.flinches.append(land)
        return land + tick(P["q_slow_t"])

    def roar():
        """Dragon's Roar on e_st: the waves round her, a taunt mark over every enemy in e_r, her rock slabs for e_sh_t."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_st"] - 1)
        c.on_me("e", at, sheet=c.big)
        c.on_me("e_shield", at, sheet=c.big, until=at + tick(P["e_sh_t"]))
        for f in foes:
            if abs(f.pos(at)[0] - me.pos(at)[0]) <= P["e_r"] / 1000:
                c.on_foe(f, "e_taunt", at, until=at + tick(P["e_taunt"]))
        return at + tick(P["e_sh_t"])

    def quake():
        """Earthquake: the ground waking under her, three stomps (r_t1-3): a quake ring where she stands, the rock
        spikes under every enemy within r_r; her stone armour after the third (shown 2 s here, r_res_t in the game)."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        c.on_me("r", t + 60)
        for k in (1, 2, 3):
            at = t + tick(P[f"r_t{k}"] - 1)
            x, y = me.pos(at)
            c.at_spot("r_quake", at, x, y, sheet=c.big, under=True)
            for f in foes:
                fx_, fy = f.pos(at)
                if (fx_ - x) ** 2 + (fy - y) ** 2 <= (P["r_r"] / 1000) ** 2:
                    c.on_foe(f, "r_hit", at + 40)
                    f.flinches.append(at + 40)
        end = t + tick(P["r_t3"])
        c.on_me("r_res", end, sheet=c.big, until=end + 2000)
        return t + tick(P["r_dur"])

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            claw()
            claw()
        elif step == "q":
            end = bite()
            c.wait(max(0, end + 200 - c.t))
        elif step == "e":
            end = roar()
            c.wait(max(0, end + 200 - c.t))
        elif step == "r":
            end = quake()
            c.wait(max(0, end + 1600 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：张开翅膀贴地低飞", ["walk_in"], 180, 170),
          ("普攻 岩爪（被动 巨岩之躯：受到的伤害永久减少18%）", ["attack"], REACH, 170),
          ("技能1 裂地咬：蹲伏、腾空扑上去落地猛咬，伤害吃护甲魔抗，被咬的人脚下地面裂开减速", ["q"], REACH + 34, 170),
          ("技能2 龙威咆哮：仰头咆哮，嘲讽周围敌人（头顶龙爪印），自己浮起岩石护盾", ["e"], REACH, 200),
          ("大招 地震：抬身重踏三次，每踏一圈地震、地下石刺戳出；结束后岩甲发光（护甲魔抗大涨）", ["r"], REACH, 200)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_terra_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[9:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_terra_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_terra_skills.gif")))


if __name__ == "__main__":
    main()
