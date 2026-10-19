"""Quinn's text (5 languages), sound_info files and her keys in the shared files, numbers from build_quinn.P.

    python tools/kit/setup_quinn.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_quinn in every language, description + skill_name),
sound/sfx/league_quinn_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Quinn named). Only her keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 奎因 (德玛西亚之翼): 侵扰, 炫目攻势, 敏锐感知, 旋翔掠杀, 深入敌后; zh_TW 葵恩 (蒂瑪西亞之翼):
追獵印記, 飛鷹突擊, 強化感知, 完美奇襲, 絕命殺戮; ja クイン: 鷲匠, 暗闇の強襲, 鷲の眼, 飛翔撃, 相棒; ko 퀸: 매사냥, 실명 공격, 예리한 감각,
공중제비, 후방 지원. Valor: 华洛 / 威洛 / ヴァロール / 발러. Skystrike: 鹰翼天翔 (zh_CN DD short text) / 天空強襲 (zh_TW tooltip) / 空中強襲 / 공중 강습 (from the ja / ko tooltips).
Slots: skill = Q Blinding Assault, skill2 = E Vault, ult = R Behind Enemy Lines; Harrier and W Heightened Senses' passive
are in the attack's text. No combo sentence in any text (the user's rule). The main pack's rules are the ones written
(R rides at the target and lands with Skystrike); the add-on league_quinn rides League's way and says so itself.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_quinn import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_quinn"
VERSION = "0.167.0"   # bumped at the PR, after asking the other sessions (main 0.166.0 with Powder #381; Yuumi #135 0.168.0)
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: placeholders until the sprite exists (tfm2_ase.py face)
VIEW = {"face": {"x": 3, "y": -31}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -10}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "奎因",
        "attack": O + "侵扰" + E + "：每" + A + "{p_cd}秒" + E + "华洛标记一次（技能也会标记），下次攻击额外造成" + phys("p_dmg", "p_ratio") +
                  "物理伤害。" + O + "敏锐感知" + E + "：之后" + A + "{w_t}秒" + E + "攻速+{w_as}%、移速+{w_ms}%。",
        "skill": "华洛飞出，在第一个敌人处爆开，周围敌人受" + phys("q_dmg", "q_ratio") + "物理伤害；被打中的英雄" + R + "缴械{q_blind}秒" + E +
                 "并被标记。",
        "skill2": "冲向敌人，造成" + phys("e_dmg", "e_ratio") + "物理伤害、" + R + "打断并减速{e_slow}%" + E + "，然后向后空翻拉开距离；目标被标记。",
        "ult": "召来华洛骑上，高速冲向敌方英雄，落地施放" + O + "鹰翼天翔" + E + "：周围敌人受" + phys("r_dmg", "r_ratio") + "物理伤害并被标记。",
        "names": ("炫目攻势", "旋翔掠杀", "深入敌后"),
    },
    "zh-hant": {
        "name": "葵恩",
        "attack": O + "追獵印記" + E + "：每" + A + "{p_cd}秒" + E + "威洛標記一次（技能也會標記），下次攻擊額外造成" + phys("p_dmg", "p_ratio") +
                  "物理傷害。" + O + "強化感知" + E + "：之後" + A + "{w_t}秒" + E + "攻速+{w_as}%、移速+{w_ms}%。",
        "skill": "威洛飛出，在第一個敵人處爆開，周圍敵人受" + phys("q_dmg", "q_ratio") + "物理傷害；被擊中的英雄" + R + "繳械{q_blind}秒" + E +
                 "並被標記。",
        "skill2": "衝向敵人，造成" + phys("e_dmg", "e_ratio") + "物理傷害、" + R + "打斷並緩速{e_slow}%" + E + "，然後向後空翻拉開距離；目標被標記。",
        "ult": "召來威洛騎上，高速衝向敵方英雄，落地施放" + O + "天空強襲" + E + "：周圍敵人受" + phys("r_dmg", "r_ratio") + "物理傷害並被標記。",
        "names": ("飛鷹突擊", "完美奇襲", "絕命殺戮"),
    },
    "en": {
        "name": "Quinn",
        "attack": O + "Harrier" + E + ": every " + A + "{p_cd}s" + E + " Valor marks her target (her spells mark too); her next "
                  "attack deals " + phys("p_dmg", "p_ratio") + " bonus physical damage. " + O + "Heightened Senses" + E + ": then for " +
                  A + "{w_t}s" + E + " she has +{w_as}% attack speed and +{w_ms}% move speed.",
        "skill": "Valor flies out and bursts on the first enemy: enemies around take " + phys("q_dmg", "q_ratio") +
                 " physical damage; a champion hit is " + R + "disarmed {q_blind}s" + E + " and marked.",
        "skill2": "Dashes to an enemy for " + phys("e_dmg", "e_ratio") + " physical damage, " + R + "interrupting and slowing it "
                  "{e_slow}%" + E + ", then flips back off it; the target is marked.",
        "ult": "Calls Valor down, rides him at an enemy champion and lands with " + O + "Skystrike" + E + ": enemies around take " +
               phys("r_dmg", "r_ratio") + " physical damage and are marked.",
        "names": ("Blinding Assault", "Vault", "Behind Enemy Lines"),
    },
    "ko": {
        "name": "퀸",
        "attack": O + "매사냥" + E + ": " + A + "{p_cd}초" + E + "마다 발러가 표식(스킬도 표식); 다음 공격이 " + phys("p_dmg", "p_ratio") +
                  " 추가 물리 피해. " + O + "예리한 감각" + E + ": 이후 " + A + "{w_t}초" + E + " 동안 공격 속도 +{w_as}%, 이동 속도 +{w_ms}%.",
        "skill": "발러가 날아가 첫 적에게서 폭발해 주변 적에게 " + phys("q_dmg", "q_ratio") + " 물리 피해; 맞은 챔피언은 " + R + "{q_blind}초 무장 해제" +
                 E + "되고 표식.",
        "skill2": "적에게 돌진해 " + phys("e_dmg", "e_ratio") + " 물리 피해와 " + R + "방해, {e_slow}% 둔화" + E + "를 주고 뒤로 공중제비; 대상은 표식.",
        "ult": "발러를 불러 타고 적 챔피언에게 날아가 착지하며 " + O + "공중 강습" + E + ": 주변 적에게 " + phys("r_dmg", "r_ratio") + " 물리 피해와 표식.",
        "names": ("실명 공격", "공중제비", "후방 지원"),
    },
    "ja": {
        "name": "クイン",
        "attack": O + "鷲匠" + E + "：" + A + "{p_cd}秒" + E + "ごとにヴァロールがマーク（スキルでもマーク）；次の攻撃が" + phys("p_dmg", "p_ratio") +
                  "の追加物理ダメージ。" + O + "鷲の眼" + E + "：その後" + A + "{w_t}秒" + E + "攻撃速度+{w_as}%、移動速度+{w_ms}%。",
        "skill": "ヴァロールが飛び最初の敵で炸裂し、周りの敵に" + phys("q_dmg", "q_ratio") + "の物理ダメージ；当たったチャンピオンは" + R +
                 "{q_blind}秒攻撃不能" + E + "でマーク。",
        "skill2": "敵へ突進して" + phys("e_dmg", "e_ratio") + "の物理ダメージと" + R + "妨害、{e_slow}%スロウ" + E + "、宙返りで離れる；対象はマーク。",
        "ult": "ヴァロールに乗って敵チャンピオンへ飛び、着地で" + O + "空中強襲" + E + "：周りの敵に" + phys("r_dmg", "r_ratio") + "の物理ダメージとマーク。",
        "names": ("暗闇の強襲", "飛翔撃", "相棒"),
    },
}

C = "league_quinn_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_quinn_a_shot": [(C + "a_shot", 0.35, 0.0)],
    "league_quinn_a_hit": [(C + "a_hit", 0.35, 0.0)],
    "league_quinn_p_dive": [(C + "p_dive", 0.45, 0.0)],
    "league_quinn_p_hit": [(C + "p_hit", 0.4, 0.0)],
    "league_quinn_q": [(C + "q", 0.45, 0.0)],
    "league_quinn_q_burst": [(C + "q_burst", 0.5, 0.0)],
    "league_quinn_q_hit": [(C + "q_burst", 0.3, 0.0)],
    "league_quinn_e": [(C + "e", 0.4, 0.0)],
    "league_quinn_e_hit": [(C + "e_hit", 0.45, 0.0)],
    "league_quinn_e_flip": [(C + "e_flip", 0.4, 0.0)],
    "league_quinn_r": [(C + "r", 0.5, 0.0)],
    "league_quinn_r_ride": [(C + "r_ride", 0.45, 0.0)],
    "league_quinn_r_land": [(C + "r_land", 0.6, 0.0)],
    "league_quinn_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_quinn_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_quinn_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "w_as", "w_ms", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "e_slow", "r_dmg", "r_ratio")}
    v["p_ratio"] = p["p_ratio"]
    for k in ("p_cd", "w_t", "q_blind"):
        v[k] = secs(p[k])
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
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 + the idle's top over the frame centre)")
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
    if "Quinn" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Quinn. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
