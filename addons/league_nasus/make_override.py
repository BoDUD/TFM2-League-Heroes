"""Build the add-on's copy of Nasus from the main pack (Siphoning Strike stacks kept through death, Fury of the Sands
halving Q only, the whole big body).

    python addons/league_nasus/make_override.py

Rebuilds Nasus with tools/kit/build_nasus.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_nasus.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_nasus/override/league_nasus.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (R's moment too: the data judges it, the add-on only logs it);
  * passive = the add-on's league_nasus:soul_eater with the numbers of P;
  * R's buff without the skill_cooldown_mult that halved E too (the add-on halves Q alone);
  * Q's and R's tooltips point to description.league_nasus.skill / .ult with the add-on's wording (the stacks kept for
    good, only Q's cooldown halved, the whole big body), keys of the add-on's own id, so the tooltip in game shows
    whether the override took.
The whole big body needs no data: the add-on's display hook reads the main pack's own buff league_nasus_r_on.
Every other champion stays untouched. Run it again whenever the main pack's Nasus changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_nasus")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_nasus as kit  # noqa: E402
import setup_nasus as setup  # noqa: E402

MOD_ID = "league_nasus"
HERO = "league_nasus"
SLOTS = ("skill", "ult")
# lang -> (the add-on's mark, the main pack's words for "lost on death" -> the add-on's, the ult's added sentence)
NATIVE = {
    "zh-hans": ("【附加包】", "（死后清空）", "（永久）", "Q、E冷却减半", "Q冷却减半", "期间整个人变大。"),
    "zh-hant": ("【擴充包】", "（死後清空）", "（永久）", "Q、E冷卻減半", "Q冷卻減半", "期間整個人變大。"),
    "en": ("[Add-on] ", " (lost on death)", " (for good)", "Q and E cooldowns halved", "Q's cooldown halved",
           " His whole body grows."),
    "ko": ("[확장] ", "(사망 시 초기화)", "(영구)", "Q·E 재사용 대기시간 절반", "Q 재사용 대기시간 절반", " 온몸이 커집니다."),
    "ja": ("【拡張】", "（死亡で消える）", "（永続）", "Q・Eのクールダウン半減", "Qのクールダウン半減", "その間全身が巨大化する。"),
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
        sys.exit("the main pack's league_nasus differs from build_nasus.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":soul_eater":
        sys.exit("the copy has no league_nasus:soul_eater passive: update this script")
    if "skill_cooldown_mult" in json.dumps(champion):
        sys.exit("the copy's R still carries skill_cooldown_mult: update build_nasus.build(native=1)")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    texts = {}
    for lang, (mark, lost, kept, both, q_only, big) in NATIVE.items():
        skill, ult = setup.TEXT[lang]["skill"], setup.TEXT[lang]["ult"]
        if lost not in skill:
            sys.exit(f"{lang}: the main pack's Q text no longer says {lost!r}: update this script")
        if both not in ult:
            sys.exit(f"{lang}: the main pack's R text no longer says {both!r}: update this script")
        texts[lang] = {"skill": (mark + skill.replace(lost, kept)).format(**values),
                       "ult": (mark + ult.replace(both, q_only) + big).format(**values)}
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
