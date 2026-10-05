"""Varus's text (5 languages), sound_info files and his keys in the shared files, numbers from build_varus.P.

    python tools/kit/setup_varus.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in vr/league): text/champion.i18n (league_varus in every language, description + skill_name),
sound/sfx/league_varus_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.60.0, Varus named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/vr/rst.py: 韦鲁斯 / 惩戒之箭, 复仇之欲, 穿刺之箭, 枯萎箭袋, 恶灵箭雨, 腐败锁链) and
Data Dragon 16.19.1 (zh_TW 法洛士 / 懲戒之箭 / 復仇怒火 / 破甲箭 / 荒蕪箭袋 / 腐敗箭雨 / 墮落連鎖, ko 바루스 / 죽지 않는 복수심 /
꿰뚫는 화살 / 역병 화살 / 퍼붓는 화살 / 부패의 사슬, ja ヴァルス / 復讐の化身 / 乾坤一擲 / 枯死の矢筒 / 滅びの矢雨 / 穢れの連鎖).
No `league_varus_attack` sound: the engine would play it at the start of every attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_varus import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_varus"
VERSION = "0.60.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
W_ = "<#ffffffff>"     # true damage
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -36}, "center": {"x": 0, "y": -12}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "韦鲁斯",
        "attack": "射箭攻击，附带" + M + "{w_on}魔法伤害" + E + "，命中英雄叠一层" + O + "枯萎" + E + "（最多3层）。被动" + O + "复仇之欲" + E +
                  "：击杀英雄后攻速+" + A + "{p_as_c}%" + E + "，击杀小兵野怪+" + A + "{p_as_m}%" + E + "，持续{p_t}秒。",
        "skill": "拉弓射出穿透箭：射程内有敌方英雄时蓄满力，造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E +
                 "，否则快速出手、伤害较低；之后每个敌人伤害递减。命中英雄时引爆枯萎：每层" + W_ + "{d_hp}%最大生命值" + E +
                 "真实伤害并缩短技能冷却。每{w_cd}秒一次蓄满的箭再加" + W_ + "{w_q_hp}%" + E + "。",
        "skill2": "向目标区域射下箭雨，造成" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "并引爆枯萎；地面腐化" + A + "{e_field_t}秒" + E +
                  "，其中的敌人" + R + "减速{e_slow}%" + E + "、受到的治疗降低{e_grievous}%。",
        "ult": "射出腐败锁链，命中第一个敌方英雄：" + phy("r_dmg", "r_ratio") + O + "物理伤害" + E + "、" + R + "禁锢{r_root}秒" + E +
               "、叠满3层枯萎；锁链随后扩散到附近的敌方英雄，" + R + "禁锢{r_root2}秒" + E + "。",
        "names": ("穿刺之箭", "恶灵箭雨", "腐败锁链"),
    },
    "zh-hant": {
        "name": "法洛士",
        "attack": "射箭攻擊，附帶" + M + "{w_on}魔法傷害" + E + "，命中英雄疊一層" + O + "荒蕪" + E + "（最多3層）。被動" + O + "復仇怒火" + E +
                  "：擊殺英雄後攻速+" + A + "{p_as_c}%" + E + "，擊殺小兵野怪+" + A + "{p_as_m}%" + E + "，持續{p_t}秒。",
        "skill": "拉弓射出穿透箭：射程內有敵方英雄時蓄滿力，造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E +
                 "，否則快速出手、傷害較低；之後每個敵人傷害遞減。命中英雄時引爆荒蕪：每層" + W_ + "{d_hp}%最大生命值" + E +
                 "真實傷害並縮短技能冷卻。每{w_cd}秒一次蓄滿的箭再加" + W_ + "{w_q_hp}%" + E + "。",
        "skill2": "向目標區域射下箭雨，造成" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "並引爆荒蕪；地面腐化" + A + "{e_field_t}秒" + E +
                  "，其中的敵人" + R + "緩速{e_slow}%" + E + "、受到的治療降低{e_grievous}%。",
        "ult": "射出墮落連鎖，命中第一個敵方英雄：" + phy("r_dmg", "r_ratio") + O + "物理傷害" + E + "、" + R + "定身{r_root}秒" + E +
               "、疊滿3層荒蕪；連鎖隨後擴散到附近的敵方英雄，" + R + "定身{r_root2}秒" + E + "。",
        "names": ("破甲箭", "腐敗箭雨", "墮落連鎖"),
    },
    "en": {
        "name": "Varus",
        "attack": "Shoots arrows dealing " + M + "{w_on} magic damage" + E + " on hit; each champion hit adds a stack of " + O +
                  "Blight" + E + " (up to 3). Passive " + O + "Living Vengeance" + E + ": a champion kill gives " + A +
                  "+{p_as_c}%" + E + " attack speed, a minion or monster kill " + A + "+{p_as_m}%" + E + ", for {p_t}s.",
        "skill": "Draws and fires a piercing arrow: fully charged with an enemy champion in reach for " + phy("q_dmg", "q_ratio") +
                 " " + O + "physical damage" + E + ", else a quick weaker shot; each further enemy takes less. A champion "
                 "hit bursts Blight: " + W_ + "{d_hp}% max health" + E + " true damage per stack and shorter cooldowns. "
                 "Every {w_cd}s a full draw adds " + W_ + "{w_q_hp}%" + E + ".",
        "skill2": "Rains arrows on an area: " + phy("e_dmg", "e_ratio") + " " + O + "physical damage" + E + ", bursting Blight. "
                  "The ground stays corrupted for " + A + "{e_field_t}s" + E + ": enemies in it are " + R + "slowed" + E +
                  " by {e_slow}% and healed {e_grievous}% less.",
        "ult": "Flings a tendril at the first enemy champion: " + phy("r_dmg", "r_ratio") + " " + O + "physical damage" + E +
               ", " + R + "rooted" + E + " for " + A + "{r_root}s" + E + ", full Blight. The corruption then spreads to enemy "
               "champions nearby, " + R + "rooting" + E + " them for " + A + "{r_root2}s" + E + ".",
        "names": ("Piercing Arrow", "Hail of Arrows", "Chain of Corruption"),
    },
    "ko": {
        "name": "바루스",
        "attack": "화살로 공격해 " + M + "{w_on}의 마법 피해" + E + "를 추가로 입히고, 챔피언에게 " + O + "역병" + E + " 중첩을 쌓습니다(최대 3). "
                  "기본 지속 효과 " + O + "죽지 않는 복수심" + E + ": 챔피언 처치 시 공격 속도 " + A + "+{p_as_c}%" + E + ", 미니언·몬스터 처치 시 " +
                  A + "+{p_as_m}%" + E + " ({p_t}초).",
        "skill": "꿰뚫는 화살을 쏩니다. 사거리 안에 적 챔피언이 있으면 끝까지 당겨 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E +
                 ", 없으면 빠르게 약하게 쏩니다. 뒤의 적일수록 피해가 줄어듭니다. 챔피언 적중 시 역병이 터져 중첩당 " + W_ +
                 "최대 체력의 {d_hp}%" + E + " 고정 피해, 스킬 재사용 대기시간 감소. {w_cd}초마다 완충 화살은 " + W_ + "{w_q_hp}%" + E + " 추가.",
        "skill2": "지역에 화살비를 퍼부어 " + phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" + E + "를 입히고 역병을 터뜨립니다. 땅이 " + A +
                  "{e_field_t}초" + E + " 오염되어 적이 {e_slow}% " + R + "둔화" + E + "되고 받는 회복이 {e_grievous}% 줄어듭니다.",
        "ult": "첫 적 챔피언에게 덩굴을 던져 " + phy("r_dmg", "r_ratio") + "의 " + O + "물리 피해" + E + ", " + A + "{r_root}초" + E + " " + R +
               "속박" + E + ", 역병 3중첩. 이어서 부패가 주변 적 챔피언에게 퍼져 " + A + "{r_root2}초" + E + " " + R + "속박" + E + "합니다.",
        "names": ("꿰뚫는 화살", "퍼붓는 화살", "부패의 사슬"),
    },
    "ja": {
        "name": "ヴァルス",
        "attack": "矢で攻撃し" + M + "{w_on}の魔法ダメージ" + E + "を追加、チャンピオンに" + O + "枯死" + E + "を付与（最大3）。パッシブ " + O +
                  "復讐の化身" + E + "：チャンピオンを倒すと攻撃速度" + A + "+{p_as_c}%" + E + "、ミニオン・モンスターで" + A + "+{p_as_m}%" + E +
                  "（{p_t}秒）。",
        "skill": "貫通する矢を放つ。射程内に敵チャンピオンがいれば引き絞り" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E +
                 "、いなければ素早く弱く撃つ。後ろの敵ほど減衰。チャンピオンに当たると枯死が弾け、1つにつき" + W_ + "最大体力の{d_hp}%" + E +
                 "の確定ダメージとスキル短縮。{w_cd}秒ごとに引き絞った矢は" + W_ + "{w_q_hp}%" + E + "追加。",
        "skill2": "範囲に矢の雨を降らせ" + phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "、枯死を弾けさせる。地面が" + A +
                  "{e_field_t}秒" + E + "穢れ、中の敵に{e_slow}%の" + R + "スロウ" + E + "と回復{e_grievous}%低下。",
        "ult": "最初の敵チャンピオンに蔓を放ち" + phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "、" + A + "{r_root}秒" + E + "の" + R +
               "スネア" + E + "、枯死3つ。続いて穢れが周囲の敵チャンピオンに広がり" + A + "{r_root2}秒" + E + R + "スネア" + E + "。",
        "names": ("乾坤一擲", "滅びの矢雨", "穢れの連鎖"),
    },
}

C = "league_varus_sfx_"
V = "league_varus_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_varus_a_shot": [(C + "attack", 0.5, 0.0), (C + "attack_fly", 0.35, 0.03)],
    "league_varus_a_hit": [(C + "attack_hit", 0.35, 0.0)],
    "league_varus_b_pop": [(C + "blight", 0.5, 0.0)],
    "league_varus_w_pop": [(C + "w_pop", 0.6, 0.0)],
    "league_varus_q_charge": [(C + "q", 0.55, 0.0), (C + "q_charge", 0.4, 0.1), (V + "q", 0.85, 0.05)],
    "league_varus_q_fire": [(C + "q_fire", 0.6, 0.0), (C + "q_fly", 0.35, 0.03)],
    "league_varus_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_varus_e_cast": [(C + "e", 0.55, 0.0), (V + "e", 0.85, 0.05)],
    "league_varus_e_land": [(C + "e_land", 0.55, 0.0)],
    "league_varus_e_hit": [(C + "e_hit", 0.35, 0.0)],
    "league_varus_r_cast": [(C + "r", 0.6, 0.0), (C + "r_fly", 0.4, 0.15), (V + "r", 0.9, 0.05)],
    "league_varus_r_hit": [(C + "r_hit", 0.6, 0.0)],
    "league_varus_r_spread": [(C + "r_spread", 0.5, 0.0)],
    "league_varus_p_rage": [(C + "rage", 0.6, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("w_on", "d_hp", "w_q_hp", "p_as_c", "p_as_m", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "e_slow",
                           "e_grievous", "r_dmg", "r_ratio")}
    v.update({k: secs(p[k]) for k in ("p_t", "w_cd", "e_field_t", "r_root", "r_root2")})
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
    if "Varus" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Varus. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
