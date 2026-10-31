r"""Pull the Murk Wolf's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_murkwolf.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). Set 18 (DA_Murkwolf18) names no event and the client ships no set-18
bank; its skin bin borrows the Rift's SRU_Murkwolf, so its voice is the Rift's own Greater Murk Wolf and its two pups:
Map11's NPC_Map11_Murkwolf_SFX and NPC_Map11_MurkwolfMini_SFX. Named by guessing (fnv1, 2026-11-01): spawn_Cast,
death_Cast, aggro3_buffactivate, idle2/idle3_buffactivate; the rest are unnamed and picked by event id, read by their
sound (C:/t/mw_work snd.py: duration, spectral centroid, onsets, pitch strength): 1953482361 = three short bright
swipes (its bite), 2598502185 = a 2.75 s strongly pitched call (the howl's own voice).
The rest is League's champions', Champions/<name>.wad.client: Warwick (a wolf's bite, the leap's landing, Primal Howl,
the blood-drinking bite), Rengar (the leap, the empowered and the critical bites) and Naafiri (her packmates' pounce and
bite: the pups).
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
C = "tft_murkwolf_sfx_"
W = "Play_sfx_SRU_Murkwolf_"
M = "Play_sfx_SRU_MurkwolfMini_"
WW = "Play_sfx_Warwick_Warwick"
RG = "Play_sfx_Rengar_Rengar"
NF = "Play_sfx_Naafiri_"
SWIPE = 1953482361      # wolf bank: three short bright swipes
CALL = 2598502185       # wolf bank: a 2.75 s strongly pitched call

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("wolf", [SWIPE], 0.7, -11, 0),                                   # the twin bite
    C + "a_hit": ("Warwick", [WW + "BasicAttack_OnHit"], 0.8, -13),
    C + "p": ("Rengar", [RG + "CritAttack_OnHit"], 0.6, -10),                   # Gray Buff: a critical bite
    C + "q": ("Rengar", [RG + "P_cast"], 0.6, -10),                             # Rending Claws: the leap
    C + "q_vo": ("wolf", [W + "aggro3_buffactivate"], 1.4, -8),
    C + "q_hit": ("Warwick", [WW + "Q_OnHit"], 1.0, -11),
    C + "q_emp": ("Rengar", [RG + "QEmpAttack_OnHit"], 0.65, -10),              # the empowered bites after it
    C + "e": ("Warwick", [WW + "E2_OnBuffActivate"], 2.0, -10),                 # the Slayer's howl
    C + "e_vo": ("wolf", [CALL], 2.2, -8),
    C + "e_hit": ("Warwick", [WW + "BasicAttackPassive2_OnHit", WW + "BasicAttackPassive1_OnHit"], 0.9, -13),    # a blood-drinking bite
    C + "r": ("wolfmini", [M + "spawn_Cast"], 1.8, -9),                         # Pack Attack: the pups come
    C + "r_vo": ("wolf", [W + "idle3_buffactivate"], 2.4, -8),
    C + "r_leap": ("Naafiri", [NF + "PackmatePounce_Qhit_cast"], 0.9, -13),
    C + "r_bite": ("Naafiri", [NF + "PackmateBasicAttack_OnHit"], 0.6, -15),
    C + "r_end": ("wolfmini", [M + "death_Cast"], 1.3, -11),                    # the pups go
    C + "d": ("wolf", [W + "death_Cast"], 1.6, -8),
}
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: wolf / wolfmini = Map11's Murk Wolves, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src in ("wolf", "wolfmini"):
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client"))
        stem = MAP11 + ("murkwolf_sfx_" if src == "wolf" else "murkwolfmini_sfx_")
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
