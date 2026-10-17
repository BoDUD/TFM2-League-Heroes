"""Mordekaiser's text (5 languages), sound_info files and his keys in the shared files, numbers from build_mordekaiser.P.

    python tools/kit/setup_mordekaiser.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_mordekaiser in every language, description + skill_name),
sound/sfx/league_mordekaiser_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre
and the ban/pick card's point once the sprite is in), mod.mod_info (0.104.0, Mordekaiser named). Only his keys change in
the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's
TOOLTIP_MAX.
Names: the client's zh_CN string table (莫德凯撒 / 铁铠冥魂; 黑暗起兮, 破灭之锤, 不坏之身, 断魂一扼, 轮回绝境; the client swaps
name and title) and Data Dragon 16.20.1 (zh_TW 魔鬥凱薩 / 暗崛 / 泯殺 / 不滅之軀 / 死之爪 / 死亡領域, ja モルデカイザー / 無窮の闇 /
滅魂の一撃 / 不滅の鎧 / 死の呪縛 / 死の国, ko 모데카이저 / 암흑 탄생 / 말살 / 불멸 / 죽음의 손아귀 / 죽음의 세계). Slots: skill = Q,
skill2 = E (Indestructible, W, told in its text), ult = R; the passive is told in the attack's text. No combo sentence
in any text (the user's rule). No `league_mordekaiser_attack` sound: the engine would play it at the start of every
attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_mordekaiser import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_mordekaiser"
VERSION = "0.104.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G_ = "<#7ee87eff>"     # heals, shields
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face)
VIEW = {"face": {"x": 1, "y": -30}, "center": {"x": 0, "y": -14}}   # at hd.rs SIZES 1.10 (tools/art/ppu_restyle.py RESTYLE mordekaiser face_to)


def mag(k):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_ap}}%{E}"


def aura():
    return f"{M}{{p_dmg}}{E} + {APi}{M}{{p_ap}}%{E} + {HPi}{M}{{p_hp}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "莫德凯撒",
        "attack": O + "黑暗起兮" + E + "：普攻附带" + APi + M + "{a_ap}%魔法伤害" + E + "。普攻、Q、E命中英雄叠层，3层时移速+{p_ms}%，每" + A +
                  "{p_per}秒" + E + "对周围敌人造成" + aura() + M + "魔法伤害" + E + "。",
        "skill": "挥锤砸向前方一条直线，造成" + mag("q") + M + "魔法伤害" + E + "；只砸中一个敌人时改为" + mag("q_iso") + "。",
        "skill2": "甩出断魂之爪，造成" + mag("e") + M + "魔法伤害" + E + "并把敌人" + R + "拉到身前" + E + "。冷却中被英雄贴近时改为" + O +
                  "不坏之身" + E + "：获得" + G_ + "{w_sh}" + E + " + " + APi + G_ + "{w_ap}%护盾" + E + "，护盾仍在时回复" + G_ +
                  "{w_heal}" + E + " + " + APi + G_ + "{w_heal_ap}%生命" + E + "。",
        "ult": "诅咒一名敌方英雄" + A + "{r_t}秒" + E + "：偷取其{r_steal}%攻击、法强、护甲、魔抗和生命，逃远会被" + R + "拉回" + E + "；期间将其击杀则回复" + G_ + "{r_kill}" + E + " + " + APi + G_ + "{r_kill_ap}%生命" + E + "。",
        "names": ("破灭之锤", "断魂一扼", "轮回绝境"),
    },
    "zh-hant": {
        "name": "魔鬥凱薩",
        "attack": O + "暗崛" + E + "：普攻附帶" + APi + M + "{a_ap}%魔法傷害" + E + "。普攻、Q、E命中英雄疊層，3層時移速+{p_ms}%，每" + A +
                  "{p_per}秒" + E + "對周圍敵人造成" + aura() + M + "魔法傷害" + E + "。",
        "skill": "揮錘砸向前方一條直線，造成" + mag("q") + M + "魔法傷害" + E + "；只砸中一個敵人時改為" + mag("q_iso") + "。",
        "skill2": "甩出死之爪，造成" + mag("e") + M + "魔法傷害" + E + "並把敵人" + R + "拉到身前" + E + "。冷卻中被英雄貼近時改為" + O +
                  "不滅之軀" + E + "：獲得" + G_ + "{w_sh}" + E + " + " + APi + G_ + "{w_ap}%護盾" + E + "，護盾仍在時回復" + G_ +
                  "{w_heal}" + E + " + " + APi + G_ + "{w_heal_ap}%生命" + E + "。",
        "ult": "詛咒一名敵方英雄" + A + "{r_t}秒" + E + "：偷取其{r_steal}%攻擊、法強、護甲、魔抗和生命，逃遠會被" + R + "拉回" + E + "；期間將其擊殺則回復" + G_ + "{r_kill}" + E + " + " + APi + G_ + "{r_kill_ap}%生命" + E + "。",
        "names": ("泯殺", "死之爪", "死亡領域"),
    },
    "en": {
        "name": "Mordekaiser",
        "attack": O + "Darkness Rise" + E + ": his attacks deal " + APi + M + "{a_ap}% magic damage" + E + " more. Attacks, Q and E "
                  "hitting champions stack it; at 3 stacks he moves {p_ms}% faster and deals " + aura() + " " + M + "magic damage" + E +
                  " to enemies around him every " + A + "{p_per}s" + E + ".",
        "skill": "Slams his mace down a line ahead for " + mag("q") + " " + M + "magic damage" + E + "; hitting a single enemy, " +
                 mag("q_iso") + " instead.",
        "skill2": "Lashes out a grasp for " + mag("e") + " " + M + "magic damage" + E + ", " + R + "pulling" + E + " enemies to him. On "
                  "cooldown with a champion close: " + O + "Indestructible" + E + ", a " + G_ + "{w_sh}" + E + " + " + APi + G_ +
                  "{w_ap}% shield" + E + "; if it still holds, he heals " + G_ + "{w_heal}" + E + " + " + APi + G_ + "{w_heal_ap}%" + E +
                  ".",
        "ult": "Curses an enemy champion for " + A + "{r_t}s" + E + ": steals {r_steal}% of its attack, ability power, armour, magic "
               "resistance and health and " + R + "drags it back" + E +
               " if it runs. Killing it meanwhile heals him " + G_ + "{r_kill}" + E + " + " + APi + G_ + "{r_kill_ap}%" + E + ".",
        "names": ("Obliterate", "Death's Grasp", "Realm of Death"),
    },
    "ko": {
        "name": "모데카이저",
        "attack": O + "암흑 탄생" + E + ": 기본 공격이 " + APi + M + "{a_ap}% 마법 피해" + E + " 추가. 기본 공격·Q·E로 챔피언 적중 시 중첩, "
                  "3중첩이면 이동 속도 {p_ms}% 증가, " + A + "{p_per}초" + E + "마다 주변 적에게 " + aura() + " " + M + "마법 피해" + E + ".",
        "skill": "전방 직선을 철퇴로 내리쳐 " + mag("q") + " " + M + "마법 피해" + E + ", 적 하나만 맞히면 " + mag("q_iso") + ".",
        "skill2": "손아귀를 뻗어 " + mag("e") + " " + M + "마법 피해" + E + "를 주고 적을 " + R + "끌어당김" + E + ". 재사용 대기 중 챔피언이 "
                  "붙으면 " + O + "불멸" + E + ": " + G_ + "{w_sh}" + E + " + " + APi + G_ + "{w_ap}% 보호막" + E + ", 보호막이 남아 있으면 " +
                  G_ + "{w_heal}" + E + " + " + APi + G_ + "{w_heal_ap}%" + E + " 회복.",
        "ult": "적 챔피언을 " + A + "{r_t}초" + E + " 저주: 공격력·주문력·방어력·마법 저항력·체력 {r_steal}% 강탈, 도망치면 " + R + "끌어옴" + E + ". 그동안 처치하면 " + G_ + "{r_kill}" + E + " + " + APi + G_ +
               "{r_kill_ap}%" + E + " 회복.",
        "names": ("말살", "죽음의 손아귀", "죽음의 세계"),
    },
    "ja": {
        "name": "モルデカイザー",
        "attack": O + "無窮の闇" + E + "：通常攻撃に" + APi + M + "{a_ap}%魔法ダメージ" + E + "追加。通常攻撃・Q・Eがチャンピオンに当たるとスタック、"
                  "3スタックで移動速度{p_ms}%増加、" + A + "{p_per}秒" + E + "ごとに周囲の敵に" + aura() + "の" + M + "魔法ダメージ" + E + "。",
        "skill": "前方の直線を鉄槌で叩き" + mag("q") + "の" + M + "魔法ダメージ" + E + "、敵1体だけなら" + mag("q_iso") + "。",
        "skill2": "呪縛の手を放ち" + mag("e") + "の" + M + "魔法ダメージ" + E + "、敵を" + R + "引き寄せる" + E + "。CD中に敵が接近すると" + O +
                  "不滅の鎧" + E + "：" + G_ + "{w_sh}" + E + " + " + APi + G_ + "{w_ap}%のシールド" + E + "、残っていれば" + G_ + "{w_heal}" +
                  E + " + " + APi + G_ + "{w_heal_ap}%" + E + "回復。",
        "ult": "敵チャンピオンを" + A + "{r_t}秒" + E + "呪う：攻撃力・魔力・物防・魔防・体力の{r_steal}%を奪い、逃げると" + R + "引き戻す" + E + "。その間に倒すと" + G_ + "{r_kill}" + E + " + " + APi + G_ + "{r_kill_ap}%" +
               E + "回復。",
        "names": ("滅魂の一撃", "死の呪縛", "死の国"),
    },
}

C = "league_mordekaiser_sfx_"
S_ = "league_mordekaiser_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + c, vol, dl)] for k, c, vol, dl in [
    ("a_swing", "a_swing", 0.45, 0.0), ("a_hit", "a_hit", 0.4, 0.0), ("p_on", "p_on", 0.5, 0.0),
    ("q", "q", 0.55, 0.0), ("q_hit", "q_hit", 0.55, 0.0), ("e", "e", 0.55, 0.0), ("e_hit", "e_hit", 0.5, 0.0),
    ("w", "w", 0.55, 0.0), ("w_heal", "w_heal", 0.5, 0.0), ("r", "r", 0.65, 0.0), ("r_win", "r_win", 0.6, 0.0),
    ("vo_q", "vo_q", 0.85, 0.0), ("vo_e", "vo_e", 0.85, 0.0), ("vo_w", "vo_w", 0.85, 0.0), ("vo_r", "vo_r", 0.9, 0.0)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("a_ap", "p_ms", "p_dmg", "p_ap", "p_hp", "q_dmg", "q_ap", "q_iso_dmg", "q_iso_ap", "e_dmg",
                           "e_ap", "w_sh", "w_ap", "w_heal", "w_heal_ap", "r_steal", "r_kill", "r_kill_ap")}
    v.update({k: secs(p[k]) for k in ("p_per", "r_t")})
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
    if "Mordekaiser" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Mordekaiser. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
