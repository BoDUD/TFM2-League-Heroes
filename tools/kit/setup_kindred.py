"""Kindred's text (5 languages), sound_info files and her keys in the shared files, numbers from build_kindred.P.

    python tools/kit/setup_kindred.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_kindred in every language, description + skill_name),
sound/sfx/league_kindred_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.109.0, Kindred named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (千珏 / 永猎双子; 千珏之印, 乱箭之舞, 狼灵狂热, 横生惧意, 羊灵生息; Data Dragon's
zh_CN swaps name and title) and Data Dragon 16.20.1 (zh_TW 鏡爪 / 鏡爪印記 / 舞動箭矢 / 魔狼狂熱 / 恐懼蔓延 / 神羊喘息,
ja キンドレッド / キンドレッドの刻印 / 矢の輪舞 / 狼の激昂 / 忍び寄る恐怖 / 羊の執行猶予, ko 킨드레드 / 킨드레드의 표식 /
화살 세례 / 늑대의 광기 / 차오르는 공포 / 양의 안식처).
Slots: skill = Q, skill2 = E + W, ult = R; the passive (the marks) is told in the attack's text. No combo sentence in
any text (the user's rule). No `league_kindred_attack` sound: the engine would play it at the start of every attack;
the release plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_kindred import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_kindred"
VERSION = "0.109.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
D = "<#ff8a65ff>"      # physical damage
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7dd87dff>"      # heals
E = "<>"
# champion_view: the face tfm2_ase.py face suggests on the sheet (league/champions/league_kindred, idle final 2026-10-14:
# crown 34 px above the feet, head centre x -0.9 -> at the crown, 1.5 px ahead)
VIEW = {"face": {"x": 1, "y": -34}, "center": {"x": 0, "y": -12}}


def phys(k):
    return f"{D}{{{k}_dmg}}{E}+{ADi}{D}{{{k}_ratio}}%{E}"


HEAL = G + "{r_heal}" + E + "+" + ADi + G + "{r_heal_ad}%" + E

TEXT = {
    "zh-hans": {
        "name": "千珏",
        "attack": O + "千珏之印" + E + "：羊灵射箭。参与击杀被她攻击过的敌方英雄获得一层印记（阵亡清空）：射程+{p_range}、攻速+{p_as}%、" + O + "横生惧意" + E +
                  "+" + M + "{p_e}魔法伤害" + E + "。",
        "skill": "跃动一小段（被近身时向后），向附近最多" + A + "3名" + E + "敌人各射一箭，造成" + phys("q") + D + "物理伤害" + E + "，攻速+{q_as}%持续" + A + "{q_as_t}秒" + E +
                 "。在" + O + "狼灵狂热" + E + "内冷却" + A + "{q_zone}秒" + E + "。",
        "skill2": O + "横生惧意" + E + "：标记敌人并" + R + "减速{e_slow}%" + E + "，此后第" + A + "3次" + E + "攻击命中时狼灵扑咬被标记者，造成" + phys("e") + D + "物理伤害" + E +
                  "（英雄额外{e_hp}%最大生命）。冷却时放" + O + "狼灵狂热" + E + "：" + A + "{w_t}秒" + E + "领域，狼灵{w_every}撕咬其中一个敌人，造成" + phys("w") + D +
                  "物理伤害" + E + "。",
        "ult": "交战中友方英雄被控制、或被敌方英雄贴身时，祝福身边区域：" + A + "{r_t}秒" + E + "内其中的友方英雄不会阵亡，结束时回复" + HEAL + "生命。",
        "names": ("乱箭之舞", "横生惧意 / 狼灵狂热", "羊灵生息"),
    },
    "zh-hant": {
        "name": "鏡爪",
        "attack": O + "鏡爪印記" + E + "：射出箭矢。參與擊殺被她攻擊過的敵方英雄獲得一層印記（陣亡清空）：射程+{p_range}、攻速+{p_as}%、" + O + "恐懼蔓延" + E +
                  "+" + M + "{p_e}魔法傷害" + E + "。",
        "skill": "躍動一小段（被近身時向後），向附近最多" + A + "3名" + E + "敵人各射一箭，造成" + phys("q") + D + "物理傷害" + E + "，攻速+{q_as}%持續" + A + "{q_as_t}秒" + E +
                 "。在" + O + "魔狼狂熱" + E + "內冷卻" + A + "{q_zone}秒" + E + "。",
        "skill2": O + "恐懼蔓延" + E + "：標記敵人並" + R + "緩速{e_slow}%" + E + "，此後第" + A + "3次" + E + "攻擊命中時魔狼撲咬被標記者，造成" + phys("e") + D + "物理傷害" + E +
                  "（英雄額外{e_hp}%最大生命）。冷卻時放" + O + "魔狼狂熱" + E + "：" + A + "{w_t}秒" + E + "領域，魔狼{w_every}撕咬其中一個敵人，造成" + phys("w") + D +
                  "物理傷害" + E + "。",
        "ult": "交戰中友方英雄被控制、或被敵方英雄貼身時，祝福身邊區域：" + A + "{r_t}秒" + E + "內其中的友方英雄不會陣亡，結束時回復" + HEAL + "生命。",
        "names": ("舞動箭矢", "恐懼蔓延／魔狼狂熱", "神羊喘息"),
    },
    "en": {
        "name": "Kindred",
        "attack": O + "Mark of the Kindred" + E + ": Lamb's arrows. Each takedown of an enemy champion she hit gives a mark (lost on death): +{p_range} range, "
                  "+{p_as}% attack speed, " + O + "Mounting Dread" + E + " +" + M + "{p_e} magic damage" + E + ".",
        "skill": "Leaps a short way (back when an enemy closes in) and shoots an arrow at each of up to " + A + "3" + E + " nearby enemies for " + phys("q") + " " + D +
                 "physical damage" + E + "; +{q_as}% attack speed for " + A + "{q_as_t}s" + E + ". Inside " + O + "Wolf's Frenzy" + E + " the cooldown is " + A +
                 "{q_zone}s" + E + ".",
        "skill2": O + "Mounting Dread" + E + ": marks an enemy and " + R + "slows it {e_slow}%" + E + "; her " + A + "3rd" + E + " attack hit after it sends Wolf at the marked one for " +
                  phys("e") + " " + D + "physical damage" + E + " (+{e_hp}% max health on champions). On cooldown, " + O + "Wolf's Frenzy" + E + ": for " + A + "{w_t}s" + E + " a" +
                  " zone where Wolf bites one enemy {w_every} for " + phys("w") + " " + D + "physical damage" + E + ".",
        "ult": "In a fight, when an allied champion is crowd-controlled or an enemy champion closes in, she blesses the ground around her: for " + A + "{r_t}s" + E +
               " allied champions in it cannot die, then they heal " + HEAL + ".",
        "names": ("Dance of Arrows", "Mounting Dread / Wolf's Frenzy", "Lamb's Respite"),
    },
    "ko": {
        "name": "킨드레드",
        "attack": O + "킨드레드의 표식" + E + ": 양의 화살. 공격한 적 챔피언 처치에 관여하면 표식 획득(사망 시 소멸): 사거리 +{p_range}, 공격 속도 +{p_as}%, " + O + "차오르는 공포" + E +
                  " " + M + "마법 피해 +{p_e}" + E + ".",
        "skill": "짧게 도약(적이 붙으면 뒤로)한 뒤 주변 적 최대 " + A + "3명" + E + "에게 화살을 한 발씩 쏴 " + phys("q") + " " + D + "물리 피해" + E + ", 공격 속도 +{q_as}% (" + A +
                 "{q_as_t}초" + E + "). " + O + "늑대의 광기" + E + " 안에서는 재사용 대기시간 " + A + "{q_zone}초" + E + ".",
        "skill2": O + "차오르는 공포" + E + ": 적에게 표식을 남기고 " + R + "{e_slow}% 둔화" + E + "; 이후 " + A + "3번째" + E + " 공격이 적중하면 늑대가 표식 대상을 덮쳐 " + phys("e") + " " + D +
                  "물리 피해" + E + "(챔피언은 최대 체력의 {e_hp}% 추가). 재사용 대기 중에는 " + O + "늑대의 광기" + E + ": " + A + "{w_t}초" + E + " 영역, 늑대가 {w_every} 적 하나를 물어 " +
                  phys("w") + " " + D + "물리 피해" + E + ".",
        "ult": "교전 중 아군 챔피언이 군중 제어를 받거나 적 챔피언이 붙으면 주변을 축복: " + A + "{r_t}초" + E + " 동안 안의 아군 챔피언은 죽지 않고, 끝날 때 " + HEAL + " 회복.",
        "names": ("화살 세례", "차오르는 공포 / 늑대의 광기", "양의 안식처"),
    },
    "ja": {
        "name": "キンドレッド",
        "attack": O + "キンドレッドの刻印" + E + "：ラムの矢。攻撃した敵チャンピオンのキルに関与すると刻印（死亡で消滅）：射程+{p_range}、攻撃速度+{p_as}%、" + O + "忍び寄る恐怖" + E +
                  "の" + M + "魔法ダメージ+{p_e}" + E + "。",
        "skill": "短く跳び（詰められたら後ろへ）、周囲の敵最大" + A + "3体" + E + "に矢を1本ずつ放ち" + phys("q") + "の" + D + "物理ダメージ" + E + "、攻撃速度+{q_as}%（" + A +
                 "{q_as_t}秒" + E + "）。" + O + "狼の激昂" + E + "の中ではクールダウン" + A + "{q_zone}秒" + E + "。",
        "skill2": O + "忍び寄る恐怖" + E + "：敵に刻印し" + R + "{e_slow}%スロウ" + E + "。その後" + A + "3回目" + E + "の攻撃でウルフが飛びかかり" + phys("e") + "の" + D + "物理ダメージ" + E +
                  "（チャンピオンは最大体力の{e_hp}%追加）。CD中は" + O + "狼の激昂" + E + "：" + A + "{w_t}秒" + E + "の領域、ウルフが{w_every}敵1体を噛み" + phys("w") + "の" + D +
                  "物理ダメージ" + E + "。",
        "ult": "戦闘中、味方チャンピオンが行動妨害を受けるか敵チャンピオンに詰められると周囲を祝福：" + A + "{r_t}秒" + E + "間、中の味方チャンピオンは倒れず、終了時に" + HEAL + "回復。",
        "names": ("矢の輪舞", "忍び寄る恐怖/狼の激昂", "羊の執行猶予"),
    },
}

C = "league_kindred_sfx_"
S_ = "league_kindred_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + k, vol, 0.0)] for k, vol in [
    ("a_shot", 0.45), ("a_hit", 0.45), ("q", 0.5), ("q_arrows", 0.5), ("q_hit", 0.45), ("e", 0.5), ("e_shot", 0.5),
    ("e_hit", 0.5), ("e_bite", 0.6), ("w", 0.55), ("w_bite", 0.45), ("r", 0.6), ("r_heal", 0.5), ("p", 0.55),
    ("vo_q", 0.8), ("vo_w", 0.8), ("vo_e", 0.8), ("vo_r", 0.85)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("q_dmg", "q_ratio", "q_as", "e_slow", "e_dmg", "e_ratio", "e_hp", "w_dmg", "w_ratio",
                           "r_heal", "r_heal_ad", "p_as")}
    v.update({k: secs(p[k]) for k in ("q_as_t", "w_t", "w_per", "r_t")})
    v["q_zone"] = secs(p["q_cd"] * 100 // (100 + p["w_cdr"]))
    v["p_range"] = p["p_range"] // 100
    v["p_e"] = p["e_mark_ap"] * p["p_ap"] // 100
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


# the Wolf's bite interval in words: (once a second, every n seconds)
EVERY = {"zh-hans": ("每秒", "每{}秒"), "zh-hant": ("每秒", "每{}秒"), "en": ("every second", "every {}s"),
         "ko": ("매초", "{}초마다"), "ja": ("毎秒", "{}秒毎に")}


def texts(p):
    v = values(p)
    out = {}
    for lang, t in TEXT.items():
        d = {"name": t["name"]}
        one, many = EVERY[lang]
        v["w_every"] = one if p["w_per"] == 60 else many.format(secs(p["w_per"]))
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
    for k in [k for k in ov if ID + "_" in k]:      # her keys rebuilt (a renamed sound leaves none behind)
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
    if "Kindred" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Kindred. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
