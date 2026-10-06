"""Build the add-on's copy of Fiora from the main pack (Grand Challenge's Vitals only on the challenged champion).

    python addons/league_fiora_duel/make_override.py

Reads the main pack's league/champion/league_fiora.data_champion (with tools/fix/fix_fiora_r_zone.py applied: the
Victory Zone already lands on the challenged champion) and writes addons/league_fiora_duel/override/
league_fiora.data_champion and .../text/champion.i18n, the same kit with three changes:
  * where R starts (the ult slot's champion and the armed attack's champion twin) the challenged champion gets the
    target buff league_fiora_r_mark for R's 480 ticks (no picture: the main pack's Vital marks are the picture);
  * the five Vital hooks (the attack, Q's two strikes, W's two lines: a SwitchByBuff league_fiora_r_on whose branch is
    the r_v4..r_v1 ladder) become: the Native league_fiora_duel:vital on the champion hit (it adds the 3-tick caster
    flag league_fiora_r_tgt when Fiora's R is on and that champion carries the mark), then r_tgt -> the R ladder (the
    flag removed), else the passive's Vital (the hook's own other branch) - read once in the same tick and, while R is
    on, again a tick later (when a buff the add-on adds becomes visible to the data is not proven in game);
  * R's tooltip points to description.league_fiora_duel.ult (the main pack's text with a "test build" lead and a line
    saying only the challenged champion has the Vitals), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Fiora changes.
"""
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_fiora_duel")
MOD_ID = "league_fiora_duel"
HERO = "league_fiora"
N = HERO + "_"
R_T = 480
O, A, G, E = "<#ff9028ff>", "<#ffb900ff>", "<#6aff55ff>", "<>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
HEAL = G + "40" + E + " + " + ADi + G + "24% "
# the test build's R text (shorter than the main pack's: the lead and the new rule must fit); MUST lists what the main
# pack's text says too, so a change there stops the script
TEXTS = {
    "zh-hans": "【破绽测试版】" + O + "无双挑战" + E + "：在一名敌方英雄身上亮出" + A + "4" + E + "处" + O + "破绽" + E + "（" + A + "8秒" + E +
               "），只有他身上有。每次命中他刺中一处，" + A + "Q、W冷却减半" + E + "；打别的英雄只出普通被动破绽。刺满4处或他被刺后死亡，" +
               "留下" + G + "胜利之地" + E + "：" + A + "3秒" + E + "内每秒为友方英雄回复" + HEAL + "攻击力" + E + "生命值。",
    "zh-hant": "【破綻測試版】" + O + "無雙挑戰" + E + "：在一名敵方英雄身上亮出" + A + "4" + E + "處" + O + "破綻" + E + "（" + A + "8秒" + E +
               "），只有他身上有。每次命中他刺中一處，" + A + "Q、W冷卻減半" + E + "；打別的英雄只出普通被動破綻。刺滿4處或他被刺後死亡，" +
               "留下" + G + "勝利之地" + E + "：" + A + "3秒" + E + "內每秒為友方英雄回復" + HEAL + "攻擊力" + E + "生命值。",
    "en": "[Vitals test build] " + O + "Grand Challenge" + E + ": reveals " + A + "4" + E + " " + O + "Vitals" + E + " on one enemy champion "
          "for " + A + "8s" + E + ", on him alone. Each hit on him strikes one and " + A + "halves Q's and W's cooldowns" + E + "; other "
          "champions only get the passive's Vital. All 4 struck, or his death after one, leaves a " + G + "Victory Zone" + E + " healing "
          "allies " + HEAL + "AD" + E + " a second for " + A + "3s" + E + ".",
    "ko": "[급소 테스트판] " + O + "대결 신청" + E + ": 적 챔피언 하나에게 " + A + "4" + E + "개의 " + O + "급소" + E + "(" + A + "8초" + E + "), 그에게만 "
          "생깁니다. 그를 맞힐 때마다 하나씩 찌르고 " + A + "Q·W 재사용 대기시간 절반" + E + "; 다른 챔피언은 기본 급소만. 4개를 다 찌르거나 찌른 뒤 "
          "그가 죽으면 " + G + "승리의 영역" + E + ": " + A + "3초" + E + " 동안 매초 아군 챔피언 " + HEAL + "공격력" + E + " 회복.",
    "ja": "【急所テスト版】" + O + "グランドチャレンジ" + E + "：敵チャンピオン1体に" + A + "4" + E + "つの" + O + "急所" + E + "（" + A + "8秒" + E +
          "）、その相手だけ。命中ごとに1つ突き" + A + "Q・WのCD半減" + E + "、他の敵はパッシブの急所だけ。4つ突くか突いた後に倒すと" + G +
          "勝利の地" + E + "：" + A + "3秒" + E + "間毎秒味方を" + HEAL + "攻撃力" + E + "回復。",
}
MUST = ["4", "8", "3", "40", "24%"]
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in list(o.values()):
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": N + buff, "effect_buff": yes,
            "effect_none": no or {"type": "Combine", "effects": []}}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


