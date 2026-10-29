"""Steb's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_steb.P.

    python tools/kit/setup_steb.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_sevika.py writes for Sevika: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_steb in every language, description + skill_name), sound/sfx/tft_steb_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX
and the texts themselves.
Names: TFT set 13's own (CommunityDragon cdragon/tft/<locale>.json, TFT13_Fish, 2026-10-29): zh_CN 斯特卜, zh_TW 史提布,
ja ステブ, ko 스텝, en Steb; his spell Field Medicine = 战地医疗 / 戰地醫療 / 野戦医療 / 야전 의료 (Q, and the passive it carries);
Wanted from his trait Enforcer's mark (执法官 / 執法者 / 執行官 / 집행자: 通缉 / 通緝 / 指名手配 / 현상수배); Medic's Pack (医疗背包) and
Twin Batons (双警棍连击) are our own (the user's pick, plan A 「战地军医」). The texts are the rules he plays with tft.dll
(addons/tft/src/steb.rs): the heal passed on to the nearest allies, the healthiest enemy marked, the bounty.
Sounds: tools/lol/extract_steb.py's clips in tft/sound/sfx/tft_steb_sfx_*.wav (git-ignored) - his own set-13 TFT sounds
(the baton swings and hits, the crit for the Wanted call and mark, the spell's cast and hit, his voice), Soraka's Astral
Infusion (the shared heal) and Wish (the pack's heal), Sona's Aria (the dose), Caitlyn's Ace in the Hole lock-on (the
mark), Jinx's Get Excited! (the bounty), Taric's Cosmic Radiance (the pack opened) and Lux's Prismatic Barrier (its
shields). A clip name never equals an event name (vo-clip-names rule): event tft_steb_<x> plays clip tft_steb_sfx_<x>.
package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_steb import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18
VERSION = "0.18.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from his soles' point, up negative): the face point between his eyes (the design's eye row 18
# of 106 at PPU 2.6: 34 over the ground; 3 ahead of his standing column, ppu_restyle's face_to); the centre in his body;
# the ban/pick card by bp_card_audit.py's rule (-39 less the idle's top -30.0, its frames()/reach() on tft/: his head 1
# game px under the card's top)
VIEW = {"face": {"x": 3, "y": -34}, "center": {"x": 2, "y": -19}, "banpick_center": {"x": 2, "y": -9}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def heal(d, r):
    return f"{A}{{{d}}}{E} + {APi}{A}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "斯特卜",
        "attack": "双警棍轮流打击，造成" + AD + O + "物理伤害" + E + "。" + O + "战地医疗" + E + "：自己受到治疗时，最近的" + A + "{p_n}" + E +
                  "名友方英雄也回复该治疗量的" + A + "{p_share}%" + E + "。",
        "skill": "给自己打一针，回复" + heal("q_heal", "q_heal_ap") + "生命，再重击目标造成" + mag("q_dmg", "q_ap") + "魔法伤害并" + R +
                 "眩晕{q_stun}秒" + E + "。",
        "skill2": "通缉附近生命最高的敌方英雄" + A + "{e_t}秒" + E + "：它受到的伤害提高" + A + "{e_amp}%" + E + "；它在通缉中阵亡时，自己和附近友方攻速提高" +
                  A + "{e_as}%" + E + "（" + A + "{e_as_t}秒" + E + "）。",
        "ult": "打开医疗背包：自己和周围友方英雄获得" + mag("r_sh", "r_sh_ap") + "的护盾（" + A + "{r_sh_t}秒" + E + "），自己减伤" + A +
               "{r_red}%" + E + "；之后每" + A + "{r_every}秒" + E + "为周围友方回复" + heal("r_hot", "r_hot_ap") + "生命，共" + A + "{r_n}" + E + "次。",
        "names": ("战地医疗", "通缉令", "医疗背包"),
    },
    "zh-hant": {
        "name": "史提布",
        "attack": "雙警棍輪流打擊，造成" + AD + O + "物理傷害" + E + "。" + O + "戰地醫療" + E + "：自己受到治療時，最近的" + A + "{p_n}" + E +
                  "名友方英雄也回復該治療量的" + A + "{p_share}%" + E + "。",
        "skill": "給自己打一針，回復" + heal("q_heal", "q_heal_ap") + "生命，再重擊目標造成" + mag("q_dmg", "q_ap") + "魔法傷害並" + R +
                 "暈眩{q_stun}秒" + E + "。",
        "skill2": "通緝附近生命最高的敵方英雄" + A + "{e_t}秒" + E + "：它受到的傷害提高" + A + "{e_amp}%" + E + "；它在通緝中陣亡時，自己和附近友方攻速提高" +
                  A + "{e_as}%" + E + "（" + A + "{e_as_t}秒" + E + "）。",
        "ult": "打開醫療背包：自己和周圍友方英雄獲得" + mag("r_sh", "r_sh_ap") + "的護盾（" + A + "{r_sh_t}秒" + E + "），自己減傷" + A +
               "{r_red}%" + E + "；之後每" + A + "{r_every}秒" + E + "為周圍友方回復" + heal("r_hot", "r_hot_ap") + "生命，共" + A + "{r_n}" + E + "次。",
        "names": ("戰地醫療", "通緝令", "醫療背包"),
    },
    "en": {
        "name": "Steb",
        "attack": "Strikes with his batons in turn for " + AD + " " + O + "physical damage" + E + ". " + O + "Field Medicine" + E +
                  ": whenever he is healed, the " + A + "{p_n}" + E + " nearest allied champions heal " + A + "{p_share}%" + E +
                  " of it too.",
        "skill": "Doses himself for " + heal("q_heal", "q_heal_ap") + " health, then strikes the target for " + mag("q_dmg", "q_ap") +
                 " " + M + "magic damage" + E + ", " + R + "stunning for {q_stun}s" + E + ".",
        "skill2": "Marks the enemy champion with the most health nearby as Wanted for " + A + "{e_t}s" + E + ": it takes " + A +
                  "{e_amp}%" + E + " more damage; if it dies while Wanted, he and nearby allies gain " + A + "{e_as}%" + E +
                  " attack speed for " + A + "{e_as_t}s" + E + ".",
        "ult": "Opens his medic's pack: he and nearby allied champions gain a " + mag("r_sh", "r_sh_ap") + " shield for " + A +
               "{r_sh_t}s" + E + " and he takes " + A + "{r_red}%" + E + " less damage; then every " + A + "{r_every}s" + E +
               ", " + A + "{r_n}" + E + " times, nearby allies heal " + heal("r_hot", "r_hot_ap") + ".",
        "names": ("Field Medicine", "Wanted!", "Medic's Pack"),
    },
    "ko": {
        "name": "스텝",
        "attack": "두 진압봉으로 번갈아 " + AD + " " + O + "물리 피해" + E + ". " + O + "야전 의료" + E + ": 회복을 받으면 가장 가까운 아군 챔피언 " + A +
                  "{p_n}" + E + "명도 그 " + A + "{p_share}%" + E + "만큼 회복.",
        "skill": "스스로 주사해 체력 " + heal("q_heal", "q_heal_ap") + " 회복, 대상을 내려쳐 " + mag("q_dmg", "q_ap") + " " + M + "마법 피해" + E +
                 "와 " + R + "{q_stun}초 기절" + E + ".",
        "skill2": "근처에서 체력이 가장 많은 적 챔피언을 " + A + "{e_t}초" + E + " 동안 현상수배: 받는 피해 " + A + "{e_amp}%" + E +
                  " 증가; 수배 중 사망하면 자신과 근처 아군 공격 속도 " + A + "{e_as}%" + E + " 증가(" + A + "{e_as_t}초" + E + ").",
        "ult": "의료 배낭을 열어 자신과 주변 아군 챔피언에게 " + mag("r_sh", "r_sh_ap") + " 보호막(" + A + "{r_sh_t}초" + E + "), 자신은 받는 피해 " +
               A + "{r_red}%" + E + " 감소; 이후 " + A + "{r_every}초" + E + "마다 " + A + "{r_n}" + E + "번 주변 아군 체력 " +
               heal("r_hot", "r_hot_ap") + " 회복.",
        "names": ("야전 의료", "현상수배", "의료 배낭"),
    },
    "ja": {
        "name": "ステブ",
        "attack": "2本の警棒で交互に" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "野戦医療" + E + "：回復を受けると、最も近い味方チャンピオン" + A +
                  "{p_n}" + E + "体もその" + A + "{p_share}%" + E + "回復。",
        "skill": "自分に注射して体力を" + heal("q_heal", "q_heal_ap") + "回復し、対象を殴って" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E +
                 "と" + R + "{q_stun}秒スタン" + E + "。",
        "skill2": "近くで最も体力の多い敵チャンピオンを" + A + "{e_t}秒" + E + "指名手配：被ダメージ" + A + "{e_amp}%" + E +
                  "増加；手配中に倒れると自分と近くの味方の攻撃速度" + A + "{e_as}%" + E + "増加（" + A + "{e_as_t}秒" + E + "）。",
        "ult": "救急バッグを開き、自分と周囲の味方チャンピオンに" + mag("r_sh", "r_sh_ap") + "のシールド（" + A + "{r_sh_t}秒" + E + "）、自分の被ダメージ" +
               A + "{r_red}%" + E + "軽減；その後" + A + "{r_every}秒" + E + "ごとに" + A + "{r_n}" + E + "回、周囲の味方の体力を" +
               heal("r_hot", "r_hot_ap") + "回復。",
        "names": ("野戦医療", "指名手配", "救急バッグ"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_steb's sfx / tsfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.45), ("a2", 0.4), ("a2_hit", 0.45),
    ("p", 0.35),
    ("q", 0.45), ("q_vo", 0.6), ("q_heal", 0.4), ("q_hit", 0.6),
    ("e", 0.45), ("e_mark", 0.5), ("e_hit", 0.5), ("e_kill", 0.5),
    ("r", 0.5), ("r_shield", 0.45), ("r_heal", 0.45))}
# the sounds tft.dll plays itself (addons/tft/src/steb.rs: the shared heal, the mark, the bounty)
DLL_SOUNDS = {f"{ID}_{x}" for x in ("p", "e_hit", "e_kill")}


def values(p):
    v = {k: p[k] for k in ("p_n", "p_share", "q_heal", "q_heal_ap", "q_dmg", "q_ap", "e_amp", "e_as", "r_sh", "r_sh_ap",
                           "r_red", "r_n", "r_hot", "r_hot_ap")}
    for k in ("q_stun", "e_t", "e_as_t", "r_sh_t", "r_every"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_steb.py")
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
    mi["contains_code"], mi["mod_type"] = True, "native"     # tft.dll (addons/tft): his rules the data cannot play
    mi["last_updated"] = "2026-10-29"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
