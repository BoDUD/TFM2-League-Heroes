#!/usr/bin/env python3
"""Preview images for Loris (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_loris.py [--out docs/preview] [--only frames|effects|skills]

  tft_loris_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_loris_effects.png   every effect animation, 3x
  tft_loris_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_loris.py,
                          60 ticks a second) and as tft.dll plays its parts (addons/tft/src/loris.rs), captioned in
                          Chinese, 4x: the run; the shield bash; Piltover Tussle (the barrier, the charge, the hit, the
                          nudge and the stun); Bulwark (the leap to a hurt Garen, the landing's barrier on him, his guard
                          mark); the Warden's shield (the burst, the barrier holding); the Iron Line (the slam's
                          shockwave, Darius and a second enemy thrown up and taunted, his iron stance).
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
from preview_garen import T, contact, frames_of, load  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me  # noqa: E402
import preview_zoe as Z  # noqa: E402
from preview_silco import Clip as SilcoClip, px_tick  # noqa: E402
from build_loris import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_loris")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_loris_fx", "tft_loris_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
REACH = 30                       # game px between his pivot and Darius's when he bashes (atk_range 25000 + bodies)


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "loris", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def scene(out, steps, gap, W=280, H=150, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_loris_fx"], fx["tft_loris_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "r" in steps:                              # a second enemy close by: the slam takes both
        c.foes = (Foe(load(GAREN), far + 22, gy),)
    if "e" in steps:                              # Garen as the hurt ally ahead of him, Darius on Garen
        ally = Foe(load(GAREN), x0 + 70, gy, mirror=False)
        c.foes = (ally,)
    c.wait(300)

    def bash():
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def tussle():
        """Piltover Tussle: the barrier on him, the charge from q_go for q_t ticks, Darius hit, nudged and stunned."""
        t = c.t
        c.on_me("q_shield", t)
        c.a("skill", tick(P["q_dur"]))
        go = t + tick(P["q_go"] - 1)
        c.at_spot("q_dash", go, me.pos(go)[0], gy, sheet=small)
        x_from = me.pos(go)[0]
        x_to = min(x_from + P["q_speed"] * P["q_t"] / 1000.0, d.x - 18)
        arrive = go + tick(P["q_t"])
        me.moves.append((go, arrive, x_from, x_to))
        hit = go + (x_to - x_from) / px_tick(P["q_speed"])
        c.on_foe(d, "q_hit", hit)
        nudge = P["q_kb_speed"] * P["q_kb_t"] / 1000.0
        d.slides.append((hit, hit + tick(P["q_kb_t"]), nudge))
        stun_end = hit + tick(P["q_stun"])
        c.on_foe(d, "q_stun", hit + tick(P["q_kb_t"]), until=stun_end)
        d.flinches.append(hit)
        return stun_end

    def bulwark():
        """Bulwark: tft.dll steps him to the hurt ally (Garen) at e_speed a tick, the landing's barrier on Garen, his guard
        mark e_t ticks; Darius hits Garen meanwhile."""
        ally = c.foes[0]
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        x_from = me.pos(t)[0]
        x_to = ally.x - 20
        land = t + 17 + (x_to - x_from) / px_tick(P["e_speed"])
        me.moves.append((t + 17, land, x_from, x_to))
        c.on_foe(ally, "e_land", land)
        c.on_foe(ally, "e_guard", land + 500, until=land + tick(P["e_t"]))
        d.attacks += [land + 300, land + 1300, land + 2300]
        return land + tick(P["e_t"])

    def warden():
        """The Warden: under 75 % the burst, then the barrier holding while the shield lasts."""
        c.on_me("p_burst", c.t)
        c.on_me("p_shield", c.t + 510, until=c.t + 3000)
        d.attacks += [c.t + 200, c.t + 1200, c.t + 2200]
        c.wait(3000)

    def iron_line():
        """The Iron Line: the shield heaved up, slammed on r_at: the shockwave at his feet, every enemy within r_r thrown
        up r_up ticks and taunted r_taunt ticks, his iron stance r_t ticks."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        slam = t + tick(P["r_at"] - 1)
        c.at_spot("r_slam", slam, me.pos(slam)[0], gy, sheet=big)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "r_hit", slam)
            foe.hops.append((slam, slam + tick(P["r_up"]), 10))
            c.on_foe(foe, "r_taunt", slam + tick(P["r_up"]), until=slam + tick(P["r_up"] + P["r_taunt"]))
        c.on_me("r_wall", slam + 300, until=slam + tick(P["r_t"]))
        return slam + tick(P["r_up"] + P["r_taunt"])

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            bash()
            bash()
        elif step == "q":
            end = tussle()
            c.wait(end + 300 - c.t)
        elif step == "e":
            end = bulwark()
            c.wait(end - c.t)
        elif step == "p":
            warden()
        elif step == "r":
            end = iron_line()
            c.wait(end + 300 - c.t)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：盾提在身侧沉重地小跑", ["walk_in"], 160, 170),
          ("普攻：举盾猛砸", ["attack"], REACH, 170),
          ("技能1 皮城争斗：身上亮起护盾，举盾冲锋，撞到的敌人被撞开、晕眩1.5秒", ["q"], 70, 170),
          ("技能2 盾卫：冲到血量最低的队友身边立盾，两人得护盾，之后4秒替他承受30%伤害", ["e"], 120, 170),
          ("被动 神盾使：每条命第一次掉到75%和25%血时，各得一层最大生命12%的护盾", ["p"], REACH, 170),
          ("大招 钢铁防线：巨盾砸地，周围敌人被击飞1秒、嘲讽2秒，自己减伤50%", ["r"], 26, 170)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_loris_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[10:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_loris_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_loris_skills.gif")))


if __name__ == "__main__":
    main()
