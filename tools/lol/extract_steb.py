r"""Pull Steb's sounds out of the local League of Legends installs.

    python tools/lol/extract_steb.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream path\vgmstream-cli.exe

His own TFT sounds (the user: 「音效什么都要自己找」): set 13's Map22 bank MODE_TFT_Set13_Champs_SFX (Riot client: --riot)
holds his baton swings and hits (Play_sfx_TFT13_FishBasicAttack / BasicAttack2 / CritAttack _OnCast / _OnHit) and his
spell (Play_sfx_TFT13_FishSpell_OnCast / _hit, found by name 2026-10-29: his bins name only FishSpell_hit); his voice, if
the bank has it, in MODE_TFT_Set13_Champs_VO (the Riot client's en_US, as Scar's). The rest is League's
(Champions/<name>.wad.client of --lol), the medic and the enforcer: Soraka's Astral Infusion for the passive's shared
heal and her Wish for the backpack's heal, Sona's Aria for Q's self heal, Caitlyn's Ace in the Hole lock-on for the
Wanted mark, Jinx's Get Excited! for a Wanted kill's attack speed, Taric's Cosmic Radiance for opening the backpack and
Lux's Prismatic Barrier for its shields.
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
C = "tft_steb_sfx_"
S13 = "Play_sfx_TFT13_Fish"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft13", [S13 + "BasicAttack_OnCast"], 0.6, -12),           # a baton swing
    C + "a_hit": ("tft13", [S13 + "BasicAttack_OnHit"], 0.6, -10),
    C + "a2": ("tft13", [S13 + "BasicAttack2_OnCast"], 0.6, -12),          # the other baton
    C + "a2_hit": ("tft13", [S13 + "BasicAttack2_OnHit"], 0.6, -10),
    C + "p": ("Soraka", ["Play_sfx_Soraka_SorakaW_OnCast"], 1.0, -13),     # passive: the heal passed on
    C + "q": ("tft13", [S13 + "Spell_OnCast"], 1.2, -10),                   # the shot of medicine
    C + "q_heal": ("Sona", ["Play_sfx_Sona_SonaW_OnCast"], 1.0, -12),
    C + "q_hit": ("tft13", [S13 + "Spell_hit"], 1.0, -8),                   # the strike
    C + "e": ("tft13", [S13 + "CritAttack_OnCast"], 0.8, -11),             # the baton pointed
    C + "e_mark": ("Caitlyn", ["Play_sfx_Caitlyn_CaitlynR_OnCast"], 1.4, -11),   # WANTED
    C + "e_hit": ("tft13", [S13 + "CritAttack_OnHit"], 0.8, -9),           # a hit on the Wanted one
    C + "e_kill": ("Jinx", ["Play_sfx_Jinx_JinxPassiveKill_OnBuffActivate"], 1.2, -11),   # a Wanted one down
    C + "r": ("Taric", ["Play_sfx_Taric_TaricR_OnCast"], 1.6, -10),        # the backpack opened
    C + "r_shield": ("Lux", ["Play_sfx_Lux_LuxPrismaticWaveShieldSelf_buffactivate"], 1.0, -12),
    C + "r_heal": ("Soraka", ["Play_sfx_Soraka_SorakaR_OnCast"], 1.6, -11),
}
VO = ("tft13_vo", ["Play_vo_TFT13_FishSpell_OnCast"], 2.0, -3)   # his line, if the bank has one
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
    ap.add_argument("--lol", required=True, help="the WeGame client's League of Legends folder (Soraka, Sona, Caitlyn, Jinx, Taric, Lux)")
    ap.add_argument("--vgmstream", required=True, help="vgmstream-cli.exe")
    a = ap.parse_args()
    out_dir = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out_dir), exist_ok=True)
    cache = {}
    clips = dict(CLIPS)
    try:
        if banks_of(VO[0], a, cache).event_media(VO[1][0]):
            clips[C + "q_vo"] = VO
    except SystemExit:
        pass
    for name, (src, events, max_s, peak, *pick) in clips.items():
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
