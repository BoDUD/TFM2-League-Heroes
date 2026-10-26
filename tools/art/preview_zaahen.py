#!/usr/bin/env python3
"""Preview images for Zaahen, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_zaahen.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_zaahen_frames.png    every animation's dense frames (hd_, PPU 1.75, as league.dll shows them)
  league_zaahen_effects.png   every effect animation, 3x
  league_zaahen_showcase.gif  a scripted fight with Darius, the add-on's kit as installed, timed like the kit, 3x:
                              Dreaded Return pulls him in (W -> Q: the glaive at once); a sweep, the recast's uppercut
                              knocks him up (Q -> R: the dive while he is up), the slam (R -> Determination: full - the
                              flash and the aura, Q and W ready); Darius backs off, Aureate Rush catches him on the
                              outer edge, the glaive again; his swing would kill: the revive, banished and rising in the
                              light (full again: Q ready), and the glaive fells him.
  league_zaahen_skills.gif    each skill and combo alone with its effects against Darius, timed like the kit
                              (tools/kit/build_zaahen.py, 60 ticks a second), captioned in Chinese, 4x: the run; glaive
                              sweeps; The Darkin Glaive (two cuts) and its recast (the uppercut knocking him up); Dreaded
                              Return (the thrust flying out, the pull and the stun, the main pack's spin folded in); W ->
                              Q; the add-on's Aureate Rush (the rush, the spin, the outer edge); Grim Deliverance (wings of
                              light, the rise, the dive, the slam); Q's knock-up -> R; Cultivation of War at full (the
                              flash, the aura, Q and W ready); the add-on's revive (banished, rising again in the light).
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
from build_zaahen import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_zaahen")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_zaahen_fx", "league_zaahen_big")}
RISE = os.path.join(LEAGUE, "effects", "league_zaahen_rise")
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
REACH = 25                       # game px between his pivot and Darius's when he strikes (atk_range 25000)
RUSH_T = 10                      # the add-on's rush (addons/league_zaahen DASH_T, ticks)


def px_tick(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


class Zaahen(Clip):
    """preview_gnar's clip with his own dense frames, effects on him, on Darius, left on the ground, flying."""

    z = 4

    def a(self, tag, dur=None, loop=False, sheet=None):
        fr = list(dense(sheet or self.sp, tag, "zaahen", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def on_him(self, tag, when, sheet=None, until=None, under=False):
        (self.under if under else self.over).append(OnMe(frames_of(sheet or self.small, tag), when, self.me,
                                                         until=until))

    def at(self, tag, when, x, y, sheet=None, under=False):
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y))

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y, loop=True, until=t1, x1=x1, y1=y))


