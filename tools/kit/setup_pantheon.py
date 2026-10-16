"""Pantheon's text (5 languages), sound_info files and his keys in the shared files, numbers from build_pantheon.P.

    python tools/kit/setup_pantheon.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_pantheon in every language, description + skill_name),
sound/sfx/league_pantheon_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.121.0, Pantheon named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 不屈之枪 / 潘森 - the client swaps name and title: 潘森; 矢志不退, 贯星长枪, 斗盾跃击,
神佑枪阵, 大荒星陨; zh_TW 潘森 / 不屈之矛, 凡人堅志, 彗星戰矛, 盾之躍擊, 聖盾猛襲, 星殞衝擊; ja パンテオン / 砕けぬ槍, 定命の意志,
彗星の槍, 跳撃の盾, イージスの猛攻, 偉大なる星路; ko 판테온 / 불굴의 창, 필멸자의 의지, 혜성의 창, 방호의 도약, 방패 돌격, 거대 유성).
Slots: skill = Q, skill2 = W (named) with E told in its text (league_galio's way), ult = R; the passive and R's armour
penetration are told in the attack's text. No combo sentence in any text (the user's rule). No `league_pantheon_attack`
sound: the engine would play it at the start of every attack; the thrust plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_pantheon import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_pantheon"
VERSION = "0.121.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
M = "<#a974ffff>"      # magic damage
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view for the idle in Codex's ready stance (rig_pantheon IDLE_SRC): the face at the helmet's crown (tfm2_ase.py
# face: 36 px over the feet, x -3; ppu_restyle's face_to); the lo_ idle's crest tops 30 px over the pivot, at or above -28 ->
# banpick_center y = -39 - (-30) (the card rule)
VIEW = {"face": {"x": -3, "y": -36}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -9}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "潘森",
        "attack": "长矛突刺。" + O + "矢志不退" + E + "：普攻命中和放技能各叠一层，" + A + "5层" + E + "时下一个技能强化（每条命开局满层）。" +
                  O + "大荒星陨" + E + "被动：护甲穿透{r_pen}%。",
        "skill": "近处向前突刺，远处蓄力后掷出长矛，对线上的敌人造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "（掷出时第一个之后减半）。" +
                 "强化：额外" + phy("q_emp", "q_emp_ratio") + "。",
        "skill2": "跃向敌方英雄，造成其{w_hp}%最大生命的伤害并" + R + "晕眩{w_stun}秒" + E + "；强化：下次普攻连刺3下。" + O + "神佑枪阵" + E +
                  "：举盾" + A + "{e_t}秒" + E + "，免疫控制、减伤{e_red}%，连刺前方后盾击造成" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "。",
        "ult": "下蹲" + A + "{r_ch}秒" + E + "后跃起，落向交战中的敌人：长矛先砸下造成" + phy("r_sp_dmg", "r_sp_ratio") + O + "物理伤害" + E +
               "并减速{r_slow}%，落地造成" + M + "{r_dmg}魔法伤害" + E + "（边缘减半），叠满被动。",
        "names": ("贯星长枪", "斗盾跃击", "大荒星陨"),
    },
    "zh-hant": {
        "name": "潘森",
        "attack": "長矛突刺。" + O + "凡人堅志" + E + "：普攻命中和施放技能各疊一層，" + A + "5層" + E + "時下一個技能強化（每條命開局滿層）。" +
                  O + "星殞衝擊" + E + "被動：護甲穿透{r_pen}%。",
        "skill": "近處向前突刺，遠處蓄力後擲出長矛，對線上的敵人造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "（擲出時第一個之後減半）。" +
                 "強化：額外" + phy("q_emp", "q_emp_ratio") + "。",
        "skill2": "躍向敵方英雄，造成其{w_hp}%最大生命的傷害並" + R + "暈眩{w_stun}秒" + E + "；強化：下次普攻連刺3下。" + O + "聖盾猛襲" + E +
                  "：舉盾" + A + "{e_t}秒" + E + "，免疫控制、減傷{e_red}%，連刺前方後盾擊造成" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "。",
        "ult": "蹲伏" + A + "{r_ch}秒" + E + "後躍起，落向交戰中的敵人：長矛先砸下造成" + phy("r_sp_dmg", "r_sp_ratio") + O + "物理傷害" + E +
               "並緩速{r_slow}%，落地造成" + M + "{r_dmg}魔法傷害" + E + "（邊緣減半），疊滿被動。",
        "names": ("彗星戰矛", "盾之躍擊", "星殞衝擊"),
    },
    "en": {
        "name": "Pantheon",
        "attack": "Spear thrusts. " + O + "Mortal Will" + E + ": attacks that land and ability casts each add a stack; at " + A +
                  "5 stacks" + E + " his next ability is empowered (full at the start of each life). " + O + "Grand Starfall" + E +
                  " passive: {r_pen}% armour penetration.",
        "skill": "Thrusts at a near target, or charges and throws the spear at a far one, dealing " + phy("q_dmg", "q_ratio") + " " + O +
                 "physical damage" + E + " to enemies on the line (a throw: half after the first). Empowered: " +
                 phy("q_emp", "q_emp_ratio") + " more.",
        "skill2": "Leaps at an enemy champion, dealing {w_hp}% of its max health and " + R + "stunning it {w_stun}s" + E +
                  "; empowered: his next attack strikes 3 times. " + O + "Aegis Assault" + E + ": raises the shield " + A + "{e_t}s" +
                  E + ", immune to crowd control, {e_red}% less damage, stabbing ahead, then bashes for " + phy("e_dmg", "e_ratio") +
                  " " + O + "physical damage" + E + ".",
        "ult": "Crouches " + A + "{r_ch}s" + E + ", leaps and falls on enemies in a fight: his spear strikes first for " +
               phy("r_sp_dmg", "r_sp_ratio") + " " + O + "physical damage" + E + " and a {r_slow}% slow, then the landing deals " +
               M + "{r_dmg} magic damage" + E + " (half at the edge) and fills Mortal Will.",
        "names": ("Comet Spear", "Shield Vault", "Grand Starfall"),
    },
    "ko": {
        "name": "판테온",
        "attack": "창으로 찌릅니다. " + O + "필멸자의 의지" + E + ": 적중한 기본 공격과 스킬 사용마다 중첩, " + A + "5중첩" + E +
                  "이면 다음 스킬 강화(목숨마다 시작 시 최대). " + O + "거대 유성" + E + " 패시브: 방어구 관통 {r_pen}%.",
        "skill": "가까우면 앞으로 찌르고, 멀면 힘을 모아 창을 던져 선 위의 적에게 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E +
                 "(던질 때 첫 적 이후 절반). 강화: " + phy("q_emp", "q_emp_ratio") + " 추가.",
        "skill2": "적 챔피언에게 도약해 최대 체력의 {w_hp}% 피해와 " + R + "{w_stun}초 기절" + E + "; 강화: 다음 기본 공격 3연타. " + O + "방패 돌격" +
                  E + ": " + A + "{e_t}초" + E + " 방패를 들어 군중 제어 면역, 피해 {e_red}% 감소, 앞을 찌른 뒤 방패로 " + phy("e_dmg", "e_ratio") +
                  "의 " + O + "물리 피해" + E + ".",
        "ult": A + "{r_ch}초" + E + " 웅크렸다 도약해 교전 중인 적에게 떨어집니다: 창이 먼저 " + phy("r_sp_dmg", "r_sp_ratio") + "의 " + O +
               "물리 피해" + E + "와 {r_slow}% 둔화, 착지 시 " + M + "{r_dmg} 마법 피해" + E + "(가장자리 절반), 패시브 최대.",
        "names": ("혜성의 창", "방호의 도약", "거대 유성"),
    },
    "ja": {
        "name": "パンテオン",
        "attack": "槍で突く。" + O + "定命の意志" + E + "：命中した通常攻撃とスキル使用でスタック、" + A + "5スタック" + E + "で次のスキル強化"
                  "（各ライフ開始時は最大）。" + O + "偉大なる星路" + E + "パッシブ：物理防御貫通{r_pen}%。",
        "skill": "近くなら前へ突き、遠ければ溜めて槍を投げ、線上の敵に" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E +
                 "（投擲は最初の敵以降半減）。強化：" + phy("q_emp", "q_emp_ratio") + "追加。",
        "skill2": "敵チャンピオンへ跳び、最大体力の{w_hp}%のダメージと" + R + "{w_stun}秒スタン" + E + "。強化：次の通常攻撃が3連撃。" + O +
                  "イージスの猛攻" + E + "：" + A + "{e_t}秒" + E + "盾を構え、CC無効・被ダメージ{e_red}%軽減、前方を突いた後に盾で" +
                  phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "。",
        "ult": A + "{r_ch}秒" + E + "身を屈めて跳び、交戦中の敵へ落下：槍が先に" + phy("r_sp_dmg", "r_sp_ratio") + "の" + O + "物理ダメージ" +
               E + "と{r_slow}%スロウ、着地で" + M + "{r_dmg}の魔法ダメージ" + E + "（外側は半減）、パッシブ最大。",
        "names": ("彗星の槍", "跳撃の盾", "偉大なる星路"),
    },
}

C = "league_pantheon_sfx_"
V = "league_pantheon_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_pantheon_a_swing": [(C + "a_swing", 0.4, 0.0)],
    "league_pantheon_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_pantheon_p_ready": [(C + "p_ready", 0.45, 0.0)],
    "league_pantheon_q_tap": [(C + "q_tap", 0.55, 0.0)],
    "league_pantheon_q_hold": [(C + "q_hold", 0.5, 0.0)],
    "league_pantheon_q_throw": [(C + "q_throw", 0.55, 0.0)],
    "league_pantheon_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_pantheon_w": [(C + "w", 0.55, 0.0)],
    "league_pantheon_w_hit": [(C + "w_hit", 0.6, 0.0)],
    "league_pantheon_w_tri": [(C + "w_tri", 0.5, 0.0)],
    "league_pantheon_e": [(C + "e", 0.55, 0.0)],
    "league_pantheon_e_bash": [(C + "e_bash", 0.6, 0.0)],
    "league_pantheon_e_hit": [(C + "a_hit", 0.35, 0.0)],
    "league_pantheon_r": [(C + "r", 0.6, 0.0)],
    "league_pantheon_r_leap": [(C + "r_leap", 0.6, 0.0)],
    "league_pantheon_r_spear": [(C + "r_spear", 0.6, 0.0)],
    "league_pantheon_r_land": [(C + "r_land", 0.65, 0.0)],
    "league_pantheon_vo_q": [(V + "q", 0.85, 0.0)],
    "league_pantheon_vo_w": [(V + "w", 0.85, 0.0)],
    "league_pantheon_vo_e": [(V + "e", 0.85, 0.0)],
    "league_pantheon_vo_r": [(V + "r", 0.9, 0.0)],
    "league_pantheon_vo_r_leap": [(V + "r_leap", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("r_pen", "q_dmg", "q_ratio", "q_emp", "q_emp_ratio", "w_hp", "e_red", "e_dmg", "e_ratio",
                           "r_sp_dmg", "r_sp_ratio", "r_slow", "r_dmg")}
    for k in ("w_stun", "e_t", "r_ch"):
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
    if "Pantheon" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Pantheon. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
