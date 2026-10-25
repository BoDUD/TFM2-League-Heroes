"""Trundle's text (5 languages), sound_info files and their keys in the shared files, numbers from build_trundle.P
(setup_yorick.py's way).

    python tools/kit/setup_trundle.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_trundle in every language, description + skill_name),
sound/sfx/league_trundle_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Trundle named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 特朗德尔 (巨魔之王): 国王的贡品; 利齿撕咬, 冰封领域, 寒冰之柱, 强权至上; zh_TW 特朗德:
帝王獻祭; 狂野撕咬, 極凍領地, 狡詰冰柱, 盛怒霸體; ja トランドル: 王への貢物; 咬み付き, 凍てつく大地, 氷冷の柱, 暴虐なる搾取; ko
트런들: 헌납; 깨물기, 얼음 왕국, 얼음 기둥, 진압.
Slots: skill = Chomp, skill2 = Pillar of Ice, ult = Subjugate; King's Tribute and Frozen Domain in the attack's text.
The texts say the main pack's rules (the add-on's copy has its own: addons/league_trundle/make_override.py). No combo
sentence in any text (the user's rule: the combos are the README's) - the domain's trigger (a bite on a champion) is
how W is cast at all, so it is said.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_trundle import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_trundle"
VERSION = "0.222.0"     # above main 0.221.0 (#526 Rumble, Ambessa), no open PR, 2026-10-25
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card
# (bp_card_audit.py with hd.rs UI_SIZES)
VIEW = {"face": {"x": 5, "y": -27}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -12}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


TEXT = {
    "zh-hans": {
        "name": "特朗德尔",
        "attack": "抡冰棒。" + n("国王的贡品") + "：打死单位回复{p_heal} + " + ADi + "{p_heal_r}%生命，冰面上双倍。" +
                  n("冰封领域") + "：利齿撕咬咬中英雄时冻住地面" + t("{w_t}秒") + "（每" + t("{w_cd}秒") + "一次），其间攻速+{w_as}%、"
                  "移速+{w_ms}%。",
        "skill": "咬一口造成" + phys("q_dmg", "q_ratio") + "物理伤害并" + cc("减速") + "{q_slow}%；" + t("{q_t}秒") +
                 "内对方攻击力-{q_sap}%，自己+{q_gain}%。",
        "skill2": "在敌方英雄处立起寒冰之柱" + t("{e_t}秒") + "，周围敌人" + cc("减速") + "{e_slow}%。",
        "ult": "吸取敌方英雄：立刻造成最大生命{r_pct0}%真实伤害，" + t("{r_t}秒") + "内" + t("每秒") + "再{r_pct}%，每次回复{r_heal} + " +
               ADi + "{r_heal_r}%生命；偷走{r_arm}%护甲和魔抗" + t("{r_hold}秒") + "。",
        "names": ("利齿撕咬", "寒冰之柱", "强权至上"),
    },
    "zh-hant": {
        "name": "特朗德",
        "attack": "揮冰棒。" + n("帝王獻祭") + "：打死單位回復{p_heal} + " + ADi + "{p_heal_r}%生命，冰面上雙倍。" +
                  n("極凍領地") + "：狂野撕咬咬中英雄時凍住地面" + t("{w_t}秒") + "（每" + t("{w_cd}秒") + "一次），其間攻速+{w_as}%、"
                  "移速+{w_ms}%。",
        "skill": "咬一口造成" + phys("q_dmg", "q_ratio") + "物理傷害並" + cc("緩速") + "{q_slow}%；" + t("{q_t}秒") +
                 "內對方攻擊力-{q_sap}%，自己+{q_gain}%。",
        "skill2": "在敵方英雄處立起狡詰冰柱" + t("{e_t}秒") + "，周圍敵人" + cc("緩速") + "{e_slow}%。",
        "ult": "吸取敵方英雄：立刻造成最大生命{r_pct0}%真實傷害，" + t("{r_t}秒") + "內" + t("每秒") + "再{r_pct}%，每次回復{r_heal} + " +
               ADi + "{r_heal_r}%生命；偷走{r_arm}%護甲和魔抗" + t("{r_hold}秒") + "。",
        "names": ("狂野撕咬", "狡詰冰柱", "盛怒霸體"),
    },
    "en": {
        "name": "Trundle",
        "attack": "Ice club blows. " + n("King's Tribute") + ": a unit he kills heals him {p_heal} + " + ADi + "{p_heal_r}%, "
                  "doubled on his domain. " + n("Frozen Domain") + ": Chomp biting a champion freezes the ground for " +
                  t("{w_t}s") + " (once every " + t("{w_cd}s") + "): +{w_as}% attack speed and +{w_ms}% move speed meanwhile.",
        "skill": "Bites for " + phys("q_dmg", "q_ratio") + " physical damage and " + cc("slows") + " {q_slow}%; for " +
                 t("{q_t}s") + " the target has {q_sap}% less attack, Trundle {q_gain}% more.",
        "skill2": "Raises a Pillar of Ice at an enemy champion for " + t("{e_t}s") + "; enemies around it are " + cc("slowed") +
                  " {e_slow}%.",
        "ult": "Drains an enemy champion: {r_pct0}% max health as true damage at once, {r_pct}% more " + t("every second") +
               " for " + t("{r_t}s") + ", each healing him {r_heal} + " + ADi + "{r_heal_r}%; steals {r_arm}% of its armour "
               "and magic resistance for " + t("{r_hold}s") + ".",
        "names": ("Chomp", "Pillar of Ice", "Subjugate"),
    },
    "ko": {
        "name": "트런들",
        "attack": "얼음 몽둥이 공격. " + n("헌납") + ": 처치한 유닛마다 체력 {p_heal} + " + ADi + "{p_heal_r}% 회복, 얼음 위에서는 2배. " +
                  n("얼음 왕국") + ": 깨물기가 챔피언을 물면 " + t("{w_t}초") + " 동안 땅을 얼림(" + t("{w_cd}초") + "마다 한 번), "
                  "그동안 공격 속도 +{w_as}%, 이동 속도 +{w_ms}%.",
        "skill": "깨물어 " + phys("q_dmg", "q_ratio") + " 물리 피해, {q_slow}% " + cc("둔화") + "; " + t("{q_t}초") +
                 " 동안 대상 공격력 -{q_sap}%, 트런들 +{q_gain}%.",
        "skill2": "적 챔피언 위치에 얼음 기둥을 " + t("{e_t}초") + " 세움, 주변 적 {e_slow}% " + cc("둔화") + ".",
        "ult": "적 챔피언을 흡수: 즉시 최대 체력 {r_pct0}% 고정 피해, " + t("{r_t}초") + " 동안 " + t("매초") + " {r_pct}% 추가, "
               "매번 체력 {r_heal} + " + ADi + "{r_heal_r}% 회복; 방어력과 마법 저항력 {r_arm}%를 " + t("{r_hold}초") + " 동안 빼앗음.",
        "names": ("깨물기", "얼음 기둥", "진압"),
    },
    "ja": {
        "name": "トランドル",
        "attack": "氷の棍棒で攻撃。" + n("王への貢物") + "：倒したユニットごとに体力{p_heal} + " + ADi + "{p_heal_r}%回復、氷の上では2倍。" +
                  n("凍てつく大地") + "：咬み付きがチャンピオンに当たると地面を" + t("{w_t}秒") + "凍らせる（" + t("{w_cd}秒") +
                  "に1回）、その間攻撃速度+{w_as}%、移動速度+{w_ms}%。",
        "skill": "咬み付いて" + phys("q_dmg", "q_ratio") + "の物理ダメージ、{q_slow}%" + cc("スロウ") + "；" + t("{q_t}秒") +
                 "間 相手の攻撃力-{q_sap}%、自身+{q_gain}%。",
        "skill2": "敵チャンピオンの位置に氷冷の柱を" + t("{e_t}秒") + "立てる、周囲の敵に{e_slow}%" + cc("スロウ") + "。",
        "ult": "敵チャンピオンから搾取：即座に最大体力{r_pct0}%の確定ダメージ、" + t("{r_t}秒") + "間" + t("毎秒") + "{r_pct}%、"
               "毎回体力{r_heal} + " + ADi + "{r_heal_r}%回復；物理防御と魔法防御の{r_arm}%を" + t("{r_hold}秒") + "奪う。",
        "names": ("咬み付き", "氷冷の柱", "暴虐なる搾取"),
    },
}

C = "league_trundle_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the impacts loud, the voice as the other heroes'
SOUNDS = {f"league_trundle_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.55), ("q", 0.6), ("q_hit", 0.7), ("w", 0.75), ("e", 0.6), ("e_rise", 0.8), ("e_hit", 0.5),
    ("r", 0.8), ("r_hit", 0.75), ("p_heal", 0.5), ("vo_q", 0.85), ("vo_w", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_heal", "p_heal_r", "w_as", "w_ms", "q_dmg", "q_ratio", "q_slow", "q_sap", "q_gain", "e_slow",
                           "r_pct0", "r_pct", "r_heal", "r_heal_r", "r_arm")}
    assert p["r_p"] == 60, "the ult texts say it drains every second"
    for k in ("w_t", "w_cd", "q_t", "e_t", "r_t"):
        v[k] = secs(p[k])
    v["r_hold"] = secs(p["r_t"] + p["r_keep"])
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
    for lang, tx in TEXT.items():
        d = {"name": tx["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = tx[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), tx["names"])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--face", help="X,Y from tfm2_ase.py face")
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 + the idle's top over the frame centre)")
    a = ap.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    tx = texts(p)
    bad = False
    for lang, (d, _) in tx.items():
        lens = {k: shown_length(TEXT[lang][k]) for k in ("attack", "skill", "skill2", "ult")}
        bad |= any(m > TOOLTIP_MAX[lang] for m in lens.values())
        print(lang, " ".join(f"{k}:{m}/{TOOLTIP_MAX[lang]}" for k, m in lens.items()))
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
    if "Trundle" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Trundle. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
