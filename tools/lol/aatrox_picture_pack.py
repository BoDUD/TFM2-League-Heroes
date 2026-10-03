#!/usr/bin/env python3
"""Build Codex's picture pack for Aatrox (art step 0) from a local League of Legends install.

    python tools/lol/aatrox_picture_pack.py --lol "D:\\WeGameApps\\lol"
    python tools/lol/aatrox_picture_pack.py --no-renders          # prompt + style pictures only

Writes dist/aatrox_picture_pack/ and dist/aatrox_picture_pack.zip, laid out as the table in
assets/source/aatrox/PICTURE_PROMPT.md lists them:
  PICTURE_PROMPT.md   the prompts
  refs/               League's base-skin Aatrox rendered through pose_ref.py (--hq, light background): the idle
                      frame 3/4 front from both sides (1a/1b), nearly frontal (2), the head from both sides (3a/3b),
                      the side (4), the back (5), six frames of World Ender (6) and of a Darkin Blade swing (7);
                      his load-screen art (8); model_info.txt (clips, textures, submeshes - for the later steps)
  style/              the Kennen A and LeBlanc A pictures Codex drew for this pack (9, 10)
Every render is tried on its own: one that fails is reported and left out, the rest are packed. The renders and
the load screen are Riot's: they stay in dist/ (git-ignored) and go to Codex only, never into the repo.
Reads (never writes) Game/DATA/FINAL/Champions/Aatrox.wad.client. Needs what pose_ref.py needs (numpy, Pillow,
Python 3.14 for zstd).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

CHAMP = "Aatrox"
BG = (225, 225, 225)
PROMPT = os.path.join(ROOT, "assets", "source", "aatrox", "PICTURE_PROMPT.md")
STYLE = {  # pack name -> repo picture (both approved by the user as this pack's chibi style)
    "9_style_kennen.png": os.path.join(ROOT, "assets", "source", "kennen", "codex_picture", "kennen-model-A.png"),
    "10_style_leblanc.png": os.path.join(ROOT, "assets", "source", "leblanc", "codex_picture", "leblanc-model-A.png"),
}
# pose_ref.py options shared by every render: textured per pixel, no labels, the light prompt background
COMMON = ["--hq", "--no-labels", "--bg", ",".join(map(str, BG)), "--pitch", "12"]


def anm_names(wad):
    blob = wad.read_path(f"data/characters/{CHAMP.lower()}/animations/skin0.bin")
    paths = set(m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\.anm", blob))
    return sorted({os.path.splitext(os.path.basename(p))[0] for p in paths}, key=str.lower)


def pick(names, needles, avoid=("_in", "_out", "to_", "recall", "dance", "taunt", "joke", "laugh", "channel")):
    """The shortest clip whose name holds the first needle that matches any (case-insensitive)."""
    for n in needles:
        hits = [c for c in names if n in c.lower() and not any(a in c.lower() for a in avoid)]
        if hits:
            return min(hits, key=lambda c: (len(c), c.lower()))
    return None


def pose_ref(args, tmp, extra):
    """Run pose_ref.py; returns its stdout, or None after printing why it failed."""
    cmd = [sys.executable, os.path.join(HERE, "pose_ref.py"), "--lol", args.lol, "--champ", CHAMP,
           "--out", tmp] + COMMON + extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        tail = (r.stderr or r.stdout).strip().splitlines()[-3:]
        print("    pose_ref.py failed: " + " | ".join(tail))
        return None
    return r.stdout


def figure_box(img):
    """Bounding box of the pixels that are not the flat background."""
    from PIL import ImageChops, Image
    diff = ImageChops.difference(img.convert("RGB"), Image.new("RGB", img.size, BG)).convert("L")
    return diff.point(lambda v: 255 if v > 12 else 0).getbbox()


def head_crop(src, dst):
    """The top 40% of the figure (horns, face, shoulders) with a margin."""
    from PIL import Image
    img = Image.open(src)
    box = figure_box(img)
    if not box:
        return False
    x0, y0, x1, y1 = box
    h = y1 - y0
    top, bottom = max(0, y0 - h // 20), min(img.height, y0 + int(h * 0.40))
    # keep the columns the head part uses, not the whole width of a sword held out
    part = img.crop((0, top, img.width, bottom))
    pbox = figure_box(part)
    if pbox:
        left, right = max(0, pbox[0] - h // 20), min(img.width, pbox[2] + h // 20)
        part = part.crop((left, 0, right, part.height))
    part.save(dst)
    return True


def frame_ref(args, tmp, dest, out_name, clip, ms, yaw, size, width, mirror=False):
    """One frame rendered to <dest>/<out_name> (dest None: left in tmp); returns its path or None."""
    print(f"  {out_name}: {clip}@{ms} yaw {yaw}{' mirrored' if mirror else ''}")
    name = os.path.splitext(out_name)[0]
    extra = ["--frame", f"{clip}@{ms}", "--name", name, "--yaw", str(yaw), "--size", str(size),
             "--width", str(width), "--fit", "0.58", "--ground", "0.88"] + (["--mirror"] if mirror else [])
    if pose_ref(args, tmp, extra) is None:
        return None
    src = os.path.join(tmp, name + ".png")
    if not os.path.exists(src):
        print("    no output")
        return None
    if dest is None:
        return src
    dst = os.path.join(dest, out_name)
    shutil.move(src, dst)
    return dst


def strip_ref(args, tmp, refs, out_name, clip, frames, yaw, size, width):
    print(f"  {out_name}: {clip}, {frames} frames, yaw {yaw}")
    if pose_ref(args, tmp, ["--anim", clip, "--frames", str(frames), "--yaw", str(yaw), "--size", str(size),
                            "--width", str(width), "--fit", "0.55", "--ground", "0.88"]) is None:
        return None
    src = os.path.join(tmp, clip + ".png")
    if not os.path.exists(src):    # --anim matches by substring: take whatever it wrote for this clip
        made = [f for f in os.listdir(tmp) if f.lower().startswith(clip.lower()) and f.endswith(".png")]
        if not made:
            print("    no output")
            return None
        src = os.path.join(tmp, sorted(made, key=len)[0])
    dst = os.path.join(refs, out_name)
    shutil.move(src, dst)
    return dst


def renders(args, refs):
    from riot import Wad
    import pose_ref as pr

    wad_path = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions", f"{CHAMP}.wad.client")
    if not os.path.exists(wad_path):
        print(f"no {wad_path}: renders skipped (check --lol)")
        return []
    wad = Wad(wad_path)
    names = anm_names(wad)
    skin_bin = wad.read_path(f"data/characters/{CHAMP.lower()}/skins/skin0.bin")
    refs_in = lambda ext: sorted(set(m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\." + ext, skin_bin)))

    # what the later steps need to know about the model
    info = [f"clips ({len(names)}):", "  " + ", ".join(names)]
    try:
        skn = pr.base_mesh(refs_in(rb"skn"))
        subs = pr.skn_submeshes(wad.read_path(skn.lower()))
        texs = refs_in(rb"(?:tex|dds)")
        info += [f"mesh: {skn}", "submeshes: " + ", ".join(s[0] for s in subs),
                 "textures named by the skin bin:"] + ["  " + t for t in texs] + \
                ["diffuse picked by pose_ref.py: " + ", ".join(pr.diffuse_textures(texs, skin_bin, skn)[:3])]
    except Exception as e:  # informational only
        info.append(f"(model info failed: {e})")
    with open(os.path.join(refs, "model_info.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(info) + "\n")
    print("\n".join(info[:2]))

    idle = pick(names, ["idle1", "idle_base", "idle"])
    ult = pick(names, ["spell4", "_r_", "ult"], avoid=("_in", "_out", "recall", "dance", "taunt", "joke", "laugh"))
    q = pick(names, ["spell1a", "spell1_a", "spell1", "_q1", "_q_"])
    print(f"clips picked: idle {idle}, ult {ult}, Q {q}")
    made = []
    with tempfile.TemporaryDirectory() as tmp:
        if idle:
            for out, yaw, mirror in (("1a_aatrox_league_front.png", 50, False),
                                     ("1b_aatrox_league_front_mirror.png", 50, True),
                                     ("2_aatrox_league_frontal.png", 15, False),
                                     ("4_aatrox_league_side.png", 90, False),
                                     ("5_aatrox_league_back.png", 145, False)):
                made.append(frame_ref(args, tmp, refs, out, idle, 0, yaw, 900, 1.3, mirror))
            for out, mirror in (("3a_aatrox_league_head.png", False), ("3b_aatrox_league_head_mirror.png", True)):
                big = frame_ref(args, tmp, None, "big_" + out, idle, 0, 40, 1500, 1.3, mirror)
                if big and head_crop(big, os.path.join(refs, out)):
                    made.append(os.path.join(refs, out))
                    print(f"    cropped the head -> {out}")
        else:
            print("no idle clip found: the front, side, back and head renders are skipped")
        if ult:
            made.append(strip_ref(args, tmp, refs, "6_aatrox_league_ult.png", ult, 6, 50, 420, 1.7))
        if q:
            made.append(strip_ref(args, tmp, refs, "7_aatrox_league_q.png", q, 6, 50, 420, 1.7))

    # the load screen: the base skin's LoadScreen texture the skin bin names
    shots = [t for t in refs_in(rb"(?:tex|dds)") if "loadscreen" in t.lower() and "/base/" in t.lower()] or \
            [t for t in refs_in(rb"(?:tex|dds)") if "loadscreen" in t.lower()]
    if shots:
        try:
            pr.read_tex(wad.read_path(sorted(shots, key=len)[0].lower())).save(
                os.path.join(refs, "8_aatrox_loadscreen.png"))
            made.append(os.path.join(refs, "8_aatrox_loadscreen.png"))
            print(f"  8_aatrox_loadscreen.png <- {sorted(shots, key=len)[0]}")
        except Exception as e:
            print(f"  load screen failed: {e}")
    else:
        print("  no load-screen texture named in the skin bin")
    return [m for m in made if m]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol", help="League of Legends folder (contains Game/)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "aatrox_picture_pack"))
    ap.add_argument("--no-renders", action="store_true", help="pack the prompt and the style pictures only")
    args = ap.parse_args()

    if os.path.isdir(args.out):
        shutil.rmtree(args.out)
    refs, style = os.path.join(args.out, "refs"), os.path.join(args.out, "style")
    os.makedirs(refs)
    os.makedirs(style)
    shutil.copy(PROMPT, os.path.join(args.out, "PICTURE_PROMPT.md"))
    for name, src in STYLE.items():
        shutil.copy(src, os.path.join(style, name))
    made = [] if args.no_renders else renders(args, refs)

    zpath = args.out.rstrip("/\\") + ".zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _dirs, files in os.walk(args.out):
            for f in sorted(files):
                full = os.path.join(base, f)
                z.write(full, os.path.relpath(full, args.out))
    wanted = ["1a_aatrox_league_front.png", "1b_aatrox_league_front_mirror.png", "2_aatrox_league_frontal.png",
              "3a_aatrox_league_head.png", "3b_aatrox_league_head_mirror.png", "4_aatrox_league_side.png",
              "5_aatrox_league_back.png", "6_aatrox_league_ult.png", "7_aatrox_league_q.png",
              "8_aatrox_loadscreen.png"]
    have = set(os.listdir(refs))
    missing = [w for w in wanted if w not in have]
    print(f"\n{zpath}: {len(have & set(wanted))} reference(s), {len(STYLE)} style picture(s), the prompt")
    if missing:
        print("missing (see the table in PICTURE_PROMPT.md for which can be left out): " + ", ".join(missing))
    print("Look at refs/1a and 1b once: the one showing his face is the 3/4 front Codex should use.")


if __name__ == "__main__":
    main()
