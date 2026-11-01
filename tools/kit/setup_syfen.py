"""Sy'fen's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_syfen.P.

    python tools/kit/setup_syfen.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_daeja.py writes for Daeja: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_syfen in every language, description + skill_name), sound/sfx/tft_syfen_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX
and the texts themselves.
Names: TFT set 7's own (CommunityDragon cdragon/tft/<locale>.json, TFT7_DragonPurple, 2026-10-30): zh_CN 赛芬, zh_TW 賽焚,
ja サイ・フェン, ko 사이펜, en Sy'fen; his ability Rampage = 暴走 / 盛怒龍顎 / 龍の猛攻 / 광분, the Whispers trait 幽影龙 (the
passive 幽影低语). Bite (噬咬) and Wing Sweep (翼刃横扫) are our own (the user's pick, plan A 「暴走猎杀」).
The texts are the rules he plays with tft.dll (addons/tft/src/syfen.rs): the shrink and the fury, Rampage at the farthest
enemy.
Sounds: tools/lol/extract_syfen.py's clips in tft/sound/sfx/tft_syfen_sfx_*.wav (git-ignored) - his own set-7 TFT sounds
(the attack, the crit for Bite's lunge, the spell attack for Rampage's start and bite), Lulu (the shrink), Cho'Gath (the
chomp), Sejuani (the wing sweep, the ram), Hecarim (the charge) and the Rift's drakes (the roar, the death). A clip name
never equals an event name (vo-clip-names rule): event tft_syfen_<x> plays clip tft_syfen_sfx_<x>.
package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_syfen import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23
VERSION = "0.23.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from his feet's point, up negative): the face point on his eye (the design's eye at column 114.5,
# row 31.5 of 101 at PPU 2.52: 28 over the ground, 23 ahead of his standing column 56 - ppu_restyle's face_to); the centre
# in his chest; the ban/pick card by bp_card_audit.py's rule (-39 less the idle's top -29: the horn tips at the card's top)
# center: the encyclopedia card puts this point at a fixed spot - set by League's rule (tools/art/bp_card_audit.py --centers, 2026-11-01)
VIEW = {"face": {"x": 23, "y": -28}, "center": {"x": 6, "y": -11}, "banpick_center": {"x": 3, "y": -10}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "赛芬",
        "attack": "翼爪和甩尾交替攻击，造成" + AD + O + "物理伤害" + E + "。" + O + "幽影低语" + E + "：他的伤害让敌人缩小" + A + "{p_t}秒" +
                  E + "（护甲、魔抗" + A + "-{p_shred}%" + E + "）；打缩小的敌人叠怒气，每层" + A + "+{p_ad}" + E + "攻击力，最多" + A +
                  "{p_max}" + E + "层。",
        "skill": "扑上去咬住目标，造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "，无视" + A + "{q_pen}%" + E + "护甲，回复" +
                 phys("q_heal", "q_heal_ad") + "生命。",
        "skill2": "张开双翼横扫身边，造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并减速" + A + "{e_slow}%" + E + "（" + A +
                  "{e_slow_t}秒" + E + "）。",
        "ult": "龙吼后冲向最远的敌方英雄（免疫控制），路上的敌人受到" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "并晕眩" + A +
               "{r_stun}秒" + E + "，最后猛咬一口造成" + phys("r_bite_dmg", "r_bite_ad") + O + "物理伤害" + E + "，无视" + A +
               "{r_pen}%" + E + "护甲。",
        "names": ("噬咬", "翼刃横扫", "暴走"),
    },
    "zh-hant": {
        "name": "賽焚",
        "attack": "翼爪和甩尾交替攻擊，造成" + AD + O + "物理傷害" + E + "。" + O + "幽影低語" + E + "：他的傷害讓敵人縮小" + A + "{p_t}秒" +
                  E + "（物防、魔防" + A + "-{p_shred}%" + E + "）；打縮小的敵人疊怒氣，每層" + A + "+{p_ad}" + E + "攻擊力，最多" + A +
                  "{p_max}" + E + "層。",
        "skill": "撲上去咬住目標，造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "，無視" + A + "{q_pen}%" + E + "物防，回復" +
                 phys("q_heal", "q_heal_ad") + "生命。",
        "skill2": "張開雙翼橫掃身邊，造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並緩速" + A + "{e_slow}%" + E + "（" + A +
                  "{e_slow_t}秒" + E + "）。",
        "ult": "龍吼後衝向最遠的敵方英雄（免疫控制），路上的敵人受到" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "並暈眩" + A +
               "{r_stun}秒" + E + "，最後猛咬一口造成" + phys("r_bite_dmg", "r_bite_ad") + O + "物理傷害" + E + "，無視" + A +
               "{r_pen}%" + E + "物防。",
        "names": ("噬咬", "翼刃橫掃", "盛怒龍顎"),
    },
    "en": {
        "name": "Sy'fen",
        "attack": "Wing claws and tail lashes in turn for " + AD + " " + O + "physical damage" + E + ". " + O + "Whispers" + E +
                  ": his damage shrinks enemies for " + A + "{p_t}s" + E + " (" + A + "-{p_shred}%" + E + " armor and magic resist); "
                  "hitting a shrunk enemy stacks " + A + "+{p_ad}" + E + " attack (up to " + A + "{p_max}" + E + ").",
        "skill": "Lunges and bites the target for " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E + ", ignoring " + A +
                 "{q_pen}%" + E + " armor, healing " + phys("q_heal", "q_heal_ad") + ".",
        "skill2": "Sweeps his wings around him: " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E + " and a " + A +
                  "{e_slow}%" + E + " slow for " + A + "{e_slow_t}s" + E + ".",
        "ult": "Roars and charges the farthest enemy champion (immune to crowd control): enemies in his path take " +
               phys("r_dmg", "r_ad") + " " + O + "physical damage" + E + " and are stunned " + A + "{r_stun}s" + E + "; then a bite "
               "for " + phys("r_bite_dmg", "r_bite_ad") + ", ignoring " + A + "{r_pen}%" + E + " armor.",
        "names": ("Bite", "Wing Sweep", "Rampage"),
    },
    "ko": {
        "name": "사이펜",
        "attack": "날개 발톱과 꼬리로 번갈아 공격해 " + AD + " " + O + "물리 피해" + E + ". " + O + "속삭임" + E + ": 피해를 준 적을 " + A +
                  "{p_t}초" + E + " 동안 축소(방어력·마법 저항력 " + A + "-{p_shred}%" + E + "), 축소된 적을 공격하면 공격력 " + A +
                  "+{p_ad}" + E + " 중첩(최대 " + A + "{p_max}" + E + ").",
        "skill": "덮쳐서 대상을 물어 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + ", 방어력 " + A + "{q_pen}%" + E +
                 " 무시, 체력 " + phys("q_heal", "q_heal_ad") + " 회복.",
        "skill2": "날개를 펼쳐 주변을 휩쓸어 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + ", " + A + "{e_slow}%" + E +
                  " 둔화(" + A + "{e_slow_t}초" + E + ").",
        "ult": "포효한 뒤 가장 먼 적 챔피언에게 돌진(군중 제어 면역), 경로의 적에게 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" +
               E + "와 기절 " + A + "{r_stun}초" + E + ", 마지막으로 물어 " + phys("r_bite_dmg", "r_bite_ad") + " " + O + "물리 피해" +
               E + ", 방어력 " + A + "{r_pen}%" + E + " 무시.",
        "names": ("물어뜯기", "날개 칼날 휩쓸기", "광분"),
    },
    "ja": {
        "name": "サイ・フェン",
        "attack": "翼の爪と尾で交互に攻撃し" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "囁き" + E + "：ダメージを与えた敵を" + A +
                  "{p_t}秒" + E + "縮小（物理防御・魔法防御" + A + "-{p_shred}%" + E + "）、縮小した敵を攻撃すると攻撃力" + A + "+{p_ad}" +
                  E + "を重ねる（最大" + A + "{p_max}" + E + "）。",
        "skill": "飛びかかって対象に噛みつき" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "、物理防御を" + A + "{q_pen}%" + E +
                 "無視、体力を" + phys("q_heal", "q_heal_ad") + "回復。",
        "skill2": "翼を広げて周囲を薙ぎ払い" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + A + "{e_slow}%" + E +
                  "スロウ（" + A + "{e_slow_t}秒" + E + "）。",
        "ult": "咆哮し最も遠い敵チャンピオンへ突進（行動妨害無効）、進路上の敵に" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E +
               "とスタン" + A + "{r_stun}秒" + E + "、最後に噛みついて" + phys("r_bite_dmg", "r_bite_ad") + "の" + O + "物理ダメージ" + E +
               "、物理防御を" + A + "{r_pen}%" + E + "無視。",
        "names": ("噛みつき", "翼刃払い", "龍の猛攻"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_syfen's sfx / tsfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.35), ("p", 0.3),
    ("q", 0.5), ("q_bite", 0.55), ("q_hit", 0.45),
    ("e", 0.5), ("e_hit", 0.45),
    ("r", 0.5), ("r_roar", 0.55), ("r_dash", 0.5), ("r_hit", 0.45), ("r_bite", 0.5), ("r_bite_hit", 0.55),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/syfen.rs: the shrink, the rams, the bite's hit, his death cry)
DLL_SOUNDS = {f"{ID}_{x}" for x in ("p", "r_hit", "r_bite_hit", "d")}


def values(p):
    v = {k: p[k] for k in ("p_shred", "p_ad", "p_max", "q_dmg", "q_ad", "q_pen", "q_heal", "q_heal_ad", "e_dmg", "e_ad",
                           "e_slow", "r_dmg", "r_ad", "r_bite_dmg", "r_bite_ad", "r_pen")}
    for k in ("p_t", "e_slow_t", "r_stun"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_syfen.py")
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
    mi["last_updated"] = "2026-10-30"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
