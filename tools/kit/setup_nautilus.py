"""Nautilus's text (5 languages), sound_info files and his keys in the shared files, numbers from build_nautilus.P.

    python tools/kit/setup_nautilus.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_nautilus in every language, description + skill_name),
sound/sfx/league_nautilus_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.94.0, Nautilus named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (诺提勒斯 / 深海泰坦; 排山倒海, 疏通航道, 泰坦之怒, 暗流涌动, 深海冲击; the client
swaps name and title) and Data Dragon 16.20.1 (zh_TW 納帝魯斯 / 沉重打擊 / 深淵鐵錨 / 巨人之怒 / 鋼鐵怒濤 / 潛航衝擊, ja
ノーチラス / 鉄の錨 / 錨投げ / 大海の激憤 / 粉砕水 / 爆雷発射, ko 노틸러스 / 강력한 일격 / 닻줄 견인 / 타이탄의 분노 / 역조 /
폭뢰). Slots: skill = Q, skill2 = W (Riptide, E, told in its text), ult = R; the passive is told in the attack's text.
No combo sentence in any text (the user's rule). No `league_nautilus_attack` sound: the engine would play it at the start
of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_nautilus import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_nautilus"
VERSION = "0.94.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
S = "<#9fd8ffff>"      # shields
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 2, "y": -18}, "center": {"x": 0, "y": -12}}


def mag(k):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_ratio}}%{E}"


SH = S + "{w_shield}" + E + " + " + APi + S + "{w_ap}%" + E

TEXT = {
    "zh-hans": {
        "name": "诺提勒斯",
        "attack": O + "排山倒海" + E + "：普攻敌方英雄时将其" + R + "禁锢{p_root}秒" + E + "，并额外造成" + mag("p") + M + "魔法伤害" + E +
                  "，之后" + A + "{p_cd}秒" + E + "内不再触发。",
        "skill": "抛出铁锚，钩中第一个敌方英雄，造成" + mag("q") + M + "魔法伤害" + E + "，并把双方拉向彼此。",
        "skill2": O + "泰坦之怒" + E + "：获得" + SH + S + "护盾" + E + "，" + A + "{w_t}秒" + E + "内普攻还会伤及目标周围的敌人" + mag("w") + "。" +
                  O + "暗流涌动" + E + "：地面震荡三波，周围敌人受到" + mag("e") + M + "魔法伤害" + E + "并" + R + "减速{e_slow}%" + E +
                  A + "{e_slow_t}秒" + E + "。",
        "ult": "对射程内一名敌方英雄发出深海冲击波：沿途敌人被" + R + "击飞" + E + "并受到" + mag("r_path") + "伤害；目标受到" + mag("r") + M +
               "魔法伤害" + E + "，" + R + "击飞{r_up}秒后眩晕{r_stun}秒" + E + "。",
        "names": ("疏通航道", "泰坦之怒", "深海冲击"),
    },
    "zh-hant": {
        "name": "納帝魯斯",
        "attack": O + "沉重打擊" + E + "：普攻敵方英雄時將其" + R + "定身{p_root}秒" + E + "，並額外造成" + mag("p") + M + "魔法傷害" + E +
                  "，之後" + A + "{p_cd}秒" + E + "內不再觸發。",
        "skill": "拋出鐵錨，鉤中第一個敵方英雄，造成" + mag("q") + M + "魔法傷害" + E + "，並把雙方拉向彼此。",
        "skill2": O + "巨人之怒" + E + "：獲得" + SH + S + "護盾" + E + "，" + A + "{w_t}秒" + E + "內普攻還會傷及目標周圍的敵人" + mag("w") + "。" +
                  O + "鋼鐵怒濤" + E + "：地面震盪三波，周圍敵人受到" + mag("e") + M + "魔法傷害" + E + "並" + R + "緩速{e_slow}%" + E +
                  A + "{e_slow_t}秒" + E + "。",
        "ult": "對射程內一名敵方英雄發出衝擊波：沿途敵人被" + R + "擊飛" + E + "並受到" + mag("r_path") + "傷害；目標受到" + mag("r") + M +
               "魔法傷害" + E + "，" + R + "擊飛{r_up}秒後暈眩{r_stun}秒" + E + "。",
        "names": ("深淵鐵錨", "巨人之怒", "潛航衝擊"),
    },
    "en": {
        "name": "Nautilus",
        "attack": O + "Staggering Blow" + E + ": his attack on an enemy champion " + R + "roots it {p_root}s" + E + " and deals " + mag("p") +
                  " " + M + "magic damage" + E + " more, then rests " + A + "{p_cd}s" + E + ".",
        "skill": "Throws his anchor at the first enemy champion: " + mag("q") + " " + M + "magic damage" + E + ", and the two are pulled "
                 "toward each other.",
        "skill2": O + "Titan's Wrath" + E + ": a " + SH + " " + S + "shield" + E + "; for " + A + "{w_t}s" + E + " his attacks also hit enemies "
                  "round the target for " + mag("w") + ". " + O + "Riptide" + E + ": three waves round him deal " + mag("e") + " " + M +
                  "magic damage" + E + " and " + R + "slow {e_slow}%" + E + " for " + A + "{e_slow_t}s" + E + ".",
        "ult": "Sends a shockwave at an enemy champion in range: enemies on its way are " + R + "knocked up" + E + " for " + mag("r_path") +
               "; the champion takes " + mag("r") + " " + M + "magic damage" + E + ", " + R + "airborne {r_up}s, then stunned {r_stun}s" + E + ".",
        "names": ("Dredge Line", "Titan's Wrath", "Depth Charge"),
    },
    "ko": {
        "name": "노틸러스",
        "attack": O + "강력한 일격" + E + ": 적 챔피언을 기본 공격하면 " + R + "{p_root}초 속박" + E + "하고 " + mag("p") + " " + M + "마법 피해" +
                  E + "를 추가로 입힘. 이후 " + A + "{p_cd}초" + E + " 동안 발동하지 않음.",
        "skill": "닻을 던져 처음 맞은 적 챔피언에게 " + mag("q") + " " + M + "마법 피해" + E + "를 입히고 서로를 끌어당김.",
        "skill2": O + "타이탄의 분노" + E + ": " + SH + " " + S + "보호막" + E + ", " + A + "{w_t}초" + E + " 동안 기본 공격이 대상 주변 적에게도 " +
                  mag("w") + " 피해. " + O + "역조" + E + ": 주변에 세 번 파동, " + mag("e") + " " + M + "마법 피해" + E + "와 " + A +
                  "{e_slow_t}초" + E + " " + R + "{e_slow}% 둔화" + E + ".",
        "ult": "사거리 내 적 챔피언에게 충격파: 경로의 적은 " + R + "공중에 뜨고" + E + " " + mag("r_path") + " 피해, 대상은 " + mag("r") + " " +
               M + "마법 피해" + E + "와 " + R + "{r_up}초 에어본 후 {r_stun}초 기절" + E + ".",
        "names": ("닻줄 견인", "타이탄의 분노", "폭뢰"),
    },
    "ja": {
        "name": "ノーチラス",
        "attack": O + "鉄の錨" + E + "：敵チャンピオンへの通常攻撃で" + R + "{p_root}秒スネア" + E + "し、" + mag("p") + "の" + M + "魔法ダメージ" +
                  E + "を追加。その後" + A + "{p_cd}秒" + E + "は発動しない。",
        "skill": "錨を投げ、最初に当たった敵チャンピオンに" + mag("q") + "の" + M + "魔法ダメージ" + E + "、互いを引き寄せる。",
        "skill2": O + "大海の激憤" + E + "：" + SH + "の" + S + "シールド" + E + "、" + A + "{w_t}秒" + E + "間通常攻撃が対象周囲の敵にも" +
                  mag("w") + "。" + O + "粉砕水" + E + "：周囲に3回の波、" + mag("e") + "の" + M + "魔法ダメージ" + E + "と" + A +
                  "{e_slow_t}秒" + E + R + "{e_slow}%スロウ" + E + "。",
        "ult": "射程内の敵チャンピオンへ衝撃波：通り道の敵は" + R + "ノックアップ" + E + "し" + mag("r_path") + "、対象は" + mag("r") + "の" + M +
               "魔法ダメージ" + E + "、" + R + "{r_up}秒打ち上げ後{r_stun}秒スタン" + E + "。",
        "names": ("錨投げ", "大海の激憤", "爆雷発射"),
    },
}

C = "league_nautilus_sfx_"
S_ = "league_nautilus_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + c, vol, dl)] for k, c, vol, dl in [
    ("a_swing", "a_swing", 0.45, 0.0), ("a_hit", "a_hit", 0.4, 0.0), ("p", "p", 0.5, 0.0), ("q", "q", 0.5, 0.0),
    ("q_fly", "q_fly", 0.45, 0.0), ("q_hit", "q_hit", 0.55, 0.0), ("q_wall", "q_wall", 0.55, 0.0), ("w", "w", 0.5, 0.0),
    ("e", "e", 0.6, 0.0), ("e_hit", "a_hit", 0.3, 0.0), ("r", "r", 0.55, 0.0), ("r_wave", "r_wave", 0.55, 0.0),
    ("r_hit", "r_hit", 0.6, 0.0), ("vo_q", "vo_q", 0.85, 0.0), ("vo_e", "vo_e", 0.85, 0.0), ("vo_r", "vo_r", 0.9, 0.0)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ratio", "q_dmg", "q_ratio", "w_shield", "w_ap", "w_dmg", "w_ratio", "e_dmg",
                           "e_ratio", "e_slow", "r_dmg", "r_ratio", "r_path_dmg", "r_path_ratio")}
    v.update({k: secs(p[k]) for k in ("p_root", "p_cd", "w_t", "e_slow_t", "r_up", "r_stun")})
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
    if "Nautilus" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Nautilus. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
