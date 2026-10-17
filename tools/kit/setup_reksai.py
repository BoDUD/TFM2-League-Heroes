"""Rek'Sai's text (5 languages), sound_info files and her keys in the shared files, numbers from build_reksai.P.

    python tools/kit/setup_reksai.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_reksai in every language, description + skill_name),
sound/sfx/league_reksai_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (0.128.0, Rek'Sai named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 雷克塞 / 虚空遁地兽: 艾克塞之怒, 女王之怒 / 猎物搜寻, 遁地 / 破土而出, 狂野之噬 / 挖掘隧道, 虚空猛冲;
zh_TW 雷珂煞: 憤怒沙蟲, 女王之怒 / 尋找獵物, 深掘 / 猛襲, 狂食 / 翻山, 虛空疾行; ja レク＝サイ: ゼル＝サイの怒り, 女王の怒り / 獲物定め,
潜伏 / 襲撃, 激情の牙 / 掘削, ヴォイドラッシュ; ko 렉사이: 제르사이의 분노, 여왕의 진노 / 먹잇감 추적, 매복 / 돌출, 성난 이빨 / 땅굴 파기,
공허의 돌진.
Slots: skill = Q Queen's Wrath (named) with Prey Seeker in its text, skill2 = W Burrow (named) with Unburrow, ult = R;
the passive and Furious Bite (E, at full Fury) in the attack's text; the tunnels (E2) are the add-on's and its texts.
No combo sentence in any text (the user's rule). No `league_reksai_attack` sound: the engine would play it at the start
of every attack; the swipe plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_reksai import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_reksai"
VERSION = "0.128.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#4fc3f7ff>"      # true damage
E = "<>"
# champion_view: the face between her helmet and her mouth (she has no eyes; tfm2_ase.py face puts the crown on the
# crest's tip, 35 px over the claws); the idle tops 25.5 px over the pivot, under the card's -28: no banpick_center
VIEW = {"face": {"x": 15, "y": -20}, "center": {"x": 0, "y": -12}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TRUE = G + "{e_dmg}" + E + " + " + ADi + G + "{e_ratio}%" + E

TEXT = {
    "zh-hans": {
        "name": "雷克塞",
        "attack": "爪咬。" + O + "艾克塞之怒" + E + "：攻击和技能命中攒怒气（最多4层，" + A + "{fury_t}秒" + E + "内不打就消散）；满怒时下一口变成" + O +
                  "狂野之噬" + E + "，造成" + TRUE + G + "真实伤害" + E + "（" + A + "{e_cd}秒" + E + "一次）。钻地时消耗怒气回复生命。",
        "skill": "敌人在身边：扑击造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "，" + A + "{q_t}秒" + E + "内攻速+{q_as}%，之后2次攻击溅射周围（+{q_bonus}%攻击力）。在远处：钻地打出" + O +
                 "猎物搜寻" + E + "，直线冲击波造成" + phy("q2_dmg", "q2_ratio") + O + "物理伤害" + E + "。",
        "skill2": "钻入地下冲到目标脚下，" + O + "破土而出" + E + "：周围敌人受到" + phy("w_dmg", "w_ratio") + O + "物理伤害" + E + "并" + R + "击飞{w_up}秒" + E +
                  "。敌方英雄扎堆而身边没有队友时不会钻过去。",
        "ult": "只对被她伤过的" + O + "猎物" + E + "：钻进地底" + A + "{r_hide}秒" + E + "（隐身、免伤、免控），再扑出造成" + phy("r_dmg", "r_ratio") +
               "+目标最大生命{r_hp}%" + O + "物理伤害" + E + "。目标被控住或有队友一起打时才放。",
        "names": ("女王之怒", "遁地", "虚空猛冲"),
    },
    "zh-hant": {
        "name": "雷珂煞",
        "attack": "爪咬。" + O + "憤怒沙蟲" + E + "：攻擊和技能命中累積怒氣（最多4層，" + A + "{fury_t}秒" + E + "內不打就消散）；滿怒時下一口變成" + O +
                  "狂食" + E + "，造成" + TRUE + G + "真實傷害" + E + "（" + A + "{e_cd}秒" + E + "一次）。鑽地時消耗怒氣回復生命。",
        "skill": "敵人在身邊：撲擊造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "，" + A + "{q_t}秒" + E + "內攻速+{q_as}%，之後2次攻擊濺射周圍（+{q_bonus}%攻擊力）。在遠處：鑽地打出" + O +
                 "尋找獵物" + E + "，直線衝擊波造成" + phy("q2_dmg", "q2_ratio") + O + "物理傷害" + E + "。",
        "skill2": "鑽入地下衝到目標腳下，" + O + "猛襲" + E + "：周圍敵人受到" + phy("w_dmg", "w_ratio") + O + "物理傷害" + E + "並" + R + "擊飛{w_up}秒" + E +
                  "。敵方英雄聚集而身邊沒有隊友時不會鑽過去。",
        "ult": "只對被她傷過的" + O + "獵物" + E + "：鑽進地底" + A + "{r_hide}秒" + E + "（隱身、免傷、免控），再撲出造成" + phy("r_dmg", "r_ratio") +
               "+目標最大生命{r_hp}%" + O + "物理傷害" + E + "。目標被控住或有隊友一起打時才施放。",
        "names": ("女王之怒", "深掘", "虛空疾行"),
    },
    "en": {
        "name": "Rek'Sai",
        "attack": "Claws and bites. " + O + "Fury of the Xer'Sai" + E + ": attacks and abilities that hit build Fury (4 at most, gone after " +
                  A + "{fury_t}s" + E + " out of combat); at full Fury her next bite is " + O + "Furious Bite" + E + ", " + TRUE + " " + G +
                  "true damage" + E + " (every " + A + "{e_cd}s" + E + "). Burrowing spends Fury to heal her.",
        "skill": "An enemy beside her: a pounce for " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + ", +{q_as}% attack speed for " +
                 A + "{q_t}s" + E + " and her next 2 attacks splash around (+{q_bonus}% AD). Farther: " + O + "Prey Seeker" + E +
                 ", a burst of earth in a line for " + phy("q2_dmg", "q2_ratio") + " " + O + "physical damage" + E + ".",
        "skill2": "Burrows and tunnels under the target, then " + O + "Un-burrow" + E + ": " + phy("w_dmg", "w_ratio") + " " + O +
                  "physical damage" + E + " around her, " + R + "knocking up {w_up}s" + E + ". She will not tunnel into a crowd of champions "
                  "with no ally near.",
        "ult": "Only at her " + O + "Prey" + E + " (champions she has hurt): she goes under for " + A + "{r_hide}s" + E +
               " (unseen, immune) and lunges for " + phy("r_dmg", "r_ratio") + " + {r_hp}% of its max health " + O + "physical damage" + E +
               ". Cast on a crowd-controlled target or with an ally on it.",
        "names": ("Queen's Wrath", "Burrow", "Void Rush"),
    },
    "ko": {
        "name": "렉사이",
        "attack": "할퀴고 문다. " + O + "제르사이의 분노" + E + ": 기본 공격과 스킬이 적중하면 분노 획득(최대 4, " + A + "{fury_t}초" + E +
                  " 비전투 시 소멸); 분노가 가득하면 다음 공격이 " + O + "성난 이빨" + E + "로 " + TRUE + "의 " + G + "고정 피해" + E + "(" + A +
                  "{e_cd}초" + E + "마다). 매복 시 분노를 소모해 체력 회복.",
        "skill": "적이 가까이: 덮쳐 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + ", " + A + "{q_t}초" + E + " 동안 공격 속도 +{q_as}%, 다음 2회 공격이 주변에 튐(+{q_bonus}% 공격력). 멀리: " +
                 O + "먹잇감 추적" + E + "으로 직선 충격파 " + phy("q2_dmg", "q2_ratio") + "의 " + O + "물리 피해" + E + ".",
        "skill2": "땅속으로 파고들어 대상 발밑으로 이동, " + O + "돌출" + E + ": 주변 적에게 " + phy("w_dmg", "w_ratio") + "의 " + O + "물리 피해" + E +
                  "와 " + R + "{w_up}초 에어본" + E + ". 아군 없이 적 챔피언 무리 속으로는 파고들지 않음.",
        "ult": "그녀가 피해를 입힌 " + O + "먹잇감" + E + "에게만: " + A + "{r_hide}초" + E + " 땅속(은신, 피해·군중 제어 면역) 후 덮쳐 " +
               phy("r_dmg", "r_ratio") + " + 대상 최대 체력 {r_hp}%의 " + O + "물리 피해" + E + ". 대상이 군중 제어 중이거나 아군이 함께 공격할 때 사용.",
        "names": ("여왕의 진노", "매복", "공허의 돌진"),
    },
    "ja": {
        "name": "レク＝サイ",
        "attack": "爪と牙で攻撃。" + O + "ゼル＝サイの怒り" + E + "：通常攻撃とスキルが当たると怒りが溜まる（最大4、" + A + "{fury_t}秒" + E +
                  "非戦闘で消える）。最大の時、次の攻撃は" + O + "激情の牙" + E + "で" + TRUE + "の" + G + "確定ダメージ" + E + "（" + A + "{e_cd}秒" + E +
                  "毎）。潜伏時に怒りを消費して回復。",
        "skill": "敵が近い時：飛びかかり" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "、" + A + "{q_t}秒" + E + "攻撃速度+{q_as}%、次の2回の攻撃が周囲に拡散（+{q_bonus}%攻撃力）。遠い時：" +
                 O + "獲物定め" + E + "で直線の衝撃波" + phy("q2_dmg", "q2_ratio") + "の" + O + "物理ダメージ" + E + "。",
        "skill2": "地中に潜り対象の足元へ、" + O + "襲撃" + E + "：周囲の敵に" + phy("w_dmg", "w_ratio") + "の" + O + "物理ダメージ" + E + "と" + R +
                  "{w_up}秒ノックアップ" + E + "。味方なしで敵チャンピオンの群れには潜り込まない。",
        "ult": "傷つけた" + O + "獲物" + E + "にのみ：" + A + "{r_hide}秒" + E + "地中へ（不可視・ダメージとCC無効）、飛び出して" + phy("r_dmg", "r_ratio") +
               "+対象の最大体力{r_hp}%の" + O + "物理ダメージ" + E + "。対象がCC中か味方と攻撃中に使う。",
        "names": ("女王の怒り", "潜伏", "ヴォイドラッシュ"),
    },
}

C = "league_reksai_sfx_"
V = "league_reksai_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_reksai_a_swing": [(C + "a_swing", 0.4, 0.0)],
    "league_reksai_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_reksai_p_full": [(C + "p_full", 0.45, 0.0)],
    "league_reksai_q": [(C + "q", 0.55, 0.0)],
    "league_reksai_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_reksai_q2": [(C + "q2", 0.55, 0.0)],
    "league_reksai_q2_hit": [(C + "q2_hit", 0.5, 0.0)],
    "league_reksai_e": [(C + "e", 0.5, 0.0)],
    "league_reksai_e_hit": [(C + "e_hit", 0.6, 0.0)],
    "league_reksai_w": [(C + "w", 0.55, 0.0)],
    "league_reksai_w_up": [(C + "w_up", 0.65, 0.0)],
    "league_reksai_w_hit": [(C + "w_hit", 0.4, 0.0)],
    "league_reksai_r": [(C + "r", 0.6, 0.0)],
    "league_reksai_r_leap": [(C + "r_leap", 0.6, 0.0)],
    "league_reksai_r_hit": [(C + "r_hit", 0.65, 0.0)],
    "league_reksai_vo_q": [(V + "q", 0.85, 0.0)],
    "league_reksai_vo_q2": [(V + "q2", 0.8, 0.0)],
    "league_reksai_vo_e": [(V + "e", 0.85, 0.0)],
    "league_reksai_vo_w": [(V + "w", 0.85, 0.0)],
    "league_reksai_vo_r": [(V + "r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("e_dmg", "e_ratio", "q_dmg", "q_ratio", "q_as", "q_bonus", "q2_dmg", "q2_ratio", "w_dmg",
                           "w_ratio", "r_dmg", "r_ratio", "r_hp")}
    for k in ("fury_t", "e_cd", "q_t", "w_up", "r_hide"):
        v[k] = secs(p[k])
    return v


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def load(path):
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def texts(p):
    v = values(p)
    out = {}
    for lang, t in TEXT.items():
        d = {"name": t["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = t[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), t["names"])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--face", help="X,Y from tfm2_ase.py face")
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 - the idle's top), when the top is at or above -28")
    a = ap.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    tx = texts(p)
    bad = False
    for lang, (d, _) in tx.items():
        lens = {k: shown_length(TEXT[lang][k]) for k in ("attack", "skill", "skill2", "ult")}
        bad |= any(n > TOOLTIP_MAX[lang] for n in lens.values())
        print(lang, " ".join(f"{k}:{n}/{TOOLTIP_MAX[lang]}" for k, n in lens.items()))
    if a.check:
        sys.stdout.reconfigure(encoding="utf-8")
        for lang, (d, _) in tx.items():
            for k in ("attack", "skill", "skill2", "ult"):
                print(lang, k, re.sub(r"<[^>]*>", "", d[k]))
        return
    if bad:
        sys.exit("a text is longer than TOOLTIP_MAX")

    i18n = load(os.path.join(MOD, "text", "champion.i18n"))
    for lang, (d, names) in tx.items():
        i18n[lang]["description"][ID] = d
        i18n[lang]["skill_name"][ID] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    for name, plays in SOUNDS.items():
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"))
    for k in [k for k in ov if ID + "_" in k]:      # her keys rebuilt (a renamed sound leaves none behind)
        del ov[k]
    for name in list(SOUNDS) + CLIPS:
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/league/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    view = json.loads(json.dumps(VIEW))
    if a.face:
        x, y = (int(v) for v in a.face.split(","))
        view["face"] = {"x": x, "y": y}
    if a.banpick is not None:
        if a.banpick > 0:
            sys.exit("never a positive banpick_center y (card-banpick rule)")
        view["banpick_center"] = {"x": 0, "y": a.banpick}
    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"))
    cv["entries"][ID] = view
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"))
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    if "Rek'Sai" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Rek'Sai. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
