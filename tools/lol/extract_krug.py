r"""Pull the Ancient Krug's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_krug.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

His own sounds (the user: 「音效什么都要自己找」). Set 18 (DA_Krug18) names no event and the client ships no set-18 bank
(as for Alune), so his voice is the Rift's own Krug: Map11's NPC_Map11_Krug_SFX banks, which sru_krug's skin bin
links (its stone fists, the death crumble, the spawn roar; names found from the bank's event hashes, 2026-10-28).
The rest is League's other rolling / rock champions, Champions/<name>.wad.client: Rammus's Powerball (the roll and its
hit), Defensive Ball Curl (the shell) and Frenzying Taunt; Malphite's Granite Shield (the stone layer), Unstoppable
Force (the leap and the landing) and Seismic Shard (the falling rocks). A monster: no voice line.
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
C = "tft_krug_sfx_"
K = "Play_sfx_SRU_Krug"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("krug", [K + "BasicAttack_OnCast"], 0.7, -11),
    C + "a_hit": ("krug", [K + "BasicAttack_OnHit"], 0.7, -9),
    C + "p": ("krug", [K + "_Death_cast"], 1.6, -7),                          # shatters
    C + "p_up": ("krug", [K + "_Spawn_cast"], 1.6, -8),                       # reforms, roaring
    C + "q": ("Rammus", ["Play_sfx_Rammus_PowerBall_OnBuffActivate"], 1.4, -9),   # curls up and rolls
    C + "q_shield": ("Malphite", ["Play_sfx_Malphite_Obduracy_OnCast"], 1.0, -10),
    C + "q_hit": ("Rammus", ["Play_sfx_Rammus_PowerBall_hit"], 1.0, -7),
    C + "e": ("Rammus", ["Play_sfx_Rammus_DefensiveBallCurl_OnCast"], 1.0, -9),   # the shell
    C + "e_taunt": ("Rammus", ["Play_sfx_Rammus_PuncturingTaunt_OnCast"], 1.2, -9),
    C + "r": ("Malphite", ["Play_sfx_Malphite_UFSlash_OnCast"], 1.2, -8),         # the leap
    C + "r_slam": ("Malphite", ["Play_sfx_Malphite_UFSlash_land"], 1.6, -5),
    C + "r_hit": ("Rammus", ["Play_sfx_Rammus_RammusRKnockup_hit"], 1.0, -8),
    C + "r_rocks": ("Malphite", ["Play_sfx_Malphite_SeismicShard_OnHit"], 1.0, -9),  # the falling rocks
}
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_krug_sfx_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: krug = Map11's Krug, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src == "krug":
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map11, Rammus, Malphite)")
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
        sr, x = decode(banks.media[variants[pick[0] if pick else 0]], a.vgmstream)
        pcm = finish(x, sr, max_s, peak)
        with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        print(f"{name:26s} {len(pcm) / sr:4.2f}s  <- {src} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
