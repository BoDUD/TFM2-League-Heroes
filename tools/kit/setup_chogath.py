"""Cho'Gath's text (5 languages), sound_info files and his keys in the shared files, numbers from build_chogath.P.

    python tools/kit/setup_chogath.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_chogath in every language, description + skill_name),
sound/sfx/league_chogath_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Cho'Gath named). Only his keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 科加斯 (虚空恐惧): 肉食者, 破裂, 野性尖叫, 恐惧之刺, 盛宴; zh_TW 科加斯 (虛空恐懼): 肉食者, 破裂,
野性尖嘯, 恐懼尖刺, 饗宴; ja チョ＝ガス: 暴食, ラプチャー, スクリーム, ヴォーパルスパイク, 捕食; ko 초가스: 육식, 파열, 흉포한 울부짖음, 날카로운 가시,
포식.
Slots: skill = Q Rupture, skill2 = W Feral Scream, ult = R Feast; the passive Carnivore and E Vorpal Spikes (e_n spiked
attacks every e_cd ticks) are in the attack's text. No combo sentence in any text (the user's rule). The main pack's
rules are the ones written (Feast's stacks end with his death); the add-on league_chogath keeps them, presses Feast
only for a kill and says so itself.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_chogath import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_chogath"
VERSION = "0.173.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, true / physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: the face point between his eyes (his head hangs low, 16 game px over his soles; tfm2_ase.py face puts
# the crown at the scythe tips, 34 px up, where a portrait would show no head); no banpick_center - the idle's top is
# 27.3 px over the frame centre, under the card rule's 28 (tools/art/bp_card_audit.py)
VIEW = {"face": {"x": 11, "y": -5}, "center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def heal(d, r):
    return f"{G}{{{d}}}{E} + {APi}{G}{{{r}}}%{E}"


def bite():
    return f"{O}{{r_dmg}}{E} + {{r_hp}}%"


TEXT = {
    "zh-hans": {
        "name": "科加斯",
        "attack": O + "肉食者" + E + "：攻击击杀单位时回复" + heal("p_heal", "p_ap") + "生命。" + O + "恐惧之刺" + E + "：每" + A + "{e_cd}秒" + E +
                  "接下来{e_n}次攻击射出一排尖刺，直线上的敌人受" + mag("e_dmg", "e_ap") + "魔法伤害并" + R + "减速{e_slow}%" + E +
                  "，英雄另受{e_hp}%最大生命真实伤害。",
        "skill": "地面破裂，" + A + "{q_delay}秒" + E + "后尖刺冲出，造成" + mag("q_dmg", "q_ap") + "魔法伤害，" + R + "击飞{q_up}秒" + E + "并" +
                 R + "减速{q_slow}%" + E + "。",
        "skill2": "向前方锥形区域尖叫，造成" + mag("w_dmg", "w_ap") + "魔法伤害并" + R + "沉默{w_sil}秒" + E + "。",
        "ult": "吞噬受伤的敌方英雄，造成" + O + "{r_dmg}" + E + " + 自身{r_hp}%最大生命的真实伤害和" + APi + M + "{r_ap}%" + E + "无视魔抗的魔法伤害；吃掉则叠一层："
               "最大生命+{r_stack_hp}、移速-{r_stack_ms}%、体型变大（不封顶，死亡清空）。",
        "names": ("破裂", "野性尖叫", "盛宴"),
    },
    "zh-hant": {
        "name": "科加斯",
        "attack": O + "肉食者" + E + "：攻擊擊殺單位時回復" + heal("p_heal", "p_ap") + "生命。" + O + "恐懼尖刺" + E + "：每" + A + "{e_cd}秒" + E +
                  "接下來{e_n}次攻擊射出一排尖刺，直線上的敵人受" + mag("e_dmg", "e_ap") + "魔法傷害並" + R + "緩速{e_slow}%" + E +
                  "，英雄另受{e_hp}%最大生命真實傷害。",
        "skill": "地面破裂，" + A + "{q_delay}秒" + E + "後尖刺衝出，造成" + mag("q_dmg", "q_ap") + "魔法傷害，" + R + "擊飛{q_up}秒" + E + "並" +
                 R + "緩速{q_slow}%" + E + "。",
        "skill2": "向前方錐形區域尖嘯，造成" + mag("w_dmg", "w_ap") + "魔法傷害並" + R + "沉默{w_sil}秒" + E + "。",
        "ult": "吞噬受傷的敵方英雄，造成" + O + "{r_dmg}" + E + " + 自身{r_hp}%最大生命的真實傷害和" + APi + M + "{r_ap}%" + E + "無視魔抗的魔法傷害；吃掉則疊一層："
               "最大生命+{r_stack_hp}、移速-{r_stack_ms}%、體型變大（不封頂，死亡清空）。",
        "names": ("破裂", "野性尖嘯", "饗宴"),
    },
    "en": {
        "name": "Cho'Gath",
        "attack": O + "Carnivore" + E + ": a unit his attack kills heals him " + heal("p_heal", "p_ap") + ". " + O + "Vorpal Spikes" +
                  E + ": every " + A + "{e_cd}s" + E + " his next {e_n} attacks fire a line of spikes: " + mag("e_dmg", "e_ap") +
                  " " + M + "magic damage" + E + " and a " + R + "{e_slow}% slow" + E + " to enemies in it, champions also taking "
                  "{e_hp}% max health true damage.",
        "skill": "Ruptures the ground: after " + A + "{q_delay}s" + E + " spikes burst out for " + mag("q_dmg", "q_ap") +
                 " magic damage, " + R + "knocking up {q_up}s" + E + " and " + R + "slowing {q_slow}%" + E + ".",
        "skill2": "Screams in a cone ahead: " + mag("w_dmg", "w_ap") + " magic damage and " + R + "silence {w_sil}s" + E + ".",
        "ult": "Devours a wounded enemy champion: " + bite() + " of his max health as true damage and " + APi + M + "{r_ap}%" + E +
               " magic damage through all magic resist. A kill is a stack: +{r_stack_hp} max health, -{r_stack_ms}% move "
               "speed and a bigger body (no cap; lost on death).",
        "names": ("Rupture", "Feral Scream", "Feast"),
    },
    "ko": {
        "name": "초가스",
        "attack": O + "육식" + E + ": 기본 공격으로 처치하면 " + heal("p_heal", "p_ap") + " 회복. " + O + "날카로운 가시" + E + ": " + A +
                  "{e_cd}초" + E + "마다 다음 {e_n}회 공격이 가시를 일직선으로 쏘아 " + mag("e_dmg", "e_ap") + " 마법 피해와 " + R +
                  "{e_slow}% 둔화" + E + ", 챔피언은 최대 체력 {e_hp}% 고정 피해 추가.",
        "skill": "땅을 갈라 " + A + "{q_delay}초" + E + " 뒤 가시가 솟아 " + mag("q_dmg", "q_ap") + " 마법 피해, " + R + "{q_up}초 에어본" + E +
                 ", " + R + "{q_slow}% 둔화" + E + ".",
        "skill2": "전방 원뿔에 울부짖어 " + mag("w_dmg", "w_ap") + " 마법 피해와 " + R + "{w_sil}초 침묵" + E + ".",
        "ult": "부상당한 적 챔피언을 삼켜 " + bite() + " (자신의 최대 체력) 고정 피해와 " + APi + M + "{r_ap}%" + E + " 마법 피해(마법 저항 무시). "
               "처치하면 중첩: 최대 체력 +{r_stack_hp}, 이동 속도 -{r_stack_ms}%, 몸집 증가(제한 없음, 사망 시 초기화).",
        "names": ("파열", "흉포한 울부짖음", "포식"),
    },
    "ja": {
        "name": "チョ＝ガス",
        "attack": O + "暴食" + E + "：通常攻撃でユニットを倒すと" + heal("p_heal", "p_ap") + "回復。" + O + "ヴォーパルスパイク" + E + "：" + A +
                  "{e_cd}秒" + E + "ごとに次の{e_n}回の攻撃が棘を直線に放ち" + mag("e_dmg", "e_ap") + "の魔法ダメージと" + R + "{e_slow}%スロウ" + E +
                  "、チャンピオンは最大体力の{e_hp}%確定ダメージ追加。",
        "skill": "地面を割り" + A + "{q_delay}秒" + E + "後に棘が突き出て" + mag("q_dmg", "q_ap") + "の魔法ダメージ、" + R + "{q_up}秒打ち上げ" + E +
                 "と" + R + "{q_slow}%スロウ" + E + "。",
        "skill2": "前方の扇状範囲に叫び" + mag("w_dmg", "w_ap") + "の魔法ダメージと" + R + "{w_sil}秒サイレンス" + E + "。",
        "ult": "傷ついた敵チャンピオンを捕食し" + bite() + "（自身の最大体力）の確定ダメージと" + APi + M + "{r_ap}%" + E + "の魔法ダメージ"
               "（魔法防御無視）。倒すとスタック：最大体力+{r_stack_hp}、移動速度-{r_stack_ms}%、体が大きくなる（上限なし、死亡で消える）。",
        "names": ("ラプチャー", "スクリーム", "捕食"),
    },
}

C = "league_chogath_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_chogath_a_swing": [(C + "a_swing", 0.35, 0.0)],
    "league_chogath_a_hit": [(C + "a_hit", 0.4, 0.0)],
    "league_chogath_p_heal": [(C + "p_heal", 0.35, 0.0)],
    "league_chogath_e_spikes": [(C + "e_spikes", 0.45, 0.0)],
    "league_chogath_e_hit": [(C + "e_hit", 0.35, 0.0)],
    "league_chogath_q": [(C + "q", 0.4, 0.0)],
    "league_chogath_q_crack": [(C + "q_crack", 0.45, 0.0)],
    "league_chogath_q_burst": [(C + "q_burst", 0.55, 0.0)],
    "league_chogath_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_chogath_w": [(C + "w", 0.55, 0.0)],
    "league_chogath_w_hit": [(C + "w_hit", 0.35, 0.0)],
    "league_chogath_r": [(C + "r", 0.5, 0.0)],
    "league_chogath_r_bite": [(C + "r_bite", 0.6, 0.0)],
    "league_chogath_r_hit": [(C + "r_hit", 0.45, 0.0)],
    "league_chogath_r_grow": [(C + "r_grow", 0.5, 0.0)],
    "league_chogath_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_chogath_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_chogath_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_chogath_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_heal", "p_ap", "e_n", "e_dmg", "e_ap", "e_hp", "e_slow", "q_dmg", "q_ap", "q_slow", "w_dmg",
                           "w_ap", "r_dmg", "r_hp", "r_ap", "r_stack_hp", "r_stack_ms")}
    for k in ("e_cd", "q_delay", "q_up", "w_sil"):
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
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 + the idle's top over the frame centre)")
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
    if "Cho'Gath" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Cho'Gath. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
