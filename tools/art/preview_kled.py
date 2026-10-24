#!/usr/bin/env python3
"""Preview images for Kled, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_kled.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_kled_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  league_kled_effects.png   every effect animation, 3x
  league_kled_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_kled.py, 60 ticks a second):
                            Kled rides in, his axe hits with Violent Tendencies (the rage flare, the ring, the fourth
                            hit); Bear Trap on a Rope (the trap flying, the snap, the alert, the trap on the ankles,
                            the yank) and Jousting at once (Q -> E: the dust, the dash through, the slash, back through
                            again, Violent Tendencies ready); Chaaaaaaaarge!!! (the shield, the crash, the ram) and the
                            trap again (R -> Q); Skaarl flees (the poof), Kled fights on foot (the axe, Pocket Pistol's
                            smoke, spray and recoil) until Skaarl comes back (the remount burst, the haste); Darius
                            falls; 3x.
  league_kled_skills.gif    each skill and combo alone with its effects, captioned in Chinese, 4x (the user,
                            2026-10-24: 「带技能的gif图呢？」, memory skills-gif-in-review).
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
from build_kled import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_kled")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_kled_fx", "league_kled_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Kled(Clip):
    """preview_gnar's clip with his own dense frames; on foot (`foot`) the f_* tags stand in."""

    flip = False
    foot = False
    z = 3                                               # the clip's zoom: render() draws at it, so his frames must too

    def a(self, tag, dur=None, loop=False, z=None):
        if self.foot and tag in ("idle", "run", "attack", "hit"):
            tag = "f_" + tag
        fr = list(dense(self.sp, tag, "kled", z or self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None, flip=self.flip)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def fly(self, tag, t0, t1, x0, x1, y0, y1=None, sheet=None):
        """A projectile's picture flying from (x0, y0) to (x1, y1) (drawn flying right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y0, loop=True, until=t1, x1=x1,
                              y1=y0 if y1 is None else y1, flip=x1 < x0))

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Darius (the trap on his ankles, the alert over his head)."""
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: the dust, the crash, the poof)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


# the fight's steps in order (showcase); skills() plays some of them alone
FIGHT = ["ride_in", "w4", "qe", "back", "rq", "dismount", "foot", "pistol", "remount", "kill"]


