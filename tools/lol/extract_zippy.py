r"""Pull Zippy's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_zippy.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). Set 7 (TFT7_DragonGuild) names its events in its skin and animation
bins and Map22's set-7 champions bank holds them under that spelling (found 2026-10-31): Attack1_OnCast / _OnHit (the
backflip kick), CritAttack_OnCast / _OnHit, RDash_cast / _hit (the leap), R_spell4_cycle (three variants) and
R_spell4_loop (the ball roll), RChargeAllySpeedBuff_buffactivate, WActive_buffactivate (two variants) and its voice
Play_vo_tft7_DragonGuildSpell_OnCast (two variants) - Kled's mount's sounds renamed. What it has none of is borrowed
from Kled himself (Skaarl): his E dash hit for the roll, his R charge shield for the leap's shield, his remount crash
for the landing; and the Rift's Razorbeak death.
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
C = "tft_zippy_sfx_"
G = "Play_sfx_tft7_DragonGuild"
V = "Play_vo_tft7_DragonGuild"
K = "Play_sfx_Kled_Kled"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft7", [G + "CritAttack_OnCast"], 0.7, -11),                      # Claw Kick
    C + "a_hit": ("tft7", [G + "CritAttack_OnHit"], 0.7, -11, 0),
    C + "p": ("tft7", [G + "WActive_buffactivate"], 1.0, -12, 0),                # Adventurer's Spirit
    C + "q": ("tft7", [G + "Attack1_OnCast"], 0.9, -9),                          # the backflip kick
    C + "q_hit": ("tft7", [G + "Attack1_OnHit"], 0.8, -9, 1),
    C + "e": ("tft7", [G + "R_spell4_cycle"], 0.9, -9, 0),                       # curls up and rolls
    C + "e_roll": ("tft7", [G + "R_spell4_loop"], 1.2, -10),
    C + "e_hit": ("Kled", [K + "EDash_hit"], 0.7, -9),
    C + "e_speed": ("tft7", [G + "RChargeAllySpeedBuff_buffactivate"], 1.0, -11),
    C + "r": ("tft7", [G + "RDash_cast"], 1.2, -8),                             # the leap
    C + "r_vo": ("tft7", [V + "Spell_OnCast"], 1.4, -8, 0),
    C + "r_shield": ("Kled", [K + "RChargeShield_buffactivate"], 1.0, -10),
    C + "r_spin": ("tft7", [G + "R_spell4_cycle"], 0.9, -9, 1),                  # the somersault in the air
    C + "r_hit": ("tft7", [G + "RDash_hit"], 1.0, -7),                           # the crash: stun + knockback
    C + "r_land": ("Kled", [K + "ReMountDash_explosion", K + "RemounttDash_explosion", K + "DismountDash_OnBuffCast"], 1.0, -9),
    C + "d": ("razorbeak", ["Play_sfx_SRU_Razorbeak_Death_cast"], 1.6, -8),      # it falls
}
SET7_EVENTS, SET7_AUDIO = 5148408258298239144, 13347058717425747428   # Map22, path hashes (names unknown)
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_razorbeak_sfx_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: tft7 = Map22's set-7 bank, razorbeak = Map11's raptor camp,
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
    if src == "razorbeak":
        w = Wad(os.path.join(final, "Maps", "Shipping", "Map11.wad.client"))
        stem = MAP11
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
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22, Map11, Kled)")
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
