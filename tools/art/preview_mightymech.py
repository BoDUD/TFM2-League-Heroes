#!/usr/bin/env python3
"""Preview images for the Mighty Mech (the tft pack), built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_mightymech.py [--out docs/preview] [--only frames|effects|skills]

  tft_mightymech_frames.png    every animation's dense frames (hd_, PPU 2.0, as tft.dll shows them)
  tft_mightymech_effects.png   every effect animation, 3x
  tft_mightymech_skills.gif    each skill alone with its effects against Darius, Garen and Ashe, timed like the kit
                               (tools/kit/build_mightymech.py, 60 ticks a second) and as tft.dll plays its parts
                               (addons/tft/src/mightymech.rs), captioned in Chinese, 4x (preview_thex.py's way): the run;
                               Piston Slash (three swings, the third the piston chop with its slow); Gravity Matrix (the
                               field under it, the taunt marks twice, the shockwave on the end); Mecha Leap (the leap, the
                               landing's crater, Darius knocked up); Ultimate Form: Super Blade (the blades flaring behind
                               it, the shield, the blade blazing, the slash wave through the line); Voyager Escort (its
                               shield as the fight starts).
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
from build_mightymech import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_mightymech")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_mightymech_fx", "tft_mightymech_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")
OTHERS = [os.path.join(ROOT, "league", "champions", n) for n in ("league_garen", "league_ashe")]
REACH = (P["atk_range"] + 2 * 15000) // 1000   # game px between its pivot and Darius's when it attacks: the range
                                                # plus both units' collision radii
LAND = 22                        # game px short of Darius where the leap comes down (its sword on him)
SPOTS = ((22, -6), (40, 6))      # Garen behind Darius, Ashe further on (game px): in the slash's line
SLASH_Y = 2                      # the slash wave over its soles' line (game px, up negative): along the ground


class Clip(SilcoClip):
    """preview_silco's clip with its own dense frames."""

    def a(self, tag, dur=None, loop=False, z=4):
        fr = list(dense(self.sp, tag, "mightymech", self.z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        return self.play(fr, dur, loop)

    def play(self, fr, dur, loop):
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def scene(out, steps, gap, W=380, H=180, z=4, tail=900, x0=90):
    """One scene (a list of steps) written to `out`."""
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_mightymech_fx"], fx["tft_mightymech_big"]
    gy = H - 34
    far = x0 + gap
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.z = z
    foes = (d,)
    if any(s in steps for s in ("q", "r")):                         # two more enemies by Darius
        foes = (d,) + tuple(Foe(load(p), far + dx, gy + dy) for p, (dx, dy) in zip(OTHERS, SPOTS))
        c.foes = foes[1:]
    c.wait(300)

    def swings():
        """Three attacks: the cut on atk_st, the third the piston chop (its slow at Darius's feet)."""
        for k in range(3):
            at = c.t + tick(P["atk_st"] - 1)
            c.on_foe(d, "a_hit", at)
            if k == 2:
                c.on_foe(d, "a_crush", at)
                c.on_foe(d, "a_slow", at, until=at + tick(P["a3_slow_t"]))
            d.flinches.append(at)
            c.a("attack", tick(P["atk_dur"]))
            c.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def matrix():
        """Gravity Matrix: the field under it for q_t, the taunt marks on the champions near it at the start and
        halfway, the shockwave at the end on every enemy within q_r."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        at = t + tick(P["q_st"] - 1)
        c.on_me("q_stance", at, sheet=c.big, until=at + tick(P["q_t"]), under=True)
        for k in (0, P["q_t"] // 2):
            for f in foes:
                c.on_foe(f, "q_taunt", at + tick(k))
        end = at + tick(P["q_t"] - 1)
        x, y = me.pos(end)
        c.at_spot("q_wave", end, x, y, sheet=c.big, under=True)
        for f in foes:
            if abs(f.pos(end)[0] - x) <= P["q_r"] / 1000 + 15:
                c.on_foe(f, "q_hit", end)
                f.flinches.append(end)
        c.wait(max(0, end - c.t))
        return end + 400

    def leap():
        """Mecha Leap (tft.dll): it leaps over e_air ticks onto Darius and lands: the crater, Darius knocked up."""
        t = c.t
        x = me.pos(t)[0]
        at = t + tick(P["e_st"] - 1)
        land = at + tick(P["e_air"])
        me.moves.append((at, land, x, d.x - LAND))
        c.a("skill2", tick(P["e_dur"]))
        c.at_spot("e_slam", land, d.x - LAND // 2, d.y, sheet=c.big, under=True)
        c.on_foe(d, "e_up", land)
        d.hops.append((land, land + tick(P["e_up"]), 10))
        return land + 600

    def blade():
        """Ultimate Form: Super Blade: the blades flaring behind it and the shield (its form's embers), the blade
        blazing behind it at r_sword, the wave along the line at r_st (r_hit on each enemy it reaches, knocked up)."""
        t = c.t
        c.a("ult", tick(P["r_dur"]))
        c.on_me("r_transform", t, sheet=c.big, under=True)
        c.on_me("r_form", t, until=t + tick(P["r_form"]) // 3)
        c.on_me("p_shield", t, until=t + tick(P["r_sh_t"]) // 3)
        c.on_me("r_sword", t + tick(P["r_sword"] - 1), sheet=c.big, under=True)
        at = t + tick(P["r_st"] - 1)
        x, y = me.pos(at)
        x1 = x + P["r_len"] // 1000
        c.fly("r_slash", at, at + 200, x, x1, y + SLASH_Y, sheet=c.big)
        for f in foes:
            hit = at + int(200 * (f.pos(at)[0] - x) / max(1, x1 - x))
            c.on_foe(f, "r_hit", hit)
            f.hops.append((hit, hit + tick(P["r_up"]), 8))
        return t + tick(P["r_dur"]) + 300

    def escort():
        """Voyager Escort (tft.dll): an enemy champion in sight, its shield for p_t (shown 1.5 s)."""
        t = c.t
        c.on_me("p_shield", t, until=t + 1500)
        c.wait(1500)
        return t + 1500

    for step in steps:
        if step == "walk_in":
            xa = me.pos(c.t)[0]
            t0 = c.t
            t1 = t0 + abs((far - REACH) - xa) / px_tick(P["ms"])
            c.a("run", t1 - t0, loop=True)
            me.moves.append((t0, t1, xa, far - REACH))
        elif step == "attack":
            swings()
        else:
            end = {"q": matrix, "e": leap, "r": blade, "p": escort}[step]()
            c.wait(max(0, end + 200 - c.t))
    c.wait(tail)
    return c.render(out, W, H, c.t, z)


# each skill alone: (caption, steps, Darius's distance, canvas height)
SCENES = [("移动：握着巨剑迈步，两条腿轮流迈步", ["walk_in"], 200, 180),
          ("被动 旅人护航：开战时给自己和生命最低的队友上护盾（自己双倍）", ["p"], REACH, 180),
          ("普攻 活塞重斩：巨剑砍下；每第三下活塞重砸，多打一下并减速", ["attack"], REACH, 180),
          ("技能 引力矩阵：张开刃翼减伤、嘲讽两次、持续回血；结束时冲击波", ["q"], REACH, 200),
          ("技能2 机甲飞跃：跳到冲击后排的敌人身上，落地击飞", ["e"], 120, 190),
          ("大招 究极变形·超级战刃：护盾和双抗，剑核爆燃，劈出剑气击飞一排", ["r"], REACH, 210)]


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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_mightymech_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_mightymech_effects.png")))
    if args.only in (None, "skills"):
        print("skills frames/seconds", skills(os.path.join(args.out, "tft_mightymech_skills.gif")))


if __name__ == "__main__":
    main()
