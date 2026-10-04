#!/usr/bin/env python3
"""Showcase GIF for Kayn, built from the exported game sprites (league/champions/league_kayn and
league/effects/league_kayn_fx), timed like the kit (60 ticks a second).

    python tools/art/preview_kayn.py [--out FILE.gif] [--z 3]

A scripted fight against Garen: Kayn runs in and attacks; Q dashes and spins (the dash trail, the spin ring, the
shadow step under him as he walks back); W winds up on Rhaast's eye and slashes along the ground (the slow on Garen);
R dives into Garen (the mark over his head while Kayn is inside, unseen) and bursts out. Then the Darkin takes him
(the transformation, the red aura): the Darkin attack, W with its spikes and R with the blood burst. Then the Shadow
Assassin (the transformation, the shadow aura): the attack with the shadow strike, W's longer slash and R's burst.
Writes a GIF (one palette) and a key frame PNG beside it.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402

ARENA = T.ARENA_BG
LEAGUE = os.path.join(ROOT, "league")
W, H = 210, 120
GY = 80                     # the pivot row of both units
KX, TX = 70, 140            # Kayn's place, Garen's place
EYE = (0, 0)                # w_wind frames already carry their spot on Rhaast's eye (import_kayn.py): play on the pivot


def tick(n):
    return n * 1000.0 / 60.0


def frames_of(sp, tag):
    return [(sp.frames[i], sp.durations[i]) for i in sp.tag_frames(tag)]


class Anim:
    def __init__(self, fr, t0, x, y, loop=False, until=None, x1=None, z=0, flip=False):
        self.fr, self.t0, self.x, self.y, self.loop, self.z, self.flip = fr, t0, x, y, loop, z, flip
        self.total = sum(ms for _, ms in fr)
        self.until = until if until is not None else (None if loop else t0 + self.total)
        self.x1 = x if x1 is None else x1

    def at(self, t):
        if self.until is None or self.until == self.t0:
            return self.x
        u = min(1.0, max(0.0, (t - self.t0) / (self.until - self.t0)))
        return int(round(self.x + (self.x1 - self.x) * u))

    def frame(self, t):
        if t < self.t0 or (self.until is not None and t >= self.until):
            return None
        dt = t - self.t0
        if self.loop:
            dt %= self.total
        for f, ms in self.fr:
            if dt < ms:
                return f.transpose(Image.FLIP_LEFT_RIGHT) if self.flip else f
            dt -= ms
        return None


def showcase(out, z=3, step=40):
    k = T.load_sprite(os.path.join(LEAGUE, "champions", "league_kayn"))
    fx = T.load_sprite(os.path.join(LEAGUE, "effects", "league_kayn_fx"))
    g = T.load_sprite(os.path.join(LEAGUE, "champions", "league_garen"))
    names = {t["name"] for t in fx.tags}

    def F(tag):
        return frames_of(fx, tag) if tag in names else [(Image.new("RGBA", (1, 1)), 100)]

    body, under, over, foe = [], [], [], []
    t = 0.0
    x = KX

    def act(tag, dur=None, loop=False, to=None):
        nonlocal t, x
        a = Anim(frames_of(k, tag), t, x, GY, loop=loop, until=(t + dur) if dur else None, x1=to)
        a.tag = tag
        body.append(a)
        t = a.until
        if to is not None:
            x = to

    def fxat(tag, at, px, py=GY, ground=False, loop=False, until=None):
        (under if ground else over).append(Anim(F(tag), at, px, py, loop=loop, until=until))

    def hurt(at, tag=None):
        foe.append(Anim(frames_of(g, "hit"), at, TX, GY, flip=True))
        if tag:
            fxat(tag, at, TX)

    def attack(form):
        pre = {"base": "", "darkin": "rh_", "shadow": "sh_"}[form]
        s = t
        act(pre + "attack")
        hurt(s + tick(10), {"base": "hit", "darkin": "hit_d", "shadow": "hit_s"}[form])
        if form == "shadow":
            fxat("sa_hit", s + tick(11), TX)
        act("idle", tick(30), loop=True)

    def skill2(form):
        pre = {"base": "", "darkin": "rh_", "shadow": "sh_"}[form]
        s = t
        act(pre + "skill2")
        fxat({"base": "w_wind", "darkin": "w_wind_d", "shadow": "w_wind_s"}[form], s, x + EYE[0], GY + EYE[1])
        line = {"base": ("w_line", 62), "darkin": ("w_line_d", 62), "shadow": ("w_line_s", 80)}[form]
        fxat(line[0], s + tick(33), x + line[1] // 2, ground=True)
        hurt(s + tick(34), "w_hit")
        fxat("w_slow", s + tick(34), TX, loop=True, until=s + tick(34 + 60))
        act("idle", tick(30), loop=True)

    def ult(form):
        pre = {"base": "", "darkin": "rh_", "shadow": "sh_"}[form]
        nonlocal x
        s = t
        fxat("r_dive", s, x, ground=True)
        act("ult", tick(12), to=TX - 8)
        fxat("r_enter", t, TX)
        mark = {"base": "r_mark", "darkin": "r_mark_d", "shadow": "r_mark_s"}[form]
        fxat(mark, t, TX, loop=True, until=t + tick(60))
        act("r_hidden", tick(60))
        s = t
        x = TX - 26
        act(pre + "ult_exit")
        hurt(s, {"base": "r_exit", "darkin": "r_exit_d", "shadow": "r_exit_s"}[form])
        act("run", tick(30), loop=True, to=KX)
        act("idle", tick(20), loop=True)

    # base Kayn: run in, attack, Q, W, R
    act("run", 900, loop=True, to=KX)
    x = KX
    body[-1].x = KX - 60
    act("idle", 300, loop=True)
    attack("base")
    s = t                                                     # Q: an 8-tick dash, the spin at tick 12
    fxat("q_dash", s, x, ground=True)
    act("skill", to=x + 24)
    fxat("q_spin", s + tick(12), x)
    hurt(s + tick(13), "q_hit")
    under.append(Anim(F("ghost"), t, x, GY, loop=True, until=t + 700, x1=KX))
    act("run", 700, loop=True, to=KX)
    act("idle", tick(20), loop=True)
    skill2("base")
    ult("base")
    # the Darkin
    fxat("tf_d", t, x)
    act("transform")
    under.append(Anim(F("form_d"), t - 700, KX, GY, loop=True, until=1e9))
    under[-1].aura = True
    act("idle", tick(20), loop=True)
    aura_d = under[-1]
    attack("darkin")
    skill2("darkin")
    ult("darkin")
    aura_d.until = t
    # the Shadow Assassin
    fxat("tf_s", t, x)
    act("transform")
    under.append(Anim(F("form_s"), t - 700, KX, GY, loop=True, until=1e9))
    under[-1].aura = True
    act("idle", tick(20), loop=True)
    aura_s = under[-1]
    attack("shadow")
    skill2("shadow")
    ult("shadow")
    act("idle", 600, loop=True)
    aura_s.until = t
    end = t

    gidle = frames_of(g, "idle")

    def foe_frame(tt):
        for a in foe:
            f = a.frame(tt)
            if f is not None:
                return f
        dt = tt % sum(ms for _, ms in gidle)
        for f, ms in gidle:
            if dt < ms:
                return f.transpose(Image.FLIP_LEFT_RIGHT)
            dt -= ms

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px - f.width // 2), int(py - f.height // 2)))

    frames, tt = [], 0.0
    key = []
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        ImageDraw.Draw(img).line([(0, GY + 12), (W, GY + 12)], fill=(120, 132, 100, 255))
        cur = next((a for a in body if a.frame(tt) is not None), None)
        for a in under:
            f = a.frame(tt)
            if f is None:
                continue
            if getattr(a, "aura", False):          # the form's aura rides with him and hides while he is inside a foe
                if cur is None or cur.tag == "r_hidden":
                    continue
                place(img, f, cur.at(tt), a.y)
            else:
                place(img, f, a.at(tt), a.y)
        place(img, foe_frame(tt), TX, GY)
        for a in body:
            f = a.frame(tt)
            if f is not None:
                place(img, f, a.at(tt), GY)
                break
        for a in over:
            f = a.frame(tt)
            if f is not None:
                place(img, f, a.at(tt), a.y)
        big = img.resize((W * z, H * z), Image.NEAREST).convert("RGB")
        frames.append(big)
        tt += step
    sample = frames[::6]
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0)
    # key frames: every 10th frame
    sel = frames[::max(1, len(frames) // 24)][:24]
    cols = 6
    sheet = Image.new("RGB", (cols * W * 2, -(-len(sel) // cols) * H * 2), (40, 40, 48))
    for i, f in enumerate(sel):
        sheet.paste(f.resize((W * 2, H * 2), Image.NEAREST), ((i % cols) * W * 2, (i // cols) * H * 2))
    sheet.save(T.long_path(out[:-4] + "_key.png"))
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview", "league_kayn_showcase.gif"))
    ap.add_argument("--z", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(os.path.dirname(T.long_path(a.out)) if hasattr(T, "long_path") else os.path.dirname(a.out), exist_ok=True)
    n, secs = showcase(a.out, a.z)
    print(a.out, n, "frames", secs, "s")


if __name__ == "__main__":
    main()
