"""Nomsy's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_nomsy.P.

    python tools/kit/setup_nomsy.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_sevika.py writes for Sevika: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_nomsy in every language, description + skill_name), sound/sfx/tft_nomsy_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX
and the texts themselves.
Names: TFT set 7's own (CommunityDragon cdragon/tft/<locale>.json, TFT7_Nomsy, 2026-10-29): zh_CN 诺姆希, zh_TW 嚼嚼, ja
ノムジー, ko 뇸뇸이, en Nomsy; her ability Fireballs! = 火球！ / 噴火球！ / ファイヤーボール！ / 불덩이!; her trait Dragon = 龙神 for
the passive's name (龙神之躯, Dragon Body). Dragon Breath (龙息) and Dragon Ascension (龙神飞升) are our own (the user's pick,
plan A 「龙神飞升」). The texts are the rules she plays with tft.dll (addons/tft/src/nomsy.rs): the low-health heal, the small
fireballs bouncing from the explosion.
Sounds: tools/lol/extract_nomsy.py's clips in tft/sound/sfx/tft_nomsy_sfx_*.wav (git-ignored) - her own set-7 TFT sounds
(the attack, the big fireball's launch and hit, the small ones' launch and hit, her two lines), the Rift's drakes (the
take-off, the landing, the Infernal Drake's fireballs), Smolder (the bolt's hit, the roar, the ascension, her death),
Shyvana's dragon heal, Annie's Incinerate and Brand's Blaze. A clip name never equals an event name (vo-clip-names
rule): event tft_nomsy_<x> plays clip tft_nomsy_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_nomsy import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19
VERSION = "0.19.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from her feet's point, up negative): the face point between her eyes (the design's eye row 29
# of 94 at PPU 2.6: 25 over the ground; 15 ahead of her standing column, ppu_restyle's face_to); the centre in her belly;
# the ban/pick card by bp_card_audit.py's rule (-39 less the idle's top -25.3: her head 1 game px under the card's top)
VIEW = {"face": {"x": 15, "y": -25}, "center": {"x": 2, "y": -14}, "banpick_center": {"x": 2, "y": -14}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "诺姆希",
        "attack": "吐出小火团，造成" + AD + O + "物理伤害" + E + "。" + O + "龙神之躯" + E + "：生命值低于" + A + "{p_low}%" + E +
                  "时每秒回复" + A + "{p_pct}%" + E + "最大生命值。",
        "skill": "抛出大火球，爆炸造成" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "，再弹出" + A + "{q_n}" + E +
                 "颗小火球打附近的敌人，各造成" + A + "{q_k}%" + E + "伤害。",
        "skill2": "向前喷出扇形龙息，造成" + mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "并灼烧" + A + "{e_burn_t}秒" + E +
                  "，魔抗降低" + A + "{e_mr}%" + E + "（" + A + "{e_mr_t}秒" + E + "）。",
        "ult": "飞上天空（减伤" + A + "{r_dr}%" + E + "、免疫控制），降下" + A + "{r_n}" + E + "颗火球，各造成" + mag("r_dmg", "r_ratio") +
               M + "魔法伤害" + E + "；落地后攻速" + A + "+{r_as}%" + E + "、法强" + A + "+{r_ap}%" + E + "（" + A + "{r_up_t}秒" + E + "）。",
        "names": ("火球！", "龙息", "龙神飞升"),
    },
    "zh-hant": {
        "name": "嚼嚼",
        "attack": "吐出小火團，造成" + AD + O + "物理傷害" + E + "。" + O + "龍神之軀" + E + "：生命值低於" + A + "{p_low}%" + E +
                  "時每秒回復" + A + "{p_pct}%" + E + "最大生命值。",
        "skill": "拋出大火球，爆炸造成" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "，再彈出" + A + "{q_n}" + E +
                 "顆小火球打附近的敵人，各造成" + A + "{q_k}%" + E + "傷害。",
        "skill2": "向前噴出扇形龍息，造成" + mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "並灼燒" + A + "{e_burn_t}秒" + E +
                  "，魔抗降低" + A + "{e_mr}%" + E + "（" + A + "{e_mr_t}秒" + E + "）。",
        "ult": "飛上天空（減傷" + A + "{r_dr}%" + E + "、免疫控制），降下" + A + "{r_n}" + E + "顆火球，各造成" + mag("r_dmg", "r_ratio") +
               M + "魔法傷害" + E + "；落地後攻速" + A + "+{r_as}%" + E + "、法強" + A + "+{r_ap}%" + E + "（" + A + "{r_up_t}秒" + E + "）。",
        "names": ("噴火球！", "龍息", "龍神飛升"),
    },
    "en": {
        "name": "Nomsy",
        "attack": "Spits a fire bolt for " + AD + " " + O + "physical damage" + E + ". " + O + "Dragon Body" + E + ": under " + A +
                  "{p_low}%" + E + " health she heals " + A + "{p_pct}%" + E + " of her max health each second.",
        "skill": "Lobs a fireball that explodes for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " and bounces " +
                 A + "{q_n}" + E + " small fireballs on to nearby enemies for " + A + "{q_k}%" + E + " of it each.",
        "skill2": "Breathes a cone of fire for " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + ", burning for " + A +
                  "{e_burn_t}s" + E + " and cutting magic resist by " + A + "{e_mr}%" + E + " for " + A + "{e_mr_t}s" + E + ".",
        "ult": "Flies up (" + A + "{r_dr}%" + E + " less damage, immune to crowd control) and rains " + A + "{r_n}" + E +
               " fireballs, each " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + "; landing, she gains " + A +
               "{r_as}%" + E + " attack speed and " + A + "{r_ap}%" + E + " ability power for " + A + "{r_up_t}s" + E + ".",
        "names": ("Fireballs!", "Dragon Breath", "Dragon Ascension"),
    },
    "ko": {
        "name": "뇸뇸이",
        "attack": "작은 불덩이를 뱉어 " + AD + " " + O + "물리 피해" + E + ". " + O + "용신의 몸" + E + ": 체력 " + A + "{p_low}%" + E +
                  " 미만이면 매초 최대 체력의 " + A + "{p_pct}%" + E + " 회복.",
        "skill": "불덩이를 던져 폭발로 " + mag("q_dmg", "q_ratio") + " " + M + "마법 피해" + E + ", 작은 불덩이 " + A + "{q_n}" + E +
                 "개가 근처 적에게 튀어 각각 " + A + "{q_k}%" + E + " 피해.",
        "skill2": "부채꼴로 불을 뿜어 " + mag("e_dmg", "e_ratio") + " " + M + "마법 피해" + E + ", " + A + "{e_burn_t}초" + E +
                  " 화상, 마법 저항력 " + A + "{e_mr}%" + E + " 감소(" + A + "{e_mr_t}초" + E + ").",
        "ult": "하늘로 날아올라(받는 피해 " + A + "{r_dr}%" + E + " 감소, 군중 제어 면역) 불덩이 " + A + "{r_n}" + E + "개를 떨어뜨려 각각 " +
               mag("r_dmg", "r_ratio") + " " + M + "마법 피해" + E + "; 착지 후 공격 속도 " + A + "+{r_as}%" + E + ", 주문력 " + A +
               "+{r_ap}%" + E + "(" + A + "{r_up_t}초" + E + ").",
        "names": ("불덩이!", "용의 숨결", "용신 승천"),
    },
    "ja": {
        "name": "ノムジー",
        "attack": "小さな火の玉を吐き" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "龍神の体" + E + "：体力" + A + "{p_low}%" + E +
                  "未満の間、毎秒最大体力の" + A + "{p_pct}%" + E + "回復。",
        "skill": "火の玉を投げ、爆発で" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "、小さな火の玉" + A + "{q_n}" + E +
                 "個が近くの敵に跳ね、それぞれ" + A + "{q_k}%" + E + "のダメージ。",
        "skill2": "扇形に炎を吐き" + mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" + E + "、" + A + "{e_burn_t}秒" + E +
                  "炎上、魔法防御" + A + "{e_mr}%" + E + "低下（" + A + "{e_mr_t}秒" + E + "）。",
        "ult": "空へ舞い上がり（被ダメージ" + A + "{r_dr}%" + E + "軽減、行動妨害無効）、火の玉" + A + "{r_n}" + E + "個を降らせそれぞれ" +
               mag("r_dmg", "r_ratio") + "の" + M + "魔法ダメージ" + E + "；着地後、攻撃速度" + A + "+{r_as}%" + E + "・魔力" + A +
               "+{r_ap}%" + E + "（" + A + "{r_up_t}秒" + E + "）。",
        "names": ("ファイヤーボール！", "ドラゴンブレス", "龍神昇天"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_nomsy's sfx / tsfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.35), ("p", 0.45),
    ("q", 0.5), ("q_vo", 0.6), ("q_hit", 0.6), ("q_bounce", 0.4), ("q_bounce_hit", 0.4),
    ("e", 0.5), ("e_hit", 0.35), ("e_burn", 0.35),
    ("r", 0.55), ("r_vo", 0.6), ("r_roar", 0.55), ("r_rain", 0.35), ("r_hit", 0.45), ("r_land", 0.55), ("r_up", 0.5),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/nomsy.rs: the heal, the small fireballs, her death cry)
DLL_SOUNDS = {f"{ID}_{x}" for x in ("p", "q_bounce", "q_bounce_hit", "d")}


def values(p):
    v = {k: p[k] for k in ("p_low", "p_pct", "q_dmg", "q_ratio", "q_n", "q_k", "e_dmg", "e_ratio", "e_mr", "r_dr", "r_n",
                           "r_dmg", "r_ratio", "r_as", "r_ap")}
    for k in ("e_burn_t", "e_mr_t", "r_up_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_nomsy.py")
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
    mi["last_updated"] = "2026-10-29"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
