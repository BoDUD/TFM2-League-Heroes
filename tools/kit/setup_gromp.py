"""Gromp's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_gromp.P.

    python tools/kit/setup_gromp.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_murkwolf.py writes for the Murk Wolf:
mod.mod_info (VERSION, the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type
native for tft.dll, the keys sorted), text/champion.i18n (tft_gromp in every language, description + skill_name),
sound/sfx/tft_gromp_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 18's own (CommunityDragon cdragon/tft/<locale>.json, DA_Gromp18_AP, 2026-11-01): zh_CN 魔沼蛙, zh_TW 啾吉,
ja グロンプ, ko 심술두꺼비, en Gromp; its ability Belchy Bubble = 打嗝泡泡 (zh_TW 飽嗝泡泡, ja ベルチーバブル, ko 꿀꺽 방울), Purple
Buff = 紫霸符 (zh_TW 紫色增益, ja パープルバフ, ko 퍼플 버프) from the same text. Toxic Spit (毒涎吐射), Slime Swamp (黏液沼泽) and
Swamp Belch (毒沼大嗝) are our own (the user's pick, plan A 「打嗝泡泡」).
The texts are the rules it plays: Purple Buff's timed, capped stacks in tft.dll (addons/tft/src/gromp.rs), the rest
the data (the bubble bursting only where it struck, the swamp and the fog lying on the ground, the growth).
Sounds: tools/lol/extract_gromp.py's clips in tft/sound/sfx/tft_gromp_sfx_*.wav (git-ignored) - the Rift's own Gromp
(its spit, splash, croaks, belly thump and death), Kog'Maw, Twitch, Cassiopeia and Singed for the rest. A clip name
never equals an event name (vo-clip-names rule): event tft_gromp_<x> plays clip tft_gromp_sfx_<x>. package_mod moves
the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_gromp import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29, the Elder Dragon 0.30, Meepsie 0.31, Murk Wolf 0.32, the Scuttle Crab 0.33 (PR #652), Gromp 0.34
VERSION = "0.34.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point on its near eye (the design's eye at
# column 57, row 12 of 54 at PPU 1.69: 25 over the ground, 6 ahead of its standing point, the design's pivot column 47 -
# ppu_restyle's face_to); the centre in its belly (3 ahead of its standing point, the middle of its 32 px); the ban/pick
# card a little lower than the Murk Wolf's (32 px from its highest point to its feet; its belly kept inside the card by
# its UI size 0.82 in league.dll's hd.rs)
VIEW = {"face": {"x": 6, "y": -25}, "center": {"x": 3, "y": -14}, "banpick_center": {"x": 0, "y": -12}}


def mag(d, r):
    """base + AP ratio, magic."""
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "魔沼蛙",
        "attack": "吐出毒口水，造成" + AD + O + "物理伤害" + E + "和" + APi + M + "{a_ap}%" + E + M + "魔法伤害" + E + "。" + O + "紫霸符" + E +
                  "：战斗中每" + A + "{p_every}秒" + E + "法术加成" + A + "+{p_ap}" + E + "，最多" + A + "{p_max}层" + E + "。",
        "skill": "打出一个毒泡泡，碰到第一个敌人造成" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "并炸开，周围敌人" + A + "{q_t}秒" + E +
                 "内受到" + mag("q_dot", "q_dratio") + M + "魔法伤害" + E + "。",
        "skill2": "往敌人脚下吐一滩黏液，持续" + A + "{e_t}秒" + E + "，站在里面的敌人减速" + A + "{e_slow}%" + E + "，每秒受到" +
                  mag("e_dps", "e_dpsr") + M + "魔法伤害" + E + "。",
        "ult": "肚子鼓起变大" + A + "{r_grow}秒" + E + "（受到伤害" + A + "-{r_dr}%" + E + "），向前打出大嗝，造成" + mag("r_dmg", "r_ratio") + M +
               "魔法伤害" + E + "并减速" + A + "{r_slow}%" + E + "，毒雾留在地上" + A + "{r_t}秒" + E + "，每秒" + mag("r_dps", "r_dpsr") + M + "魔法伤害" + E + "。",
        "names": ("打嗝泡泡", "黏液沼泽", "毒沼大嗝"),
    },
    "zh-hant": {
        "name": "啾吉",
        "attack": "吐出毒口水，造成" + AD + O + "物理傷害" + E + "和" + APi + M + "{a_ap}%" + E + M + "魔法傷害" + E + "。" + O + "紫色增益" + E +
                  "：戰鬥中每" + A + "{p_every}秒" + E + "魔攻" + A + "+{p_ap}" + E + "，最多" + A + "{p_max}層" + E + "。",
        "skill": "吐出飽嗝泡泡，碰到第一個敵軍造成" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "並炸開，周圍敵軍" + A + "{q_t}秒" + E +
                 "內受到" + mag("q_dot", "q_dratio") + M + "魔法傷害" + E + "。",
        "skill2": "往敵軍腳下吐一灘黏液，持續" + A + "{e_t}秒" + E + "，站在裡面的敵軍緩速" + A + "{e_slow}%" + E + "，每秒受到" +
                  mag("e_dps", "e_dpsr") + M + "魔法傷害" + E + "。",
        "ult": "肚子鼓起變大" + A + "{r_grow}秒" + E + "（受到傷害" + A + "-{r_dr}%" + E + "），向前打出大嗝，造成" + mag("r_dmg", "r_ratio") + M +
               "魔法傷害" + E + "並緩速" + A + "{r_slow}%" + E + "，毒霧留在地上" + A + "{r_t}秒" + E + "，每秒" + mag("r_dps", "r_dpsr") + M + "魔法傷害" + E + "。",
        "names": ("飽嗝泡泡", "黏液沼澤", "毒沼大嗝"),
    },
    "en": {
        "name": "Gromp",
        "attack": "Spits for " + AD + " " + O + "physical damage" + E + " and " + APi + M + "{a_ap}%" + E + " " + M + "magic damage" + E +
                  ". " + O + "Purple Buff" + E + ": in a fight it gains " + A + "+{p_ap}" + E + " Ability Power every " + A + "{p_every}s" + E +
                  ", up to " + A + "{p_max}" + E + " stacks.",
        "skill": "Belches a bubble that bursts on the first enemy hit for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E +
                 "; enemies around it take " + mag("q_dot", "q_dratio") + " " + M + "magic damage" + E + " over " + A + "{q_t}s" + E + ".",
        "skill2": "Spits a pool of slime under an enemy for " + A + "{e_t}s" + E + ": enemies in it are slowed by " + A + "{e_slow}%" + E +
                  " and take " + mag("e_dps", "e_dpsr") + " " + M + "magic damage" + E + " per second.",
        "ult": "Swells up for " + A + "{r_grow}s" + E + " (" + A + "{r_dr}%" + E + " less damage taken) and belches a cone of poison for " +
               mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + ", slowing by " + A + "{r_slow}%" + E + "; the fog lingers " + A +
               "{r_t}s" + E + ", dealing " + mag("r_dps", "r_dpsr") + " " + M + "magic damage" + E + " per second.",
        "names": ("Belchy Bubble", "Slime Swamp", "Swamp Belch"),
    },
    "ko": {
        "name": "심술두꺼비",
        "attack": "독침을 뱉어 " + AD + " " + O + "물리 피해" + E + "와 " + APi + M + "{a_ap}%" + E + " " + M + "마법 피해" + E + ". " + O +
                  "퍼플 버프" + E + ": 전투 중 " + A + "{p_every}초" + E + "마다 주문력 " + A + "+{p_ap}" + E + ", 최대 " + A + "{p_max}중첩" + E + ".",
        "skill": "독 방울을 뱉어 처음 맞은 적에게 " + mag("q_dmg", "q_ratio") + " " + M + "마법 피해" + E + "를 주고 터지며, 주변 적은 " + A +
                 "{q_t}초" + E + " 동안 " + mag("q_dot", "q_dratio") + " " + M + "마법 피해" + E + ".",
        "skill2": "적의 발밑에 점액을 뱉어 " + A + "{e_t}초" + E + " 동안 남깁니다. 안의 적은 " + A + "{e_slow}%" + E + " 둔화되고 초당 " +
                  mag("e_dps", "e_dpsr") + " " + M + "마법 피해" + E + ".",
        "ult": A + "{r_grow}초" + E + " 동안 몸이 부풀어(받는 피해 " + A + "-{r_dr}%" + E + ") 앞으로 독 트림을 뿜어 " + mag("r_dmg", "r_ratio") +
               " " + M + "마법 피해" + E + "와 " + A + "{r_slow}%" + E + " 둔화. 독안개가 " + A + "{r_t}초" + E + " 동안 남아 초당 " +
               mag("r_dps", "r_dpsr") + " " + M + "마법 피해" + E + ".",
        "names": ("꿀꺽 방울", "점액 늪", "독늪 트림"),
    },
    "ja": {
        "name": "グロンプ",
        "attack": "毒液を吐き" + AD + "の" + O + "物理ダメージ" + E + "と" + APi + M + "{a_ap}%" + E + "の" + M + "魔法ダメージ" + E + "。" + O +
                  "パープルバフ" + E + "：戦闘中" + A + "{p_every}秒" + E + "ごとに魔力" + A + "+{p_ap}" + E + "、最大" + A + "{p_max}スタック" + E + "。",
        "skill": "毒の泡を吐き、最初に当たった敵に" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "を与えて弾け、周囲の敵に" + A +
                 "{q_t}秒" + E + "かけて" + mag("q_dot", "q_dratio") + "の" + M + "魔法ダメージ" + E + "。",
        "skill2": "敵の足元に粘液を吐き" + A + "{e_t}秒" + E + "残す。中の敵は" + A + "{e_slow}%" + E + "スロウ、毎秒" + mag("e_dps", "e_dpsr") +
                  "の" + M + "魔法ダメージ" + E + "。",
        "ult": A + "{r_grow}秒" + E + "間膨らみ（被ダメージ" + A + "-{r_dr}%" + E + "）、前方に毒のげっぷを放ち" + mag("r_dmg", "r_ratio") + "の" + M +
               "魔法ダメージ" + E + "と" + A + "{r_slow}%" + E + "スロウ。毒霧が" + A + "{r_t}秒" + E + "残り、毎秒" + mag("r_dps", "r_dpsr") + "の" + M +
               "魔法ダメージ" + E + "。",
        "names": ("ベルチーバブル", "粘液の沼", "毒沼のげっぷ"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_gromp's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.35), ("a_hit", 0.3),
    ("p", 0.3),
    ("q", 0.5), ("q_vo", 0.45), ("q_hit", 0.45),
    ("e", 0.45), ("e_vo", 0.45), ("e_hit", 0.4), ("e_slow", 0.3),
    ("r", 0.55), ("r_vo", 0.5), ("r_cloud", 0.45), ("r_tick", 0.25),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/gromp.rs: Purple Buff filling up, its death croak)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("a_ap", "p_ap", "p_max", "q_dmg", "q_ratio", "q_dot", "q_dratio", "e_slow", "r_dr", "r_dmg",
                           "r_ratio", "r_slow")}
    for k in ("p_every", "q_t", "e_t", "r_grow", "r_t"):
        v[k] = secs(p[k])
    # the swamp and the fog strike every e_p / r_p ticks: per second
    v["e_dps"], v["e_dpsr"] = round(p["e_dmg"] * 60 / p["e_p"]), round(p["e_ratio"] * 60 / p["e_p"])
    v["r_dps"], v["r_dpsr"] = round(p["r_fdmg"] * 60 / p["r_p"]), round(p["r_fratio"] * 60 / p["r_p"])
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
        lens = {k: shown_length(d[k]) for k in ("attack", "skill", "skill2", "ult")}
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_gromp.py")
            clips.add(c)
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    ov.setdefault("asset/base/text/champion", {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"})
    ov.setdefault("asset/base/style/champion_view",
                  {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"})
    for k in [k for k in ov if k.startswith(f"asset/base/sound/sfx/{ID}_")]:   # its sound keys rebuilt
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
    mi["last_updated"] = "2026-11-01"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
