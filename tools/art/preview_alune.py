#!/usr/bin/env python3
"""Preview images for Alune (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_alune.py [--out docs/preview] [--only frames|effects|skills]

  tft_alune_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_alune_effects.png   every effect animation, 3x
  tft_alune_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_alune.py,
                          60 ticks a second), captioned in Chinese, 4x: the glide; the ring flung and flying back
                          (tft.dll); Moonfall's three shards on the three enemies nearest her - Darius, Garen and Ashe (the
                          eclipse mark); Moonlight on her;
                          the moon's phases over her head growing with Q / E / Q and the ult at full moon (the moon
                          wanes); Moon Descends alone (the shadow, the moon pressing down, the crash).
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
from preview_pyke import Me, OnFoe, mirrored  # noqa: E402
import preview_zoe as Z  # noqa: E402
from build_alune import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_alune")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_alune_fx", "tft_alune_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
# Moonfall's other two enemies (the user, 2026-10-26: 「怎么出现三个诺手」 - three copies of Darius read as a glitch)
OTHERS = [os.path.join(ROOT, "league", "champions", f"league_{h}") for h in ("garen", "ashe")]
REACH = 55                       # game px between her pivot and Darius's when she attacks (atk_range 55000)


def px_tick(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


class Clip(Z.Clip):
    """preview_zoe's clip with her own dense frames and more than one enemy (Darius, `foes`)."""

    foes = ()

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "alune", self.z))
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
    small, big = fx["tft_alune_fx"], fx["tft_alune_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "q" in steps:                              # Moonfall's three: Garen and Ashe near Darius
        c.foes = (Foe(load(OTHERS[0]), far + 26, gy - 10), Foe(load(OTHERS[1]), far + 20, gy + 12))
    phase = [0]
    shown = []

    def moon_up():
        """The passive: one phase more (at most full), its picture over her head."""
        t = c.t
        if shown:
            shown[-1].until = t
        phase[0] = min(3, phase[0] + 1)
        an = Z.OnMe(frames_of(small, f"p_moon{phase[0]}"), t, me, until=t + 60000)
        c.over.append(an)
        shown.append(an)

    def wane(t):
        if shown:
            shown[-1].until = t
        phase[0] = 0

    c.wait(300)

    def ring():
        """The ring flung on a_rel at Darius (homing), its hit, and flying back to her through him (tft.dll)."""
        t = c.t
        rel = t + tick(P["a_rel"] - 1)
        hit = c.shot("a_ring", "a_hit", rel, P["a_speed"])
        c.a("attack", tick(P["atk_dur"]))
        x1, x0_ = d.pos(hit)[0], me.pos(hit)[0] + 4
        home = hit + (x1 - x0_) / px_tick(P["a_speed"])
        c.over.append(Anim(mirrored(frames_of(small, "a_ring")), hit, int(x1), int(me.y - 14), loop=True,
                           until=home, x1=int(x0_), y1=int(me.y - 14)))
        c.on("a_hit", hit + 40)
        d.flinches.append(hit + 40)
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def moonfall():
        """Moonfall: the shards called on q_rel, each falling q_fall ticks on an enemy (q_drop), the splash and the
        eclipse mark."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        rel = t + tick(P["q_rel"] - 1)
        land = rel + tick(P["q_fall"])
        for foe in (d,) + tuple(c.foes):
            x, y = foe.pos(rel)
            c.at_spot("q_drop", rel, x, y, sheet=big, under=False)
            c.at_spot("q_hit", land, x, y, sheet=small, under=False)
            c.on_foe(foe, "q_shred", land + 60, until=land + 2200)
            foe.flinches.append(land)
        c.t = max(c.t, t + tick(P["q_dur"]))
        moon_up()

    def moonlight():
        """Moonlight: the blessing on e_rel, the glow on her (and every ally near: none here)."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        rel = t + tick(P["e_rel"] - 1)
        c.on_me("e_glow", rel, until=rel + 1600)
        moon_up()

    def moon_descends():
        """Moon Descends: on r_rel the shadow on the ground under Darius and the moon pressing down over him for r_open
        ticks, the crash where it lands (the hit, the stun)."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        rel = t + tick(P["r_rel"] - 1)
        x, y = d.pos(rel)
        c.at_spot("r_warn", rel, x, y, sheet=big, under=True)
        c.at_spot("r_fall", rel, x, y, sheet=big, under=False)
        land = rel + tick(P["r_open"])
        c.at_spot("r_moon", land, x, y, sheet=big, under=False)
        c.on("r_hit", land)
        d.flinches.append(land)
        wane(land)
        return land

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            ring()
            ring()
        elif step == "q":
            moonfall()
            c.wait(1600)
        elif step == "e":
            moonlight()
            c.wait(1500)
        elif step == "phases":                    # Q, E, Q: the moon grows to full; the ult at full, the moon wanes
            moonfall()
            c.wait(500)
            moonlight()
            c.wait(500)
            moonfall()
            c.wait(600)
            land = moon_descends()
            c.wait(land + 900 - c.t)
        elif step == "r":
            land = moon_descends()
            c.wait(land + 900 - c.t)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：坐在月牙法杖上滑行", ["walk_in"], 150, 170),
          ("普攻：把螺旋月环像飞盘一样甩出去，打中后飞回她手里，回程路上的敌人再挨一下", ["attack"], REACH, 170),
          ("技能1 月之降临：月光碎片落在离她最近的三个敌人身上，魔法伤害、降魔抗", ["q"], REACH, 190),
          ("技能2 月华：她和身边的队友攻速提高", ["e"], REACH, 170),
          ("被动 月相：每放一次技能头顶的月亮长一档，满月时大招最痛，砸完回到新月", ["phases"], REACH, 210),
          ("大招 月曜降临：满月从天而降，伤害由命中的敌人平分（人越少越痛），中心眩晕", ["r"], REACH, 210)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_alune_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[10:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_alune_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_alune_skills.gif")))


if __name__ == "__main__":
    main()
