"""Pull Rakan's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_rakan.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Rakan.wad.client and Rakan.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

His events in the base bank (the client's own names, listed by work/rk/rakan_assets.py): RakanBasicAttack_OnCast /
_OnHit (the feather thrown, its hit); RakanQMis_OnMissileLaunch (Gleaming Quill thrown; RakanQ_OnCast1 is empty),
RakanQ_hit_champ, RakanQMark_buffactivate_healcharge (the heal armed) and RakanQMark_buffdeactivate_heal (the heal);
RakanW_OnCast (Grand Entrance's dash), RakanWCast_hit (the spiral's knock-up); RakanECast_OnCast (Battle Dance's
flight), RakanEShield_OnBuffActivate (the shield on the ally); RakanPassiveReady_shield (Fey Feathers' shield);
RakanR_OnCast (The Quickness), RakanRDebuff_hit_champ (a charm). Voice: the Q / W / E / R cast3D lines. The icons:
Rakan_Q = Q, Rakan_W = W (E rides on it), Rakan_R = R.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/rakan/skins/base/rakan_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/rakan/skins/base/rakan_base_vo_"  # same path in every language

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_rakan_sfx_attack": ("Play_sfx_Rakan_RakanBasicAttack_OnCast", 215983410, 0.8, -10),
    "league_rakan_sfx_attack_hit": ("Play_sfx_Rakan_RakanBasicAttack_OnHit", 245544221, 0.8, -11),
    "league_rakan_sfx_q": ("Play_sfx_Rakan_RakanQMis_OnMissileLaunch", 397806884, 1.0, -8),
    "league_rakan_sfx_q_hit": ("Play_sfx_Rakan_RakanQ_hit_champ", 291009117, 1.0, -8),
    "league_rakan_sfx_q_charge": ("Play_sfx_Rakan_RakanQMark_buffactivate_healcharge", 226356309, 1.4, -10),
    "league_rakan_sfx_q_heal": ("Play_sfx_Rakan_RakanQMark_buffdeactivate_heal", 608721181, 1.4, -8),
    "league_rakan_sfx_w": ("Play_sfx_Rakan_RakanW_OnCast", 25184703, 1.0, -8),
    "league_rakan_sfx_w_hit": ("Play_sfx_Rakan_RakanWCast_hit", 1051984120, 1.6, -7),
    "league_rakan_sfx_e": ("Play_sfx_Rakan_RakanECast_OnCast", 136650289, 0.8, -9),
    "league_rakan_sfx_e_shield": ("Play_sfx_Rakan_RakanEShield_OnBuffActivate", 723671481, 1.3, -9),
    "league_rakan_sfx_p_shield": ("Play_sfx_Rakan_RakanPassiveReady_shield", 925700258, 1.2, -10),
    "league_rakan_sfx_r": ("Play_sfx_Rakan_RakanR_OnCast", 636744434, 3.0, -7),
    "league_rakan_sfx_r_hit": ("Play_sfx_Rakan_RakanRDebuff_hit_champ", 428403494, 0.9, -9),
    "league_rakan_vo_q": ("Play_vo_Rakan_RakanQ_cast3D", 604252826, 1.6, -3),
    "league_rakan_vo_w": ("Play_vo_Rakan_RakanW_cast3D", 228451665, 1.4, -3),
    "league_rakan_vo_e": ("Play_vo_Rakan_RakanE_hit3D", 2016895425, 1.4, -3),
    "league_rakan_vo_r": ("Play_vo_Rakan_RakanR_cast3D", 1809680582, 2.2, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_rakan_skill": "ASSETS/Characters/Rakan/HUD/Icons2D/Rakan_Q.dds",
    "league_rakan_skill2": "ASSETS/Characters/Rakan/HUD/Icons2D/Rakan_W.dds",
    "league_rakan_ult": "ASSETS/Characters/Rakan/HUD/Icons2D/Rakan_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Rakan.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Rakan.{args.lang}.wad.client"))
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
