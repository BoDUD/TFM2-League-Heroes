"""Build the add-on's copy of Kassadin from the main pack (Void Stone exact, Force Pulse charge, Riftwalk landing).

    python addons/league_kassadin/make_override.py

Rebuilds Kassadin with tools/kit/build_kassadin.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_kassadin.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_kassadin/override/league_kassadin.data_champion and .../text/champion.i18n: the build with
native=1 -
  * everything of the main pack's kit, minus the data's resistance buff and the own-cast E refunds;
  * passive league_kassadin:void_stone (params: E's and Q's cooldowns, the cut a cast, the reach, the reduction);
  * R calls league_kassadin:rift instead of blinking to a random champion in reach;
  * the attack's, E's and R's tooltips point to description.league_kassadin_void.* with the add-on's wording, so the
    tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Kassadin changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_kassadin")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_kassadin as kit  # noqa: E402
import setup_kassadin as setup  # noqa: E402

TEXT_ID = "league_kassadin_void"        # the text's key (the hero's own id is league_kassadin)
HERO = "league_kassadin"
# lang -> slot -> (old text the main pack has, new text) ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
SWAP = {
    "zh-hans": {"attack": ("降低约10%", "正好降低10%"),
                "skill2": ("每次施放虚无法球或虚空行走都会缩短它的冷却", "附近每有英雄施放技能（敌我都算）就缩短它的冷却"),
                "ult": ("闪现到附近一名敌方英雄身边", "闪现到能击杀、或身边英雄最多的敌方后排身边（不进敌方塔下）；附近没有敌方英雄时也对小兵放，闪进兵堆清兵")},
    "zh-hant": {"attack": ("降低約10%", "正好降低10%"),
                "skill2": ("每次施放虛無法球或虛空行走都會縮短它的冷卻", "附近每有英雄施放技能（敵我都算）就縮短它的冷卻"),
                "ult": ("閃現到附近一名敵方英雄身邊", "閃現到能擊殺、或身邊英雄最多的敵方後排身邊（不進敵方塔下）；附近沒有敵方英雄時也對小兵放，閃進兵堆清兵")},
    "en": {"attack": ("about 10% less", "exactly 10% less"),
           "skill2": ("Each Null Sphere or Riftwalk he casts shortens its cooldown", "Every spell any champion casts near him shortens its cooldown"),
           "ult": ("Blinks next to a nearby enemy champion", "Blinks next to the enemy he can kill, else the back liner with most champions round it (never under a tower); with no enemy champion near, into a minion wave to clear it")},
    "ko": {"attack": ("약 10% 감소", "정확히 10% 감소"),
           "skill2": ("무의 구체나 균열 이동을 쓸 때마다 재사용 대기시간 감소", "근처에서 챔피언이 스킬을 쓸 때마다(아군·적 모두) 재사용 대기시간 감소"),
           "ult": ("근처 적 챔피언 옆으로 순간이동해", "처치할 수 있는 적, 없으면 주변 챔피언이 가장 많은 적 후열 옆으로 순간이동해(포탑 아래 제외; 근처에 적 챔피언이 없으면 미니언 무리 속으로)")},
    "ja": {"attack": ("約10%軽減", "ちょうど10%軽減"),
           "skill2": ("ヴォイドスフィアかリフトウォークを使うたびCD短縮", "近くで誰かがスキルを使うたび（敵味方とも）CD短縮"),
           "ult": ("近くの敵チャンピオンの傍へ瞬間移動し", "倒せる敵、いなければ周りの敵が最も多い後衛の傍へ瞬間移動し（塔下は除く；近くに敵チャンピオンがいなければミニオンの群れへ）")},
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
        sys.exit("the main pack's league_kassadin differs from build_kassadin.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if "league_kassadin:rift" not in json.dumps(champion["ult"]) or "passive" not in champion:
        sys.exit("the copy does not call the add-on: update this script")
    for slot in ("attack", "skill2", "ult"):
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = setup.values(p)
    texts = {}
    for lang, swaps in SWAP.items():
        texts[lang] = {}
        for slot, (old, new) in swaps.items():
            src = setup.TEXT[lang][slot]
            if old not in src:
                sys.exit(f"{lang}.{slot}: {old!r} is not in setup_kassadin.TEXT")
            texts[lang][slot] = (LEAD[lang] + src.replace(old, new)).format(**values)
    long = {f"{lang}.{slot}": setup.shown_length(t) for lang, d in texts.items() for slot, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
