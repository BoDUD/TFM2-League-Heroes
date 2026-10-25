#!/usr/bin/env python3
"""Preview images for Trundle, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_trundle.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_trundle_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  league_trundle_effects.png   every effect animation, 3x
  league_trundle_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_trundle.py, 60 ticks a
                               second): club blows; Chomp (the bite, his strength over his head, Darius's weakness and
                               slow) on a champion freezes the ground at once (Q -> W: the hop, the domain, the frozen
                               patch under him); Pillar of Ice behind Darius (the add-on's terrain: Darius turns to run
                               and cannot get past it) gives Chomp back (E -> Q); Subjugate (the seizing, the shackles,
                               a drain a second, the broken shield) gives Chomp back and raises a pillar on him (R -> Q
                               + E); Darius falls on the domain: King's Tribute heals him twice as much; 3x.
  league_trundle_skills.gif    each skill and combo alone with its effects, captioned in Chinese, 4x (the user,
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
from build_trundle import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_trundle")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_trundle_fx", "league_trundle_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
# the add-on's pillar stands behind its champion: its centre e_wall + PILLAR_GAP (addons/league_trundle) past it, in px
PILLAR_DX = (P["e_wall"] + 7000) // 1000


class Trundle(Clip):
    """preview_gnar's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "trundle", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Darius (the marks over his head, the shackles, the slow at his feet)."""
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def on_him(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Trundle (his strength over his head, the frozen patch under him, the tribute)."""
        (self.under if under else self.over).append(OnMe(frames_of(sheet or self.small, tag), when, self.me,
                                                         until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: the domain, the pillar, the hop's ring)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


# the fight's steps in order (showcase); skills() plays some of them alone
FIGHT = ["walk_in", "attack", "q_w", "e_q", "r", "kill"]


def showcase(out, z=3, steps=FIGHT, W=320, H=150, gap=150, tail=1500, w_ready=True):
    """The scripted fight (or some of its steps: skills() plays each skill alone) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_trundle_fx"], fx["league_trundle_big"]
    gy = H - 30
    x0 = 40
    far = x0 + gap                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Trundle(load(CHAMP), d, me, small, big)
    st = {"w_ready": w_ready, "domain": -1.0}
    c.wait(300)

    def blow():
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        b = t + tick(P["a_hit"] - 1)
        c.on("a_hit", b)
        d.flinches.append(b)

    def domain():
        """The Frozen Domain (the passive's hop after a bite on a champion): the frost ring, the ground freezing over
        where he stands, the frozen patch under him while it lasts."""
        t = c.t
        c.a("w", tick(P["w_dur"]))
        x = me.pos(t)[0]
        c.at("w_hop", t + tick(P["w_dur"] - 2), x, gy, under=True)
        c.at("w_domain", t, x, gy, sheet=big, under=True)
        c.on_him("w_aura", t + 800, until=t + tick(P["w_t"]), under=True)
        st["domain"] = t + tick(P["w_t"])
        st["w_ready"] = False

    def chomp():
        """Chomp: the bite, the slow and the weakness on Darius, his strength over his head; on a champion with W ready
        the domain at once (Q -> W)."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        h = t + tick(P["q_hit"] - 1)
        c.on("q_hit", h)
        d.flinches.append(h)
        c.on_foe("slow", h, until=h + tick(max(P["q_slow_t"], 30)), under=True)
        c.on_foe("q_sap", h, until=h + tick(P["q_t"]))
        c.on_him("q_buff", h, until=h + tick(P["q_t"]))
        if st["w_ready"]:
            domain()

    def pillar(when, run=True):
        """Pillar of Ice behind Darius (the add-on's terrain): rising, standing e_t ticks; the spikes at his feet and the
        slow; he turns to run off and cannot get past it."""
        x = d.pos(when)[0] + PILLAR_DX
        c.at("e_pillar", when, x, gy, sheet=big)
        c.on("e_hit", when + tick(1))
        c.on_foe("slow", when, until=when + tick(P["e_t"]), under=True)
        if run:
            d.runs.append((when + 250, when + 1150))   # running at the pillar: going nowhere

    def raise_pillar():
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        pillar(t + tick(P["e_rel"] - 1))

    def subjugate():
        """Subjugate: the seizing, the shackles while it drains, a drain each r_p ticks, the broken shield; Q back and a
        pillar on him (R -> Q + E)."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        g = t + tick(P["r_rel"] - 1)
        c.on("r_hit", g)
        d.flinches.append(g)
        end = g + tick(P["r_t"])
        c.on_foe("r_chain", g + 300, until=end)
        k = g + tick(P["r_p"])
        while k <= end:
            c.on("r_tick", k)
            k += tick(P["r_p"])
        c.on_foe("r_sap", g, until=end + tick(P["r_keep"]))
        pillar(g + tick(1), run=False)
        return g

    def walk(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    for step in steps:
        if step == "walk_in":
            walk(far - 40)
        elif step == "attack":          # two club blows
            blow()
            blow()
        elif step == "q":               # Chomp alone (W cooling)
            chomp()
            c.wait(900)
        elif step == "q_w":             # Chomp on a champion freezes the ground at once (Q -> W), blows on it
            chomp()
            blow()
            blow()
        elif step == "e":               # Pillar of Ice alone: behind him, he cannot run past it
            raise_pillar()
            c.wait(1400)
        elif step == "e_q":             # the pillar holds him and gives Chomp back (E -> Q)
            raise_pillar()
            chomp()
            c.wait(700)
        elif step == "r":               # Subjugate: Q back and a pillar on him (R -> Q + E)
            subjugate()
            chomp()
            blow()
            c.wait(600)
        elif step == "kill":            # he falls near Trundle (on the domain: the tribute twice)
            blow()
            d.death = c.t + 40
            c.on_him("p_heal", c.t + 120)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height, W
# ready for the bite)
SCENES = [("移动：拖着冰狼牙棒跑", ["walk_in"], 150, 160, True),
          ("普攻：抡冰狼牙棒砸", ["attack"], 44, 160, True),
          ("技能1 利齿撕咬：咬一口——伤害、减速，偷他的攻击力（头上红獠牙 = 我变强，暗红獠牙 = 他变弱）", ["q"], 44, 160, False),
          ("连招 咬中英雄→冰封领域：立刻跳起冻住地面，冰面上攻速、移速更快", ["q_w"], 44, 160, True),
          ("技能2 寒冰之柱：冰柱立在他身后（附加包：真的地形），他想往后跑被挡住，周围减速", ["e"], 50, 190, False),
          ("连招 冰柱→利齿撕咬马上好", ["e_q"], 44, 190, False),
          ("大招 强权至上：抓住他吸生命、护甲、魔抗 4 秒，顺带冒一根冰柱，利齿撕咬刷新", ["r"], 50, 190, False),
          ("被动 国王的贡品：身边敌人倒下就回血（站在冰面上回双倍）", ["q_w", "kill"], 44, 160, True)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h, ready) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        showcase(path, z=z, steps=steps, W=230, H=h, gap=gap, tail=900, w_ready=ready)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_trundle_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_trundle_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_trundle_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_trundle_skills.gif")))


if __name__ == "__main__":
    main()
