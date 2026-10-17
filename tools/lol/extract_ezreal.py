"""Pull Ezreal's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_ezreal.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Ezreal.wad.client and Ezreal.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Ezreal's skin bin. The basic attack's hit events (BasicAttack_OnHit1,
BasicAttack2_OnHit2, CritAttack_OnHit0) are named there but defined in no bank, so the attack's hit
is Mystic Shot's lightest hit variant, shortened and quieter. Essence Flux has its throw, the orb
sticking to a champion and the detonation; Arcane Shift the blink and the homing bolt's launch and
hit; Trueshot Barrage the charge, the release and the hit. Every zh_CN voice take is its own
recording (none is byte- or sample-identical to en_US); the three picked are the ones with the most
syllables (the short takes are grunts): W (played with the W+Q combo), E and R. Plain Q casts come
every few seconds and get no voice.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/ezreal/skins/base/ezreal_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/ezreal/skins/base/ezreal_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_ezreal_sfx_attack_shot": ("Play_sfx_Ezreal_EzrealBasicAttack_OnMissileLaunch", 620068021, 0.6, -6),
    "league_ezreal_sfx_attack_hit": ("Play_sfx_Ezreal_EzrealQ_OnHit", 183122777, 0.4, -10),
    "league_ezreal_sfx_q_cast": ("Play_sfx_Ezreal_EzrealQ_OnCast", 258194894, 0.9, -3),
    "league_ezreal_sfx_q_hit": ("Play_sfx_Ezreal_EzrealQ_OnHit", 738256140, 0.9, -5),
    "league_ezreal_sfx_w_cast": ("Play_sfx_Ezreal_EzrealW_OnCast", 783596333, 1.0, -4),
    "league_ezreal_sfx_w_hit": ("Play_sfx_Ezreal_EzrealW_OnHit", 586485724, 1.2, -5),
    "league_ezreal_sfx_w_boom": ("Play_sfx_Ezreal_EzrealWAttach_detonate", 586902453, 1.4, -3),
    "league_ezreal_sfx_e_cast": ("Play_sfx_Ezreal_EzrealE_OnCast", 578012949, 1.0, -4),
    "league_ezreal_sfx_e_bolt": ("Play_sfx_Ezreal_EzrealEMissile_OnMissileLaunch", 893800350, 0.8, -5),
    "league_ezreal_sfx_e_hit": ("Play_sfx_Ezreal_EzrealEMissile_OnHit", 152123294, 1.0, -4),
    "league_ezreal_sfx_r_cast": ("Play_sfx_Ezreal_EzrealR_OnCast", 303197261, 1.8, -3),
    "league_ezreal_sfx_r_fire": ("Play_sfx_Ezreal_EzrealR_OnMissileCast", 685370749, 2.0, -2),
    "league_ezreal_sfx_r_hit": ("Play_sfx_Ezreal_EzrealR_OnHit", 522296616, 0.9, -4),
    "league_ezreal_vo_w": ("Play_vo_Ezreal_EzrealW_cast3D", 971645115, 1.5, -2),
    "league_ezreal_vo_e": ("Play_vo_Ezreal_EzrealE_cast3D", 1137398613, 1.5, -2),
    "league_ezreal_vo_r": ("Play_vo_Ezreal_EzrealR_cast3D", 26133770, 2.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (skill is Q with W folded in: Q's icon; skill2 is E)
    "league_ezreal_skill": "ASSETS/Characters/Ezreal/HUD/Icons2D/Ezreal_Q.dds",
    "league_ezreal_skill2": "ASSETS/Characters/Ezreal/HUD/Icons2D/Ezreal_E.dds",
    "league_ezreal_ult": "ASSETS/Characters/Ezreal/HUD/Icons2D/Ezreal_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Ezreal.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Ezreal.{args.lang}.wad.client"))
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
