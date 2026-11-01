"""The Scuttle Crab's text (5 languages), sound_info files and the tft pack's shared files, numbers from
build_scuttlecrab.P.

    python tools/kit/setup_scuttlecrab.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_meepsie.py writes for Meepsie: mod.mod_info
(VERSION, the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for
tft.dll, the keys sorted), text/champion.i18n (tft_scuttlecrab in every language, description + skill_name),
sound/sfx/tft_scuttlecrab_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 18's own (CommunityDragon cdragon/tft/<locale>.json, DA_Scuttlecrab18, 2026-11-01): zh_CN 峡谷迅捷蟹 (the
user's 迅捷蟹 in game), zh_TW 河蟹, ja スカトルクラブ, ko 바위 게, en Scuttle Crab (the client's "Scuttlecrab" split as League
writes it); its ability Can You Dig It? = 这种快乐你懂吗？ in zh_CN, but the user's kit names the ult 你挖得动吗？ (zh_TW 你挖得動嗎？,
ja 掘り起こせるか？, ko 팔 수 있겠어?). Green Buff (绿霸符, TFT's trait buff), Crab Dance (螃蟹舞), Speed Shrine (疾行神龛) and
Shell Shield (蟹壳护盾) are our own (the user's pick, plan A 「河道守护」).
The texts are the rules it plays with tft.dll (addons/tft/src/scuttlecrab.rs): the Green Buff on whoever falls low near
it, the shell bursting when its shield is spent.
Sounds: tools/lol/extract_scuttlecrab.py's clips in tft/sound/sfx/tft_scuttlecrab_sfx_*.wav (git-ignored) - League's
river crab (its dance, its speed shrine, its shield breaking, the stun, climbing out, its death), Rek'Sai (digging in,
healing under the ground, the knock-up), Rammus (curling up, the shell's bump), Soraka's heal and Sona's haste.
A clip name never equals an event name (vo-clip-names rule): event tft_scuttlecrab_<x> plays clip
tft_scuttlecrab_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_scuttlecrab import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29, the Elder Dragon 0.30, Meepsie 0.31, Murk Wolf 0.32, the Scuttle Crab 0.33
VERSION = "0.33.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point on its stone face plate (the design's plate
# at column 82, row 49 of 80 at PPU 2.667: 12 over the ground, 9 ahead of its standing point, the design's pivot column
# 57 - ppu_restyle's face_to); the centre in its body (half its 30 px); the ban/pick card -15 (bp_card_audit.card
# mocks: at -12 its legs went under the card's edge)
VIEW = {"face": {"x": 9, "y": -12}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -15}}


def mag(d, r):
    """base + AP ratio (magic damage, a heal, a shield)."""
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def phys(d, r):
    """base + AD ratio, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "迅捷蟹",
        "attack": "跳一段螃蟹舞，踩中身边所有敌人，造成" + AD + O + "物理伤害" + E + "。" + O + "绿霸符" + E + "：附近的友方英雄生命低于" + A +
                  "{p_low}%" + E + "时回复" + A + "{p_pct}%" + E + "最大生命（每人" + A + "{p_cd}秒" + E + "一次）。",
        "skill": "在脚下放下神龛（" + A + "{q_t}秒" + E + "），水花使周围敌人受到" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并减速" + R +
                 "{q_slow}%" + E + "；神龛里的友方英雄移速" + A + "+{q_ms}%" + E + "、攻速" + A + "+{q_as}%" + E + "。",
        "skill2": "缩进壳里，获得" + mag("e_sh", "e_sh_ap") + "护盾（" + A + "{e_t}秒" + E + "）。护盾打光或到时间时蟹壳碎裂：周围敌人受到" +
                  mag("e_dmg", "e_dmg_ap") + M + "魔法伤害" + E + "、" + R + "眩晕" + E + A + "{e_stun}秒" + E + "并减速" + R + "{e_slow}%" + E + "。",
        "ult": "钻入地下" + A + "{r_t}秒" + E + "：受到的伤害降低" + A + "{r_red}%" + E + "、免疫控制，持续回复" + mag("r_heal", "r_heal_ap") +
               "生命；然后钻出地面，周围敌人受到" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "并被" + R + "击飞" + E + A + "{r_up}秒" + E + "。",
        "names": ("疾行神龛", "蟹壳护盾", "你挖得动吗？"),
    },
    "zh-hant": {
        "name": "河蟹",
        "attack": "跳一段螃蟹舞，踩中身邊所有敵軍，造成" + AD + O + "物理傷害" + E + "。" + O + "綠色增益" + E + "：附近的友方英雄生命低於" + A +
                  "{p_low}%" + E + "時回復" + A + "{p_pct}%" + E + "最大生命（每人" + A + "{p_cd}秒" + E + "一次）。",
        "skill": "在腳下放下神龕（" + A + "{q_t}秒" + E + "），水花使周圍敵軍受到" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並緩速" + R +
                 "{q_slow}%" + E + "；神龕裡的友方英雄移速" + A + "+{q_ms}%" + E + "、攻速" + A + "+{q_as}%" + E + "。",
        "skill2": "縮進殼裡，獲得" + mag("e_sh", "e_sh_ap") + "護盾（" + A + "{e_t}秒" + E + "）。護盾被打破或時間到時蟹殼碎裂：周圍敵軍受到" +
                  mag("e_dmg", "e_dmg_ap") + M + "魔法傷害" + E + "、" + R + "暈眩" + E + A + "{e_stun}秒" + E + "並緩速" + R + "{e_slow}%" + E + "。",
        "ult": "鑽入地下" + A + "{r_t}秒" + E + "：受到的傷害降低" + A + "{r_red}%" + E + "、免疫控場，持續回復" + mag("r_heal", "r_heal_ap") +
               "生命；接著鑽出地面，周圍敵軍受到" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "並被" + R + "擊飛" + E + A + "{r_up}秒" + E + "。",
        "names": ("疾行神龕", "蟹殼護盾", "你挖得動嗎？"),
    },
    "en": {
        "name": "Scuttle Crab",
        "attack": "Dances, stomping every enemy beside it for " + AD + " " + O + "physical damage" + E + ". " + O + "Green Buff" + E +
                  ": a nearby allied champion falling under " + A + "{p_low}%" + E + " health restores " + A + "{p_pct}%" + E +
                  " of its max health (once every " + A + "{p_cd}s" + E + " each).",
        "skill": "Raises a speed shrine at its feet for " + A + "{q_t}s" + E + ": its splash deals " + mag("q_dmg", "q_ap") + " " + M +
                 "magic damage" + E + " to enemies around and slows them " + R + "{q_slow}%" + E + "; allied champions in it gain " + A +
                 "{q_ms}%" + E + " move speed and " + A + "{q_as}%" + E + " attack speed.",
        "skill2": "Pulls into its shell for a " + mag("e_sh", "e_sh_ap") + " shield (" + A + "{e_t}s" + E + "). When the shield breaks or "
                  "runs out, the shell bursts: enemies around take " + mag("e_dmg", "e_dmg_ap") + " " + M + "magic damage" + E + ", are " + R +
                  "stunned" + E + " " + A + "{e_stun}s" + E + " and slowed " + R + "{e_slow}%" + E + ".",
        "ult": "Burrows for " + A + "{r_t}s" + E + ", taking " + A + "{r_red}%" + E + " less damage, immune to crowd control and healing " +
               mag("r_heal", "r_heal_ap") + "; then bursts out: enemies around take " + phys("r_dmg", "r_ad") + " " + O +
               "physical damage" + E + " and are " + R + "knocked up" + E + " " + A + "{r_up}s" + E + ".",
        "names": ("Speed Shrine", "Shell Shield", "Can You Dig It?"),
    },
    "ko": {
        "name": "바위 게",
        "attack": "게 춤을 춰 주변 모든 적에게 " + AD + " " + O + "물리 피해" + E + ". " + O + "초록 버프" + E + ": 주변 아군 챔피언의 체력이 " + A +
                  "{p_low}%" + E + " 아래로 떨어지면 최대 체력의 " + A + "{p_pct}%" + E + " 회복(각자 " + A + "{p_cd}초" + E + "마다 한 번).",
        "skill": "발밑에 신속의 성소를 세워(" + A + "{q_t}초" + E + ") 물보라로 주변 적에게 " + mag("q_dmg", "q_ap") + " " + M + "마법 피해" + E + ", " +
                 R + "{q_slow}%" + E + " 둔화. 성소 안의 아군 챔피언은 이동 속도 " + A + "+{q_ms}%" + E + ", 공격 속도 " + A + "+{q_as}%" + E + ".",
        "skill2": "껍데기 속에 숨어 " + mag("e_sh", "e_sh_ap") + " 보호막(" + A + "{e_t}초" + E + "). 보호막이 깨지거나 끝나면 껍데기가 터져 주변 적에게 " +
                  mag("e_dmg", "e_dmg_ap") + " " + M + "마법 피해" + E + ", " + R + "기절" + E + " " + A + "{e_stun}초" + E + ", " + R + "{e_slow}%" + E +
                  " 둔화.",
        "ult": "땅속으로 " + A + "{r_t}초" + E + " 파고들어 받는 피해 " + A + "{r_red}%" + E + " 감소, 군중 제어 면역, " + mag("r_heal", "r_heal_ap") +
               " 회복. 이후 튀어나와 주변 적에게 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + ", " + R + "에어본" + E + " " + A + "{r_up}초" +
               E + ".",
        "names": ("신속의 성소", "껍데기 보호막", "팔 수 있겠어?"),
    },
    "ja": {
        "name": "スカトルクラブ",
        "attack": "カニダンスで周囲の全ての敵に" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "グリーンバフ" + E + "：近くの味方チャンピオンの体力が" +
                  A + "{p_low}%" + E + "を下回ると最大体力の" + A + "{p_pct}%" + E + "を回復（各自" + A + "{p_cd}秒" + E + "に1回）。",
        "skill": "足元に祠を置き（" + A + "{q_t}秒" + E + "）、水しぶきで周囲の敵に" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" + R +
                 "{q_slow}%" + E + "スロウ。祠の中の味方チャンピオンは移動速度" + A + "+{q_ms}%" + E + "、攻撃速度" + A + "+{q_as}%" + E + "。",
        "skill2": "甲羅にこもり" + mag("e_sh", "e_sh_ap") + "のシールド（" + A + "{e_t}秒" + E + "）。シールドが割れるか切れると甲羅が弾け、周囲の敵に" +
                  mag("e_dmg", "e_dmg_ap") + "の" + M + "魔法ダメージ" + E + "、" + R + "スタン" + E + A + "{e_stun}秒" + E + "、" + R + "{e_slow}%" + E +
                  "スロウ。",
        "ult": A + "{r_t}秒" + E + "地中に潜り、受けるダメージ" + A + "-{r_red}%" + E + "、行動妨害無効、" + mag("r_heal", "r_heal_ap") +
               "回復。その後飛び出し、周囲の敵に" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "ノックアップ" + E + A +
               "{r_up}秒" + E + "。",
        "names": ("疾走の祠", "甲羅の盾", "掘り起こせるか？"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_scuttlecrab's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.35), ("a_hit", 0.3), ("p", 0.35),
    ("q", 0.45), ("q_buff", 0.3),
    ("e", 0.45), ("e_break", 0.5), ("e_slow", 0.35),
    ("r", 0.5), ("r_heal", 0.35), ("r_up", 0.5), ("r_hit", 0.5),
    ("d", 0.5))}
# the sounds tft.dll plays itself (addons/tft/src/scuttlecrab.rs: the Green Buff's heal, the shell bursting and its
# shards slowing, its death)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_e_break", f"{ID}_e_slow", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("p_low", "p_pct", "q_dmg", "q_ap", "q_slow", "q_ms", "q_as", "e_sh", "e_sh_ap", "e_dmg",
                           "e_dmg_ap", "e_slow", "r_red", "r_heal", "r_heal_ap", "r_dmg", "r_ad")}
    for k in ("p_cd", "q_t", "e_t", "e_stun", "r_t", "r_up"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_scuttlecrab.py")
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
