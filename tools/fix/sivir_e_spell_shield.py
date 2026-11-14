#!/usr/bin/env python3
"""Sivir's Spell Shield lasts 1.5 s, as in League (the user, 2026-11-14, on the list of differences from League:
「全改吧」).

    python tools/fix/sivir_e_spell_shield.py [--check]

League (the wiki, V26.20): "Sivir gains a spell shield for 1.5 seconds"; it blocks the next hostile effect, then heals
her and activates Fleet of Foot. Here E raised the shield for up to 3 s (180 ticks). The rest stays as it was, because
the engine has no "block one ability": while the shroud holds (`league_sivir_e_shroud`, skill_damaged_reduce 100 and
cc_immune) every skill and crowd control is stopped, and the first hit of any kind (a 1-point shield that breaks:
`league_sivir_e_guard`, WithShield, read by a poll every 6 ticks) heals her, starts Fleet of Foot and ends the shroud a
second later (HOLD, unchanged), so a burst of skills cast together is still caught.
The four timings hang together: the sensor shield lasts T + 4 ticks, the read window `league_sivir_e_guard_on` T - 4,
the shroud T, the poll T - 2 (they were 184 / 176 / 180 / 178 for 180).
Edits league/champion/league_sivir.data_champion and E's five texts in league/text/champion.i18n in place. Idempotent;
--check only says whether it is there.
"""
import argparse
import json
import os
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KIT = os.path.join(ROOT, "league", "champion", "league_sivir.data_champion")
TEXT = os.path.join(ROOT, "league", "text", "champion.i18n")
T = 90                       # League's 1.5 s
WANT = {"sensor": T + 4, "league_sivir_e_guard_on": T - 4, "league_sivir_e_shroud": T, "league_sivir_e_poll": T - 2}
# E's text: "up to 3 s" -> "up to 1.5 s" (the 1 s after the first hit stays)
WORDS = {"zh-hans": ("最多<#ffb900ff>3秒<>", "最多<#ffb900ff>1.5秒<>"),
         "zh-hant": ("最多<#ffb900ff>3秒<>", "最多<#ffb900ff>1.5秒<>"),
         "en": ("for up to <#ffb900ff>3s<>", "for up to <#ffb900ff>1.5s<>"),
         "ko": ("최대 <#ffb900ff>3초<>", "최대 <#ffb900ff>1.5초<>"),
         "ja": ("最大<#ffb900ff>3秒<>", "最大<#ffb900ff>1.5秒<>")}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    raw = open(lp(path), "rb").read().decode("utf-8")
    return json.loads(raw, object_pairs_hook=OrderedDict), raw


def dump(data, raw):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if "\r\n" in raw:
        text = text.replace("\n", "\r\n")
    return text + raw[len(raw.rstrip("\r\n")):]


def timings(e2):
    """The four timing holders in E's effect: name -> the dict whose "tick" it is."""
    out = {}
    for e in e2["effects"]:
        if e.get("type") == "RangeEffect" and e.get("target") == "AllyOnlySelf":
            sens = [x for x in e["effects"] if x.get("type") == "Shield" and x.get("amount") == 1]
            if sens:
                out["sensor"] = sens[0]
        elif e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] in WANT:
            out[e["buff_state"]["name"]] = e["buff_state"]["duration"]["Time"]
        elif e.get("type") == "ParabolicProjectile" and e.get("name") == "league_sivir_e_lob":
            poll = [x for x in e["end_effects"] if x.get("name") == "league_sivir_e_poll"]
            if poll:
                out["league_sivir_e_poll"] = poll[0]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    kit, raw = load(KIT)
    assert dump(kit, raw) == raw, "the kit is not in the form this script writes"
    found = timings(kit["skill2"]["effect"])
    if sorted(found) != sorted(WANT):
        sys.exit(f"E's timings not all found ({sorted(found)}): the kit changed")
    done = all(found[k]["tick"] == v for k, v in WANT.items())
    text, traw = load(TEXT)
    assert dump(text, traw) == traw, "champion.i18n is not in the form this script writes"
    worded = all(new in text[lang]["description"]["league_sivir"]["skill2"] for lang, (_, new) in WORDS.items())
    if a.check:
        print("Spell Shield 1.5 s:", "there" if done and worded else "NOT there")
        sys.exit(0 if done and worded else 1)
    if not done:
        for k, v in WANT.items():
            found[k]["tick"] = v
        open(lp(KIT), "w", encoding="utf-8", newline="").write(dump(kit, raw))
    if not worded:
        for lang, (old, new) in WORDS.items():
            s = text[lang]["description"]["league_sivir"]["skill2"]
            if new in s:
                continue
            if s.count(old) != 1:
                sys.exit(f"{lang}: {old!r} not found once in E's text")
            text[lang]["description"]["league_sivir"]["skill2"] = s.replace(old, new)
        open(lp(TEXT), "w", encoding="utf-8", newline="").write(dump(text, traw))
    print("Spell Shield lasts 1.5 s:", "already there" if done and worded else "written")


if __name__ == "__main__":
    main()
