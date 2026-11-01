r"""Pull the Sentry's sounds (苍蓝哨戒, Pebbles) out of the local League of Legends install (the Riot client).

    python tools/lol/extract_sentry.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). Set 18 (DA_18_Sentry) names no event and the client ships no set-18 bank;
its skin bin borrows the Rift's SRU_BlueMini, whose Map11 banks (NPC_Map11_BlueMini_SFX events/audio) are empty stubs
(48 / 32 bytes, 2026-11-02): the Blue camp's little stones are silent in League. So it borrows from League's champions,
Champions/<name>.wad.client, event names read from their bins: Vel'Koz's lasers (the bolt, the Life Form Disintegration
Ray for 蔚蓝激光, his Organic Deconstruction research for the magic-resist shred), Viktor's Death Ray for 棱镜扫射 and his
Q charge for 青霸符, Ezreal's Arcane Shift for 裂石跃迁, Taliyah's stones (the halves grinding open, the rubble ring, a
rock wall breaking for its death).
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

C = "tft_sentry_sfx_"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("Velkoz", ["Play_sfx_Velkoz_VelkozBasicAttack_OnCast"], 0.8, -12),            # a bolt from the core
    C + "a_hit": ("Velkoz", ["Play_sfx_Velkoz_VelkozBasicAttack_OnHit"], 0.6, -12),
    C + "p": ("Viktor", ["Play_sfx_Viktor_ViktorQBuff_buffactivate"], 1.0, -14),             # 青霸符: cooldowns cut
    C + "q": ("Velkoz", ["Play_sfx_Velkoz_VelkozR_OnCast"], 2.6, -10),                       # the laser, channelled
    C + "q_hit": ("Velkoz", ["Play_sfx_Velkoz_VelkozR_hit"], 0.6, -14),                      # each tick on the target
    C + "q_shred": ("Velkoz", ["Play_sfx_Velkoz_VelkozP1_buffactivate_champ"], 0.8, -14),    # magic resist down
    C + "q_end": ("Velkoz", ["Play_sfx_Velkoz_VelkozRBeamEnd_buffactivate"], 1.0, -12),
    C + "e": ("Ezreal", ["Play_sfx_Ezreal_EzrealE_OnCast"], 1.0, -10),                       # the blink back
    C + "e_split": ("Taliyah", ["Play_sfx_Taliyah_TaliyahQ_rockswirl_cast"], 0.8, -12),      # the halves part
    C + "e_ring": ("Taliyah", ["Play_sfx_Taliyah_TaliyahE_cast"], 1.2, -10),                 # the rubble left behind
    C + "e_slow": ("Taliyah", ["Play_sfx_Taliyah_TaliyahEMineRumble_buffactivate"], 0.8, -13),
    C + "r": ("Taliyah", ["Play_sfx_Taliyah_TaliyahWSound_cast"], 1.2, -10),                 # the halves grind wide open
    C + "r_charge": ("Viktor", ["Play_sfx_Viktor_ViktorE_OnCast"], 1.2, -9),
    C + "r_beam": ("Viktor", ["Play_sfx_Viktor_ViktorEMissile_missilelaunch_claw"], 2.0, -8),   # the sweep
    C + "r_hit": ("Viktor", ["Play_sfx_Viktor_ViktorEMissile_hit"], 0.8, -12),
    C + "d": ("Taliyah", ["Play_sfx_Taliyah_TaliyahRWallBlowUp_buffactivate"], 2.0, -9),     # the shards fall apart
}


def banks_of(src, a, cache):
    """A champion's base-skin sfx banks (events + audio), read once."""
    if src in cache:
        return cache[src]
    w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Champions", f"{src}.wad.client"))
    stem = f"assets/sounds/wwise2016/sfx/characters/{src.lower()}/skins/base/{src.lower()}_base_sfx_"
    audio = w.read_path(stem + "audio.bnk")
    media = dict(bnk_media(audio))
    if w.has(stem + "audio.wpk"):
        media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
    cache[src] = SoundBanks([w.read_path(stem + "events.bnk"), audio], media)
    return cache[src]


def variants_of(banks, ev):
    """An event's media, by its name or (unnamed) its event id."""
    if isinstance(ev, int):
        return [m for m in dict.fromkeys(banks._resolve(ev, set())) if m in banks.media]
    return banks.event_media(ev)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map11 and the champions)")
    ap.add_argument("--vgmstream", required=True, help="vgmstream-cli.exe")
    a = ap.parse_args()
    out_dir = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out_dir), exist_ok=True)
    cache = {}
    for name, (src, events, max_s, peak, *pick) in CLIPS.items():
        banks = banks_of(src, a, cache)
        event, variants = None, []
        for ev in events:
            variants = variants_of(banks, ev)
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
        print(f"{name:28s} {len(pcm) / sr:4.2f}s  <- {src} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
