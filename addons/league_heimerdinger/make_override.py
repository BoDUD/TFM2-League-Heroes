"""Build the add-on's copy of Heimerdinger from the main pack (turrets firing visible shots, the affinity by towers too).

    python addons/league_heimerdinger/make_override.py [--check]

Rebuilds Heimerdinger with tools/kit/build_heimerdinger.py (its parameter table P), checks that the plain build is the
main pack's league/champion/league_heimerdinger.data_champion byte for byte (so the copy never drifts from the shipped
kit), that src/lib.rs's default Params are P's numbers and its T_MUZZLE / X_MUZZLE the side turrets' muzzles
(assets/source/heimerdinger/hd/side_muzzles.json, written by tools/art/import_heimerdinger_fx.py), and writes
addons/league_heimerdinger/override/league_heimerdinger.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the bolt and W's rockets, E's grenade, R upgrading the next spell, the combos);
  * the turrets keep their sounds and three slots but no zones: Q's put and the upgraded Q's apex run the add-on's
    league_heimerdinger:q / :x, which stand its native turrets and say which side they face (t_face_l / x_face_l):
    the turrets are drawn from the side (league_heimerdinger_turret_r / _l, _apex_r / _l);
  * passive = the add-on's league_heimerdinger:affinity with the numbers of P it and the hook (combo.rs) use
    (passive.params);
  * the shots' views (t_shot, t_beam_line, x_shot: drawn in league_heimerdinger_fx, unbound in the main pack);
  * 0.3.0, the turrets' bodies (src/lib.rs; tools/art/unit_heimerdinger_turrets.py draws their sheets): the side turret
    the hidden bolt draws where it stops plays only without `T_UNIT` (the turrets) / `X_UNIT` (the apex) - the native put
    spawns the body at the cast and lays the flag when the host gives a unit. The bodies' attack timings (TU_ACT /
    TU_LANDS, XU_ACT / XU_LANDS), muzzles (TU_MUZZLE / XU_MUZZLE) and the slots' flags (SLOT_FLAGS) are checked against
    the unit sheets and P: change either and this script stops until lib.rs follows;
  * the skill's tooltip points to description.league_heimerdinger.skill with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Heimerdinger changes. --check: write nothing,
exit 1 when the files on disk are not what this would write.
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
sys.path.insert(0, os.path.join(ROOT, "tools", "art"))
import unit_heimerdinger_turrets as bodies  # noqa: E402

MOD_ID = "league_heimerdinger"
HERO = "league_heimerdinger"
SLOTS = ("skill",)
# the main pack's tooltip with the add-on's prefix and the towers in the affinity (each pair must match once)
PREFIX = {"zh-hans": "【扩展包】", "zh-hant": "【擴充包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
SWAP = {
    "zh-hans": [("攻击一个敌人", "射击一个敌人"), ("在炮台旁移速", "在炮台或己方防御塔旁移速"),
                ("放下一座炮台（最多3座）", "放下一座炮台（最多3座，可被摧毁）")],
    "zh-hant": [("攻擊一個敵人", "射擊一個敵人"), ("在砲臺旁跑速", "在砲臺或己方防禦塔旁跑速"),
                ("放下一座砲臺（最多3座）", "放下一座砲臺（最多3座，可被摧毀）")],
    "en": [("strikes one enemy", "shoots one enemy"), ("near his turrets.", "near his turrets or his side's towers."),
           ("Sets down a turret (up to 3)", "Sets down a turret (up to 3; it can be destroyed)")],
    "ko": [("포탑 근처에서", "포탑이나 아군 타워 근처에서"), ("포탑을 설치한다(최대 3개, ", "포탑을 설치한다(최대 3개, 파괴 가능, ")],
    "ja": [("砲台の近くで", "砲台か味方タワーの近くで"), ("砲台を設置（最大3基、", "砲台を設置（最大3基、破壊可能、")],
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


def consts(src):
    """src/lib.rs's `pub const NAME: <type> = <value>;` - integers, strings, string arrays, (i64, i64) pairs."""
    out = {}
    for name, kind, value in re.findall(r"pub const (\w+): (usize|&str|\[&str; \d+\]|\(i64, i64\)) = ([^;]+);", src):
        value = value.strip()
        if kind == "&str":
            out[name] = value.strip('"')
        elif kind.startswith("["):
            out[name] = re.findall(r'"([^"]+)"', value)
        elif kind.startswith("("):
            out[name] = tuple(int(v.replace("_", "")) for v in re.findall(r"-?[0-9_]+", value))
        else:
            out[name] = int(value.replace("_", ""))
    return out


