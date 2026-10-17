"""Nasus's text (5 languages), sound_info files and his keys in the shared files, numbers from build_nasus.P.

    python tools/kit/setup_nasus.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_nasus in every language, description + skill_name),
sound/sfx/league_nasus_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Nasus named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 内瑟斯 / 沙漠死神: 吞噬灵魂, 汲魂痛击, 枯萎, 灵魂烈焰, 死神降临; zh_TW 納瑟斯: 食魂者, 虹吸打擊,
枯萎, 靈魂烈焰, 死神降臨; ja ナサス: ソウルイーター, サイフォンストライク, ウィザー, スピリットファイア, アヌビスの怒り; ko 나서스: 영혼의 포식자,
흡수의 일격, 쇠약, 영혼의 불길, 사막의 분노.
Slots: skill = Q Siphoning Strike, skill2 = E Spirit Fire, ult = R Fury of the Sands; the passive and Wither (W, cast on
its own) in the attack's text. No combo sentence in any text (the user's rule).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_nasus import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_nasus"
VERSION = "0.134.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
T = "<#ffffffff>"      # true damage
E = "<>"
# champion_view: the face on his glowing eye (set from tfm2_ase.py face after the sheet is written); the ear tips reach
# 44 game px over the soles, the headdress 37: banpick_center by the headdress (never positive: card-banpick rule)
VIEW = {"face": {"x": 7, "y": -36}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -2}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def hp_mag(d, r):
    return f"{M}{{{d}}}{E} + {HPi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "内瑟斯",
        "attack": "法杖重击。" + O + "吞噬灵魂" + E + "：生命偷取" + A + "{p_vamp}%" + E + "。" + O + "枯萎" + E + "：交战时每" + A + "{w_cd}秒" + E +
                  "自动衰老一名交战中的敌方英雄" + A + "{w_t}秒" + E + "：" + R + "减速{w_s0}%→{w_s1}%" + E + "，攻速降低{w_a0}%→{w_a1}%。",
        "skill": "法杖重击，造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "，外加与层数相同的" + M + "魔法伤害" + E + "。击杀单位+" + A +
                 "{q_s}层" + E + "，击杀英雄+" + A + "{q_sc}层" + E + "（死后清空）。",
        "skill2": "在目标处燃起灵魂之火：造成" + hp_mag("e_dmg", "e_hp") + M + "魔法伤害" + E + "，之后" + A + "{e_t}秒" + E + "内每秒" +
                  hp_mag("e_dot", "e_dot_hp") + "，火中敌人护甲" + R + "-{e_shred}%" + E + "。",
        "ult": "变身" + A + "{r_t}秒" + E + "：生命+{r_hp}，护甲魔抗+{r_def}，攻击距离增加，Q、E冷却减半；沙暴每" + A + "{r_p}秒" + E +
               "造成周围敌人" + T + "{r_pct}%最大生命真实伤害" + E + "。2名敌方英雄在身边或交战时才放。",
        "names": ("汲魂痛击", "灵魂烈焰", "死神降临"),
    },
    "zh-hant": {
        "name": "納瑟斯",
        "attack": "法杖重擊。" + O + "食魂者" + E + "：生命竊取" + A + "{p_vamp}%" + E + "。" + O + "枯萎" + E + "：交戰時每" + A + "{w_cd}秒" + E +
                  "自動衰老一名交戰中的敵方英雄" + A + "{w_t}秒" + E + "：" + R + "緩速{w_s0}%→{w_s1}%" + E + "，攻速降低{w_a0}%→{w_a1}%。",
        "skill": "法杖重擊，造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "，外加與層數相同的" + M + "魔法傷害" + E + "。擊殺單位+" + A +
                 "{q_s}層" + E + "，擊殺英雄+" + A + "{q_sc}層" + E + "（死後清空）。",
        "skill2": "在目標處燃起靈魂之火：造成" + hp_mag("e_dmg", "e_hp") + M + "魔法傷害" + E + "，之後" + A + "{e_t}秒" + E + "內每秒" +
                  hp_mag("e_dot", "e_dot_hp") + "，火中敵人護甲" + R + "-{e_shred}%" + E + "。",
        "ult": "變身" + A + "{r_t}秒" + E + "：生命+{r_hp}，護甲魔抗+{r_def}，攻擊距離增加，Q、E冷卻減半；沙暴每" + A + "{r_p}秒" + E +
               "造成周圍敵人" + T + "{r_pct}%最大生命真實傷害" + E + "。2名敵方英雄在身邊或交戰時才施放。",
        "names": ("虹吸打擊", "靈魂烈焰", "死神降臨"),
    },
    "en": {
        "name": "Nasus",
        "attack": "A staff blow. " + O + "Soul Eater" + E + ": " + A + "{p_vamp}%" + E + " life steal. " + O + "Wither" + E + ": in a fight, every " +
                  A + "{w_cd}s" + E + " he ages an enemy champion in the fight for " + A + "{w_t}s" + E + ": a " + R +
                  "slow growing {w_s0}% -> {w_s1}%" + E + " and attack speed -{w_a0}% -> -{w_a1}%.",
        "skill": "A staff blow for " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + " plus " + M + "magic damage" + E +
                 " equal to his stacks. A unit it kills gives " + A + "{q_s} stacks" + E + ", a champion " + A + "{q_sc}" + E +
                 " (lost on death).",
        "skill2": "Spirit fire at the target spot: " + hp_mag("e_dmg", "e_hp") + " " + M + "magic damage" + E + ", then " +
                  hp_mag("e_dot", "e_dot_hp") + " a second for " + A + "{e_t}s" + E + "; enemies in it lose " + R + "{e_shred}% armour" + E + ".",
        "ult": "He grows for " + A + "{r_t}s" + E + ": +{r_hp} health, +{r_def} armour and magic resistance, more attack range, Q and E "
               "cooldowns halved; the sandstorm deals " + T + "{r_pct}% of each nearby enemy's max health as true damage" + E +
               " every " + A + "{r_p}s" + E + ". Cast with 2 enemy champions close, or in a fight.",
        "names": ("Siphoning Strike", "Spirit Fire", "Fury of the Sands"),
    },
    "ko": {
        "name": "나서스",
        "attack": "지팡이 일격. " + O + "영혼의 포식자" + E + ": 생명력 흡수 " + A + "{p_vamp}%" + E + ". " + O + "쇠약" + E + ": 전투 중 " + A +
                  "{w_cd}초" + E + "마다 싸우는 적 챔피언을 " + A + "{w_t}초" + E + "간 늙게 함: " + R + "둔화 {w_s0}%→{w_s1}%" + E +
                  ", 공격 속도 -{w_a0}%→-{w_a1}%.",
        "skill": "지팡이 일격으로 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + "와 중첩만큼의 " + M + "마법 피해" + E +
                 ". 처치한 유닛마다 " + A + "{q_s}중첩" + E + ", 챔피언 " + A + "{q_sc}중첩" + E + "(사망 시 초기화).",
        "skill2": "목표 지점에 영혼의 불: " + hp_mag("e_dmg", "e_hp") + "의 " + M + "마법 피해" + E + ", 이후 " + A + "{e_t}초" + E +
                  "간 매초 " + hp_mag("e_dot", "e_dot_hp") + ", 불 속의 적 방어력 " + R + "-{e_shred}%" + E + ".",
        "ult": A + "{r_t}초" + E + "간 거대화: 체력 +{r_hp}, 방어력·마법 저항력 +{r_def}, 사거리 증가, Q·E 재사용 대기시간 절반; 모래폭풍이 " +
               A + "{r_p}초" + E + "마다 주변 적에게 최대 체력의 " + T + "{r_pct}% 고정 피해" + E + ". 적 챔피언 2명이 가까이 있거나 전투 중에 사용.",
        "names": ("흡수의 일격", "영혼의 불길", "사막의 분노"),
    },
    "ja": {
        "name": "ナサス",
        "attack": "杖の一撃。" + O + "ソウルイーター" + E + "：ライフスティール" + A + "{p_vamp}%" + E + "。" + O + "ウィザー" + E + "：戦闘中" + A +
                  "{w_cd}秒" + E + "毎に戦う敵チャンピオンを" + A + "{w_t}秒" + E + "老化：" + R + "スロウ{w_s0}%→{w_s1}%" + E +
                  "、攻撃速度-{w_a0}%→-{w_a1}%。",
        "skill": "杖の一撃で" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "とスタック分の" + M + "魔法ダメージ" + E +
                 "。倒したユニット毎に" + A + "{q_s}スタック" + E + "、チャンピオンは" + A + "{q_sc}" + E + "（死亡で消える）。",
        "skill2": "目標地点に霊魂の炎：" + hp_mag("e_dmg", "e_hp") + "の" + M + "魔法ダメージ" + E + "、その後" + A + "{e_t}秒" + E + "間毎秒" +
                  hp_mag("e_dot", "e_dot_hp") + "、炎の中の敵は物理防御" + R + "-{e_shred}%" + E + "。",
        "ult": A + "{r_t}秒" + E + "巨大化：体力+{r_hp}、物理防御・魔法防御+{r_def}、射程増加、Q・Eのクールダウン半減。砂嵐が" + A +
               "{r_p}秒" + E + "毎に周囲の敵へ最大体力の" + T + "{r_pct}%確定ダメージ" + E + "。敵2体が近いか戦闘中に使う。",
        "names": ("サイフォンストライク", "スピリットファイア", "アヌビスの怒り"),
    },
}

C = "league_nasus_sfx_"
V = "league_nasus_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_nasus_a_swing": [(C + "a_swing", 0.35, 0.0)],
    "league_nasus_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_nasus_q": [(C + "q", 0.45, 0.0)],
    "league_nasus_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_nasus_q_soul": [(C + "q_soul", 0.45, 0.0)],
    "league_nasus_w": [(C + "w", 0.5, 0.0)],
    "league_nasus_w_hit": [(C + "w_hit", 0.4, 0.0)],
    "league_nasus_e": [(C + "e", 0.45, 0.0)],
    "league_nasus_e_hit": [(C + "e_hit", 0.5, 0.0)],
    "league_nasus_e_fire": [(C + "e_fire", 0.4, 0.0)],
    "league_nasus_r": [(C + "r", 0.6, 0.0)],
    "league_nasus_r_storm": [(C + "r_storm", 0.55, 0.0)],
    "league_nasus_vo_q": [(V + "q", 0.85, 0.0)],
    "league_nasus_vo_w": [(V + "w", 0.85, 0.0)],
    "league_nasus_vo_e": [(V + "e", 0.85, 0.0)],
    "league_nasus_vo_r": [(V + "r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_vamp", "q_dmg", "q_ratio", "q_s", "q_sc", "e_dmg", "e_hp", "e_dot", "e_dot_hp", "e_shred",
                           "r_hp", "r_def", "r_pct", "w_s0", "w_a0")}
    v["w_s1"] = p["w_s0"] + 4 * p["w_ds"]
    v["w_a1"] = p["w_a0"] + 4 * p["w_da"]
    for k in ("w_cd", "w_t", "e_t", "r_t", "r_p"):
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
    for k in [k for k in ov if ID + "_" in k]:      # his keys rebuilt (a renamed sound leaves none behind)
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
    if "Nasus" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Nasus. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
