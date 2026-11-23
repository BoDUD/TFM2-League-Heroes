#!/usr/bin/env python3
"""终末包每个英雄的跑步都按联盟英雄的节奏：一圈 RUN_CYCLE 秒。

    python tools/art/ragnarok_run_pace.py            # 改 ragnarok/champions/*#anim.fanim 里跑步的帧时长
    python tools/art/ragnarok_run_pace.py --check    # 有一个不是这个节奏就退出 1（CI 跑）

用户 2026-11-23 看审阅动图问「这跑步节奏是加速了吗 gif图 这么快」：不是加速，是 Codex 交的节奏——跑一圈 0.50-0.64 秒
（索尔 0.80），联盟英雄跑一圈的中位数 0.90 秒、盖伦 0.94 秒，终末的英雄迈腿快六成。看过放慢前后的对照动图以后：「全包都放慢」。
每个跑步动作（run，形态的 c_run / h_run / mu_run / ad_run，连同 hd_ / lo_）一圈拉到 RUN_CYCLE 秒：每帧照原来的比例，取到毫秒，
最后一帧补齐。只改时长，不动像素、不动别的动作；人在地上走的速度不变，腿摆得慢一些。

导入（tools/art/import_<英雄>.py）写的是 Codex 的时长：重新导入一个英雄以后按顺序跑 ppu_hd.py、hero_reels.py，最后跑这个。
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHEETS = os.path.join(ROOT, "ragnarok", "champions")
RUN_CYCLE = 0.92            # 秒：联盟英雄跑一圈的中位数 0.90、盖伦 0.94


def is_run(tag):
    return tag == "run" or tag.endswith("_run")


def paced(durs):
    """一圈拉到 RUN_CYCLE：每帧照原来的比例取到毫秒，最后一帧补齐（再跑一遍不变）。"""
    total = sum(durs)
    out = [round(RUN_CYCLE * d / total, 3) for d in durs[:-1]]
    out.append(round(RUN_CYCLE - sum(out), 3))
    if min(out) <= 0:
        raise ValueError(f"a frame would last {min(out)} s: {durs}")
    return out


def pace_file(path):
    """一个英雄的 .fanim：返回 (改过的文本或 None, [(标签, 原来一圈, 现在一圈)])。"""
    text = open(path, encoding="utf-8-sig").read()
    fanim = json.loads(text)
    anims = fanim["anims"]
    done = []
    for tag in [t for t in anims if is_run(t) and not t.startswith(("hd_", "lo_"))]:
        old = [f["duration"] for f in anims[tag]["frames"]]
        new = paced(old)
        for t in (tag, "hd_" + tag, "lo_" + tag):
            if t not in anims:
                continue
            frames = anims[t]["frames"]
            if len(frames) != len(new):
                raise ValueError(f"{path}: {t} has {len(frames)} frames, {tag} {len(new)}")
            for f, d in zip(frames, new):
                f["duration"] = d
        done.append((tag, round(sum(old), 3), round(sum(new), 3)))
    out = json.dumps(fanim, ensure_ascii=False, separators=(",", ":"))      # 和 hero_reels.py、导入写的一样
    return (out if json.loads(out) != json.loads(text) else None), done


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    bad = 0
    for path in sorted(glob.glob(os.path.join(SHEETS, "ragnarok_*#anim.fanim"))):
        out, done = pace_file(path)
        name = os.path.basename(path).split("#")[0]
        if out is None:
            continue
        if a.check:
            print(f"{name}: run not at {RUN_CYCLE} s a cycle - run tools/art/ragnarok_run_pace.py")
            bad += 1
            continue
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(out)
        print(name, ", ".join(f"{t} {o} -> {n} s" for t, o, n in done))
    if a.check:
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
