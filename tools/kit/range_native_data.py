"""Turn a hand-made kit's range buffs into league.dll's markers (tools/kit/range_buffs.py) in place.

    python tools/kit/range_native_data.py league_akali league_evelynn league_kayle league_riven

For the kits with no build script: every buff in range_buffs.RANGE_BUFFS loses its `range` (the value must be the
table's) and the attack gets the `league:range` node, last in its top Combine. The file keeps its layout (indent 2,
its own line ends). Running it again changes nothing.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import range_buffs  # noqa: E402


def convert(hero):
    path = os.path.join(ROOT, "league", "champion", f"{hero}.data_champion")
    raw = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    d = range_buffs.apply(json.loads(raw.lstrip("﻿")))
    out = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
    if raw.startswith("﻿"):
        out = "﻿" + out
    changed = out != raw
    if changed:
        io.open(path, "w", encoding="utf-8", newline="").write(out)
    return changed


def main():
    for hero in sys.argv[1:]:
        print(hero, "converted" if convert(hero) else "unchanged")


if __name__ == "__main__":
    main()
