r"""Pull Sion's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_sion.py --lol "D:\WeGameApps\lol" --vgmstream pathgmstream-cli.exe

Same route as extract_galio.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Sion.wad.client and Sion.<lang>.wad.client, resolves the base-skin Wwise events below to their
media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games)
plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in his bins, the longest variant): the axe swing SionBasicAttack_OnCast / _OnHit; Decimating Smash's
charge SionQ_OnBuffActivate and its full-charge slam SionQSoundAfterHalf_OnBuffCast; Roar of the Slayer's SionE_OnCast
and the shred SionEArmorShred_OnBuffCast; Soul Furnace's shield SionWShieldStacks_OnBuffActivate and its blast
_OnBuffDeactivate; Unstoppable Onslaught's start SionR_OnBuffCast and its crash SionR_OnBuffDeactivate; Glory in Death's
rise SionPassiveZombie_OnBuffCast (the add-on's). Voice: SionQ_cast3D, SionWSoundShield_OnBuffCast, SionE_cast3D,
SionR_cast3D, and for the add-on's revive SionPassiveDelay_OnBuffCast.
Icons: Sion_Q = skill (Q), Sion_E = skill2 (E, W folded in), Sion_R1 = ult (R); Sion_W1 and Sion_Passive1 are written
too (README / the add-on).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/sion/skins/base/sion_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/sion/skins/base/sion_base_vo_"  # same in every language
P = "Play_sfx_Sion_"
V = "Play_vo_Sion_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_sion_sfx_a_swing": (P + "SionBasicAttack_OnCast", 897132531, 0.5, -12),
    "league_sion_sfx_a_hit": (P + "SionBasicAttack_OnHit", 118086465, 0.6, -11),
    "league_sion_sfx_q": (P + "SionQ_OnBuffActivate", 852118441, 1.2, -11),
    "league_sion_sfx_q_hit": (P + "SionQSoundAfterHalf_OnBuffCast", 15771971, 1.4, -8),
    "league_sion_sfx_e": (P + "SionE_OnCast", 923553686, 1.2, -10),
    "league_sion_sfx_e_hit": (P + "SionEArmorShred_OnBuffCast", 336304205, 0.8, -10),
    "league_sion_sfx_w": (P + "SionWShieldStacks_OnBuffActivate", 660225775, 1.4, -11),
    "league_sion_sfx_w_hit": (P + "SionWShieldStacks_OnBuffDeactivate", 257941783, 1.4, -9),
    "league_sion_sfx_r": (P + "SionR_OnBuffCast", 433162662, 1.6, -10),
    "league_sion_sfx_r_hit": (P + "SionR_OnBuffDeactivate", 562047862, 1.8, -8),
    "league_sion_sfx_p_rise": (P + "SionPassiveZombie_OnBuffCast", 75479208, 1.8, -10),
    "league_sion_sfx_vo_q": (V + "SionQ_cast3D", 311603564, 2.2, -4),
    "league_sion_sfx_vo_w": (V + "SionWSoundShield_OnBuffCast", 452555665, 2.2, -4),
    "league_sion_sfx_vo_e": (V + "SionE_cast3D", 1549454433, 2.2, -4),
    "league_sion_sfx_vo_r": (V + "SionR_cast3D", 713439442, 2.6, -4),
    "league_sion_sfx_vo_p": (V + "SionPassiveDelay_OnBuffCast", 649009447, 2.2, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_sion_skill": "ASSETS/Characters/Sion/HUD/Icons2D/Sion_Q.dds",
    "league_sion_skill2": "ASSETS/Characters/Sion/HUD/Icons2D/Sion_E.dds",
    "league_sion_ult": "ASSETS/Characters/Sion/HUD/Icons2D/Sion_R1.dds",
    "league_sion_w": "ASSETS/Characters/Sion/HUD/Icons2D/Sion_W1.dds",
    "league_sion_passive": "ASSETS/Characters/Sion/HUD/Icons2D/Sion_Passive1.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Sion.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Sion.{args.lang}.wad.client"))
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
