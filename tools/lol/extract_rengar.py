r"""Pull Rengar's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_rengar.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_rengar.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Rengar.wad.client and Rengar.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

His events (found in his bins by work/rg/snd_names_rg.py, picked with work/rg/snd_probe_rg.py): the swing
RengarBasicAttack_OnCast / _OnHit; the passive leap RengarP_cast and RengarP_leaphit; Savagery RengarQ_OnCast (the leap
up) and RengarQAttack_OnHit, empowered RengarQEmpAttack_OnHit; Battle Roar RengarW_OnCast, empowered RengarWEmp_OnCast;
the bola RengarE_missilelaunch / RengarE_hit, empowered RengarEEmpmis_OnHit; Thrill of the Hunt
RengarRSecondaryTarget_start, its pounce RengarCritAttack_OnHit. Voice: Q, W, E, R, the full-Ferocity line
(Spell3DPStackFour) and his first encounter with Kha'Zix (FirstEncounter3DKhazix, the easter egg).
Icons: Rengar_W = skill (Battle Roar), Rengar_E = skill2 (Bola Strike), Rengar_R = ult (Savagery is automatic).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/rengar/skins/base/rengar_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/rengar/skins/base/rengar_base_vo_"  # same in every language
P = "Play_sfx_Rengar_Rengar"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_rengar_sfx_attack": (P + "BasicAttack_OnCast", 484668233, 0.45, -11),
    "league_rengar_sfx_attack_hit": (P + "BasicAttack_OnHit", 876769892, 0.4, -11),
    "league_rengar_sfx_leap": (P + "P_cast", 939844980, 0.55, -9),
    "league_rengar_sfx_leap_hit": (P + "P_leaphit", 299643670, 0.45, -9),
    "league_rengar_sfx_q": (P + "Q_OnCast", 648887529, 0.8, -9),
    "league_rengar_sfx_q_hit": (P + "QAttack_OnHit", 691770131, 0.5, -9),
    "league_rengar_sfx_q_emp": (P + "QEmpAttack_OnHit", 636951633, 0.65, -8),
    "league_rengar_sfx_w": (P + "W_OnCast", 660985211, 0.8, -8),
    "league_rengar_sfx_w_emp": (P + "WEmp_OnCast", 601125969, 0.7, -8),
    "league_rengar_sfx_e": (P + "E_missilelaunch", 555612877, 0.6, -9),
    "league_rengar_sfx_e_hit": (P + "E_hit", 638434982, 0.7, -10),
    "league_rengar_sfx_e_emp_hit": (P + "EEmpmis_OnHit", 288751881, 0.7, -9),
    "league_rengar_sfx_r": (P + "RSecondaryTarget_start", 273848724, 1.25, -8),
    "league_rengar_sfx_r_hit": (P + "CritAttack_OnHit", 93136753, 0.6, -8),
    "league_rengar_sfx_vo_q": ("Play_vo_Rengar_RengarQ_cast3D", 2097185959, 0.9, -4),
    "league_rengar_sfx_vo_w": ("Play_vo_Rengar_RengarW_cast3D", 501040173, 1.0, -4),
    "league_rengar_sfx_vo_e": ("Play_vo_Rengar_RengarE_cast3D", 315447474, 0.95, -4),
    "league_rengar_sfx_vo_r": ("Play_vo_Rengar_RengarR_cast3D", 323276812, 1.4, -3),
    "league_rengar_sfx_vo_fero": ("Play_vo_Rengar_Spell3DPStackFour", 152564945, 2.1, -3),
    "league_rengar_sfx_vo_khazix": ("Play_vo_Rengar_FirstEncounter3DKhazix", 1797592850, 3.0, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_rengar_skill": "ASSETS/Characters/Rengar/HUD/Icons2D/Rengar_W.dds",
    "league_rengar_skill2": "ASSETS/Characters/Rengar/HUD/Icons2D/Rengar_E.dds",
    "league_rengar_ult": "ASSETS/Characters/Rengar/HUD/Icons2D/Rengar_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Rengar.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Rengar.{args.lang}.wad.client"))
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
