#!/usr/bin/env python3
"""Put the add-ons' data next to league_addons.dll: one mod folder that holds every native add-on.

    python addons/league_addons/assemble.py OUT [--src addons] [--only league_nocturne_dark,league_leesin_hop]
                                            [--dll addons/target/release/league_addons.dll] [--version 0.1.0]

For each add-on folder in --src (default: every addons/league_* but this one; --only picks some, e.g. the heroes
already released): its override/ and effects/ files are copied, every `asset/<add-on>/` path inside them and in its
mod.override_info becomes `asset/league_addons/`, the champion remaps are merged into one mod.override_info and the
text files into one text/champion.i18n (their keys are the add-ons' own ids - `description.league_leesin_hop` - so
none collide; a clash stops the script). mod.mod_info: mod_id league_addons, native code, and the highest `league`
version any of them needs. --src can be the Workshop release folders (texts already prefixed), not only the repo's.
"""
import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.dirname(HERE)
ID = "league_addons"
TEXT = "asset/base/text/champion"


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


def version_key(v):
    return tuple(int(x) for x in v.lstrip(">=").split("."))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--src", default=ADDONS)
    ap.add_argument("--only", help="comma-separated add-on ids")
    ap.add_argument("--dll", default=os.path.join(ADDONS, "target", "release", f"{ID}.dll"))
    ap.add_argument("--version", default="0.1.0")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else sorted(
        d for d in os.listdir(a.src) if d.startswith("league_") and d != ID
        and os.path.isfile(os.path.join(a.src, d, "mod.override_info")))
    if os.path.exists(a.out):
        sys.exit(f"{a.out} already exists")
    override, text, need = {}, {}, ">=0.0.0"
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
                        s = f.read()
                    with open(dst, "w", encoding="utf-8", newline="\n") as f:
                        f.write(s.replace(old, new))
        for k, v in load(os.path.join(src, "mod.override_info")).items():
            if k == TEXT:
                continue
            if k in override:
                sys.exit(f"{name}: {k} is remapped by another add-on too")
            override[k] = {**v, "remapping": v["remapping"].replace(old, new)}
        merge(text, load(os.path.join(src, "text", "champion.i18n")))
        for dep in load(os.path.join(src, "mod.mod_info"))["dependencies"]:
            if dep["mod_id"] == "league" and version_key(dep["version"]) > version_key(need):
                need = dep["version"]
    override[TEXT] = {"remapping": f"asset/{ID}/text/champion", "type": "merge"}
    os.makedirs(os.path.join(a.out, "text"), exist_ok=True)
    dump(text, os.path.join(a.out, "text", "champion.i18n"))
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
          f"{len(override) - 1} remaps, {sum(len(fs) for _, _, fs in os.walk(a.out))} files")


if __name__ == "__main__":
    main()
