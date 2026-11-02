r"""Pull the Crimson Raptor's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_raptor.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). Set 18 (DA_CrimsonRaptor18) names no event and the client ships no set-18
bank; its skin bin borrows the Rift's SRU_Razorbeak, so its voice is the Rift's own raptors: Map11's NPC_Map11_Razorbeak_SFX
(the big one = Mama) and NPC_Map11_RazorbeakMini_SFX (the little ones = the R's Tiny Beaks). Named by guessing their hashes
(2026-10-31): Spawn_cast, Death_cast, n2a / a2n_buffactivate, and the minis' SRU_RazorbeakMiniBasicAttack_OnCast / _OnHit
and Spawn2-4_cast; the big one's feather shot answers to no guessed name, so it is picked by event id, read by its sound
(2026-10-31, C:/t/rp_work snd.py): 3812101906 = three noisy ~1 s whooshes (the feather thrown), 3961990197 = two short
noisy hits, 4253603741 = the whooshes plus three tonal ~2.3 kHz screeches (its call).
The rest is League's other bird / feather champions, Champions/<name>.wad.client: Xayah's feathers (Q fan), Quinn and
Valor (the hop back, the attack-speed rush), Vayne's Tumble, Jarvan IV's Dragon Strike (armour shred).
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
C = "tft_raptor_sfx_"
B = "Play_sfx_SRU_Razorbeak_"
M = "Play_sfx_SRU_RazorbeakMini_"
SHOT = 3812101906    # Map11 Razorbeak: a feather thrown (3 noisy whooshes, 0.9-1.1 s)
SHOT_HIT = 3961990197   # Map11 Razorbeak: the feather landing (2 short hits)
CALL = 4253603741    # Map11 Razorbeak: whooshes + its screeches (variants 0-2 tonal ~2.3 kHz)

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("beak", [SHOT], 0.9, -11, 2),
    C + "a_hit": ("beak", [SHOT_HIT], 0.6, -10),
    C + "p": ("JarvanIV", ["Play_sfx_JarvanIV_JarvanIVDragonStrike_hit"], 0.8, -14),   # Orange Buff: armour cracked
    C + "q": ("Xayah", ["Play_sfx_Xayah_XayahQ_OnCast"], 1.2, -9),                    # five feathers in a fan
    C + "q_vo": ("beak", [CALL], 1.2, -10, 0),                                        # its screech
    C + "q_hit": ("Xayah", ["Play_sfx_Xayah_XayahPassiveAttack_OnHit"], 0.8, -12),
    C + "e": ("Vayne", ["Play_sfx_Vayne_VayneTumble_OnCast"], 1.0, -10),               # the hop back
    C + "e_vo": ("beak", [B + "n2a_buffactivate"], 1.3, -9),                          # startled
    C + "e_rush": ("Quinn", ["Play_sfx_Quinn_QuinnW_OnCast"], 1.2, -12),
    C + "r": ("beak", [CALL], 1.6, -7, 2),                                            # the call for the flock
    C + "r_chick": ("mini", [M + "Spawn2_cast"], 0.9, -9),                            # the Tiny Beaks arrive
    C + "r_peck": ("mini", [M + "SRU_RazorbeakMiniBasicAttack_OnCast"], 0.6, -13),
    C + "r_peck_hit": ("mini", [M + "SRU_RazorbeakMiniBasicAttack_OnHit"], 0.7, -14, 1),
    C + "r_end": ("mini", [M + "Death_cast"], 0.8, -13),                              # they fly off
    C + "d": ("beak", [B + "Death_cast"], 1.8, -7),
}
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_{}_sfx_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: beak / mini = Map11's raptors, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src in ("beak", "mini"):
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client"))
        stem = MAP11.format("razorbeak" if src == "beak" else "razorbeakmini")
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
