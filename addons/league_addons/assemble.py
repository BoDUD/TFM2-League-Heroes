#!/usr/bin/env python3
"""Put the add-ons' data next to league_addons.dll: one mod folder that holds every native add-on.

    python addons/league_addons/assemble.py OUT [--src addons] [--only league_nocturne_dark,league_leesin_hop]
                                            [--dll addons/target/release/league_addons.dll] [--version 0.1.0]
    python addons/league_addons/assemble.py OUT --standalone league_dragons [--dll addons/target/release/league_dragons.dll]

For each add-on folder in --src (default: every addons/league_* but this one and the STANDALONE ones; --only picks
some, e.g. the heroes already released): its override/ and effects/ files are copied (a champion copy's effect trees through
tools/kit/slim.py, the same exact rewrites tools/package_mod.py makes), every `asset/<add-on>/` path inside them and in its
mod.override_info becomes `asset/league_addons/`, the champion remaps are merged into one mod.override_info and the
text files into one of the same name each: every add-on's text/champion.i18n into one text/champion.i18n (their keys
are the add-ons' own ids - `description.league_leesin_hop` - so none collide; a clash stops the script), and any other
game text an add-on merges (text/object.i18n, text/ui.i18n ...) into text/<name>.i18n with an `asset/base/text/<name>`
merge remap. mod.mod_info: mod_id league_addons,
native code, and the highest `league` version any of them needs. --src can be the Workshop release folders (texts
already prefixed), not only the repo's.

The STANDALONE add-ons are mods of their own - their own DLL (the add-on crate's cdylib) and their own line in the
game's mod list, to switch on and off alone - and never go into the bundle: league_dragons (0.3.0, the user
2026-11-10: 「把我们的龙魂也单独做成mod开关啊」). --standalone writes one of them as its mod folder: its mod.mod_info,
mod.override_info, effects/, override/ and text/ as they are (their `asset/<add-on>/` paths are its own) and its DLL.
"""
import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ADDONS), "tools", "kit"))
import slim  # noqa: E402  the exact effect-tree rewrites (fewer nodes for the trees the game copies every tick)
import range_buffs  # noqa: E402  reach(): the league:range node for an attack with an aura at cast time
ID = "league_addons"
TEXTS = "asset/base/text/"


def load(p):
    with open(p, encoding="utf-8-sig") as f:
        return json.load(f)


def dump(o, p):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(o, ensure_ascii=False, indent=2) + "\n")


def merge(into, more, path=""):
    for k, v in more.items():
        if k not in into:
            into[k] = v
        elif isinstance(into[k], dict) and isinstance(v, dict):
            merge(into[k], v, f"{path}/{k}")
        elif into[k] != v:
            sys.exit(f"text clash at {path}/{k}")


# add-ons that are mods of their own (see the docstring): never in the bundle
STANDALONE = ("league_dragons",)


def standalone(a):
    """write the add-on a.standalone as its own mod folder a.out"""
    name = a.standalone
    if name not in STANDALONE:
        sys.exit(f"{name} is not a standalone add-on ({', '.join(STANDALONE)})")
    src = os.path.join(a.src, name)
    if os.path.exists(a.out):
        sys.exit(f"{a.out} already exists")
    os.makedirs(a.out)
    for f in ("mod.mod_info", "mod.override_info"):
        shutil.copyfile(os.path.join(src, f), os.path.join(a.out, f))
    # the players' settings file, where the add-on has one (league_dragons settings.ini)
    if os.path.isfile(os.path.join(src, "settings.ini")):
        shutil.copyfile(os.path.join(src, "settings.ini"), os.path.join(a.out, "settings.ini"))
    n = 0
    for d in ("effects", "override", "text"):
        if os.path.isdir(os.path.join(src, d)):
            shutil.copytree(os.path.join(src, d), os.path.join(a.out, d))
            n += len(os.listdir(os.path.join(src, d)))
    dll = a.dll or os.path.join(ADDONS, "target", "release", f"{name}.dll")
    shutil.copyfile(dll, os.path.join(a.out, f"{name}.dll"))
    print(f"{a.out}: {name} as its own mod ({n} data files + {name}.dll)")


