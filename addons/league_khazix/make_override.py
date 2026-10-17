"""Build the add-on's copy of Kha'Zix from the main pack (Unseen Threat from vision, evolutions from his level).

    python addons/league_khazix/make_override.py

Rebuilds Kha'Zix with tools/kit/build_khazix.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_khazix.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_khazix/override/league_khazix.data_champion and .../text/champion.i18n: the build with native=1 -
  * no level probes in the attack and no "ready after quiet ticks" check in the actions (R's stealth still readies it);
  * passive = the add-on's league_khazix:void with {lv_q, lv_e, lv_r, q_evo_range}: every tick it readies Unseen Threat
    while the enemy team cannot see him and puts on the evolutions his level has reached;
  * the attack's tooltip (the passive) points to description.league_khazix.attack with a "test build" lead and the
    vision wording, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Kha'Zix changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_khazix")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_khazix as kit  # noqa: E402
import setup_khazix as setup  # noqa: E402

MOD_ID = "league_khazix"
# lang -> (the lead, the main pack's out-of-combat wording, the vision wording)
NATIVE = {
    "zh-hans": ("【视野测试版】", "隐身或{quiet}秒没出手后", "不在敌方视野里时"),
    "zh-hant": ("【視野測試版】", "隱形或{quiet}秒沒出手後", "不在敵方視野裡時"),
    "en": ("[Vision test build] ", "after stealth or {quiet}s without acting", "while the enemy cannot see him"),
    "ko": ("[시야 테스트판] ", "은신 후 또는 {quiet}초간 행동하지 않으면", "적에게 보이지 않을 때"),
    "ja": ("【視界テスト版】", "インビジブル後か{quiet}秒行動しないと", "敵から見えていない時"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_khazix.data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_khazix differs from build_khazix.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if "pr_lv" in text or "league_khazix_fight" in text:
        sys.exit("the copy still probes or checks the quiet ticks: update this script")
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":void":
        sys.exit("the copy has no league_khazix:void passive: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    values = setup.values(p)
    texts = {}
    for lang, (lead, old, new) in NATIVE.items():
        attack = setup.TEXT[lang]["attack"]
        if attack.count(old) != 1:
            sys.exit(f"{lang}: the main pack's passive text changed ({old!r} not found once): update NATIVE")
        texts[lang] = (lead + attack.replace(old, new)).format(**values)
    long = {lang: setup.shown_length(t) for lang, t in texts.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_khazix.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no test-build text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: {"attack": texts[lang]}}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {lang: f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
