"""Warwick's text (5 languages), sound_info files and his keys in the shared files, numbers from build_warwick.P.

    python tools/kit/setup_warwick.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_warwick in every language, description + skill_name),
sound/sfx/league_warwick_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Warwick named). Only his keys change in the shared files. JSON: indent 2, CRLF,
UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 沃里克 (祖安怒兽): 血之饥渴, 野兽之口, 鲜血追猎, 远祖嗥叫, 无尽束缚; zh_TW 沃維克 (嗜血狂怒):
永恆飢渴, 猛獸狂顎, 血跡獵蹤, 本能怒嚎, 無盡束縛; ja ワーウィック: 永遠の渇き, 野獣の牙, 血の追跡, 怒りの咆哮, 絶狼牙連撃; ko 워윅:
끝없는 허기, 야수의 송곳니, 피의 사냥, 원시의 포효, 무한의 구속.
Slots: skill = Q Jaws of the Beast, skill2 = E Primal Howl, ult = R Infinite Duress; the passive Eternal Hunger and W Blood
Hunt in the attack's text. No combo sentence in any text (the user's rule); the README and the add-on league_warwick
say them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_warwick import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_warwick"
VERSION = "0.180.0"     # the next free number above main 0.179.0 (the combos #411, 2026-10-20); retaken at merge time
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
M = "<#a974ffff>"      # magic damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between his eyes (the idle's eyes 41.5 design rows over his soles at PPU 1.5: 28 game px;
# 11 px ahead of his standing point - the hunched head is pushed out over his far foot; ppu_restyle face_to); the
# ban/pick card: his idle drawn at 0.88 (league.dll UI_SIZES: 63 game px wide with the raised tail) with its top 31.1 px
# over the frame centre at that size -> banpick_center -8 (tools/art/bp_card_audit.py; the spike under the canvas top)
VIEW = {"face": {"x": 11, "y": -28}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -8}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def adp(r):
    return f"{ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "沃里克",
        "attack": "挥爪。" + O + "血之饥渴" + E + "：普攻附带" + M + "{p_dmg}" + E + "魔法伤害并回复{p_heal}生命。" + O + "鲜血追猎" + E +
                  "：打中英雄后" + A + "{w_t}秒" + E + "内攻速+{w_as}%、移速+{w_ms}%。",
        "skill": "扑向目标撕咬，造成" + phys("q_dmg", "q_ratio") + "+{q_hp}%目标最大生命值物理伤害，回复" + phys("q_heal", "q_heal_r") + "生命。",
        "skill2": A + "{e_t}秒" + E + "内受到的伤害减少{e_red}%，结束时仰天嚎叫，让周围的敌人" + R + "恐惧" + E + A + "{e_fear}秒" + E + "。",
        "ult": "朝前扑出，" + R + "压制" + E + "撞到的第一个敌方英雄" + A + "{r_sup}秒" + E + "，期间连抓三下，每下" + phys("r_dmg", "r_ratio") +
               "物理伤害并回复{r_heal}生命。",
        "names": ("野兽之口", "远祖嗥叫", "无尽束缚"),
    },
    "zh-hant": {
        "name": "沃維克",
        "attack": "揮爪。" + O + "永恆飢渴" + E + "：普攻附帶" + M + "{p_dmg}" + E + "魔法傷害並回復{p_heal}生命。" + O + "血跡獵蹤" + E +
                  "：打中英雄後" + A + "{w_t}秒" + E + "內攻速+{w_as}%、移速+{w_ms}%。",
        "skill": "撲向目標撕咬，造成" + phys("q_dmg", "q_ratio") + "+{q_hp}%目標最大生命值物理傷害，回復" + phys("q_heal", "q_heal_r") + "生命。",
        "skill2": A + "{e_t}秒" + E + "內受到的傷害減少{e_red}%，結束時仰天怒嚎，讓周圍的敵人" + R + "恐懼" + E + A + "{e_fear}秒" + E + "。",
        "ult": "朝前撲出，" + R + "壓制" + E + "撞到的第一個敵方英雄" + A + "{r_sup}秒" + E + "，期間連抓三下，每下" + phys("r_dmg", "r_ratio") +
               "物理傷害並回復{r_heal}生命。",
        "names": ("猛獸狂顎", "本能怒嚎", "無盡束縛"),
    },
    "en": {
        "name": "Warwick",
        "attack": "A claw swipe. " + O + "Eternal Hunger" + E + ": his attacks deal " + M + "{p_dmg}" + E + " bonus magic damage and heal him "
                  "{p_heal}. " + O + "Blood Hunt" + E + ": hitting a champion gives +{w_as}% attack speed and +{w_ms}% move speed for " +
                  A + "{w_t}s" + E + ".",
        "skill": "Lunges at the target and bites for " + phys("q_dmg", "q_ratio") + " + {q_hp}% of its max health as physical damage, "
                 "healing " + phys("q_heal", "q_heal_r") + ".",
        "skill2": "Takes {e_red}% less damage for " + A + "{e_t}s" + E + ", then howls, making nearby enemies " + R + "flee" + E + " for " +
                  A + "{e_fear}s" + E + ".",
        "ult": "Leaps forward and " + R + "suppresses" + E + " the first enemy champion hit for " + A + "{r_sup}s" + E + ", clawing it three "
               "times for " + phys("r_dmg", "r_ratio") + " physical damage each and healing {r_heal} each.",
        "names": ("Jaws of the Beast", "Primal Howl", "Infinite Duress"),
    },
    "ko": {
        "name": "워윅",
        "attack": "할퀴기. " + O + "끝없는 허기" + E + ": 기본 공격이 " + M + "{p_dmg}" + E + " 추가 마법 피해를 입히고 체력 {p_heal} 회복. " +
                  O + "피의 사냥" + E + ": 챔피언 적중 시 " + A + "{w_t}초" + E + " 동안 공격 속도 +{w_as}%, 이동 속도 +{w_ms}%.",
        "skill": "대상에게 달려들어 물어뜯어 " + phys("q_dmg", "q_ratio") + " + 대상 최대 체력 {q_hp}% 물리 피해, 체력 " +
                 phys("q_heal", "q_heal_r") + " 회복.",
        "skill2": A + "{e_t}초" + E + " 동안 받는 피해 {e_red}% 감소, 끝나면 울부짖어 주변 적 " + A + "{e_fear}초" + E + " " + R + "공포" + E + ".",
        "ult": "앞으로 도약해 처음 부딪힌 적 챔피언을 " + A + "{r_sup}초" + E + " " + R + "제압" + E + "하고 세 번 할퀴어 매번 " +
               phys("r_dmg", "r_ratio") + " 물리 피해, 체력 {r_heal} 회복.",
        "names": ("야수의 송곳니", "원시의 포효", "무한의 구속"),
    },
    "ja": {
        "name": "ワーウィック",
        "attack": "爪で引き裂く。" + O + "永遠の渇き" + E + "：通常攻撃が" + M + "{p_dmg}" + E + "の追加魔法ダメージを与え、体力を{p_heal}回復。" +
                  O + "血の追跡" + E + "：チャンピオンに命中すると" + A + "{w_t}秒" + E + "攻撃速度+{w_as}%、移動速度+{w_ms}%。",
        "skill": "対象に飛びかかって噛みつき、" + phys("q_dmg", "q_ratio") + "+対象の最大体力の{q_hp}%の物理ダメージ、体力を" +
                 phys("q_heal", "q_heal_r") + "回復。",
        "skill2": A + "{e_t}秒" + E + "間受けるダメージを{e_red}%軽減し、終わると咆哮して周囲の敵を" + A + "{e_fear}秒" + E + R + "恐怖" + E + "させる。",
        "ult": "前方へ跳びかかり、最初に当たった敵チャンピオンを" + A + "{r_sup}秒" + E + R + "サプレッション" + E + "、その間3回引き裂き、毎回" +
               phys("r_dmg", "r_ratio") + "の物理ダメージと体力{r_heal}回復。",
        "names": ("野獣の牙", "怒りの咆哮", "絶狼牙連撃"),
    },
}

C = "league_warwick_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_warwick_a_swing": [(C + "a", 0.4, 0.0)],
    "league_warwick_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_warwick_q_cast": [(C + "q", 0.45, 0.0)],
    "league_warwick_q_hit": [(C + "q_land", 0.3, 0.0), (C + "q_hit", 0.45, 0.0)],
    "league_warwick_e_cast": [(C + "e", 0.45, 0.0)],
    "league_warwick_e_howl": [(C + "e_howl", 0.55, 0.0)],
    "league_warwick_r_cast": [(C + "r", 0.5, 0.0)],
    "league_warwick_r_land": [(C + "r_hit", 0.45, 0.0)],
    "league_warwick_r_hit": [(C + "p_bite", 0.35, 0.0)],
    "league_warwick_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_warwick_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_warwick_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_heal", "w_as", "w_ms", "q_dmg", "q_ratio", "q_hp", "q_heal", "q_heal_r",
                           "e_red", "r_dmg", "r_ratio", "r_heal")}
    for k in ("w_t", "e_t", "e_fear", "r_sup"):
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
    if "Warwick" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Warwick. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
