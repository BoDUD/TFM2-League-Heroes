#!/usr/bin/env python3
"""Preview images for Kobuko (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_kobuko.py [--out docs/preview] [--only frames|effects|skills]

  tft_kobuko_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  tft_kobuko_effects.png   every effect animation, 3x
  tft_kobuko_skills.gif    each skill alone with its effects against Darius, timed like the kit (tools/kit/build_kobuko.py,
                           60 ticks a second) and as tft.dll plays its part (addons/tft/src/kobuko.rs), captioned in
                           Chinese, 4x: the run; the palm strike; Golden Claw Mantra (the golden shield, the armed claw's
                           spiral, the golden claw strike, the stun); Tiger Pounce (the leap onto Darius, the landing
                           ring, Darius and a second enemy thrown up); the Second Phase (the roar's flames, the rage
                           burning on); Game Over! (the spring out of sight, the landing mark under Darius, the crash's
                           shockwave, both enemies thrown up).
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
from preview_garen import T, contact, load  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me  # noqa: E402
import preview_zoe as Z  # noqa: E402
from preview_silco import Clip as SilcoClip, px_tick  # noqa: E402
from build_kobuko import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_kobuko")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_kobuko_fx", "tft_kobuko_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
REACH = 34                       # game px between his pivot and Darius's when he strikes (atk_range 25000 + his bulk)


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4, frames=None):
        fr = list(dense(self.sp, tag, "kobuko", self.z))
        if frames is not None:                         # only these frames of the tag (the ult's crash)
            fr = [fr[k] for k in frames]
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def scene(out, steps, gap, W=280, H=150, z=4, tail=900, x0=50):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_kobuko_fx"], fx["tft_kobuko_big"]
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    if "e" in steps or "r" in steps:              # a second enemy close by: the landing takes both
        c.foes = (Foe(load(GAREN), far + 22, gy),)
    c.wait(300)

    def strike(claw=False):
        """A palm strike; armed, the attack's strike swaps to the golden claw (`claw`) on atk_st."""
        hit = c.t + tick(P["atk_st"] - 1)
        d.flinches.append(hit)
        if claw:
            c.a("attack", tick(P["atk_st"] - 1))
            c.on_foe(d, "q_hit", hit)
            c.on_foe(d, "q_stun", hit, until=hit + tick(P["q_stun"]))
            c.a("claw", tick(P["claw_t"]))
            c.wait(max(0, hit - tick(P["atk_st"] - 1) + tick(P["atk_dur"]) - c.t))
        else:
            c.on_foe(d, "a_hit", hit)
            c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def mantra():
        """Golden Claw Mantra: the golden shield, the claw armed (its spiral over him) until the next strike."""
        t = c.t
        c.on_me("q_shield", t)
        c.a("skill", tick(P["q_dur"]))
        c.wait(200)
        armed = c.t
        claw_at = armed + tick(P["atk_st"] - 1)
        c.on_me("q_on", armed - 200, until=claw_at)
        strike(claw=True)
        c.wait(tick(P["q_stun"]) - 600)

    def pounce():
        """Tiger Pounce: MoveToTarget at e_speed onto Darius; on arrival the ring and every enemy within e_r thrown up."""
        t = c.t
        x_from = me.pos(t)[0]
        x_to = d.x - 18
        land = t + 17 + (x_to - x_from) / px_tick(P["e_speed"])
        me.moves.append((t + 17, land, x_from, x_to))
        c.a("skill2", tick(P["e_dur"]))
        c.at_spot("e_land", land, x_to, gy, sheet=small)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "e_hit", land)
            foe.hops.append((land, land + tick(P["e_up"]), 7))
        return land + tick(P["e_up"])

    def phase():
        """The Second Phase: tft.dll at half health - the roar's flames, then the rage burning on."""
        c.on_me("p_burst", c.t)
        c.on_me("p_rage", c.t + 400, until=c.t + 3200, under=True)
        d.attacks += [c.t + 200, c.t + 1200, c.t + 2200]
        c.wait(400)
        strike()
        strike()

    def game_over():
        """Game Over!: crouch and spring (seen r_go ticks), unseen until r_at, the landing mark under Darius meanwhile;
        Teleport onto him: the crash's shockwave, every enemy within r_r thrown up r_up ticks."""
        t = c.t
        c.on_foe(d, "r_mark", t + 17)
        c.a("ult", tick(P["r_go"]))
        go = t + tick(P["r_go"] - 1)
        c.at_spot("r_jump", go, me.pos(go)[0], gy, sheet=small)
        crash = t + tick(P["r_at"] - 1)
        me.moves.append((crash - 1, crash, me.pos(go)[0], d.x - 6))
        c.wait(crash - c.t)
        c.a("ult", tick(P["r_dur"] - P["r_at"] + 1), frames=[-1])
        c.at_spot("r_slam", crash, d.x - 6, gy, sheet=big)
        for foe in (d,) + tuple(c.foes):
            c.on_foe(foe, "r_hit", crash)
            foe.hops.append((crash, crash + tick(P["r_up"]), 12))
        return crash + tick(P["r_up"])

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            strike()
            strike()
        elif step == "q":
            mantra()
        elif step == "e":
            end = pounce()
            c.wait(end + 300 - c.t)
        elif step == "p":
            phase()
        elif step == "r":
            end = game_over()
            c.wait(end + 300 - c.t)
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone (the user, 2026-10-24: 「带技能的gif图呢？」): (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：圆滚滚地小跑", ["walk_in"], 160, 170),
          ("普攻：猫爪掌", ["attack"], REACH, 170),
          ("技能1 金爪真言：套上金色护盾，下一掌变成金爪重掌，晕眩1秒", ["q"], REACH, 170),
          ("技能2 猛虎扑：扑到敌人身上，落地把周围的敌人击飞", ["e"], 90, 170),
          ("被动 第二阶段：第一次掉到一半血时怒吼，狂怒到阵亡（攻速+40%、吸血20%）", ["p"], REACH, 170),
          ("大招 游戏结束！：一跃冲天，从天而降砸在敌人身上，周围敌人被击飞", ["r"], 120, 190)]


def skills(out, z=4):
    """Every skill alone with its effects, captioned, one GIF."""
    import tempfile
    from PIL import ImageDraw, ImageFont, ImageSequence
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
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=[int(ms) for _, ms in out_frames], loop=0)
    return len(q), round(sum(ms for _, ms in out_frames) / 1000, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "skills"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_kobuko_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_kobuko_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_kobuko_skills.gif")))


if __name__ == "__main__":
    main()
