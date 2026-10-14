r"""Pull Kindred's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_kindred.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_nilah.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Kindred.wad.client and Kindred.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

Her events (named in her bins, a short variant of each mostly): Lamb's arrow KindredBasicAttack_OnMissileLaunch /
_OnHit; Dance of Arrows KindredQ_OnCast (the leap), KindredQ_missilelaunch_multi (the three arrows) and
KindredQMissile_OnHit; Mounting Dread KindredE_OnCast, KindredE_OnMissileLaunch (the marking arrow), KindredE_OnHit
(the mark lands) and KindredEWolfMissile_OnHitLocation (Wolf's pounce); Wolf's Frenzy KindredW_OnCast and the Wolf's
bite KindredWolfBasicAttack_OnHit; Lamb's Respite KindredR_buffactivate (cut to the zone's 4 s) and
KindredR_heal_buffactivate; a mark collected KindredP_collect_buffactivate. Voice: the spell lines KindredQ_cast3D,
KindredW_cast3D, KindredE_cast3D, KindredR_cast3D (none of the four is the same media in zh_CN and en_US: spoken).
Icons: Kindred_Q = skill (Q), Kindred_E = skill2 (E + W), Kindred_R = ult; W and the passive are written too
(README / buff icons).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/kindred/skins/base/kindred_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/kindred/skins/base/kindred_base_vo_"  # same in every language
P = "Play_sfx_Kindred_"
V = "Play_vo_Kindred_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_kindred_sfx_a_shot": (P + "KindredBasicAttack_OnMissileLaunch", 24932106, 0.6, -12),
    "league_kindred_sfx_a_hit": (P + "KindredBasicAttack_OnHit", 143124679, 0.5, -12),
    "league_kindred_sfx_q": (P + "KindredQ_OnCast", 613689236, 0.8, -10),
    "league_kindred_sfx_q_arrows": (P + "KindredQ_missilelaunch_multi", 416694410, 0.7, -10),
    "league_kindred_sfx_q_hit": (P + "KindredQMissile_OnHit", 789227674, 0.5, -12),
    "league_kindred_sfx_e": (P + "KindredE_OnCast", 159574241, 0.4, -10),
    "league_kindred_sfx_e_shot": (P + "KindredE_OnMissileLaunch", 454914413, 0.8, -10),
    "league_kindred_sfx_e_hit": (P + "KindredE_OnHit", 701011945, 1.4, -10),
    "league_kindred_sfx_e_bite": (P + "KindredEWolfMissile_OnHitLocation", 676549998, 1.4, -9),
    "league_kindred_sfx_w": (P + "KindredW_OnCast", 128031330, 1.8, -10),
    "league_kindred_sfx_w_bite": (P + "KindredWolfBasicAttack_OnHit", 802286647, 0.6, -11),
    "league_kindred_sfx_r": (P + "KindredR_buffactivate", 436110905, 4.0, -9),
    "league_kindred_sfx_r_heal": (P + "KindredR_heal_buffactivate", 756856195, 1.8, -10),
    "league_kindred_sfx_p": (P + "KindredP_collect_buffactivate", 414541725, 1.8, -10),
    "league_kindred_sfx_vo_q": (V + "KindredQ_cast3D", 628403527, 1.0, -4),
    "league_kindred_sfx_vo_w": (V + "KindredW_cast3D", 604138474, 3.0, -4),
    "league_kindred_sfx_vo_e": (V + "KindredE_cast3D", 922668415, 1.0, -4),
    "league_kindred_sfx_vo_r": (V + "KindredR_cast3D", 1555544660, 3.0, -4),
}
I = "ASSETS/Characters/Kindred/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_kindred_skill": I + "Kindred_Q.dds",
    "league_kindred_skill2": I + "Kindred_E.dds",
    "league_kindred_ult": I + "Kindred_R.dds",
    "league_kindred_w": I + "Kindred_W.dds",
    "league_kindred_passive": I + "Kindred_Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Kindred.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Kindred.{args.lang}.wad.client"))
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
