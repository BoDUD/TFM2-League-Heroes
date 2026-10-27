r"""Pull Loris's sounds out of the local League of Legends installs.

    python tools/lol/extract_loris.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream path\vgmstream-cli.exe

His own TFT sounds (the user: 「音效什么都要自己找」): set 16's Map22 banks MODE_TFT_Set16_Champs_SFX (Riot client: --riot)
hold his shield bash and its hit, the heavy crit hit, the cast and the charge (Play_sfx_TFT16_Loris*, found by the set's
naming, 2026-10-27: BasicAttack(2)_OnCast / _OnHit, CritAttack_*, Spell_OnCast, Spell_dash). His shield buff and its
shockwave (the two events his skin bin names, SpellBuff_buffactivate / _shockwave_buffactivate) resolve only in set 13's
bank, under the same model's old name TFT13_Beardy (MODE_TFT_Set13_Champs_SFX). His voice is in MODE_TFT_Set16_Champs_VO
(one event, Play_vo_TFT16_LorisSpell_OnCast; the Riot client's en_US: WeGame has no set-16 voice). Borrowed from League
(Champions/*.wad.client of --lol): Bulwark's leap to an ally is Braum's Stand Behind Me landing (BraumWDash_land), and the
ground cracking under the Iron Line is Glacial Fissure's hit (BraumRMissile_OnHit) - the other shield-bearing support.
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
C = "tft_loris_sfx_"
S16 = "Play_sfx_TFT16_Loris"
S13 = "Play_sfx_TFT13_Beardy"
BR = "Play_sfx_Braum_Braum"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft16", [S16 + "BasicAttack_OnCast"], 0.6, -12),
    C + "a_hit": ("tft16", [S16 + "BasicAttack_OnHit"], 0.6, -11),
    C + "p": ("tft13", [S13 + "SpellBuff_buffactivate"], 1.2, -10, 1),     # Warden: the passive's shield
    C + "q": ("tft16", [S16 + "Spell_OnCast"], 1.2, -10),                  # the shield up, the charge called
    C + "q_dash": ("tft16", [S16 + "Spell_dash", S16 + "Spell_Dash"], 1.2, -10),
    C + "q_hit": ("tft16", [S16 + "CritAttack_OnHit"], 0.8, -9),
    C + "e": ("Braum", [BR + "WDash_land"], 0.9, -10),
    C + "e_shield": ("tft13", [S13 + "SpellBuff_buffactivate"], 1.2, -10),
    C + "r": ("tft13", [S13 + "Spell_OnCast"], 1.2, -10),                  # the shield lifted high
    C + "r_slam": ("tft13", [S13 + "SpellBuff_shockwave_buffactivate"], 1.6, -7),
    C + "r_hit": ("Braum", [BR + "RMissile_OnHit"], 1.2, -9),
    C + "vo": ("tft16_vo", ["Play_vo_TFT16_LorisSpell_OnCast"], 3.0, -3, 2),   # his battle cry: the longest (0.53 s)
}
SFX = "assets/sounds/wwise2016/sfx/shared/mode_tft_set{set}_champs_sfx_"
VO16 = "assets/sounds/wwise2016/vo/{lang}/shared/mode_tft_set16_champs_vo_"


def map22_banks(w, stem):
    """A Map22 bank pair (events + audio, the wpk too when there is one)."""
    audio = w.read_path(stem + "audio.bnk")
    media = dict(bnk_media(audio))
    if w.has(stem + "audio.wpk"):
        media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
    return SoundBanks([w.read_path(stem + "events.bnk"), audio], media)


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once."""
    if src in cache:
        return cache[src]
    if src in ("tft16", "tft13"):
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map22.wad.client"))
        cache[src] = map22_banks(w, SFX.format(set=src[3:]))
    elif src == "tft16_vo":
        tries = [(a.lol, "Map22.zh_CN.wad.client", "zh_cn"), (a.riot, "Map22.zh_CN.wad.client", "zh_cn"),
                 (a.riot, "Map22.en_US.wad.client", "en_us")]
        for base, wad, lang in tries:
            path = os.path.join(base, "Game", "DATA", "FINAL", "Maps", "Shipping", wad)
            if not os.path.isfile(lp(path)):
                continue
            w = Wad(path)
            stem = VO16.format(lang=lang)
            if not w.has(stem + "events.bnk"):
                continue
            cache[src] = map22_banks(w, stem)
            print(f"voice from {wad} ({lang})")
            break
        else:
            sys.exit("no MODE_TFT_Set16_Champs_VO bank in either client")
    else:
        w = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", f"{src}.wad.client"))
        bank = f"assets/sounds/wwise2016/sfx/characters/{src.lower()}/skins/base/{src.lower()}_base_sfx_"
        audio = w.read_path(bank + "audio.bnk")
        cache[src] = SoundBanks([w.read_path(bank + "events.bnk"), audio], dict(bnk_media(audio)))
    return cache[src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22 with sets 13 / 16)")
    ap.add_argument("--lol", required=True, help="the WeGame client's League of Legends folder (Braum)")
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
