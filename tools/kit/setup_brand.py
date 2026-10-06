"""Brand's text (5 languages), sound_info files and his keys in the shared files, numbers from build_brand.P.

    python tools/kit/setup_brand.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_brand in every language, description + skill_name),
sound/sfx/league_brand_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.70.1, Brand named). Only his keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (布兰德 / 复仇焰魂, 炽热之焰 - its burn 烈焰焚身 -, 火焰烙印, 烈焰之柱, 烈火燃烧,
烈焰风暴) and Data Dragon 16.19.1 (zh_TW 布蘭德 / 復仇業火, 烈炎鐵血, 火焰烙印, 煉獄風暴, 天火燎原, 末日熔岩; ko 브랜드 /
타오르는 복수, 불길, 불태우기, 화염 기둥, 발화, 파멸의 불덩이; ja ブランド / 復讐の炎, 炎上, 焦炎, 烈火の柱, 焼灼, 業火).
skill is W (Pillar of Flame); skill2 is named after E, which leads the E -> Q combo (Q in the text).
No `league_brand_attack` sound: the engine would play it at the start of every attack; the cast's sound plays from the
tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_brand import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_brand"
VERSION = "0.70.1"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
W = "<#f5f5f5ff>"      # true damage
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -38}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "布兰德",
        "attack": "被动" + O + "炽热之焰" + E + "：技能命中使敌人" + O + "烈焰焚身" + E + "{p_t}秒，每秒受到" + mag("p_burn", "p_burn_ap") + M +
                  "魔法伤害" + E + "。技能命中英雄叠层，第3层时该英雄{p_wait}秒后爆炸，对周围造成" +
                  mag("p_det", "p_det_ap") + "+" + W + "{p_det_hp}%最大生命值" + E + "伤害。",
        "skill": "短暂延迟后在目标处升起烈焰之柱，对范围内敌人造成" + mag("w_dmg", "w_ap") + M + "魔法伤害" + E +
                 "并点燃；有英雄在燃烧时伤害提高{w_bonus}%。",
        "skill2": O + "烈火燃烧" + E + "：点燃敌方英雄并蔓延到周围，造成" + mag("e_dmg", "e_ap") + "。随后" + O + "火焰烙印" + E +
                  "：火球命中首个敌人造成" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并" + R + "晕眩{q_stun}秒" + E +
                  "。命中英雄且烈焰之柱就绪时，再对他施放烈焰之柱。",
        "ult": "火种在敌人间弹射" + A + "{r_n}次" + E + "，优先英雄，每次造成" + mag("r_dmg", "r_ap") + M + "魔法伤害" + E + "、点燃并" + R +
               "减速{r_slow}%" + E + "。目标附近没有其他敌人时不施放。",
        "names": ("烈焰之柱", "烈火燃烧", "烈焰风暴"),
    },
    "zh-hant": {
        "name": "布蘭德",
        "attack": "被動" + O + "烈炎鐵血" + E + "：技能命中使敵人燃燒{p_t}秒，每秒受到" + mag("p_burn", "p_burn_ap") + M + "魔法傷害" + E +
                  "。技能命中英雄疊層，第3層時該英雄{p_wait}秒後爆炸，對周圍造成" + mag("p_det", "p_det_ap") +
                  "+" + W + "{p_det_hp}%最大生命值" + E + "傷害。",
        "skill": "短暫延遲後在目標處升起火柱，對範圍內敵人造成" + mag("w_dmg", "w_ap") + M + "魔法傷害" + E +
                 "並點燃；有英雄在燃燒時傷害提高{w_bonus}%。",
        "skill2": O + "天火燎原" + E + "：點燃敵方英雄並蔓延到周圍，造成" + mag("e_dmg", "e_ap") + "。隨後" + O + "火焰烙印" + E +
                  "：火球命中首個敵人造成" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並" + R + "暈眩{q_stun}秒" + E +
                  "。命中英雄且煉獄風暴就緒時，再對他施放煉獄風暴。",
        "ult": "火種在敵人間彈射" + A + "{r_n}次" + E + "，優先英雄，每次造成" + mag("r_dmg", "r_ap") + M + "魔法傷害" + E + "、點燃並" + R +
               "緩速{r_slow}%" + E + "。目標附近沒有其他敵人時不施放。",
        "names": ("煉獄風暴", "天火燎原", "末日熔岩"),
    },
    "en": {
        "name": "Brand",
        "attack": "Passive " + O + "Blaze" + E + ": his spells set enemies ablaze for {p_t}s, dealing " + mag("p_burn", "p_burn_ap") + " " +
                  M + "magic damage" + E + " a second. Spell hits on champions stack; at 3 stacks that "
                  "champion detonates {p_wait}s later for " + mag("p_det", "p_det_ap") + " + " + W + "{p_det_hp}% max health" + E +
                  " damage round it.",
        "skill": "After a short delay a pillar of flame rises at the target, dealing " + mag("w_dmg", "w_ap") + " " + M +
                 "magic damage" + E + " to enemies in it and setting them ablaze; {w_bonus}% more while a champion burns.",
        "skill2": O + "Conflagration" + E + ": sets an enemy champion ablaze, spreading to those around it, for " +
                  mag("e_dmg", "e_ap") + ". Then " + O + "Sear" + E + ": a fireball hits the first enemy for " + mag("q_dmg", "q_ap") +
                  " " + M + "magic damage" + E + ", " + R + "stunning {q_stun}s" + E +
                  ". On a champion with Pillar of Flame ready, the pillar follows on him.",
        "ult": "A fireball bounces " + A + "{r_n} times" + E + " among enemies, champions first, each dealing " + mag("r_dmg", "r_ap") +
               " " + M + "magic damage" + E + ", setting ablaze and " + R + "slowing {r_slow}%" + E +
               ". Not cast on a target with no other enemy near.",
        "names": ("Pillar of Flame", "Conflagration", "Pyroclasm"),
    },
    "ko": {
        "name": "브랜드",
        "attack": "기본 지속 효과 " + O + "불길" + E + ": 스킬 적중 시 {p_t}초간 불태워 초당 " + mag("p_burn", "p_burn_ap") + "의 " + M +
                  "마법 피해" + E + ". 챔피언 적중 시 중첩, 3중첩 시 그 챔피언이 {p_wait}초 후 폭발해 주변에 " +
                  mag("p_det", "p_det_ap") + " + " + W + "최대 체력의 {p_det_hp}%" + E + " 피해.",
        "skill": "잠시 후 대상 위치에 화염 기둥이 솟아 범위 내 적에게 " + mag("w_dmg", "w_ap") + "의 " + M + "마법 피해" + E +
                 "를 주고 불태움. 불타는 챔피언이 있으면 피해 {w_bonus}% 증가.",
        "skill2": O + "발화" + E + ": 적 챔피언을 불태우고 주변으로 번지며 " + mag("e_dmg", "e_ap") + ". 이어서 " + O + "불태우기" + E +
                  ": 화염구가 처음 맞은 적에게 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" + E + "와 " + R + "{q_stun}초 기절" + E +
                  ". 챔피언 적중 시 화염 기둥이 준비되어 있으면 그에게 이어서 시전.",
        "ult": "화염구가 적 사이를 " + A + "{r_n}번" + E + " 튕기며(챔피언 우선) 각각 " + mag("r_dmg", "r_ap") + "의 " + M + "마법 피해" + E +
               ", 불태우고 " + R + "{r_slow}% 둔화" + E + ". 대상 주변에 다른 적이 없으면 시전하지 않음.",
        "names": ("화염 기둥", "발화", "파멸의 불덩이"),
    },
    "ja": {
        "name": "ブランド",
        "attack": "パッシブ " + O + "炎上" + E + "：スキル命中で{p_t}秒間炎上させ毎秒" + mag("p_burn", "p_burn_ap") + "の" + M + "魔法ダメージ" +
                  E + "。チャンピオンへの命中でスタック、3スタックでそのチャンピオンが{p_wait}秒後に爆発し周囲に" +
                  mag("p_det", "p_det_ap") + "+" + W + "最大体力の{p_det_hp}%" + E + "のダメージ。",
        "skill": "少し後に対象地点に烈火の柱が立ち、範囲内の敵に" + mag("w_dmg", "w_ap") + "の" + M + "魔法ダメージ" + E +
                 "を与え炎上させる。燃えているチャンピオンがいるとダメージ{w_bonus}%増加。",
        "skill2": O + "焼灼" + E + "：敵チャンピオンを炎上させ周囲に燃え広がり" + mag("e_dmg", "e_ap") + "。続けて" + O + "焦炎" + E +
                  "：火球が最初の敵に" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" + R + "{q_stun}秒スタン" + E +
                  "。チャンピオンに命中し烈火の柱が使えれば続けて彼に放つ。",
        "ult": "火球が敵の間を" + A + "{r_n}回" + E + "跳ね（チャンピオン優先）、各" + mag("r_dmg", "r_ap") + "の" + M + "魔法ダメージ" + E +
               "、炎上と" + R + "{r_slow}%スロウ" + E + "。対象の近くに他の敵がいなければ使わない。",
        "names": ("烈火の柱", "焼灼", "業火"),
    },
}

C = "league_brand_sfx_"
V = "league_brand_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_brand_a_cast": [(C + "a_cast", 0.4, 0.0)],
    "league_brand_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_brand_w_cast": [(C + "w_cast", 0.5, 0.0)],
    "league_brand_w_blast": [(C + "w_blast", 0.6, 0.0)],
    "league_brand_e_cast": [(C + "e_cast", 0.5, 0.0)],
    "league_brand_e_hit": [(C + "e_hit", 0.5, 0.0)],
    "league_brand_q_cast": [(C + "q_cast", 0.55, 0.0)],
    "league_brand_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_brand_r_cast": [(C + "r_cast", 0.6, 0.0)],
    "league_brand_r_bounce": [(C + "r_bounce", 0.45, 0.0)],
    "league_brand_r_hit": [(C + "r_hit", 0.4, 0.0)],
    "league_brand_p_boom": [(C + "p_boom", 0.6, 0.0)],
    "league_brand_vo_q": [(V + "q", 0.75, 0.0)],
    "league_brand_vo_w": [(V + "w", 0.75, 0.0)],
    "league_brand_vo_e": [(V + "e", 0.75, 0.0)],
    "league_brand_vo_r": [(V + "r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def values(p):
    v = {k: p[k] for k in ("p_burn", "p_burn_ap", "p_det", "p_det_ap", "p_det_hp", "w_dmg", "w_ap", "w_bonus", "e_dmg",
                           "e_ap", "q_dmg", "q_ap", "r_n", "r_dmg", "r_ap", "r_slow")}
    for k in ("p_t", "p_wait", "q_stun"):
        v[k] = secs(p[k])
    return v


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


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
    if "Brand" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Brand. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
