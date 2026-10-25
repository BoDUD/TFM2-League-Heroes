#!/usr/bin/env python3
"""Preview images for Rumble, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_rumble.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_rumble_frames.png    every animation's dense frames (hd_, PPU 1.75, as league.dll shows them)
  league_rumble_effects.png   every effect animation, 3x
  league_rumble_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_rumble.py, 60 ticks a
                              second): the ball's blows; Flamespitter; the Electro-Harpoon and its second shot, which
                              brings the fire at once (E2 -> Q); the heat climbing into the Danger Zone (the steam, and
                              Scrap Shield at once: DZ -> W); The Equalizer's rockets coming down in a burning line on
                              him, across or up and down as the kit picks it, bringing a harpoon (R -> E); Overheat (the
                              blowout, the mech red-hot and smoking, red-hot burning blows); 3x.
  league_rumble_skills.gif    each skill and combo alone with its effects, captioned in Chinese, 4x (memory
                              skills-gif-in-review).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from PIL import Image  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_gnar import Clip  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe  # noqa: E402
from build_rumble import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_rumble")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_rumble_fx", "league_rumble_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
GAREN = os.path.join(LEAGUE, "champions", "league_garen")
MUZZLE = 26                     # his cannon's mouth in front of him (game px) where the harpoon leaves it


class Rumble(Clip):
    """preview_gnar's clip with his own dense frames."""

    zoom = 3                    # the clip's zoom: his dense frames drawn at the same zoom as Darius and the effects

    def a(self, tag, dur=None, loop=False, z=None):
        fr = list(dense(self.sp, tag, "rumble", z or self.zoom))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Darius (the slow's crackle, the burn at his feet)."""
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: the burning line)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))

    def on_unit(self, tag, when, unit, sheet=None, until=None, under=False):
        """A picture following another enemy (the burn at Garen's feet)."""
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, unit,
                                                          until=until))

    def render(self, out, W, H, end, z=3, step=40):
        """preview_gnar's Clip.render with the other enemies (self.extra) drawn too, every unit in its row's order."""
        frames, tt = [], 0.0
        while tt < end:
            img = Image.new("RGBA", (W * z, H * z), ARENA)
            for an in self.under:
                f = an.frame(tt)
                if f is not None:
                    put(img, f, *an.pos(tt), z)
            units = [(u.y, u.frame(tt), u.pos(tt)) for u in [self.d] + self.extra]
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


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


# the fight's steps in order (showcase); skills() plays some of them alone
FIGHT = ["walk_in", "attack", "q", "e_e2_q", "dz", "r_e", "oh"]


