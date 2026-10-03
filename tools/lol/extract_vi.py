"""Pull Vi's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_vi.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Vi.wad.client and Vi.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

Her events in the base bank: ViBasicAttack_OnHit (one of 16 punches), ViWBuff_hit_champ (Denting Blows' third hit),
ViPassiveBuff_OnBuffActivate (Blast Shield; a 24 s loop, its first 0.9 s), ViQ_OnCast (the charge), ViQMissile_OnMissile
Launch (the dash), ViQ_hit_champ (the stop on a champion) and ViQ_hit_minion (whatever she passes), ViE_OnCast (the
gauntlet arming), ViEAttack_missilelaunch (the blast cone), ViR_OnCast, ViRKnockback_OnBuffActivate (the ones she knocks
aside) and ViRDunkTarget_land's start (the slam). Voice: Q (Spell3DQ2Cast), the E punch (ViEAttack_cast3D) and a battle
cry for R (Attack2DGeneral).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/vi/skins/base/vi_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/vi/skins/base/vi_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_vi_sfx_attack_hit": ("Play_sfx_Vi_ViBasicAttack_OnHit", 136644305, 0.5, -12),
    "league_vi_sfx_w_proc": ("Play_sfx_Vi_ViWBuff_hit_champ", 559770654, 1.2, -8),
    "league_vi_sfx_bs_on": ("Play_sfx_Vi_ViPassiveBuff_OnBuffActivate", 1015145463, 0.9, -10),
    "league_vi_sfx_q_charge": ("Play_sfx_Vi_ViQ_OnCast", 47775919, 1.3, -9),
    "league_vi_sfx_q_go": ("Play_sfx_Vi_ViQMissile_OnMissileLaunch", 178105554, 1.2, -8),
    "league_vi_sfx_q_stop": ("Play_sfx_Vi_ViQ_hit_champ", 338741063, 1.6, -5),
    "league_vi_sfx_q_hit": ("Play_sfx_Vi_ViQ_hit_minion", 80201791, 0.5, -12),
    "league_vi_sfx_e_cast": ("Play_sfx_Vi_ViE_OnCast", 914244032, 1.0, -10),
    "league_vi_sfx_e_punch": ("Play_sfx_Vi_ViEAttack_missilelaunch", 688639269, 1.0, -7),
    "league_vi_sfx_e_hit": ("Play_sfx_Vi_ViQ_hit_minion", 51205834, 0.5, -12),
    "league_vi_sfx_r_cast": ("Play_sfx_Vi_ViR_OnCast", 836905022, 1.6, -6),
    "league_vi_sfx_r_side": ("Play_sfx_Vi_ViRKnockback_OnBuffActivate", 173547506, 0.5, -10),
    "league_vi_sfx_r_hit": ("Play_sfx_Vi_ViRDunkTarget_land", 86668507, 1.6, -4),
    "league_vi_vo_q": ("Play_vo_Vi_Spell3DQ2Cast", 1625294817, 0.8, -2),
    "league_vi_vo_e": ("Play_vo_Vi_ViEAttack_cast3D", 1419620073, 0.8, -2),
    "league_vi_vo_r": ("Play_vo_Vi_Attack2DGeneral", 1664228626, 2.0, -3),
}
ICONS = {  # TFM2 slot -> Riot icon (Denting Blows and Blast Shield ride on the attack and the hits)
    "league_vi_skill": "ASSETS/Characters/Vi/HUD/Icons2D/ViQ.dds",
    "league_vi_skill2": "ASSETS/Characters/Vi/HUD/Icons2D/ViE.dds",
    "league_vi_ult": "ASSETS/Characters/Vi/HUD/Icons2D/ViR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Vi.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Vi.{args.lang}.wad.client"))
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
            print(f"{name:34s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:34s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
