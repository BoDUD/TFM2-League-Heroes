"""Maddie's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_maddie.P.

    python tools/kit/setup_maddie.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft): mod.mod_info (VERSION, the pack's description:
setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys sorted,
setup_alune.py's way), text/champion.i18n (tft_maddie in every language, description + skill_name),
sound/sfx/tft_maddie_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 13's own (CommunityDragon latest cdragon/tft/<locale>.json, TFT13_Shooter, 2026-10-27): zh_CN 麦迪,
zh_TW 梅狄, ja マディー, ko 매디; Fan the Hammer = 连拨击锤 / 旋風鎚 / ファニングショット / 탄환 세례; her trait Sniper = 狙神 /
狙擊專家 / スナイパー / 저격수 names the passive. Wanted (通缉令, after her other trait Enforcer's Wanted mark) and Enforcer's
Snipe (执法狙杀) are our own (TFT has one ability; the user's pick, plan A 「狙神·通缉」). The texts are the rules she plays
with tft.dll (addons/tft/src/maddie.rs): the Sniper bonus by distance, the bullets at the farthest enemy, the Wanted
enemy with the most health and its bounty, the snipe at the weakest.
Sounds: tools/lol/extract_maddie.py's clips in tft/sound/sfx/tft_maddie_sfx_*.wav (git-ignored) - her own set-13 TFT
sounds (the rifle's shot, hit, reload, crit hit and spell, her voice on the ult) and Caitlyn's Ace in the Hole (the
lock-on for the Wanted mark and the aim, its shot and its hit for the snipe). A clip name never equals an event name
(vo-clip-names rule): event tft_maddie_<x> plays clip tft_maddie_sfx_<x>. package_mod moves the clips to sound/bgm/ at
install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_maddie import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
VERSION = "0.6.0"      # Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6: the next free one at merge
ADi, TOOLTIP_MAX = pack.ADi, pack.TOOLTIP_MAX
O, A, R, E = pack.O, pack.A, pack.R, pack.E
# champion_view (game px from her soles' point, up negative): the face point between her eyes (the design's eye row 10.5
# of 57 at PPU 1.5: 31 over the ground, 1 ahead of her standing column); the centre in her body; the ban/pick card by
# bp_card_audit.py's rule (y = -39 - top: her lo_idle reaches 28.0 over its centre -> -11)
VIEW = {"face": {"x": 1, "y": -31}, "center": {"x": 0, "y": -19}, "banpick_center": {"x": 0, "y": -11}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "麦迪",
        "attack": "步枪射击，造成" + AD + O + "物理伤害" + E + "。" + O + "狙神" + E + "：目标离得越远，她造成的伤害越高，最多+" + A +
                  "{p_max}%" + E + "；被通缉的敌人阵亡时她领一份赏金：攻速+" + A + "{w_as}%" + E + "，最多" + A + "{w_max}" + E + "份。",
        "skill": "半蹲朝范围内最远的敌人连开" + A + "{q_n}" + E + "枪（先打英雄），每枪打中路上第一个敌人，造成" + phys("q_dmg", "q_ratio") +
                 O + "物理伤害" + E + "。",
        "skill2": "通缉附近当前生命最高的敌方英雄" + A + "{e_t}秒" + E + "：它受到的伤害+" + A + "{e_amp}%" + E + "。",
        "ult": "瞄准后向生命比例最低的敌方英雄射出一发穿透子弹，路上每个敌人受到" + phys("r_dmg", "r_ratio") + O + "物理伤害" + E +
               "，按其已损失生命比例最多再加" + A + "{r_exec}%" + E + "。",
        "names": ("连拨击锤", "通缉令", "执法狙杀"),
    },
    "zh-hant": {
        "name": "梅狄",
        "attack": "步槍射擊，造成" + AD + O + "物理傷害" + E + "。" + O + "狙擊專家" + E + "：目標離得越遠，她造成的傷害越高，最多+" + A +
                  "{p_max}%" + E + "；被通緝的敵人陣亡時她領一份賞金：攻速+" + A + "{w_as}%" + E + "，最多" + A + "{w_max}" + E + "份。",
        "skill": "半蹲朝範圍內最遠的敵人連開" + A + "{q_n}" + E + "槍（優先英雄），每槍擊中路上第一個敵人，造成" + phys("q_dmg", "q_ratio") +
                 O + "物理傷害" + E + "。",
        "skill2": "通緝附近目前生命最高的敵方英雄" + A + "{e_t}秒" + E + "：它受到的傷害+" + A + "{e_amp}%" + E + "。",
        "ult": "瞄準後向生命比例最低的敵方英雄射出一發穿透子彈，路上每個敵人受到" + phys("r_dmg", "r_ratio") + O + "物理傷害" + E +
               "，依其已損失生命比例最多再加" + A + "{r_exec}%" + E + "。",
        "names": ("旋風鎚", "通緝令", "執法狙殺"),
    },
    "en": {
        "name": "Maddie",
        "attack": "Fires her rifle for " + AD + " " + O + "physical damage" + E + ". " + O + "Sniper" + E + ": she deals more "
                  "damage the farther the target, up to " + A + "{p_max}%" + E + "; when a Wanted enemy dies she collects a "
                  "bounty: " + A + "{w_as}%" + E + " attack speed, up to " + A + "{w_max}" + E + " bounties.",
        "skill": "Crouches and fires " + A + "{q_n}" + E + " shots at the farthest enemy in range (champions first); each hits "
                 "the first enemy in its way for " + phys("q_dmg", "q_ratio") + " " + O + "physical damage" + E + ".",
        "skill2": "Marks the nearby enemy champion with the most health as Wanted for " + A + "{e_t}s" + E + ": it takes " + A +
                  "{e_amp}%" + E + " more damage.",
        "ult": "Takes aim, then fires a piercing round at the enemy champion with the lowest share of health: every enemy in "
               "its line takes " + phys("r_dmg", "r_ratio") + " " + O + "physical damage" + E + ", up to " + A + "{r_exec}%" +
               E + " more by the share of health it is missing.",
        "names": ("Fan the Hammer", "Wanted", "Enforcer's Snipe"),
    },
    "ko": {
        "name": "매디",
        "attack": "소총을 쏴 " + AD + " 물리 피해. " + O + "저격수" + E + ": 대상이 멀수록 피해가 커진다(최대 +" + A + "{p_max}%" + E +
                  "). 현상수배된 적이 죽으면 현상금: 공격 속도 +" + A + "{w_as}%" + E + "(최대 " + A + "{w_max}" + E + "번).",
        "skill": "몸을 낮추고 사거리 안에서 가장 먼 적(챔피언 우선)에게 " + A + "{q_n}" + E + "발을 쏜다. 한 발마다 경로의 첫 적에게 " +
                 phys("q_dmg", "q_ratio") + " 물리 피해.",
        "skill2": "주변에서 현재 체력이 가장 높은 적 챔피언을 " + A + "{e_t}초" + E + " 동안 현상수배: 받는 피해 +" + A + "{e_amp}%" + E + ".",
        "ult": "조준한 뒤 체력 비율이 가장 낮은 적 챔피언에게 관통탄을 쏜다: 경로의 모든 적에게 " + phys("r_dmg", "r_ratio") +
               " 물리 피해, 잃은 체력 비율에 따라 최대 " + A + "{r_exec}%" + E + " 추가.",
        "names": ("탄환 세례", "현상수배", "집행자의 저격"),
    },
    "ja": {
        "name": "マディー",
        "attack": "ライフルを撃ち、" + AD + "の物理ダメージ。" + O + "スナイパー" + E + "：対象が遠いほどダメージが増える（最大+" + A +
                  "{p_max}%" + E + "）。指名手配の敵が倒れると賞金：攻撃速度+" + A + "{w_as}%" + E + "（最大" + A + "{w_max}" + E + "回）。",
        "skill": "身をかがめ、射程内で最も遠い敵（チャンピオン優先）に" + A + "{q_n}" + E + "発撃つ。1発ごとに射線上の最初の敵に" +
                 phys("q_dmg", "q_ratio") + "の物理ダメージ。",
        "skill2": "近くで現在体力が最も高い敵チャンピオンを" + A + "{e_t}秒" + E + "間指名手配：受けるダメージ+" + A + "{e_amp}%" + E + "。",
        "ult": "狙いを定め、体力の割合が最も低い敵チャンピオンに貫通弾を撃つ：射線上の全ての敵に" + phys("r_dmg", "r_ratio") +
               "の物理ダメージ、失った体力の割合に応じて最大" + A + "{r_exec}%" + E + "増加。",
        "names": ("ファニングショット", "指名手配", "執行官の狙撃"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_maddie's sfx / tsfx) and tft.dll's
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.3, 0.0)],
    f"{ID}_a_reload": [(CLIP + "a_reload", 0.25, 0.0)],
    f"{ID}_q_cast": [(CLIP + "q_cast", 0.4, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.35, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.3, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.6, 0.0)],
    f"{ID}_r_aim": [(CLIP + "r_aim", 0.45, 0.0)],
    f"{ID}_r_shot": [(CLIP + "r_shot", 0.6, 0.0)],
    f"{ID}_r_hit": [(CLIP + "r_hit", 0.5, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/maddie.rs: each bullet and its hit, the Wanted mark, the round's hit)
DLL_SOUNDS = {f"{ID}_q", f"{ID}_q_hit", f"{ID}_e", f"{ID}_r_hit"}


def values(p):
    v = {k: p[k] for k in ("p_max", "w_as", "w_max", "q_n", "q_dmg", "q_ratio", "e_amp", "r_dmg", "r_ratio", "r_exec")}
    v["e_t"] = secs(p["e_t"])
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_maddie.py")
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
    mi["last_updated"] = "2026-10-27"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
