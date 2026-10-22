"""K'Sante's text (5 languages), sound_info files and his keys in the shared files, numbers from build_ksante.P.

    python tools/kit/setup_ksante.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_ksante in every language, description + skill_name),
sound/sfx/league_ksante_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, K'Sante named). Only his keys change in the shared files. JSON: indent 2, CRLF,
UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 奎桑提 (纳祖芒荣耀): 血性本能, 无双陀斧, 辟路先锋, 大步驰援, 傲岸雄姿; zh_TW 卡桑帝
(納祖瑪之傲): 無畏本能, 恩屠浮強擊, 開山闢路, 精熟腳步, 拼死一搏; ja カ・サンテ: 不屈の本能, 破撃のエントーフォ, 切り開く猛進,
辰砂の足取り, オールアウト; ko 크산테: 불굴의 본능, 엔토포 타격, 길을 여는 자, 발놀림, 총공세.
Slots: skill = Q Ntofo Strikes, skill2 = W Path Maker (Footwork's shield in its text), ult = R All Out; the passive
Dauntless Instinct in the attack's text. No combo sentence in any text (the user's rule); the README says them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_ksante import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_ksante"
VERSION = "0.191.0"     # provisional: above main 0.190.6 (2026-10-22, Zoe #457); the merger bumps it if taken
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # shields, lifesteal
E = "<>"
# champion_view: the face between his eyes (ppu_restyle's face_to: 36 game px over his soles, on his standing point); the
# ban/pick card at base's rule for his head (tools/art/bp_card_audit.py: -39 - the head's top -31.8, a game px under the
# canvas top; the ntofo tips over it are clipped, the table's CLIPPED on purpose)
VIEW = {"face": {"x": 0, "y": -36}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -6}}


def phys(d, r, hp=None):
    """{d} + r% AD (+ hp% of his max health), physical."""
    s = f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"
    return s + (f" + {HPi}{O}{{{hp}}}%{E}" if hp else "")


def t(x):
    return A + x + E


TEXT = {
    "zh-hans": {
        "name": "奎桑提",
        "attack": "陀斧重击。" + O + "血性本能" + E + "：技能命中后，下一次普攻额外造成" + O + "{p_dmg}" + E + " + 目标{p_hp}%最大生命值的物理伤害。",
        "skill": "向前砸地，造成" + phys("q_dmg", "q_ratio", "q_hp") + "物理伤害并减速{q_slow}%。命中叠一层，两层时变成冲击波，" + R + "拉回" + E +
                 "路径上的敌人，造成" + phys("q3_dmg", "q3_ratio", "q3_hp") + "物理伤害。",
        "skill2": "蓄力，受到伤害降低{w_dr}%并获得" + G + "护盾" + E + "，然后冲撞，造成" + phys("w_dmg", "w_ratio") + " + 目标{w_thp}%最大生命值的"
                  "物理伤害，" + R + "击退" + E + "并" + R + "晕眩" + E + t("{w_stun}秒") + "。全盛时不击退晕眩，改为{ao_w_thp}%。",
        "ult": "盾击敌方英雄，造成" + phys("r_dmg", "r_ratio") + "物理伤害并" + R + "击退" + E + "，追上去砸地造成" + phys("r2_dmg", "r2_ratio", "r2_hp") +
               "物理伤害，进入全盛姿态" + t("{ao_t}秒") + "：攻击+{ao_atk}%、攻速+{ao_as}%、" + G + "吸血{ao_vamp}%" + E + "、技能冷却缩短，"
               "护甲和魔抗{ao_def}%。",
        "names": ("无双陀斧", "辟路先锋", "傲岸雄姿"),
    },
    "zh-hant": {
        "name": "卡桑帝",
        "attack": "恩屠浮重擊。" + O + "無畏本能" + E + "：技能命中後，下一次普攻額外造成" + O + "{p_dmg}" + E + " + 目標{p_hp}%最大生命值的物理傷害。",
        "skill": "向前砸地，造成" + phys("q_dmg", "q_ratio", "q_hp") + "物理傷害並緩速{q_slow}%。命中疊一層，兩層時變成衝擊波，" + R + "拉回" + E +
                 "路徑上的敵人，造成" + phys("q3_dmg", "q3_ratio", "q3_hp") + "物理傷害。",
        "skill2": "蓄力，受到傷害降低{w_dr}%並獲得" + G + "護盾" + E + "，然後衝撞，造成" + phys("w_dmg", "w_ratio") + " + 目標{w_thp}%最大生命值的"
                  "物理傷害，" + R + "擊退" + E + "並" + R + "暈眩" + E + t("{w_stun}秒") + "。拼死一搏時不擊退暈眩，改為{ao_w_thp}%。",
        "ult": "盾擊敵方英雄，造成" + phys("r_dmg", "r_ratio") + "物理傷害並" + R + "擊退" + E + "，追上去砸地造成" + phys("r2_dmg", "r2_ratio", "r2_hp") +
               "物理傷害，進入拼死一搏" + t("{ao_t}秒") + "：攻擊+{ao_atk}%、攻速+{ao_as}%、" + G + "吸血{ao_vamp}%" + E + "、技能冷卻縮短，"
               "護甲和魔抗{ao_def}%。",
        "names": ("恩屠浮強擊", "開山闢路", "拼死一搏"),
    },
    "en": {
        "name": "K'Sante",
        "attack": "A heavy ntofo strike. " + O + "Dauntless Instinct" + E + ": after his abilities hit, his next attack deals " + O +
                  "{p_dmg}" + E + " + {p_hp}% of the target's max health bonus physical damage.",
        "skill": "Strikes the ground ahead for " + phys("q_dmg", "q_ratio", "q_hp") + " physical damage, slowing {q_slow}%. Each hit is a "
                 "stack; at two the strike becomes a shockwave that " + R + "pulls" + E + " enemies in for " +
                 phys("q3_dmg", "q3_ratio", "q3_hp") + " physical damage.",
        "skill2": "Braces, taking {w_dr}% less damage behind a " + G + "shield" + E + ", then rams for " + phys("w_dmg", "w_ratio") +
                  " + {w_thp}% of each target's max health physical damage, " + R + "knocking back" + E + " and " + R + "stunning" +
                  E + " for " + t("{w_stun}s") + ". All Out: no knockback or stun, {ao_w_thp}% instead.",
        "ult": "Bashes an enemy champion for " + phys("r_dmg", "r_ratio") + " physical damage, " + R + "knocking it back" + E + ", then "
               "slams it for " + phys("r2_dmg", "r2_ratio", "r2_hp") + ". He goes All Out for " + t("{ao_t}s") + ": +{ao_atk}% attack, "
               "+{ao_as}% attack speed, " + G + "{ao_vamp}% lifesteal" + E + ", shorter cooldowns, {ao_def}% armor and magic resist.",
        "names": ("Ntofo Strikes", "Path Maker", "All Out"),
    },
    "ja": {
        "name": "カ・サンテ",
        "attack": "エントーフォの重撃。" + O + "不屈の本能" + E + "：スキル命中後、次の通常攻撃が" + O + "{p_dmg}" + E +
                  "＋対象の最大体力の{p_hp}%の追加物理ダメージ。",
        "skill": "前方の地面を打ち" + phys("q_dmg", "q_ratio", "q_hp") + "の物理ダメージと{q_slow}%スロウ。命中でスタック、2スタックで衝撃波になり、"
                 "敵を" + R + "引き寄せ" + E + phys("q3_dmg", "q3_ratio", "q3_hp") + "の物理ダメージ。",
        "skill2": "構えて被ダメージ{w_dr}%軽減と" + G + "シールド" + E + "を得て突進し、" + phys("w_dmg", "w_ratio") + "＋対象の最大体力の{w_thp}%の"
                  "物理ダメージ、" + R + "ノックバック" + E + "と" + t("{w_stun}秒") + R + "スタン" + E + "。オールアウト中はノックバック・スタンなしで{ao_w_thp}%。",
        "ult": "敵チャンピオンを盾で打ち" + phys("r_dmg", "r_ratio") + "の物理ダメージと" + R + "ノックバック" + E + "、追って叩きつけ" +
               phys("r2_dmg", "r2_ratio", "r2_hp") + "。" + t("{ao_t}秒") + "オールアウト：攻撃+{ao_atk}%、攻撃速度+{ao_as}%、" + G +
               "ライフスティール{ao_vamp}%" + E + "、CD短縮、物防魔防{ao_def}%。",
        "names": ("破撃のエントーフォ", "切り開く猛進", "オールアウト"),
    },
    "ko": {
        "name": "크산테",
        "attack": "엔토포 강타. " + O + "불굴의 본능" + E + ": 스킬 적중 후 다음 기본 공격이 " + O + "{p_dmg}" + E + " + 대상 최대 체력의 {p_hp}% "
                  "추가 물리 피해.",
        "skill": "앞쪽 땅을 내리쳐 " + phys("q_dmg", "q_ratio", "q_hp") + " 물리 피해와 {q_slow}% 둔화. 적중 시 중첩, 2중첩이면 충격파가 되어 적을 " +
                 R + "끌어당기고" + E + " " + phys("q3_dmg", "q3_ratio", "q3_hp") + " 물리 피해.",
        "skill2": "버티며 받는 피해 {w_dr}% 감소와 " + G + "보호막" + E + "을 얻고 돌진해 " + phys("w_dmg", "w_ratio") + " + 대상 최대 체력의 {w_thp}% "
                  "물리 피해, " + R + "밀쳐내기" + E + "와 " + t("{w_stun}초") + " " + R + "기절" + E + ". 총공세 중에는 대신 {ao_w_thp}%.",
        "ult": "적 챔피언을 방패로 쳐 " + phys("r_dmg", "r_ratio") + " 물리 피해와 " + R + "밀쳐내기" + E + ", 쫓아가 내리찍어 " +
               phys("r2_dmg", "r2_ratio", "r2_hp") + ". " + t("{ao_t}초") + " 동안 총공세: 공격력 +{ao_atk}%, 공격 속도 +{ao_as}%, " + G +
               "생명력 흡수 {ao_vamp}%" + E + ", 재사용 대기시간 감소, 방어력과 마법 저항력 {ao_def}%.",
        "names": ("엔토포 타격", "길을 여는 자", "총공세"),
    },
}

C = "league_ksante_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
# the sfx toward Lux's 0.8 (the level Orianna's and Zoe's got, 2026-10-22; attacks lower: they come often), the voice as
# the other heroes'
SOUNDS = {f"league_ksante_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("ao_a", 0.55), ("p_hit", 0.65), ("q", 0.8), ("q_hit", 0.7), ("q3", 0.85),
    ("q3_hit", 0.8), ("w", 0.8), ("w_dash", 0.75), ("w_land", 0.85), ("w_hit", 0.75), ("r", 0.85), ("r_hit", 0.85),
    ("r_dash", 0.75), ("r_slam", 0.9), ("ao_on", 0.85), ("vo_q", 0.85), ("vo_q3", 0.85), ("vo_w", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(x):
    return f"{x / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_hp", "q_dmg", "q_ratio", "q_hp", "q_slow", "q3_dmg", "q3_ratio", "q3_hp", "w_dr",
                           "w_dmg", "w_ratio", "w_thp", "ao_w_thp", "r_dmg", "r_ratio", "r2_dmg", "r2_ratio", "r2_hp",
                           "ao_atk", "ao_as", "ao_vamp", "ao_def")}
    for k in ("w_stun", "ao_t"):
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
    if "K'Sante" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and K'Sante. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
