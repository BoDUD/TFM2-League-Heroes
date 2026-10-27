"""Violet's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_violet.P.

    python tools/kit/setup_violet.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_vander.py writes for Vander: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_violet in every language, description + skill_name),
sound/sfx/tft_violet_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 13's own (CommunityDragon latest cdragon/tft/<locale>.json, TFT13_Red, 2026-10-28): zh_CN 蔚奥莱,
zh_TW 菲爾蕾特, ja ヴァイオレット, ko 바이올렛, en Violet; 1-2-3 Combo = 1-2-3连招 / 連擊組合技 / 1-2-3 コンボ / 3단 연계기; her
trait Pit Fighter = 搏击手 / 競技鬥士 / ピットファイター / 투사 names the passive, Family = 家人 / 家族 / ファミリー / 가족 the fury's
bonus. Gauntlet Rush (冲拳) and Undercity Fist (底城怒拳) are our own (TFT has one ability; the user's pick, plan A
「搏击手·1-2-3连招」). The texts are the rules she plays with tft.dll (addons/tft/src/violet.rs): the second wind at half
health once a life, the fury's attack speed per Family ally (Powder, Vander, Jinx).
Sounds: tools/lol/extract_violet.py's clips in tft/sound/sfx/tft_violet_sfx_*.wav (git-ignored) - her own set-13 TFT
sounds (the punch, its hits, the second punch for the jabs, the combo's small and large hits, the crit hit for the
rush, her voice on the ult) and her grown-up self Vi's: Vault Breaker's launch for the rush, Cease and Desist's jump,
Relentless Force's blast for the slam, Denting Blows' proc for the fury, Blast Shield for the second wind (tft.dll plays
that one). A clip name never equals an event name (vo-clip-names rule): event tft_violet_<x> plays clip
tft_violet_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_violet import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
VERSION = "0.10.0"     # Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9
ADi, TOOLTIP_MAX = pack.ADi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from her soles' point, up negative): the face point between her eyes (the design's eye row 17
# of 76 at PPU 2.0: 30 over the ground; 4 ahead of her standing column); the centre in her body; the ban/pick card by
# bp_card_audit.py's rule (checked there after the sheet is built)
VIEW = {"face": {"x": 4, "y": -30}, "center": {"x": 0, "y": -19}, "banpick_center": {"x": 0, "y": -6}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def ratio(r):
    return f"{ADi}{O}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "蔚奥莱",
        "attack": "挥拳造成" + AD + O + "物理伤害" + E + "。" + O + "搏击手" + E + "：每次命中额外造成" + ratio("p_true") + "真实伤害，" +
                  "全能吸血" + A + "{p_vamp}%" + E + "；每条命第一次生命低于" + A + "{p_line}%" + E + "时，" + A + "{p_t}秒" + E + "内回复" +
                  A + "{p_heal}%" + E + "最大生命。",
        "skill": "两记刺拳各造成" + ratio("q_jab") + O + "物理伤害" + E + "，再一记上勾拳造成" + phys("q_dmg", "q_ad") + "物理伤害并" + R +
                 "击飞{q_air}秒" + E + "。",
        "skill2": "冲向敌人一拳打退，造成" + phys("e_dmg", "e_ad") + "物理伤害。",
        "ult": "跳进敌群双拳砸地，周围的敌人受到" + phys("r_dmg", "r_ad") + "物理伤害并被" + R + "击飞{r_up}秒" + E + "；之后" + A +
               "{r_t}秒" + E + "内攻速+" + A + "{r_as}%" + E + "、吸血+" + A + "{r_vamp}%" + E + "，队里每有一个" + O + "家人" + E + "攻速再+" +
               A + "{r_fam}%" + E + "。",
        "names": ("1-2-3连招", "冲拳", "底城怒拳"),
    },
    "zh-hant": {
        "name": "菲爾蕾特",
        "attack": "揮拳造成" + AD + O + "物理傷害" + E + "。" + O + "競技鬥士" + E + "：每次命中額外造成" + ratio("p_true") + "真實傷害，" +
                  "全能吸血" + A + "{p_vamp}%" + E + "；每條命第一次生命低於" + A + "{p_line}%" + E + "時，" + A + "{p_t}秒" + E + "內回復" +
                  A + "{p_heal}%" + E + "最大生命。",
        "skill": "兩記刺拳各造成" + ratio("q_jab") + O + "物理傷害" + E + "，再一記上勾拳造成" + phys("q_dmg", "q_ad") + "物理傷害並" + R +
                 "擊飛{q_air}秒" + E + "。",
        "skill2": "衝向敵人一拳打退，造成" + phys("e_dmg", "e_ad") + "物理傷害。",
        "ult": "跳進敵群雙拳砸地，周圍的敵人受到" + phys("r_dmg", "r_ad") + "物理傷害並被" + R + "擊飛{r_up}秒" + E + "；之後" + A +
               "{r_t}秒" + E + "內攻速+" + A + "{r_as}%" + E + "、吸血+" + A + "{r_vamp}%" + E + "，隊裡每有一個" + O + "家族" + E + "成員攻速再+" +
               A + "{r_fam}%" + E + "。",
        "names": ("連擊組合技", "衝拳", "底城怒拳"),
    },
    "en": {
        "name": "Violet",
        "attack": "Punches for " + AD + " " + O + "physical damage" + E + ". " + O + "Pit Fighter" + E + ": every hit deals " +
                  ratio("p_true") + " more as true damage, " + A + "{p_vamp}%" + E + " omnivamp; the first time a life drops under " +
                  A + "{p_line}%" + E + " health she heals " + A + "{p_heal}%" + E + " of her max health over " + A + "{p_t}s" + E + ".",
        "skill": "Two jabs of " + ratio("q_jab") + " " + O + "physical damage" + E + ", then an uppercut for " + phys("q_dmg", "q_ad") +
                 " physical damage that " + R + "knocks the target up for {q_air}s" + E + ".",
        "skill2": "Rushes an enemy and punches it back for " + phys("e_dmg", "e_ad") + " physical damage.",
        "ult": "Leaps into the enemies and smashes the ground: nearby enemies take " + phys("r_dmg", "r_ad") + " physical damage and "
               "are " + R + "knocked up for {r_up}s" + E + ". For " + A + "{r_t}s" + E + " she gains " + A + "{r_as}%" + E + " attack speed and " +
               A + "{r_vamp}%" + E + " omnivamp, " + A + "{r_fam}%" + E + " more attack speed for each " + O + "Family" + E + " ally.",
        "names": ("1-2-3 Combo", "Gauntlet Rush", "Undercity Fist"),
    },
    "ko": {
        "name": "바이올렛",
        "attack": "주먹으로 " + AD + " 물리 피해. " + O + "투사" + E + ": 적중마다 " + ratio("p_true") + " 고정 피해 추가, 모든 피해 흡혈 " +
                  A + "{p_vamp}%" + E + "; 목숨마다 처음 체력이 " + A + "{p_line}%" + E + " 아래로 떨어지면 " + A + "{p_t}초" + E +
                  " 동안 최대 체력의 " + A + "{p_heal}%" + E + " 회복.",
        "skill": "잽 두 번에 각각 " + ratio("q_jab") + " " + O + "물리 피해" + E + ", 이어서 어퍼컷으로 " + phys("q_dmg", "q_ad") +
                 " 물리 피해와 " + R + "{q_air}초 에어본" + E + ".",
        "skill2": "적에게 돌진해 주먹으로 밀쳐내며 " + phys("e_dmg", "e_ad") + " 물리 피해.",
        "ult": "적진으로 뛰어들어 두 주먹으로 땅을 내리친다: 주변 적에게 " + phys("r_dmg", "r_ad") + " 물리 피해와 " + R +
               "{r_up}초 에어본" + E + ". " + A + "{r_t}초" + E + " 동안 공격 속도 +" + A + "{r_as}%" + E + ", 흡혈 +" + A + "{r_vamp}%" + E +
               ", 팀의 " + O + "가족" + E + "마다 공격 속도 +" + A + "{r_fam}%" + E + ".",
        "names": ("3단 연계기", "건틀릿 돌진", "지하도시의 주먹"),
    },
    "ja": {
        "name": "ヴァイオレット",
        "attack": "拳で殴り、" + AD + "の物理ダメージ。" + O + "ピットファイター" + E + "：命中ごとに" + ratio("p_true") + "の確定ダメージ追加、" +
                  "オムニヴァンプ" + A + "{p_vamp}%" + E + "。1回の命につき最初に体力が" + A + "{p_line}%" + E + "を下回ると、" + A +
                  "{p_t}秒" + E + "で最大体力の" + A + "{p_heal}%" + E + "回復。",
        "skill": "ジャブ2発でそれぞれ" + ratio("q_jab") + "の" + O + "物理ダメージ" + E + "、続くアッパーで" + phys("q_dmg", "q_ad") +
                 "の物理ダメージと" + R + "{q_air}秒のノックアップ" + E + "。",
        "skill2": "敵に突進して殴り飛ばし、" + phys("e_dmg", "e_ad") + "の物理ダメージ。",
        "ult": "敵の中へ跳び込み両拳で地面を殴る：周囲の敵に" + phys("r_dmg", "r_ad") + "の物理ダメージと" + R + "{r_up}秒のノックアップ" + E +
               "。" + A + "{r_t}秒" + E + "間、攻撃速度+" + A + "{r_as}%" + E + "、吸血+" + A + "{r_vamp}%" + E + "、味方の" + O + "ファミリー" + E +
               "1人ごとに攻撃速度+" + A + "{r_fam}%" + E + "。",
        "names": ("1-2-3 コンボ", "ガントレットラッシュ", "地下街の怒拳"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_violet's sfx / tsfx) and tft.dll's p
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.4, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.4, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.45, 0.0), (CLIP + "a2_hit", 0.35, 0.0)],
    f"{ID}_q_up": [(CLIP + "q_up", 0.55, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_e_hit": [(CLIP + "e_hit", 0.5, 0.0)],
    f"{ID}_p": [(CLIP + "p", 0.45, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.6, 0.0)],
    f"{ID}_r_jump": [(CLIP + "r_jump", 0.45, 0.0)],
    f"{ID}_r_slam": [(CLIP + "r_slam", 0.6, 0.0)],
    f"{ID}_r_buff": [(CLIP + "r_buff", 0.4, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/violet.rs: the second wind)
DLL_SOUNDS = {f"{ID}_p"}


def values(p):
    v = {k: p[k] for k in ("p_true", "p_vamp", "p_line", "p_heal", "q_jab", "q_dmg", "q_ad", "e_dmg", "e_ad", "r_dmg",
                           "r_ad", "r_as", "r_vamp", "r_fam")}
    for k in ("p_t", "q_air", "r_up", "r_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_violet.py")
            clips.add(c)
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    ov.setdefault("asset/base/text/champion", {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"})
    ov.setdefault("asset/base/style/champion_view",
                  {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"})
    for k in [k for k in ov if k.startswith(f"asset/base/sound/sfx/{ID}_")]:   # her sound keys rebuilt
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
    mi["contains_code"], mi["mod_type"] = True, "native"     # tft.dll (addons/tft): her rules the data cannot play
    mi["last_updated"] = "2026-10-28"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
