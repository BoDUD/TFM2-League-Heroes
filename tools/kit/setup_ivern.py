"""Ivern's text (5 languages), sound_info files and his keys in the shared files, numbers from build_ivern.P.

    python tools/kit/setup_ivern.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_ivern in every language, description + skill_name),
sound/sfx/league_ivern_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Ivern named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 艾翁 (翠神): 森林之友; 根深敌固, 揠苗助攻, 种豆得瓜, 小菊！; zh_TW 埃爾文: 森林之友; 盤根束縛,
茂林春生, 守護種子, 黛西！; ja アイバーン: モリノトモダチ; ネッコナゲ, シゲミヅクリ, タネバクダン, デイジー！; ko 아이번: 숲의 친구; 덩굴뿌리,
수풀 가꾸기, 보호의 씨앗, 데이지!.
Slots: skill = Triggerseed, skill2 = Rootcaller, ult = Daisy!; Brushmaker (the passive) in the attack's text. No combo
sentence in any text (the user's rule); the README says them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_ivern import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_ivern"
VERSION = "0.195.0"     # the next free number above main 0.194.0 (Hwei #466) (2026-10-22)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card (set at export:
# tools/art/bp_card_audit.py)
VIEW = {"face": {"x": 4, "y": -29}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


def sh(x):
    return G + x + E


TEXT = {
    "zh-hans": {
        "name": "艾翁",
        "attack": "扔出一颗种子。" + n("揠苗助攻") + "：每次种豆得瓜都在脚下长出草丛" + t("{w_t}秒") + "，草丛里的队友攻击+{w_atk}%，"
                  "他自己的普攻追加" + mag("w_dmg", "w_ratio") + "魔法伤害。",
        "skill": "给身边的队友（没有就给自己）种下种子：" + sh("护盾") + mag("e_sh", "e_sh_r") + "，" + t("{e_t}秒") + "后爆开，对周围敌人造成" +
                 mag("e_dmg", "e_ratio") + "魔法伤害并减速{e_slow}%。",
        "skill2": "甩出荆棘藤，造成" + mag("q_dmg", "q_ratio") + "魔法伤害并" + cc("禁锢") + t("{q_root}秒") + "；身边的队友移速+{q_ms}%冲过去。",
        "ult": "召唤" + n("小菊") + "落到敌方英雄身上，" + cc("击飞") + "并造成" + mag("r_drop", "r_drop_r") + "魔法伤害；之后" + t("{r_t}秒") +
               "内每秒一拳" + mag("r_dmg", "r_ratio") + "，每第三拳砸地再加" + mag("r_slam", "r_slam_r") + "并" + cc("击飞") + "。",
        "names": ("种豆得瓜", "根深敌固", "小菊！"),
    },
    "zh-hant": {
        "name": "埃爾文",
        "attack": "扔出一顆種子。" + n("茂林春生") + "：每次施放守護種子都在腳下長出草叢" + t("{w_t}秒") + "，草叢裡的隊友攻擊+{w_atk}%，"
                  "他自己的普攻追加" + mag("w_dmg", "w_ratio") + "魔法傷害。",
        "skill": "替身邊的隊友（沒有就替自己）種下種子：" + sh("護盾") + mag("e_sh", "e_sh_r") + "，" + t("{e_t}秒") + "後爆開，對周圍敵人造成" +
                 mag("e_dmg", "e_ratio") + "魔法傷害並緩速{e_slow}%。",
        "skill2": "甩出荊棘藤，造成" + mag("q_dmg", "q_ratio") + "魔法傷害並" + cc("定身") + t("{q_root}秒") + "；身邊的隊友移速+{q_ms}%衝過去。",
        "ult": "召喚" + n("黛西") + "落到敵方英雄身上，" + cc("擊飛") + "並造成" + mag("r_drop", "r_drop_r") + "魔法傷害；之後" + t("{r_t}秒") +
               "內每秒一拳" + mag("r_dmg", "r_ratio") + "，每第三拳砸地再加" + mag("r_slam", "r_slam_r") + "並" + cc("擊飛") + "。",
        "names": ("守護種子", "盤根束縛", "黛西！"),
    },
    "en": {
        "name": "Ivern",
        "attack": "Throws a seed. " + n("Brushmaker") + ": each Triggerseed grows a brush at his feet for " + t("{w_t}s") +
                  "; allies in it gain +{w_atk}% attack and his own attacks deal " + mag("w_dmg", "w_ratio") + " magic damage more.",
        "skill": "Plants a seed on the ally beside him (else on himself): a " + sh("shield") + " of " + mag("e_sh", "e_sh_r") +
                 " that bursts after " + t("{e_t}s") + ", dealing " + mag("e_dmg", "e_ratio") + " magic damage to the enemies around "
                 "and slowing them {e_slow}%.",
        "skill2": "Lashes out a vine: " + mag("q_dmg", "q_ratio") + " magic damage and a " + cc("root") + " for " + t("{q_root}s") +
                  "; the allies beside him rush in with +{q_ms}% move speed.",
        "ult": "Calls " + n("Daisy") + " down on an enemy champion: a " + cc("knock-up") + " and " + mag("r_drop", "r_drop_r") +
               " magic damage, then a punch every second for " + t("{r_t}s") + " (" + mag("r_dmg", "r_ratio") + "), every third a "
               "slam for " + mag("r_slam", "r_slam_r") + " more that " + cc("knocks up") + ".",
        "names": ("Triggerseed", "Rootcaller", "Daisy!"),
    },
    "ko": {
        "name": "아이번",
        "attack": "씨앗을 던진다. " + n("수풀 가꾸기") + ": 보호의 씨앗마다 발밑에 수풀이 " + t("{w_t}초") + " 자라 안의 아군 공격력 "
                  "+{w_atk}%, 그의 기본 공격은 " + mag("w_dmg", "w_ratio") + " 마법 피해 추가.",
        "skill": "곁의 아군(없으면 자신)에게 씨앗을 심는다: " + sh("보호막") + " " + mag("e_sh", "e_sh_r") + ", " + t("{e_t}초") +
                 " 뒤 터져 주변 적에게 " + mag("e_dmg", "e_ratio") + " 마법 피해와 {e_slow}% 둔화.",
        "skill2": "덩굴을 휘둘러 " + mag("q_dmg", "q_ratio") + " 마법 피해와 " + t("{q_root}초") + " " + cc("속박") +
                  "; 곁의 아군은 이동 속도 +{q_ms}%로 달려든다.",
        "ult": n("데이지") + "를 적 챔피언 위에 불러 " + cc("공중에 띄우고") + " " + mag("r_drop", "r_drop_r") + " 마법 피해, 이후 " +
               t("{r_t}초") + " 동안 매초 주먹 " + mag("r_dmg", "r_ratio") + ", 세 번째마다 내려찍어 " + mag("r_slam", "r_slam_r") +
               " 추가와 " + cc("에어본") + ".",
        "names": ("보호의 씨앗", "덩굴뿌리", "데이지!"),
    },
    "ja": {
        "name": "アイバーン",
        "attack": "種を投げる。" + n("シゲミヅクリ") + "：タネバクダンのたびに足元へ茂みが" + t("{w_t}秒") + "生え、中の味方は攻撃力+{w_atk}%、"
                  "自身の通常攻撃は" + mag("w_dmg", "w_ratio") + "の魔法ダメージを追加。",
        "skill": "そばの味方（いなければ自身）に種を植える：" + sh("シールド") + mag("e_sh", "e_sh_r") + "、" + t("{e_t}秒") + "後に弾けて周囲の敵に" +
                 mag("e_dmg", "e_ratio") + "の魔法ダメージと{e_slow}%スロウ。",
        "skill2": "ツタを振るい" + mag("q_dmg", "q_ratio") + "の魔法ダメージと" + t("{q_root}秒") + cc("スネア") + "。そばの味方は移動速度+{q_ms}%で駆けつける。",
        "ult": n("デイジー") + "を敵英雄の上に呼び" + cc("ノックアップ") + "と" + mag("r_drop", "r_drop_r") + "の魔法ダメージ、その後" + t("{r_t}秒") +
               "毎秒パンチ" + mag("r_dmg", "r_ratio") + "、3発ごとに叩きつけて" + mag("r_slam", "r_slam_r") + "追加と" + cc("ノックアップ") + "。",
        "names": ("タネバクダン", "ネッコナゲ", "デイジー！"),
    },
}

C = "league_ivern_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the sfx toward Lux's 0.8 (the attack lower: it comes often; Daisy's punches
# every second a little lower too), the voice as the other heroes'
SOUNDS = {f"league_ivern_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("w", 0.6), ("e", 0.75), ("e_burst", 0.8), ("e_hit", 0.6), ("q", 0.8), ("q_hit", 0.8),
    ("r", 0.85), ("r_drop", 0.9), ("r_punch", 0.65), ("r_slam", 0.85), ("vo_e", 0.85), ("vo_q", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("w_atk", "w_dmg", "w_ratio", "e_sh", "e_sh_r", "e_dmg", "e_ratio", "e_slow", "q_dmg",
                           "q_ratio", "q_ms", "r_drop", "r_drop_r", "r_dmg", "r_ratio", "r_slam", "r_slam_r")}
    for k in ("w_t", "e_t", "q_root"):
        v[k] = secs(p[k])
    v["r_t"] = secs(p["r_t"] - 1)            # the casted effect lasts one tick past its last punch
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
    for lang, tx in TEXT.items():
        d = {"name": tx["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = tx[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), tx["names"])))
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
        bad |= any(m > TOOLTIP_MAX[lang] for m in lens.values())
        print(lang, " ".join(f"{k}:{m}/{TOOLTIP_MAX[lang]}" for k, m in lens.items()))
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
    if "Ivern" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Ivern. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
