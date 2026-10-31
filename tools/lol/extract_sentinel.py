r"""Pull the Blue Sentinel's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_sentinel.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). Set 18 (DA_Sentinel18) names no event and the client ships no set-18 bank
(as for the Krug); its skin bin borrows the Rift's SRU_Blue, so its voice is the Rift's own Blue Sentinel: Map11's
NPC_Map11_Blue_SFX banks. Named by guessing their hashes (2026-10-31): Aggro1-3 (the roars), Death_cast, Spawn_cast (it
rises from the ground and slams it); the fist swings and their hits answer to no guessed name, so they are picked by
their event id (read by their loudness: a wind-up then the slam, or a hit at once).
The rest is League's other stone / rune champions, Champions/<name>.wad.client: Malphite's Ground Slam (Q) and Granite
Shield, Rammus's taunt, Ornn's Volcanic Rupture (the fissure), Sona's Song of Celerity (the Blue Buff on allies) and
Ryze's Rune Prison (Mana Reave).
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
C = "tft_sentinel_sfx_"
B = "Play_sfx_SRU_Blue_"
SWING = 1194156411   # Map11 Blue: a fist wound up and slammed (5 variants; the 5th is the shortest swing)
FIST_HIT = 3497640   # Map11 Blue: a stone fist landing (2 variants)

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("blue", [SWING], 1.0, -11, 4),
    C + "a_hit": ("blue", [FIST_HIT], 0.8, -9),
    C + "p": ("Sona", ["Play_sfx_Sona_SonaE_OnCast"], 1.2, -13),                      # Blue Buff on the allies
    C + "q": ("Malphite", ["Play_sfx_Malphite_Landslide_OnCast"], 1.2, -8),           # both fists into the ground
    C + "q_hit": ("Malphite", ["Play_sfx_Malphite_Landslide_hit"], 0.8, -11),
    C + "e": ("Malphite", ["Play_sfx_Malphite_MalphiteShieldEffect_OnBuffActivate"], 1.2, -10),   # the carved skin
    C + "e_taunt": ("Rammus", ["Play_sfx_Rammus_PuncturingTaunt_OnCast"], 1.2, -9),
    C + "r": ("blue", [B + "Spawn_cast"], 2.2, -6),                                   # the slam that wakes it
    C + "r_vo": ("blue", [B + "Aggro1"], 2.4, -6),                                    # its roar
    C + "r_shield": ("Malphite", ["Play_sfx_Malphite_Obduracy_OnCast"], 1.0, -10),
    C + "r_crack": ("Ornn", ["Play_sfx_Ornn_OrnnQ_OnMissileLaunch"], 1.4, -9),       # the fissure runs
    C + "r_hit": ("Ornn", ["Play_sfx_Ornn_OrnnEKnockUp_OnBuffActivate"], 1.0, -11),   # knocked up
    C + "r_reave": ("Ryze", ["Play_sfx_Ryze_RyzeW_hit"], 1.0, -12),                  # Mana Reave
    C + "d": ("blue", [B + "Death_cast"], 3.0, -7),
}
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_blue_sfx_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: blue = Map11's Blue Sentinel, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src == "blue":
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
