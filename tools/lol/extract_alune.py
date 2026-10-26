r"""Pull Alune's sounds out of the local League of Legends installs.

    python tools/lol/extract_alune.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream path\vgmstream-cli.exe

Her own TFT sounds (the user: 「音效什么都要自己找」): set 18 names one event for her (Play_sfx_TFT18_AluneSpell_OnMissileLaunch,
in her spell data) but no bank the client ships holds it; her set-11 unit (TFT11_Alune, the 3-cost Umbral Invoker with
the same moon glaive) still has her whole kit in Map22's MODE_TFT_Set11_Champs_SFX banks (Riot client: --riot), and her
voice in MODE_TFT_Set11_Champs_VO (one event, Play_vo_TFT11_AluneSpell_OnCast, a few lines; the WeGame client's
zh_CN Map22 first, so she speaks Chinese where it has her). The full moon's fall is League's own moonfall: Diana's
(Champions/Diana.wad.client of --lol), her Pale Cascade for Moonlight's shimmer and her Moonfall for the slam.
Read, never written; the base skin's / bank's Wwise events resolved to their media (the first variant), decoded with
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
C = "tft_alune_sfx_"
S11 = "Play_sfx_TFT11_Alune"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS)
CLIPS = {
    C + "a": ("tft11", [S11 + "BasicAttack_OnMissileLaunch", S11 + "BasicAttack_OnCast"], 0.7, -10),
    C + "a_hit": ("tft11", [S11 + "BasicAttack_OnHit"], 0.6, -9),
    C + "q": ("tft11", [S11 + "Spell_OnCast"], 1.2, -7),
    C + "q_hit": ("tft11", [S11 + "SpellMissile_OnHit"], 0.9, -8),
    C + "e_cast": ("Diana", ["Play_sfx_Diana_DianaOrbs_OnCast"], 1.2, -7),
    C + "e": ("tft11", [S11 + "Spell_OnMissileLaunch"], 0.6, -12),
    C + "r": ("Diana", ["Play_sfx_Diana_DianaR_OnCast"], 1.4, -5),
    C + "r_vo": ("tft11_vo", ["Play_vo_TFT11_AluneSpell_OnCast"], 3.0, -3),
    C + "r_blast": ("Diana", ["Play_sfx_Diana_DianaR_explosion"], 1.6, -3),
}
SET11 = "assets/sounds/wwise2016/sfx/shared/mode_tft_set11_champs_sfx_"
VO11 = "assets/sounds/wwise2016/vo/{lang}/shared/mode_tft_set11_champs_vo_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once."""
    if src in cache:
        return cache[src]
    if src == "tft11":
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map22.wad.client"))
        audio = w.read_path(SET11 + "audio.bnk")
        cache[src] = SoundBanks([w.read_path(SET11 + "events.bnk"), audio], dict(bnk_media(audio)))
    elif src == "tft11_vo":
        tries = [(a.lol, "Map22.zh_CN.wad.client", "zh_cn"), (a.lol, "Map22.zh_CN.wad.client", "en_us"),
                 (a.riot, "Map22.en_US.wad.client", "en_us")]
        for base, wad, lang in tries:
            path = os.path.join(base, "Game", "DATA", "FINAL", "Maps", "Shipping", wad)
            if not os.path.isfile(lp(path)):
                continue
            w = Wad(path)
            stem = VO11.format(lang=lang)
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
            sys.exit("no MODE_TFT_Set11_Champs_VO bank in either client")
    else:
        w = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", f"{src}.wad.client"))
        bank = f"assets/sounds/wwise2016/sfx/characters/{src.lower()}/skins/base/{src.lower()}_base_sfx_"
        audio = w.read_path(bank + "audio.bnk")
        cache[src] = SoundBanks([w.read_path(bank + "events.bnk"), audio], dict(bnk_media(audio)))
    return cache[src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22 with set 11)")
    ap.add_argument("--lol", required=True, help="the WeGame client's League of Legends folder (Diana, Chinese voice)")
    ap.add_argument("--vgmstream", required=True, help="vgmstream-cli.exe")
    a = ap.parse_args()
    out_dir = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out_dir), exist_ok=True)
    cache = {}
    for name, (src, events, max_s, peak) in CLIPS.items():
        banks = banks_of(src, a, cache)
        event, variants = None, []
        for ev in events:
            variants = banks.event_media(ev)
            if variants:
                event = ev
                break
        if not variants:
            sys.exit(f"{name}: none of {events} resolves in {src} - game patch changed the bank?")
        sr, x = decode(banks.media[variants[0]], a.vgmstream)
        pcm = finish(x, sr, max_s, peak)
        with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        print(f"{name:26s} {len(pcm) / sr:4.2f}s  <- {src} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
