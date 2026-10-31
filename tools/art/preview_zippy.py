#!/usr/bin/env python3
"""Preview images for Zippy (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_zippy.py [--out docs/preview] [--only frames|effects|skills]

  tft_zippy_frames.png    every animation's dense frames (hd_, PPU 2.2, as league.dll shows them)
  tft_zippy_effects.png   every effect animation, 3x
  tft_zippy_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                          (tools/kit/build_zippy.py, 60 ticks a second) and as tft.dll plays its parts
                          (addons/tft/src/zippy.rs), captioned in Chinese, 4x (preview_sohm.py's way): the sprint; Claw
                          Kick (with Adventurer's Spirit's gold ring under it, as with allies near); Backflip Kick (Darius
                          knocked up); Rolling Charge (the ball rolling e_speed a tick for e_t ticks through Darius and
                          Garen, the speed wisps at its feet - no ally here); Somersault Assault (the shield, the spring,
                          the leap at the healthiest - Ashe, the others hurt - the crash and its stun stars).
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
from build_zippy import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_zippy")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_zippy_fx", "tft_zippy_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = P["atk_range"] // 1000   # game px between its pivot and Darius's when it attacks
SPOTS = ((22, -3), (46, 3))      # Garen and Ashe behind Darius, on the line (game px)
TOUCH = 22                       # tft.dll lands this far in front of the one it leaps at (zippy.rs TOUCH 22000)


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "zippy", self.z))
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


def scene(out, steps, gap, W=300, H=170, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_zippy_fx"], fx["tft_zippy_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if any(s in steps for s in ("e", "r")):                   # two more enemies behind Darius
        c.foes = tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
    foes = (d,) + tuple(c.foes)
    c.wait(300)

    def kick():
        """One attack: the claw kick on atk_st, its hit on Darius."""
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def backflip():
        """Backflip Kick: the crouch, the flip, the feet up on q_st: the arcs on Darius, knocked up q_up ticks."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        hit = t + tick(P["q_st"] - 1)
        c.on_foe(d, "q_hit", hit)
        d.hops.append((hit, hit + tick(P["q_up"]), 10))
        return hit + tick(P["q_up"]) + 200

    def roll():
        """Rolling Charge: the speed wisps at its feet (an ally's; none here: on itself), the curl, from e_st the ball
        rolling e_speed a tick for e_t ticks, the dust where it set off, a bump on everyone it rolls over."""
        t = c.t
        c.on_me("e_speed", t, until=t + tick(P["e_ms_t"]), under=True)
        c.a("skill2", tick(P["e_dur"]))
        go = t + tick(P["e_st"] - 1)
        x0_, y0_ = me.pos(go)
        x1 = x0_ + P["e_speed"] * P["e_t"] / 1000
        t1 = go + tick(P["e_t"])
        c.at_spot("e", go, x0_, y0_, sheet=small)
        me.moves.append((go, t1, x0_, x1))
        for foe in foes:
            fx_ = foe.pos(go)[0]
            if x0_ <= fx_ <= x1:
                th = go + (fx_ - x0_) / (x1 - x0_) * (t1 - go)
                c.on_foe(foe, "e_hit", th)
                foe.flinches.append(th)
        return t1 + 300

    def assault(target):
        """Somersault Assault: the shield at once (r_sh_t), the spring dust on r_go, the leap (tft.dll: r_speed a tick)
        landing TOUCH in front of `target` (the healthiest), the crash on it: the stars of its stun, a short knockback."""
        t = c.t
        c.on_me("r_shield", t, sheet=c.big, until=t + tick(P["r_sh_t"]))
        c.a("ult", tick(P["r_dur"]))
        go = t + tick(P["r_go"] - 1)
        xa, ya = me.pos(go)
        c.at_spot("r", go, xa, ya, sheet=small)
        xb = target.pos(go)[0] - TOUCH
        land = go + tick(max(1, (xb - xa) * 1000.0 / P["r_speed"]))
        me.moves.append((go, land, xa, xb))
        x, y = target.pos(land)
        c.at_spot("r_hit", land, x, y, sheet=c.big, under=False)
        target.slides.append((land, land + tick(P["r_kb_t"]), P["r_kb"] * P["r_kb_t"] / 1000))
        target.flinches.append(land + tick(P["r_kb_t"]))
        return land + tick(P["r_stun"])

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            t0 = c.t
            kick()
            kick()
            c.on_me("p_guild", t0, until=c.t, under=True)
        elif step == "q":
            end = backflip()
            c.wait(max(0, end + 300 - c.t))
        elif step == "e":
            end = roll()
            c.wait(max(0, end + 300 - c.t))
        elif step == "r":
            end = assault(foes[-1])
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：身子前倾，两条腿交替飞奔，尾巴往后伸直", ["walk_in"], 180, 170),
          ("普攻 利爪踢 + 被动 冒险家之魂：抬腿一蹬；身边有队友时脚下亮起金环（护甲魔抗）", ["attack"], REACH, 170),
          ("技能1 后空翻踢：后空翻两脚往上踢，把达瑞斯踢飞", ["q"], REACH, 170),
          ("技能2 翻滚冲锋：缩成羽毛球滚过去，撞到的敌人受伤；脚边的风线是友军加速（这里没有队友，加在自己身上）", ["e"], 30, 170),
          ("大招 翻滚突袭：套上护盾，跳起来缩成球砸向生命百分比最高的敌人（这里是满血的艾希），晕眩并击退", ["r"], 30, 200)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_zippy_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[8:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_zippy_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_zippy_skills.gif")))


if __name__ == "__main__":
    main()
