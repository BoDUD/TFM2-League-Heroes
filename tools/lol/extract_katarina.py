r"""Pull Katarina's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_katarina.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_milio.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Katarina.wad.client and Katarina.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

Her events (named in skin0.bin; one clear variant of each, lengths and peaks measured from the decoded variants): the
stab KatarinaBasicAttack_OnCast / _OnHit; Bouncing Blade's KatarinaQ_OnCast (the throw), KatarinaQMis_OnMissileLaunch
(the spinning blade), Katarina_Q_OnHit (its short hit variant), KatarinaQdaggerarc_OnMissileLaunch (the dagger arcing
to the ground) and Q_dagger_land_dirt (it sticks in); Preparation's KatarinaW_OnCast; Shunpo's KatarinaE_OnCast;
Sheathed Blades' Dagger_PickUpPBAoE_Cast (the spin on a pick-up); Voracity's KatarinaPassive_buffactivate (the reset);
Death Lotus' KatarinaR_OnCast (the 2.5 s channel). Voice: Q / W share the cast3D pool (one line each, E takes a third
from it: League has no E voice event), R has its own lines (KatarinaR_cast3D's last four). Clip names differ from the
sound names (league_katarina_sfx_*, memory vo-clip-names).
Icons: Katarina_Q = skill (Q, Shunpo onto the dagger), Katarina_W = skill2 (W, Shunpo in first), Katarina_R = ult;
E, the passive and the dagger spin are written too (README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/katarina/skins/base/katarina_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/katarina/skins/base/katarina_base_vo_"  # same in every language
P = "Play_sfx_Katarina_"
V = "Play_vo_Katarina_Katarina"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_katarina_sfx_a_swing": (P + "KatarinaBasicAttack_OnCast", 246668763, 0.5, -13),
    "league_katarina_sfx_a_hit": (P + "KatarinaBasicAttack_OnHit", 720395475, 0.6, -12),
    "league_katarina_sfx_q_cast": (P + "KatarinaQ_OnCast", 1004250906, 0.8, -12),
    "league_katarina_sfx_q_blade": (P + "KatarinaQMis_OnMissileLaunch", 382371290, 0.64, -12),
    "league_katarina_sfx_q_hit": (P + "Katarina_Q_OnHit", 670145850, 0.31, -12),
    "league_katarina_sfx_q_arc": (P + "KatarinaQdaggerarc_OnMissileLaunch", 143611163, 1.0, -13),
    "league_katarina_sfx_q_land": (P + "Q_dagger_land_dirt", 1007990563, 1.0, -13),
    "league_katarina_sfx_w_toss": (P + "KatarinaW_OnCast", 620563555, 1.4, -11),
    "league_katarina_sfx_e_blink": (P + "KatarinaE_OnCast", 812400259, 1.1, -11),
    "league_katarina_sfx_pick": (P + "Dagger_PickUpPBAoE_Cast", 534482511, 1.3, -10),
    "league_katarina_sfx_reset": (P + "KatarinaPassive_buffactivate", 930317716, 1.5, -11),
    "league_katarina_sfx_r_lotus": (P + "KatarinaR_OnCast", 237935629, 2.6, -10),
    "league_katarina_sfx_vo_q": (V + "Q_cast3D", 453320334, 1.0, -6),
    "league_katarina_sfx_vo_w": (V + "W_cast3D", 286288425, 1.0, -6),
    "league_katarina_sfx_vo_e": (V + "Q_cast3D", 1357287092, 1.0, -6),
    "league_katarina_sfx_vo_r": (V + "R_cast3D", 1968276283, 2.6, -6),
}
I = "ASSETS/Characters/Katarina/HUD/Icons2D/Katarina_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_katarina_skill": I + "Q.dds",
    "league_katarina_skill2": I + "W.dds",
    "league_katarina_ult": I + "R.dds",
    "league_katarina_e": I + "E.dds",
    "league_katarina_passive": I + "Passive.dds",
    "league_katarina_spin": I + "DaggerSpin.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Katarina.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Katarina.{args.lang}.wad.client"))
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
