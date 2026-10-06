"""Gwen's text (5 languages), sound_info files and her keys in the shared files, numbers from build_gwen.P.

    python tools/kit/setup_gwen.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_gwen in every language, description + skill_name),
sound/sfx/league_gwen_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.68.0, Gwen named). Only her keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (格温 / 灵罗娃娃, 千穿百孔, 快刀剪乱, 丝缕缠流 - its mist 圣霭 -, 断续疾走, 引针簇射) and
Data Dragon 16.19.1 (zh_TW 關 / 聖啟織偶, 千刀萬剮, 剪剪！, 聖霧絲縷, 剪步如飛, 飛針走線; ko 그웬 / 신성한 재봉사, 가위 난도질,
싹둑싹둑!, 신성한 안개, 돌격가위, 바느질; ja グウェン / 聖なるお針子, 裁断, チョキチョキッ！, 聖なる霧, スキップスラッシュ, 針仕事).
skill2 is named after E, which leads the combo (W in the text).
No `league_gwen_attack` sound: the engine would play it at the start of every attack; the snip's sound plays from the
tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_gwen import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_gwen"
VERSION = "0.68.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts, invisibility
R = "<#ef5350ff>"      # crowd control
W = "<#f5f5f5ff>"      # true damage
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 1, "y": -38}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def needles():
    return f"{M}{{r_dmg1}}/{{r_dmg2}}/{{r_dmg3}}{E} + {APi}{M}{{r_ratio}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "格温",
        "attack": "被动" + O + "千穿百孔" + E + "：攻击和技能命中附加" + mag("p_dmg", "p_ratio") + M + "魔法伤害" + E + "，对英雄再造成" + W +
                  "{p_hp}%最大生命值真实伤害" + E + "并回复" + mag("p_heal", "p_heal_r") + "生命。每次攻击叠一层剪刀层数，最多{q_n}层。",
        "skill": "在身前剪" + A + "1+层数" + E + "下，每下" + mag("q_mini", "q_mini_r") + "，最后一剪" + mag("q_dmg", "q_ratio") + M +
                 "魔法伤害" + E + "，正中央的敌人额外受到" + W + "{q_true}真实伤害" + E + "。每下都带被动。",
        "skill2": O + "断续疾走" + E + "：冲向敌方英雄，{e_t}秒内攻速+{e_as}%、攻击距离增加、攻击附加" + mag("e_dmg", "e_ratio") + "。落地放出" +
                  O + "丝缕缠流" + E + "：圣霭{w_t}秒，她在雾中时" + A + "隐身" + E + "（远处敌人选不中她），护甲和魔抗+{w_def}。",
        "ult": "朝敌方英雄连掷三轮针：1根、3根、5根，各造成" + needles() + M + "魔法伤害" + E + "并" + R + "减速{r_slow}%" + E +
               "{r_slow_t}秒，带被动。",
        "names": ("快刀剪乱", "断续疾走", "引针簇射"),
    },
    "zh-hant": {
        "name": "關",
        "attack": "被動" + O + "千刀萬剮" + E + "：攻擊和技能命中附加" + mag("p_dmg", "p_ratio") + M + "魔法傷害" + E + "，對英雄再造成" + W +
                  "{p_hp}%最大生命值真實傷害" + E + "並回復" + mag("p_heal", "p_heal_r") + "生命。每次攻擊疊一層剪刀層數，最多{q_n}層。",
        "skill": "在身前剪" + A + "1+層數" + E + "下，每下" + mag("q_mini", "q_mini_r") + "，最後一剪" + mag("q_dmg", "q_ratio") + M +
                 "魔法傷害" + E + "，正中央的敵人額外受到" + W + "{q_true}真實傷害" + E + "。每下都帶被動。",
        "skill2": O + "剪步如飛" + E + "：衝向敵方英雄，{e_t}秒內攻速+{e_as}%、攻擊距離增加、攻擊附加" + mag("e_dmg", "e_ratio") + "。落地放出" +
                  O + "聖霧絲縷" + E + "：聖霧{w_t}秒，她在霧中時" + A + "隱形" + E + "（遠處敵人選不中她），護甲和魔抗+{w_def}。",
        "ult": "朝敵方英雄連擲三輪針：1根、3根、5根，各造成" + needles() + M + "魔法傷害" + E + "並" + R + "緩速{r_slow}%" + E +
               "{r_slow_t}秒，帶被動。",
        "names": ("剪剪！", "剪步如飛", "飛針走線"),
    },
    "en": {
        "name": "Gwen",
        "attack": "Passive " + O + "A Thousand Cuts" + E + ": her attacks and skill hits deal " + mag("p_dmg", "p_ratio") + " bonus " + M +
                  "magic damage" + E + "; to champions also " + W + "{p_hp}% max health true damage" + E + ", healing her " +
                  mag("p_heal", "p_heal_r") + ". Each attack adds a snip stack (up to {q_n}).",
        "skill": "Snips in front of her " + A + "1 + stacks" + E + " times for " + mag("q_mini", "q_mini_r") + " each, then a final snip for " +
                 mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + "; enemies in the centre take " + W + "{q_true} true damage" + E +
                 " more. Every snip applies the passive.",
        "skill2": O + "Skip 'n Slash" + E + ": dashes at an enemy champion; for {e_t}s her attacks gain {e_as}% attack speed, range and " +
                  mag("e_dmg", "e_ratio") + " on hit. Where she lands " + O + "Hallowed Mist" + E + " settles for {w_t}s: inside it she is " +
                  A + "invisible" + E + " (enemies far away cannot target her) with +{w_def} armour and magic resist.",
        "ult": "Hurls three volleys of needles at an enemy champion - 1, 3 and 5 needles - each dealing " + needles() + " " + M +
               "magic damage" + E + ", " + R + "slowing {r_slow}%" + E + " for {r_slow_t}s and applying the passive.",
        "names": ("Snip Snip!", "Skip 'n Slash", "Needlework"),
    },
    "ko": {
        "name": "그웬",
        "attack": "기본 지속 효과 " + O + "가위 난도질" + E + ": 공격과 스킬 적중 시 " + mag("p_dmg", "p_ratio") + "의 추가 " + M + "마법 피해" + E +
                  ", 챔피언에게는 " + W + "최대 체력의 {p_hp}% 고정 피해" + E + "를 더 주고 " + mag("p_heal", "p_heal_r") +
                  " 회복. 공격마다 가위 중첩 1, 최대 {q_n}.",
        "skill": "앞을 " + A + "1+중첩" + E + "번 자르며 각각 " + mag("q_mini", "q_mini_r") + ", 마지막 가위질은 " + mag("q_dmg", "q_ratio") +
                 "의 " + M + "마법 피해" + E + ", 중앙의 적은 " + W + "{q_true} 고정 피해" + E + " 추가. 매번 기본 지속 효과 적용.",
        "skill2": O + "돌격가위" + E + ": 적 챔피언에게 돌진, {e_t}초간 공격 속도 +{e_as}%, 사거리 증가, 적중 시 " + mag("e_dmg", "e_ratio") +
                  ". 착지한 곳에 " + O + "신성한 안개" + E + " {w_t}초: 안개 안에서 " + A + "투명" + E +
                  "(멀리 있는 적은 대상 지정 불가), 방어력과 마법 저항력 +{w_def}.",
        "ult": "적 챔피언에게 바늘을 세 번 던짐(1, 3, 5개): 각각 " + needles() + "의 " + M + "마법 피해" + E + ", " + R +
               "{r_slow_t}초간 {r_slow}% 둔화" + E + ", 기본 지속 효과 적용.",
        "names": ("싹둑싹둑!", "돌격가위", "바느질"),
    },
    "ja": {
        "name": "グウェン",
        "attack": "パッシブ " + O + "裁断" + E + "：通常攻撃とスキル命中で" + mag("p_dmg", "p_ratio") + "の追加" + M + "魔法ダメージ" + E +
                  "、チャンピオンには" + W + "最大体力の{p_hp}%の確定ダメージ" + E + "も与え" + mag("p_heal", "p_heal_r") +
                  "回復。通常攻撃ごとにハサミのスタック+1、最大{q_n}。",
        "skill": "前方を" + A + "1+スタック" + E + "回切り各" + mag("q_mini", "q_mini_r") + "、最後の一断ちで" + mag("q_dmg", "q_ratio") + "の" +
                 M + "魔法ダメージ" + E + "、中心の敵は" + W + "{q_true}の確定ダメージ" + E + "を追加で受ける。毎回パッシブ適用。",
        "skill2": O + "スキップスラッシュ" + E + "：敵チャンピオンへ突進、{e_t}秒間攻撃速度+{e_as}%、射程増加、命中時" + mag("e_dmg", "e_ratio") +
                  "。着地点に" + O + "聖なる霧" + E + "が{w_t}秒：霧の中では" + A + "インビジブル" + E + "（遠くの敵は対象にできない）、物防と魔防+{w_def}。",
        "ult": "敵チャンピオンへ針を3回投げる（1本、3本、5本）：各" + needles() + "の" + M + "魔法ダメージ" + E + "、" + R +
               "{r_slow_t}秒間{r_slow}%スロウ" + E + "、パッシブ適用。",
        "names": ("チョキチョキッ！", "スキップスラッシュ", "針仕事"),
    },
}

C = "league_gwen_sfx_"
V = "league_gwen_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_gwen_a_swing": [(C + "a_swing", 0.4, 0.0)],
    "league_gwen_a_hit": [(C + "a_hit", 0.35, 0.0)],
    "league_gwen_q_open": [(C + "q_open", 0.45, 0.0)],
    "league_gwen_q_snip": [(C + "q_snip", 0.45, 0.0)],
    "league_gwen_q_final": [(C + "q_final", 0.6, 0.0)],
    "league_gwen_q_hit": [(C + "q_hit", 0.25, 0.0)],
    "league_gwen_q_true": [(C + "q_true", 0.45, 0.0)],
    "league_gwen_e_cast": [(C + "e_cast", 0.55, 0.0)],
    "league_gwen_w_cast": [(C + "w_cast", 0.55, 0.0)],
    "league_gwen_r_cast": [(C + "r_cast", 0.55, 0.0)],
    "league_gwen_r_throw": [(C + "r_throw", 0.55, 0.0)],
    "league_gwen_r_hit": [(C + "r_hit", 0.35, 0.0)],
    "league_gwen_vo_q": [(V + "q", 0.75, 0.0)],
    "league_gwen_vo_w": [(V + "w", 0.75, 0.1)],
    "league_gwen_vo_e": [(V + "e", 0.8, 0.0)],
    "league_gwen_vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ratio", "p_hp", "p_heal", "p_heal_r", "q_n", "q_mini", "q_mini_r", "q_dmg",
                           "q_ratio", "q_true", "e_as", "e_dmg", "e_ratio", "w_def", "r_dmg1", "r_dmg2", "r_dmg3",
                           "r_ratio", "r_slow")}
    for k in ("e_t", "w_t", "r_slow_t"):
        v[k] = secs(p[k])
    return v


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


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
    for k in [k for k in ov if ID in k]:      # her keys rebuilt (a renamed sound leaves none behind)
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
    if "Gwen" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Gwen. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
