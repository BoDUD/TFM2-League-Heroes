r"""Pull Mordekaiser's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_mordekaiser.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_corki.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Mordekaiser.wad.client and Mordekaiser.<lang>.wad.client, resolves the base-skin Wwise events
below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in his skin bin; a trailing byte after a bin string is not part of the name), picked by size among
the variants: the swing MordekaiserBasicAttack_OnCast / _OnHit; Darkness Rise at three stacks
MordekaiserPassive_FullStacks_buffactivate_vfx; Obliterate's cast MordekaiserQ_OnCast and its heavier hit
MordekaiserQ_hit2; Death's Grasp MordekaiserEMissile_OnMissileCast / _OnHit; Indestructible's shield
MordekaiserW_OnBuffActivate and its heal MordekaiserWHeal_OnCast; Realm of Death MordekaiserR_OnCast, and its hit
MordekaiserR_Hit for the kill inside the realm. Voice: his Q, E, W and R cast lines.
Icons: MordekaiserQ = skill (Q), MordekaiserE = skill2 (E, W folded), MordekaiserR = ult (R); MordekaiserW and
MordekaiserPassive are written too.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/mordekaiser/skins/base/mordekaiser_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/mordekaiser/skins/base/mordekaiser_base_vo_"  # same in every language
P = "Play_sfx_Mordekaiser_Mordekaiser"
V = "Play_vo_Mordekaiser_Mordekaiser"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_mordekaiser_sfx_a_swing": (P + "BasicAttack_OnCast", 269156314, 0.5, -12),
    "league_mordekaiser_sfx_a_hit": (P + "BasicAttack_OnHit", 159929300, 0.6, -11),
    "league_mordekaiser_sfx_p_on": (P + "Passive_FullStacks_buffactivate_vfx", 219667683, 1.4, -11),
    "league_mordekaiser_sfx_q": (P + "Q_OnCast", 196435643, 0.6, -10),
    "league_mordekaiser_sfx_q_hit": (P + "Q_hit2", 12955350, 1.2, -9),
    "league_mordekaiser_sfx_e": (P + "EMissile_OnMissileCast", 515512869, 0.8, -10),
    "league_mordekaiser_sfx_e_hit": (P + "EMissile_OnHit", 580498306, 0.8, -10),
    "league_mordekaiser_sfx_w": (P + "W_OnBuffActivate", 748857756, 1.4, -10),
    "league_mordekaiser_sfx_w_heal": (P + "WHeal_OnCast", 1016691965, 1.2, -10),
    "league_mordekaiser_sfx_r": (P + "R_OnCast", 915629501, 1.0, -9),
    "league_mordekaiser_sfx_r_win": (P + "R_Hit", 452427788, 1.6, -9),
    "league_mordekaiser_sfx_vo_q": (V + "Q_cast3D", 977696382, 1.4, -4),
    "league_mordekaiser_sfx_vo_e": (V + "E_cast3D", 1825206671, 1.6, -4),
    "league_mordekaiser_sfx_vo_w": (V + "W_cast3D", 1840118457, 1.8, -4),
    "league_mordekaiser_sfx_vo_r": (V + "R_cast2D", 1495898902, 2.6, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_mordekaiser_skill": "ASSETS/Characters/Mordekaiser/HUD/Icons2D/MordekaiserQ.dds",
    "league_mordekaiser_skill2": "ASSETS/Characters/Mordekaiser/HUD/Icons2D/MordekaiserE.dds",
    "league_mordekaiser_ult": "ASSETS/Characters/Mordekaiser/HUD/Icons2D/MordekaiserR.dds",
    "league_mordekaiser_w": "ASSETS/Characters/Mordekaiser/HUD/Icons2D/MordekaiserW.dds",
    "league_mordekaiser_passive": "ASSETS/Characters/Mordekaiser/HUD/Icons2D/MordekaiserPassive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Mordekaiser.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Mordekaiser.{args.lang}.wad.client"))
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
