"""Renekton's text (5 languages), sound_info files and his keys in the shared files, numbers from build_renekton.P.

    python tools/kit/setup_renekton.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_renekton in every language, description + skill_name),
sound/sfx/league_renekton_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.73.0, Renekton named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (the Chinese client swaps name and title: 雷克顿 / 荒漠屠夫; 怒之领域, 巨鳄狂袭,
冷酷捕猎, 横冲直撞, 终极统治) and Data Dragon 16.19.1 (zh_TW 雷尼克頓 / 沙漠屠夫, 怒不可遏, 弱肉強食, 庖丁解牛, 大切八塊,
君臨天下; ko 레넥톤 / 사막의 도살자, 분노의 지배, 양떼 도륙, 무자비한 포식자, 자르고 토막내기, 강신; ja レネクトン / 砂漠の解体屋,
激情の支配, ミートカット, メッタ斬り, スライス・アンド・ダイス, セベクの怒り). skill2 is named after E (the dash leads the
combo; the icon is E's), W in the text.
No `league_renekton_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_renekton import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_renekton"
VERSION = "0.73.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R_ = "<#ef5350ff>"     # crowd control
E = "<>"
# champion_view: placeholder until the sprite is in (setup --face / --banpick then)
VIEW = {"face": {"x": 4, "y": -24}, "center": {"x": 0, "y": -12}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "雷克顿",
        "attack": "近战挥砍。被动" + O + "怒之领域" + E + "：普攻和技能命中积攒怒气（最多{f_n}层，" + A + "{f_t}秒" + E +
                  "没积攒就清空）；满层时下一个技能被强化并耗尽怒气。",
        "skill": "横扫周围，造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "，每打中一个敌人回血，打中英雄回得更多。" +
                 "强化：" + phy("q_dmg_e", "q_ratio_e") + "，回血×{q_heal_x}（W 冷却时才用怒气）。",
        "skill2": "冲过敌方英雄造成" + phy("e_dmg", "e_ratio") + "，接" + O + "冷酷捕猎" + E + "：连砍两刀，" + R_ + "眩晕" + E + A +
                  "{w_stun}秒" + E + "（强化三刀、" + A + "{w_stun_e}秒" + E + "）；Q 好了接 Q，再冲一次，强化时削甲{e_shred}%。",
        "ult": "交战时变身" + A + "{r_t}秒" + E + "：" + HPi + "生命+{r_hp}，每" + A + "{r_period}秒" + E + "对周围造成{r_dmg} + " +
               HPi + "{r_hp_dmg}%的" + M + "魔法伤害" + E + "，不断积攒怒气。",
        "names": ("巨鳄狂袭", "横冲直撞", "终极统治"),
    },
    "zh-hant": {
        "name": "雷尼克頓",
        "attack": "近戰揮砍。被動" + O + "怒不可遏" + E + "：普攻和技能命中累積怒氣（最多{f_n}層，" + A + "{f_t}秒" + E +
                  "沒累積就清空）；滿層時下一個技能被強化並耗盡怒氣。",
        "skill": "橫掃周圍，造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "，每打中一個敵人回血，打中英雄回得更多。" +
                 "強化：" + phy("q_dmg_e", "q_ratio_e") + "，回血×{q_heal_x}（W 冷卻時才用怒氣）。",
        "skill2": "衝過敵方英雄造成" + phy("e_dmg", "e_ratio") + "，接" + O + "庖丁解牛" + E + "：連砍兩刀，" + R_ + "暈眩" + E + A +
                  "{w_stun}秒" + E + "（強化三刀、" + A + "{w_stun_e}秒" + E + "）；Q 好了接 Q，再衝一次，強化時削甲{e_shred}%。",
        "ult": "交戰時變身" + A + "{r_t}秒" + E + "：" + HPi + "生命+{r_hp}，每" + A + "{r_period}秒" + E + "對周圍造成{r_dmg} + " +
               HPi + "{r_hp_dmg}%的" + M + "魔法傷害" + E + "，不斷累積怒氣。",
        "names": ("弱肉強食", "大切八塊", "君臨天下"),
    },
    "en": {
        "name": "Renekton",
        "attack": "Melee slashes. Passive " + O + "Reign of Anger" + E + ": hits build Fury (up to {f_n} stacks, lost after " +
                  A + "{f_t}s" + E + " without a gain); at full Fury his next skill is empowered and spends it.",
        "skill": "Swings round him for " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + ", healing for every "
                 "enemy hit, more for champions. Empowered: " + phy("q_dmg_e", "q_ratio_e") + ", heals x{q_heal_x} (only "
                 "while W is on cooldown).",
        "skill2": "Dashes through an enemy champion for " + phy("e_dmg", "e_ratio") + ", then " + O + "Ruthless Predator" + E +
                  ": two strikes and a " + R_ + "stun" + E + " of " + A + "{w_stun}s" + E + " (empowered: three, " + A +
                  "{w_stun_e}s" + E + "); Q if ready, then a second dash that, empowered, shreds {e_shred}% armour.",
        "ult": "Transforms when the fight starts, for " + A + "{r_t}s" + E + ": +{r_hp} " + HPi + "health, every " + A +
               "{r_period}s" + E + " {r_dmg} + " + HPi + "{r_hp_dmg}% " + M + "magic damage" + E + " round him, and Fury "
               "keeps building.",
        "names": ("Cull the Meek", "Slice and Dice", "Dominus"),
    },
    "ko": {
        "name": "레넥톤",
        "attack": "근접 베기. 기본 지속 효과 " + O + "분노의 지배" + E + ": 공격과 스킬 적중으로 분노 축적(최대 {f_n}중첩, " + A +
                  "{f_t}초" + E + " 동안 쌓지 않으면 사라짐). 가득 차면 다음 스킬이 강화되고 분노를 소모.",
        "skill": "주변을 베어 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + ", 적중한 적마다 체력 회복, 챔피언은 더 많이. "
                 "강화: " + phy("q_dmg_e", "q_ratio_e") + ", 회복 x{q_heal_x}(W 재사용 대기 중일 때만).",
        "skill2": "적 챔피언을 관통 돌진해 " + phy("e_dmg", "e_ratio") + ", 이어서 " + O + "무자비한 포식자" + E + ": 2회 베기와 " +
                  A + "{w_stun}초" + E + " " + R_ + "기절" + E + "(강화: 3회, " + A + "{w_stun_e}초" + E + "). Q가 있으면 Q, "
                  "다시 돌진, 강화 시 방어력 {e_shred}% 감소.",
        "ult": "교전 시 " + A + "{r_t}초" + E + " 변신: " + HPi + "체력 +{r_hp}, " + A + "{r_period}초" + E + "마다 주변에 {r_dmg} + " +
               HPi + "{r_hp_dmg}%의 " + M + "마법 피해" + E + ", 분노가 계속 쌓임.",
        "names": ("양떼 도륙", "자르고 토막내기", "강신"),
    },
    "ja": {
        "name": "レネクトン",
        "attack": "近接斬撃。パッシブ " + O + "激情の支配" + E + "：攻撃とスキルの命中で憤怒を蓄積（最大{f_n}スタック、" + A +
                  "{f_t}秒" + E + "増えないと消失）。最大で次のスキルが強化され憤怒を消費。",
        "skill": "周囲を薙ぎ払い" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "、命中した敵ごとに回復（チャンピオンは多め）。" +
                 "強化：" + phy("q_dmg_e", "q_ratio_e") + "、回復x{q_heal_x}（Wがクールダウン中のみ）。",
        "skill2": "敵チャンピオンを突き抜け" + phy("e_dmg", "e_ratio") + "、続けて" + O + "メッタ斬り" + E + "：2回斬り" + A +
                  "{w_stun}秒" + E + R_ + "スタン" + E + "（強化：3回、" + A + "{w_stun_e}秒" + E + "）。Qがあれば Q、再突進、"
                  "強化で物防{e_shred}%低下。",
        "ult": "交戦時" + A + "{r_t}秒" + E + "変身：" + HPi + "体力+{r_hp}、" + A + "{r_period}秒" + E + "ごとに周囲へ{r_dmg} + " +
               HPi + "{r_hp_dmg}%の" + M + "魔法ダメージ" + E + "、憤怒が溜まり続ける。",
        "names": ("ミートカット", "スライス・アンド・ダイス", "セベクの怒り"),
    },
}

C = "league_renekton_sfx_"
V = "league_renekton_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_renekton_a_swing": [(C + "swing", 0.4, 0.0)],
    "league_renekton_a_hit": [(C + "hit", 0.4, 0.0)],
    "league_renekton_q_cast": [(C + "q_cast", 0.55, 0.0)],
    "league_renekton_q_hit": [(C + "q_hit", 0.35, 0.0)],
    "league_renekton_w_cast": [(C + "w_cast", 0.45, 0.0)],
    "league_renekton_w_super": [(C + "w_super", 0.55, 0.0)],
    "league_renekton_w_stun": [(C + "w_hit", 0.5, 0.0)],
    "league_renekton_w_hit": [(C + "hit", 0.4, 0.0)],
    "league_renekton_e_dash": [(C + "e_dash", 0.5, 0.0)],
    "league_renekton_e_hit": [(C + "e_hit", 0.45, 0.0)],
    "league_renekton_r_cast": [(C + "r_cast", 0.6, 0.0)],
    "league_renekton_r_roar": [(C + "r_roar", 0.55, 0.1)],
    "league_renekton_vo_q": [(V + "q", 0.85, 0.0)],
    "league_renekton_vo_w": [(V + "w", 0.85, 0.0)],
    "league_renekton_vo_e": [(V + "e", 0.85, 0.0)],
    "league_renekton_vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("f_n", "q_dmg", "q_ratio", "q_dmg_e", "q_ratio_e", "q_heal_x", "e_dmg", "e_ratio", "e_shred",
                           "r_hp", "r_dmg", "r_hp_dmg")}
    for k in ("f_t", "w_stun", "w_stun_e", "r_t", "r_period"):
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
    if "Renekton" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Renekton. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
