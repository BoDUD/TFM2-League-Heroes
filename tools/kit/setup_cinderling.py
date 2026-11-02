"""The Cinderling's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_cinderling.P.

    python tools/kit/setup_cinderling.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_sentry.py writes for the Sentry: mod.mod_info
(VERSION, the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for
tft.dll, the keys sorted), text/champion.i18n (tft_cinderling in every language, description + skill_name),
sound/sfx/tft_cinderling_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 18's own (CommunityDragon cdragon/tft/<locale>.json, DA_Cinderling18, 2026-11-02): zh_CN 绯红树怪, zh_TW
樹精, ja シンダーリング, ko 불타는 묘목, en Cinderling; its ability Razor Leaves = 刃叶 (zh_TW 飛葉快刀, ja 鋭葉カッター, ko 예리한
잎사귀), Scarlet Buff = 绯红霸符 (zh_TW 緋紅增益, ja スカーレットバフ, ko 진홍색 버프) from the same text. Ember Leaf (余烬叶), Burrow
(钻土突袭) and Wildfire Leafstorm (燎原叶暴) are our own (the user's OK of the proposed kit, 2026-11-02).
The texts are the rules the data plays (build_cinderling; tft.dll's cinderling.rs only plays its death sound).
Sounds: tools/lol/extract_cinderling.py's clips in tft/sound/sfx/tft_cinderling_sfx_*.wav (git-ignored) - the Rift's Red
camp minis' own voice (Map11 SRU_RedMini) and Zyra's leaves, Brand's fire, Rek'Sai's burrow, the Red Brambleback's buff.
A clip name never equals an event name (vo-clip-names rule): event tft_cinderling_<x> plays clip
tft_cinderling_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_cinderling import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29, the Elder Dragon 0.30, Meepsie 0.31, Murk Wolf 0.32, the Scuttle Crab 0.33, Gromp 0.34, the encyclopedia
# centres 0.35 (PR #657), the log fixes 0.36 (PR #659), the Sentry 0.37, Brock 0.38 (claude/tft-brock), the Cinderling
# 0.39
VERSION = "0.39.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point on its big eye (2 ahead of its standing
# point, 11 over the ground - ppu_restyle's face_to); the centre (League's rule, tools/art/bp_card_audit.py --centers);
# the ban/pick card as the Sentry's
VIEW = {"face": {"x": 2, "y": -11}, "center": {"x": 0, "y": -6}, "banpick_center": {"x": 0, "y": -12}}


def phys(d, r):
    """base + AD ratio, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "绯红树怪",
        "attack": "甩出余烬叶，造成" + AD + O + "物理伤害" + E + "。" + O + "绯红霸符" + E + "：每放一个技能攻击力" + A + "+{p_ad}" + E +
                  "（最多" + A + "4层" + E + "，" + A + "{p_t}秒" + E + "不放技能清空）；满层时普攻灼烧英雄。",
        "skill": "五片叶刃聚向目标，共造成" + phys("q_dmg", "q_ratio") + O + "物理伤害" + E + "，施加" + A + "{q_wound_t}秒" + E + "重伤（治疗" + A +
                 "-{q_wound}%" + E + "）和灼烧（每秒" + R + "{p_burn}%" + E + "最大生命" + R + "真实伤害" + E + "，" + A + "{p_burn_t}秒" + E + "）。",
        "skill2": "钻进地里溅起泥土，周围敌人受到" + phys("e_dmg", "e_ratio") + O + "物理伤害" + E + "并减速" + A + "{e_slow}%" + E + "（" + A +
                  "{e_hold}秒" + E + "），再从远离目标的地方钻出（地下受伤" + A + "-{e_dr}%" + E + "）。",
        "ult": "站起来点燃叶子：" + A + "{r_t}秒" + E + "内攻速" + A + "+{r_as}%" + E + "，每" + A + "{r_p}秒" + E + "向附近敌人射出" + A + "{r_n}片" + E +
               "燃烧叶刃，各造成" + phys("r_dmg", "r_ratio") + O + "物理伤害" + E + "，英雄被灼烧。",
        "names": ("刃叶", "钻土突袭", "燎原叶暴"),
    },
    "zh-hant": {
        "name": "樹精",
        "attack": "甩出餘燼葉，造成" + AD + O + "物理傷害" + E + "。" + O + "緋紅增益" + E + "：每施放一個技能物攻" + A + "+{p_ad}" + E +
                  "（最多" + A + "4層" + E + "，" + A + "{p_t}秒" + E + "不施放技能清空）；滿層時普攻燃燒英雄。",
        "skill": "五片葉刃匯聚向目標，共造成" + phys("q_dmg", "q_ratio") + O + "物理傷害" + E + "，附加" + A + "{q_wound_t}秒" + E + "重創（治療" + A +
                 "-{q_wound}%" + E + "）和燃燒（每秒" + R + "{p_burn}%" + E + "最大生命" + R + "真實傷害" + E + "，" + A + "{p_burn_t}秒" + E + "）。",
        "skill2": "鑽進地裡濺起泥土，周圍敵軍受到" + phys("e_dmg", "e_ratio") + O + "物理傷害" + E + "並緩速" + A + "{e_slow}%" + E + "（" + A +
                  "{e_hold}秒" + E + "），再從遠離目標的地方鑽出（地下受傷" + A + "-{e_dr}%" + E + "）。",
        "ult": "站起來點燃葉子：" + A + "{r_t}秒" + E + "內攻速" + A + "+{r_as}%" + E + "，每" + A + "{r_p}秒" + E + "向附近敵軍射出" + A + "{r_n}片" + E +
               "燃燒葉刃，各造成" + phys("r_dmg", "r_ratio") + O + "物理傷害" + E + "，英雄被燃燒。",
        "names": ("飛葉快刀", "鑽土突襲", "燎原葉暴"),
    },
    "en": {
        "name": "Cinderling",
        "attack": "Flicks an ember leaf for " + AD + " " + O + "physical damage" + E + ". " + O + "Scarlet Buff" + E + ": each spell cast grants " +
                  A + "+{p_ad}" + E + " Attack Damage (up to " + A + "4" + E + " stacks, lost after " + A + "{p_t}s" + E + " without a cast); at "
                  "full stacks its attacks Burn champions.",
        "skill": "Five razor leaves converge on its target for " + phys("q_dmg", "q_ratio") + " " + O + "physical damage" + E + " in all, "
                 "applying Wound (" + A + "-{q_wound}%" + E + " healing, " + A + "{q_wound_t}s" + E + ") and Burn (" + R + "{p_burn}%" + E +
                 " max Health " + R + "true damage" + E + " a second, " + A + "{p_burn_t}s" + E + ").",
        "skill2": "Burrows, kicking up earth: nearby enemies take " + phys("e_dmg", "e_ratio") + " " + O + "physical damage" + E +
                  " and are slowed by " + A + "{e_slow}%" + E + " for " + A + "{e_hold}s" + E + "; it bursts out away from its target (" + A +
                  "-{e_dr}%" + E + " damage taken underground).",
        "ult": "Rears up and sets its leaves ablaze: for " + A + "{r_t}s" + E + " it gains " + A + "+{r_as}%" + E + " Attack Speed and every " +
               A + "{r_p}s" + E + " fires " + A + "{r_n}" + E + " burning leaves at nearby enemies for " + phys("r_dmg", "r_ratio") + " " + O +
               "physical damage" + E + " each, Burning champions.",
        "names": ("Razor Leaves", "Burrow", "Wildfire Leafstorm"),
    },
    "ko": {
        "name": "불타는 묘목",
        "attack": "잿불 잎사귀를 던져 " + AD + " " + O + "물리 피해" + E + ". " + O + "진홍색 버프" + E + ": 스킬을 쓸 때마다 공격력 " + A + "+{p_ad}" + E +
                  "(최대 " + A + "4중첩" + E + ", " + A + "{p_t}초" + E + " 동안 스킬을 안 쓰면 초기화). 최대 중첩 시 기본 공격이 챔피언에게 화상.",
        "skill": "날카로운 잎사귀 5개가 대상에게 모여 총 " + phys("q_dmg", "q_ratio") + " " + O + "물리 피해" + E + "를 주고 " + A + "{q_wound_t}초" + E +
                 " 동안 상처(회복 " + A + "-{q_wound}%" + E + ")와 화상(매초 최대 체력 " + R + "{p_burn}%" + E + " " + R + "고정 피해" + E + ", " + A +
                 "{p_burn_t}초" + E + ").",
        "skill2": "흙을 튀기며 땅속으로 파고들어 주변 적에게 " + phys("e_dmg", "e_ratio") + " " + O + "물리 피해" + E + "와 " + A + "{e_slow}%" + E +
                  " 둔화(" + A + "{e_hold}초" + E + "). 대상에게서 먼 곳으로 솟아오릅니다(땅속 피해 " + A + "-{e_dr}%" + E + ").",
        "ult": "일어서서 잎사귀에 불을 붙입니다: " + A + "{r_t}초" + E + " 동안 공격 속도 " + A + "+{r_as}%" + E + ", " + A + "{r_p}초" + E + "마다 주변 적에게 " +
               "불타는 잎사귀 " + A + "{r_n}개" + E + "를 날려 각각 " + phys("r_dmg", "r_ratio") + " " + O + "물리 피해" + E + ", 챔피언은 화상.",
        "names": ("예리한 잎사귀", "땅굴 기습", "들불 잎폭풍"),
    },
    "ja": {
        "name": "シンダーリング",
        "attack": "燃える葉を投げ" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "スカーレットバフ" + E + "：スキル使用ごとに攻撃力" + A + "+{p_ad}" + E +
                  "（最大" + A + "4" + E + "スタック、" + A + "{p_t}秒" + E + "使わないと消滅）。最大スタック時、通常攻撃がチャンピオンを燃焼。",
        "skill": "5枚の鋭い葉が対象に収束し、合計" + phys("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "、" + A + "{q_wound_t}秒" + E +
                 "の負傷（回復" + A + "-{q_wound}%" + E + "）と燃焼（毎秒最大体力の" + R + "{p_burn}%" + E + R + "確定ダメージ" + E + "、" + A +
                 "{p_burn_t}秒" + E + "）。",
        "skill2": "土を跳ね上げて地中に潜り、周囲の敵に" + phys("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "と" + A + "{e_slow}%" + E +
                  "スロウ（" + A + "{e_hold}秒" + E + "）。対象から離れた所に飛び出す（地中で被ダメージ" + A + "-{e_dr}%" + E + "）。",
        "ult": "立ち上がり葉に火をつける：" + A + "{r_t}秒" + E + "間攻撃速度" + A + "+{r_as}%" + E + "、" + A + "{r_p}秒" + E + "ごとに近くの敵へ燃える葉を" +
               A + "{r_n}枚" + E + "放ち各" + phys("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "、チャンピオンは燃焼。",
        "names": ("鋭葉カッター", "土潜り奇襲", "燎原リーフストーム"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_cinderling's sfx), and its death
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.35), ("a_hit", 0.3),
    ("p", 0.35),
    ("q", 0.45), ("q_vo", 0.4), ("q_hit", 0.35), ("q_burn", 0.3),
    ("e", 0.45), ("e_out", 0.5), ("e_vo", 0.4),
    ("r", 0.5), ("r_vo", 0.45), ("r_shot", 0.2), ("r_hit", 0.25),
    ("d", 0.5), ("p_burn", 0.25))}
# the sound tft.dll plays itself (addons/tft/src/cinderling.rs: its death)
DLL_SOUNDS = {f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("p_ad", "p_burn", "q_dmg", "q_ratio", "q_wound", "e_dr", "e_dmg", "e_ratio", "e_slow", "r_as",
                           "r_n", "r_dmg", "r_ratio")}
    for k in ("p_t", "p_burn_t", "q_wound_t", "e_hold", "r_t", "r_p"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_cinderling.py")
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
    mi["contains_code"], mi["mod_type"] = True, "native"     # tft.dll (addons/tft): the other heroes' rules
    mi["last_updated"] = "2026-11-02"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
