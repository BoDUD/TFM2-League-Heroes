"""Build the add-on's copy of Tryndamere from the main pack (Undying Rage at low health).

    python addons/league_tryndamere_rage/make_override.py

Rebuilds Tryndamere with tools/kit/build_tryndamere.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_tryndamere.data_champion byte for byte (so the copy never drifts from the shipped kit),
and writes addons/league_tryndamere_rage/override/league_tryndamere.data_champion and .../text/champion.i18n:
the same kit with three changes -
  * the main pack's danger check in his attack (two enemy champions on him, or hit at five checks in a row, while R
    is armed) is dropped; R still arms when the AI casts it (900 ticks, refunded when unused);
  * passive = the add-on's league_tryndamere_rage:guard with the numbers from P as its params: while R is armed it
    starts Undying Rage when his health drops low or a burst lands (an enemy champion close), and with R not armed it
    drinks Bloodlust when he is hurt;
  * R's tooltip points to description.league_tryndamere_rage.ult (a "low-health test build" lead, so the tooltip in
    game shows whether the override took).
Every other champion stays untouched. Run it again whenever the main pack's Tryndamere changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_tryndamere_rage")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_tryndamere as kit  # noqa: E402

MOD_ID = "league_tryndamere_rage"
TEXT_KEY = "description.league_tryndamere_rage.ult"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
A, G, O, E = "<#ffb900ff>", "<#66bb6aff>", "<#ff9028ff>", "<>"
TEXT = {
    "zh-hans": "【残血开大测试版】身边有敌方英雄、生命低于" + A + "{r_hp}%" + E + "（或刚被打掉一大截）时爆发：怒气全满，" + A + "{r_t}秒" + E +
               "内生命不会降到1以下；结束时施放" + O + "嗜血杀戮" + E + "，按怒气回复" + G + "{q_heal}" + E + " + " + ADi + G + "{q_heal_ratio}%" + E +
               "生命，每层再加" + G + "{q_per}" + E + " + " + ADi + G + "{q_per_ratio}%" + E + "。大招没好时残血也会喝嗜血杀戮。",
    "zh-hant": "【殘血開大測試版】身邊有敵方英雄、生命低於" + A + "{r_hp}%" + E + "（或剛被打掉一大截）時爆發：怒氣全滿，" + A + "{r_t}秒" + E +
               "內生命不會降到1以下；結束時施放" + O + "嗜血殺戮" + E + "，按怒氣回復" + G + "{q_heal}" + E + " + " + ADi + G + "{q_heal_ratio}%" + E +
               "生命，每層再加" + G + "{q_per}" + E + " + " + ADi + G + "{q_per_ratio}%" + E + "。大招沒好時殘血也會喝嗜血殺戮。",
    "en": "[Low-health test build] With an enemy champion close and his health below " + A + "{r_hp}%" + E + " (or a big hit just "
          "taken): full Fury, and for " + A + "{r_t}s" + E + " his health cannot fall below 1. As it ends he casts " + O + "Bloodlust" + E +
          ", spending his Fury to heal " + G + "{q_heal}" + E + " + " + ADi + G + "{q_heal_ratio}%" + E + ", plus " + G + "{q_per}" + E +
          " + " + ADi + G + "{q_per_ratio}%" + E + " per stack. With R not ready he drinks Bloodlust when hurt.",
    "ko": "[빈사 발동 테스트판] 적 챔피언이 가까이 있고 체력이 " + A + "{r_hp}%" + E + " 미만(또는 방금 크게 맞음)이면 발동: 분노가 가득 차고 " + A +
          "{r_t}초" + E + " 동안 체력이 1 아래로 떨어지지 않습니다. 끝날 때 " + O + "피의 갈망" + E + "으로 " + G + "{q_heal}" + E + " + " + ADi + G +
          "{q_heal_ratio}%" + E + ", 중첩당 " + G + "{q_per}" + E + " + " + ADi + G + "{q_per_ratio}%" + E + " 회복. 궁극기가 없을 때도 빈사면 피의 갈망을 씁니다.",
    "ja": "【瀕死発動テスト版】敵チャンピオンが近くにいて体力" + A + "{r_hp}%" + E + "未満（か大ダメージ直後）で発動：フューリー最大、" + A + "{r_t}秒" + E +
          "間体力が1未満にならない。終わりに" + O + "血の欲望" + E + "で" + G + "{q_heal}" + E + " + " + ADi + G + "{q_heal_ratio}%" + E + "、1つにつき" +
          G + "{q_per}" + E + " + " + ADi + G + "{q_per_ratio}%" + E + "回復。アルティメットがない時も瀕死なら血の欲望を使う。",
}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_tryndamere.data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_tryndamere differs from build_tryndamere.P: rebuild it first")
    champion = kit.build(p, native=True)
    attack = json.dumps(champion["attack"])
    if "league_tryndamere_go" in attack or "league_tryndamere_sense" in attack:
        sys.exit("the danger check is still in the attack: update this script")
    ult = json.dumps(champion["ult"])
    if "league_tryndamere_r_armed" not in ult or "league_tryndamere_r_retry" not in ult:
        sys.exit("R no longer arms / refunds itself: update this script")
    champion["ult"]["description"] = "#asset/base/text/champion?" + TEXT_KEY
    values = {k: p[k] for k in ("q_heal", "q_heal_ratio", "q_per", "q_per_ratio")}
    values.update(r_hp=p["n_r_hp"], r_t=f"{p['r_t'] / 60:g}")
    texts = {lang: t.format(**values) for lang, t in TEXT.items()}
    long = {lang: shown_length(t) for lang, t in texts.items() if shown_length(t) > TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_tryndamere.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no low-health text for %s" % sorted(missing))
    text = {lang: {"description": {MOD_ID: {"ult": texts[lang]}}} for lang in main_text}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- danger check dropped, passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))


if __name__ == "__main__":
    main()
