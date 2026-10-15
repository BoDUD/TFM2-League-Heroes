r"""Pull Smolder's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_smolder.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_malzahar.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Smolder.wad.client and Smolder.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.

His events (named in skin0.bin / smolder.bin, listed with %TEMP%/sm_work/snd/sndprobe.py; one variant of each, the
lengths from decode_all.py there): the attack SmolderBasicAttack_OnMissileLaunch / _OnHit; Super Scorcher Breath's
SmolderQ_OnMissileLaunch and _OnHit, the tier-1 explosion SmolderQ_aoe_hit, the tier-2 blowback
SmolderQ_blowback_missilelaunch / _blowback_hit, the tier-3 burn SmolderQ3Burn_OnBuffActivate (its first second: the
event is a 14 s loop) and the three tier-up ceremonies SmolderQ_EvolveCeremony1-3_buffactivate; Achooo!'s
SmolderW_OnMissileLaunch (the sneeze), SmolderW_hit_minion (the line's hit) and SmolderW_hit_champ (the explosion); Flap,
Flap, Flap's SmolderE_OnCast, SmolderEAttack_OnMissileLaunch / _OnHit; MMOOOMMMM!'s SmolderR_OnCast, SmolderR_missile (his
mother's flight), SmolderR_MomMissile_OnHit_champion and _self_heal. Voice (zh_CN): SmolderQ_cast3D, SmolderW_cast3D,
SmolderE_cast3D, SmolderR_cast3D and SmolderQUpgrade (the tier-up line). Clip names differ from the sound names
(league_smolder_sfx_*, memory vo-clip-names).
Icons: Icons_Smolder_Q1 = skill (Q), Icons_Smolder_W = skill2 (W, E on its flag), Icons_Smolder_R = ult; E, the passive and
Q's evolved icons Q2-Q4 (tiers 1-3) are written too (README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/smolder/skins/base/smolder_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/smolder/skins/base/smolder_base_vo_"  # same in every language
P = "Play_sfx_Smolder_Smolder"
V = "Play_vo_Smolder_Smolder"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_smolder_sfx_a_cast": (P + "BasicAttack_OnMissileLaunch", 1070593574, 0.6, -13),
    "league_smolder_sfx_a_hit": (P + "BasicAttack_OnHit", 739471383, 0.5, -13),
    "league_smolder_sfx_q_cast": (P + "Q_OnMissileLaunch", 816713947, 0.7, -11),
    "league_smolder_sfx_q_hit": (P + "Q_OnHit", 157525707, 0.9, -11),
    "league_smolder_sfx_q_boom": (P + "Q_aoe_hit", 834309821, 0.9, -10),
    "league_smolder_sfx_q_back": (P + "Q_blowback_missilelaunch", 783007526, 0.6, -11),
    "league_smolder_sfx_q_t2_hit": (P + "Q_blowback_hit", 183515466, 0.6, -13),
    "league_smolder_sfx_q_burn": (P + "Q3Burn_OnBuffActivate", 350886741, 1.0, -14),
    "league_smolder_sfx_p_t1": (P + "Q_EvolveCeremony1_buffactivate", 938935824, 2.5, -9),
    "league_smolder_sfx_p_t2": (P + "Q_EvolveCeremony2_buffactivate", 122212390, 2.5, -9),
    "league_smolder_sfx_p_t3": (P + "Q_EvolveCeremony3_buffactivate", 30963304, 3.0, -9),
    "league_smolder_sfx_w_cast": (P + "W_OnMissileLaunch", 692902358, 1.2, -9),
    "league_smolder_sfx_w_hit": (P + "W_hit_minion", 975325795, 0.6, -13),
    "league_smolder_sfx_w_boom": (P + "W_hit_champ", 455315288, 0.9, -10),
    "league_smolder_sfx_e_cast": (P + "E_OnCast", 661918955, 0.9, -10),
    "league_smolder_sfx_e_shot": (P + "EAttack_OnMissileLaunch", 483271392, 0.45, -15),
    "league_smolder_sfx_e_hit": (P + "EAttack_OnHit", 3074629, 0.35, -15),
    "league_smolder_sfx_r_cast": (P + "R_OnCast", 15173515, 1.6, -8),
    "league_smolder_sfx_r_mom": (P + "R_missile", 432424772, 2.5, -9),
    "league_smolder_sfx_r_hit": (P + "R_MomMissile_OnHit_champion", 608304110, 0.6, -11),
    "league_smolder_sfx_r_heal": (P + "R_MomMissile_self_heal", 159785, 1.0, -10),
    "league_smolder_sfx_vo_q": (V + "Q_cast3D", 1999435637, 1.6, -6),
    "league_smolder_sfx_vo_w": (V + "W_cast3D", 2018962031, 1.6, -6),
    "league_smolder_sfx_vo_e": (V + "E_cast3D", 866616656, 1.6, -6),
    "league_smolder_sfx_vo_r": (V + "R_cast3D", 904650990, 2.0, -6),
    "league_smolder_sfx_vo_up": (V + "QUpgrade", 687324763, 2.0, -6),
}
I = "ASSETS/Characters/Smolder/HUD/Icons2D/Icons_Smolder_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_smolder_skill": I + "Q1.dds",
    "league_smolder_skill2": I + "W.dds",
    "league_smolder_ult": I + "R.dds",
    "league_smolder_e": I + "E.dds",
    "league_smolder_passive": I + "Passive.dds",
    "league_smolder_q2": I + "Q2.dds",
    "league_smolder_q3": I + "Q3.dds",
    "league_smolder_q4": I + "Q4.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Smolder.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Smolder.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (event, mid, max_s, peak) in CLIPS.items():
            variants = banks.event_media(event)
            if mid not in variants:
                sys.exit(f"{event}: media {mid} not found (variants: {variants}) - game patch changed the bank?")
            sr, x = decode(media[mid], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
