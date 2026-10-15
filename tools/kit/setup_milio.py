"""Milio's text (5 languages), sound_info files and his keys in the shared files, numbers from build_milio.P.

    python tools/kit/setup_milio.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_milio in every language, description + skill_name),
sound/sfx/league_milio_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.113.0, Milio named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (米利欧 / 明烛 - the client swaps name and title, as for Smolder; 热情洋溢！,
火爆飞踢, 依依不舍, 融融情谊, 生生不息) and Data Dragon 16.20.1 (zh_TW 米里歐 / 爐火餘溫 / 究極火焰球 / 舒適營火 / 溫暖擁抱 /
賦生燄息, ja ミリオ / ファイヤーアップ！ / ウルトラメガファイヤーキック / 癒しの焚き火 / 抱擁のぬくもり / 生命の息吹, ko 밀리오 /
타오르는 힘 / 초특급 불꽃 킥 / 아늑한 모닥불 / 따스한 포옹 / 생명의 온기).
Slots: skill = Q, skill2 = E + W (the campfire rides the hug), ult = R; the passive (Fired Up!) is told in the attack's
text. No combo sentence in any text (the user's rule). No `league_milio_attack` sound: the engine would play it at the
start of every attack; the attack plays its own from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_milio import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_milio"
VERSION = "0.113.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
C = "<#ef5350ff>"      # crowd control
S = "<#9fd8ffff>"      # shields
G = "<#7cfc00ff>"      # heals
E = "<>"
# champion_view: the face point at his crown (tools/art/rig_milio.py face_point; ppu_restyle RESTYLE milio face_to)
VIEW = {"face": {"x": 0, "y": -30}, "center": {"x": 0, "y": -12}}


def mag(k):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_ap}}%{E}"


SH = S + "{e_sh}" + E + " + " + APi + S + "{e_ap}%" + E
WH = G + "{w_h}" + E + " + " + APi + G + "{w_hap}%" + E
RH = G + "{r_heal}" + E + " + " + APi + G + "{r_hap}%" + E

TEXT = {
    "zh-hans": {
        "name": "米利欧",
        "attack": "射出小火球。被动" + O + "热情洋溢！" + E + "：技能触及的友方获得" + A + "{p_atk}%" + E + "攻击力和法术强度（" + A + "{p_t}秒" + E +
                  "），米利欧获得" + A + "{p_ms}%" + E + "移速。",
        "skill": "踢出火球，击退命中的第一个敌人，随后火球落下，对周围敌人造成" + mag("q") + M + "魔法伤害" + E + "并" + C + "减速{q_slow}%" + E +
                 "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": O + "融融情谊" + E + "（2次）：友方英雄获得" + SH + S + "护盾" + E + "和" + A + "{e_ms}%" + E + "移速（" + A + "{e_t}秒" + E + "）。" +
                  O + "依依不舍" + E + "：在其身上点燃营火" + A + "{w_t}秒" + E + "，每" + A + "{w_p}秒" + E + "治疗周围友方" + WH + "并增加攻击距离。",
        "ult": "友方被控制或被敌人贴身时，为周围友方英雄恢复" + RH + "生命，" + C + "免疫控制{r_imm}秒" + E + "并获得" + A + "{r_ten}%" + E + "韧性（" + A +
               "{r_tt}秒" + E + "）。",
        "names": ("火爆飞踢", "融融情谊 / 依依不舍", "生生不息"),
    },
    "zh-hant": {
        "name": "米里歐",
        "attack": "射出小火球。被動" + O + "爐火餘溫" + E + "：技能觸及的友軍獲得" + A + "{p_atk}%" + E + "攻擊力和魔法攻擊（" + A + "{p_t}秒" + E +
                  "），米里歐獲得" + A + "{p_ms}%" + E + "跑速。",
        "skill": "踢出火球，擊退命中的第一個敵人，隨後火球落下，對周圍敵人造成" + mag("q") + M + "魔法傷害" + E + "並" + C + "緩速{q_slow}%" + E +
                 "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": O + "溫暖擁抱" + E + "（2次）：友方英雄獲得" + SH + S + "護盾" + E + "和" + A + "{e_ms}%" + E + "跑速（" + A + "{e_t}秒" + E + "）。" +
                  O + "舒適營火" + E + "：在其身上點燃營火" + A + "{w_t}秒" + E + "，每" + A + "{w_p}秒" + E + "治療周圍友軍" + WH + "並增加攻擊距離。",
        "ult": "友軍被控場或被敵人貼身時，為周圍友方英雄恢復" + RH + "生命，" + C + "免疫控場{r_imm}秒" + E + "並獲得" + A + "{r_ten}%" + E + "韌性（" + A +
               "{r_tt}秒" + E + "）。",
        "names": ("究極火焰球", "溫暖擁抱 / 舒適營火", "賦生燄息"),
    },
    "en": {
        "name": "Milio",
        "attack": "Throws a small fireball. Passive " + O + "Fired Up!" + E + ": allies his spells touch gain " + A + "{p_atk}%" + E +
                  " attack and ability power for " + A + "{p_t}s" + E + "; Milio gains " + A + "{p_ms}%" + E + " move speed.",
        "skill": "Kicks a fireball that knocks back the first enemy hit, then falls on it: enemies around take " + mag("q") + " " + M +
                 "magic damage" + E + " and are " + C + "slowed by {q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": O + "Warm Hugs" + E + " (2 charges): an allied champion gains a " + SH + " " + S + "shield" + E + " and " + A + "{e_ms}%" + E +
                  " move speed for " + A + "{e_t}s" + E + ". " + O + "Cozy Campfire" + E + ": a fire follows them for " + A + "{w_t}s" + E +
                  ", every " + A + "{w_p}s" + E + " healing allies nearby " + WH + " and extending their attack range.",
        "ult": "When an ally is crowd-controlled or an enemy closes in, allied champions around him heal " + RH + ", are " + C +
               "immune to crowd control for {r_imm}s" + E + " and gain " + A + "{r_ten}%" + E + " tenacity for " + A + "{r_tt}s" + E + ".",
        "names": ("Ultra Mega Fire Kick", "Warm Hugs / Cozy Campfire", "Breath of Life"),
    },
    "ko": {
        "name": "밀리오",
        "attack": "작은 불덩이를 던집니다. 기본 지속 효과 " + O + "타오르는 힘" + E + ": 스킬이 닿은 아군은 " + A + "{p_t}초" + E + " 동안 공격력과 주문력이 " +
                  A + "{p_atk}%" + E + " 증가, 밀리오는 이동 속도 " + A + "{p_ms}%" + E + ".",
        "skill": "불덩이를 차서 처음 맞힌 적을 밀어내고, 떨어지며 주변 적에게 " + mag("q") + " " + M + "마법 피해" + E + "와 " + A + "{q_slow_t}초" + E +
                 " 동안 " + C + "{q_slow}% 둔화" + E + ".",
        "skill2": O + "따스한 포옹" + E + "(2회): 아군 챔피언에게 " + SH + " " + S + "보호막" + E + "과 이동 속도 " + A + "{e_ms}%" + E + "(" + A + "{e_t}초" + E +
                  "). " + O + "아늑한 모닥불" + E + ": " + A + "{w_t}초" + E + " 동안 따라다니며 " + A + "{w_p}초" + E + "마다 주변 아군 " + WH +
                  " 회복, 사거리 증가.",
        "ult": "아군이 군중 제어되거나 적이 붙으면 주변 아군 챔피언이 " + RH + " 회복, " + C + "{r_imm}초 군중 제어 면역" + E + ", " + A + "{r_tt}초" + E +
               " 동안 강인함 " + A + "{r_ten}%" + E + ".",
        "names": ("초특급 불꽃 킥", "따스한 포옹 / 아늑한 모닥불", "생명의 온기"),
    },
    "ja": {
        "name": "ミリオ",
        "attack": "小さな火の玉を投げる。自動効果" + O + "ファイヤーアップ！" + E + "：スキルが触れた味方は" + A + "{p_t}秒" + E + "攻撃力と魔力" + A +
                  "{p_atk}%" + E + "増加、ミリオは移動速度" + A + "{p_ms}%" + E + "。",
        "skill": "火の玉を蹴り、最初の敵をノックバック、落ちた火の玉が周囲の敵に" + mag("q") + "の" + M + "魔法ダメージ" + E + "と" + A + "{q_slow_t}秒" + E +
                 C + "{q_slow}%スロウ" + E + "。",
        "skill2": O + "抱擁のぬくもり" + E + "（2回）：味方チャンピオンに" + SH + "の" + S + "シールド" + E + "と移動速度" + A + "{e_ms}%" + E + "（" + A +
                  "{e_t}秒" + E + "）。" + O + "癒しの焚き火" + E + "：" + A + "{w_t}秒" + E + "付き添い、" + A + "{w_p}秒" + E + "ごとに周囲の味方を" + WH +
                  "回復、射程増加。",
        "ult": "味方が行動妨害を受けるか敵に接近された時、周囲の味方チャンピオンを" + RH + "回復、" + C + "{r_imm}秒行動妨害無効" + E + "、" + A + "{r_tt}秒" + E +
               "行動妨害耐性" + A + "{r_ten}%" + E + "。",
        "names": ("ウルトラメガファイヤーキック", "抱擁のぬくもり / 癒しの焚き火", "生命の息吹"),
    },
}


S_ = "league_milio_"
CL = "league_milio_sfx_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(CL + k, vol, 0.0)] for k, vol in [
    ("a_cast", 0.4), ("a_hit", 0.4), ("q_kick", 0.5), ("q_hit", 0.5), ("q_land", 0.55), ("e_hug", 0.5),
    ("w_fire", 0.5), ("w_pulse", 0.3), ("r_cast", 0.6), ("r_hit", 0.4), ("p_fired", 0.35),
    ("vo_q", 0.7), ("vo_e", 0.7), ("vo_w", 0.7), ("vo_r", 0.75)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_atk", "p_ms", "q_dmg", "q_ap", "q_slow", "e_sh", "e_ap", "e_ms", "w_h", "w_hap",
                           "r_heal", "r_hap", "r_ten")}
    v.update({k: secs(p[k]) for k in ("p_t", "q_slow_t", "e_t", "w_t", "w_p", "r_imm", "r_tt")})
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
    if "Milio" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Milio. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
