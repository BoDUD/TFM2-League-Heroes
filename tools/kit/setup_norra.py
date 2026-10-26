"""Norra's sound_info files and her sound entries in the tft pack's mod.override_info (texts, champion_view and the
mod_info come at integration, setup_powder.py's way).

    python tools/kit/setup_norra.py

Writes (in tft/, mod_id tft): sound/sfx/tft_norra_*.sound_info and, in mod.override_info, two entries a sound (its
event -> our .sound_info, its clip -> our audio: the custom-sound rule). Only her keys change in the shared files. JSON:
indent 2, CRLF, UTF-8.
Sounds: League clips borrowed by tools/lol/extract_norra.py into tft/sound/sfx/tft_norra_sfx_*.wav (git-ignored) - the
user's call for her (2026-10-26: 「诺拉用抓好的英雄联盟音效」), unlike Powder's base-game mixes. A clip name never equals
an event name (vo-clip-names rule): event tft_norra_<x> plays clip tft_norra_sfx_<x>. package_mod moves the clips to
sound/bgm/ at install.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_norra import lp, MOD_ID, ID  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_norra's sfx / tsfx)
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.35, 0.0)],
    f"{ID}_p_heal": [(CLIP + "p_heal", 0.35, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.45, 0.0)],
    f"{ID}_q_blast": [(CLIP + "q_blast", 0.5, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_e_shield": [(CLIP + "e_shield", 0.4, 0.0)],
    f"{ID}_e_anvil": [(CLIP + "e_anvil", 0.5, 0.0)],
    f"{ID}_e_book": [(CLIP + "e_book", 0.5, 0.0)],
    f"{ID}_e_potion": [(CLIP + "e_potion", 0.45, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.5, 0.0)],
    f"{ID}_r_blast": [(CLIP + "r_blast", 0.55, 0.0)],
    f"{ID}_r_hit": [(CLIP + "r_hit", 0.35, 0.0)],
}


def load(path, default=None):
    if default is not None and not os.path.isfile(lp(path)):
        return default
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    os.makedirs(os.path.dirname(lp(path)), exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def kit_sounds():
    """Every Sfx / TargetSfx name the kit plays."""
    kit = load(os.path.join(MOD, "champion", f"{ID}.data_champion"))
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
    walk(kit)
    return found


def main():
    played = kit_sounds()
    if played != set(SOUNDS):
        sys.exit(f"the kit plays {sorted(played - set(SOUNDS))} without a sound_info, SOUNDS has unused "
                 f"{sorted(set(SOUNDS) - played)}")
    clips = set()
    for name, plays in SOUNDS.items():
        for c, _, _ in plays:
            if c == name:
                sys.exit(f"{name}: plays a clip of its own name")
            if not os.path.isfile(lp(os.path.join(MOD, "sound", "sfx", c + ".wav"))):
                print(f"warning: {c}.wav missing - run tools/lol/extract_norra.py")
            clips.add(c)
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    for k in [k for k in ov if k.startswith(f"asset/base/sound/sfx/{ID}_")]:   # her sound keys rebuilt
        del ov[k]
    for name in list(SOUNDS) + sorted(clips):
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/{MOD_ID}/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)
    print(len(SOUNDS), "sounds,", len(clips), "clips written")


if __name__ == "__main__":
    main()
