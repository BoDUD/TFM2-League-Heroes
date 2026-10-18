"""Katarina's text (5 languages), sound_info files and her keys in the shared files, numbers from build_katarina.P.

    python tools/kit/setup_katarina.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_katarina in every language, description + skill_name),
sound/sfx/league_katarina_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.115.0, Katarina named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (卡特琳娜 / 不祥之刃 - the client swaps name and title; 贪婪, 弹射之刃, 伺机待发,
瞬步, 死亡莲华) and Data Dragon 16.20.1 (zh_TW 卡特蓮娜 / 貪婪 / 彈射利刃 / 備戰 / 瞬步 / 死亡蓮花, ja カタリナ /
貪欲なる暗殺者 / バウンドナイフ / プリペレーション / 瞬歩 / デスロータス, ko 카타리나 / 탐욕 / 단검 투척 / 준비 / 순보 / 죽음의 연꽃).
Slots: skill = Q (+ Shunpo onto the dagger), skill2 = W (+ Shunpo in first), ult = R; Voracity and the daggers are
told in the attack's text. No combo sentence in any text (the user's rule). No `league_katarina_attack` sound: the
engine would play it at the start of every attack; the stab plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_katarina import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_katarina"
VERSION = "0.115.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # physical damage, AD, names
M = "<#a974ffff>"      # magic damage / AP
A = "<#ffb900ff>"      # durations, counts
C = "<#ef5350ff>"      # crowd control
W = "<#ffffffff>"      # move speed
S = "<#ceff99ff>"      # attack speed
R = "<#ffdd8eff>"      # armour / magic resistance
T = "<#f5f5f5ff>"      # true damage
E = "<>"
# champion_view: a placeholder face until the sprite (tfm2_ase.py face), the centre from the idle
# 2026-10-18 ban/pick card audit (frame centre, HD from lo_idle / 1.5; user: 「还有哪些英雄BP位置不对的一起改了」): none -> -11: the head reached the card's top edge (Talon's rule: at or above -28)
# 2026-10-18: face (1,-36) - (0,-37) framed four rows of hair and cut the chin; kept equal to champion_view and ppu_restyle.py
VIEW = {"face": {"x": 1, "y": -36}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -11}}


def phys(k):
    return f"{O}{{{k}_dmg}}{E}+{ADi}{O}{{{k}_ad}}%{E}"


def mag(k):
    return f"{M}{{{k}_dmg}}{E}+{APi}{M}{{{k}_ap}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "卡特琳娜",
        "attack": O + "贪婪" + E + "：被她伤害过的敌方英雄" + A + "{p_win}秒" + E + "内阵亡时，Q、W冷却刷新，瞬步就绪。落地的匕首留" + A + "{d_life}秒" + E +
                  "，捡起时旋斩周围敌人，造成" + mag("p") + M + "魔法伤害" + E + "，瞬步冷却降为" + A + "{e_short}秒" + E + "。",
        "skill": "掷出弹射之刃，造成" + mag("q") + M + "魔法伤害" + E + "，再弹向附近" + A + "{q_bn}" + E + "个敌人；匕首落在第一个目标身后。" + O + "瞬步" + E +
                 "就绪且匕首旁有敌方英雄时，瞬步到匕首处。",
        "skill2": O + "瞬步" + E + "就绪时先瞬步到敌方英雄身边，造成" + mag("e") + M + "魔法伤害" + E + "（冷却" + A + "{e_cd}秒" + E + "）；再把匕首抛向空中，" + A +
                  "{w_fall}秒" + E + "后落地，获得逐渐衰减的" + W + "移速+{w_ms}%" + E + "。",
        "ult": "原地旋转引导" + A + "{r_t}秒" + E + "，向周围的敌方英雄连续掷出匕首，共造成" + mag("r") + M + "魔法伤害" + E + "并使其" + C + "治疗效果-{r_gw}%" + E +
               "。受到控制时中断。",
        "names": ("弹射之刃", "伺机待发", "死亡莲华"),
    },
    "zh-hant": {
        "name": "卡特蓮娜",
        "attack": O + "貪婪" + E + "：被她傷害過的敵方英雄" + A + "{p_win}秒" + E + "內陣亡時，Q、W冷卻刷新，瞬步就緒。落地的匕首留" + A + "{d_life}秒" + E +
                  "，撿起時旋斬周圍敵人，造成" + mag("p") + M + "魔法傷害" + E + "，瞬步冷卻降為" + A + "{e_short}秒" + E + "。",
        "skill": "擲出彈射利刃，造成" + mag("q") + M + "魔法傷害" + E + "，再彈向附近" + A + "{q_bn}" + E + "個敵人；匕首落在第一個目標身後。" + O + "瞬步" + E +
                 "就緒且匕首旁有敵方英雄時，瞬步到匕首處。",
        "skill2": O + "瞬步" + E + "就緒時先瞬步到敵方英雄身邊，造成" + mag("e") + M + "魔法傷害" + E + "（冷卻" + A + "{e_cd}秒" + E + "）；再把匕首拋向空中，" + A +
                  "{w_fall}秒" + E + "後落地，獲得逐漸衰減的" + W + "跑速+{w_ms}%" + E + "。",
        "ult": "原地旋轉引導" + A + "{r_t}秒" + E + "，向周圍的敵方英雄連續擲出匕首，共造成" + mag("r") + M + "魔法傷害" + E + "並使其" + C + "治療效果-{r_gw}%" + E +
               "。受到控制時中斷。",
        "names": ("彈射利刃", "備戰", "死亡蓮花"),
    },
    "en": {
        "name": "Katarina",
        "attack": O + "Voracity" + E + ": when an enemy champion she damaged dies within " + A + "{p_win}s" + E + ", Q and W refresh and Shunpo is ready. "
                  "Daggers on the ground last " + A + "{d_life}s" + E + "; picking one up slashes nearby enemies for " + mag("p") + " " + M + "magic damage" + E +
                  " and cuts Shunpo's cooldown to " + A + "{e_short}s" + E + ".",
        "skill": "Throws a bouncing blade for " + mag("q") + " " + M + "magic damage" + E + " that bounces to " + A + "{q_bn}" + E + " nearby enemies; the dagger "
                 "lands behind the first target. If " + O + "Shunpo" + E + " is ready and an enemy champion is near the dagger, she blinks to it.",
        "skill2": "If " + O + "Shunpo" + E + " is ready she first blinks to an enemy champion for " + mag("e") + " " + M + "magic damage" + E + " (cooldown " + A +
                  "{e_cd}s" + E + "); then tosses a dagger into the air that lands after " + A + "{w_fall}s" + E + ", gaining " + W + "{w_ms}% move speed" + E +
                  " that decays.",
        "ult": "Channels for " + A + "{r_t}s" + E + ", throwing daggers at nearby enemy champions for " + mag("r") + " " + M + "magic damage" + E + " in total and " + C +
               "{r_gw}% reduced healing" + E + ". Crowd control interrupts it.",
        "names": ("Bouncing Blade", "Preparation", "Death Lotus"),
    },
    "ko": {
        "name": "카타리나",
        "attack": O + "탐욕" + E + ": 그녀가 피해를 입힌 적 챔피언이 " + A + "{p_win}초" + E + " 안에 죽으면 Q, W 재사용 대기시간 초기화, 순보 준비. 바닥의 단검은 " + A +
                  "{d_life}초" + E + " 유지, 주우면 주변 적에게 " + mag("p") + " " + M + "마법 피해" + E + ", 순보 대기시간 " + A + "{e_short}초" + E + "로 감소.",
        "skill": "튕기는 단검을 던져 " + mag("q") + " " + M + "마법 피해" + E + ", 주변 적 " + A + "{q_bn}" + E + "명에게 튕김; 단검은 첫 대상 뒤에 떨어짐. " + O + "순보" + E +
                 "가 준비되고 단검 근처에 적 챔피언이 있으면 단검으로 순보.",
        "skill2": O + "순보" + E + "가 준비되면 먼저 적 챔피언에게 순보해 " + mag("e") + " " + M + "마법 피해" + E + "(대기시간 " + A + "{e_cd}초" + E + "); 이후 단검을 공중에 "
                  "던져 " + A + "{w_fall}초" + E + " 뒤 떨어지며 점차 감소하는 " + W + "이동 속도 +{w_ms}%" + E + ".",
        "ult": A + "{r_t}초" + E + " 동안 정신을 집중해 주변 적 챔피언에게 단검을 던져 총 " + mag("r") + " " + M + "마법 피해" + E + "와 " + C + "치유 감소 {r_gw}%" + E +
               ". 군중 제어 시 중단.",
        "names": ("단검 투척", "준비", "죽음의 연꽃"),
    },
    "ja": {
        "name": "カタリナ",
        "attack": O + "貪欲なる暗殺者" + E + "：彼女がダメージを与えた敵チャンピオンが" + A + "{p_win}秒" + E + "以内に倒れるとQ・WのCD解消、瞬歩使用可能。落ちた短剣は" + A +
                  "{d_life}秒" + E + "残り、拾うと周囲の敵に" + mag("p") + "の" + M + "魔法ダメージ" + E + "、瞬歩のCDが" + A + "{e_short}秒" + E + "に。",
        "skill": "跳ね返るナイフを投げ" + mag("q") + "の" + M + "魔法ダメージ" + E + "、近くの敵" + A + "{q_bn}" + E + "体に跳ね返る。短剣は最初の対象の後ろに落ちる。" + O +
                 "瞬歩" + E + "が使用可能で短剣の近くに敵チャンピオンがいれば短剣へ瞬歩。",
        "skill2": O + "瞬歩" + E + "が使用可能なら先に敵チャンピオンへ瞬歩し" + mag("e") + "の" + M + "魔法ダメージ" + E + "（CD" + A + "{e_cd}秒" + E + "）。短剣を宙に投げ" +
                  A + "{w_fall}秒" + E + "後に落下、減衰する" + W + "移動速度+{w_ms}%" + E + "。",
        "ult": A + "{r_t}秒" + E + "間詠唱し、周囲の敵チャンピオンに短剣を投げ続け合計" + mag("r") + "の" + M + "魔法ダメージ" + E + "と" + C + "回復量-{r_gw}%" + E +
               "。行動妨害で中断。",
        "names": ("バウンドナイフ", "プリペレーション", "デスロータス"),
    },
}

S_ = "league_katarina_"
CL = "league_katarina_sfx_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(CL + k, vol, 0.0)] for k, vol in [
    ("a_swing", 0.4), ("a_hit", 0.45), ("q_cast", 0.45), ("q_blade", 0.45), ("q_hit", 0.4), ("q_arc", 0.4),
    ("q_land", 0.45), ("w_toss", 0.5), ("e_blink", 0.5), ("pick", 0.55), ("reset", 0.55), ("r_lotus", 0.6),
    ("vo_q", 0.8), ("vo_w", 0.8), ("vo_e", 0.8), ("vo_r", 0.85)]}
SOUNDS[S_ + "e_hit"] = [(CL + "a_hit", 0.45, 0.0)]       # Shunpo's strike: the stab's hit
SOUNDS[S_ + "r_hit"] = [(CL + "q_hit", 0.22, 0.0)]       # every Death Lotus dagger (15 a target): quiet
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("q_dmg", "q_ap", "q_bn", "p_dmg", "p_ap", "e_dmg", "e_ap", "w_ms", "r_dmg", "r_ap", "r_gw")}
    v.update({k: secs(p[k]) for k in ("p_win", "d_life", "e_short", "e_cd", "w_fall", "r_t")})
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
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 - the idle's top), when the top is above -28")
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
    for k in [k for k in ov if ID in k]:      # his keys rebuilt (a renamed sound leaves none behind)
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
    if "Katarina" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Katarina. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
