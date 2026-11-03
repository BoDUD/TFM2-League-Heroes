r"""Pull the Mighty Mech's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_mightymech.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

All its own (the user: 「音效什么都要自己找」): its set-17 skin and animation bins name set 15's Galio mech events
(Map22 MODE_TFT_Set15_Champs_SFX: Play_sfx_tft15_Galio* - the sword swing and slam, the shield, the leap and its
landing) and set 17's own (MODE_TFT_Set17_Champs_SFX: GalioSpell_buffactivate / _hit = Gravity Matrix and its
shockwave, Galio_Mecha_transform); set 15's Mighty Mech trait bank (MODE_TFT_Set15_Traits_SFX) holds the blade
blazing (Sentai_Sword_ceremony), the mech's summoning fanfare and its heavy ground hit (no death event is named
in any bin: the ground hit stands in for it). Event names read from every PROP bin in Map22 and TFTSet15/17 (2026-11-03).
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
C = "tft_mightymech_sfx_"
G15 = "Play_sfx_tft15_Galio"
G17 = "Play_sfx_tft17_Galio"
SENTAI = "Play_sfx_trait_tft15_Sentai_"

# clip name -> (bank, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("set15_champs", [G15 + "BasicAttack_Sword_cast"], 0.9, -10),    # the sword swing (it always holds it)
    C + "a_hit": ("set15_champs", [G15 + "BasicAttack_Sword_hit"], 0.6, -9),
    C + "q": ("set17_champs", [G17 + "Spell_buffactivate"], 2.0, -9),           # Gravity Matrix: braces, the field up
    C + "q_shield": ("set15_champs", [G15 + "Shield_cast"], 1.6, -11),          # the field pulls a shot in
    C + "q_hit": ("set17_champs", [G17 + "Spell_hit"], 1.8, -8),                # the shockwave when it ends
    C + "e": ("set15_champs", [G15 + "Spell1_launch"], 1.2, -9),                # leaps up
    C + "e_hit": ("set15_champs", [G15 + "Spell1_hit"], 1.3, -8),               # lands, knocks up
    C + "r": ("set17_champs", [G17 + "_Mecha_transform"], 2.5, -8),             # transforms into the Ultimate form
    C + "r_sword": ("set15_traits", [SENTAI + "Sword_ceremony"], 2.5, -9),      # the blade blazes and grows (the trait's sword ceremony)
    C + "r_swing": ("set15_champs", [G15 + "Spell3_Sword_slam_cast"], 1.1, -9),
    C + "r_hit": ("set15_champs", [G15 + "Spell3_Sword_slam_hit"], 1.6, -7),    # the slam lands
    C + "p": ("set15_traits", [SENTAI + "Summon_ceremony"], 2.6, -10),          # the mech powers up (each life)
    C + "d": ("set15_traits", [SENTAI + "prismatic_ground_hit"], 1.9, -8),      # crashes down
}
SHARED = "assets/sounds/wwise2016/sfx/shared/mode_tft_{}_sfx_"


def banks_of(src, a, cache):
    """A Map22 sfx bank (events + audio, the wpk too when there is one), read once."""
    if src in cache:
        return cache[src]
    w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map22.wad.client"))
    stem = SHARED.format(src)
    audio = w.read_path(stem + "audio.bnk")
    media = dict(bnk_media(audio))
    if w.has(stem + "audio.wpk"):
        media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
    cache[src] = SoundBanks([w.read_path(stem + "events.bnk"), audio], media)
    return cache[src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22)")
    ap.add_argument("--vgmstream", required=True, help="vgmstream-cli.exe")
    ap.add_argument("--out", help="where the WAVs go (default tft/sound/sfx)")
    a = ap.parse_args()
    out_dir = a.out or os.path.join(MOD, "sound", "sfx")
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
        print(f"{name:32s} {len(pcm) / sr:4.2f}s  <- {src} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
