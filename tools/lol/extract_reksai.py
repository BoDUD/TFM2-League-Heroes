r"""Pull Rek'Sai's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_reksai.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

Same route as extract_rell.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/RekSai.wad.client and RekSai.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

Her events (named in skin0.bin, prefix Play_sfx_Reksai_): the bite ReksaiBasicAttack_OnCast / _OnHit; Fury full
ReksaiP_fullstacks; Queen's Wrath ReksaiQ_OnCast and its swipes ReksaiQAttack_OnHit; Prey Seeker ReksaiQBurrowed_OnCast
and ReksaiQBurrowedMis_hit; Furious Bite ReksaiE_OnCast and the max-Fury bite ReksaiE_hit_fullstacks; Burrow
ReksaiW_buffactivate, Unburrow ReksaiW_hit; Void Rush ReksaiR_OnCast, the leap ReksaiR_leap, the blow ReksaiR_hit, the
roar ReksaiR_roar. Voice (Play_vo_Reksai_): RekSaiQAttack3_cast3D, RekSaiE_cast3D, RekSaiW_OnBuffActivate,
Attack2DGeneral (Prey Seeker).
Icons: reksai_q1 (Queen's Wrath) = skill, reksai_w2 (Unburrow) = skill2, reksai_r = ult; q2 / w1 / e1 / e2 / passive
are written too (league_reksai_q2 / _w1 / _e / _e2 / _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/reksai/skins/base/reksai_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/reksai/skins/base/reksai_base_vo_"  # same in every language
P = "Play_sfx_Reksai_"
V = "Play_vo_Reksai_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_reksai_sfx_a_swing": (P + "ReksaiBasicAttack_OnCast", 705239, 0.6, -14),
    "league_reksai_sfx_a_hit": (P + "ReksaiBasicAttack_OnHit", 669701, 0.6, -14),
    "league_reksai_sfx_p_full": (P + "ReksaiP_fullstacks", 826674638, 1.0, -14),
    "league_reksai_sfx_q": (P + "ReksaiQ_OnCast", 209540356, 1.0, -12),
    "league_reksai_sfx_q_hit": (P + "ReksaiQAttack_OnHit", 120571503, 0.6, -12),
    "league_reksai_sfx_q2": (P + "ReksaiQBurrowed_OnCast", 751966871, 1.0, -11),
    "league_reksai_sfx_q2_hit": (P + "ReksaiQBurrowedMis_hit", 314782196, 0.9, -11),
    "league_reksai_sfx_e": (P + "ReksaiE_OnCast", 543676275, 0.6, -12),
    "league_reksai_sfx_e_hit": (P + "ReksaiE_hit_fullstacks", 963765863, 0.9, -10),
    "league_reksai_sfx_w": (P + "ReksaiW_buffactivate", 715009455, 1.4, -11),
    "league_reksai_sfx_w_up": (P + "ReksaiW_hit", 493424595, 1.4, -9),
    "league_reksai_sfx_w_hit": (P + "ReksaiW_hit", 946826053, 0.8, -13),
    "league_reksai_sfx_r": (P + "ReksaiR_OnCast", 451945623, 1.0, -10),
    "league_reksai_sfx_r_leap": (P + "ReksaiR_leap", 155857163, 1.0, -10),
    "league_reksai_sfx_r_hit": (P + "ReksaiR_hit", 841844918, 1.0, -9),
    "league_reksai_sfx_vo_r": (P + "ReksaiR_roar", 187183257, 2.4, -7),
    "league_reksai_sfx_vo_q": (V + "RekSaiQAttack3_cast3D", 572456810, 2.0, -6),
    "league_reksai_sfx_vo_q2": (V + "Attack2DGeneral", 62309510, 2.0, -6),
    "league_reksai_sfx_vo_e": (V + "RekSaiE_cast3D", 200535433, 2.0, -6),
    "league_reksai_sfx_vo_w": (V + "RekSaiW_OnBuffActivate", 874047226, 2.0, -6),
}
I = "assets/characters/reksai/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_reksai_skill": I + "reksai_q1.dds",
    "league_reksai_skill2": I + "reksai_w2.dds",
    "league_reksai_ult": I + "reksai_r.dds",
    "league_reksai_q2": I + "reksai_q2.dds",
    "league_reksai_w1": I + "reksai_w1.dds",
    "league_reksai_e": I + "reksai_e1.dds",
    "league_reksai_e2": I + "reksai_e2.dds",
    "league_reksai_passive": I + "reksai_passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "RekSai.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"RekSai.{args.lang}.wad.client"))
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
