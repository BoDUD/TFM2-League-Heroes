"""Karma's text (5 languages), sound_info files and her keys in the shared files, numbers from build_karma.P.

    python tools/kit/setup_karma.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in kr/league): text/champion.i18n (league_karma in every language, description + skill_name),
sound/sfx/league_karma_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.84.0, Karma named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/kr/rst.py: 卡尔玛 / 天启者, 聚能之炎, 心灵烈焰, 坚定不移, 鼓舞, 梵咒; the
Mantra bonuses 灵光闪耀, 焕发, 蔑视) and Data Dragon 16.19.1 (zh_TW 卡瑪 / 炎靈融合 / 輪迴怒火 / 特化鏈結 / 靈能啟示 / 真言符印,
ko 카르마 / 열정 응집 / 내면의 열정 / 굳은 결의 / 고무 / 만트라, ja カルマ / 寄せ火 / 心炎 / 魂縛 / 激励 / マントラ; those three
name no bonus, the text says "Mantra + Q"). Slots: skill = Q, skill2 = W, ult = R; the passive and the automatic E are told
in the attack's text. No `league_karma_attack` sound: the engine would play it at the start of every attack; the bolt
sounds play from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_karma import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_karma"
VERSION = "0.84.9"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
S = "<#9fd8ffff>"      # shields
G = "<#7cfc00ff>"      # health
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 1, "y": -32}, "center": {"x": 0, "y": -11}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def sh(d, r):
    return f"{S}{{{d}}}{E} + {APi}{S}{{{r}}}%{E}"


def heal(d, r):
    return f"{G}{{{d}}}{E} + {APi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "卡尔玛",
        "attack": "射出灵能飞弹。" + O + "聚能之炎" + E + "：技能命中英雄，梵咒冷却最多缩短" + A + "{g_max}%" + E + "。" + O + "鼓舞" + E +
                  "（自动，" + A + "{e_cd}秒" + E + "）：给被控或交战中的队友（或自己）" + sh("e_sh", "e_ap") + S + "护盾" + E +
                  "，移速+" + A + "{e_ms}%" + E + "。",
        "skill": "射出灵火，命中首个敌人爆炸，周围敌人受到" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并" + R + "减速{q_slow}%" + E +
                 "。" + O + "灵光闪耀" + E + "（梵咒）：额外" + mag("rq_dmg", "rq_ap") + "伤害并留下火环，" + A + "{rq_wait}秒" + E +
                 "后爆发造成" + mag("rq_dmg2", "rq_ap2") + "伤害、" + R + "减速{rq_slow}%" + E + "。",
        "skill2": "连住敌方英雄，造成" + mag("w_dmg", "w_ap") + M + "魔法伤害" + E + "；" + A + "{w_hold}秒" + E + "未挣脱则再次受伤并" + R +
                  "禁锢{w_root}秒" + E + "。" + O + "焕发" + E + "（梵咒，被围攻时）：回复" + heal("rw_heal", "rw_ap") + "生命，" + R +
                  "禁锢{rw_root}秒" + E + "。" + O + "连招" + E + "：禁锢时梵咒Q随即跟上。",
        "ult": "强化" + A + "{r_arm}秒" + E + "内的下一个技能：队友危险时立即" + O + "蔑视" + E + "（附近队友都获得" + sh("re_sh", "re_ap") +
               S + "护盾" + E + "和加速），否则强化Q或被围攻时的W。未使用则返还冷却。",
        "names": ("心灵烈焰", "坚定不移", "梵咒"),
    },
    "zh-hant": {
        "name": "卡瑪",
        "attack": "射出靈能飛彈。" + O + "炎靈融合" + E + "：技能命中英雄，真言符印冷卻最多縮短" + A + "{g_max}%" + E + "。" + O + "靈能啟示" +
                  E + "（自動，" + A + "{e_cd}秒" + E + "）：給被控或交戰中的隊友（或自己）" + sh("e_sh", "e_ap") + S + "護盾" + E +
                  "，跑速+" + A + "{e_ms}%" + E + "。",
        "skill": "射出靈火，命中首個敵人爆炸，周圍敵人受到" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並" + R + "緩速{q_slow}%" + E +
                 "。" + O + "真言加持" + E + "：額外" + mag("rq_dmg", "rq_ap") + "傷害並留下火環，" + A + "{rq_wait}秒" + E +
                 "後爆發造成" + mag("rq_dmg2", "rq_ap2") + "傷害、" + R + "緩速{rq_slow}%" + E + "。",
        "skill2": "連住敵方英雄，造成" + mag("w_dmg", "w_ap") + M + "魔法傷害" + E + "；" + A + "{w_hold}秒" + E + "未掙脫則再次受傷並" + R +
                  "定身{w_root}秒" + E + "。" + O + "真言加持" + E + "（被圍攻時）：回復" + heal("rw_heal", "rw_ap") + "生命，" + R +
                  "定身{rw_root}秒" + E + "。" + O + "連招" + E + "：定身時真言Q隨即跟上。",
        "ult": "強化" + A + "{r_arm}秒" + E + "內的下一項技能：隊友危險時立即強化靈能啟示（附近隊友都獲得" + sh("re_sh", "re_ap") + S +
               "護盾" + E + "和跑速），否則強化Q或被圍攻時的W。未使用則返還冷卻。",
        "names": ("輪迴怒火", "特化鏈結", "真言符印"),
    },
    "en": {
        "name": "Karma",
        "attack": "Fires a spirit bolt. " + O + "Gathering Fire" + E + ": spell hits on champions cut Mantra's cooldown by up to " +
                  A + "{g_max}%" + E + ". " + O + "Inspire" + E + " (automatic, " + A + "{e_cd}s" + E + "): an ally in crowd "
                  "control or in a fight (or Karma) gets a " + sh("e_sh", "e_ap") + " " + S + "shield" + E + " and " + A +
                  "+{e_ms}%" + E + " move speed.",
        "skill": "Fires a spirit flame that bursts on the first enemy hit: enemies around take " + mag("q_dmg", "q_ap") + " " + M +
                 "magic damage" + E + " and are " + R + "slowed by {q_slow}%" + E + ". " + O + "Soulflare" + E + " (Mantra): " +
                 mag("rq_dmg", "rq_ap") + " more and a circle of flame that blows " + A + "{rq_wait}s" + E + " later for " +
                 mag("rq_dmg2", "rq_ap2") + ", " + R + "slowing {rq_slow}%" + E + ".",
        "skill2": "Tethers an enemy champion for " + mag("w_dmg", "w_ap") + " " + M + "magic damage" + E + "; unbroken for " + A +
                  "{w_hold}s" + E + " it deals the damage again and " + R + "roots for {w_root}s" + E + ". " + O + "Renewal" + E +
                  " (Mantra, when crowded): heals " + heal("rw_heal", "rw_ap") + " and " + R + "roots for {rw_root}s" + E + ". " +
                  O + "Combo" + E + ": a root is followed by a Soulflare.",
        "ult": "Empowers her next spell within " + A + "{r_arm}s" + E + ": with an ally in danger, " + O + "Defiance" + E + " at once "
               "(allies around him get a " + sh("re_sh", "re_ap") + " " + S + "shield" + E + " and the haste); else the next Q, "
               "or W when crowded. Unused, the cooldown comes back.",
        "names": ("Inner Flame", "Focused Resolve", "Mantra"),
    },
    "ko": {
        "name": "카르마",
        "attack": "영혼의 탄을 쏩니다. " + O + "열정 응집" + E + ": 스킬이 챔피언에게 맞으면 만트라 재사용 대기시간이 최대 " + A +
                  "{g_max}%" + E + " 줄어듭니다. " + O + "고무" + E + "(자동, " + A + "{e_cd}초" + E + "): 군중 제어에 걸렸거나 교전 중인 "
                  "아군(또는 카르마)에게 " + sh("e_sh", "e_ap") + "의 " + S + "보호막" + E + "과 이동 속도 " + A + "+{e_ms}%" + E + ".",
        "skill": "영혼의 불꽃을 쏘아 처음 맞힌 적에게서 터뜨려 주변 적에게 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" + E + "와 " +
                 R + "{q_slow}% 둔화" + E + ". " + O + "만트라" + E + ": " + mag("rq_dmg", "rq_ap") + "의 추가 피해와 불꽃 원을 남기고, " + A +
                 "{rq_wait}초" + E + " 뒤 터져 " + mag("rq_dmg2", "rq_ap2") + "의 피해와 " + R + "{rq_slow}% 둔화" + E + ".",
        "skill2": "적 챔피언과 연결해 " + mag("w_dmg", "w_ap") + "의 " + M + "마법 피해" + E + "; " + A + "{w_hold}초" + E + " 동안 끊어지지 않으면 "
                  "피해를 다시 입히고 " + R + "{w_root}초 속박" + E + ". " + O + "만트라" + E + "(포위됐을 때): " + heal("rw_heal", "rw_ap") +
                  "의 체력 회복, " + R + "{rw_root}초 속박" + E + ". " + O + "연계" + E + ": 속박되면 강화된 Q가 이어서 나감.",
        "ult": A + "{r_arm}초" + E + " 안에 쓰는 다음 스킬을 강화합니다: 아군이 위험하면 바로 강화된 고무(주변 아군 모두 " + sh("re_sh", "re_ap") +
               "의 " + S + "보호막" + E + "과 이동 속도), 아니면 다음 Q나 포위됐을 때의 W. 쓰지 않으면 재사용 대기시간을 돌려받습니다.",
        "names": ("내면의 열정", "굳은 결의", "만트라"),
    },
    "ja": {
        "name": "カルマ",
        "attack": "霊弾を撃つ。" + O + "寄せ火" + E + "：スキルがチャンピオンに当たるとマントラのクールダウンが最大" + A + "{g_max}%" + E +
                  "短縮。" + O + "激励" + E + "（自動、" + A + "{e_cd}秒" + E + "）：行動妨害中か交戦中の味方（または自身）に" +
                  sh("e_sh", "e_ap") + "の" + S + "シールド" + E + "と移動速度" + A + "+{e_ms}%" + E + "。",
        "skill": "霊炎を放ち最初の敵で炸裂、周囲の敵に" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" + R + "{q_slow}%スロウ" + E +
                 "。" + O + "マントラ" + E + "：追加" + mag("rq_dmg", "rq_ap") + "、炎の輪が" + A + "{rq_wait}秒" + E + "後に爆発し" +
                 mag("rq_dmg2", "rq_ap2") + "と" + R + "{rq_slow}%スロウ" + E + "。",
        "skill2": "敵チャンピオンと鎖で繋ぎ" + mag("w_dmg", "w_ap") + "の" + M + "魔法ダメージ" + E + "。" + A + "{w_hold}秒" + E + "切れなければ"
                  "再度ダメージと" + R + "{w_root}秒スネア" + E + "。" + O + "マントラ" + E + "（囲まれた時）：" + heal("rw_heal", "rw_ap") +
                  "回復、" + R + "{rw_root}秒スネア" + E + "。" + O + "コンボ" + E + "：スネアに強化Qが続く。",
        "ult": A + "{r_arm}秒" + E + "以内の次のスキルを強化：味方が危険なら即座に強化激励（周囲の味方にも" + sh("re_sh", "re_ap") + "の" + S +
               "シールド" + E + "と移動速度）、それ以外は次のQか囲まれた時のW。使わなければクールダウンが戻る。",
        "names": ("心炎", "魂縛", "マントラ"),
    },
}

C = "league_karma_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
S_ = "league_karma_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    S_ + "a_cast": [(C + "attack", 0.4, 0.0)],
    S_ + "a_hit": [(C + "attack_hit", 0.35, 0.0)],
    S_ + "q_cast": [(C + "q", 0.5, 0.0)],
    S_ + "q_hit": [(C + "q_hit", 0.5, 0.0)],
    S_ + "rq_hit": [(C + "rq_hit", 0.55, 0.0)],
    S_ + "rq_field": [(C + "rq_field", 0.55, 0.0)],
    S_ + "w_cast": [(C + "w", 0.5, 0.0)],
    S_ + "w_root": [(C + "w_root", 0.5, 0.0)],
    S_ + "e_cast": [(C + "e", 0.45, 0.0)],
    S_ + "re_cast": [(C + "re", 0.55, 0.0)],
    S_ + "r_cast": [(C + "r", 0.55, 0.0)],
    S_ + "vo_q": [(C + "vo_q", 0.8, 0.0)],
    S_ + "vo_w": [(C + "vo_w", 0.8, 0.0)],
    S_ + "vo_e": [(C + "vo_e", 0.8, 0.0)],
    S_ + "vo_r": [(C + "vo_r", 0.8, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    keys = ("q_dmg", "q_ap", "q_slow", "rq_dmg", "rq_ap", "rq_dmg2", "rq_ap2", "rq_slow", "w_dmg", "w_ap", "rw_heal",
            "rw_ap", "e_sh", "e_ap", "e_ms", "re_sh", "re_ap")
    v = {k: p[k] for k in keys}
    v["g_max"] = min(p["g_step"] * p["g_rungs"], 90)
    v.update({k: secs(p[k]) for k in ("e_cd", "rq_wait", "w_hold", "w_root", "rw_root", "r_arm")})
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
    for k in [k for k in ov if ID in k]:      # her keys rebuilt (a renamed sound leaves none behind)
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
    if "Karma" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Karma. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
