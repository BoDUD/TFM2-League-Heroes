#!/usr/bin/env python3
"""Preview images for Norra (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_norra.py [--out docs/preview] [--only frames|effects|skills]

  tft_norra_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_norra_effects.png   every effect animation, 3x
  tft_norra_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_norra.py,
                          60 ticks a second), captioned in Chinese, 4x (the user, 2026-10-24: 「带技能的gif图呢？」): the
                          walk; the star bolt; Memory Surge (the gathering, the bolt flung and her recoil, the blast, the
                          Threads); Threads of Homecoming (the two portals, the threads crossing, the Threads); and the
                          tft.dll's (addons/tft/src/norra.rs): the trinkets scattered one by one and taken by whoever steps on
                          them, Journey to Nowhere on whoever comes close, Portalpalooza!'s yarn balls along their lines.
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
from preview_gnar import Clip  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe  # noqa: E402
import preview_zoe as Z  # noqa: E402
from build_norra import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_norra")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_norra_fx", "tft_norra_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
HAND = -16                     # her bolts leave her pointing hand at about her shoulder (game px over the pivot)
TRINKET_DX = 40                # the add-on's trinkets: this many game px to each side of the landing point
BALL_TICKS = 16                # tft.dll's yarn ball crossing the rift (norra.rs BALL_TICKS)
WALK = 0.06                    # Darius's walk, game px a ms


class Darius(Foe):
    """preview_leesin's Darius, who also walks (left when dx < 0: towards her) and can be banished (out of sight)."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.walks, self.gone = [], []                 # (t0, t1, dx), (t0, t1)

    def pos(self, t):
        x, y = super().pos(t)
        for t0, t1, dx in self.walks:
            if t >= t0:
                x += dx * min(1.0, (t - t0) / (t1 - t0))
        return int(round(x)), y

    def frame(self, t):
        if any(t0 <= t < t1 for t0, t1 in self.gone):
            return None
        for t0, t1, dx in self.walks:
            if t0 <= t < t1:
                f = self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
                return self.flip(f) if dx < 0 else f
        return super().frame(t)


