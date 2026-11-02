"""Silco's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_silco.P.

    python tools/kit/setup_silco.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft): mod.mod_info (VERSION, the pack's description:
setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys sorted,
setup_alune.py's way), text/champion.i18n (tft_silco in every language, description + skill_name),
sound/sfx/tft_silco_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 13's own (CommunityDragon latest cdragon/tft/<locale>.json, TFT13_Silco): zh_CN 希尔科, zh_TW 希爾科, ja
シルコ, ko 실코; Canned Monstrosity = 罐装畸变体 / 罐裝怪物 / 缶詰めの怪物 / 통에 담긴 괴수; his trait Dominator = 统领 / 霸主 /
ドミネーター / 지배자 names the passive. Shimmer Shot (微光注射) and Chem-Baron's Flood (炼金狂潮) are our own (TFT has one
ability; the user's pick, plan A 「统领·畸变体」). The texts are the rules he plays with tft.dll (addons/tft/src/silco.rs):
the shield at every spawn, the monstrosities that leap on to the next enemy, the dose for the strongest ally nearby and
its comedown, the fog.
Sounds: tools/lol/extract_silco.py's clips in tft/sound/sfx/tft_silco_sfx_*.wav (git-ignored) - his own set-13 TFT sounds
(the vial's throw and hit, the canister's throw and burst, his voice line on the ult), Naafiri's packmates' bite for the
monstrosities, Renata Glasc's chemtech dose for Shimmer Shot and Gragas's Explosive Cask for the giant canister. A clip
name never equals an event name (vo-clip-names rule): event tft_silco_<x> plays clip tft_silco_sfx_<x>. package_mod moves
the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_silco import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
VERSION = "0.5.0"      # Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5: the next free one at merge
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from his soles' point, up negative): the face point between his eyes (the design's eye row 14 of
# 80 at PPU 2: 33 over the ground, 2 ahead of his standing column); the centre in his body; the ban/pick card by
# bp_card_audit.py's rule (y = -39 - top: his lo_idle reaches 29.3 over its centre -> -10, the hair a pixel under the
# canvas top; 41 px tall on the 40-px canvas, the soles 2 px under its bottom, no UI size)
# center: the encyclopedia card puts this point at a fixed spot - set by League's rule (tools/art/bp_card_audit.py --centers, 2026-11-01)
VIEW = {"face": {"x": 2, "y": -33}, "center": {"x": 0, "y": -13}, "banpick_center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "希尔科",
        "attack": "甩出一支微光药剂，造成" + AD + O + "物理伤害" + E + "。" + O + "统领" + E + "：每次出生获得" + mag("s_amt", "s_ap") +
                  "护盾（" + A + "{s_t}秒" + E + "）；每放一次技能法强+" + A + "{d_ap}%" + E + "，最多" + A + "{d_max}" + E + "层，阵亡清空。",
        "skill": "扔出储罐，造成" + mag("q_dmg", "q_ratio") + "魔法伤害，放出" + A + "{q_n}" + E + "只畸变体扑向附近的敌人，各咬" + A +
                 "{m_n}" + E + "口，每口" + mag("m_dmg", "m_ratio") + "魔法伤害；被咬的人倒下就跳到下一个。",
        "skill2": "把微光抛给身边攻击力最高的友方英雄（没有就自己）：攻速+" + A + "{e_as}%" + E + "、移速+" + A + "{e_ms}%" + E + "，" + A +
                  "{e_t}秒" + E + "；药效过去扣当前生命的" + A + "{e_cost}%" + E + "。",
        "ult": "向敌方英雄扔出巨型储罐，造成" + mag("r_dmg", "r_ratio") + "魔法伤害，放出" + A + "{r_n}" + E + "只畸变体，留下" + A +
               "{r_fog_t}秒" + E + "毒雾：敌人" + R + "减速" + E + A + "{r_slow}%" + E + "，每秒受到" + mag("r_fog_dmg", "r_fog_ratio") +
               "魔法伤害。",
        "names": ("罐装畸变体", "微光注射", "炼金狂潮"),
    },
    "zh-hant": {
        "name": "希爾科",
        "attack": "甩出一支微光藥劑，造成" + AD + O + "物理傷害" + E + "。" + O + "霸主" + E + "：每次出生獲得" + mag("s_amt", "s_ap") +
                  "護盾（" + A + "{s_t}秒" + E + "）；每施放一次技能法術強度+" + A + "{d_ap}%" + E + "，最多" + A + "{d_max}" + E + "層，陣亡清空。",
        "skill": "扔出儲罐，造成" + mag("q_dmg", "q_ratio") + "魔法傷害，放出" + A + "{q_n}" + E + "隻怪物撲向附近的敵人，各咬" + A +
                 "{m_n}" + E + "口，每口" + mag("m_dmg", "m_ratio") + "魔法傷害；被咬的人倒下就跳到下一個。",
        "skill2": "把微光拋給身邊攻擊力最高的友方英雄（沒有就自己）：攻速+" + A + "{e_as}%" + E + "、移速+" + A + "{e_ms}%" + E + "，" + A +
                  "{e_t}秒" + E + "；藥效過去扣除目前生命的" + A + "{e_cost}%" + E + "。",
        "ult": "向敵方英雄扔出巨型儲罐，造成" + mag("r_dmg", "r_ratio") + "魔法傷害，放出" + A + "{r_n}" + E + "隻怪物，留下" + A +
               "{r_fog_t}秒" + E + "毒霧：敵人" + R + "緩速" + E + A + "{r_slow}%" + E + "，每秒受到" + mag("r_fog_dmg", "r_fog_ratio") +
               "魔法傷害。",
        "names": ("罐裝怪物", "微光注射", "鍊金狂潮"),
    },
    "en": {
        "name": "Silco",
        "attack": "Flings a Shimmer vial for " + AD + " " + O + "physical damage" + E + ". " + O + "Dominator" + E + ": each time "
                  "he spawns he gains a " + mag("s_amt", "s_ap") + " shield for " + A + "{s_t}s" + E + "; each skill he casts "
                  "grants " + A + "{d_ap}%" + E + " ability power, up to " + A + "{d_max}" + E + " times, lost on death.",
        "skill": "Throws a canister for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " and lets out " + A + "{q_n}" +
                 E + " monstrosities that pounce on nearby enemies and bite " + A + "{m_n}" + E + " times each for " +
                 mag("m_dmg", "m_ratio") + " " + M + "magic damage" + E + "; when their victim falls they leap to the next.",
        "skill2": "Tosses Shimmer to the allied champion with the most attack near him (himself if none): " + A + "{e_as}%" + E +
                  " attack speed and " + A + "{e_ms}%" + E + " move speed for " + A + "{e_t}s" + E + "; the comedown then takes " +
                  A + "{e_cost}%" + E + " of their current health.",
        "ult": "Throws a giant canister at an enemy champion for " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E +
               ", letting out " + A + "{r_n}" + E + " monstrosities and leaving a Shimmer fog for " + A + "{r_fog_t}s" + E +
               ": enemies in it are " + R + "slowed" + E + " by " + A + "{r_slow}%" + E + " and take " +
               mag("r_fog_dmg", "r_fog_ratio") + " " + M + "magic damage" + E + " a second.",
        "names": ("Canned Monstrosity", "Shimmer Shot", "Chem-Baron's Flood"),
    },
    "ko": {
        "name": "실코",
        "attack": "시머 약병을 던져 " + AD + " 물리 피해. " + O + "지배자" + E + ": 등장할 때마다 " + mag("s_amt", "s_ap") + " 보호막(" + A +
                  "{s_t}초" + E + "). 스킬을 쓸 때마다 주문력 +" + A + "{d_ap}%" + E + "(최대 " + A + "{d_max}" + E + "번, 죽으면 사라짐).",
        "skill": "통을 던져 " + mag("q_dmg", "q_ratio") + " 마법 피해를 입히고 괴수 " + A + "{q_n}" + E + "마리를 풀어놓는다. 괴수는 주변 적에게 "
                 "달려들어 " + A + "{m_n}" + E + "번 물며 한 번에 " + mag("m_dmg", "m_ratio") + " 마법 피해, 물던 적이 쓰러지면 다음 적에게 뛰어간다.",
        "skill2": "주변에서 공격력이 가장 높은 아군 챔피언(없으면 자신)에게 시머를 던진다: " + A + "{e_t}초" + E + " 동안 공격 속도 +" + A +
                  "{e_as}%" + E + ", 이동 속도 +" + A + "{e_ms}%" + E + ". 약효가 끝나면 현재 체력의 " + A + "{e_cost}%" + E + "를 잃는다.",
        "ult": "적 챔피언에게 거대한 통을 던져 " + mag("r_dmg", "r_ratio") + " 마법 피해, 괴수 " + A + "{r_n}" + E + "마리와 " + A +
               "{r_fog_t}초" + E + " 동안 시머 안개를 남긴다: 안의 적은 " + A + "{r_slow}%" + E + " " + R + "둔화" + E + ", 초당 " +
               mag("r_fog_dmg", "r_fog_ratio") + " 마법 피해.",
        "names": ("통에 담긴 괴수", "시머 주사", "화공 대범람"),
    },
    "ja": {
        "name": "シルコ",
        "attack": "シマーの薬瓶を投げ、" + AD + "の物理ダメージ。" + O + "ドミネーター" + E + "：出現するたびに" + mag("s_amt", "s_ap") +
                  "のシールド（" + A + "{s_t}秒" + E + "）。スキルを使うたびに魔力+" + A + "{d_ap}%" + E + "（最大" + A + "{d_max}" + E +
                  "回、倒れると消える）。",
        "skill": "缶を投げて" + mag("q_dmg", "q_ratio") + "の魔法ダメージ、怪物" + A + "{q_n}" + E + "体を放つ。怪物は近くの敵に飛びかかり" + A +
                 "{m_n}" + E + "回噛みつき、1回" + mag("m_dmg", "m_ratio") + "の魔法ダメージ。噛んだ敵が倒れると次の敵へ跳ぶ。",
        "skill2": "近くで攻撃力が最も高い味方チャンピオン（いなければ自分）にシマーを投げる：" + A + "{e_t}秒" + E + "間攻撃速度+" + A +
                  "{e_as}%" + E + "、移動速度+" + A + "{e_ms}%" + E + "。効き目が切れると現在体力の" + A + "{e_cost}%" + E + "を失う。",
        "ult": "敵チャンピオンに巨大な缶を投げ、" + mag("r_dmg", "r_ratio") + "の魔法ダメージ、怪物" + A + "{r_n}" + E + "体と" + A +
               "{r_fog_t}秒" + E + "のシマーの霧を残す：霧の中の敵は" + A + "{r_slow}%" + E + R + "スロウ" + E + "、毎秒" +
               mag("r_fog_dmg", "r_fog_ratio") + "の魔法ダメージ。",
        "names": ("缶詰めの怪物", "シマー注射", "化学の大洪水"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_silco's sfx / tsfx) and tft.dll's bite
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.35, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.45, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.45, 0.0)],
    f"{ID}_m_bite": [(CLIP + "m_bite", 0.25, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.4, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.6, 0.0)],
    f"{ID}_r_hit": [(CLIP + "r_hit", 0.55, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/silco.rs: a monstrosity's bite), not the kit's data
DLL_SOUNDS = {f"{ID}_m_bite"}


def values(p):
    v = {k: p[k] for k in ("s_amt", "s_ap", "d_ap", "d_max", "q_dmg", "q_ratio", "q_n", "m_n", "m_dmg", "m_ratio", "e_as",
                           "e_ms", "e_cost", "r_dmg", "r_ratio", "r_n", "r_slow", "r_fog_dmg", "r_fog_ratio")}
    for k in ("s_t", "e_t", "r_fog_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_silco.py")
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
    mi["last_updated"] = "2026-10-27"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
