"""Qiyana's text (5 languages), sound_info files and her keys in the shared files, numbers from build_qiyana.P.

    python tools/kit/setup_qiyana.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_qiyana in every language, description + skill_name),
sound/sfx/league_qiyana_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Qiyana named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 奇亚娜 (元素女皇): 凌人贵气, 以绪塔尔之锋, 方圆塑令, 天纵之勇, 惊才绝景; zh_TW 姬亞娜 (元素女帝):
皇家特權, 伊克斯塔爾迴旋刀, 元素之形, 勇往直前, 大顯身手; ja キヤナ: 女帝の威風, イシュタルの切先, 大地の力, 俊烈, 天賦絢爛; ko 키아나:
왕가의 특권, 이쉬탈의 칼날, 대지창조, 대담무쌍, 여왕의 진가.
Slots: skill = Q Edge of Ixtal, skill2 = E Audacity with W Terrashape (the element and Q's refresh), ult = R Supreme
Display of Talent; the passive Royal Privilege and Terrashape's enchant in the attack's text. No combo sentence in any
text (the user's rule); the README says them. The element's cycle is the main pack's (the add-on has W of its own, from
the terrain, and says so in its own texts, addons/league_qiyana/make_override.py). The enchant's magic is the main pack's
ApAttack, whose ratio is ability power (mag_ap); the add-on's natives scale it with attack damage (mag).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_qiyana import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_qiyana"
VERSION = "0.193.0"     # the next free number above main 0.192.0 (Udyr #461) (2026-10-22)
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
M = "<#a974ffff>"      # magic damage
G = "<#7bd96bff>"      # healing, shields
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face between her eyes (ppu_restyle's face_to); the ban/pick card at base's rule for her height
# (tools/art/bp_card_audit.py)
VIEW = {"face": {"x": 1, "y": -27}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -6}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def mag(d, r):
    """Magic damage scaling with attack damage (the add-on's natives)."""
    return f"{M}{{{d}}}{E} + {ADi}{M}{{{r}}}%{E}"


def mag_ap(d, r):
    """Magic damage scaling with ability power (the main pack's ApAttack: its ratio is ability power)."""
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "奇亚娜",
        "attack": "挥环攻击。" + O + "凌人贵气" + E + "：普攻和Q、E每" + A + "{rp_cd}秒" + E + "首次命中额外造成" + phys("rp_dmg", "rp_ratio") +
                  "物理伤害，换上新元素时重置。附有元素时攻速+{w_as}%、攻击距离+{w_range}，普攻和Q、E额外造成" +
                  mag_ap("w_on", "w_on_ap") + "魔法伤害。",
        "skill": "挥环斩向身前一条直线，造成" + phys("q_dmg", "q_ratio") + "物理伤害（第一个之后{q_far}%）。附有元素时掷出环刃，在第一个敌人处"
                 "炸开并消耗元素：河流" + R + "定身" + E + A + "{q_root}秒" + E + "后减速{q_slow}%；岩石多" + phys("q_rock", "q_rock_r") +
                 "；草丛伪装" + A + "{q_inv}秒" + E + "并加速{q_ms}%。",
        "skill2": "突进到敌人身上，造成" + phys("e_dmg", "e_ratio") + "物理伤害；" + O + "方圆塑令" + E + "：为武器附上元素（草丛、河流、岩石轮换），"
                  "并刷新以绪塔尔之锋。",
        "ult": "挥环放出冲击波，对路径上的敌人造成" + phys("r_dmg", "r_ratio") + "物理伤害（英雄另受最大生命{r_hp}%），将其" + R + "击退" + E +
               "后" + R + "晕眩" + E + A + "{r_stun}秒" + E + "。",
        "names": ("以绪塔尔之锋", "天纵之勇", "惊才绝景"),
    },
    "zh-hant": {
        "name": "姬亞娜",
        "attack": "揮環攻擊。" + O + "皇家特權" + E + "：普攻和Q、E每" + A + "{rp_cd}秒" + E + "首次命中額外造成" + phys("rp_dmg", "rp_ratio") +
                  "物理傷害，換上新元素時重置。附有元素時攻速+{w_as}%、攻擊距離+{w_range}，普攻和Q、E額外造成" +
                  mag_ap("w_on", "w_on_ap") + "魔法傷害。",
        "skill": "揮環斬向身前一條直線，造成" + phys("q_dmg", "q_ratio") + "物理傷害（第一個之後{q_far}%）。附有元素時擲出環刃，在第一個敵人處"
                 "炸開並消耗元素：河流" + R + "定身" + E + A + "{q_root}秒" + E + "後緩速{q_slow}%；岩石多" + phys("q_rock", "q_rock_r") +
                 "；草叢偽裝" + A + "{q_inv}秒" + E + "並加速{q_ms}%。",
        "skill2": "突進到敵人身上，造成" + phys("e_dmg", "e_ratio") + "物理傷害；" + O + "元素之形" + E + "：為武器附上元素（草叢、河流、岩石輪換），"
                  "並刷新伊克斯塔爾迴旋刀。",
        "ult": "揮環放出衝擊波，對路徑上的敵人造成" + phys("r_dmg", "r_ratio") + "物理傷害（英雄另受最大生命{r_hp}%），將其" + R + "擊退" + E +
               "後" + R + "暈眩" + E + A + "{r_stun}秒" + E + "。",
        "names": ("伊克斯塔爾迴旋刀", "勇往直前", "大顯身手"),
    },
    "en": {
        "name": "Qiyana",
        "attack": "A swing of her ring blade. " + O + "Royal Privilege" + E + ": her first attack, Q or E hit every " + A + "{rp_cd}s" + E +
                  " deals " + phys("rp_dmg", "rp_ratio") + " physical damage more; a new element resets it. While her ring holds an "
                  "element she has +{w_as}% attack speed and +{w_range} range, and her attacks, Q and E deal " + mag_ap("w_on", "w_on_ap") +
                  " magic damage more.",
        "skill": "Slashes a line before her for " + phys("q_dmg", "q_ratio") + " physical damage ({q_far}% beyond the first). With an "
                 "element she hurls the ring, bursting on the first enemy and spending it: river " + R + "roots" + E + " for " + A +
                 "{q_root}s" + E + " then slows {q_slow}%; rock deals " + phys("q_rock", "q_rock_r") + " more; grass camouflages her for " +
                 A + "{q_inv}s" + E + " with +{q_ms}% move speed.",
        "skill2": "Dashes onto an enemy for " + phys("e_dmg", "e_ratio") + " physical damage. " + O + "Terrashape" + E + ": the dash "
                  "enchants her ring with an element (grass, river and rock in turn) and refreshes Edge of Ixtal.",
        "ult": "Swings the ring and sends a shockwave that deals " + phys("r_dmg", "r_ratio") + " physical damage to the enemies on "
               "its way (champions also lose {r_hp}% of their maximum health), " + R + "knocking them back" + E + " and " + R +
               "stunning" + E + " them for " + A + "{r_stun}s" + E + ".",
        "names": ("Edge of Ixtal", "Audacity", "Supreme Display of Talent"),
    },
    "ko": {
        "name": "키아나",
        "attack": "고리 칼날로 공격. " + O + "왕가의 특권" + E + ": 기본 공격·Q·E가 " + A + "{rp_cd}초" + E + "마다 첫 적중 시 " +
                  phys("rp_dmg", "rp_ratio") + " 물리 피해 추가, 새 원소를 얻으면 초기화. 무기에 원소가 깃들면 공격 속도 +{w_as}%, 사거리 "
                  "+{w_range}, 기본 공격·Q·E가 " + mag_ap("w_on", "w_on_ap") + " 마법 피해 추가.",
        "skill": "앞쪽 직선을 베어 " + phys("q_dmg", "q_ratio") + " 물리 피해(첫 대상 이후 {q_far}%). 원소가 있으면 고리를 던져 첫 적에게서 "
                 "터지며 원소 소모: 강 " + A + "{q_root}초" + E + " " + R + "속박" + E + " 후 {q_slow}% 둔화, 바위 " + phys("q_rock", "q_rock_r") +
                 " 추가 피해, 풀숲 " + A + "{q_inv}초" + E + " 위장과 이동 속도 +{q_ms}%.",
        "skill2": "적에게 돌진해 " + phys("e_dmg", "e_ratio") + " 물리 피해. " + O + "대지창조" + E + ": 무기에 원소를 깃들이고(풀숲, 강, 바위 "
                  "순서) 이쉬탈의 칼날 초기화.",
        "ult": "고리를 휘둘러 충격파를 날려 경로의 적에게 " + phys("r_dmg", "r_ratio") + " 물리 피해(챔피언은 최대 체력 {r_hp}% 추가)를 주고 " +
               R + "밀쳐낸 뒤" + E + " " + A + "{r_stun}초" + E + " " + R + "기절" + E + ".",
        "names": ("이쉬탈의 칼날", "대담무쌍", "여왕의 진가"),
    },
    "ja": {
        "name": "キヤナ",
        "attack": "リングで攻撃。" + O + "女帝の威風" + E + "：通常攻撃・Q・Eの" + A + "{rp_cd}秒" + E + "ごとの最初の命中が" +
                  phys("rp_dmg", "rp_ratio") + "の物理ダメージを追加、新しいエレメントでリセット。エレメントがある間、攻撃速度+{w_as}%・"
                  "射程+{w_range}、通常攻撃・Q・Eが" + mag_ap("w_on", "w_on_ap") + "の魔法ダメージを追加。",
        "skill": "前方の直線を薙ぎ" + phys("q_dmg", "q_ratio") + "の物理ダメージ（2体目以降{q_far}%）。エレメントがあればリングを投げ、最初の敵で"
                 "炸裂して消費：川は" + A + "{q_root}秒" + E + R + "スネア" + E + "後{q_slow}%スロウ、岩は" + phys("q_rock", "q_rock_r") +
                 "追加、草むらは" + A + "{q_inv}秒" + E + "迷彩と移動速度+{q_ms}%。",
        "skill2": "敵へ突進し" + phys("e_dmg", "e_ratio") + "の物理ダメージ。" + O + "大地の力" + E + "：武器にエレメントを宿し（草むら・川・岩の順）、"
                  "イシュタルの切先を再使用可能に。",
        "ult": "リングを振るって衝撃波を放ち、道中の敵に" + phys("r_dmg", "r_ratio") + "の物理ダメージ（チャンピオンは最大体力の{r_hp}%も）と" +
               R + "ノックバック" + E + "、" + A + "{r_stun}秒" + E + "の" + R + "スタン" + E + "。",
        "names": ("イシュタルの切先", "俊烈", "天賦絢爛"),
    },
}

C = "league_qiyana_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
# the sfx toward Lux's 0.8 (the level Orianna's, Zoe's and K'Sante's got, 2026-10-22; attacks lower: they come often), the
# voice as the other heroes'
SOUNDS = {f"league_qiyana_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("p_hit", 0.65), ("w_on", 0.7), ("q", 0.8), ("q_w", 0.8), ("q_r", 0.8), ("q_g", 0.8),
    ("q_hit", 0.7), ("q_w_hit", 0.75), ("q_r_hit", 0.75), ("q_g_hit", 0.75), ("e", 0.75), ("e_hit", 0.8), ("r", 0.85),
    ("r_burst", 0.9), ("r_hit", 0.85), ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("rp_dmg", "rp_ratio", "w_as", "w_range", "w_on", "w_on_r", "w_on_ap", "q_dmg", "q_ratio", "q_far",
                           "q_slow", "q_rock", "q_rock_r", "q_ms", "e_dmg", "e_ratio", "r_dmg", "r_ratio", "r_hp")}
    for k in ("rp_cd", "q_root", "q_inv", "r_stun"):
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
    if "Qiyana" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Qiyana. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
