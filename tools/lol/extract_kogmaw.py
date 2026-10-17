r"""Pull Kog'Maw's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_kogmaw.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_rengar.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/KogMaw.wad.client and KogMaw.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

His events (found in his bins by work/km/snd_names_km.py, picked with work/km/snd_probe_km.py): the spit
KogMawBasicAttack_OnMissileLaunch / _OnHit; Bio-Arcane Barrage KogMawBioArcaneBarrage_OnCast; Caustic Spittle
KogMawQ_OnCast / _OnMissileLaunch / _hit; Void Ooze KogMawVoidOoze_OnCast, KogMawVoidOozeMissile_OnMissileLaunch / _hit;
Living Artillery KogMawLivingArtillery_OnCast (the shot), _fall (the whistle, loudest 0.56 s in: played when the mark
appears, about when the shell lands) and _hit; Icathian Surprise KogMawIcathianSurprise_OnBuffActivate (the void form
wakes) and _buffdeactivate (it bursts). Voice: Q, W, E, R and his death cry for the passive.
Icons: KogMaw_CausticSpittle = skill (Q), KogMaw_VoidOoze = skill2 (E), KogMaw_LivingArtillery = ult (R).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/kogmaw/skins/base/kogmaw_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/kogmaw/skins/base/kogmaw_base_vo_"  # same in every language
P = "Play_sfx_KogMaw_KogMaw"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_kogmaw_sfx_attack": (P + "BasicAttack_OnMissileLaunch", 27576367, 0.45, -11),
    "league_kogmaw_sfx_attack_hit": (P + "BasicAttack_OnHit", 346371269, 0.35, -12),
    "league_kogmaw_sfx_w": (P + "BioArcaneBarrage_OnCast", 313275785, 0.7, -9),
    "league_kogmaw_sfx_q": (P + "Q_OnCast", 605456908, 0.6, -10),
    "league_kogmaw_sfx_q_shot": (P + "Q_OnMissileLaunch", 835841805, 0.45, -9),
    "league_kogmaw_sfx_q_splash": (P + "Q_hit", 737946506, 0.4, -9),
    "league_kogmaw_sfx_e": (P + "VoidOoze_OnCast", 368408851, 0.9, -10),
    "league_kogmaw_sfx_e_shot": (P + "VoidOozeMissile_OnMissileLaunch", 934767904, 1.0, -9),
    "league_kogmaw_sfx_e_splash": (P + "VoidOozeMissile_hit", 36839331, 0.45, -10),
    "league_kogmaw_sfx_r": (P + "LivingArtillery_OnCast", 300096418, 0.4, -9),
    "league_kogmaw_sfx_r_whistle": (P + "LivingArtillery_fall", 915465873, 0.9, -10),
    "league_kogmaw_sfx_r_blast": (P + "LivingArtillery_hit", 246525437, 0.7, -8),
    "league_kogmaw_sfx_p": (P + "IcathianSurprise_OnBuffActivate", 700232037, 0.85, -8),
    "league_kogmaw_sfx_p_burst": (P + "IcathianSurprise_buffdeactivate", 597462729, 0.9, -8),
    "league_kogmaw_sfx_vo_q": ("Play_vo_KogMaw_KogMawQ_cast3D", 267513523, 0.5, -4),
    "league_kogmaw_sfx_vo_w": ("Play_vo_KogMaw_KogMawBioArcaneBarrage_OnBuffActivate", 268522980, 0.9, -4),
    "league_kogmaw_sfx_vo_e": ("Play_vo_KogMaw_KogMawVoidOoze_cast3D", 878061963, 1.0, -4),
    "league_kogmaw_sfx_vo_r": ("Play_vo_KogMaw_KogMawLivingArtillery_cast3D", 1066709854, 0.9, -4),
    "league_kogmaw_sfx_vo_death": ("Play_vo_KogMaw_Death3D", 804413983, 1.05, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_kogmaw_skill": "ASSETS/Characters/KogMaw/HUD/Icons2D/KogMaw_CausticSpittle.dds",
    "league_kogmaw_skill2": "ASSETS/Characters/KogMaw/HUD/Icons2D/KogMaw_VoidOoze.dds",
    "league_kogmaw_ult": "ASSETS/Characters/KogMaw/HUD/Icons2D/KogMaw_LivingArtillery.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "KogMaw.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"KogMaw.{args.lang}.wad.client"))
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
