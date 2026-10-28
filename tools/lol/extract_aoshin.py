r"""Pull Ao Shin's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_aoshin.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

His own sounds (the user: 「音效什么都要自己找」). Set 7 (TFT7_AoShin) names no event in its bins and the client ships no
set-7 bank any more (Map22 holds sets 10-17 only; TFTSet7.wad.client has no .bnk), so his voice is the Rift's own storm
dragon: Map11's Cloud Drake (sru_dragon_air's skin bin links NPC_Map11_Dragons_Cloud_SFX and the shared
NPC_Map11_Dragons_SFX: its wind-ball attack and hit, the take-off, the aggro roar, the death; 2026-10-28).
The lightning is League's storm champions', Champions/<name>.wad.client: Volibear's Sky Splitter (the bolt from the sky
for the passive's storm and every strike of the ult, its gathering cloud for the ult's cast), Kennen's Mark of the Storm
stun and Electrical Surge (the breath's crackle and its hit), Janna's Eye of the Storm (the cloud shield).
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
C = "tft_aoshin_sfx_"
D = "Play_sfx_SRU_Dragon_"
VB = "Play_sfx_Volibear_Volibear"
KN = "Play_sfx_Kennen_Kennen"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("cloud", [D + "Cloud_Attack_OnCast"], 0.8, -11, 5),                      # the ball lightning
    C + "a_hit": ("cloud", [D + "Cloud_Attack_OnHitLocation"], 0.6, -10, 4),
    C + "p": ("dragons", [D + "aggro1_buffactive", D + "aggro3_buffactive"], 1.8, -6),   # the storm's roar
    C + "p_bolt": ("Volibear", [VB + "E_explo"], 1.5, -6),                              # lightning from the sky
    C + "p_stun": ("Kennen", [KN + "MarkoftheStorm_stun"], 0.9, -10),
    C + "q": ("Kennen", [KN + "BringTheLight_OnCast"], 1.0, -8),                        # the lightning breath
    C + "q_hit": ("Kennen", [KN + "BringTheLight_hit"], 0.8, -9),
    C + "e": ("dragons", [D + "DragonTakeOff_cast"], 1.2, -8),                          # wings up, away
    C + "e_shield": ("Janna", ["Play_sfx_Janna_EyeOfTheStorm_OnBuffActivate"], 1.2, -10),
    C + "r": ("Volibear", [VB + "E_buffactivate"], 1.5, -8),                            # the storm gathers
    C + "r_roar": ("cloud_vo", ["Play_vo_SRU_Dragon_Cloud_Attack_OnCast"], 1.6, -5),        # the drake's own cry
    C + "r_bolt": ("Volibear", [VB + "E_hit"], 1.0, -9),                              # one strike
    C + "r_hit": ("Kennen", [KN + "MegaProc_OnHit"], 0.7, -11),
    C + "d": ("dragons", [D + "death_cast"], 2.0, -7, 1),                                  # falls from the sky
}
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_dragons_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: cloud / dragons = Map11's drakes, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src in ("cloud", "cloud_vo", "dragons"):
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client"))
        stem = MAP11 + ("sfx_" if src == "dragons" else "cloud_sfx_")
    else:
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Champions", f"{src}.wad.client"))
        stem = f"assets/sounds/wwise2016/sfx/characters/{src.lower()}/skins/base/{src.lower()}_base_sfx_"
    audio = w.read_path(stem + "audio.bnk")
    media = dict(bnk_media(audio))
    if w.has(stem + "audio.wpk"):
        media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
    cache[src] = SoundBanks([w.read_path(stem + "events.bnk"), audio], media)
    return cache[src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map11, the champions)")
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
