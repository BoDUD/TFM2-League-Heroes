#!/usr/bin/env python3
"""Preview images for Scar (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_scar.py [--out docs/preview] [--only frames|effects|skills]

  tft_scar_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_scar_effects.png   every effect animation, 3x
  tft_scar_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_scar.py,
                         60 ticks a second) and as tft.dll plays its parts (addons/tft/src/scar.rs), captioned in
                         Chinese, 4x (preview_violet.py's way): the walk; the thrusts; the Firelight Dash (on the board
                         onto Darius, the strike, the heal); Puddle Jumper Surprise (a bomb at each of the three nearest:
                         Darius, Garen, Ashe, each stunned); the Spear Sweep (Darius and Garen knocked back); the
                         Firelight Raid (on the board at Darius, two fire bombs on the way, the landing blast throwing
                         Darius and Garen up, the guard).
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
from build_scar import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_scar")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_scar_fx", "tft_scar_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
ASHE = os.path.join(ROOT, "league", "champions", "league_ashe")
REACH = 40                       # game px between his pivot and Darius's when he thrusts (the spear reaches 26 ahead)


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "scar", self.z))
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


def scene(out, steps, gap, W=300, H=150, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_scar_fx"], fx["tft_scar_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "q" in steps:                              # the three nearest: Darius, Garen and Ashe
        c.foes = (Foe(load(GAREN), far + 26, gy - 10), Foe(load(ASHE), far + 20, gy + 12))
    elif "e" in steps or "r" in steps:            # a second enemy close by
        c.foes = (Foe(load(GAREN), far + 22, gy),)
    c.wait(300)

    def thrust():
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def dash():
        """The Firelight Dash: on the board onto Darius at p_speed, the strike, tft.dll's heal (Darius hit him first)."""
        d.attacks += [c.t + 100, c.t + 500]
        c.a("hit", 200)
        c.wait(500)
        t = c.t
        x_from = me.pos(t)[0]
        x_to = d.x - REACH
        land = t + max(1, x_to - x_from) / px_tick(P["p_speed"])
        me.moves.append((t, land, x_from, x_to))
        c.a("surf", max(tick(P["p_surf_t"]), land - t))
        c.on_foe(d, "p_hit", land)
        d.flinches.append(land)
        c.on_me("p_heal", land + 30)
        return land + 600

    def bombs():
        """Puddle Jumper Surprise: on q_rel a bomb at each of the three nearest, each stunned q_stun ticks."""
        t = c.t
        rel = t + tick(P["q_rel"] - 1)
        x0_, y0_ = me.pos(rel)[0] + 8, me.y - 30
        end = rel
        for foe in (d,) + tuple(c.foes):
            x1, y1 = foe.pos(rel)
            land = rel + max(1, x1 - x0_) / px_tick(P["q_speed"])
            c.fly("q_bomb", rel, land, x0_, x1, y0_ + (y1 - gy) // 2)
            c.on_foe(foe, "q_hit", land)
            c.on_foe(foe, "q_stun", land, until=land + tick(P["q_stun"]))
            foe.flinches.append(land)
            end = max(end, land + tick(P["q_stun"]))
        c.a("skill", tick(P["q_dur"]))
        return end

    def sweep():
        """The Spear Sweep: on e_st the cone in front, every enemy in it knocked back."""
        t = c.t + tick(P["e_st"] - 1)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "e_hit", t)
            foe.flinches.append(t)
            foe.slides.append((t, t + tick(P["e_kb_t"]) * 4, P["e_kb_speed"] * P["e_kb_t"] / 1000))
        c.a("skill2", tick(P["e_dur"]))
        return t + 400

    def raid():
        """The Firelight Raid: on the board at Darius at r_speed, fire bombs at r_b1 / r_b2 where he is, on arrival the
        landing blast (every enemy within r_r thrown up r_up ticks) and the guard."""
        t = c.t
        x_from = me.pos(t)[0]
        x_to = d.x - REACH
        land = t + (x_to - x_from) / px_tick(P["r_speed"])
        me.moves.append((t, land, x_from, x_to))
        c.a("ride", land - t)
        for b in ("r_b1", "r_b2"):
            tb = t + tick(P[b] - 1)
            if tb < land:
                c.at_spot("r_bomb", tb, me.pos(tb)[0], gy, sheet=small)
        c.a("land", tick(P["r_land_t"]))
        c.at_spot("r_land", land, x_to, gy, sheet=big)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "r_hit", land)
            foe.hops.append((land, land + tick(P["r_up"]), 10))
        end = land + 1600
        c.on_me("r_guard", land + 100, until=end)
        c.wait(max(0, land + tick(P["r_up"]) - c.t))
        while c.t + tick(P["atk_cd"]) < end:
            thrust()
        return end

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            thrust()
            thrust()
        elif step in ("p", "q", "e", "r"):
            end = {"p": dash, "q": bombs, "e": sweep, "r": raid}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：吊儿郎当地大步走，长矛竖在身侧", ["walk_in"], 160, 170),
          ("普攻：长矛刺击", ["attack"], REACH, 170),
          ("被动 野火冲刺：每6秒下一击踩滑板冲过去捅一矛，回复上次冲刺以来所受伤害的25%", ["p"], 110, 170),
          ("技能1 水坑狙击惊喜：向最近的3名敌人各扔一颗炸弹，魔法伤害+晕眩1秒，自己回血", ["q"], 90, 190),
          ("技能2 长矛横扫：横扫前方，打退敌人", ["e"], REACH, 170),
          ("大招 野火突袭：踩滑板冲向敌人，一路丢燃烧弹；落地爆炸击飞0.5秒，之后4秒减伤40%", ["r"], 130, 190)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_scar_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[8:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_scar_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_scar_skills.gif")))


if __name__ == "__main__":
    main()
