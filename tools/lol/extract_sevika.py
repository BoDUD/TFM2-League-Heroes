r"""Pull Sevika's sounds out of the local League of Legends installs.

    python tools/lol/extract_sevika.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream pathgmstream-cli.exe

Her own TFT sounds (the user: 「音效什么都要自己找」): set 13's Map22 bank MODE_TFT_Set13_Champs_SFX (Riot client: --riot)
holds nearly her whole kit (Play_sfx_TFT13_Lieutenant*, named in her skin and animation bins, 2026-10-29): the arm's two
punches and their hits, the slot machine's roll, Jinx's rockets, the jackpot, the flamethrower (stance, cast, loop), the
extendo punch (cast, launch, hit), the slam (dash, hit, explosion) and the chomp (cast, hit); her voice is in
MODE_TFT_Set13_Champs_VO (Play_vo_TFT13_LieutenantSpell_OnCast; the Riot client's en_US, as Scar's). The rest is
League's (Champions/<name>.wad.client of --lol): Lux's Prismatic Barrier for the passive's shield mod and Jinx's Get
Excited! for its shimmer mod (Jinx built the mods).
Read, never written; the base skin's / bank's Wwise events resolved to their media (the first variant unless given),
decoded with vgmstream and written as mono 16-bit WAVs to tft/sound/sfx/ (git-ignored: audio (c) Riot Games).
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
C = "tft_sevika_sfx_"
S13 = "Play_sfx_TFT13_Lieutenant"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft13", [S13 + "BasicAttack_OnCast"], 0.6, -12),          # the arm's punch
    C + "a_hit": ("tft13", [S13 + "BasicAttack_hit"], 0.6, -10),
    C + "a2": ("tft13", [S13 + "BasicAttack2_OnCast"], 0.6, -11),        # every third: the claws clamp
    C + "a2_hit": ("tft13", [S13 + "BasicAttack2_hit"], 0.7, -9),
    C + "p": ("tft13", [S13 + "_Spell_roll"], 1.4, -10),                 # the slot machine rolls
    C + "p_rocket": ("tft13", [S13 + "_Rockets_missilecast"], 1.2, -10),  # mod: Jinx's rockets
    C + "p_rocket_hit": ("tft13", [S13 + "_Rockets_hit"], 0.8, -11),
    C + "p_shield": ("Lux", ["Play_sfx_Lux_LuxPrismaticWaveShieldSelf_buffactivate"], 1.0, -11),   # mod: shield
    C + "p_shimmer": ("Jinx", ["Play_sfx_Jinx_JinxPassiveKill_OnBuffActivate"], 1.2, -11),        # mod: shimmer
    C + "p_jackpot": ("tft13", [S13 + "_Jackpot_result"], 1.6, -8),      # mod: triple - the jackpot
    C + "p_jackpot_fx": ("tft13", [S13 + "_Jackpot_fountain_explo"], 1.6, -10),
    C + "q": ("tft13", [S13 + "_Flamethrower_stance"], 0.8, -10),       # the arm levelled
    C + "q_fire": ("tft13", [S13 + "_Flamethrower_cast"], 1.2, -9),
    C + "q_loop": ("tft13", [S13 + "_Flamethrower_loop"], 2.0, -11),
    C + "e": ("tft13", [S13 + "_Spell_ExtendoPunch_cast"], 1.0, -10),
    C + "e_launch": ("tft13", [S13 + "_Spell_ExtendoPunch_launch"], 1.0, -9),
    C + "e_hit": ("tft13", [S13 + "_Spell_ExtendoPunch_hit"], 1.0, -7),
    C + "e_stun": ("tft13", [S13 + "_Spell_Slam_hit"], 1.0, -8),         # knocked into the one behind
    C + "r": ("tft13", [S13 + "_Spell_Chomp_cast"], 1.2, -9),
    C + "r_vo": ("tft13_vo", ["Play_vo_TFT13_LieutenantSpell_OnCast"], 2.0, -3),
    C + "r_dash": ("tft13", [S13 + "_Spell_Slam_dash"], 0.8, -10),
    C + "r_hit": ("tft13", [S13 + "_Spell_Chomp_hit"], 1.0, -7),         # each bite
    C + "r_kill": ("tft13", [S13 + "_Spell_Slam_explo"], 1.4, -7),       # the execute
}
SET13 = "assets/sounds/wwise2016/sfx/shared/mode_tft_set13_champs_sfx_"
VO13 = "assets/sounds/wwise2016/vo/{lang}/shared/mode_tft_set13_champs_vo_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once."""
    if src in cache:
        return cache[src]
    if src == "tft13":
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map22.wad.client"))
        audio = w.read_path(SET13 + "audio.bnk")
        cache[src] = SoundBanks([w.read_path(SET13 + "events.bnk"), audio], dict(bnk_media(audio)))
    elif src == "tft13_vo":
        tries = [(a.lol, "Map22.zh_CN.wad.client", "zh_cn"), (a.riot, "Map22.zh_CN.wad.client", "zh_cn"),
                 (a.riot, "Map22.en_US.wad.client", "en_us")]
        for base, wad, lang in tries:
            path = os.path.join(base, "Game", "DATA", "FINAL", "Maps", "Shipping", wad)
            if not os.path.isfile(lp(path)):
                continue
            w = Wad(path)
            stem = VO13.format(lang=lang)
            if not w.has(stem + "events.bnk"):
                continue
            audio = w.read_path(stem + "audio.bnk")
            media = dict(bnk_media(audio))
            if w.has(stem + "audio.wpk"):
                media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
            cache[src] = SoundBanks([w.read_path(stem + "events.bnk"), audio], media)
            print(f"voice from {wad} ({lang})")
            break
        else:
            sys.exit("no MODE_TFT_Set13_Champs_VO bank in either client")
    else:
        w = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", f"{src}.wad.client"))
        bank = f"assets/sounds/wwise2016/sfx/characters/{src.lower()}/skins/base/{src.lower()}_base_sfx_"
        audio = w.read_path(bank + "audio.bnk")
        media = dict(bnk_media(audio))
        if w.has(bank + "audio.wpk"):
            media.update(parse_wpk(w.read_path(bank + "audio.wpk")))
        cache[src] = SoundBanks([w.read_path(bank + "events.bnk"), audio], media)
    return cache[src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22 with set 13)")
    ap.add_argument("--lol", required=True, help="the WeGame client's League of Legends folder (Lux, Jinx)")
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
