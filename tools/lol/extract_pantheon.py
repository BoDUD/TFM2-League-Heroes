r"""Pull Pantheon's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_pantheon.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_kalista.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Pantheon.wad.client and Pantheon.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in skin0.bin, listed with a probe of the base skin's bins): the thrust PantheonBasicAttack_OnCast /
_OnHit, empowered W's thrusts PantheonWEmpoweredAttack_hit_vfx; Mortal Will ready PantheonQ_buffactivate_empowered_vfx;
Comet Spear's tap PantheonQTap_cast_empowered_lua (the whoosh) and hit PantheonQTap_hit_vfx, its hold
PantheonQ_buffactivate_vfx and throw PantheonQMissile_missilecast_lua; Shield Vault's leap (no cast sound of its own: the
crit's whoosh PantheonCritAttack_OnCast) and slam PantheonW_hit; Aegis Assault PantheonE_OnCast and its slam
PantheonEShieldSlam_hit_lua; Grand Starfall's crouch PantheonR_buffactivate_vfx, the leap PantheonR_OnCast_stereo, the
spear's impact PantheonR_impact_vfx and the landing PantheonR_land_vfx. Voice: PantheonQTap_cast3D, PantheonW_cast3D,
Attack2DGeneral (E has no line), PantheonR_cast3D twice (the crouch, the leap).
Icons: Pantheon_Q1 (Comet Spear) = skill, Pantheon_W1 (Shield Vault) = skill2, Pantheon_R (Grand Starfall) = ult;
E (Aegis Assault, told in skill2's text) and the passive are written too (league_pantheon_e / _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/pantheon/skins/base/pantheon_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/pantheon/skins/base/pantheon_base_vo_"  # same in every language
P = "Play_sfx_Pantheon_Pantheon"
V = "Play_vo_Pantheon_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_pantheon_sfx_a_swing": (P + "BasicAttack_OnCast", 678732111, 0.6, -14),
    "league_pantheon_sfx_a_hit": (P + "BasicAttack_OnHit", 15461235, 0.6, -14),
    "league_pantheon_sfx_w_tri": (P + "WEmpoweredAttack_hit_vfx", 53923318, 0.8, -12),
    "league_pantheon_sfx_p_ready": (P + "Q_buffactivate_empowered_vfx", 373734925, 1.0, -13),
    "league_pantheon_sfx_q_tap": (P + "QTap_cast_empowered_lua", 181528245, 0.9, -11),
    "league_pantheon_sfx_q_hit": (P + "QTap_hit_vfx", 159441603, 0.9, -11),
    "league_pantheon_sfx_q_hold": (P + "Q_buffactivate_vfx", 849927174, 1.0, -12),
    "league_pantheon_sfx_q_throw": (P + "QMissile_missilecast_lua", 983799119, 1.2, -11),
    "league_pantheon_sfx_w": (P + "CritAttack_OnCast", 123097416, 0.8, -12),
    "league_pantheon_sfx_w_hit": (P + "W_hit", 1065376863, 1.0, -10),
    "league_pantheon_sfx_e": (P + "E_OnCast", 725704520, 1.6, -11),
    "league_pantheon_sfx_e_bash": (P + "EShieldSlam_hit_lua", 1069232639, 1.2, -10),
    "league_pantheon_sfx_r": (P + "R_buffactivate_vfx", 685244675, 2.0, -11),
    "league_pantheon_sfx_r_leap": (P + "R_OnCast_stereo", 3911959, 1.6, -10),
    "league_pantheon_sfx_r_spear": (P + "R_impact_vfx", 427591306, 1.6, -10),
    "league_pantheon_sfx_r_land": (P + "R_land_vfx", 931137241, 2.0, -9),
    "league_pantheon_sfx_vo_q": (V + "PantheonQTap_cast3D", 2006392617, 1.6, -6),
    "league_pantheon_sfx_vo_w": (V + "PantheonW_cast3D", 2015952055, 1.6, -6),
    "league_pantheon_sfx_vo_e": (V + "Attack2DGeneral", 648971130, 2.0, -6),
    "league_pantheon_sfx_vo_r": (V + "PantheonR_cast3D", 525248407, 2.6, -6),
    "league_pantheon_sfx_vo_r_leap": (V + "PantheonR_cast3D", 4996106, 2.6, -6),
}
I = "ASSETS/Characters/Pantheon/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_pantheon_skill": I + "Pantheon_Q1.dds",
    "league_pantheon_skill2": I + "Pantheon_W1.dds",
    "league_pantheon_ult": I + "Pantheon_R.dds",
    "league_pantheon_e": I + "Pantheon_E1.dds",
    "league_pantheon_passive": I + "Pantheon_Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Pantheon.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Pantheon.{args.lang}.wad.client"))
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
