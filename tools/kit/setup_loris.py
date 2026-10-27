"""Loris's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_loris.P.

    python tools/kit/setup_loris.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft): mod.mod_info (VERSION, the pack's description:
setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys sorted,
setup_alune.py's way), text/champion.i18n (tft_loris in every language, description + skill_name),
sound/sfx/tft_loris_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 16's own (CommunityDragon latest cdragon/tft/<locale>.json, TFT16_Loris, 2026-10-27): zh_CN 洛里斯,
zh_TW 洛里斯, ja ロリス, ko 로리스; Piltover Tussle = 皮城争斗 / 皮爾托福的決鬥 / ピルトーヴァーの闘争 / 필트오버 난투; his trait
Warden = 神盾使 / 守護者 / ワーデン / 파수꾼 names the passive. Bulwark (盾卫) and the Iron Line (钢铁防线) are our own (TFT has one
ability, split here into the charge and the taunt; the user's pick, plan A 「神盾使·皮城争斗」). The texts are the rules
he plays with tft.dll (addons/tft/src/loris.rs): the Warden shields at 75% / 25%, Bulwark's leap to the ally with the
lowest share of health and the share of its damage he takes.
Sounds: tools/lol/extract_loris.py's clips in tft/sound/sfx/tft_loris_sfx_*.wav (git-ignored) - his own set-16 TFT
sounds (the bash, its hit, the crit hit, the cast, the charge, his voice on the ult), set 13's Beardy shield buff and
shockwave (the shields, the slam) and Braum's Stand Behind Me landing and Glacial Fissure hit. A clip name never equals
an event name (vo-clip-names rule): event tft_loris_<x> plays clip tft_loris_sfx_<x>. package_mod moves the clips to
sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_loris import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
VERSION = "0.7.0"      # Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7: the next free one
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from his soles' point, up negative): the face point between his eyes (the design's eye row 11.5
# of 84 at PPU 2.0: 36 over the ground, 1 ahead of his standing column); the centre in his body; the ban/pick card by
# bp_card_audit.py's rule (y = -39 - top: his lo_idle reaches 34.7 over its centre -> -4)
VIEW = {"face": {"x": 1, "y": -36}, "center": {"x": 0, "y": -21}, "banpick_center": {"x": 0, "y": -4}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "洛里斯",
        "attack": "举盾猛砸，造成" + AD + O + "物理伤害" + E + "。" + O + "神盾使" + E + "：每条命第一次生命低于" + A + "{p_hi}%" + E +
                  "和" + A + "{p_lo}%" + E + "时，各获得最大生命" + A + "{p_pct}%" + E + "的护盾（" + A + "{p_t}秒" + E + "）。",
        "skill": "获得" + mag("q_sh", "q_sh_ap") + "的护盾（" + A + "{q_sh_t}秒" + E + "），举盾冲锋，撞到的敌人受到" + mag("q_dmg", "q_ap") +
                 "魔法伤害并" + R + "晕眩{q_stun}秒" + E + "。",
        "skill2": "冲到附近生命比例最低的友方英雄身边，两人各获得" + mag("e_sh", "e_sh_ap") + "的护盾（" + A + "{e_t}秒" + E +
                  "），期间替他承受" + A + "{e_share}%" + E + "的伤害。",
        "ult": "把巨盾砸进地里，周围的敌人受到" + mag("r_dmg", "r_ap") + "魔法伤害、被" + R + "击飞{r_up}秒" + E + "并" + R + "嘲讽{r_taunt}秒" +
               E + "；自己受到的伤害降低" + A + "{r_red}%" + E + "（" + A + "{r_t}秒" + E + "）。",
        "names": ("皮城争斗", "盾卫", "钢铁防线"),
    },
    "zh-hant": {
        "name": "洛里斯",
        "attack": "舉盾猛砸，造成" + AD + O + "物理傷害" + E + "。" + O + "守護者" + E + "：每條命第一次生命低於" + A + "{p_hi}%" + E +
                  "和" + A + "{p_lo}%" + E + "時，各獲得最大生命" + A + "{p_pct}%" + E + "的護盾（" + A + "{p_t}秒" + E + "）。",
        "skill": "獲得" + mag("q_sh", "q_sh_ap") + "的護盾（" + A + "{q_sh_t}秒" + E + "），舉盾衝鋒，撞到的敵人受到" + mag("q_dmg", "q_ap") +
                 "魔法傷害並" + R + "暈眩{q_stun}秒" + E + "。",
        "skill2": "衝到附近生命比例最低的友方英雄身邊，兩人各獲得" + mag("e_sh", "e_sh_ap") + "的護盾（" + A + "{e_t}秒" + E +
                  "），期間替他承受" + A + "{e_share}%" + E + "的傷害。",
        "ult": "把巨盾砸進地裡，周圍的敵人受到" + mag("r_dmg", "r_ap") + "魔法傷害、被" + R + "擊飛{r_up}秒" + E + "並" + R + "嘲諷{r_taunt}秒" +
               E + "；自己受到的傷害降低" + A + "{r_red}%" + E + "（" + A + "{r_t}秒" + E + "）。",
        "names": ("皮爾托福的決鬥", "盾衛", "鋼鐵防線"),
    },
    "en": {
        "name": "Loris",
        "attack": "Bashes with his shield for " + AD + " " + O + "physical damage" + E + ". " + O + "Warden" + E + ": the first "
                  "time each life his health falls under " + A + "{p_hi}%" + E + " and under " + A + "{p_lo}%" + E + " he gains "
                  "a shield of " + A + "{p_pct}%" + E + " of his maximum health (" + A + "{p_t}s" + E + ").",
        "skill": "Gains a " + mag("q_sh", "q_sh_ap") + " shield (" + A + "{q_sh_t}s" + E + ") and charges behind his shield: "
                 "enemies he runs into take " + mag("q_dmg", "q_ap") + " magic damage and are " + R + "stunned for "
                 "{q_stun}s" + E + ".",
        "skill2": "Leaps to the nearby allied champion with the lowest share of health: both gain a " + mag("e_sh", "e_sh_ap") +
                  " shield (" + A + "{e_t}s" + E + ") and he takes " + A + "{e_share}%" + E + " of the damage meant for it.",
        "ult": "Slams his shield into the ground: nearby enemies take " + mag("r_dmg", "r_ap") + " magic damage, are " + R +
               "knocked up for {r_up}s" + E + " and " + R + "taunted for {r_taunt}s" + E + "; he takes " + A + "{r_red}%" + E +
               " less damage (" + A + "{r_t}s" + E + ").",
        "names": ("Piltover Tussle", "Bulwark", "Iron Line"),
    },
    "ko": {
        "name": "로리스",
        "attack": "방패로 내리쳐 " + AD + " 물리 피해. " + O + "파수꾼" + E + ": 목숨마다 처음으로 체력이 " + A + "{p_hi}%" + E + ", " + A +
                  "{p_lo}%" + E + " 아래로 떨어지면 각각 최대 체력의 " + A + "{p_pct}%" + E + " 보호막(" + A + "{p_t}초" + E + ").",
        "skill": mag("q_sh", "q_sh_ap") + " 보호막(" + A + "{q_sh_t}초" + E + ")을 얻고 방패를 들고 돌진: 부딪힌 적에게 " +
                 mag("q_dmg", "q_ap") + " 마법 피해, " + R + "{q_stun}초 기절" + E + ".",
        "skill2": "주변에서 체력 비율이 가장 낮은 아군 챔피언에게 도약: 둘 다 " + mag("e_sh", "e_sh_ap") + " 보호막(" + A + "{e_t}초" + E +
                  "), 그 동안 그 아군이 받을 피해의 " + A + "{e_share}%" + E + "를 대신 받는다.",
        "ult": "방패를 땅에 내리꽂는다: 주변 적에게 " + mag("r_dmg", "r_ap") + " 마법 피해, " + R + "{r_up}초 에어본" + E + ", " + R +
               "{r_taunt}초 도발" + E + ". 자신은 받는 피해 " + A + "{r_red}%" + E + " 감소(" + A + "{r_t}초" + E + ").",
        "names": ("필트오버 난투", "방패 수호", "강철 방어선"),
    },
    "ja": {
        "name": "ロリス",
        "attack": "盾で殴り、" + AD + "の物理ダメージ。" + O + "ワーデン" + E + "：ライフごとに初めて体力が" + A + "{p_hi}%" + E + "と" + A +
                  "{p_lo}%" + E + "を下回ると、それぞれ最大体力の" + A + "{p_pct}%" + E + "のシールド（" + A + "{p_t}秒" + E + "）。",
        "skill": mag("q_sh", "q_sh_ap") + "のシールド（" + A + "{q_sh_t}秒" + E + "）を得て盾を構えて突進：ぶつかった敵に" +
                 mag("q_dmg", "q_ap") + "の魔法ダメージと" + R + "{q_stun}秒のスタン" + E + "。",
        "skill2": "近くで体力の割合が最も低い味方チャンピオンへ跳び、2人とも" + mag("e_sh", "e_sh_ap") + "のシールド（" + A + "{e_t}秒" +
                  E + "）。その間、その味方が受けるダメージの" + A + "{e_share}%" + E + "を肩代わりする。",
        "ult": "盾を地面に叩きつける：周囲の敵に" + mag("r_dmg", "r_ap") + "の魔法ダメージ、" + R + "{r_up}秒のノックアップ" + E + "と" + R +
               "{r_taunt}秒の挑発" + E + "。自身の被ダメージ" + A + "{r_red}%" + E + "軽減（" + A + "{r_t}秒" + E + "）。",
        "names": ("ピルトーヴァーの闘争", "ブルワーク", "鉄の防衛線"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_loris's sfx / tsfx) and tft.dll's
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.35, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.4, 0.0)],
    f"{ID}_q_dash": [(CLIP + "q_dash", 0.45, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.4, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_e_shield": [(CLIP + "e_shield", 0.4, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.45, 0.0)],
    f"{ID}_vo": [(CLIP + "vo", 0.6, 0.0)],
    f"{ID}_r_slam": [(CLIP + "r_slam", 0.6, 0.0)],
    f"{ID}_r_hit": [(CLIP + "r_hit", 0.45, 0.0)],
    f"{ID}_p": [(CLIP + "p", 0.45, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/loris.rs: Bulwark's landing, the Warden shield)
DLL_SOUNDS = {f"{ID}_e_shield", f"{ID}_p"}


def values(p):
    v = {k: p[k] for k in ("p_hi", "p_lo", "p_pct", "q_sh", "q_sh_ap", "q_dmg", "q_ap", "e_sh", "e_sh_ap", "e_share",
                           "r_dmg", "r_ap", "r_red")}
    for k in ("p_t", "q_sh_t", "q_stun", "e_t", "r_up", "r_taunt", "r_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_loris.py")
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
    mi["last_updated"] = "2026-10-27"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
