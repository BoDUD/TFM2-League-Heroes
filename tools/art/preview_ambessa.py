#!/usr/bin/env python3
"""Preview images for Ambessa, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_ambessa.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_ambessa_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  league_ambessa_effects.png   every effect animation, 3x
  league_ambessa_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_ambessa.py, 60 ticks a
                               second, the add-on's League rules): twin-blade blows; Cunning Sweep (the half circle
                               drawn into her frames, the cut and the blade's edge on Darius) then Drakehound's Step
                               (the streaks, the dust where it stops, the amber stir till the empowered cleave) and
                               Sundering Slam at once (Q -> Q2: the leap, the rift along the line, the hit); Lacerate
                               (the whirl, the cut, the slow; the step; the second whirl where it stops); Repudiation
                               (the shell, Darius striking her braced, the slam and the burst); Public Execution (the
                               smoke where she was, the mark over the pin, the crater) giving Q back at once (R -> Q ->
                               Q2); he falls; 3x.
  league_ambessa_skills.gif    each skill and combo alone with its effects, captioned in Chinese, 4x (the user,
                               2026-10-24: 「带技能的gif图呢？」).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows  # noqa: E402
from preview_garen import T, contact, frames_of, load  # noqa: E402
from preview_gnar import Clip  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_ambessa import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_ambessa")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_ambessa_fx", "league_ambessa_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
REACH = 20                      # game px between her and Darius where a dash or the blink stops (the two radii)


class Ambessa(Clip):
    """preview_gnar's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "ambessa", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Darius (the slow, the suppression mark)."""
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def mine(self, tag, when, sheet=None, until=None, under=False):
        """A picture following her (the whirl, the shell, the shockwave, the stir)."""
        (self.under if under else self.over).append(OnMe(frames_of(sheet or self.small, tag), when, self.me,
                                                         until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: the dust, the smoke, the crater, the rift)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


# the fight's steps in order (showcase); skills() plays some of them alone
FIGHT = ["walk_in", "attack", "q_q2", "e", "w", "r", "kill"]


def showcase(out, z=3, steps=FIGHT, W=320, H=150, gap=150, tail=1500):
    """The scripted fight (or some of its steps: skills() plays each skill alone) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_ambessa_fx"], fx["league_ambessa_big"]
    gy = H - 30
    x0 = 40
    far = x0 + gap                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Ambessa(load(CHAMP), d, me, small, big)
    st = {"pw": -1.0}
    c.wait(300)

    def blow():
        """Twin blades; after a step, the empowered cleave (its stir under her goes)."""
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        b = t + tick(P["a_hit"] - 1)
        if b < st["pw"]:
            c.on("pw_hit", b)
            st["pw"] = -1.0
            for an in c.under:                          # the stir ends with the empowered blow
                if getattr(an, "stir", False) and an.until > b:
                    an.until = b
        else:
            c.on("a_hit", b)
        d.flinches.append(b)

    def step(t0, then=None):
        """Drakehound's Step at t0: the lunge (its streaks drawn in), the dash at Darius, the dust where it stops, the
        empowered blow readied (the stir round her feet till then); `then` runs at the dash's end."""
        c.t = t0
        xa = me.pos(t0)[0]
        x1 = max(xa, min(xa + P["st_reach"] / 1000, d.pos(t0)[0] - REACH))
        t1 = t0 + max(tick(1), (x1 - xa) / px_ms(P["st_speed"]))
        # the lunge's pose for st_dur ticks - cut at the dash's end when an action starts there (E's second lash)
        c.a("step", min(tick(P["st_dur"]), t1 - t0) if then else tick(P["st_dur"]))
        me.moves.append((t0, t1, xa, x1))
        c.at("st_land", t1, x1, gy, under=True)
        st["pw"] = t0 + tick(P["pw_t"])
        stir = Anim(frames_of(small, "pw_aura"), t0, 0, 0, loop=True, until=st["pw"])
        stir.pos, stir.stir = me.pos, True
        c.under.append(stir)
        if then:
            c.t = max(c.t, t1)
            then(t1)

    def sweep():
        """Cunning Sweep: wound up, the half circle (in her frames), the cut on Darius and the blade's edge (the add-on:
        he stands past q_tip % of the radius); the step q_hit - 1 + st_gap ticks in. -> the hit's time."""
        t = c.t
        h = t + tick(P["q_hit"] - 1)
        c.a("skill", tick(P["q_hit"] - 1 + P["st_gap"]))
        c.on("q_hit", h)
        if d.pos(h)[0] - me.pos(h)[0] >= P["q_r"] / 1000 * P["q_tip"] / 100:
            c.on("q_tip", h + tick(1))
        d.flinches.append(h)
        step(h + tick(P["st_gap"]))
        return h

    def slam():
        """Sundering Slam (the controller, q2_gap ticks after a sweep that hit): the leap, the slam, the rift along the
        line from her through Darius (drawn at its middle, q2_vis ticks), the hit; the step."""
        t = c.t
        h = t + tick(P["q2_hit"] - 1)
        c.a("slam", tick(P["q2_hit"] - 1 + P["st_gap"]))
        mid = me.pos(h)[0] + P["q2_len"] / 2000
        c.at("q2_crack", h, mid, gy, sheet=big, until=h + tick(P["q2_vis"]))
        c.on("q2_hit", h)
        d.flinches.append(h)
        step(h + tick(P["st_gap"]))
        return h

    def lash(when):
        c.mine("e_lash", when, sheet=big)
        c.on("e_hit", when)
        c.on_foe("slow", when, until=when + tick(P["e_slow_t"]), under=True)
        d.flinches.append(when)

    def lacerate():
        """Lacerate: the chains flung out, the whirl, the cut and the slow; the step; the second whirl where it stops
        (the lash pose played again)."""
        t = c.t
        h = t + tick(P["e_hit"] - 1)
        c.a("skill2", tick(P["e_hit"] - 1 + P["st_gap"]))
        lash(h)

        def again(t1):
            c.t = t1
            c.a("skill2", tick(P["e_dur"] - P["e_hit"]))
            lash(t1)
        step(h + tick(P["st_gap"]), then=again)

    def repudiation():
        """Repudiation (the controller, an enemy champion close): the shell, Darius striking her braced, the slam and its
        shockwave round her, the hit and the struck brace's burst (the add-on); the step."""
        t = c.t
        s = t + tick(P["w_brace"])
        c.a("w", tick(P["w_brace"] + P["st_gap"]))
        c.mine("w_brace", t)
        d.attacks.append(t + 80)
        c.mine("w_slam", s, sheet=big, under=True)
        c.on("w_hit", s)
        c.on("w_crit", s + tick(1))
        d.flinches.append(s)
        step(s + tick(P["st_gap"]))

    def execution():
        """Public Execution: the lunge, the smoke where she was, the blink onto Darius, the mark over the pin, the slam
        and the crater; Q back at once (R -> Q -> Q2). -> the crash's time."""
        t = c.t
        b = t + tick(P["r_go"] - 1)
        s = b + tick(P["r_slam"])
        c.a("ult", s - t + tick(P["ctl_p"]))
        xa = me.pos(b)[0]
        c.at("r_blink", b, xa, gy, sheet=big)
        me.moves.append((b, b + 1, xa, d.pos(b)[0] - REACH))
        c.on_foe("r_pin", b, until=b + tick(P["r_sup"]))
        c.at("r_crash", s, d.pos(s)[0], gy, sheet=big, under=True)
        d.flinches.append(s)
        return s

    def walk(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    for step_ in steps:
        if step_ == "walk_in":
            walk(far - 36)
        elif step_ == "attack":          # two blows
            blow()
            blow()
        elif step_ == "q":               # the sweep, the step, the empowered cleave
            sweep()
            blow()
            c.wait(300)
        elif step_ == "q_q2":            # the sweep, the step, the slam at once (Q -> Q2), its step, the cleave
            sweep()
            slam()
            blow()
            c.wait(300)
        elif step_ == "e":
            lacerate()
            c.wait(500)
        elif step_ == "w":
            repudiation()
            c.wait(500)
        elif step_ == "r_only":
            execution()
            c.wait(900)
        elif step_ == "r":               # R -> Q -> Q2, the cleave
            execution()
            sweep()
            slam()
            blow()
            c.wait(300)
        elif step_ == "kill":
            blow()
            d.death = c.t + 40
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：拖着两把龙犬刃跑", ["walk_in"], 150, 150),
          ("普攻：双刀左右开弓", ["attack"], 40, 150),
          ("技能1 暗袭：身前横扫半圈（刀尖扫到的再加伤，附加包）→ 龙犬诡步冲一步 → 下一刀强化", ["q"], 40, 150),
          ("连招 暗袭→裂斩：扫中后马上跳起双刀砸地，裂缝沿直线往前", ["q_q2"], 40, 150),
          ("技能2 血戮：甩链刀绕身一圈（减速）→ 冲一步 → 再甩一圈", ["e"], 40, 150),
          ("铁令（敌方英雄靠近时自动）：举刀格挡（护盾），格挡时挨了打砸地更狠（附加包）", ["w"], 40, 150),
          ("大招 公开处刑：闪到敌人身边，按住压制，再砸进地里", ["r_only"], 70, 160),
          ("连招 公开处刑→暗袭→裂斩：砸下后马上横扫，再砸地", ["r"], 70, 160)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        showcase(path, z=z, steps=steps, W=220, H=h, gap=gap, tail=900)
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
    sample = Image.new("RGB", (W, H * 6))
    for i, (img, _) in enumerate(out_frames[::max(1, len(out_frames) // 6)][:6]):
        sample.paste(img, (0, i * H))
    pal = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [img.quantize(palette=pal, dither=Image.Dither.NONE) for img, _ in out_frames]
    q[0].save(out, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in out_frames], loop=0)
    return len(q), round(sum(ms for _, ms in out_frames) / 1000, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase", "skills"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_ambessa_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_ambessa_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_ambessa_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_ambessa_skills.gif")))


if __name__ == "__main__":
    main()
