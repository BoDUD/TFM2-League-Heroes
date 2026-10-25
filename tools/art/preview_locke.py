#!/usr/bin/env python3
"""Preview images for Locke, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_locke.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_locke_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  league_locke_effects.png   every effect animation, 3x
  league_locke_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_locke.py, 60 ticks a
                             second): nail stabs; Ritual Nails (three nails, the slow, the mark over his head) gives
                             Ashen Pursuit back (Q -> E): out of the ash next to Darius, the ignition at once (E -> W, his
                             W look - the add-on's), the pursuit's dash through him popping the nails; Purgatory (the
                             case swung and flung, the seal circle, the mark) gives Ritual Nails back (R -> Q); Darius
                             under the line is sealed (the add-on's execute), the artifact left where he fell, picked up,
                             Ashen Pursuit ready again (a takedown); 3x.
  league_locke_skills.gif    each skill and combo alone with its effects, captioned in Chinese, 4x (the user,
                             2026-10-24: 「带技能的gif图呢？」).
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
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_locke import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_locke")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_locke_fx", "league_locke_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
W_TAGS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dash")   # the add-on's W look (view.rs)
HAND = -14                     # the nails leave his hand at chest height (game px over the pivot)
CASE = -24                     # the case flies at about his head's height


class Locke(Clip):
    """preview_gnar's clip with his own dense frames; in his W look while it lasts (the add-on swaps the tags)."""

    w_until = -1.0
    facing_left = False                                 # turned round after the pursuit's dash took him past Darius

    def tag(self, tag):
        return "w_" + tag if self.t < self.w_until and tag in W_TAGS else tag

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, self.tag(tag), "locke", z))
        if self.facing_left:                            # mirrored, its 1x size kept for put()
            fr = [(mirror(f), ms) for f, ms in fr]
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def wait(self, ms):
        if ms > 0:
            self.a("idle", ms, loop=True)

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Darius (the marks over his head, the slow at his feet)."""
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def on_him(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Locke (the soul fire, the ignition, the reset sigil, the seal)."""
        (self.under if under else self.over).append(OnMe(frames_of(sheet or self.small, tag), when, self.me,
                                                         until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None, last=False):
        """A picture left where it was played (a not-following view: the ash, the dash's slash, the seal circle);
        `last`: only its last frame, held (the artifact lying on the ground)."""
        fr = frames_of(sheet or self.small, tag)
        if last:
            fr = fr[-1:]
        (self.under if under else self.over).append(Anim(fr, when, x, y, loop=until is not None, until=until))


def mirror(f):
    """A dense frame turned to face left, its info (the 1x size put() centres it by) kept."""
    g = f.transpose(Image.FLIP_LEFT_RIGHT)
    g.info.update(f.info)
    return g


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


# the fight's steps in order (showcase); skills() plays some of them alone
FIGHT = ["walk_in", "attack", "q_e", "back", "r_q", "seal"]


def showcase(out, z=3, steps=FIGHT, W=320, H=150, gap=150, tail=1500, w_ready=True):
    """The scripted fight (or some of its steps: skills() plays each skill alone) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_locke_fx"], fx["league_locke_big"]
    gy = H - 30
    x0 = 40
    far = x0 + gap                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Locke(load(CHAMP), d, me, small, big)
    st = {"w_ready": w_ready, "marks": False, "e_next": False, "mark": None}
    c.wait(300)

    def stab():
        """A nail stab: Silver Stake on him, the nails his Q left popped."""
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        b = t + tick(P["atk_st"] - 1)
        c.on("a_hit", b)
        d.flinches.append(b)
        if st["marks"]:
            c.on("q_pop", b)
            st["mark"].until = b + tick(P["q_mark_p"]) / 2
            st["marks"] = False

    def nails():
        """Ritual Nails: three nails q_gap ticks apart, each a hit and the slow; the mark over his head. -> the first
        nail's landing."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        first = None
        for k in range(3):
            rel = t + tick(P["q_at"] - 1 + k * P["q_gap"])
            xa, xb = me.pos(rel)[0] + 8, d.pos(rel)[0]
            land = rel + abs(xb - xa) / px_ms(P["q_speed"])
            c.fly("q_nail", rel, land, xa, xb, gy + HAND)
            c.on("q_hit", land)
            d.flinches.append(land)
            c.on_foe("slow", land, until=land + tick(P["q_slow_t"]), under=True)
            first = first or land
        # the mark shows while he holds the count (the kit's casted reads it every q_mark_p ticks): a stab's pop ends it
        st["mark"] = OnFoe(frames_of(c.small, "q_mark"), first, d, until=first + tick(P["q_mark_t"]))
        c.over.append(st["mark"])
        st["marks"] = True
        return first

    def ignite():
        """Soul Ignition: the hunch and the arms spread, the flames rising; the soul fire round him while it lasts,
        his W look (the add-on's), drawn back in at the end."""
        t = c.t
        c.a("w", tick(P["w_dur"]))
        c.on_him("w_ign", t)
        end = t + tick(P["w_t"])
        c.on_him("w_aura", t + 400, until=end, under=True)
        c.on_him("w_end", end)
        c.w_until = end
        st["w_ready"] = False

    def blink():
        """Ashen Pursuit: the ash where he left, out of the ash next to Darius, the shockwave; the next attack armed;
        the ignition at once with W ready (E -> W)."""
        t = c.t
        xs, xt = me.pos(t)[0], d.pos(t)[0] - 24   # (in game on Darius: the bodies push apart a few ticks later)
        c.at("e_out", t, xs, gy)
        me.moves.append((t, t + 1, xs, xt))
        c.at("e_in", t + 1, xt, gy)
        c.a("skill2", tick(P["e_dur"]))
        h = t + tick(P["e_at"] - 1)
        c.on("e_hit", h)
        d.flinches.append(h)
        st["e_next"] = True
        if st["w_ready"]:
            ignite()

    def pursuit():
        """The attack after E: the dash through Darius (e_speed), the slash where he started, the stab's hit, the nails
        popped."""
        t = c.t
        c.a("attack", tick(P["atk_st"] - 1))
        t1 = c.t
        xs, xt = me.pos(t1)[0], d.pos(t1)[0] + 16
        c.at("e_dash", t1, xs, gy)
        c.a("dash", tick(P["e_dash_t"]))
        me.moves.append((t1, t1 + abs(xt - xs) / px_ms(P["e_speed"]), xs, xt))
        c.on("a_hit", t1 + 60)
        d.flinches.append(t1 + 60)
        if st["marks"]:
            c.on("q_pop", t1 + 60)
            st["mark"].until = t1 + 60 + tick(P["q_mark_p"]) / 2
            st["marks"] = False
        st["e_next"] = False
        c.facing_left = True                            # past him: turned round to face him
        c.wait(tick(P["atk_dur"] - P["atk_st"] - P["e_dash_t"] + 1))

    def purgatory(sealed_at=None):
        """Purgatory: the case swung and flung at Darius's spot, the seal circle where it lands, the blast's hit, the
        slow, the mark and its checks (to `sealed_at`, the tick the add-on executes him and takes the mark off). -> the
        landing."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        rel = t + tick(P["r_rel"] - 1)
        land = rel + tick(P["r_travel"])
        xl = d.pos(rel)[0]
        c.fly("r_case", rel, land, me.pos(rel)[0] + 4, xl, gy + CASE)
        c.at("r_land", land, xl, gy, sheet=big, under=True)
        c.on("r_hit", land)
        d.flinches.append(land)
        c.on_foe("slow", land, until=land + tick(P["r_slow_t"]), under=True)
        end = land + tick(P["r_t"]) if sealed_at is None else land + sealed_at
        c.on_foe("r_mark", land, until=end)
        k = land + tick(P["r_p"])
        while k <= end:
            c.on("r_tick", k)
            k += tick(P["r_p"])
        return land

    def walk(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    for step in steps:
        if step == "walk_in":
            walk(far - 26)
        elif step == "attack":          # two nail stabs, Silver Stake on each
            stab()
            stab()
        elif step == "q_pop":           # Ritual Nails, then a stab pops the nails
            nails()
            c.wait(250)
            stab()
            c.wait(300)
        elif step == "q_e":             # the nails on a champion ready E (Q -> E): out of the ash by him, the ignition
            nails()                     # at once (E -> W, his W look: the add-on's), the pursuit's dash through him
            blink()
            pursuit()
            stab()
            stab()
        elif step == "back":            # past him after the dash: round to his front again, facing him
            walk(far - 40)
            c.facing_left = False
            c.wait(200)
        elif step == "w":               # the soul fire alone: faster stabs in his W look (the add-on's)
            ignite()
            stab()
            stab()
            stab()
            walk(me.pos(c.t)[0] - 30)
            walk(far - 26)
        elif step == "r_q":             # Purgatory, Ritual Nails back (R -> Q)
            purgatory()
            nails()
            stab()
            c.wait(400)
        elif step == "seal":            # under the line in the mark: sealed (the add-on's execute), the artifact left
            land = purgatory(tick(2 * P["r_p"]))   # where he fell, picked up (a seal, the ult's cooldown cut); the
            k = land + tick(2 * P["r_p"])          # takedown readies Ashen Pursuit (the reset sigil)
            c.wait(k - c.t)
            d.death = k
            c.on("r_tick", k)
            xa = d.pos(k)[0]
            c.at("r_land", k + 400, xa, gy, sheet=big, under=True, until=k + 1700, last=True)
            c.on_him("p_reset", k + 80)
            c.wait(380)
            walk(xa - 2)
            c.on_him("r_seal", c.t)
            c.wait(700)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height, W
# ready)
SCENES = [("移动：背着棺匣跑", ["walk_in"], 150, 150, True),
          ("普攻 + 被动 圣银穿心：拿钉子捅，每一下附带魔法伤害", ["attack"], 30, 150, True),
          ("技能1 伏魔三钉：连扔三颗钉——伤害、减速，头上留下钉印；普攻引爆钉印", ["q_pop"], 70, 150, False),
          ("连招 钉中英雄→灰猎无影马上好：化成灰烬闪到他身边→立即点燃灵焰仪式→下一次普攻冲刺穿过他", ["q_e"], 80, 150, True),
          ("被动 灵焰仪式（附加包）：攻速、移速更快，整个人变成 W 的样子，结束时回血", ["w"], 30, 150, True),
          ("大招 万魔狱：抡起棺匣扔出去——封印法阵、减速、封印标记；连招：伏魔三钉马上好", ["r_q"], 80, 170, False),
          ("处决（附加包）：标记期间血量低于处决线就被封印，法器掉在原地，捡起来处决线永久提高、大招冷却减少；参与击杀灰猎无影刷新",
           ["seal"], 80, 170, False)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h, ready) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        showcase(path, z=z, steps=steps, W=250, H=h, gap=gap, tail=900, w_ready=ready)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_locke_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_locke_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_locke_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_locke_skills.gif")))


if __name__ == "__main__":
    main()
