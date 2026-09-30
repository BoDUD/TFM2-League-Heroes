"""Pull Ahri's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_ahri.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Ahri.wad.client and Ahri.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Her spells in the base bins: AhriQ = Orb of Deception (AhriQMissile out, AhriQDamage_hit on each unit,
AhriQReturnMissile back, AhriQReturnDamage_hit the true-damage hit), AhriW = Fox-Fire (AhriW_OnCast, one
AhriWDamageMissile per fire), AhriE = Charm (AhriEMissile, a second voice line on the hit, a giggle),
AhriR = Spirit Rush (AhriR_OnCast each dash, AhriRMissile the essence bolts), the passive's heal
(AhriPassive_minionheal). Every spell voice line differs between the zh_CN and en_US banks (translated);
a short one of each is taken.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/ahri/skins/base/ahri_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/ahri/skins/base/ahri_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_ahri_sfx_attack_shot": ("Play_sfx_Ahri_AhriBasicAttack_OnMissileLaunch", 633926029, 0.7, -8),
    "league_ahri_sfx_attack_hit": ("Play_sfx_Ahri_AhriBasicAttack_OnHit", 107563738, 0.5, -6),
    "league_ahri_sfx_q_cast": ("Play_sfx_Ahri_AhriQMissile_OnMissileLaunch", 523172130, 1.1, -5),
    "league_ahri_sfx_q_hit": ("Play_sfx_Ahri_AhriQDamage_hit", 334740066, 0.7, -6),
    "league_ahri_sfx_q_return": ("Play_sfx_Ahri_AhriQReturnMissile_OnMissileLaunch", 269587611, 1.2, -6),
    "league_ahri_sfx_q_true": ("Play_sfx_Ahri_AhriQReturnDamage_hit", 81644229, 0.5, -5),
    "league_ahri_sfx_w_cast": ("Play_sfx_Ahri_AhriW_OnCast", 93355387, 1.3, -5),
    "league_ahri_sfx_w_fire": ("Play_sfx_Ahri_AhriWDamageMissile_missilelaunch", 600109118, 0.7, -8),
    "league_ahri_sfx_w_hit": ("Play_sfx_Ahri_AhriWDamageMissile_hit", 170548952, 0.8, -7),
    "league_ahri_sfx_e_cast": ("Play_sfx_Ahri_AhriE_OnCast", 850666001, 1.0, -5),
    "league_ahri_sfx_e_hit": ("Play_sfx_Ahri_AhriEMissile_hit", 551030173, 1.3, -4),
    "league_ahri_sfx_r_cast": ("Play_sfx_Ahri_AhriR_OnCast", 460339781, 1.0, -4),
    "league_ahri_sfx_r_bolt": ("Play_sfx_Ahri_AhriRMissile_OnMissileLaunch", 765120000, 0.8, -8),
    "league_ahri_sfx_r_hit": ("Play_sfx_Ahri_AhriRMissile_OnHit", 299482429, 0.8, -7),
    "league_ahri_sfx_heal": ("Play_sfx_Ahri_AhriPassive_minionheal_buffactivate", 704313670, 1.1, -6),
    "league_ahri_vo_w": ("Play_vo_Ahri_AhriW_cast3D", 883693965, 1.2, -2),
    "league_ahri_vo_e": ("Play_vo_Ahri_AhriE_cast3D", 367926320, 1.0, -2),
    "league_ahri_vo_e_hit": ("Play_vo_Ahri_AhriEMissile_hit3D", 167001001, 1.2, -2),
    "league_ahri_vo_r": ("Play_vo_Ahri_AhriR_cast3D", 1261324591, 1.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Fox-Fire rides on Orb of Deception, Essence Theft on the attack)
    "league_ahri_skill": "ASSETS/Characters/Ahri/HUD/Icons2D/Icons_Ahri_Q.dds",
    "league_ahri_skill2": "ASSETS/Characters/Ahri/HUD/Icons2D/Icons_Ahri_E.dds",
    "league_ahri_ult": "ASSETS/Characters/Ahri/HUD/Icons2D/Icons_Ahri_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Ahri.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Ahri.{args.lang}.wad.client"))
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
            print(f"{name:32s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:32s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