class Norra(Clip):
    """preview_gnar's clip with her own dense frames at the clip's zoom."""

    z = 3

    def a(self, tag, dur=None, loop=False, z=None):
        fr = list(dense(self.sp, tag, "norra", z or self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Darius (the Threads round him, the yarn round his feet)."""
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: a trinket, the rift, the portals); looped to
        `until`."""
        fr = frames_of(sheet or self.small, tag)
        (self.under if under else self.over).append(Anim(fr, when, x, y, loop=until is not None, until=until))

    def fly_left(self, tag, t0, t1, x0, x1, y):
        """A projectile flying left: its picture turned with its flight (the game turns them; drawn flying right)."""
        fr = []
        for f, ms in frames_of(self.small, tag):
            g = f.transpose(Image.ROTATE_180)
            g.info.update(f.info)
            fr.append((g, ms))
        self.over.append(Anim(fr, t0, x0, y, loop=True, until=t1, x1=x1, y1=y))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def play(out, steps, z=4, W=250, H=150, gap=80, tail=900):
    """Some of her moves against Darius, `gap` game px away, written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_norra_fx"], fx["tft_norra_big"]
    gy = H - 30
    x0 = 40
    d = Darius(load(DARIUS), x0 + gap, gy)
    me = Me(x0, gy)
    c = Norra(load(CHAMP), d, me, small, big)
    c.z = z
    c.wait(300)

    def bolt():
        """The attack: the finger pointed, the star bolt off it (a_rel), its hit."""
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        rel = t + tick(P["a_rel"] - 1)
        xa, xb = me.pos(rel)[0] + 9, d.pos(rel)[0]
        land = rel + abs(xb - xa) / px_ms(P["a_speed"])
        c.fly("a_bolt", rel, land, xa, xb, gy + HAND)
        c.on("a_hit", land)
        d.flinches.append(land)

    def surge():
        """Memory Surge: gathered, the bolt flung at where he stood (q_travel) as she recoils (MoveBack), the blast on
        the ground, the hit and the Threads the tick after. -> (the landing, where)."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        rel = t + tick(P["q_rel"] - 1)
        land = rel + tick(P["q_travel"])
        xs, xl = me.pos(rel)[0], d.pos(rel)[0]
        c.fly("q_bolt", rel, land, xs + 8, xl, gy + HAND)
        hop = P["q_hop"] * P["q_hop_t"] / 1000.0
        me.moves.append((rel, rel + tick(P["q_hop_t"]), xs, xs - hop))
        c.at("q_blast", land, xl, gy, sheet=big)
        hit = land + tick(1)
        c.on("q_hit", hit)
        d.flinches.append(hit)
        c.on_foe("t_mark", hit, until=hit + tick(P["t_t"]))
        return land, xl

    def weave():
        """Threads of Homecoming: the two portals at his sides as the lob leaves (e_rel), the threads crossing when it
        lands (e_delay), his hit and the Threads."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        rel = t + tick(P["e_rel"] - 1)
        c.at("e_threads", rel, d.pos(rel)[0], gy, sheet=big)
        hit = rel + tick(P["e_delay"] + 1)
        c.on("t_hit", hit)
        d.flinches.append(hit)
        c.on_foe("t_mark", hit, until=hit + tick(P["t_t"]))

    def walk(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    for step in steps:
        if step == "walk_in":
            walk(d.x - 30)
        elif step == "attack":
            bolt()
            c.wait(350)
            bolt()
        elif step == "q":
            surge()
            c.wait(500)
        elif step == "e":
            weave()
            c.wait(600)
        elif step == "trinkets":        # the add-on's: a Q with the trinkets ready scatters three; he stands on the
            land, xl = surge()          # middle one (taken at once: the add-on looks the tick after), walks onto the
            mid = land + tick(1)        # right one, then back across onto the left one
            near = TRINKET_DX - P["p_tr"] / 1000.0                  # how far into a gap a trinket reaches him
            w1 = land + 900
            d.walks.append((w1, w1 + 600, 30))
            right = w1 + 600 * near / 30
            w2 = w1 + 900
            d.walks.append((w2, w2 + 1000, -50))
            left = w2 + 1000 * (30 + near) / 50
            for side, dx, until in (("l", -TRINKET_DX, left), ("c", 0, mid), ("r", TRINKET_DX, right)):
                c.at(f"p_trinket_{side}", land, xl + dx, gy, under=True, until=until)
            for tb in (mid, right, left):
                c.on("p_burst", tb)
                d.flinches.append(tb)
            c.wait(left + 900 - c.t)
        elif step == "journey":         # the add-on's: he walks up to her; within w_r the portal opens under him, out of
            xd, xm = d.pos(c.t)[0], me.pos(c.t)[0]                  # sight w_t ticks, spat out and slowed
            reach = xm + P["w_r"] / 1000.0
            t0 = c.t + 200
            t1 = t0 + (xd - reach) / WALK
            d.walks.append((t0, t1, -(xd - reach)))
            c.at("w_in", t1, reach, gy)
            c.at("w_lock", t1, reach, gy)
            back = t1 + tick(P["w_t"])
            d.gone.append((t1, back))
            c.at("w_out", back, reach, gy)
            c.wait(back + 300 - c.t)
            bolt()
            c.wait(300)
        elif step == "r":               # the add-on's: the rift on his spot (r_r), four volleys r_gap apart, a yarn ball
            t = c.t                     # from each end along the line through him; his hit once a volley; slowed
            c.a("ult", tick(P["r_dur"]))
            rel = t + tick(P["r_rel"] - 1)
            land = rel + tick(P["r_travel"])
            xl = d.pos(rel)[0]
            k = land
            while k <= land + tick(4 * P["r_gap"]):
                c.at("r_rift", k, xl, gy, sheet=big, under=True)
                k += tick(P["r_show"])
            half = P["r_r"] / 1000.0
            for v in range(1, 5):
                tv = land + tick(P["r_gap"] * v)
                arrive = tv + tick(BALL_TICKS)
                c.fly("r_ball", tv, arrive, xl - half, xl + half, gy)
                c.fly_left("r_ball", tv, arrive, xl + half, xl - half, gy)
                hit = tv + tick(BALL_TICKS / 2)
                c.on("r_hit", hit)
                d.flinches.append(hit)
                c.on_foe("r_slow", hit, until=hit + tick(P["r_slow_t"]))
            c.wait(land + tick(4 * P["r_gap"] + BALL_TICKS) + 300 - c.t)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：小碎步，耳朵往后飘", ["walk_in"], 150, 150),
          ("普攻：指尖射出星光弹", ["attack"], 70, 150),
          ("技能1 回忆涌现：蓄力后射出回忆魔法弹并后退一步——落点爆炸，打中的英雄挂上线缕（变大、减速）", ["q"], 80, 150),
          ("技能2 思乡线缕：目标两侧开两扇门，0.3秒后线缕穿过——伤害，挂上线缕", ["e"], 80, 150),
          ("被动 寄情琐物：技能落地撒下3个琐物，敌方英雄踩到哪个，哪个就飞到他身上炸开", ["trinkets"], 80, 150),
          ("被动 奇异旅程：敌方英雄一贴身就开门，放逐1.5秒，吐回来后减速", ["journey"], 70, 150),
          ("大招 传送门欢腾！：脚下展开大裂隙，4波毛线球从两头沿线对飞，每个球碰到的第一个英雄减速", ["r"], 80, 160)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        play(path, steps, z=z, W=250, H=h, gap=gap)
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
    ap.add_argument("--only", choices=["frames", "effects", "skills"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_norra_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[10:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_norra_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_norra_skills.gif")))


if __name__ == "__main__":
    main()
