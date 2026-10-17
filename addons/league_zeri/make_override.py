"""Build the add-on's copy of Zeri from the main pack (Ultrashock Laser off walls, Living Battery steals shields).

    python addons/league_zeri/make_override.py

Rebuilds Zeri with tools/kit/build_zeri.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_zeri.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_zeri/override/league_zeri.data_champion and .../text/champion.i18n: build(p, native=True) -
  * W's pulse lays league_zeri_w_go on her while it flies and hits nothing once league_zeri_w_wall is on her (the
    passive turned it into a laser at a wall);
  * the charged shot gives no shield of its own (the steal replaces it);
  * passive = league_zeri:battery with steal, steal_t and W's numbers as its params;
  * the attack's and W's tooltips (merged over the main text) name the shield steal and the wall.
Every other champion stays untouched. Run it again whenever the main pack's Zeri or her text changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_zeri")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_zeri as kit  # noqa: E402
import setup_zeri as setup  # noqa: E402

MOD_ID = "league_zeri"
HERO = "league_zeri"
# lang -> slot -> (the main text's words, the add-on's); {steal} = P["p_steal"]
SWAP = {
    "zh-hans": {"attack": ("，自己获得护盾和移速。", "，自己获得移速；伤害打到敌人护盾时偷取{steal}%变成自己的护盾。"),
                "skill": ("先打中小兵或野怪时", "先打中小兵、野怪或撞到墙时")},
    "zh-hant": {"attack": ("，自己獲得護盾和移速。", "，自己獲得移速；傷害打到敵人護盾時偷取{steal}%變成自己的護盾。"),
                "skill": ("先打中小兵或野怪時", "先打中小兵、野怪或撞到牆時")},
    "en": {"attack": (", and she gains a shield and Move Speed.",
                      ", and she gains Move Speed. Damaging an enemy shield steals {steal}% of it as her own shield."),
           "skill": ("If a minion or monster stops it,", "If a minion, a monster or a wall stops it,")},
    "ko": {"attack": (", 자신은 보호막과 이동 속도.", ", 자신은 이동 속도. 적 보호막에 피해를 주면 {steal}%를 훔쳐 자신의 보호막으로."),
           "skill": ("미니언이나 몬스터에 막히면", "미니언·몬스터·벽에 막히면")},
    "ja": {"attack": ("、自身にシールドと移動速度。", "、自身に移動速度。敵シールドへのダメージの{steal}%を奪い自分のシールドに。"),
           "skill": ("ミニオンかモンスターに当たると", "ミニオン、モンスター、壁に当たると")},
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_zeri differs from build_zeri.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":battery":
        sys.exit("the copy has no league_zeri:battery passive: update build_zeri.py")
    flat = json.dumps(champion)
    for name in ("league_zeri_w_go", "league_zeri_w_wall", "league_zeri_w_pulse", "league_zeri_p_shv",
                 "league_zeri_w_slow", "league_zeri_w_hit", "league_zeri_w_beam"):
        if name not in flat:
            sys.exit(f"{name} is no longer in the copy: update src/lib.rs")
    if '"type": "Shield"' in flat:
        sys.exit("the copy still gives the charged shot's shield: the steal replaces it")

    texts = {}
    main_texts = setup.texts(p)
    for lang, swaps in SWAP.items():
        d, _ = main_texts[lang]
        texts[lang] = {}
        for slot, (old, new) in swaps.items():
            if d[slot].count(old) != 1:
                sys.exit(f"{lang} {slot}: the main pack's text changed ({old!r} not found once): update SWAP")
            texts[lang][slot] = d[slot].replace(old, new.format(steal=p["p_steal"]))
    long = {(lang, slot): setup.shown_length(t) for lang, ts in texts.items() for slot, t in ts.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {HERO: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], champion["passive"]["params"])
    print("tooltip lengths", {f"{lang}.{slot}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, ts in texts.items() for slot, t in ts.items()})


if __name__ == "__main__":
    main()
