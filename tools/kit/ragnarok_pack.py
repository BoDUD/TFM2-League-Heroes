"""The ragnarok pack's shared files and the helpers every hero's setup_<hero>.py uses (setup_lubu.py, setup_thor.py).

The pack (mod_id ragnarok, ragnarok/) owns mod.mod_info (VERSION, the description naming every hero of HEROES,
contains_code / mod_type native for ragnarok.dll, the keys sorted) and the text / champion_view merges of
mod.override_info. Each hero's setup writes only its own keys (`write_hero`): its texts in text/champion.i18n, its
sound/sfx/<id>_*.sound_info files with two override entries a sound (its event -> our .sound_info, its clip -> our
audio, the custom-sound rule), its champion_view entry. JSON as the game writes it: indent 2, CRLF, UTF-8.
An event never shares a clip's name: event <id>_<x> plays clip <id>_sfx_<...> or <id>_vo_<...>.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
MOD = os.path.join(REPO, MOD_ID)
VERSION = "0.11.0"
NAME = "Record of Ragnarok Heroes"
HEROES = ["Lu Bu", "Thor", "Zeus", "Adam", "Poseidon", "Sasaki Kojiro", "Heracles", "Jack the Ripper", "Raiden Tameemon", "Shiva", "Buddha", "Zerofuku", "Hades", "Qin Shi Huang", "Beelzebub", "Nikola Tesla", "Leonidas", "Apollo"]
DESC = ("Fighters of Record of Ragnarok for Teamfight Manager 2: {heroes}. Kits are our own designs after the manga's "
        "fights: Lu Bu's Shield Breaker counts his blows double against shields and shatters them for real (the pack's "
        "own code, ragnarok.dll); Thor's Mjolnir flies out and back to his hand and awakens on every third skill; Zeus swells into his muscle "
        "body once he warms up and presses it down into Adamas for his ultimate; Adam reads every move with God Reader, "
        "dodges it and hits back with a copy, down to the Fist That Transcends Time; Poseidon needs no one - alone he "
        "hits harder and takes less (the pack's own code), and his trident floods a target for forty days and nights; "
        "Sasaki Kojiro, the greatest loser in history, learns every foe he strikes and hits them harder each time (the "
        "pack's own code), turns his blade back with Swallow Return and draws two swords for Niten Ganryu; "
        "Heracles, the god of justice who fights for humanity, spreads the brand of his Twelve Labors with every "
        "skill (the pack's own code) and makes his pact with Cerberus for his ultimate; Jack the Ripper sees the "
        "colour of every heart and strikes the frightened harder (the pack's own code), slips into the London fog "
        "under an umbrella his gloves made divine and throws a knife that Dear God made a divine weapon; Raiden "
        "Tameemon, the strongest sumo wrestler, unbinds the muscles he held back all his life before his first "
        "Yatagarasu, slaps with Tsuppari and stamps the ground with Shiko; Shiva dances with four arms to a rhythm "
        "that speeds him up (the pack's own code) and sets his heart alight for Tandava Karma; Buddha, the god who "
        "turned his back on the gods, sees every blow coming with Future Sight, turns his Six Realms Staff into a spear "
        "and the Kannon Shield and cuts with the Great Nirvana Sword Zero; Zerofuku, the god of misfortune, marks his foes "
        "with misfortune and swings a Misery Cleaver that grows on it, until Hajun devours him from within and breaks out "
        "of a dark cocoon for the rest of his life, with arm blades and a demon drill; Hades, king of the underworld and "
        "eldest of the three brothers, sweeps the wind of Persephone Rhoai with his bident, smashes the ground and "
        "forges the Ichor Desmos with his own blood for one thrust; Qin Shi Huang, the first emperor, sees the stars "
        "in his foes, catches their force with the Chiyou Armor Sleeves and turns it back, shielding his allies, "
        "until he draws the Goujian sword; Beelzebub, lord of the flies, makes everything his skills touch vibrate and "
        "lose its magic resist, sends waves from his bone staff, raises the Gate of Hell and crushes his foes into the "
        "black core of the False God Chaos; Nikola Tesla fights in his Super Automaton Beta, his plasma fists hitting "
        "twice, drops God's Prison on his foes and, while it stands, warps onto them with Tesla Step; Leonidas, king "
        "of Sparta, guards the allies around him like a phalanx, hurls his chained shield to drag a foe in, raises "
        "it to send back what hits him and charges with the Shield of Truth; Apollo, god of the sun, binds his foes "
        "with Artemis's Thread, looses arrows from a bow of light and has her statue shoot him at them as a silver "
        "arrow. "
        "Sharper frames from ragnarok.dll itself, with or without the League of Legends Heroes and Teamfight Tactics "
        "Heroes packs. Pixel art, effects, icons and sound effects made for this pack; Japanese voice lines from the "
        "official promotional recordings. Non-commercial fan project; Record of Ragnarok (c) its creators and "
        "publishers.")

# the game's tooltip box (lint_mod's TOOLTIP_MAX, the tft pack's numbers)
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
M = "<#a974ffff>"      # magic damage
S = "<#e8d44dff>"      # shields
E = "<>"
AD = ADi + O + "100%" + E


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def ratio(r):
    return f"{ADi}{O}{{{r}}}%{E}"


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def load(path, default=None):
    if default is not None and not os.path.isfile(lp(path)):
        return default
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    os.makedirs(os.path.dirname(lp(path)), exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def kit_sounds(hid):
    """Every Sfx / TargetSfx name a hero's kit plays."""
    found = set()

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") in ("Sfx", "TargetSfx"):
                found.add(o["name"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(load(os.path.join(MOD, "champion", f"{hid}.data_champion")))
    return found


def dll_sounds(hid, module):
    """The sounds ragnarok.dll plays for a hero (`vo("...")` in a play_sfx of addons/ragnarok/src/<module>.rs, and its
    voice lines "v_...")."""
    src = open(lp(os.path.join(REPO, "addons", "ragnarok", "src", f"{module}.rs")), encoding="utf-8").read()
    names = {f"{hid}_{x}" for x in re.findall(r'play_sfx\(&vo\("(\w+)"\)', src)}
    names |= {f"{hid}_{x}" for x in re.findall(r'"(v_\w+)"', src)}
    return names


def check_lengths(text):
    """Print each text's shown length against TOOLTIP_MAX; True when one is too long."""
    bad = False
    for lang, t in text.items():
        lens = {k: shown_length(t[k]) for k in ("attack", "skill", "skill2", "ult")}
        bad |= any(n > TOOLTIP_MAX[lang] for n in lens.values())
        print(lang, " ".join(f"{k}:{n}/{TOOLTIP_MAX[lang]}" for k, n in lens.items()))
    return bad


def print_texts(tx):
    sys.stdout.reconfigure(encoding="utf-8")
    for lang, (d, _) in tx.items():
        for k in ("attack", "skill", "skill2", "ult"):
            print(lang, k, re.sub(r"<[^>]*>", "", d[k]))


def write_hero(hid, tx, sounds, view, module, seed):
    """One hero's keys in the pack's shared files: tx {lang: (description dict, skill_name dict)}, sounds {event:
    [(clip, volume, delay)]} (must be every sound the kit and the DLL module play), view (champion_view entry)."""
    played = kit_sounds(hid) | dll_sounds(hid, module)
    if played != set(sounds):
        sys.exit(f"the kit or the DLL plays {sorted(played - set(sounds))} without a sound_info, SOUNDS has unused "
                 f"{sorted(set(sounds) - played)}")

    i18n = load(os.path.join(MOD, "text", "champion.i18n"), {})
    for lang, (d, names) in tx.items():
        i18n.setdefault(lang, {}).setdefault("description", {})[hid] = d
        i18n[lang].setdefault("skill_name", {})[hid] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    clips = set()
    for name, plays in sounds.items():
        for c, _, _ in plays:
            if c == name:
                sys.exit(f"{name}: plays a clip of its own name")
            if not any(os.path.isfile(lp(os.path.join(MOD, "sound", "sfx", c + ext))) for ext in (".mp3", ".wav")):
                print(f"warning: {c}.mp3 missing - run {seed}")
            clips.add(c)
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    ov.setdefault("asset/base/text/champion", {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"})
    ov.setdefault("asset/base/style/champion_view",
                  {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"})
    for k in [k for k in ov if k.startswith(f"asset/base/sound/sfx/{hid}_")]:   # this hero's sound keys rebuilt
        del ov[k]
    for name in list(sounds) + sorted(clips):
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/{MOD_ID}/sound/sfx/{name}", "type": "override"}
    # the sound entries sorted, so the file is the same whichever hero's setup ran last
    snd = sorted(k for k in ov if k.startswith("asset/base/sound/sfx/"))
    ov = {**{k: v for k, v in ov.items() if not k.startswith("asset/base/sound/sfx/")}, **{k: ov[k] for k in snd}}
    save(os.path.join(MOD, "mod.override_info"), ov)

    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"), {"entries": {}})
    cv["entries"][hid] = json.loads(json.dumps(view))
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)
    return len(sounds), len(clips)


def write_mod_info():
    mi = load(os.path.join(MOD, "mod.mod_info"), {})
    if tuple(int(x) for x in mi.get("version", "0.0.0").split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    mi.update({"author": "BoDUD", "dependencies": [{"mod_id": "base", "version": ">=0.4.11"}], "mod_id": MOD_ID,
               "name": NAME, "description": DESC.format(heroes=", ".join(HEROES)), "contains_code": True,
               "mod_type": "native", "last_updated": "2026-11-22"})
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
