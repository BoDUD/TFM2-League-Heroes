"""Pull Xerath's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_xerath.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Xerath.wad.client and Xerath.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events in the base bank (the event names are plain strings in the WAD's .bin files): the orb leaves with
XerathBasicAttack_OnMissileLaunch; XerathBasicAttack_OnHit1 has no media, so the hit is the quietest variant of
XerathManaAttack_OnHit (Mana Surge's hit, whose loud variant is the surge's own) and the surge starts with
XerathManaAttack_buffactivate. Arcanopulse: XerathArcanopulseChargeUp_OnCast, XerathArcanoPulse2_missilelaunch,
XerathArcanopulse2_hit. Shocking Orb: XerathMageSpearMissile_OnMissileLaunch and _hitchamp. Eye of Destruction:
XerathArcaneBarrage2_OnCast and _explosion. Rite of the Arcane: XerathLocusOfPower2_OnCast, each shell
XerathLocusPulse_OnMissileLaunch and XerathLocusOfPower2_hit, the end _OnBuffDeactivate.
Voice: XerathArcanopulse2_cast3D (Q), XerathArcaneBarrage2_cast3D (E -> W; Shocking Orb's own event has no media) and
XerathLocusOfPower2_cast3D (R).
Icons: Xerath_Q1 = skill, Xerath_E1 = skill2 (E leads the combo), Xerath_R1 = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/xerath/skins/base/xerath_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/xerath/skins/base/xerath_base_vo_"  # same in every language
P = "Play_sfx_Xerath_Xerath"
V = "Play_vo_Xerath_Xerath"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_xerath_sfx_cast": (P + "BasicAttack_OnMissileLaunch", 850181620, 0.6, -10),
    "league_xerath_sfx_hit": (P + "ManaAttack_OnHit", 189576610, 0.45, -13),
    "league_xerath_sfx_surge": (P + "ManaAttack_buffactivate", 710642693, 0.9, -10),
    "league_xerath_sfx_surge_hit": (P + "ManaAttack_OnHit", 698706543, 0.8, -9),
    "league_xerath_sfx_q_charge": (P + "ArcanopulseChargeUp_OnCast", 864922404, 1.2, -9),
    "league_xerath_sfx_q_fire": (P + "ArcanoPulse2_missilelaunch", 903278922, 1.2, -7),
    "league_xerath_sfx_q_hit": (P + "Arcanopulse2_hit", 652696820, 0.6, -12),
    "league_xerath_sfx_e_cast": (P + "MageSpearMissile_OnMissileLaunch", 1008565670, 1.2, -8),
    "league_xerath_sfx_e_hit": (P + "MageSpearMissile_hitchamp", 820798655, 0.8, -8),
    "league_xerath_sfx_w_cast": (P + "ArcaneBarrage2_OnCast", 135042958, 0.8, -9),
    "league_xerath_sfx_w_blast": (P + "ArcaneBarrage2_explosion", 584518383, 1.5, -7),
    "league_xerath_sfx_r_cast": (P + "LocusOfPower2_OnCast", 780153065, 2.0, -7),
    "league_xerath_sfx_r_shot": (P + "LocusPulse_OnMissileLaunch", 528591252, 1.0, -9),
    "league_xerath_sfx_r_blast": (P + "LocusOfPower2_hit", 191960755, 1.5, -7),
    "league_xerath_sfx_r_end": (P + "LocusOfPower2_OnBuffDeactivate", 458141038, 0.7, -9),
    "league_xerath_vo_q": (V + "Arcanopulse2_cast3D", 297548091, 0.6, -4),
    "league_xerath_vo_e": (V + "ArcaneBarrage2_cast3D", 931123522, 1.0, -4),
    "league_xerath_vo_r": (V + "LocusOfPower2_cast3D", 76484870, 1.9, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_xerath_skill": "ASSETS/Characters/Xerath/HUD/Icons2D/Xerath_Q1.dds",
    "league_xerath_skill2": "ASSETS/Characters/Xerath/HUD/Icons2D/Xerath_E1.dds",
    "league_xerath_ult": "ASSETS/Characters/Xerath/HUD/Icons2D/Xerath_R1.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Xerath.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Xerath.{args.lang}.wad.client"))
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
