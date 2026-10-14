"""Smolder's text (5 languages), sound_info files and his keys in the shared files, numbers from build_smolder.P.

    python tools/kit/setup_smolder.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_smolder in every language, description + skill_name),
sound/sfx/league_smolder_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.112.0, Smolder named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (斯莫德 / 炽炎雏龙; 龙之研习, 超级灼热龙息, 阿嚏！, 扑棱，扑棱，扑棱！, 妈----！; the client
swaps name and title, %TEMP%/sm_work/names.py) and Data Dragon 16.20.1 (zh_TW 史矛德 / 帝煌雛龍 / 龍性精通 / 激灼龍息 /
悶燃黏嚏 / 振翼高飛 / 媽媽幫我！, ja スモルダー / 炎の幼龍 / 駆けだしドラゴン / スーパーこげこげブレス / くしゅん！ / パタパタパタ /
ママーッ！！, ko 스몰더 / 꼬마 불꽃용 / 용 훈련 / 초강력 화염 숨결 / 에취! / 펄럭펄럭 / 엄마아아아!; the local client has no
zh_TW / ja_JP / ko_KR string tables).
Slots: skill = Q, skill2 = W (E on its own flag), ult = R; the passive (the stacks, what a stack adds, Q's tiers) is told
in the attack's text. No combo sentence in any text (the user's rule). No `league_smolder_attack` sound: the engine would
play it at the start of every attack; the attack plays its own from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_smolder import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_smolder"
VERSION = "0.112.0"                  # #104: 马尔扎哈 (league_malzahar) merged first as #103 / 0.111.0
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
D = "<#ff8a65ff>"      # physical damage
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#6aff55ff>"      # heals
W = "<#f5f5f5ff>"      # true damage
S = "<#ffffffff>"      # move speed
E = "<>"
# champion_view: a placeholder until the sheet is final - tfm2_ase.py face on the 2026-10-15 1x sheet (crown 25 px over
# the feet, head centre x -3.8): (-2, -25); centre: his body, a small quadruped (-10). Re-measure on the final sheet
# (and with hd.rs's PPU scale) and pass --face.
VIEW = {"face": {"x": -2, "y": -25}, "center": {"x": 0, "y": -10}}


def phys(k):
    return f"{D}{{{k}_dmg}}{E}+{ADi}{D}{{{k}_ratio}}%{E}"


# the burn a second (true damage) and what a stack adds to the breath / the sneeze / each flight fireball (magic)
BURN = W + "{q_burn_dmg}" + E + "+" + ADi + W + "{q_burn_ratio}%" + E + "+" + W + "{q_burn_hp}%"
STK = M + "{q_sv}/{w_sv}/{e_sv}"

TEXT = {
    "zh-hans": {
        "name": "斯莫德",
        "attack": "喷出小火球。被动" + O + "龙之研习" + E + "：技能命中英雄、龙息击杀单位各获得1层（阵亡清空），每层使龙息、喷嚏、扑棱火球各+" + STK + "魔法伤害" +
                  E + "。龙息在" + A + "{t1}/{t2}/{t3}层" + E + "时依次获得爆炸、反冲火球、灼烧。",
        "skill": "喷吐火球，造成" + phys("q") + D + "物理伤害" + E + "。" + A + "{t1}层" + E + "：爆炸波及周围敌人；" + A + "{t2}层" + E +
                 "：向目标身后喷出反冲火球（{q_t2_pct}%伤害）；" + A + "{t3}层" + E + "：灼烧" + A + "{q_burn_t}秒" + E + "，每秒造成" + BURN + "最大生命真实伤害" + E + "。",
        "skill2": "打喷嚏喷出火焰，造成" + phys("w") + D + "物理伤害" + E + "并" + R + "减速{w_slow}%" + E + "，命中英雄时爆炸，再造成" + phys("w_x") + D + "物理伤害" + E +
                  "。被近身或追击残血时改用" + O + "扑棱，扑棱，扑棱！" + E + "：飞起并" + S + "加速{e_ms}%" + E + "，向残血敌人连发" + A + "{e_n}" + E + "枚火球，各" +
                  phys("e") + D + "物理伤害" + E + "。",
        "ult": "呼唤妈妈沿直线喷火，造成" + phys("r") + D + "物理伤害" + E + "，中心的敌人多受" + A + "{r_sweet}%" + E + "伤害并" + R + "减速{r_slow}%" + E + "（" + A +
               "{r_slow_t}秒" + E + "）。斯莫德站在中心线上时回复" + G + "{r_heal}" + E + "+" + ADi + G + "{r_heal_ad}%" + E + "生命。",
        "names": ("超级灼热龙息", "阿嚏！ / 扑棱，扑棱，扑棱！", "妈----！"),
    },
    "zh-hant": {
        "name": "史矛德",
        "attack": "噴出小火球。被動" + O + "龍性精通" + E + "：技能命中英雄、龍息擊殺單位各獲得1層（陣亡清空），每層使龍息、噴嚏、振翼火球各+" + STK + "魔法傷害" +
                  E + "。龍息在" + A + "{t1}/{t2}/{t3}層" + E + "時依次獲得爆炸、反衝火球、灼燒。",
        "skill": "噴吐火球，造成" + phys("q") + D + "物理傷害" + E + "。" + A + "{t1}層" + E + "：爆炸波及周圍敵人；" + A + "{t2}層" + E +
                 "：向目標身後噴出反衝火球（{q_t2_pct}%傷害）；" + A + "{t3}層" + E + "：灼燒" + A + "{q_burn_t}秒" + E + "，每秒造成" + BURN + "最大生命真實傷害" + E + "。",
        "skill2": "打噴嚏噴出火焰，造成" + phys("w") + D + "物理傷害" + E + "並" + R + "緩速{w_slow}%" + E + "，命中英雄時爆炸，再造成" + phys("w_x") + D + "物理傷害" + E +
                  "。被近身或追擊殘血時改用" + O + "振翼高飛" + E + "：飛起並" + S + "加速{e_ms}%" + E + "，向殘血敵人連發" + A + "{e_n}" + E + "枚火球，各" +
                  phys("e") + D + "物理傷害" + E + "。",
        "ult": "呼喚媽媽沿直線噴火，造成" + phys("r") + D + "物理傷害" + E + "，中心的敵人多受" + A + "{r_sweet}%" + E + "傷害並" + R + "緩速{r_slow}%" + E + "（" + A +
               "{r_slow_t}秒" + E + "）。史矛德站在中心線上時回復" + G + "{r_heal}" + E + "+" + ADi + G + "{r_heal_ad}%" + E + "生命。",
        "names": ("激灼龍息", "悶燃黏嚏 / 振翼高飛", "媽媽幫我！"),
    },
    "en": {
        "name": "Smolder",
        "attack": "Spits a small fireball. Passive " + O + "Dragon Practice" + E + ": each champion his abilities hit and each unit his breath kills gives a "
                  "stack (lost on death), adding " + STK + " magic damage" + E + " to the breath, the sneeze and each flight fireball. At " + A +
                  "{t1}/{t2}/{t3}" + E + " stacks the breath gains an explosion, blowback fireballs and a burn.",
        "skill": "Breathes a fireball for " + phys("q") + " " + D + "physical damage" + E + ". " + A + "{t1}" + E + " stacks: it explodes on the enemies "
                 "around the target. " + A + "{t2}" + E + ": fireballs blow back behind the target ({q_t2_pct}% damage). " + A + "{t3}" + E + ": it burns for " + A +
                 "{q_burn_t}s" + E + ", " + BURN + " max health true damage" + E + " a second.",
        "skill2": "Sneezes fire for " + phys("w") + " " + D + "physical damage" + E + " and a " + R + "{w_slow}% slow" + E + "; on a champion it explodes for " +
                  phys("w_x") + " " + D + "physical damage" + E + ". When dived, or chasing a wounded enemy: " + O + "Flap, Flap, Flap" + E + " - he flies, gains " +
                  S + "{e_ms}% move speed" + E + " and fires " + A + "{e_n}" + E + " fireballs at the weakest enemy, " + phys("e") + " " + D + "physical damage" + E +
                  " each.",
        "ult": "Calls his mother, who breathes fire along a line: " + phys("r") + " " + D + "physical damage" + E + "; enemies in the middle take " + A +
               "{r_sweet}%" + E + " more and are " + R + "slowed {r_slow}%" + E + " for " + A + "{r_slow_t}s" + E + ". If Smolder stands on the middle line he heals " +
               G + "{r_heal}" + E + "+" + ADi + G + "{r_heal_ad}%" + E + ".",
        "names": ("Super Scorcher Breath", "Achooo! / Flap, Flap, Flap", "MMOOOMMMM!"),
    },
    "ko": {
        "name": "스몰더",
        "attack": "작은 불덩이를 뱉습니다. 기본 지속 효과 " + O + "용 훈련" + E + ": 스킬로 챔피언을 맞히거나 숨결로 적을 처치할 때마다 1중첩(사망 시 소멸), 중첩마다 숨결, "
                  "재채기, 비행 불덩이에 " + STK + " 마법 피해" + E + " 추가. " + A + "{t1}/{t2}/{t3}중첩" + E + "에서 숨결이 폭발, 역류 화염구, 화상을 얻습니다.",
        "skill": "불덩이를 뿜어 " + phys("q") + " " + D + "물리 피해" + E + ". " + A + "{t1}중첩" + E + ": 대상 주변 적에게 폭발. " + A + "{t2}중첩" + E +
                 ": 대상 뒤로 역류 화염구({q_t2_pct}% 피해). " + A + "{t3}중첩" + E + ": " + A + "{q_burn_t}초" + E + " 동안 화상, 초당 " + BURN + " 최대 체력 고정 피해" + E +
                 ".",
        "skill2": "재채기로 불을 뿜어 " + phys("w") + " " + D + "물리 피해" + E + "와 " + R + "{w_slow}% 둔화" + E + ", 챔피언에게 맞으면 폭발해 " + phys("w_x") + " " + D +
                  "물리 피해" + E + ". 적이 붙거나 약한 적을 쫓을 때는 " + O + "펄럭펄럭" + E + ": 날아오르며 " + S + "이동 속도 +{e_ms}%" + E + ", 약한 적에게 불덩이 " + A +
                  "{e_n}개" + E + "(각 " + phys("e") + " " + D + "물리 피해" + E + ").",
        "ult": "엄마를 불러 직선으로 불을 뿜습니다: " + phys("r") + " " + D + "물리 피해" + E + ", 중앙의 적은 " + A + "{r_sweet}%" + E + " 추가 피해와 " + R +
               "{r_slow}% 둔화" + E + "(" + A + "{r_slow_t}초" + E + "). 스몰더가 중앙선 위에 있으면 " + G + "{r_heal}" + E + "+" + ADi + G + "{r_heal_ad}%" + E +
               " 회복.",
        "names": ("초강력 화염 숨결", "에취! / 펄럭펄럭", "엄마아아아!"),
    },
    "ja": {
        "name": "スモルダー",
        "attack": "小さな火の玉を吐く。自動効果" + O + "駆けだしドラゴン" + E + "：スキルでチャンピオンに命中、ブレスで敵を倒すたびに1スタック（死亡で消滅）、"
                  "スタックごとにブレス・くしゃみ・飛行中の火の玉に" + STK + "魔法ダメージ" + E + "追加。" + A + "{t1}/{t2}/{t3}" + E + "でブレスが爆発・逆噴射・炎上を得る。",
        "skill": "火の玉を吐き" + phys("q") + "の" + D + "物理ダメージ" + E + "。" + A + "{t1}" + E + "：周囲の敵に爆発。" + A + "{t2}" + E + "：対象の後方へ火球（{q_t2_pct}%）。" +
                 A + "{t3}" + E + "：" + A + "{q_burn_t}秒" + E + "炎上、毎秒" + BURN + "最大体力の確定ダメージ" + E + "。",
        "skill2": "くしゃみで炎を吹き" + phys("w") + "の" + D + "物理ダメージ" + E + "と" + R + "{w_slow}%スロウ" + E + "、チャンピオンに当たると爆発し" + phys("w_x") + "の" +
                  D + "物理ダメージ" + E + "。詰められた時か弱った敵を追う時は" + O + "パタパタパタ" + E + "：飛び上がり" + S + "移動速度+{e_ms}%" + E + "、弱った敵に火の玉" +
                  A + "{e_n}発" + E + "（各" + phys("e") + "）。",
        "ult": "ママを呼び直線上に炎を吐かせる：" + phys("r") + "の" + D + "物理ダメージ" + E + "、中央の敵は" + A + "{r_sweet}%" + E + "増加と" + R + "{r_slow}%スロウ" + E +
               "（" + A + "{r_slow_t}秒" + E + "）。スモルダーが中央線上にいれば" + G + "{r_heal}" + E + "+" + ADi + G + "{r_heal_ad}%" + E + "回復。",
        "names": ("スーパーこげこげブレス", "くしゅん！/パタパタパタ", "ママーッ！！"),
    },
}

S_ = "league_smolder_"
CL = "league_smolder_sfx_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(CL + k, vol, 0.0)] for k, vol in [
    ("a_cast", 0.4), ("a_hit", 0.4), ("q_cast", 0.5), ("q_hit", 0.45), ("q_boom", 0.5), ("q_back", 0.45),
    ("q_t2_hit", 0.35), ("q_burn", 0.35), ("p_t1", 0.6), ("p_t2", 0.6), ("p_t3", 0.65), ("w_cast", 0.55),
    ("w_hit", 0.35), ("w_boom", 0.55), ("e_cast", 0.5), ("e_shot", 0.3), ("e_hit", 0.3), ("r_cast", 0.6),
    ("r_mom", 0.6), ("r_hit", 0.45), ("r_heal", 0.5), ("vo_q", 0.75), ("vo_w", 0.75), ("vo_e", 0.75),
    ("vo_r", 0.8), ("vo_up", 0.8)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("t1", "t2", "t3", "q_dmg", "q_ratio", "q_t2_pct", "q_burn_dmg", "q_burn_ratio", "q_burn_hp",
                           "w_dmg", "w_ratio", "w_slow", "w_x_dmg", "w_x_ratio", "e_ms", "e_n", "e_dmg", "e_ratio", "r_dmg",
                           "r_ratio", "r_sweet", "r_slow", "r_heal", "r_heal_ad")}
    v.update({k: secs(p[k]) for k in ("r_slow_t", "q_burn_t")})
    for k in ("q", "w", "e"):     # per stack: k_stack% of his ability power (one a stack)
        v[k + "_sv"] = f"{p[k + '_stack'] / 100:.2f}".rstrip("0").rstrip(".")
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
    if "Smolder" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Smolder. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
