"""Smeech's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_smeech.P.

    python tools/kit/setup_smeech.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_scar.py writes for Scar: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_smeech in every language, description + skill_name),
sound/sfx/tft_smeech_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 13's own (CommunityDragon cdragon/tft/<locale>.json, TFT13_Gremlin, 2026-10-29): zh_CN 史密奇, zh_TW
斯米奇, ja スミーチ, ko 스미치, en Smeech; Scrap Hacker = 废铁黑客 / 拼裝駭客 / スクラップハッカー / 고물상 해커; his trait Ambusher =
伏击专家 / 潛伏者 / 伏兵 / 매복자 names the passive. Scrap Rip (拆解) and Scrap Frenzy (废铁狂潮) are our own (TFT has one ability;
the user's pick, plan A 「废铁伏击手」).
The texts are the rules he plays with tft.dll (addons/tft/src/smeech.rs): the skill crits, the leap at the lowest-health
enemy and its re-leap on a kill, the hops to enemies not hit yet.
Sounds: tools/lol/extract_smeech.py's clips in tft/sound/sfx/tft_smeech_sfx_*.wav (git-ignored) - his own set-13 TFT
sounds (the two claws' swings and hits, the crit, the leap and the slashes, his voice on the leap), Kha'Zix's leap and
Taste Their Fear (the landing, the rip), Twitch's Expunge (the armour torn), Kha'Zix's Void Assault and leap, Master
Yi's Alpha Strike and Rengar's empowered Savagery (the frenzy). A clip name never equals an event name (vo-clip-names
rule): event tft_smeech_<x> plays clip tft_smeech_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_smeech import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15 (on its own branch), Smeech 0.16
VERSION = "0.16.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from his soles' point, up negative): the face point between his eyes (the design's eye row 39
# of 87, his soles on row 80, at PPU 2.4: 17 over the ground; 14 ahead of his standing column); the centre in his
# waistcoat; the ban/pick card by bp_card_audit.py's rule (-39 less his top -22: the hat 1 px under the card's top)
VIEW = {"face": {"x": 14, "y": -17}, "center": {"x": 2, "y": -12}, "banpick_center": {"x": 2, "y": -17}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "史密奇",
        "attack": "双爪轮流挥抓，造成" + AD + O + "物理伤害" + E + "。" + O + "伏击专家" + E + "：暴击率" + A + "{p_crit}%" + E +
                  "；技能也能暴击，技能暴击造成" + A + "{p_crit_dmg}%" + E + "伤害。",
        "skill": "跳向范围内" + A + "生命最低" + E + "的敌人，连斩" + A + "3" + E + "次，每次造成" + phys("q_dmg", "q_ad") + O +
                 "物理伤害" + E + "；目标阵亡则再跳一次，伤害为" + A + "{q_again}%" + E + "。",
        "skill2": "双爪撕扯目标，造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "，并使其" + R + "护甲降低{e_shred}%" + E + "，持续" +
                  A + "{e_t}秒" + E + "。",
        "ult": A + "{r_dur}秒" + E + "内" + R + "不受控制" + E + "、减伤" + A + "{r_dr}%" + E + "，接连跳斩最多" + A + "{r_n}" + E +
               "名未被斩过的敌人，每次造成" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "并获得" + A + "{r_crit}%" + E + "暴击率（" + A +
               "{r_t}秒" + E + "）。",
        "names": ("废铁黑客", "拆解", "废铁狂潮"),
    },
    "zh-hant": {
        "name": "斯米奇",
        "attack": "雙爪輪流揮抓，造成" + AD + O + "物理傷害" + E + "。" + O + "潛伏者" + E + "：暴擊率" + A + "{p_crit}%" + E +
                  "；技能也能暴擊，技能暴擊造成" + A + "{p_crit_dmg}%" + E + "傷害。",
        "skill": "跳向範圍內" + A + "生命最低" + E + "的敵人，連斬" + A + "3" + E + "次，每次造成" + phys("q_dmg", "q_ad") + O +
                 "物理傷害" + E + "；目標陣亡則再跳一次，傷害為" + A + "{q_again}%" + E + "。",
        "skill2": "雙爪撕扯目標，造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "，並使其" + R + "護甲降低{e_shred}%" + E + "，持續" +
                  A + "{e_t}秒" + E + "。",
        "ult": A + "{r_dur}秒" + E + "內" + R + "不受控制" + E + "、減傷" + A + "{r_dr}%" + E + "，接連跳斬最多" + A + "{r_n}" + E +
               "名未被斬過的敵人，每次造成" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "並獲得" + A + "{r_crit}%" + E + "暴擊率（" + A +
               "{r_t}秒" + E + "）。",
        "names": ("拼裝駭客", "拆解", "廢鐵狂潮"),
    },
    "en": {
        "name": "Smeech",
        "attack": "Rakes with each claw in turn for " + AD + " " + O + "physical damage" + E + ". " + O + "Ambusher" + E + ": " + A +
                  "{p_crit}%" + E + " crit chance; his abilities can crit too, for " + A + "{p_crit_dmg}%" + E + " damage.",
        "skill": "Leaps at the " + A + "lowest-health" + E + " enemy in range and slashes it " + A + "3" + E + " times for " +
                 phys("q_dmg", "q_ad") + " " + O + "physical damage" + E + " each. If it dies, he leaps again for " + A +
                 "{q_again}%" + E + " damage.",
        "skill2": "Rips the target with both claws for " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E + ", " + R +
                  "shredding {e_shred}% of its armor" + E + " for " + A + "{e_t}s" + E + ".",
        "ult": "For " + A + "{r_dur}s" + E + " he is " + R + "unstoppable" + E + " and takes " + A + "{r_dr}%" + E + " less damage, "
               "leaping at up to " + A + "{r_n}" + E + " enemies he has not yet hit, each for " + phys("r_dmg", "r_ad") + " " + O +
               "physical damage" + E + ", gaining " + A + "{r_crit}%" + E + " crit chance for " + A + "{r_t}s" + E + " per leap.",
        "names": ("Scrap Hacker", "Scrap Rip", "Scrap Frenzy"),
    },
    "ko": {
        "name": "스미치",
        "attack": "양 발톱으로 번갈아 할퀴어 " + AD + " " + O + "물리 피해" + E + ". " + O + "매복자" + E + ": 치명타 확률 " + A +
                  "{p_crit}%" + E + "; 스킬도 치명타 가능, 스킬 치명타는 " + A + "{p_crit_dmg}%" + E + " 피해.",
        "skill": "범위 내 " + A + "체력이 가장 낮은" + E + " 적에게 도약해 " + A + "3" + E + "회 베어 각각 " + phys("q_dmg", "q_ad") + " " + O +
                 "물리 피해" + E + "; 대상이 죽으면 " + A + "{q_again}%" + E + " 피해로 다시 도약.",
        "skill2": "양 발톱으로 대상을 찢어 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + A + "{e_t}초" + E + " 동안 " + R +
                  "방어력 {e_shred}% 감소" + E + ".",
        "ult": A + "{r_dur}초" + E + " 동안 " + R + "저지 불가" + E + ", 피해 " + A + "{r_dr}%" + E + " 감소, 아직 베지 않은 적에게 최대 " + A +
               "{r_n}" + E + "회 도약해 각각 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + ", 도약마다 치명타 확률 " + A +
               "{r_crit}%" + E + "(" + A + "{r_t}초" + E + ").",
        "names": ("고물상 해커", "분해", "고물 광란"),
    },
    "ja": {
        "name": "スミーチ",
        "attack": "左右の爪で交互に引っかき、" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "伏兵" + E + "：クリティカル率" + A +
                  "{p_crit}%" + E + "。スキルもクリティカルし、" + A + "{p_crit_dmg}%" + E + "のダメージ。",
        "skill": "範囲内で" + A + "体力が最も低い" + E + "敵に跳びかかり" + A + "3" + E + "回斬りつけ、各" + phys("q_dmg", "q_ad") + "の" + O +
                 "物理ダメージ" + E + "。倒すと" + A + "{q_again}%" + E + "のダメージで再跳躍。",
        "skill2": "両爪で対象を引き裂き、" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + A + "{e_t}秒" + E + "間" + R +
                  "物理防御{e_shred}%低下" + E + "。",
        "ult": A + "{r_dur}秒" + E + "間" + R + "阻止不能" + E + "、被ダメージ" + A + "{r_dr}%" + E + "軽減。まだ斬っていない敵に最大" + A +
               "{r_n}" + E + "回跳びかかり、各" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "、跳躍ごとにクリティカル率" + A +
               "{r_crit}%" + E + "（" + A + "{r_t}秒" + E + "）。",
        "names": ("スクラップハッカー", "解体", "スクラップフレンジー"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_smeech's sfx / tsfx) and tft.dll's
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.4, 0.0)],
    f"{ID}_a2": [(CLIP + "a2", 0.4, 0.0)],
    f"{ID}_a2_hit": [(CLIP + "a2_hit", 0.4, 0.0)],
    f"{ID}_p_hit": [(CLIP + "p", 0.4, 0.0), (CLIP + "p_hit", 0.5, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.45, 0.0)],
    f"{ID}_q_vo": [(CLIP + "q_vo", 0.6, 0.0)],
    f"{ID}_q_land": [(CLIP + "q_land", 0.45, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.45, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_e_hit": [(CLIP + "e_hit", 0.5, 0.0)],
    f"{ID}_e_shred": [(CLIP + "e_shred", 0.4, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.5, 0.0)],
    f"{ID}_r_leap": [(CLIP + "r_leap", 0.4, 0.0)],
    f"{ID}_r_hit": [(CLIP + "r_hit", 0.5, 0.0)],
    f"{ID}_r_end": [(CLIP + "r_end", 0.5, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/smeech.rs: the landing, the slashes, the hops' hits, a skill crit)
DLL_SOUNDS = {f"{ID}_q_land", f"{ID}_q_hit", f"{ID}_r_hit", f"{ID}_p_hit"}


def values(p):
    v = {k: p[k] for k in ("p_crit", "q_dmg", "q_ad", "q_again", "e_dmg", "e_ad", "e_shred", "r_dr", "r_n", "r_dmg", "r_ad",
                           "r_crit")}
    v["p_crit_dmg"] = 200 + p["p_cdmg"]
    for k in ("e_t", "r_dur", "r_t"):
        v[k] = secs(p[k])
    return v


def kit_sounds():
    """Every Sfx / TargetSfx name the kit plays."""
    found = set()

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") in ("Sfx", "TargetSfx"):
                found.add(o["name"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(load(os.path.join(MOD, "champion", f"{ID}.data_champion")))
    return found


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
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    p = dict(P)
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

    played = kit_sounds() | DLL_SOUNDS
    if played != set(SOUNDS):
        sys.exit(f"the kit plays {sorted(played - set(SOUNDS))} without a sound_info, SOUNDS has unused "
                 f"{sorted(set(SOUNDS) - played)}")

    i18n = load(os.path.join(MOD, "text", "champion.i18n"), {})
    for lang, (d, names) in tx.items():
        i18n.setdefault(lang, {}).setdefault("description", {})[ID] = d
        i18n[lang].setdefault("skill_name", {})[ID] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    clips = set()
    for name, plays in SOUNDS.items():
        for c, _, _ in plays:
            if c == name:
                sys.exit(f"{name}: plays a clip of its own name")
            if not os.path.isfile(lp(os.path.join(MOD, "sound", "sfx", c + ".wav"))):
                print(f"warning: {c}.wav missing - run tools/lol/extract_smeech.py")
            clips.add(c)
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    ov.setdefault("asset/base/text/champion", {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"})
    ov.setdefault("asset/base/style/champion_view",
                  {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"})
    for k in [k for k in ov if k.startswith(f"asset/base/sound/sfx/{ID}_")]:   # his sound keys rebuilt
        del ov[k]
    for name in list(SOUNDS) + sorted(clips):
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/{MOD_ID}/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"), {"entries": {}})
    cv["entries"][ID] = json.loads(json.dumps(VIEW))
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"))
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    mi["description"] = pack.DESC.format(heroes=", ".join(pack.HEROES))
    mi["contains_code"], mi["mod_type"] = True, "native"     # tft.dll (addons/tft): his rules the data cannot play
    mi["last_updated"] = "2026-10-29"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
