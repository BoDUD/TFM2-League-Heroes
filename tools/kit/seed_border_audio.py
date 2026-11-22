"""把 Codex 交的边境巡团配音拷进 border/sound/sfx/（<id>_vo_<x>.mp3，十二个人各九句）。

    python tools/kit/seed_border_audio.py [--zip <Codex 的 zip>] [--check]

读 zip 里的 mods/border_patrol/sound/voice/zh-hans/*.mp3，和 zip 里 docs/border_patrol/sha256.json 记的哈希对过再写；
--check 只比对仓库里的和 zip 里的是不是一样。这些是 Codex 合成的普通话试音（不是谁的录音），跟着仓库走。
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "border", "sound", "sfx")
ZIP = r"D:/TFM2-Workshop/border_patrol_packs/Border_Patrol_Mirror_Sea_Anime_Assets_v0.5.0.zip"
HEROES = ["cenlei", "xiaolun", "dengmi", "zhumo", "fusuo", "yanxi", "yindu", "lanti", "luxin", "jiyan", "zhongli",
          "wuling"]
VOICE = ["pick", "attack", "move", "hit", "skill", "skill2", "ult", "dead", "win"]
SRC = "mods/border_patrol/sound/voice/zh-hans/"


def sha_table(z):
    try:
        raw = json.loads(z.read("docs/border_patrol/sha256.json").decode("utf-8"))
    except KeyError:
        return {}
    out = {}

    def walk(o, key=""):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
        elif isinstance(o, str) and len(o) == 64 and key:
            out[os.path.basename(key)] = o
    walk(raw)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", default=ZIP)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    z = zipfile.ZipFile(a.zip)
    known = sha_table(z)
    os.makedirs(OUT, exist_ok=True)
    bad = n = 0
    for h in HEROES:
        for v in VOICE:
            name = f"border_{h}_vo_{v}.mp3"
            data = z.read(SRC + name)
            digest = hashlib.sha256(data).hexdigest()
            if name in known and known[name] != digest:
                print(f"{name}: sha256 differs from Codex's sha256.json")
                bad += 1
                continue
            dst = os.path.join(OUT, name)
            if a.check:
                if not os.path.isfile(dst) or open(dst, "rb").read() != data:
                    print(f"{name}: differs - run {os.path.relpath(__file__, REPO)}")
                    bad += 1
                continue
            with open(dst, "wb") as f:
                f.write(data)
            n += 1
    print(f"{n} clips written to {os.path.relpath(OUT, REPO)}" if not a.check else f"checked, {bad} bad")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
