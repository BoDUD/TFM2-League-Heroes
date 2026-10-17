"""Pull Master Yi's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_masteryi.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/MasterYi.wad.client and MasterYi.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in his base bins (Play_sfx_MasterYi_* / Play_vo_MasterYi_*). Alpha Strike's cast
is the whole blink sequence (AlphaStrike_missilecast, cut to its loud first second), each strike its
own hit; the Wuju-charged basic-attack hit (basic2wuju) plays while Wuju Style runs. Meditate's cast,
Wuju Style's activation and Highlander's activation are the other casts. The zh_CN voice bank has
lines for Alpha Strike, Meditate and Highlander (all translated: none is byte-equal to the en_US
bank); Wuju Style's voice event has no media. The lines picked are the short phrases (about three
or four syllables, 1.2-1.7 s).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/masteryi/skins/base/masteryi_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/masteryi/skins/base/masteryi_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_masteryi_sfx_attack_hit": ("Play_sfx_MasterYi_MasterYiBasicAttack_OnHit", 84648135, 0.5, -5),
    "league_masteryi_sfx_e_hit": ("Play_sfx_MasterYi_MasterYiBasicAttack_basic2wuju", 834889418, 0.7, -5),
    "league_masteryi_sfx_double": ("Play_sfx_MasterYi_MasterYiDoubleStrike_OnCast", 860189031, 0.55, -5),
    "league_masteryi_sfx_q_cast": ("Play_sfx_MasterYi_AlphaStrike_missilecast", 378075409, 1.2, -4),
    "league_masteryi_sfx_q_hit": ("Play_sfx_MasterYi_AlphaStrike_hit", 555085050, 0.5, -4),
    "league_masteryi_sfx_w_cast": ("Play_sfx_MasterYi_Meditate_OnCast", 637673445, 1.3, -6),
    "league_masteryi_sfx_e_cast": ("Play_sfx_MasterYi_WujuStyle_OnCast", 289182248, 0.9, -4),
    "league_masteryi_sfx_r_cast": ("Play_sfx_MasterYi_Highlander_OnBuffActivate", 873615538, 2.0, -4),
    "league_masteryi_vo_q": ("Play_vo_MasterYi_AlphaStrike_cast3D", 472813866, 1.8, -2),
    "league_masteryi_vo_w": ("Play_vo_MasterYi_Meditate_cast3D", 968269496, 1.8, -2),
    "league_masteryi_vo_r": ("Play_vo_MasterYi_Highlander_cast3D", 1468237420, 1.3, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Meditate rides on Wuju Style, Double Strike is a passive: no slots)
    "league_masteryi_skill": "ASSETS/Characters/MasterYi/HUD/Icons2D/MasterYi_Q.dds",
    "league_masteryi_skill2": "ASSETS/Characters/MasterYi/HUD/Icons2D/MasterYi_E1.dds",
    "league_masteryi_ult": "ASSETS/Characters/MasterYi/HUD/Icons2D/MasterYi_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "MasterYi.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"MasterYi.{args.lang}.wad.client"))
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
