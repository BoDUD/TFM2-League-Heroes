"""Build the add-on's copy of Jayce from the main pack (Thundering Blow toward his side, the smart gate shot; the whole-body
cannon needs nothing in the data).

    python addons/league_jayce/make_override.py

Rebuilds Jayce with tools/kit/build_jayce.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_jayce.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_jayce/override/league_jayce.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit plus passive league_jayce:hextech (params: the knock-back's speed and ticks, the
    gate shot's range and damage - src/lib.rs Params::default must be the same, its test reads this copy);
  * the champion branch of Thundering Blow calls the native effect league_jayce:blow instead of the data's Knockback
    (the same push, aimed toward his allies / his tower); minions and monsters keep the data's knock-back;
  * the attack's, skill2's and the ult's tooltips point to description.league_jayce_hextech.* with the add-on's
    wording, so the tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Jayce changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_jayce")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_jayce as kit  # noqa: E402
import setup_jayce as setup  # noqa: E402

TEXT_ID = "league_jayce_hextech"      # the text's key (the hero's own id is league_jayce)
HERO = "league_jayce"
SLOTS = ("attack", "skill2", "ult")
# lang -> slot -> [(old text the main pack has, new text)] ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
SWAP = {
    "zh-hans": {"attack": [],
                "skill2": [("锤：击退敌人", "锤：把敌人击退向己方")],
                "ult": [("向敌方英雄射出", "向能击杀或血最少的英雄射出")]},
    "zh-hant": {"attack": [],
                "skill2": [("錘：擊退敵人", "錘：把敵人擊退向己方")],
                "ult": [("向敵方英雄射出", "向能擊殺或血最少的英雄射出")]},
    "en": {"attack": [],
           "skill2": [("Hammer: knocks an enemy back", "Hammer: knocks an enemy back toward his side")],
           "ult": [("fires an accelerated orb at a champion:", "fires an accelerated orb at the champion it can kill, else the lowest:")]},
    "ko": {"attack": [],
           "skill2": [("해머: 적을 밀쳐내며", "해머: 적을 아군 쪽으로 밀쳐내며")],
           "ult": [("챔피언에게 가속된 구체를", "처치 가능하거나 체력이 가장 낮은 챔피언에게 가속된 구체를")]},
    "ja": {"attack": [],
           "skill2": [("ハンマー：敵をノックバックし", "ハンマー：敵を味方側へノックバックし")],
           "ult": [("チャンピオンへ加速した球を", "倒せるか体力の最も低いチャンピオンへ加速した球を")]},
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
        sys.exit("the main pack's league_jayce differs from build_jayce.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != "league_jayce:hextech":
        sys.exit("the copy does not call the add-on: update this script")
    if '"effect_ref": "league_jayce:blow"' not in json.dumps(champion):
        sys.exit("the copy's Thundering Blow does not call league_jayce:blow: update build_jayce.py")
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
                    sys.exit(f"{lang}.{slot}: {old!r} is not once in setup_jayce.TEXT")
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
