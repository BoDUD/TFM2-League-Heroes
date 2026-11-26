"""把须佐之男用到的音频从 Codex 的交付拷进 ragnarok/sound/sfx/（不进仓库，和联盟、金铲铲包的音频一样）。

    python tools/kit/seed_susanoo_audio.py [--from <交付根目录>]

交付（2026-11-23，D:/TFM2-Workshop/susanoo_packs/output，提交 890ad4437）：6 条原创刀声、剑压和命中音效（sound/*.mp3），没有配音。
只拷 setup_susanoo.SOUNDS 放的，改名成 ragnarok_susanoo_sfx_*，每条先对 assets/source/susanoo/checksums.json 里的 SHA-256。
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from setup_susanoo import SOUNDS, MOD, ID, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
DEFAULT = r"D:\TFM2-Workshop\susanoo_packs\output"


def codex_name(clip):
    """ragnarok_susanoo_sfx_x -> x；ragnarok_susanoo_vo_x -> voice_x（Codex 交付里的文件名）。"""
    rest = clip[len(ID) + 1:]
    return "voice_" + rest[3:] if rest.startswith("vo_") else rest[4:]


def checksums():
    """assets/source/susanoo/checksums.json：sound/<名>.mp3 的 SHA-256。"""
    path = os.path.join(REPO, "assets", "source", "susanoo", "checksums.json")
    sums = json.load(open(path, encoding="utf-8"))
    return {k[len("sound/"):-len(".mp3")]: v for k, v in sums.items() if k.startswith("sound/") and k.endswith(".mp3")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default=DEFAULT)
    a = ap.parse_args()
    sha = checksums()
    clips = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})
    out = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out), exist_ok=True)
    for c in clips:
        name = codex_name(c)
        if name not in sha:
            sys.exit(f"{c}: {name} is not in Codex's checksums")
        src = os.path.join(a.src, "sound", name + ".mp3")
        if not os.path.isfile(src):
            sys.exit(f"missing: {src}")
        data = open(src, "rb").read()
        if hashlib.sha256(data).hexdigest() != sha[name]:
            sys.exit(f"{src}: SHA-256 differs from Codex's checksums")
        shutil.copyfile(src, lp(os.path.join(out, c + ".mp3")))
    print(f"{len(clips)} clips -> {out}")


if __name__ == "__main__":
    main()
