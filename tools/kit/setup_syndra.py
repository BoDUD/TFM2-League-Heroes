"""Syndra's text (5 languages), sound_info files and her keys in the shared files, numbers from build_syndra.P.

    python tools/kit/setup_syndra.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_syndra in every language, description + skill_name),
sound/sfx/league_syndra_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (VERSION, Syndra named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (辛德拉 / 暗黑元首 - the name and title slots are swapped there, as for Viktor;
卓尔不凡, 暗黑法球, 驱使念力, 弱者退散, 能量倾泻) and Data Dragon 16.20.1 (zh_TW 星朵拉 / 黑暗領主, 卓越, 黑暗星體, 意志之力,
虛弱潰散, 超能解放; ko 신드라 / 어둠의 여제, 초월, 어둠 구체, 의지의 힘, 적군 와해, 풀려난 힘; ja シンドラ / 暗黒の女王,
絶大なる魔力, ダークスフィア, ダークフォース, 闇の波導, 魔力の奔流). skill2 is named after E (Scatter the Weak; the icon
is E's), W in the text. No combo line in the texts (the pros' QE lives in the kit and the README).
No `league_syndra_attack` sound: the engine would play it at the start of every attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_syndra import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_syndra"
VERSION = "0.91.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
Wh = "<#ffffffff>"     # true damage
E = "<>"
# champion_view: set from tfm2_ase.py face once the sprite is in (run with --face / --banpick)
VIEW = {"face": {"x": 0, "y": -30}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "辛德拉",
        "attack": "被动" + O + "卓尔不凡" + E + "：" + A + "{lv_q}" + E + "级Q对英雄伤害+{q_champ}%，" + A + "{lv_w}" + E + "级W附带" +
                  Wh + "{w_true}%真实伤害" + E + "，" + A + "{lv_e}" + E + "级E范围更大，" + A + "{lv_r}" + E + "级R的法球无视魔抗。",
        "skill": "召唤暗黑法球，对周围敌人造成" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "。法球留在原地" + A + "{orb_t}秒" +
                 E + "。",
        "skill2": "先用" + O + "驱使念力" + E + "把法球掷向敌方英雄，造成" + mag("w_dmg", "w_ratio") + M + "魔法伤害" + E + "并" + R +
                  "减速{w_slow}%" + E + "。再锥形击退敌人，造成" + mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "，被推开的法球使附近敌人" +
                  R + "晕眩{e_stun}秒" + E + "。",
        "ult": "向一名敌方英雄发射" + A + "3颗+场上法球数" + E + "（最多7颗），每颗造成" + mag("r_dmg", "r_ratio") + M + "魔法伤害" +
               E + "。",
        "names": ("暗黑法球", "弱者退散", "能量倾泻"),
    },
    "zh-hant": {
        "name": "星朵拉",
        "attack": "被動" + O + "卓越" + E + "：" + A + "{lv_q}" + E + "級Q對英雄傷害+{q_champ}%，" + A + "{lv_w}" + E + "級W附帶" + Wh +
                  "{w_true}%真實傷害" + E + "，" + A + "{lv_e}" + E + "級E範圍更大，" + A + "{lv_r}" + E + "級R的星體無視魔抗。",
        "skill": "召喚黑暗星體，對周圍敵人造成" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "。星體留在原地" + A + "{orb_t}秒" +
                 E + "。",
        "skill2": "先用" + O + "意志之力" + E + "把星體擲向敵方英雄，造成" + mag("w_dmg", "w_ratio") + M + "魔法傷害" + E + "並" + R +
                  "緩速{w_slow}%" + E + "。再錐形擊退敵人，造成" + mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "，被推開的星體使附近敵人" +
                  R + "暈眩{e_stun}秒" + E + "。",
        "ult": "向一名敵方英雄發射" + A + "3顆+場上星體數" + E + "（最多7顆），每顆造成" + mag("r_dmg", "r_ratio") + M + "魔法傷害" +
               E + "。",
        "names": ("黑暗星體", "虛弱潰散", "超能解放"),
    },
    "en": {
        "name": "Syndra",
        "attack": "Passive " + O + "Transcendent" + E + ": at level " + A + "{lv_q}" + E + " Dark Sphere deals {q_champ}% more to "
                  "champions, at " + A + "{lv_w}" + E + " Force of Will adds " + Wh + "{w_true}% true damage" + E + ", at " + A +
                  "{lv_e}" + E + " Scatter the Weak grows, at " + A + "{lv_r}" + E + " Unleashed Power ignores Magic Resist.",
        "skill": "A Dark Sphere deals " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " around it and stays for " + A +
                 "{orb_t}s" + E + ".",
        "skill2": "First " + O + "Force of Will" + E + " throws a sphere at an enemy champion for " + mag("w_dmg", "w_ratio") + " " + M +
                  "magic damage" + E + ", " + R + "slowing {w_slow}%" + E + ". Then a cone deals " + mag("e_dmg", "e_ratio") + " " + M +
                  "magic damage" + E + " and knocks enemies back; spheres pushed " + R + "stun" + E + " enemies near them for " + A +
                  "{e_stun}s" + E + ".",
        "ult": "Fires " + A + "3 + her spheres" + E + " (up to 7) at an enemy champion, each dealing " + mag("r_dmg", "r_ratio") + " " +
               M + "magic damage" + E + ".",
        "names": ("Dark Sphere", "Scatter the Weak", "Unleashed Power"),
    },
    "ko": {
        "name": "신드라",
        "attack": "기본 지속 효과 " + O + "초월" + E + ": " + A + "{lv_q}" + E + "레벨 Q 챔피언 피해 +{q_champ}%, " + A + "{lv_w}" + E +
                  "레벨 W " + Wh + "고정 피해 {w_true}%" + E + " 추가, " + A + "{lv_e}" + E + "레벨 E 범위 증가, " + A + "{lv_r}" + E +
                  "레벨 R 구체가 마법 저항력 무시.",
        "skill": "어둠 구체가 주변 적에게 " + mag("q_dmg", "q_ratio") + "의 " + M + "마법 피해" + E + ". 구체는 " + A + "{orb_t}초" + E +
                 " 동안 남음.",
        "skill2": "먼저 " + O + "의지의 힘" + E + "으로 적 챔피언에게 구체를 던져 " + mag("w_dmg", "w_ratio") + "의 " + M + "마법 피해" +
                  E + ", " + R + "{w_slow}% 둔화" + E + ". 이어서 부채꼴로 " + mag("e_dmg", "e_ratio") + "의 " + M + "마법 피해" + E +
                  "와 밀쳐내기, 밀려난 구체 주변 적 " + R + "기절 {e_stun}초" + E + ".",
        "ult": "적 챔피언 하나에게 " + A + "구체 3개 + 남은 구체 수" + E + "(최대 7개) 발사, 개당 " + mag("r_dmg", "r_ratio") + "의 " + M +
               "마법 피해" + E + ".",
        "names": ("어둠 구체", "적군 와해", "풀려난 힘"),
    },
    "ja": {
        "name": "シンドラ",
        "attack": "パッシブ " + O + "絶大なる魔力" + E + "：" + A + "{lv_q}" + E + "レベルでQのチャンピオンへのダメージ+{q_champ}%、" + A +
                  "{lv_w}" + E + "レベルでWに" + Wh + "{w_true}%確定ダメージ" + E + "、" + A + "{lv_e}" + E + "レベルでE拡大、" + A +
                  "{lv_r}" + E + "レベルでRが魔法防御無視。",
        "skill": "ダークスフィアが周囲の敵に" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "。スフィアは" + A +
                 "{orb_t}秒" + E + "残る。",
        "skill2": "まず" + O + "ダークフォース" + E + "でスフィアを敵チャンピオンに投げ" + mag("w_dmg", "w_ratio") + "の" + M +
                  "魔法ダメージ" + E + "と" + R + "{w_slow}%スロウ" + E + "。続けて扇状に" + mag("e_dmg", "e_ratio") + "の" + M +
                  "魔法ダメージ" + E + "とノックバック、押されたスフィアが周囲の敵を" + R + "{e_stun}秒スタン" + E + "。",
        "ult": "敵チャンピオン1体に" + A + "3個+残りのスフィア" + E + "（最大7個）を放ち、1個ごとに" + mag("r_dmg", "r_ratio") + "の" + M +
               "魔法ダメージ" + E + "。",
        "names": ("ダークスフィア", "闇の波導", "魔力の奔流"),
    },
}

C = "league_syndra_sfx_"
V = "league_syndra_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_syndra_shot": [(C + "shot", 0.4, 0.0)],
    "league_syndra_hit": [(C + "hit", 0.35, 0.0)],
    "league_syndra_q_cast": [(C + "q_cast", 0.5, 0.0)],
    "league_syndra_q_blast": [(C + "q_blast", 0.55, 0.0)],
    "league_syndra_w_grab": [(C + "w_grab", 0.5, 0.0)],
    "league_syndra_w_throw": [(C + "w_throw", 0.5, 0.0)],
    "league_syndra_w_land": [(C + "w_land", 0.55, 0.0)],
    "league_syndra_e_cast": [(C + "e_cast", 0.55, 0.0)],
    "league_syndra_e_push": [(C + "e_push", 0.45, 0.0)],
    "league_syndra_e_stun": [(C + "e_stun", 0.5, 0.0)],
    "league_syndra_r_cast": [(C + "r_cast", 0.55, 0.0)],
    "league_syndra_r_launch": [(C + "r_launch", 0.35, 0.0)],
    "league_syndra_r_hit": [(C + "r_hit", 0.45, 0.0)],
    "league_syndra_evo": [(C + "evo", 0.55, 0.0)],
    "league_syndra_vo_q": [(V + "q", 0.85, 0.0)],
    "league_syndra_vo_w": [(V + "w", 0.85, 0.0)],
    "league_syndra_vo_e": [(V + "e", 0.85, 0.0)],
    "league_syndra_vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def values(p):
    v = {k: p[k] for k in ("lv_q", "lv_w", "lv_e", "lv_r", "q_champ", "w_true", "q_dmg", "q_ratio", "w_dmg", "w_ratio",
                           "w_slow", "e_dmg", "e_ratio", "r_dmg", "r_ratio")}
    for k in ("orb_t", "e_stun"):
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
    if "Syndra" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Syndra. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
