"""Pull Yone's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_yone.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Yone.wad.client and Yone.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

His spells go by their own names in the base bins: YoneQ / YoneQ3 = Mortal Steel and its dash
(YoneQ3Ready = Gathering Storm at two stacks), YoneW = Spirit Cleave (YonePShield = its shield), YoneE =
Soul Unbound (YoneE_mark on each champion struck, YoneE_return_cast as the spirit snaps back, YoneE_hit for
the repeated damage), YoneR = Fate Sealed. Every zh_CN spell line differs from the en_US one (no
untranslated shouts); the shortest variant of each is taken, since TFM2 casts come quickly.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/yone/skins/base/yone_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/yone/skins/base/yone_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_yone_sfx_attack_hit": ("Play_sfx_Yone_YoneBasicAttack_OnHit", 32292976, 0.6, -6),
    "league_yone_sfx_attack2_hit": ("Play_sfx_Yone_YoneBasicAttack2_OnHit", 447192276, 0.8, -5),
    "league_yone_sfx_q_cast": ("Play_sfx_Yone_YoneQ_OnCast", 115778047, 0.9, -5),
    "league_yone_sfx_q_hit": ("Play_sfx_Yone_YoneQ_hit", 528184656, 0.8, -5),
    "league_yone_sfx_q_ready": ("Play_sfx_Yone_YoneQ3Ready_OnBuffActivate", 758058148, 1.2, -8),
    "league_yone_sfx_q3_cast": ("Play_sfx_Yone_YoneQ3_OnCast", 667080352, 1.4, -4),
    "league_yone_sfx_q3_hit": ("Play_sfx_Yone_YoneQ3_hit", 144577483, 1.1, -4),
    "league_yone_sfx_w_cast": ("Play_sfx_Yone_YoneW_OnCast", 1031367120, 1.2, -5),
    "league_yone_sfx_w_hit": ("Play_sfx_Yone_YoneW_hit", 117104795, 0.8, -6),
    "league_yone_sfx_shield": ("Play_sfx_Yone_YonePShield_buffactivate", 197299419, 1.0, -8),
    "league_yone_sfx_e_cast": ("Play_sfx_Yone_YoneE_cast", 852026027, 1.2, -4),
    "league_yone_sfx_e_mark": ("Play_sfx_Yone_YoneE_mark_buffactivate", 557545750, 0.8, -8),
    "league_yone_sfx_e_return": ("Play_sfx_Yone_YoneE_return_cast", 708762305, 1.1, -4),
    "league_yone_sfx_e_hit": ("Play_sfx_Yone_YoneE_hit", 386342691, 0.7, -5),
    "league_yone_sfx_r_cast": ("Play_sfx_Yone_YoneR_OnCast", 57735016, 1.3, -3),
    "league_yone_sfx_r_dash": ("Play_sfx_Yone_YoneR_cast_dash", 583920156, 1.2, -4),
    "league_yone_sfx_r_hit": ("Play_sfx_Yone_YoneR_hit_initial", 976342648, 1.4, -3),
    "league_yone_vo_q": ("Play_vo_Yone_YoneQ_cast3D", 1187090324, 1.6, -2),
    "league_yone_vo_q3": ("Play_vo_Yone_YoneQ3_cast3D", 97285779, 1.4, -2),
    "league_yone_vo_w": ("Play_vo_Yone_YoneW_cast3D", 512584525, 1.4, -2),
    "league_yone_vo_e": ("Play_vo_Yone_YoneE_cast3D", 1168756081, 2.6, -2),
    "league_yone_vo_e_end": ("Play_vo_Yone_Spell3DEEnd", 2069926360, 1.2, -2),
    "league_yone_vo_r": ("Play_vo_Yone_YoneR_cast3D", 1545931167, 1.6, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Soul Unbound rides on Spirit Cleave, Way of the Hunter is the attack: no slots)
    "league_yone_skill": "ASSETS/Characters/Yone/HUD/Icons2D/YoneQ.dds",
    "league_yone_skill2": "ASSETS/Characters/Yone/HUD/Icons2D/YoneW.dds",
    "league_yone_ult": "ASSETS/Characters/Yone/HUD/Icons2D/YoneR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Yone.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Yone.{args.lang}.wad.client"))
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
