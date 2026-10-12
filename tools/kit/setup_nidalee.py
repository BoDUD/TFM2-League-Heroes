"""Nidalee's text (5 languages), sound_info files and her keys in the shared files, numbers from build_nidalee.P.

    python tools/kit/setup_nidalee.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_nidalee in every language, description + skill_name),
sound/sfx/league_nidalee_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.105.0, Nidalee named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (奈德丽 / 狂野女猎手; 寻觅, 标枪投掷 / 推倒, 丛林伏击 / 猛扑, 野性奔腾 / 挥击, 美洲狮形态; the
client swaps name and title) and Data Dragon 16.20.1 (zh_TW 奈德麗 / 穿梭 / 標槍投擲／擊倒 / 叢林伏擊／猛撲 / 野性奔騰／揮擊 /
美洲獅之形, ja ニダリー / 品定め / 槍投げ/テイクダウン / 虎挟み/ジャンプ / 高揚/クロウ / クーガーの心, ko 니달리 / 수풀 배회 / 창 투척 /
숨통 끊기 / 매복 덫 / 급습 / 태고의 생명력 / 할퀴기 / 쿠거의 상).
Slots: skill = Q (both forms), skill2 = E + W (human) / W + E (cougar), ult = the hunt pounce (R's name); the passive and
the form switch are told in the attack's text. No combo sentence in any text (the user's rule). No
`league_nidalee_attack` sound: the engine would play it at the start of every attack; the throw plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_nidalee import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_nidalee"
VERSION = "0.105.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
D = "<#ff8a65ff>"      # physical damage
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
G = "<#7dd87dff>"      # heals
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 4, "y": -34}, "center": {"x": 0, "y": -12}}


def mag(k):
    return f"{M}{{{k}_dmg}}{E}+{APi}{M}{{{k}_ap}}%{E}"


Q = M + "{q_dmg}" + E + "+" + APi + M + "{q_ap}%" + E
TD = D + "{cq_dmg}" + E + "+" + ADi + D + "{cq_ad}%" + E
TDM = M + "{cq_mdmg}" + E + "+" + APi + M + "{cq_ap}%" + E
HEAL = G + "{e_heal}" + E + "+" + APi + G + "{e_ap}%" + E

TEXT = {
    "zh-hans": {
        "name": "奈德丽",
        "attack": O + "寻觅" + E + "：标枪或夹子命中英雄将其捕猎" + A + "{p_t}秒" + E + "，期间移速+{p_ms}%。出手前按战况切换人形（远程）和美洲狮（近战）形态，切换冷却" +
                  A + "{r_cd}秒" + E + "。",
        "skill": "人形：投出标枪造成" + Q + M + "魔法伤害" + E + "，飞得越远越高（最多{q_far}%）。" + O + "推倒" + E + "：下次攻击额外造成" + TD + D + "物理" + E + "和" +
                 TDM + M + "魔法伤害" + E + "，对捕猎目标+{cq_h}%。",
        "skill2": "人形：治疗友方英雄" + HEAL + "，攻速+{e_as}%持续" + A + "{e_as_t}秒" + E + "；冷却时放" + O + "丛林伏击" + E + "，持续造成" + mag("w") + M + "魔法伤害" +
                  E + "。" + O + "猛扑" + E + "：扑向敌人造成" + mag("cw") + M + "魔法伤害" + E + "；" + O + "挥击" + E + "造成" + mag("ce") + M + "魔法伤害" + E + "。",
        "ult": "化身美洲狮，重置美洲狮技能，扑向英雄造成" + mag("r") + M + "魔法伤害" + E + "，落地挥击并准备推倒。",
        "names": ("标枪投掷 / 推倒", "野性奔腾 / 猛扑", "美洲狮形态"),
    },
    "zh-hant": {
        "name": "奈德麗",
        "attack": O + "穿梭" + E + "：標槍或陷阱命中英雄將其狩獵" + A + "{p_t}秒" + E + "，期間跑速+{p_ms}%。出手前依戰況切換人形（遠程）和美洲獅（近戰）形態，切換冷卻" +
                  A + "{r_cd}秒" + E + "。",
        "skill": "人形：擲出標槍造成" + Q + M + "魔法傷害" + E + "，飛得越遠越高（最多{q_far}%）。" + O + "擊倒" + E + "：下次攻擊額外造成" + TD + D + "物理" + E + "和" +
                 TDM + M + "魔法傷害" + E + "，對狩獵目標+{cq_h}%。",
        "skill2": "人形：治療友方英雄" + HEAL + "，攻速+{e_as}%持續" + A + "{e_as_t}秒" + E + "；冷卻時放" + O + "叢林伏擊" + E + "，持續造成" + mag("w") + M + "魔法傷害" +
                  E + "。" + O + "猛撲" + E + "：撲向敵人造成" + mag("cw") + M + "魔法傷害" + E + "；" + O + "揮擊" + E + "造成" + mag("ce") + M + "魔法傷害" + E + "。",
        "ult": "化身美洲獅，重置美洲獅技能，撲向英雄造成" + mag("r") + M + "魔法傷害" + E + "，落地揮擊並準備擊倒。",
        "names": ("標槍投擲／擊倒", "野性奔騰／猛撲", "美洲獅之形"),
    },
    "en": {
        "name": "Nidalee",
        "attack": O + "Prowl" + E + ": javelin and trap hits hunt a champion for " + A + "{p_t}s" + E + " (+{p_ms}% move speed). Before each attack she "
                  "switches between human (ranged) and cougar (melee) as the fight needs, every " + A + "{r_cd}s" + E + " at most.",
        "skill": "Human: throws a javelin for " + Q + " " + M + "magic damage" + E + ", more the farther it flies (up to {q_far}%). " + O + "Takedown" + E +
                 ": her next attack deals " + TD + " " + D + "physical" + E + " and " + TDM + " " + M + "magic damage" + E + " more, +{cq_h}% on the hunted.",
        "skill2": "Human: heals an allied champion for " + HEAL + " and gives {e_as}% attack speed for " + A + "{e_as_t}s" + E + "; on cooldown she sets a " + O +
                  "Bushwhack" + E + " trap, " + mag("w") + " " + M + "magic damage" + E + " a pulse. " + O + "Pounce" + E + ": leaps for " + mag("cw") + " " + M +
                  "magic damage" + E + "; " + O + "Swipe" + E + ": " + mag("ce") + " " + M + "magic damage" + E + " around her.",
        "ult": "Turns into the cougar, resets the cougar's abilities and pounces on a champion for " + mag("r") + " " + M + "magic damage" + E +
               ", then swipes and readies Takedown.",
        "names": ("Javelin Toss / Takedown", "Primal Surge / Pounce", "Aspect of the Cougar"),
    },
    "ko": {
        "name": "니달리",
        "attack": O + "수풀 배회" + E + ": 창이나 덫에 맞은 챔피언을 " + A + "{p_t}초" + E + " 동안 사냥 (이동 속도 +{p_ms}%). 공격 전에 상황에 따라 인간(원거리)과 쿠거(근접) 형태를 "
                  "바꾸며, 전환 대기시간 " + A + "{r_cd}초" + E + ".",
        "skill": "인간: 창을 던져 " + Q + " " + M + "마법 피해" + E + ", 멀리 날수록 증가 (최대 {q_far}%). " + O + "숨통 끊기" + E + ": 다음 공격이 " + TD + " " + D + "물리" + E +
                 "와 " + TDM + " " + M + "마법 피해" + E + " 추가, 사냥 대상 +{cq_h}%.",
        "skill2": "인간: 아군 챔피언 " + HEAL + " 회복, " + A + "{e_as_t}초" + E + " 동안 공격 속도 +{e_as}%; 대기 중이면 " + O + "매복 덫" + E + "으로 " + mag("w") + " " + M +
                  "마법 피해" + E + " 지속. " + O + "급습" + E + ": 도약해 " + mag("cw") + " " + M + "마법 피해" + E + "; " + O + "할퀴기" + E + ": " + mag("ce") + " " + M +
                  "마법 피해" + E + ".",
        "ult": "쿠거로 변해 쿠거 스킬을 초기화하고 챔피언에게 도약해 " + mag("r") + " " + M + "마법 피해" + E + ", 착지 후 할퀴고 숨통 끊기를 준비.",
        "names": ("창 투척 / 숨통 끊기", "태고의 생명력 / 급습", "쿠거의 상"),
    },
    "ja": {
        "name": "ニダリー",
        "attack": O + "品定め" + E + "：槍か虎挟みが当たったチャンピオンを" + A + "{p_t}秒" + E + "狩る（移動速度+{p_ms}%）。攻撃の前に戦況で人間（遠隔）とクーガー（近接）を切り替え、間隔" +
                  A + "{r_cd}秒" + E + "。",
        "skill": "人間：槍を投げ" + Q + "の" + M + "魔法ダメージ" + E + "、遠いほど増加（最大{q_far}%）。" + O + "テイクダウン" + E + "：次の通常攻撃に" + TD + "の" + D + "物理" + E +
                 "と" + TDM + "の" + M + "魔法ダメージ" + E + "、狩る相手に+{cq_h}%。",
        "skill2": "人間：味方チャンピオンを" + HEAL + "回復、攻撃速度+{e_as}%（" + A + "{e_as_t}秒" + E + "）；クールダウン中は" + O + "虎挟み" + E + "で" + mag("w") + "の" + M +
                  "魔法ダメージ" + E + "。" + O + "ジャンプ" + E + "：飛びかかり" + mag("cw") + "の" + M + "魔法ダメージ" + E + "；" + O + "クロウ" + E + "：" + mag("ce") + "の" + M +
                  "魔法ダメージ" + E + "。",
        "ult": "クーガーに変身しクーガーのスキルをリセット、チャンピオンへ飛びかかり" + mag("r") + "の" + M + "魔法ダメージ" + E + "、着地でクロウ、テイクダウン準備。",
        "names": ("槍投げ/テイクダウン", "高揚/ジャンプ", "クーガーの心"),
    },
}

C = "league_nidalee_sfx_"
S_ = "league_nidalee_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + k, vol, 0.0)] for k, vol in [
    ("a_throw", 0.45), ("a_hit", 0.45), ("c_swing", 0.45), ("c_hit", 0.45), ("cq_arm", 0.5), ("cq", 0.5),
    ("cq_hit", 0.55), ("q", 0.55), ("q_hit", 0.55), ("e", 0.55), ("e_heal", 0.5), ("w", 0.5), ("w_land", 0.5),
    ("w_snap", 0.55), ("cw", 0.5), ("cw_land", 0.55), ("cw_hit", 0.5), ("ce", 0.55), ("ce_hit", 0.5),
    ("tf_cougar", 0.55), ("tf_human", 0.55), ("r", 0.6), ("r_hit", 0.6),
    ("vo_q", 0.8), ("vo_w", 0.8), ("vo_e", 0.8), ("vo_cougar", 0.8), ("vo_human", 0.8), ("vo_cq", 0.75),
    ("vo_cw", 0.75), ("vo_ce", 0.75), ("vo_r", 0.85)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_ms", "q_dmg", "q_ap", "q_far", "cq_dmg", "cq_ad", "cq_mdmg", "cq_ap", "e_heal", "e_ap",
                           "e_as", "w_dmg", "w_ap", "cw_dmg", "cw_ap", "ce_dmg", "ce_ap", "r_dmg", "r_ap")}
    v.update({k: secs(p[k]) for k in ("p_t", "e_as_t")})
    v["r_cd"] = secs(p["r_cd_t"])
    v["cq_h"] = p["cq_h"] - 100
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
    for k in [k for k in ov if ID in k]:      # her keys rebuilt (a renamed sound leaves none behind)
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
    if "Nidalee" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Nidalee. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
