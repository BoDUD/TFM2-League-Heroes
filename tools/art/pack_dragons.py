"""Step-1 Codex pack for the Rift's epic monsters of our league_dragons add-on: one FRONT-VIEW design picture each for
Baron Nashor (纳什男爵, drawn over the game's Morgard = asset ingame/epic) and the six elemental drakes + the Elder
Dragon (炼狱 / 山脉 / 海洋 / 云端 / 海克斯 / 化学科技亚龙, 远古巨龙: skins of the game's Serpen = asset ingame/serpen,
chosen on screen by the marker buff league_dragons_el_<element>). The user, 2026-11-09: 「大小龙模型呢？codex做吗 还有攻击动画」.

    python tools/art/pack_dragons.py --out <dir> --prompt <DRAGONS_PROMPT_1.md> [--lol "D:/Riot Games/League of
        Legends"] [--only [model ...]]

Writes <out>/refs/<model>/ (League renders of the Rift monster itself from Map11.wad.client - mesh, skeleton, colour
map and its own animation graph: 1 front = THE pose to draw, 2 head close-up from the front, 3 a 3/4 view for the
details, 4 the layout guide; Riot's, kept local, never committed), <out>/native/ (the game's Serpen and Morgard frame by
frame at 4x with their pivot, and a scale overview at game size: what the new models replace, how big they are),
<out>/style/ (this pack's own sprites at 8x: style only), <out>/SPEC.json (canvas, squares, target boxes, the native
tags each model's sheet must carry), the prompt, then <out>.zip.

The game facts (bundle.game_data, read 2026-11-09; tools/../.claude/skills/tfm2-hero-mod/scripts/tfm2_ase.py):
- Both natives face the viewer (front view) and stand still. Every frame of a sheet is centred on the unit's position
  (the pivot = the frame's centre pixel).
- Morgard (ingame/epic): idle 4 x 160 ms (a breath: top -65 / -63 / -61 / -63), base = idle frame 1, attack_left
  5 x 80 ms, attack_right 5 x 80 ms = attack_left mirrored about x = -0.5 EXACTLY (and idle is mirror-symmetric too),
  attack_target_effect 7 x 60 ms (claw marks drawn on the target), dead 13 x 60 ms (turns to grey stone from the
  feet up, then shatters into flying pieces). Figure x -53..+52, y -65..+55 (106 x 121 game px; dead pieces to +-94).
  epic_jungle attack: action attack_left, duration 24 ticks, hit at tick 18 (= 300 ms: frame 3), range 80000.
- Serpen (ingame/serpen): idle 4 x 160 ms (top -35 / -33 / -30 / -33), base = idle frame 1, attack 5 x 80 ms (a
  tail sweep all round + a grey shockwave ring of ~110 px radius, frames up to 227 x 225), dead 8 x 80 ms (rears up,
  turns grey, dissolves in scan lines, last frame empty). No hit tag. Figure x -28..+25, y -35..+37 (54 x 73).
  serpen_jungle attack: action attack, duration 24 ticks, hit at tick 18 (frame 3), range 80000.
Our sizes keep each native's footprint and bottom line (drakes 72 x 64, the Elder 84 x 72, both standing on the
Serpen's bottom row +37; Baron 100 x 120 on Morgard's +55, mirror-symmetric about x = -0.5) and this pack's density
(dense PPU like the hero batches: the dragons 1.8 = the heroes' own square size on screen, Baron 1.5 - see KINDS).
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
sys.path.insert(0, os.path.join(REPO, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import anim_graph as G  # noqa: E402
import pose_ref as P  # noqa: E402
from riot import Wad  # noqa: E402

GREY = (225, 225, 225)
ARENA = (92, 98, 86)                   # tfm2_ase's arena floor colour
MAP11 = ("Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client")
STANCE = 12437627865425093600          # every drake's and the Elder's graph: standing on all fours, wings half raised
BARON_IDLE = 1126220602055605983       # sru_baron idle1_base (4.0 s)
# model -> (character folder, mesh stem (.skn / .skl), colour map, idle clip, head joints). Infernal, Mountain and Cloud
# share sru_dragon_air's mesh and skeleton (only the colour maps differ); Ocean, Hextech and Chemtech have their own
# meshes on the same skeleton; the Elder its own; Baron is the 2024 base model (SRU_Baron_Base, 131 joints).
MODELS = {
    "baron": ("sru_baron", "ASSETS/Characters/SRU_Baron/Skins/Base/SRU_Baron_Base",
              "ASSETS/Characters/SRU_Baron/Skins/Base/Baron_Base_TX_CM.tex", BARON_IDLE,
              ("Head1", "Head2", "JawTop", "JawBot", "L_Head2", "L_Head3", "L_Head4", "L_Head5", "L_HeadJawBot",
               "L_HeadJawTop", "R_Head2", "R_Head3", "R_Head4", "R_Head5", "R_HeadJawBot", "R_HeadJawTop")),
    "infernal": ("sru_dragon_fire", "ASSETS/Characters/sru_dragon_air/skins/base/SRU_Dragon_Air",
                 "assets/characters/sru_dragon_fire/skins/base/sru_dragon_fire_tx_cm.tex", STANCE, ("Head", "Jaw")),
    "mountain": ("sru_dragon_earth", "ASSETS/Characters/sru_dragon_air/skins/base/SRU_Dragon_Air",
                 "assets/characters/sru_dragon_earth/skins/base/sru_dragon_earth_tx_cm_2.tex", STANCE, ("Head", "Jaw")),
    "ocean": ("sru_dragon_water", "ASSETS/Characters/sru_dragon_water/Skins/Base/SRU_Dragon_Water",
              "assets/characters/sru_dragon_water/skins/base/sru_dragon_water_tx_cm.tex", STANCE, ("Head", "Jaw")),
    "cloud": ("sru_dragon_air", "ASSETS/Characters/sru_dragon_air/skins/base/SRU_Dragon_Air",
              "assets/characters/sru_dragon_air/skins/base/sru_dragon_air_tx_cm.tex", STANCE, ("Head", "Jaw")),
    "hextech": ("sru_dragon_hextech", "ASSETS/Characters/sru_dragon_hextech/Skins/Base/sru_dragon_hextech",
                "assets/characters/sru_dragon_hextech/skins/base/sru_dragon_hextech_tx_cm.tex", STANCE,
                ("Head", "Jaw")),
    "chemtech": ("sru_dragon_chemtech", "ASSETS/Characters/SRU_Dragon_ChemTech/skins/base/sru_dragon_chemtech",
                 "assets/characters/sru_dragon_chemtech/skins/base/sru_dragon_chemtech_tx_cm.tex", STANCE,
                 ("Head", "Jaw")),
    "elder": ("sru_dragon_elder", "ASSETS/Characters/SRU_Dragon_Elder/Skins/Base/SRU_Dragon_Elder",
              "assets/characters/sru_dragon_elder/skins/base/sru_dragon_elder_tx_cm.tex", STANCE, ("Head", "Jaw")),
}
DRAKES = ("infernal", "mountain", "ocean", "cloud", "hextech", "chemtech")
PITCH = 25                             # the PPU hero batches' camera pitch (poses.json)
# the Codex picture of each kind: canvas, square px, squares a game pixel (PPU), the figure's target in GAME px (w at
# most, h) and its bottom row relative to the pivot (the native's), the canvas row of the soles / pit line, the canvas
# column of the centre
KINDS = {
    "drake": dict(canvas=(1536, 1024), sq=6, ppu=1.8, game_w=72, game_h=64, bottom=37, sole_y=960, centre_x=768,
                  native="serpen", tags="serpen"),
    "elder": dict(canvas=(1536, 1024), sq=6, ppu=1.8, game_w=84, game_h=72, bottom=37, sole_y=960, centre_x=768,
                  native="serpen", tags="serpen"),
    "baron": dict(canvas=(1024, 1536), sq=6, ppu=1.5, game_w=100, game_h=120, bottom=55, sole_y=1470, centre_x=510,
                  native="epic", tags="epic"),
}
# (every line and the centre on a square edge of the canvas's own 6-px grid: 960 = 160 x 6, 768 = 128 x 6, 1470 =
# 245 x 6, 510 = 85 x 6 - Baron's mirror axis falls between two squares, as Morgard's does between two pixels. Baron
# at PPU 1.5: 180 rows, not 216 - Codex's own drawings hold ~70-130 rows a figure (batch 6 raws: ~16 px squares on
# 1254 = 71 rows; the tft Elder's 7.5 px = 125 rows), so asking 216 would only be read back coarser anyway)
KIND = {"baron": "baron", "elder": "elder", **{d: "drake" for d in DRAKES}}
# the native sheets' tags our sheets keep (names, counts, durations, hit frame) - read from the bundle 2026-11-09
TAGS = {
    "serpen": [("idle", 4, 160, "breath: up / mid / down / mid (native tops -35 -33 -30 -33)"),
               ("base", 1, 100, "= idle frame 1"),
               ("attack", 5, 80, "hit at tick 18 of 24 = 300 ms = frame 3; native: tail sweep all round + grey ring "
                                 "~110 px radius (frames up to 227 x 225)"),
               ("dead", 8, 80, "native: rears up, turns grey, dissolves in scan lines; frame 7 EMPTY")],
    "epic": [("idle", 4, 160, "breath (native tops -65 -63 -61 -63); mirror-symmetric"),
             ("base", 1, 100, "= idle frame 1"),
             ("attack_left", 5, 80, "hit at tick 18 of 24 = 300 ms = frame 3; strikes toward image left"),
             ("attack_right", 5, 80, "= attack_left mirrored about x = -0.5, exactly (native)"),
             ("attack_target_effect", 7, 60, "impact drawn ON THE TARGET (native: purple claw marks, 31-51 x 33-41)"),
             ("dead", 13, 60, "native: grey stone from the feet up (frames 3-8), shatters into flying pieces (9-12)")],
}
STYLE = {   # name -> (pack folder, sheet, tag): this pack's sprites, hd frame 0 at 8x
    "1_style_daeja.png": ("tft", "tft_daeja", "hd_idle"),
    "2_style_elderdragon.png": ("tft", "tft_elderdragon", "hd_idle"),
    "3_style_riftherald.png": ("tft", "tft_riftherald", "hd_idle"),
    "4_style_kogmaw.png": ("league", "league_kogmaw", "hd_idle"),
}


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def target(kind):
    """The figure's target on the Codex canvas (rows, max columns, px tall, max px wide, top row) and in the game: its
    1x box relative to the pivot (x0, y0, x1, y1 inclusive; Baron's axis at x = -0.5 like Morgard's) and the odd frame
    size, centred on the pivot, that holds it standing (+1 row for the breath); hd frames are PPU times as big."""
    k = KINDS[kind]
    rows, cols = round(k["game_h"] * k["ppu"]), round(k["game_w"] * k["ppu"])
    w, h = k["game_w"], k["game_h"]
    box = (-(w // 2), k["bottom"] - h + 1, w - w // 2 - 1, k["bottom"])
    hw, hh = max(-box[0], box[2]) + 1, max(-box[1], box[3]) + 1
    return dict(rows=rows, cols=cols, px_h=rows * k["sq"], px_w=cols * k["sq"], top_y=k["sole_y"] - rows * k["sq"],
                box_1x=box, frame_1x=(2 * hw + 1, 2 * hh + 1),
                frame_hd=(2 * round(hw * k["ppu"]) + 1, 2 * round(hh * k["ppu"]) + 1))


class Model:
    """A Rift monster: its mesh on its own skeleton, one colour map, the atomic clips of its animation graph."""

    def __init__(self, lol, name):
        folder, mesh, tex, self.idle, heads = MODELS[name]
        self.name = name
        self.w = Wad(os.path.join(lol, *MAP11))
        b = self.w.read_path(mesh + ".skn")
        self.tris, self.v = P.read_skn(b)
        self.tex = P.read_tex(self.w.read_path(tex.lower()))
        self.joints, self.infl = P.read_skl(self.w.read_path((mesh + ".skl").lower()))
        bind = P.globals_(self.joints, [P.trs(j["t"], j["r"], j["s"]) for j in self.joints])
        self.bind_inv = [np.linalg.inv(m) for m in bind]
        names = [j["name"] for j in self.joints]
        heads = {names.index(n) for n in heads if n in names}
        top = np.array(self.infl)[self.v["bones"].astype(np.int64)][np.arange(len(self.v)), np.argmax(self.v["w"], 1)]
        self.head = np.isin(top, list(heads))
        self.clips = {}
        for _cls, fields in G.parse_prop(self.w.read_path(f"data/characters/{folder}/animations/skin0.bin")):
            for key, clip in fields.get("mClipDataMap") or []:
                res = (clip or {}).get("mAnimationResourceData")
                if isinstance(res, dict) and isinstance(res.get("mAnimationFilePath"), int):
                    self.clips[key] = res["mAnimationFilePath"]

    def posed(self, clip, ms):
        if clip is None:                       # the bind pose (Baron's is mirror-symmetric to the pixel)
            glob = P.globals_(self.joints, [P.trs(j["t"], j["r"], j["s"]) for j in self.joints])
            return P.skin(self.v, self.infl, self.bind_inv, glob)
        anim = P.read_anim(self.w.read(clip))
        local = P.local_pose(self.joints, anim, min(ms / 1000.0, max(anim["duration"] - 1e-3, 0.0)))
        glob = P.globals_(self.joints, [P.trs(*p) for p in local])
        return P.skin(self.v, self.infl, self.bind_inv, glob)


def rotated(pv, yaw, pitch):
    """render_hq's own camera transform (x right, y up on the image)."""
    cy, sy = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))
    cp, sp = np.cos(np.radians(pitch)), np.sin(np.radians(pitch))
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    return pv @ (rx @ ry).T


