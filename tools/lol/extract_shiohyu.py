r"""Pull Shi Oh Yu's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_shiohyu.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

His own sounds (the user: 「音效什么都要自己找」). Set 7 (TFT7_DragonGreen) names one event in his skin bin
(Play_sfx_tft7_DragonGreenAttack1_windup) and Map22's set-7 champions bank (the one Nomsy's and Daeja's come from) holds
his whole attack family under that spelling (no underscore after the name; found 2026-10-30): BasicAttack, Attack1-3
and CritAttack, each _OnCast / _OnHit - the three claw swipes, Jade Form's three empowered blows. Nothing for Jade Form
itself, so the rest is borrowed: Malphite for stone (Granite Shield's stone skin for the passive, Ground Slam for E),
Lee Sin for the fist rush (Resonating Strike's dash), Taric for jade (Cosmic Radiance as the stance comes on, Dazzle's
stunning line for the third blow's wave) and the Rift's drakes in Map11 (the roar, the death).
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
C = "tft_shiohyu_sfx_"
G = "Play_sfx_tft7_DragonGreen"
D = "Play_sfx_SRU_Dragon_"
MA = "Play_sfx_Malphite_"
LE = "Play_sfx_LeeSin_LeeSin"
TA = "Play_sfx_Taric_Taric"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft7", [G + "BasicAttack_OnCast"], 0.8, -10),                    # the claw swipes (three variants)
    C + "a_hit": ("tft7", [G + "BasicAttack_OnHit"], 0.7, -10),
    C + "p": ("Malphite", [MA + "MalphiteShieldEffect_OnBuffActivate"], 1.2, -9),  # stone skin
    C + "q": ("LeeSin", [LE + "QTwo_OnCast"], 0.9, -9),                         # the rush to the target
    C + "q_punch": ("tft7", [G + "CritAttack_OnCast"], 0.7, -9),                # the fist flurry
    C + "q_hit": ("tft7", [G + "CritAttack_OnHit"], 0.7, -9),
    C + "e": ("Malphite", [MA + "Landslide_OnCast"], 1.4, -8),                  # the fist into the ground
    C + "e_hit": ("Malphite", [MA + "Landslide_hit"], 1.0, -9),
    C + "r": ("Taric", [TA + "R_OnCast"], 1.8, -8),                             # Jade Form comes on
    C + "r_roar": ("dragons", [D + "aggro3_buffactive", D + "aggro2_buffactive"], 1.8, -6),
    C + "r1": ("tft7", [G + "Attack1_OnCast"], 0.8, -9),                        # blow 1: the stun
    C + "r1_hit": ("tft7", [G + "Attack1_OnHit"], 0.8, -8),
    C + "r2": ("tft7", [G + "Attack2_OnCast"], 0.8, -9),                        # blow 2: true damage
    C + "r2_hit": ("tft7", [G + "Attack2_OnHit"], 0.8, -8),
    C + "r3": ("tft7", [G + "Attack3_OnCast"], 0.9, -8),                        # blow 3: the jade wave
    C + "r3_wave": ("Taric", [TA + "E_cast"], 1.2, -8),
    C + "r3_hit": ("Taric", [TA + "E_hit"], 0.9, -8),
    C + "d": ("dragons", [D + "death_cast"], 2.0, -7, 1),                       # he falls
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
