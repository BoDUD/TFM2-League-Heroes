"""Build the add-on's copy of Heimerdinger from the main pack (turrets firing visible shots, the affinity by towers too).

    python addons/league_heimerdinger/make_override.py

Rebuilds Heimerdinger with tools/kit/build_heimerdinger.py (its parameter table P), checks that the plain build is the
main pack's league/champion/league_heimerdinger.data_champion byte for byte (so the copy never drifts from the shipped
kit), that src/lib.rs's default Params are P's numbers and its T_MUZZLE / X_MUZZLE the side turrets' muzzles
(assets/source/heimerdinger/hd/side_muzzles.json, written by tools/art/import_heimerdinger_fx.py), and writes
addons/league_heimerdinger/override/league_heimerdinger.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the bolt and W's rockets, E's grenade, R by the situation, the combos);
  * the turrets keep their sounds and three slots but no zones: Q's put and R's apex run the add-on's
    league_heimerdinger:q / :x, which stand its native turrets and say which side they face (t_face_l / x_face_l):
    the turrets are drawn from the side (league_heimerdinger_turret_r / _l, _apex_r / _l);
  * passive = the add-on's league_heimerdinger:affinity with the numbers of P it uses (passive.params);
  * the shots' views (t_shot, t_beam_line, x_shot: drawn in league_heimerdinger_fx, unbound in the main pack);
  * the skill's tooltip points to description.league_heimerdinger.skill with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Heimerdinger changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_heimerdinger")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_heimerdinger as kit  # noqa: E402
import setup_heimerdinger as setup  # noqa: E402

MOD_ID = "league_heimerdinger"
HERO = "league_heimerdinger"
SLOTS = ("skill",)
# the main pack's tooltip with the add-on's prefix and the towers in the affinity (each pair must match once)
PREFIX = {"zh-hans": "【扩展包】", "zh-hant": "【擴充包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
SWAP = {
    "zh-hans": [("攻击一个敌人", "射击一个敌人"), ("在炮台旁移速", "在炮台或己方防御塔旁移速")],
    "zh-hant": [("攻擊一個敵人", "射擊一個敵人"), ("在砲臺旁跑速", "在砲臺或己方防禦塔旁跑速")],
    "en": [("strikes one enemy", "shoots one enemy"), ("near his turrets.", "near his turrets or his side's towers.")],
    "ko": [("포탑 근처에서", "포탑이나 아군 타워 근처에서")],
    "ja": [("砲台の近くで", "砲台か味方タワーの近くで")],
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_defaults():
    """src/lib.rs's `impl Default for Params` numbers."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    body = src.split("impl Default for Params", 1)[1].split("\n    }\n}", 1)[0]
    return {m.group(1): int(m.group(2).replace("_", "")) for m in re.finditer(r"(\w+): ([0-9_]+),", body)}


def rust_muzzles():
    """src/lib.rs's `pub const T_MUZZLE: (i64, i64) = (.., ..);` and X_MUZZLE, in game px."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    got = {m.group(1): (int(m.group(2).replace("_", "")) / 1000, int(m.group(3).replace("_", "")) / 1000)
           for m in re.finditer(r"pub const ([TX])_MUZZLE: \(i64, i64\) = \((-?[0-9_]+), (-?[0-9_]+)\);", src)}
    return {"turret": got.get("T"), "apex": got.get("X")}


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_heimerdinger differs from build_heimerdinger.P: rebuild it first")
    got = rust_defaults()
    wrong = {k: (got.get(k), p[k]) for k in kit.NATIVE_KEYS if got.get(k) != p[k]}
    if wrong or set(got) != set(kit.NATIVE_KEYS):
        sys.exit("src/lib.rs's Params defaults differ from build_heimerdinger.P (rust, P): %s %s"
                 % (wrong, sorted(set(got) ^ set(kit.NATIVE_KEYS))))
    with open(lp(os.path.join(ROOT, "assets", "source", "heimerdinger", "hd", "side_muzzles.json")), encoding="utf-8") as f:
        art = json.load(f)
    rust = rust_muzzles()
    off = {k: (rust[k], art[k]) for k in art if rust[k] is None or max(abs(a - b) for a, b in zip(rust[k], art[k])) > 0.02}
    if off:
        sys.exit("src/lib.rs's T_MUZZLE / X_MUZZLE differ from the side turrets' muzzles (rust, art): %s" % off)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":affinity":
        sys.exit("the copy has no league_heimerdinger:affinity passive: update this script")
    text = json.dumps(champion)
    if "RangePeriodProjectile" in text or '"league_heimerdinger:q"' not in text or '"league_heimerdinger:x"' not in text:
        sys.exit("the copy still carries the turrets' zones or lacks the native turrets: update this script")
    if not all(f'"league_heimerdinger_{k}_turret_{d}"' in text for k in "tx" for d in "rl"):
        sys.exit("the copy does not draw the side turrets: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    native = {}
    for lang, swaps in SWAP.items():
        s = setup.TEXT[lang]["skill"]
        for a, b in swaps:
            if s.count(a) != 1:
                sys.exit(f"{lang}: {a!r} is not once in the main pack's skill tooltip: update SWAP")
            s = s.replace(a, b)
        native[lang] = {"skill": PREFIX[lang] + s}
    values = setup.values(p)
    texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in native.items()}
    long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in native.items() for k, tx in d.items()
            if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in native.items() for k, tx in d.items()})


if __name__ == "__main__":
    main()
