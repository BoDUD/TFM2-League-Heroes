"""Scar's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_scar.P.

    python tools/kit/setup_scar.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_violet.py writes for Violet: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_scar in every language, description + skill_name),
sound/sfx/tft_scar_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 13's own (CommunityDragon latest cdragon/tft/<locale>.json, TFT13_FlyGuy, 2026-10-28): zh_CN 刀疤,
zh_TW 斯卡, ja スカー, ko 스카, en Scar; Sumpsnipe Surprise = 水坑狙击惊喜 / 汙水坑驚喜 / 最下層の奇襲 / 지하동굴 깜짝선물; his traits
Firelight = 野火帮 / 野火幫 / ファイヤーライト / 점화단 and Watcher = 监察 / 守望者 / ウォッチャー / 주시자 name the passive. The Spear
Sweep (长矛横扫) and the Firelight Raid (野火突袭) are our own (TFT has one ability; the user's pick, plan A 「野火坦克」).
The texts are the rules he plays with tft.dll (addons/tft/src/scar.rs): the dash's heal by the damage taken since the
last one, Watcher by health, the bombs at the nearest enemies.
Sounds: tools/lol/extract_scar.py's clips in tft/sound/sfx/tft_scar_sfx_*.wav (git-ignored) - his own set-13 TFT
sounds (the thrust and its hit, the second swing and its hit for the sweep, the crit hit for the dash's strike, the
throw, the bomb going off, the heal, his voice on the throw), Firelight Ekko's hoverboard (the dash, the raid's boost,
the guard's shield) and Ziggs's bombs (the fire bombs, the landing blast). A clip name never equals an event name
(vo-clip-names rule): event tft_scar_<x> plays clip tft_scar_sfx_<x>. package_mod moves the clips to sound/bgm/ at
install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_scar import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14 (Ao Shin was merged first)
VERSION = "0.14.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from his soles' point, up negative): the face point between the mask's eye sockets (the
# design's socket row 16 of 76 at PPU 2.0: 30 over the ground; 9 ahead of his standing column); the centre in his body;
# the ban/pick card by bp_card_audit.py's rule (checked there after the sheet is built)
# center: the encyclopedia card puts this point at a fixed spot - set by League's rule (tools/art/bp_card_audit.py --centers, 2026-11-01)
VIEW = {"face": {"x": 9, "y": -30}, "center": {"x": 2, "y": -11}, "banpick_center": {"x": 2, "y": -6}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "刀疤",
        "attack": "长矛刺击造成" + AD + O + "物理伤害" + E + "。" + O + "野火冲刺" + E + "：每" + A + "{p_cd}秒" + E + "下一击踩滑板冲刺，" +
                  "造成" + phys("p_dmg", "p_ad") + "+" + APi + M + "{p_ap}%" + E + "伤害，回复上次冲刺以来所受伤害的" + A + "{p_heal}%" + E +
                  "。" + O + "监察" + E + "：生命不低于" + A + "{w_line}%" + E + "时减伤" + A + "{w_hi}%" + E + "，否则" + A + "{w_lo}%" + E + "。",
        "skill": "向最近的" + A + "{q_n}" + E + "名敌人各扔一颗炸弹，造成" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并" + R +
                 "晕眩{q_stun}秒" + E + "；自己回复" + mag("q_heal", "q_heal_ap") + "生命。",
        "skill2": "长矛横扫前方，造成" + phys("e_dmg", "e_ad") + "+" + HPi + O + "{e_hp}%" + E + "物理伤害并" + R + "击退" + E + "敌人。",
        "ult": "踩滑板冲向敌人，途中丢下两颗燃烧弹（各" + mag("r_bomb", "r_bomb_ap") + "魔法伤害）；落地爆炸，周围敌人受到" +
               mag("r_dmg", "r_ap") + "魔法伤害并被" + R + "击飞{r_up}秒" + E + "，之后" + A + "{r_t}秒" + E + "内减伤" + A + "{r_dr}%" + E + "。",
        "names": ("水坑狙击惊喜", "长矛横扫", "野火突袭"),
    },
    "zh-hant": {
        "name": "斯卡",
        "attack": "長矛刺擊造成" + AD + O + "物理傷害" + E + "。" + O + "野火衝刺" + E + "：每" + A + "{p_cd}秒" + E + "下一擊踩滑板衝刺，" +
                  "造成" + phys("p_dmg", "p_ad") + "+" + APi + M + "{p_ap}%" + E + "傷害，回復上次衝刺以來所受傷害的" + A + "{p_heal}%" + E +
                  "。" + O + "守望者" + E + "：生命不低於" + A + "{w_line}%" + E + "時減傷" + A + "{w_hi}%" + E + "，否則" + A + "{w_lo}%" + E + "。",
        "skill": "向最近的" + A + "{q_n}" + E + "名敵人各扔一顆炸彈，造成" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並" + R +
                 "暈眩{q_stun}秒" + E + "；自己回復" + mag("q_heal", "q_heal_ap") + "生命。",
        "skill2": "長矛橫掃前方，造成" + phys("e_dmg", "e_ad") + "+" + HPi + O + "{e_hp}%" + E + "物理傷害並" + R + "擊退" + E + "敵人。",
        "ult": "踩滑板衝向敵人，途中丟下兩顆燃燒彈（各" + mag("r_bomb", "r_bomb_ap") + "魔法傷害）；落地爆炸，周圍敵人受到" +
               mag("r_dmg", "r_ap") + "魔法傷害並被" + R + "擊飛{r_up}秒" + E + "，之後" + A + "{r_t}秒" + E + "內減傷" + A + "{r_dr}%" + E + "。",
        "names": ("汙水坑驚喜", "長矛橫掃", "野火突襲"),
    },
    "en": {
        "name": "Scar",
        "attack": "Thrusts his spear for " + AD + " " + O + "physical damage" + E + ". " + O + "Firelight Dash" + E + ": every " + A +
                  "{p_cd}s" + E + " his next hit is a hoverboard dash for " + phys("p_dmg", "p_ad") + " + " + APi + M + "{p_ap}%" + E +
                  ", healing " + A + "{p_heal}%" + E + " of the damage taken since the last dash. " + O + "Watcher" + E + ": " + A +
                  "{w_hi}%" + E + " damage reduction at " + A + "{w_line}%" + E + " health or more, " + A + "{w_lo}%" + E + " below.",
        "skill": "Throws a bomb at each of the " + A + "{q_n}" + E + " nearest enemies for " + mag("q_dmg", "q_ap") + " " + M +
                 "magic damage" + E + ", " + R + "stunning for {q_stun}s" + E + ". Heals himself " + mag("q_heal", "q_heal_ap") + ".",
        "skill2": "Sweeps his spear in front of him for " + phys("e_dmg", "e_ad") + " + " + HPi + O + "{e_hp}%" + E +
                  " physical damage, " + R + "knocking enemies back" + E + ".",
        "ult": "Rides his hoverboard at an enemy, dropping two fire bombs (" + mag("r_bomb", "r_bomb_ap") + " magic damage each); "
               "landing, a blast deals " + mag("r_dmg", "r_ap") + " magic damage around him and " + R + "knocks up for {r_up}s" + E +
               ", then he takes " + A + "{r_dr}%" + E + " less damage for " + A + "{r_t}s" + E + ".",
        "names": ("Sumpsnipe Surprise", "Spear Sweep", "Firelight Raid"),
    },
    "ko": {
        "name": "스카",
        "attack": "창으로 찔러 " + AD + " 물리 피해. " + O + "점화단 돌진" + E + ": " + A + "{p_cd}초" + E + "마다 다음 공격이 호버보드 돌진, " +
                  phys("p_dmg", "p_ad") + " + " + APi + M + "{p_ap}%" + E + " 피해, 지난 돌진 이후 받은 피해의 " + A + "{p_heal}%" + E +
                  " 회복. " + O + "주시자" + E + ": 체력 " + A + "{w_line}%" + E + " 이상이면 피해 감소 " + A + "{w_hi}%" + E + ", 아니면 " +
                  A + "{w_lo}%" + E + ".",
        "skill": "가장 가까운 적 " + A + "{q_n}" + E + "명에게 폭탄을 던져 " + mag("q_dmg", "q_ap") + " " + M + "마법 피해" + E + "와 " + R +
                 "{q_stun}초 기절" + E + "; 자신은 " + mag("q_heal", "q_heal_ap") + " 회복.",
        "skill2": "앞쪽을 창으로 휩쓸어 " + phys("e_dmg", "e_ad") + " + " + HPi + O + "{e_hp}%" + E + " 물리 피해와 " + R + "밀쳐내기" + E + ".",
        "ult": "호버보드로 적에게 돌진하며 화염 폭탄 두 개(각 " + mag("r_bomb", "r_bomb_ap") + " 마법 피해); 착지 폭발로 주변 적에게 " +
               mag("r_dmg", "r_ap") + " 마법 피해와 " + R + "{r_up}초 에어본" + E + ", 이후 " + A + "{r_t}초" + E + " 동안 피해 감소 " + A +
               "{r_dr}%" + E + ".",
        "names": ("지하동굴 깜짝선물", "창 휩쓸기", "점화단 습격"),
    },
    "ja": {
        "name": "スカー",
        "attack": "槍で突き、" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "ファイヤーライトダッシュ" + E + "：" + A + "{p_cd}秒" + E +
                  "ごとに次の攻撃がホバーボード突進、" + phys("p_dmg", "p_ad") + "+" + APi + M + "{p_ap}%" + E + "のダメージ、前回の突進以降に" +
                  "受けたダメージの" + A + "{p_heal}%" + E + "回復。" + O + "ウォッチャー" + E + "：体力" + A + "{w_line}%" + E + "以上で被ダメージ" +
                  A + "{w_hi}%" + E + "軽減、未満で" + A + "{w_lo}%" + E + "。",
        "skill": "最も近い敵" + A + "{q_n}" + E + "体に爆弾を投げ、" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" + R +
                 "{q_stun}秒スタン" + E + "。自身は" + mag("q_heal", "q_heal_ap") + "回復。",
        "skill2": "前方を槍で薙ぎ払い、" + phys("e_dmg", "e_ad") + "+" + HPi + O + "{e_hp}%" + E + "の物理ダメージと" + R + "ノックバック" + E +
                  "。",
        "ult": "ホバーボードで敵へ突進し、焼夷弾を2つ落とす（各" + mag("r_bomb", "r_bomb_ap") + "の魔法ダメージ）。着地の爆発で周囲の敵に" +
               mag("r_dmg", "r_ap") + "の魔法ダメージと" + R + "{r_up}秒のノックアップ" + E + "、その後" + A + "{r_t}秒" + E + "間被ダメージ" +
               A + "{r_dr}%" + E + "軽減。",
        "names": ("最下層の奇襲", "スピアスイープ", "ファイヤーライト強襲"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_scar's sfx / tsfx) and tft.dll's
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.4, 0.0)],
    f"{ID}_p": [(CLIP + "p", 0.45, 0.0)],
    f"{ID}_p_hit": [(CLIP + "p_hit", 0.5, 0.0)],
    f"{ID}_p_heal": [(CLIP + "p_heal", 0.4, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.45, 0.0)],
    f"{ID}_q_vo": [(CLIP + "q_vo", 0.6, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.5, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_e_hit": [(CLIP + "e_hit", 0.5, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.5, 0.0)],
    f"{ID}_r_bomb": [(CLIP + "r_bomb", 0.5, 0.0)],
    f"{ID}_r_mines": [(CLIP + "r_mines", 0.6, 0.0)],
    f"{ID}_r_guard": [(CLIP + "r_guard", 0.45, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/scar.rs: the dash's heal, the bombs' hits)
DLL_SOUNDS = {f"{ID}_p_heal", f"{ID}_q_hit"}


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ad", "p_ap", "p_heal", "w_line", "w_hi", "w_lo", "q_n", "q_dmg", "q_ap", "q_heal",
                           "q_heal_ap", "e_dmg", "e_ad", "e_hp", "r_bomb", "r_bomb_ap", "r_dmg", "r_ap", "r_dr")}
    for k in ("p_cd", "q_stun", "r_up", "r_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_scar.py")
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
    mi["last_updated"] = "2026-10-28"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
