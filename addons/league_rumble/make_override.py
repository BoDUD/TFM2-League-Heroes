"""Build the add-on's copy of Rumble from the main pack (Flamespitter cast on the move).

    python addons/league_rumble/make_override.py [--check]

Rebuilds Rumble with tools/kit/build_rumble.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_rumble.data_champion (so the copy never drifts from the shipped kit), and writes
addons/league_rumble/override/league_rumble.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit, but Flamespitter holds him only for the aim (q_first ticks of `skill`) and puts
    league_rumble_q_on on him for the burst: he walks while it burns, and the add-on's view hook plays his q_run /
    q_stand frames (the fire drawn in) while it lasts (the user, 2026-10-29: 「兰博不会边走边放火吗」);
  * Flamespitter's damage at WALK_K% (base and AP ratio): walking, he keeps nearly every pulse on his target;
  * Q's tooltip (setup_rumble's text with those numbers) opens with the add-on's mark and says he walks, so the tooltip
    in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Rumble changes; --check exits 1 when the
files are not what it would write.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_rumble")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_rumble as kit  # noqa: E402
import setup_rumble as setup  # noqa: E402

MOD_ID = "league_rumble"
HERO = "league_rumble"
SLOTS = ("skill",)
# Flamespitter's damage in the copy, % of the main pack's (q_dmg and q_ap): kd.py top lane, seeds 1-8 / 9-16, 2026-10-29 -
# the main pack +0.51 / +0.10; walking at 100% +2.23 / +1.98 (he chases with the fire on), 70% +1.24 / +1.29,
# 60% +0.36 / +0.24, 50% -0.34 / -0.74
WALK_K = 60
# Q's text, marked and with the walk said (the same words in each language)
MARK = {"zh-hans": ("【扩展包】", "喷火时可以走动。"), "zh-hant": ("【擴充包】", "噴火時可以走動。"),
        "en": ("[Add-on] ", " He can walk while it burns."), "ko": ("[확장] ", " 화염 방사 중 이동 가능."),
        "ja": ("【拡張】", "噴射中も移動できる。")}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def read(path):
    with open(lp(path), encoding="utf-8", newline="") as f:
        return f.read()


def files():
    """{path: text} of the copy and its texts."""
    p = dict(kit.P)
    if dumps_main(kit.build(p)) != read(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")):
        sys.exit("the main pack's league_rumble differs from build_rumble.P: rebuild it first")
    q = dict(p, q_dmg=p["q_dmg"] * WALK_K // 100, q_ap=p["q_ap"] * WALK_K // 100)
    champion = kit.build(q, native=True)
    if '"league_rumble_q_on"' not in json.dumps(champion["skill"]):
        sys.exit("the copy's Flamespitter puts no league_rumble_q_on on him: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
    main_text = json.loads(read(os.path.join(ROOT, "league", "text", "champion.i18n")).lstrip("﻿"))
    missing = set(main_text) - set(MARK)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    made = setup.texts(q)
    texts = {}
    for lang in main_text:
        head, tail = MARK[lang]
        texts[lang] = {slot: head + made[lang][0][slot] + tail for slot in SLOTS}
        n = setup.shown_length(texts[lang]["skill"])
        if n > setup.TOOLTIP_MAX[lang]:
            sys.exit(f"{lang}: Q's tooltip {n} > {setup.TOOLTIP_MAX[lang]} shown characters")
    return {
        os.path.join(ADDON, "override", HERO + ".data_champion"): json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
        os.path.join(ADDON, "text", "champion.i18n"): json.dumps(
            {lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text}, ensure_ascii=False, indent=2) + "\n",
    }


def main():
    check = "--check" in sys.argv[1:]
    stale = []
    for path, text in files().items():
        old = read(path).replace("\r\n", "\n") if os.path.isfile(lp(path)) else None
        if old == text:
            continue
        stale.append(os.path.relpath(path, ROOT))
        if not check:
            os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
            with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
    if check:
        if stale:
            sys.exit("league_rumble: out of date: %s (run addons/league_rumble/make_override.py)" % ", ".join(stale))
        print("league_rumble: override and text up to date")
    else:
        print("wrote " + (", ".join(stale) or "nothing (up to date)"))


if __name__ == "__main__":
    main()
