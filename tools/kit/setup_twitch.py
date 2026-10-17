"""Twitch's text (5 languages), sound_info files and his keys in the shared files, numbers from build_twitch.P.

    python tools/kit/setup_twitch.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_twitch in every language, description + skill_name),
sound/sfx/league_twitch_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.71.0, Twitch named). Only his keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (the Chinese client swaps name and title: 图奇 / 瘟疫之源; 死亡毒液, 埋伏, 剧毒之桶,
毒性爆发, 火力全开) and Data Dragon 16.19.1 (zh_TW 圖奇 / 瘟疫之源, 死亡毒液, 潛伏, 虛弱之毒, 毒性爆發, 噴射，然後祈禱吧！; ko
트위치 / 역병 쥐, 맹독, 매복, 독약 병, 오염, 무차별 난사; ja トゥイッチ / 黒死のドブネズミ, スゴイ毒ダ！, オイラだヨ！, コイツを食らエ！,
ボーン！, ヒャッハー！). skill2 is named after W (the cask; the icon is W's), E in the text.
No `league_twitch_attack` sound: the engine would play it at the start of every attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_twitch import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_twitch"
VERSION = "0.71.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
W_ = "<#ffffffff>"     # true damage
E = "<>"
# champion_view: the face point on his head - the ears' tips 22 over the pivot, the head's middle column 4 ahead (tfm2_ase.py
# face suggests -36, the backpack's top); the idle's top is 26 over the pivot, so no banpick_center (only tops above -28)
VIEW = {"face": {"x": 1, "y": -30}, "center": {"x": 0, "y": -11}}   # 10-09 shrunk to 85%: the crown 30 over the feet (tfm2_ase.py face)


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def tru(d, r):
    return f"{W_}{{{d}}}{E} + {ADi}{W_}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "图奇",
        "attack": "弩箭攻击。被动" + O + "死亡毒液" + E + "：普攻、毒桶和大招的箭每次挂一层毒，每层" + A + "{v_t}秒" + E +
                  "内每秒造成" + tru("v_dmg", "v_ratio") + W_ + "真实伤害" + E + "。",
        "skill": "伪装隐身最多" + A + "{q_t}秒" + E + "并加速{q_ms}%，出手即现形，之后" + A + "{q_as_t}秒" + E + "攻速+{q_as}%。" +
                 "击杀敌方英雄时刷新冷却。",
        "skill2": "扔出毒桶：范围内敌人挂一层毒并减速{w_slow}%，毒池持续" + A + "{w_pool}秒" + E + "。随后接" + O + "毒性爆发" + E +
                  "：每层毒造成" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "。",
        "ult": A + "{r_t}秒" + E + "内射程+{r_range}、攻击力+{r_ad}，弩箭穿透一条直线，每多穿一个少{r_fall}%（最低{r_min}%）。" +
               "两名敌方英雄在附近时施放。",
        "names": ("埋伏", "剧毒之桶", "火力全开"),
    },
    "zh-hant": {
        "name": "圖奇",
        "attack": "弩箭攻擊。被動" + O + "死亡毒液" + E + "：普攻、毒桶和大招的箭每次掛一層毒，每層" + A + "{v_t}秒" + E +
                  "內每秒造成" + tru("v_dmg", "v_ratio") + W_ + "真實傷害" + E + "。",
        "skill": "偽裝隱形最多" + A + "{q_t}秒" + E + "並加速{q_ms}%，出手即現形，之後" + A + "{q_as_t}秒" + E + "攻速+{q_as}%。" +
                 "擊殺敵方英雄時重置冷卻。",
        "skill2": "擲出毒桶：範圍內敵人掛一層毒並緩速{w_slow}%，毒池持續" + A + "{w_pool}秒" + E + "。隨後接" + O + "毒性爆發" + E +
                  "：每層毒造成" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "。",
        "ult": A + "{r_t}秒" + E + "內射程+{r_range}、攻擊力+{r_ad}，弩箭貫穿一條直線，每多穿一個少{r_fall}%（最低{r_min}%）。" +
               "兩名敵方英雄在附近時施放。",
        "names": ("潛伏", "虛弱之毒", "噴射，然後祈禱吧！"),
    },
    "en": {
        "name": "Twitch",
        "attack": "Crossbow bolts. Passive " + O + "Deadly Venom" + E + ": his attacks, the cask and R's bolts each add a stack "
                  "of venom that deals " + tru("v_dmg", "v_ratio") + " " + W_ + "true damage" + E + " per second for " + A +
                  "{v_t}s" + E + ".",
        "skill": "Camouflaged for up to " + A + "{q_t}s" + E + " with {q_ms}% move speed; attacking or casting reveals him and "
                 "grants {q_as}% attack speed for " + A + "{q_as_t}s" + E + ". Champion takedowns reset the cooldown.",
        "skill2": "Hurls a cask: enemies in the area gain a stack and are slowed {w_slow}%; the puddle lasts " + A + "{w_pool}s" +
                  E + ". Then " + O + "Contaminate" + E + ": every venom stack deals " + phy("e_dmg", "e_ratio") + " " + O +
                  "physical damage" + E + ".",
        "ult": "For " + A + "{r_t}s" + E + ": +{r_range} range and +{r_ad} attack; bolts pierce in a line, {r_fall}% less per "
               "unit hit (down to {r_min}%). Cast with two enemy champions nearby.",
        "names": ("Ambush", "Venom Cask", "Spray and Pray"),
    },
    "ko": {
        "name": "트위치",
        "attack": "석궁 공격. 기본 지속 효과 " + O + "맹독" + E + ": 기본 공격, 독약 병, 궁극기 화살마다 독 1중첩, 중첩당 " + A +
                  "{v_t}초" + E + " 동안 초당 " + tru("v_dmg", "v_ratio") + "의 " + W_ + "고정 피해" + E + ".",
        "skill": "최대 " + A + "{q_t}초" + E + " 위장, 이동 속도 {q_ms}%. 공격하거나 스킬을 쓰면 드러나고 " + A + "{q_as_t}초" + E +
                 " 동안 공격 속도 {q_as}%. 챔피언 처치 시 초기화.",
        "skill2": "독약 병 투척: 범위 안의 적에게 독 1중첩, {w_slow}% 둔화, 웅덩이 " + A + "{w_pool}초" + E + ". 이어서 " + O + "오염" +
                  E + ": 독 중첩마다 " + phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" + E + ".",
        "ult": A + "{r_t}초" + E + " 동안 사거리 +{r_range}, 공격력 +{r_ad}. 화살이 일직선으로 관통하며 대상마다 {r_fall}% 감소(최소 {r_min}%). "
               "적 챔피언 둘이 가까이 있을 때 사용.",
        "names": ("매복", "독약 병", "무차별 난사"),
    },
    "ja": {
        "name": "トゥイッチ",
        "attack": "クロスボウで攻撃。パッシブ " + O + "スゴイ毒ダ！" + E + "：通常攻撃・毒瓶・アルティメットの矢ごとに毒1スタック、" +
                  "1スタックにつき" + A + "{v_t}秒" + E + "間毎秒" + tru("v_dmg", "v_ratio") + "の" + W_ + "確定ダメージ" + E + "。",
        "skill": "最大" + A + "{q_t}秒" + E + "カモフラージュ、移動速度{q_ms}%。攻撃かスキルで姿を現し" + A + "{q_as_t}秒" + E +
                 "攻撃速度{q_as}%。キルでCD解消。",
        "skill2": "毒瓶を投げ、範囲の敵に毒1スタックと{w_slow}%スロウ、毒溜まり" + A + "{w_pool}秒" + E + "。続けて" + O + "ボーン！" +
                  E + "：毒1スタックにつき" + phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "。",
        "ult": A + "{r_t}秒" + E + "間射程+{r_range}・攻撃力+{r_ad}、矢が一直線に貫通し1体ごとに{r_fall}%減少（最低{r_min}%）。" +
               "敵チャンピオン2体が近い時に使用。",
        "names": ("オイラだヨ！", "コイツを食らエ！", "ヒャッハー！"),
    },
}

C = "league_twitch_sfx_"
V = "league_twitch_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_twitch_a_shot": [(C + "shot", 0.4, 0.0)],
    "league_twitch_a_hit": [(C + "hit", 0.35, 0.0)],
    "league_twitch_q_cast": [(C + "q_cast", 0.55, 0.0)],
    "league_twitch_q_out": [(C + "q_out", 0.5, 0.0)],
    "league_twitch_q_reset": [(C + "q_reset", 0.55, 0.0)],
    "league_twitch_w_cast": [(C + "w_cast", 0.45, 0.0)],
    "league_twitch_w_throw": [(C + "w_throw", 0.5, 0.0)],
    "league_twitch_w_land": [(C + "w_land", 0.55, 0.0)],
    "league_twitch_e_cast": [(C + "e_cast", 0.55, 0.0)],
    "league_twitch_e_pop": [(C + "e_pop", 0.6, 0.0)],
    "league_twitch_r_cast": [(C + "r_cast", 0.6, 0.0)],
    "league_twitch_r_shot": [(C + "r_shot", 0.45, 0.0)],
    "league_twitch_r_hit": [(C + "r_hit", 0.35, 0.0)],
    "league_twitch_vo_q": [(V + "q", 0.85, 0.0)],
    "league_twitch_vo_w": [(V + "w", 0.85, 0.0)],
    "league_twitch_vo_e": [(V + "e", 0.85, 0.0)],
    "league_twitch_vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("v_dmg", "v_ratio", "q_ms", "q_as", "w_slow", "e_dmg", "e_ratio", "r_ad", "r_fall",
                           "r_min")}
    v["r_range"] = p["r_bonus"] // 100
    for k in ("v_t", "q_t", "q_as_t", "w_pool", "r_t"):
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
    if "Twitch" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Twitch. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
