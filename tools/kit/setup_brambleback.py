"""The Crimson Brambleback's text (5 languages), sound_info files and the tft pack's shared files, numbers from
build_brambleback.P.

    python tools/kit/setup_brambleback.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_sentinel.py writes for the Sentinel: mod.mod_info
(VERSION, the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for
tft.dll, the keys sorted), text/champion.i18n (tft_brambleback in every language, description + skill_name),
sound/sfx/tft_brambleback_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 18's own (CommunityDragon cdragon/tft/<locale>.json, DA_Brambleback18, 2026-10-31): zh_CN 绯红印记树怪,
zh_TW 樹精長老, ja ブランブルバック, ko 덩굴정령, en Brambleback; its ability Crimson Fury = 猩红之怒 (zh_TW 猩紅狂怒,
ja 深紅の憤怒, ko 핏빛 분노), Red Buff = 红霸符 (zh_TW 紅色增益, ja レッドバフ, ko 레드 버프) from the same text. Bramble Claw
(荆爪横扫), Bramble Pounce (荆棘飞扑) and Crimson Roar (绯红咆哮) are our own (the user's pick, plan A 「猩红之怒」).
The texts are the rules it plays with tft.dll (addons/tft/src/brambleback.rs): the burn by the target's maximum health
(never a tower), the heal by its own, the leap on to the next after a kill.
Sounds: tools/lol/extract_brambleback.py's clips in tft/sound/sfx/tft_brambleback_sfx_*.wav (git-ignored) - the Rift's
own Red Brambleback (its claw, its roars, the death), Warwick, Rengar, Brand and Nasus for the rest. A clip name never
equals an event name (vo-clip-names rule): event tft_brambleback_<x> plays clip tft_brambleback_sfx_<x>. package_mod
moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_brambleback import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Crimson Brambleback 0.28
VERSION = "0.28.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point between its two eyes (the design's eyes
# round column 77.5, row 30.5 of 68 at PPU 1.7: 22 over the ground, 15 ahead of its standing point, the design's pivot
# column 52 - ppu_restyle's face_to); the centre in its body (the pivot column, half its 40 px); the ban/pick card as
# the Sentinel's (the same 40 px at PPU 1.7)
VIEW = {"face": {"x": 15, "y": -22}, "center": {"x": 0, "y": -20}, "banpick_center": {"x": 0, "y": -10}}


def phys(d, r):
    """base + AD ratio, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "绯红印记树怪",
        "attack": "大爪横扫，造成" + AD + O + "物理伤害" + E + "。" + O + "红霸符" + E + "：普攻灼烧目标" + A + "{burn_t}秒" + E + "（每秒" + HPi +
                  R + "{burn_ps}%" + E + "真实伤害），回复" + HPi + O + "{heal}%" + E + "生命；击杀后扑向下一个敌人，造成" + phys("k_dmg", "k_ad") +
                  O + "物理伤害" + E + "。",
        "skill": "跃起扑向目标，造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并减速" + R + "{q_slow}%" + E + "（" + A + "{q_slow_t}秒" +
                 E + "）。",
        "skill2": "人立怒吼：周围敌人减速" + R + "{e_slow}%" + E + "、攻击力降低" + R + "{e_atk}%" + E + "，自己受到的伤害降低" + O + "{e_dr}%" + E +
                  "，持续" + A + "{e_t}秒" + E + "。",
        "ult": "狂暴" + A + "{r_t}秒" + E + "：攻击力" + O + "+{r_atk}%" + E + "、攻速" + O + "+{r_as}%" + E + "，无视目标" + O + "{r_pen}%" + E +
               "护甲。",
        "names": ("荆棘飞扑", "绯红咆哮", "猩红之怒"),
    },
    "zh-hant": {
        "name": "樹精長老",
        "attack": "大爪橫掃，造成" + AD + O + "物理傷害" + E + "。" + O + "紅色增益" + E + "：普攻燃燒目標" + A + "{burn_t}秒" + E + "（每秒" + HPi +
                  R + "{burn_ps}%" + E + "真實傷害），回復" + HPi + O + "{heal}%" + E + "生命；擊殺後撲向下一個敵人，造成" + phys("k_dmg", "k_ad") +
                  O + "物理傷害" + E + "。",
        "skill": "躍起撲向目標，造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並緩速" + R + "{q_slow}%" + E + "（" + A + "{q_slow_t}秒" +
                 E + "）。",
        "skill2": "人立怒吼：周圍敵人緩速" + R + "{e_slow}%" + E + "、攻擊力降低" + R + "{e_atk}%" + E + "，自己受到的傷害降低" + O + "{e_dr}%" + E +
                  "，持續" + A + "{e_t}秒" + E + "。",
        "ult": "狂暴" + A + "{r_t}秒" + E + "：攻擊力" + O + "+{r_atk}%" + E + "、攻速" + O + "+{r_as}%" + E + "，無視目標" + O + "{r_pen}%" + E +
               "物防。",
        "names": ("荊棘飛撲", "緋紅咆哮", "猩紅狂怒"),
    },
    "en": {
        "name": "Brambleback",
        "attack": "A claw rake for " + AD + " " + O + "physical damage" + E + ". " + O + "Red Buff" + E + ": attacks Burn for " + A +
                  "{burn_t}s" + E + " (" + HPi + R + "{burn_ps}%" + E + " true damage a second) and heal " + HPi + O + "{heal}%" + E +
                  "; after a kill it leaps at the next enemy for " + phys("k_dmg", "k_ad") + " " + O + "physical damage" + E + ".",
        "skill": "Pounces on its target for " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E + ", slowing it " + R +
                 "{q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": "Rears up and roars: nearby enemies are slowed " + R + "{e_slow}%" + E + " and lose " + R + "{e_atk}%" + E +
                  " attack, it takes " + O + "{e_dr}%" + E + " less damage, for " + A + "{e_t}s" + E + ".",
        "ult": "Frenzied for " + A + "{r_t}s" + E + ": " + O + "+{r_atk}%" + E + " attack, " + O + "+{r_as}%" + E +
               " attack speed, ignores " + O + "{r_pen}%" + E + " of its target's armor.",
        "names": ("Bramble Pounce", "Crimson Roar", "Crimson Fury"),
    },
    "ko": {
        "name": "덩굴정령",
        "attack": "발톱으로 할퀴어 " + AD + " " + O + "물리 피해" + E + ". " + O + "레드 버프" + E + ": 기본 공격이 " + A + "{burn_t}초" + E +
                  " 동안 화상(초당 " + HPi + R + "{burn_ps}%" + E + " 고정 피해)을 입히고 " + HPi + O + "{heal}%" + E +
                  " 회복; 처치 후 다음 적에게 도약해 " + phys("k_dmg", "k_ad") + " " + O + "물리 피해" + E + ".",
        "skill": "대상에게 덮쳐 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + ", " + A + "{q_slow_t}초" + E + " 동안 " + R +
                 "{q_slow}%" + E + " 둔화.",
        "skill2": "일어서서 포효: 주변 적 " + R + "{e_slow}%" + E + " 둔화, 공격력 " + R + "{e_atk}%" + E + " 감소, 자신은 받는 피해 " + O +
                  "{e_dr}%" + E + " 감소(" + A + "{e_t}초" + E + ").",
        "ult": A + "{r_t}초" + E + " 동안 광폭화: 공격력 " + O + "+{r_atk}%" + E + ", 공격 속도 " + O + "+{r_as}%" + E + ", 대상 방어력 " + O +
               "{r_pen}%" + E + " 무시.",
        "names": ("가시덩굴 덮치기", "진홍의 포효", "핏빛 분노"),
    },
    "ja": {
        "name": "ブランブルバック",
        "attack": "爪でなぎ払い" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "レッドバフ" + E + "：通常攻撃が" + A + "{burn_t}秒" + E +
                  "燃焼（毎秒" + HPi + R + "{burn_ps}%" + E + "の確定ダメージ）させ、" + HPi + O + "{heal}%" + E + "回復。倒すと次の敵に跳びかかり" +
                  phys("k_dmg", "k_ad") + "の" + O + "物理ダメージ" + E + "。",
        "skill": "対象に跳びかかり" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "、" + A + "{q_slow_t}秒" + E + "間" + R +
                 "{q_slow}%" + E + "スロウ。",
        "skill2": "立ち上がって咆哮：周囲の敵を" + R + "{e_slow}%" + E + "スロウ、攻撃力" + R + "{e_atk}%" + E + "低下、自身の被ダメージ" + O +
                  "{e_dr}%" + E + "軽減（" + A + "{e_t}秒" + E + "）。",
        "ult": A + "{r_t}秒" + E + "間激昂：攻撃力" + O + "+{r_atk}%" + E + "、攻撃速度" + O + "+{r_as}%" + E + "、対象の物理防御を" + O +
               "{r_pen}%" + E + "無視。",
        "names": ("茨の飛びかかり", "深紅の咆哮", "深紅の憤怒"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_brambleback's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.4),
    ("p", 0.3),
    ("q", 0.5), ("q_hit", 0.45), ("q_next", 0.45),
    ("e", 0.5), ("e_guard", 0.35), ("e_slow", 0.35),
    ("r", 0.5), ("r_vo", 0.5), ("r_fire", 0.4),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/brambleback.rs: a fresh burn, the leap on and its landing, the collapse)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_q_next", f"{ID}_q_hit", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("k_dmg", "k_ad", "q_dmg", "q_ad", "q_slow", "e_slow", "e_atk", "e_dr", "r_atk", "r_as", "r_pen")}
    v["heal"] = f"{p['p_heal'] / 10:g}"                                       # per mille of its maximum health
    v["burn_ps"] = f"{p['p_burn'] * 60 / p['p_burn_every'] / 10:g}"           # per mille a tick -> % a second
    for k, src in (("q_slow_t", "q_slow_t"), ("e_t", "e_t"), ("r_t", "r_t"), ("burn_t", "p_burn_t")):
        v[k] = secs(p[src])
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_brambleback.py")
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
    mi["last_updated"] = "2026-10-31"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
