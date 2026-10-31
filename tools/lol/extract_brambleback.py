r"""Pull the Crimson Brambleback's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_brambleback.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). Set 18 (DA_Brambleback18) names no event and the client ships no set-18
bank (as for the Krug and the Sentinel); its skin bin borrows the Rift's SRU_Red, so its voice is the Rift's own Red
Brambleback: Map11's NPC_Map11_Red_SFX banks. Named by guessing their hashes (2026-10-31): Spawn_cast, Death_cast,
n2a_buffactivate (its animation bin names it; only the death is used); the claw swings, their hits and the roars answer to no guessed name, so
they are picked by their event id (read by their length and loudness: a swing ~1 s, a hit ~0.7 s with a sharp attack, a
roar ~2 s; the 2589636900 roar swells to its peak at 1 s).
The rest is League's other beasts and fire, Champions/<name>.wad.client: Warwick's Jaws of the Beast (the leap) and
Primal Howl (the guard), Rengar's Savagery (the leap on to the next), Brand's burning hit (Red Buff's burn; its heal plays no sound, every claw heals) and Ablaze
(the fury's fire), Nasus's Wither (the roar's slow) and Fury of the Sands (Crimson Fury).
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
C = "tft_brambleback_sfx_"
B = "Play_sfx_SRU_Red_"
SWING = 455574750    # Map11 Red: a claw swung (5 variants: three swings ~1 s, then two longer grunts)
CLAW_HIT = 2226943004   # Map11 Red: a claw landing (3 variants, ~0.7 s, sharp attack)
ROAR = 3747811588    # Map11 Red: a roar (3 variants, ~2 s, loud at once)
ROAR_SWELL = 2589636900   # Map11 Red: a roar that swells to its peak at 1 s (2 variants)

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("red", [SWING], 1.0, -11),
    C + "a_hit": ("red", [CLAW_HIT], 0.7, -9),
    C + "p": ("Brand", ["Play_sfx_Brand_BrandBasicAttack_OnHit"], 0.8, -14),           # Red Buff: the burn
    C + "q": ("Warwick", ["Play_sfx_Warwick_WarwickQ_OnCast"], 1.0, -9),               # the leap
    C + "q_hit": ("Warwick", ["Play_sfx_Warwick_WarwickQ_OnHit"], 0.9, -9),
    C + "q_next": ("Rengar", ["Play_sfx_Rengar_RengarQ_OnCast"], 1.0, -10),           # on to the next target
    C + "e": ("red", [ROAR], 2.0, -6),                                                 # its roar
    C + "e_guard": ("Warwick", ["Play_sfx_Warwick_WarwickE_OnCast"], 1.2, -11),        # the guard
    C + "e_slow": ("Nasus", ["Play_sfx_Nasus_NasusW_OnCast"], 1.0, -12),
    C + "r": ("Nasus", ["Play_sfx_Nasus_NasusR_OnCast"], 2.0, -8),                     # Crimson Fury
    C + "r_vo": ("red", [ROAR_SWELL], 2.1, -6),
    C + "r_fire": ("Brand", ["Play_sfx_Brand_BrandW_buffactivate"], 1.2, -12),
    C + "d": ("red", [B + "Death_cast"], 2.6, -7),
}
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_red_sfx_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: red = Map11's Red Brambleback, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src == "red":
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client"))
        stem = MAP11
    else:
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
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map11 and the champions)")
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
        sr, x = decode(banks.media[variants[pick[0] if pick else 0]], a.vgmstream)
        pcm = finish(x, sr, max_s, peak)
        with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        print(f"{name:28s} {len(pcm) / sr:4.2f}s  <- {src} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
