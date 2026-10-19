"""Vex's text (5 languages), sound_info files and her keys in the shared files, numbers from build_vex.P.

    python tools/kit/setup_vex.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_vex in every language, description + skill_name),
sound/sfx/league_vex_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Vex named). Only her keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 薇古丝 (愁云使者): 终焉暮气, 寒心波云, 生人勿近, 溟濛渐染, 愁煞; zh_TW 薇可絲 (愁霧影巫):
無望厄障, 冷酷暗箭, 個人舒適圈, 闇黑迫近, 飛影急襲; ja ヴェックス: フコウとユーウツ, 無気力ショット, パーソナルスペース, ヤミとばし,
影法師; ko 벡스: 파멸과 우울, 안개 화살, 거리 두기, 커지는 어둠, 그림자 파동.
Slots: skill = Q Mistral Bolt, skill2 = E Looming Darkness, ult = R Shadow Surge; the passive Doom 'n Gloom and W
Personal Space are in the attack's text. No combo sentence in any text (the user's rule). The main pack's rules are the
ones written; the add-on league_vex (a real Gloom on each enemy, dashes marked, R back on a kill) says so itself.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_vex import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_vex"
VERSION = "0.174.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
E = "<>"
# champion_view: provisional until the sprite (tfm2_ase.py face)
VIEW = {"face": {"x": 1, "y": -24}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def sh(a, r):
    return f"{G}{{{a}}}{E} + {APi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "薇古丝",
        "attack": "射出暗影弹。" + O + "终焉暮气" + E + "：每" + A + "{p_cd}秒" + E + "下一个技能" + R + "恐惧" + E + "命中的敌人" + A + "{p_fear}秒" +
                  E + "。" + O + "生人勿近" + E + "：敌方英雄靠近时改为获得" + sh("w_sh", "w_sh_ratio") + "护盾并震伤周围" +
                  mag("w_dmg", "w_ratio") + "（每" + A + "{w_cd}秒" + E + "）。",
        "skill": "射出一道暗风，穿过路径上的所有敌人，造成" + mag("q_dmg", "q_ratio") + "魔法伤害。",
        "skill2": "影子飞到目标处扩散，造成" + mag("e_dmg", "e_ratio") + "魔法伤害、减速{e_slow}%" + A + "{e_slow_t}秒" + E + "，并施加" + O +
                  "暮气" + E + "：她下一次技能打中带暮气的英雄额外造成" + mag("g_dmg", "g_ratio") + "魔法伤害。",
        "ult": "射出飞弹标记一名敌方英雄，造成" + mag("r_dmg", "r_ratio") + "魔法伤害，随后冲到他身边再造成" + mag("r2_dmg", "r2_ratio") +
               "魔法伤害。",
        "names": ("寒心波云", "溟濛渐染", "愁煞"),
    },
    "zh-hant": {
        "name": "薇可絲",
        "attack": "射出暗影彈。" + O + "無望厄障" + E + "：每" + A + "{p_cd}秒" + E + "下一個技能" + R + "恐懼" + E + "命中的敵人" + A + "{p_fear}秒" +
                  E + "。" + O + "個人舒適圈" + E + "：敵方英雄靠近時改為獲得" + sh("w_sh", "w_sh_ratio") + "護盾並震傷周圍" +
                  mag("w_dmg", "w_ratio") + "（每" + A + "{w_cd}秒" + E + "）。",
        "skill": "射出一道暗風，穿過路徑上的所有敵人，造成" + mag("q_dmg", "q_ratio") + "魔法傷害。",
        "skill2": "影子飛到目標處擴散，造成" + mag("e_dmg", "e_ratio") + "魔法傷害、緩速{e_slow}%" + A + "{e_slow_t}秒" + E + "，並施加" + O +
                  "陰霾" + E + "：她下一次技能打中帶陰霾的英雄額外造成" + mag("g_dmg", "g_ratio") + "魔法傷害。",
        "ult": "射出飛彈標記一名敵方英雄，造成" + mag("r_dmg", "r_ratio") + "魔法傷害，隨後衝到他身邊再造成" + mag("r2_dmg", "r2_ratio") +
               "魔法傷害。",
        "names": ("冷酷暗箭", "闇黑迫近", "飛影急襲"),
    },
    "en": {
        "name": "Vex",
        "attack": "Fires a shadow bolt. " + O + "Doom" + E + ": every " + A + "{p_cd}s" + E + " her next spell " + R + "fears" + E +
                  " the enemies hit for " + A + "{p_fear}s" + E + ". " + O + "Personal Space" + E + ": with an enemy champion close, "
                  "she instead gains a " + sh("w_sh", "w_sh_ratio") + " shield and blasts the enemies around her for " +
                  mag("w_dmg", "w_ratio") + " " + M + "magic damage" + E + " (every " + A + "{w_cd}s" + E + ").",
        "skill": "Sends a gust of shadow through every enemy in a line for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" +
                 E + ".",
        "skill2": "Her Shadow flies to the target and spreads: " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E +
                  ", slowed {e_slow}% for " + A + "{e_slow_t}s" + E + ", and " + O + "Gloom" + E + ": her next spell hit on a "
                  "Gloomed champion deals " + mag("g_dmg", "g_ratio") + " more.",
        "ult": "Fires a missile that marks an enemy champion for " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E +
               ", then surges to it for " + mag("r2_dmg", "r2_ratio") + " more.",
        "names": ("Mistral Bolt", "Looming Darkness", "Shadow Surge"),
    },
    "ko": {
        "name": "벡스",
        "attack": "그림자 탄을 쏜다. " + O + "파멸" + E + ": " + A + "{p_cd}초" + E + "마다 다음 스킬이 맞힌 적을 " + A + "{p_fear}초" + E +
                  " " + R + "공포" + E + ". " + O + "거리 두기" + E + ": 적 챔피언이 가까우면 대신 " + sh("w_sh", "w_sh_ratio") +
                  " 보호막을 얻고 주변에 " + mag("w_dmg", "w_ratio") + " 마법 피해(" + A + "{w_cd}초" + E + "마다).",
        "skill": "직선상의 모든 적을 꿰뚫는 그림자 바람으로 " + mag("q_dmg", "q_ratio") + " 마법 피해.",
        "skill2": "그림자가 대상 위치로 날아가 퍼지며 " + mag("e_dmg", "e_ratio") + " 마법 피해, " + A + "{e_slow_t}초" + E +
                  " {e_slow}% 둔화, " + O + "우울" + E + " 부여: 우울한 챔피언에게 다음 스킬이 적중하면 " + mag("g_dmg", "g_ratio") +
                  " 추가 피해.",
        "ult": "투사체로 적 챔피언을 표식해 " + mag("r_dmg", "r_ratio") + " 마법 피해, 이어서 돌진해 " + mag("r2_dmg", "r2_ratio") +
               " 마법 피해.",
        "names": ("안개 화살", "커지는 어둠", "그림자 파동"),
    },
    "ja": {
        "name": "ヴェックス",
        "attack": "影の弾を撃つ。" + O + "フコウ" + E + "：" + A + "{p_cd}秒" + E + "ごとに次のスキルが当たった敵を" + A + "{p_fear}秒" + E + R +
                  "恐怖" + E + "。" + O + "パーソナルスペース" + E + "：敵チャンピオンが近いと代わりに" + sh("w_sh", "w_sh_ratio") +
                  "のシールドを得て周囲に" + mag("w_dmg", "w_ratio") + "の魔法ダメージ（" + A + "{w_cd}秒" + E + "ごと）。",
        "skill": "直線上の全ての敵を貫く影の風で" + mag("q_dmg", "q_ratio") + "の魔法ダメージ。",
        "skill2": "影が目標地点へ飛んで広がり、" + mag("e_dmg", "e_ratio") + "の魔法ダメージ、" + A + "{e_slow_t}秒" + E +
                  "{e_slow}%スロウ、" + O + "ユーウツ" + E + "付与：ユーウツのチャンピオンに次のスキルが当たると" +
                  mag("g_dmg", "g_ratio") + "追加。",
        "ult": "弾で敵チャンピオンにマークをつけ" + mag("r_dmg", "r_ratio") + "の魔法ダメージ、続いて突進して" +
               mag("r2_dmg", "r2_ratio") + "の魔法ダメージ。",
        "names": ("無気力ショット", "ヤミとばし", "影法師"),
    },
}

C = "league_vex_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {f"league_vex_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.3), ("a_hit", 0.35), ("w", 0.45), ("w_hit", 0.4), ("q", 0.4), ("q_fly", 0.4), ("q_hit", 0.45),
    ("e", 0.4), ("e_land", 0.5), ("e_hit", 0.35), ("g_pop", 0.5), ("p_ready", 0.4), ("p_fear", 0.45),
    ("r", 0.45), ("r_fly", 0.4), ("r_mark", 0.45), ("r_dash", 0.45), ("r_hit", 0.55),
    ("vo_q", 0.85), ("vo_e", 0.85), ("vo_w", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("w_sh", "w_sh_ratio", "w_dmg", "w_ratio", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "e_slow",
                           "g_dmg", "g_ratio", "r_dmg", "r_ratio", "r2_dmg", "r2_ratio")}
    for k in ("p_cd", "p_fear", "w_cd", "e_slow_t"):
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
    if "Vex" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Vex. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
