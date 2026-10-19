"""Cassiopeia's text (5 languages), sound_info files and her keys in the shared files, numbers from build_cassiopeia.P.

    python tools/kit/setup_cassiopeia.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_cassiopeia in every language, description + skill_name),
sound/sfx/league_cassiopeia_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Cassiopeia named). Only her keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 卡西奥佩娅 (魔蛇之拥): 优雅蛇行, 瘟毒爆炸, 剧毒迷雾, 双生毒牙, 石化凝视; zh_TW 卡莎碧雅
(蛇之擁抱): 致命節奏, 毒霧爆擊, 劇毒瘴氣, 雙生毒牙, 石化凝視; ja カシオペア: 妖艶な蛇行, ノクサスブラスト, ミアズマ, ツインファング,
石化の魔眼; ko 카시오페아: 독사의 품격, 맹독 폭발, 독기의 늪, 쌍독니, 석화의 응시.
Slots: skill = Q Noxious Blast, skill2 = W Miasma, ult = R Petrifying Gaze; Twin Fang is her attack (its text names it)
and the passive is in the attack's text. No combo sentence in any text (the user's rule). The main pack's rules are the
ones written (the fang's bonus while her poison is out, the gaze stunning the near ones); the add-on league_cassiopeia
checks the fang's own target and the enemies' real facing and says so itself.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_cassiopeia import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_cassiopeia"
VERSION = "0.148.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: the face point between her eyes (ppu_restyle face_to); banpick_center -6 by the card rule
# (tools/art/bp_card_audit.py: her idle's crest tops 33.3 game px over the frame centre: -39 + 33.3)
VIEW = {"face": {"x": 2, "y": -29}, "center": {"x": 0, "y": -16}, "banpick_center": {"x": 0, "y": -11}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def heal(r):
    return f"{APi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "卡西奥佩娅",
        "attack": O + "双生毒牙" + E + "：甩出毒牙，造成" + mag("e_dmg", "e_ratio") + "魔法伤害；Q、W毒到敌人后" + A + "{v_t}秒" + E + "内，"
                  "多造成" + mag("e_bonus", "e_bratio") + "并" + G + "回复" + E + heal("e_heal") + "生命。" + O + "优雅蛇行" + E + "：移速成长更高。",
        "skill": A + "0.4秒" + E + "后在目标处炸开，敌人中毒" + A + "{q_t}秒" + E + "，共受" + mag("q_dmg", "q_ratio") + "魔法伤害；毒到英雄时她移速"
                 "+{q_ms}%，" + A + "{q_t}秒" + E + "内渐退。",
        "skill2": "放出持续" + A + "{w_t}秒" + E + "的毒雾：每秒" + mag("w_dmg", "w_ratio") + "魔法伤害，" + R + "减速{w_slow}%、禁锢" + E +
                  "（不能用位移技能）。",
        "ult": "朝面前扇形石化凝视，造成" + mag("r_dmg", "r_ratio") + "魔法伤害：近处交战的敌人" + R + "石化{r_stun}秒" + E + "，远处的" + R +
               "减速{r_slow}%" + E + "。前方有2个以上敌方英雄或被突进时才放。",
        "names": ("瘟毒爆炸", "剧毒迷雾", "石化凝视"),
    },
    "zh-hant": {
        "name": "卡莎碧雅",
        "attack": O + "雙生毒牙" + E + "：甩出毒牙，造成" + mag("e_dmg", "e_ratio") + "魔法傷害；Q、W毒到敵人後" + A + "{v_t}秒" + E + "內，"
                  "多造成" + mag("e_bonus", "e_bratio") + "並" + G + "回復" + E + heal("e_heal") + "生命。" + O + "致命節奏" + E + "：移速成長更高。",
        "skill": A + "0.4秒" + E + "後在目標處炸開，敵人中毒" + A + "{q_t}秒" + E + "，共受" + mag("q_dmg", "q_ratio") + "魔法傷害；毒到英雄時她移速"
                 "+{q_ms}%，" + A + "{q_t}秒" + E + "內漸退。",
        "skill2": "放出持續" + A + "{w_t}秒" + E + "的毒霧：每秒" + mag("w_dmg", "w_ratio") + "魔法傷害，" + R + "緩速{w_slow}%、禁錮" + E +
                  "（不能用位移技能）。",
        "ult": "朝面前扇形石化凝視，造成" + mag("r_dmg", "r_ratio") + "魔法傷害：近處交戰的敵人" + R + "石化{r_stun}秒" + E + "，遠處的" + R +
               "緩速{r_slow}%" + E + "。前方有2個以上敵方英雄或被突進時才放。",
        "names": ("毒霧爆擊", "劇毒瘴氣", "石化凝視"),
    },
    "en": {
        "name": "Cassiopeia",
        "attack": O + "Twin Fang" + E + ": flings a fang for " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + "; within " + A +
                  "{v_t}s" + E + " of her Q or W poisoning an enemy it deals " + mag("e_bonus", "e_bratio") + " more and " + G + "heals her" +
                  E + " " + heal("e_heal") + ". " + O + "Serpentine Grace" + E + ": more move speed per level.",
        "skill": "Blasts the target's spot after " + A + "0.4s" + E + ", poisoning enemies there for " + A + "{q_t}s" + E + ": " +
                 mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " in all. Poisoning a champion gives her {q_ms}% move speed, "
                 "fading over " + A + "{q_t}s" + E + ".",
        "skill2": "Releases a poison cloud for " + A + "{w_t}s" + E + ": " + mag("w_dmg", "w_ratio") + " " + M + "magic damage" + E +
                  " a second, " + R + "{w_slow}% slow and grounded" + E + " (no dashes) inside.",
        "ult": "Gazes in a cone in front of her: " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + "; nearby enemies in the "
               "fight are " + R + "petrified for {r_stun}s" + E + ", farther ones " + R + "slowed {r_slow}%" + E + ". Cast with 2+ enemy "
               "champions in front or when dived.",
        "names": ("Noxious Blast", "Miasma", "Petrifying Gaze"),
    },
    "ko": {
        "name": "카시오페아",
        "attack": O + "쌍독니" + E + ": 독니를 날려 " + mag("e_dmg", "e_ratio") + " 마법 피해; Q·W로 적을 중독시킨 뒤 " + A + "{v_t}초" + E +
                  " 동안 " + mag("e_bonus", "e_bratio") + " 추가, " + G + "체력 회복" + E + " " + heal("e_heal") + ". " + O + "독사의 품격" + E +
                  ": 레벨당 이동 속도 증가.",
        "skill": A + "0.4초" + E + " 뒤 대상 위치에서 폭발, 적을 " + A + "{q_t}초" + E + " 중독시켜 총 " + mag("q_dmg", "q_ratio") +
                 " 마법 피해; 챔피언 적중 시 이동 속도 +{q_ms}%, " + A + "{q_t}초" + E + "에 걸쳐 감소.",
        "skill2": A + "{w_t}초" + E + "간 독구름: 매초 " + mag("w_dmg", "w_ratio") + " 마법 피해, " + R + "{w_slow}% 둔화, 이동 불가" + E +
                  "(돌진 불가).",
        "ult": "앞쪽 부채꼴로 응시: " + mag("r_dmg", "r_ratio") + " 마법 피해; 가까이서 싸우는 적은 " + R + "{r_stun}초 석화" + E + ", 먼 적은 " +
               R + "{r_slow}% 둔화" + E + ". 앞에 적 챔피언 2명 이상이거나 돌진당할 때 사용.",
        "names": ("맹독 폭발", "독기의 늪", "석화의 응시"),
    },
    "ja": {
        "name": "カシオペア",
        "attack": O + "ツインファング" + E + "：毒牙を放ち" + mag("e_dmg", "e_ratio") + "の魔法ダメージ；Q・Wで敵を毒にしてから" + A + "{v_t}秒" +
                  E + "は" + mag("e_bonus", "e_bratio") + "追加し" + G + "体力回復" + E + heal("e_heal") + "。" + O + "妖艶な蛇行" + E +
                  "：移動速度の成長が高い。",
        "skill": A + "0.4秒" + E + "後に対象地点で爆発、敵を" + A + "{q_t}秒" + E + "毒状態にし計" + mag("q_dmg", "q_ratio") + "の魔法ダメージ；"
                 "チャンピオンに命中で移動速度+{q_ms}%（" + A + "{q_t}秒" + E + "で減衰）。",
        "skill2": A + "{w_t}秒" + E + "の毒霧：毎秒" + mag("w_dmg", "w_ratio") + "の魔法ダメージ、" + R + "{w_slow}%スロウ・移動阻害" + E +
                  "（突進不可）。",
        "ult": "前方の扇形に魔眼：" + mag("r_dmg", "r_ratio") + "の魔法ダメージ；近くで戦う敵は" + R + "{r_stun}秒石化" + E + "、遠くの敵は" + R +
               "{r_slow}%スロウ" + E + "。前方に敵2体以上か突進された時に使う。",
        "names": ("ノクサスブラスト", "ミアズマ", "石化の魔眼"),
    },
}

C = "league_cassiopeia_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_cassiopeia_a": [(C + "a", 0.3, 0.0)],
    "league_cassiopeia_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_cassiopeia_q": [(C + "q", 0.45, 0.0)],
    "league_cassiopeia_q_blast": [(C + "q_blast", 0.45, 0.0)],
    "league_cassiopeia_q_hit": [(C + "q_hit", 0.3, 0.0)],
    "league_cassiopeia_w": [(C + "w", 0.45, 0.0)],
    "league_cassiopeia_w_land": [(C + "w_land", 0.45, 0.0)],
    "league_cassiopeia_r": [(C + "r", 0.55, 0.0)],
    "league_cassiopeia_r_hit": [(C + "r_hit", 0.45, 0.0)],
    "league_cassiopeia_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_cassiopeia_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_cassiopeia_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("e_dmg", "e_ratio", "e_bonus", "e_bratio", "e_heal", "q_dmg", "q_ratio", "q_ms", "w_slow",
                           "r_dmg", "r_ratio", "r_slow")}
    per_s = 60 / p["w_p"]
    v["w_dmg"], v["w_ratio"] = round(p["w_dmg"] * per_s), round(p["w_ratio"] * per_s)
    for k in ("v_t", "q_t", "w_t", "r_stun"):
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
    for k in [k for k in ov if ID + "_" in k]:      # his keys rebuilt (a renamed sound leaves none behind)
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
    if "Cassiopeia" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Cassiopeia. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
