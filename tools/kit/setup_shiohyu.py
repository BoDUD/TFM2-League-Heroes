"""Shi Oh Yu's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_shiohyu.P.

    python tools/kit/setup_shiohyu.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_daeja.py writes for Daeja: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_shiohyu in every language, description + skill_name),
sound/sfx/tft_shiohyu_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 7's own (CommunityDragon cdragon/tft/<locale>.json, TFT7_DragonGreen, 2026-10-30): zh_CN 石傲玉, zh_TW 襲奧玉,
ja シ・オー・ユー, ko 시오유, en Shi Oh Yu; his ability Jade Form = 玉龙形态 / 翠玉之型 / 翡翠の構え / 비취 형태. Jade Skin (玉石之肤),
the Dragon Claw Combo (龙爪三连), Jade Fist Barrage (玉拳连打) and Earthshaker (震地) are our own (the user's pick, plan A
「玉龙三连」). The passive's text rides on the attack's (the pack's heroes have no passive slot; tft.dll plays it:
addons/tft/src/shiohyu.rs).
Sounds: tools/lol/extract_shiohyu.py's clips in tft/sound/sfx/tft_shiohyu_sfx_*.wav (git-ignored) - his own set-7 TFT
attack sounds (the swipes, the crit for the fists, Attack1-3 for Jade Form's blows), Malphite (the stone skin, the ground
slam), Lee Sin (the rush), Taric (Jade Form, the wave) and the Rift's drakes (the roar, the death). A clip name never
equals an event name (vo-clip-names rule): event tft_shiohyu_<x> plays clip tft_shiohyu_sfx_<x>. package_mod moves the
clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_shiohyu import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22
VERSION = "0.22.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
T = "<#f5f5f5ff>"      # true damage (setup_aoshin's)
# champion_view (game px from his feet's point, up negative): the face point at his glowing eye (the design's eye
# (53, 38) of 74 x 103 at PPU 2.46, his standing column 46: 3 ahead, 26 over the ground; ppu_restyle's face_to); the
# centre in his chest; the ban/pick card by bp_card_audit.py's rule (-39 less the idle's top -30.5 over its frame centre:
# the wing tips 1 game px under the card's top)
VIEW = {"face": {"x": 3, "y": -26}, "center": {"x": -1, "y": -18}, "banpick_center": {"x": -1, "y": -8}}


def ad(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "石傲玉",
        "attack": "左右爪交替挥击，第3下造成" + ad("a3_dmg", "a3_ad") + O + "物理伤害" + E + "。" + O + "玉石之肤" + E + "：生命低于" +
                  A + "{p_low}%" + E + "时化作玉石，减伤" + A + "{p_red}%" + E + "（" + A + "{p_t}秒" + E + "，冷却" + A + "{p_cd}秒" +
                  E + "）。",
        "skill": "冲向目标连打" + A + "{q_n}" + E + "拳，每拳造成" + ad("q_dmg", "q_ad") + O + "物理伤害" + E + "。",
        "skill2": "一拳砸地，周围敌人受到" + ad("e_dmg", "e_ad") + O + "物理伤害" + E + "，被" + R + "击飞{e_up}秒" + E + "并减速" + A +
                  "{e_slow}%" + E + "。",
        "ult": "减伤" + A + "{r_red}%" + E + "、免疫控制，接下来3次普攻各造成" + ad("r_dmg", "r_ad") + "伤害：第1下" + R + "晕眩{r_stun}秒" +
               E + "；第2下为" + T + "真实伤害" + E + "；第3下打出直线冲击波，" + R + "晕眩" + E + "沿线敌人。",
        "names": ("玉拳连打", "震地", "玉龙形态"),
    },
    "zh-hant": {
        "name": "襲奧玉",
        "attack": "左右爪交替揮擊，第3下造成" + ad("a3_dmg", "a3_ad") + O + "物理傷害" + E + "。" + O + "玉石之膚" + E + "：生命低於" +
                  A + "{p_low}%" + E + "時化作翠玉，減傷" + A + "{p_red}%" + E + "（" + A + "{p_t}秒" + E + "，冷卻" + A + "{p_cd}秒" +
                  E + "）。",
        "skill": "衝向目標連打" + A + "{q_n}" + E + "拳，每拳造成" + ad("q_dmg", "q_ad") + O + "物理傷害" + E + "。",
        "skill2": "一拳砸地，周圍敵人受到" + ad("e_dmg", "e_ad") + O + "物理傷害" + E + "，被" + R + "擊飛{e_up}秒" + E + "並緩速" + A +
                  "{e_slow}%" + E + "。",
        "ult": "減傷" + A + "{r_red}%" + E + "、免疫控場，接下來3次普攻各造成" + ad("r_dmg", "r_ad") + "傷害：第1下" + R + "暈眩{r_stun}秒" +
               E + "；第2下為" + T + "真實傷害" + E + "；第3下打出直線衝擊波，" + R + "暈眩" + E + "沿線敵軍。",
        "names": ("玉拳連打", "震地", "翠玉之型"),
    },
    "en": {
        "name": "Shi Oh Yu",
        "attack": "Swipes with alternating claws; every third deals " + ad("a3_dmg", "a3_ad") + " " + O + "physical damage" + E +
                  ". " + O + "Jade Skin" + E + ": under " + A + "{p_low}%" + E + " health his skin turns to jade, " + A +
                  "{p_red}%" + E + " less damage for " + A + "{p_t}s" + E + " (" + A + "{p_cd}s" + E + " cooldown).",
        "skill": "Rushes at the target and lands " + A + "{q_n}" + E + " punches, each " + ad("q_dmg", "q_ad") + " " + O +
                 "physical damage" + E + ".",
        "skill2": "Smashes the ground: nearby enemies take " + ad("e_dmg", "e_ad") + " " + O + "physical damage" + E + ", are " + R +
                  "knocked up for {e_up}s" + E + " and slowed " + A + "{e_slow}%" + E + ".",
        "ult": "Takes " + A + "{r_red}%" + E + " less damage and is immune to crowd control; his next 3 attacks deal " +
               ad("r_dmg", "r_ad") + " each: the 1st " + R + "stuns for {r_stun}s" + E + ", the 2nd is " + T + "true damage" + E +
               ", the 3rd sends a wave down a line that " + R + "stuns" + E + " every enemy in it.",
        "names": ("Jade Fist Barrage", "Earthshaker", "Jade Form"),
    },
    "ko": {
        "name": "시오유",
        "attack": "양 발톱을 번갈아 휘두르며 세 번째 공격은 " + ad("a3_dmg", "a3_ad") + " " + O + "물리 피해" + E + ". " + O + "비취 피부" +
                  E + ": 체력이 " + A + "{p_low}%" + E + " 미만이 되면 피부가 비취로 변해 받는 피해 " + A + "{p_red}%" + E + " 감소(" + A +
                  "{p_t}초" + E + ", 재사용 " + A + "{p_cd}초" + E + ").",
        "skill": "대상에게 돌진해 주먹을 " + A + "{q_n}" + E + "번 날려 각각 " + ad("q_dmg", "q_ad") + " " + O + "물리 피해" + E + ".",
        "skill2": "땅을 내리쳐 주변 적에게 " + ad("e_dmg", "e_ad") + " " + O + "물리 피해" + E + ", " + R + "{e_up}초 공중에 띄움" + E +
                  ", " + A + "{e_slow}%" + E + " 둔화.",
        "ult": "받는 피해 " + A + "{r_red}%" + E + " 감소, 군중 제어 면역. 다음 3번의 공격이 각각 " + ad("r_dmg", "r_ad") + " 피해: 1번째 " +
               R + "{r_stun}초 기절" + E + ", 2번째 " + T + "고정 피해" + E + ", 3번째 일직선 충격파로 적 모두 " + R + "기절" + E + ".",
        "names": ("비취 연타", "대지 강타", "비취 형태"),
    },
    "ja": {
        "name": "シ・オー・ユー",
        "attack": "左右の爪で交互に攻撃し、3回目は" + ad("a3_dmg", "a3_ad") + "の" + O + "物理ダメージ" + E + "。" + O + "翡翠の肌" + E +
                  "：体力が" + A + "{p_low}%" + E + "未満で肌が翡翠になり、被ダメージ" + A + "{p_red}%" + E + "軽減（" + A + "{p_t}秒" + E +
                  "、クールダウン" + A + "{p_cd}秒" + E + "）。",
        "skill": "対象へ突進し拳を" + A + "{q_n}" + E + "回叩き込み、それぞれ" + ad("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "。",
        "skill2": "地面を殴りつけ、周囲の敵に" + ad("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "、" + R + "{e_up}秒打ち上げ" + E +
                  "、" + A + "{e_slow}%" + E + "スロウ。",
        "ult": "被ダメージ" + A + "{r_red}%" + E + "軽減、行動妨害無効。次の3回の通常攻撃がそれぞれ" + ad("r_dmg", "r_ad") + "：1回目" + R +
               "{r_stun}秒スタン" + E + "、2回目" + T + "確定ダメージ" + E + "、3回目は直線の衝撃波で敵全員を" + R + "スタン" + E + "。",
        "names": ("翡翠連拳", "大地砕き", "翡翠の構え"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_shiohyu's sfx / tsfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.35), ("p", 0.5),
    ("q", 0.45), ("q_punch", 0.35), ("q_hit", 0.35),
    ("e", 0.5), ("e_hit", 0.5),
    ("r", 0.5), ("r_roar", 0.5), ("r1", 0.45), ("r1_hit", 0.45), ("r2", 0.45), ("r2_hit", 0.45),
    ("r3", 0.45), ("r3_wave", 0.5), ("r3_hit", 0.45),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/shiohyu.rs: the jade skin, his death cry)
DLL_SOUNDS = {f"{ID}_{x}" for x in ("p", "d")}


def values(p):
    v = {k: p[k] for k in ("a3_dmg", "a3_ad", "p_low", "p_red", "q_n", "q_dmg", "q_ad", "e_dmg", "e_ad", "e_slow",
                           "r_red", "r_dmg", "r_ad")}
    for k in ("p_t", "p_cd", "e_up", "r_stun"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_shiohyu.py")
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
