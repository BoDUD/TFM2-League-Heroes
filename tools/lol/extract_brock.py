r"""Pull Brock's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_brock.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

His own TFT sounds (the user: 「音效什么都要自己找」): set 16's Map22 bank MODE_TFT_Set16_Champs_SFX holds his fist swings and
their hits, the crit and his ult (Play_sfx_TFT16_Brock*, found by the set's naming, 2026-11-02: BasicAttack(2)_OnCast /
_OnHit, CritAttack_OnCast / _OnHit, Spell_OnCast, Spell_hit (3 variants) - the one event his skin bin names); set 16 ships
no voice for him. Borrowed from League (Champions/*.wad.client): Malphite's Seismic Shard (the boulder thrown and its hit),
Granite Shield (the mossy shell) and Ground Slam's hit (knocked up by the slam); Maokai's Twisted Advance (his roots
lunge) and Zyra's Grasping Roots (the roots close); the Rift's Krug crumbling (Map11) for his death.
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
C = "tft_brock_sfx_"
S16 = "Play_sfx_TFT16_Brock"
MA = "Play_sfx_Malphite_"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft16", [S16 + "BasicAttack_OnCast"], 0.8, -11),
    C + "a_hit": ("tft16", [S16 + "BasicAttack_OnHit"], 0.8, -9),
    C + "a_up": ("tft16", [S16 + "CritAttack_OnHit"], 1.0, -8),                 # every third blow: knocked up
    C + "q": ("Malphite", [MA + "SeismicShard_OnMissileLaunch"], 1.0, -10),     # the boulder hurled
    C + "q_hit": ("Malphite", [MA + "SeismicShard_OnHit"], 1.0, -9),
    C + "e": ("Maokai", ["Play_sfx_Maokai_MaokaiW_OnCast"], 1.2, -10),          # the roots lunge underground
    C + "e_root": ("Zyra", ["Play_sfx_Zyra_ZyraE_OnCast"], 1.2, -10),           # they burst up and close
    C + "e_shield": ("Malphite", [MA + "MalphiteShieldEffect_OnBuffActivate"], 1.2, -10),
    C + "r": ("tft16", [S16 + "Spell_OnCast"], 1.6, -8),                        # the leap
    C + "r_jump": ("tft16", [S16 + "CritAttack_OnCast"], 1.0, -10),
    C + "r_slam": ("tft16", [S16 + "Spell_hit"], 2.0, -5),                      # the board-wide slam
    C + "r_hit": ("Malphite", [MA + "Landslide_hit"], 1.0, -10),                # knocked up by it
    C + "r_rock": ("tft16", [S16 + "Spell_hit"], 1.2, -12, 2),                  # a falling rock (another variant)
    C + "d": ("krug", ["Play_sfx_SRU_Krug_Death_cast"], 2.0, -7),               # he crumbles
}
SFX16 = "assets/sounds/wwise2016/sfx/shared/mode_tft_set16_champs_sfx_"
KRUG = "assets/sounds/wwise2016/sfx/shared/npc_map11_krug_sfx_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio, the wpk too when there is one), read once: tft16 = Map22's set-16 bank,
    krug = Map11's Krug, else a champion's base skin."""
    if src in cache:
        return cache[src]
    final = os.path.join(a.riot, "Game", "DATA", "FINAL")
    if src == "tft16":
        w, stem = Wad(os.path.join(final, "Maps", "Shipping", "Map22.wad.client")), SFX16
    elif src == "krug":
        w, stem = Wad(os.path.join(final, "Maps", "Shipping", "Map11.wad.client")), KRUG
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
