#!/usr/bin/env python3
"""Preview images for Silco (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_silco.py [--out docs/preview] [--only frames|effects|skills]

  tft_silco_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_silco_effects.png   every effect animation, 3x
  tft_silco_skills.gif    each skill alone with its effects against Darius (Garen and Ashe beside him where the
                          monstrosities spread), timed like the kit (tools/kit/build_silco.py, 60 ticks a second) and as
                          tft.dll plays its parts (addons/tft/src/silco.rs), captioned in Chinese, 4x: the walk; the vial;
                          the canister lobbed (the mark under it), its burst and two monstrosities pouncing on the two
                          nearest enemies and biting; the Shimmer Shot on himself (no ally in the scene), its high and
                          the comedown; the Dominator's shield and the eye at five steps; the giant canister, its blast,
                          four monstrosities and the fog slowing the enemies inside.
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
from preview_pyke import Me, OnFoe  # noqa: E402
import preview_zoe as Z  # noqa: E402
from build_silco import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_silco")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_silco_fx", "tft_silco_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", f"league_{h}") for h in ("garen", "ashe")]
REACH = 55                       # game px between his pivot and Darius's when he attacks (atk_range 55000)
ARC = 26                         # a lobbed canister's height at the top of its arc (game px)


def px_tick(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


class Lob(Anim):
    """A lobbed picture: straight from (x, y) to (x1, y1) and up an arc of ARC px over the way."""

    def pos(self, t):
        x, y = super().pos(t)
        u = min(1.0, max(0.0, (t - self.t0) / max(1, self.until - self.t0)))
        return x, int(round(y - 4 * ARC * u * (1 - u)))


class Clip(Z.Clip):
    """preview_zoe's clip with his own dense frames and more than one enemy (Darius, `foes`)."""

    foes = ()

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "silco", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def on_foe(self, foe, tag, when, sheet=None, until=None):
        self.over.append(OnFoe(frames_of(sheet or self.small, tag), when, foe, until=until))

    def render(self, out, W, H, end, z=4, step=40):
        frames, tt = [], 0.0
        while tt < end:
            img = Image.new("RGBA", (W * z, H * z), ARENA)
            for an in self.under:
                f = an.frame(tt)
                if f is not None:
                    put(img, f, *an.pos(tt), z)
            units = [(f.y, f.frame(tt), f.pos(tt)) for f in (self.d,) + tuple(self.foes)]
            for an in self.body:
                f = an.frame(tt)
                if f is not None:
                    units.append((self.me.y + 0.5, f, an.pos(tt)))
                    break
            for _, f, p in sorted(units, key=lambda u: u[0]):
                if f is not None:
                    put(img, f, *p, z)
            for an in self.over:
                f = an.frame(tt)
                if f is not None:
                    put(img, f, *an.pos(tt), z)
            frames.append(img.convert("RGB"))
            tt += step
        sample = frames[::6]
        strip = Image.new("RGB", (W * z, H * z * len(sample)))
        for i, f in enumerate(sample):
            strip.paste(f, (0, i * H * z))
        pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        q_ = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
        q_[0].save(T.long_path(out), save_all=True, append_images=q_[1:], duration=step, loop=0)
        return len(frames), round(end / 1000.0, 1)


