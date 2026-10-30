"""Build the add-on's copy of Azir from the main pack (the Sun Disc, the guards facing the charge).

    python addons/league_azir/make_override.py

Rebuilds Azir with tools/kit/build_azir.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_azir.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_azir/override/league_azir.data_champion and
.../text/champion.i18n: the build with native=1 -
  * passive = league_azir:disc (params: d_life d_per d_range d_dmg d_ap d_near r_speed r_len r_stamps s_step): the Sun
    Disc on a fallen tower of his team's, once a game;
  * R's wall calls league_azir:r_wall with the ult's target instead of stamping right-facing guards itself (the add-on
    stamps them facing the way the wall runs); the wall's damage and knockback are the data's, unchanged;
  * the attack's tooltip (a key of the add-on's own id) adds the Sun Disc, so the tooltip in game shows whether the
    override took;
  * 0.1.7: view_projectiles for the line of sand from him to each soldier, `league_azir_tether_<px>` for px in
    TETHER_MIN..=TETHER_MAX step 2 (src/lib.rs), the add-on's own sheet effects/league_azir_tether
    (tools/art/fx_azir_tether.py) under the units (z -1): his passive spawns one a soldier every tick.
Every other champion stays untouched. Run it again whenever the main pack's Azir changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_azir")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_azir as kit  # noqa: E402
import setup_azir as setup  # noqa: E402

MOD_ID = "league_azir"
HERO = "league_azir"
TETHER = "league_azir_tether"   # the add-on's own sheet: the line of sand to the soldiers (tools/art/fx_azir_tether.py)
mag, t, n = setup.mag, setup.t, setup.n
# lang -> the add-on's sentence after the main pack's attack text
DISC = {
    "zh-hans": "【附加包】" + n("太阳圆盘") + "：每局一次在倒下的我方塔旁立起，" + t("{d_life}秒") + "内每" + t("{d_per}秒") + "打最近敌人" +
               mag("d_dmg", "d_ap") + "。",
    "zh-hant": "【附加包】" + n("太陽圓盤") + "：每局一次在倒下的我方塔旁立起，" + t("{d_life}秒") + "內每" + t("{d_per}秒") + "打最近的敵人" +
               mag("d_dmg", "d_ap") + "。",
    "en": "[Add-on] " + n("Sun Disc") + ": once a game it rises by a fallen tower of his, for " + t("{d_life}s") +
          " striking the nearest enemy every " + t("{d_per}s") + ": " + mag("d_dmg", "d_ap") + ".",
    "ko": "[확장] " + n("태양 원반") + ": 게임당 한 번 무너진 아군 포탑 옆에 솟아 " + t("{d_life}초") + "간 " + t("{d_per}초") +
          "마다 가장 가까운 적에게 " + mag("d_dmg", "d_ap") + ".",
    "ja": "【拡張】" + n("太陽の円盤") + "：1試合1回倒れた味方タワー跡に立ち" + t("{d_life}秒") + "間" + t("{d_per}秒") + "毎に最寄りの敵へ" +
          mag("d_dmg", "d_ap") + "。",
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_defaults():
    """Params::default() in src/lib.rs as {field: value}."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    return {k.strip(): int(v.strip().rstrip(",")) for k, v in re.findall(r"(\w+): (\d+),?", m.group(1))}


def tether_views():
    """The line's pieces as projectile views (one length a tag), checked against the sheet."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    lo, hi = (int(re.search(r"pub const " + k + r": usize = (\d+);", src).group(1)) for k in ("TETHER_MIN", "TETHER_MAX"))
    with open(lp(os.path.join(ADDON, "effects", TETHER + "#anim.fanim")), encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    want = [f"tether_{k}" for k in range(lo, hi + 1, 2)]
    missing = [t for t in want if t not in anims]
    if missing:
        sys.exit(f"effects/{TETHER} lacks {missing}: run tools/art/fx_azir_tether.py")
    # under the units (z -1): his body and the soldiers' cover the line's ends
    return [{"type": "Animated", "name": f"{HERO}_{t}", "anim": f"asset/{MOD_ID}/effects/{TETHER}", "tag": t,
             "repeat": True, "z": -1} for t in want]


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_azir differs from build_azir.P: rebuild it first")
    wrong = {k: (v, p[k]) for k, v in rust_defaults().items() if v != p[k]}
    if wrong:
        sys.exit("src/lib.rs Params defaults differ from build_azir.P (rust, P): %s" % wrong)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":disc":
        sys.exit("the copy has no league_azir:disc passive: update this script")
    if '"league_azir:r_wall"' not in json.dumps(champion):
        sys.exit("the copy's wall does not call league_azir:r_wall: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"
    tethers = tether_views()
    if {v["name"] for v in champion["view_projectiles"]} & {v["name"] for v in tethers}:
        sys.exit("the main pack's Azir already has the tether's view names: update this script")
    champion["view_projectiles"] = champion["view_projectiles"] + tethers

    values = dict(setup.values(p), d_life=setup.secs(p["d_life"]), d_per=setup.secs(p["d_per"]), d_dmg=p["d_dmg"],
                  d_ap=p["d_ap"])
    texts = {lang: {"attack": (setup.TEXT[lang]["attack"] + DISC[lang]).format(**values)} for lang in DISC}
    long = {f"{lang}.attack": setup.shown_length(setup.TEXT[lang]["attack"] + DISC[lang]) for lang in DISC
            if setup.shown_length(setup.TEXT[lang]["attack"] + DISC[lang]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.attack": f"{setup.shown_length(setup.TEXT[lang]['attack'] + DISC[lang])}/"
                              f"{setup.TOOLTIP_MAX[lang]}" for lang in DISC})


if __name__ == "__main__":
    main()
