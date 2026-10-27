r"""Pull Kobuko's sounds out of the local League of Legends install (the Riot client).

    python tools/lol/extract_kobuko.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

His own TFT sounds (the user: 「音效什么都要自己找」), all from the Riot client's Map22 banks, found by the sets' naming and
the events his skin bins name (2026-10-27). Set 15 (MODE_TFT_Set15_Champs_SFX, the look we draw): his palm strike and its
hit, the heavy crit strike, the golden shield (Play_sfx_TFT15_KobukoShield_buffactviate - Riot's spelling), the stun,
the mentor knock-up and the mentor slam. Set 14 (MODE_TFT_Set14_Champs_SFX, his cyber-boss self): the "second phase"
power-up (KobukoSpell_buffactivate), the leap's wind-up (Spell_buffcast) and the big hit (Spell_hit_big). His voice: set
14's spell call in MODE_TFT_Set14_Champs_VO (the en_US variant 0, the longest; WeGame has no TFT voice banks).
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
C = "tft_kobuko_sfx_"
S15 = "Play_sfx_TFT15_Kobuko"
S14 = "Play_sfx_TFT14_Kobuko"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("tft15", [S15 + "BasicAttack_OnCast"], 0.6, -12),
    C + "a_hit": ("tft15", [S15 + "BasicAttack_OnHit"], 0.6, -11),
    C + "p": ("tft14", [S14 + "Spell_buffactivate"], 1.6, -8),            # the second phase: enraged
    C + "q": ("tft15", [S15 + "Shield_buffactviate"], 1.2, -10),          # the golden shield
    C + "q_hit": ("tft15", [S15 + "CritAttack_OnHit"], 0.8, -9),          # the empowered palm
    C + "q_stun": ("tft15", [S15 + "Spell_stun"], 1.0, -11),
    C + "e": ("tft15", [S15 + "CritAttack_OnCast"], 0.8, -10),            # the pounce
    C + "e_hit": ("tft15", [S15 + "Spell_Mentor_knockup"], 1.2, -9),
    C + "r": ("tft14", [S14 + "Spell_buffcast"], 1.2, -10),               # the leap
    C + "r_slam": ("tft15", [S15 + "Spell_Mentor_slam"], 1.6, -7),
    C + "r_hit": ("tft14", [S14 + "Spell_hit_big"], 1.2, -8),
    C + "vo": ("tft14_vo", ["Play_vo_TFT14_KobukoSpell_OnCast"], 3.0, -3, 0),   # his battle cry: the longest
}
SFX = "assets/sounds/wwise2016/sfx/shared/mode_tft_set{set}_champs_sfx_"
VO = "assets/sounds/wwise2016/vo/en_us/shared/mode_tft_set{set}_champs_vo_"
SHIPPING = ("Game", "DATA", "FINAL", "Maps", "Shipping")


def map22_banks(w, stem):
    """A Map22 bank pair (events + audio, the wpk too when there is one)."""
    audio = w.read_path(stem + "audio.bnk")
    media = dict(bnk_media(audio))
    if w.has(stem + "audio.wpk"):
        media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
    return SoundBanks([w.read_path(stem + "events.bnk"), audio], media)


def banks_of(src, a, cache):
    """A source's banks (events + audio), read once: tftNN = that set's sfx, tftNN_vo = its en_US voice."""
    if src in cache:
        return cache[src]
    if src.endswith("_vo"):
        w = Wad(os.path.join(a.riot, *SHIPPING, "Map22.en_US.wad.client"))
        cache[src] = map22_banks(w, VO.format(set=src[3:5]))
    else:
        w = Wad(os.path.join(a.riot, *SHIPPING, "Map22.wad.client"))
        cache[src] = map22_banks(w, SFX.format(set=src[3:]))
    return cache[src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22 with sets 14 / 15)")
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
