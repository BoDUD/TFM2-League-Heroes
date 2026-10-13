"""Galio's text (5 languages), sound_info files and his keys in the shared files, numbers from build_galio.P.

    python tools/kit/setup_galio.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_galio in every language, description + skill_name),
sound/sfx/league_galio_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.106.0, Galio named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (加里奥 / 正义巨像; 巨像重击, 战争罡风, 杜朗护盾, 正义冲拳, 英雄登场; the client swaps
name and title) and Data Dragon 16.20.1 (zh_TW 加里歐 / 護國意志 / 征戰風暴 / 杜蘭德之盾 / 光榮制裁 / 英靈之門, ja ガリオ /
巨像の一撃 / 戦の旋風 / デュランドの守り / 正義の鉄拳 / 英雄降臨, ko 갈리오 / 석상의 강타 / 전장의 돌풍 / 듀란드의 방패 / 정의의 주먹 /
영웅출현).
Slots: skill = Q, skill2 = E (W told in its text), ult = R; the passive and W's passive shield are told in the attack's
text. No combo sentence in any text (the user's rule). No `league_galio_attack` sound: the engine would play it at the
start of every attack; the punch plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_galio import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_galio"
VERSION = "0.106.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7dd87dff>"      # shields
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
# 2026-10-13, at 100 % (rig_galio.py): the face on his head's crown (the eyes on row -21, the crown -27)
VIEW = {"face": {"x": 1, "y": -27}, "center": {"x": 0, "y": -12}}


def mag(k, ap="ap"):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_{ap}}}%{E}"


SMASH = M + "{p_dmg}" + E + " + " + APi + M + "{p_ap}%" + E
WARD = G + "{w_ps} + " + APi + "{w_ps_ap}%" + E
TORN = M + "{q_tdmg}" + E + " + " + APi + M + "{q_tap}%" + E
RSH = G + "{r_sh} + " + APi + "{r_sh_ap}%" + E

TEXT = {
    "zh-hans": {
        "name": "加里奥",
        "attack": O + "巨像重击" + E + "：每" + A + "{p_cd}秒" + E + "下一次普攻对周围敌人造成" + SMASH + M + "魔法伤害" + E + "。" + O + "杜朗护盾" + E +
                  "被动：普攻时获得" + WARD + "护盾，每" + A + "{w_ps_cd}秒" + E + "一次。",
        "skill": "射出两道风刃，落点造成" + mag("q") + M + "魔法伤害" + E + "，并留下" + A + "{q_t}秒" + E + "龙卷风，每" + A + "{q_tp}秒" + E + "造成" + TORN +
                 M + "魔法伤害" + E + "。",
        "skill2": "冲向敌方英雄，撞到第一个英雄造成" + mag("e") + M + "魔法伤害" + E + "并" + R + "击飞{e_up}秒" + E + "。" + O + "杜朗护盾" + E + "：蓄力" + A +
                  "{w_ch}秒" + E + "，伤害降低{w_dr}%，随后" + R + "嘲讽{w_taunt}秒" + E + "周围敌人，造成" + mag("w") + M + "魔法伤害" + E + "。",
        "ult": "给陷入苦战的友方英雄" + RSH + "护盾，引导" + A + "{r_ch}秒" + E + "后飞到其身边，落地造成" + mag("r") + M + "魔法伤害" + E + "并" + R +
               "击飞{r_up}秒" + E + "，周围友方英雄也获得护盾。",
        "names": ("战争罡风", "正义冲拳", "英雄登场"),
    },
    "zh-hant": {
        "name": "加里歐",
        "attack": O + "護國意志" + E + "：每" + A + "{p_cd}秒" + E + "下一次普攻對周圍敵人造成" + SMASH + M + "魔法傷害" + E + "。" + O + "杜蘭德之盾" + E +
                  "被動：普攻時獲得" + WARD + "護盾，每" + A + "{w_ps_cd}秒" + E + "一次。",
        "skill": "射出兩道風刃，落點造成" + mag("q") + M + "魔法傷害" + E + "，並留下" + A + "{q_t}秒" + E + "龍捲風，每" + A + "{q_tp}秒" + E + "造成" + TORN +
                 M + "魔法傷害" + E + "。",
        "skill2": "衝向敵方英雄，撞到第一個英雄造成" + mag("e") + M + "魔法傷害" + E + "並" + R + "擊飛{e_up}秒" + E + "。" + O + "杜蘭德之盾" + E + "：蓄力" + A +
                  "{w_ch}秒" + E + "，傷害降低{w_dr}%，隨後" + R + "嘲諷{w_taunt}秒" + E + "周圍敵人，造成" + mag("w") + M + "魔法傷害" + E + "。",
        "ult": "給陷入苦戰的友方英雄" + RSH + "護盾，引導" + A + "{r_ch}秒" + E + "後飛到其身邊，落地造成" + mag("r") + M + "魔法傷害" + E + "並" + R +
               "擊飛{r_up}秒" + E + "，周圍友方英雄也獲得護盾。",
        "names": ("征戰風暴", "光榮制裁", "英靈之門"),
    },
    "en": {
        "name": "Galio",
        "attack": O + "Colossal Smash" + E + ": every " + A + "{p_cd}s" + E + " his next attack deals " + SMASH + " " + M + "magic damage" + E +
                  " to enemies around him. " + O + "Shield of Durand" + E + " passive: attacking grants a " + WARD + " shield, once every " + A +
                  "{w_ps_cd}s" + E + ".",
        "skill": "Fires two windblasts: " + mag("q") + " " + M + "magic damage" + E + " where they land, leaving a tornado for " + A + "{q_t}s" + E +
                 " that deals " + TORN + " " + M + "magic damage" + E + " every " + A + "{q_tp}s" + E + ".",
        "skill2": "Charges at an enemy champion: the first champion hit takes " + mag("e") + " " + M + "magic damage" + E + " and is " + R +
                  "knocked up {e_up}s" + E + ". " + O + "Shield of Durand" + E + ": braces for " + A + "{w_ch}s" + E + " taking {w_dr}% less damage, then " +
                  R + "taunts" + E + " nearby enemies for " + R + "{w_taunt}s" + E + ", dealing " + mag("w") + " " + M + "magic damage" + E + ".",
        "ult": "Grants an allied champion in a fight a " + RSH + " shield, channels " + A + "{r_ch}s" + E + " and flies to it; landing deals " + mag("r") +
               " " + M + "magic damage" + E + " and " + R + "knocks up {r_up}s" + E + "; allied champions there are shielded too.",
        "names": ("Winds of War", "Justice Punch", "Hero's Entrance"),
    },
    "ko": {
        "name": "갈리오",
        "attack": O + "석상의 강타" + E + ": " + A + "{p_cd}초" + E + "마다 다음 기본 공격이 주변 적에게 " + SMASH + " " + M + "마법 피해" + E + ". " + O +
                  "듀란드의 방패" + E + " 기본 지속 효과: 기본 공격 시 " + WARD + " 보호막, " + A + "{w_ps_cd}초" + E + "마다 한 번.",
        "skill": "돌풍 두 개를 날려 떨어진 곳에 " + mag("q") + " " + M + "마법 피해" + E + ", " + A + "{q_t}초" + E + " 동안 회오리가 남아 " + A + "{q_tp}초" + E +
                 "마다 " + TORN + " " + M + "마법 피해" + E + ".",
        "skill2": "적 챔피언에게 돌진해 처음 부딪힌 챔피언에게 " + mag("e") + " " + M + "마법 피해" + E + "와 " + R + "{e_up}초 에어본" + E + ". " + O +
                  "듀란드의 방패" + E + ": " + A + "{w_ch}초" + E + " 동안 받는 피해 {w_dr}% 감소 후 주변 적을 " + R + "{w_taunt}초 도발" + E + ", " + mag("w") +
                  " " + M + "마법 피해" + E + ".",
        "ult": "싸우는 아군 챔피언에게 " + RSH + " 보호막, " + A + "{r_ch}초" + E + " 정신 집중 후 날아가 착지하며 " + mag("r") + " " + M + "마법 피해" + E +
               "와 " + R + "{r_up}초 에어본" + E + ", 주변 아군 챔피언도 보호막.",
        "names": ("전장의 돌풍", "정의의 주먹", "영웅출현"),
    },
    "ja": {
        "name": "ガリオ",
        "attack": O + "巨像の一撃" + E + "：" + A + "{p_cd}秒" + E + "毎に次の通常攻撃が周囲の敵に" + SMASH + "の" + M + "魔法ダメージ" + E + "。" + O +
                  "デュランドの守り" + E + "自動効果：通常攻撃で" + WARD + "のシールド（" + A + "{w_ps_cd}秒" + E + "毎）。",
        "skill": "二つの旋風を放ち着弾点に" + mag("q") + "の" + M + "魔法ダメージ" + E + "、" + A + "{q_t}秒" + E + "竜巻が残り" + A + "{q_tp}秒" + E + "毎に" + TORN +
                 "の" + M + "魔法ダメージ" + E + "。",
        "skill2": "敵チャンピオンへ突進し最初に当たったチャンピオンに" + mag("e") + "の" + M + "魔法ダメージ" + E + "と" + R + "{e_up}秒ノックアップ" + E + "。" + O +
                  "デュランドの守り" + E + "：" + A + "{w_ch}秒" + E + "構え被ダメージ{w_dr}%軽減、周囲の敵を" + R + "{w_taunt}秒挑発" + E + "し" + mag("w") + "の" +
                  M + "魔法ダメージ" + E + "。",
        "ult": "戦う味方チャンピオンに" + RSH + "のシールド、" + A + "{r_ch}秒" + E + "詠唱後に飛来し着地で" + mag("r") + "の" + M + "魔法ダメージ" + E + "と" + R +
               "{r_up}秒ノックアップ" + E + "、周囲の味方もシールド。",
        "names": ("戦の旋風", "正義の鉄拳", "英雄降臨"),
    },
}

C = "league_galio_sfx_"
S_ = "league_galio_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + c, vol, dl)] for k, c, vol, dl in [
    ("a_swing", "a_swing", 0.45, 0.0), ("a_hit", "a_hit", 0.45, 0.0), ("p", "p", 0.5, 0.0), ("p_hit", "p_hit", 0.6, 0.0),
    ("q", "q", 0.55, 0.0), ("q_hit", "q_hit", 0.55, 0.0), ("e", "e", 0.6, 0.0), ("e_hit", "e_hit", 0.6, 0.0),
    ("w", "w", 0.55, 0.0), ("w_hit", "w_hit", 0.6, 0.0), ("r", "r", 0.6, 0.0), ("r_ally", "r_ally", 0.5, 0.0),
    ("r_land", "r_land", 0.7, 0.0),
    ("vo_q", "vo_q", 0.8, 0.0), ("vo_w", "vo_w", 0.8, 0.0), ("vo_e", "vo_e", 0.8, 0.0), ("vo_r", "vo_r", 0.85, 0.0)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "w_ps", "w_ps_ap", "q_dmg", "q_ap", "q_tdmg", "q_tap", "e_dmg", "e_ap",
                           "w_dr", "w_dmg", "w_ap", "r_sh", "r_sh_ap", "r_dmg", "r_ap")}
    v.update({k: secs(p[k]) for k in ("p_cd", "w_ps_cd", "q_t", "q_tp", "e_up", "w_ch", "w_taunt", "r_ch", "r_up")})
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
    if "Galio" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Galio. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
