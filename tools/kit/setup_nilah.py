"""Nilah's text (5 languages), sound_info files and her keys in the shared files, numbers from build_nilah.P.

    python tools/kit/setup_nilah.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_nilah in every language, description + skill_name),
sound/sfx/league_nilah_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.107.0, Nilah named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (尼菈 / 不羁之悦; 喜色川流, 游刃万变, 轻纱飞漾, 纵情逐流, 神恩激荡; the client swaps
name and title) and Data Dragon 16.20.1 (zh_TW 淣菈 / 樂無止境 / 百變之刃 / 歡躍面紗 / 湍流淩步 / 神之禮讚, ja ニーラ /
終わりなき喜び / 形なき刃 / 歓喜のヴェール / 流撃 / アポテオシス, ko 닐라 / 영원한 기쁨 / 무형의 검 / 승리의 장막 / 급류 / 환희).
Slots: skill = Q, skill2 = E + W, ult = R; the passive (the empowered attacks' heal) is told in the attack's text. No
combo sentence in any text (the user's rule). No `league_nilah_attack` sound: the engine would play it at the start of
every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_nilah import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_nilah"
VERSION = "0.107.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
D = "<#ff8a65ff>"      # physical damage
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
G = "<#7dd87dff>"      # heals, shields
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28); the face is
# where tools/art/ppu_restyle.py puts it for her 90 % frames (RESTYLE nilah face_to)
VIEW = {"face": {"x": -1, "y": -36}, "center": {"x": 0, "y": -12}}


def phys(k):
    return f"{D}{{{k}_dmg}}{E}+{ADi}{D}{{{k}_ratio}}%{E}"


RT = D + "{r_tdmg}" + E + "+" + ADi + D + "{r_tratio}%" + E
HEAL = G + "{r_heal}" + E + "+" + ADi + G + "{r_heal_ad}%" + E
SH = G + "{r_sh}" + E + "+" + ADi + G + "{r_sh_ad}%" + E

TEXT = {
    "zh-hans": {
        "name": "尼菈",
        "attack": O + "喜色川流" + E + "：鞭刃近战攻击。" + O + "游刃万变" + E + "后" + A + "{q_t}秒" + E + "内，射程+{q_add}，攻击扇形顺劈，额外造成" + ADi + D +
                  "{q_spl}%" + E + D + "物理伤害" + E + "，并回复伤害{q_vamp}%的生命。",
        "skill": "朝目标方向甩出鞭刃，对直线上的所有敌人造成" + phys("q") + D + "物理伤害" + E + "，并强化之后" + A + "{q_t}秒" + E + "的攻击。",
        "skill2": O + "纵情逐流" + E + "：穿过敌方英雄冲刺，落地对周围造成" + phys("e") + D + "物理伤害" + E + "，" + A + "2层" + E + "充能。用完时放" + O + "轻纱飞漾" + E +
                  "：" + A + "{w_t}秒" + E + "内闪避所有攻击，技能伤害-{w_mred}%，移速+{w_ms}%，附近友方英雄同样获得" + A + "{w_ally_t}秒" + E + "。",
        "ult": "旋转鞭刃" + A + "{r_t}秒" + E + "，每段造成" + RT + D + "物理伤害" + E + "，最后造成" + phys("r") + D + "物理伤害" + E + "并把周围敌人拉到身边；附近友方英雄回复" +
               HEAL + "生命并获得" + SH + "护盾。",
        "names": ("游刃万变", "纵情逐流 / 轻纱飞漾", "神恩激荡"),
    },
    "zh-hant": {
        "name": "淣菈",
        "attack": O + "樂無止境" + E + "：鞭刃近戰攻擊。" + O + "百變之刃" + E + "後" + A + "{q_t}秒" + E + "內，射程+{q_add}，攻擊扇形順劈，額外造成" + ADi + D +
                  "{q_spl}%" + E + D + "物理傷害" + E + "，並回復傷害{q_vamp}%的生命。",
        "skill": "朝目標方向甩出鞭刃，對直線上的所有敵人造成" + phys("q") + D + "物理傷害" + E + "，並強化之後" + A + "{q_t}秒" + E + "的攻擊。",
        "skill2": O + "湍流淩步" + E + "：穿過敵方英雄衝刺，落地對周圍造成" + phys("e") + D + "物理傷害" + E + "，" + A + "2層" + E + "充能。用完時放" + O + "歡躍面紗" + E +
                  "：" + A + "{w_t}秒" + E + "內閃避所有攻擊，技能傷害-{w_mred}%，跑速+{w_ms}%，附近友方英雄同樣獲得" + A + "{w_ally_t}秒" + E + "。",
        "ult": "旋轉鞭刃" + A + "{r_t}秒" + E + "，每段造成" + RT + D + "物理傷害" + E + "，最後造成" + phys("r") + D + "物理傷害" + E + "並把周圍敵人拉到身邊；附近友方英雄回復" +
               HEAL + "生命並獲得" + SH + "護盾。",
        "names": ("百變之刃", "湍流淩步／歡躍面紗", "神之禮讚"),
    },
    "en": {
        "name": "Nilah",
        "attack": O + "Joy Unending" + E + ": melee whip-blade attacks. For " + A + "{q_t}s" + E + " after " + O + "Formless Blade" + E + " they reach {q_add} farther, "
                  "cut a cone for " + ADi + D + "{q_spl}%" + E + " more " + D + "physical damage" + E + " and heal her for {q_vamp}% of the damage.",
        "skill": "Lashes her whip-blade in a line, dealing " + phys("q") + " " + D + "physical damage" + E + " to every enemy on it, and empowers her attacks for " +
                 A + "{q_t}s" + E + ".",
        "skill2": O + "Slipstream" + E + ": dashes through an enemy champion, dealing " + phys("e") + " " + D + "physical damage" + E + " around her landing; " + A +
                  "2 charges" + E + ". With both spent, " + O + "Jubilant Veil" + E + ": for " + A + "{w_t}s" + E + " she dodges every attack, takes {w_mred}% less "
                  "from abilities and gains {w_ms}% move speed; nearby allied champions get the same for " + A + "{w_ally_t}s" + E + ".",
        "ult": "Spins her whip-blade for " + A + "{r_t}s" + E + ", dealing " + RT + " " + D + "physical damage" + E + " a hit, then " + phys("r") + " " + D +
               "physical damage" + E + " and pulls nearby enemies to her; nearby allied champions heal " + HEAL + " and gain a " + SH + " shield.",
        "names": ("Formless Blade", "Slipstream / Jubilant Veil", "Apotheosis"),
    },
    "ko": {
        "name": "닐라",
        "attack": O + "영원한 기쁨" + E + ": 채찍검 근접 공격. " + O + "무형의 검" + E + " 후 " + A + "{q_t}초" + E + " 동안 사거리 +{q_add}, 공격이 부채꼴로 베어 " + ADi + D +
                  "{q_spl}%" + E + " " + D + "물리 피해" + E + "를 추가로 주고 피해의 {q_vamp}%만큼 회복.",
        "skill": "채찍검을 직선으로 휘둘러 모든 적에게 " + phys("q") + " " + D + "물리 피해" + E + ", 이후 " + A + "{q_t}초" + E + " 동안 공격 강화.",
        "skill2": O + "급류" + E + ": 적 챔피언을 관통해 돌진, 착지 지점 주변에 " + phys("e") + " " + D + "물리 피해" + E + ", " + A + "2회" + E + " 충전. 모두 쓰면 " + O +
                  "승리의 장막" + E + ": " + A + "{w_t}초" + E + " 동안 모든 공격 회피, 스킬 피해 -{w_mred}%, 이동 속도 +{w_ms}%; 주변 아군 챔피언도 " + A + "{w_ally_t}초" + E +
                  " 동안 같은 효과.",
        "ult": A + "{r_t}초" + E + " 동안 채찍검을 돌려 " + RT + " " + D + "물리 피해" + E + "를 반복, 마지막에 " + phys("r") + " " + D + "물리 피해" + E +
               "를 주고 주변 적을 끌어당김; 주변 아군 챔피언은 " + HEAL + " 회복, " + SH + " 보호막.",
        "names": ("무형의 검", "급류 / 승리의 장막", "환희"),
    },
    "ja": {
        "name": "ニーラ",
        "attack": O + "終わりなき喜び" + E + "：鞭刃の近接攻撃。" + O + "形なき刃" + E + "の後" + A + "{q_t}秒" + E + "、射程+{q_add}、扇状に斬り" + ADi + D +
                  "{q_spl}%" + E + "の" + D + "物理ダメージ" + E + "を追加、与ダメージの{q_vamp}%回復。",
        "skill": "鞭刃を直線に振るい、線上の全ての敵に" + phys("q") + "の" + D + "物理ダメージ" + E + "、その後" + A + "{q_t}秒" + E + "通常攻撃を強化。",
        "skill2": O + "流撃" + E + "：敵チャンピオンを突き抜けてダッシュ、着地点の周囲に" + phys("e") + "の" + D + "物理ダメージ" + E + "、" + A + "2回" + E + "チャージ。使い切ると" +
                  O + "歓喜のヴェール" + E + "：" + A + "{w_t}秒" + E + "全ての通常攻撃を回避、スキルダメージ-{w_mred}%、移動速度+{w_ms}%、周囲の味方も" + A + "{w_ally_t}秒" + E + "同じ効果。",
        "ult": A + "{r_t}秒" + E + "鞭刃を回し" + RT + "の" + D + "物理ダメージ" + E + "を繰り返し、最後に" + phys("r") + "の" + D + "物理ダメージ" + E + "と周囲の敵を引き寄せる；" +
               "周囲の味方は" + HEAL + "回復、" + SH + "のシールド。",
        "names": ("形なき刃", "流撃/歓喜のヴェール", "アポテオシス"),
    },
}

C = "league_nilah_sfx_"
S_ = "league_nilah_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + k, vol, 0.0)] for k, vol in [
    ("a_swing", 0.45), ("a_hit", 0.45), ("qa_swing", 0.45), ("qa_hit", 0.5), ("q", 0.55), ("q_hit", 0.55),
    ("eq", 0.55), ("eq_hit", 0.55), ("e", 0.5), ("e_hit", 0.55), ("w", 0.5), ("w_ally", 0.45), ("r", 0.6),
    ("r_hit", 0.45), ("r_pull", 0.6), ("r_heal", 0.5),
    ("vo_q", 0.8), ("vo_w", 0.8), ("vo_e", 0.8), ("vo_r", 0.85)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("q_dmg", "q_ratio", "q_spl", "q_vamp", "e_dmg", "e_ratio", "w_mred", "w_ms", "r_tdmg",
                           "r_tratio", "r_dmg", "r_ratio", "r_heal", "r_heal_ad", "r_sh", "r_sh_ad")}
    v.update({k: secs(p[k]) for k in ("q_t", "w_t", "w_ally_t", "r_t")})
    v["q_add"] = p["q_add"] // 100
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
    if "Nilah" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Nilah. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
