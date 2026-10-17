r"""Pull Swain's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_swain.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_reksai.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Swain.wad.client and Swain.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in the skin bins, prefix Play_sfx_Swain_Swain): the attack's click BasicAttack_OnCast (the action's
start) and its raven bolt's whoosh BasicAttack_OnMissileLaunch (the release tick), BasicAttack_OnHit; Death's Hand
Q_OnCast and the bolts QMissile_castmiss (release), QMissile_hit_target; Nevermove E_OnCast, the hand E_OnMissileCast
(release), its way back EReturnMissile_OnMissileLaunch, the root ERoot_hit_champ, the pull PDisplacementCheck_buffactivate;
Vision of Empire's eye W_hitlocation and its blast W_hit; a fragment PSoulCollect_hit; Demonic Ascension R_OnCast, the
demon R_buffactivate, Demonflare RSoulFlare_buffdeactivate and RSoulFlare_hit. Voice (Play_vo_Swain_): SwainQ_cast3D,
SwainE_cast3D, Spell2DPCastGeneral (the eye), Laugh3DGeneral (the demon rising), Spell3DREnd (Demonflare).
Icons: swain_q = skill, swain_e = skill2, swain_r = ult; swain_w / e2 / r2 / p are written too (league_swain_w, _e2,
_r2, _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/swain/skins/base/swain_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/swain/skins/base/swain_base_vo_"  # same in every language
P = "Play_sfx_Swain_Swain"
V = "Play_vo_Swain_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_swain_sfx_a_cast": (P + "BasicAttack_OnCast", 585637667, 0.5, -16),
    "league_swain_sfx_a_launch": (P + "BasicAttack_OnMissileLaunch", 630500580, 0.6, -14),
    "league_swain_sfx_a_hit": (P + "BasicAttack_OnHit", 437968055, 0.6, -14),
    "league_swain_sfx_q": (P + "Q_OnCast", 372007732, 0.6, -13),
    "league_swain_sfx_q_launch": (P + "QMissile_castmiss", 236656213, 0.9, -12),
    "league_swain_sfx_q_hit": (P + "QMissile_hit_target", 648449935, 0.6, -13),
    "league_swain_sfx_e": (P + "E_OnCast", 709057759, 0.6, -13),
    "league_swain_sfx_e_launch": (P + "E_OnMissileCast", 125188364, 1.0, -12),
    "league_swain_sfx_e_back": (P + "EReturnMissile_OnMissileLaunch", 969383508, 1.0, -12),
    "league_swain_sfx_e_hit": (P + "ERoot_hit_champ", 655946240, 1.0, -11),
    "league_swain_sfx_e_pull": (P + "PDisplacementCheck_buffactivate", 762123083, 1.2, -11),
    "league_swain_sfx_w_open": (P + "W_hitlocation", 510294382, 1.4, -11),
    "league_swain_sfx_w_hit": (P + "W_hit", 785137315, 0.6, -12),
    "league_swain_sfx_p_frag": (P + "PSoulCollect_hit", 296557267, 1.2, -12),
    "league_swain_sfx_r": (P + "R_OnCast", 690795204, 1.6, -10),
    "league_swain_sfx_r_rise": (P + "R_buffactivate", 770657740, 2.4, -10),
    "league_swain_sfx_r_flare": (P + "RSoulFlare_buffdeactivate", 522310967, 1.2, -9),
    "league_swain_sfx_r_fl_hit": (P + "RSoulFlare_hit", 605475180, 0.8, -11),
    "league_swain_sfx_vo_q": (V + "SwainQ_cast3D", 1397975458, 1.5, -6),
    "league_swain_sfx_vo_e": (V + "SwainE_cast3D", 292096052, 1.5, -6),
    "league_swain_sfx_vo_w": (V + "Spell2DPCastGeneral", 94031978, 2.5, -6),
    "league_swain_sfx_vo_r": (V + "Laugh3DGeneral", 2112121098, 3.0, -6),
    "league_swain_sfx_vo_r2": (V + "Spell3DREnd", 629723546, 2.0, -6),
}
I = "assets/characters/swain/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_swain_skill": I + "swain_q.dds",
    "league_swain_skill2": I + "swain_e.dds",
    "league_swain_ult": I + "swain_r.dds",
    "league_swain_w": I + "swain_w.dds",
    "league_swain_e2": I + "swain_e2.dds",
    "league_swain_r2": I + "swain_r2.dds",
    "league_swain_passive": I + "swain_p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Swain.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Swain.{args.lang}.wad.client"))
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
