"""Renata's text (5 languages), sound_info files and her keys in the shared files, numbers from build_renata.P.

    python tools/kit/setup_renata.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_renata in every language, description + skill_name),
sound/sfx/league_renata_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point), mod.mod_info (0.136.0, Renata named). Only her keys change in the shared files. JSON:
indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 炼金男爵 烈娜塔 · 戈拉斯克 - the client swaps name and title: 烈娜塔; 物尽其用, 铁腕竞合,
及时救难, 忠诚激励, 恶意收购; zh_TW 睿娜妲, 唯利是圖, 霸道手腕, 急難救助, 有酬必報, 惡意收購; ja レナータ, レバレッジ,
手荒い挨拶, 緊急支援, ロイヤリティープログラム, 敵対的買収; ko 레나타, 영향력, 악수, 긴급 구제, 충성 고객 우대, 적대적 인수).
Slots: skill = E, skill2 = Q, ult = R; the passive and W (fired by the watch) are told in the attack's text. No combo
sentence in any text (the user's rule). No `league_renata_attack` sound: the engine would play it at the start of every
attack; the shot's sound plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_renata import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_renata"
VERSION = "0.136.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names
M = "<#a974ffff>"      # magic
TR = "<#f5f5f5ff>"     # true damage
A = "<#ffb900ff>"      # durations, counts, percents
E = "<>"
# champion_view: the face at her crown (tfm2_ase.py face: 36 px over the feet); the idle tops 25 px over the pivot, under
# -28, so no banpick_center (the card rule: the card then places her like every hero that fits)
VIEW = {"face": {"x": 1, "y": -36}, "center": {"x": 0, "y": -11}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def a(k, unit=""):
    return f"{A}{{{k}}}{unit}{E}"


TEXT = {
    "zh-hans": {
        "name": "烈娜塔",
        "attack": "手枪普攻。" + O + "物尽其用" + E + "：命中英雄时额外造成最大生命" + a("p_hp", "%") + TR + "真实伤害" + E + "并标记；队友在旁攻击时引爆，造成" +
                  mag("p_pop", "p_pop_ap") + M + "魔法伤害" + E + "。" + O + "及时救难" + E + "：队友被控或团战时自动施放，攻速+" + a("w_as", "%") +
                  "、移速+" + a("w_ms", "%") + "，" + a("w_t", "秒") + "内不会阵亡，结束时回复" + mag("w_heal", "w_heal_ap") + "生命。",
        "skill": "发射一对飞弹，命中敌人或飞到尽头时爆炸，造成" + mag("e_dmg", "e_ap") + M + "魔法伤害" + E + "并减速" + a("e_slow", "%") +
                 "；途经的友方英雄获得" + mag("e_sh", "e_sh_ap") + "护盾，持续" + a("e_sh_t", "秒") + "。",
        "skill2": "射出机械手，抓住第一个敌人，造成" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并禁锢" + a("q_root", "秒") +
                  "，随后把它甩向身后；落点周围的敌人受到" + mag("q2_dmg", "q2_ap") + M + "魔法伤害" + E + "，甩出的是英雄时还会被眩晕" +
                  a("q_stun", "秒") + "。",
        "ult": "附近有2个以上敌方英雄，或敌方英雄被控制时，放出化学波：命中的敌方英雄狂暴" + a("r_t", "秒") + "，不能攻击我方、不能施法，" +
               "每" + a("r_per", "秒") + "攻击身边的队友，造成" + mag("r_hit", "r_hit_ap") + M + "魔法伤害" + E + "。",
        "names": ("忠诚激励", "铁腕竞合", "恶意收购"),
    },
    "zh-hant": {
        "name": "睿娜妲",
        "attack": "手槍普攻。" + O + "唯利是圖" + E + "：命中英雄時額外造成最大生命" + a("p_hp", "%") + TR + "真實傷害" + E + "並標記；隊友在旁攻擊時引爆，造成" +
                  mag("p_pop", "p_pop_ap") + M + "魔法傷害" + E + "。" + O + "急難救助" + E + "：隊友被控或團戰時自動施放，攻速+" + a("w_as", "%") +
                  "、跑速+" + a("w_ms", "%") + "，" + a("w_t", "秒") + "內不會陣亡，結束時回復" + mag("w_heal", "w_heal_ap") + "生命。",
        "skill": "發射一對飛彈，命中敵人或飛到盡頭時爆炸，造成" + mag("e_dmg", "e_ap") + M + "魔法傷害" + E + "並緩速" + a("e_slow", "%") +
                 "；途經的友方英雄獲得" + mag("e_sh", "e_sh_ap") + "護盾，持續" + a("e_sh_t", "秒") + "。",
        "skill2": "射出機械手，抓住第一個敵人，造成" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並定身" + a("q_root", "秒") +
                  "，隨後把它甩向身後；落點周圍的敵人受到" + mag("q2_dmg", "q2_ap") + M + "魔法傷害" + E + "，甩出的是英雄時還會被暈眩" +
                  a("q_stun", "秒") + "。",
        "ult": "附近有2個以上敵方英雄，或敵方英雄被控制時，放出化學波：命中的敵方英雄狂暴" + a("r_t", "秒") + "，不能攻擊我方、不能施法，" +
               "每" + a("r_per", "秒") + "攻擊身邊的隊友，造成" + mag("r_hit", "r_hit_ap") + M + "魔法傷害" + E + "。",
        "names": ("有酬必報", "霸道手腕", "惡意收購"),
    },
    "en": {
        "name": "Renata",
        "attack": "Pistol attacks. " + O + "Leverage" + E + ": hits on champions deal " + a("p_hp", "%") + " of their max health as " + TR +
                  "true damage" + E + " and mark them; an ally attacking beside her pops the mark for " + mag("p_pop", "p_pop_ap") + " " + M +
                  "magic damage" + E + ". " + O + "Bailout" + E + ": cast by itself on an ally in crowd control or in a teamfight: +" +
                  a("w_as", "%") + " attack speed, +" + a("w_ms", "%") + " move speed, cannot die for " + a("w_t", "s") + ", then heals " +
                  mag("w_heal", "w_heal_ap") + ".",
        "skill": "Fires a pair of missiles that burst on the first enemy or at the end: " + mag("e_dmg", "e_ap") + " " + M + "magic damage" +
                 E + " and a " + a("e_slow", "%") + " slow; allied champions they pass get a " + mag("e_sh", "e_sh_ap") + " shield for " +
                 a("e_sh_t", "s") + ".",
        "skill2": "Launches a chemtech hand that grabs the first enemy: " + mag("q_dmg", "q_ap") + " " + M + "magic damage" + E +
                  " and a " + a("q_root", "s") + " root, then flings it behind her; enemies where it lands take " + mag("q2_dmg", "q2_ap") +
                  " " + M + "magic damage" + E + " and, if a champion was thrown, a " + a("q_stun", "s") + " stun.",
        "ult": "With 2+ enemy champions near, or one in crowd control, sends out a chemical wave: enemy champions hit go berserk for " +
               a("r_t", "s") + ", unable to attack her team or cast, lashing out at their own allies every " + a("r_per", "s") +
               " for " + mag("r_hit", "r_hit_ap") + " " + M + "magic damage" + E + ".",
        "names": ("Loyalty Program", "Handshake", "Hostile Takeover"),
    },
    "ko": {
        "name": "레나타",
        "attack": "권총 공격. " + O + "영향력" + E + ": 챔피언 적중 시 최대 체력의 " + a("p_hp", "%") + " " + TR + "고정 피해" + E +
                  "를 주고 표식을 남김. 아군이 곁에서 공격하면 터져 " + mag("p_pop", "p_pop_ap") + "의 " + M + "마법 피해" + E + ". " +
                  O + "긴급 구제" + E + ": 아군이 군중 제어되거나 한타 중이면 자동 시전, 공격 속도 +" + a("w_as", "%") + ", 이동 속도 +" +
                  a("w_ms", "%") + ", " + a("w_t", "초") + " 동안 죽지 않고 끝날 때 " + mag("w_heal", "w_heal_ap") + " 회복.",
        "skill": "미사일 한 쌍 발사, 첫 적이나 끝에서 폭발해 " + mag("e_dmg", "e_ap") + "의 " + M + "마법 피해" + E + "와 " +
                 a("e_slow", "%") + " 둔화. 지나간 아군 챔피언은 " + a("e_sh_t", "초") + " 동안 " + mag("e_sh", "e_sh_ap") + " 보호막.",
        "skill2": "화공 손을 날려 첫 적을 잡아 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" + E + "와 " + a("q_root", "초") +
                  " 속박, 이어서 뒤로 던짐. 떨어진 곳의 적은 " + mag("q2_dmg", "q2_ap") + "의 " + M + "마법 피해" + E +
                  ", 던진 대상이 챔피언이면 " + a("q_stun", "초") + " 기절.",
        "ult": "근처에 적 챔피언이 2명 이상이거나 군중 제어된 적이 있으면 화학 파동 발사: 맞은 적 챔피언은 " + a("r_t", "초") +
               " 동안 광폭해져 우리 편을 공격하거나 스킬을 쓰지 못하고, " + a("r_per", "초") + "마다 자기 아군에게 " +
               mag("r_hit", "r_hit_ap") + "의 " + M + "마법 피해" + E + ".",
        "names": ("충성 고객 우대", "악수", "적대적 인수"),
    },
    "ja": {
        "name": "レナータ",
        "attack": "拳銃で通常攻撃。" + O + "レバレッジ" + E + "：チャンピオンに最大体力の" + a("p_hp", "%") + "の" + TR + "確定ダメージ" + E +
                  "とマーク。味方がそばで攻撃すると爆発し" + mag("p_pop", "p_pop_ap") + "の" + M + "魔法ダメージ" + E + "。" + O +
                  "緊急支援" + E + "：味方が行動妨害中か集団戦で自動発動、攻撃速度+" + a("w_as", "%") + "、移動速度+" + a("w_ms", "%") +
                  "、" + a("w_t", "秒") + "倒れず、終了時" + mag("w_heal", "w_heal_ap") + "回復。",
        "skill": "ミサイル2発を放ち、最初の敵か射程端で爆発して" + mag("e_dmg", "e_ap") + "の" + M + "魔法ダメージ" + E + "と" +
                 a("e_slow", "%") + "スロウ。通過した味方チャンピオンに" + mag("e_sh", "e_sh_ap") + "のシールド（" + a("e_sh_t", "秒") + "）。",
        "skill2": "ケミテックの手で最初の敵を掴み" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" + a("q_root", "秒") +
                  "スネア、背後へ投げ飛ばす。落下地点の敵に" + mag("q2_dmg", "q2_ap") + "の" + M + "魔法ダメージ" + E +
                  "、投げたのがチャンピオンなら" + a("q_stun", "秒") + "スタン。",
        "ult": "敵チャンピオン2体以上が近いか行動妨害中の敵がいる時、化学波を放つ：命中した敵チャンピオンは" + a("r_t", "秒") +
               "狂乱し、こちらへの攻撃とスキルが不可、" + a("r_per", "秒") + "ごとに自分の味方を攻撃して" + mag("r_hit", "r_hit_ap") +
               "の" + M + "魔法ダメージ" + E + "。",
        "names": ("ロイヤリティープログラム", "手荒い挨拶", "敵対的買収"),
    },
}

C = "league_renata_sfx_"
# sound name -> [(clip, volume, delay)] (clip names differ from the sound names: a clip named like its sound is not
# found in game)
SOUNDS = {
    "league_renata_a": [(C + "a", 0.4, 0.0), (C + "a_fly", 0.3, 0.05)],
    "league_renata_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_renata_p_hit": [(C + "p_hit", 0.3, 0.0)],
    "league_renata_p_pop": [(C + "p_pop", 0.5, 0.0)],
    "league_renata_q": [(C + "q", 0.5, 0.0)],
    "league_renata_q_fly": [(C + "q_fly", 0.45, 0.0)],
    "league_renata_q_hit": [(C + "q_hit", 0.55, 0.0)],
    "league_renata_q_fling": [(C + "q_fling", 0.55, 0.0)],
    "league_renata_q_crash": [(C + "q_crash", 0.55, 0.0)],
    "league_renata_w": [(C + "w", 0.5, 0.0)],
    "league_renata_w_buff": [(C + "w_buff", 0.5, 0.0)],
    "league_renata_w_save": [(C + "w_save", 0.6, 0.0)],
    "league_renata_e": [(C + "e", 0.5, 0.0)],
    "league_renata_e_fly": [(C + "e_fly", 0.45, 0.0)],
    "league_renata_e_hit": [(C + "e_hit", 0.45, 0.0)],
    "league_renata_e_boom": [(C + "e_boom", 0.45, 0.0)],
    "league_renata_e_shield": [(C + "e_shield", 0.4, 0.0)],
    "league_renata_r": [(C + "r", 0.6, 0.0)],
    "league_renata_r_wave": [(C + "r_wave", 0.6, 0.0)],
    "league_renata_r_hit": [(C + "r_hit", 0.55, 0.0)],
    "league_renata_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_renata_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_renata_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_renata_vo_r": [(C + "vo_r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_hp", "p_pop", "p_pop_ap", "w_as", "w_ms", "w_heal", "w_heal_ap", "e_dmg", "e_ap", "e_slow",
                           "e_sh", "e_sh_ap", "q_dmg", "q_ap", "q2_dmg", "q2_ap", "r_hit", "r_hit_ap")}
    for k in ("w_t", "e_sh_t", "q_root", "q_stun", "r_t", "r_per"):
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
    a_ = ap.parse_args()
    p = dict(P)
    if a_.params:
        p.update(json.load(open(a_.params, encoding="utf-8")))
    tx = texts(p)
    bad = False
    sys.stdout.reconfigure(encoding="utf-8")
    for lang, (d, _) in tx.items():
        lens = {k: shown_length(TEXT[lang][k]) for k in ("attack", "skill", "skill2", "ult")}
        bad |= any(n_ > TOOLTIP_MAX[lang] for n_ in lens.values())
        print(lang, " ".join(f"{k}:{n_}/{TOOLTIP_MAX[lang]}" for k, n_ in lens.items()))
    if a_.check:
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
    for k in [k for k in ov if ID in k]:      # her keys rebuilt (a renamed sound leaves none behind)
        del ov[k]
    for name in list(SOUNDS) + CLIPS:
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/league/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    view = json.loads(json.dumps(VIEW))
    if a_.face:
        x, y = (int(v) for v in a_.face.split(","))
        view["face"] = {"x": x, "y": y}
    if a_.banpick is not None:
        if a_.banpick > 0:
            sys.exit("never a positive banpick_center y (card-banpick rule)")
        view["banpick_center"] = {"x": 0, "y": a_.banpick}
    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"))
    cv["entries"][ID] = view
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"))
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    if "Renata" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' .]+?)\. Kits", r", \1 and Renata. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
