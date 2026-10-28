#!/usr/bin/env python3
"""Preview images for the Ancient Krug (the tft pack), built from the exported game sprites (so they also prove the
sheets load).

    python tools/art/preview_krug.py [--out docs/preview] [--only frames|effects|skills]

  tft_krug_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_krug_effects.png   every effect animation, 3x
  tft_krug_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_krug.py,
                         60 ticks a second) and as tft.dll plays its part (addons/tft/src/krug.rs), captioned in
                         Chinese, 4x: the run; the rock-fist slam; Rock and Roll (the stone layer, the boulder rolling
                         onto Darius, the hit, Darius knocked back); Stone Shell (the stomp, the shell held, Darius
                         taunted); the Shattered Rebirth (a lethal blow: the shatter, the rubble, the reforming, the
                         taunt, the Mini Krug's ring); Ancient Landslide (the spring out of sight, the landing mark under
                         Darius, the crash, both enemies thrown up, the falling rocks).
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
from build_krug import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_krug")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_krug_fx", "tft_krug_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
REACH = 38                       # game px between his pivot and Darius's when he strikes (atk_range 25000 + his bulk)
REFORM = 24                      # addons/tft/src/krug.rs REFORM


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4, frames=None):
        fr = list(dense(self.sp, tag, "krug", self.z))
        if frames is not None:                         # only these frames of the tag (the ult's crash)
            fr = [fr[k] for k in frames]
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def hide(self, dur):
        """Unseen for `dur` ms (the ult's CasterInvisible): an empty frame in his place."""
        blank = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        an = Anim([(blank, dur)], self.t, 0, 0, until=self.t + dur)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until


def scene(out, steps, gap, W=280, H=150, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_krug_fx"], fx["tft_krug_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "r" in steps or "e" in steps:              # a second enemy close by: the crash and the taunt take both
        c.foes = (Foe(load(GAREN), far + 22, gy),)
    c.wait(300)

    def strike():
        """A rock-fist slam: the fists land on atk_st."""
        hit = c.t + tick(P["atk_st"] - 1)
        d.flinches.append(hit)
        c.on_foe(d, "a_hit", hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def roll():
        """Rock and Roll: the stone layer, then MoveToTarget at q_speed onto Darius; on arrival the hit and the
        knock-back."""
        t = c.t
        c.on_me("q_shield", t)
        x_from = me.pos(t)[0]
        x_to = d.x - REACH + 8
        arrive = t + 17 + (x_to - x_from) / px_tick(P["q_speed"])
        me.moves.append((t + 17, arrive, x_from, x_to))
        c.a("skill", tick(P["q_dur"]))
        c.on_foe(d, "q_hit", arrive)
        d.flinches.append(arrive)
        d.slides.append((arrive, arrive + tick(P["q_kb"]), px_tick(P["q_kb_speed"]) * tick(P["q_kb"])))
        c.wait(max(0, arrive + 600 - c.t))

    def shell():
        """Stone Shell: the stomp, the shell held e_t ticks (cut short here), the enemies near taunted into him."""
        t = c.t
        c.at_spot("e_cast", t + 100, me.pos(t)[0], gy, sheet=small)
        c.on_me("e_shell", t + 100, until=t + 2200)
        c.a("skill2", tick(P["e_dur"]))
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "e_taunt", t + 100, until=t + 100 + tick(P["e_taunt"]))
        d.attacks += [t + 300, t + 1300]
        c.wait(200)
        strike()
        strike()

    def rebirth():
        """The Shattered Rebirth (tft.dll): a lethal blow - the shatter (Animation CC `shatter`, p_burst), lying in
        pieces p_t ticks, the reforming (`reform`, p_up), the enemies near taunted, the Mini Krug's ring from then on."""
        t = c.t
        d.attacks += [t - 200]
        c.on_me("p_burst", t, until=t + 400)
        c.a("shatter", tick(P["p_t"]))
        up = c.t
        c.on_me("p_up", up, until=up + 420)
        c.on_me("p_mini", up, until=up + 4000, under=True)
        c.on_foe(d, "e_taunt", up, until=up + tick(P["p_taunt"]))
        c.a("reform", tick(REFORM))
        strike()
        strike()

    def landslide():
        """Ancient Landslide: crouch and spring (seen r_go ticks), unseen until r_at, the landing mark under Darius
        meanwhile; Teleport onto him: the crash, every enemy within r_r thrown up r_up ticks; r_rock_t later the rocks."""
        t = c.t
        c.on_foe(d, "r_mark", t + 17)
        c.a("ult", tick(P["r_go"]), frames=[0, 1])
        go = t + tick(P["r_go"] - 1)
        c.at_spot("r_jump", go, me.pos(go)[0], gy, sheet=small)
        crash = t + tick(P["r_at"] - 1)
        me.moves.append((crash - 1, crash, me.pos(go)[0], d.x - 6))
        c.hide(crash - c.t)                            # CasterInvisible: unseen until the crash
        c.a("ult", tick(P["r_dur"] - P["r_at"] + 1), frames=[3, 4])
        c.at_spot("r_slam", crash, d.x - 6, gy, sheet=big)
        rocks = crash + tick(P["r_rock_t"])
        c.at_spot("r_rocks", rocks, d.x - 6, gy, sheet=big)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "r_hit", crash)
            foe.hops.append((crash, crash + tick(P["r_up"]), 12))
            c.on_foe(foe, "r_rock_hit", rocks + 250)
        return rocks + 700

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            strike()
            strike()
        elif step == "q":
            roll()
        elif step == "e":
            shell()
        elif step == "p":
            rebirth()
        elif step == "r":
            end = landslide()
            c.wait(end + 300 - c.t)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：四肢着地沉重地奔跑", ["walk_in"], 160, 170),
          ("普攻：岩拳砸地", ["attack"], REACH, 170),
          ("技能1 岩之摇滚：包上一层石头（护盾），缩成石球滚过去撞飞敌人", ["q"], 110, 170),
          ("技能2 坚岩外壳：缩进巨石（护甲魔抗+），嘲讽周围的敌人", ["e"], REACH, 170),
          ("被动 碎岩重生：致命一击时碎成石堆，再以小石甲虫站起（35%血、攻速+30%），嘲讽周围敌人", ["p"], REACH, 170),
          ("大招 远古崩落：跃起砸进敌群击飞，随后天上落石", ["r"], 120, 200)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_krug_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[9:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_krug_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_krug_skills.gif")))


if __name__ == "__main__":
    main()
