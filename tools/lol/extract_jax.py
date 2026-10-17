"""Pull Jax's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_jax.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Jax.wad.client and Jax.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Jax's skin bin. The basic attack keeps League's swing (played by the engine as
league_jax_attack) and its hit; Empower its charge-up and its hit; Leap Strike the jump and the landing;
Counter Strike the stance's start and its counter (the stance loop is cut to the 2 s stance, the hit of
each stunned champion to 1 s); Grandmaster-at-Arms the cast, the slam and the passive's third hit. Of the
zh_CN voice takes (each its own recording) the longest ones are used. The long buff events (Empower's
4.3 s charge hum, R's 11 s armour hum) are cut to their start.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/jax/skins/base/jax_base_sfx_"
# the same path in every language WAD
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/jax/skins/base/jax_base_vo_"

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_jax_sfx_attack": ("Play_sfx_Jax_JaxBasicAttack_OnCast", 581722606, 0.8, -8),
    "league_jax_sfx_attack_hit": ("Play_sfx_Jax_JaxBasicAttack_OnHit", 236648208, 0.65, -6),
    "league_jax_sfx_w_cast": ("Play_sfx_Jax_JaxW_OnCast", 386131772, 1.0, -5),
    "league_jax_sfx_w_hit": ("Play_sfx_Jax_JaxW_hit", 186437953, 1.2, -3),
    "league_jax_sfx_q_cast": ("Play_sfx_Jax_JaxQ_cast", 176264222, 1.2, -4),
    "league_jax_sfx_q_hit": ("Play_sfx_Jax_JaxQ_hit", 510862683, 1.3, -3),
    "league_jax_sfx_e_cast": ("Play_sfx_Jax_JaxE_OnBuffActivate", 338032282, 2.0, -5),
    "league_jax_sfx_e_burst": ("Play_sfx_Jax_JaxE_OnBuffDeactivate", 979182295, 1.5, -3),
    "league_jax_sfx_e_hit": ("Play_sfx_Jax_JaxE_hit", 954101919, 1.0, -5),
    "league_jax_sfx_r_cast": ("Play_sfx_Jax_JaxR_OnCast", 667472112, 1.4, -4),
    "league_jax_sfx_r_slam": ("Play_sfx_Jax_JaxR_hit_aoe", 101899824, 1.8, -2),
    "league_jax_sfx_r_proc": ("Play_sfx_Jax_JaxRPassiveAttack_OnHit", 453571133, 1.0, -4),
    "league_jax_vo_w": ("Play_vo_Jax_JaxWAttack_cast3D", 42077869, 2.8, -2),
    "league_jax_vo_q": ("Play_vo_Jax_JaxQ_cast3D", 1264796763, 1.2, -2),
    "league_jax_vo_e": ("Play_vo_Jax_JaxE_cast3D", 1006203993, 2.1, -2),
    "league_jax_vo_r": ("Play_vo_Jax_JaxR_cast3D", 1913787277, 2.9, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (skill is Leap Strike with Empower folded in: Q's icon)
    "league_jax_skill": "ASSETS/Characters/Jax/HUD/Icons2D/JaxQ.dds",
    "league_jax_skill2": "ASSETS/Characters/Jax/HUD/Icons2D/JaxE.dds",
    "league_jax_ult": "ASSETS/Characters/Jax/HUD/Icons2D/JaxR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Jax.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Jax.{args.lang}.wad.client"))
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
