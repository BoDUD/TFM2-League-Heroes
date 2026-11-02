r"""Pull T-Hex's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_thex.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own TFT sounds (the user: 「音效什么都要自己找」): set 16's Map22 bank MODE_TFT_Set16_Champs_SFX holds its gatling
burst, the crit, the Hex Armory cast and its shield (Play_sfx_TFT16_THex*, found by the set's naming, 2026-11-02:
BasicAttack(2)_OnCast / _OnHit, CritAttack_OnCast / _OnHit, Spell_OnCast, Spell_OnBuffActivate); the HexMech trait bank
MODE_TFT_Set16_Traits_SFX the pilot jumping in and thrown out (Play_sfx_trait_tft16_HexMech_pilot_jumpin / _eject, the
two its anim bin names); set 16 ships no voice for it. Borrowed from League (Champions/*.wad.client): Corki's Missile
Barrage (the homing missiles launched, their blasts, the big one's blast for the ult's missiles), Package's carpet
bomb blast (the mech bursting), Viktor's Death Ray (the Hex Armory laser), Renekton's Slice (the charge) and Rengar's
empowered Savagery hit (the bite).
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
C = "tft_thex_sfx_"
S16 = "Play_sfx_TFT16_THex"
CO = "Play_sfx_Corki_"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft16", [S16 + "BasicAttack_OnCast"], 0.8, -11),                  # the gatling burst
    C + "a_crit": ("tft16", [S16 + "CritAttack_OnHit"], 0.8, -9),                # every fourth attack (Gunslinger)
    C + "q": ("Corki", [CO + "MissileBarrageMissile_OnMissileLaunch"], 0.8, -10),  # the pods fire
    C + "q_hit": ("Corki", [CO + "MissileBarrageMissile_boom"], 0.8, -11),
    C + "e": ("Renekton", ["Play_sfx_Renekton_RenektonDice_OnCast"], 0.9, -10),   # the charge
    C + "e_hit": ("Rengar", ["Play_sfx_Rengar_RengarQEmpAttack_OnHit"], 0.7, -8),  # the bite
    C + "r": ("tft16", [S16 + "Spell_OnCast"], 1.6, -8),                         # Hex Armory
    C + "r_shield": ("tft16", [S16 + "Spell_OnBuffActivate"], 1.2, -10),
    C + "r_laser": ("Viktor", ["Play_sfx_Viktor_ViktorE_OnCast"], 1.0, -9),      # each beat's laser
    C + "r_hit": ("Corki", [CO + "MissileBarrageMissile2_boom"], 0.9, -11),      # each beat's missiles
    C + "p_in": ("tft16t", ["Play_sfx_trait_tft16_HexMech_pilot_jumpin"], 1.5, -9),
    C + "p_eject": ("tft16t", ["Play_sfx_trait_tft16_HexMech_pilot_eject"], 1.5, -8),
    C + "d": ("Corki", [CO + "CarpetBombMega_hit"], 1.4, -7),                    # the mech bursts
}
SFX16 = "assets/sounds/wwise2016/sfx/shared/mode_tft_set16_champs_sfx_"
TRAITS16 = "assets/sounds/wwise2016/sfx/shared/mode_tft_set16_traits_sfx_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio, the wpk too when there is one), read once: tft16 = Map22's set-16 champion
    bank, tft16t = its trait bank, else a champion's base skin."""
    if src in cache:
        return cache[src]
    final = os.path.join(a.riot, "Game", "DATA", "FINAL")
    if src in ("tft16", "tft16t"):
        w = Wad(os.path.join(final, "Maps", "Shipping", "Map22.wad.client"))
        stem = SFX16 if src == "tft16" else TRAITS16
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
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22, Map11, champions)")
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
