"""Three Codex packs from the 2026-10-18 in-game review (the user: 「船长猴子阿克尚波比蛇女像素太高需要降低 船长猴子局内太大 还有走路很僵硬
姿势也很僵硬 特别猴子非常奇怪 身形又大走路又奇怪」, 「猴子在局内很奇怪啊 走路了 平A 放技能 都像一个僵尸」, 「船长走路也有点僵硬的」,
「阿克尚怎么体型这么胖？」 -> 「阿克尚让 Codex 按英雄联盟的身材重画瘦一点的定稿，动作照新定稿重做；和船长走路、猴子重做的提示词包一起写好发给
Codex」):

- akshan_slim_pack: Akshan's design redrawn slimmer on the game grid at his new PPU 1.2 (38 game rows hair to soles = 46
  squares): the same pose, costume and colours as the approved design, League's slim build (his chest and hips were
  26-29 game px wide, the pack's other marksmen 12-24: the step-1 read-back was cut by rows only and Codex drew a thick
  cape and tabard).
- gangplank_run_swap_pack: Gangplank's walk as a Codex skin swap over oppi's Swain run (Akshan's accepted way, memory
  swain-session / akshan-session): image 1 oppi's 8 frames scaled to his design's 62 rows hat to soles, image 2 the design,
  image 3 League's Gangplank run.
- wukong_redo_pack: a new Wukong design on the game grid at PPU 1.2 and 85 % (32 game rows hair to soles = 39 squares):
  League's idle (monkeyking_idle1 ~2.4 s: a wide low stance, the staff held level across the chest in both hands, the tail
  curled up) instead of the old pose (both empty hands reaching forward, the staff standing apart - every action was
  that pose moved whole, 「像一个僵尸」); costume and colours from the old design.

    python tools/art/pack_redo_1018.py [--lol D:/WeGameApps/lol]

Writes ak/dist/redo_packs/<pack>.zip (prompt + pictures). League's renders and oppi's frames stay out of the repo.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
AK = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(AK, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402

SRC = os.path.join(AK, "assets", "source")
CHAMPS = os.path.join(AK, "league", "champions")
DIST = os.path.join(AK, "dist", "redo_packs")
TMP = "C:/t/ak_work/redo"
REFS = os.path.join(TMP, "refs")
OPPI_SWAIN = r"D:/steam/steamapps/workshop/content/3009300/3774304166/champions/swain.aseprite"
GREY = (225, 225, 225)
PX, CANVAS, SOLE_Y = 10, 1254, 1200


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def rgba(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA"))


def trim(a):
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def on_grey(a, k=8, pad=2):
    """Squares at k x on light grey (one square = k pixels)."""
    can = Image.new("RGBA", (a.shape[1] + 2 * pad, a.shape[0] + 2 * pad), GREY + (255,))
    can.alpha_composite(Image.fromarray(a), (pad, pad))
    return can.convert("RGB").resize((can.width * k, can.height * k), Image.NEAREST)


def sheet_frame(hero, tag, i=0):
    anims = json.load(open(lp(os.path.join(CHAMPS, f"league_{hero}#anim.fanim")), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][i]["data"]
    sh = Image.open(lp(os.path.join(CHAMPS, f"league_{hero}#sheet.png"))).convert("RGBA")
    return trim(np.asarray(sh.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))))


def strip(hero, tag, k=6):
    """Every frame of a sheet tag side by side at k x on grey (what the game shows now)."""
    anims = json.load(open(lp(os.path.join(CHAMPS, f"league_{hero}#anim.fanim")), encoding="utf-8-sig"))["anims"]
    fr = [sheet_frame(hero, tag, i) for i in range(len(anims[tag]["frames"]))]
    H = max(f.shape[0] for f in fr)
    W = sum(f.shape[1] + 4 for f in fr) + 4
    can = Image.new("RGBA", (W, H + 4), GREY + (255,))
    x = 4
    for f in fr:
        can.alpha_composite(Image.fromarray(f), (x, 2 + H - f.shape[0]))
        x += f.shape[1] + 4
    return can.convert("RGB").resize((can.width * k, can.height * k), Image.NEAREST)


def render_frame(src, n, i):
    """Frame i of an n-frame pose_ref strip, cropped round the figure."""
    im = Image.open(src).convert("RGB")
    w = im.width // n
    c = np.asarray(im.crop((i * w, 0, (i + 1) * w, im.height - 22))).astype(int)
    bg = c[3, 3]
    m = np.abs(c - bg).sum(2) > 24
    ys, xs = np.nonzero(m)
    pad = 12
    return Image.fromarray(c.astype(np.uint8)).crop((max(0, xs.min() - pad), max(0, ys.min() - pad),
                                                     min(w, xs.max() + pad), min(c.shape[0], ys.max() + pad)))


# one League frame rendered big (pose_ref --frame, 1200 px): name -> (champ, clip@ms, width)
BIG = {"wk_idle_a": ("MonkeyKing", "monkeyking_idle1@2383", 1.6), "wk_idle_b": ("MonkeyKing", "monkeyking_idle1@3575", 1.6),
       "ak_idle": ("Akshan", "Akshan_Idle1@0", 1.2)}


def big_frame(name):
    im = Image.open(os.path.join(TMP, "big", name + ".png")).convert("RGB")
    c = np.asarray(im).astype(int)
    m = np.abs(c - c[3, 3]).sum(2) > 24
    ys, xs = np.nonzero(m)
    pad = 30
    return im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad), min(im.height, ys.max() + pad)))


def ensure_renders(lol):
    for name, (champ, frame, width) in BIG.items():
        if os.path.isfile(os.path.join(TMP, "big", name + ".png")):
            continue
        subprocess.run([sys.executable, os.path.join(AK, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
                        "--hq", "--mirror", "--no-labels", "--size", "1200", "--width", str(width), "--yaw", "45",
                        "--frame", frame, "--name", name, "--out", os.path.join(TMP, "big")], check=True)
    jobs = [("MonkeyKing", "Idle", 4), ("MonkeyKing", "Run", 6), ("Akshan", "Idle1", 4), ("Gangplank", "Run", 6)]
    for champ, anim, n in jobs:
        out = os.path.join(REFS, champ)
        if os.path.isdir(out) and os.listdir(out):
            continue
        subprocess.run([sys.executable, os.path.join(AK, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
                        "--anim", anim, "--frames", str(n), "--hq", "--mirror", "--out", out], check=True)


def layout(name, rows, hair_y, note, box=None):
    """The canvas with the grid every 5 squares, the hair-top line (green), the ground (red), an optional width box."""
    can = Image.new("RGB", (CANVAS, CANVAS), (255, 255, 255))
    d = ImageDraw.Draw(can)
    for x in range(0, CANVAS, PX * 5):
        d.line([(x, 0), (x, CANVAS)], fill=(210, 210, 210))
    for y in range(0, CANVAS, PX * 5):
        d.line([(0, y), (CANVAS, y)], fill=(210, 210, 210))
    if box:
        x0, x1 = box
        d.rectangle([x0, hair_y, x1, SOLE_Y], outline=(60, 120, 230), width=3)
    d.line([(0, hair_y), (CANVAS, hair_y)], fill=(40, 170, 60), width=3)
    d.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40), width=3)
    d.text((12, 12), note, fill=(40, 40, 40))
    can.save(name)


def zip_dir(folder, zpath):
    os.makedirs(lp(os.path.dirname(zpath)), exist_ok=True)
    base = os.path.basename(folder)
    with zipfile.ZipFile(lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.join(base, os.path.relpath(p, folder)))
    print("->", zpath)


def fresh(name):
    out = os.path.join(TMP, name)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    return out


# ------------------------------------------------------------------------------------------------ Akshan
AK_ROWS = 46            # 38 game rows hair to soles x PPU 1.2
AK_HAIR = SOLE_Y - AK_ROWS * PX
AK_BODY_MAX = 24        # squares across the shoulders / hips with the cape (20 game px; Kai'Sa 19-24, Jhin 19-23)


def akshan(prompts):
    out = fresh("akshan_slim_pack")
    d = trim(rgba(os.path.join(SRC, "akshan", "hd", "design.png")))
    on_grey(d).save(os.path.join(out, "1_现在的定稿_太胖.png"))
    big_frame("ak_idle").save(os.path.join(out, "2_英雄联盟阿克尚_待机.png"))
    cx = CANVAS // 2 // PX * PX
    layout(os.path.join(out, "3_layout.png"), AK_ROWS, AK_HAIR,
           f"Akshan: green = hair top y {AK_HAIR}, red = ground y {SOLE_Y} ({AK_ROWS} squares of {PX} px); blue box = "
           f"body width at most {AK_BODY_MAX} squares (the raised gun may stick out above and to the side)",
           box=(cx - AK_BODY_MAX * PX // 2, cx + AK_BODY_MAX * PX // 2))
    for i, (hero, tag) in enumerate((("kaisa", "hd_idle"), ("jhin", "idle"), ("akshan", "hd_idle")), 4):
        on_grey(sheet_frame(hero, tag)).save(os.path.join(out, "style", f"{i}_style_{hero}.png"))
    shutil.copyfile(os.path.join(prompts, "AKSHAN_SLIM_PROMPT.md"), os.path.join(out, "PROMPT.md"))
    zip_dir(out, os.path.join(DIST, "akshan_slim_pack.zip"))


# ------------------------------------------------------------------------------------------------ Gangplank
GP_CW, GP_CH, GP_FEET = 92, 80, 77      # a cell in the design's squares (PPU 1.5), the soles' row in it
GP_BODY = 62                            # the design: hat top to soles
OPPI_BODY = 32                          # oppi's Swain idle: head top to soles (the raven not counted)
KEY = (0, 255, 0)


def on_key(a):
    o = np.zeros(a.shape[:2] + (3,), np.uint8)
    o[:] = KEY
    m = a[..., 3] > 0
    o[m] = a[m][:, :3]
    return o


def gangplank(prompts):
    out = fresh("gangplank_run_swap_pack")
    shutil.rmtree(os.path.join(out, "style"))
    s = T.load_sprite(OPPI_SWAIN)
    t = s.tag("run")
    run = [np.asarray(s.frames[i].convert("RGBA")) for i in range(t["frm"], t["to"] + 1)]
    idle = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    soles = np.nonzero(idle[..., 3])[0].max()
    allm = np.zeros(run[0].shape[:2], bool)
    for f in run:
        allm |= f[..., 3] > 0
    yy, xx = np.nonzero(allm)
    x0, x1, y0 = xx.min(), xx.max() + 1, yy.min()
    k = GP_BODY / OPPI_BODY
    sheet = np.zeros((2 * GP_CH, 4 * GP_CW, 4), np.uint8)
    for n, f in enumerate(run):
        crop = f[y0:soles + 1, x0:x1]
        a = np.asarray(Image.fromarray(crop).resize((round(crop.shape[1] * k), round(crop.shape[0] * k)), Image.NEAREST))
        h, w = a.shape[:2]
        Y, X = (n // 4) * GP_CH + GP_FEET - h + 1, (n % 4) * GP_CW + (GP_CW - w) // 2
        Y0 = max(Y, (n // 4) * GP_CH)
        a = a[Y0 - Y:]
        m = a[..., 3] > 0
        sheet[Y0:Y0 + a.shape[0], X:X + w][m] = a[m]
    d = trim(rgba(os.path.join(SRC, "gangplank", "hd", "design.png")))
    cell = np.zeros((GP_CH, GP_CW, 4), np.uint8)
    dy, dx = GP_FEET - d.shape[0] + 1, (GP_CW - d.shape[1]) // 2
    m = d[..., 3] > 0
    cell[dy:dy + d.shape[0], dx:dx + d.shape[1]][m] = d[m]
    Image.fromarray(up(on_key(sheet), 6)).save(os.path.join(out, "1_动作骨架_oppi走路.png"))
    Image.fromarray(up(on_key(cell), 6)).save(os.path.join(out, "2_角色_普朗克定稿.png"))
    shutil.copyfile(os.path.join(REFS, "Gangplank", "Gangplank_Run.png"), os.path.join(out, "3_英雄联盟普朗克跑步.png"))
    strip("gangplank", "hd_run").save(os.path.join(out, "4_现在的走路_太僵硬.png"))
    shutil.copyfile(os.path.join(prompts, "GANGPLANK_RUN_PROMPT.md"), os.path.join(out, "PROMPT.md"))
    zip_dir(out, os.path.join(DIST, "gangplank_run_swap_pack.zip"))
    print("gangplank run scale", round(k, 3), "sheet", sheet.shape[:2], "design", d.shape[:2])


# ------------------------------------------------------------------------------------------------ Wukong
WK_ROWS = 39            # 38 game rows x 85 % = 32 game rows hair to soles, x PPU 1.2
WK_HAIR = SOLE_Y - WK_ROWS * PX


def wukong(prompts):
    out = fresh("wukong_redo_pack")
    d = trim(rgba(os.path.join(SRC, "wukong", "hd", "design.png")))
    on_grey(d).save(os.path.join(out, "1_旧定稿_服装颜色照它_姿势不要.png"))
    for src, name in (("wk_idle_a", "2_英雄联盟悟空_待机_照这个姿势.png"), ("wk_idle_b", "2b_英雄联盟悟空_待机_另一帧.png")):
        big_frame(src).save(os.path.join(out, name))
    shutil.copyfile(os.path.join(REFS, "MonkeyKing", "MonkeyKing_run.png"), os.path.join(out, "3_英雄联盟悟空_跑步_只看.png"))
    layout(os.path.join(out, "4_layout.png"), WK_ROWS, WK_HAIR,
           f"Wukong: green = top of the hair tuft y {WK_HAIR}, red = ground y {SOLE_Y} ({WK_ROWS} squares of {PX} px); "
           "the tail and the staff may stick out above / to the sides")
    for name, tag in (("hd_idle", "idle"), ("hd_run", "run"), ("hd_attack", "attack")):
        strip("wukong", name).save(os.path.join(out, f"5_现在的{tag}_像僵尸_不要.png"))
    for i, (hero, tag) in enumerate((("akshan", "hd_idle"), ("tahmkench", "hd_idle"), ("leesin", "idle")), 6):
        on_grey(sheet_frame(hero, tag)).save(os.path.join(out, "style", f"{i}_style_{hero}.png"))
    shutil.copyfile(os.path.join(prompts, "WUKONG_REDO_PROMPT.md"), os.path.join(out, "PROMPT.md"))
    zip_dir(out, os.path.join(DIST, "wukong_redo_pack.zip"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", default=r"D:/WeGameApps/lol")
    ap.add_argument("--only", choices=["akshan", "gangplank", "wukong"])
    a = ap.parse_args()
    ensure_renders(a.lol)
    prompts = os.path.join(SRC, "redo_1018")
    for name, fn in (("akshan", akshan), ("gangplank", gangplank), ("wukong", wukong)):
        if not a.only or a.only == name:
            fn(prompts)


if __name__ == "__main__":
    main()
