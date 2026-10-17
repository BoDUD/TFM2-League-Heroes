r"""Pull Rell's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_rell.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_pantheon.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Rell.wad.client and Rell.<lang>.wad.client, resolves the base-skin Wwise events below to their
media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games)
plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

Her events (named in skin0.bin): the lance thrust RellBasicAttack_OnCast / _OnHit; Shattering Strike RellQ_OnCast and
its hit RellQ_hit (shared media with the cast: the hit's own one is 994763690); Full Tilt RellE_OnCast and the blast
RellE_empowered_hit; Crash Down RellW_Dismount_OnCast, _land and _hit; Mount Up RellW_MountUp_OnCast and the charge's
blow RellW_EmpoweredAttack_hit; Magnet Storm RellR_OnCast and a pulse RellR_Damage_OnBuffCast; Break the Mold at five
stacks RellP_debuff_maxstack_buffactivate. Voice: RellQ / RellE / RellW_Dismount / RellW_MountUp / RellR _cast3D.
Icons: RellQ = skill (Q, E told in its text), RellW (Crash Down) = skill2, RellR = ult; RellE, RellMount (Mount Up) and
RellP are written too (league_rell_e / _mount / _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/rell/skins/base/rell_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/rell/skins/base/rell_base_vo_"  # same in every language
P = "Play_sfx_Rell_Rell"
V = "Play_vo_Rell_Rell"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_rell_sfx_a_swing": (P + "BasicAttack_OnCast", 1020964209, 0.6, -14),
    "league_rell_sfx_a_hit": (P + "BasicAttack_OnHit", 17944821, 0.6, -14),
    "league_rell_sfx_p_max": (P + "P_debuff_maxstack_buffactivate", 185804826, 1.0, -14),
    "league_rell_sfx_q": (P + "Q_OnCast", 504971934, 1.2, -11),
    "league_rell_sfx_q_hit": (P + "Q_hit", 994763690, 0.9, -11),
    "league_rell_sfx_e": (P + "E_OnCast", 128382670, 1.4, -12),
    "league_rell_sfx_e_boom": (P + "E_empowered_hit", 850231747, 1.0, -11),
    "league_rell_sfx_w": (P + "W_Dismount_OnCast", 942034532, 1.2, -11),
    "league_rell_sfx_w_land": (P + "W_Dismount_land", 392817480, 1.4, -9),
    "league_rell_sfx_w_hit": (P + "W_Dismount_hit", 237933521, 0.6, -12),
    "league_rell_sfx_w2": (P + "W_MountUp_OnCast", 283616124, 1.2, -11),
    "league_rell_sfx_w2_hit": (P + "W_EmpoweredAttack_hit", 355446324, 1.2, -10),
    "league_rell_sfx_r": (P + "R_OnCast", 195739574, 1.4, -9),
    "league_rell_sfx_r_hit": (P + "R_Damage_OnBuffCast", 666596321, 0.8, -13),
    "league_rell_sfx_vo_q": (V + "Q_cast3D", 1213307893, 2.0, -6),
    "league_rell_sfx_vo_e": (V + "E_cast3D", 131747333, 2.0, -6),
    "league_rell_sfx_vo_w": (V + "W_Dismount_cast3D", 548061131, 2.0, -6),
    "league_rell_sfx_vo_w2": (V + "W_MountUp_cast3D", 1199216928, 2.0, -6),
    "league_rell_sfx_vo_r": (V + "R_cast3D", 1550227897, 2.6, -6),
}
I = "ASSETS/Characters/Rell/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_rell_skill": I + "RellQ.dds",
    "league_rell_skill2": I + "RellW.dds",
    "league_rell_ult": I + "RellR.dds",
    "league_rell_e": I + "RellE.dds",
    "league_rell_mount": I + "RellMount.dds",
    "league_rell_passive": I + "RellP.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Rell.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Rell.{args.lang}.wad.client"))
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
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
