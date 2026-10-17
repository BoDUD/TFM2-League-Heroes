"""Build the add-on's copy of Zilean from the main pack (Chronoshift guard + rewind v2).

    python addons/league_zilean_rewind/make_override.py

Reads league/champion/league_zilean.data_champion and league/text/champion.i18n and writes
addons/league_zilean_rewind/override/league_zilean.data_champion and .../text/champion.i18n:
the same kit with three changes -
  * the main pack's armed R check in each of the four actions (an ally in CC, or himself with two
    enemy champions close, gets the 5 s rune and a fixed heal at tick 299) is dropped; R still arms
    when the AI casts it (900 ticks, refunded when unused);
  * passive_ult = the add-on's passive league_zilean_rewind:guard, which while R is armed puts the
    rune on the allied champion (or Zilean) in danger - an enemy champion close and low health or a
    big hit just taken - and the add-on rewinds that champion only when lethal damage lands (2.5 s
    banished and immune, then the heal); an unused rune heals nothing;
  * R's tooltip points to description.league_zilean_rewind.ult (the guard + rewind text with a
    "rewind test build" lead, so the tooltip in game shows whether the override took).
Soraka, Kayle and every other champion stay untouched. Run it again whenever the main pack's
Zilean changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_zilean_rewind")
MOD_ID = "league_zilean_rewind"
TEXT_KEY = "description.league_zilean_rewind.ult"
ARMED = "league_zilean_r_armed"
BUSY = "league_zilean_r_busy"
AP = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TEXT = {
    "zh-hans": "【复活测试版】附近的友方英雄或基兰自己快要阵亡时（身边有敌人，生命低于<#ffb900ff>30%<>或刚被打掉一大截），"
               "为其挂上时光符文<#ffb900ff>5秒<>：期间受到致命伤害不会阵亡，而是时光倒流<#ffb900ff>2.5秒<>（无法被选中），"
               f"之后回复<#6aff55ff>400<> + {AP}<#6aff55ff>150% 法强<>生命值；符文没用上则不回血。",
    "zh-hant": "【復活測試版】附近的友方英雄或極靈自己快要陣亡時（身邊有敵人，生命低於<#ffb900ff>30%<>或剛被打掉一大截），"
               "為其掛上時光符文<#ffb900ff>5秒<>：期間受到致命傷害不會陣亡，而是時光倒流<#ffb900ff>2.5秒<>（無法被選取），"
               f"之後回復<#6aff55ff>400<> + {AP}<#6aff55ff>150% 法術強度<>生命；符文沒用上則不回復。",
    "en": "[Rewind test build] When an allied champion near him (or Zilean himself) is about to die - an enemy close and "
          "health below <#ffb900ff>30%<> or a big hit just taken - he places a time rune on them for <#ffb900ff>5s<>: "
          f"lethal damage instead rewinds them for <#ffb900ff>2.5s<> (untargetable), then they revive with "
          f"<#6aff55ff>400<> + {AP}<#6aff55ff>150% AP<> health. An unused rune does nothing.",
    "ko": "[되감기 테스트판] 주변 아군 챔피언이나 질리언 자신이 쓰러지기 직전이면(적이 가까이 있고 체력 "
          "<#ffb900ff>30%<> 미만이거나 방금 크게 맞음) <#ffb900ff>5초<> 동안 시간의 룬을 겁니다: 치명적인 피해를 받으면 "
          f"<#ffb900ff>2.5초<> 동안 시간이 되돌아간 뒤(대상 지정 불가) <#6aff55ff>400<> + {AP}<#6aff55ff>150% 주문력<>의 "
          "체력으로 되살아납니다. 쓰이지 않은 룬은 효과가 없습니다.",
    "ja": "【巻き戻し試験版】近くの味方チャンピオンかジリアン自身が倒れそうな時（敵が近く、体力<#ffb900ff>30%<>未満か大きな"
          "ダメージ直後）、その対象に<#ffb900ff>5秒<>時のルーン：致命傷を受けると倒れず<#ffb900ff>2.5秒<>時が戻り（対象不可）、"
          f"<#6aff55ff>400<> + {AP}<#6aff55ff>150% 魔力<>の体力で復活。使われなければ効果なし。",
}
# the skill details panel's limits (lint_mod.TOOLTIP_MAX)
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def is_pulse(node):
    """The main pack's armed R check: SwitchByBuff on r_armed whose armed branch checks r_busy."""
    return (isinstance(node, dict) and node.get("type") == "SwitchByBuff" and node.get("buff_name") == ARMED
            and isinstance(node.get("effect_buff"), dict) and node["effect_buff"].get("buff_name") == BUSY)


def drop_pulses(node, counts):
    """Replace every armed R check with an empty Combine (the guard passive picks the rune's target)."""
    items = node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else []
    for key, value in list(items):
        if is_pulse(value):
            node[key] = {"type": "Combine", "effects": []}
            counts["pulses"] += 1
        else:
            drop_pulses(value, counts)


def main():
    src = os.path.join(ROOT, "league", "champion", "league_zilean.data_champion")
    with open(lp(src), encoding="utf-8") as f:
        champion = json.load(f)
    champion["ult"]["description"] = "#asset/base/text/champion?" + TEXT_KEY
    counts = {"pulses": 0}
    for slot in ("attack", "skill", "skill2", "ult"):
        drop_pulses(champion[slot], counts)
    if counts["pulses"] != 4:
        sys.exit("expected the armed R check in the 4 actions, found %d: update this script" % counts["pulses"])
    kit = json.dumps([champion[slot] for slot in ("attack", "skill", "skill2", "ult")])
    if "league_zilean_r_rune" in kit or '"tick": 299' in kit:
        sys.exit("the rune or its heal timer is still in the kit after dropping the checks: update this script")
    ult = json.dumps(champion["ult"])
    if ARMED not in ult or "league_zilean_r_retry" not in ult:
        sys.exit("R no longer arms / refunds itself: update this script")
    if "passive_ult" in champion:
        sys.exit("the main pack's Zilean has a passive_ult now: update this script")
    champion["passive_ult"] = {"passive_ref": MOD_ID + ":guard", "params": {}}
    long = {lang: shown_length(t) for lang, t in TEXT.items() if shown_length(t) > TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_zilean.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(TEXT)
    if missing:
        sys.exit("no rewind text for %s" % sorted(missing))
    text = {lang: {"description": {MOD_ID: {"ult": TEXT[lang]}}} for lang in main_text}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "-", counts["pulses"],
          "armed R checks dropped, passive_ult = guard")


if __name__ == "__main__":
    main()
