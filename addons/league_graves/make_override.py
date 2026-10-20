"""Build the add-on's copy of Graves from the main pack (the shotgun's add-on rules).

    python addons/league_graves/make_override.py

Rebuilds Graves with tools/kit/build_graves.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_graves.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_graves/override/league_graves.data_champion and .../text/champion.i18n: the build with native - 
  * everything of the main pack's kit;
  * the shotgun's pellet and spread call league_graves:hit on every unit they hit (Quickdraw's cooldown, the knockback);
  * Collateral Damage's shell calls league_graves:cone on the champion it hits (the ring round him dropped);
  * passive league_graves:grit (params from P);
  * the attack's, E's and R's tooltips point to description.league_graves_addon.* with the add-on's wording, so the
    tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Graves changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_graves")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_graves as kit  # noqa: E402
import setup_graves as setup  # noqa: E402

TEXT_ID = "league_graves_addon"      # the text's key (the hero's own id is league_graves)
HERO = "league_graves"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, A, E = setup.O, setup.A, setup.E
# what the add-on adds after the main pack's text of each slot
MORE = {
    "attack": {
        "zh-hans": "被两颗弹丸打中的小兵、野怪会被击退。",
        "zh-hant": "被兩顆彈丸打中的小兵、野怪會被擊退。",
        "en": " Minions and monsters hit by two pellets are knocked back.",
        "ko": " 탄환 두 발에 맞은 미니언과 몬스터는 밀려남.",
        "ja": "弾丸2発を受けたミニオンとモンスターはノックバック。",
    },
    "skill2": {
        "zh-hans": "普攻每打中一下，冷却缩短" + A + "{e_cut}秒" + E + "（每次普攻最多{e_cuts}下）。",
        "zh-hant": "普攻每打中一下，冷卻縮短" + A + "{e_cut}秒" + E + "（每次普攻最多{e_cuts}下）。",
        "en": " Each shotgun hit cuts its cooldown by " + A + "{e_cut}s" + E + " (at most {e_cuts} an attack).",
        "ko": " 기본 공격 적중마다 재사용 대기시간 " + A + "{e_cut}초" + E + " 감소 (공격당 최대 {e_cuts}회).",
        "ja": "通常攻撃が当たるたびにクールダウン" + A + "{e_cut}秒" + E + "短縮（1回の攻撃で最大{e_cuts}回）。",
    },
    "ult": {
        "zh-hans": "（爆炸是那名英雄身后的锥形）",
        "zh-hant": "（爆炸是那名英雄身後的錐形）",
        "en": " (the explosion is a cone behind that champion)",
        "ko": " (폭발은 그 챔피언 뒤쪽 부채꼴)",
        "ja": "（爆発はそのチャンピオンの後方の扇形）",
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
        sys.exit("the main pack's league_graves differs from build_graves.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != "league_graves:grit":
        sys.exit("the copy does not call the add-on: update this script")
    for slot in MORE:
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    v = setup.values(p)
    v["e_cut"] = setup.secs(p["e_cut"])
    v["e_cuts"] = p["e_cuts"]
    texts = {}
    for lang in LEAD:
        d = {}
        for slot, more in MORE.items():
            d[slot] = ((LEAD[lang] if slot == "attack" else "") + setup.TEXT[lang][slot] + more[lang]).format(**v)
        texts[lang] = d
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
