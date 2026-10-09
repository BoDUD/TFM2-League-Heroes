"""Olaf's text (5 languages), sound_info files and his keys in the shared files, numbers from build_olaf.P.

    python tools/kit/setup_olaf.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in ol/league): text/champion.i18n (league_olaf in every language, description + skill_name),
sound/sfx/league_olaf_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.85.0, Olaf named). Only his keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 狂战之怒 / 逆流投掷 / 挺过去 / 鲁莽挥击 / 诸神黄昏, zh_TW 歐拉夫 / 狂戰之怒 / 逆流投擲 /
咬牙苦撐 / 魯莽揮擊 / 諸神黃昏, ja オラフ / 狂戦士の怒り / 斧投げ / 根性比べ / 捨て身切り / ラグナロク, ko 올라프 / 광전사의 분노 /
역류 / 버티기 / 무모한 강타 / 라그나로크). The slot names: skill = Q, skill2 = E, ult = R; the passive and the automatic W
are told in the attack's text.
No `league_olaf_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_olaf import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_olaf"
VERSION = "0.85.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control, immunity
W = "<#f5f5f5ff>"      # true damage
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -34}, "center": {"x": 0, "y": -12}}


def phy(k):
    return f"{O}{{{k}_dmg}}{E} + {ADi}{O}{{{k}_ratio}}%{E}"


def tru(k):
    return f"{W}{{{k}_dmg}}{E} + {ADi}{W}{{{k}_ratio}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "奥拉夫",
        "attack": O + "狂战之怒" + E + "：越挨打攻速越高（每层+{p_as}%，共{p_n}层），最高两层吸血{p_vamp}%。" +
                  O + "挺过去" + E + "（自动，" + A + "{w_cd}秒" + E + "）：交战时攻速+{w_as}%并获得护盾。" +
                  O + "诸神黄昏" + E + "被动：护甲、魔抗+{r_def}。",
        "skill": "向目标所在处掷斧，沿途造成" + phy("q") + "伤害，" + R + "减速{q_slow}%" + E + "、护甲-{q_shred}%。斧头插地" + A +
                 "{q_life}秒" + E + "，走过去捡起则冷却大幅缩短。",
        "skill2": "鲁莽挥击，造成" + tru("e") + W + "真实伤害" + E + "，自己承受其中{e_self}%；击杀则返还。",
        "ult": R + "免疫控制" + E + "，攻击力+{r_atk}%、移速+{r_ms}%，持续" + A + "{r_t}秒" + E + "；攻击英雄时延续（最多" + A + "{r_max}秒" + E +
               "）。" + O + "连招" + E + "：R冲入→E→捡斧再投。",
        "names": ("逆流投掷", "鲁莽挥击", "诸神黄昏"),
    },
    "zh-hant": {
        "name": "歐拉夫",
        "attack": O + "狂戰之怒" + E + "：越挨打攻速越高（每層+{p_as}%，共{p_n}層），最高兩層吸血{p_vamp}%。" +
                  O + "咬牙苦撐" + E + "（自動，" + A + "{w_cd}秒" + E + "）：交戰時攻速+{w_as}%並獲得護盾。" +
                  O + "諸神黃昏" + E + "被動：護甲、魔抗+{r_def}。",
        "skill": "向目標所在處擲斧，沿途造成" + phy("q") + "傷害，" + R + "緩速{q_slow}%" + E + "、護甲-{q_shred}%。斧頭插地" + A +
                 "{q_life}秒" + E + "，走過去撿起則冷卻大幅縮短。",
        "skill2": "魯莽揮擊，造成" + tru("e") + W + "真實傷害" + E + "，自己承受其中{e_self}%；擊殺則返還。",
        "ult": R + "免疫控場" + E + "，攻擊力+{r_atk}%、移速+{r_ms}%，持續" + A + "{r_t}秒" + E + "；攻擊英雄時延續（最多" + A + "{r_max}秒" + E +
               "）。" + O + "連招" + E + "：R衝入→E→撿斧再擲。",
        "names": ("逆流投擲", "魯莽揮擊", "諸神黃昏"),
    },
    "en": {
        "name": "Olaf",
        "attack": "Axe swing. " + O + "Berserker Rage" + E + ": the more he is hit, the faster he attacks (+{p_as}% a level, {p_n} "
                  "levels; the top two also {p_vamp}% life steal). " + O + "Tough It Out" + E + " (automatic, " + A + "{w_cd}s" + E +
                  "): in a fight +{w_as}% attack speed and a shield. " + O + "Ragnarok" + E + " passive: +{r_def} armour and magic "
                  "resistance.",
        "skill": "Throws an axe at the target's spot: " + phy("q") + " to every enemy on the way, " + R + "slowed {q_slow}%" + E +
                 ", armour -{q_shred}%. The axe stays " + A + "{q_life}s" + E + "; walking over it picks it up and cuts the "
                 "cooldown short.",
        "skill2": "A reckless blow for " + tru("e") + W + " true damage" + E + "; he takes {e_self}% of it himself, refunded on a "
                  "kill.",
        "ult": R + "Immune to crowd control" + E + ", +{r_atk}% attack and +{r_ms}% move speed for " + A + "{r_t}s" + E + "; hitting "
               "champions keeps it going (up to " + A + "{r_max}s" + E + "). " + O + "Combo" + E + ": R in, E, pick up the axe, "
               "throw again.",
        "names": ("Undertow", "Reckless Swing", "Ragnarok"),
    },
    "ko": {
        "name": "올라프",
        "attack": O + "광전사의 분노" + E + ": 맞을수록 공격 속도 증가(단계당 +{p_as}%, {p_n}단계, 상위 두 단계 생명력 흡수 {p_vamp}%). " +
                  O + "버티기" + E + "(자동, " + A + "{w_cd}초" + E + "): 교전 시 공격 속도 +{w_as}%와 보호막. " +
                  O + "라그나로크" + E + " 기본 지속 효과: 방어력·마법 저항력 +{r_def}.",
        "skill": "대상 위치로 도끼를 던져 지나는 적에게 " + phy("q") + "의 피해, " + R + "{q_slow}% 둔화" + E + ", 방어력 -{q_shred}%. 도끼는 " +
                 A + "{q_life}초" + E + " 꽂혀 있고, 주우면 재사용 대기시간이 크게 줄어듦.",
        "skill2": "무모한 강타로 " + tru("e") + W + " 고정 피해" + E + ", 자신도 그 {e_self}%를 받음; 처치 시 돌려받음.",
        "ult": R + "군중 제어 면역" + E + ", 공격력 +{r_atk}%, 이동 속도 +{r_ms}%, " + A + "{r_t}초" + E + "; 챔피언 공격 시 연장(최대 " + A +
               "{r_max}초" + E + "). " + O + "연계" + E + ": R 돌진→E→도끼 줍고 재투척.",
        "names": ("역류", "무모한 강타", "라그나로크"),
    },
    "ja": {
        "name": "オラフ",
        "attack": O + "狂戦士の怒り" + E + "：殴られるほど攻撃速度上昇（1段階+{p_as}%、{p_n}段階、上位2段階はライフスティール{p_vamp}%）。" +
                  O + "根性比べ" + E + "（自動、" + A + "{w_cd}秒" + E + "）：交戦時に攻撃速度+{w_as}%とシールド。" +
                  O + "ラグナロク" + E + "自動効果：物防・魔防+{r_def}。",
        "skill": "対象の位置へ斧を投げ、通過した敵に" + phy("q") + "、" + R + "{q_slow}%スロウ" + E + "、物防-{q_shred}%。斧は" + A +
                 "{q_life}秒" + E + "地面に残り、拾うとクールダウンが大きく短縮。",
        "skill2": "捨て身の一撃で" + tru("e") + W + "確定ダメージ" + E + "、自身もその{e_self}%を受ける；倒せば返還。",
        "ult": R + "行動妨害無効" + E + "、攻撃力+{r_atk}%、移動速度+{r_ms}%、" + A + "{r_t}秒" + E + "；チャンピオンを攻撃すると延長（最大" + A +
               "{r_max}秒" + E + "）。" + O + "コンボ" + E + "：Rで突入→E→斧を拾って再投擲。",
        "names": ("斧投げ", "捨て身切り", "ラグナロク"),
    },
}

C = "league_olaf_sfx_"
V = "league_olaf_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
S = "league_olaf_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    S + "a_swing": [(C + "attack", 0.45, 0.0)],
    S + "a_hit": [(C + "attack_hit", 0.35, 0.0)],
    S + "q": [(C + "q", 0.5, 0.0)],
    S + "q_hit": [(C + "q_hit", 0.4, 0.0)],
    S + "q_land": [(C + "q_land", 0.45, 0.0)],
    S + "q_pick": [(C + "q_pick", 0.5, 0.0)],
    S + "w": [(C + "w", 0.5, 0.0)],
    S + "e": [(C + "e", 0.5, 0.0)],
    S + "e_hit": [(C + "e_hit", 0.45, 0.0)],
    S + "r": [(C + "r", 0.6, 0.0)],
    S + "vo_q": [(V + "q", 0.8, 0.0)],
    S + "vo_w": [(V + "w", 0.8, 0.0)],
    S + "vo_e": [(V + "e", 0.8, 0.0)],
    S + "vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_as", "p_n", "p_vamp", "w_as", "r_def", "q_dmg", "q_ratio", "q_slow", "q_shred", "e_dmg",
                           "e_ratio", "e_self", "r_atk", "r_ms")}
    v.update({k: secs(p[k]) for k in ("w_cd", "q_life", "r_t", "r_max")})
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
    if "Olaf" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Olaf. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
