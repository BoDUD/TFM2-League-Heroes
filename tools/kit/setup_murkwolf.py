"""Murk Wolf's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_murkwolf.P.

    python tools/kit/setup_murkwolf.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_raptor.py writes for the Crimson Raptor:
mod.mod_info (VERSION, the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type
native for tft.dll, the keys sorted), text/champion.i18n (tft_murkwolf in every language, description + skill_name),
sound/sfx/tft_murkwolf_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 18's own (CommunityDragon cdragon/tft/<locale>.json, DA_Murkwolf18, 2026-11-01): zh_CN 暗影狼, zh_TW 魔狼,
ja マークウルフ, ko 어스름늑대, en Murkwolf; its ability Rending Claws = 撕裂之爪 (zh_TW 撕扯之爪, ja 引き裂く爪, ko 찢어발기는 발톱),
Grey Buff = 灰霸符 (zh_TW 灰色增益, ja グレーバフ, ko 그레이 버프) from the same text. Twin Bite (双头撕咬), Slayer's Howl (狂战士之嚎)
and Pack Attack (狼群攻击) are our own (the user's pick, plan A 「撕裂之爪」).
The texts are the rules it plays with tft.dll (addons/tft/src/murkwolf.rs): the leap to the lowest-health enemy
(champions first), the counted empowered attacks, the howl's bonus doubled on the badly hurt, the pups' bites riding its
attacks, its skills' crits.
Sounds: tools/lol/extract_murkwolf.py's clips in tft/sound/sfx/tft_murkwolf_sfx_*.wav (git-ignored) - the Rift's own
murk wolves (the big one's bite, growls, howl and death; the little ones' spawn and death for the pups), Warwick,
Rengar and Naafiri for the rest. A clip name never equals an event name (vo-clip-names rule): event tft_murkwolf_<x>
plays clip tft_murkwolf_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_murkwolf import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29, the Elder Dragon 0.30, Meepsie 0.31 (PR #649), Murk Wolf 0.32
VERSION = "0.32.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point on its near eye (the design's eye at
# column 50, row 34 of 60 at PPU 1.67: 16 over the ground, 9 ahead of its standing point, the design's pivot column 36 -
# ppu_restyle's face_to); the centre in its body (3 ahead of its standing point, the middle of its back's 32 px); the
# ban/pick card as the Crimson Raptor's (the same 36 px from its highest point to its soles; its two heads kept inside
# the card by its UI size 0.9 in league.dll's hd.rs)
# center: the encyclopedia card puts this point at a fixed spot - set by League's rule (tools/art/bp_card_audit.py --centers, 2026-11-01)
VIEW = {"face": {"x": 9, "y": -16}, "center": {"x": 3, "y": -8}, "banpick_center": {"x": 0, "y": -14}}


def phys(d, r):
    """base + AD ratio, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "暗影狼",
        "attack": "两个头一起撕咬，造成" + AD + O + "物理伤害" + E + "。" + O + "灰霸符" + E + "：暴击率" + A + "{p_crit}%" + E +
                  "，随已损失生命值最多再" + A + "+{p_bonus}%" + E + "，技能也能暴击。",
        "skill": "跃向附近生命值最低的敌人，造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "。接下来" + A + "{q_n}次" + E +
                 "攻击攻速" + A + "+{q_as}%" + E + "，额外造成" + phys("q_emp_dmg", "q_emp_ad") + O + "物理伤害" + E + "。",
        "skill2": "仰头长嚎，" + A + "{e_t}秒" + E + "内吸血" + A + "{e_vamp}%" + E + "，伤害提高" + A + "{e_amp}%" + E + "，对生命低于" +
                  A + "{e_line}%" + E + "的敌人翻倍。",
        "ult": "叫来" + A + "2只" + E + "小暗影狼扑向目标，造成" + phys("r_leap_dmg", "r_leap_ad") + O + "物理伤害" + E + "。" + A +
               "{r_t}秒" + E + "内它每次攻击，小狼咬" + A + "{r_n}口" + E + "，每口" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "。",
        "names": ("撕裂之爪", "狂战士之嚎", "狼群攻击"),
    },
    "zh-hant": {
        "name": "魔狼",
        "attack": "兩個頭一起撕咬，造成" + AD + O + "物理傷害" + E + "。" + O + "灰色增益" + E + "：暴擊率" + A + "{p_crit}%" + E +
                  "，隨已損失生命最多再" + A + "+{p_bonus}%" + E + "，技能也能暴擊。",
        "skill": "躍向附近生命最低的敵軍，造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "。接下來" + A + "{q_n}次" + E +
                 "普攻攻速" + A + "+{q_as}%" + E + "，額外造成" + phys("q_emp_dmg", "q_emp_ad") + O + "物理傷害" + E + "。",
        "skill2": "仰頭長嚎，" + A + "{e_t}秒" + E + "內吸血" + A + "{e_vamp}%" + E + "，傷害提高" + A + "{e_amp}%" + E + "，對生命低於" +
                  A + "{e_line}%" + E + "的敵軍加倍。",
        "ult": "叫來" + A + "2隻" + E + "小魔狼撲向目標，造成" + phys("r_leap_dmg", "r_leap_ad") + O + "物理傷害" + E + "。" + A +
               "{r_t}秒" + E + "內牠每次普攻，小狼咬" + A + "{r_n}口" + E + "，每口" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "。",
        "names": ("撕扯之爪", "狂戰士之嚎", "狼群攻擊"),
    },
    "en": {
        "name": "Murkwolf",
        "attack": "Both heads bite for " + AD + " " + O + "physical damage" + E + ". " + O + "Grey Buff" + E + ": " + A +
                  "{p_crit}%" + E + " critical strike chance, up to " + A + "+{p_bonus}%" + E + " more with its missing Health; "
                  "its skills can critically strike.",
        "skill": "Leaps to the nearby enemy with the lowest Health for " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E +
                 ". Its next " + A + "{q_n}" + E + " attacks gain " + A + "+{q_as}%" + E + " attack speed and deal " +
                 phys("q_emp_dmg", "q_emp_ad") + " bonus " + O + "physical damage" + E + ".",
        "skill2": "Howls: for " + A + "{e_t}s" + E + " it gains " + A + "{e_vamp}%" + E + " omnivamp and deals " + A + "{e_amp}%" + E +
                  " more damage, doubled against enemies below " + A + "{e_line}%" + E + " Health.",
        "ult": "Calls " + A + "2" + E + " murk wolf pups that pounce on its target for " + phys("r_leap_dmg", "r_leap_ad") + " " + O +
               "physical damage" + E + ". For " + A + "{r_t}s" + E + ", each of its attacks the pups bite " + A + "{r_n}" + E +
               " times for " + phys("r_dmg", "r_ad") + " " + O + "physical damage" + E + " each.",
        "names": ("Rending Claws", "Slayer's Howl", "Pack Attack"),
    },
    "ko": {
        "name": "어스름늑대",
        "attack": "두 머리로 물어뜯어 " + AD + " " + O + "물리 피해" + E + ". " + O + "그레이 버프" + E + ": 치명타 확률 " + A + "{p_crit}%" + E +
                  ", 잃은 체력에 비례해 최대 " + A + "+{p_bonus}%" + E + " 더 증가하며 스킬도 치명타가 발생합니다.",
        "skill": "근처 체력이 가장 낮은 적에게 도약해 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + ". 다음 기본 공격 " + A + "{q_n}회" + E +
                 " 동안 공격 속도 " + A + "+{q_as}%" + E + ", 추가로 " + phys("q_emp_dmg", "q_emp_ad") + " " + O + "물리 피해" + E + ".",
        "skill2": "울부짖어 " + A + "{e_t}초" + E + " 동안 모든 피해 흡혈 " + A + "{e_vamp}%" + E + ", 주는 피해 " + A + "{e_amp}%" + E +
                  " 증가. 체력이 " + A + "{e_line}%" + E + " 미만인 적에게는 두 배.",
        "ult": "새끼 늑대 " + A + "2마리" + E + "를 불러 대상에게 덮쳐 " + phys("r_leap_dmg", "r_leap_ad") + " " + O + "물리 피해" + E + ". " +
               A + "{r_t}초" + E + " 동안 기본 공격할 때마다 새끼 늑대가 " + A + "{r_n}번" + E + " 물어 각각 " + phys("r_dmg", "r_ad") + " " + O +
               "물리 피해" + E + ".",
        "names": ("찢어발기는 발톱", "광전사의 울부짖음", "늑대 무리 공격"),
    },
    "ja": {
        "name": "マークウルフ",
        "attack": "2つの頭で噛みつき" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "グレーバフ" + E + "：クリティカル率" + A + "{p_crit}%" + E +
                  "、減少体力に応じて最大" + A + "+{p_bonus}%" + E + "。スキルもクリティカルする。",
        "skill": "近くで最も体力の低い敵に跳びかかり" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "。次の" + A + "{q_n}回" + E +
                 "の通常攻撃は攻撃速度" + A + "+{q_as}%" + E + "、" + phys("q_emp_dmg", "q_emp_ad") + "の追加" + O + "物理ダメージ" + E + "。",
        "skill2": "遠吠えし、" + A + "{e_t}秒" + E + "間オムニヴァンプ" + A + "{e_vamp}%" + E + "、与ダメージ" + A + "+{e_amp}%" + E + "。体力" +
                  A + "{e_line}%" + E + "未満の敵には2倍。",
        "ult": "子狼を" + A + "2体" + E + "呼び、対象に飛びかからせ" + phys("r_leap_dmg", "r_leap_ad") + "の" + O + "物理ダメージ" + E + "。" + A +
               "{r_t}秒" + E + "間、通常攻撃のたびに子狼が" + A + "{r_n}回" + E + "噛みつき、それぞれ" + phys("r_dmg", "r_ad") + "の" + O +
               "物理ダメージ" + E + "。",
        "names": ("引き裂く爪", "狂戦士の遠吠え", "群狼の襲撃"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_murkwolf's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.35), ("a_hit", 0.35),
    ("p", 0.3),
    ("q", 0.5), ("q_vo", 0.45), ("q_hit", 0.35), ("q_emp", 0.25),
    ("e", 0.45), ("e_vo", 0.5), ("e_hit", 0.25),
    ("r", 0.5), ("r_vo", 0.45), ("r_leap", 0.4), ("r_bite", 0.2), ("r_end", 0.35),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/murkwolf.rs: a skill's crit, the howl's doubled hit, its death cry,
# the rend, an empowered bite, a pup's bite)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_e_hit", f"{ID}_d", f"{ID}_q_hit", f"{ID}_q_emp", f"{ID}_r_bite"}


def values(p):
    v = {k: p[k] for k in ("p_crit", "p_bonus", "q_dmg", "q_ad", "q_n", "q_as", "q_emp_dmg", "q_emp_ad", "e_vamp",
                           "e_amp", "e_line", "r_leap_dmg", "r_leap_ad", "r_n", "r_dmg", "r_ad")}
    for k in ("e_t", "r_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_murkwolf.py")
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