def version_key(v):
    return tuple(int(x) for x in v.lstrip(">=").split("."))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--src", default=ADDONS)
    ap.add_argument("--only", help="comma-separated add-on ids")
    ap.add_argument("--dll", default=None, help="the DLL to ship (default: target/release/<mod id>.dll)")
    ap.add_argument("--standalone", help="write this add-on (one of STANDALONE) as its own mod folder instead")
    ap.add_argument("--version", default="0.1.0")
    a = ap.parse_args()
    if a.standalone:
        return standalone(a)
    a.dll = a.dll or os.path.join(ADDONS, "target", "release", f"{ID}.dll")
    if a.only and set(a.only.split(",")) & set(STANDALONE):
        sys.exit(f"{', '.join(STANDALONE)}: their own mods, never in the bundle")
    names = a.only.split(",") if a.only else sorted(
        d for d in os.listdir(a.src) if d.startswith("league_") and d != ID and d not in STANDALONE
        and os.path.isfile(os.path.join(a.src, d, "mod.override_info")))
    if os.path.exists(a.out):
        sys.exit(f"{a.out} already exists")
    override, texts, need = {}, {"champion": {}}, ">=0.0.0"
    for name in names:
        src = os.path.join(a.src, name)
        old, new = f"asset/{name}/", f"asset/{ID}/"
        for sub in ("override", "effects"):
            d = os.path.join(src, sub)
            for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                dst = os.path.join(a.out, sub, fn)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if fn.endswith(".png"):
                    shutil.copyfile(os.path.join(d, fn), dst)
                else:
                    with open(os.path.join(d, fn), encoding="utf-8-sig") as f:
                        s = f.read().replace(old, new)
                    if fn.endswith(".data_champion"):        # the exact effect-tree rewrites, as tools/package_mod.py
                        # compact (league_sylas's copy carries every League champion's ult: 12 MB pretty-printed)
                        # reach(): an attack with an area on allies / on the caster at cast time gets league.dll's
                        # league:range node (the game's AI hardly orders it at champions otherwise: range_buffs.py)
                        lean = range_buffs.reach(slim.slim_champion(json.loads(s)))
                        if range_buffs.reach(slim.slim_champion(lean)) != lean:
                            sys.exit(f"{name}/{sub}/{fn}: the packed copy does not read back as itself")
                        s = json.dumps(lean, ensure_ascii=False, separators=(",", ":")) + "\n"
                    with open(dst, "w", encoding="utf-8", newline="\n") as f:
                        f.write(s)
        for k, v in load(os.path.join(src, "mod.override_info")).items():
            if k.startswith(TEXTS):      # the game texts it merges: its text/<name>.i18n, merged below into one each
                continue
            if k in override:
                sys.exit(f"{name}: {k} is remapped by another add-on too")
            override[k] = {**v, "remapping": v["remapping"].replace(old, new)}
        tdir = os.path.join(src, "text")    # league_irelia has none: it keeps the main pack's texts
        for fn in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
            if fn.endswith(".i18n"):
                merge(texts.setdefault(fn[:-len(".i18n")], {}), load(os.path.join(tdir, fn)), fn)
        for dep in load(os.path.join(src, "mod.mod_info"))["dependencies"]:
            if dep["mod_id"] == "league" and version_key(dep["version"]) > version_key(need):
                need = dep["version"]
    os.makedirs(os.path.join(a.out, "text"), exist_ok=True)
    for stem in sorted(texts, key=lambda s: (s == "champion", s)):     # the champion text last, as it always was
        override[TEXTS + stem] = {"remapping": f"asset/{ID}/text/{stem}", "type": "merge"}
        dump(texts[stem], os.path.join(a.out, "text", f"{stem}.i18n"))
    dump(override, os.path.join(a.out, "mod.override_info"))
    dump({"author": "BoDUD", "contains_code": True,
          "dependencies": [{"mod_id": "base", "version": ">=0.4.11"}, {"mod_id": "league", "version": need}],
          "description": "League of Legends Heroes add-ons in one native mod: " + ", ".join(names) + ".",
          "mod_id": ID, "mod_type": "native", "name": "League Heroes: Add-ons", "version": a.version},
         os.path.join(a.out, "mod.mod_info"))
    shutil.copyfile(a.dll, os.path.join(a.out, f"{ID}.dll"))
    left = [p for p in (os.path.join(dp, f) for dp, _, fs in os.walk(a.out) for f in fs)
            if not p.endswith((".png", ".dll")) and any(f"asset/{n}/" in open(p, encoding="utf-8").read() for n in names)]
    if left:
        sys.exit(f"paths of the add-ons' own folders left in {left}")
    print(f"{a.out}: {len(names)} add-ons ({', '.join(names)}), league {need}, "
          f"{len(override) - len(texts)} remaps, texts {', '.join(sorted(texts))}, "
          f"{sum(len(fs) for _, _, fs in os.walk(a.out))} files")


if __name__ == "__main__":
    main()
