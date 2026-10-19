"""Rammus's text (5 languages), sound_info files and his keys in the shared files, numbers from build_rammus.P.

    python tools/kit/setup_rammus.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_rammus in every language, description + skill_name),
sound/sfx/league_rammus_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Rammus named). Only his keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 拉莫斯 (披甲龙龟): 锥刺甲壳, 动力冲刺, 尖刺防御, 狂乱嘲讽, 冲天猛撞; zh_TW 拉姆斯 (披甲龍龜):
錐刺甲殼, 動力衝刺, 尖刺防禦, 披甲怒嘲, 飛天動地; ja ラムス: トゲトゲ, ころころ, かたくなる, ぴりぴり, どーんどーん; ko 람머스:
가시박힌 껍질, 대회전, 몸 말아 웅크리기, 광란의 도발, 지진 폭격.
Slots: skill = Q Powerball, skill2 = E Frenzying Taunt, ult = R Soaring Slam; the passive Spiked Shell and W Defensive
Ball Curl (cast by the watch) are in the attack's text. No combo sentence in any text (the user's rule). The main
pack's rules are the ones written (the shell scales with max health, W returns a share of every hit); the add-on
league_rammus pays them from his armour and rolls Powerball League's way, and says so itself.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_rammus import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_rammus"
VERSION = "0.163.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: the face point on his face under the shell's hood (his eyes are 14.5 px over the soles, the crown -29:
# lint_mod allows 10 under the crown, so -19, the hood's lip over the eyes; ppu_restyle face_to the same). No
# banpick_center: his highest lo_idle row is -24.7 over the frame centre, under the card canvas's -28
VIEW = {"face": {"x": 5, "y": -19}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def shell(d, r, h):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E} + {HPi}{M}{{{h}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "拉莫斯",
        "attack": "翻身撞击。" + O + "锥刺甲壳" + E + "：普攻多造成" + shell("p_dmg", "p_ap", "p_hp") + "魔法伤害。" + O + "尖刺防御" + E +
                  "：敌方英雄靠近时蜷起来，" + A + "{w_t}秒" + E + "内双抗+{w_def}%，反弹{w_ref}%受到的伤害。",
        "skill": "缩成球滚向目标，撞上时对周围造成" + mag("q_dmg", "q_ap") + "魔法伤害，" + R + "击退" + E + "并" + R + "减速{q_slow}%" + E +
                 A + "{q_slow_t}秒" + E + "。",
        "skill2": R + "嘲讽" + E + "一名敌方英雄" + A + "{e_taunt}秒" + E + "。",
        "ult": "跳起砸向敌方英雄，对区域造成" + mag("r_dmg", "r_ap") + "魔法伤害并" + R + "减速{r_slow}%" + E + "，之后余震{r_pulses}次；"
               "刚滚完动力冲刺时，中心的敌人再受一次冲刺伤害并" + R + "击飞{r_up}秒" + E + "。",
        "names": ("动力冲刺", "狂乱嘲讽", "冲天猛撞"),
    },
    "zh-hant": {
        "name": "拉姆斯",
        "attack": "翻身撞擊。" + O + "錐刺甲殼" + E + "：普攻多造成" + shell("p_dmg", "p_ap", "p_hp") + "魔法傷害。" + O + "尖刺防禦" + E +
                  "：敵方英雄靠近時蜷起來，" + A + "{w_t}秒" + E + "內雙抗+{w_def}%，反彈{w_ref}%受到的傷害。",
        "skill": "縮成球滾向目標，撞上時對周圍造成" + mag("q_dmg", "q_ap") + "魔法傷害，" + R + "擊退" + E + "並" + R + "緩速{q_slow}%" + E +
                 A + "{q_slow_t}秒" + E + "。",
        "skill2": R + "嘲諷" + E + "一名敵方英雄" + A + "{e_taunt}秒" + E + "。",
        "ult": "跳起砸向敵方英雄，對區域造成" + mag("r_dmg", "r_ap") + "魔法傷害並" + R + "緩速{r_slow}%" + E + "，之後餘震{r_pulses}次；"
               "剛滾完動力衝刺時，中心的敵人再受一次衝刺傷害並" + R + "擊飛{r_up}秒" + E + "。",
        "names": ("動力衝刺", "披甲怒嘲", "飛天動地"),
    },
    "en": {
        "name": "Rammus",
        "attack": "A tumbling slam. " + O + "Spiked Shell" + E + ": attacks deal " + shell("p_dmg", "p_ap", "p_hp") + " " + M +
                  "magic damage" + E + " more. " + O + "Defensive Ball Curl" + E + ": with an enemy champion close he curls up: for " + A +
                  "{w_t}s" + E + " +{w_def}% armour and magic resist, and {w_ref}% of the damage he takes is returned.",
        "skill": "Curls into a ball and rolls at the target; on impact nearby enemies take " + mag("q_dmg", "q_ap") + " " + M +
                 "magic damage" + E + ", are " + R + "knocked back" + E + " and " + R + "slowed {q_slow}%" + E + " for " + A + "{q_slow_t}s" +
                 E + ".",
        "skill2": R + "Taunts" + E + " an enemy champion for " + A + "{e_taunt}s" + E + ".",
        "ult": "Leaps onto an enemy champion: the area takes " + mag("r_dmg", "r_ap") + " " + M + "magic damage" + E + " and is " + R +
               "slowed {r_slow}%" + E + ", then {r_pulses} aftershocks. Right after a Powerball the centre also takes Powerball's damage "
               "and is " + R + "knocked up {r_up}s" + E + ".",
        "names": ("Powerball", "Frenzying Taunt", "Soaring Slam"),
    },
    "ko": {
        "name": "람머스",
        "attack": "몸통 박치기. " + O + "가시박힌 껍질" + E + ": 기본 공격이 " + shell("p_dmg", "p_ap", "p_hp") + " 마법 피해 추가. " + O +
                  "몸 말아 웅크리기" + E + ": 적 챔피언이 가까우면 웅크려 " + A + "{w_t}초" + E + " 동안 방어력·마법 저항력 +{w_def}%, "
                  "받은 피해의 {w_ref}% 반사.",
        "skill": "몸을 말아 대상에게 굴러가 부딪히면 주변 적에게 " + mag("q_dmg", "q_ap") + " 마법 피해, " + R + "밀쳐내기" + E + ", " + A +
                 "{q_slow_t}초" + E + " " + R + "{q_slow}% 둔화" + E + ".",
        "skill2": "적 챔피언 하나를 " + A + "{e_taunt}초" + E + " " + R + "도발" + E + ".",
        "ult": "적 챔피언에게 뛰어올라 내려찍어 범위에 " + mag("r_dmg", "r_ap") + " 마법 피해와 " + R + "{r_slow}% 둔화" + E + ", 이어서 여진 "
               "{r_pulses}회. 대회전 직후라면 중심의 적은 대회전 피해를 한 번 더 받고 " + R + "{r_up}초 에어본" + E + ".",
        "names": ("대회전", "광란의 도발", "지진 폭격"),
    },
    "ja": {
        "name": "ラムス",
        "attack": "体当たり。" + O + "トゲトゲ" + E + "：通常攻撃に" + shell("p_dmg", "p_ap", "p_hp") + "の魔法ダメージ追加。" + O + "かたくなる" +
                  E + "：敵チャンピオンが近いと丸まり、" + A + "{w_t}秒" + E + "物防・魔防+{w_def}%、受けたダメージの{w_ref}%を反射。",
        "skill": "丸まって対象へ転がり、ぶつかると周りの敵に" + mag("q_dmg", "q_ap") + "の魔法ダメージ、" + R + "ノックバック" + E + "と" + A +
                 "{q_slow_t}秒" + E + "の" + R + "{q_slow}%スロウ" + E + "。",
        "skill2": "敵チャンピオン1体を" + A + "{e_taunt}秒" + E + R + "挑発" + E + "。",
        "ult": "敵チャンピオンへ跳び上がって叩きつけ、範囲に" + mag("r_dmg", "r_ap") + "の魔法ダメージと" + R + "{r_slow}%スロウ" + E + "、続けて"
               "余震{r_pulses}回。ころころの直後なら中心の敵はころころのダメージをもう一度受け" + R + "{r_up}秒ノックアップ" + E + "。",
        "names": ("ころころ", "ぴりぴり", "どーんどーん"),
    },
}

C = "league_rammus_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_rammus_a_swing": [(C + "a_swing", 0.3, 0.0)],
    "league_rammus_a_hit": [(C + "a_hit", 0.4, 0.0)],
    "league_rammus_q": [(C + "q", 0.45, 0.0)],
    "league_rammus_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_rammus_w": [(C + "w", 0.45, 0.0)],
    "league_rammus_e": [(C + "e", 0.45, 0.0)],
    "league_rammus_e_hit": [(C + "e_hit", 0.4, 0.0)],
    "league_rammus_r": [(C + "r", 0.45, 0.0)],
    "league_rammus_r_land": [(C + "r_land", 0.55, 0.0)],
    "league_rammus_r_hit": [(C + "r_hit", 0.45, 0.0)],
    "league_rammus_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_rammus_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_rammus_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_rammus_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "p_hp", "w_def", "w_ref", "q_dmg", "q_ap", "q_slow", "r_dmg", "r_ap",
                           "r_slow", "r_pulses")}
    for k in ("w_t", "q_slow_t", "e_taunt", "r_up"):
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
    if "Rammus" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Rammus. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
