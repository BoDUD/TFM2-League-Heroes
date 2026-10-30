r"""Pull Daeja's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_daeja.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

His own sounds (the user: 「音效什么都要自己找」). Set 7 (TFT7_DragonBlue) names four events in his skin bin and Map22 still
holds them in the set-7 champions bank (the one Nomsy's sounds come from): Windblast's cast, launch and hit
(Q_cast / Q_launch / Q_hit; found 2026-10-30). His bins name no attack, wing or death sound, so the rest is borrowed:
Janna for the wind (the wind bolt of his attack, Zephyr's slowing gust for E, Howling Gale's charge as he rises for R),
Ezreal for the barrages (his TFT ability icon is Ezreal's Mystic Shot and his particles reuse Ezreal's Q missiles:
the passive's three bolts, Trueshot Barrage for R's big blasts) and the Rift's drakes in Map11 (the wing beat, the
roar, the landing, the death).
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
C = "tft_daeja_sfx_"
B = "Play_sfx_tft7_DragonBlue_"
D = "Play_sfx_SRU_Dragon_"
EZ = "Play_sfx_Ezreal_Ezreal"
JA = "Play_sfx_Janna_"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("Janna", [JA + "JannaBasicAttack_OnCast"], 0.7, -11),             # the wind bolt from his fist
    C + "a_hit": ("Janna", [JA + "JannaBasicAttack_OnHit"], 0.7, -11),
    C + "p": ("Ezreal", [EZ + "Q_OnMissileLaunch", EZ + "Q_OnCast"], 0.6, -13),  # the three barrages
    C + "p_hit": ("Ezreal", [EZ + "Q_OnHit"], 0.6, -13),
    C + "q": ("tft7", [B + "Q_cast"], 1.4, -8),                                 # Windblast: the wings sweep
    C + "q_launch": ("tft7", [B + "Q_launch"], 1.4, -8),
    C + "q_hit": ("tft7", [B + "Q_hit"], 1.0, -9),
    C + "e": ("dragons", [D + "DragonTakeOff_cast"], 1.0, -9),                 # the wing beat, the hop back
    C + "e_wind": ("Janna", [JA + "SowTheWind_OnMissileLaunch"], 1.0, -10),     # the slowing gust
    C + "e_slow": ("Janna", [JA + "SowTheWind_OnHit"], 0.8, -11),
    C + "r": ("Janna", [JA + "HowlingGale_charge"], 1.6, -9),                  # wings out, up he goes
    C + "r_roar": ("dragons", [D + "aggro3_buffactive", D + "aggro2_buffactive"], 1.8, -6),
    C + "r_blast": ("Ezreal", [EZ + "R_OnMissileLaunch", EZ + "R_OnCast"], 1.4, -8),   # one of the three big blasts
    C + "r_hit": ("Ezreal", [EZ + "R_OnHit"], 1.0, -8),
    C + "r_land": ("dragons", [D + "landing_buffactive"], 1.2, -8),
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
