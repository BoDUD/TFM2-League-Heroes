"""Build the add-on's copy of Gangplank from the main pack (Remove Scurvy cleanses and is eaten at low health, kegs chain,
Silver Serpents).

    python addons/league_gangplank/make_override.py

Rebuilds Gangplank with tools/kit/build_gangplank.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_gangplank.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_gangplank/override/league_gangplank.data_champion and .../text/champion.i18n: the build with
native=1 -
  * passive league_gangplank:scurvy (params: w_low, e_chain, e_r, e_link, p_ms, p_ms_t, the e_* of the third keg and
    the sv_* of the Silver Serpents);
  * the orange raises `league_gangplank_w_now` and the watch also eats it on `league_gangplank_w_low`; a keg that blew
    raises `league_gangplank_k<s>_now`, and a keg's chain reads `league_gangplank_k<s>_cn` (the add-on's, with a
    distance) in place of the other keg's blast;
  * the Silver Serpents (0.3.0): a Parrrley kill raises `league_gangplank_q_kill`; Cannon Barrage reads the upgrades the
    add-on bought (`league_gangplank_up_dd` / `up_faw` / `up_rm`) and marks the champions it lands on; the skill bar's
    stack box shows his serpents (tools/kit/stack_nums.py, this copy only);
  * the attack's, Parrrley's, Powder Keg's and Cannon Barrage's tooltips point to description.league_gangplank_addon.*
    with the add-on's wording, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Gangplank changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_gangplank")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_gangplank as kit  # noqa: E402
import setup_gangplank as setup  # noqa: E402

TEXT_ID = "league_gangplank_addon"       # the texts' key (the hero's own id is league_gangplank)
HERO = "league_gangplank"
A = setup.A                              # counts in the tooltips
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
# the main pack's wording -> the add-on's (every phrase must be in the main text)
SWAP = {
    "zh-hans": {
        "attack": [("：3级起被控制或被围攻时吃橘子，回复", "：3级起被控、被围或生命低于{w_low}%时吃橘子解控，回")],
        "skill": [("都会被引爆。", "都会被引爆。击杀掠夺" + A + "{sv_lo}-{sv_hi}<>银蛇币（随时间增加）和{g_lo}-{g_hi}金币，"
                   "回泉水时每" + A + "{sv_cost}<>枚按局势升级大招。")],
        "skill2": [("扔火药桶（最多", "扔火药桶（可存"),
                   ("后引线点燃。", "后点燃；开枪时给相连桶外的敌人补第三桶。"),
                   ("或另一个桶的爆炸引爆", "或相连的桶爆炸引爆")],
        "ult": [("被控制的敌方英雄。", "被控制的敌方英雄。银蛇币升级：大炮弹（一波的" + A + "{r_dd_pct}%<>真实伤害）、"
                 + A + "{r_faw}波<>、炮幕内队友加速{r_rm_ms}%。")],
    },
    "zh-hant": {
        "attack": [("：3級起被控制或被圍攻時吃橘子，回復", "：3級起被控、被圍或生命低於{w_low}%時吃橘子解控，回")],
        "skill": [("都會被引爆。", "都會被引爆。擊殺掠奪" + A + "{sv_lo}-{sv_hi}<>銀蛇幣（隨時間增加）和{g_lo}-{g_hi}金幣，"
                   "回泉水時每" + A + "{sv_cost}<>枚按局勢升級大招。")],
        "skill2": [("扔火藥桶（最多", "扔火藥桶（可存"),
                   ("後引線點燃。", "後點燃；開槍時給相連桶外的敵人補第三桶。"),
                   ("或另一個桶的爆炸引爆", "或相連的桶爆炸引爆")],
        "ult": [("被控制的敵方英雄。", "被控制的敵方英雄。銀蛇幣升級：大砲彈（一波的" + A + "{r_dd_pct}%<>真實傷害）、"
                 + A + "{r_faw}波<>、砲幕內隊友加速{r_rm_ms}%。")],
    },
    "en": {
        "attack": [("sets the target ablaze for", "burns the target for"),
                   ("a Powder Keg blowing up resets it", "a keg blast resets it"),
                   ("when crowd-controlled or crowded he eats an orange: heals",
                    "when controlled, crowded or below {w_low}% health he eats an orange: cleanses, heals"),
                   (" and is " + setup.R + "immune to crowd control" + setup.E, " and is " + setup.R + "CC-immune" + setup.E)],
        "skill": [(" blows up.", " blows up. A kill plunders " + A + "{sv_lo}-{sv_hi}<> Silver Serpents (rising over time) and "
                   "{g_lo}-{g_hi} gold; at his fountain each " + A + "{sv_cost}<> buy the ult upgrade the match calls for.")],
        "skill2": [("(up to ", "(holds "), ("; its fuse is lit after", ", lit after"),
                   (". A lit keg blows up on Parrrley,", ". Parrrley throws a third keg at a foe past two linked ones. "
                    "A lit keg blows up on Parrrley,"),
                   ("or the other keg's blast", "or a linked keg's blast")],
        "ult": [("crowd control first.", "crowd control first. Upgrades: a mega-cannonball (" + A + "{r_dd_pct}%<> of a wave as true "
                 "damage), " + A + "{r_faw} waves<>, allies in it {r_rm_ms}% faster.")],
    },
    "ko": {
        "attack": [("군중 제어나 포위 시 오렌지를 먹어", "군중 제어, 포위, 체력 {w_low}% 미만 시 오렌지로 정화,")],
        "skill": [("모두 폭발.", "모두 폭발. 처치 시 은뱀 주화 " + A + "{sv_lo}-{sv_hi}<>개(시간에 따라 증가)와 골드 {g_lo}-{g_hi} 약탈, "
                   "우물에서 " + A + "{sv_cost}<>개마다 상황에 맞춰 궁극기 강화.")],
        "skill2": [("(최대 ", "(충전 "), (" 후 심지 점화. ", " 후 점화. 혀어어어업상 때 연결된 통 밖의 적에게 셋째 통(삼연통). "),
                   ("다른 통의 폭발로", "연결된 통의 폭발로")],
        "ult": [("군중 제어된 적 우선.", "군중 제어된 적 우선. 은뱀 주화 강화: 거대 포탄(한 번의 " + A + "{r_dd_pct}%<> 고정 피해), "
                 + A + "{r_faw}번<>, 안의 아군 이동 속도 {r_rm_ms}% 증가.")],
    },
    "ja": {
        "attack": [("、自身{p_ms}%加速、火薬樽の爆発で再使用可能", "、{p_ms}%加速、樽の爆発で再使用可"),
                   ("行動妨害や包囲時にオレンジを食べ", "妨害・包囲・体力{w_low}%未満でオレンジを食べ解除、")],
        "skill": [("すべて爆発。", "すべて爆発。倒すとシルバーサーペント" + A + "{sv_lo}-{sv_hi}<>枚（時間で増加）と{g_lo}-{g_hi}ゴールドを"
                   "奪い、泉で" + A + "{sv_cost}<>枚ごとに戦況でRを強化。")],
        "skill2": [("（最大", "（ストック"), ("後に点火。", "後に点火、発砲時は連結樽の外の敵へ3個目。"),
                   ("別の樽の爆発で", "連結した樽の爆発で")],
        "ult": [("行動妨害中の敵を優先。", "行動妨害中の敵を優先。強化：巨大砲弾（1波の" + A + "{r_dd_pct}%<>を確定ダメージ）、"
                 + A + "{r_faw}波<>、範囲内の味方{r_rm_ms}%加速。")],
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_gangplank differs from build_gangplank.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if champion.get("passive", {}).get("passive_ref") != "league_gangplank:scurvy" or \
            not all(f"league_gangplank_{f}" in text for f in ("w_now", "w_low", "k1_now", "k2_cn", "q_kill", "r_land",
                                                               "up_dd", "up_faw", "up_rm")):
        sys.exit("the copy does not call the add-on: update this script")
    for k in SWAP["en"]:
        champion[k]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{k}"

    raw = {}
    for lang, swaps in SWAP.items():
        raw[lang] = {}
        for k, pairs in swaps.items():
            t = setup.TEXT[lang][k]
            for old, new in pairs:
                if old not in t:
                    sys.exit(f"{lang}.{k}: {old!r} is not in the main pack's text")
                t = t.replace(old, new, 1)
            raw[lang][k] = LEAD[lang] + t
    # the Silver Serpents: a kill's serpents and gold at Parrrley's ranks 1 and 5 (the add-on's plunder / plunder_gold)
    serpents = {"sv_lo": ((3 + 1) * p["sv_scale"] + 50) // 100, "sv_hi": ((3 + 5) * p["sv_scale"] + 50) // 100,
                "g_lo": ((2 + 1) * p["sv_gold"] + 50) // 100, "g_hi": ((2 + 5) * p["sv_gold"] + 50) // 100}
    values = dict(setup.values(p), w_low=p["w_low"], sv_cost=p["sv_cost"], r_faw=p["r_faw"], r_dd_pct=p["r_dd_pct"],
                  r_rm_ms=p["r_rm_ms"], **serpents)
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in raw.items()}
    lens = {f"{lang}.{k}": (setup.shown_length(t), setup.TOOLTIP_MAX[lang]) for lang, d in raw.items() for k, t in d.items()}
    for key, (n, cap) in lens.items():
        print(f"{key}: {n}/{cap}")
    long = {k: v for k, v in lens.items() if v[0] > v[1]}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(champion))
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(tpath)), exist_ok=True)
    with open(lp(tpath), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(i18n))
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
