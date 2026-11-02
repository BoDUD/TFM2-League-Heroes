r"""Pull the Rift Herald's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_riftherald.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

All his own (the user: 「音效什么都要自己找」): set 16's Map22 bank MODE_TFT_Set16_Champs_SFX holds his TFT spin attack
and Warp Armor (Play_sfx_tft16_RiftHerald*: SpinAttack_cast / _vox, Spell_chargeup, Spell_hit - the events his set-16
skin and animation bins name); the Rift's own Herald (Map11 NPC_Map11_RiftHerald_SFX, event names read from
data/characters/sru_riftherald/**.bin, 2026-11-02) holds his claw swings and their hits, the spin's hit, the charge
(wind-up roar, the sonic boom, the ram into a champion), the angry roar, the void spawn and his death.
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
C = "tft_riftherald_sfx_"
S16 = "Play_sfx_tft16_RiftHerald"
SRU = "Play_sfx_SRU_RiftHerald"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("sru", [SRU + "BasicAttack_OnCast"], 0.8, -11),             # the claw swing
    C + "a_hit": ("sru", [SRU + "BasicAttack_OnHit"], 0.8, -9),
    C + "q": ("tft16", [S16 + "_SpinAttack_cast"], 1.2, -9),              # the spin
    C + "q_vox": ("tft16", [S16 + "_SpinAttack_vox"], 1.2, -10),
    C + "q_hit": ("sru", [SRU + "_SpinAttack_hit"], 0.8, -10),
    C + "e": ("sru", [SRU + "_dash_windup_vox"], 1.4, -9),                # rears up before the charge
    C + "e_boom": ("sru", [SRU + "_dash_sonicboom"], 1.2, -10),
    C + "e_hit": ("sru", [SRU + "_charge_hit_champion"], 1.2, -7),        # rams a champion: stunned
    C + "r": ("tft16", [S16 + "Spell_chargeup"], 1.8, -9),                # Warp Armor: he swells
    C + "r_roar": ("sru", [SRU + "_idle_angry_vox_roar"], 2.0, -8),
    C + "r_hit": ("tft16", [S16 + "Spell_hit"], 1.6, -6),                 # the slam
    C + "r_armor": ("sru", [SRU + "_spawn_void"], 1.6, -12),              # the warped carapace glows
    C + "d": ("sru", [SRU + "_death"], 2.5, -7),                          # he collapses
}
SFX16 = "assets/sounds/wwise2016/sfx/shared/mode_tft_set16_champs_sfx_"
HERALD = "assets/sounds/wwise2016/sfx/shared/npc_map11_riftherald_sfx_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio, the wpk too when there is one), read once: tft16 = Map22's set-16 bank,
    sru = Map11's Rift Herald."""
    if src in cache:
        return cache[src]
    final = os.path.join(a.riot, "Game", "DATA", "FINAL")
    if src == "tft16":
        w, stem = Wad(os.path.join(final, "Maps", "Shipping", "Map22.wad.client")), SFX16
    else:
        w, stem = Wad(os.path.join(final, "Maps", "Shipping", "Map11.wad.client")), HERALD
    audio = w.read_path(stem + "audio.bnk")
    media = dict(bnk_media(audio))
    if w.has(stem + "audio.wpk"):
        media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
    cache[src] = SoundBanks([w.read_path(stem + "events.bnk"), audio], media)
    return cache[src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22, Map11)")
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
        print(f"{name:30s} {len(pcm) / sr:4.2f}s  <- {src} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
