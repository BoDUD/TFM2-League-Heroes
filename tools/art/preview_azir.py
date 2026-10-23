#!/usr/bin/env python3
"""Preview images for Azir, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_azir.py [--out docs/preview] [--only frames|effects|showcase]
    python tools/art/preview_azir.py --skills out.gif

  league_azir_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_azir_effects.png   every effect animation, 3x (his effects, the soldier's, the guards', the Sun Disc's sheets)
  league_azir_showcase.gif  a scripted fight against Darius in the mid lane, timed like the kit (tools/kit/build_azir.py,
                            60 ticks a second): two attacks - a sand soldier rises in front of him and stabs for him
                            (the sand spear on Darius); Conquering Sands - the sand rush through Darius (the quicksand),
                            the soldier moved to his spot rising there and stabbing at once (Q -> stab); Shifting Sands
                            - the sand shield, the dash onto him, the geyser, one more soldier (E -> a soldier); at once
                            Emperor's Divide pushing back (E -> R): Azir steps behind him and the guards' wall charges back
                            toward where Azir came from, knocking Darius away (the guards facing left: the add-on's tags);
                            he falls; 3x.
  --skills out.gif          (not in docs/) every skill on its own against Darius, one titled segment each (SKILLS), 4x:
                            the attack and its soldier, Q, E's dash, E's hop away from a diver, R pushing out (正推),
                            E -> R pushing back (反推), the Sun Disc (the add-on) - the user, 2026-10-23: 「带技能特效的gif图
                            给我看看」.
Every picture goes on its view's layer in the kit (z below 0 under the units, else over them, a higher z on top): the
soldiers stand over the units, so the ones moved onto Darius stand in front of him, as in the game.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_gnar import Clip  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_azir import P, build  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_azir")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_azir_fx", "league_azir_big")}
SUMMONS = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_azir_soldier", "league_azir_guard", "league_azir_disc")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
KIT = build(P)
Z = {v["tag"]: v["z"] for v in KIT["view_effects"] + KIT["view_projectiles"]}   # a picture's layer in the game
RISE_TICKS = 34                 # addons/league_azir/src/lib.rs: the Sun Disc's stamps and rays start after its rise
FONTS = ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf")   # --skills' titles in Chinese when one is here
SKILLS = [   # --skills: each segment's title (Chinese, English)
    ("① 普攻 · 沙兵现身：普攻在他身前召出沙兵，沙兵替他刺",
     "1 attack, Arise!: a soldier rises in front of him and stabs for him"),
    ("② 狂沙猛攻（Q）：沙浪穿过、流沙减速，沙兵移到敌人身上马上刺",
     "2 Conquering Sands: the rush, the slow, the soldier onto him stabbing at once"),
    ("③ 流沙移形（E）：沙盾，冲到敌人身上，脚下沙柱，多一个沙兵",
     "3 Shifting Sands: the shield, the dash, the geyser, one more soldier"),
    ("④ 流沙移形（E）被贴身时：沙盾，往后跳开",
     "4 Shifting Sands with a diver on him: the shield, a hop back"),
    ("⑤ 禁军之墙（R）正推：禁军从他身边冲出，把扑上来的人推远",
     "5 Emperor's Divide pushing out: the guards shove the diver away"),
    ("⑥ E → R 反推：冲到身上、绕到身后，禁军把人推回己方",
     "6 E -> R pushing back: he steps behind him, the guards shove him back"),
    ("⑦ 太阳圆盘（附加包）：倒下的我方塔旁升起，每秒一道太阳光束",
     "7 the Sun Disc (add-on): on a fallen tower's ruin, a solar ray a second"),
]


class Him(Me):
    """preview_pyke's Me on whole game pixels (his dash and his step behind move him between them)."""

    def pos(self, t):
        x, y = super().pos(t)
        return int(round(x)), int(round(y))