def view(m, yaw, pitch=PITCH, size=1400, head=False, margin=0.06, bind=False):
    """The idle pose (or the bind pose) rendered with the world ground kept (Baron: everything under it - his column
    in the pit - left out), fitted to its projected box (or its head's) with a margin, on transparent."""
    pv = m.posed(None if bind else m.idle, 0.0)
    tris = m.tris
    if m.name == "baron":
        tris = tris[pv[tris].mean(1)[:, 1] >= 0.0]
        used = np.unique(tris)
    else:
        pv = pv - np.array([0.0, pv[:, 1].min(), 0.0])
        used = np.arange(len(pv))
    v = rotated(pv, yaw, pitch)
    sel = v[np.intersect1d(used, np.nonzero(m.head)[0])] if head else v[used]
    x0, x1, y0, y1 = sel[:, 0].min(), sel[:, 0].max(), sel[:, 1].min(), sel[:, 1].max()
    scale = size * (1 - 2 * margin) / max(x1 - x0, y1 - y0)
    shift = -(x0 + x1) / 2 * scale / size
    ground = size / 2 + (y0 + y1) / 2 * scale
    im = P.render_hq(pv, tris, m.v["uv"], m.tex, yaw, pitch, (size, size), scale, ground, shift=shift)
    return im


def on_grey(im, crop=True, pad=0.05):
    if crop:
        x0, y0, x1, y1 = im.getbbox()
        mg = int(max(x1 - x0, y1 - y0) * pad)
        im = im.crop((max(0, x0 - mg), max(0, y0 - mg), min(im.width, x1 + mg), min(im.height, y1 + mg)))
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    return can.convert("RGB")


