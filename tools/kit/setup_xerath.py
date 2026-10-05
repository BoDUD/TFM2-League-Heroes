"""Xerath's text (5 languages), sound_info files and his keys in the shared files, numbers from build_xerath.P.

    python tools/kit/setup_xerath.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_xerath in every language, description + skill_name),
sound/sfx/league_xerath_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.63.0, Xerath named). Only his keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (泽拉斯 / 远古巫灵, 法力澎湃, 奥能脉冲, 毁灭之眼, 冲击法球, 奥术仪式) and Data Dragon
16.19.1 (zh_TW 齊勒斯 / 遠古魔導, 祕術強襲, 祕術脈衝, 毀滅之眼, 幻魔打擊, 魔導祭典; ko 제라스 / 초월한 마법사, 마나 쇄도, 비전 파동,
파멸의 눈, 충격 구체, 비전 의식; ja ゼラス / 超越魔神, マナサージ, アルカノパルス, デストラクションアイ, ショックオーブ, アーケーンライト).
No `league_xerath_attack` sound: the engine would play it at the start of every attack; the orb's sound plays from the
tree at the release.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_xerath import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_xerath"
VERSION = "0.63.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -36}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "泽拉斯",
        "attack": "发射奥术法球攻击。被动" + O + "法力澎湃" + E + "：每" + A + "{p_wait}秒" + E + "下一次攻击额外造成" + mag("p_dmg", "p_ap") +
                  M + "魔法伤害" + E + "，并使小技能冷却缩短{p_cut}%；他每击杀一个单位，等待缩短{p_step}秒。",
        "skill": "蓄力后射出贯穿光束，对直线上的敌人造成" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "。附近有敌方英雄时蓄满，射得更远；"
                 "只打小兵时快速蓄力，伤害{q_quick}%。",
        "skill2": O + "冲击法球" + E + "：命中第一个敌人造成" + mag("e_dmg", "e_ap") + "并" + R + "晕眩{e_s1}~{e_s3}秒" + E + "（飞得越远越久）。随后" +
                  O + "毁灭之眼" + E + "落在敌方英雄头上，造成" + mag("w_dmg", "w_ap") + "并" + R + "减速" + E + "，中心伤害+{w_mid}%。",
        "ult": "飞升并原地引导，向远处的敌方英雄连发" + A + "{r_n}次" + E + "魔法炮击，落点预警后爆炸，每发造成" + mag("r_dmg", "r_ap") + M +
               "魔法伤害" + E + "；每次命中英雄，之后的炮击伤害+{r_ramp}%。被控制会打断。",
        "names": ("奥能脉冲", "冲击法球", "奥术仪式"),
    },
    "zh-hant": {
        "name": "齊勒斯",
        "attack": "發射祕術法球攻擊。被動" + O + "祕術強襲" + E + "：每" + A + "{p_wait}秒" + E + "下一次攻擊額外造成" + mag("p_dmg", "p_ap") +
                  M + "魔法傷害" + E + "，並使小技能冷卻縮短{p_cut}%；他每擊殺一個單位，等待縮短{p_step}秒。",
        "skill": "蓄力後射出貫穿光束，對直線上的敵人造成" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "。附近有敵方英雄時蓄滿，射得更遠；"
                 "只打小兵時快速蓄力，傷害{q_quick}%。",
        "skill2": O + "幻魔打擊" + E + "：命中第一個敵人造成" + mag("e_dmg", "e_ap") + "並" + R + "暈眩{e_s1}~{e_s3}秒" + E + "（飛得越遠越久）。隨後" +
                  O + "毀滅之眼" + E + "落在敵方英雄頭上，造成" + mag("w_dmg", "w_ap") + "並" + R + "緩速" + E + "，中心傷害+{w_mid}%。",
        "ult": "飛升並原地引導，向遠處的敵方英雄連發" + A + "{r_n}次" + E + "魔法炮擊，落點預警後爆炸，每發造成" + mag("r_dmg", "r_ap") + M +
               "魔法傷害" + E + "；每次命中英雄，之後的炮擊傷害+{r_ramp}%。被控制會打斷。",
        "names": ("祕術脈衝", "幻魔打擊", "魔導祭典"),
    },
    "en": {
        "name": "Xerath",
        "attack": "Fires arcane orbs. Passive " + O + "Mana Surge" + E + ": every " + A + "{p_wait}s" + E + " his next attack deals " +
                  mag("p_dmg", "p_ap") + " bonus " + M + "magic damage" + E + " and cuts his basic spells' cooldowns by {p_cut}%. "
                  "Each unit he kills brings it {p_step}s sooner.",
        "skill": "Charges, then fires a piercing beam: " + mag("q_dmg", "q_ap") + " " + M + "magic damage" + E + " to every enemy in "
                 "the line. With an enemy champion near he charges fully for a longer beam; against minions alone a quick "
                 "charge deals {q_quick}%.",
        "skill2": O + "Shocking Orb" + E + ": the first enemy hit takes " + mag("e_dmg", "e_ap") + " and is " + R + "stunned" + E +
                  " for {e_s1}-{e_s3}s (longer the farther it flew). Then the " + O + "Eye of Destruction" + E + " falls on the "
                  "enemy champion: " + mag("w_dmg", "w_ap") + " and a " + R + "slow" + E + ", +{w_mid}% in the centre.",
        "ult": "Ascends and channels in place, calling " + A + "{r_n}" + E + " arcane shells down on distant enemy champions. "
               "Each lands after a warning for " + mag("r_dmg", "r_ap") + " " + M + "magic damage" + E + "; every champion hit "
               "adds {r_ramp}% to the shells after it. Crowd control breaks the channel.",
        "names": ("Arcanopulse", "Shocking Orb", "Rite of the Arcane"),
    },
    "ko": {
        "name": "제라스",
        "attack": "비전 구체로 공격합니다. 기본 지속 효과 " + O + "마나 쇄도" + E + ": " + A + "{p_wait}초" + E + "마다 다음 공격이 " +
                  mag("p_dmg", "p_ap") + "의 추가 " + M + "마법 피해" + E + "를 입히고 기본 스킬 재사용 대기시간을 {p_cut}% 줄입니다. "
                  "유닛을 처치할 때마다 {p_step}초 빨라집니다.",
        "skill": "충전 후 관통하는 광선을 발사해 직선상의 적에게 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" + E + "를 입힙니다. "
                 "적 챔피언이 가까우면 끝까지 충전해 더 멀리, 미니언만 있으면 빠르게 충전해 {q_quick}% 피해.",
        "skill2": O + "충격 구체" + E + ": 처음 맞힌 적에게 " + mag("e_dmg", "e_ap") + " 피해와 {e_s1}~{e_s3}초 " + R + "기절" + E +
                  "(멀리 날수록 길게). 이어서 " + O + "파멸의 눈" + E + "이 적 챔피언에게 떨어져 " + mag("w_dmg", "w_ap") + " 피해와 " +
                  R + "둔화" + E + ", 중심은 +{w_mid}%.",
        "ult": "승천해 제자리에서 정신을 집중하며 먼 적 챔피언에게 비전 포격을 " + A + "{r_n}회" + E + " 퍼붓습니다. 경고 후 폭발해 " +
               mag("r_dmg", "r_ap") + "의 " + M + "마법 피해" + E + ", 챔피언 적중마다 이후 포격 +{r_ramp}%. 군중 제어에 끊깁니다.",
        "names": ("비전 파동", "충격 구체", "비전 의식"),
    },
    "ja": {
        "name": "ゼラス",
        "attack": "魔力のオーブで攻撃。パッシブ " + O + "マナサージ" + E + "：" + A + "{p_wait}秒" + E + "ごとに次の攻撃が" +
                  mag("p_dmg", "p_ap") + "の追加" + M + "魔法ダメージ" + E + "、通常スキルのクールダウン{p_cut}%短縮。ユニットを倒すたび"
                  "{p_step}秒早まる。",
        "skill": "チャージ後に貫通する光線を放ち、直線上の敵に" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "。敵チャンピオンが"
                 "近いとフルチャージで長射程、ミニオンだけなら素早く{q_quick}%。",
        "skill2": O + "ショックオーブ" + E + "：最初に当たった敵に" + mag("e_dmg", "e_ap") + "、{e_s1}~{e_s3}秒" + R + "スタン" + E +
                  "（遠いほど長い）。続いて" + O + "デストラクションアイ" + E + "が敵チャンピオンに落ち" + mag("w_dmg", "w_ap") + "と" +
                  R + "スロウ" + E + "、中心は+{w_mid}%。",
        "ult": "昇華してその場で詠唱し、遠くの敵チャンピオンへ魔法砲撃を" + A + "{r_n}回" + E + "。予告の後に爆発し" + mag("r_dmg", "r_ap") +
               "の" + M + "魔法ダメージ" + E + "、チャンピオン命中ごとに以降+{r_ramp}%。CCで中断。",
        "names": ("アルカノパルス", "ショックオーブ", "アーケーンライト"),
    },
}

C = "league_xerath_sfx_"
V = "league_xerath_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_xerath_a_cast": [(C + "cast", 0.45, 0.0)],
    "league_xerath_a_hit": [(C + "hit", 0.35, 0.0)],
    "league_xerath_p_surge": [(C + "surge", 0.5, 0.0)],
    "league_xerath_p_hit": [(C + "surge_hit", 0.5, 0.0)],
    "league_xerath_q_charge": [(C + "q_charge", 0.5, 0.0)],
    "league_xerath_q_fire": [(C + "q_fire", 0.6, 0.0)],
    "league_xerath_q_hit": [(C + "q_hit", 0.3, 0.0)],
    "league_xerath_e_cast": [(C + "e_cast", 0.55, 0.0)],
    "league_xerath_e_hit": [(C + "e_hit", 0.5, 0.0)],
    "league_xerath_w_cast": [(C + "w_cast", 0.45, 0.0)],
    "league_xerath_w_blast": [(C + "w_blast", 0.6, 0.0)],
    "league_xerath_w_hit": [(C + "q_hit", 0.25, 0.0)],
    "league_xerath_r_cast": [(C + "r_cast", 0.6, 0.0)],
    "league_xerath_r_shot": [(C + "r_shot", 0.45, 0.0)],
    "league_xerath_r_blast": [(C + "r_blast", 0.55, 0.0)],
    "league_xerath_r_hit": [(C + "q_hit", 0.3, 0.0)],
    "league_xerath_r_end": [(C + "r_end", 0.45, 0.0)],
    "league_xerath_vo_q": [(V + "q", 0.8, 0.0)],
    "league_xerath_vo_e": [(V + "e", 0.85, 0.0)],
    "league_xerath_vo_r": [(V + "r", 0.9, 0.1)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "q_dmg", "q_ap", "q_quick", "e_dmg", "e_ap", "w_dmg", "w_ap", "w_mid", "r_n",
                           "r_dmg", "r_ap", "r_ramp")}
    v["p_wait"] = secs(p["p_step"] * 4)
    v["p_step"] = secs(p["p_step"])
    v["p_cut"] = round(100 - 10000 / (100 + p["p_cdr"]))
    v["e_s1"], v["e_s3"] = secs(p["e_stun1"]), secs(p["e_stun3"])
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
    if "Xerath" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Xerath. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
