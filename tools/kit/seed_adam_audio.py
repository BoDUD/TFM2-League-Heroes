"""把亚当用到的音频从 Codex 的交付拷进 ragnarok/sound/sfx/（不进仓库，和联盟、金铲铲包的音频一样）。

    python tools/kit/seed_adam_audio.py [--from <解压后的交付根目录>]

交付（2026-11-21，分支 codex/ragnarok-adam-assets 35eaf0a86；本地包 D:/TFM2-Workshop/adam_packs/outputs/
adam_assets.zip，解压在同名文件夹）：16 条原创音效和七句官方日语原声（齐藤壮马）。只拷 setup_adam.SOUNDS 放的，
每条先对 assets/source/adam/audio/manifest.json 里的 SHA-256。
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from setup_adam import SOUNDS, MOD, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MANIFEST = os.path.join(REPO, "assets", "source", "adam", "audio", "manifest.json")
DEFAULT = r"D:\TFM2-Workshop\adam_packs\outputs\adam_assets"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default=DEFAULT)
    a = ap.parse_args()
    m = json.load(open(MANIFEST, encoding="utf-8"))
    sha = {os.path.basename(c["mp3"])[:-4]: (c["mp3"], c["mp3_sha256"]) for c in m["sfx"] + m["voice"]}
    clips = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})
    out = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out), exist_ok=True)
    for c in clips:
        if c not in sha:
            sys.exit(f"{c}: not in Codex's manifest")
        rel, digest = sha[c]
        src = os.path.join(a.src, rel)
        if not os.path.isfile(src):
            sys.exit(f"missing: {src}")
        data = open(src, "rb").read()
        if hashlib.sha256(data).hexdigest() != digest:
            sys.exit(f"{src}: SHA-256 differs from the manifest")
        shutil.copyfile(src, lp(os.path.join(out, c + ".mp3")))
    print(f"{len(clips)} clips -> {out}")


if __name__ == "__main__":
    main()
