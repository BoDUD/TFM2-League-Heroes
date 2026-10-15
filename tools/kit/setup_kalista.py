"""Kalista's text (5 languages), sound_info files and her keys in the shared files, numbers from build_kalista.P.

    python tools/kit/setup_kalista.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_kalista in every language, description + skill_name),
sound/sfx/league_kalista_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.117.0, Kalista named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 复仇之矛 / 卡莉丝塔 - the client swaps name and title: 卡莉丝塔; 武术姿态, 穿刺, 哨兵, 撕裂,
命运的召唤; zh_TW 克黎思妲 / 復仇之矛, 好戰突進, 赦罪穿刺, 憎靈守衛, 痛苦撕扯, 命運呼喚; ja カリスタ / 復讐の槍, 戦の所作,
貫魂の一投, 執念の霊魂, 引き裂く遺恨, 宿命の呼び声; ko 칼리스타 / 복수의 화신, 전투 태세, 꿰뚫는 창, 감시하는 혼, 뽑아 찢기, 운명의 부름).
Slots: skill = Q, skill2 = E, ult = R; the passive and W's Soul-Marked are told in the attack's text. No combo sentence
in any text (the user's rule). No `league_kalista_attack` sound: the engine would play it at the start of every
attack; the throw plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_kalista import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_kalista"
VERSION = "0.117.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
W_ = "<#ffffffff>"     # true damage
E = "<>"
# champion_view: placeholders until the sprite is in (tfm2_ase.py face then --face / --banpick)
VIEW = {"face": {"x": 0, "y": -33}, "center": {"x": 0, "y": -11}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "卡莉丝塔",
        "attack": "投矛，命中的敌人身上插一支矛（" + A + "{sp_t}秒" + E + "）。" + O + "武术姿态" + E + "：被敌方英雄贴近时，投矛后向后跳开。" +
                  O + "哨兵" + E + "：有队友在目标身边时，额外造成目标" + W_ + "{w_hp}%最大生命值的真实伤害" + E + "（" + A + "{w_cd}秒" + E +
                  "一次）。",
        "skill": "掷出长矛，对第一个敌人造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "并插上一支矛；若将其击杀，长矛穿过去命中下一个。",
        "skill2": "拔出所有敌人身上的矛：每支造成" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "并减速{e_slow}%。击杀英雄时刷新冷却。" +
                  "插满" + A + "{e_need}支" + E + "时自动拔出。",
        "ult": "把身边一名队友拉进身体保护" + A + "{r_hold}秒" + E + "，然后甩向目标，落地击飞周围敌人" + A + "{r_up}秒" + E + "，造成" +
               phy("r_dmg", "r_ratio") + O + "物理伤害" + E + "。",
        "names": ("穿刺", "撕裂", "命运的召唤"),
    },
    "zh-hant": {
        "name": "克黎思妲",
        "attack": "投矛，命中的敵人身上插一支矛（" + A + "{sp_t}秒" + E + "）。" + O + "好戰突進" + E + "：被敵方英雄貼近時，投矛後向後跳開。" +
                  O + "憎靈守衛" + E + "：有隊友在目標身邊時，額外造成目標" + W_ + "{w_hp}%最大生命的真實傷害" + E + "（" + A + "{w_cd}秒" +
                  E + "一次）。",
        "skill": "擲出長矛，對第一個敵人造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "並插上一支矛；若將其擊殺，長矛穿過去命中下一個。",
        "skill2": "拔出所有敵人身上的矛：每支造成" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "並緩速{e_slow}%。擊殺英雄時重置冷卻。" +
                  "插滿" + A + "{e_need}支" + E + "時自動拔出。",
        "ult": "把身邊一名隊友拉進身體保護" + A + "{r_hold}秒" + E + "，然後擲向目標，落地擊飛周圍敵人" + A + "{r_up}秒" + E + "，造成" +
               phy("r_dmg", "r_ratio") + O + "物理傷害" + E + "。",
        "names": ("赦罪穿刺", "痛苦撕扯", "命運呼喚"),
    },
    "en": {
        "name": "Kalista",
        "attack": "Throws spears; each one stays in the enemy it hits for " + A + "{sp_t}s" + E + ". " + O + "Martial Poise" + E +
                  ": with an enemy champion close, she hops back after each spear. " + O + "Sentinel" + E + ": with an ally "
                  "beside her target, deals " + W_ + "{w_hp}% of its max health as true damage" + E + " (once every " + A +
                  "{w_cd}s" + E + ").",
        "skill": "Throws a spear that deals " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + " to the first "
                 "enemy hit and sticks a spear in it; if it kills, the spear passes through to the next.",
        "skill2": "Rips out every spear: each deals " + phy("e_dmg", "e_ratio") + " " + O + "physical damage" + E + " and slows "
                  "{e_slow}%. Killing a champion refunds the cooldown. Rips on its own at " + A + "{e_need} spears" + E + ".",
        "ult": "Draws an ally beside her into herself for " + A + "{r_hold}s" + E + ", then hurls them at the target; the landing "
               "knocks up nearby enemies for " + A + "{r_up}s" + E + " and deals " + phy("r_dmg", "r_ratio") + " " + O +
               "physical damage" + E + ".",
        "names": ("Pierce", "Rend", "Fate's Call"),
    },
    "ko": {
        "name": "칼리스타",
        "attack": "창을 던지며, 맞은 적에게 창이 " + A + "{sp_t}초" + E + " 꽂힙니다. " + O + "전투 태세" + E + ": 적 챔피언이 가까우면 "
                  "창을 던진 뒤 뒤로 도약. " + O + "감시하는 혼" + E + ": 대상 곁에 아군이 있으면 대상 최대 체력의 " + W_ + "{w_hp}% 고정 피해" + E +
                  "(" + A + "{w_cd}초" + E + "마다).",
        "skill": "창을 던져 처음 맞은 적에게 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + "를 입히고 창을 꽂습니다. 처치하면 "
                 "창이 관통해 다음 적을 맞힙니다.",
        "skill2": "모든 창을 뽑습니다: 창마다 " + phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" + E + ", {e_slow}% 둔화. 챔피언 처치 시 "
                  "재사용 대기시간 초기화. 창이 " + A + "{e_need}개" + E + "면 자동으로 뽑습니다.",
        "ult": "곁의 아군을 " + A + "{r_hold}초" + E + " 동안 몸에 거둔 뒤 대상에게 던집니다. 착지하면 주변 적을 " + A + "{r_up}초" + E +
               " 띄워 올리고 " + phy("r_dmg", "r_ratio") + "의 " + O + "물리 피해" + E + ".",
        "names": ("꿰뚫는 창", "뽑아 찢기", "운명의 부름"),
    },
    "ja": {
        "name": "カリスタ",
        "attack": "槍を投げ、当たった敵に槍が" + A + "{sp_t}秒" + E + "刺さる。" + O + "戦の所作" + E + "：敵チャンピオンが近いと投擲後に後ろへ跳ぶ。" +
                  O + "執念の霊魂" + E + "：対象の傍に味方がいると最大体力の" + W_ + "{w_hp}%の確定ダメージ" + E + "（" + A + "{w_cd}秒" + E +
                  "毎）。",
        "skill": "槍を投げ、最初の敵に" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "を与え槍を刺す。倒すと貫通して次の敵に当たる。",
        "skill2": "全ての槍を引き抜く：1本につき" + phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "と{e_slow}%スロウ。" +
                  "チャンピオンを倒すとCD解消。" + A + "{e_need}本" + E + "で自動発動。",
        "ult": "傍の味方を" + A + "{r_hold}秒" + E + "身に宿し、対象へ投げ放つ。着地で周囲の敵を" + A + "{r_up}秒" + E + "打ち上げ、" +
               phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "。",
        "names": ("貫魂の一投", "引き裂く遺恨", "宿命の呼び声"),
    },
}

C = "league_kalista_sfx_"
V = "league_kalista_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_kalista_a_throw": [(C + "a_throw", 0.4, 0.0)],
    "league_kalista_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_kalista_hop": [(C + "hop", 0.4, 0.0)],
    "league_kalista_w_hit": [(C + "w_hit", 0.5, 0.0)],
    "league_kalista_q": [(C + "q", 0.55, 0.0)],
    "league_kalista_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_kalista_e": [(C + "e", 0.6, 0.0)],
    "league_kalista_e_reset": [(C + "w_hit", 0.45, 0.0)],
    "league_kalista_r": [(C + "r", 0.6, 0.0)],
    "league_kalista_r_take": [(C + "r_take", 0.55, 0.0)],
    "league_kalista_r_fly": [(C + "r_fly", 0.55, 0.0)],
    "league_kalista_r_hit": [(C + "r_hit", 0.6, 0.0)],
    "league_kalista_vo_q": [(V + "q", 0.85, 0.0)],
    "league_kalista_vo_e": [(V + "e", 0.85, 0.0)],
    "league_kalista_vo_r": [(V + "r", 0.9, 0.05)],
    "league_kalista_vo_r_fly": [(V + "r_fly", 0.85, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("w_hp", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "e_slow", "e_need", "r_dmg", "r_ratio")}
    for k in ("sp_t", "w_cd", "r_hold", "r_up"):
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
    if "Kalista" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Kalista. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