def main():
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if N + "r_won" not in json.dumps(champion):
        sys.exit("the main pack's Fiora lacks the Victory Zone fix: run tools/fix/fix_fiora_r_zone.py first")

    # R's starts: the challenged champion gets the mark
    starts = []

    def start(o):
        if o.get("type") == "Combine" and any(
                e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] == N + "r_on"
                and e["buff_state"]["duration"] == {"Time": {"tick": R_T}} for e in o.get("effects", [])):
            starts.append(o)

    for slot in ("attack", "ult"):
        walk(champion[slot]["effect"], start)
    starts = list({id(x): x for x in starts}.values())
    if len(starts) != 2:
        sys.exit(f"expected 2 R starts, found {len(starts)}: update this script")
    for o in starts:
        o["effects"].append({"type": "AddBuff", "buff_state": {"name": N + "r_mark",
                                                               "duration": {"Time": {"tick": R_T}}}})

    # the five Vital hooks
    hooks = []

    def hook(o):
        if (o.get("type") == "SwitchByBuff" and o.get("buff_name") == N + "r_on"
                and o.get("effect_buff", {}).get("buff_name") == N + "r_v4"):
            hooks.append(o)

    for slot in ("attack", "skill", "skill2"):
        walk(champion[slot]["effect"], hook)
    hooks = list({id(x): x for x in hooks}.values())
    if len(hooks) != 5:
        sys.exit(f"expected 5 Vital hooks, found {len(hooks)}: update this script")
    for o in hooks:
        ladder, passive = o["effect_buff"], o["effect_none"]
        duel = combine({"type": "RemoveCasterBuff", "name": N + "r_tgt"}, ladder)
        late = sw("r_on", {"type": "Delayed", "tick": 1,
                           "effects": [sw("r_tgt", copy.deepcopy(duel), copy.deepcopy(passive))]}, copy.deepcopy(passive))
        new = combine({"type": "Native", "effect_ref": MOD_ID + ":vital"}, sw("r_tgt", duel, late))
        o.clear()
        o.update(new)
    champion["ult"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".ult"

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    for lang in main_text:
        ult = re.sub(r"<[^>]*>", "", main_text[lang]["description"][HERO]["ult"])
        missing = [m for m in MUST if m not in ult]
        if missing:
            sys.exit(f"{lang}: the main pack's R text no longer says {missing}: update TEXTS")
    texts = {lang: TEXTS[lang] for lang in main_text}
    long = {lang: shown_length(t) for lang, t in texts.items() if shown_length(t) > TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: {"ult": texts[lang]}}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), f"- {len(starts)} R starts mark,",
          f"{len(hooks)} Vital hooks ask {MOD_ID}:vital")
    print("tooltip lengths", {lang: f"{shown_length(t)}/{TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
