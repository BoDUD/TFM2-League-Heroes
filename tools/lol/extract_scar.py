r"""Pull Scar's sounds out of the local League of Legends installs.

    python tools/lol/extract_scar.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream path\vgmstream-cli.exe

His own TFT sounds (the user: 「音效什么都要自己找」): set 13's Map22 banks MODE_TFT_Set13_Champs_SFX (Riot client: --riot)
hold his spear - the thrust and its hit, the second swing and its hit, the crit hit - and his Puddle Jumper Surprise:
the throw, the bomb going off and the heal (Play_sfx_TFT13_FlyGuy*, found by the set's naming 2026-10-28:
BasicAttack(2)_OnCast / _OnHit, CritAttack_OnHit, Spell_OnCast / _hit / _heal / _loop); his voice is in
MODE_TFT_Set13_Champs_VO (Play_vo_TFT13_FlyGuySpell_OnCast, 3 variants; the Riot client's en_US, as Violet's).
The Firelights' hoverboard is Firelight Ekko's (League skin 36, Champions/Ekko.wad.client of --riot: the Phase Dive
dash for the passive's ride, the boost of his passive's speed for the ult's ride, Parallel Convergence's shield for
the ult's guard). The fire bombs the ult drops are Ziggs's (Champions/Ziggs.wad.client of --lol: the Bouncing Bomb's
hit and the Hexplosive Minefield's mines going off).
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
C = "tft_scar_sfx_"
S13 = "Play_sfx_TFT13_FlyGuy"
EK = "Play_sfx_EkkoSkin36_Ekko"
ZG = "Play_sfx_Ziggs_Ziggs"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft13", [S13 + "BasicAttack_OnCast"], 0.6, -12),
    C + "a_hit": ("tft13", [S13 + "BasicAttack_OnHit"], 0.6, -10),
    C + "p": ("ekko36", [EK + "E_OnCast"], 1.0, -9),                    # the hoverboard dash
    C + "p_hit": ("tft13", [S13 + "CritAttack_OnHit"], 0.8, -8),
    C + "p_heal": ("tft13", [S13 + "Spell_heal"], 1.2, -10),
    C + "q": ("tft13", [S13 + "Spell_OnCast"], 1.0, -10),               # the throw
    C + "q_vo": ("tft13_vo", ["Play_vo_TFT13_FlyGuySpell_OnCast"], 2.0, -3),
    C + "q_hit": ("tft13", [S13 + "Spell_hit"], 1.2, -6),               # a bomb going off
    C + "e": ("tft13", [S13 + "BasicAttack2_OnCast"], 0.7, -10),        # the sweep
    C + "e_hit": ("tft13", [S13 + "BasicAttack2_OnHit"], 0.8, -8),
    C + "r": ("ekko36", [EK + "PassiveSpeed_OnBuffActivate"], 1.4, -8),  # onto the board, away
    C + "r_bomb": ("Ziggs", [ZG + "Q_hit"], 1.0, -7),                    # a fire bomb going off
    C + "r_mines": ("Ziggs", [ZG + "W_detonate"], 1.2, -6),              # the last blast on landing
    C + "r_guard": ("ekko36", [EK + "WShield_OnBuffActivate"], 1.2, -9),  # the guard after landing
}
SET13 = "assets/sounds/wwise2016/sfx/shared/mode_tft_set13_champs_sfx_"
VO13 = "assets/sounds/wwise2016/vo/{lang}/shared/mode_tft_set13_champs_vo_"
EKKO36 = "assets/sounds/wwise2016/sfx/characters/ekko/skins/skin36/ekko_skin36_sfx_"


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
    elif src == "ekko36":
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Champions", "Ekko.wad.client"))
        audio = w.read_path(EKKO36 + "audio.bnk")
        cache[src] = SoundBanks([w.read_path(EKKO36 + "events.bnk"), audio], dict(bnk_media(audio)))
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
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22 with set 13, Ekko)")
    ap.add_argument("--lol", required=True, help="the WeGame client's League of Legends folder (Ziggs)")
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
