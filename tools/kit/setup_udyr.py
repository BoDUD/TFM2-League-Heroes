"""Udyr's text (5 languages), sound_info files and his keys in the shared files, numbers from build_udyr.P.

    python tools/kit/setup_udyr.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_udyr in every language, description + skill_name),
sound/sfx/league_udyr_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Udyr named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 乌迪尔 (兽灵行者): 众灵纽带, 狂暴爪击, 坚铁甲胄, 踏火蛮冲, 极凌飓风; zh_TW 烏迪爾 (神靈行者):
人神一體, 野蠻利爪, 鋼筋鐵骨, 熾熱衝撞, 霜翼風暴; ja ウディア: 精霊の繋ぎ手, 野性の爪, 鉄の外皮, 焔の猛進, 氷翼の嵐; ko 우디르: 가교,
야생 발톱, 강철 갑옷, 불길 쇄도, 날개 돋친 폭풍.
Slots: skill = Q Wilding Claw (the Bear), skill2 = E Blazing Stampede (the Ram), ult = R Wingborne Storm (the Phoenix);
the passive Bridge Between and W Iron Mantle (the Boar) in the attack's text. No combo sentence in any text (the user's
rule); the README says them. The awakened casts are each ability's own recast (what the same stance twice does), not a
combo sentence.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_udyr import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_udyr"
VERSION = "0.192.0"     # the next free number above main 0.191.1 (K'Sante #458, Neeko's reel #459, Darius #460) (2026-10-22)
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
M = "<#a974ffff>"      # magic damage
G = "<#7bd96bff>"      # healing, shields
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face between his eyes (ppu_restyle's face_to: 2 game px ahead of his standing point, 33 over the
# ground); the ban/pick card at base's rule for his height (tools/art/bp_card_audit.py: top -29.3 -> -10)
VIEW = {"face": {"x": 2, "y": -33}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -10}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def mag(d, r):
    return f"{M}{{{d}}}{E} + {ADi}{M}{{{r}}}%{E}"


def grn(d, r):
    return f"{G}{{{d}}}{E} + {ADi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "乌迪尔",
        "attack": "拳击目标。" + O + "众灵纽带" + E + "：放技能后两次攻击攻速+{p_as}%。" + O + "坚铁甲胄" + E + "：每" + A + "{w_icd}秒" + E +
                  "首个技能附带" + grn("w_sh", "w_sh_r") + "护盾，之后两次攻击各回复" + grn("w_heal", "w_heal_r") + "生命。",
        "skill": "熊姿态：攻速+{q_as}%持续" + A + "{q_t}秒" + E + "，下两次攻击额外造成" + phys("q_dmg", "q_ratio") + "+目标{q_thp}%最大生命值。"
                 "觉醒（熊姿态再放）：攻速+{q_as2}%，两次攻击引来闪电，造成" + mag("q2_dmg", "q2_ratio") + "魔法伤害。",
        "skill2": "公羊姿态：移速+{e_ms}%，冲向敌方英雄，撞击造成" + phys("e_dmg", "e_full") + "物理伤害并" + R + "晕眩" + E + A + "{e_stun}秒" +
                  E + "。觉醒（公羊姿态再放）：移速+{e_ms2}%，" + A + "{e_imm}秒" + E + "免疫控制。",
        "ult": "凤凰姿态：冰风暴环绕自身" + A + "{r_t}秒" + E + "，每" + A + "{r_gap}秒" + E + "对周围敌人造成" + mag("r_dmg", "r_ratio") + "魔法伤害并" +
               R + "减速" + E + "{r_slow}%；结束时风暴飞向一名敌方英雄，造成" + mag("r2_dmg", "r2_ratio") + "魔法伤害并减速{r2_slow}%。",
        "names": ("狂暴爪击", "踏火蛮冲", "极凌飓风"),
    },
    "zh-hant": {
        "name": "烏迪爾",
        "attack": "拳擊目標。" + O + "人神一體" + E + "：施放技能後兩次攻擊攻速+{p_as}%。" + O + "鋼筋鐵骨" + E + "：每" + A + "{w_icd}秒" + E +
                  "首個技能附帶" + grn("w_sh", "w_sh_r") + "護盾，之後兩次攻擊各回復" + grn("w_heal", "w_heal_r") + "生命。",
        "skill": "熊姿態：攻速+{q_as}%持續" + A + "{q_t}秒" + E + "，下兩次攻擊額外造成" + phys("q_dmg", "q_ratio") + "+目標{q_thp}%最大生命值。"
                 "覺醒（熊姿態再放）：攻速+{q_as2}%，兩次攻擊引來閃電，造成" + mag("q2_dmg", "q2_ratio") + "魔法傷害。",
        "skill2": "公羊姿態：移速+{e_ms}%，衝向敵方英雄，撞擊造成" + phys("e_dmg", "e_full") + "物理傷害並" + R + "暈眩" + E + A + "{e_stun}秒" +
                  E + "。覺醒（公羊姿態再放）：移速+{e_ms2}%，" + A + "{e_imm}秒" + E + "免疫控制。",
        "ult": "鳳凰姿態：冰風暴環繞自身" + A + "{r_t}秒" + E + "，每" + A + "{r_gap}秒" + E + "對周圍敵人造成" + mag("r_dmg", "r_ratio") + "魔法傷害並" +
               R + "緩速" + E + "{r_slow}%；結束時風暴飛向一名敵方英雄，造成" + mag("r2_dmg", "r2_ratio") + "魔法傷害並緩速{r2_slow}%。",
        "names": ("野蠻利爪", "熾熱衝撞", "霜翼風暴"),
    },
    "en": {
        "name": "Udyr",
        "attack": "A punch. " + O + "Bridge Between" + E + ": after each ability his next two attacks gain +{p_as}% attack speed. " + O +
                  "Iron Mantle" + E + ": his first ability every " + A + "{w_icd}s" + E + " also shields him for " + grn("w_sh", "w_sh_r") +
                  " and his next two attacks heal him " + grn("w_heal", "w_heal_r") + " each.",
        "skill": "Bear stance: +{q_as}% attack speed for " + A + "{q_t}s" + E + " and his next two attacks deal " + phys("q_dmg", "q_ratio") +
                 " + {q_thp}% of the target's max health more. Awakened (cast in the Bear stance): +{q_as2}% attack speed and both "
                 "attacks call lightning for " + mag("q2_dmg", "q2_ratio") + " magic damage around the target.",
        "skill2": "Ram stance: +{e_ms}% move speed, he charges an enemy champion and rams it for " + phys("e_dmg", "e_full") +
                  " physical damage, " + R + "stunning" + E + " it for " + A + "{e_stun}s" + E + ". Awakened (cast in the Ram stance): "
                  "+{e_ms2}% move speed and immune to crowd control for " + A + "{e_imm}s" + E + ".",
        "ult": "Phoenix stance: a glacial storm whirls round him for " + A + "{r_t}s" + E + ", every " + A + "{r_gap}s" + E + " dealing " +
               mag("r_dmg", "r_ratio") + " magic damage to nearby enemies and " + R + "slowing" + E + " them {r_slow}%; at its end the "
               "storm is unleashed at an enemy champion for " + mag("r2_dmg", "r2_ratio") + " magic damage and a {r2_slow}% slow.",
        "names": ("Wilding Claw", "Blazing Stampede", "Wingborne Storm"),
    },
    "ko": {
        "name": "우디르",
        "attack": "주먹으로 공격. " + O + "가교" + E + ": 스킬 사용 후 다음 두 번의 공격 속도 +{p_as}%. " + O + "강철 갑옷" + E + ": " + A +
                  "{w_icd}초" + E + "마다 첫 스킬에 " + grn("w_sh", "w_sh_r") + " 보호막, 다음 두 번의 공격마다 체력 " + grn("w_heal", "w_heal_r") +
                  " 회복.",
        "skill": "곰 태세: " + A + "{q_t}초" + E + " 동안 공격 속도 +{q_as}%, 다음 두 번의 공격이 " + phys("q_dmg", "q_ratio") + " + 대상 최대 "
                 "체력의 {q_thp}% 추가 피해. 각성(곰 태세에서 재사용): 공격 속도 +{q_as2}%, 두 번의 공격이 번개를 불러 " +
                 mag("q2_dmg", "q2_ratio") + " 마법 피해.",
        "skill2": "숫양 태세: 이동 속도 +{e_ms}%, 적 챔피언에게 돌진해 " + phys("e_dmg", "e_full") + " 물리 피해와 " + A + "{e_stun}초" + E +
                  " " + R + "기절" + E + ". 각성(숫양 태세에서 재사용): 이동 속도 +{e_ms2}%, " + A + "{e_imm}초" + E + " 동안 군중 제어 면역.",
        "ult": "불사조 태세: " + A + "{r_t}초" + E + " 동안 얼음 폭풍이 주위를 돌며 " + A + "{r_gap}초" + E + "마다 주변 적에게 " +
               mag("r_dmg", "r_ratio") + " 마법 피해와 {r_slow}% " + R + "둔화" + E + "; 끝날 때 폭풍이 적 챔피언에게 날아가 " +
               mag("r2_dmg", "r2_ratio") + " 마법 피해와 {r2_slow}% 둔화.",
        "names": ("야생 발톱", "불길 쇄도", "날개 돋친 폭풍"),
    },
    "ja": {
        "name": "ウディア",
        "attack": "拳で攻撃。" + O + "精霊の繋ぎ手" + E + "：スキル後の2回の通常攻撃は攻撃速度+{p_as}%。" + O + "鉄の外皮" + E + "：" + A +
                  "{w_icd}秒" + E + "ごとの最初のスキルで" + grn("w_sh", "w_sh_r") + "のシールド、続く2回の攻撃で体力" +
                  grn("w_heal", "w_heal_r") + "回復。",
        "skill": "熊の構え：" + A + "{q_t}秒" + E + "攻撃速度+{q_as}%、次の2回の攻撃が" + phys("q_dmg", "q_ratio") + "+対象の最大体力の{q_thp}%"
                 "を追加。覚醒（熊の構えで再使用）：攻撃速度+{q_as2}%、2回の攻撃が雷を呼び" + mag("q2_dmg", "q2_ratio") + "の魔法ダメージ。",
        "skill2": "雄羊の構え：移動速度+{e_ms}%、敵チャンピオンへ突進し" + phys("e_dmg", "e_full") + "の物理ダメージと" + A + "{e_stun}秒" + E +
                  "の" + R + "スタン" + E + "。覚醒（雄羊の構えで再使用）：移動速度+{e_ms2}%、" + A + "{e_imm}秒" + E + "行動妨害無効。",
        "ult": "不死鳥の構え：" + A + "{r_t}秒" + E + "氷の嵐がまとい、" + A + "{r_gap}秒" + E + "ごとに周囲の敵に" + mag("r_dmg", "r_ratio") +
               "の魔法ダメージと{r_slow}%の" + R + "スロウ" + E + "。終わりに嵐が敵チャンピオンへ飛び" + mag("r2_dmg", "r2_ratio") +
               "の魔法ダメージと{r2_slow}%スロウ。",
        "names": ("野性の爪", "焔の猛進", "氷翼の嵐"),
    },
}

C = "league_udyr_sfx_"     # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_udyr_a": [(C + "a", 0.4, 0.0)],
    "league_udyr_a_q": [(C + "a_q", 0.4, 0.0)],
    "league_udyr_a_e": [(C + "a_e", 0.4, 0.0)],
    "league_udyr_a_r": [(C + "a_r", 0.4, 0.0)],
    "league_udyr_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_udyr_q": [(C + "q", 0.45, 0.0)],
    "league_udyr_q_wake": [(C + "q_wake", 0.5, 0.0)],
    "league_udyr_q_hit": [(C + "q_hit", 0.35, 0.0)],
    "league_udyr_q_bolt": [(C + "q_bolt", 0.35, 0.0)],
    "league_udyr_q_bolt_hit": [(C + "q_bolt_hit", 0.4, 0.0)],
    "league_udyr_e": [(C + "e", 0.45, 0.0)],
    "league_udyr_e_wake": [(C + "e_wake", 0.5, 0.0)],
    "league_udyr_e_dash": [(C + "e_dash", 0.4, 0.0)],
    "league_udyr_e_hit_swing": [(C + "e_hit_swing", 0.4, 0.0)],
    "league_udyr_e_hit": [(C + "e_hit", 0.45, 0.0)],
    "league_udyr_r": [(C + "r", 0.45, 0.0)],
    "league_udyr_r_pulse": [(C + "r_pulse", 0.25, 0.0)],
    "league_udyr_r_rel": [(C + "r_rel", 0.5, 0.0)],
    "league_udyr_r_hit": [(C + "r_hit", 0.25, 0.0)],
    "league_udyr_r_rel_hit": [(C + "r_rel_hit", 0.45, 0.0)],
    "league_udyr_w": [(C + "w", 0.45, 0.0)],
    "league_udyr_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_udyr_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_udyr_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_as", "w_sh", "w_sh_r", "w_heal", "w_heal_r", "q_as", "q_as2", "q_dmg", "q_ratio", "q_thp",
                           "q2_dmg", "q2_ratio", "e_ms", "e_ms2", "e_dmg", "r_dmg", "r_ratio", "r_slow", "r2_dmg",
                           "r2_ratio", "r2_slow")}
    v["e_full"] = 100                       # the ram's blow: e_dmg + 100% AD (build_udyr's attack(e_dmg, 100))
    for k in ("w_icd", "q_t", "e_stun", "e_imm", "r_t", "r_gap"):
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
    if "Udyr" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Udyr. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
