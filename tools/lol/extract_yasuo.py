"""Pull Yasuo's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_yasuo.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Yasuo.wad.client and Yasuo.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in the champion bins. Q1, Q2 and Q3 share one set of sword swings; the Q3 whirlwind
has its own launch and hit. Voice lines, compared with the en_US bank: the Q1 and E shouts are the same
recordings in both languages (wordless); both zh_CN Q3 lines are Chinese takes of "Hasaki", and the one
whose rhythm matches the English take best is used; the R line is the one shared with en_US ("Sorye ge
ton"). Wind Wall rides on the passive in TFM2, so it gets its cast sound but no voice.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/yasuo/skins/base/yasuo_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/yasuo/skins/base/yasuo_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_yasuo_sfx_attack_hit": ("Play_sfx_Yasuo_YasuoBasicAttack_OnHit", 268183591, 0.6, -4),
    "league_yasuo_sfx_q_cast": ("Play_sfx_Yasuo_YasuoQW_OnCast", 179472225, 0.8, -4),
    "league_yasuo_sfx_q_hit": ("Play_sfx_Yasuo_YasuoQ_hit", 72091670, 0.9, -4),
    "league_yasuo_sfx_q_ready": ("Play_sfx_Yasuo_YasuoQ3W_OnBuffActivate", 294804316, 1.2, -8),
    "league_yasuo_sfx_q3_cast": ("Play_sfx_Yasuo_YasuoQ3W_missilelaunch", 706858599, 1.4, -3),
    "league_yasuo_sfx_q3_hit": ("Play_sfx_Yasuo_YasuoQ3W_hit", 153026395, 1.0, -4),
    "league_yasuo_sfx_eq": ("Play_sfx_Yasuo_YasuoEQComboSoundHit_OnBuffActivate", 558685910, 1.0, -3),
    "league_yasuo_sfx_e_cast": ("Play_sfx_Yasuo_YasuoDashWrapper_cast", 591673493, 1.0, -4),
    "league_yasuo_sfx_e_hit": ("Play_sfx_Yasuo_YasuoDashWrapper_hit", 327728017, 0.7, -4),
    "league_yasuo_sfx_w": ("Play_sfx_Yasuo_YasuoWMovingWall_OnCast", 530452173, 1.6, -4),
    "league_yasuo_sfx_shield": ("Play_sfx_Yasuo_YasuoPassiveShield_OnBuffActivate", 667139755, 1.0, -5),
    "league_yasuo_sfx_r_cast": ("Play_sfx_Yasuo_YasuoRDummySpell_OnCast", 35601773, 1.6, -3),
    "league_yasuo_sfx_r_combo": ("Play_sfx_Yasuo_YasuoRKnockUpCombo_OnBuffActivate", 372517854, 1.6, -4),
    "league_yasuo_sfx_r_land": ("Play_sfx_Yasuo_YasuoRKnockUpCombo_hit_land", 826044039, 1.4, -3),
    "league_yasuo_vo_q": ("Play_vo_Yasuo_YasuoQ1_cast3D", 1423518222, 1.0, -2),
    "league_yasuo_vo_q3": ("Play_vo_Yasuo_YasuoQ3Wrapper_cast3D", 1685576159, 1.2, -2),
    "league_yasuo_vo_e": ("Play_vo_Yasuo_YasuoEDash_cast3D", 522189190, 0.8, -2),
    "league_yasuo_vo_r": ("Play_vo_Yasuo_YasuoR_cast3D", 2132191535, 2.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (the passive and Wind Wall ride on the basic attack, so they have no slot)
    "league_yasuo_skill": "ASSETS/Characters/Yasuo/HUD/Icons2D/Yasuo_Q1.dds",
    "league_yasuo_skill2": "ASSETS/Characters/Yasuo/HUD/Icons2D/Yasuo_E.dds",
    "league_yasuo_ult": "ASSETS/Characters/Yasuo/HUD/Icons2D/Yasuo_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Yasuo.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Yasuo.{args.lang}.wad.client"))
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