def walk(o):
    """every dict of a tree"""
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def replace(o, match, make, count):
    """the tree with every dict `match` takes replaced by `make` of it (counted in `count`)"""
    if isinstance(o, dict):
        if match(o):
            count.append(o)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


def units(champion, c):
    """0.3.0: the side turret drawn where the hidden bolt stops plays only without the body's flag. The natives' numbers
    (c: src/lib.rs) checked against the unit sheets and P."""
    want = {}
    want["TU_ACT"], want["TU_LANDS"] = bodies.flash_lands(c["H28G"])
    want["XU_ACT"], want["XU_LANDS"] = bodies.flash_lands(c["H28Q"])
    m = bodies.muzzles()
    want["TU_MUZZLE"], want["XU_MUZZLE"] = m[c["H28G"]], m[c["H28Q"]]
    want["SLOT_FLAGS"] = [f"{HERO}_t{k}_busy" for k in kit.SLOTS]
    wrong = {k: (c.get(k), v) for k, v in want.items() if c.get(k) != v}
    if wrong:
        sys.exit(f"the bodies' numbers differ from src/lib.rs (lib, sheet or kit): {wrong}")
    text = json.dumps(champion)
    for f in c["SLOT_FLAGS"]:
        if f'"{f}"' not in text:
            sys.exit(f"the main pack's Heimerdinger has no slot flag {f}: update src/lib.rs")
    names = {x.get("buff_name") for x in walk(champion) if x.get("type") == "SwitchByBuff"}
    names |= {x["buff_state"]["name"] for x in walk(champion) if isinstance(x.get("buff_state"), dict)}
    if any(c[k] in names for k in ("T_UNIT", "X_UNIT")) or any(str(b).startswith((c["T_UID"], c["X_UID"])) for b in names):
        sys.exit("the main pack's Heimerdinger already uses one of the add-on's buff names: update src/lib.rs")
    for side, flag, n in (("t", c["T_UNIT"], len(kit.SLOTS)), ("x", c["X_UNIT"], 1)):
        found = []
        champion = replace(champion, lambda o: o.get("type") == "SwitchByBuff" and o.get("buff_name") == f"{HERO}_{side}_face_l",
                           lambda o: {"type": "SwitchByBuff", "buff_name": flag, "effect_buff": {"type": "Combine", "effects": []},
                                      "effect_none": o}, found)
        if len(found) != n:
            sys.exit(f"the side picture {side}_face_l is drawn {len(found)} times, not {n}: update this script")
    return champion


def main():
    check = "--check" in sys.argv[1:]
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
    c = consts(open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read())
    # 0.3.1: W's rockets charge the beam in the data (the copy's attack keeps the ladder); the native turrets read and spend
    # its top flag, src/lib.rs's WC_FULL
    if f'"{c["WC_FULL"]}"' not in json.dumps(champion["attack"]) or f'"{HERO}_wc{p["wc_n"] - 1}"' not in json.dumps(champion["attack"]):
        sys.exit("the copy's rockets do not climb to src/lib.rs's WC_FULL: update src/lib.rs or this script")
    champion = units(champion, c)
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
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    files = {out: json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
             out_text: json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                                  ensure_ascii=False, indent=2) + "\n"}
    if check:
        stale = [os.path.relpath(path, ROOT) for path, text in files.items()
                 if not os.path.isfile(lp(path)) or open(lp(path), encoding="utf-8").read() != text]
        if stale:
            sys.exit("not as make_override.py writes them: %s" % stale)
        print("ok")
        return
    for path, text in files.items():
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in native.items() for k, tx in d.items()})


if __name__ == "__main__":
    main()
