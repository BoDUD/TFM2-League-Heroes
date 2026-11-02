"""Sevika's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_sevika.P.

    python tools/kit/setup_sevika.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_renni.py writes for Renni: mod.mod_info (VERSION, the
pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys
sorted), text/champion.i18n (tft_sevika in every language, description + skill_name), sound/sfx/tft_sevika_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX
and the texts themselves.
Names: TFT set 13's own (CommunityDragon latest cdragon/tft/<locale>.json, TFT13_Lieutenant, 2026-10-29): zh_CN 塞薇卡,
zh_TW 塞薇卡, ja セヴィカ, ko 세비카, en Sevika; her three spells Flamethrower / Extendo-Punch / Chomp = 喷火器 / 伸缩拳 / 嚼一嚼,
火焰噴射器 / 延伸重拳 / 撕咬, 火炎放射器 / エクステンドパンチ / 咬み砕き, 화염 방사기 / 늘어나는 펀치 / 깨물기; her trait High Roller = 百变铁手 /
豪氣賭客 / ギャンブラー / 도박꾼 for the passive. The Mechanical Fist (机械铁拳) is our own (the user's pick, plan A 「百变铁手」: TFT's one
ability taken apart into her three slots). The texts are the rules she plays with tft.dll (addons/tft/src/sevika.rs): the
slot machine on every skill, the punch's knockback and the stun of the two knocked together, the chomp's bites, bleed,
execute and re-dash.
Sounds: tools/lol/extract_sevika.py's clips in tft/sound/sfx/tft_sevika_sfx_*.wav (git-ignored) - her own set-13 TFT
sounds (the arm's punches and clamp, the slot machine's roll, Jinx's rockets, the jackpot, the flamethrower, the extendo
punch, the slam's dash, hit and explosion, the chomp, her voice), Lux's Prismatic Barrier for the shield mod and Jinx's
Get Excited! for the shimmer mod. A clip name never equals an event name (vo-clip-names rule): event tft_sevika_<x>
plays clip tft_sevika_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sevika import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17
VERSION = "0.17.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from her soles' point, up negative): the face point between her eyes (the design's eye row 12
# of 70 at PPU 1.8: 32 over the ground; 1 ahead of her standing column, ppu_restyle's face_to); the centre in her body;
# the ban/pick card by bp_card_audit.py's rule (-39 less the idle's top -27.9: her head 1 game px under the card's top)
# center: the encyclopedia card puts this point at a fixed spot - set by League's rule (tools/art/bp_card_audit.py --centers, 2026-11-01)
VIEW = {"face": {"x": 1, "y": -32}, "center": {"x": 1, "y": -12}, "banpick_center": {"x": 1, "y": -11}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "塞薇卡",
        "attack": "铁拳造成" + ADi + O + "{a_pct}%" + E + O + "物理伤害" + E + "，每第" + A + "3" + E + "下钳击造成" + phys("a2_dmg", "a2_ad") +
                  "。" + O + "百变铁手" + E + "：每次施放技能随机一个改件：火箭、护盾、" + A + "{p_as}%" + E + "攻速，" + A + "{p_tri}%" + E +
                  "中头奖强化本次技能。",
        "skill": "喷火" + A + "{q_dur}秒" + E + "，对前方扇形造成" + A + "{q_n}" + E + "次" + phys("q_dmg", "q_ad") + O + "物理伤害" + E +
                 "，期间减伤" + A + "{q_dr}%" + E + "。",
        "skill2": "射出铁拳，造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并击退；撞到身后的敌人则两人" + R + "眩晕{e_stun}秒" + E +
                  "。",
        "ult": "冲向目标连咬" + A + "{r_n}" + E + "口，每口" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "，" + R + "眩晕{r_stun}秒" + E +
               "并流血；目标生命低于" + A + "{r_exec}%" + E + "时直接咬死，再冲向下一个英雄。",
        "names": ("喷火器", "伸缩拳", "嚼一嚼"),
    },
    "zh-hant": {
        "name": "塞薇卡",
        "attack": "鐵拳造成" + ADi + O + "{a_pct}%" + E + O + "物理傷害" + E + "，每第" + A + "3" + E + "下鉗擊造成" + phys("a2_dmg", "a2_ad") +
                  "。" + O + "豪氣賭客" + E + "：每次施放技能隨機一個改件：火箭、護盾、" + A + "{p_as}%" + E + "攻速，" + A + "{p_tri}%" + E +
                  "中大獎強化本次技能。",
        "skill": "噴火" + A + "{q_dur}秒" + E + "，對前方扇形造成" + A + "{q_n}" + E + "次" + phys("q_dmg", "q_ad") + O + "物理傷害" + E +
                 "，期間減傷" + A + "{q_dr}%" + E + "。",
        "skill2": "射出鐵拳，造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並擊退；撞到身後的敵人則兩人" + R + "暈眩{e_stun}秒" + E +
                  "。",
        "ult": "衝向目標連咬" + A + "{r_n}" + E + "口，每口" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "，" + R + "暈眩{r_stun}秒" + E +
               "並流血；目標生命低於" + A + "{r_exec}%" + E + "時直接咬死，再衝向下一個英雄。",
        "names": ("火焰噴射器", "延伸重拳", "撕咬"),
    },
    "en": {
        "name": "Sevika",
        "attack": "Punches for " + ADi + O + "{a_pct}%" + E + " " + O + "physical damage" + E + "; every " + A + "3rd" + E +
                  " the claws clamp for " + phys("a2_dmg", "a2_ad") + ". " + O + "High Roller" + E + ": each skill rolls one of "
                  "Jinx's mods - rockets, a shield or " + A + "{p_as}%" + E + " attack speed; a " + A + "{p_tri}%" + E +
                  " jackpot empowers the cast.",
        "skill": "Flames for " + A + "{q_dur}s" + E + ": " + A + "{q_n}" + E + " waves into the cone ahead, each " +
                 phys("q_dmg", "q_ad") + " " + O + "physical damage" + E + "; she takes " + A + "{q_dr}%" + E + " less damage "
                 "meanwhile.",
        "skill2": "Fires her fist for " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E + ", knocking the target back; "
                  "knocked into an enemy, both are " + R + "stunned for {e_stun}s" + E + ".",
        "ult": "Dashes in and bites " + A + "{r_n}" + E + " times, each " + phys("r_dmg", "r_ad") + " " + O + "physical damage" + E +
               ", " + R + "stunning for {r_stun}s" + E + " and bleeding; under " + A + "{r_exec}%" + E + " health the target is "
               "executed and she dashes to the next champion.",
        "names": ("Flamethrower", "Extendo-Punch", "Chomp"),
    },
    "ko": {
        "name": "세비카",
        "attack": "주먹으로 " + ADi + O + "{a_pct}%" + E + " " + O + "물리 피해" + E + ", " + A + "3" + E + "번째마다 집게로 " +
                  phys("a2_dmg", "a2_ad") + ". " + O + "도박꾼" + E + ": 스킬마다 개조 하나를 무작위로: 로켓, 보호막, 공격 속도 " + A +
                  "{p_as}%" + E + "; " + A + "{p_tri}%" + E + " 대박이면 이번 스킬 강화.",
        "skill": A + "{q_dur}초" + E + " 동안 화염 방사: 앞쪽 부채꼴에 " + A + "{q_n}" + E + "번 각각 " + phys("q_dmg", "q_ad") + " " + O +
                 "물리 피해" + E + ", 그동안 받는 피해 " + A + "{q_dr}%" + E + " 감소.",
        "skill2": "주먹을 날려 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 넉백; 뒤의 적과 부딪히면 둘 다 " + R +
                  "{e_stun}초 기절" + E + ".",
        "ult": "돌진해 " + A + "{r_n}" + E + "번 물어 각각 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + ", " + R +
               "{r_stun}초 기절" + E + "과 출혈; 체력 " + A + "{r_exec}%" + E + " 미만이면 처형하고 다음 챔피언에게 돌진.",
        "names": ("화염 방사기", "늘어나는 펀치", "깨물기"),
    },
    "ja": {
        "name": "セヴィカ",
        "attack": "鉄拳で" + ADi + O + "{a_pct}%" + E + "の" + O + "物理ダメージ" + E + "、" + A + "3" + E + "回ごとに鉤爪で" +
                  phys("a2_dmg", "a2_ad") + "。" + O + "ギャンブラー" + E + "：スキルごとに改造を1つ：ロケット、シールド、攻撃速度" + A +
                  "{p_as}%" + E + "；" + A + "{p_tri}%" + E + "の大当たりでそのスキル強化。",
        "skill": A + "{q_dur}秒" + E + "間火炎放射：前方の扇形に" + A + "{q_n}" + E + "回、それぞれ" + phys("q_dmg", "q_ad") + "の" + O +
                 "物理ダメージ" + E + "、その間被ダメージ" + A + "{q_dr}%" + E + "軽減。",
        "skill2": "拳を飛ばし" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "とノックバック；後ろの敵にぶつかると2人とも" + R +
                  "{e_stun}秒スタン" + E + "。",
        "ult": "突進して" + A + "{r_n}" + E + "回噛みつき、それぞれ" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "、" + R +
               "{r_stun}秒スタン" + E + "と出血；体力" + A + "{r_exec}%" + E + "未満なら処刑し、次のチャンピオンへ突進。",
        "names": ("火炎放射器", "エクステンドパンチ", "咬み砕き"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_sevika's sfx / tsfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.4), ("a2", 0.45), ("a2_hit", 0.5),
    ("p", 0.45), ("p_rocket", 0.35), ("p_rocket_hit", 0.35), ("p_shield", 0.45), ("p_shimmer", 0.45),
    ("p_jackpot", 0.6), ("p_jackpot_fx", 0.5),
    ("q", 0.45), ("q_fire", 0.5), ("q_loop", 0.45),
    ("e", 0.5), ("e_launch", 0.5), ("e_hit", 0.6), ("e_stun", 0.55),
    ("r", 0.5), ("r_vo", 0.6), ("r_dash", 0.5), ("r_hit", 0.6), ("r_kill", 0.65))}
# the sounds tft.dll plays itself (addons/tft/src/sevika.rs: the mods, the fist, the bites, the re-dash)
DLL_SOUNDS = {f"{ID}_{x}" for x in ("p_rocket", "p_rocket_hit", "p_shield", "p_shimmer", "p_jackpot", "p_jackpot_fx",
                                     "e_launch", "e_hit", "e_stun", "r_dash", "r_hit", "r_kill")}


def values(p):
    v = {k: p[k] for k in ("a_pct", "a2_dmg", "a2_ad", "p_as", "p_tri", "q_n", "q_dmg", "q_ad", "q_dr", "e_dmg", "e_ad",
                           "r_n", "r_dmg", "r_ad", "r_exec")}
    for k in ("q_dur", "e_stun", "r_stun"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_sevika.py")
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
