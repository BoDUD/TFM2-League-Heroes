"""Build the add-on's copy of Azir from the main pack (the Sun Disc, the guards facing the charge).

    python addons/league_azir/make_override.py

Rebuilds Azir with tools/kit/build_azir.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_azir.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are the copy's numbers (its passive params: P's, its own stab and Q n_*), and writes
addons/league_azir/override/league_azir.data_champion and .../text/champion.i18n: the build with native=1 -
  * passive = league_azir:disc (params: d_life d_per d_range d_dmg d_ap d_near r_speed r_len r_stamps s_step): the Sun
    Disc on a fallen tower of his team's, once a game;
  * R's wall calls league_azir:r_wall with the ult's target instead of stamping right-facing guards itself (the add-on
    stamps them facing the way the wall runs); the wall's damage and knockback are the data's, unchanged;
  * the attack's tooltip (a key of the add-on's own id) adds the Sun Disc, so the tooltip in game shows whether the
    override took;
  * 0.1.7: view_projectiles for the line of sand from him to each soldier, `league_azir_tether_<px>` for px in
    TETHER_MIN..=TETHER_MAX step 2 (src/lib.rs), the add-on's own sheet effects/league_azir_tether
    (tools/art/fx_azir_tether.py) under the units (z -1): his passive spawns one a soldier every tick (0.2.0: each one
    flies two ticks, or the screen never drew it; lengths up to 80 px);
  * 0.2.0: the soldiers' stabs, Q's move and E's need of a soldier skip a soldier the add-on crumbled (`league_azir_x<s>`
    on him, taken off by the slot's next rise); the passive's params add s_life, s_tie (League's 660 less his body) and
    d_cd (the Sun Disc's 90-second cooldown, its sentence below);
  * 0.2.4: view_effects `league_azir_r_one_<a|b|la|lb>`, one guard alone (league/effects/league_azir_guard's
    one_<r|l>_<a|b>, tools/art/rig_azir.py): the add-on stands them in one line across the charge (the user 2026-11-11:
    「沙皇R的大招推起来像是有三排士兵」 - three stamps of three guards overlapped into three ranks);
  * 0.3.0 (the user, 2026-11-17: 「Q 沙兵真的冲过去」「沙兵刺击穿透一条线」): the copy's skill aims Q's move with
    league_azir:q_go / q_wave, its controller offers every enemy to league_azir:q_pick and calls league_azir:q_fly as the
    soldiers leave (the add-on draws them dashing, ss_dash views, their paths dealing Q); its stab and Q numbers are its
    own (P's n_*: the line stab and the dash make each hit lighter), so the attack text says the line stab with them and
    the add-on's text carries Q's text too.
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
    "zh-hans": "【附加包】" + n("太阳圆盘") + "：倒塔旁每" + t("{d_cd}秒") + "可立，" + t("{d_life}秒") + "内每" + t("{d_per}秒") +
               "打最近敌人" + mag("d_dmg", "d_ap") + "。",
    "zh-hant": "【附加包】" + n("太陽圓盤") + "：倒塔旁每" + t("{d_cd}秒") + "可立，" + t("{d_life}秒") + "內每" + t("{d_per}秒") +
               "打最近的敵人" + mag("d_dmg", "d_ap") + "。",
    "en": "[Add-on] " + n("Sun Disc") + ": every " + t("{d_cd}s") + " one can rise by a fallen tower, for " + t("{d_life}s") +
          " striking the nearest enemy every " + t("{d_per}s") + ": " + mag("d_dmg", "d_ap") + ".",
    "ko": "[확장] " + n("태양 원반") + ": " + t("{d_cd}초") + "마다 무너진 포탑 옆에 솟아 " + t("{d_life}초") + "간 " + t("{d_per}초") +
          "마다 가장 가까운 적에게 " + mag("d_dmg", "d_ap") + ".",
    "ja": "【拡張】" + n("太陽の円盤") + "：" + t("{d_cd}秒") + "毎にタワー跡に立ち" + t("{d_life}秒") + "間" + t("{d_per}秒") + "毎に最寄りの敵へ" +
          mag("d_dmg", "d_ap") + "。",
}
# 0.3.0 (the user, 2026-11-17: 「沙兵刺击穿透一条线」): lang -> (the main pack's stab clause, the copy's: the soldiers
# stab through a line); the disc sentence was shortened to fit (zh 倒下的塔旁…可立一次 -> 倒塔旁…可立, ja 倒れたタワー跡 -> タワー跡)
LINE = {
    "zh-hans": ("他附近的士兵代他刺击", "他附近的士兵代他刺穿一线"),
    "zh-hant": ("他附近的砂兵代他刺擊", "他附近的砂兵代他刺穿一線"),
    "en": ("the soldiers near him stab for him", "the soldiers near him stab through a line for him"),
    "ko": ("가까운 병사가 대신 찔러", "가까운 병사가 대신 일직선으로 꿰뚫어"),
    "ja": ("近くの砂兵が代わりに突き", "近くの砂兵が代わりに一直線に突き"),
}


# 0.3.0: lang -> (the main pack's Q clause on the landing's stab, the copy's: they stab at once only on a champion - Q -> stab
# as it was, its moves onto minions and monsters do not stab)
QLAND = {
    "zh-hans": ("落地马上刺击", "落到英雄身上马上刺击"),
    "zh-hant": ("落地立刻刺擊", "落到英雄身上立刻刺擊"),
    "en": ("they stab at once on arrival", "on a champion they stab at once"),
    "ko": ("도착하자마자 찌른다", "챔피언에게 도착하면 바로 찌른다"),
    "ja": ("着くとすぐ突く", "英雄に着くとすぐ突く"),
}


def skill_text(lang):
    """The copy's Q text: the main pack's, the landing's stab on a champion only."""
    old, new = QLAND[lang]
    main = setup.TEXT[lang]["skill"]
    if main.count(old) != 1:
        sys.exit(f"{lang}: the main pack's Q text has no `{old}`: update QLAND")
    return main.replace(old, new)


