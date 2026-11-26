"""把洛基用到的音频从 Codex 的交付拷进 ragnarok/sound/sfx/（不进仓库，和联盟、金铲铲包的音频一样）。

    python tools/kit/seed_loki_audio.py [--from <交付根目录>]

交付（2026-11-26，D:/TFM2-Workshop/loki_packs/outputs/loki_final_assets.zip，解压在 loki_final_assets，提交 629e39838）：11 条原创音效和 6 句动画洛基声优松冈禎丞的原声（voice_*.mp3，官方宣传片截的）。
只拷 setup_loki.SOUNDS 放的，改名成 ragnarok_loki_sfx_* / ragnarok_loki_vo_*，每条先对 assets/source/loki/audio/sources.json 里的 SHA-256。
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from setup_loki import SOUNDS, MOD, ID, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
DEFAULT = r"D:\TFM2-Workshop\loki_packs\outputs\loki_final_assets"


def codex_name(clip):
    """ragnarok_loki_sfx_x -> x；ragnarok_loki_vo_x -> voice_x（Codex 交付里的文件名）。"""
    rest = clip[len(ID) + 1:]
    return "voice_" + rest[3:] if rest.startswith("vo_") else rest[4:]


def checksums():
    """assets/source/loki/audio/sources.json：每条的 mp3_sha256。"""
    path = os.path.join(REPO, "assets", "source", "loki", "audio", "sources.json")
    return {c["id"]: c["mp3_sha256"] for c in json.load(open(path, encoding="utf-8"))["clips"]}


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
        src = os.path.join(a.src, "audio", "mp3", name + ".mp3")
        if not os.path.isfile(src):
            sys.exit(f"missing: {src}")
        data = open(src, "rb").read()
        if hashlib.sha256(data).hexdigest() != sha[name]:
            sys.exit(f"{src}: SHA-256 differs from Codex's checksums")
        shutil.copyfile(src, lp(os.path.join(out, c + ".mp3")))
    print(f"{len(clips)} clips -> {out}")


if __name__ == "__main__":
    main()
