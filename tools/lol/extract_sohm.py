r"""Pull Sohm's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_sohm.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Her own sounds (the user: 「音效什么都要自己找」). Set 7 (TFT7_AquaticDragon) names her events in her skin and animation
bins and Map22's set-7 champions bank (Nomsy's, Shi Oh Yu's and Sy'fen's) holds them under that spelling (found
2026-10-30): BasicAttack and CritAttack, each _OnCast / _OnHit, QWaveMissile_missilecast / _OnHit /
_mark_buffactivate (Tideblossom's wave and its flower) and QMissile_cast / _hit (the flower moving on). The rest is
Nami's: Ebb and Flow's splash on an ally for a tide stack (碧波之力), Ebb and Flow's cast and Tidecaller's Blessing for the water
shield (海潮护佑), Tidal Wave's cast and Aqua Prison's burst for the bloom (潮汐绽放); and the Rift's drake death.
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
C = "tft_sohm_sfx_"
G = "Play_sfx_tft7_AquaticDragon"
D = "Play_sfx_SRU_Dragon_"
NA = "Play_sfx_Nami_Nami"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft7", [G + "BasicAttack_OnCast"], 0.8, -11),                   # the water bolt
    C + "a_hit": ("tft7", [G + "BasicAttack_OnHit"], 0.7, -11),
    C + "p": ("Nami", [NA + "WMissileAlly_hit"], 0.9, -13),                     # a tide stack
    C + "q": ("tft7", [G + "QWaveMissile_missilecast"], 1.0, -9),              # Tideblossom's wave
    C + "q_hit": ("tft7", [G + "QWaveMissile_OnHit"], 0.8, -9),
    C + "q_mark": ("tft7", [G + "QWaveMissile_mark_buffactivate"], 1.0, -10),  # the water flower opens
    C + "q_jump": ("tft7", [G + "QMissile_cast"], 0.8, -10),                   # the flower moves on
    C + "q_jump_hit": ("tft7", [G + "QMissile_hit"], 0.8, -10),
    C + "e": ("Nami", [NA + "W_OnCast"], 0.9, -10),                            # the claws push the water out
    C + "e_shield": ("Nami", [NA + "E_OnBuffActivate"], 1.0, -10),             # the ally's water shield
    C + "r": ("Nami", [NA + "R_OnCast"], 1.6, -8),                             # the tide rises
    C + "r_cast": ("tft7", [G + "CritAttack_OnCast"], 0.9, -9),
    C + "r_bloom": ("Nami", [NA + "Q_hit"], 1.2, -8),                          # every flower bursts
    C + "r_hit": ("tft7", [G + "CritAttack_OnHit"], 0.8, -9),
    C + "d": ("dragons", [D + "death_cast"], 2.0, -7),                         # she sinks
}
SET7_EVENTS, SET7_AUDIO = 5148408258298239144, 13347058717425747428   # Map22, path hashes (names unknown)
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_dragons_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: tft7 = Map22's set-7 bank, dragons / infernal = Map11's drakes,
    else a champion's base skin."""
    if src in cache:
        return cache[src]
    final = os.path.join(a.riot, "Game", "DATA", "FINAL")
    if src == "tft7":
        w = Wad(os.path.join(final, "Maps", "Shipping", "Map22.wad.client"))
        if SET7_EVENTS not in w.entries or SET7_AUDIO not in w.entries:
            sys.exit("Map22 has no set-7 bank at the known hashes - game patch changed it? (look for the bank whose "
                     "HIRC holds Play_sfx_tft7_Nomsy_fireball_hit)")
        audio = w.read(SET7_AUDIO)
        cache[src] = SoundBanks([w.read(SET7_EVENTS), audio], dict(bnk_media(audio)))
        return cache[src]
    if src in ("dragons", "infernal"):
        w = Wad(os.path.join(final, "Maps", "Shipping", "Map11.wad.client"))
        stem = MAP11 + ("sfx_" if src == "dragons" else "infernal_sfx_")
    else:
        w = Wad(os.path.join(final, "Champions", f"{src}.wad.client"))
        stem = f"assets/sounds/wwise2016/sfx/characters/{src.lower()}/skins/base/{src.lower()}_base_sfx_"
    audio = w.read_path(stem + "audio.bnk")
    media = dict(bnk_media(audio))
    if w.has(stem + "audio.wpk"):
        media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
    cache[src] = SoundBanks([w.read_path(stem + "events.bnk"), audio], media)
    return cache[src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22, Map11, the champions)")
    ap.add_argument("--vgmstream", required=True, help="vgmstream-cli.exe")
    a = ap.parse_args()
    out_dir = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out_dir), exist_ok=True)
    cache = {}
    for name, (src, events, max_s, peak, *pick) in CLIPS.items():
        banks = banks_of(src, a, cache)
        event, variants = None, []
        for ev in events:
            variants = banks.event_media(ev)
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
        print(f"{name:26s} {len(pcm) / sr:4.2f}s  <- {src} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
