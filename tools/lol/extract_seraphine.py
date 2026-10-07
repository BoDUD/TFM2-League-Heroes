r"""Pull Seraphine's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_seraphine.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Seraphine.wad.client and Seraphine.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

Her events are Play_sfx_Seraphine_Seraphine<spell>_<event>; the voice events Play_vo_Seraphine_Seraphine<key>Cast_cast3D.
The sound-wave attack BasicAttack_OnMissileLaunch, the note-charged attack PassiveAttack_OnMissileLaunch; High Note
Q_OnCast, QInitialMissile_OnMissileLaunch / _OnHitLocation; Surround Sound W_OnCast, WShield_buffactivate and
W2Warning_OnBuffDeactivate (the heal); Beat Drop E_OnCast and EStun_OnBuffActivate; the echo PEcho_ready_buffactivate_self;
Encore R_OnCast, R_OnMissileLaunch and RCharm_hit. Voice clips are league_seraphine_sfx_vo_* (never the sound's own name).
Icons: Seraphine_Q3 = skill, Seraphine_E3 = skill2 (E->W; W is in its text), Seraphine_R = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/seraphine/skins/base/seraphine_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/seraphine/skins/base/seraphine_base_vo_"  # same in every language
P = "Play_sfx_Seraphine_Seraphine"
V = "Play_vo_Seraphine_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_seraphine_sfx_shot": (P + "BasicAttack_OnMissileLaunch", 160078753, 0.6, -12),
    "league_seraphine_sfx_note": (P + "PassiveAttack_OnMissileLaunch", 133632451, 0.7, -11),
    "league_seraphine_sfx_q_cast": (P + "Q_OnCast", 895481833, 0.8, -10),
    "league_seraphine_sfx_q_throw": (P + "QInitialMissile_OnMissileLaunch", 490561593, 0.7, -10),
    "league_seraphine_sfx_q_hit": (P + "QInitialMissile_OnHitLocation", 13865021, 0.9, -9),
    "league_seraphine_sfx_w_cast": (P + "W_OnCast", 655350838, 1.3, -9),
    "league_seraphine_sfx_w_shield": (P + "WShield_buffactivate", 399104007, 0.9, -11),
    "league_seraphine_sfx_w_heal": (P + "W2Warning_OnBuffDeactivate", 438945577, 1.2, -10),
    "league_seraphine_sfx_e_cast": (P + "E_OnCast", 820665655, 0.8, -9),
    "league_seraphine_sfx_e_stun": (P + "EStun_OnBuffActivate", 777213724, 1.3, -10),
    "league_seraphine_sfx_echo": (P + "PEcho_ready_buffactivate_self", 88512264, 1.5, -11),
    "league_seraphine_sfx_r_cast": (P + "R_OnCast", 162389452, 1.4, -8),
    "league_seraphine_sfx_r_wave": (P + "R_OnMissileLaunch", 717640036, 1.1, -9),
    "league_seraphine_sfx_r_charm": (P + "RCharm_hit", 92558949, 1.3, -10),
    "league_seraphine_sfx_vo_q": (V + "SeraphineQCast_cast3D", 734997032, 2.0, -4),
    "league_seraphine_sfx_vo_w": (V + "SeraphineWCast_cast3D", 887305575, 2.0, -4),
    "league_seraphine_sfx_vo_e": (V + "SeraphineECast_cast3D", 317557704, 2.0, -4),
    "league_seraphine_sfx_vo_r": (V + "SeraphineR_cast3D", 695528171, 2.5, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_seraphine_skill": "ASSETS/Characters/Seraphine/HUD/Icons2D/Seraphine_Q3.dds",
    "league_seraphine_skill2": "ASSETS/Characters/Seraphine/HUD/Icons2D/Seraphine_E3.dds",
    "league_seraphine_ult": "ASSETS/Characters/Seraphine/HUD/Icons2D/Seraphine_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Seraphine.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Seraphine.{args.lang}.wad.client"))
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
