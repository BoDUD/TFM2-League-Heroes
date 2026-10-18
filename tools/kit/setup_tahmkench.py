"""Tahm Kench's text (5 languages), sound_info files and his keys in the shared files, numbers from build_tahmkench.P.

    python tools/kit/setup_tahmkench.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_tahmkench in every language, description + skill_name),
sound/sfx/league_tahmkench_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.118.0, Tahm Kench named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 塔姆 / 河流之王; 培养品味, 巨舌鞭笞, 深渊潜航, 厚实表皮, 大快朵颐 - Data Dragon swaps
name and title; zh_TW 貪啃奇 / 品味獨到 / 毒舌 / 遨遊深淵 / 血多皮厚 / 大快朵頤, ja タム・ケンチ / 舌慣らし / 味見 / 川潜り /
ゆるゆる皮膜 / 丸呑み, ko 탐 켄치 / 절대 미각 / 혀 채찍 / 심연 잠수 / 두꺼운 피부 / 집어삼키기).
Slots: skill = Q, skill2 = W, ult = R; the passive and Thick Skin are told in the attack's text. No combo sentence in
any text (the user's rule). No `league_tahmkench_attack` sound: the engine would play it at the start of every attack;
the slap plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_tahmkench import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_tahmkench"
VERSION = "0.118.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7dd87dff>"      # heals, shields
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
# 2026-10-18 ban/pick card audit (frame centre, HD from lo_idle / 1.5; user: 「还有哪些英雄BP位置不对的一起改了」): -8 -> -6: the hat was cut
# 2026-10-18: face (-1,-38) - (-1,-36) put his eyes on the top two rows; kept equal to champion_view and ppu_restyle.py
VIEW = {"face": {"x": -1, "y": -38}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -6}}


def mag(k):
    """dmg + AP% + max-health% (his), the magic damage of an ability."""
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_ap}}%{E} + {M}{{{k}_hp}}%{E}"


PAS = M + "{p_dmg}" + E + " + " + M + "{p_hp}%" + E
SHIELD = G + "{e_sh}" + E + " + " + APi + G + "{e_sh_ap}%" + E
RSH = G + "{r_sh}" + E + " + " + APi + G + "{r_sh_ap}%" + E
HEAL = G + "{q_heal}" + E + " + " + APi + G + "{q_heal_ap}%" + E

TEXT = {
    "zh-hans": {
        "name": "塔姆",
        "attack": O + "培养品味" + E + "：普攻额外造成" + PAS + "最大生命" + M + "魔法伤害" + E + "，普攻、Q、W命中英雄叠一层，最多" + A + "3层" + E + "。" +
                  O + "厚实表皮" + E + "：受到伤害降低{e_red}%，被两名敌方英雄围住时获得" + SHIELD + "护盾。",
        "skill": "舌头鞭打第一个单位，造成" + mag("q") + "最大生命" + M + "魔法伤害" + E + "，" + R + "减速{q_slow}%" + E + A + "{q_slow_t}秒" + E +
                 "；命中英雄回复" + HEAL + "生命并叠一层，" + A + "3层" + E + "时" + R + "眩晕{q_stun}秒" + E + "。",
        "skill2": "潜入地下" + A + "{w_up}秒" + E + "（不可选中），在目标处冒出，造成" + mag("w") + "最大生命" + M + "魔法伤害" + E + "并" + R + "击飞{w_air}秒" + E + "。",
        "ult": "吞下被控制、身陷敌群的队友" + A + "{r_ally_t}秒" + E + "，吐出时给予" + RSH + "护盾；或吞下" + A + "3层" + E + "的敌方英雄" + A +
               "{r_t}秒" + E + "，造成" + mag("r") + "最大生命" + M + "魔法伤害" + E + "和其最大生命{r_thp}%真实伤害。",
        "names": ("巨舌鞭笞", "深渊潜航", "大快朵颐"),
    },
    "zh-hant": {
        "name": "貪啃奇",
        "attack": O + "品味獨到" + E + "：普攻額外造成" + PAS + "最大生命" + M + "魔法傷害" + E + "，普攻、Q、W命中英雄疊一層，最多" + A + "3層" + E + "。" +
                  O + "血多皮厚" + E + "：受到傷害降低{e_red}%，被兩名敵方英雄圍住時獲得" + SHIELD + "護盾。",
        "skill": "舌頭鞭打第一個單位，造成" + mag("q") + "最大生命" + M + "魔法傷害" + E + "，" + R + "緩速{q_slow}%" + E + A + "{q_slow_t}秒" + E +
                 "；命中英雄回復" + HEAL + "生命並疊一層，" + A + "3層" + E + "時" + R + "暈眩{q_stun}秒" + E + "。",
        "skill2": "潛入地下" + A + "{w_up}秒" + E + "（無法被選取），在目標處冒出，造成" + mag("w") + "最大生命" + M + "魔法傷害" + E + "並" + R + "擊飛{w_air}秒" + E + "。",
        "ult": "吞下被控制、身陷敵群的隊友" + A + "{r_ally_t}秒" + E + "，吐出時給予" + RSH + "護盾；或吞下" + A + "3層" + E + "的敵方英雄" + A +
               "{r_t}秒" + E + "，造成" + mag("r") + "最大生命" + M + "魔法傷害" + E + "和其最大生命{r_thp}%真實傷害。",
        "names": ("毒舌", "遨遊深淵", "大快朵頤"),
    },
    "en": {
        "name": "Tahm Kench",
        "attack": O + "An Acquired Taste" + E + ": attacks deal " + PAS + " max health " + M + "magic damage" + E + " more; attacks, Q and W stack on champions, up to " +
                  A + "3" + E + ". " + O + "Thick Skin" + E + ": {e_red}% less damage taken; surrounded by two enemy champions he gains a " + SHIELD + " shield.",
        "skill": "Lashes his tongue at the first unit hit: " + mag("q") + " max health " + M + "magic damage" + E + " and a " + R + "{q_slow}% slow" + E + " for " + A +
                 "{q_slow_t}s" + E + ". On a champion he heals " + HEAL + " and adds a stack; at " + A + "3" + E + " it " + R + "stuns {q_stun}s" + E + ".",
        "skill2": "Dives underground for " + A + "{w_up}s" + E + " (untargetable) and bursts up at the target: " + mag("w") + " max health " + M + "magic damage" + E +
                  " and a " + R + "{w_air}s knock-up" + E + ".",
        "ult": "Swallows an ally caught in crowd control among enemies for " + A + "{r_ally_t}s" + E + " and spits him out with a " + RSH +
               " shield; or an enemy champion with " + A + "3" + E + " stacks for " + A + "{r_t}s" + E + ": " + mag("r") + " max health " + M + "magic damage" + E +
               " and {r_thp}% of its max health as true damage.",
        "names": ("Tongue Lash", "Abyssal Dive", "Devour"),
    },
    "ko": {
        "name": "탐 켄치",
        "attack": O + "절대 미각" + E + ": 기본 공격이 " + PAS + " 최대 체력 " + M + "마법 피해" + E + " 추가, 기본 공격·Q·W가 챔피언에 중첩 (최대 " + A + "3" + E + "). " +
                  O + "두꺼운 피부" + E + ": 받는 피해 {e_red}% 감소, 적 챔피언 둘에게 둘러싸이면 " + SHIELD + " 보호막.",
        "skill": "혀로 첫 대상을 후려쳐 " + mag("q") + " 최대 체력 " + M + "마법 피해" + E + "와 " + A + "{q_slow_t}초" + E + " " + R + "{q_slow}% 둔화" + E +
                 ". 챔피언이면 " + HEAL + " 회복하고 중첩, " + A + "3중첩" + E + "에 " + R + "{q_stun}초 기절" + E + ".",
        "skill2": A + "{w_up}초" + E + " 동안 땅속으로 잠수 (대상 지정 불가) 후 대상 위치에서 솟아올라 " + mag("w") + " 최대 체력 " + M + "마법 피해" + E + "와 " + R +
                  "{w_air}초 에어본" + E + ".",
        "ult": "군중 제어에 걸려 적에게 둘러싸인 아군을 " + A + "{r_ally_t}초" + E + " 삼켜 뱉을 때 " + RSH + " 보호막; 또는 " + A + "3중첩" + E +
               " 적 챔피언을 " + A + "{r_t}초" + E + " 삼켜 " + mag("r") + " 최대 체력 " + M + "마법 피해" + E + "와 대상 최대 체력 {r_thp}% 고정 피해.",
        "names": ("혀 채찍", "심연 잠수", "집어삼키기"),
    },
    "ja": {
        "name": "タム・ケンチ",
        "attack": O + "舌慣らし" + E + "：通常攻撃に" + PAS + "最大体力の" + M + "魔法ダメージ" + E + "追加、通常攻撃・Q・Wがチャンピオンにスタック（最大" + A + "3" + E + "）。" +
                  O + "ゆるゆる皮膜" + E + "：被ダメージ{e_red}%軽減、敵チャンピオン2体に囲まれると" + SHIELD + "のシールド。",
        "skill": "舌で最初のユニットを打ち" + mag("q") + "最大体力の" + M + "魔法ダメージ" + E + "と" + R + "{q_slow}%スロウ" + E + "（" + A + "{q_slow_t}秒" + E +
                 "）。チャンピオンなら" + HEAL + "回復しスタック、" + A + "3" + E + "で" + R + "{q_stun}秒スタン" + E + "。",
        "skill2": A + "{w_up}秒" + E + "地中に潜り（対象不可）対象の位置に飛び出し" + mag("w") + "最大体力の" + M + "魔法ダメージ" + E + "と" + R + "{w_air}秒ノックアップ" + E + "。",
        "ult": "敵に囲まれ行動妨害を受けた味方を" + A + "{r_ally_t}秒" + E + "丸呑みし吐き出す時" + RSH + "のシールド。または" + A + "3" + E +
               "スタックの敵チャンピオンを" + A + "{r_t}秒" + E + "丸呑みし" + mag("r") + "最大体力の" + M + "魔法ダメージ" + E + "と最大体力{r_thp}%の確定ダメージ。",
        "names": ("味見", "川潜り", "丸呑み"),
    },
}

C = "league_tahmkench_sfx_"
S_ = "league_tahmkench_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + c, vol, dl)] for k, c, vol, dl in [
    ("a_swing", "a_swing", 0.45, 0.0), ("a_hit", "a_hit", 0.45, 0.0), ("p_stack", "p_stack", 0.5, 0.0),
    ("q", "q", 0.55, 0.0), ("q_hit", "q_hit", 0.55, 0.0), ("q_stun", "q_stun", 0.6, 0.0), ("q_heal", "q_heal", 0.45, 0.0),
    ("w", "w", 0.55, 0.0), ("w_warn", "w_warn", 0.5, 0.0), ("w_land", "w_land", 0.6, 0.0),
    ("e_shield", "e_shield", 0.55, 0.0), ("r_enemy", "r_enemy", 0.65, 0.0), ("r_ally", "r_ally", 0.6, 0.0),
    ("r_spit", "r_spit", 0.6, 0.0),
    ("vo_q", "vo_q", 0.8, 0.0), ("vo_w", "vo_w", 0.8, 0.0), ("vo_e", "vo_e", 0.8, 0.0), ("vo_r", "vo_r", 0.85, 0.0)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_hp", "e_red", "e_sh", "e_sh_ap", "q_dmg", "q_ap", "q_hp", "q_slow", "q_heal",
                           "q_heal_ap", "w_dmg", "w_ap", "w_hp", "r_dmg", "r_ap", "r_hp", "r_thp", "r_sh", "r_sh_ap")}
    v.update({k: secs(p[k]) for k in ("q_slow_t", "q_stun", "w_up", "w_air", "r_t", "r_ally_t")})
    return v


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def load(path):
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


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
    ap.add_argument("--params")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--face", help="X,Y from tfm2_ase.py face")
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 - the idle's top), when the top is above -28")
    a = ap.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
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

    i18n = load(os.path.join(MOD, "text", "champion.i18n"))
    for lang, (d, names) in tx.items():
        i18n[lang]["description"][ID] = d
        i18n[lang]["skill_name"][ID] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    for name, plays in SOUNDS.items():
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"))
    for k in [k for k in ov if ID in k]:      # his keys rebuilt (a renamed sound leaves none behind)
        del ov[k]
    for name in list(SOUNDS) + CLIPS:
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/league/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    view = json.loads(json.dumps(VIEW))
    if a.face:
        x, y = (int(v) for v in a.face.split(","))
        view["face"] = {"x": x, "y": y}
    if a.banpick is not None:
        if a.banpick > 0:
            sys.exit("never a positive banpick_center y (card-banpick rule)")
        view["banpick_center"] = {"x": 0, "y": a.banpick}
    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"))
    cv["entries"][ID] = view
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"))
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    if "Tahm Kench" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Tahm Kench. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