def showcase(out, z=3, steps=FIGHT, W=340, H=130, gap=150, tail=1500):
    """The scripted fight (or some of its steps: skills() plays each skill alone) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_kled_fx"], fx["league_kled_big"]
    gy = H - 30
    x0 = 40
    far = x0 + gap                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Kled(load(CHAMP), d, me, small, big)
    c.z = z
    c.wait(300)

    def walk(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    def blow(fourth=False, quick=False):
        """An axe blow (the fourth of Violent Tendencies heavier); quick: Violent Tendencies' attack speed."""
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        b = t + tick(P["a_hit"] - 1)
        c.on("w_hit" if fourth else "a_hit", b)
        d.flinches.append(b)
        if not quick:
            c.wait(tick(P["atk_cd"] - P["atk_dur"]))
        return b

    def tendencies():
        """Violent Tendencies: the rage flare and ring on him, four quick hits, the fourth heavier."""
        t = c.t
        c.on_me("w_on", t)
        last = None
        for k in range(4):
            last = blow(fourth=k == 3, quick=True)
            c.wait(tick(max(0, P["atk_cd"] * 100 // (100 + P["w_as"]) - P["atk_dur"])))
        c.on_me("w_aura", t, until=last + 60, under=True)

    def trap():
        """Bear Trap on a Rope: the trap flying, the snap, the alert, the trap on his ankles, the yank."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        rel = t + tick(P["q_rel"] - 1)
        xs = me.pos(rel)[0] + 10
        hit = rel + abs(d.pos(rel)[0] - xs) / px_ms(P["q_speed"])
        c.fly("q_trap", rel, hit, xs, d.pos(rel)[0], gy - 14)
        c.on("q_hit", hit)
        c.on_foe("q_mark", hit)
        d.flinches.append(hit)
        yank = hit + tick(P["q_teth"])
        c.on_foe("q_rope", hit, until=yank, under=True)
        c.on_foe("q_yank", yank)
        pull = P["q_pull"] * P["q_pull_t"] / 1000.0
        d.slides.append((yank, yank + tick(P["q_pull_t"]), -pull))
        d.flinches.append(yank)
        return yank + tick(P["q_pull_t"])

    def joust(second=False):
        """Jousting: the dust where Skaarl starts, the dash through Darius, the slash, the haste."""
        t = c.t
        c.a("skill2", tick(P["e_dur"]))
        go = t + tick(P["e_go"] - 1)
        xa = me.pos(go)[0]
        xd = d.pos(go)[0]
        xb = xd + (15 if xa < xd else -15)
        c.at("e_dust", go, xa, gy, sheet=c.big, under=True)
        t1 = go + abs(xb - xa) / px_ms(P["e_speed"])
        me.moves.append((go, t1, xa, xb))
        hit = go + abs(xd - xa) / px_ms(P["e_speed"])
        c.on("e_hit", hit)
        d.flinches.append(hit)
        c.on_me("haste", go, until=go + tick(P["e_ms_t"]), under=True)
        if second:
            c.on_me("w_ready", t1)
        c.flip = xb < xa if second else c.flip
        return t1

    def charge():
        """Chaaaaaaaarge!!!: the shield round him, Skaarl at a sprint, the crash, the ram knocking Darius back."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        go = t + tick(P["r_go"] - 1)
        xa = me.pos(go)[0]
        stop = d.pos(go)[0] - 22
        t1 = go + abs(stop - xa) / px_ms(P["r_speed"])
        me.moves.append((go, t1, xa, stop))
        c.on_me("r_trail", go, sheet=c.big)
        c.on_me("haste", go, until=t1 + tick(P["r_ms_t"]), under=True)
        c.at("r_crash", t1, d.pos(t1)[0], gy, sheet=c.big, under=True)
        c.on("r_hit", t1)
        d.flinches.append(t1)
        d.slides.append((t1, t1 + tick(P["r_kb_t"]), P["r_kb"] * P["r_kb_t"] / 1000.0))
        return t1

    def pistol():
        """Pocket Pistol: the gunsmoke, the spray, the pellets on Darius, the recoil blowing him back."""
        t = c.t
        c.a("f_skill", tick(P["p_dur"]))
        rel = t + tick(P["p_rel"] - 1)
        xs = me.pos(rel)[0] + 8
        hit = rel + abs(d.pos(rel)[0] - xs) / px_ms(P["p_speed"])
        c.on_me("p_flash", rel)
        c.fly("p_blast", rel, hit, xs, d.pos(rel)[0], gy - 10)
        c.on("p_hit", hit)
        d.flinches.append(hit)
        back = P["p_back"] * P["p_back_t"] / 1000.0
        xb = me.pos(rel)[0]
        me.moves.append((rel, rel + tick(P["p_back_t"]), xb, xb - back))

    for step in steps:
        if step == "ride_in":           # riding Skaarl in
            walk(far - 26)
        elif step == "attack":          # two axe blows
            blow()
            blow()
        elif step == "w4":              # Violent Tendencies: four quick hits
            tendencies()
            c.wait(300)
        elif step == "q":               # Bear Trap on a Rope alone
            end = trap()
            c.wait(end - c.t + 200)
        elif step == "qe":              # the yank, Jousting at once, through and back (Q -> E, E -> W ready)
            end = trap()
            c.wait(end - c.t)
            joust()
            c.wait(tick(P["e_gap"]))
            joust(second=True)
            c.flip = False
            c.wait(300)
        elif step == "e":               # Jousting alone (through and back)
            joust()
            c.wait(tick(P["e_gap"]))
            joust(second=True)
            c.flip = False
            c.wait(300)
        elif step == "back":            # he rides off
            c.wait(200)
            xb = me.pos(c.t)[0]
            me.moves.append((c.t, c.t + 600, xb, xb - 70))
            c.a("run", 600, loop=True)
        elif step == "r":               # Chaaaaaaaarge!!! alone
            end = charge()
            c.wait(end - c.t + 300)
        elif step == "rq":              # the ram, the trap again at once (R -> Q)
            end = charge()
            c.wait(end - c.t)
            end = trap()
            c.wait(end - c.t + 200)
        elif step == "dismount":        # Skaarl's health gone: he flees, Kled on foot
            c.at("dismount", c.t, me.pos(c.t)[0], gy - 9, sheet=c.big)
            c.foot = True
            c.wait(600)
        elif step == "foot":            # on foot: the axe
            blow()
            blow()
        elif step == "pistol":          # Pocket Pistol (courage)
            pistol()
            c.wait(300)
        elif step == "remount":         # courage full: Skaarl back
            c.on_me("remount", c.t, sheet=c.big)
            c.foot = False
            c.on_me("haste", c.t, until=c.t + tick(P["re_ms_t"]), under=True)
            c.wait(700)
        elif step == "kill":
            blow()
            d.death = c.t + 40
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：骑着斯嘎尔跑", ["ride_in"], 150, 130),
          ("普攻：挥斧砍", ["attack"], 26, 130),
          ("被动 暴烈秉性（W）：隔一阵四下快攻，第四下重击（按目标最大生命）", ["w4"], 26, 130),
          ("技能1 飞索捕熊器：扔出捕熊夹夹住英雄，过一会儿拽过来", ["q"], 110, 130),
          ("技能2 比武：斯嘎尔冲过敌人，穿过英雄还能再冲回来", ["e"], 50, 130),
          ("连招 Q→E：拽过来立刻比武，两次穿过后暴烈秉性就绪", ["qe"], 110, 130),
          ("大招 冲啊——！！：带护盾冲锋，撞飞第一个英雄，队友加速", ["r"], 140, 130),
          ("连招 R→Q：撞中后立刻再扔捕熊夹", ["rq"], 140, 130),
          ("被动 斯嘎尔：斯嘎尔的血打空就逃跑，克烈下马步行（攻击降低）", ["dismount", "foot"], 26, 130),
          ("下马 随身手枪：喷一枪霰弹，后坐力把自己弹开，攒勇气", ["dismount", "pistol"], 60, 130),
          ("被动 勇气攒满：斯嘎尔回来重新上马，加速，暴烈秉性就绪", ["dismount", "remount"], 60, 130)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap, h) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        showcase(path, z=z, steps=steps, W=230, H=h, gap=gap, tail=900)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_kled_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_kled_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_kled_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_kled_skills.gif")))


if __name__ == "__main__":
    main()
