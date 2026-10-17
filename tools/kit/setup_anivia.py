"""Anivia's text (5 languages), sound_info files and her keys in the shared files, numbers from build_anivia.P.

    python tools/kit/setup_anivia.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_anivia in every language, description + skill_name),
sound/sfx/league_anivia_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Anivia named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 艾尼维亚 / 冰晶凤凰: 寒霜涅槃, 寒冰闪耀, 寒冰屏障, 霜寒刺骨, 冰川风暴; zh_TW 艾妮維亞: 寒霜涅槃,
寒冰閃耀, 寒冰屏障, 霜寒刺骨, 冰川風暴; ja アニビア: 再誕, フラッシュフロスト, アイスウォール, フロストバイト, ブリザード; ko 애니비아: 환생,
냉기 폭발, 결정화, 동상, 얼음 폭풍.
Slots: skill = Q Flash Frost (with W Crystallize), skill2 = E Frostbite, ult = R Glacial Storm; Rebirth in the attack's
text, said to need the add-on (the user: 「主包不做蛋，寒霜涅槃只放在扩展包里，说明写清楚」). No combo sentence in any text
(the user's rule).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_anivia import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_anivia"
VERSION = "0.138.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: set from tfm2_ase.py face once the sheet exists
VIEW = {"face": {"x": 4, "y": -30}, "center": {"x": 0, "y": -14}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "艾尼维亚",
        "attack": "冰弹。" + O + "寒霜涅槃" + E + "（需安装扩展包）：受到致命伤害时变成冰蛋" + A + "{egg_t}秒" + E + "，蛋没被打碎就复活；冷却" +
                  A + "{egg_cd}秒" + E + "。",
        "skill": "射出冰球，穿过的敌人受到" + mag("q_pass", "q_pass_r") + "并" + R + "减速{q_slow}%" + E + "；碰到英雄或到达落点时引爆：" +
                 mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "并" + R + "眩晕{q_stun}秒" + E + "。" + O + "寒冰屏障" + E + "：晕到英雄时在原地竖起冰墙" +
                 A + "{w_t}秒" + E + "，敌人过不去。",
        "skill2": "冰锥造成" + mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "；目标被控制时，或冰川风暴成形后，伤害翻倍。",
        "ult": "在敌方英雄处召唤暴风雪" + A + "{r_t}秒" + E + "，逐渐变大；每" + A + "{r_p}秒" + E + "造成" + mag("r_dmg", "r_ratio") + M + "魔法伤害" + E +
               "并" + R + "减速" + E + "，成形后伤害×" + A + "{r_full}" + E + "。有被控制的敌方英雄或2名敌方英雄在身边时才放。",
        "names": ("寒冰闪耀", "霜寒刺骨", "冰川风暴"),
    },
    "zh-hant": {
        "name": "艾妮維亞",
        "attack": "冰彈。" + O + "寒霜涅槃" + E + "（需安裝擴充包）：受到致命傷害時變成冰蛋" + A + "{egg_t}秒" + E + "，蛋沒被打碎就復活；冷卻" +
                  A + "{egg_cd}秒" + E + "。",
        "skill": "射出冰球，穿過的敵人受到" + mag("q_pass", "q_pass_r") + "並" + R + "緩速{q_slow}%" + E + "；碰到英雄或到達落點時引爆：" +
                 mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "並" + R + "暈眩{q_stun}秒" + E + "。" + O + "寒冰屏障" + E + "：暈到英雄時在原地豎起冰牆" +
                 A + "{w_t}秒" + E + "，敵人過不去。",
        "skill2": "冰錐造成" + mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "；目標被控制時，或冰川風暴成形後，傷害加倍。",
        "ult": "在敵方英雄處召喚暴風雪" + A + "{r_t}秒" + E + "，逐漸變大；每" + A + "{r_p}秒" + E + "造成" + mag("r_dmg", "r_ratio") + M + "魔法傷害" + E +
               "並" + R + "緩速" + E + "，成形後傷害×" + A + "{r_full}" + E + "。有被控制的敵方英雄或2名敵方英雄在身邊時才施放。",
        "names": ("寒冰閃耀", "霜寒刺骨", "冰川風暴"),
    },
    "en": {
        "name": "Anivia",
        "attack": "An ice bolt. " + O + "Rebirth" + E + " (needs the add-on): lethal damage turns her into an egg for " + A + "{egg_t}s" + E +
                  "; if the egg survives she is reborn. Cooldown " + A + "{egg_cd}s" + E + ".",
        "skill": "An ice ball: " + mag("q_pass", "q_pass_r") + " " + M + "magic damage" + E + " and a " + R + "{q_slow}% slow" + E +
                 " to enemies it passes; it bursts on the first champion or at its spot for " + mag("q_dmg", "q_ratio") + " " + M +
                 "magic damage" + E + " and a " + R + "{q_stun}s stun" + E + ". " + O + "Crystallize" + E + ": a champion stunned, an ice wall "
                 "rises there for " + A + "{w_t}s" + E + " that enemies cannot cross.",
        "skill2": "An ice shard for " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + ", doubled if the target is crowd "
                  "controlled or her Glacial Storm has formed.",
        "ult": "A blizzard on an enemy champion for " + A + "{r_t}s" + E + ", growing as it lasts: every " + A + "{r_p}s" + E + " " +
               mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + " and a " + R + "slow" + E + ", x" + A + "{r_full}" + E +
               " once formed. Cast on a crowd-controlled champion or with 2 enemy champions near her.",
        "names": ("Flash Frost", "Frostbite", "Glacial Storm"),
    },
    "ko": {
        "name": "애니비아",
        "attack": "얼음 화살. " + O + "환생" + E + "(확장팩 필요): 치명적인 피해를 받으면 " + A + "{egg_t}초" + E + "간 알로 변하고, 알이 버티면 "
                  "부활. 재사용 대기시간 " + A + "{egg_cd}초" + E + ".",
        "skill": "얼음 구체: 지나간 적에게 " + mag("q_pass", "q_pass_r") + " 피해와 " + R + "{q_slow}% 둔화" + E + "; 첫 챔피언이나 목표 지점에서 폭발해 " +
                 mag("q_dmg", "q_ratio") + "의 " + M + "마법 피해" + E + "와 " + R + "{q_stun}초 기절" + E + ". " + O + "결정화" + E +
                 ": 챔피언을 기절시키면 그 자리에 " + A + "{w_t}초" + E + "간 적이 넘을 수 없는 얼음벽.",
        "skill2": "얼음 조각으로 " + mag("e_dmg", "e_ratio") + "의 " + M + "마법 피해" + E + ". 대상이 군중 제어 상태이거나 얼음 폭풍이 완성되면 2배.",
        "ult": "적 챔피언 위치에 " + A + "{r_t}초" + E + "간 점점 커지는 눈보라: " + A + "{r_p}초" + E + "마다 " + mag("r_dmg", "r_ratio") +
               "의 " + M + "마법 피해" + E + "와 " + R + "둔화" + E + ", 완성되면 " + A + "{r_full}배" + E + ". 군중 제어된 챔피언이나 적 챔피언 2명이 가까울 때 사용.",
        "names": ("냉기 폭발", "동상", "얼음 폭풍"),
    },
    "ja": {
        "name": "アニビア",
        "attack": "氷の弾。" + O + "再誕" + E + "（拡張パック必要）：致死ダメージで" + A + "{egg_t}秒" + E + "卵になり、卵が耐えれば復活。クールダウン" +
                  A + "{egg_cd}秒" + E + "。",
        "skill": "氷の球：通過した敵に" + mag("q_pass", "q_pass_r") + "と" + R + "スロウ{q_slow}%" + E + "。最初のチャンピオンか着弾点で炸裂し" +
                 mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "と" + R + "スタン{q_stun}秒" + E + "。" + O + "アイスウォール" + E +
                 "：スタンさせるとそこに" + A + "{w_t}秒" + E + "敵が越えられない氷の壁。",
        "skill2": "氷の欠片で" + mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" + E + "。対象が行動妨害中か、ブリザード完成後は2倍。",
        "ult": "敵チャンピオンの位置に" + A + "{r_t}秒" + E + "広がる吹雪：" + A + "{r_p}秒" + E + "毎に" + mag("r_dmg", "r_ratio") + "の" + M +
               "魔法ダメージ" + E + "と" + R + "スロウ" + E + "、完成後は×" + A + "{r_full}" + E + "。行動妨害中の敵か敵2体が近い時に使う。",
        "names": ("フラッシュフロスト", "フロストバイト", "ブリザード"),
    },
}

C = "league_anivia_sfx_"
V = "league_anivia_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_anivia_a": [(C + "a", 0.35, 0.0)],
    "league_anivia_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_anivia_q": [(C + "q", 0.45, 0.0)],
    "league_anivia_q_pass": [(C + "q_pass", 0.3, 0.0)],
    "league_anivia_q_blast": [(C + "q_blast", 0.55, 0.0)],
    "league_anivia_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_anivia_w": [(C + "w", 0.55, 0.0)],
    "league_anivia_e": [(C + "e", 0.45, 0.0)],
    "league_anivia_e_hit": [(C + "e_hit", 0.45, 0.0)],
    "league_anivia_r": [(C + "r", 0.5, 0.0)],
    "league_anivia_r_storm": [(C + "r_storm", 0.5, 0.0)],
    "league_anivia_r_hit": [(C + "r_hit", 0.2, 0.0)],
    "league_anivia_p_egg": [(C + "p_egg", 0.6, 0.0)],
    "league_anivia_p_hatch": [(C + "p_hatch", 0.6, 0.0)],
    "league_anivia_vo_q": [(V + "q", 0.85, 0.0)],
    "league_anivia_vo_w": [(V + "w", 0.85, 0.0)],
    "league_anivia_vo_e": [(V + "e", 0.85, 0.0)],
    "league_anivia_vo_r": [(V + "r", 0.9, 0.0)],
    "league_anivia_vo_p": [(V + "p", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("q_pass", "q_pass_r", "q_slow", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "r_dmg", "r_ratio",
                           "r_full")}
    for k in ("q_stun", "w_t", "r_t", "r_p", "egg_t", "egg_cd"):
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
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 - the idle's top over the frame centre)")
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
    if "Anivia" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Anivia. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
