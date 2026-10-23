r"""Pull Azir's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_azir.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

The Aurora route (extract_aurora.py): reads (never writes) Game/DATA/FINAL/Champions/Azir.wad.client and
Azir.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event unless
a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Azir_Azir, the event names his skin bins name): his own attack's cast and hit; a
soldier rising (W's spawn) and a soldier's stab; Conquering Sands' cast, the soldiers' landing and their hit; Shifting
Sands' cast, the knock-up on arrival and the hit; Emperor's Divide's cast, the wall rising and the bump; the Sun Disc
(the obelisk) rising and its shot (the add-on's). Voice (Play_vo_Azir_): AzirQ_cast3D, AzirE_cast3D, AzirR_cast3D.
Icons (assets/characters/azir/hud/icons2d/): azir_q = skill (Conquering Sands), azir_e = skill2 (Shifting Sands),
azir_r = ult (Emperor's Divide), azir_w = Arise! (league_azir_w), azir_passive = Shurima's Legacy (league_azir_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/azir/skins/base/azir_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/azir/skins/base/azir_base_vo_"  # same in every language
P = "Play_sfx_Azir_Azir"
V = "Play_vo_Azir_"
C = "league_azir_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the sfx at the level Aurora's got, the voice as the others'
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast", P + "BasicAttack2_OnCast"], None, 0.7, -8),
    C + "a_hit": ([P + "BasicAttack_OnHit", P + "BasicAttack2_OnHit"], None, 0.8, -7),
    C + "s_spawn": ([P + "WSpawnSound_OnBuffCast", P + "SandSoldier_buffcast"], None, 1.0, -7),
    C + "s_stab": ([P + "BasicAttackSoldier_cast1", P + "SoldierMissile_hit_champ"], None, 0.7, -8),
    C + "q": ([P + "Q_OnCast"], None, 1.2, -6),
    C + "q_land": ([P + "SandSoldier_buffcast", P + "WSpawnSound_buffdeactivate"], None, 1.0, -6),
    C + "q_hit": ([P + "SoldierMissile_hit_champ", P + "BasicAttackSoldier_OnHit"], None, 0.9, -6),
    C + "e": ([P + "E_OnBuffCast", P + "E_missilelaunch"], None, 1.2, -6),
    C + "e_land": ([P + "EKnockup_OnBuffCast", P + "EShield_OnBuffActivate"], None, 1.2, -5),
    C + "e_hit": ([P + "BasicAttackSoldier_OnHit", P + "SoldierMissile_hit_minion"], None, 0.9, -6),
    C + "r": ([P + "RSpawnSound_OnBuffCast"], None, 1.5, -5),
    C + "r_wall": ([P + "RSpawnSound_OnBuffActivate", P + "RSpawnSound_OnBuffDeactivate"], None, 2.0, -4),
    C + "r_hit": ([P + "RBump_OnBuffCast"], None, 1.0, -5),
    C + "d_rise": ([P + "Obelisk_buffcast", P + "ObeliskSound_OnBuffCast"], None, 2.0, -5),
    C + "d_beam": ([P + "Obelisk_buffactivate", "Play_sfx_AzirSoldier_AzirSoldierMissile_OnMissileLaunch"], None, 1.0, -7),
    C + "vo_q": ([V + "AzirQ_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "AzirE_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "AzirR_cast3D"], None, 3.0, -6),
}
I = "assets/characters/azir/hud/icons2d/azir_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_azir_skill": I + "q.dds",
    "league_azir_skill2": I + "e.dds",
    "league_azir_ult": I + "r.dds",
    "league_azir_w": I + "w.dds",
    "league_azir_passive": I + "passive.dds",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Azir.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Azir.{args.lang}.wad.client"))
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