class Azir(Clip):
    """preview_gnar's clip at zoom z with his own dense frames (turned round after he steps behind Darius), his summons
    and his skills, each played from the clip's time against Darius where he stands then, timed like the kit."""

    def __init__(self, *a, z=3):
        super().__init__(*a)
        self.z, self.flip_from = z, None
        self.soldier, self.guard, self.disc = (load(SUMMONS[f"league_azir_{n}"]) for n in ("soldier", "guard", "disc"))

    def a(self, tag, dur=None, loop=False, z=None):
        fr = list(dense(self.sp, tag, "azir", z or self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        flip = self.flip_from is not None and self.t >= self.flip_from
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None, flip=flip)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def put(self, an, tag):
        """An effect on its picture's layer in the kit: under the units below z 0, else over them above lower z."""
        an.z = Z[tag]
        if an.z < 0:
            self.under.append(an)
            return an
        k = len(self.over)
        while k and self.over[k - 1].z > an.z:
            k -= 1
        self.over.insert(k, an)
        return an

    def on(self, tag, when, sheet=None, until=None):
        return self.put(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until), tag)

    def on_me(self, tag, when, sheet=None, until=None):
        return self.put(OnMe(frames_of(sheet or self.small, tag), when, self.me, until=until), tag)

    def fly(self, tag, t0, t1, x0, x1, y):
        return self.put(Anim(frames_of(self.small, tag), t0, x0, y, loop=True, until=t1, x1=x1, y1=y), tag)

    def at(self, tag, when, x, y, sheet=None, until=None):
        """An effect picture on a fixed spot."""
        return self.put(Anim(frames_of(sheet or self.small, tag), when, x, y, loop=until is not None, until=until), tag)

    def on_ground(self, tag, when, sheet=None, until=None):
        """A picture on the ground under Darius (under the units)."""
        self.under.append(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until))

    def stand(self, slot, when, x, y, until):
        """A soldier rising on (x, y) at `when`, then standing until `until` (the sheet's dense frames): the standing one."""
        rise = dense(self.soldier, f"soldier_{slot}_rise", "azir", self.z)
        stand = dense(self.soldier, f"soldier_{slot}", "azir", self.z)
        end = when + sum(ms for _, ms in rise)
        self.put(Anim(rise, when, x, y), f"soldier_{slot}_rise")
        return self.put(Anim(stand, end, x, y, loop=True, until=until), f"soldier_{slot}")

    def guards(self, when, x, y, left):
        """R's wall: the guards' hops (r_stamps of them, each its step's picture) from (x, y), the dust under them."""
        side = "l" if left else "r"
        hop = P["r_len"] // P["r_stamps"] / 1000.0
        ms = tick(P["r_len"] // P["r_stamps"] // P["r_speed"])
        for i in range(1, P["r_stamps"] + 1):
            tag = f"charge_{side}_{'ab'[i % 2]}"
            hx = x + (-hop if left else hop) * i
            t = when + ms * i
            self.put(Anim(dense(self.guard, tag, "azir", self.z), t, int(round(hx)), y, loop=True, until=t + ms), tag)
            self.at("r_dust", t, int(round(hx)), y)

    def where(self):
        """The clip's time, his x, Darius' x, the units' row."""
        return self.t, self.me.pos(self.t)[0], self.d.pos(self.t)[0], self.me.y

    def attack(self, sx=None):
        """An attack; with sx, the soldier it raises there first (Arise!: the hidden bolt's stop s_place ahead of him),
        returned standing. The soldiers stab Darius at the release (the sand spear on him)."""
        t, _, _, y = self.where()
        self.a("attack", tick(P["atk_dur"]))
        soldier = None
        if sx is not None:
            rose = t + (P["s_place"] / P["s_speed"]) * 1000 / 60
            self.at("s_spawn", rose, int(sx), y)
            soldier = self.stand("a", rose, int(sx), y, until=None)
        stab = t + tick(P["a_rel"] - 1)
        self.on("s_stab", stab)
        self.d.flinches.append(stab)
        self.wait(tick(P["atk_cd"] - P["atk_dur"]))
        return soldier

    def q(self, old, until=None):
        """Conquering Sands at Darius: the sand rush through him (his slow), the standing soldier `old` gone at its next
        checkpoint and one rising on his spot, stabbing at once (Q -> stab), standing until `until`."""
        t, x, far, y = self.where()
        self.a("skill", tick(P["q_dur"]))
        rel = t + tick(P["q_rel"] - 1)
        reach = rel + (far - x - 8) / px_ms(P["q_speed"])
        self.fly("q_wave", rel, reach + 80, x + 8, far + 8, y - 11)
        self.on("q_hit", reach)
        self.on_ground("slow", reach, until=reach + tick(P["q_slow_t"]))
        self.d.flinches.append(reach)
        land = rel + tick(3 + P["q_travel"])                # the controller's next run, then the lob
        old.until = land                                    # the old soldier stops at its next checkpoint
        self.at("q_land", land, far, y)
        self.stand("a", land, far, y, until=until)
        self.on("s_stab", land + tick(2))
        self.d.flinches.append(land + tick(2))

    def e_dash(self, until=None):
        """Shifting Sands onto Darius (his ult ready): the sand shell, the dash, the geyser, the hit, one more soldier on
        his spot (E -> a soldier) standing until `until`."""
        t, x, far, y = self.where()
        self.a("skill2", tick(P["e_dur"]))
        self.on_me("e_shield", t, until=t + tick(P["e_t"]))
        dash0 = t + tick(P["e_go_at"] - 1)
        stop = far - 12
        dash1 = dash0 + (stop - x) / px_ms(P["e_speed"])
        self.me.moves.append((dash0, dash1, x, stop))
        self.on_me("e_land", dash1)
        self.on("e_hit", dash1)
        self.d.flinches.append(dash1)
        self.stand("b", dash1 + tick(4), far, y, until=until)
        self.wait(max(0, int(dash1) + 60 - self.t))

    def e_hop(self):
        """Shifting Sands with Darius on him (within e_self): the sand shell and the hop back (MoveBack, away from him)."""
        t, x, _, _ = self.where()
        self.a("skill2", tick(P["e_dur"]))
        self.on_me("e_shield", t, until=t + tick(P["e_t"]))
        back = P["e_back"] * P["e_back_t"] / 1000.0
        self.me.moves.append((t + tick(1), t + tick(1 + P["e_back_t"]), x, x - back))

    def r(self, back=False):
        """Emperor's Divide at Darius: with `back` (E just landed on him: 反推) he first steps behind him and the guards
        charge back the way he came, else they charge out from him (正推); the sand wall under him, the slam, the
        knockback away from him. The slam's time."""
        t, x, far, y = self.where()
        if back:
            rush0 = t + tick(P["r_rush_at"] - 1)
            behind = far + 15
            self.me.moves.append((rush0, rush0 + (behind - x) / px_ms(P["r_rush"]), x, behind))
            self.flip_from = t
            x = behind
        self.a("ult", tick(P["r_dur"]))
        wall = t + tick(P["r_at"] - 1)
        self.on_me("r_rise", wall, sheet=self.big)
        left = far < x
        self.guards(wall, x, y, left=left)
        hit = wall + tick(max(1, abs(far - x) // (P["r_speed"] // 1000)))
        self.on("r_hit", hit)
        self.d.flinches.append(hit)
        kb = P["r_kb_speed"] * P["r_kb"] / 1000.0
        self.d.slides.append((hit, hit + tick(P["r_kb"]), -kb if left else kb))
        return hit

    def sun_disc(self, x, rays, stay=0):
        """The Sun Disc (the add-on's league_azir:disc) rising on the ruin at x: its burst and rise, then the disc and the
        ring at its foot stamped every s_step, a solar ray on Darius every d_per - `rays` of them, the disc standing `stay`
        ms more (it stands d_life in the game). Its end."""
        t, _, _, y = self.where()
        up = t + tick(RISE_TICKS)
        end = up + tick(P["d_per"]) * rays + stay
        self.at("d_rise", t, x, y, sheet=self.big)
        self.put(Anim(dense(self.disc, "disc_rise", "azir", self.z), t, x, y), "disc_rise")
        self.put(Anim(dense(self.disc, "disc", "azir", self.z), up, x, y, loop=True, until=end), "disc")
        self.at("d_glow", up, x, y, until=end)
        for k in range(rays):
            ray = up + tick(P["d_per"]) * k
            self.on("d_beam", ray, sheet=self.big)
            self.d.flinches.append(ray)
        return end

    def shots(self, W, H, end, step=40):
        """preview_gnar's Clip.render frames (RGB, at the clip's zoom) up to `end`, not written."""
        z = self.z
        frames, tt = [], 0.0
        while tt < end:
            img = Image.new("RGBA", (W * z, H * z), ARENA)
            for an in self.under:
                f = an.frame(tt)
                if f is not None:
                    put(img, f, *an.pos(tt), z)
            units = [(self.d.y, self.d.frame(tt), self.d.pos(tt))]
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
        return frames


def px_ms(speed):
    """A projectile's speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_azir_fx"], fx["league_azir_big"]
    W, H = 300, 140
    gy = 112
    x0 = 90
    d = Foe(load(DARIUS), x0 + 50, gy)                   # in his attack's reach (52.5 game px)
    c = Azir(load(CHAMP), d, Him(x0, gy), small, big, z=z)
    c.wait(400)
    end_all = 12000
    soldier = c.attack(x0 + P["s_place"] / 1000.0)      # two attacks: the first raises a soldier, both stab Darius
    c.attack()
    c.q(soldier, until=end_all)
    c.wait(500)
    c.e_dash(until=end_all)
    hit = c.r(back=True)                                # at once (E -> R): he steps behind Darius, the wall pushes back
    d.death = hit + tick(P["r_kb"]) + 500
    end = d.death + 1600
    c.wait(end - c.t)
    return c.render(out, W, H, end, z)


def skills(out, z=4, step=40):
    """Every skill on its own against Darius (SKILLS: one titled segment each), its pictures as the kit plays them."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_azir_fx"], fx["league_azir_big"]
    champ, darius = load(CHAMP), load(DARIUS)
    W, H, gy = 220, 110, 80
    ahead = P["s_place"] / 1000.0

    def scene(x0, dx, soldier=False):
        """Azir at x0, Darius dx to his right; with `soldier`, one an earlier attack raised stands in front of him (E
        needs one, Q moves it)."""
        c = Azir(champ, Foe(darius, x0 + dx, gy), Him(x0, gy), small, big, z=z)
        return c, (c.stand("a", -1500, int(x0 + ahead), gy, until=None) if soldier else None)

    clips = []
    c, _ = scene(70, 50)
    c.wait(400)
    c.attack(70 + ahead)
    c.attack()
    c.wait(500)
    clips.append(c)
    c, old = scene(60, 60, soldier=True)
    c.wait(500)
    c.q(old)
    c.wait(1400)
    clips.append(c)
    c, _ = scene(60, 55, soldier=True)
    c.wait(500)
    c.e_dash()
    c.wait(1300)
    clips.append(c)
    c, _ = scene(100, 20, soldier=True)                 # Darius swinging at him
    c.d.attacks += [150, 850]
    c.wait(1150)
    c.e_hop()
    c.wait(1300)
    clips.append(c)
    c, _ = scene(70, 22)
    c.d.attacks += [150, 850]
    c.wait(1150)
    c.r()
    c.wait(1300)
    clips.append(c)
    c, _ = scene(60, 55, soldier=True)
    c.wait(500)
    c.e_dash()
    c.r(back=True)
    c.wait(1500)
    clips.append(c)
    c, _ = scene(55, 80)                                # the ruin 40 px from him (d_near 60), Darius 40 from it (d_range 45)
    c.wait(400)
    c.wait(c.sun_disc(95, 3, stay=700) - c.t)
    clips.append(c)

    font = next((ImageFont.truetype(f, 20) for f in FONTS if os.path.exists(f)), None)
    bar_h = 34
    frames = []
    for (zh, en), c in zip(SKILLS, clips):
        bar = Image.new("RGB", (W * z, bar_h), (40, 40, 40))
        ImageDraw.Draw(bar).text((8, 5), zh if font else en, fill=(235, 235, 235), font=font)
        for f in c.shots(W, H, c.t, step):
            full = Image.new("RGB", (W * z, H * z + bar_h))
            full.paste(bar, (0, 0))
            full.paste(f, (0, bar_h))
            frames.append(full)
    sample = frames[::12]
    strip = Image.new("RGB", (W * z, (H * z + bar_h) * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * (H * z + bar_h)))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q_ = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q_[0].save(T.long_path(out), save_all=True, append_images=q_[1:], duration=step, loop=0)
    return len(frames), round(len(frames) * step / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    ap.add_argument("--skills", help="write only the per-skill GIF, here")
    args = ap.parse_args()
    if args.skills:
        print("skills frames/seconds", skills(args.skills))
        return
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_azir_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in {**FX, **SUMMONS}.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags if not t["name"].startswith("hd_")]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_azir_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_azir_showcase.gif")))


if __name__ == "__main__":
    main()
