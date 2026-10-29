r"""Pull Smeech's sounds out of the local League of Legends installs.

    python tools/lol/extract_smeech.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream path\vgmstream-cli.exe

His own TFT sounds (the user: 「音效什么都要自己找」): set 13's Map22 banks MODE_TFT_Set13_Champs_SFX (Riot client: --riot)
hold his claws - two raking swings and their hits, the crit rake - and his Scrap Hacker: the leap and the slashes
(Play_sfx_TFT13_Gremlin*, found by the set's naming 2026-10-29: BasicAttack(2)_OnCast / _OnHit, CritAttack_OnCast /
_OnHit, Spell_OnCast / _OnHit); his voice is in MODE_TFT_Set13_Champs_VO (Play_vo_TFT13_GremlinSpell_OnCast, 3
variants; the Riot client's en_US, as Scar's and Renni's). The rest is League's (Champions/<name>.wad.client of --lol):
Kha'Zix's leap landing for Q's, his Taste Their Fear for E's rip, Twitch's Expunge for the armour torn off, Kha'Zix's
Void Assault for R's vanish, Master Yi's Alpha Strike for each of R's chained slashes and Rengar's empowered Savagery
for its last.
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
C = "tft_smeech_sfx_"
S13 = "Play_sfx_TFT13_Gremlin"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft13", [S13 + "BasicAttack_OnCast"], 0.6, -12),        # the near claw rakes
    C + "a_hit": ("tft13", [S13 + "BasicAttack_OnHit"], 0.6, -10),
    C + "a2": ("tft13", [S13 + "BasicAttack2_OnCast"], 0.6, -12),      # the far claw
    C + "a2_hit": ("tft13", [S13 + "BasicAttack2_OnHit"], 0.6, -10),
    C + "p": ("tft13", [S13 + "CritAttack_OnCast"], 0.8, -10),         # an ambush crit (attack or skill)
    C + "p_hit": ("tft13", [S13 + "CritAttack_OnHit"], 0.8, -8),
    C + "q": ("tft13", [S13 + "Spell_OnCast"], 1.2, -9),               # the leap
    C + "q_vo": ("tft13_vo", ["Play_vo_TFT13_GremlinSpell_OnCast"], 2.0, -3),
    C + "q_land": ("Khazix", ["Play_sfx_Khazix_KhazixE_hit"], 0.9, -10),
    C + "q_hit": ("tft13", [S13 + "Spell_OnHit"], 1.0, -8),            # each of the three slashes
    C + "e": ("Khazix", ["Play_sfx_Khazix_KhazixQ_OnCast"], 0.8, -10),  # the rip
    C + "e_hit": ("Khazix", ["Play_sfx_Khazix_KhazixQ_OnHit"], 0.9, -9),
    C + "e_shred": ("Twitch", ["Play_sfx_Twitch_TwitchExpunge_OnHit"], 0.9, -11),   # the armour torn off
    C + "r": ("Khazix", ["Play_sfx_Khazix_KhazixR_OnCast"], 1.4, -9),   # into the scrap frenzy
    C + "r_leap": ("Khazix", ["Play_sfx_Khazix_KhazixE_OnCast"], 0.8, -11),
    C + "r_hit": ("MasterYi", ["Play_sfx_MasterYi_AlphaStrike_hit"], 0.8, -9),
    C + "r_end": ("Rengar", ["Play_sfx_Rengar_RengarQEmp_OnCast"], 1.0, -8),
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
    ap.add_argument("--lol", required=True, help="the WeGame client's League of Legends folder (Kha'Zix, Twitch, ...)")
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
