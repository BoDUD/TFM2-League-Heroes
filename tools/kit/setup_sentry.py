"""The Sentry's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_sentry.P.

    python tools/kit/setup_sentry.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_gromp.py writes for Gromp: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_sentry in every language, description + skill_name),
sound/sfx/tft_sentry_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 18's own (CommunityDragon cdragon/tft/<locale>.json, DA_18_Sentry, 2026-11-02): zh_CN 苍蓝哨戒, zh_TW
小石子, ja 小石, ko 조약돌, en Pebbles; its ability Azure Laser = 蔚蓝激光 (zh_TW 蒼藍雷射, ja 蒼き光線, ko 하늘빛 레이저), Teal Buff
= 青霸符 (zh_TW 深藍綠色增益, ja ティールバフ, ko 청록색 버프) from the same text. Shard Bolt (碎光弹), Rift Leap (裂石跃迁) and Prism
Sweep (棱镜扫射) are our own (the user's pick, plan A 「蔚蓝激光」).
The texts are the rules it plays: Teal Buff's ult refund and the laser's range break in tft.dll (addons/tft/src/
sentry.rs), the rest the data (the laser's waves and shred, crowd control breaking it, the leap, the sweep).
Sounds: tools/lol/extract_sentry.py's clips in tft/sound/sfx/tft_sentry_sfx_*.wav (git-ignored) - the Rift's Blue camp
minis are silent, so Vel'Koz's lasers, Viktor's Death Ray, Ezreal's blink and Taliyah's stones. A clip name never
equals an event name (vo-clip-names rule): event tft_sentry_<x> plays clip tft_sentry_sfx_<x>. package_mod moves the
clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sentry import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29, the Elder Dragon 0.30, Meepsie 0.31, Murk Wolf 0.32, the Scuttle Crab 0.33, Gromp 0.34, the encyclopedia
# centres 0.35 (PR #657), the log fixes 0.36 (PR #659), the Sentry 0.37
VERSION = "0.37.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point on its core (on its standing column, 19 over
# the ground: 22 design rows + the 3-row hover at PPU 1.29 - ppu_restyle's face_to); the centre (League's rule,
# tools/art/bp_card_audit.py --centers, 2026-11-02: its solid top 32.7 px up -> -6); the ban/pick card as Gromp's
# (the same 33 px from its top to its lowest point)
VIEW = {"face": {"x": 0, "y": -19}, "center": {"x": 0, "y": -6}, "banpick_center": {"x": 0, "y": -12}}


def mag(d, r):
    """base + AP ratio, magic."""
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "苍蓝哨戒",
        "attack": "蓝核射出碎光弹，造成" + AD + O + "物理伤害" + E + "和" + APi + M + "{a_ap}%" + E + M + "魔法伤害" + E + "。" + O + "青霸符" + E +
                  "：蔚蓝激光每引导" + A + "{p_every}秒" + E + "，大招冷却" + A + "-{p_cut}秒" + E + "。",
        "skill": "对目标引导激光" + A + "{q_t}秒" + E + "（可以边飘边照），共造成" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "，每" + A +
                 "{q_p}秒" + E + "魔抗" + A + "-{q_mr}" + E + "（可叠加，持续" + A + "{q_hold}秒" + E + "）。目标离开射程或自己被控时中断。",
        "skill2": "两块石头猛地分开再合拢，周围敌人受到" + mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "并减速" + A + "{e_slow}%" + E + "（" + A +
                  "{e_hold}秒" + E + "），自己向后闪开。",
        "ult": "两块石头张开，蓝核射出光柱扫过前方扇形，造成" + mag("r_dmg", "r_ratio") + M + "魔法伤害" + E + "，魔抗" + A + "-{r_mr}" + E + "（" + A +
               "{r_hold}秒" + E + "）。",
        "names": ("蔚蓝激光", "裂石跃迁", "棱镜扫射"),
    },
    "zh-hant": {
        "name": "小石子",
        "attack": "藍核射出碎光彈，造成" + AD + O + "物理傷害" + E + "和" + APi + M + "{a_ap}%" + E + M + "魔法傷害" + E + "。" + O + "深藍綠色增益" + E +
                  "：蒼藍雷射每照射" + A + "{p_every}秒" + E + "，大絕冷卻" + A + "-{p_cut}秒" + E + "。",
        "skill": "對目標照射雷射" + A + "{q_t}秒" + E + "（可以邊飄邊照），共造成" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "，每" + A +
                 "{q_p}秒" + E + "魔防" + A + "-{q_mr}" + E + "（可疊加，持續" + A + "{q_hold}秒" + E + "）。目標離開射程或自己被控時中斷。",
        "skill2": "兩塊石頭猛地分開再合攏，周圍敵軍受到" + mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "並緩速" + A + "{e_slow}%" + E + "（" + A +
                  "{e_hold}秒" + E + "），自己向後閃開。",
        "ult": "兩塊石頭張開，藍核射出光柱掃過前方扇形，造成" + mag("r_dmg", "r_ratio") + M + "魔法傷害" + E + "，魔防" + A + "-{r_mr}" + E + "（" + A +
               "{r_hold}秒" + E + "）。",
        "names": ("蒼藍雷射", "裂石躍遷", "稜鏡掃射"),
    },
    "en": {
        "name": "Pebbles",
        "attack": "Fires a shard bolt from its core for " + AD + " " + O + "physical damage" + E + " and " + APi + M + "{a_ap}%" + E + " " + M +
                  "magic damage" + E + ". " + O + "Teal Buff" + E + ": every " + A + "{p_every}s" + E + " of Azure Laser channeled cuts its "
                  "ult's cooldown by " + A + "{p_cut}s" + E + ".",
        "skill": "Channels a laser at its target for " + A + "{q_t}s" + E + " (it can float while lasing), dealing " +
                 mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " in all and " + A + "-{q_mr}" + E + " Magic Resist every " + A +
                 "{q_p}s" + E + " (stacking, " + A + "{q_hold}s" + E + "). Breaks if the target leaves range or it is crowd controlled.",
        "skill2": "Its two halves split apart and close again: nearby enemies take " + mag("e_dmg", "e_ratio") + " " + M +
                  "magic damage" + E + " and are slowed by " + A + "{e_slow}%" + E + " for " + A + "{e_hold}s" + E + "; it blinks back.",
        "ult": "Its halves open wide and its core sweeps a beam across a cone in front for " + mag("r_dmg", "r_ratio") + " " + M +
               "magic damage" + E + " and " + A + "-{r_mr}" + E + " Magic Resist for " + A + "{r_hold}s" + E + ".",
        "names": ("Azure Laser", "Rift Leap", "Prism Sweep"),
    },
    "ko": {
        "name": "조약돌",
        "attack": "핵에서 파편 광탄을 쏴 " + AD + " " + O + "물리 피해" + E + "와 " + APi + M + "{a_ap}%" + E + " " + M + "마법 피해" + E + ". " +
                  O + "청록색 버프" + E + ": 하늘빛 레이저를 " + A + "{p_every}초" + E + " 집중할 때마다 궁극기 재사용 대기시간 " + A +
                  "-{p_cut}초" + E + ".",
        "skill": "대상에게 " + A + "{q_t}초" + E + " 동안 레이저를 집중해(떠다니며 가능) 총 " + mag("q_dmg", "q_ratio") + " " + M + "마법 피해" +
                 E + "를 주고 " + A + "{q_p}초" + E + "마다 마법 저항력 " + A + "-{q_mr}" + E + "(중첩, " + A + "{q_hold}초" + E + "). 대상이 "
                 "사거리를 벗어나거나 군중 제어를 받으면 끊깁니다.",
        "skill2": "두 조각이 갈라졌다 다시 붙으며 주변 적에게 " + mag("e_dmg", "e_ratio") + " " + M + "마법 피해" + E + "와 " + A +
                  "{e_slow}%" + E + " 둔화(" + A + "{e_hold}초" + E + "). 자신은 뒤로 순간이동합니다.",
        "ult": "두 조각이 활짝 열리고 핵이 전방 부채꼴로 광선을 휩쓸어 " + mag("r_dmg", "r_ratio") + " " + M + "마법 피해" + E +
               "와 마법 저항력 " + A + "-{r_mr}" + E + "(" + A + "{r_hold}초" + E + ").",
        "names": ("하늘빛 레이저", "균열 도약", "프리즘 휩쓸기"),
    },
    "ja": {
        "name": "小石",
        "attack": "コアから砕光弾を放ち" + AD + "の" + O + "物理ダメージ" + E + "と" + APi + M + "{a_ap}%" + E + "の" + M + "魔法ダメージ" + E + "。" +
                  O + "ティールバフ" + E + "：蒼き光線を" + A + "{p_every}秒" + E + "詠唱するごとにアルティメットのクールダウン" + A +
                  "-{p_cut}秒" + E + "。",
        "skill": "対象に光線を" + A + "{q_t}秒" + E + "照射し（浮遊しながら可）、合計" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E +
                 "、" + A + "{q_p}秒" + E + "ごとに魔法防御" + A + "-{q_mr}" + E + "（スタック、" + A + "{q_hold}秒" + E + "）。対象が射程外に"
                 "出るか行動妨害で中断。",
        "skill2": "二つの石が割れて再び閉じ、周囲の敵に" + mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" + E + "と" + A + "{e_slow}%" + E +
                  "スロウ（" + A + "{e_hold}秒" + E + "）。自身は後方へ跳ぶ。",
        "ult": "二つの石が大きく開き、コアから光柱を前方扇形に薙ぎ払い" + mag("r_dmg", "r_ratio") + "の" + M + "魔法ダメージ" + E +
               "と魔法防御" + A + "-{r_mr}" + E + "（" + A + "{r_hold}秒" + E + "）。",
        "names": ("蒼き光線", "裂石跳躍", "プリズムスイープ"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_sentry's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.35), ("a_hit", 0.3),
    ("p", 0.3),
    ("q", 0.45), ("q_hit", 0.2), ("q_shred", 0.3), ("q_end", 0.35),
    ("e", 0.45), ("e_split", 0.45), ("e_ring", 0.45), ("e_slow", 0.3),
    ("r", 0.5), ("r_charge", 0.5), ("r_beam", 0.55), ("r_hit", 0.35),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/sentry.rs: Teal Buff's refund, the shards falling apart)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("a_ap", "q_dmg", "q_ratio", "q_mr", "e_dmg", "e_ratio", "e_slow", "r_dmg", "r_ratio", "r_mr")}
    for k in ("p_every", "p_cut", "q_t", "q_p", "q_hold", "e_hold", "r_hold"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_sentry.py")
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
    mi["last_updated"] = "2026-11-02"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
