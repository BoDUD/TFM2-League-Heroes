r"""Pull Nomsy's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_nomsy.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Her own sounds (the user: 「音效什么都要自己找」). Set 7 (TFT7_Nomsy) names her events in her bins (skin0.bin's particles,
animations/skin0.bin) and Map22 still holds them: a set-7 champions events bank (path hash 5148408258298239144, 846
events, no path known) with its media in the audio bank 13347058717425747428 - her attack, the big fireball's launch and
hit, the small bouncing fireballs' launch and hit and her two lines (fireball_charge / fireball_cast, in the sfx bank;
found 2026-10-29). The rest is the Rift's and League's fire dragons: Map11's Infernal Drake (sru_dragon_fire's skin bin
links NPC_Map11_Dragons_Infernal_SFX and the shared NPC_Map11_Dragons_SFX: the take-off and the landing for the ult, its
fireballs for the rain), Smolder (her little fire bolt's hit, the ult's roar, her death), Shyvana's dragon-form Burnout
heal for the passive and Annie's Incinerate for the breath, Brand's Blaze for its burn.
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
C = "tft_nomsy_sfx_"
N = "Play_sfx_tft7_Nomsy_"
D = "Play_sfx_SRU_Dragon_"
SM = "Play_sfx_Smolder_"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft7", [N + "BasicAttack_cast"], 0.7, -11),                     # her little fire bolt
    C + "a_hit": ("Smolder", [SM + "SmolderBasicAttack_OnHit", SM + "SmolderBasicAttack_OnHit1"], 0.6, -11),
    C + "p": ("Shyvana", ["Play_sfx_Shyvana_ShyvanaDragonW_heal"], 1.0, -12),   # the dragon's body mends
    C + "q": ("tft7", [N + "fireball_launch"], 1.0, -9),                       # Fireballs!
    C + "q_vo": ("tft7", ["Play_vo_tft7_Nomsy_fireball_cast"], 1.6, -5),
    C + "q_hit": ("tft7", [N + "fireball_hit"], 1.2, -8),
    C + "q_bounce": ("tft7", [N + "fireball_small_launch"], 0.8, -11),           # the small ones bounce on
    C + "q_bounce_hit": ("tft7", [N + "fireball_small_hit"], 0.8, -10),
    C + "e": ("Annie", ["Play_sfx_Annie_AnnieW_OnCast"], 1.2, -9),               # the breath
    C + "e_hit": ("Annie", ["Play_sfx_Annie_AnnieW_hit"], 0.8, -11),
    C + "e_burn": ("Brand", ["Play_sfx_Brand_P_firemark1_loop1", "Play_sfx_Brand_P_firemark1_loop"], 1.0, -13),
    C + "r": ("dragons", [D + "DragonTakeOff_cast"], 1.4, -8),                  # wings out, up she goes
    C + "r_vo": ("tft7", ["Play_vo_tft7_Nomsy_fireball_charge"], 1.6, -5),
    C + "r_roar": ("Smolder", [SM + "SmolderR_roar"], 1.6, -7),
    C + "r_rain": ("infernal", [D + "Infernal_Attack_OnMissileLaunch"], 0.9, -10),  # one fireball of the rain
    C + "r_hit": ("dragons", [D + "DragonFireball_hit"], 1.0, -9),
    C + "r_land": ("dragons", [D + "landing_buffactive"], 1.2, -8),
    C + "r_up": ("Smolder", [SM + "SmolderQ_EvolveCeremony1_buffactivate", SM + "SmolderQ_EvolveCeremony1_buffactivate6"], 1.4, -10),   # ascended: AS and AP up
    C + "d": ("Smolder", [SM + "Death3D_cast", SM + "Death3D_cas"], 1.6, -8),
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
