"""Build the add-on's copy of Elise from the main pack (the Cocoon, Rappel and the hunt cast on the AI hook's target; the
whole-body spider needs nothing in the data).

    python addons/league_elise/make_override.py

Rebuilds Elise with tools/kit/build_elise.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_elise.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_elise/override/league_elise.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit plus passive league_elise:queen (params: the Cocoon's range and half width, Rappel's
    and the ult's reach - src/lib.rs Params::default must be the same, its test reads this copy);
  * skill2 and the ult cast on a target (`Targeting`): the Cocoon's aim lock, Rappel's drop and the hunt go at the cast's
    target - the one the add-on's AI hook picks - instead of a random champion in reach;
  * skill2's and the ult's tooltips point to description.league_elise_queen.* with the add-on's wording, so the tooltips
    in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Elise changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_elise")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_elise as kit  # noqa: E402
import setup_elise as setup  # noqa: E402

TEXT_ID = "league_elise_queen"      # the text's key (the hero's own id is league_elise)
HERO = "league_elise"
SLOTS = ("skill2", "ult")
# lang -> slot -> [(old text the main pack has, new text)] ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
SWAP = {
    "zh-hans": {"skill2": [("人形：吐茧", "人形：向线上没被挡的英雄吐茧"), ("落到英雄身上", "落到血最少的英雄身上")],
                "ult": [("向英雄吐茧", "向被控住或血最少的英雄吐茧")]},
    "zh-hant": {"skill2": [("人形：吐繭", "人形：向線上沒被擋的英雄吐繭"), ("落到英雄身上", "落到血最少的英雄身上")],
                "ult": [("向英雄吐繭", "向被控住或血最少的英雄吐繭")]},
    "en": {"skill2": [("Human: a cocoon", "Human: a cocoon at a champion with a clear line"),
                      ("drops on a champion", "drops on the lowest champion")],
           "ult": [("Spits a cocoon at a champion,", "Spits a cocoon at the held or lowest champion,")]},
    "ko": {"skill2": [("인간: 고치로 ", "인간: 막히지 않은 챔피언에게 고치로 "), ("챔피언에게 내려옴", "체력이 가장 낮은 챔피언에게 내려옴")],
           "ult": [("챔피언에게 고치를 뱉고", "기절했거나 체력이 가장 낮은 챔피언에게 고치를 뱉고")]},
    "ja": {"skill2": [("人間：繭で", "人間：遮られないチャンピオンへ繭で"), ("チャンピオンへ降下", "体力の最も低いチャンピオンへ降下")],
           "ult": [("チャンピオンへ繭を吐き", "拘束中か体力の最も低いチャンピオンへ繭を吐き")]},
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_elise differs from build_elise.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != "league_elise:queen":
        sys.exit("the copy does not call the add-on: update this script")
    if champion["skill2"]["casting_type"] != "Targeting" or champion["ult"]["casting_type"] != "Targeting":
        sys.exit("the copy's skill2 / ult are not cast on a target: update build_elise.py")
    for slot in SLOTS:
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = setup.values(p)
    texts = {}
    for lang, swaps in SWAP.items():
        texts[lang] = {}
        for slot in SLOTS:
            src = setup.TEXT[lang][slot]
            for old, new in swaps[slot]:
                if src.count(old) != 1:
                    sys.exit(f"{lang}.{slot}: {old!r} is not once in setup_elise.TEXT")
                src = src.replace(old, new)
            texts[lang][slot] = (LEAD[lang] + src).format(**values)
    lens = {f"{lang}.{slot}": setup.shown_length(LEAD[lang] + t) for lang, d in SWAP.items() for slot in SLOTS
            for t in [_swapped(setup.TEXT[lang][slot], d[slot])]}
    long = {k: n for k, n in lens.items() if n > setup.TOOLTIP_MAX[k.split(".")[0]]}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(champion))
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(tpath)), exist_ok=True)
    with open(lp(tpath), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(i18n))
    print(out)
    print(tpath)
    print("passive", champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {k: f"{n}/{setup.TOOLTIP_MAX[k.split('.')[0]]}" for k, n in lens.items()})


def _swapped(src, pairs):
    for old, new in pairs:
        src = src.replace(old, new)
    return src


if __name__ == "__main__":
    main()
