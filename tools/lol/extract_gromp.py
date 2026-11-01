r"""Pull Gromp's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_gromp.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). Set 18 (DA_Gromp18_AP) names no event and the client ships no set-18
bank; its skin bin borrows the Rift's SRU_Gromp, so its voice is the Rift's own Gromp: Map11's NPC_Map11_Gromp_SFX.
Named by guessing (fnv1, 2026-11-01): spawn_cast, death_cast, aggro2/aggro3_buffactivate, idle2/idle3_buffactivate; the
rest are unnamed and picked by event id, read by their spectrograms (C:/t/gp_work spec.py): 293961550 = a short wet
burst (its spit), 1675042177 = a splash decaying over ~1 s (3 variants), 1113834141 = a ~2 s rattling croak
(4 variants), 1121474553 = a deep thump with a long tail (the belly).
The rest is League's champions', Champions/<name>.wad.client: Kog'Maw (Caustic Spittle, Void Ooze: a spat bubble and
a slowing slime trail), Twitch (the Venom Cask bursting), Cassiopeia (the poison ticks, the Miasma cloud) and Singed
(Mega Adhesive: the sticky slow).
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
C = "tft_gromp_sfx_"
G = "Play_sfx_SRU_Gromp_"
KM = "Play_sfx_KogMaw_KogMaw"
CA = "Play_sfx_Cassiopeia_Cassiopeia"
SPIT = 293961550        # gromp bank: a short wet burst
SPLASH = 1675042177     # gromp bank: a splash decaying over ~1 s
CROAK = 1113834141      # gromp bank: a ~2 s rattling croak
THUMP = 1121474553      # gromp bank: a deep thump with a long tail

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("gromp", [SPIT], 0.7, -11),                                     # the spit
    C + "a_hit": ("gromp", [SPLASH], 0.8, -14),
    C + "p": ("KogMaw", [KM + "CausticSpittleCharged_OnBuffActivate"], 1.0, -14),   # Purple Buff: a stack of power
    C + "q": ("KogMaw", [KM + "Q_OnCast"], 0.8, -10),                         # Belchy Bubble: the bubble spat
    C + "q_vo": ("gromp", [G + "aggro2_buffactivate"], 0.8, -9),
    C + "q_hit": ("Twitch", ["Play_sfx_Twitch_TwitchVenomCaskMissile_OnHitLocation"], 1.2, -10),   # it bursts
    C + "q_dot": ("Cassiopeia", [CA + "Q_tick"], 0.5, -16),                   # the poison ticking
    C + "e": ("KogMaw", [KM + "VoidOoze_OnCast"], 1.0, -10),                 # Slime Swamp: the slime spat
    C + "e_vo": ("gromp", [CROAK], 1.6, -10, 3),
    C + "e_hit": ("KogMaw", [KM + "VoidOozeMissile_hit"], 1.0, -11),         # the puddle splats down
    C + "e_slow": ("Singed", ["Play_sfx_Singed_MegaAdhesive_OnBuffActivate"], 1.2, -14),   # stuck in it
    C + "r": ("gromp", [THUMP], 1.6, -8),                                     # Swamp Belch: the belly swells
    C + "r_vo": ("gromp", [G + "aggro3_buffactivate"], 2.4, -8),             # the big croak / belch
    C + "r_cloud": ("Cassiopeia", [CA + "W_OnCast"], 1.8, -10),               # the poison cloud spreads
    C + "r_tick": ("Cassiopeia", [CA + "W_hit"], 0.6, -16),
    C + "d": ("gromp", [G + "death_cast"], 1.8, -8),
}
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: gromp = Map11's Gromp, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src == "gromp":
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client"))
        stem = MAP11 + "gromp_sfx_"
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
