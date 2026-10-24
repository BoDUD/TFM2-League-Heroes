#!/usr/bin/env python3
"""Preview images for Taliyah, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_taliyah.py [--out docs/preview] [--only frames|effects|showcase]

  league_taliyah_frames.png    every animation's dense frames (hd_, PPU 1.75, as league.dll shows them)
  league_taliyah_effects.png   every effect animation, 3x
  league_taliyah_showcase.gif  a scripted fight with Syndra, timed like the kit (tools/kit/build_taliyah.py, 60 ticks a
                               second): Taliyah surfs in on her boulder (the surf's dust: out of a fight she surfs),
                               flicks a pebble, throws Threaded Volley - five rocks, the Worked Ground left under her -
                               then Seismic Shove with Unraveled Earth: the mines strewn under Syndra, the ground
                               erupting, Syndra thrown toward her through the mines, which blow up and stun her (W -> E);
                               Weaver's Wall rises where Syndra stands (she is dragged out to Taliyah's side) and at once a
                               second Shove throws her back into it - stunned against the wall (R -> W), Taliyah surfing
                               on the wall's speed; Threaded Volley again, standing on her Worked Ground: the boulder and
                               its slow (Q on Worked Ground); two pebbles finish Syndra; 3x.
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
from preview_pyke import Me, OnFoe  # noqa: E402
from build_taliyah import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_taliyah")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_taliyah_fx", "league_taliyah_big")}
SYNDRA = os.path.join(LEAGUE, "champions", "league_syndra")


class Taliyah(Clip):
    """preview_gnar's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "taliyah", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def fly(self, tag, t0, t1, x0, x1, y0, y1=None, sheet=None):
        """A projectile's picture flying from (x0, y0) to (x1, y1) (drawn flying right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y0, loop=True, until=t1, x1=x1,
                              y1=y0 if y1 is None else y1, flip=x1 < x0))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: the worked ground, the mines, the wall)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


FIGHT = ["surf_in", "attack", "q", "shove", "wall", "boulder", "kill"]


def showcase(out, z=3, steps=FIGHT, W=250, H=170, gap=130, tail=1400):
    """The scripted fight (or some of its steps: skills() plays each skill alone) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_taliyah_fx"], fx["league_taliyah_big"]
    gy = 90
    x0 = 30
    far = x0 + gap                                      # Syndra
    d = Foe(load(SYNDRA), far, gy)
    me = Me(x0, gy)
    c = Taliyah(load(CHAMP), d, me, small, big)
    c.wait(300)

    def run(x1, surf=True):
        """She surfs to x1 (the surf's dust under her while she is out of a fight or on the wall's speed)."""
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"] * (100 + P["p_ms"]) / 100)
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))
        if surf:
            c.on_me("surf", t0, until=t1, under=True)
        return t1

    def hand(t):
        x, _ = me.pos(t)
        return x + 8, gy - 22

    def pebble(when):
        """The attack: a pebble flicked at a_rel, homing on Syndra."""
        rel = when + tick(P["a_rel"] - 1)
        hx, hy = hand(rel)
        lands = rel + abs(d.pos(rel)[0] - hx) / px_ms(P["a_speed"])
        c.fly("a_rock", rel, lands, hx, d.pos(lands)[0], hy, gy - 16)
        c.on("a_hit", lands)
        d.flinches.append(lands)

    def volley(when, boulder=False):
        """Threaded Volley at q_rel: five rocks q_gap apart (or, on Worked Ground, one boulder that slows)."""
        rel = when + tick(P["q_rel"] - 1)
        hx, hy = hand(rel)
        if boulder:
            lands = rel + abs(d.pos(rel)[0] - hx) / px_ms(P["q_b_speed"])
            c.fly("q_boulder", rel, lands + 200, hx, d.pos(lands)[0] + 40, gy - 10)
            c.on("q_big_hit", lands)
            c.on("slow", lands, until=lands + tick(P["q_b_slow_t"]))
            d.flinches.append(lands)
            return lands
        for k in range(P["q_n"]):
            t = rel + tick(k * P["q_gap"])
            lands = t + abs(d.pos(t)[0] - hx) / px_ms(P["q_speed"])
            c.fly("q_rock", t, lands, hx, d.pos(lands)[0], hy, gy - 14)
            c.on("q_hit", lands)
            d.flinches.append(lands)
        c.at("q_ground", rel, me.pos(rel)[0], gy, sheet=big, under=True, until=rel + tick(P["q_gt"]))
        return rel

    def shove(when, into_wall=None):
        """Seismic Shove with Unraveled Earth: the mark thrown at w_rel, the eruption w_delay later where Syndra
        stands - the mines strewn there, Syndra thrown toward Taliyah through them and stunned as they blow up; with
        the wall standing she is shoved away from Taliyah into it and stunned against it."""
        c.a("skill2", tick(P["w_dur"]))
        erupt = when + tick(P["w_rel"] - 1 + P["w_delay"])
        x = d.pos(erupt)[0]
        c.at("e_mines", erupt, x, gy, sheet=big, under=True, until=erupt + tick(P["e_t"]))
        c.at("w_erupt", erupt, x, gy, sheet=big)
        c.on("w_hit", erupt)
        if into_wall is None:
            back = -P["w_go"] * P["w_throw"] / 1000.0
            d.slides.append((erupt, erupt + tick(P["w_throw"]), back))
            d.hops.append((erupt, erupt + tick(P["w_throw"]), 6))
            stun = erupt + tick(P["w_throw"])
            c.on("e_blast", stun, until=stun + tick(P["e_stun"]))
        else:
            d.slides.append((erupt, erupt + tick(P["r_kb"]), into_wall - x))
            stun = erupt + tick(P["r_kb"])
            c.on("e_blast", stun, until=stun + tick(P["r_wstun"]))
        d.flinches.append(erupt)
        return stun

    state = {}
    for step in steps:
        if step == "surf_in":           # in on her boulder, out of a fight: the surf's speed and dust
            run(x0 + 50)
        elif step == "attack":          # a pebble
            t = c.t
            c.a("attack", tick(P["atk_dur"]))
            pebble(t)
        elif step == "q":               # Threaded Volley: five rocks, the Worked Ground under her
            t = c.t
            c.a("skill", tick(P["q_dur"]))
            volley(t)
        elif step == "shove":           # Seismic Shove + Unraveled Earth: thrown through the mines - stunned (W -> E)
            t = c.t
            shove(t)
            c.wait(tick(P["w_delay"] + P["w_throw"] + P["e_stun"]) - tick(P["w_dur"]) + 100)
        elif step == "wall":            # Weaver's Wall where Syndra stands (r_rel): dragged out to Taliyah's side; the
            t = c.t                     # second Shove at once throws her back into it (R -> W), stunned against it
            c.a("ult", tick(P["r_dur"]))
            rise = t + tick(P["r_rel"] - 1)
            wall_x = d.pos(rise)[0]
            c.at("r_wall", rise, wall_x, gy, sheet=big, under=True, until=rise + tick(P["r_t"]))
            out_ = P["r_w"] / 2000.0 + 2                # dragged out of the wall's band (r_w wide)
            d.slides.append((rise, rise + tick(4), -out_))
            c.on_me("surf", rise, until=rise + tick(P["r_surf"]), under=True)
            w2 = rise + tick(P["r_w_at"])
            c.t = max(c.t, w2)
            state["stun"] = shove(w2, into_wall=wall_x - 4)
        elif step == "boulder":         # Threaded Volley on her Worked Ground: the boulder and its slow
            if "stun" in state:
                c.t = max(c.t, state["stun"] - tick(P["q_rel"]))
            t = c.t
            c.a("skill", tick(P["q_dur"]))
            volley(t, boulder=True)
        elif step == "kill":            # two pebbles finish her
            for _ in range(2):
                t = c.t
                c.a("attack", tick(P["atk_dur"]))
                pebble(t)
            d.death = c.t + 120
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase", "skills"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_taliyah_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_taliyah_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_taliyah_showcase.gif")))
    if args.only == "skills":
        print("skills", skills(os.path.join(args.out, "league_taliyah_skills.gif")))


