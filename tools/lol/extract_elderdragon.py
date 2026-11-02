r"""Pull the Elder Dragon's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_elderdragon.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). Set 18 (DA_18_ElderDragon) names no event and the client ships no set-18
bank; its skin bin borrows the Rift's sru_dragon_elder, so its voice is the Rift's own Elder Dragon: Map11's
NPC_Map11_Dragons_Elder_SFX (its own bank, every event unnamed) and the drakes' shared NPC_Map11_Dragons_SFX (take-off,
landing, aggro roars, spawn, death - named by guessing, as Ao Shin's and Daeja's). The Elder bank's events are picked by
event id, read by their sound (2026-11-01, C:/t/ed_work snd5.py: duration, spectral flatness, low-band share, onsets,
pitch strength): 3900284606 = six short roar-whooshes (its attack), 2646778143 = three noisy bursts with no tail (a fire
blast landing), 3357920976 = the drakes' ~1.5-2.5 s fire roar (the breath), 2983700658 = four strongly pitched growls (its
cry), 3133625017 v2-3 = high sustained shimmering tones (the Elder buff), and the shared bank's unnamed 1628668882 = three
short heavy low thumps (a bite landing).
The rest is League's champions', Champions/<name>.wad.client: Brand's Blaze mark (the Ignite catching), Janna's Zephyr hit
(the wing gust striking), Malphite's Unstoppable Force landing (the ult's slam).
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
C = "tft_elderdragon_sfx_"
D = "Play_sfx_SRU_Dragon_"
ATTACK = 3900284606     # Elder bank: six short roar-whooshes
BLAST = 2646778143      # Elder bank: three noisy bursts, no tail
BREATH = 3357920976     # Elder bank: the fire roar (the shared bank's 1532049892 media)
CRY = 2983700658        # Elder bank: four pitched growls
BUFF = 3133625017       # Elder bank: v2-3 high shimmering tones
THUMP = 1628668882      # shared bank: three short heavy low thumps

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("elder", [ATTACK], 1.0, -10, 1),                                   # the bite's roar
    C + "a_hit": ("dragons", [THUMP], 0.7, -9, 1),                               # the jaws land
    C + "p": ("elder", [BUFF], 1.4, -9, 2),                                      # the Elder buff: an execute
    C + "q": ("elder", [BREATH], 1.8, -7, 1),                                    # the Flame Breath
    C + "q_vo": ("elder", [CRY], 1.2, -8, 0),
    C + "q_hit": ("elder", [BLAST], 0.9, -10, 0),
    C + "burn": ("Brand", ["Play_sfx_Brand_P_firemark1_loop", "Play_sfx_Brand_P_firemark1_loop1"], 0.8, -13),   # Ignite
    C + "e": ("dragons", [D + "DragonTakeOff_cast"], 1.2, -8, 0),                # the wing buffet
    C + "e_vo": ("dragons", [D + "aggro3_buffactive", D + "aggro1_buffactive"], 1.4, -7),
    C + "e_hit": ("Janna", ["Play_sfx_Janna_SowTheWind_OnHit"], 0.8, -11),       # the gust strikes
    C + "r": ("dragons", [D + "DragonTakeOff_cast"], 1.5, -7, 2),                # up into the sky
    C + "r_vo": ("dragons", [D + "Spawn_cast"], 2.2, -5),                        # its great roar
    C + "r_land": ("dragons", [D + "landing_buffactive"], 1.5, -6),
    C + "r_slam": ("Malphite", ["Play_sfx_Malphite_UFSlash_land", "Play_sfx_Malphite_UFSlash_hit"], 1.2, -8),
    C + "d": ("dragons", [D + "Death_cast"], 2.4, -6, 1),                        # sinks and falls
}
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_dragons_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: elder / dragons = Map11's dragons, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src in ("elder", "dragons"):
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client"))
        stem = MAP11 + ("elder_sfx_" if src == "elder" else "sfx_")
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
