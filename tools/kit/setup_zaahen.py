"""Zaahen's text (5 languages), sound_info files and their keys in the shared files, numbers from build_zaahen.P
(setup_skarner.py's way).

    python tools/kit/setup_zaahen.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_zaahen in every language, description + skill_name),
sound/sfx/league_zaahen_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Zaahen named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 亚恒 (不落魔锋): 不落之志; 暗裔长刀, 厄影回锋, 赤金突袭, 大赦; zh_TW 薩亨: 邪心修真;
冥血大刀, 冥厄鉤鐮, 偃月天衝, 冥聖裁決; ja ザーヘン: 戦威修養; ダーキングレイヴ, 戦慄の再臨, 絢爛たる進撃, 無慈悲なる裁き; ko 자헨:
전쟁 단련; 다르킨의 글레이브, 공포의 귀환, 찬란한 쇄도, 단호한 판결.
Slots: skill = The Darkin Glaive (its recast's uppercut in the same text), skill2 = Dreaded Return (Aureate Rush's spin
folded in: said in its text), ult = Grim Deliverance (its passive armour penetration said there); Cultivation of War in
the attack's text. The texts say the main pack's rules (the add-on's copy has its own: addons/league_zaahen/
make_override.py). No combo sentence in any text (the user's rule: the combos are the README's).
champion_view's face is his crown under the horns (text-audio.md: base heroes' face points sit at the crown), measured
up from the feet on hd/idle.png (the circlet's top at row 13 of 84, 71 rows = 41 game px at PPU 1.75; the head's
middle column 55.5 against the standing column 54: 1 px ahead) - tfm2_ase.py face took the glaive's blade tip, high on
the image left, for a crown.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_zaahen import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_zaahen"
VERSION = "0.228.0"     # above main 0.227.0 (#550 Skarner), 2026-10-26
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7ae582ff>"      # heals, shields
E = "<>"
VIEW = {"face": {"x": 1, "y": -41}, "center": {"x": 0, "y": -12}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def heal(d, r):
    return f"{G}{{{d}}}{E} + {ADi}{G}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


TEXT = {
    "zh-hans": {
        "name": "亚恒",
        "attack": "长刀横扫。" + n("不落之志") + "：打中英雄叠果决，每层攻击力+{det_ad}%，叠满{det_n}层攻击力+{full_ad}%并得" +
                  heal("rv_sh", "rv_sh_r") + "护盾（每" + t("{rv_cd}秒") + "一次）；" + t("{det_t}秒") + "没打中英雄就清空。",
        "skill": "两连斩，每斩" + phys("q_dmg", "q_ratio") + "物理伤害、打中英雄回复" + heal("q_heal", "q_heal_r") + "（别的单位一半）。" +
                 t("{q_win}秒") + "内再按：上挑造成" + phys("q3_dmg", "q3_ratio") + "并" + cc("击飞") + t("{q_air}秒") + "。",
        "skill2": "往前刺出长刀：沿途敌人受到" + phys("w_dmg", "w_ratio") + "物理伤害、" + cc("晕眩") + t("{w_stun}秒") +
                  "并被拽回身边；接着" + n("赤金突袭") + "绕身一斩，" + phys("e_dmg", "e_ratio") + "。",
        "ult": "展翼升空（免控、受到伤害-{r_dr}%），冲向敌方英雄插刀落地：周围敌人受到" + phys("r_dmg", "r_ratio") +
               "物理伤害，每打中一个英雄回复" + heal("r_heal", "r_heal_r") + "。被动：攻击无视{r_pen}%护甲。",
        "names": ("暗裔长刀", "厄影回锋", "大赦"),
    },
    "zh-hant": {
        "name": "薩亨",
        "attack": "長刀橫掃。" + n("邪心修真") + "：打中英雄疊決心，每層攻擊力+{det_ad}%，疊滿{det_n}層攻擊力+{full_ad}%並得" +
                  heal("rv_sh", "rv_sh_r") + "護盾（每" + t("{rv_cd}秒") + "一次）；" + t("{det_t}秒") + "沒打中英雄就清空。",
        "skill": "兩連斬，每斬" + phys("q_dmg", "q_ratio") + "物理傷害、打中英雄回復" + heal("q_heal", "q_heal_r") + "（其他單位一半）。" +
                 t("{q_win}秒") + "內再按：上挑造成" + phys("q3_dmg", "q3_ratio") + "並" + cc("擊飛") + t("{q_air}秒") + "。",
        "skill2": "往前刺出長刀：沿途敵人受到" + phys("w_dmg", "w_ratio") + "物理傷害、" + cc("暈眩") + t("{w_stun}秒") +
                  "並被拽回身邊；接著" + n("偃月天衝") + "繞身一斬，" + phys("e_dmg", "e_ratio") + "。",
        "ult": "展翼升空（免控、受到傷害-{r_dr}%），衝向敵方英雄插刀落地：周圍敵人受到" + phys("r_dmg", "r_ratio") +
               "物理傷害，每打中一個英雄回復" + heal("r_heal", "r_heal_r") + "。被動：攻擊無視{r_pen}%護甲。",
        "names": ("冥血大刀", "冥厄鉤鐮", "冥聖裁決"),
    },
    "en": {
        "name": "Zaahen",
        "attack": "Glaive sweeps. " + n("Cultivation of War") + ": hits on champions stack Determination, +{det_ad}% attack "
                  "each; at {det_n} stacks +{full_ad}% attack and a " + heal("rv_sh", "rv_sh_r") + " shield (once every " +
                  t("{rv_cd}s") + "); the stacks drop after " + t("{det_t}s") + " without a champion hit.",
        "skill": "Slashes twice, " + phys("q_dmg", "q_ratio") + " physical damage each, healing " + heal("q_heal", "q_heal_r") +
                 " per slash on a champion (half on other units). Recast within " + t("{q_win}s") + ": an uppercut for " +
                 phys("q3_dmg", "q3_ratio") + " that " + cc("knocks up") + " for " + t("{q_air}s") + ".",
        "skill2": "Stabs the glaive forward: enemies in its path take " + phys("w_dmg", "w_ratio") + " physical damage, are " +
                  cc("stunned") + " for " + t("{w_stun}s") + " and pulled to him; then " + n("Aureate Rush") +
                  " spins the glaive round him for " + phys("e_dmg", "e_ratio") + ".",
        "ult": "Rises on his wings (crowd-control immune, {r_dr}% less damage taken) and dives on an enemy champion, driving "
               "the glaive into the ground: enemies around take " + phys("r_dmg", "r_ratio") + " physical damage; he heals " +
               heal("r_heal", "r_heal_r") + " per champion hit. Passive: his hits ignore {r_pen}% armour.",
        "names": ("The Darkin Glaive", "Dreaded Return", "Grim Deliverance"),
    },
    "ko": {
        "name": "자헨",
        "attack": "글레이브 휩쓸기. " + n("전쟁 단련") + ": 챔피언 적중마다 결의 중첩, 중첩당 공격력 +{det_ad}%; {det_n}중첩이면 공격력 "
                  "+{full_ad}%와 " + heal("rv_sh", "rv_sh_r") + " 보호막(" + t("{rv_cd}초") + "마다); " + t("{det_t}초") +
                  " 동안 챔피언을 못 맞히면 사라짐.",
        "skill": "두 번 벰: 한 번에 " + phys("q_dmg", "q_ratio") + " 물리 피해, 챔피언 적중 시 " + heal("q_heal", "q_heal_r") +
                 " 회복(다른 유닛은 절반). " + t("{q_win}초") + " 안에 재사용: 올려 베기로 " + phys("q3_dmg", "q3_ratio") + " 피해와 " +
                 t("{q_air}초") + " " + cc("에어본") + ".",
        "skill2": "글레이브로 앞을 찌름: 경로의 적에게 " + phys("w_dmg", "w_ratio") + " 물리 피해, " + t("{w_stun}초") + " " +
                  cc("기절") + "시키고 끌어당김; 이어서 " + n("찬란한 쇄도") + "로 주변을 베어 " + phys("e_dmg", "e_ratio") + ".",
        "ult": "날개를 펴고 솟아올라(군중 제어 면역, 받는 피해 -{r_dr}%) 적 챔피언에게 내리꽂음: 주변 적에게 " + phys("r_dmg", "r_ratio") +
               " 물리 피해, 챔피언 적중마다 " + heal("r_heal", "r_heal_r") + " 회복. 기본 지속 효과: 방어구 {r_pen}% 관통.",
        "names": ("다르킨의 글레이브", "공포의 귀환", "단호한 판결"),
    },
    "ja": {
        "name": "ザーヘン",
        "attack": "グレイヴで薙ぎ払う。" + n("戦威修養") + "：チャンピオンへの命中で決意スタック、1スタック攻撃力+{det_ad}%；{det_n}スタックで"
                  "攻撃力+{full_ad}%とシールド" + heal("rv_sh", "rv_sh_r") + "（" + t("{rv_cd}秒") + "毎）；" + t("{det_t}秒") +
                  "命中がないと消える。",
        "skill": "2回斬る：1回" + phys("q_dmg", "q_ratio") + "の物理ダメージ、チャンピオン命中で" + heal("q_heal", "q_heal_r") +
                 "回復（他は半分）。" + t("{q_win}秒") + "内に再使用：斬り上げで" + phys("q3_dmg", "q3_ratio") + "と" + t("{q_air}秒") +
                 cc("ノックアップ") + "。",
        "skill2": "グレイヴを前方へ突き出す：通過した敵に" + phys("w_dmg", "w_ratio") + "の物理ダメージ、" + t("{w_stun}秒") +
                  cc("スタン") + "して引き寄せる；続けて" + n("絢爛たる進撃") + "で周囲を斬る、" + phys("e_dmg", "e_ratio") + "。",
        "ult": "翼を広げて舞い上がり（CC無効、被ダメージ-{r_dr}%）、敵チャンピオンへ降下して突き立てる：周囲の敵に" +
               phys("r_dmg", "r_ratio") + "の物理ダメージ、チャンピオン1体ごとに" + heal("r_heal", "r_heal_r") + "回復。"
               "自動効果：物理防御{r_pen}%貫通。",
        "names": ("ダーキングレイヴ", "戦慄の再臨", "無慈悲なる裁き"),
    },
}

C = "league_zaahen_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the impacts loud, the voice as the other heroes'
SOUNDS = {f"league_zaahen_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.55), ("q", 0.6), ("q_hit", 0.7), ("q2", 0.6), ("q_up", 0.75), ("w", 0.7), ("w_hit", 0.7),
    ("e", 0.6), ("e_hit", 0.65), ("r", 0.8), ("r_slam", 0.8), ("r_hit", 0.7), ("p_full", 0.6), ("rv", 0.75),
    ("vo_q", 0.85), ("vo_w", 0.85), ("vo_e", 0.85), ("vo_r", 0.9), ("vo_p", 0.85), ("vo_rv", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("det_ad", "det_n", "full_ad", "rv_sh", "rv_sh_r", "q_dmg", "q_ratio", "q3_dmg", "q3_ratio",
                           "w_dmg", "w_ratio", "e_dmg", "e_ratio", "r_dmg", "r_ratio", "r_heal", "r_heal_r", "r_dr", "r_pen")}
    v["q_heal"], v["q_heal_r"] = p["q_heal"], p["q_heal_r"]
    for k in ("rv_cd", "det_t", "q_win", "q_air", "w_stun"):
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
    if "Zaahen" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Zaahen. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
