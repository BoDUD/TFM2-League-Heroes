"""Shyvana's text (5 languages), sound_info files and her keys in the shared files, numbers from build_shyvana.P.

    python tools/kit/setup_shyvana.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_shyvana in every language, description + skill_name),
sound/sfx/league_shyvana_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Shyvana named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (the rework) - zh_CN 希瓦娜 (龙血武姬): 龙鳞铁衣, 焚焰打击, 烈火圣盾, 爆炎吐息, 魔龙降世; zh_TW
希瓦娜 (半龍少女): 真龍鱗甲, 餘燼龍擊, 業火燃盾, 融焰爆裂, 真龍轉生; ja シヴァーナ: スケールメイル, エンバーストライク,
インフェルノイージス, モルテンバースト, 龍の降臨; ko 쉬바나: 미늘갑옷, 잉걸불 일격, 지옥불 방패, 용암 분출, 용의 강림.
Slots: skill = Q Emberstrike, skill2 = E Molten Burst, ult = R Dragon's Descent; W Inferno Aegis in the attack's text,
Dragon Fury and Scalemail in the ult's. No combo sentence in any text (the user's rule); the README says them. Q's
recasts are its own strikes (the text says what the next attacks do), not a combo sentence.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_shyvana import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_shyvana"
VERSION = "0.185.0"     # the next free number above main 0.184.1 (2026-10-21); retaken at merge time (Ornn is on its way)
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
M = "<#a974ffff>"      # magic damage
W = "<#f5f5f5ff>"      # true damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: provisional until the sprite (tfm2_ase.py face)
VIEW = {"face": {"x": 0, "y": -24}, "center": {"x": 0, "y": -12}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def tru(d, r):
    return f"{W}{{{d}}}{E} + {ADi}{W}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "希瓦娜",
        "attack": "挥击，附带目标{p_hp}%最大生命值的物理伤害。" + O + "烈火圣盾" + E + "：每" + A + "{w_cd}秒" + E + "的普攻获得" +
                  phys("w_sh", "w_sh_r") + "护盾和{w_ms}%移速，" + A + "{w_t}秒" + E + "后爆炸，造成" + M + "{w_dmg}+{w_hp}%最大生命值" + E +
                  "魔法伤害。",
        "skill": "斩击前方，造成" + phys("q_dmg", "q_ratio") + "物理伤害；" + A + "{q_win}秒" + E + "内下次普攻横扫周围，造成" +
                 phys("q2_dmg", "q2_ratio") + "物理伤害；魔龙形态再下次普攻撕咬，造成" + tru("q3_dmg", "q3_ratio") + "真实伤害。",
        "skill2": "掷出火球，命中敌人或到达终点时爆炸，造成" + M + "{e_dmg}+{e_hp}%最大生命值" + E + "魔法伤害并减速{e_slow}%，持续" + A +
                  "{e_slow_t}秒" + E + "。魔龙形态下火球更大、穿透敌人，并留下燃烧的地面。",
        "ult": O + "龙怒" + E + "攒满时化身魔龙，飞向敌方英雄并沿途喷火，造成" + M + "{r_dmg}+{r_hp}%最大生命值" + E + "魔法伤害并使其" + R +
               "恐惧" + E + A + "{r_fear}秒" + E + "。魔龙持续" + A + "{dg_t}秒" + E + "，生命+{dg_hp}%，" + O + "龙鳞铁衣" + E +
               "使护甲和魔抗+{dg_def}%。",
        "names": ("焚焰打击", "爆炎吐息", "魔龙降世"),
    },
    "zh-hant": {
        "name": "希瓦娜",
        "attack": "揮擊，附帶目標{p_hp}%最大生命值的物理傷害。" + O + "業火燃盾" + E + "：每" + A + "{w_cd}秒" + E + "的普攻獲得" +
                  phys("w_sh", "w_sh_r") + "護盾和{w_ms}%移速，" + A + "{w_t}秒" + E + "後爆炸，造成" + M + "{w_dmg}+{w_hp}%最大生命值" + E +
                  "魔法傷害。",
        "skill": "斬擊前方，造成" + phys("q_dmg", "q_ratio") + "物理傷害；" + A + "{q_win}秒" + E + "內下次普攻橫掃周圍，造成" +
                 phys("q2_dmg", "q2_ratio") + "物理傷害；真龍形態再下次普攻撕咬，造成" + tru("q3_dmg", "q3_ratio") + "真實傷害。",
        "skill2": "擲出火球，命中敵人或到達終點時爆炸，造成" + M + "{e_dmg}+{e_hp}%最大生命值" + E + "魔法傷害並緩速{e_slow}%，持續" + A +
                  "{e_slow_t}秒" + E + "。真龍形態下火球更大、穿透敵人，並留下燃燒的地面。",
        "ult": O + "龍怒" + E + "集滿時化身為龍，飛向敵方英雄並沿途噴火，造成" + M + "{r_dmg}+{r_hp}%最大生命值" + E + "魔法傷害並使其" + R +
               "恐懼" + E + A + "{r_fear}秒" + E + "。龍形持續" + A + "{dg_t}秒" + E + "，生命+{dg_hp}%，" + O + "真龍鱗甲" + E +
               "使護甲和魔抗+{dg_def}%。",
        "names": ("餘燼龍擊", "融焰爆裂", "真龍轉生"),
    },
    "en": {
        "name": "Shyvana",
        "attack": "A strike that also deals {p_hp}% of the target's max health as physical damage. " + O + "Inferno Aegis" + E +
                  ": every " + A + "{w_cd}s" + E + " an attack gives her a " + phys("w_sh", "w_sh_r") + " shield and +{w_ms}% move "
                  "speed; after " + A + "{w_t}s" + E + " the flames explode for " + M + "{w_dmg} + {w_hp}% of her max health" + E +
                  " magic damage.",
        "skill": "Slashes ahead for " + phys("q_dmg", "q_ratio") + " physical damage. Within " + A + "{q_win}s" + E + " her next "
                 "attack sweeps around her for " + phys("q2_dmg", "q2_ratio") + "; as a dragon the one after bites for " +
                 tru("q3_dmg", "q3_ratio") + " true damage.",
        "skill2": "Hurls a fireball that bursts on the first enemy or at its end for " + M + "{e_dmg} + {e_hp}% of her max "
                  "health" + E + " magic damage, slowing by {e_slow}% for " + A + "{e_slow_t}s" + E + ". As a dragon it is bigger, "
                  "passes through enemies and leaves the ground burning.",
        "ult": "With full " + O + "Dragon Fury" + E + " she becomes a dragon and flies at an enemy champion breathing fire: " + M +
               "{r_dmg} + {r_hp}% of her max health" + E + " magic damage and " + R + "fear" + E + " for " + A + "{r_fear}s" + E +
               ". The dragon lasts " + A + "{dg_t}s" + E + " with +{dg_hp}% health; " + O + "Scalemail" + E + " gives +{dg_def}% "
               "armour and magic resist.",
        "names": ("Emberstrike", "Molten Burst", "Dragon's Descent"),
    },
    "ko": {
        "name": "쉬바나",
        "attack": "공격이 대상 최대 체력의 {p_hp}% 물리 피해를 추가로 입힘. " + O + "지옥불 방패" + E + ": " + A + "{w_cd}초" + E + "마다 "
                  "공격 시 " + phys("w_sh", "w_sh_r") + " 보호막과 이동 속도 +{w_ms}%, " + A + "{w_t}초" + E + " 후 폭발해 " + M +
                  "{w_dmg} + 최대 체력의 {w_hp}%" + E + " 마법 피해.",
        "skill": "전방을 베어 " + phys("q_dmg", "q_ratio") + " 물리 피해. " + A + "{q_win}초" + E + " 안에 다음 공격은 주변을 쓸어 " +
                 phys("q2_dmg", "q2_ratio") + " 물리 피해, 용의 모습이면 그다음 공격이 물어뜯어 " + tru("q3_dmg", "q3_ratio") +
                 " 고정 피해.",
        "skill2": "화염구를 던져 처음 맞힌 적이나 끝에서 폭발, " + M + "{e_dmg} + 최대 체력의 {e_hp}%" + E + " 마법 피해와 " + A +
                  "{e_slow_t}초" + E + " 동안 {e_slow}% 둔화. 용의 모습이면 더 크고 적을 관통하며 땅을 불태움.",
        "ult": O + "용의 분노" + E + "가 가득 차면 용으로 변해 적 챔피언에게 날아가며 불을 뿜어 " + M + "{r_dmg} + 최대 체력의 {r_hp}%" + E +
               " 마법 피해와 " + A + "{r_fear}초" + E + " " + R + "공포" + E + ". 용의 모습 " + A + "{dg_t}초" + E + ", 체력 +{dg_hp}%, " +
               O + "미늘갑옷" + E + "으로 방어력과 마법 저항력 +{dg_def}%.",
        "names": ("잉걸불 일격", "용암 분출", "용의 강림"),
    },
    "ja": {
        "name": "シヴァーナ",
        "attack": "通常攻撃が対象の最大体力の{p_hp}%の物理ダメージを追加。" + O + "インフェルノイージス" + E + "：" + A + "{w_cd}秒" + E +
                  "ごとの攻撃で" + phys("w_sh", "w_sh_r") + "のシールドと移動速度+{w_ms}%、" + A + "{w_t}秒" + E + "後に爆発し" + M +
                  "{w_dmg}+最大体力の{w_hp}%" + E + "の魔法ダメージ。",
        "skill": "前方を斬り" + phys("q_dmg", "q_ratio") + "の物理ダメージ。" + A + "{q_win}秒" + E + "以内の次の攻撃は周囲をなぎ払い" +
                 phys("q2_dmg", "q2_ratio") + "、ドラゴン時はその次の攻撃で噛みつき" + tru("q3_dmg", "q3_ratio") + "の確定ダメージ。",
        "skill2": "火球を放ち、最初の敵か終点で爆発して" + M + "{e_dmg}+最大体力の{e_hp}%" + E + "の魔法ダメージと" + A + "{e_slow_t}秒" + E +
                  "の{e_slow}%スロウ。ドラゴン時は大きく敵を貫通し、地面を燃やす。",
        "ult": O + "ドラゴンフューリー" + E + "が満ちるとドラゴンに変身し、敵チャンピオンへ飛びながら炎を吐いて" + M + "{r_dmg}+最大体力の{r_hp}%" + E +
               "の魔法ダメージと" + A + "{r_fear}秒" + E + "の" + R + "フィアー" + E + "。ドラゴンは" + A + "{dg_t}秒" + E + "、体力+{dg_hp}%、" +
               O + "スケールメイル" + E + "で物防と魔防+{dg_def}%。",
        "names": ("エンバーストライク", "モルテンバースト", "龍の降臨"),
    },
}

C = "league_shyvana_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_shyvana_a": [(C + "a", 0.4, 0.0)],
    "league_shyvana_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_shyvana_d_a": [(C + "d_a", 0.4, 0.0)],
    "league_shyvana_q": [(C + "q", 0.45, 0.0)],
    "league_shyvana_q_hit": [(C + "q_hit", 0.35, 0.0)],
    "league_shyvana_q2": [(C + "q2", 0.45, 0.0)],
    "league_shyvana_q2_hit": [(C + "q2_hit", 0.35, 0.0)],
    "league_shyvana_d_q": [(C + "d_q", 0.45, 0.0)],
    "league_shyvana_d_q2": [(C + "d_q2", 0.45, 0.0)],
    "league_shyvana_q3": [(C + "d_q3", 0.5, 0.0)],
    "league_shyvana_q3_hit": [(C + "d_q3_hit", 0.4, 0.0)],
    "league_shyvana_w": [(C + "w", 0.4, 0.0)],
    "league_shyvana_w_blast": [(C + "w_blast", 0.45, 0.0)],
    "league_shyvana_w_hit": [(C + "a_hit", 0.2, 0.0)],
    "league_shyvana_w_heal": [(C + "w_heal", 0.35, 0.0)],
    "league_shyvana_e": [(C + "e", 0.45, 0.0)],
    "league_shyvana_de": [(C + "de", 0.5, 0.0)],
    "league_shyvana_e_land": [(C + "e_hit", 0.45, 0.0)],
    "league_shyvana_e_hit": [(C + "de_hit", 0.25, 0.0)],
    "league_shyvana_r": [(C + "r", 0.5, 0.0)],
    "league_shyvana_r_hit": [(C + "r_hit", 0.35, 0.0)],
    "league_shyvana_r_land": [(C + "d_a_hit", 0.45, 0.0)],
    "league_shyvana_tf_dragon": [(C + "tf", 0.5, 0.0)],
    "league_shyvana_tf_human": [(C + "untf", 0.45, 0.0)],
    "league_shyvana_full": [(C + "full", 0.4, 0.0)],
    "league_shyvana_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_shyvana_vo_q3": [(C + "vo_q3", 0.85, 0.0)],
    "league_shyvana_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_shyvana_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_hp", "w_sh", "w_sh_r", "w_ms", "w_dmg", "w_hp", "q_dmg", "q_ratio", "q2_dmg", "q2_ratio",
                           "q3_dmg", "q3_ratio", "e_dmg", "e_hp", "e_slow", "r_dmg", "r_hp", "dg_hp", "dg_def")}
    for k in ("w_cd", "w_t", "q_win", "e_slow_t", "r_fear", "dg_t"):
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
    if "Shyvana" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Shyvana. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