def scene(out, steps, gap, W=260, H=150, z=4, tail=900, x0=60):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_silco_fx"], fx["tft_silco_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "q" in steps or "r" in steps:              # the monstrosities spread: Garen and Ashe near Darius
        c.foes = (Foe(load(OTHERS[0]), far + 26, gy - 10), Foe(load(OTHERS[1]), far + 20, gy + 12))
    c.wait(300)

    def vial():
        """The vial thrown on a_rel at Darius (homing), its hit."""
        rel = c.t + tick(P["a_rel"] - 1)
        c.shot("a_vial", "a_hit", rel, P["a_speed"])
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def lob(tag, sheet, rel, travel, foe):
        x0_, y0_ = me.pos(rel)[0] + 4, me.y - 30
        x1, y1 = foe.pos(rel)
        c.over.append(Lob(frames_of(sheet, tag), rel, int(x0_), int(y0_), loop=True, until=rel + travel, x1=int(x1),
                          y1=int(y1)))
        return x1, y1

    def monsters(n, land, x, y):
        """tft.dll's monstrosities: each pounces on the next of the nearest enemies (round again when fewer), bites
        m_n times every m_gap ticks, melts."""
        foes = sorted((d,) + tuple(c.foes), key=lambda f: abs(f.pos(land)[0] - x) + abs(f.pos(land)[1] - y))
        for k in range(n):
            foe = foes[k % len(foes)]
            c.on_foe(foe, "m_leap", land)
            first = land + tick(P["m_leap"])
            for b in range(P["m_n"]):
                t = first + b * tick(P["m_gap"])
                c.on_foe(foe, "m_bite" if k % 2 == 0 else "m_bite_r", t)
                foe.flinches.append(t + 120)
            end = first + P["m_n"] * tick(P["m_gap"])
            fx_, fy = foe.pos(end)
            c.at_spot("m_die", end, fx_, fy, sheet=small, under=False)
        return land + tick(P["m_leap"]) + P["m_n"] * tick(P["m_gap"])

    def canister():
        """Canister of Monstrosities: lobbed on q_rel for q_fall ticks (the mark under it), the burst, two monsters."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        rel = t + tick(P["q_rel"] - 1)
        land = rel + tick(P["q_fall"])
        x, y = lob("q_can", small, rel, land - rel, d)
        c.at_spot("q_warn", rel, x, y, sheet=small, under=True)
        c.at_spot("q_burst", land, x, y, sheet=big, under=False)
        d.flinches.append(land)
        return monsters(P["q_n"], land, x, y)

    def dose():
        """Shimmer Shot on himself (no ally here): the dose on e_rel, the high for e_t, the comedown."""
        rel = c.t + tick(P["e_rel"] - 1)
        c.a("skill2", tick(P["e_dur"]))
        c.on_me("e_dose", rel)
        c.on_me("e_shimmer", rel + 200, until=rel + tick(P["e_t"]))
        c.on_me("e_crash", rel + tick(P["e_t"]))
        return rel + tick(P["e_t"]) + 600

    def flood():
        """Chem-Baron's Flood: the giant canister lobbed on r_rel for r_fall ticks over the warning, the blast, four
        monsters, the fog replayed every second for r_fog_t ticks, the enemies inside slowed."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        rel = t + tick(P["r_rel"] - 1)
        land = rel + tick(P["r_fall"])
        x, y = lob("r_can", big, rel, land - rel, d)
        c.at_spot("r_warn", rel, x, y, sheet=big, under=True)
        c.at_spot("r_burst", land, x, y, sheet=big, under=False)
        for k in range(P["r_fog_t"] // 60):
            c.at_spot("r_fog", land + k * 1000, x, y, sheet=big, under=True)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "r_slow", land + 60, until=land + tick(P["r_fog_t"]))
            foe.flinches.append(land)
        return max(monsters(P["r_n"], land, x, y), land + tick(P["r_fog_t"]))

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            vial()
            vial()
        elif step == "q":
            end = canister()
            c.wait(end + 300 - c.t)
        elif step == "e":
            end = dose()
            c.wait(end - c.t)
        elif step == "p":                         # the shield he spawns with, the eye at five steps
            c.on_me("p_shield", c.t, until=c.t + 2600)
            c.on_me("p_dom", c.t + 1300, until=c.t + 2600)
            c.wait(2600)
        elif step == "r":
            end = flood()
            c.wait(end + 300 - c.t)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：拄着手杖走", ["walk_in"], 150, 170),
          ("普攻：甩出一支微光药剂", ["attack"], REACH, 170),
          ("技能1 罐装畸变体：扔出储罐砸地炸开，放出2只畸变体扑到最近的敌人身上连咬5口", ["q"], REACH, 190),
          ("技能2 微光注射：把微光抛给身边攻击力最高的队友（没有就自己），药效过去掉一点血", ["e"], REACH, 170),
          ("被动 统领：每次出生得到护盾；每放一次技能叠一层法强，叠满5层头顶亮起伤疤眼", ["p"], REACH, 170),
          ("大招 炼金狂潮：巨型储罐砸地大爆炸，放出4只畸变体，留下减速的微光毒雾", ["r"], REACH, 210)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_silco_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[10:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_silco_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_silco_skills.gif")))


if __name__ == "__main__":
    main()
