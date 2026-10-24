#!/usr/bin/env python3
"""league_ahri's tooltips for tools/fix/ahri_league.py's kit (five languages, the numbers from its P):
the attack (it carries Essence Theft), Charm (the slow instead of the damage amp), Spirit Rush (the recast window) and
Fox-Fire's haste time in Orb of Deception's text.

    python tools/fix/ahri_league_text.py

Also used by addons/league_ahri/make_override.py for the add-on's attack text (attack(lang, addon=True)).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ahri_league as K  # noqa: E402

ROOT = K.ROOT
PATH = os.path.join(ROOT, "league", "text", "champion.i18n")
O, M, Y, G, R, E = "<#ff9028ff>", "<#a974ffff>", "<#ffb900ff>", "<#6aff55ff>", "<#ef5350ff>", "<>"
AP = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
AD = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
AP_WORD = {"zh-hans": "% 法术强度", "zh-hant": "% 魔法強度", "en": "% Ability Power", "ko": "", "ja": ""}


def ap(lang, n):
    if lang == "ko":
        return AP + M + f"주문력의 {n}%" + E
    if lang == "ja":
        return AP + M + f"魔力の{n}%" + E
    return AP + M + f"{n}{AP_WORD[lang]}" + E


def y(x):
    return Y + str(x) + E


def g(x):
    return G + str(x) + E


def sec(t):
    s = t / 60
    return f"{s:g}"


def attack(lang, p, addon=False):
    k, ka, t, ta, w = p["k_heal"], p["k_ap"], p["t_heal"], p["t_ap"], sec(p["p_win"])
    if lang == "zh-hans":
        kills = "每补到" + y(1) + "个小兵或野怪（用什么打死的都算）" if addon else "普攻每打死" + y(1) + "个小兵或野怪"
        champ = "她参与击杀的每个敌方英雄都让她" if addon else "她" + y(w + "秒") + "内伤害过的敌方英雄阵亡时，"
        return ("【附加包】" if addon else "") + "普攻发射妖力球，造成" + AD + O + "100% 攻击力" + E + "的" + O + "物理伤害" + E + \
            "。被动 " + O + "摄魂夺魄" + E + "：" + kills + "积攒" + y(1) + "层，满" + y(9) + "层回复" + g(k) + " + " + \
            ap(lang, ka) + "的" + G + "生命值" + E + "；" + champ + "回复" + g(t) + " + " + ap(lang, ta) + "的" + G + "生命值" + E + "。"
    if lang == "zh-hant":
        kills = "每擊殺" + y(1) + "個小兵或野怪（用什麼打死的都算）" if addon else "普攻每擊殺" + y(1) + "個小兵或野怪"
        champ = "她參與擊殺的每個敵方英雄都讓她" if addon else "她" + y(w + "秒") + "內傷害過的敵方英雄陣亡時，"
        return ("【附加包】" if addon else "") + "普攻發射妖力球，造成" + AD + O + "100% 攻擊力" + E + "的" + O + "物理傷害" + E + \
            "。被動 " + O + "銷魂" + E + "：" + kills + "累積" + y(1) + "層，滿" + y(9) + "層回復" + g(k) + " + " + \
            ap(lang, ka) + "的" + G + "生命值" + E + "；" + champ + "回復" + g(t) + " + " + ap(lang, ta) + "的" + G + "生命值" + E + "。"
    if lang == "en":
        kills = "every minion or monster she kills (with anything)" if addon else "every minion or monster her attacks kill"
        champ = ("Every enemy champion she takes down heals her " if addon else
                 "When an enemy champion she damaged in the last " + y(w + "s") + " dies, she heals ")
        return ("[Add-on] " if addon else "") + "Basic attacks fire a fox-magic orb for " + AD + O + "100% AD" + E + " " + O + \
            "physical damage" + E + ". Passive " + O + "Essence Theft" + E + ": " + kills + " grants an essence; at " + y(9) + \
            " she heals " + g(k) + " + " + ap(lang, ka) + ". " + champ + g(t) + " + " + ap(lang, ta) + "."
    if lang == "ko":
        kills = "미니언이나 몬스터를 처치할 때마다(무엇으로든)" if addon else "기본 공격으로 미니언이나 몬스터를 처치할 때마다"
        champ = "관여한 적 챔피언 처치마다 " if addon else y(w + "초") + " 안에 피해를 입힌 적 챔피언이 죽으면 "
        return ("[확장] " if addon else "") + "기본 공격으로 여우 구슬을 날려 " + AD + O + "공격력의 100%" + E + " " + O + "물리 피해" + E + \
            "를 입힙니다. 기본 지속 효과 " + O + "정기 흡수" + E + ": " + kills + " 정기 1개, " + y(9) + "개가 모이면 " + g(k) + " + " + \
            ap(lang, ka) + "의 " + G + "체력" + E + "을 회복합니다. " + champ + g(t) + " + " + ap(lang, ta) + "의 " + G + "체력" + E + \
            "을 회복합니다."
    if lang == "ja":
        kills = "ミニオンかモンスターを倒すたびに（何で倒しても）" if addon else "通常攻撃でミニオンかモンスターを倒すたびに"
        champ = "敵チャンピオンの撃破に関わるたびに" if addon else y(w + "秒") + "以内にダメージを与えた敵チャンピオンが倒れると"
        return ("【拡張】" if addon else "") + "通常攻撃は妖力の玉を放ち、" + AD + O + "攻撃力の100%" + E + "の" + O + "物理ダメージ" + E + \
            "を与える。パッシブ " + O + "生気吸引" + E + "：" + kills + "生気1つ、" + y(9) + "つで" + g(k) + " + " + ap(lang, ka) + \
            "の" + G + "体力" + E + "を回復。" + champ + g(t) + " + " + ap(lang, ta) + "の" + G + "体力" + E + "を回復。"
    raise KeyError(lang)


def ult(lang, p):
    n, w, more = 2, sec(p["r_win"]), sec(p["r_more"])
    if lang == "zh-hans":
        return "向前冲刺（离敌方英雄太近时向后冲），再向附近敌人射出" + y(3) + "枚精魄弹，优先英雄，每枚造成" + M + "55" + E + " + " + \
            ap(lang, 35) + "的" + M + "魔法伤害" + E + "。施放后" + y(w + "秒") + "内可再施放" + y(n) + "次；期间参与击杀英雄再给" + \
            y(1) + "次，并至少再开" + y(more + "秒") + "。"
    if lang == "zh-hant":
        return "向前衝刺（離敵方英雄太近時向後衝），再向附近敵人射出" + y(3) + "枚精魄彈，優先英雄，每枚造成" + M + "55" + E + " + " + \
            ap(lang, 35) + "的" + M + "魔法傷害" + E + "。施放後" + y(w + "秒") + "內可再施放" + y(n) + "次；期間參與擊殺英雄再給" + \
            y(1) + "次，並至少再開" + y(more + "秒") + "。"
    if lang == "en":
        return "Ahri dashes (away from an enemy champion that is too close, otherwise toward her target), then fires " + y(3) + \
            " essence bolts at nearby enemies, champions first, each dealing " + M + "55" + E + " + " + ap(lang, 35) + " " + M + \
            "magic damage" + E + ". She can cast it " + y(n) + " more times within " + y(w + "s") + \
            "; a champion takedown meanwhile grants one more and keeps it open at least " + y(more + "s") + "."
    if lang == "ko":
        return "돌진한 뒤(적 챔피언이 너무 가까우면 뒤로) 주변 적에게 정기 구슬 " + y(3) + "개를 쏩니다(챔피언 우선). 구슬마다 " + M + "55" + E + \
            " + " + ap(lang, 35) + " " + M + "마법 피해" + E + ". 사용 후 " + y(w + "초") + " 안에 " + y(n) + \
            "번 더 쓸 수 있고, 그동안 챔피언 처치에 관여하면 1번 더, 최소 " + y(more + "초") + " 더 열립니다."
    if lang == "ja":
        return "ダッシュし（敵チャンピオンが近すぎれば後方へ）、近くの敵に精気弾を" + y(3) + "発放つ（チャンピオン優先）。1発ごとに" + M + "55" + E + \
            " + " + ap(lang, 35) + "の" + M + "魔法ダメージ" + E + "。使用後" + y(w + "秒") + "以内にあと" + y(n) + \
            "回使え、その間にチャンピオンを倒すと1回追加、最低" + y(more + "秒") + "延長。"
    raise KeyError(lang)


CHARM = {
    "zh-hans": ("；该英雄" + y("2秒") + "内受到的伤害提高" + y("15%") + "。", "，期间减速" + y("{s}%") + "。"),
    "zh-hant": ("；該英雄" + y("2秒") + "內受到的傷害提高" + y("15%") + "。", "，期間緩速" + y("{s}%") + "。"),
    "ko": (" 대상은 " + y("2초") + " 동안 받는 피해가 " + y("15%") + " 증가합니다.", " 매혹된 동안 " + y("{s}%") + " 느려집니다."),
    "ja": ("対象は" + y("2秒") + "間受けるダメージが" + y("15%") + "増加する。", "魅了中は" + y("{s}%") + "スロウ。"),
}
HASTE = {"zh-hans": "秒", "zh-hant": "秒", "en": "s", "ko": "초", "ja": "秒"}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}     # lint_mod's


def shown_length(s):
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def main():
    p = dict(K.P)
    raw = open(K.lp(PATH), "rb").read()
    t = json.loads(raw.decode("utf-8-sig"))
    for lang, tab in t.items():
        d = tab["description"]["league_ahri"]
        d["attack"] = attack(lang, p)
        d["ult"] = ult(lang, p)
        if lang == "en":
            d["skill2"] = re.sub(r" It takes .*$", " Charmed, it is slowed by " + y(f"{p['e_slow']}%") + ".", d["skill2"])
        else:
            old, new = CHARM[lang]
            if old in d["skill2"]:
                d["skill2"] = d["skill2"].replace(old, new.format(s=p["e_slow"]))
        d["skill"] = d["skill"].replace(y("1.5" + HASTE[lang]), y(sec(p["w_haste"]) + HASTE[lang]))
        assert "15%" not in d["skill2"], (lang, d["skill2"])
        for k in ("attack", "skill", "skill2", "ult"):
            n = shown_length(d[k])
            assert n <= TOOLTIP_MAX[lang], f"{lang}.{k}: {n} > {TOOLTIP_MAX[lang]}"
    text = json.dumps(t, ensure_ascii=False, indent=2)
    if b"\r\n" in raw:
        text = text.replace("\n", "\r\n")
    open(K.lp(PATH), "wb").write((raw[:3] if raw.startswith(b"\xef\xbb\xbf") else b"") + text.encode("utf-8"))


if __name__ == "__main__":
    main()
