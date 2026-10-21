"""Naafiri's text (5 languages), sound_info files and her keys in the shared files, numbers from build_naafiri.P.

    python tools/kit/setup_naafiri.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_naafiri in every language, description + skill_name),
sound/sfx/league_naafiri_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Naafiri named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 纳亚菲利 (百裂冥犬): 狂烈种群, 暗裔犬牙, 暴吼, 剔骨本能, 猎狗血性; zh_TW 娜菲芮 (百犬之牙):
眾犬吠聲, 冥血匕首, 獵犬嚎殺, 開膛破肚, 尋血獵犬; ja ナフィーリ: 我らは一つ, ダーキンダガー, 群れの呼び声, 獰猛なる刃, 猟犬の追跡;
ko 나피리: 늘어나는 무리, 다르킨 단검, 무리의 부름, 적출, 사냥개의 추적.
Slots: skill = Q Darkin Daggers, skill2 = E Eviscerate, ult = R Hounds' Pursuit opened by W The Call of the Pack; the
passive in the attack's text. No combo sentence in any text (the user's rule); the README says them. Q's second dagger
is its own recast (the text says what the next attack does), not a combo sentence.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_naafiri import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_naafiri"
VERSION = "0.187.0"     # the next free number above Ornn's PR #421 (0.185.0) and Shyvana's branch (0.186.0) (2026-10-21)
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
G = "<#7bd96bff>"      # healing, shields
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: drafts until her frames exist (a hound: the face low and ahead of her standing point)
VIEW = {"face": {"x": 10, "y": -18}, "center": {"x": 0, "y": -10}, "banpick_center": {"x": 0, "y": -4}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def grn(d, r):
    return f"{G}{{{d}}}{E} + {ADi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "纳亚菲利",
        "attack": "扑咬目标。" + O + "狂烈种群" + E + "：每次普攻和技能命中时狗群一起撕咬，造成" + phys("pk_dmg", "pk_ratio") +
                  "物理伤害（非英雄单位减半）。",
        "skill": "掷出匕首，造成" + phys("q_dmg", "q_ratio") + "物理伤害并流血" + A + "{q_bleed}秒" + E + "（共" + phys("q_b_dmg", "q_b_ratio") +
                 "）；狗群扑向命中的英雄撕咬" + A + "{pk_ride}秒" + E + "。" + A + "{q_win}秒" + E + "内下次普攻掷出第二把匕首，造成" +
                 phys("q2_dmg", "q2_ratio") + "，命中英雄回复" + grn("q_heal", "q_heal_r") + "生命。",
        "skill2": "冲向目标，撕裂周围的敌人两次，造成" + phys("e_dmg", "e_ratio") + "和" + phys("e2_dmg", "e2_ratio") + "物理伤害。",
        "ult": O + "暴吼" + E + "：" + A + "{r_imm}秒" + E + "不可选取，" + A + "{roar_t}秒" + E + "内狗群翻倍、攻击力+{roar_ad}%、移速+{roar_ms}%；"
               "随后扑向敌方英雄，造成" + phys("r_dmg", "r_ratio") + "物理伤害、" + R + "减速" + E + "并降低{r_shred}%护甲。" + A + "{r_win}秒" + E +
               "内参与击杀可再扑一次，获得" + grn("r_sh", "r_sh_r") + "护盾。",
        "names": ("暗裔犬牙", "剔骨本能", "猎狗血性"),
    },
    "zh-hant": {
        "name": "娜菲芮",
        "attack": "撲咬目標。" + O + "眾犬吠聲" + E + "：每次普攻和技能命中時犬群一起撕咬，造成" + phys("pk_dmg", "pk_ratio") +
                  "物理傷害（非英雄單位減半）。",
        "skill": "擲出匕首，造成" + phys("q_dmg", "q_ratio") + "物理傷害並流血" + A + "{q_bleed}秒" + E + "（共" + phys("q_b_dmg", "q_b_ratio") +
                 "）；犬群撲向命中的英雄撕咬" + A + "{pk_ride}秒" + E + "。" + A + "{q_win}秒" + E + "內下次普攻擲出第二把匕首，造成" +
                 phys("q2_dmg", "q2_ratio") + "，命中英雄回復" + grn("q_heal", "q_heal_r") + "生命。",
        "skill2": "衝向目標，撕裂周圍的敵人兩次，造成" + phys("e_dmg", "e_ratio") + "和" + phys("e2_dmg", "e2_ratio") + "物理傷害。",
        "ult": O + "獵犬嚎殺" + E + "：" + A + "{r_imm}秒" + E + "無法被選取，" + A + "{roar_t}秒" + E + "內犬群加倍、攻擊力+{roar_ad}%、移速+{roar_ms}%；"
               "隨後撲向敵方英雄，造成" + phys("r_dmg", "r_ratio") + "物理傷害、" + R + "緩速" + E + "並降低{r_shred}%護甲。" + A + "{r_win}秒" + E +
               "內參與擊殺可再撲一次，獲得" + grn("r_sh", "r_sh_r") + "護盾。",
        "names": ("冥血匕首", "開膛破肚", "尋血獵犬"),
    },
    "en": {
        "name": "Naafiri",
        "attack": "A lunging bite. " + O + "We Are More" + E + ": every attack and ability hit, her pack bites too for " +
                  phys("pk_dmg", "pk_ratio") + " physical damage (half to non-champions).",
        "skill": "Hurls a dagger for " + phys("q_dmg", "q_ratio") + " physical damage and a bleed of " + phys("q_b_dmg", "q_b_ratio") +
                 " over " + A + "{q_bleed}s" + E + "; her pack leaps on a champion hit and mauls it for " + A + "{pk_ride}s" + E + ". Within " +
                 A + "{q_win}s" + E + " her next attack hurls the second dagger for " + phys("q2_dmg", "q2_ratio") + ", healing her " +
                 grn("q_heal", "q_heal_r") + " on a champion.",
        "skill2": "Dashes onto the target and shreds the enemies around her twice for " + phys("e_dmg", "e_ratio") + " and " +
                  phys("e2_dmg", "e2_ratio") + " physical damage.",
        "ult": O + "The Call of the Pack" + E + ": untargetable for " + A + "{r_imm}s" + E + ", for " + A + "{roar_t}s" + E + " a pack twice "
               "as big, +{roar_ad}% attack and +{roar_ms}% move speed. Then she pounces on an enemy champion for " + phys("r_dmg", "r_ratio") +
               " physical damage, a " + R + "slow" + E + " and -{r_shred}% armour. A takedown within " + A + "{r_win}s" + E + " lets her "
               "pounce once more with a " + grn("r_sh", "r_sh_r") + " shield.",
        "names": ("Darkin Daggers", "Eviscerate", "Hounds' Pursuit"),
    },
    "ko": {
        "name": "나피리",
        "attack": "달려들어 물어뜯음. " + O + "늘어나는 무리" + E + ": 공격과 스킬이 적중할 때마다 무리가 함께 물어 " + phys("pk_dmg", "pk_ratio") +
                  " 물리 피해 (챔피언이 아니면 절반).",
        "skill": "단검을 던져 " + phys("q_dmg", "q_ratio") + " 물리 피해와 " + A + "{q_bleed}초" + E + " 동안 " + phys("q_b_dmg", "q_b_ratio") +
                 " 출혈; 맞힌 챔피언에게 무리가 덤벼들어 " + A + "{pk_ride}초" + E + " 동안 물어뜯음. " + A + "{q_win}초" + E + " 안에 다음 "
                 "공격은 두 번째 단검으로 " + phys("q2_dmg", "q2_ratio") + ", 챔피언 적중 시 체력 " + grn("q_heal", "q_heal_r") + " 회복.",
        "skill2": "대상에게 돌진해 주변 적을 두 번 찢어 " + phys("e_dmg", "e_ratio") + ", " + phys("e2_dmg", "e2_ratio") + " 물리 피해.",
        "ult": O + "무리의 부름" + E + ": " + A + "{r_imm}초" + E + " 동안 대상으로 지정 불가, " + A + "{roar_t}초" + E + " 동안 무리 두 배, "
               "공격력 +{roar_ad}%, 이동 속도 +{roar_ms}%. 이어서 적 챔피언에게 덮쳐 " + phys("r_dmg", "r_ratio") + " 물리 피해, " + R + "둔화" +
               E + ", 방어력 -{r_shred}%. " + A + "{r_win}초" + E + " 안에 처치 관여 시 " + grn("r_sh", "r_sh_r") + " 보호막과 함께 한 번 더 덮침.",
        "names": ("다르킨 단검", "적출", "사냥개의 추적"),
    },
    "ja": {
        "name": "ナフィーリ",
        "attack": "飛びかかって噛みつく。" + O + "我らは一つ" + E + "：通常攻撃とスキルが当たるたびに群れも噛みつき" + phys("pk_dmg", "pk_ratio") +
                  "の物理ダメージ（チャンピオン以外は半分）。",
        "skill": "短剣を投げ" + phys("q_dmg", "q_ratio") + "の物理ダメージと" + A + "{q_bleed}秒" + E + "の出血（計" + phys("q_b_dmg", "q_b_ratio") +
                 "）、当たったチャンピオンに群れが" + A + "{pk_ride}秒" + E + "食らいつく。" + A + "{q_win}秒" + E + "以内の次の攻撃で二本目を投げ" +
                 phys("q2_dmg", "q2_ratio") + "、チャンピオンなら体力" + grn("q_heal", "q_heal_r") + "回復。",
        "skill2": "対象へ突進し、周囲の敵を二度切り裂いて" + phys("e_dmg", "e_ratio") + "と" + phys("e2_dmg", "e2_ratio") + "の物理ダメージ。",
        "ult": O + "群れの呼び声" + E + "：" + A + "{r_imm}秒" + E + "対象指定不可、" + A + "{roar_t}秒" + E + "群れが倍、攻撃力+{roar_ad}%、"
               "移動速度+{roar_ms}%。続けて敵チャンピオンに飛びかかり" + phys("r_dmg", "r_ratio") + "の物理ダメージ、" + R + "スロウ" + E +
               "、物防-{r_shred}%。" + A + "{r_win}秒" + E + "以内のキル関与で" + grn("r_sh", "r_sh_r") + "のシールドともう一度飛びかかる。",
        "names": ("ダーキンダガー", "獰猛なる刃", "猟犬の追跡"),
    },
}

C = "league_naafiri_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_naafiri_a": [(C + "a", 0.4, 0.0)],
    "league_naafiri_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_naafiri_pk_bite": [(C + "pk_bite", 0.25, 0.0)],
    "league_naafiri_pk_leap": [(C + "pk_leap", 0.35, 0.0)],
    "league_naafiri_q": [(C + "q", 0.45, 0.0)],
    "league_naafiri_q_hit": [(C + "q_hit", 0.35, 0.0)],
    "league_naafiri_q2": [(C + "q2", 0.45, 0.0)],
    "league_naafiri_q2_hit": [(C + "q2_hit", 0.4, 0.0)],
    "league_naafiri_e": [(C + "e", 0.45, 0.0)],
    "league_naafiri_e_slash": [(C + "e_hit", 0.4, 0.0)],
    "league_naafiri_e_slash2": [(C + "e_end", 0.4, 0.0)],
    "league_naafiri_e_hit": [(C + "e_hit", 0.25, 0.0)],
    "league_naafiri_r_roar": [(C + "r_roar", 0.5, 0.0)],
    "league_naafiri_r_dash": [(C + "r_dash", 0.45, 0.0)],
    "league_naafiri_r_hit": [(C + "r_hit", 0.45, 0.0), (C + "r_pack", 0.3, 0.05)],
    "league_naafiri_r_reset": [(C + "r_reset", 0.5, 0.0)],
    "league_naafiri_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_naafiri_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_naafiri_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("pk_dmg", "pk_ratio", "q_dmg", "q_ratio", "q_b_dmg", "q_b_ratio", "q2_dmg", "q2_ratio",
                           "q_heal", "q_heal_r", "e_dmg", "e_ratio", "e2_dmg", "e2_ratio", "roar_ad", "roar_ms",
                           "r_dmg", "r_ratio", "r_shred", "r_sh", "r_sh_r")}
    for k in ("pk_ride", "q_bleed", "q_win", "r_imm", "roar_t", "r_win"):
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
    if "Naafiri" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Naafiri. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
