"""Yuumi's text (5 languages), sound_info files and her keys in the shared files, numbers from build_yuumi.P.

    python tools/kit/setup_yuumi.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_yuumi in every language, description + skill_name),
sound/sfx/league_yuumi_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Yuumi named). Only her keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 悠米 (魔法猫咪): 猫的博爱, 摸鱼飞弹, 悠米出动！, 旺盛精力, 魔典终章; zh_TW 悠咪 (魔法靈貓):
貓貓摯友, 奇幻圖騰, 飛撲抱抱！, 蹦蹦衝刺, 最終篇章; ja ユーミ: ネコはトモダチ, きまぐれミサイル, ユー＆ミー！, バビューン！,
ファイナルチャプター; ko 유미: 야옹이 친구, 사르르탄, 너랑 유미랑!, 슈우우웅, 대단원.
Slots: skill = Q Prowling Projectile, skill2 = W You and Me! with E Zoomies, ult = R Final Chapter; the passive Feline
Friendship is in the attack's text. No combo sentence in any text (the user's rule). The main pack's rules are the ones
written (a timed attach); the add-on league_yuumi keeps her on the ally and says so itself.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_yuumi import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_yuumi"
VERSION = "0.170.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
E = "<>"
# champion_view: the face point between her eyes (set from tfm2_ase.py face once the frames exist)
VIEW = {"face": {"x": 2, "y": -24}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def grn(d, r):
    return f"{G}{{{d}}}{E} + {APi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "悠米",
        "attack": "射出书页光弹。" + O + "猫的博爱" + E + "：每" + A + "{p_cd}秒" + E + "普攻命中英雄时多造成" + mag("p_dmg", "p_ap") +
                  "魔法伤害，回复自己" + grn("p_heal", "p_hap") + "生命，下次附身时队友也回复同样多。",
        "skill": "发射飞弹，打中第一个敌人造成" + mag("q_dmg", "q_ap") + "魔法伤害并减速{q_slow}%；飞了" + A + "{q_t1}秒" + E + "以上改为" +
                 mag("q_edmg", "q_eap") + "，减速{q_eslow}%。",
        "skill2": O + "悠米出动！" + E + "：附身在交战中的队友身上" + A + "{w_t}秒" + E + "（不可选取、跟着他走，照样能放摸鱼飞弹和魔典终章），他每秒回复" +
                  grn("w_heal", "w_hap") + "生命。" + O + "旺盛精力" + E + "：给他" + grn("e_sh", "e_ap") + "护盾，攻速+{e_as}%、移速+{e_ms}%。",
        "ult": "翻开魔典连发{r_n}道波纹，每道造成" + mag("r_dmg", "r_ap") + "魔法伤害并减速，沿途友军回复" + grn("r_heal", "r_hap") +
               "生命；第{r_root_k}道" + R + "定身" + E + A + "{r_root}秒" + E + "。",
        "names": ("摸鱼飞弹", "悠米出动！", "魔典终章"),
    },
    "zh-hant": {
        "name": "悠咪",
        "attack": "射出書頁光彈。" + O + "貓貓摯友" + E + "：每" + A + "{p_cd}秒" + E + "普攻命中英雄時多造成" + mag("p_dmg", "p_ap") +
                  "魔法傷害，回復自己" + grn("p_heal", "p_hap") + "生命，下次附身時隊友也回復同樣多。",
        "skill": "發射飛彈，打中第一個敵人造成" + mag("q_dmg", "q_ap") + "魔法傷害並緩速{q_slow}%；飛了" + A + "{q_t1}秒" + E + "以上改為" +
                 mag("q_edmg", "q_eap") + "，緩速{q_eslow}%。",
        "skill2": O + "飛撲抱抱！" + E + "：附身在交戰中的隊友身上" + A + "{w_t}秒" + E + "（無法被選取、跟著他走，照樣能放奇幻圖騰和最終篇章），他每秒回復" +
                  grn("w_heal", "w_hap") + "生命。" + O + "蹦蹦衝刺" + E + "：給他" + grn("e_sh", "e_ap") + "護盾，攻速+{e_as}%、移速+{e_ms}%。",
        "ult": "翻開魔典連發{r_n}道波紋，每道造成" + mag("r_dmg", "r_ap") + "魔法傷害並緩速，沿途友軍回復" + grn("r_heal", "r_hap") +
               "生命；第{r_root_k}道" + R + "定身" + E + A + "{r_root}秒" + E + "。",
        "names": ("奇幻圖騰", "飛撲抱抱！", "最終篇章"),
    },
    "en": {
        "name": "Yuumi",
        "attack": "Fires a page bolt. " + O + "Feline Friendship" + E + ": every " + A + "{p_cd}s" + E + " an attack on a champion deals " +
                  mag("p_dmg", "p_ap") + " " + M + "magic damage" + E + " more and heals her " + grn("p_heal", "p_hap") +
                  "; the ally she attaches to next is healed as much.",
        "skill": "Fires a missile at the first enemy hit: " + mag("q_dmg", "q_ap") + " " + M + "magic damage" + E + " and {q_slow}% slow; after " +
                 A + "{q_t1}s" + E + " of flight " + mag("q_edmg", "q_eap") + " and {q_eslow}% slow instead.",
        "skill2": O + "You and Me!" + E + ": attaches to an ally in the fight for " + A + "{w_t}s" + E + " (untargetable, moving with him, still casting Prowling Projectile and Final Chapter); he heals " +
                  grn("w_heal", "w_hap") + " a second. " + O + "Zoomies" + E + ": he gets a " + grn("e_sh", "e_ap") + " shield, +{e_as}% attack "
                  "speed and +{e_ms}% move speed.",
        "ult": "Opens the book and sends {r_n} waves: each deals " + mag("r_dmg", "r_ap") + " " + M + "magic damage" + E + " and slows, and heals "
               "allies on its way " + grn("r_heal", "r_hap") + "; wave {r_root_k} " + R + "roots" + E + " for " + A + "{r_root}s" + E + ".",
        "names": ("Prowling Projectile", "You and Me!", "Final Chapter"),
    },
    "ko": {
        "name": "유미",
        "attack": "책장 탄을 쏜다. " + O + "야옹이 친구" + E + ": " + A + "{p_cd}초" + E + "마다 챔피언을 기본 공격하면 " + mag("p_dmg", "p_ap") +
                  " 마법 피해 추가, 자신 " + grn("p_heal", "p_hap") + " 회복, 다음에 붙는 아군도 같은 만큼 회복.",
        "skill": "미사일을 쏴 처음 맞힌 적에게 " + mag("q_dmg", "q_ap") + " 마법 피해, {q_slow}% 둔화. " + A + "{q_t1}초" + E + " 넘게 날면 " +
                 mag("q_edmg", "q_eap") + ", {q_eslow}% 둔화.",
        "skill2": O + "너랑 유미랑!" + E + ": 싸우는 아군에게 " + A + "{w_t}초" + E + " 붙는다(대상 지정 불가, 함께 이동, 사르르탄과 대단원 사용 가능). 아군은 초당 " +
                  grn("w_heal", "w_hap") + " 회복. " + O + "슈우우웅" + E + ": 보호막 " + grn("e_sh", "e_ap") + ", 공격 속도 +{e_as}%, 이동 속도 +{e_ms}%.",
        "ult": "책을 펼쳐 파동 {r_n}개를 보낸다. 파동마다 " + mag("r_dmg", "r_ap") + " 마법 피해와 둔화, 닿은 아군 " + grn("r_heal", "r_hap") +
               " 회복. {r_root_k}번째 파동은 " + A + "{r_root}초" + E + " " + R + "속박" + E + ".",
        "names": ("사르르탄", "너랑 유미랑!", "대단원"),
    },
    "ja": {
        "name": "ユーミ",
        "attack": "ページ弾を撃つ。" + O + "ネコはトモダチ" + E + "：" + A + "{p_cd}秒" + E + "ごとにチャンピオンへの通常攻撃が" + mag("p_dmg", "p_ap") +
                  "の魔法ダメージ追加、自身を" + grn("p_heal", "p_hap") + "回復、次にくっつく味方も同じだけ回復。",
        "skill": "ミサイルを撃ち、最初に当たった敵に" + mag("q_dmg", "q_ap") + "の魔法ダメージと{q_slow}%スロウ。" + A + "{q_t1}秒" + E + "以上飛ぶと" +
                 mag("q_edmg", "q_eap") + "、{q_eslow}%スロウ。",
        "skill2": O + "ユー＆ミー！" + E + "：戦闘中の味方に" + A + "{w_t}秒" + E + "くっつく（対象指定不可、一緒に移動、きまぐれミサイルとファイナルチャプターは使える）。味方は毎秒" +
                  grn("w_heal", "w_hap") + "回復。" + O + "バビューン！" + E + "：シールド" + grn("e_sh", "e_ap") + "、攻撃速度+{e_as}%、移動速度+{e_ms}%。",
        "ult": "本を開き波を{r_n}つ放つ。1つごとに" + mag("r_dmg", "r_ap") + "の魔法ダメージとスロウ、通った味方を" + grn("r_heal", "r_hap") +
               "回復。{r_root_k}つ目は" + A + "{r_root}秒" + E + R + "スネア" + E + "。",
        "names": ("きまぐれミサイル", "ユー＆ミー！", "ファイナルチャプター"),
    },
}

C = "league_yuumi_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {f"league_yuumi_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.3), ("a_hit", 0.35), ("p_hit", 0.45), ("q", 0.4), ("q_hit", 0.45), ("q_ehit", 0.55), ("w", 0.4),
    ("w_on", 0.4), ("w_off", 0.4), ("e_hit", 0.45), ("r", 0.5), ("r_wave", 0.35), ("r_hit", 0.35), ("r_heal", 0.3),
    ("vo_q", 0.85), ("vo_w", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "p_heal", "p_hap", "q_dmg", "q_ap", "q_slow", "q_edmg", "q_eap", "q_eslow",
                           "w_heal", "w_hap", "e_sh", "e_ap", "e_as", "e_ms", "r_n", "r_dmg", "r_ap", "r_heal", "r_hap",
                           "r_root_k")}
    for k in ("p_cd", "q_t1", "w_t", "r_root"):
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
    if "Yuumi" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Yuumi. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
