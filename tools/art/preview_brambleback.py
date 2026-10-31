#!/usr/bin/env python3
"""Preview images for the Crimson Brambleback (the tft pack), built from the exported game sprites (so they also prove
the sheets load).

    python tools/art/preview_brambleback.py [--out docs/preview] [--only frames|effects|skills]

  tft_brambleback_frames.png    every animation's dense frames (hd_, PPU 1.7, as league.dll shows them)
  tft_brambleback_effects.png   every effect animation, 3x
  tft_brambleback_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                                (tools/kit/build_brambleback.py, 60 ticks a second) and as tft.dll plays its parts
                                (addons/tft/src/brambleback.rs), captioned in Chinese, 4x (preview_sentinel.py's way):
                                the gallop; Bramble Claw with Red Buff's burn; Bramble Pounce (the leap, the ring under
                                the target, the snare) and tft.dll's leap on to the next (shown on Garen); Crimson Roar
                                (the waves, the fear marks, the bark guard); Crimson Fury (the burst, then the blaze
                                through two rakes).
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
from build_brambleback import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_brambleback")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_brambleback_fx", "tft_brambleback_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it attacks: the range
                                                # plus both units' collision radii (its claws reach that far)
SPOTS = ((24, -4), (46, 6))      # Garen behind Darius, Ashe further on (game px)


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "brambleback", self.z))
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


def scene(out, steps, gap, W=380, H=170, z=4, tail=900, x0=80):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_brambleback_fx"], fx["tft_brambleback_big"]
    gy = H - 34
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    foes = (d,)
    if any(s in steps for s in ("q", "e", "r")):                   # two more enemies on
        foes = (d,) + tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
        c.foes = foes[1:]
    c.wait(300)

    def rake():
        """One attack: Bramble Claw's rake on atk_st, Red Buff's burn on the target (tft.dll) for p_burn_t."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        c.on_foe(d, "p_burn", hit, until=hit + tick(P["p_burn_t"]))
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def leap(target, speed):
        """The spring at `target` (the skill tag while it flies), landing touching it: the ring and the snare."""
        t = c.t
        xa, xb = me.pos(t)[0], target.pos(t)[0] - 22
        fly = max(tick(P["q_dur"]), abs(xb - xa) / px_tick(speed))
        c.a("skill", fly)
        me.moves.append((t, t + fly, xa, xb))
        at = t + fly
        c.on_foe(target, "q_hit", at)
        c.on_foe(target, "q_slow", at, until=at + tick(P["q_slow_t"]))
        target.flinches.append(at)
        return at

    def roar():
        """Crimson Roar: the waves at e_st, the bark guard for e_t (2 s shown), the fear mark over every enemy in e_r."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        at = t + tick(P["e_st"] - 1)
        c.on_me("e_cast", at, sheet=c.big)
        c.on_me("e_guard", at, sheet=c.big, until=at + 2000)
        for f in foes:
            if abs(f.pos(at)[0] - me.pos(at)[0]) <= P["e_r"] / 1000 + 15:
                c.on_foe(f, "e_slow", at, until=at + tick(P["e_t"]))
        return at + 2000

    def fury():
        """Crimson Fury: the burst at r_st, then the blaze through two rakes."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        at = t + tick(P["r_st"] - 1)
        c.on_me("r_cast", at, sheet=c.big)
        c.on_me("r_fury", at, sheet=c.big, until=at + 2600)
        rake()
        rake()
        return at + 2600

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            rake()
            rake()
        elif step == "q":
            at = leap(d, P["q_speed"])
            c.wait(max(0, at + 500 - c.t))
            c.a("idle", 300)
            at = leap(foes[1], P["k_speed"])      # tft.dll's leap on to the next, shown on Garen
            c.wait(max(0, at + 600 - c.t))
        elif step == "e":
            end = roar()
            c.wait(max(0, end + 200 - c.t))
        elif step == "r":
            end = fury()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：像大猩猩一样前爪撑地奔跑", ["walk_in"], 200, 170),
          ("普攻 荆爪横扫：大爪横扫；被动 红霸符：目标灼烧（按最大生命的真实伤害），自己回血", ["attack"], REACH, 180),
          ("技能1 荆棘飞扑：跃起扑到目标身上，物理伤害并被荆棘缠住减速；击杀后自动扑向下一个敌人（第二下示意）", ["q"], 70, 190),
          ("技能2 绯红咆哮：人立怒吼，周围敌人减速、攻击力降低（头顶爪痕），自己树皮护体减伤", ["e"], REACH, 200),
          ("大招 猩红之怒：全身红纹烧起来狂暴，攻击力、攻速大涨，无视一部分护甲", ["r"], REACH, 210)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_brambleback_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_brambleback_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_brambleback_skills.gif")))


if __name__ == "__main__":
    main()
