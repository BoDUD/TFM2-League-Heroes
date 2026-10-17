"""Build the add-on's copy of Swain from the main pack (Soul Fragments kept through death, the whole body as the demon).

    python addons/league_swain/make_override.py

Rebuilds Swain with tools/kit/build_swain.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_swain.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_swain/override/league_swain.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (R's moment too: the data judges it, the add-on only logs it);
  * passive = the add-on's league_swain:flock with the numbers of P;
  * the attack's and ult's tooltips point to description.league_swain.attack / .ult with the add-on's wording (the
    fragments kept for good, the whole body as the demon), keys of the add-on's own id, so the tooltip in game shows
    whether the override took.
The whole body as the demon needs no data: the add-on's display hook reads the main pack's own buff league_swain_r_on.
Every other champion stays untouched. Run it again whenever the main pack's Swain changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_swain")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_swain as kit  # noqa: E402
import setup_swain as setup  # noqa: E402

MOD_ID = "league_swain"
HERO = "league_swain"
SLOTS = ("attack", "ult")
# lang -> (the add-on's mark, the main pack's words for "lost on death" -> the add-on's, the ult's added sentence)
NATIVE = {
    "zh-hans": ("【附加包】", "（死后清空）", "（永久）", "期间整个化身恶魔。"),
    "zh-hant": ("【擴充包】", "（死後清空）", "（永久）", "期間整個化身惡魔。"),
    "en": ("[Add-on] ", " (lost on death)", " (for good)", " His whole body becomes the demon."),
    "ko": ("[확장] ", "(사망 시 초기화)", "(영구)", " 온몸이 악마로 변합니다."),
    "ja": ("【拡張】", "（死亡で消える）", "（永続）", "その間全身が悪魔になる。"),
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_swain differs from build_swain.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":flock":
        sys.exit("the copy has no league_swain:flock passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    texts = {}
    for lang, (mark, lost, kept, demon) in NATIVE.items():
        attack = setup.TEXT[lang]["attack"]
        if lost not in attack:
            sys.exit(f"{lang}: the main pack's attack text no longer says {lost!r}: update this script")
        texts[lang] = {"attack": (mark + attack.replace(lost, kept)).format(**values),
                       "ult": (mark + setup.TEXT[lang]["ult"] + demon).format(**values)}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in texts.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in texts.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
