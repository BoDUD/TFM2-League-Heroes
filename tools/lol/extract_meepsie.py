r"""Pull Meepsie's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_meepsie.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). Set 17's TFT17_IvernMinion names three events in its skin bin -
Play_sfx_tft17_IvernMinion_Hero_cast, _slam_into, _slam_hit (its Big Bang) - kept in Map22.wad.client: the set-17 events
bank 15129048668926572079 and their media in bank 9260171914222294871 (both found by hash, 2026-11-01, C:/t/mp_work
findbank.py / media.py). Meepsie is League's Daisy (Ivern's IvernMinion) made of moon rock, and its slam events mirror
Daisy's, so the rest of the golem is Daisy's own (Champions/Ivern.wad.client: her punch, hit, slam wind-up, voice and
farewell); the meeps are Bard's (his meep spawn, a meep flying and striking, the meeps' slow, his healing shrine).
Read, never written; the bank's Wwise events resolved to their media (the first variant unless picked), decoded with
vgmstream and written as mono 16-bit WAVs to tft/sound/sfx/ (git-ignored: audio (c) Riot Games).
"""
import argparse
import os
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_garen import decode, finish, lp  # noqa: E402
from riot import SoundBanks, Wad, bnk_media, parse_wpk  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MOD = os.path.join(ROOT, "tft")
C = "tft_meepsie_sfx_"
T = "Play_sfx_tft17_IvernMinion_"
DY = "Play_sfx_Ivern_IvernR_Daisy_"
B = "Play_sfx_Bard_"
EVENTS, MEDIA = 15129048668926572079, 9260171914222294871   # Map22: the set-17 events bank and its media bank

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("Ivern", [DY + "attack_into"], 0.9, -9),                    # the moon-rock punch
    C + "a_hit": ("Ivern", [DY + "hit"], 0.8, -9),
    C + "p": ("Bard", [B + "meep_hit"], 0.6, -13),                        # the pilot's zap on a punch
    C + "q": ("Ivern", [DY + "slam_ready"], 0.9, -9),                     # the fist raised over the ground
    C + "q_hit": ("Ivern", [DY + "slam_hit"], 1.2, -8),                   # the moon-dust quake
    C + "q_slow": ("Bard", [B + "meep_slow"], 0.8, -13),
    C + "e": ("Bard", [B + "BardMeepSpawn"], 1.0, -10),                   # the healing meeps pop out
    C + "e_vo": ("Ivern", [DY + "Vox_Giggle"], 1.2, -9),
    C + "e_fly": ("Bard", [B + "meep_mis"], 0.8, -12),
    C + "e_heal": ("Bard", [B + "BardWActualHealing_OnBuffActivate"], 1.2, -11),
    C + "r": ("tft17", [T + "Hero_cast"], 1.5, -7),                       # the Big Bang: up and away
    C + "r_vo": ("Ivern", [DY + "Vox_Rage"], 1.5, -7),
    C + "r_into": ("tft17", [T + "slam_into"], 1.2, -7),                  # coming down
    C + "r_hit": ("tft17", [T + "slam_hit"], 1.6, -6),                    # the slam lands
    C + "d": ("Ivern", [DY + "Vox_Bye"], 1.8, -8),                        # falls on its face
}


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: tft17 = Map22's set-17 banks, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src == "tft17":
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map22.wad.client"))
        audio = w.read(MEDIA)
        cache[src] = SoundBanks([w.read(EVENTS), audio], dict(bnk_media(audio)))
        return cache[src]
    w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Champions", f"{src}.wad.client"))
    stem = f"assets/sounds/wwise2016/sfx/characters/{src.lower()}/skins/base/{src.lower()}_base_sfx_"
    audio = w.read_path(stem + "audio.bnk")
    media = dict(bnk_media(audio))
    if w.has(stem + "audio.wpk"):
        media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
    cache[src] = SoundBanks([w.read_path(stem + "events.bnk"), audio], media)
    return cache[src]


def variants_of(banks, ev):
    """An event's media, by its name or (unnamed) its event id."""
    if isinstance(ev, int):
        return [m for m in dict.fromkeys(banks._resolve(ev, set())) if m in banks.media]
    return banks.event_media(ev)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22 and the champions)")
    ap.add_argument("--vgmstream", required=True, help="vgmstream-cli.exe")
    a = ap.parse_args()
    out_dir = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out_dir), exist_ok=True)
    cache = {}
    for name, (src, events, max_s, peak, *pick) in CLIPS.items():
        banks = banks_of(src, a, cache)
        event, variants = None, []
        for ev in events:
            variants = variants_of(banks, ev)
            if variants:
                event = ev
                break
        if not variants:
            sys.exit(f"{name}: none of {events} resolves in {src} - game patch changed the bank?")
        k = min(pick[0], len(variants) - 1) if pick else 0
        sr, x = decode(banks.media[variants[k]], a.vgmstream)
        pcm = finish(x, sr, max_s, peak)
        with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        print(f"{name:30s} {len(pcm) / sr:4.2f}s  <- {src} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
