"""Baron Nashor's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_baronnashor.P.

    python tools/kit/setup_baronnashor.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_thex.py writes for T-Hex: mod.mod_info (VERSION, the
pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys
sorted), text/champion.i18n (tft_baronnashor in every language, description + skill_name),
sound/sfx/tft_baronnashor_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 16's own (CommunityDragon cdragon/tft/<locale>.json, TFT16_BaronNashor, 2026-11-03): zh_CN 纳什男爵, zh_TW
巴龍納什, en Baron Nashor, ja バロンナッシャー, ko 내셔 남작; its ability Wrath of the Void = 虚空之怒 (zh_TW 虛空之怒, ja ヴォイドの
激憤, ko 공허의 분노). Void Rift (虚空裂隙, after TFT's rift and its tentacles), Corrosive Bite (腐蚀撕咬), Corrosive Breath
(腐蚀吐息, League's acid) and Burrow Strike (钻地突袭, TFT's burrowing dash) are ours (the user's pick, plan A 打野).
The texts are the rules it plays: the tentacles in tft.dll (addons/tft/src/baronnashor.rs), the rest the data (the bite
and its line, the breath and its acid, the burrow and the knock-up, the spike slam and the acid barrage).
Sounds: tools/lol/extract_baronnashor.py's clips in tft/sound/sfx/tft_baronnashor_sfx_*.wav (git-ignored) - its own
set-16 bite, burrow, unburrow, strike, spike slam and acid balls, the Rift Baron's tentacle knock-up, acid spit, death
breath, acid landing, spawn roar and void suck. A clip name never equals an event name (vo-clip-names rule): event
tft_baronnashor_<x> plays clip tft_baronnashor_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_baronnashor import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# ... the Rift Herald 0.40 (PR #663), T-Hex 0.41, the voice lines 0.42-0.45, the log fixes 0.46 (PR #674), Baron Nashor 0.47
VERSION = "0.47.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from its soles' point, up negative): the face point on its middle eye (ppu_restyle's face_to:
# hd/idle.png's eye (37.5, 30) from the pivot (28, 94) at PPU 2.04); the centre by League's rule (tools/art/
# bp_card_audit.py --centers, 2026-11-03: its solid top 45.3 px up -> -19); the ban/pick card by its rule (y = -39 - top:
# the lo_idle reaches 35.3 px over its centre -> -4)
VIEW = {"face": {"x": 5, "y": -31}, "center": {"x": 0, "y": -19}, "banpick_center": {"x": 0, "y": -4}}


def phys(d, r):
    """d + r% AD, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "纳什男爵",
        "attack": "撕咬目标，并对从自己穿过目标的一条直线上的敌人造成" + ADi + O + "{a_line}%" + E + O + "物理伤害" + E + "。" + O + "虚空裂隙" + E +
                  "：战斗中每" + A + "{p_every}秒" + E + "，在附近随机一名敌方英雄脚下喷出触手，造成" + phys("p_dmg", "p_ad") + O + "物理伤害" + E +
                  "并" + R + "击飞{p_up}秒" + E + "。",
        "skill": "向前方喷出扇形酸液，造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "，并使敌人" + R + "护甲和魔抗降低{q_shred}%" + E + "（" + A +
                 "{q_t}秒" + E + "）。",
        "skill2": "钻入地下冲向目标（期间免疫控制），破土而出，对周围敌人造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R +
                  "击飞{e_up}秒" + E + "。",
        "ult": "施放期间免疫控制。猛击地面竖起尖刺，对周围敌人造成" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "；随后连续吐出" + A + "{r_n}" + E +
               "团酸液，落在附近随机敌人身上，每团造成" + phys("r_mdmg", "r_mad") + O + "物理伤害" + E + "并腐蚀护甲和魔抗。",
        "names": ("腐蚀吐息", "钻地突袭", "虚空之怒"),
    },
    "zh-hant": {
        "name": "巴龍納什",
        "attack": "撕咬目標，並對從自身穿過目標的一條直線上的敵軍造成" + ADi + O + "{a_line}%" + E + O + "物理傷害" + E + "。" + O + "虛空裂隙" + E +
                  "：戰鬥中每" + A + "{p_every}秒" + E + "，在附近隨機一名敵方英雄腳下噴出觸手，造成" + phys("p_dmg", "p_ad") + O + "物理傷害" + E +
                  "並" + R + "擊飛{p_up}秒" + E + "。",
        "skill": "向前方噴出扇形酸液，造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "，並使敵軍" + R + "護甲和魔抗降低{q_shred}%" + E + "（" + A +
                 "{q_t}秒" + E + "）。",
        "skill2": "鑽入地下衝向目標（期間免疫控制），破土而出，對周圍敵軍造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R +
                  "擊飛{e_up}秒" + E + "。",
        "ult": "施放期間免疫控制。猛擊地面豎起尖刺，對周圍敵軍造成" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "；隨後連續吐出" + A + "{r_n}" + E +
               "團酸液，落在附近隨機敵軍身上，每團造成" + phys("r_mdmg", "r_mad") + O + "物理傷害" + E + "並腐蝕護甲和魔抗。",
        "names": ("腐蝕吐息", "鑽地突襲", "虛空之怒"),
    },
    "en": {
        "name": "Baron Nashor",
        "attack": "Bites the target and deals " + ADi + O + "{a_line}%" + E + " " + O + "physical damage" + E + " to every enemy in a line "
                  "through it. " + O + "Void Rift" + E + ": in a fight, every " + A + "{p_every}s" + E + " a tentacle bursts up under a random "
                  "nearby enemy champion for " + phys("p_dmg", "p_ad") + " " + O + "physical damage" + E + ", " + R + "knocking it up for "
                  "{p_up}s" + E + ".",
        "skill": "Breathes a cone of acid ahead for " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E + ", " + R + "lowering armor and "
                 "magic resist by {q_shred}%" + E + " for " + A + "{q_t}s" + E + ".",
        "skill2": "Burrows to the target (immune to crowd control) and bursts out, dealing " + phys("e_dmg", "e_ad") + " " + O +
                  "physical damage" + E + " around it and " + R + "knocking up for {e_up}s" + E + ".",
        "ult": "Immune to crowd control while casting. Slams the ground, raising spikes for " + phys("r_dmg", "r_ad") + " " + O +
               "physical damage" + E + " around it, then spits " + A + "{r_n}" + E + " acid balls at random nearby enemies, each " +
               phys("r_mdmg", "r_mad") + " " + O + "physical damage" + E + " and corroding armor and magic resist.",
        "names": ("Corrosive Breath", "Burrow Strike", "Wrath of the Void"),
    },
    "ko": {
        "name": "내셔 남작",
        "attack": "대상을 물어뜯고, 대상을 지나는 직선 위의 모든 적에게 " + ADi + O + "{a_line}%" + E + " " + O + "물리 피해" + E + ". " + O + "공허 균열" +
                  E + ": 전투 중 " + A + "{p_every}초" + E + "마다 주변 무작위 적 챔피언 아래에서 촉수가 솟아 " + phys("p_dmg", "p_ad") + " " + O +
                  "물리 피해" + E + ", " + R + "{p_up}초 에어본" + E + ".",
        "skill": "앞쪽 부채꼴로 산성액을 뿜어 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + ", " + A + "{q_t}초" + E + " 동안 " + R + "방어력과 "
                 "마법 저항력 {q_shred}% 감소" + E + ".",
        "skill2": "땅속으로 파고들어 대상에게 이동(군중 제어 면역)한 뒤 솟아올라 주변 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E +
                  ", " + R + "{e_up}초 에어본" + E + ".",
        "ult": "시전 중 군중 제어 면역. 땅을 내리쳐 가시를 솟게 해 주변 적에게 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + "; 이후 주변 "
               "무작위 적에게 산성 덩어리 " + A + "{r_n}" + E + "개를 뱉어 각각 " + phys("r_mdmg", "r_mad") + " " + O + "물리 피해" + E + "와 "
               "방어력·마법 저항력 부식.",
        "names": ("부식성 숨결", "땅굴 습격", "공허의 분노"),
    },
    "ja": {
        "name": "バロンナッシャー",
        "attack": "対象に噛みつき、対象を貫く直線上の敵すべてに" + ADi + O + "{a_line}%" + E + "の" + O + "物理ダメージ" + E + "。" + O + "ヴォイドの裂け目" +
                  E + "：戦闘中" + A + "{p_every}秒" + E + "ごとに近くのランダムな敵チャンピオンの足元から触手が突き出し、" + phys("p_dmg", "p_ad") +
                  "の" + O + "物理ダメージ" + E + "と" + R + "{p_up}秒のノックアップ" + E + "。",
        "skill": "前方扇状に酸を吐き、" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "を与え、" + R + "物理防御と魔法防御を{q_shred}%低下" +
                 E + "（" + A + "{q_t}秒" + E + "）。",
        "skill2": "地中に潜って対象へ移動し（行動妨害無効）、地上へ飛び出して周囲の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" +
                  R + "{e_up}秒のノックアップ" + E + "。",
        "ult": "詠唱中は行動妨害無効。地面を叩いてトゲを突き出し、周囲の敵に" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "。その後、"
               "近くのランダムな敵へ酸の塊を" + A + "{r_n}" + E + "個吐き、各" + phys("r_mdmg", "r_mad") + "の" + O + "物理ダメージ" + E + "と防御の腐食。",
        "names": ("腐食のブレス", "地中強襲", "ヴォイドの激憤"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_baronnashor's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.35),
    ("p", 0.45),
    ("q", 0.4), ("q_breath", 0.45), ("q_hit", 0.35),
    ("e", 0.45), ("e_up", 0.5), ("e_hit", 0.45),
    ("r", 0.55), ("r_roar", 0.5), ("r_acid", 0.3), ("r_hit", 0.3),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/baronnashor.rs: the tentacles and the death)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("a_line", "p_dmg", "p_ad", "q_dmg", "q_ad", "q_shred", "e_dmg", "e_ad", "r_dmg", "r_ad", "r_n",
                           "r_mdmg", "r_mad")}
    for k in ("p_every", "p_up", "q_t", "e_up"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_baronnashor.py")
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
    mi["last_updated"] = "2026-11-03"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
