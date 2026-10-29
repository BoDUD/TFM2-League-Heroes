#!/usr/bin/env python3
"""Preview images for Steb (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_steb.py [--out docs/preview] [--only frames|effects|skills]

  tft_steb_frames.png    every animation's dense frames (hd_, PPU 2.6, as league.dll shows them)
  tft_steb_effects.png   every effect animation, 3x
  tft_steb_skills.gif    each skill alone with its effects against Darius, with Garen and Braum behind him as his
                         allies, timed like the kit (tools/kit/build_steb.py, 60 ticks a second) and as tft.dll plays
                         its parts (addons/tft/src/steb.rs), captioned in Chinese, 4x (preview_sevika.py's way): the
                         run; the two batons in turn; Field Medicine (the dose, its share on the two allies, the strike
                         and the stun); Wanted (the mark on Darius, the bounty on his death: the rush on Steb and his
                         allies); Medic's Pack (the circle, the shields, his guard, six healing pulses and their shares).
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
from build_steb import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_steb")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_steb_fx", "tft_steb_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
BRAUM = os.path.join(ROOT, "league", "champions", "league_braum")
REACH = 34                       # game px between his pivot and Darius's when he strikes (the baton reaches ~26 ahead)
ALLIES = (38, 74)                # his allies behind him (game px), facing right


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "steb", self.z))
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


def scene(out, steps, gap, W=340, H=150, z=4, tail=900, x0=120):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_steb_fx"], fx["tft_steb_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    allies = (Foe(load(GAREN), x0 - ALLIES[0], gy, mirror=False), Foe(load(BRAUM), x0 - ALLIES[1], gy, mirror=False))
    if any(s in steps for s in ("q", "e", "r")):
        c.foes = allies
    c.wait(300)

    def strike(second=False):
        """One attack: a baton, the other one the next time (attack / attack2)."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack2" if second else "attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def share(t):
        """The passive: the heal he got passed on to his two nearest allies (tft.dll's p_heal on each)."""
        for ally in allies:
            c.on_foe(ally, "p_heal", t + 30)

    def medicine():
        """Field Medicine: the dose on q_heal_at (the share to the allies), the strike on q_st, the stun."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        th = t + tick(P["q_heal_at"] - 1)
        c.on_me("q_heal", th)
        share(th)
        ts = t + tick(P["q_st"] - 1)
        c.on_foe(d, "q_hit", ts)
        d.flinches.append(ts)
        c.on_foe(d, "q_stun", ts, until=ts + tick(P["q_stun"]))
        return ts + tick(P["q_stun"])

    def wanted():
        """Wanted: the mark on the healthiest enemy (Darius here) on e_st; he falls to the allies' blows while Wanted,
        the bounty: e_kill on Steb, the rush on him and his allies."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        tm = t + tick(P["e_st"] - 1)
        c.on_foe(d, "e_mark", tm)
        down = tm + 1600
        c.on_foe(d, "e_wanted", tm + 460, until=down)
        for k in range(4):                      # the allies' blows land on the marked one
            d.flinches.append(tm + 500 + k * 280)
        d.death = down
        c.a("idle", down - c.t, loop=True)
        c.on_me("e_kill", down)
        for who in allies:
            c.on_foe(who, "e_rush", down + 200, until=down + 2200)
        c.on_me("e_rush", down + 200, until=down + 2200)
        return down + 2200

    def pack():
        """Medic's Pack: on r_at the circle on the ground, the shields on him and his allies, his guard; from r_at a
        healing pulse every r_every, r_n times, each passed on by the passive."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        to = t + tick(P["r_at"] - 1)
        c.on_me("r_pack", to, sheet=big)
        c.on_me("r_guard", to, until=to + tick(P["r_t"]))
        for ally in allies:
            c.on_foe(ally, "r_shield", to, until=to + tick(P["r_sh_t"]))
        for k in range(P["r_n"]):
            tp = to + tick(k * P["r_every"])
            c.on_me("r_heal", tp)
            for ally in allies:
                c.on_foe(ally, "r_heal", tp)
            share(tp + 120)
        end = to + tick(max(P["r_t"], P["r_sh_t"], P["r_n"] * P["r_every"]))
        c.a("idle", end - c.t, loop=True)
        return end

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            for k in range(4):
                strike(second=k % 2 == 1)
        elif step in ("q", "e", "r"):
            end = {"q": medicine, "e": wanted, "r": pack}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：往前跑（金铲铲原样的一整个跑步周期，两腿轮流在前）", ["walk_in"], 160, 170),
          ("普攻 双警棍连击：两根警棍轮流打", ["attack"], REACH, 170),
          ("技能1 战地医疗：给自己打一针回血（最近两名队友分到 25%），再一棍重击眩晕", ["q"], REACH, 180),
          ("技能2 通缉令：通缉生命最高的敌人（受到伤害 +25%），它倒下后全队攻速提高", ["e"], 70, 180),
          ("大招 医疗背包：全队护盾、自己减伤，之后连续六次治疗（治疗也会分给队友）", ["r"], 70, 190)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_steb_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[8:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_steb_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_steb_skills.gif")))


if __name__ == "__main__":
    main()
