r"""Pull Norra's sounds out of a local League of Legends install (TFT keeps no sounds for her anywhere we can read).

    python tools/lol/extract_norra.py --lol "D:\WeGameApps\lol" --vgmstream path\vgmstream-cli.exe

Norra has no voice and no sounds of her own outside TFT set 12, which the client no longer ships (the user: 「音效什么都要
自己找」). So every clip is borrowed from a League champion whose sound fits the move, read (never written) from
Game/DATA/FINAL/Champions/<Champ>.wad.client, the base skin's Wwise events resolved to their media (the first variant),
decoded with vgmstream and written as mono 16-bit WAVs to tft/sound/sfx/ (git-ignored: audio (c) Riot Games):
Zoe's star magic for her bolt and Memory Surge and her bubble popping for a trinket, Bard's chimes for the trinkets and
his portal door for Journey to Nowhere and Threads of Homecoming, his Tempered Fate for the rift of Portalpalooza!, and
Yuumi's (her cat's own) bolts for the threads and the yarn balls - the clips follow Wild Rift's kit (2026-10-26).
"""
import argparse
import os
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_garen import decode, finish, lp  # noqa: E402
from riot import SoundBanks, Wad, bnk_media  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MOD = os.path.join(ROOT, "tft")
C = "tft_norra_sfx_"

# clip name -> (champion, [events to try, first that resolves], max seconds, peak dBFS)
CLIPS = {
    C + "a": ("Zoe", ["Play_sfx_Zoe_ZoeBasicAttack_OnMissileLaunch", "Play_sfx_Zoe_ZoeBasicAttack_OnCast"], 0.6, -10),
    C + "a_hit": ("Zoe", ["Play_sfx_Zoe_ZoeBasicAttack_OnHit"], 0.6, -9),
    # Beloved Trinkets: the keepsakes laid down (Bard's chimes), one bursting on a champion (Zoe's bubble popping)
    C + "p_drop": ("Bard", ["Play_sfx_Bard_BardPChimePickedUp_spin", "Play_sfx_Bard_BardPChimePickedUp"], 1.0, -10),
    C + "p_burst": ("Zoe", ["Play_sfx_Zoe_ZoeEB_pop", "Play_sfx_Zoe_ZoeW_balloonpop"], 0.8, -8),
    # Journey to Nowhere: the portal that swallows (Bard's door opening)
    C + "w": ("Bard", ["Play_sfx_Bard_BardECreateDoor_OnBuffActivate", "Play_sfx_Bard_BardE_OnCast"], 1.2, -7),
    # Memory Surge: the gathering, the bolt flung, its blast
    C + "q": ("Zoe", ["Play_sfx_Zoe_ZoeQ_OnCast", "Play_sfx_Zoe_ZoeQMissile_OnMissileCast"], 0.9, -9),
    C + "q_fire": ("Zoe", ["Play_sfx_Zoe_ZoeQMissile_OnMissileLaunch", "Play_sfx_Zoe_ZoeQ_OnCast"], 0.9, -8),
    C + "q_blast": ("Zoe", ["Play_sfx_Zoe_ZoeQMis2_big_hit", "Play_sfx_Zoe_ZoeQMis2_OnHit"], 1.2, -6),
    # Threads of Homecoming: the two portals appearing (Bard's door exit), the threads lashing (Yuumi's projectile)
    C + "e": ("Bard", ["Play_sfx_Bard_BardECreateDoor_exitappear", "Play_sfx_Bard_BardECreateDoor_OnBuffActivate"], 1.0, -8),
    C + "e_hit": ("Yuumi", ["Play_sfx_Yuumi_YuumiQskillshot_OnMissileLaunch", "Play_sfx_Yuumi_YuumiQ_OnCast"], 0.8, -8),
    # Portalpalooza!: the wind-up, the rift opening, each volley of yarn balls, a ball's hit (Yuumi's Final Chapter)
    C + "r": ("Bard", ["Play_sfx_Bard_BardR_windup_cast", "Play_sfx_Bard_BardR_OnCast"], 1.5, -7),
    C + "r_open": ("Bard", ["Play_sfx_Bard_BardR_OnCast", "Play_sfx_Bard_BardR_explo"], 1.5, -6),
    C + "r_ball": ("Yuumi", ["Play_sfx_Yuumi_YuumiRmissile_OnMissileCast"], 1.0, -8),
    C + "r_hit": ("Yuumi", ["Play_sfx_Yuumi_YuumiRmissile_hitregular", "Play_sfx_Yuumi_YuumiRmissile_OnHit"], 0.8, -8),
}


def banks_of(champs_dir, champ, cache):
    """A champion's base-skin sfx banks (events + audio), read once."""
    if champ not in cache:
        w = Wad(os.path.join(champs_dir, f"{champ}.wad.client"))
        bank = f"assets/sounds/wwise2016/sfx/characters/{champ.lower()}/skins/base/{champ.lower()}_base_sfx_"
        audio = w.read_path(bank + "audio.bnk")
        cache[champ] = SoundBanks([w.read_path(bank + "events.bnk"), audio], dict(bnk_media(audio)))
    return cache[champ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--vgmstream", required=True, help="vgmstream-cli.exe")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    out_dir = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out_dir), exist_ok=True)
    cache = {}
    for name, (champ, events, max_s, peak) in CLIPS.items():
        banks = banks_of(champs, champ, cache)
        event, variants = None, []
        for ev in events:
            variants = banks.event_media(ev)
            if variants:
                event = ev
                break
        if not variants:
            sys.exit(f"{name}: none of {events} resolves in {champ} - game patch changed the bank?")
        sr, x = decode(banks.media[variants[0]], args.vgmstream)
        pcm = finish(x, sr, max_s, peak)
        with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        print(f"{name:28s} {len(pcm) / sr:4.2f}s  <- {champ} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