def showcase(out, z=3, steps=FIGHT, W=300, H=150, gap=60, tail=1500, others=(), low=30):
    """The scripted fight (or some of its steps: skills() plays each skill alone) written to `out`. others: (dx, dy)
    of more enemies (Garen) from Darius; low: game px from the units' row to the canvas's bottom."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_rumble_fx"], fx["league_rumble_big"]
    gy = H - low
    x0 = 40
    far = x0 + gap                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Rumble(load(CHAMP), d, me, small, big)
    c.zoom = z
    c.extra = [Foe(load(GAREN), far + dx, gy + dy) for dx, dy in others]
    st = {"oh": -1.0}
    c.wait(300)

    def blow():
        t = c.t
        c.a("oh_attack" if t < st["oh"] else "attack", tick(P["atk_dur"]))   # Overheated: the red-hot swing
        b = t + tick(P["a_hit"] - 1)
        c.on("a_hit", b)
        if b < st["oh"]:                                # Overheated: the blow burns
            c.on("oh_hit", b + tick(1))
        d.flinches.append(b)

    def flamespitter():
        """The cannon levelled, the fire poured (drawn into his frames), a scorch on Darius each pulse."""
        t = c.t
        c.a("skill", tick(P["q_t"]))
        for k in range(P["q_n"]):
            h = t + tick(P["q_first"] + k * P["q_gap"] - 1)
            c.on("q_hit", h)
            d.flinches.append(h)
        return t

    def harpoon(second=False):
        """A harpoon shot at Darius: its flight, the jolt (the second's bigger), the slow's crackle on him."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        rel = t + tick(P["e_rel"] - 1)
        xs = me.pos(rel)[0] + MUZZLE
        land = rel + max(0, d.pos(rel)[0] - xs) / px_ms(P["e_speed"])
        c.fly("e_harpoon", rel, land, xs, d.pos(rel)[0], gy)
        c.on("e2_hit" if second else "e_hit", land)
        d.flinches.append(land)
        c.on_foe("e_zap", land, until=land + tick(P["e_slow_t"]))
        return land

    def shield(when):
        """Scrap Shield (the controller): the shell round him, the exhaust at his feet while he is faster."""
        c.on_me("w_shield", when, until=when + tick(P["w_sh_t"]))
        c.on_me("haste", when, until=when + tick(P["w_ms_t"]), under=True)

    def equalizer():
        """The rockets off his back on r_rel; the burning line laid on Darius's spot across the screen or up and down
        it, whichever holds more of the enemies (the kit's two probes, three or more counted as three; as many:
        across), the burn and a flinch each r_p on everyone standing in it. -> (the moment it is laid, the band)."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        rel = t + tick(P["r_rel"] - 1)
        c.on_me("r_launch", rel, sheet=big, under=True)          # behind him (the kit's z -1)
        land = rel + tick(2)
        cx, cy = d.pos(land)
        foes = [d] + c.extra

        def inside(ax, f):
            fx_, fy_ = f.pos(land)
            w, h = (P["r_len"], P["r_wid"]) if ax == "h" else (P["r_wid"], P["r_len"])
            return abs(fx_ - cx) <= w / 2000 + 6 and abs(fy_ - cy) <= h / 2000 + 6
        nh = min(3, sum(inside("h", f) for f in foes))
        nv = min(3, sum(inside("v", f) for f in foes))
        ax = "v" if nv > nh else "h"
        c.at(f"r_band_{ax}", land, cx, cy, sheet=big, under=True)
        t0, t1 = land + tick(P["r_bite"]), land + tick(P["r_t"])
        for f in foes:
            if inside(ax, f):
                c.on_unit("burn", t0, f, until=t1, under=True)
                k = t0
                while k < t1:
                    f.flinches.append(k)
                    k += tick(P["r_p"])
        return land, ax

    def walk(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    for step in steps:
        if step == "walk_in":
            walk(far - 30)
        elif step == "walk_w":          # walking up to Darius: Scrap Shield goes up when he is in reach (w_near)
            xa = me.pos(c.t)[0]
            near = far - P["w_near"] / 1000.0
            t_near = c.t + max(0.0, near - xa) / px_ms(P["ms"])
            walk(far - 30)
            shield(t_near)
            c.wait(900)
        elif step == "attack":          # two blows of the ball
            blow()
            blow()
            c.wait(200)
        elif step == "q":               # Flamespitter alone
            flamespitter()
            c.wait(300)
        elif step == "e":               # the Electro-Harpoon alone
            harpoon()
            c.wait(900)
        elif step == "e_e2_q":          # a harpoon through a champion opens the second; the second brings the fire
            land = harpoon()
            c.wait(max(0.0, land + tick(P["e_gap"]) - c.t))
            harpoon(True)
            flamespitter()
            c.wait(200)
        elif step == "dz":              # the heat past 50: the vent, the steam, Scrap Shield at once (DZ -> W)
            t = c.t
            c.on_me("dz_on", t)
            c.on_me("dz_steam", t + 300, until=t + 2600, under=True)          # behind him (the kit's z -1)
            shield(t + tick(P["ctl_p"]))
            blow()
            blow()
            c.wait(600)
        elif step == "r":               # The Equalizer alone (across or up and down: where the enemies stand)
            equalizer()
            c.wait(2200)
        elif step == "r_e":             # the rockets down bring a harpoon (R -> E)
            land, _ = equalizer()
            c.wait(max(0.0, land + tick(2) - c.t))
            harpoon()
            c.wait(1200)
        elif step == "oh":              # Overheat (红温): the blowout, the mech red-hot and smoking while it lasts,
            t = c.t                     # burning blows (his red-hot idle and run: the add-on's view hook)
            c.on_me("oh_on", t, sheet=big)
            st["oh"] = t + 3000
            c.on_me("oh_smoke", t + 500, until=st["oh"], under=True)          # behind him (the kit's z -1)
            c.idle = "oh_idle"
            c.wait(500)
            blow()
            blow()
            blow()
            c.wait(max(0.0, st["oh"] - c.t))
            c.idle = "idle"
            c.wait(400)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (memory skills-gif-in-review): (caption, steps, Darius's distance, canvas width, canvas height,
# Garen's (dx, dy) from Darius, the units' row from the canvas's bottom)
SCENES = [("移动：机甲迈着短腿跑", ["walk_in"], 150, 240, 150, (), 30),
          ("普攻：抡起带刺铁球砸下", ["attack"], 40, 220, 150, (), 30),
          ("技能1 纵火盛宴：端平喷火炮往前喷一大股火，烧到的每 0.25 秒一跳", ["q"], 50, 240, 150, (), 30),
          ("技能2 电子鱼叉：射出鱼叉，伤害 + 减速（他身上噼啪的电）", ["e"], 75, 240, 150, (), 30),
          ("连招 E→E2→Q：鱼叉射中英雄，再射第二发（更痛、减速更多），第二发打中马上喷火", ["e_e2_q"], 50, 240, 150, (), 30),
          ("W 破碎护盾：敌方英雄一靠近就自动套上青色护盾，脚下喷气加速", ["walk_w"], 150, 240, 150, (), 30),
          ("被动 危险地带：热量过半，两边喷出蒸汽（技能加强），破碎护盾马上套上", ["dz"], 40, 220, 150, (), 30),
          ("大招 恒温灼烧（横着放）：敌人左右站开，火箭横着砸成一条火线", ["r"], 75, 300, 170, ((34, 0),), 40),
          ("大招 恒温灼烧（竖着放）：敌人上下站开，火箭竖着砸成一条火线（先数哪边罩住的人多）", ["r"], 75, 260, 230,
           ((6, -34),), 70),
          ("连招 R→E：火箭落地，电子鱼叉马上射出", ["r_e"], 75, 260, 170, (), 40),
          ("被动 过热（红温）：热量满了，炸出火和黑烟，机甲烧得通红，几秒放不了技能，普攻带火", ["oh"], 40, 220, 160, (), 30)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, w, h, others, low) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        showcase(path, z=z, steps=steps, W=w, H=h, gap=gap, tail=900, others=others, low=low)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_rumble_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_rumble_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_rumble_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_rumble_skills.gif")))


if __name__ == "__main__":
    main()
