"""Alune's sound_info files and her sound entries in the tft pack's mod.override_info (texts, champion_view and the
mod_info come at integration, setup_powder.py's way).

    python tools/kit/setup_alune.py

Writes (in tft/, mod_id tft): sound/sfx/tft_alune_*.sound_info and, in mod.override_info, two entries a sound (its
event -> our .sound_info, its clip -> our audio: the custom-sound rule). Only her keys change in the shared files. JSON:
indent 2, CRLF, UTF-8.
Sounds: tools/lol/extract_alune.py's clips in tft/sound/sfx/tft_alune_sfx_*.wav (git-ignored) - her own set-11 TFT
sounds (attack, Moonfall's cast and shards, her Chinese voice line on the ult) and Diana's Pale Cascade / Moonfall for
Moonlight and the full moon. A clip name never equals an event name (vo-clip-names rule): event tft_alune_<x> plays
clip tft_alune_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_alune import lp, MOD_ID, ID  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_alune's sfx / tsfx)
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.35, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.45, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.35, 0.0)],
    f"{ID}_e_cast": [(CLIP + "e_cast", 0.45, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.25, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.5, 0.0), (CLIP + "r_vo", 0.6, 0.0)],
    f"{ID}_r_blast": [(CLIP + "r_blast", 0.55, 0.0)],
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_alune.py")
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
