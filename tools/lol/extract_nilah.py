r"""Pull Nilah's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_nilah.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_nidalee.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Nilah.wad.client and Nilah.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

Her events (named in her bins, the biggest variant of each mostly): the whip NilahBasicAttack_OnCast / _OnHit; the
empowered whip after Formless Blade NilahQAttack_OnCast / _OnHit; Formless Blade NilahQ_OnCast / _hit, its spin after
Slipstream NilahEQ_oml / _hit; Slipstream NilahE_OnCast / _OnHit; Jubilant Veil NilahW_cast_self and the ally's
NilahWAllyBuff_OnBuffActivate; Apotheosis NilahR_OnCast / _hit, the pull NilahRPull_hit and the heal on allies
NilahR_buffactivate_other. Voice: the spell lines NilahQ_cast3D, NilahW_cast3D, NilahE_cast3D, NilahR_cast3D.
Icons: NilahQ = skill (Q), NilahE = skill2 (E + W), NilahR = ult; W and the passive are written too (README / buff icons).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/nilah/skins/base/nilah_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/nilah/skins/base/nilah_base_vo_"  # same in every language
P = "Play_sfx_Nilah_"
V = "Play_vo_Nilah_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_nilah_sfx_a_swing": (P + "NilahBasicAttack_OnCast", 269174441, 0.45, -12),
    "league_nilah_sfx_a_hit": (P + "NilahBasicAttack_OnHit", 903308449, 0.5, -12),
    "league_nilah_sfx_qa_swing": (P + "NilahQAttack_OnCast", 777429456, 0.5, -12),
    "league_nilah_sfx_qa_hit": (P + "NilahQAttack_OnHit", 695128487, 0.6, -11),
    "league_nilah_sfx_q": (P + "NilahQ_OnCast", 403165054, 0.7, -10),
    "league_nilah_sfx_q_hit": (P + "NilahQ_hit", 583546384, 0.8, -10),
    "league_nilah_sfx_eq": (P + "NilahEQ_oml", 648029627, 0.8, -10),
    "league_nilah_sfx_eq_hit": (P + "NilahEQ_hit", 836429118, 0.7, -10),
    "league_nilah_sfx_e": (P + "NilahE_OnCast", 446201257, 0.6, -11),
    "league_nilah_sfx_e_hit": (P + "NilahE_OnHit", 897417805, 0.7, -10),
    "league_nilah_sfx_w": (P + "NilahW_cast_self", 435072929, 1.4, -10),
    "league_nilah_sfx_w_ally": (P + "NilahWAllyBuff_OnBuffActivate", 485209463, 1.0, -12),
    "league_nilah_sfx_r": (P + "NilahR_OnCast", 87659984, 1.2, -9),
    "league_nilah_sfx_r_hit": (P + "NilahR_hit", 448381877, 0.4, -11),
    "league_nilah_sfx_r_pull": (P + "NilahRPull_hit", 84824863, 1.2, -9),
    "league_nilah_sfx_r_heal": (P + "NilahR_buffactivate_other", 440156538, 1.0, -11),
    "league_nilah_sfx_vo_q": (V + "NilahQ_cast3D", 316249626, 2.0, -4),
    "league_nilah_sfx_vo_w": (V + "NilahW_cast3D", 1593748356, 2.2, -4),
    "league_nilah_sfx_vo_e": (V + "NilahE_cast3D", 543542943, 2.0, -4),
    "league_nilah_sfx_vo_r": (V + "NilahR_cast3D", 162472847, 2.4, -4),
}
I = "ASSETS/Characters/Nilah/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_nilah_skill": I + "NilahQ.dds",
    "league_nilah_skill2": I + "NilahE.dds",
    "league_nilah_ult": I + "NilahR.dds",
    "league_nilah_w": I + "NilahW.dds",
    "league_nilah_passive": I + "NIlahP.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Nilah.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Nilah.{args.lang}.wad.client"))
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
