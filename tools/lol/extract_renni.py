r"""Pull Renni's sounds out of the local League of Legends installs.

    python tools/lol/extract_renni.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream path\vgmstream-cli.exe

Her own TFT sounds (the user: 「音效什么都要自己找」): set 13's Map22 banks MODE_TFT_Set13_Champs_SFX (Riot client: --riot)
hold her chainsaw - two revving swings and their grinding hits - and her Mudrunner Slam: the heave up and the slam
(Play_sfx_TFT13_Chainsaw*, found by the set's naming 2026-10-29: BasicAttack(2)_OnCast / _OnHit, Spell_OnCast /
_OnHit, SpellHero_OnCast / _hit); her voice is in MODE_TFT_Set13_Champs_VO (Play_vo_TFT13_ChainsawSpell_OnCast, 3
variants; the Riot client's en_US, as Scar's). The rest is League's (Champions/<name>.wad.client of --lol): Vi's
Vault Breaker launch for Q's charge, Braum's Unbreakable for E's saw raised as a guard, Dr. Mundo's Maximum Dosage
and Heart Zapper's heal for the passive's shimmer shot.
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
C = "tft_renni_sfx_"
S13 = "Play_sfx_TFT13_Chainsaw"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft13", [S13 + "BasicAttack_OnCast"], 0.7, -12),          # the saw revved forward
    C + "a_hit": ("tft13", [S13 + "BasicAttack_OnHit"], 0.6, -10),       # the grind
    C + "p": ("DrMundo", ["Play_sfx_DrMundo_DrMundoR_OnCast"], 1.4, -9),  # the shimmer shot
    C + "p_heal": ("DrMundo", ["Play_sfx_DrMundo_DrMundoW_heal_buffactivate"], 1.0, -11),
    C + "q": ("Vi", ["Play_sfx_Vi_ViQMissile_OnMissileLaunch"], 1.0, -9),  # the charge
    C + "q_saw": ("tft13", [S13 + "BasicAttack2_OnCast"], 0.8, -10),     # the saw revved at the end of it
    C + "q_hit": ("tft13", [S13 + "BasicAttack2_OnHit"], 0.7, -9),       # each grind of the cone
    C + "e": ("Braum", ["Play_sfx_Braum_BraumE_OnCast"], 1.0, -9),       # the saw raised as a guard
    C + "r": ("tft13", [S13 + "Spell_OnCast"], 1.6, -9),                 # the heave
    C + "r_vo": ("tft13_vo", ["Play_vo_TFT13_ChainsawSpell_OnCast"], 2.0, -3),
    C + "r_lift": ("tft13", [S13 + "SpellHero_OnCast"], 1.6, -9),        # held up overhead, the saw grinding
    C + "r_hit": ("tft13", [S13 + "Spell_OnHit"], 1.4, -6),              # the slam
    C + "r_slam": ("tft13", [S13 + "SpellHero_hit"], 1.4, -6),
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
    ap.add_argument("--lol", required=True, help="the WeGame client's League of Legends folder (Vi, Braum, Dr. Mundo)")
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