def guide(front, kind, name, path):
    """The layout guide: the front render as a flat silhouette at the target height (layout only - the drawing is
    chibi, its width comes from the square counts), soles / pit line dark grey, the top line light grey, the widest the
    figure may go as light dashed verticals, the centre (Baron: the mirror axis) as a thin line."""
    k, t = KINDS[kind], target(kind)
    cw, ch = k["canvas"]
    a = front.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    bb = a.getbbox()
    a = a.crop(bb)
    s = t["px_h"] / a.height
    a = a.resize((max(1, round(a.width * s)), t["px_h"]), Image.NEAREST)
    sil = Image.new("RGBA", a.size, (150, 160, 185, 255))
    sil.putalpha(a)
    can = Image.new("RGBA", (cw, ch), GREY + (255,))
    can.alpha_composite(sil, (k["centre_x"] - a.width // 2, k["sole_y"] - t["px_h"]))
    d = ImageDraw.Draw(can)
    d.line([(0, k["sole_y"]), (cw, k["sole_y"])], fill=(110, 110, 110, 255), width=2)
    d.line([(0, t["top_y"]), (cw, t["top_y"])], fill=(190, 190, 190, 255), width=1)
    for x in (k["centre_x"] - t["px_w"] // 2, k["centre_x"] + t["px_w"] // 2):
        for y in range(t["top_y"], k["sole_y"], 16):
            d.line([(x, y), (x, y + 8)], fill=(185, 185, 185, 255), width=1)
    d.line([(k["centre_x"], t["top_y"] - 24), (k["centre_x"], k["sole_y"] + 24)], fill=(200, 200, 200, 255), width=1)
    what = "the pit line (where the body leaves the ground)" if kind == "baron" else "the soles (lowest claws)"
    d.text((20, 16), f"{name}: {what} dark line y={k['sole_y']}; top light line y={t['top_y']} = {t['px_h']} px "
                     f"({t['rows']} squares of {k['sq']} px)", fill=(60, 60, 60, 255))
    d.text((20, 32), f"widest at most {t['px_w']} px ({t['cols']} squares) between the dashed lines; centre "
                     f"x={k['centre_x']}{' = the mirror axis' if kind == 'baron' else ''}; layout only (the silhouette "
                     f"is the 3D model's, the drawing is chibi)", fill=(60, 60, 60, 255))
    can.convert("RGB").save(path)
    return dict(silhouette_px=[a.width, a.height], silhouette_squares=[round(a.width / k["sq"]), t["rows"]])


def native_sheet(sp, tags, path, z=4):
    """The native frames, one row a tag, every cell of a row the union box of that tag's frames (+2 px) at z, the
    pivot (the unit's position) as a red cross."""
    rows = []
    for t in tags:
        idx = sp.tag_frames(t)
        boxes = [sp.frames[i].getbbox() for i in idx if sp.frames[i].getbbox()]
        bb = (min(b[0] for b in boxes) - 2, min(b[1] for b in boxes) - 2, max(b[2] for b in boxes) + 2,
              max(b[3] for b in boxes) + 2)
        bb = (min(bb[0], sp.w // 2 - 3), min(bb[1], sp.h // 2 - 3),             # the pivot always inside
              max(bb[2], sp.w // 2 + 4), max(bb[3], sp.h // 2 + 4))
        for k in range(0, len(idx), 7):          # at most 7 cells a row (Morgard's dead has 13)
            rows.append((t, idx[k:k + 7], bb, k))
    lab = 16
    width = max(len(idx) * ((bb[2] - bb[0]) * z + 4) for _, idx, bb, _ in rows)
    out = Image.new("RGB", (width, sum((bb[3] - bb[1]) * z + lab + 4 for _, _, bb, _ in rows)), (205, 205, 205))
    d = ImageDraw.Draw(out)
    y = 0
    for t, idx, bb, first in rows:
        w, h = (bb[2] - bb[0]) * z, (bb[3] - bb[1]) * z
        for c, i in enumerate(idx):
            x0, y0 = c * (w + 4), y + lab
            cell = Image.new("RGBA", (w, h), ARENA + (255,))
            cell.alpha_composite(sp.frames[i].crop(bb).resize((w, h), Image.NEAREST))
            out.paste(cell.convert("RGB"), (x0, y0))
            px, py = x0 + (sp.w // 2 - bb[0]) * z + z // 2, y0 + (sp.h // 2 - bb[1]) * z + z // 2
            d.line([(px - 6, py), (px + 6, py)], fill=(255, 0, 0))
            d.line([(px, py - 6), (px, py + 6)], fill=(255, 0, 0))
            d.text((x0 + 2, y0 - lab + 2), f"{t} {first + c}  {sp.durations[i]} ms", fill=(0, 0, 0))
        y += h + lab + 4
    out.save(path)


def sheet_frame(pack, sheet, tag, z=None):
    stem = os.path.join(REPO, pack, "champions", sheet)
    f = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"][tag]["frames"][0]["data"]
    im = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    im = im.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    if z is None:
        return im
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    pad.alpha_composite(im, (2, 2))
    return pad.convert("RGB").resize((pad.width * z, pad.height * z), Image.NEAREST)


def scale_overview(serpen, epic, path, z=3):
    """At game size x z on the arena colour, all standing on one line: Morgard and Serpen (the natives), two heroes
    (1x idle frame 0), this pack's tft Elder Dragon and Baron (1x), and the target boxes of the new models."""
    items = []
    frames = [("Morgard (native)", epic.frames[epic.tag_frames("idle")[0]]),
              ("Serpen (native)", serpen.frames[serpen.tag_frames("idle")[0]])]
    for lab, pack, sheet in (("Jinx (hero)", "league", "league_jinx"), ("Garen (hero)", "league", "league_garen"),
                             ("tft Elder Dragon", "tft", "tft_elderdragon"), ("tft Baron", "tft", "tft_baronnashor")):
        frames.append((lab, sheet_frame(pack, sheet, "idle")))
    for lab, im in frames:                      # each cut to its figure: the lowest row stands on the floor
        im = im.crop(im.getbbox())
        items.append((lab, im, im.height - 1))
    boxes = [("NEW Baron 100x120", 100, 120), ("NEW drake 72x64", 72, 64), ("NEW Elder 84x72", 84, 72)]
    gap, lab_h = 10, 30
    width = sum(im.width for _, im, _ in items) + sum(w for _, w, _ in boxes) + gap * (len(items) + len(boxes) + 1)
    height = 135
    out = Image.new("RGBA", (width * z, (height + lab_h) * z), ARENA + (255,))
    d = ImageDraw.Draw(out)
    floor = height
    x = gap
    for lab, im, bottom in items:
        out.alpha_composite(im.resize((im.width * z, im.height * z), Image.NEAREST), (x * z, (floor - bottom - 1) * z))
        d.text((x * z, (floor + 4) * z), lab, fill=(255, 255, 255, 255))
        x += im.width + gap
    for lab, w, h in boxes:
        d.rectangle([x * z, (floor - h) * z, (x + w) * z - 1, floor * z - 1], outline=(255, 230, 120, 255), width=2)
        d.text((x * z + 4, (floor - h) * z + 4), lab, fill=(255, 230, 120, 255))
        x += w + gap
    d.line([(0, floor * z), (width * z, floor * z)], fill=(40, 40, 40, 255), width=1)
    out.convert("RGB").save(path)


def overview(out, h=360):
    """<out>/0_overview.png: the eight front renders in one row, labelled with the picture each one is for."""
    names = list(DRAKES) + ["elder", "baron"]
    ims = []
    for n in names:
        im = Image.open(os.path.join(out, "refs", n, f"1_{n}_front.png")).convert("RGB")
        ims.append((n, im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)))
    sheet = Image.new("RGB", (sum(im.width + 8 for _, im in ims), h + 22), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    x = 0
    for n, im in ims:
        sheet.paste(im, (x, 22))
        d.text((x + 4, 5), f"{'drake_' + n if n in DRAKES else n}-A.png", fill=(0, 0, 0))
        x += im.width + 8
    sheet.save(os.path.join(out, "0_overview.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompt", required=True, help="the prompt document copied into the pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    ap.add_argument("--only", nargs="*", default=None, help="render these models only (refs of the others kept)")
    a = ap.parse_args()
    for d in ("refs", "native", "style"):
        os.makedirs(os.path.join(a.out, d), exist_ok=True)
    spec = {"pitch": PITCH, "kinds": {}, "models": {}}
    for kind in KINDS:
        spec["kinds"][kind] = {**KINDS[kind], **target(kind), "tags": TAGS[KINDS[kind]["tags"]]}
    for name in MODELS:
        kind = KIND[name]
        folder = os.path.join(a.out, "refs", name)
        os.makedirs(folder, exist_ok=True)
        info = {"kind": kind, "lol_character": MODELS[name][0], "idle_clip": str(MODELS[name][3])}
        os.makedirs(a.out + ".cache", exist_ok=True)
        kept = os.path.join(a.out + ".cache", f"{name}.json")      # beside the pack, not in it
        if a.only is None or name in a.only:
            m = Model(a.lol, name)
            # Baron: the design is mirror-symmetric (Morgard's attack_right is attack_left mirrored), so its front and
            # head come from the bind pose - straight, facing the viewer, symmetric to the pixel - and its idle (which
            # sways, the head turned a little) is shown beside it for the resting claws
            bind = name == "baron"
            front = view(m, 0, bind=bind)
            on_grey(front).save(os.path.join(folder, f"1_{name}_front.png"))
            on_grey(view(m, 0, size=1000, head=True, margin=0.2 if bind else 0.12, bind=bind), crop=False).save(
                os.path.join(folder, f"2_{name}_head.png"))
            on_grey(view(m, 35, size=1200)).save(os.path.join(folder, f"3_{name}_34.png"))
            info.update(guide(front, kind, name, os.path.join(folder, f"4_{name}_layout.png")))
            if bind:
                on_grey(view(m, 0)).save(os.path.join(folder, f"5_{name}_idle_front.png"))
            json.dump(info, open(kept, "w", encoding="utf-8"), indent=1)
            print(name, "rendered")
        elif os.path.exists(kept):
            info = json.load(open(kept, encoding="utf-8"))
        spec["models"][name] = info
    overview(a.out)
    import tfm2_ase as T
    serpen = T.load_sprite("asset/base/aseprite_resources/ingame/serpen")
    epic = T.load_sprite("asset/base/aseprite_resources/ingame/epic")
    native_sheet(serpen, ["idle", "base", "attack", "dead"], os.path.join(a.out, "native", "serpen_frames_4x.png"))
    native_sheet(epic, ["idle", "base", "attack_left", "attack_right", "attack_target_effect", "dead"],
                 os.path.join(a.out, "native", "morgard_frames_4x.png"))
    for nm, sp in (("serpen", serpen), ("morgard", epic)):
        im = sp.frames[sp.tag_frames("idle")[0]]
        im = im.crop(im.getbbox())
        pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
        pad.alpha_composite(im, (2, 2))
        pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(
            os.path.join(a.out, "native", f"{nm}_idle_8x.png"))
    scale_overview(serpen, epic, os.path.join(a.out, "native", "scale_overview_3x.png"))
    spec["natives"] = {
        "serpen": {"asset": "asset/base/aseprite_resources/ingame/serpen", "canvas": [serpen.w, serpen.h],
                   "figure_idle0_rel_pivot": [-28, -35, 25, 37], "size": [54, 73]},
        "epic": {"asset": "asset/base/aseprite_resources/ingame/epic", "canvas": [epic.w, epic.h],
                 "figure_idle0_rel_pivot": [-53, -65, 52, 55], "size": [106, 121]},
    }
    for fn, (pack, sheet, tag) in STYLE.items():
        sheet_frame(pack, sheet, tag, 8).save(os.path.join(a.out, "style", fn))
    json.dump(spec, open(os.path.join(a.out, "SPEC.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    shutil.copyfile(a.prompt, os.path.join(a.out, os.path.basename(a.prompt)))
    zp = shutil.make_archive(a.out, "zip", a.out)      # the files at the zip's root, as the earlier packs
    print("written", zp)


if __name__ == "__main__":
    main()
