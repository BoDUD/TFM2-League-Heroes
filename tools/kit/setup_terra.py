"""Terra's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_terra.P.

    python tools/kit/setup_terra.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_sohm.py writes for Sohm: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_terra in every language, description + skill_name), sound/sfx/tft_terra_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX
and the texts themselves.
Names: TFT set 7.5's own (CommunityDragon cdragon/tft/<locale>.json, TFT7_DragonEarth, 2026-10-31): zh_CN 泰拉, zh_TW 泰拉,
ja テラ, ko 테라, en Terra; her ability Earthquake = 地震 (zh_TW 地動山搖, ja 地震, ko 지진), the Monolith trait 巨岩龙 (the
passive 巨岩之躯). Rock Claw (岩爪), Rending Bite (裂地咬) and Dragon's Roar (龙威咆哮) are our own (the user's pick, plan A
「地震巨岩」).
The texts are the rules she plays with tft.dll (addons/tft/src/terra.rs): the hide on every life, the armour + magic
resistance part of the bite and of each stomp.
Sounds: tools/lol/extract_terra.py's clips in tft/sound/sfx/tft_terra_sfx_*.wav (git-ignored) - her own set-7 TFT sounds
(the claw, the crit for the bite, the quake's cast, three stomps, its hit, the shield and the armour, two roars), Malphite,
Skarner and Rammus for the hits and the taunt, the Rift's drakes (the death). A clip name never equals an event name
(vo-clip-names rule): event tft_terra_<x> plays clip tft_terra_sfx_<x>.
package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_terra import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25
VERSION = "0.25.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
ARi = "<i#asset/base/ui/banpick/champion_stat_icon:armor_0>"
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from her feet's point, up negative): the face point on her eye (the design's eye at column 74.5,
# row 28.5 of 52 at PPU 1.45: 16 over the ground, 17 ahead of her standing point, the root column 50 - ppu_restyle's
# face_to); the centre in her body (its middle column 43, half her 36 px); the ban/pick card by bp_card_audit.py's rule
# (-39 less the idle's top -24.5, as Nomsy's: her wing bones 1 game px under the card's top)
VIEW = {"face": {"x": 17, "y": -16}, "center": {"x": -5, "y": -18}, "banpick_center": {"x": 0, "y": -14}}


def phys(d, r, df):
    """base + AD ratio + armour-and-resistance ratio."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E} + {ARi}{O}{{{df}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "泰拉",
        "attack": "岩爪一拍，造成" + AD + O + "物理伤害" + E + "。" + O + "巨岩之躯" + E + "：受到的伤害永久减少" + A + "{p_red}%" + E + "。",
        "skill": "低头扑咬目标，造成" + phys("q_dmg", "q_ad", "q_def") + O + "物理伤害" + E + "（" + ARi + "=护甲+魔抗），减速" + R +
                 "{q_slow}%" + E + "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "仰天咆哮，" + R + "嘲讽" + E + "周围敌人" + A + "{e_taunt}秒" + E + "，自己获得" + O + "{e_sh}" + E + " + " + ADi + O +
                  "{e_sh_ad}%" + E + "的岩石护盾（" + A + "{e_sh_t}秒" + E + "）。",
        "ult": "重踏三次（施放中" + R + "免疫控制" + E + "），每踏对周围敌人造成" + phys("r_dmg", "r_ad", "r_def") + O + "物理伤害" + E +
               "；之后护甲和魔抗" + A + "+{r_res}" + E + "（" + A + "{r_res_t}秒" + E + "）。",
        "names": ("裂地咬", "龙威咆哮", "地震"),
    },
    "zh-hant": {
        "name": "泰拉",
        "attack": "岩爪一拍，造成" + AD + O + "物理傷害" + E + "。" + O + "巨岩之軀" + E + "：受到的傷害永久減少" + A + "{p_red}%" + E + "。",
        "skill": "低頭撲咬目標，造成" + phys("q_dmg", "q_ad", "q_def") + O + "物理傷害" + E + "（" + ARi + "=護甲+魔抗），緩速" + R +
                 "{q_slow}%" + E + "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "仰天咆哮，" + R + "嘲諷" + E + "周圍敵人" + A + "{e_taunt}秒" + E + "，自己獲得" + O + "{e_sh}" + E + " + " + ADi + O +
                  "{e_sh_ad}%" + E + "的岩石護盾（" + A + "{e_sh_t}秒" + E + "）。",
        "ult": "重踏三次（施放中" + R + "免疫控制" + E + "），每踏對周圍敵人造成" + phys("r_dmg", "r_ad", "r_def") + O + "物理傷害" + E +
               "；之後護甲和魔抗" + A + "+{r_res}" + E + "（" + A + "{r_res_t}秒" + E + "）。",
        "names": ("裂地咬", "龍威咆哮", "地動山搖"),
    },
    "en": {
        "name": "Terra",
        "attack": "A rock claw swipe for " + AD + " " + O + "physical damage" + E + ". " + O + "Monolith Hide" + E +
                  ": she always takes " + A + "{p_red}%" + E + " less damage.",
        "skill": "Lunges low and bites the target for " + phys("q_dmg", "q_ad", "q_def") + " " + O + "physical damage" + E + " (" +
                 ARi + " = armor + magic resist), slowing it " + R + "{q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": "Roars, " + R + "taunting" + E + " nearby enemies for " + A + "{e_taunt}s" + E + ", and gains a " + O + "{e_sh}" + E +
                  " + " + ADi + O + "{e_sh_ad}%" + E + " rock shield for " + A + "{e_sh_t}s" + E + ".",
        "ult": "Stomps three times (" + R + "unstoppable" + E + " while casting), each dealing " + phys("r_dmg", "r_ad", "r_def") + " " +
               O + "physical damage" + E + " around her; then " + A + "+{r_res}" + E + " armor and magic resist for " + A +
               "{r_res_t}s" + E + ".",
        "names": ("Rending Bite", "Dragon's Roar", "Earthquake"),
    },
    "ko": {
        "name": "테라",
        "attack": "바위 발톱으로 내리쳐 " + AD + " " + O + "물리 피해" + E + ". " + O + "거석의 몸" + E + ": 받는 피해가 항상 " + A + "{p_red}%" +
                  E + " 감소.",
        "skill": "낮게 덮쳐 대상을 물어 " + phys("q_dmg", "q_ad", "q_def") + " " + O + "물리 피해" + E + "(" + ARi + " = 방어력+마법 저항력), " +
                 A + "{q_slow_t}초" + E + " 동안 " + R + "{q_slow}%" + E + " 둔화.",
        "skill2": "포효해 주변 적을 " + A + "{e_taunt}초" + E + " 동안 " + R + "도발" + E + "하고, " + O + "{e_sh}" + E + " + " + ADi + O +
                  "{e_sh_ad}%" + E + "의 바위 보호막(" + A + "{e_sh_t}초" + E + ")을 얻습니다.",
        "ult": "땅을 세 번 구릅니다(시전 중 " + R + "저지 불가" + E + "). 매번 주변 적에게 " + phys("r_dmg", "r_ad", "r_def") + " " + O +
               "물리 피해" + E + ", 이후 " + A + "{r_res_t}초" + E + " 동안 방어력과 마법 저항력 " + A + "+{r_res}" + E + ".",
        "names": ("대지 물어뜯기", "용의 포효", "지진"),
    },
    "ja": {
        "name": "テラ",
        "attack": "岩の爪で叩き" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "巨岩の体" + E + "：受けるダメージが常に" + A + "{p_red}%" +
                  E + "減少。",
        "skill": "低く飛びかかって噛みつき" + phys("q_dmg", "q_ad", "q_def") + "の" + O + "物理ダメージ" + E + "（" + ARi + "＝物理防御＋魔法防御）、" +
                 A + "{q_slow_t}秒" + E + "間" + R + "{q_slow}%" + E + "スロウ。",
        "skill2": "咆哮して周囲の敵を" + A + "{e_taunt}秒" + E + "間" + R + "挑発" + E + "し、" + O + "{e_sh}" + E + " + " + ADi + O +
                  "{e_sh_ad}%" + E + "の岩のシールド（" + A + "{e_sh_t}秒" + E + "）を得る。",
        "ult": "3回踏み鳴らし（詠唱中" + R + "阻止不可" + E + "）、そのたびに周囲の敵へ" + phys("r_dmg", "r_ad", "r_def") + "の" + O +
               "物理ダメージ" + E + "。その後" + A + "{r_res_t}秒" + E + "間物理防御と魔法防御" + A + "+{r_res}" + E + "。",
        "names": ("大地の噛みつき", "竜の咆哮", "地震"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_terra's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.35),
    ("q", 0.5), ("q_hit", 0.45),
    ("e", 0.55), ("e_taunt", 0.4), ("e_shield", 0.45),
    ("r", 0.5), ("r_vo", 0.5), ("r_stomp1", 0.55), ("r_stomp2", 0.55), ("r_stomp3", 0.6), ("r_hit", 0.35),
    ("r_armor", 0.45),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/terra.rs: her death cry)
DLL_SOUNDS = {f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("p_red", "q_dmg", "q_ad", "q_def", "q_slow", "e_sh", "e_sh_ad", "r_dmg", "r_ad", "r_def",
                           "r_res")}
    for k in ("q_slow_t", "e_taunt", "e_sh_t", "r_res_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_terra.py")
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
    mi["contains_code"], mi["mod_type"] = True, "native"     # tft.dll (addons/tft): the rules the data cannot play
    mi["last_updated"] = "2026-10-31"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
