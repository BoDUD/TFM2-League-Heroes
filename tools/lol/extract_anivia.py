r"""Pull Anivia's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_anivia.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_nasus.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Anivia.wad.client and Anivia.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

Her events (named in the skin bin, prefix Play_sfx_Anivia_): the ice bolt AniviaBasicAttack_OnMissileLaunch (its hit
has no media: Frostbite_OnHit stands in, quieter); Flash Frost FlashFrostSpell_OnMissileLaunch (the orb), _OnHit (an
enemy passed), _explode (the blast), FrashFrostSpell_hit_stun (a unit stunned); Crystallize_OnCast (the wall);
Frostbite_OnMissileLaunch and _OnHit; Glacial Storm GlacialStorm_buffactivate (two media: the call, then the storm's
loop) and GlacialStorm_max (formed: the storm's bite); Rebirth Rebirth_cast (into the egg) and Rebirth_OnBuffActivate
(the hatching). Voice (Play_vo_Anivia_): Attack2DGeneral (Q, W, R and the rebirth, four of its ten lines),
Frostbite_cast3D (E).
Icons: anivia_q = skill, anivia_e = skill2, anivia_r = ult; anivia_w is written too (league_anivia_w, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/anivia/skins/base/anivia_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/anivia/skins/base/anivia_base_vo_"  # same in every language
P = "Play_sfx_Anivia_"
V = "Play_vo_Anivia_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_anivia_sfx_a": (P + "AniviaBasicAttack_OnMissileLaunch", 199257006, 0.7, -15),
    "league_anivia_sfx_a_hit": (P + "Frostbite_OnHit", 356721926, 0.6, -18),
    "league_anivia_sfx_q": (P + "FlashFrostSpell_OnMissileLaunch", 19271242, 1.5, -12),
    "league_anivia_sfx_q_pass": (P + "FlashFrostSpell_OnHit", 632510014, 0.8, -15),
    "league_anivia_sfx_q_blast": (P + "FlashFrostSpell_explode", 787130977, 1.2, -10),
    "league_anivia_sfx_q_hit": (P + "FrashFrostSpell_hit_stun", 948725159, 1.0, -13),
    "league_anivia_sfx_w": (P + "Crystallize_OnCast", 530438217, 1.5, -10),
    "league_anivia_sfx_e": (P + "Frostbite_OnMissileLaunch", 154597272, 0.9, -12),
    "league_anivia_sfx_e_hit": (P + "Frostbite_OnHit", 356721926, 0.9, -11),
    "league_anivia_sfx_r": (P + "GlacialStorm_buffactivate", 1072498615, 2.0, -10),
    "league_anivia_sfx_r_storm": (P + "GlacialStorm_buffactivate", 654023714, 3.0, -12),
    "league_anivia_sfx_r_hit": (P + "GlacialStorm_max", 150675687, 0.8, -18),
    "league_anivia_sfx_p_egg": (P + "Rebirth_cast", 930829679, 2.0, -9),
    "league_anivia_sfx_p_hatch": (P + "Rebirth_OnBuffActivate", 334487340, 2.5, -9),
    "league_anivia_sfx_vo_q": (V + "Attack2DGeneral", 495282220, 2.0, -6),
    "league_anivia_sfx_vo_w": (V + "Attack2DGeneral", 1427851795, 2.0, -6),
    "league_anivia_sfx_vo_e": (V + "Frostbite_cast3D", 1274167001, 1.2, -6),
    "league_anivia_sfx_vo_r": (V + "Attack2DGeneral", 1467915641, 2.6, -6),
    "league_anivia_sfx_vo_p": (V + "Attack2DGeneral", 112260228, 2.0, -6),
}
I = "assets/characters/anivia/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_anivia_skill": I + "anivia_q.dds",
    "league_anivia_skill2": I + "anivia_e.dds",
    "league_anivia_ult": I + "anivia_r.dds",
    "league_anivia_w": I + "anivia_w.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Anivia.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Anivia.{args.lang}.wad.client"))
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