def attack_text(lang):
    """The copy's attack text: the main pack's with the line stab, then the Sun Disc's sentence."""
    old, new = LINE[lang]
    main = setup.TEXT[lang]["attack"]
    if main.count(old) != 1:
        sys.exit(f"{lang}: the main pack's attack text has no `{old}` to make the line stab of: update LINE")
    return main.replace(old, new) + DISC[lang]


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
    champion = kit.build(dict(p, native=1))
    # the add-on's numbers are the copy's passive params (0.3.0: its own stab and Q, n_*; the rest P's)
    params = champion.get("passive", {}).get("params", {})
    wrong = {k: (v, params.get(k, p.get(k))) for k, v in rust_defaults().items() if v != params.get(k, p.get(k))}
    if wrong:
        sys.exit("src/lib.rs Params defaults differ from the copy's params (build_azir.P; rust, copy): %s" % wrong)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":disc":
        sys.exit("the copy has no league_azir:disc passive: update this script")
    if '"league_azir:r_wall"' not in json.dumps(champion):
        sys.exit("the copy's wall does not call league_azir:r_wall: update this script")
    ones = [v for v in champion["view_effects"] if v["name"].startswith(HERO + "_r_one_")]
    with open(lp(os.path.join(ROOT, "league", "effects", "league_azir_guard#anim.fanim")), encoding="utf-8-sig") as f:
        guard_tags = json.load(f)["anims"]
    if len(ones) != 4 or any(v["tag"] not in guard_tags or "hd_" + v["tag"] not in guard_tags for v in ones):
        sys.exit("the copy's single guards (r_one_*) are not all in league/effects/league_azir_guard: "
                 "run tools/art/rig_azir.py --summons")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"
    tethers = tether_views()
    if {v["name"] for v in champion["view_projectiles"]} & {v["name"] for v in tethers}:
        sys.exit("the main pack's Azir already has the tether's view names: update this script")
    champion["view_projectiles"] = champion["view_projectiles"] + tethers

    # the copy's stab and Q numbers are its own (n_*, 0.3.0): its attack text and its Q text show them
    own = dict(p, s_dmg=p["n_s_dmg"], s_ap=p["n_s_ap"], q_dmg=p["n_q_dmg"], q_ap=p["n_q_ap"])
    values = dict(setup.values(own), d_life=setup.secs(p["d_life"]), d_per=setup.secs(p["d_per"]), d_cd=setup.secs(p["d_cd"]),
                  d_dmg=p["d_dmg"], d_ap=p["d_ap"])
    texts = {lang: {"attack": attack_text(lang).format(**values), "skill": skill_text(lang).format(**values)}
             for lang in DISC}
    long = {f"{lang}.{k}": setup.shown_length(f(lang)) for lang in DISC for k, f in (("attack", attack_text), ("skill", skill_text))
            if setup.shown_length(f(lang)) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.attack": f"{setup.shown_length(attack_text(lang))}/"
                              f"{setup.TOOLTIP_MAX[lang]}" for lang in DISC})


if __name__ == "__main__":
    main()
