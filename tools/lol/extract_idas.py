r"""Pull Idas's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_idas.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Her own sounds (the user: 「音效什么都要自己找」). Set 7 (TFT7_DragonGold) names her events in her skin bin and Map22 still
holds them in the set-7 champions bank (the one Nomsy's sounds come from, found 2026-10-29): the golden breath's cast
and its armour-melting hit (GoldBreath_cast / GoldBreath_buffactivate), Golden Scales' cast, loop and burst (R_cast /
R_loop / R_hit) and the flame-breath hit her bin borrows from set 7's Shyvana (tft7_ShyvanaRFlameBreath_hit; found
2026-10-30). Her bins name no attack, roar or death sound, so those come from League's own dragons: Shyvana in dragon
form (the claws, Burnout's heal), the Rift's drakes in Map11 (E's roar and wing beat, R's roar, the death),
and the golden shields from Lux's Prismatic Barrier (the Guardian's vow), Janna's Eye of the Storm (E's small shield)
and Rakan's Battle Dance (R's shield on each ally).
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
C = "tft_idas_sfx_"
G = "Play_sfx_tft7_DragonGold_"
D = "Play_sfx_SRU_Dragon_"
SH = "Play_sfx_Shyvana_Shyvana"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("Shyvana", [SH + "DragonBasicAttack_OnCast"], 0.8, -11),         # the claw
    C + "a_hit": ("Shyvana", [SH + "DragonBasicAttack_OnHit"], 0.7, -11),
    C + "p": ("Lux", ["Play_sfx_Lux_LuxPrismaticWaveShieldSelf_buffactivate"], 1.0, -9),   # the Guardian's vow
    C + "q": ("tft7", [G + "GoldBreath_cast"], 1.4, -8),                        # the golden breath
    C + "q_hit": ("tft7", ["Play_sfx_tft7_ShyvanaRFlameBreath_hit"], 0.9, -10),
    C + "q_shred": ("tft7", [G + "GoldBreath_buffactivate"], 1.0, -11),          # the armour melts
    C + "e": ("dragons", [D + "aggro1_buffactive", D + "aggro3_buffactive"], 1.6, -6),   # the roar
    C + "e_wing": ("dragons", [D + "DragonTakeOff_cast"], 1.0, -9),              # the wing beat
    C + "e_shield": ("Janna", ["Play_sfx_Janna_EyeOfTheStorm_OnBuffActivate"], 1.0, -11),
    C + "r": ("tft7", [G + "R_cast"], 1.6, -8),                                 # the wings close round her
    C + "r_loop": ("tft7", [G + "R_loop"], 2.0, -12),
    C + "r_hit": ("tft7", [G + "R_hit"], 1.6, -7),                              # the scales burst out
    C + "r_roar": ("dragons", [D + "aggro3_buffactive", D + "aggro2_buffactive"], 1.8, -6),
    C + "r_heal": ("Shyvana", [SH + "DragonW_heal"], 1.0, -12),
    C + "r_shield": ("Rakan", ["Play_sfx_Rakan_RakanEShield_OnBuffActivate"], 1.2, -10),
    C + "d": ("dragons", [D + "death_cast"], 2.0, -7, 1),                       # she falls
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
