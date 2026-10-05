"""Alistar's text (5 languages), sound_info files and his keys in the shared files, numbers from build_alistar.P.

    python tools/kit/setup_alistar.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_alistar in every language, description + skill_name),
sound/sfx/league_alistar_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.61.0, Alistar named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/al/rst.py: 阿利斯塔 / 牛头酋长, 凯旋怒吼, 大地粉碎, 野蛮冲撞, 践踏, 坚定意志) and
Data Dragon 16.19.1 (zh_TW 亞歷斯塔 / 勝利怒吼 / 大地粉碎 / 野蠻衝撞 / 蠻牛之力 / 堅定意志, ko 알리스타 / 승리의 포효 / 분쇄 /
박치기 / 짓밟기 / 꺾을 수 없는 의지, ja アリスター / 戦士の咆哮 / 圧砕 / 頭突き / 踏破 / 不屈の意志). No `league_alistar_attack`
sound: the engine would play it at the start of every attack; the punch sound plays from the tree on the hit.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_alistar import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_alistar"
VERSION = "0.61.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 9, "y": -32}, "center": {"x": 0, "y": -12}}   # the head between the horns (the hump is higher)


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


G = "<#7cfc00ff>"      # heals


def hl(d, r):
    return f"{G}{{{d}}}{E} + {APi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "阿利斯塔",
        "attack": "用双拳重击。被动" + O + "凯旋怒吼" + E + "：控制命中敌方英雄" + A + "{p_need}次" + E + "后怒吼，回复自己" +
                  hl("p_heal", "p_ap") + "、周围友方英雄" + hl("p_ally", "p_ally_ap") + "生命。",
        "skill": O + "践踏" + E + "接" + O + "大地粉碎" + E + "：先践踏" + A + "{e_t}秒" + E + "（每脚" + mag("e_dmg", "e_ap") +
                 "），再砸地，周围敌人受到" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并" + R + "击飞{q_up}秒" + E + "。踩中英雄" +
                 A + "5次" + E + "后，下次普攻" + R + "眩晕{e_stun}秒" + E + "。",
        "skill2": O + "野蛮冲撞" + E + "接" + O + "大地粉碎" + E + "：冲向敌方英雄，撞退并造成" + mag("w_dmg", "w_ap") + M +
                  "魔法伤害" + E + "，随即砸地" + R + "击飞" + E + "周围敌人，同时开始践踏。",
        "ult": "交战时怒吼：" + R + "免疫控制{r_imm}秒" + E + "，" + A + "{r_t}秒" + E + "内受到的伤害降低" + A + "{r_red}%" + E + "。",
        "names": ("大地粉碎", "野蛮冲撞", "坚定意志"),
    },
    "zh-hant": {
        "name": "亞歷斯塔",
        "attack": "用雙拳重擊。被動" + O + "勝利怒吼" + E + "：控制命中敵方英雄" + A + "{p_need}次" + E + "後怒吼，回復自己" +
                  hl("p_heal", "p_ap") + "、周圍友方英雄" + hl("p_ally", "p_ally_ap") + "生命。",
        "skill": O + "蠻牛之力" + E + "接" + O + "大地粉碎" + E + "：先踐踏" + A + "{e_t}秒" + E + "（每腳" + mag("e_dmg", "e_ap") +
                 "），再砸地，周圍敵人受到" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並" + R + "擊飛{q_up}秒" + E + "。踩中英雄" +
                 A + "5次" + E + "後，下次普攻" + R + "暈眩{e_stun}秒" + E + "。",
        "skill2": O + "野蠻衝撞" + E + "接" + O + "大地粉碎" + E + "：衝向敵方英雄，撞退並造成" + mag("w_dmg", "w_ap") + M +
                  "魔法傷害" + E + "，隨即砸地" + R + "擊飛" + E + "周圍敵人，同時開始踐踏。",
        "ult": "交戰時怒吼：" + R + "免疫控制{r_imm}秒" + E + "，" + A + "{r_t}秒" + E + "內受到的傷害降低" + A + "{r_red}%" + E + "。",
        "names": ("大地粉碎", "野蠻衝撞", "堅定意志"),
    },
    "en": {
        "name": "Alistar",
        "attack": "Pounds with both fists. Passive " + O + "Triumphant Roar" + E + ": after his crowd control lands on enemy "
                  "champions " + A + "{p_need} times" + E + " he roars, healing himself " + hl("p_heal", "p_ap") +
                  " and allied champions nearby " + hl("p_ally", "p_ally_ap") + ".",
        "skill": O + "Trample" + E + " into " + O + "Pulverize" + E + ": he tramples for " + A + "{e_t}s" + E + " (" +
                 mag("e_dmg", "e_ap") + " a stomp), then smashes the ground: " + mag("q_dmg", "q_ap") + " " + M + "magic damage" +
                 E + " and a " + R + "{q_up}s knock-up" + E + " around him. After " + A + "5" + E + " stomps on champions his "
                 "next attack " + R + "stuns" + E + " for {e_stun}s.",
        "skill2": O + "Headbutt" + E + " into " + O + "Pulverize" + E + ": charges an enemy champion, knocks him back for " +
                  mag("w_dmg", "w_ap") + " " + M + "magic damage" + E + ", then smashes the ground, " + R + "knocking up" + E +
                  " enemies around him. Starts Trample too.",
        "ult": "Roars in a fight: " + R + "immune to crowd control" + E + " for " + A + "{r_imm}s" + E + ", takes " + A +
               "{r_red}%" + E + " less damage for " + A + "{r_t}s" + E + ".",
        "names": ("Pulverize", "Headbutt", "Unbreakable Will"),
    },
    "ko": {
        "name": "알리스타",
        "attack": "두 주먹으로 내리칩니다. 기본 지속 효과 " + O + "승리의 포효" + E + ": 군중 제어를 적 챔피언에게 " + A + "{p_need}번" + E +
                  " 적중시키면 포효해 자신은 " + hl("p_heal", "p_ap") + ", 주변 아군 챔피언은 " + hl("p_ally", "p_ally_ap") +
                  "의 체력을 회복합니다.",
        "skill": O + "짓밟기" + E + " 후 " + O + "분쇄" + E + ": " + A + "{e_t}초" + E + " 동안 짓밟고(한 번에 " + mag("e_dmg", "e_ap") +
                 ") 땅을 내리쳐 주변 적에게 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" + E + "를 입히고 " + R +
                 "{q_up}초 띄워 올립니다" + E + ". 챔피언을 " + A + "5번" + E + " 밟으면 다음 기본 공격이 " + R + "{e_stun}초 기절" + E +
                 "시킵니다.",
        "skill2": O + "박치기" + E + " 후 " + O + "분쇄" + E + ": 적 챔피언에게 돌진해 밀쳐내며 " + mag("w_dmg", "w_ap") + "의 " + M +
                  "마법 피해" + E + "를 입히고, 곧바로 땅을 내리쳐 주변 적을 " + R + "띄워 올립니다" + E + ". 짓밟기도 시작합니다.",
        "ult": "교전 중 포효: " + A + "{r_imm}초" + E + " 동안 " + R + "군중 제어 면역" + E + ", " + A + "{r_t}초" + E + " 동안 받는 피해가 " +
               A + "{r_red}%" + E + " 감소합니다.",
        "names": ("분쇄", "박치기", "꺾을 수 없는 의지"),
    },
    "ja": {
        "name": "アリスター",
        "attack": "両拳で殴りつける。パッシブ " + O + "戦士の咆哮" + E + "：行動妨害を敵チャンピオンに" + A + "{p_need}回" + E +
                  "当てると咆哮し、自身は" + hl("p_heal", "p_ap") + "、周囲の味方チャンピオンは" + hl("p_ally", "p_ally_ap") + "回復。",
        "skill": O + "踏破" + E + "から" + O + "圧砕" + E + "：" + A + "{e_t}秒" + E + "踏み鳴らし（1回" + mag("e_dmg", "e_ap") +
                 "）、地面を叩いて周囲の敵に" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" + R + "{q_up}秒のノックアップ" +
                 E + "。チャンピオンを" + A + "5回" + E + "踏むと次の通常攻撃が" + R + "{e_stun}秒スタン" + E + "。",
        "skill2": O + "頭突き" + E + "から" + O + "圧砕" + E + "：敵チャンピオンに突進してノックバックし" + mag("w_dmg", "w_ap") + "の" + M +
                  "魔法ダメージ" + E + "、すぐ地面を叩いて周囲の敵を" + R + "ノックアップ" + E + "。踏破も始める。",
        "ult": "戦闘中に咆哮：" + A + "{r_imm}秒" + E + R + "行動妨害無効" + E + "、" + A + "{r_t}秒" + E + "間受けるダメージ" + A +
               "{r_red}%" + E + "軽減。",
        "names": ("圧砕", "頭突き", "不屈の意志"),
    },
}

C = "league_alistar_sfx_"
V = "league_alistar_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_alistar_a_hit": [(C + "hit", 0.45, 0.0)],
    "league_alistar_q_cast": [(C + "q", 0.55, 0.0), (V + "q", 0.85, 0.05)],
    "league_alistar_q_hit": [(C + "q_hit", 0.65, 0.0)],
    "league_alistar_w_cast": [(C + "w", 0.6, 0.0), (V + "w", 0.85, 0.05)],
    "league_alistar_w_hit": [(C + "w_hit", 0.6, 0.0)],
    "league_alistar_e_step": [(C + "e", 0.25, 0.0)],
    "league_alistar_e_ready": [(C + "e_ready", 0.6, 0.0)],
    "league_alistar_e_stun": [(C + "e_stun", 0.6, 0.0)],
    "league_alistar_p_roar": [(C + "p", 0.55, 0.0)],
    "league_alistar_r_cast": [(C + "r", 0.7, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_need", "p_heal", "p_ap", "p_ally", "p_ally_ap", "e_dmg", "e_ap", "q_dmg", "q_ap", "w_dmg",
                           "w_ap", "r_red")}
    v.update({k: secs(p[k]) for k in ("e_t", "e_stun", "q_up", "r_imm", "r_t")})
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
    if "Alistar" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Alistar. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