def scene(out, steps, gap, W=260, H=150, z=4, tail=900, x0=70):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_zaahen_fx"], fx["league_zaahen_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Zaahen(load(CHAMP), d, me, small, big)
    c.z = z
    c.wait(300)

    def sweep(n=1):
        for _ in range(n):
            t = c.t
            c.a("attack", tick(P["atk_dur"]))
            b = t + tick(P["a_hit"] - 1)
            c.on("a_hit", b)
            d.flinches.append(b)
            c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def walk(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_tick(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    def glaive(kill=False):
        """The Darkin Glaive: the glaive drawn back, two cuts on q_h1 / q_h2 (the second felling Darius: kill)."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        for hit, tag in ((P["q_h1"], "q_hit"), (P["q_h2"], "q_hit2")):
            b = t + tick(hit - 1)
            c.on(tag, b)
            d.flinches.append(b)
        if kill:
            d.death = b

    def uppercut():
        """Its recast: crouched, the uppercut on q3_hit knocking Darius up for q_air ticks."""
        t = c.t
        c.a("skill_up", tick(P["q3_dur"]))
        b = t + tick(P["q3_hit"] - 1)
        c.on_foe("q_uphit", b)
        d.hops.append((b, b + tick(P["q_air"]), 14))
        return b

    def dreaded(spin=True):
        """Dreaded Return: the thrust let fly on w_rel, the glaive's light down the line to Darius, the hook, the pull
        to him and the stun; the main pack's spin (Aureate Rush folded in) on w_e."""
        t = c.t
        c.a("skill2e" if spin else "skill2", tick(P["w_e_dur"] if spin else P["w_dur"]))
        rel = t + tick(P["w_rel"] - 1)
        x, y = me.pos(rel)
        sp = px_tick(P["w_speed"])
        hit = rel + max(0.0, (d.pos(rel)[0] - 6 - (x + 8))) / sp
        c.fly("w_glaive", rel, hit, x + 8, d.pos(hit)[0] - 6, y - 14)
        c.on("w_hit", hit)
        d.flinches.append(hit)
        pull = d.pos(hit)[0] - (me.pos(hit)[0] + REACH)
        if pull > 0:
            d.slides.append((hit, hit + tick(P["w_stun"]) + 60, -pull))
        if spin:
            s = t + tick(P["w_e"] - 1)
            c.at("e_spin", s - 120, me.pos(s)[0], gy, sheet=big, under=True)
            c.on("e_hit", s)
            d.flinches.append(s)

    def rush():
        """The add-on's Aureate Rush: the rush up to e_dash toward Darius (he lands with Darius on the outer ring), the
        spin on landing, the strike on e_hit."""
        t = c.t
        xa = me.pos(t)[0]
        ring = (P["e_r0"] + P["e_r"]) / 2000.0
        xb = min(xa + P["e_dash"] / 1000.0, d.pos(t)[0] - ring)
        me.moves.append((t, t + tick(RUSH_T), xa, xb))
        c.a("dash", tick(RUSH_T))
        t2 = c.t
        c.a("skill3", tick(P["e_dur"]))
        s = t2 + tick(P["e_hit"] - 1)
        c.at("e_spin", s - 120, xb, gy, sheet=big, under=True)
        c.on("e_hit", s)
        d.flinches.append(s)

    def deliverance():
        """Grim Deliverance: wings of light from the cast, the rise, the dive on r_jump to Darius, the slam on r_slam:
        the shockwave on the ground and the hit."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        c.on_him("r_rise", t, sheet=big, under=True)
        j, s = t + tick(P["r_jump"] - 1), t + tick(P["r_slam"] - 1)
        xa = me.pos(j)[0]
        xb = d.pos(s)[0] - 12
        me.moves.append((j, j + (s - j) * 0.6, xa, xb))
        c.at("r_slam", s, xb + 4, gy, sheet=big, under=True)
        c.on("r_hit", s + 40)
        d.flinches.append(s + 40)

    def full():
        """Cultivation of War filled: the flash, the darkin aura while it lasts (Q and W ready)."""
        t = c.t
        c.on_him("p_full", t)
        c.on_him("p_aura", t, until=t + 2600, under=True)

    def revive():
        """The add-on's revive: lethal damage at full Determination - banished, his rising drawn by the effect sheet
        (rise_r: collapsed, kneeling on the planted glaive, standing with the wings spread), then on his feet again."""
        c.a("rise_r", tick(P["rv_rise"]), sheet=load(RISE))
        c.on_him("p_full", c.t)

    for step in steps:
        if step == "walk_in":
            walk(far - REACH)
        elif step == "attack":
            sweep(2)
        elif step == "q":
            glaive()
            c.wait(700)
        elif step == "q2":
            glaive()
            c.wait(tick(P["q_gap"]) - 100)
            uppercut()
            c.wait(900)
        elif step == "w":
            dreaded()
            c.wait(700)
        elif step == "w_q":                 # W -> Q: the pull readies the glaive at once
            dreaded()
            glaive()
            c.wait(700)
        elif step == "e":
            rush()
            c.wait(700)
        elif step == "r":
            deliverance()
            c.wait(900)
        elif step == "q_r":                 # Q's knock-up -> R: its cooldown cut, the dive while Darius is up
            glaive()
            c.wait(tick(P["q_gap"]) - 100)
            uppercut()
            deliverance()
            c.wait(900)
        elif step == "full":
            sweep(2)
            full()
            glaive()
            c.wait(800)
        elif step == "revive":
            sweep(1)
            revive()
            c.wait(600)
        elif step == "fight":               # the showcase: every combo in one fight, the add-on's kit as installed
            dreaded(spin=False)             # the add-on's W (no spin): the pull and the stun
            glaive()                        # W -> Q: the glaive ready at once
            sweep(1)
            uppercut()                      # the recast knocks him up
            deliverance()                   # Q -> R: its cooldown cut, the dive while he is up (onto him)
            full()                          # R -> Determination up a lot: full - the flash and the aura, Q and W ready
            t0 = c.t + 100                  # Darius backs off, out of the glaive's reach
            d.runs.append((t0, t0 + 470))
            d.slides.append((t0, t0 + 470, 28))
            c.wait(t0 + 470 + 50 - c.t)
            rush()                          # the add-on's Aureate Rush (its whole e_dash): Darius on the outer edge
            glaive()                        # Q again (ready from full)
            t0 = c.t + 60                   # Darius swings back: lethal at full Determination
            d.attacks.append(t0)
            c.wait(t0 + sum(ms for _, ms in d.attack[:-1]) - c.t)
            revive()                        # banished, rising in the light; full again: Q ready
            glaive(kill=True)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


def showcase(out):
    """The scripted fight (every combo in play), 3x."""
    return scene(out, ["fight"], 60, W=170, H=120, z=3, tail=1200, x0=55)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：拖着暗裔长刀跑，暗裔翅膀往后掠", ["walk_in"], 150, 170),
          ("普攻：长刀横扫", ["attack"], REACH, 170),
          ("技能1 暗裔长刀：两连斩，每一斩都回血", ["q"], REACH, 170),
          ("技能1 再按一次：下蹲上挑，把人挑飞", ["q2"], REACH, 190),
          ("技能2 厄影回锋：长刀刺出把人拽回、短暂眩晕；主包接着绕身一斩（赤金突袭并进W）", ["w"], 70, 170),
          ("连招 W 拽中英雄 → 暗裔长刀马上好", ["w_q"], 70, 170),
          ("附加包 赤金突袭：冲向英雄再绕身斩，外圈伤害更高、多打最大生命值", ["e"], 60, 170),
          ("大招 大赦：展开光翼升空（免控、减伤），冲向英雄插刀落地，打中回血", ["r"], 55, 200),
          ("连招 上挑挑飞 → 大招冷却缩短，趁对方在空中插刀", ["q_r"], REACH, 200),
          ("被动 不落之志：打英雄叠果决，叠满攻击力翻倍、暗裔气焰，Q 和 W 马上好", ["full"], REACH, 170),
          ("附加包 复活：叠满时受到致命伤害，倒下 4 秒（无敌、选不中）再展翼站起来", ["revive"], REACH, 200)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_zaahen_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_zaahen_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_zaahen_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_zaahen_skills.gif")))


if __name__ == "__main__":
    main()
