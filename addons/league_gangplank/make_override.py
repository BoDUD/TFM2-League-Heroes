"""Build the add-on's copy of Gangplank from the main pack (Remove Scurvy cleanses and is eaten at low health, kegs chain).

    python addons/league_gangplank/make_override.py

Rebuilds Gangplank with tools/kit/build_gangplank.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_gangplank.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_gangplank/override/league_gangplank.data_champion and .../text/champion.i18n: the build with
native=1 -
  * passive league_gangplank:scurvy (params: w_low, e_chain, e_r, e_link, p_ms, p_ms_t);
  * the orange raises `league_gangplank_w_now` and the watch also eats it on `league_gangplank_w_low`; a keg that blew
    raises `league_gangplank_k<s>_now`, and a keg's chain reads `league_gangplank_k<s>_cn` (the add-on's, with a
    distance) in place of the other keg's blast;
  * the attack's and Powder Keg's tooltips point to description.league_gangplank_addon.* with the add-on's wording, so
    the tooltip in game shows whether the override took.
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
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
# the main pack's wording -> the add-on's (every phrase must be in the main text)
SWAP = {
    "zh-hans": {
        "attack": [("：3级起被控制或被围攻时吃橘子，回复", "：3级起被控、被围或生命低于{w_low}%时吃橘子解控，回")],
        "skill2": [("扔火药桶（最多", "扔火药桶（可存"),
                   ("后引线点燃。", "后点燃；开枪时给相连桶外的敌人补第三桶。"),
                   ("或另一个桶的爆炸引爆", "或相连的桶爆炸引爆")],
    },
    "zh-hant": {
        "attack": [("：3級起被控制或被圍攻時吃橘子，回復", "：3級起被控、被圍或生命低於{w_low}%時吃橘子解控，回")],
        "skill2": [("扔火藥桶（最多", "扔火藥桶（可存"),
                   ("後引線點燃。", "後點燃；開槍時給相連桶外的敵人補第三桶。"),
                   ("或另一個桶的爆炸引爆", "或相連的桶爆炸引爆")],
    },
    "en": {
        "attack": [("sets the target ablaze for", "burns the target for"),
                   ("a Powder Keg blowing up resets it", "a keg blast resets it"),
                   ("when crowd-controlled or crowded he eats an orange: heals",
                    "when controlled, crowded or below {w_low}% health he eats an orange: cleanses, heals"),
                   (" and is " + setup.R + "immune to crowd control" + setup.E, " and is " + setup.R + "CC-immune" + setup.E)],
        "skill2": [("(up to ", "(holds "), ("; its fuse is lit after", ", lit after"),
                   (". A lit keg blows up on Parrrley,", ". Parrrley throws a third keg at a foe past two linked ones. "
                    "A lit keg blows up on Parrrley,"),
                   ("or the other keg's blast", "or a linked keg's blast")],
    },
    "ko": {
        "attack": [("군중 제어나 포위 시 오렌지를 먹어", "군중 제어, 포위, 체력 {w_low}% 미만 시 오렌지로 정화,")],
        "skill2": [("(최대 ", "(충전 "), (" 후 심지 점화. ", " 후 점화. 혀어어어업상 때 연결된 통 밖의 적에게 셋째 통(삼연통). "),
                   ("다른 통의 폭발로", "연결된 통의 폭발로")],
    },
    "ja": {
        "attack": [("、自身{p_ms}%加速、火薬樽の爆発で再使用可能", "、{p_ms}%加速、樽の爆発で再使用可"),
                   ("行動妨害や包囲時にオレンジを食べ", "妨害・包囲・体力{w_low}%未満でオレンジを食べ解除、")],
        "skill2": [("（最大", "（ストック"), ("後に点火。", "後に点火、発砲時は連結樽の外の敵へ3個目。"),
                   ("別の樽の爆発で", "連結した樽の爆発で")],
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
            not all(f"league_gangplank_{f}" in text for f in ("w_now", "w_low", "k1_now", "k2_cn")):
        sys.exit("the copy does not call the add-on: update this script")
    for k in ("attack", "skill2"):
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
    values = dict(setup.values(p), w_low=p["w_low"])
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
