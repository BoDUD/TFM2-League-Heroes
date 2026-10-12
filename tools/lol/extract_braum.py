r"""Pull Braum's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_braum.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_gragas.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Braum.wad.client and Braum.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in his bins, picked by size among the variants): the punch BraumBasicAttack_OnCast /
BraumBasicAttack2_OnHit; the passive's stun BraumBasicAttackPassiveOverride_hit; Winter's Bite's
BraumQMissile_OnMissileLaunch and _hit; Unbreakable's BraumE_OnCast; Stand Behind Me's leap (BraumBasicAttack3_OnCast, a
whoosh: the leap has no cast sound of its own) and BraumWDash_land; Glacial Fissure's BraumRMissile_OnMissileLaunch and
_OnHit. Voice: the longest take of each spell's own line (BraumQ_cast3D, BraumWDummySpell_cast3D, BraumE_cast3D,
BraumRWrapper_cast3D).
Icons: Braum_Q = skill (Q), Braum_E = skill2 (E, W folded in), Braum_R = ult (R); Braum_W and Braum_Passive are
written too (README / buff icons).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/braum/skins/base/braum_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/braum/skins/base/braum_base_vo_"  # same in every language
P = "Play_sfx_Braum_"
V = "Play_vo_Braum_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_braum_sfx_a_swing": (P + "BraumBasicAttack_OnCast", 22215941, 0.45, -12),
    "league_braum_sfx_a_hit": (P + "BraumBasicAttack2_OnHit", 22330407, 0.6, -12),
    "league_braum_sfx_p_proc": (P + "BraumBasicAttackPassiveOverride_hit", 510145146, 0.9, -9),
    "league_braum_sfx_q": (P + "BraumQMissile_OnMissileLaunch", 854713798, 0.9, -10),
    "league_braum_sfx_q_hit": (P + "BraumQMissile_hit", 1071447244, 1.0, -9),
    "league_braum_sfx_e": (P + "BraumE_OnCast", 709831717, 1.0, -9),
    "league_braum_sfx_w": (P + "BraumBasicAttack3_OnCast", 117748257, 0.6, -11),
    "league_braum_sfx_w_land": (P + "BraumWDash_land", 840358885, 0.9, -9),
    "league_braum_sfx_r": (P + "BraumRMissile_OnMissileLaunch", 653245930, 1.4, -8),
    "league_braum_sfx_r_hit": (P + "BraumRMissile_OnHit", 802818776, 1.2, -8),
    "league_braum_sfx_vo_q": (V + "BraumQ_cast3D", 288913721, 2.2, -4),
    "league_braum_sfx_vo_w": (V + "BraumWDummySpell_cast3D", 1214393075, 2.2, -4),
    "league_braum_sfx_vo_e": (V + "BraumE_cast3D", 1202179382, 2.2, -4),
    "league_braum_sfx_vo_r": (V + "BraumRWrapper_cast3D", 224669258, 2.2, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_braum_skill": "ASSETS/Characters/Braum/HUD/Icons2D/Braum_Q.dds",
    "league_braum_skill2": "ASSETS/Characters/Braum/HUD/Icons2D/Braum_E.dds",
    "league_braum_ult": "ASSETS/Characters/Braum/HUD/Icons2D/Braum_R.dds",
    "league_braum_w": "ASSETS/Characters/Braum/HUD/Icons2D/Braum_W.dds",
    "league_braum_passive": "ASSETS/Characters/Braum/HUD/Icons2D/Braum_Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Braum.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Braum.{args.lang}.wad.client"))
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
