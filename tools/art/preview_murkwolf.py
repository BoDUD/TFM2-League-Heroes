#!/usr/bin/env python3
"""Preview images for Murk Wolf (the tft pack), built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_murkwolf.py [--out docs/preview] [--only frames|effects|skills]

  tft_murkwolf_frames.png    every animation's dense frames (hd_, PPU 1.67, as league.dll shows them)
  tft_murkwolf_effects.png   every effect animation, 3x
  tft_murkwolf_skills.gif    each skill alone with its effects against Darius, timed like the kit
                             (tools/kit/build_murkwolf.py, 60 ticks a second) and as tft.dll plays its parts
                             (addons/tft/src/murkwolf.rs), captioned in Chinese, 4x (preview_raptor.py's way): the trot;
                             Twin Bite (the snap on the bitten); Rending Claws (the leap, the landing murk, the claw X
                             with Grey Buff's crit star, then three quicker bites with the claws' glint round it);
                             Slayer's Howl (the smoke round it, two bites); Pack Attack (the two pups beside it, their
                             pounce, then each attack followed by their bites).
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
from build_murkwolf import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_murkwolf")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_murkwolf_fx", "tft_murkwolf_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it attacks
LEAP_FROM = 70                                  # game px further back it leaps from
LAND = P["q_gap"] // 1000                       # tft.dll lands it this far short of the target


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "murkwolf", self.z))
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


def scene(out, steps, gap, W=360, H=170, z=4, tail=900, x0=90):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_murkwolf_fx"], fx["tft_murkwolf_big"]
    gy = H - 40
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    c.wait(300)
    pack = {"until": -1}

    def bite(cd=None, emp=False):
        """One attack: the snap on atk_st; Rending Claws' bonus bite on it; the pups' bites after it while the pack is
        out."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        if rel_pack := hit < pack["until"]:
            for k in range(1, P["r_n"] + 1):
                c.on_foe(d, "r_bite", hit + tick(k * P["r_gap"]))
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick((cd or P["atk_cd"]) - P["atk_dur"]))
        return rel_pack or emp

    def rend():
        """Rending Claws: the spring (q_jump), tft.dll's landing LAND short of Darius with the murk under it, the claw X
        and a crit's star on him, the rend; then q_n quicker bites with the claws' glint round it."""
        t = c.t
        c.a("leap", tick(P["q_jump"]))
        land = t + tick(P["q_jump"] - 1)
        x, _ = me.pos(t)
        me.moves.append((land - 1, land, x, d.pos(land)[0] - REACH))
        c.at_spot("q_land", land, d.pos(land)[0] - REACH, me.pos(land)[1], sheet=c.small, under=True)
        c.on_foe(d, "q_hit", land)
        c.on_foe(d, "p_hit", land + 60)
        d.flinches.append(land)
        c.a("rend", tick(P["q_dur"] - P["q_jump"]))
        cd = P["atk_cd"] * 100 / (100 + P["q_as"])
        glint = c.t
        for _ in range(P["q_n"]):
            bite(cd, emp=True)
        c.on_me("q_emp", glint, until=c.t)
        return c.t

    def howl():
        """Slayer's Howl: on e_st the smoke round it for e_t (shown 1.8 s) with two bites."""
        t = c.t
        c.a("howl", tick(P["e_dur"]))
        at = t + tick(P["e_st"] - 1)
        c.on_me("e_howl", at, until=at + 1800)
        bite()
        bite()
        return at + 1800

    def call():
        """Pack Attack: the two pups beside it for r_t (shown 2.6 s), their pounce on r_st, two attacks with their
        bites."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        at = t + tick(P["r_st"] - 1)
        pack["until"] = at + 2600
        c.on_me("r_pack_r", t, sheet=c.big, until=pack["until"])   # tft.dll: the pair facing Darius (to the right)
        c.on_foe(d, "r_hit", at)
        d.flinches.append(at)
        bite()
        bite()
        return pack["until"]

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            bite()
            bite()
        elif step == "q":
            end = rend()
            c.wait(max(0, end + 300 - c.t))
        elif step == "e":
            end = howl()
            c.wait(max(0, end + 200 - c.t))
        elif step == "r":
            end = call()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：压低身子小跑，三条腿轮流迈", ["walk_in"], 200, 160),
          ("普攻 双头撕咬：两个头一起咬下去", ["attack"], REACH, 160),
          ("技能1 撕裂之爪：跃向残血敌人，落地暗影尘土、X 形爪痕（暴击时银星），之后三次快咬（脚下青色爪光）",
           ["q"], REACH + LEAP_FROM, 170),
          ("技能2 狂战士之嚎：仰头长嚎，身边紫黑色暗影烟往上蹿（吸血、伤害提高）", ["e"], REACH, 170),
          ("大招 狼群攻击：两只小暗影狼扑上去，之后它每次攻击小狼跟着咬两口", ["r"], REACH, 170)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_murkwolf_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_murkwolf_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_murkwolf_skills.gif")))


if __name__ == "__main__":
    main()
