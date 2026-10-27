"""Vander's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_vander.P.

    python tools/kit/setup_vander.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_loris.py writes for Loris: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_vander in every language, description + skill_name),
sound/sfx/tft_vander_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 13's own (CommunityDragon latest cdragon/tft/<locale>.json, TFT13_Prime, 2026-10-27): zh_CN 范德尔,
zh_TW 范德爾, ja ヴァンダー, ko 밴더, en Vander; Hound of the Underground = 地下猎犬 / 底城獵犬 / 地下都市の猟犬 / 지하의 사냥개;
his trait Watcher = 监察 / 守望者 / ウォッチャー / 주시자 names the passive, Family = 家人 / 家族 / ファミリー / 가족 the strike's
bonus. Iron Fist (铁拳突进) and Last Stand on the Bridge (桥头死守) are our own (TFT has one ability; the user's pick, plan A
「监察·地下猎犬」). The texts are the rules he plays with tft.dll (addons/tft/src/vander.rs): the Watcher by his health, the
strike's bonus per Family ally (Powder, Vi, Jinx), the stand's reduction per enemy champion round him.
Sounds: tools/lol/extract_vander.py's clips in tft/sound/sfx/tft_vander_sfx_*.wav (git-ignored) - his own set-13 TFT
sounds (the punch, its hits, the uppercut, the crit hit for the strike, the stance and its buff, the HERO blow, his
voice on the ult) and Vi's Cease and Desist jump and dunk for the leap and the slam. A clip name never equals an event
name (vo-clip-names rule): event tft_vander_<x> plays clip tft_vander_sfx_<x>. package_mod moves the clips to
sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_vander import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
VERSION = "0.9.0"      # Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8: the next free one
ADi, TOOLTIP_MAX = pack.ADi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from his soles' point, up negative): the face point between his eyes (the design's eye row 12
# of 80 at PPU 2.0: 34 over the ground; the stance leans his head 8 ahead of his standing column); the centre in his
# body; the ban/pick card by bp_card_audit.py's rule (checked there after the sheet is built)
VIEW = {"face": {"x": 8, "y": -34}, "center": {"x": 0, "y": -20}, "banpick_center": {"x": 0, "y": -6}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "范德尔",
        "attack": "挥拳造成" + AD + O + "物理伤害" + E + "。" + O + "监察" + E + "：受到的伤害降低" + A + "{p_lo}%" + E + "，生命高于" + A +
                  "{p_line}%" + E + "时降低" + A + "{p_hi}%" + E + "。",
        "skill": "摆出防御姿态，" + R + "嘲讽" + E + "周围的敌人" + R + "{q_taunt}秒" + E + "，获得" + A + "{q_def}" + E + "护甲和" + A +
                 "{q_mr}" + E + "魔抗（" + A + "{q_t}秒" + E + "）；下一拳造成" + phys("q_dmg", "q_ad") + "物理伤害，队里每有一个" + O +
                 "家人" + E + "再加" + ADi + O + "{q_fam}%" + E + "。",
        "skill2": "冲向敌人打出上勾拳，造成" + phys("e_dmg", "e_ad") + "物理伤害并" + R + "晕眩{e_stun}秒" + E + "，身边的敌人受到" + A +
                  "{e_splash}%" + E + "的伤害。",
        "ult": "跳进敌群砸地，周围的敌人受到" + phys("r_dmg", "r_ad") + "物理伤害并被" + R + "击飞{r_up}秒" + E + "；之后" + A + "{r_t}秒" + E +
               "内受到的伤害降低" + A + "{r_red}%" + E + "，身边每个敌方英雄再降低" + A + "{r_per}%" + E + "（最多" + A + "{r_cap}" + E + "个）。",
        "names": ("地下猎犬", "铁拳突进", "桥头死守"),
    },
    "zh-hant": {
        "name": "范德爾",
        "attack": "揮拳造成" + AD + O + "物理傷害" + E + "。" + O + "守望者" + E + "：受到的傷害降低" + A + "{p_lo}%" + E + "，生命高於" + A +
                  "{p_line}%" + E + "時降低" + A + "{p_hi}%" + E + "。",
        "skill": "擺出防禦姿態，" + R + "嘲諷" + E + "周圍的敵人" + R + "{q_taunt}秒" + E + "，獲得" + A + "{q_def}" + E + "護甲和" + A +
                 "{q_mr}" + E + "魔抗（" + A + "{q_t}秒" + E + "）；下一拳造成" + phys("q_dmg", "q_ad") + "物理傷害，隊裡每有一個" + O +
                 "家族" + E + "成員再加" + ADi + O + "{q_fam}%" + E + "。",
        "skill2": "衝向敵人打出上勾拳，造成" + phys("e_dmg", "e_ad") + "物理傷害並" + R + "暈眩{e_stun}秒" + E + "，身邊的敵人受到" + A +
                  "{e_splash}%" + E + "的傷害。",
        "ult": "跳進敵群砸地，周圍的敵人受到" + phys("r_dmg", "r_ad") + "物理傷害並被" + R + "擊飛{r_up}秒" + E + "；之後" + A + "{r_t}秒" + E +
               "內受到的傷害降低" + A + "{r_red}%" + E + "，身邊每個敵方英雄再降低" + A + "{r_per}%" + E + "（最多" + A + "{r_cap}" + E + "個）。",
        "names": ("底城獵犬", "鐵拳突進", "橋頭死守"),
    },
    "en": {
        "name": "Vander",
        "attack": "Punches for " + AD + " " + O + "physical damage" + E + ". " + O + "Watcher" + E + ": takes " + A + "{p_lo}%" + E +
                  " less damage, " + A + "{p_hi}%" + E + " while his health is above " + A + "{p_line}%" + E + ".",
        "skill": "Drops into a guard: nearby enemies are " + R + "taunted for {q_taunt}s" + E + ", he gains " + A + "{q_def}" + E +
                 " armour and " + A + "{q_mr}" + E + " magic resist (" + A + "{q_t}s" + E + "). His next punch deals " +
                 phys("q_dmg", "q_ad") + " physical damage, " + ADi + O + "{q_fam}%" + E + " more for each " + O + "Family" + E +
                 " ally on his team.",
        "skill2": "Rushes an enemy and uppercuts it for " + phys("e_dmg", "e_ad") + " physical damage, " + R + "stunning it for "
                  "{e_stun}s" + E + "; enemies next to him take " + A + "{e_splash}%" + E + " of the blow.",
        "ult": "Leaps into the enemies and slams the ground: nearby enemies take " + phys("r_dmg", "r_ad") + " physical damage and "
               "are " + R + "knocked up for {r_up}s" + E + ". For " + A + "{r_t}s" + E + " he takes " + A + "{r_red}%" + E + " less damage, " +
               A + "{r_per}%" + E + " more for each enemy champion near him (up to " + A + "{r_cap}" + E + ").",
        "names": ("Hound of the Underground", "Iron Fist", "Last Stand on the Bridge"),
    },
    "ko": {
        "name": "밴더",
        "attack": "주먹으로 " + AD + " 물리 피해. " + O + "주시자" + E + ": 받는 피해 " + A + "{p_lo}%" + E + " 감소, 체력이 " + A +
                  "{p_line}%" + E + " 이상이면 " + A + "{p_hi}%" + E + " 감소.",
        "skill": "방어 자세: 주변 적을 " + R + "{q_taunt}초 도발" + E + "하고 방어력 " + A + "{q_def}" + E + ", 마법 저항력 " + A + "{q_mr}" + E +
                 "(" + A + "{q_t}초" + E + "). 다음 주먹은 " + phys("q_dmg", "q_ad") + " 물리 피해, 팀의 " + O + "가족" + E + "마다 " + ADi +
                 O + "{q_fam}%" + E + " 추가.",
        "skill2": "적에게 돌진해 어퍼컷: " + phys("e_dmg", "e_ad") + " 물리 피해와 " + R + "{e_stun}초 기절" + E + ", 주변 적은 " + A +
                  "{e_splash}%" + E + "의 피해.",
        "ult": "적진으로 뛰어들어 땅을 내리친다: 주변 적에게 " + phys("r_dmg", "r_ad") + " 물리 피해와 " + R + "{r_up}초 에어본" + E + ". " +
               A + "{r_t}초" + E + " 동안 받는 피해 " + A + "{r_red}%" + E + " 감소, 주변 적 챔피언마다 " + A + "{r_per}%" + E + " 추가(최대 " +
               A + "{r_cap}" + E + "명).",
        "names": ("지하의 사냥개", "철권 돌진", "다리 위의 사수"),
    },
    "ja": {
        "name": "ヴァンダー",
        "attack": "拳で殴り、" + AD + "の物理ダメージ。" + O + "ウォッチャー" + E + "：被ダメージ" + A + "{p_lo}%" + E + "軽減、体力が" + A +
                  "{p_line}%" + E + "より多いと" + A + "{p_hi}%" + E + "軽減。",
        "skill": "防御の構え：周囲の敵を" + R + "{q_taunt}秒挑発" + E + "し、物理防御" + A + "{q_def}" + E + "と魔法防御" + A + "{q_mr}" + E +
                 "（" + A + "{q_t}秒" + E + "）。次の拳は" + phys("q_dmg", "q_ad") + "の物理ダメージ、味方の" + O + "ファミリー" + E +
                 "1人ごとに" + ADi + O + "{q_fam}%" + E + "追加。",
        "skill2": "敵に突進してアッパー：" + phys("e_dmg", "e_ad") + "の物理ダメージと" + R + "{e_stun}秒のスタン" + E + "、近くの敵には" + A +
                  "{e_splash}%" + E + "のダメージ。",
        "ult": "敵の中へ跳び込み地面を殴る：周囲の敵に" + phys("r_dmg", "r_ad") + "の物理ダメージと" + R + "{r_up}秒のノックアップ" + E +
               "。" + A + "{r_t}秒" + E + "間、被ダメージ" + A + "{r_red}%" + E + "軽減、近くの敵チャンピオン1体ごとに" + A + "{r_per}%" + E +
               "追加（最大" + A + "{r_cap}" + E + "体）。",
        "names": ("地下都市の猟犬", "鉄拳突進", "橋の上の死守"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_vander's sfx / tsfx)
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.4, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.45, 0.0)],
    f"{ID}_q_buff": [(CLIP + "q_buff", 0.4, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.5, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_e_hit": [(CLIP + "e_hit", 0.45, 0.0), (CLIP + "a2_hit", 0.4, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.6, 0.0)],
    f"{ID}_r_jump": [(CLIP + "r_jump", 0.45, 0.0)],
    f"{ID}_r_slam": [(CLIP + "r_slam", 0.6, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/vander.rs plays none)
DLL_SOUNDS = set()


def values(p):
    v = {k: p[k] for k in ("p_lo", "p_hi", "p_line", "q_def", "q_mr", "q_dmg", "q_ad", "q_fam", "e_dmg", "e_ad",
                           "e_splash", "r_dmg", "r_ad", "r_red", "r_per", "r_cap")}
    for k in ("q_taunt", "q_t", "e_stun", "r_up", "r_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_vander.py")
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
