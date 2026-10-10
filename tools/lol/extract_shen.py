r"""Pull Shen's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_shen.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_draven.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Shen.wad.client and Shen.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

His events (found in his bins by work/sn/snd_names_sn.py, picked with work/sn/snd_probe_sn.py): the swing
ShenBasicAttack_OnCast / _OnHit; an empowered hit ShenQAttack_hit_strong; Twilight Assault ShenQ_OnCast, the blade
passing ShenQAttack_hit_weak, back in his hand ShenQBuffStrong_OnBuffActivate; Spirit's Refuge ShenW_OnCast; Shadow
Dash ShenE_OnCast, ShenEDash_taunt; Ki Barrier ShenPassiveShield_OnBuffActivate; Stand United ShenR_foley (the channel),
ShenRshield_OnBuffActivate (the ally's shield, cut), ShenRChannelManager_OnBuffDeactivate (the arrival). Voice: Q, W,
E and R.
Icons: Shen_Q = skill (Q), Shen_E = skill2 (E), Shen_R = ult (R).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/shen/skins/base/shen_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/shen/skins/base/shen_base_vo_"  # same in every language
P = "Play_sfx_Shen_Shen"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_shen_sfx_a_swing": (P + "BasicAttack_OnCast", 624848399, 0.35, -11),
    "league_shen_sfx_a_hit": (P + "BasicAttack_OnHit", 82842219, 0.3, -12),
    "league_shen_sfx_a_emp": (P + "QAttack_hit_strong", 923103244, 0.8, -10),
    "league_shen_sfx_q": (P + "Q_OnCast", 525347176, 0.5, -10),
    "league_shen_sfx_q_hit": (P + "QAttack_hit_weak", 971644463, 0.45, -11),
    "league_shen_sfx_q_back": (P + "QBuffStrong_OnBuffActivate", 443117145, 0.8, -11),
    "league_shen_sfx_w": (P + "W_OnCast", 69044102, 1.0, -9),
    "league_shen_sfx_e": (P + "E_OnCast", 107394285, 0.3, -10),
    "league_shen_sfx_e_hit": (P + "EDash_taunt", 37018046, 0.65, -9),
    "league_shen_sfx_p": (P + "PassiveShield_OnBuffActivate", 154854926, 0.6, -12),
    "league_shen_sfx_r": (P + "R_foley", 438315696, 2.5, -9),
    "league_shen_sfx_r_ally": (P + "Rshield_OnBuffActivate", 939005010, 1.2, -10),
    "league_shen_sfx_r_land": (P + "RChannelManager_OnBuffDeactivate", 591599450, 0.75, -9),
    "league_shen_sfx_vo_q": ("Play_vo_Shen_ShenQAttack_cast3D", 749070915, 0.45, -4),
    "league_shen_sfx_vo_w": ("Play_vo_Shen_ShenW_cast3D", 468512986, 0.45, -4),
    "league_shen_sfx_vo_e": ("Play_vo_Shen_ShenE_cast3D", 517243248, 0.35, -4),
    "league_shen_sfx_vo_r": ("Play_vo_Shen_ShenR_cast3D", 1231746451, 2.4, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_shen_skill": "ASSETS/Characters/Shen/HUD/Icons2D/Shen_Q.dds",
    "league_shen_skill2": "ASSETS/Characters/Shen/HUD/Icons2D/Shen_E.dds",
    "league_shen_ult": "ASSETS/Characters/Shen/HUD/Icons2D/Shen_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Shen.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Shen.{args.lang}.wad.client"))
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
