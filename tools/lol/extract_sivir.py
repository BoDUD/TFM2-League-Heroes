"""Pull Sivir's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_sivir.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Sivir.wad.client and Sivir.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

Her events in the base bank (the client's own names): SivirBasicAttack_OnCast (the throw's swish, loudest 0.13-0.21 s
in) with SivirBasicAttack_OnMissileLaunch (the spinning blade) and SivirBasicAttack_OnHit; SivirW_OnCast (Ricochet
starts), SivirWAttack_OnMissileLaunch (a ricochet throw), SivirWBounce_hit (a bounce lands); SivirQ_OnCast (the
throw), SivirQMissile_OnMissileLaunch / SivirQMissileReturn_OnMissileLaunch (the blade out and back) and SivirQ_hit;
SivirE_OnBuffActivate (the shield goes up) and SivirE_OnBuffDeactivate (spent); SivirR_OnCast (the war cry) and
SivirPassiveSpeed_OnBuffActivate (a burst of speed: the hunt renewed). Voice: the SivirQ / SivirWAttack cast3D lines and
Spell3DEHit (a blocked spell). The icons: Sivir_Q = Q, Sivir_E = E, Sivir_R = R (W rides on the attack).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/sivir/skins/base/sivir_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/sivir/skins/base/sivir_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_sivir_sfx_a_cast": ("Play_sfx_Sivir_SivirBasicAttack_OnCast", 728915442, 0.5, -9),
    "league_sivir_sfx_a_throw": ("Play_sfx_Sivir_SivirBasicAttack_OnMissileLaunch", 313782301, 0.7, -10),
    "league_sivir_sfx_a_hit": ("Play_sfx_Sivir_SivirBasicAttack_OnHit", 61684845, 0.5, -13),
    "league_sivir_sfx_w_cast": ("Play_sfx_Sivir_SivirW_OnCast", 1045026004, 0.8, -7),
    "league_sivir_sfx_w_throw": ("Play_sfx_Sivir_SivirWAttack_OnMissileLaunch", 412983443, 1.0, -9),
    "league_sivir_sfx_w_bounce": ("Play_sfx_Sivir_SivirWBounce_hit", 50824256, 0.4, -11),
    "league_sivir_sfx_q_cast": ("Play_sfx_Sivir_SivirQ_OnCast", 441434341, 0.6, -7),
    "league_sivir_sfx_q_out": ("Play_sfx_Sivir_SivirQMissile_OnMissileLaunch", 636809438, 1.3, -8),
    "league_sivir_sfx_q_back": ("Play_sfx_Sivir_SivirQMissileReturn_OnMissileLaunch", 790270116, 0.9, -8),
    "league_sivir_sfx_q_hit": ("Play_sfx_Sivir_SivirQ_hit", 526778842, 0.5, -9),
    "league_sivir_sfx_e_cast": ("Play_sfx_Sivir_SivirE_OnBuffActivate", 530898384, 2.0, -7),
    "league_sivir_sfx_e_block": ("Play_sfx_Sivir_SivirE_OnBuffDeactivate", 411313603, 0.6, -7),
    "league_sivir_sfx_r_cast": ("Play_sfx_Sivir_SivirR_OnCast", 790477901, 1.8, -6),
    "league_sivir_sfx_r_renew": ("Play_sfx_Sivir_SivirPassiveSpeed_OnBuffActivate", 29086942, 0.5, -9),
    "league_sivir_vo_q": ("Play_vo_Sivir_SivirQ_cast3D", 336090326, 0.9, -2),
    "league_sivir_vo_w": ("Play_vo_Sivir_SivirWAttack_cast3D", 986191496, 0.9, -2),
    "league_sivir_vo_e": ("Play_vo_Sivir_Spell3DEHit", 944698564, 0.7, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_sivir_skill": "ASSETS/Characters/Sivir/HUD/Icons2D/Sivir_Q.dds",
    "league_sivir_skill2": "ASSETS/Characters/Sivir/HUD/Icons2D/Sivir_E.dds",
    "league_sivir_ult": "ASSETS/Characters/Sivir/HUD/Icons2D/Sivir_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Sivir.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Sivir.{args.lang}.wad.client"))
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
