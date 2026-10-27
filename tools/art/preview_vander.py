#!/usr/bin/env python3
"""Preview images for Vander (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_vander.py [--out docs/preview] [--only frames|effects|skills]

  tft_vander_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_vander_effects.png   every effect animation, 3x
  tft_vander_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_vander.py,
                           60 ticks a second) and as tft.dll plays its parts (addons/tft/src/vander.rs), captioned in
                           Chinese, 4x: the run; the punches; the Hound of the Underground (the guard, Darius taunted,
                           the charged fist, the heavy strike); Iron Fist (the rush, the uppercut, the stun); the
                           Watcher (the ring under him while Darius hits him); Last Stand on the Bridge (the leap, the
                           slam's shockwave, Darius and Garen thrown up, the stand's embers).
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
from build_vander import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_vander")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_vander_fx", "tft_vander_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
REACH = 40                       # game px between his pivot and Darius's when he punches (his stance reaches 20 ahead)


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "vander", self.z))
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
    small, big = fx["tft_vander_fx"], fx["tft_vander_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "r" in steps:                              # a second enemy close by: the slam takes both
        c.foes = (Foe(load(GAREN), far + 22, gy),)
    c.wait(300)

    def punch(strike=False):
        hit = c.t + tick(P["atk_st"] - 1)
        c.on_foe(d, "q_hit" if strike else "a_hit", hit)
        d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))
        return hit

    def hound():
        """The Hound: the stomp into the guard, Darius taunted q_taunt ticks, the guard held q_t ticks, the charged fist
        over his head until the next punch, the heavy strike."""
        t = c.t
        c.on_me("q_guard_in", t)
        c.on_me("q_guard", t + 420, until=t + tick(P["q_t"]))
        c.on_foe(d, "q_taunt", t, until=t + tick(P["q_taunt"]))
        d.attacks += [t + 300, t + 1300]
        c.a("skill", tick(P["q_dur"]))
        c.wait(tick(P["atk_cd"]))
        c.on_me("q_ready", t + 300, until=c.t + tick(P["atk_st"] - 1))
        hit = punch(strike=True)
        return hit

    def iron_fist():
        """Iron Fist: the dust where he starts, the rush onto Darius at e_speed, the uppercut and the stun."""
        t = c.t
        c.at_spot("e_dash", t, me.pos(t)[0], gy, sheet=small)
        x_from = me.pos(t)[0]
        x_to = d.x - REACH
        land = t + (x_to - x_from) / px_tick(P["e_speed"])
        me.moves.append((t, land, x_from, x_to))
        c.a("skill2", land - t)
        c.a("upper", tick(P["e_up_t"]))
        c.on_foe(d, "e_hit", land)
        c.on_foe(d, "e_stun", land + 100, until=land + tick(P["e_stun"]))
        d.flinches.append(land)
        return land + tick(P["e_stun"])

    def watcher():
        """The Watcher: the thin ring under him while Darius hits him."""
        c.on_me("p_watch", c.t, until=c.t + 2600)
        d.attacks += [c.t + 200, c.t + 1200, c.t + 2200]
        c.a("idle", 2600)

    def last_stand():
        """Last Stand: the leap onto Darius at r_speed, on landing the slam: the shockwave at his feet, every enemy within
        r_r thrown up r_up ticks, the stand's embers r_t ticks."""
        t = c.t
        x_from = me.pos(t)[0]
        x_to = d.x - REACH
        land = t + (x_to - x_from) / px_tick(P["r_speed"])
        me.moves.append((t, land, x_from, x_to))
        c.a("ult", land - t)
        c.a("slam", tick(P["r_slam_t"]))
        c.at_spot("r_slam", land, x_to, gy, sheet=big)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "r_hit", land)
            foe.hops.append((land, land + tick(P["r_up"]), 10))
        c.on_me("r_hold", land + 200, until=land + tick(P["r_t"]))
        return land + tick(P["r_t"])

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            punch()
            punch()
        elif step == "q":
            end = hound()
            c.wait(max(0, end + 600 - c.t))
        elif step == "e":
            end = iron_fist()
            c.wait(max(0, end + 300 - c.t))
        elif step == "p":
            watcher()
        elif step == "r":
            end = last_stand()
            c.wait(max(0, end + 200 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：拳手架势小跑", ["walk_in"], 160, 170),
          ("普攻：拳套重拳", ["attack"], REACH, 170),
          ("技能1 地下猎犬：防御姿态，嘲讽周围敌人，加双抗；下一拳变成重击", ["q"], REACH, 170),
          ("技能2 铁拳突进：冲到敌人身上一记上勾拳，晕眩0.5秒", ["e"], 80, 170),
          ("被动 监察：受到的伤害降低10%，血量高于一半时降低20%", ["p"], REACH, 170),
          ("大招 桥头死守：跳进敌群砸地，击飞周围敌人1秒，之后4秒减伤（身边敌人越多减得越多）", ["r"], 90, 190)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_vander_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[10:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_vander_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_vander_skills.gif")))


if __name__ == "__main__":
    main()
