"""Skarner's text (5 languages), sound_info files and their keys in the shared files, numbers from build_skarner.P
(setup_trundle.py's way).

    python tools/kit/setup_skarner.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_skarner in every language, description + skill_name),
sound/sfx/league_skarner_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Skarner named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 斯卡纳 (上古领主): 战栗; 撼地 / 擎天, 震地壁垒, 以绪塔尔冲击, 毒刺贯体; zh_TW 史加納:
震動餘波; 翻天覆地 / 尖岩飛彈, 壁壘波動, 伊克斯塔爾衝擊, 蠍尾穿刺; ja スカーナー: 響振動; 砕けし大地 / 大地の怒り, 激震の砦,
イシュタルの衝動, インペイル; ko 스카너: 진동의 가닥; 부서진 대지 / 지반 돌출, 대지의 수호자, 이쉬탈의 격돌, 꿰뚫기.
Slots: skill = Shattered Earth (its Upheaval throw in the same text), skill2 = Ixtal's Impact, ult = Impale; Threads of
Vibration and Seismic Bastion in the attack's text (the bastion's trigger - the charge's carry ending - is how W is cast
at all, so it is said). The texts say the main pack's rules (the add-on's copy has its own:
addons/league_skarner/make_override.py). No combo sentence in any text (the user's rule: the combos are the README's).
champion_view's face is his hood's crown measured up from the feet (text-audio.md): the face sits low at the front of
his body, not at the top of the tails tfm2_ase.py face takes for a crown.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_skarner import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_skarner"
VERSION = "0.227.0"     # above main 0.226.0 (#548 Locke 0.225.0, #549 Draven PPU), merged second, 2026-10-26
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point on his hood's crown (x ahead of the pivot, y up from the feet: hd/idle.png's hood top,
# row 34 of 59, its middle column 51.5 of the standing 40, at PPU 1.75, ~1.5 px ahead), the body centre as base's, the
# ban/pick card (bp_card_audit.py)
VIEW = {"face": {"x": 8, "y": -14}, "center": {"x": 0, "y": -12}}


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
        "name": "斯卡纳",
        "attack": "毒刺扎击。" + n("战栗") + "：普攻、巨石、毒刺打中英雄叠层，满{p_n}层" + t("{p_t}秒") + "内每秒掉最大生命{p_pct}%。" +
                  n("震地壁垒") + "：冲锋停下时得" + phys("w_sh", "w_sh_r") + "护盾" + t("{w_sh_t}秒") + "，震伤周围" +
                  phys("w_dmg", "w_ratio") + "、" + cc("减速") + "{w_slow}%。",
        "skill": "掘起巨石" + t("{q_t}秒") + "，攻速+{q_as}%；3次普攻溅射" + phys("q_dmg", "q_ratio") + "，第3次加最大生命{q_hp}%、" +
                 cc("减速") + "{q_slow}%。举满" + t("{q_hold}秒") + "就扔出" + n("擎天") + "：" + phys("q_toss_dmg", "q_toss_ratio") +
                 "+最大生命{q_hp}%。",
        "skill2": "冲向敌方英雄，撞上后拖着走，停下时造成" + phys("e_dmg", "e_ratio") + "物理伤害并" + cc("晕眩") + t("{e_stun}秒") + "。",
        "ult": "三根毒刺往前扎：直线上的敌方英雄受到" + phys("r_dmg", "r_ratio") + "物理伤害，被" + cc("压制") + t("{r_sup}秒") +
               "并拖到身边跟着走；扎中后移速+{r_ms}%" + t("{r_ms_t}秒") + "。",
        "names": ("撼地", "以绪塔尔冲击", "毒刺贯体"),
    },
    "zh-hant": {
        "name": "史加納",
        "attack": "毒刺扎擊。" + n("震動餘波") + "：普攻、巨石、毒刺打中英雄疊層，滿{p_n}層" + t("{p_t}秒") + "內每秒掉最大生命{p_pct}%。" +
                  n("壁壘波動") + "：衝鋒停下時得" + phys("w_sh", "w_sh_r") + "護盾" + t("{w_sh_t}秒") + "，震傷周圍" +
                  phys("w_dmg", "w_ratio") + "、" + cc("緩速") + "{w_slow}%。",
        "skill": "掘起巨石" + t("{q_t}秒") + "，攻速+{q_as}%；3次普攻濺射" + phys("q_dmg", "q_ratio") + "，第3次加最大生命{q_hp}%、" +
                 cc("緩速") + "{q_slow}%。舉滿" + t("{q_hold}秒") + "就扔出" + n("尖岩飛彈") + "：" + phys("q_toss_dmg", "q_toss_ratio") +
                 "+最大生命{q_hp}%。",
        "skill2": "衝向敵方英雄，撞上後拖著走，停下時造成" + phys("e_dmg", "e_ratio") + "物理傷害並" + cc("暈眩") + t("{e_stun}秒") + "。",
        "ult": "三根毒刺往前扎：直線上的敵方英雄受到" + phys("r_dmg", "r_ratio") + "物理傷害，被" + cc("壓制") + t("{r_sup}秒") +
               "並拖到身邊跟著走；扎中後移速+{r_ms}%" + t("{r_ms_t}秒") + "。",
        "names": ("翻天覆地", "伊克斯塔爾衝擊", "蠍尾穿刺"),
    },
    "en": {
        "name": "Skarner",
        "attack": "Stinger strikes. " + n("Threads of Vibration") + ": his attacks, the boulder and Impale stack Quaking on "
                  "champions; at {p_n} they take {p_pct}% max health a second for " + t("{p_t}s") + ". " +
                  n("Seismic Bastion") + ": when his charge stops he gains a " + phys("w_sh", "w_sh_r") + " shield for " +
                  t("{w_sh_t}s") + " and quakes the ground for " + phys("w_dmg", "w_ratio") + ", " + cc("slowing") +
                  " {w_slow}%.",
        "skill": "Rips up a boulder for " + t("{q_t}s") + ": +{q_as}% attack speed, his next 3 attacks splash " +
                 phys("q_dmg", "q_ratio") + ", the third {q_hp}% max health more and " + cc("slows") + " {q_slow}%. Held " +
                 t("{q_hold}s") + ", it is thrown (" + n("Upheaval") + "): " + phys("q_toss_dmg", "q_toss_ratio") +
                 " + {q_hp}% max health.",
        "skill2": "Charges an enemy champion and carries it along; when the charge stops it takes " + phys("e_dmg", "e_ratio") +
                  " physical damage and is " + cc("stunned") + " for " + t("{e_stun}s") + ".",
        "ult": "His three tails lash forward: enemy champions on the line take " + phys("r_dmg", "r_ratio") +
               " physical damage, are " + cc("suppressed") + " for " + t("{r_sup}s") + " and dragged along beside him; on a "
               "hit he gains {r_ms}% move speed for " + t("{r_ms_t}s") + ".",
        "names": ("Shattered Earth", "Ixtal's Impact", "Impale"),
    },
    "ko": {
        "name": "스카너",
        "attack": "독침 공격. " + n("진동의 가닥") + ": 기본 공격, 바위, 꿰뚫기가 챔피언에게 진동 중첩, {p_n}중첩이면 " + t("{p_t}초") +
                  " 동안 매초 최대 체력 {p_pct}% 피해. " + n("대지의 수호자") + ": 돌진이 멈추면 " + phys("w_sh", "w_sh_r") +
                  " 보호막 " + t("{w_sh_t}초") + ", 주변에 " + phys("w_dmg", "w_ratio") + " 피해, {w_slow}% " + cc("둔화") + ".",
        "skill": "바위를 " + t("{q_t}초") + " 들어 올림: 공격 속도 +{q_as}%, 다음 기본 공격 3회가 " + phys("q_dmg", "q_ratio") +
                 " 범위 피해, 3번째는 최대 체력 {q_hp}% 추가와 {q_slow}% " + cc("둔화") + ". " + t("{q_hold}초") + " 들고 있으면 던짐(" +
                 n("지반 돌출") + "): " + phys("q_toss_dmg", "q_toss_ratio") + " + 최대 체력 {q_hp}%.",
        "skill2": "적 챔피언에게 돌진해 끌고 감; 돌진이 멈추면 " + phys("e_dmg", "e_ratio") + " 물리 피해와 " + t("{e_stun}초") + " " +
                  cc("기절") + ".",
        "ult": "세 꼬리로 앞을 꿰뚫음: 직선 위 적 챔피언에게 " + phys("r_dmg", "r_ratio") + " 물리 피해, " + t("{r_sup}초") + " " +
               cc("제압") + "하고 곁으로 끌고 다님; 적중하면 이동 속도 +{r_ms}% " + t("{r_ms_t}초") + ".",
        "names": ("부서진 대지", "이쉬탈의 격돌", "꿰뚫기"),
    },
    "ja": {
        "name": "スカーナー",
        "attack": "毒針で攻撃。" + n("響振動") + "：通常攻撃・岩・インペイルがチャンピオンに振動を付与、{p_n}スタックで" + t("{p_t}秒") +
                  "間毎秒最大体力{p_pct}%のダメージ。" + n("激震の砦") + "：突進が止まるとシールド" + phys("w_sh", "w_sh_r") +
                  "を" + t("{w_sh_t}秒") + "得て周囲に" + phys("w_dmg", "w_ratio") + "、{w_slow}%" + cc("スロウ") + "。",
        "skill": "岩を" + t("{q_t}秒") + "掲げる：攻撃速度+{q_as}%、次の通常攻撃3回が" + phys("q_dmg", "q_ratio") + "の範囲ダメージ、"
                 "3回目は最大体力{q_hp}%追加と{q_slow}%" + cc("スロウ") + "。" + t("{q_hold}秒") + "持つと投げる（" + n("大地の怒り") +
                 "）：" + phys("q_toss_dmg", "q_toss_ratio") + "+最大体力{q_hp}%。",
        "skill2": "敵チャンピオンに突進して引きずる；止まると" + phys("e_dmg", "e_ratio") + "の物理ダメージと" + t("{e_stun}秒") +
                  cc("スタン") + "。",
        "ult": "三本の尾で前方を貫く：直線上の敵チャンピオンに" + phys("r_dmg", "r_ratio") + "の物理ダメージ、" + t("{r_sup}秒") +
               cc("サプレッション") + "して引きずる；命中すると移動速度+{r_ms}%を" + t("{r_ms_t}秒") + "。",
        "names": ("砕けし大地", "イシュタルの衝動", "インペイル"),
    },
}

C = "league_skarner_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the impacts loud, the voice as the other heroes'
SOUNDS = {f"league_skarner_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.55), ("q", 0.65), ("q_hit", 0.7), ("q_toss", 0.6), ("q_land", 0.75), ("w", 0.75),
    ("e", 0.6), ("e_hit", 0.6), ("e_slam", 0.75), ("r", 0.8), ("r_hit", 0.75), ("p_burst", 0.55),
    ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_n", "p_pct", "w_sh", "w_sh_r", "w_dmg", "w_ratio", "w_slow", "q_as", "q_dmg", "q_ratio",
                           "q_hp", "q_slow", "q_toss_dmg", "q_toss_ratio", "e_dmg", "e_ratio", "r_dmg", "r_ratio", "r_ms")}
    assert p["p_p"] == 60, "the texts say Quaking burns every second"
    for k in ("p_t", "w_sh_t", "q_t", "q_hold", "e_stun", "r_sup", "r_ms_t"):
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
    ap.add_argument("--face", help="X,Y (x ahead of the pivot, y up from the feet)")
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
    if "Skarner" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Skarner. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
