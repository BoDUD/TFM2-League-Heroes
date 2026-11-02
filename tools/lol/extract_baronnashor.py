r"""Pull Baron Nashor's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_baronnashor.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

All his own (the user: 「音效什么都要自己找」): set 16's Map22 bank MODE_TFT_Set16_Champs_SFX holds his TFT bite, burrow
strike, spike slam and acid balls (Play_sfx_tft16_BaronNashor*: BasicAttack_OnCast / _OnHit, Strike_burrow / _unburrow /
_hit, Spike_missilecast, AcidBall_cast / _missilelaunch, Tail_cast - the events his set-16 skin and animation bins
name); the Rift's own Baron (Map11 NPC_Map11_Baron_SFX, event names read from every bin in Map11.wad.client,
2026-11-03) holds the knock-up tentacle (BaronBackSideStun), the acid breath and its landing, his spawn roar and the
void suck he makes going under (no death event is named in any bin: the suck stands in for it).
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
C = "tft_baronnashor_sfx_"
S16 = "Play_sfx_tft16_BaronNashor"
SRU = "Play_sfx_SRU_Baron_"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft16", [S16 + "BasicAttack_OnCast"], 0.9, -10),           # the bite
    C + "a_hit": ("tft16", [S16 + "BasicAttack_OnHit"], 0.8, -9),
    C + "p": ("sru", [SRU + "BaronBackSideStun_missilecast"], 1.2, -9),   # a tentacle bursts up under an enemy
    C + "q": ("sru", [SRU + "BaronAcidBall_cast"], 1.0, -10),             # spits acid
    C + "q_breath": ("sru", [SRU + "BaronDeathBreath_cast_vosfx"], 1.6, -10),
    C + "q_hit": ("sru", [SRU + "BaronAcidBall_hit_land"], 1.0, -9),      # the acid splashes, armour corrodes
    C + "e": ("tft16", [S16 + "Strike_burrow"], 1.0, -9),                 # dives into the ground
    C + "e_up": ("tft16", [S16 + "Strike_unburrow"], 1.2, -8),            # bursts out under the target
    C + "e_hit": ("tft16", [S16 + "Strike_hit"], 1.0, -7),                # knocks the neighbours up
    C + "r": ("tft16", [S16 + "Spike_missilecast"], 1.4, -7),             # Void's Wrath: the slam, spikes erupt
    C + "r_roar": ("sru", [SRU + "spawn_out_cast_vox_reverb"], 2.2, -8),
    C + "r_acid": ("tft16", [S16 + "AcidBall_missilelaunch"], 0.9, -11),  # each acid ball of the barrage
    C + "r_hit": ("sru", [SRU + "NewSpellLivingArtillery_hit"], 1.0, -10),
    C + "d": ("sru", [SRU + "spawn_suck"], 2.5, -8),                      # sinks back into the void
}
SFX16 = "assets/sounds/wwise2016/sfx/shared/mode_tft_set16_champs_sfx_"
BARON = "assets/sounds/wwise2016/sfx/shared/npc_map11_baron_sfx_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio, the wpk too when there is one), read once: tft16 = Map22's set-16 bank,
    sru = Map11's Baron."""
    if src in cache:
        return cache[src]
    final = os.path.join(a.riot, "Game", "DATA", "FINAL")
    if src == "tft16":
        w, stem = Wad(os.path.join(final, "Maps", "Shipping", "Map22.wad.client")), SFX16
    else:
        w, stem = Wad(os.path.join(final, "Maps", "Shipping", "Map11.wad.client")), BARON
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
