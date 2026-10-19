"""Volibear's text (5 languages), sound_info files and his keys in the shared files, numbers from build_volibear.P.

    python tools/kit/setup_volibear.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_volibear in every language, description + skill_name),
sound/sfx/league_volibear_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Volibear named). Only his keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 沃利贝尔 (不灭狂雷): 狂雷渐起, 擂首一击, 暴怒撕咬, 霹天雳地, 天声震落; zh_TW 弗力貝爾 (無情風暴):
無情風暴, 雷霆貫擊, 狂熊撕咬, 蒼穹裂隙, 風暴使者; ja ボリベア: 無慈悲の嵐, 稲妻の猛攻, 激昂の斬撃, 天破の一撃, 嵐を起こす者; ko 볼리베어:
무자비한 폭풍, 번개 강타, 광란의 상처, 천공 분열, 폭풍을 부르는 자.
Slots: skill = Q Thundering Smash, skill2 = E Sky Splitter, ult = R Stormbringer; the passive and W Frenzied Maul (a
maul every w_cd ticks) are in the attack's text. No combo sentence in any text (the user's rule). The main pack's
rules are the ones written (the second maul heals a flat amount); the add-on league_volibear heals by missing health,
chains the lightning and silences towers, and says so itself.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_volibear import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_volibear"
VERSION = "0.164.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle face_to); banpick_center: the card rule (-39 - top)
VIEW = {"face": {"x": 6, "y": -26}, "center": {"x": 0, "y": -16}, "banpick_center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def heal(d, r):
    return f"{G}{{{d}}}{E} + {ADi}{G}{{{r}}}%{E}"


def shield(d, r):
    return f"{G}{{{d}}}{E} + {APi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "沃利贝尔",
        "attack": O + "狂雷渐起" + E + "：攻击和技能叠攻速（每层{p_as}%，5层）；满层后攻击放出闪电，" + mag("p_dmg", "p_ap") + "魔法伤害。" +
                  O + "暴怒撕咬" + E + "：每" + A + "{w_cd}秒" + E + "攻击变成撕咬，造成" + phys("w_dmg", "w_ratio") + "物理伤害并标记英雄，"
                  "再咬时伤害+{w2}%并回复" + heal("w_heal", "w_heal_ad") + "生命。",
        "skill": "移速+{q_ms}%冲向敌方英雄，扑上去造成" + phys("q_dmg", "q_ratio") + "物理伤害并" + R + "眩晕{q_stun}秒" + E + "。",
        "skill2": "召雷劈向目标区域，" + A + "{e_delay}秒" + E + "后造成" + mag("e_dmg", "e_ap") + "魔法伤害（英雄另受{e_hp}%最大生命），" + R +
                  "减速{e_slow}%" + E + "；自己在范围内时得到" + shield("e_sh", "e_sh_ap") + "护盾。",
        "ult": "跃向敌方英雄砸地，周围敌人受" + phys("r_dmg", "r_ratio") + "物理伤害并" + R + "减速{r_slow}%" + E + "；之后" + A + "{r_form}秒" +
               E + "内生命+{r_hp}、攻击距离增加。",
        "names": ("擂首一击", "霹天雳地", "天声震落"),
    },
    "zh-hant": {
        "name": "弗力貝爾",
        "attack": O + "無情風暴" + E + "：攻擊和技能疊攻速（每層{p_as}%，5層）；滿層後攻擊放出閃電，" + mag("p_dmg", "p_ap") + "魔法傷害。" +
                  O + "狂熊撕咬" + E + "：每" + A + "{w_cd}秒" + E + "攻擊變成撕咬，造成" + phys("w_dmg", "w_ratio") + "物理傷害並標記英雄，"
                  "再咬時傷害+{w2}%並回復" + heal("w_heal", "w_heal_ad") + "生命。",
        "skill": "移速+{q_ms}%衝向敵方英雄，撲上去造成" + phys("q_dmg", "q_ratio") + "物理傷害並" + R + "暈眩{q_stun}秒" + E + "。",
        "skill2": "召雷劈向目標區域，" + A + "{e_delay}秒" + E + "後造成" + mag("e_dmg", "e_ap") + "魔法傷害（英雄另受{e_hp}%最大生命），" + R +
                  "緩速{e_slow}%" + E + "；自己在範圍內時得到" + shield("e_sh", "e_sh_ap") + "護盾。",
        "ult": "躍向敵方英雄砸地，周圍敵人受" + phys("r_dmg", "r_ratio") + "物理傷害並" + R + "緩速{r_slow}%" + E + "；之後" + A + "{r_form}秒" +
               E + "內生命+{r_hp}、攻擊距離增加。",
        "names": ("雷霆貫擊", "蒼穹裂隙", "風暴使者"),
    },
    "en": {
        "name": "Volibear",
        "attack": O + "The Relentless Storm" + E + ": attacks and spells stack attack speed ({p_as}% each, 5); at 5 his attacks "
                  "loose lightning for " + mag("p_dmg", "p_ap") + " " + M + "magic damage" + E + ". " + O + "Frenzied Maul" + E +
                  ": every " + A + "{w_cd}s" + E + " an attack becomes a maul for " + phys("w_dmg", "w_ratio") + " physical damage "
                  "and marks a champion; mauling a marked one deals {w2}% more and heals " + heal("w_heal", "w_heal_ad") + ".",
        "skill": "Rushes at an enemy champion with {q_ms}% move speed and pounces for " + phys("q_dmg", "q_ratio") +
                 " physical damage, " + R + "stunning {q_stun}s" + E + ".",
        "skill2": "Calls lightning on an area: after " + A + "{e_delay}s" + E + " it deals " + mag("e_dmg", "e_ap") + " magic damage "
                  "(+{e_hp}% max health to champions) and " + R + "slows {e_slow}%" + E + "; standing in it shields him for " +
                  shield("e_sh", "e_sh_ap") + ".",
        "ult": "Leaps onto an enemy champion: enemies around take " + phys("r_dmg", "r_ratio") + " physical damage and are " + R +
               "slowed {r_slow}%" + E + "; for " + A + "{r_form}s" + E + " he has +{r_hp} health and more attack range.",
        "names": ("Thundering Smash", "Sky Splitter", "Stormbringer"),
    },
    "ko": {
        "name": "볼리베어",
        "attack": O + "무자비한 폭풍" + E + ": 공격과 스킬이 공격 속도 중첩(중첩당 {p_as}%, 5회); 5회면 공격이 번개를 내뿜어 " +
                  mag("p_dmg", "p_ap") + " 마법 피해. " + O + "광란의 상처" + E + ": " + A + "{w_cd}초" + E + "마다 공격이 할퀴기로 바뀌어 " +
                  phys("w_dmg", "w_ratio") + " 물리 피해와 표식; 표식 대상에게는 피해 {w2}% 증가, " + heal("w_heal", "w_heal_ad") + " 회복.",
        "skill": "이동 속도 +{q_ms}%로 적 챔피언에게 돌진해 덮쳐 " + phys("q_dmg", "q_ratio") + " 물리 피해와 " + R + "{q_stun}초 기절" + E + ".",
        "skill2": "지역에 번개를 불러 " + A + "{e_delay}초" + E + " 뒤 " + mag("e_dmg", "e_ap") + " 마법 피해(챔피언은 최대 체력 {e_hp}% 추가)와 " + R +
                  "{e_slow}% 둔화" + E + "; 범위 안에 있으면 " + shield("e_sh", "e_sh_ap") + " 보호막.",
        "ult": "적 챔피언에게 도약해 주변 적에게 " + phys("r_dmg", "r_ratio") + " 물리 피해와 " + R + "{r_slow}% 둔화" + E + "; " + A + "{r_form}초" +
               E + " 동안 체력 +{r_hp}, 사거리 증가.",
        "names": ("번개 강타", "천공 분열", "폭풍을 부르는 자"),
    },
    "ja": {
        "name": "ボリベア",
        "attack": O + "無慈悲の嵐" + E + "：攻撃とスキルで攻撃速度スタック（1つ{p_as}%、5つ）；5つで攻撃が稲妻を放ち" + mag("p_dmg", "p_ap") +
                  "の魔法ダメージ。" + O + "激昂の斬撃" + E + "：" + A + "{w_cd}秒" + E + "ごとに攻撃が噛みつきになり" + phys("w_dmg", "w_ratio") +
                  "の物理ダメージとマーク；マーク中は{w2}%増し、" + heal("w_heal", "w_heal_ad") + "回復。",
        "skill": "移動速度+{q_ms}%で敵チャンピオンへ突進し、飛びかかって" + phys("q_dmg", "q_ratio") + "の物理ダメージと" + R + "{q_stun}秒スタン" +
                 E + "。",
        "skill2": "範囲に雷を呼び" + A + "{e_delay}秒" + E + "後に" + mag("e_dmg", "e_ap") + "の魔法ダメージ（チャンピオンは最大体力の{e_hp}%追加）と" +
                  R + "{e_slow}%スロウ" + E + "；範囲内にいると" + shield("e_sh", "e_sh_ap") + "のシールド。",
        "ult": "敵チャンピオンへ跳びかかり周りの敵に" + phys("r_dmg", "r_ratio") + "の物理ダメージと" + R + "{r_slow}%スロウ" + E + "；" + A +
               "{r_form}秒" + E + "体力+{r_hp}、射程増加。",
        "names": ("稲妻の猛攻", "天破の一撃", "嵐を起こす者"),
    },
}

C = "league_volibear_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_volibear_a_swing": [(C + "a_swing", 0.35, 0.0)],
    "league_volibear_a_hit": [(C + "a_hit", 0.4, 0.0)],
    "league_volibear_p_bolt": [(C + "p_bolt", 0.4, 0.0)],
    "league_volibear_p_hit": [(C + "p_hit", 0.35, 0.0)],
    "league_volibear_w": [(C + "w", 0.4, 0.0)],
    "league_volibear_w_hit": [(C + "w_hit", 0.45, 0.0)],
    "league_volibear_w_heal": [(C + "w_heal", 0.45, 0.0)],
    "league_volibear_q": [(C + "q", 0.4, 0.0)],
    "league_volibear_q_smash": [(C + "q_smash", 0.45, 0.0)],
    "league_volibear_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_volibear_e": [(C + "e", 0.4, 0.0)],
    "league_volibear_e_cloud": [(C + "e_cloud", 0.4, 0.0)],
    "league_volibear_e_bolt": [(C + "e_bolt", 0.55, 0.0)],
    "league_volibear_e_hit": [(C + "e_hit", 0.35, 0.0)],
    "league_volibear_e_sh": [(C + "e_sh", 0.4, 0.0)],
    "league_volibear_r": [(C + "r", 0.5, 0.0)],
    "league_volibear_r_land": [(C + "r_land", 0.6, 0.0)],
    "league_volibear_r_hit": [(C + "r_hit", 0.45, 0.0)],
    "league_volibear_r_tower": [(C + "r_tower", 0.45, 0.0)],
    "league_volibear_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_volibear_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_volibear_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_volibear_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_as", "p_dmg", "p_ap", "w_dmg", "w2", "w_heal", "w_heal_ad", "q_ms", "q_dmg", "e_dmg", "e_ap",
                           "e_hp", "e_slow", "e_sh", "e_sh_ap", "r_dmg", "r_ratio", "r_slow", "r_hp")}
    v["w_ratio"] = 100 + p["w_ratio"]     # the maul is his blow with w_ratio% AD more
    v["q_ratio"] = 100 + p["q_ratio"]     # the pounce is his blow with q_ratio% AD more
    for k in ("w_cd", "q_stun", "e_delay", "r_form"):
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
    if "Volibear" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Volibear. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
