"""Powder's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_powder.P.

    python tools/kit/setup_powder.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft): mod.mod_info (made when missing; VERSION, Powder named),
text/champion.i18n (tft_powder in every language, description + skill_name), sound/sfx/tft_powder_*.sound_info,
mod.override_info (the text and champion_view merges and every sound), style/champion_view (face, centre,
banpick_center). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each
text's shown length against lint_mod's TOOLTIP_MAX.
Names: TFT set 13 zh_CN 爆爆 (Powder), zh_TW 爆爆, ja パウダー, ko 파우더. Her skills are our own (TFT has one ability,
the monkey bomb): 猴子炸弹 / 快跑，爆爆！/ 海克斯水晶炸弹, the passive 伏击者 (TFT's Ambusher trait) in the attack's text.

Sounds: no audio file of ours. Every clip below is one of the base game's own sound effects, played by name from our
.sound_info (asset/base/sound/sfx/<clip>, the way the base events play them), layered and mixed into her own events;
League's audio is Riot's and never used for this pack. A clip name never equals an event name (vo-clip-names rule).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_powder import P, lp, MOD_ID, ID  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
VERSION = "0.1.0"
NAME = "Teamfight Tactics Heroes"
# the pack's description, shared with tools/kit/setup_norra.py, setup_alune.py and setup_silco.py (every hero of the
# pack in HEROES)
DESC = ("Teamfight Tactics units that League of Legends does not have, for Teamfight Manager 2: {heroes}. Powder's, "
        "Alune's and Silco's kits are our own designs, drawn from TFT and Arcane; Norra's follows League of Legends: "
        "Wild Rift (what the data cannot play is the pack's own code, tft.dll). Sharper frames when the League of "
        "Legends Heroes pack (league) is also enabled. Non-commercial fan project; Teamfight Tactics, Wild Rift "
        "and Arcane (c) Riot Games.")
HEROES = ["Powder", "Norra", "Alune", "Silco", "Maddie", "Loris", "Kobuko", "Vander", "Violet", "Krug", "Ao Shin", "Scar", "Renni"]
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between her eyes, 10 px under the crown (tfm2_ase.py face: crown 35 px up; lint_mod allows
# 10 under the crown); her idle's top is 23.5 px over the pivot: the ban/pick card fits it, no banpick_center
VIEW = {"face": {"x": 0, "y": -25}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "爆爆",
        "attack": "扔出自制小鞭炮，造成" + AD + O + "物理伤害" + E + "。" + O + "伏击者" + E + "：技能炸弹可以暴击（" + A + "{p_crit}%" + E +
                  "几率，伤害翻倍）。",
        "skill": "把上了发条的猴子炸弹丢到目标脚下，范围内敌人受到" + mag("q_dmg", "q_ratio") + "魔法伤害，中心再受一次；被炸到的敌人" + R +
                 "灼烧" + E + A + "{q_burn_t}秒" + E + "，并" + R + "重伤" + E + A + "{q_wound_t}秒" + E + "（受到治疗-{q_wound}%）。",
        "skill2": "敌方英雄靠近时摔下闪光烟雾弹：周围敌人受到" + mag("e_dmg", "e_ratio") + "魔法伤害并" + R + "致盲" + E + A + "{e_blind}秒" + E +
                  "（无法普攻），自己向后跳开。",
        "ult": "把装着海克斯水晶的包丢向敌方英雄，引线烧完" + A + "{r_fuse}秒" + E + "后蓝光大爆炸：范围内敌人受到" + mag("r_dmg", "r_ratio") +
               "魔法伤害并" + R + "击飞" + E + A + "{r_up}秒" + E + "。",
        "names": ("猴子炸弹", "快跑，爆爆！", "海克斯水晶炸弹"),
    },
    "zh-hant": {
        "name": "爆爆",
        "attack": "扔出自製小鞭炮，造成" + AD + O + "物理傷害" + E + "。" + O + "伏擊者" + E + "：技能炸彈可以暴擊（" + A + "{p_crit}%" + E +
                  "機率，傷害加倍）。",
        "skill": "把上了發條的猴子炸彈丟到目標腳下，範圍內敵人受到" + mag("q_dmg", "q_ratio") + "魔法傷害，中心再受一次；被炸到的敵人" + R +
                 "燃燒" + E + A + "{q_burn_t}秒" + E + "，並" + R + "重傷" + E + A + "{q_wound_t}秒" + E + "（受到治療-{q_wound}%）。",
        "skill2": "敵方英雄靠近時摔下閃光煙霧彈：周圍敵人受到" + mag("e_dmg", "e_ratio") + "魔法傷害並" + R + "致盲" + E + A + "{e_blind}秒" + E +
                  "（無法普攻），自己向後跳開。",
        "ult": "把裝著海克斯水晶的包丟向敵方英雄，引線燒完" + A + "{r_fuse}秒" + E + "後藍光大爆炸：範圍內敵人受到" + mag("r_dmg", "r_ratio") +
               "魔法傷害並" + R + "擊飛" + E + A + "{r_up}秒" + E + "。",
        "names": ("猴子炸彈", "快跑，爆爆！", "海克斯水晶炸彈"),
    },
    "en": {
        "name": "Powder",
        "attack": "Throws a homemade firecracker for " + AD + " " + O + "physical damage" + E + ". " + O + "Ambusher" + E +
                  ": her skill bombs can crit (" + A + "{p_crit}%" + E + " chance, double damage).",
        "skill": "Lobs her wind-up monkey bomb at the target's feet: enemies in the blast take " + mag("q_dmg", "q_ratio") + " " + M +
                 "magic damage" + E + ", those in the middle take it twice. Everyone hit " + R + "burns" + E + " for " + A +
                 "{q_burn_t}s" + E + " and is " + R + "wounded" + E + " for " + A + "{q_wound_t}s" + E + " (healing -{q_wound}%).",
        "skill2": "When an enemy champion comes close, smashes a flash-smoke bomb: enemies around her take " + mag("e_dmg", "e_ratio") +
                  " " + M + "magic damage" + E + " and are " + R + "blinded" + E + " for " + A + "{e_blind}s" + E +
                  " (no basic attacks), and she hops back.",
        "ult": "Lobs the bag with the hex crystal at an enemy champion. After a " + A + "{r_fuse}s" + E + " fuse it bursts in blue: "
               "enemies in the blast take " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + " and are " + R + "knocked up" + E +
               " for " + A + "{r_up}s" + E + ".",
        "names": ("Monkey Bomb", "Run, Powder!", "Hex Crystal Bomb"),
    },
    "ko": {
        "name": "파우더",
        "attack": "직접 만든 폭죽을 던져 " + AD + " 물리 피해. " + O + "매복자" + E + ": 스킬 폭탄이 치명타로 터질 수 있다(" + A + "{p_crit}%" + E +
                  ", 피해 2배).",
        "skill": "태엽 원숭이 폭탄을 대상의 발밑에 던져 폭발 범위의 적에게 " + mag("q_dmg", "q_ratio") + " 마법 피해, 중심은 한 번 더. 맞은 적은 " + A +
                 "{q_burn_t}초" + E + " " + R + "불태움" + E + ", " + A + "{q_wound_t}초" + E + " " + R + "상처" + E + "(받는 회복 -{q_wound}%).",
        "skill2": "적 챔피언이 다가오면 섬광 연막탄을 터뜨려 주변 적에게 " + mag("e_dmg", "e_ratio") + " 마법 피해와 " + A + "{e_blind}초" + E + " " + R +
                  "실명" + E + "(기본 공격 불가), 자신은 뒤로 뛴다.",
        "ult": "마법공학 수정이 든 가방을 적 챔피언에게 던진다. " + A + "{r_fuse}초" + E + " 뒤 푸른 폭발: 범위의 적에게 " + mag("r_dmg", "r_ratio") +
               " 마법 피해와 " + A + "{r_up}초" + E + " " + R + "공중에 띄움" + E + ".",
        "names": ("원숭이 폭탄", "도망쳐, 파우더!", "마법공학 수정 폭탄"),
    },
    "ja": {
        "name": "パウダー",
        "attack": "手作りの爆竹を投げ、" + AD + "の物理ダメージ。" + O + "アンブッシャー" + E + "：スキルの爆弾がクリティカルする（" + A + "{p_crit}%" + E +
                  "、ダメージ2倍）。",
        "skill": "ぜんまい仕掛けのモンキーボムを対象の足元に投げ、範囲の敵に" + mag("q_dmg", "q_ratio") + "の魔法ダメージ、中心はもう一度。当たった敵は" + A +
                 "{q_burn_t}秒" + E + R + "炎上" + E + "、" + A + "{q_wound_t}秒" + E + R + "重傷" + E + "（回復-{q_wound}%）。",
        "skill2": "敵チャンピオンが近づくと閃光煙幕弾を叩きつけ、周りの敵に" + mag("e_dmg", "e_ratio") + "の魔法ダメージと" + A + "{e_blind}秒" + E + R +
                  "ブラインド" + E + "（通常攻撃不可）、自分は後ろへ跳ぶ。",
        "ult": "ヘクスクリスタル入りの鞄を敵チャンピオンへ投げる。" + A + "{r_fuse}秒" + E + "後に青く大爆発：範囲の敵に" + mag("r_dmg", "r_ratio") +
               "の魔法ダメージと" + A + "{r_up}秒" + E + R + "ノックアップ" + E + "。",
        "names": ("モンキーボム", "逃げて、パウダー！", "ヘクスクリスタル爆弾"),
    },
}

# sound name -> [(base clip, volume, delay)]: base sound effects layered into her own events
SOUNDS = {
    f"{ID}_a": [("alchemist_attack_cast_resource", 0.35, 0.0)],
    f"{ID}_a_hit": [("bomber_attack_hit_resource", 0.35, 0.0)],
    f"{ID}_q": [("clown_skill_resource", 0.4, 0.0), ("alchemist_skill_cast_resource", 0.35, 0.05)],
    f"{ID}_q_blast": [("gambler_skill2_boom_resource", 0.5, 0.0), ("bomber_skill_hit_resource", 0.45, 0.02)],
    f"{ID}_q_hit": [("alchemist_skill2_hit_resource", 0.25, 0.0)],
    f"{ID}_e": [("ninja_attack0", 0.3, 0.0)],
    f"{ID}_e_pop": [("ninja_skill2_resource2", 0.45, 0.0), ("bomber_skill2_resource", 0.35, 0.0)],
    f"{ID}_e_hit": [("illusionist_attack0", 0.25, 0.0)],
    f"{ID}_r": [("strongman_ult_throw_resource", 0.45, 0.0), ("magic_knight_skill2_resource1", 0.35, 0.05)],
    f"{ID}_r_fuse": [("bomber_trap_on_resource", 0.45, 0.0), ("alchemist_skill_loop_resource", 0.3, 0.3)],
    f"{ID}_r_blast": [("dokkaebi_ult_explode_resource", 0.55, 0.0), ("exorcist_ult_explode_resource", 0.5, 0.0),
                      ("spirit_caller_ult_resource_explode", 0.45, 0.05)],
    f"{ID}_r_hit": [("astrologer_skill1_impact_resource", 0.3, 0.0)],
}


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_crit", "q_dmg", "q_ratio", "q_wound", "e_dmg", "e_ratio", "r_dmg", "r_ratio")}
    for k in ("q_burn_t", "q_wound_t", "e_blind", "r_fuse", "r_up"):
        v[k] = secs(p[k])
    return v


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def load(path, default=None):
    if default is not None and not os.path.isfile(lp(path)):
        return default
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    os.makedirs(os.path.dirname(lp(path)), exist_ok=True)
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

    i18n = load(os.path.join(MOD, "text", "champion.i18n"), {})
    for lang, (d, names) in tx.items():
        i18n.setdefault(lang, {}).setdefault("description", {})[ID] = d
        i18n[lang].setdefault("skill_name", {})[ID] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    for name, plays in SOUNDS.items():
        for c, _, _ in plays:
            if c == name:
                sys.exit(f"{name}: plays a clip of its own name")
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    ov.setdefault("asset/base/text/champion", {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"})
    ov.setdefault("asset/base/style/champion_view",
                  {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"})
    for k in [k for k in ov if ID + "_" in k]:      # her keys rebuilt (a renamed sound leaves none behind)
        del ov[k]
    for name in SOUNDS:
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/{MOD_ID}/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    view = json.loads(json.dumps(VIEW))
    if a.face:
        x, y = (int(v) for v in a.face.split(","))
        view["face"] = {"x": x, "y": y}
    if a.banpick is not None:
        if a.banpick > 0:
            sys.exit("never a positive banpick_center y (card-banpick rule)")
        view["banpick_center"] = {"x": 0, "y": a.banpick}
    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"), {"entries": {}})
    cv["entries"][ID] = view
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"), {
        "author": "BoDUD", "dependencies": [{"mod_id": "base", "version": ">=0.4.11"}], "description": "",
        "last_updated": "2026-10-19", "mod_id": MOD_ID, "name": NAME, "version": VERSION})
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    mi["description"] = DESC.format(heroes=", ".join(HEROES))
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
