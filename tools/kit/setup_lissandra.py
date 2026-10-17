"""Lissandra's text (5 languages), sound_info files and her keys in the shared files, numbers from build_lissandra.P.

    python tools/kit/setup_lissandra.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_lissandra in every language, description + skill_name),
sound/sfx/league_lissandra_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.59.0, Lissandra named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/lz/rst.py: 丽桑卓 / 冰霜女巫, 冰脉驱役, 寒冰碎片, 冰霜之环, 冰川之径, 冰封陵墓) and
Data Dragon 16.19.1 (zh_TW 麗珊卓 / 寒霜霸權 / 幽影碎冰 / 暴雪結界 / 急速冰刺 / 永凍墳地, ko 리산드라 / 냉기의 지배 / 얼음 파편 /
서릿발 / 얼음갈퀴 길 / 얼음 무덤, ja リサンドラ / アイスボーンへの服従 / アイスシャード / リング・オブ・フロスト / グラシアルパス /
フローズングレイブ). No `league_lissandra_attack` sound: the engine would play it at the start of every attack; the
throw sound plays from the tree at the release.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_lissandra import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_lissandra"
VERSION = "0.59.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -36}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


G = "<#7cfc00ff>"      # heals


def heal_txt():
    return f"{G}{{r_heal}}{E} + {APi}{G}{{r_heal_ap}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "丽桑卓",
        "attack": "发射冰弹攻击。被动" + O + "冰脉驱役" + E + "：她击杀的敌方英雄化为冰仆，" + A + "{p_delay}秒" + E + "后碎裂，对周围敌人造成" +
                  mag("p_dmg", "p_ap") + M + "魔法伤害" + E + "并" + R + "减速" + E + "。",
        "skill": "射出冰锥，沿途每个敌人受到" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并" + R + "减速{q_slow}%" + E +
                 "。出手时方向已锁定，可以躲开。",
        "skill2": O + "冰霜之环" + E + "：周围敌人受到" + mag("w_dmg", "w_ap") + M + "魔法伤害" + E + "并" + R + "定身{w_root}秒" + E +
                  "。身边没敌人时放" + O + "冰川之径" + E + "：冰爪造成" + mag("e_dmg", "e_ap") + "，追上正在交战的敌方英雄后再放冰环。",
        "ult": "冰封敌方英雄：" + R + "眩晕{r_stun}秒" + E + "，受到" + mag("r_dmg", "r_ap") + M + "魔法伤害" + E + "。被两名以上敌方英雄围住时改为冰封自己" +
               A + "{r_self_t}秒" + E + "：免疫伤害和控制，回复" + heal_txt() + "生命。冰块周围留下减速冰地。",
        "names": ("寒冰碎片", "冰霜之环", "冰封陵墓"),
    },
    "zh-hant": {
        "name": "麗珊卓",
        "attack": "發射冰彈攻擊。被動" + O + "寒霜霸權" + E + "：她擊殺的敵方英雄化為冰僕，" + A + "{p_delay}秒" + E + "後碎裂，對周圍敵人造成" +
                  mag("p_dmg", "p_ap") + M + "魔法傷害" + E + "並" + R + "緩速" + E + "。",
        "skill": "射出冰錐，沿途每個敵人受到" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並" + R + "緩速{q_slow}%" + E +
                 "。出手時方向已鎖定，可以閃開。",
        "skill2": O + "暴雪結界" + E + "：周圍敵人受到" + mag("w_dmg", "w_ap") + M + "魔法傷害" + E + "並" + R + "定身{w_root}秒" + E +
                  "。身邊沒敵人時施放" + O + "急速冰刺" + E + "：冰爪造成" + mag("e_dmg", "e_ap") + "，追上交戰中的敵方英雄後再放結界。",
        "ult": "冰封敵方英雄：" + R + "暈眩{r_stun}秒" + E + "，受到" + mag("r_dmg", "r_ap") + M + "魔法傷害" + E + "。被兩名以上敵方英雄包圍時改為冰封自己" +
               A + "{r_self_t}秒" + E + "：免疫傷害和控制，回復" + heal_txt() + "生命。冰塊周圍留下緩速冰地。",
        "names": ("幽影碎冰", "暴雪結界", "永凍墳地"),
    },
    "en": {
        "name": "Lissandra",
        "attack": "Throws ice bolts. Passive " + O + "Iceborn Subjugation" + E + ": an enemy champion she kills becomes a frozen "
                  "thrall that shatters after " + A + "{p_delay}s" + E + ", dealing " + mag("p_dmg", "p_ap") + " " + M +
                  "magic damage" + E + " around it and " + R + "slowing" + E + ".",
        "skill": "Throws a shard of ice that deals " + mag("q_dmg", "q_ap") + " " + M + "magic damage" + E + " to every enemy it "
                 "passes and " + R + "slows" + E + " them by {q_slow}%. The aim is set as she throws, so it can be dodged.",
        "skill2": O + "Ring of Frost" + E + ": enemies around her take " + mag("w_dmg", "w_ap") + " " + M + "magic damage" + E +
                  " and are " + R + "rooted" + E + " for " + A + "{w_root}s" + E + ". With no enemy near, " + O + "Glacial Path" +
                  E + " first: a claw dealing " + mag("e_dmg", "e_ap") + "; she blinks after it to an enemy champion her team is "
                  "fighting and casts the ring there.",
        "ult": "Encases an enemy champion: " + R + "stunned" + E + " for " + A + "{r_stun}s" + E + ", " + mag("r_dmg", "r_ap") +
               " " + M + "magic damage" + E + ". Surrounded by two or more enemy champions, she encases herself instead for " +
               A + "{r_self_t}s" + E + ": immune to damage and crowd control, healing " + heal_txt() + ". The ice leaves a "
               "slowing field around the tomb.",
        "names": ("Ice Shard", "Ring of Frost", "Frozen Tomb"),
    },
    "ko": {
        "name": "리산드라",
        "attack": "얼음 화살로 공격합니다. 기본 지속 효과 " + O + "냉기의 지배" + E + ": 리산드라가 처치한 적 챔피언은 얼음 종이 되어 " + A +
                  "{p_delay}초" + E + " 후 부서지며 주변 적에게 " + mag("p_dmg", "p_ap") + "의 " + M + "마법 피해" + E + "를 입히고 " +
                  R + "둔화" + E + "시킵니다.",
        "skill": "얼음 파편을 던져 지나가는 모든 적에게 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" + E + "를 입히고 {q_slow}% " +
                 R + "둔화" + E + "시킵니다. 던질 때 방향이 정해져 피할 수 있습니다.",
        "skill2": O + "서릿발" + E + ": 주변 적에게 " + mag("w_dmg", "w_ap") + "의 " + M + "마법 피해" + E + "를 입히고 " + A + "{w_root}초" +
                  E + " " + R + "속박" + E + "합니다. 주변에 적이 없으면 먼저 " + O + "얼음갈퀴 길" + E + ": 갈퀴가 " + mag("e_dmg", "e_ap") +
                  "의 피해를 주고, 교전 중인 적 챔피언 곁으로 이동해 서릿발을 사용합니다.",
        "ult": "적 챔피언을 얼려 " + A + "{r_stun}초" + E + " " + R + "기절" + E + "시키고 " + mag("r_dmg", "r_ap") + "의 " + M + "마법 피해" +
               E + ". 적 챔피언 둘 이상에게 둘러싸이면 대신 자신을 " + A + "{r_self_t}초" + E + " 얼려 피해와 군중 제어에 면역이 되고 " +
               heal_txt() + "의 체력을 회복합니다. 얼음 주변에 둔화 지대가 남습니다.",
        "names": ("얼음 파편", "서릿발", "얼음 무덤"),
    },
    "ja": {
        "name": "リサンドラ",
        "attack": "氷の矢で攻撃。パッシブ " + O + "アイスボーンへの服従" + E + "：倒した敵チャンピオンは氷の従者となり、" + A + "{p_delay}秒" + E +
                  "後に砕けて周囲の敵に" + mag("p_dmg", "p_ap") + "の" + M + "魔法ダメージ" + E + "と" + R + "スロウ" + E + "。",
        "skill": "氷の欠片を放ち、通り抜けた敵すべてに" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と{q_slow}%の" + R +
                 "スロウ" + E + "。放つ前に方向が決まるので避けられる。",
        "skill2": O + "リング・オブ・フロスト" + E + "：周囲の敵に" + mag("w_dmg", "w_ap") + "の" + M + "魔法ダメージ" + E + "と" + A +
                  "{w_root}秒" + E + "の" + R + "スネア" + E + "。近くに敵がいなければ先に" + O + "グラシアルパス" + E + "：爪が" +
                  mag("e_dmg", "e_ap") + "、交戦中の敵チャンピオンの側へ移動してリングを放つ。",
        "ult": "敵チャンピオンを凍らせ" + A + "{r_stun}秒" + E + R + "スタン" + E + "、" + mag("r_dmg", "r_ap") + "の" + M + "魔法ダメージ" + E +
               "。敵チャンピオン2体以上に囲まれると代わりに自分を" + A + "{r_self_t}秒" + E + "凍らせ、ダメージと行動妨害を無効化し" +
               heal_txt() + "回復。氷の周りにスロウの氷原が残る。",
        "names": ("アイスシャード", "リング・オブ・フロスト", "フローズングレイブ"),
    },
}

C = "league_lissandra_sfx_"
V = "league_lissandra_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_lissandra_a_throw": [(C + "attack", 0.5, 0.0), (C + "bolt", 0.35, 0.05)],
    "league_lissandra_a_hit": [(C + "bolt_hit", 0.35, 0.0)],
    "league_lissandra_q_cast": [(C + "q", 0.6, 0.0), (C + "q_fly", 0.35, 0.05), (V + "q", 0.85, 0.05)],
    "league_lissandra_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_lissandra_w_ring": [(C + "w", 0.6, 0.0), (V + "w", 0.85, 0.05)],
    "league_lissandra_w_hit": [(C + "w_root", 0.4, 0.0)],
    "league_lissandra_e_cast": [(C + "e", 0.55, 0.0), (V + "e", 0.85, 0.05)],
    "league_lissandra_e_hit": [(C + "e_hit", 0.45, 0.0)],
    "league_lissandra_e_port": [(C + "e_port", 0.6, 0.0)],
    "league_lissandra_r_cast": [(C + "r", 0.6, 0.0), (C + "r_field", 0.4, 0.1), (V + "r", 0.9, 0.1)],
    "league_lissandra_r_tomb": [(C + "r_tomb", 0.6, 0.0)],
    "league_lissandra_r_self": [(C + "r_self", 0.6, 0.0), (C + "r_field", 0.4, 0.1), (V + "r_self", 0.9, 0.1)],
    "league_lissandra_r_hit": [(C + "r_hit", 0.35, 0.0)],
    "league_lissandra_p_rise": [(C + "p_rise", 0.55, 0.0)],
    "league_lissandra_p_burst": [(C + "p_burst", 0.6, 0.0)],
    "league_lissandra_p_hit": [(C + "q_hit", 0.3, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "q_dmg", "q_ap", "q_slow", "w_dmg", "w_ap", "e_dmg", "e_ap", "r_dmg", "r_ap",
                           "r_heal", "r_heal_ap")}
    v.update({k: secs(p[k]) for k in ("p_delay", "w_root", "r_stun", "r_self_t")})
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
    if "Lissandra" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Lissandra. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
