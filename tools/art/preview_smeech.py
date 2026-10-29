#!/usr/bin/env python3
"""Preview images for Smeech (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_smeech.py [--out docs/preview] [--only frames|effects|skills]

  tft_smeech_frames.png    every animation's dense frames (hd_, PPU 2.4, as league.dll shows them)
  tft_smeech_effects.png   every effect animation, 3x
  tft_smeech_skills.gif    each skill alone with its effects against Darius, timed like the kit
                           (tools/kit/build_smeech.py, 60 ticks a second) and as tft.dll plays its parts
                           (addons/tft/src/smeech.rs), captioned in Chinese, 4x (preview_scar.py's way): the walk; the
                           two claws' rakes; Scrap Hacker (over Darius onto Ashe, the weakest, three slashes - the last a
                           crit that kills her - then the re-leap onto Garen); Scrap Rip (Darius's armour torn, the mark
                           over his head); Scrap Frenzy (the aura, a hop onto each of Darius, Garen and Ashe in turn).
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
from build_smeech import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_smeech")
FX = {"tft_smeech_fx": os.path.join(TFT, "effects", "tft_smeech_fx")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
GAREN = os.path.join(ROOT, "league", "champions", "league_garen")
ASHE = os.path.join(ROOT, "league", "champions", "league_ashe")
REACH = 44                       # game px between his pivot and Darius's when he rakes (his claws reach 30 ahead)
GAP = P["q_gap"] // 1000         # where tft.dll lands him: q_gap short of the target


class Clip(SilcoClip):
    """preview_silco's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "smeech", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        if dur and not loop and dur < sum(ms for _, ms in fr):   # a shorter play: every frame shorter alike
            k = dur / sum(ms for _, ms in fr)
            fr = [(f, ms * k) for f, ms in fr]
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def scene(out, steps, gap, W=320, H=160, z=4, tail=900, x0=40):
    """One scene (a list of steps) written to `out`."""
    small = load(FX["tft_smeech_fx"])
    gy = H - 30
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, small)
    c.z = z
    garen = ashe = None
    if "q" in steps or "r" in steps:              # Ashe the weakest behind Darius, Garen beside
        garen, ashe = Foe(load(GAREN), far + 30, gy - 8), Foe(load(ASHE), far + 70, gy + 6)
        c.foes = (garen, ashe)
    c.wait(300)

    def jump(t, foe):
        """tft.dll lands him q_gap short of the foe on his side (a blink)."""
        x_from, x_to = me.pos(t)[0], foe.x - GAP
        me.moves.append((t, t + 1, x_from, x_to))

    def rakes():
        for tag, hit in (("attack", "a_hit"), ("attack2", "a_hit")):
            t = c.t + tick(P["atk_st"] - 1)
            c.on_foe(d, hit, t)
            d.flinches.append(t)
            c.a(tag, tick(P["atk_dur"]))
            c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def hacker():
        """Scrap Hacker: up, landed beside Ashe (the lowest health), three slashes, the third a crit that kills her;
        the re-leap onto Garen, three slashes at q_again%."""
        t = c.t
        land = t + tick(P["q_jump"] - 1)
        c.a("leap", tick(P["q_jump"]))
        jump(land, ashe)
        c.on_me("q_land", land, under=True)
        c.a("stabs", tick(P["q_dur"] - P["q_jump"]))
        for k, s in enumerate(("q_s1", "q_s2", "q_s3")):
            ts = land + tick(P[s])
            c.on_foe(ashe, "q_hit", ts)
            ashe.flinches.append(ts)
            if k == 2:
                c.on_foe(ashe, "p_hit", ts)
                ashe.death = ts + 40
        again = land + tick(P["q_s3"]) + 60
        jump(again, garen)
        c.on_me("q_land", again, under=True)
        for s in ("q_s1", "q_s2", "q_s3"):
            ts = again + tick(P[s])
            c.on_foe(garen, "q_hit", ts)
            garen.flinches.append(ts)
        return again + tick(P["q_s3"]) + 300

    def rip():
        """Scrap Rip: on e_st both claws tear Darius, his armour mark over his head for e_t."""
        t = c.t + tick(P["e_st"] - 1)
        c.on_foe(d, "e_hit", t)
        d.flinches.append(t)
        c.on_foe(d, "e_shred", t, until=t + 1600)
        c.a("skill2", tick(P["e_dur"]))
        return t + 1600

    def frenzy():
        """Scrap Frenzy: the aura for r_dur; a hop every r_gap from r_st onto the next enemy not hit yet (champions
        first, the lowest health first): Ashe, Garen, Darius; then nobody left."""
        t = c.t
        c.on_me("r_frenzy", t, until=t + tick(P["r_dur"]), under=True)
        c.a("ult", tick(P["r_dur"]))
        for i, foe in enumerate((ashe, garen, d)):
            th = t + tick(P["r_st"] + i * P["r_gap"] - 1)
            jump(th, foe)
            c.on_foe(foe, "r_hit", th)
            foe.flinches.append(th)
            if i == 2:
                c.on_foe(foe, "p_hit", th)
        return t + tick(P["r_dur"]) + 300

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            rakes()
            rakes()
        elif step in ("q", "e", "r"):
            end = {"q": hacker, "e": rip, "r": frenzy}[step]()
            c.wait(max(0, end + 300 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：长腿大步走", ["walk_in"], 180, 190),
          ("普攻 双爪连撕：左右爪轮流挥抓", ["attack"], REACH, 170),
          ("技能1 废铁黑客：跳向生命最低的敌人（艾希）连斩3下，暴击斩杀后再跳向盖伦，伤害70%", ["q"], 70, 190),
          ("技能2 拆解：双爪撕扯，降低护甲30%（头顶碎盾）4秒", ["e"], REACH, 180),
          ("大招 废铁狂潮：1.2秒不受控制减伤30%，接连跳斩没打过的敌人，每跳叠暴击率", ["r"], 70, 190)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_smeech_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_smeech_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_smeech_skills.gif")))


if __name__ == "__main__":
    main()
