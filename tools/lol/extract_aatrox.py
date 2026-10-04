"""Pull Aatrox's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_aatrox.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Aatrox.wad.client and Aatrox.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

His events in the base bank (the client's own names, measured with work/at/snd_probe.py): every Darkin Blade cast
(AatroxQ1/Q2/Q3_OnCast_all) layers the cast's own sound (343285381 / 500087760 / 711456995) over one of eleven
sword swooshes it shares with E; the hits are _OnHit_normal_all (shared by Q1 and Q2, Q3's own) and
_OnHit_sweetspot_all (the edge); AatroxBasicAttack_OnCast / _OnHit (swing and impact), AatroxPassiveAttack_OnCast
(the empowered swing; its _OnHit2 is empty in this bank, so the crit impact stands in); AatroxE_OnCast (a random
whoosh of the same pool); AatroxW_OnCast / _OnMissileCast / _OnMissileLaunch / _OnHit (the chain thrown, flying,
hitting), AatroxWChains_OnBuffActivate (the chains closing round the impact) and AatroxWBump_OnBuffActivate (the
pull); AatroxR_OnBuffActivate_all (the transformation). Voice: the Q / W / E / R cast3D lines. The icons: Aatrox_Q = Q (E rides on it), Aatrox_W = W, Aatrox_R = R.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/aatrox/skins/base/aatrox_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/aatrox/skins/base/aatrox_base_vo_"  # same path in every language

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_aatrox_sfx_attack": ("Play_sfx_Aatrox_AatroxBasicAttack_OnCast", 55548831, 0.8, -10),
    "league_aatrox_sfx_attack_hit": ("Play_sfx_Aatrox_AatroxBasicAttack_OnHit", 121586855, 0.8, -11),
    "league_aatrox_sfx_p_cast": ("Play_sfx_Aatrox_AatroxPassiveAttack_OnCast", 780778749, 1.0, -7),
    "league_aatrox_sfx_p_hit": ("Play_sfx_Aatrox_AatroxCritAttack_OnHit", 726862961, 1.1, -7),
    "league_aatrox_sfx_q1": ("Play_sfx_Aatrox_AatroxQ1_OnCast_all", 343285381, 1.1, -7),
    "league_aatrox_sfx_q2": ("Play_sfx_Aatrox_AatroxQ2_OnCast_all", 500087760, 1.1, -7),
    "league_aatrox_sfx_q3": ("Play_sfx_Aatrox_AatroxQ3_OnCast_all", 711456995, 1.25, -7),
    "league_aatrox_sfx_swoosh": ("Play_sfx_Aatrox_AatroxQ1_OnCast_all", 720821530, 1.2, -10),
    "league_aatrox_sfx_q_hit": ("Play_sfx_Aatrox_AatroxQ1_OnHit_normal_all", 206122075, 1.0, -9),
    "league_aatrox_sfx_q_edge": ("Play_sfx_Aatrox_AatroxQ1_OnHit_sweetspot_all", 755125850, 1.0, -7),
    "league_aatrox_sfx_q3_hit": ("Play_sfx_Aatrox_AatroxQ3_OnHit_normal_all", 693279096, 1.0, -9),
    "league_aatrox_sfx_q3_edge": ("Play_sfx_Aatrox_AatroxQ3_OnHit_sweetspot_all", 195253461, 1.2, -7),
    "league_aatrox_sfx_e": ("Play_sfx_Aatrox_AatroxE_OnCast", 84421605, 0.8, -9),
    "league_aatrox_sfx_w_cast": ("Play_sfx_Aatrox_AatroxW_OnCast", 244005772, 0.5, -9),
    "league_aatrox_sfx_w_throw": ("Play_sfx_Aatrox_AatroxW_OnMissileCast", 166429304, 0.8, -8),
    "league_aatrox_sfx_w_fly": ("Play_sfx_Aatrox_AatroxW_OnMissileLaunch", 475823576, 1.2, -10),
    "league_aatrox_sfx_w_hit": ("Play_sfx_Aatrox_AatroxW_OnHit", 1001358263, 1.4, -8),
    "league_aatrox_sfx_w_chains": ("Play_sfx_Aatrox_AatroxWChains_OnBuffActivate", 515734159, 1.8, -9),
    "league_aatrox_sfx_w_pull": ("Play_sfx_Aatrox_AatroxWBump_OnBuffActivate", 508351699, 1.3, -8),
    "league_aatrox_sfx_r": ("Play_sfx_Aatrox_AatroxR_OnBuffActivate_all", 129728129, 3.2, -6),
    "league_aatrox_vo_q": ("Play_vo_Aatrox_AatroxQ_cast3D", 607537853, 2.0, -3),
    "league_aatrox_vo_w": ("Play_vo_Aatrox_AatroxW_cast3D", 435115763, 1.6, -3),
    "league_aatrox_vo_e": ("Play_vo_Aatrox_AatroxE_cast3D", 219875568, 1.3, -3),
    "league_aatrox_vo_r": ("Play_vo_Aatrox_AatroxR_cast3D", 1596608250, 2.1, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_aatrox_skill": "ASSETS/Characters/Aatrox/HUD/Icons2D/Aatrox_Q.dds",
    "league_aatrox_skill2": "ASSETS/Characters/Aatrox/HUD/Icons2D/Aatrox_W.dds",
    "league_aatrox_ult": "ASSETS/Characters/Aatrox/HUD/Icons2D/Aatrox_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Aatrox.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Aatrox.{args.lang}.wad.client"))
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
