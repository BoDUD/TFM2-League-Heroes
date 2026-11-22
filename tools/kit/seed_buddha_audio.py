"""把释迦用到的音频从 Codex 的交付拷进 ragnarok/sound/sfx/（不进仓库，和联盟、金铲铲包的音频一样）。

    python tools/kit/seed_buddha_audio.py [--from <解压后的交付根目录>]

交付（2026-11-22，D:/TFM2-Workshop/buddha_packs/outputs/buddha_assets_done.zip，音频解压在 buddha_packs/outputs/
buddha_assets/audio）：15 条原创音效（sfx_*.mp3）和六句官方日语原声（中村悠一，voice_*.mp3；宣传片结尾那句不用）。
只拷 setup_buddha.SOUNDS 放的，改名成 ragnarok_buddha_sfx_* / ragnarok_buddha_vo_*，每条先对
assets/source/buddha/audio/sources.json 里的 SHA-256。
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from setup_buddha import SOUNDS, MOD, ID, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
SOURCES = os.path.join(REPO, "assets", "source", "buddha", "audio", "sources.json")
DEFAULT = r"D:\TFM2-Workshop\buddha_packs\outputs\buddha_assets"


def codex_name(clip):
    """ragnarok_buddha_sfx_x -> sfx_x；ragnarok_buddha_vo_x -> voice_x（Codex 交付里的文件名）。"""
    rest = clip[len(ID) + 1:]
    return "voice_" + rest[3:] if rest.startswith("vo_") else rest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default=DEFAULT)
    a = ap.parse_args()
    sha = {c["id"]: c["mp3_sha256"] for c in json.load(open(SOURCES, encoding="utf-8"))["clips"]}
    clips = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})
    out = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out), exist_ok=True)
    for c in clips:
        name = codex_name(c)
        if name not in sha:
            sys.exit(f"{c}: {name} is not in Codex's sources.json")
        src = os.path.join(a.src, "audio", "mp3", name + ".mp3")
        if not os.path.isfile(src):
            sys.exit(f"missing: {src}")
        data = open(src, "rb").read()
        if hashlib.sha256(data).hexdigest() != sha[name]:
            sys.exit(f"{src}: SHA-256 differs from sources.json")
        shutil.copyfile(src, lp(os.path.join(out, c + ".mp3")))
    print(f"{len(clips)} clips -> {out}")


if __name__ == "__main__":
    main()
