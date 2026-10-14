"""Bard's text (5 languages), sound_info files and his keys in the shared files, numbers from build_bard.P.

    python tools/kit/setup_bard.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_bard in every language, description + skill_name),
sound/sfx/league_bard_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.108.0, Bard named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (巴德 / 星界游神; 旅者的召唤, 星界束缚, 游神圣坛, 神奇旅程, 调和命运; the client swaps name
and title) and Data Dragon 16.20.1 (zh_TW 巴德 / 旅者引領 / 宇宙制約 / 守望神龕 / 奇幻旅程 / 凝滯命域, ja バード / 旅人の呼び声 /
宇宙の法則 / 回復の遺物 / 精霊の旅路 / 運命の調律, ko 바드 / 방랑자의 부름 / 우주의 결속 / 수호자의 성소 / 신비한 차원문 / 운명의 소용돌이).
Slots: skill = Q, skill2 = W + E, ult = R; the passive (the Meeps) is told in the attack's text. No combo sentence in
any text (the user's rule). No `league_bard_attack` sound: the engine would play it at the start of every attack; the
attack plays its own from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_bard import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_bard"
VERSION = "0.108.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
G = "<#7cfc00ff>"      # heals
C = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face)
VIEW = {"face": {"x": 5, "y": -34}, "center": {"x": 0, "y": -12}}   # tfm2_ase face picked the bell-mouth: the crown is the mane's top over the mask


def mag(k):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_ap}}%{E}"


HEAL = G + "{w_heal}" + E + " + " + APi + G + "{w_ap}%" + E

TEXT = {
    "zh-hans": {
        "name": "巴德",
        "attack": "射出星光。被动" + O + "旅者的召唤" + E + "：每" + A + "{p_cd}秒" + E + "一只米普随攻击飞出，对目标周围的敌人造成" + mag("p") + M + "魔法伤害" + E +
                  "并" + C + "减速{p_slow}%" + E + "（" + A + "{p_slow_t}秒" + E + "）。",
        "skill": "射出星界能量，命中的第一个敌人受到" + mag("q") + M + "魔法伤害" + E + "并" + C + "减速{q_slow}%" + E + "；若其身后还有敌人，两者都受到伤害并" +
                 C + "眩晕{q_stun}秒" + E + "。",
        "skill2": O + "游神圣坛" + E + "：向交战中的友方英雄（或自己）投出圣坛，治疗" + HEAL + "，移速+{w_ms}%。" + O + "神奇旅程" + E + "：被敌人近身时开门，带身边的友方英雄远离，移速+{e_ms}%（" +
                  A + "{e_cd}秒" + E + "一次）。",
        "ult": "向聚在一起的敌方英雄（或被控制的友方英雄）投出金色法球，范围内所有单位（含友军、自己和防御塔）" + C + "时停{r_t}秒" + E + "：无法行动、无法被选中、不受伤害。",
        "names": ("星界束缚", "游神圣坛 / 神奇旅程", "调和命运"),
    },
    "zh-hant": {
        "name": "巴德",
        "attack": "射出星光。被動" + O + "旅者引領" + E + "：每" + A + "{p_cd}秒" + E + "一隻小精靈隨攻擊飛出，對目標周圍的敵人造成" + mag("p") + M + "魔法傷害" + E +
                  "並" + C + "緩速{p_slow}%" + E + "（" + A + "{p_slow_t}秒" + E + "）。",
        "skill": "射出星界能量，命中的第一個敵人受到" + mag("q") + M + "魔法傷害" + E + "並" + C + "緩速{q_slow}%" + E + "；若其身後還有敵人，兩者都受到傷害並" +
                 C + "暈眩{q_stun}秒" + E + "。",
        "skill2": O + "守望神龕" + E + "：向交戰中的友方英雄（或自己）投出神龕，治療" + HEAL + "，跑速+{w_ms}%。" + O + "奇幻旅程" + E + "：被敵人近身時開門，帶身邊的友方英雄遠離，跑速+{e_ms}%（" +
                  A + "{e_cd}秒" + E + "一次）。",
        "ult": "向聚在一起的敵方英雄（或被控制的友方英雄）投出金色法球，範圍內所有單位（含友軍、自己和防禦塔）" + C + "凝滯{r_t}秒" + E + "：無法行動、無法被選取、不受傷害。",
        "names": ("宇宙制約", "守望神龕 / 奇幻旅程", "凝滯命域"),
    },
    "en": {
        "name": "Bard",
        "attack": "Fires a star bolt. Passive " + O + "Traveler's Call" + E + ": every " + A + "{p_cd}s" + E + " a Meep flies with his attack, dealing " + mag("p") +
                  " " + M + "magic damage" + E + " to enemies around the target and " + C + "slowing them by {p_slow}%" + E + " for " + A + "{p_slow_t}s" + E + ".",
        "skill": "Fires a bolt of cosmic energy: the first enemy hit takes " + mag("q") + " " + M + "magic damage" + E + " and is " + C + "slowed by {q_slow}%" + E +
                 "; if another enemy is behind it, both take the damage and are " + C + "stunned for {q_stun}s" + E + ".",
        "skill2": O + "Caretaker's Shrine" + E + ": throws a shrine to an allied champion in a fight (or himself), healing " + HEAL + " and giving {w_ms}% move speed. " + O +
                  "Magical Journey" + E + ": when enemies close in, opens a door and takes nearby allied champions away with him, +{e_ms}% move speed (every " + A +
                  "{e_cd}s" + E + ").",
        "ult": "Lobs a golden orb at grouped enemy champions (or an allied champion in crowd control): every unit in the area, allies, Bard and turrets included, is put in " +
               C + "stasis for {r_t}s" + E + " - it cannot act, be targeted or be harmed.",
        "names": ("Cosmic Binding", "Caretaker's Shrine / Magical Journey", "Tempered Fate"),
    },
    "ko": {
        "name": "바드",
        "attack": "별빛을 쏩니다. 기본 지속 효과 " + O + "방랑자의 부름" + E + ": " + A + "{p_cd}초" + E + "마다 정령이 공격과 함께 날아가 대상 주변 적에게 " + mag("p") + " " + M +
                  "마법 피해" + E + "를 입히고 " + C + "{p_slow}% 둔화" + E + " (" + A + "{p_slow_t}초" + E + ").",
        "skill": "우주 에너지를 발사해 처음 맞은 적에게 " + mag("q") + " " + M + "마법 피해" + E + "와 " + C + "{q_slow}% 둔화" + E + "; 뒤에 다른 적이 있으면 둘 다 피해를 입고 " + C +
                 "{q_stun}초 기절" + E + ".",
        "skill2": O + "수호자의 성소" + E + ": 교전 중인 아군 챔피언(또는 자신)에게 성소를 던져 " + HEAL + " 회복, 이동 속도 +{w_ms}%. " + O + "신비한 차원문" + E +
                  ": 적이 붙으면 문을 열어 주변 아군 챔피언과 함께 멀어지고 이동 속도 +{e_ms}% (" + A + "{e_cd}초" + E + "마다).",
        "ult": "모인 적 챔피언(또는 군중 제어된 아군 챔피언)에게 황금 구체를 던져 범위 안 모든 유닛(아군, 바드, 포탑 포함)을 " + C + "{r_t}초 동안 경직" + E +
               "시킵니다: 행동, 지정, 피해 불가.",
        "names": ("우주의 결속", "수호자의 성소 / 신비한 차원문", "운명의 소용돌이"),
    },
    "ja": {
        "name": "バード",
        "attack": "星の矢を放つ。自動効果" + O + "旅人の呼び声" + E + "：" + A + "{p_cd}秒" + E + "ごとにミープが攻撃と共に飛び、対象周囲の敵に" + mag("p") + "の" + M +
                  "魔法ダメージ" + E + "と" + C + "{p_slow}%スロウ" + E + "（" + A + "{p_slow_t}秒" + E + "）。",
        "skill": "宇宙の力を放ち、最初に当たった敵に" + mag("q") + "の" + M + "魔法ダメージ" + E + "と" + C + "{q_slow}%スロウ" + E + "；後ろに別の敵がいれば両方にダメージと" +
                 C + "{q_stun}秒スタン" + E + "。",
        "skill2": O + "回復の遺物" + E + "：交戦中の味方チャンピオン（か自分）に遺物を投げ" + HEAL + "回復、移動速度+{w_ms}%。" + O + "精霊の旅路" + E +
                  "：敵に詰められると扉を開き、近くの味方と離脱、移動速度+{e_ms}%（" + A + "{e_cd}秒" + E + "ごと）。",
        "ult": "固まった敵チャンピオン（かCC中の味方）に金の球を投げ、範囲内の全ユニット（味方・自分・タワーも）を" + C + "{r_t}秒停止" + E + "：行動・対象指定・ダメージ不可。",
        "names": ("宇宙の法則", "回復の遺物 / 精霊の旅路", "運命の調律"),
    },
}

S_ = "league_bard_"
CL = "league_bard_sfx_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(CL + k, vol, 0.0)] for k, vol in [
    ("a_cast", 0.4), ("a_hit", 0.4), ("p_meep", 0.45), ("p_hit", 0.45), ("q_cast", 0.55), ("q_hit", 0.5),
    ("q_bind", 0.55), ("w_cast", 0.5), ("w_heal", 0.5), ("e_cast", 0.55), ("e_out", 0.55), ("r_cast", 0.6),
    ("r_land", 0.6), ("r_lock", 0.5), ("vo_q", 0.7), ("vo_w", 0.7), ("vo_e", 0.7), ("vo_r", 0.75)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "p_slow", "q_dmg", "q_ap", "q_slow", "w_heal", "w_ap", "w_ms", "e_ms")}
    v.update({k: secs(p[k]) for k in ("p_cd", "p_slow_t", "q_stun", "r_t")})
    v["e_cd"] = secs(p["e_cd_t"])
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
    if "Bard" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Bard. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