# each skill alone (the user, 2026-10-24: 「带技能的gif图给我看下」): (caption, steps, Syndra's distance, canvas height)
SCENES = [("移动：踩石冲浪（脱战加速，石头下面扬沙）", ["surf_in"], 130, 170),
          ("普攻：甩出一块小石子", ["attack"], 60, 170),
          ("技能1 石穿：连射五颗石头，脚下留下掘石场", ["q"], 80, 170),
          ("连招：站在掘石场上再放石穿 = 一颗大石头 + 减速", ["q", "boulder"], 80, 170),
          ("技能2 撒石阵+岩突：撒下石雷，地面隆起把人掀过雷区 = 眩晕", ["shove"], 70, 170),
          ("大招 墙幔：石墙竖起，马上接岩突把人推到墙上 = 撞墙眩晕", ["wall"], 70, 170)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        showcase(path, z=z, steps=steps, W=190, H=h, gap=gap, tail=900)
        for f in ImageSequence.Iterator(Image.open(path)):
            frames.append((cap, f.convert("RGB").copy(), f.info.get("duration", 40)))
    W = max(f.width for _, f, _ in frames)
    H = max(f.height for _, f, _ in frames) + 26
    out_frames = []
    for cap, f, ms in frames:
        img = Image.new("RGB", (W, H), (40, 40, 40))
        img.paste(f, (0, 26))
        ImageDraw.Draw(img).text((6, 3), cap, fill=(240, 240, 240), font=font)
        out_frames.append((img, ms))
    sample = Image.new("RGB", (W, H * 6))
    for i, (img, _) in enumerate(out_frames[::max(1, len(out_frames) // 6)][:6]):
        sample.paste(img, (0, i * H))
    pal = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [img.quantize(palette=pal, dither=Image.Dither.NONE) for img, _ in out_frames]
    q[0].save(out, save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in out_frames], loop=0)
    return len(q), round(sum(ms for _, ms in out_frames) / 1000, 1)


if __name__ == "__main__":
    main()
