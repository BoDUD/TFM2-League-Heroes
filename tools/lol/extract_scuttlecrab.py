r"""Pull the Scuttle Crab's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_scuttlecrab.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). TFT ships nothing of its own for set 18's DA_Scuttlecrab18 (no skin or
animation bin, 2026-11-01), so the crab is League's river Scuttle Crab: Map11.wad.client's shared NPC_Map11_Crab_SFX banks
(its dance, its speed shrine, its shield breaking, the stun, rising out of the ground, its death; event names from
data/characters/sru_crab/skins/skin0.bin). The rest from champions that do the same thing: Rek'Sai burrowing, healing under
the ground (her passive) and bursting up into a knock-up; Rammus curling into his shell and his shell's bump; Soraka's heal
for the Green Buff; Sona's haste for the shrine's allies.
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
C = "tft_scuttlecrab_sfx_"
CR = "Play_sfx_SRU_Crab"
RS = "Play_sfx_Reksai_"
RM = "Play_sfx_Rammus_"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("crab", [CR + "_Sru_Dance"], 1.0, -10),                      # the dance
    C + "a_hit": ("Rammus", [RM + "RammusBasicAttack_OnHit"], 0.6, -10),   # a shell bump on everyone next to it
    C + "p": ("Soraka", ["Play_sfx_Soraka_SorakaW_OnCast"], 1.2, -11),    # the Green Buff heals an ally
    C + "q": ("crab", [CR + "SpeedShrine_buffactivate"], 1.4, -9),         # the speed shrine at its feet
    C + "q_buff": ("Sona", ["Play_sfx_Sona_SonaEHaste_buffactivate"], 0.9, -13),   # an ally hasted in it
    C + "e": ("Rammus", [RM + "DefensiveBallCurl_OnCast"], 0.9, -9),       # curls into the shell
    C + "e_break": ("crab", [CR + "_shieldbreak_cast"], 1.0, -8),          # the shell breaks
    C + "e_slow": ("crab", [CR + "_stun"], 0.8, -11),                      # the shards slow
    C + "r": ("RekSai", [RS + "RekSaiW_buffactivate"], 1.2, -8),   # digs in
    C + "r_heal": ("RekSai", [RS + "RekSaiPRegen_OnBuffActivate"], 1.2, -12),   # heals under the ground
    C + "r_up": ("crab", [CR + "_spawn_cast"], 1.4, -8),                   # climbs out
    C + "r_hit": ("RekSai", [RS + "RekSaiW_hit"], 1.0, -7),  # the knock-up
    C + "d": ("crab", [CR + "_death_cast"], 1.5, -9),
}


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: crab = Map11's shared Scuttle Crab banks, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src == "crab":
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client"))
        stem = "assets/sounds/wwise2016/sfx/shared/npc_map11_crab_sfx_"
        audio = w.read_path(stem + "audio.bnk")
        cache[src] = SoundBanks([w.read_path(stem + "events.bnk"), audio], dict(bnk_media(audio)))
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
