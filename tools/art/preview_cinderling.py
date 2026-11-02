#!/usr/bin/env python3
"""Preview images for the Cinderling (the tft pack), built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_cinderling.py [--out docs/preview] [--only frames|effects|skills]

  tft_cinderling_frames.png    every animation's dense frames (hd_, PPU 2.33, as league.dll shows them)
  tft_cinderling_effects.png   every effect animation, 3x
  tft_cinderling_skills.gif    each skill alone with its effects against Darius, timed like the kit
                               (tools/kit/build_cinderling.py, 60 ticks a second), captioned in Chinese, 4x
                               (preview_gromp.py's way): the hop; Ember Leaf (the leaf flying, its cut on Darius) with
                               Scarlet Buff full (the ember crown, the burn on him); Razor Leaves (five leaves from five
                               heights, the convergence on him, the wound mark and the burn); Burrow (the dig where it
                               stands kicking earth on him and his mud, the move back under the ground, the burst out
                               there); Wildfire Leafstorm (the fire behind it standing, the burning-leaf arc round it,
                               the burning leaves at him every r_p, their hits, his burn).
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
from build_cinderling import P, Q_Y  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_cinderling")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_cinderling_fx", "tft_cinderling_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
REACH = P["atk_range"] // 1000                  # game px between its pivot and Darius's when it attacks
AHEAD = 8                                       # where its leaves leave, game px ahead of its pivot


def height(y_offset):
    """A projectile's height over the pivot in game px (5000 - y_offset units, 1000 a px)."""
    return (5000 - y_offset) // 1000


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "cinderling", self.z))
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


def scene(out, steps, gap, W=400, H=180, z=4, tail=900, x0=100):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_cinderling_fx"], fx["tft_cinderling_big"]
    gy = H - 40
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z

    def fly(tag, rel, speed, h):
        """A straight shot from its leaves at Darius, h px over its pivot; returns its arrival."""
        x0_, y0_ = me.pos(rel)
        x0_ += AHEAD
        x1 = d.pos(rel)[0]
        hit = rel + tick((x1 - x0_) * 1000.0 / speed)
        c.fly(tag, rel, hit, x0_, x1, y0_ - h)
        return hit

    def burn(t):
        c.on_foe(d, "p_burn", t, until=t + tick(P["p_burn_t"]))

    def leaf(full):
        hit = fly("a_leaf", c.t + tick(P["a_rel"] - 1), P["a_speed"], height(P["a_y"]))
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        if full:
            burn(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def razor():
        """Razor Leaves: five leaves from Q_Y's heights, the middle one first; the convergence, wound and burn on
        Darius as the middle one lands."""
        t = c.t
        mid = len(Q_Y) // 2
        last = 0
        for k, y in enumerate(Q_Y):
            rel = t + tick(P["q_rel"] - 1 + abs(k - mid) * P["q_gap"])
            hit = fly("q_leaf", rel, P["q_speed"], height(y))
            d.flinches.append(hit)
            last = max(last, hit)
            if k == mid:
                c.on_foe(d, "q_hit", hit)
                c.on_foe(d, "q_wound", hit, until=hit + tick(P["q_wound_t"]))
                burn(hit)
        c.a("skill", tick(P["q_dur"]))
        return last + tick(P["q_wound_t"])

    def burrow():
        """Burrow: the dig where it stands (the earth kicked on Darius and his mud), back e_back x e_move under the
        ground, the burst out there."""
        t = c.t
        x, y = me.pos(t)
        c.at_spot("e_dig", t, x, y + 11, sheet=c.small)
        kick = t + tick(P["e_kick"] - 1)
        c.on_foe(d, "e_slow", kick, until=kick + tick(P["e_hold"]))
        d.flinches.append(kick)
        t0, t1 = t + tick(P["e_dig"] - 1), t + tick(P["e_dig"] - 1 + P["e_move"])
        back = P["e_back"] * P["e_move"] // 1000
        me.moves.append((t0, t1, x, x - back))
        out_t = t + tick(P["e_dig"] + P["e_move"])
        c.at_spot("e_pop", out_t, x - back, y + 11, sheet=c.small)
        c.a("skill2", tick(P["e_dur"]))
        return out_t + 600

    def storm():
        """Wildfire Leafstorm: the fire behind it on r_rel, the leaf arc round it for r_t, r_n burning leaves at Darius
        every r_p (all at him: he is the only enemy), their hits and his burn."""
        t = c.t
        rel = t + tick(P["r_rel"] - 1)
        c.on_me("r_cast", t, sheet=c.big)
        c.on_me("r_blaze", rel, sheet=c.big, until=rel + tick(P["r_t"]), under=True)
        c.a("ult", tick(P["r_dur"]))
        for k in range(P["r_t"] // P["r_p"]):
            for j in range(P["r_n"]):
                hit = fly("r_leaf", rel + tick(k * P["r_p"] + j * 3), P["r_speed"], height(P["a_y"]) + 3 * (j - 1))
                c.on_foe(d, "r_hit", hit)
                d.flinches.append(hit)
            burn(hit)
        # it keeps attacking (faster) while the storm goes on
        while c.t < rel + tick(P["r_t"]):
            c.a("attack", tick(P["atk_dur"]))
            c.wait(tick(P["atk_cd"] * 100 // (100 + P["r_as"]) - P["atk_dur"]))
        return rel + tick(P["r_t"])

    c.wait(300)
    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            leaf(False)
            t0 = c.t
            leaf(True)
            leaf(True)
            c.on_me("p_full", t0, sheet=c.big, until=c.t)
        elif step == "q":
            end = razor()
            c.wait(max(0, end + 200 - c.t))
        elif step == "e":
            end = burrow()
            c.wait(max(0, end - c.t))
        elif step == "r":
            end = storm()
            c.wait(max(0, end + 200 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：一蹦一蹦地往前跑", ["walk_in"], 220, 170),
          ("普攻 余烬叶：往前一蹦甩出叶子；绯红霸符叠满（叶尖冒火）后普攻灼烧英雄", ["attack"], REACH, 180),
          ("技能1 刃叶：叶子竖起，五片叶刃从不同高度飞向目标：物理伤害 + 重伤（头顶裂叶）+ 灼烧", ["q"], REACH, 180),
          ("技能2 钻土突袭：钻进地里溅起泥土（近身敌人伤害 + 减速），在地下往后退，再从远处钻出", ["e"], 40, 170),
          ("大招 燎原叶暴：站起来点燃叶子，身边火叶环绕，攻速变快，不停朝敌人射燃烧叶刃", ["r"], REACH, 190)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_cinderling_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_cinderling_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_cinderling_skills.gif")))


if __name__ == "__main__":
    main()
