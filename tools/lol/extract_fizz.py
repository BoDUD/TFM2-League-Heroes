"""Pull Fizz's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_fizz.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Fizz.wad.client and Fizz.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Fizz's skin bin. The basic attack has its swing and its hit; Seastone Trident (W) the
empowered swing, its hit and the chime of the refund on a kill (the minion version of the icon buff); Urchin Strike
(Q) the dash and its hit; Playful (E) the vault and the big slam; Chum the Waters (R) the cast, the fish leaving, the
fish stuck on its champion (2 s, as long as the wait) and the shark's burst. Voice (zh_CN): Q's, E's and R's cast
lines (the longest take of R's seven).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/fizz/skins/base/fizz_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/fizz/skins/base/fizz_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_fizz_sfx_attack_swing": ("Play_sfx_Fizz_FizzBasicAttack_OnCast", 128075086, 0.45, -6),
    "league_fizz_sfx_attack_hit": ("Play_sfx_Fizz_FizzBasicAttack_OnHit", 552161823, 0.45, -8),
    "league_fizz_sfx_w_cast": ("Play_sfx_Fizz_FizzW_OnCast", 190125323, 0.8, -6),
    "league_fizz_sfx_w_hit": ("Play_sfx_Fizz_FizzW_hit", 256296469, 0.7, -5),
    "league_fizz_sfx_w_reset": ("Play_sfx_Fizz_FizzWIcon_buffactivate_minion", 1051369076, 1.0, -6),
    "league_fizz_sfx_q_cast": ("Play_sfx_Fizz_FizzPiercingStrike_OnCast", 447283817, 0.9, -4),
    "league_fizz_sfx_q_hit": ("Play_sfx_Fizz_FizzPiercingStrike_hit", 73289027, 0.75, -5),
    "league_fizz_sfx_e_cast": ("Play_sfx_Fizz_FizzJump_OnCast", 168231327, 0.55, -5),
    "league_fizz_sfx_e_slam": ("Play_sfx_Fizz_FizzTrickSlam_hit_ground_lrg", 660181957, 1.3, -4),
    "league_fizz_sfx_r_cast": ("Play_sfx_Fizz_FizzR_OnCast", 960698459, 1.5, -5),
    "league_fizz_sfx_r_throw": ("Play_sfx_Fizz_FizzRMissile_OnMissileLaunch", 88125207, 1.0, -5),
    "league_fizz_sfx_r_stick": ("Play_sfx_Fizz_FizzRMissile_buffactivate", 657938081, 2.0, -6),
    "league_fizz_sfx_r_shark": ("Play_sfx_Fizz_FizzMarinerDoomBomb_hit", 1048595243, 2.0, -3),
    "league_fizz_vo_q": ("Play_vo_Fizz_FizzQ_cast3D", 1081092506, 0.85, -2),
    "league_fizz_vo_e": ("Play_vo_Fizz_FizzE_cast3D", 1410792179, 0.8, -2),
    "league_fizz_vo_r": ("Play_vo_Fizz_FizzR_cast3D", 574366280, 2.1, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_fizz_skill": "ASSETS/Characters/Fizz/HUD/Icons2D/Fizz_Q.dds",
    "league_fizz_skill2": "ASSETS/Characters/Fizz/HUD/Icons2D/Fizz_E1.dds",
    "league_fizz_ult": "ASSETS/Characters/Fizz/HUD/Icons2D/Fizz_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Fizz.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Fizz.{args.lang}.wad.client"))
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
            print(f"{name:38s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:38s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
