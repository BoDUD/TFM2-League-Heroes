r"""Pull Illaoi's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_illaoi.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Hwei route (extract_hwei.py): reads (never writes) Game/DATA/FINAL/Champions/Illaoi.wad.client and
Illaoi.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event unless
a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Illaoi_Illaoi, the event names her skin bins name): the attack's cast and hit; a
tentacle spawning and its hit on a champion; Harsh Lesson's cast and its leap's hit; Test of Spirit's cast, the ghost
tentacle's hit and the Vessel; Leap of Faith's cast, its smash and its hit. Voice (Play_vo_Illaoi_): Spell3DWHit,
IllaoiE_cast3D, IllaoiR_cast3D.
Icons: illaoi_w = skill (Harsh Lesson), illaoi_e = skill2 (Test of Spirit), illaoi_r = ult (Leap of Faith), illaoi_q =
Tentacle Smash (league_illaoi_q), illaoi_p = Prophet of an Elder God (league_illaoi_passive).
"""
import argparse
import io
import os
import sys
import wave

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_garen import decode, finish, lp  # noqa: E402
from riot import SoundBanks, Wad, bnk_media, parse_wpk  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MOD = os.path.join(ROOT, "league")
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/illaoi/skins/base/illaoi_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/illaoi/skins/base/illaoi_base_vo_"  # same in every language
P = "Play_sfx_Illaoi_Illaoi"
V = "Play_vo_Illaoi_"
C = "league_illaoi_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the sfx at the level Qiyana's and Hwei's got, the voice as the others'
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.7, -8),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -7),
    C + "p_spawn": ([P + "TentacleSpawn_buffactivate", P + "TentacleSpawn_buffactivate5"], None, 1.2, -7),
    C + "p_hit": ([P + "TentacleAttack_champ_hit", P + "TentacleAttack_Ground_Hit"], None, 0.9, -7),
    C + "w": ([P + "W_OnCast", P + "W_OnBuffActivate"], None, 1.0, -6),
    C + "w_hit": ([P + "WAttack_OnBuffCast", P + "WAttack_OnCast"], None, 1.0, -5),
    C + "e": ([P + "E_OnCast", P + "EMis_OnMissileLaunch"], None, 1.2, -6),
    C + "e_hit": ([P + "EMis_OnHit", P + "E_spirit_hit"], None, 1.2, -5),
    C + "e_break": ([P + "EVessel_buffactivate", P + "ESpiritExpire_buffdeactivate"], None, 1.5, -5),
    C + "r": ([P + "R_OnCast3", P + "R_OnBuffActivate"], None, 1.5, -5),
    C + "r_slam": ([P + "R2_OnBuffCast", P + "R_hit"], 1, 2.0, -4),   # R_hit's second variant: not r_hit's
    C + "r_hit": ([P + "R_hit"], None, 1.0, -6),
    C + "vo_w": ([V + "Spell3DWHit"], None, 2.5, -6),
    C + "vo_e": ([V + "IllaoiE_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "IllaoiR_cast3D"], None, 3.0, -6),
}
I = "assets/characters/illaoi/hud/icons2d/illaoi_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_illaoi_skill": I + "w.dds",
    "league_illaoi_skill2": I + "e.dds",
    "league_illaoi_ult": I + "r.dds",
    "league_illaoi_q": I + "q.dds",
    "league_illaoi_passive": I + "p.dds",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Illaoi.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Illaoi.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            event, variants = None, []
            for ev in events:
                variants = banks.event_media(ev)
                if variants:
                    event = ev
                    break
            if not variants:
                sys.exit(f"{name}: none of {events} resolves - game patch changed the bank?")
            m = variants[0] if mid is None else variants[min(mid, len(variants) - 1)]
            sr, x = decode(media[m], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event} ({len(variants)} variants)")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
