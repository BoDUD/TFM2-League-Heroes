"""Xin Zhao's text (5 languages), sound_info files and his keys in the shared files, numbers from build_xinzhao.P.

    python tools/kit/setup_xinzhao.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_xinzhao in every language, description + skill_name),
sound/sfx/league_xinzhao_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.64.0, Xin Zhao named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.19.1 (zh_CN 赵信 / 果决, 三重爪击, 风斩电刺, 无畏冲锋, 新月护卫; zh_TW 趙信 / 鬥戰決心, 三重爪擊,
風雷迅馳, 一騎當先, 新月無雙; ko 신 짜오 / 결심, 삼조격, 풍전참뢰, 무쌍돌격, 현월수호; ja シン・ジャオ / 不退転, 三槍撃, 風成雷鳴,
兵貴神速, 三日月槍守).
No `league_xinzhao_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_xinzhao import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_xinzhao"
VERSION = "0.64.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control, debuffs
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -36}, "center": {"x": 0, "y": -12}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def hl(d, r):
    return f"{G}{{{d}}}{E} + {ADi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "赵信",
        "attack": "长枪攻击。被动" + O + "果决" + E + "：每第三次攻击额外造成" + ADi + O + "{p_ratio}%" + E + "物理伤害，并回复" +
                  hl("p_heal", "p_heal_ratio") + "生命。",
        "skill": "冲向目标，对周围敌人造成" + phy("e_dmg", "e_ratio") + "物理伤害并" + R + "减速{e_slow}%" + E + "，攻击速度+{e_as}%，持续" + A +
                 "{e_as_t}秒" + E + "。随后" + O + "三重爪击" + E + "：接下来3次攻击各额外造成" + phy("q_dmg", "q_ratio") + "，第三次" + R +
                 "击飞{q_up}秒" + E + "。",
        "skill2": "先横扫面前，造成" + phy("w1_dmg", "w1_ratio") + "物理伤害；再向前直刺，造成" + phy("w2_dmg", "w2_ratio") + "物理伤害并" + R +
                  "减速{w_slow}%" + E + "，持续{w_slow_t}秒。",
        "ult": "横扫周围，造成" + phy("r_dmg", "r_ratio") + "加目标最大生命值{r_hp}%的物理伤害，除被挑战的目标（施放对象）外全部" + R + "击退" + E + "。之后" +
               A + "{r_t}秒" + E + "内受到的伤害降低{r_red}%。",
        "names": ("无畏冲锋", "风斩电刺", "新月护卫"),
    },
    "zh-hant": {
        "name": "趙信",
        "attack": "長槍攻擊。被動" + O + "鬥戰決心" + E + "：每第三次攻擊額外造成" + ADi + O + "{p_ratio}%" + E + "物理傷害，並回復" +
                  hl("p_heal", "p_heal_ratio") + "生命。",
        "skill": "衝向目標，對周圍敵人造成" + phy("e_dmg", "e_ratio") + "物理傷害並" + R + "緩速{e_slow}%" + E + "，攻擊速度+{e_as}%，持續" + A +
                 "{e_as_t}秒" + E + "。隨後" + O + "三重爪擊" + E + "：接下來3次攻擊各額外造成" + phy("q_dmg", "q_ratio") + "，第三次" + R +
                 "擊飛{q_up}秒" + E + "。",
        "skill2": "先橫掃面前，造成" + phy("w1_dmg", "w1_ratio") + "物理傷害；再向前直刺，造成" + phy("w2_dmg", "w2_ratio") + "物理傷害並" + R +
                  "緩速{w_slow}%" + E + "，持續{w_slow_t}秒。",
        "ult": "橫掃周圍，造成" + phy("r_dmg", "r_ratio") + "加目標最大生命值{r_hp}%的物理傷害，除被挑戰的目標（施放對象）外全部" + R + "擊退" + E + "。之後" +
               A + "{r_t}秒" + E + "內受到的傷害降低{r_red}%。",
        "names": ("一騎當先", "風雷迅馳", "新月無雙"),
    },
    "en": {
        "name": "Xin Zhao",
        "attack": "Spear thrusts. Passive " + O + "Determination" + E + ": every third attack deals " + ADi + O + "{p_ratio}%" + E +
                  " more physical damage and heals him " + hl("p_heal", "p_heal_ratio") + ".",
        "skill": "Charges the target, dealing " + phy("e_dmg", "e_ratio") + " physical damage to nearby enemies and " + R +
                 "slowing" + E + " them by {e_slow}%; he gains {e_as}% attack speed for " + A + "{e_as_t}s" + E + ". Then " + O +
                 "Three Talon Strike" + E + ": his next 3 attacks deal " + phy("q_dmg", "q_ratio") + " more, the third " + R +
                 "knocks up" + E + " for {q_up}s.",
        "skill2": "Slashes in front of him for " + phy("w1_dmg", "w1_ratio") + " physical damage, then thrusts ahead for " +
                  phy("w2_dmg", "w2_ratio") + " physical damage, " + R + "slowing" + E + " by {w_slow}% for {w_slow_t}s.",
        "ult": "Sweeps around him for " + phy("r_dmg", "r_ratio") + " plus {r_hp}% of the target's max health as physical damage, "
               + R + "knocking back" + E + " every enemy but the challenged one. For " + A + "{r_t}s" + E +
               " afterwards he takes {r_red}% less damage.",
        "names": ("Audacious Charge", "Wind Becomes Lightning", "Crescent Guard"),
    },
    "ko": {
        "name": "신 짜오",
        "attack": "창으로 공격합니다. 기본 지속 효과 " + O + "결심" + E + ": 세 번째 공격마다 " + ADi + O + "{p_ratio}%" + E +
                  "의 물리 피해를 추가로 입히고 " + hl("p_heal", "p_heal_ratio") + "의 체력을 회복합니다.",
        "skill": "대상에게 돌진해 주변 적에게 " + phy("e_dmg", "e_ratio") + "의 물리 피해를 입히고 {e_slow}% " + R + "둔화" + E + "시키며, " + A +
                 "{e_as_t}초" + E + " 동안 공격 속도가 {e_as}% 증가합니다. 이어서 " + O + "삼조격" + E + ": 다음 기본 공격 3회가 " +
                 phy("q_dmg", "q_ratio") + "의 추가 피해를 입히고, 세 번째는 {q_up}초 동안 " + R + "공중에 띄웁니다" + E + ".",
        "skill2": "앞을 베어 " + phy("w1_dmg", "w1_ratio") + "의 물리 피해를 입힌 뒤 앞으로 찔러 " + phy("w2_dmg", "w2_ratio") +
                  "의 물리 피해를 입히고 {w_slow_t}초 동안 {w_slow}% " + R + "둔화" + E + "시킵니다.",
        "ult": "주변을 휩쓸어 " + phy("r_dmg", "r_ratio") + " + 대상 최대 체력의 {r_hp}%만큼 물리 피해를 입히고, 도전받은 대상을 제외한 모든 적을 " +
               R + "밀어냅니다" + E + ". 이후 " + A + "{r_t}초" + E + " 동안 받는 피해가 {r_red}% 감소합니다.",
        "names": ("무쌍돌격", "풍전참뢰", "현월수호"),
    },
    "ja": {
        "name": "シン・ジャオ",
        "attack": "槍で攻撃。パッシブ " + O + "不退転" + E + "：3回目の攻撃ごとに" + ADi + O + "{p_ratio}%" + E + "の物理ダメージを追加し、" +
                  hl("p_heal", "p_heal_ratio") + "回復。",
        "skill": "対象に突撃し周囲の敵に" + phy("e_dmg", "e_ratio") + "の物理ダメージと{e_slow}%の" + R + "スロウ" + E + "、攻撃速度+{e_as}%（" + A +
                 "{e_as_t}秒" + E + "）。続けて" + O + "三槍撃" + E + "：次の3回の攻撃が" + phy("q_dmg", "q_ratio") + "を追加、3回目は{q_up}秒" + R +
                 "ノックアップ" + E + "。",
        "skill2": "前方を薙ぎ払い" + phy("w1_dmg", "w1_ratio") + "の物理ダメージ、続けて突きで" + phy("w2_dmg", "w2_ratio") + "の物理ダメージと" +
                  "{w_slow}%の" + R + "スロウ" + E + "（{w_slow_t}秒）。",
        "ult": "周囲を薙ぎ払い" + phy("r_dmg", "r_ratio") + "+対象の最大体力の{r_hp}%の物理ダメージ、チャレンジ中の対象以外を" + R + "ノックバック" + E +
               "。その後" + A + "{r_t}秒" + E + "間、受けるダメージ-{r_red}%。",
        "names": ("兵貴神速", "風成雷鳴", "三日月槍守"),
    },
}

C = "league_xinzhao_sfx_"
V = "league_xinzhao_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_xinzhao_a_swing": [(C + "swing", 0.45, 0.0)],
    "league_xinzhao_a_hit": [(C + "hit", 0.4, 0.0)],
    "league_xinzhao_p_hit": [(C + "p_hit", 0.5, 0.0)],
    "league_xinzhao_p_heal": [(C + "p_heal", 0.4, 0.0)],
    "league_xinzhao_q_arm": [(C + "q", 0.45, 0.0)],
    "league_xinzhao_q_thrust": [(C + "swing", 0.5, 0.0)],
    "league_xinzhao_q1": [(C + "q1", 0.45, 0.0)],
    "league_xinzhao_q2": [(C + "q2", 0.45, 0.0)],
    "league_xinzhao_q3": [(C + "q3", 0.55, 0.0), (V + "q3", 0.85, 0.0)],
    "league_xinzhao_e_cast": [(C + "e", 0.55, 0.0), (V + "e", 0.85, 0.05)],
    "league_xinzhao_e_hit": [(C + "e_hit", 0.5, 0.0)],
    "league_xinzhao_w_cast": [(C + "w", 0.5, 0.0), (V + "w", 0.85, 0.05)],
    "league_xinzhao_w_launch": [(C + "w_launch", 0.5, 0.0)],
    "league_xinzhao_w_hit": [(C + "w_hit", 0.4, 0.0)],
    "league_xinzhao_r_cast": [(C + "r", 0.6, 0.0), (V + "r", 0.9, 0.05)],
    "league_xinzhao_r_chal": [(C + "r_chal", 0.45, 0.0)],
    "league_xinzhao_r_knock": [(C + "r_knock", 0.5, 0.0)],
    "league_xinzhao_r_guard": [(C + "r_guard", 0.4, 0.0)],
    "league_xinzhao_r_end": [(C + "r_end", 0.4, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_ratio", "p_heal", "p_heal_ratio", "e_dmg", "e_ratio", "e_slow", "e_as", "q_dmg", "q_ratio",
                           "w1_dmg", "w1_ratio", "w2_dmg", "w2_ratio", "w_slow", "r_dmg", "r_ratio", "r_hp", "r_red")}
    v.update({k: secs(p[k]) for k in ("e_as_t", "q_up", "w_slow_t", "r_t")})
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
    if "Xin Zhao" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Xin Zhao. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
