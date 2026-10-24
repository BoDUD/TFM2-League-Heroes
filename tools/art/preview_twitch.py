#!/usr/bin/env python3
"""Preview images for Twitch, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_twitch.py [--out docs/preview] [--only frames|effects|showcase|skills]

  league_twitch_frames.png    every animation's dense frames (hd_, PPU 2.2, as league.dll shows them)
  league_twitch_effects.png   every effect animation, 3x
  league_twitch_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                              (tools/kit/build_twitch.py, 60 ticks a second): Q - the smoke, he creeps in hidden (drawn
                              faint), the first bolt reveals him (the flash, the attack speed glow) and poisons Darius;
                              W -> E: the cask lobbed from over his head between them, the splash and the puddle, both
                              slowed, then Contaminate bursts the venom on both; R: the surge, the aura, piercing bolts
                              through Darius and Garen; Darius falls and Ambush resets; 3x
  league_twitch_skills.gif    each skill and combo alone with its effects, captioned in Chinese, 4x (memory
                              skills-gif-in-review)
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_annie import Held  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_twitch import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_twitch")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_twitch_fx", "league_twitch_big")}
# (ahead, up) px of his pivot where each shot leaves, on the PPU redo's frames (rig_twitch_hd.py): the crossbow's tip
# (the bolt's y_offset 0: the pivot's row), the raised crossbow of Spray and Pray, the far hand over his head that
# throws Venom Cask
MUZZLE = (25, 0)
R_MUZZLE = (23, 4)
CASK = (16, 19)
BOLT = P["bolt_speed"] / 1000                    # px a tick
RBOLT = P["r_speed"] / 1000


def faint(f):
    """Hidden: drawn at a third of its alpha (the game shows his own team a faded figure)."""
    g = f.copy()
    g.putalpha(g.getchannel("A").point(lambda v: v // 3))
    return g


class Fight:
    """The fight's state: Twitch (dense frames), Darius and Garen in line ahead of him, what plays when."""

    def __init__(self, z, gap, gy):
        self.z = z
        self.sp = load(CHAMP)
        fx = {k: load(v) for k, v in FX.items()}
        self.small, self.big = fx["league_twitch_fx"], fx["league_twitch_big"]
        self.x0 = 40
        self.d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), self.x0 + gap, gy)
        self.g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), self.x0 + gap + 37, gy)
        self.me = Me(self.x0, gy)
        self.gy = gy
        self.body, self.under, self.over, self.hidden = [], [], [], []
        self.t = 300.0
        self.poisoned = False

    def a(self, tag, dur=None, loop=False):
        x, y = self.me.pos(self.t)
        an = Anim(dense(self.sp, tag, "twitch", self.z), self.t, x, y, loop=loop,
                  until=(self.t + dur) if dur is not None else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def hit(self, foe, tag, when, sheet=None):
        self.over.append(OnFoe(frames_of(sheet or self.small, tag), when, foe))
        foe.flinches.append(when)

    def bolt(self, foe, when, tag="a_bolt", speed=BOLT, last=None, muzzle=MUZZLE):
        """A bolt from the crossbow's tip to the foe (or on to `last`, the piercing one)."""
        sx = self.me.pos(when)[0] + muzzle[0]
        tx = (last or foe).pos(when)[0]
        arrive = when + tick(max(1, abs(tx - sx) / speed))
        self.over.append(Anim(frames_of(self.small, tag), when, sx, self.gy - muzzle[1], until=arrive, x1=tx,
                              y1=self.gy - muzzle[1]))
        return arrive

    def wait(self, ms):
        if ms > 0:
            self.a("idle", ms, loop=True)


def step_run(f):
    f.me.moves.append((f.t, f.t + 700, f.me.pos(f.t)[0], f.me.pos(f.t)[0] + 60))
    f.a("run", 700, loop=True)


def step_attack(f):
    f.hit(f.d, "a_hit", f.bolt(f.d, f.t + tick(P["a_st"])))
    f.poisoned = True
    f.a("attack", tick(P["atk_dur"]))
    f.wait(tick(40))


def step_q(f):
    """Ambush: the smoke, he creeps in hidden; the first bolt reveals him (the flash, the attack speed glow)."""
    q0 = f.t
    f.over.append(OnMe(frames_of(f.small, "q_cast"), q0, f.me))
    f.a("skill", tick(P["q_anim"]))
    creep = 900
    f.hidden.append((q0 + 120, f.t + creep))
    f.me.moves.append((f.t, f.t + creep, f.me.pos(f.t)[0], f.me.pos(f.t)[0] + 45))
    f.a("run", creep, loop=True)
    f.over.append(OnMe(frames_of(f.small, "q_out"), f.t, f.me))
    f.over.append(OnMe(frames_of(f.small, "q_as"), f.t, f.me, until=f.t + 2600))
    for _ in range(2):
        step_attack(f)


def step_w(f):
    """Venom Cask: lobbed from his far hand over his head between Darius and Garen; the splash, the puddle, the slow."""
    rel = f.t + tick(P["w_rel"])
    land = rel + tick(P["w_travel"])
    sx, sy = f.me.pos(rel)[0] + CASK[0], f.gy - CASK[1]
    cx = (f.d.pos(rel)[0] + f.g.pos(rel)[0]) // 2
    up = (sx + cx) // 2
    f.over.append(Anim(frames_of(f.small, "w_cask"), rel, sx, sy, until=(rel + land) / 2, x1=up, y1=f.gy - 40))
    f.over.append(Anim(frames_of(f.small, "w_cask"), (rel + land) / 2, up, f.gy - 40, until=land, x1=cx,
                       y1=f.gy - 4))
    f.a("skill2", tick(P["w_dur"]))
    pool = land + tick(P["w_pool"])
    f.under.append(Anim(frames_of(f.big, "w_pool"), land, cx, f.gy + 9, loop=True, until=pool))
    for foe in (f.d, f.g):
        f.hit(foe, "w_hit", land)
        f.under.append(OnFoe(frames_of(f.small, "w_slow"), land, foe, until=pool))
    f.poisoned = True
    f.wait(land + tick(P["e_wait"]) - f.t)


def step_e(f):
    """Contaminate: the venom on both bursts."""
    pop = f.t + tick(P["e_rel"])
    f.under.append(OnMe(frames_of(f.big, "e_cast"), pop, f.me))
    for foe in (f.d, f.g):
        f.hit(foe, "v_pop", pop, f.big)
    f.a("skill2_e", tick(P["e_anim"]))
    f.wait(300)


def step_r(f):
    """Spray and Pray: the surge, the aura, piercing bolts through Darius and Garen."""
    r0 = f.t
    f.over.append(OnMe(frames_of(f.big, "r_cast"), r0 + tick(P["r_anim"]) // 2, f.me))
    f.over.append(OnMe(frames_of(f.big, "r_on"), r0, f.me, until=r0 + 2200))
    f.a("ult", tick(P["r_anim"]))
    for _ in range(3):
        when = f.t + tick(P["a_st"])
        sx = f.me.pos(when)[0] + MUZZLE[0]
        f.bolt(f.d, when, "r_bolt", RBOLT, last=f.g)
        for foe in (f.d, f.g):
            f.hit(foe, "r_hit", when + tick(max(1, abs(foe.pos(when)[0] - sx) / RBOLT)), f.big)
        f.a("attack", tick(P["atk_dur"]))
        f.wait(tick(20))


def step_kill(f):
    """Darius falls (poisoned): Ambush resets over Twitch's head."""
    f.d.death = f.t - 200
    f.over.append(OnMe(frames_of(f.small, "q_reset"), f.d.death + tick(P["k_read"]), f.me))
    f.wait(1400)


STEPS = {"run": step_run, "attack": step_attack, "q": step_q, "w": step_w, "e": step_e, "r": step_r,
         "kill": step_kill}
FIGHT = ["q", "w", "e", "r", "kill"]


def showcase(out, z=3, steps=FIGHT, W=400, H=150, gap=110, tail=0, step=40):
    """The scripted fight (or some of its steps: skills() plays each skill alone) written to `out`."""
    gy = H - 42
    f = Fight(z, gap, gy)
    for s in steps:
        STEPS[s](f)
    f.wait(tail)
    end = f.t

    def place(img, fr, x, y):
        put(img, fr, int(x), int(y), z)

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W * z, H * z), ARENA)
        for an in f.under:
            fr = an.frame(tt)
            if fr is not None:
                place(img, fr, *an.pos(tt))
        units = [(f.g.pos(tt)[1], f.g.frame(tt), f.g.pos(tt)), (f.d.pos(tt)[1], f.d.frame(tt), f.d.pos(tt))]
        for an in f.body:
            fr = an.frame(tt)
            if fr is not None:
                if any(h0 <= tt < h1 for h0, h1 in f.hidden):
                    fr = faint(fr)
                units.append((an.pos(tt)[1] + 0.5, fr, an.pos(tt)))
                break
        for _, fr, p in sorted(units, key=lambda u: u[0]):
            if fr is not None:
                place(img, fr, *p)
        for an in f.over:
            fr = an.frame(tt)
            if fr is not None:
                place(img, fr, *an.pos(tt))
        frames.append(img.convert("RGB"))
        tt += step
    sample = frames[::6]
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, fr in enumerate(sample):
        strip.paste(fr, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q_ = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    q_[0].save(T.long_path(out), save_all=True, append_images=q_[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


# each skill alone (memory skills-gif-in-review): (caption, steps, Darius's distance)
SCENES = [("移动：弓着背端着弩小跑", ["run"], 120),
          ("普攻：弩箭射中，目标叠上一层死亡毒液", ["attack"], 70),
          ("技能1 埋伏：烟雾里隐身潜行，第一下普攻现身，攻速提升", ["q"], 110),
          ("技能2 剧毒之桶：远侧的手把毒桶举过头顶甩出，溅毒并留下毒池减速", ["w"], 70),
          ("连招 W→E：毒桶命中后立刻毒性爆发，引爆两人身上的毒", ["w", "e"], 70),
          ("大招 火力全开：弩箭穿透，一排敌人一起中箭", ["r"], 70),
          ("击杀：中毒的英雄阵亡，埋伏立刻刷新", ["attack", "kill"], 70)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import ImageDraw, ImageFont, ImageSequence
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    tmp = tempfile.mkdtemp()
    frames = []
    for k, (cap, steps, gap) in enumerate(SCENES):
        path = os.path.join(tmp, f"s{k}.gif")
        showcase(path, z=z, steps=steps, W=230, H=110, gap=gap, tail=600)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_twitch_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_twitch_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_twitch_showcase.gif")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "league_twitch_skills.gif")))


if __name__ == "__main__":
    main()
