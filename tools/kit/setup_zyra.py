"""Zyra's text (5 languages), sound_info files and her keys in the shared files, numbers from build_zyra.P.

    python tools/kit/setup_zyra.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_zyra in every language, description + skill_name),
sound/sfx/league_zyra_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Zyra named). Only her keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 婕拉 (荆棘之兴): 荆棘花园, 致命棘刺, 狂野生长, 缠绕之根, 绞杀之藤; zh_TW 枷蘿 (荊棘漫遊者):
荊棘花園, 致死棘刺, 狂暴蔓延, 索命棘蔓, 致命綻放; ja ザイラ: 茨の楽園, 死華の棘, 狂い咲き, 捕縛の根, 茨のゆりかご; ko 자이라: 가시 정원,
치명적인 가시, 맹렬한 성장, 휘감는 뿌리, 올가미 덩굴. The plants as the spells' own texts name them: Thorn Spitter / Vine Lasher,
棘刺噴吐草 / 棘蔓鞭笞草, 棘吹草 / 棘鞭草, 가시 발사 꽃 / 덩굴 채찍손; zh_CN's text names none: 荆棘喷射者 / 藤蔓鞭击者 (the usual names).
Slots: skill = Q Deadly Spines, skill2 = E Grasping Roots, ult = R Stranglethorns; the passive Garden of Thorns and W
Rampant Growth are in the attack's text (every Q and E plants a seed that grows at once). No combo sentence in any
text (the user's rule).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_zyra import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_zyra"
VERSION = "0.177.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
E = "<>"
# champion_view: provisional until the sprite (tfm2_ase.py face)
VIEW = {"face": {"x": 1, "y": -30}, "center": {"x": 0, "y": -15}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


TEXT = {
    "zh-hans": {
        "name": "婕拉",
        "attack": "甩出一颗荆棘种子。" + O + "荆棘花园" + E + "：她每次放Q、E都先种下一颗种子，长成植物作战" + t("{t_life}秒") +
                  "，每" + t("{t_per}秒") + "攻击一个敌人，造成" + mag("t_dmg", "t_ratio") + "魔法伤害。",
        "skill": "地面炸出棘刺，范围内的敌人受到" + mag("q_dmg", "q_ratio") + "魔法伤害。种子长成" + O + "荆棘喷射者" + E + "，远距离攻击。",
        "skill2": "放出贯穿地面的藤蔓，路径上的敌人受到" + mag("e_dmg", "e_ratio") + "魔法伤害并被" + R + "禁锢" + E + t("{e_root}秒") +
                  "。种子长成" + O + "藤蔓鞭击者" + E + "，近距离攻击并减速{v_slow}%。",
        "ult": "召唤扭曲的密林，造成" + mag("r_dmg", "r_ratio") + "魔法伤害，" + t("{r_knock}秒") + "后" + R + "击飞" + E + "仍在其中的敌人" +
               t("{r_air}秒") + "。植物被激怒" + t("{r_rage}秒") + "，伤害提高{rage_up}%。",
        "names": ("致命棘刺", "缠绕之根", "绞杀之藤"),
    },
    "zh-hant": {
        "name": "枷蘿",
        "attack": "甩出一顆荊棘種子。" + O + "荊棘花園" + E + "：她每次施放Q、E都先種下一顆種子，長成植物作戰" + t("{t_life}秒") +
                  "，每" + t("{t_per}秒") + "攻擊一個敵人，造成" + mag("t_dmg", "t_ratio") + "魔法傷害。",
        "skill": "地面炸出棘刺，範圍內的敵人受到" + mag("q_dmg", "q_ratio") + "魔法傷害。種子長成" + O + "棘刺噴吐草" + E + "，遠距離攻擊。",
        "skill2": "射出貫穿地面的藤蔓，路徑上的敵人受到" + mag("e_dmg", "e_ratio") + "魔法傷害並被" + R + "定身" + E + t("{e_root}秒") +
                  "。種子長成" + O + "棘蔓鞭笞草" + E + "，近距離攻擊並緩速{v_slow}%。",
        "ult": "召喚扭曲的密林，造成" + mag("r_dmg", "r_ratio") + "魔法傷害，" + t("{r_knock}秒") + "後" + R + "擊飛" + E + "仍在其中的敵人" +
               t("{r_air}秒") + "。植物被激怒" + t("{r_rage}秒") + "，傷害提高{rage_up}%。",
        "names": ("致死棘刺", "索命棘蔓", "致命綻放"),
    },
    "en": {
        "name": "Zyra",
        "attack": "Flings a thorn seed. " + O + "Garden of Thorns" + E + ": each Q and E first plants a seed that grows into a "
                  "plant fighting for " + t("{t_life}s") + ", striking one enemy every " + t("{t_per}s") + " for " +
                  mag("t_dmg", "t_ratio") + " " + M + "magic damage" + E + ".",
        "skill": "Spines burst from the ground, dealing " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E +
                 " to enemies in the area. The seed grows a " + O + "Thorn Spitter" + E + " that fires from afar.",
        "skill2": "Vines run through the ground, dealing " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + " and " + R +
                  "rooting" + E + " every enemy on the line for " + t("{e_root}s") + ". The seed grows a " + O + "Vine Lasher" + E +
                  " whose short-range strikes slow by {v_slow}%.",
        "ult": "Summons a twisted thicket that deals " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + " and after " +
               t("{r_knock}s") + " " + R + "knocks up" + E + " the enemies still in it for " + t("{r_air}s") + ". Her plants are "
               "enraged for " + t("{r_rage}s") + ": {rage_up}% more damage.",
        "names": ("Deadly Spines", "Grasping Roots", "Stranglethorns"),
    },
    "ko": {
        "name": "자이라",
        "attack": "가시 씨앗을 던진다. " + O + "가시 정원" + E + ": Q와 E를 쓸 때마다 먼저 씨앗을 심어 " + t("{t_life}초") +
                  " 동안 싸우는 식물로 키운다. 식물은 " + t("{t_per}초") + "마다 적 하나에게 " + mag("t_dmg", "t_ratio") + " 마법 피해.",
        "skill": "지면에서 가시가 폭발해 범위 안의 적에게 " + mag("q_dmg", "q_ratio") + " 마법 피해. 씨앗은 원거리에서 공격하는 " + O +
                 "가시 발사 꽃" + E + "이 된다.",
        "skill2": "지면을 뚫는 덩굴로 직선상의 적에게 " + mag("e_dmg", "e_ratio") + " 마법 피해를 입히고 " + t("{e_root}초") + " " + R +
                  "속박" + E + ". 씨앗은 근거리에서 공격하며 {v_slow}% 둔화시키는 " + O + "덩굴 채찍손" + E + "이 된다.",
        "ult": "뒤틀린 덤불을 불러 " + mag("r_dmg", "r_ratio") + " 마법 피해, " + t("{r_knock}초") + " 뒤 안에 남은 적을 " +
               t("{r_air}초") + " " + R + "에어본" + E + ". 식물이 " + t("{r_rage}초") + " 동안 격노해 피해 {rage_up}% 증가.",
        "names": ("치명적인 가시", "휘감는 뿌리", "올가미 덩굴"),
    },
    "ja": {
        "name": "ザイラ",
        "attack": "トゲの種を投げる。" + O + "茨の楽園" + E + "：QとEを使うたび先に種を植え、" + t("{t_life}秒") + "戦う植物に育てる。植物は" +
                  t("{t_per}秒") + "ごとに敵1体に" + mag("t_dmg", "t_ratio") + "の魔法ダメージ。",
        "skill": "地面からトゲが弾け、範囲内の敵に" + mag("q_dmg", "q_ratio") + "の魔法ダメージ。種は遠距離から攻撃する" + O + "棘吹草" + E +
                 "になる。",
        "skill2": "地中を伸びるツタが直線上の敵に" + mag("e_dmg", "e_ratio") + "の魔法ダメージを与え" + t("{e_root}秒") + R + "移動不能" + E +
                  "。種は近距離を攻撃し{v_slow}%スロウを与える" + O + "棘鞭草" + E + "になる。",
        "ult": "ねじれた茂みを呼び" + mag("r_dmg", "r_ratio") + "の魔法ダメージ、" + t("{r_knock}秒") + "後に中の敵を" + t("{r_air}秒") + R +
               "打ち上げ" + E + "。植物が" + t("{r_rage}秒") + "激昂しダメージ{rage_up}%増加。",
        "names": ("死華の棘", "捕縛の根", "茨のゆりかご"),
    },
}

C = "league_zyra_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {f"league_zyra_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.3), ("a_hit", 0.35), ("q", 0.4), ("q_burst", 0.5), ("q_hit", 0.35), ("t_grow", 0.4), ("t_hit", 0.3),
    ("e", 0.4), ("e_hit", 0.45), ("v_grow", 0.4), ("v_hit", 0.3), ("r", 0.45), ("r_land", 0.55), ("r_knock", 0.55),
    ("r_rage", 0.4), ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("t_dmg", "t_ratio", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "v_slow", "r_dmg", "r_ratio")}
    for k in ("t_life", "t_per", "e_root", "r_knock", "r_air", "r_rage"):
        v[k] = secs(p[k])
    v["rage_up"] = p["rage"] - 100
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
    if "Zyra" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Zyra. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
