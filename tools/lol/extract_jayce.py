r"""Pull Jayce's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_jayce.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_milio.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Jayce.wad.client and Jayce.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in skin0.bin, listed with %TEMP%/jy_work/sndprobe.py; one clear variant of each, lengths from
%TEMP%/jy_work/vprobe.py): the hammer JayceBasicAttack_OnCast / _OnHit; the cannon JayceRangedAttack_OnMissileLaunch /
_OnHit and Hyper Charge's shot JayceHyperChargeRangedAttack_OnMissileLaunch; the shred shot JaycePassiveRangedAttack_hit;
To the Skies JayceToTheSkies_OnCast / _hit; Shock Blast JayceShockBlastMis_OnMissileLaunch / _hit, through the gate
JayceShockBlastWallMis_OnMissileLaunch / _hit and JayceAccelerationGate_OnCast; Thundering Blow JayceThunderingBlow_OnCast
/ _OnHit; Lightning Field JayceStaticField_OnCast; Hyper Charge JayceHyperCharge_OnCast; the turns JayceStanceHtG_OnCast
(to the cannon) and JayceStanceGtH_OnCast (to the hammer). Voice: JayceToTheSkies_cast3D, JayceShockBlast_cast3D,
JayceThunderingBlow_cast3D, JayceStanceHtG_cast3D, JayceStanceGtH_cast3D, JayceShockBlastWallSound_OnBuffActivate (the
ult). Lightning Field, Hyper Charge and the gate have no voice event of their own. Clip names differ from the sound names
(league_jayce_sfx_*, memory vo-clip-names).
Icons: JayceQ_Melee (To the Skies, the default form's Q) = skill, JayceE_Melee (Thundering Blow, skill2's first spell) =
skill2, JayceE_Ranged (Acceleration Gate, the ult's gate shot) = ult; the cannon's Q / W, the hammer's W, both R
icons and the passive are written too (league_jayce_cq / _cw / _w / _r_cannon / _r_hammer / _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/jayce/skins/base/jayce_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/jayce/skins/base/jayce_base_vo_"  # same in every language
P = "Play_sfx_Jayce_Jayce"
V = "Play_vo_Jayce_Jayce"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_jayce_sfx_a_swing": (P + "BasicAttack_OnCast", 345019387, 0.6, -13),
    "league_jayce_sfx_a_hit": (P + "BasicAttack_OnHit", 694346607, 0.8, -12),
    "league_jayce_sfx_c_shot": (P + "RangedAttack_OnMissileLaunch", 164858832, 0.55, -13),
    "league_jayce_sfx_c_hit": (P + "RangedAttack_OnHit", 997434646, 0.6, -13),
    "league_jayce_sfx_h_shot": (P + "HyperChargeRangedAttack_OnMissileLaunch", 355881247, 0.6, -12),
    "league_jayce_sfx_shred": (P + "PassiveRangedAttack_hit", 454280872, 1.4, -12),
    "league_jayce_sfx_q_leap": (P + "ToTheSkies_OnCast", 680243973, 0.6, -11),
    "league_jayce_sfx_q_land": (P + "ToTheSkies_hit", 504065354, 1.4, -10),
    "league_jayce_sfx_q_hit": (P + "BasicAttack_OnHit", 313447979, 0.8, -14),
    "league_jayce_sfx_cq": (P + "ShockBlastMis_OnMissileLaunch", 130386377, 0.9, -11),
    "league_jayce_sfx_cq_boom": (P + "ShockBlastMis_hit", 332479465, 1.4, -10),
    "league_jayce_sfx_cq_hit": (P + "RangedAttack_OnHit", 855867948, 0.6, -15),
    "league_jayce_sfx_gate": (P + "AccelerationGate_OnCast", 673419753, 1.2, -11),
    "league_jayce_sfx_gq": (P + "ShockBlastWallMis_OnMissileLaunch", 78859068, 1.6, -10),
    "league_jayce_sfx_gq_boom": (P + "ShockBlastWallMis_hit", 760263547, 1.8, -9),
    "league_jayce_sfx_e_cast": (P + "ThunderingBlow_OnCast", 403878803, 0.8, -12),
    "league_jayce_sfx_e_blow": (P + "ThunderingBlow_OnHit", 222225550, 1.5, -10),
    "league_jayce_sfx_w_field": (P + "StaticField_OnCast", 721796847, 2.2, -11),
    "league_jayce_sfx_hyper": (P + "HyperCharge_OnCast", 817944486, 1.8, -11),
    "league_jayce_sfx_tf_c": (P + "StanceHtG_OnCast", 768250984, 1.6, -10),
    "league_jayce_sfx_tf_h": (P + "StanceGtH_OnCast", 114452615, 1.6, -10),
    "league_jayce_sfx_vo_q": (V + "ToTheSkies_cast3D", 153050410, 1.6, -6),
    "league_jayce_sfx_vo_cq": (V + "ShockBlast_cast3D", 225445459, 1.0, -6),
    "league_jayce_sfx_vo_e": (V + "ThunderingBlow_cast3D", 587658086, 1.0, -6),
    "league_jayce_sfx_vo_tf_c": (V + "StanceHtG_cast3D", 1691921322, 2.0, -6),
    "league_jayce_sfx_vo_tf_h": (V + "StanceGtH_cast3D", 434527006, 1.6, -6),
    "league_jayce_sfx_vo_r": (V + "ShockBlastWallSound_OnBuffActivate", 1084376326, 1.4, -6),
}
I = "ASSETS/Characters/Jayce/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_jayce_skill": I + "JayceQ_Melee.dds",
    "league_jayce_skill2": I + "JayceE_Melee.dds",
    "league_jayce_ult": I + "JayceE_Ranged.dds",
    "league_jayce_cq": I + "JayceQ_Ranged.dds",
    "league_jayce_w": I + "JayceW_Melee.dds",
    "league_jayce_cw": I + "JayceW_Ranged.dds",
    "league_jayce_r_cannon": I + "JayceR_Melee.dds",
    "league_jayce_r_hammer": I + "JayceR_Ranged.dds",
    "league_jayce_passive": I + "Jayce_Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Jayce.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Jayce.{args.lang}.wad.client"))
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
