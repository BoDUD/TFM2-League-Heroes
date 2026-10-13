r"""Pull Nidalee's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_nidalee.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_braum.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Nidalee.wad.client and Nidalee.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

Her events (named in her bins, the biggest variant of each): the human throw NidaleeBasicAttack_OnMissileLaunch /
_OnHit; the cougar's claw NidaleeCougarBasicAttack_OnCast / _OnHit; Takedown's Takedown_OnCast (arming),
NidaleeTakedownAttack_OnCast / _OnHit (the bite); Javelin Toss's JavelinToss_OnMissileLaunch / _hit; Primal Surge's
PrimalSurge_OnCast / _OnBuffActivate; Bushwhack's _OnCast / _set / _hit; Pounce's _OnCast / _land / _hit; Swipe's _OnCast /
_OnHit; Aspect of the Cougar's AspectOfTheCougar_OnCast (both ways; the cougar's from the cougar bank); the hunt pounce
uses Pounce_markjump and Pounce_hit. Voice: the spell lines (Spell3DQCast, Spell3DWCast, Spell3DECast, Spell3DRCast,
AspectOfTheCougar_OnCast) and the cougar's growls (NidaleeCougarBasicAttack_OnCast voice).
Icons: Nidalee_Q1 = skill (Q), Nidalee_E1 = skill2 (E + W, the cougar's W + E), Nidalee_R1 = ult; the cougar's Q2 / W2 /
E2, the human W1 and the passive are written too (README / buff icons).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/nidalee/skins/base/nidalee_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/nidalee/skins/base/nidalee_base_vo_"  # same in every language
P = "Play_sfx_Nidalee_"
PC = "Play_sfx_NidaleeCougar_"
V = "Play_vo_Nidalee_"
VC = "Play_vo_NidaleeCougar_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_nidalee_sfx_a_throw": (P + "NidaleeBasicAttack_OnMissileLaunch", 155982393, 0.5, -12),
    "league_nidalee_sfx_a_hit": (P + "NidaleeBasicAttack_OnHit", 205535710, 0.5, -12),
    "league_nidalee_sfx_c_swing": (PC + "NidaleeCougarBasicAttack_OnCast", 3505277, 0.45, -12),
    "league_nidalee_sfx_c_hit": (PC + "NidaleeCougarBasicAttack_OnHit", 414125210, 0.6, -12),
    "league_nidalee_sfx_cq_arm": (PC + "Takedown_OnCast", 522414047, 0.8, -11),
    "league_nidalee_sfx_cq": (PC + "NidaleeTakedownAttack_OnCast", 459397109, 0.5, -11),
    "league_nidalee_sfx_cq_hit": (PC + "NidaleeTakedownAttack_OnHit", 1001408241, 0.7, -9),
    "league_nidalee_sfx_q": (P + "JavelinToss_OnMissileLaunch", 417490357, 1.0, -10),
    "league_nidalee_sfx_q_hit": (P + "JavelinToss_hit", 45616270, 0.9, -9),
    "league_nidalee_sfx_e": (P + "PrimalSurge_OnCast", 739688255, 1.2, -10),
    "league_nidalee_sfx_e_heal": (P + "PrimalSurge_OnBuffActivate", 135103839, 1.2, -11),
    "league_nidalee_sfx_w": (P + "Bushwhack_OnCast", 173717048, 0.7, -11),
    "league_nidalee_sfx_w_land": (P + "Bushwhack_set", 94703923, 0.8, -11),
    "league_nidalee_sfx_w_snap": (P + "Bushwhack_hit", 87377778, 0.9, -10),
    "league_nidalee_sfx_cw": (PC + "Pounce_OnCast", 857424827, 0.6, -11),
    "league_nidalee_sfx_cw_land": (PC + "Pounce_land", 881689960, 0.7, -10),
    "league_nidalee_sfx_cw_hit": (PC + "Pounce_hit", 477372588, 0.6, -10),
    "league_nidalee_sfx_ce": (PC + "Swipe_OnCast", 317712980, 0.8, -10),
    "league_nidalee_sfx_ce_hit": (PC + "Swipe_OnHit", 205535710, 0.5, -11),
    "league_nidalee_sfx_tf_cougar": (P + "AspectOfTheCougar_OnCast", 796904591, 1.0, -10),
    "league_nidalee_sfx_tf_human": (PC + "AspectOfTheCougar_OnCast", 837477622, 1.0, -10),
    "league_nidalee_sfx_r": (PC + "Pounce_markjump", 1018287005, 1.0, -9),
    "league_nidalee_sfx_r_hit": (PC + "Pounce_hit", 106745466, 0.7, -9),
    "league_nidalee_sfx_vo_q": (V + "Spell3DQCast", 86413726, 2.0, -4),
    "league_nidalee_sfx_vo_w": (V + "Spell3DWCast", 815778723, 2.0, -4),
    "league_nidalee_sfx_vo_e": (V + "Spell3DECast", 1248730215, 2.0, -4),
    "league_nidalee_sfx_vo_cougar": (V + "AspectOfTheCougar_OnCast", 924645128, 2.0, -4),
    "league_nidalee_sfx_vo_human": (V + "Spell3DRCast", 644797782, 2.0, -4),
    "league_nidalee_sfx_vo_cq": (VC + "NidaleeCougarBasicAttack_OnCast", 87116344, 1.2, -5),
    "league_nidalee_sfx_vo_cw": (VC + "NidaleeCougarBasicAttack_OnCast", 913026718, 1.2, -5),
    "league_nidalee_sfx_vo_ce": (VC + "NidaleeCougarBasicAttack_OnCast", 143626893, 1.2, -5),
    "league_nidalee_sfx_vo_r": (V + "Kill3DQ", 178013572, 2.2, -4),
}
I = "ASSETS/Characters/Nidalee/HUD/Icons2D/Nidalee_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_nidalee_skill": I + "Q1.dds",
    "league_nidalee_skill2": I + "E1.dds",
    "league_nidalee_ult": I + "R1.dds",
    "league_nidalee_w": I + "W1.dds",
    "league_nidalee_cougar_q": I + "Q2.dds",
    "league_nidalee_cougar_w": I + "W2.dds",
    "league_nidalee_cougar_e": I + "E2.dds",
    "league_nidalee_passive": I + "Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Nidalee.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Nidalee.{args.lang}.wad.client"))
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
