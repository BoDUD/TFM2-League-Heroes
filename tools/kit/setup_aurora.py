"""Aurora's text (5 languages), sound_info files and her keys in the shared files, numbers from build_aurora.P.

    python tools/kit/setup_aurora.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_aurora in every language, description + skill_name),
sound/sfx/league_aurora_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Aurora named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 阿萝拉 (双界灵兔): 驱灵奇术; 飞去来咒, 灵纱洞开, 怪奇喷涌, 双界合一; zh_TW 歐羅拉 (跨界靈使):
精靈附體; 二重靈咒, 跨越兩界, 靈異逆躍, 雙界合一; ja オーロラ: 精霊の解放; 折れ重なる魔法, ベールを越えて, ウィアーディング,
世界の狭間; ko 오로라: 영혼 방호술; 이중 저주, 장막 너머로, 마법의 문, 세계의 경계.
Slots: skill = Twofold Hex, skill2 = The Weirding, ult = Between Worlds; the passive (Across the Veil folded in) in the
attack's text - the main pack's stand-in (an enemy champion on top of her); the add-on's text (addons/league_aurora
make_override.py) says the low-health one it reads. No combo sentence in any text (the user's rule); the README says them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_aurora import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_aurora"
VERSION = "0.199.0"     # the next free number above main 0.198.0 (Varus PPU #478) (2026-10-23)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: the face point between her eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card (set at export:
# tools/art/bp_card_audit.py)
VIEW = {"face": {"x": 1, "y": -27}, "center": {"x": 0, "y": -18}, "banpick_center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


def hl(x):
    return G + x + E


TEXT = {
    "zh-hans": {
        "name": "阿萝拉",
        "attack": "魔杖点出灵光。" + n("驱灵奇术") + "：命中英雄叠层，第三层抽出灵物，造成" + mag("p_dmg", "p_ratio") + "+{p_hp}%最大生命值的伤害，" +
                  hl("回复") + mag("p_heal", "p_heal_r") + "生命并加速。" + n("灵纱洞开") + "：被敌方英雄贴身时后跳，隐身" + t("{w_inv}秒") + "、加速{w_ms}%（" +
                  t("{w_cd}秒") + "一次）。",
        "skill": "放出咒弹穿过敌人，造成" + mag("q_dmg", "q_ratio") + "魔法伤害并留下诅咒；" + t("{q_hold}秒") + "后把诅咒抽回，回程再造成" +
                 mag("q2_dmg", "q2_ratio") + "魔法伤害。",
        "skill2": "向前喷出灵魂冲击，造成" + mag("e_dmg", "e_ratio") + "魔法伤害并" + cc("减速") + "{e_slow1}%（逐渐减弱），随后向后跳开。",
        "ult": "跳到敌方英雄身上，冲击波造成" + mag("r_dmg", "r_ratio") + "魔法伤害并" + cc("减速") + "{r_slow1}%；张开领域" + t("{r_t}秒") + "，" +
               cc("减速") + "其中敌人{r_slow}%，目标走开时她穿过领域追上去。",
        "names": ("飞去来咒", "怪奇喷涌", "双界合一"),
    },
    "zh-hant": {
        "name": "歐羅拉",
        "attack": "魔杖點出靈光。" + n("精靈附體") + "：命中英雄疊層，第三層抽出精靈，造成" + mag("p_dmg", "p_ratio") + "+{p_hp}%最大生命值的傷害，" +
                  hl("回復") + mag("p_heal", "p_heal_r") + "生命並加速。" + n("跨越兩界") + "：被敵方英雄貼身時後跳，隱形" + t("{w_inv}秒") + "、加速{w_ms}%（" +
                  t("{w_cd}秒") + "一次）。",
        "skill": "放出咒彈穿過敵人，造成" + mag("q_dmg", "q_ratio") + "魔法傷害並留下詛咒；" + t("{q_hold}秒") + "後把詛咒抽回，回程再造成" +
                 mag("q2_dmg", "q2_ratio") + "魔法傷害。",
        "skill2": "向前噴出靈魂衝擊，造成" + mag("e_dmg", "e_ratio") + "魔法傷害並" + cc("緩速") + "{e_slow1}%（逐漸減弱），隨後向後跳開。",
        "ult": "跳到敵方英雄身上，衝擊波造成" + mag("r_dmg", "r_ratio") + "魔法傷害並" + cc("緩速") + "{r_slow1}%；張開領域" + t("{r_t}秒") + "，" +
               cc("緩速") + "其中敵人{r_slow}%，目標走開時她穿過領域追上去。",
        "names": ("二重靈咒", "靈異逆躍", "雙界合一"),
    },
    "en": {
        "name": "Aurora",
        "attack": "A spirit bolt off her wand. " + n("Spirit Abjuration") + ": her hits on champions add up; the third exorcises a "
                  "spirit for " + mag("p_dmg", "p_ratio") + " + {p_hp}% of the target's max health, and it " + hl("heals") + " her " +
                  mag("p_heal", "p_heal_r") + " and speeds her up. " + n("Across the Veil") + ": with an enemy champion on top of her, "
                  "she hops back, " + "invisible for " + t("{w_inv}s") + " and {w_ms}% faster (once every " + t("{w_cd}s") + ").",
        "skill": "A hex flies through her enemies for " + mag("q_dmg", "q_ratio") + " magic damage, cursing them; " +
                 t("{q_hold}s") + " later the curses are drawn back, dealing " + mag("q2_dmg", "q2_ratio") + " magic damage on the "
                 "way home.",
        "skill2": "A blast of spirit magic before her: " + mag("e_dmg", "e_ratio") + " magic damage and a " + cc("slow") +
                  " of {e_slow1}% that fades; then she hops back.",
        "ult": "Leaps onto an enemy champion: the shockwave deals " + mag("r_dmg", "r_ratio") + " magic damage and " + cc("slows") +
               " {r_slow1}%; a realm opens for " + t("{r_t}s") + ", " + cc("slowing") + " the enemies in it {r_slow}%, and she "
               "steps across it after her target when it walks away.",
        "names": ("Twofold Hex", "The Weirding", "Between Worlds"),
    },
    "ko": {
        "name": "오로라",
        "attack": "지팡이로 영혼 빛을 쏜다. " + n("영혼 방호술") + ": 챔피언 적중이 쌓여 세 번째에 영혼을 뽑아 " + mag("p_dmg", "p_ratio") +
                  " + 최대 체력의 {p_hp}% 피해, " + mag("p_heal", "p_heal_r") + " " + hl("회복") + "과 이동 속도 증가. " + n("장막 너머로") +
                  ": 적 챔피언이 붙으면 뒤로 뛰어 " + t("{w_inv}초") + " 투명, 이동 속도 +{w_ms}% (" + t("{w_cd}초") + "마다).",
        "skill": "주문 탄이 적을 꿰뚫어 " + mag("q_dmg", "q_ratio") + " 마법 피해와 저주; " + t("{q_hold}초") + " 뒤 저주를 끌어당겨 돌아오는 길에 " +
                 mag("q2_dmg", "q2_ratio") + " 마법 피해.",
        "skill2": "앞으로 영혼 충격파를 뿜어 " + mag("e_dmg", "e_ratio") + " 마법 피해와 점점 약해지는 {e_slow1}% " + cc("둔화") +
                  ", 이후 뒤로 뛴다.",
        "ult": "적 챔피언에게 도약해 충격파로 " + mag("r_dmg", "r_ratio") + " 마법 피해와 {r_slow1}% " + cc("둔화") + "; " + t("{r_t}초") +
               " 동안 영역을 열어 안의 적을 {r_slow}% " + cc("둔화") + ", 대상이 벗어나면 영역을 건너 쫓아간다.",
        "names": ("이중 저주", "마법의 문", "세계의 경계"),
    },
    "ja": {
        "name": "オーロラ",
        "attack": "杖から霊光を放つ。" + n("精霊の解放") + "：英雄への命中が重なり、3回目で精霊を引き出し" + mag("p_dmg", "p_ratio") +
                  "＋最大体力の{p_hp}%のダメージ、" + mag("p_heal", "p_heal_r") + hl("回復") + "し加速。" + n("ベールを越えて") +
                  "：敵英雄に詰められると後ろへ跳び" + t("{w_inv}秒") + "透明、移動速度+{w_ms}%（" + t("{w_cd}秒") + "ごと）。",
        "skill": "呪弾が敵を貫き" + mag("q_dmg", "q_ratio") + "の魔法ダメージと呪い、" + t("{q_hold}秒") + "後に呪いを引き戻し帰り道で" +
                 mag("q2_dmg", "q2_ratio") + "の魔法ダメージ。",
        "skill2": "前方へ霊の衝撃を放ち" + mag("e_dmg", "e_ratio") + "の魔法ダメージと弱まっていく{e_slow1}%" + cc("スロウ") + "、その後後ろへ跳ぶ。",
        "ult": "敵英雄へ跳び衝撃波で" + mag("r_dmg", "r_ratio") + "の魔法ダメージと{r_slow1}%" + cc("スロウ") + "。" + t("{r_t}秒") +
               "間領域を開き中の敵を{r_slow}%" + cc("スロウ") + "、対象が離れると領域を越えて追う。",
        "names": ("折れ重なる魔法", "ウィアーディング", "世界の狭間"),
    },
}

C = "league_aurora_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the sfx toward Lux's 0.8 (the attack lower: it comes often), the voice as the
# other heroes'
SOUNDS = {f"league_aurora_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("q", 0.75), ("q_hit", 0.7), ("q_back", 0.7), ("q_back_hit", 0.7), ("p_spirit", 0.65),
    ("w", 0.75), ("e", 0.75), ("e_hit", 0.75), ("r", 0.85), ("r_land", 0.9), ("r_zone", 0.7), ("r_hit", 0.6),
    ("r_blink", 0.75), ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ratio", "p_hp", "p_heal", "p_heal_r", "w_ms", "q_dmg", "q_ratio", "q2_dmg",
                           "q2_ratio", "e_dmg", "e_ratio", "e_slow1", "r_dmg", "r_ratio", "r_slow1", "r_slow")}
    for k in ("w_inv", "w_cd", "q_hold", "r_t"):
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
    for lang, tx in TEXT.items():
        d = {"name": tx["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = tx[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), tx["names"])))
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
        bad |= any(m > TOOLTIP_MAX[lang] for m in lens.values())
        print(lang, " ".join(f"{k}:{m}/{TOOLTIP_MAX[lang]}" for k, m in lens.items()))
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
    if "Aurora" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Aurora. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
