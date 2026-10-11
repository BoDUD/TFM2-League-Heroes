r"""Pull Zeri's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_zeri.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_syndra.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Zeri.wad.client and Zeri.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

Her events are Play_sfx_Zeri_Zeri<spell>_<event> (found by scanning her wad for Play_ strings; the empowered-pierce
launches, the special rounds and the shield buff resolve to no media in the base bank). Burst Fire ZeriQ_OnCast (the
seven-round burst, her attack), ZeriQMis_hit; the charged shot of Living Battery ZeriQBasicAttackEmpowered_OnCast /
_OnHit, the pack full ZeriQPassiveReady_OnBuffCast, the shield ZeriPassive_hit; Ultrashock Laser ZeriW_OnCast,
ZeriW_OnMissileLaunch, ZeriW_beam_buffactivate (the laser), ZeriW_hit; Spark Surge ZeriE_cast, ZeriE_foley_land_hit;
Lightning Crash ZeriR_OnCast (the nova), ZeriR_buffcast (overcharged), ZeriRChain_hit (the chain lightning). Voice
clips are league_zeri_sfx_vo_* (never the sound's own name): W, E, R and the pack full; Q's lines are her attack's,
too frequent to play.
Icons: ZeriW = skill (W), ZeriE = skill2 (E), ZeriR = ult (R).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/zeri/skins/base/zeri_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/zeri/skins/base/zeri_base_vo_"  # same in every language
P = "Play_sfx_Zeri_Zeri"
V = "Play_vo_Zeri_Zeri"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_zeri_sfx_shot": (P + "Q_OnCast", 907706576, 0.7, -12),
    "league_zeri_sfx_hit": (P + "QMis_hit", 884025587, 0.4, -14),
    "league_zeri_sfx_charged": (P + "QBasicAttackEmpowered_OnCast", 313194394, 0.8, -10),
    "league_zeri_sfx_charged_hit": (P + "QBasicAttackEmpowered_OnHit", 945153067, 1.0, -9),
    "league_zeri_sfx_ready": (P + "QPassiveReady_OnBuffCast", 371733252, 0.8, -13),
    "league_zeri_sfx_shield": (P + "Passive_hit", 1049316598, 0.6, -12),
    "league_zeri_sfx_w_cast": (P + "W_OnCast", 582351336, 0.9, -10),
    "league_zeri_sfx_w_launch": (P + "W_OnMissileLaunch", 962622354, 0.8, -10),
    "league_zeri_sfx_w_beam": (P + "W_beam_buffactivate", 63336871, 1.2, -8),
    "league_zeri_sfx_w_hit": (P + "W_hit", 823649689, 1.0, -9),
    "league_zeri_sfx_e_cast": (P + "E_cast", 145417287, 0.7, -10),
    "league_zeri_sfx_e_land": (P + "E_foley_land_hit", 536653330, 0.6, -11),
    "league_zeri_sfx_r_cast": (P + "R_OnCast", 598475591, 1.2, -8),
    "league_zeri_sfx_r_buff": (P + "R_buffcast", 663964067, 1.5, -10),
    "league_zeri_sfx_r_chain": (P + "RChain_hit", 32801128, 0.6, -12),
    "league_zeri_sfx_vo_w": (V + "W_cast3D", 99041897, 2.2, -4),
    "league_zeri_sfx_vo_e": (V + "E_cast3D", 1470413627, 2.2, -4),
    "league_zeri_sfx_vo_r": (V + "R_cast3D", 520669717, 2.5, -4),
    "league_zeri_sfx_vo_ready": (V + "QPassiveReady_OnBuffActivate", 13990963, 2.0, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_zeri_skill": "ASSETS/Characters/Zeri/HUD/Icons2D/ZeriW.dds",
    "league_zeri_skill2": "ASSETS/Characters/Zeri/HUD/Icons2D/ZeriE.dds",
    "league_zeri_ult": "ASSETS/Characters/Zeri/HUD/Icons2D/ZeriR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Zeri.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Zeri.{args.lang}.wad.client"))
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
