"""Ornn's text (5 languages), sound_info files and his keys in the shared files, numbers from build_ornn.P.

    python tools/kit/setup_ornn.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_ornn in every language, description + skill_name),
sound/sfx/league_ornn_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Ornn named). Only his keys change in the shared files. JSON: indent 2, CRLF,
UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 奥恩 (山隐之焰): 活体锻炉, 火山突堑, 风箱炎息, 炽烈冲锋, 熔铸之神的召唤, Brittle 易碎;
zh_TW 鄂爾 (爐心山神): 活火爐, 火山脈動, 熾焰吹息, 熔岩俯衝, 鑄火者的呼喚, 焦化; ja オーン: 歩く鍛冶場, 溶岩隆起, ふいごの息,
灼熱の突撃, 鍛冶神の呼び声, 脆弱; ko 오른: 간이 대장간, 용암 균열, 불꽃 풀무질, 화염 돌진, 대장장이 신의 부름, 불안정.
Slots: skill = Q Volcanic Rupture, skill2 = E Searing Charge, ult = R Call of the Forge God; the passive Living Forge
(its stats and Brittle) and W Bellows Breath in the attack's text. No combo sentence in any text (the user's rule) -
except where the combo IS the skill (E's quake on the pillar, R's headbutt). The add-on league_ornn says its own.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_ornn import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_ornn"
VERSION = "0.185.0"     # the next free number above main 0.184.1 (2026-10-21)
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
M = "<#a974ffff>"      # magic damage
T = "<#ffffffff>"      # true damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: placeholder until the art (tfm2_ase.py face): his eyes 42 design rows over his soles at PPU 1.5 (28 px)
VIEW = {"face": {"x": 4, "y": -28}, "center": {"x": 0, "y": -16}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def hpp(d, h, col=O):
    return f"{col}{{{d}}}{E} + {HPi}{col}{{{h}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "奥恩",
        "attack": O + "活体锻炉" + E + "：护甲、魔抗+{p_def}%，生命+{p_hp}%。W/E/R使敌方英雄" + O + "易碎" + E + "，普攻打中易碎的英雄造成" + T + "{br_hp}%最大生命" + E + "真实伤害并" + R + "击飞" + E + "。" +
                  O + "风箱炎息" + E + "：每" + A + "{w_cd}秒" + E + "喷火，" + R + "不可阻挡" + E + "并获得护盾，造成" + hpp("w_sum", "w_hpsum", M) + "魔法伤害。",
        "skill": "砸地裂出一道裂隙，造成" + phys("q_dmg", "q_ratio") + "物理伤害并" + R + "减速{q_slow}%" + E + "，尽头升起熔岩柱，持续" + A + "{q_life}秒" + E + "。",
        "skill2": "冲向目标，造成" + hpp("e_dmg", "e_hp") + "物理伤害。撞上熔岩柱时撞碎它，周围敌人" + R + "击飞" + A + "{e_up}秒" + E + E + "并受到" + hpp("e_q_dmg", "e_q_hp") + "物理伤害，英雄易碎。",
        "ult": "召唤熔岩公羊从远处冲向自己，造成" + hpp("r_dmg", "r_hp", M) + "魔法伤害并" + R + "减速{r_slow}%" + E + "；公羊到身边时头槌把它顶回去，沿路造成" + hpp("r2_dmg", "r2_hp", M) + "魔法伤害并" + R + "击飞" + E + "。",
        "names": ("火山突堑", "炽烈冲锋", "熔铸之神的召唤"),
    },
    "zh-hant": {
        "name": "鄂爾",
        "attack": O + "活火爐" + E + "：護甲、魔抗+{p_def}%，生命+{p_hp}%。W/E/R使敵方英雄" + O + "焦化" + E + "，普攻打中焦化的英雄造成" + T + "{br_hp}%最大生命" + E + "真實傷害並" + R + "擊飛" + E + "。" +
                  O + "熾焰吹息" + E + "：每" + A + "{w_cd}秒" + E + "噴火，" + R + "不可阻擋" + E + "並獲得護盾，造成" + hpp("w_sum", "w_hpsum", M) + "魔法傷害。",
        "skill": "砸地裂出一道裂隙，造成" + phys("q_dmg", "q_ratio") + "物理傷害並" + R + "緩速{q_slow}%" + E + "，盡頭升起熔岩柱，持續" + A + "{q_life}秒" + E + "。",
        "skill2": "衝向目標，造成" + hpp("e_dmg", "e_hp") + "物理傷害。撞上熔岩柱時撞碎它，周圍敵人" + R + "擊飛" + A + "{e_up}秒" + E + E + "並受到" + hpp("e_q_dmg", "e_q_hp") + "物理傷害，英雄焦化。",
        "ult": "召喚熔岩公羊從遠處衝向自己，造成" + hpp("r_dmg", "r_hp", M) + "魔法傷害並" + R + "緩速{r_slow}%" + E + "；公羊到身邊時頭槌把牠頂回去，沿路造成" + hpp("r2_dmg", "r2_hp", M) + "魔法傷害並" + R + "擊飛" + E + "。",
        "names": ("火山脈動", "熔岩俯衝", "鑄火者的呼喚"),
    },
    "en": {
        "name": "Ornn",
        "attack": O + "Living Forge" + E + ": +{p_def}% armour and magic resist, +{p_hp}% health. W, E and R make enemy champions " + O + "Brittle" + E +
                  "; his attack on a Brittle champion deals " + T + "{br_hp}% of its max health" + E + " as true damage and " + R + "knocks it up" + E + ". " +
                  O + "Bellows Breath" + E + ": every " + A + "{w_cd}s" + E + " he breathes fire, " + R + "unstoppable" + E + " and shielded, dealing " +
                  hpp("w_sum", "w_hpsum", M) + " magic damage.",
        "skill": "Slams the ground: a fissure deals " + phys("q_dmg", "q_ratio") + " physical damage and " + R + "slows {q_slow}%" + E +
                 "; a magma pillar rises at its end for " + A + "{q_life}s" + E + ".",
        "skill2": "Charges the target, dealing " + hpp("e_dmg", "e_hp") + " physical damage. Charging into a pillar shatters it: enemies "
                  "around are " + R + "knocked up" + E + " for " + A + "{e_up}s" + E + " and take " + hpp("e_q_dmg", "e_q_hp") + " physical damage, "
                  "champions made Brittle.",
        "ult": "Summons a fire ram that charges back to him, dealing " + hpp("r_dmg", "r_hp", M) + " magic damage and " + R + "slowing {r_slow}%" + E +
               "; when it reaches him he headbutts it back, dealing " + hpp("r2_dmg", "r2_hp", M) + " magic damage and " + R + "knocking up" + E +
               " along its path.",
        "names": ("Volcanic Rupture", "Searing Charge", "Call of the Forge God"),
    },
    "ko": {
        "name": "오른",
        "attack": O + "간이 대장간" + E + ": 방어력·마법 저항력 +{p_def}%, 체력 +{p_hp}%. W/E/R이 적 챔피언을 " + O + "불안정" + E + " 상태로 만들고, "
                  "불안정한 챔피언을 기본 공격하면 " + T + "최대 체력 {br_hp}%" + E + " 고정 피해와 " + R + "에어본" + E + ". " +
                  O + "불꽃 풀무질" + E + ": " + A + "{w_cd}초" + E + "마다 불을 뿜어 " + R + "저지 불가" + E + "·보호막, " + hpp("w_sum", "w_hpsum", M) + " 마법 피해.",
        "skill": "땅을 내리쳐 균열이 " + phys("q_dmg", "q_ratio") + " 물리 피해와 " + R + "{q_slow}% 둔화" + E + ". 끝에 용암 기둥이 " + A + "{q_life}초" + E + " 솟음.",
        "skill2": "대상에게 돌진해 " + hpp("e_dmg", "e_hp") + " 물리 피해. 기둥에 부딪히면 부수고 주변 적을 " + R + "{e_up}초 에어본" + E + "시키며 " +
                  hpp("e_q_dmg", "e_q_hp") + " 물리 피해, 챔피언은 불안정.",
        "ult": "용암 숫양을 소환해 자신에게 달려오게 하여 " + hpp("r_dmg", "r_hp", M) + " 마법 피해와 " + R + "{r_slow}% 둔화" + E + ". 도착하면 박치기로 "
               "되돌려 보내 경로의 적에게 " + hpp("r2_dmg", "r2_hp", M) + " 마법 피해와 " + R + "에어본" + E + ".",
        "names": ("용암 균열", "화염 돌진", "대장장이 신의 부름"),
    },
    "ja": {
        "name": "オーン",
        "attack": O + "歩く鍛冶場" + E + "：物理・魔法防御+{p_def}%、体力+{p_hp}%。W/E/Rで敵チャンピオンを" + O + "脆弱" + E + "にし、脆弱な相手への通常攻撃は" +
                  T + "最大体力の{br_hp}%" + E + "の確定ダメージと" + R + "ノックアップ" + E + "。" + O + "ふいごの息" + E + "：" + A + "{w_cd}秒" + E + "ごとに炎を吐き、" +
                  R + "阻害無効" + E + "とシールド、" + hpp("w_sum", "w_hpsum", M) + "の魔法ダメージ。",
        "skill": "地面を叩き、亀裂が" + phys("q_dmg", "q_ratio") + "の物理ダメージと" + R + "{q_slow}%スロウ" + E + "。終点に溶岩の柱が" + A + "{q_life}秒" + E + "立つ。",
        "skill2": "対象へ突進し" + hpp("e_dmg", "e_hp") + "の物理ダメージ。柱に当たると砕き、周囲の敵を" + R + "{e_up}秒ノックアップ" + E + "して" +
                  hpp("e_q_dmg", "e_q_hp") + "の物理ダメージ、チャンピオンは脆弱。",
        "ult": "溶岩の雄羊を呼び自分へ突進させ、" + hpp("r_dmg", "r_hp", M) + "の魔法ダメージと" + R + "{r_slow}%スロウ" + E + "。到着すると頭突きで跳ね返し、"
               "通り道に" + hpp("r2_dmg", "r2_hp", M) + "の魔法ダメージと" + R + "ノックアップ" + E + "。",
        "names": ("溶岩隆起", "灼熱の突撃", "鍛冶神の呼び声"),
    },
}

C = "league_ornn_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_ornn_a": [(C + "a", 0.4, 0.0)],
    "league_ornn_a_hit": [(C + "a_hit", 0.35, 0.0)],
    "league_ornn_br": [(C + "br", 0.3, 0.0)],
    "league_ornn_br_pop": [(C + "br_pop", 0.5, 0.0)],
    "league_ornn_w": [(C + "w", 0.5, 0.0)],
    "league_ornn_w_hit": [(C + "w_hit", 0.15, 0.0)],
    "league_ornn_q": [(C + "q", 0.4, 0.0)],
    "league_ornn_q_crack": [(C + "q_crack", 0.45, 0.0)],
    "league_ornn_q_hit": [(C + "q_hit", 0.35, 0.0)],
    "league_ornn_q_pillar": [(C + "q_pillar", 0.5, 0.0)],
    "league_ornn_q_break": [(C + "q_break", 0.55, 0.0)],
    "league_ornn_e": [(C + "e", 0.45, 0.0)],
    "league_ornn_e_hit": [(C + "e_hit", 0.45, 0.0)],
    "league_ornn_e_up": [(C + "e_up", 0.45, 0.0)],
    "league_ornn_r": [(C + "r", 0.5, 0.0)],
    "league_ornn_r_run": [(C + "r_run", 0.5, 0.0)],
    "league_ornn_r_hit": [(C + "r_hit", 0.4, 0.0)],
    "league_ornn_r2": [(C + "r2", 0.45, 0.0)],
    "league_ornn_r2_butt": [(C + "r2_butt", 0.6, 0.0)],
    "league_ornn_r2_run": [(C + "r2_run", 0.5, 0.0)],
    "league_ornn_r2_hit": [(C + "r_hit", 0.45, 0.0)],
    "league_ornn_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_ornn_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_ornn_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_ornn_vo_r": [(C + "vo_r", 0.9, 0.0)],
    "league_ornn_vo_r2": [(C + "vo_r2", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_def", "p_hp", "br_hp", "q_dmg", "q_ratio", "q_slow", "e_dmg", "e_hp", "e_q_dmg", "e_q_hp",
                           "r_dmg", "r_hp", "r_slow", "r2_dmg", "r2_hp")}
    v["w_sum"] = p["w_dmg"] * p["w_n"]
    v["w_hpsum"] = p["w_hp"] * p["w_n"]
    for k in ("w_cd", "q_life", "e_up"):
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
    if "Ornn" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Ornn. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
