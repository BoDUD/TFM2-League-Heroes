"""Pull Lucian's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_lucian.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Lucian.wad.client and Lucian.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Lucian's skin bin. The basic attack has its shot and its hit; Lightslinger's second
shot its own shot (PassiveShot); Piercing Light the cast, the beam (QLaser) and the hit on its target;
Relentless Pursuit the dash; Ardent Blaze the throw and the star burst (WBlowup); The Culling the cast and the
3.9 s firing loop (R_OnBuffActivate, cut to the 3 s channel), which carries the shots, so the single shots and
their hits are left out. Q has no voice event; of E's and R's zh_CN takes (each its own recording) the ones
with the most syllables are used - E's takes are short, W's are grunts, so skill2 (E, then W) plays E's.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/lucian/skins/base/lucian_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/lucian/skins/base/lucian_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_lucian_sfx_attack_shot": ("Play_sfx_Lucian_LucianBasicAttack_OnMissileCast", 938350373, 0.6, -6),
    "league_lucian_sfx_attack_hit": ("Play_sfx_Lucian_LucianBasicAttack_OnHit", 12194984, 0.45, -8),
    "league_lucian_sfx_passive_shot": ("Play_sfx_Lucian_LucianPassiveShot_OnMissileCast", 782739414, 0.8, -6),
    "league_lucian_sfx_q_cast": ("Play_sfx_Lucian_LucianQ_OnCast", 264429047, 0.6, -4),
    "league_lucian_sfx_q_beam": ("Play_sfx_Lucian_LucianQLaser_buffactivate", 1031670556, 1.1, -3),
    "league_lucian_sfx_q_hit": ("Play_sfx_Lucian_LucianQTar_hit", 48637357, 0.9, -5),
    "league_lucian_sfx_e_cast": ("Play_sfx_Lucian_LucianE_OnCast", 360306981, 1.2, -4),
    "league_lucian_sfx_w_cast": ("Play_sfx_Lucian_LucianW_OnCast", 578852102, 1.2, -4),
    "league_lucian_sfx_w_boom": ("Play_sfx_Lucian_LucianWBlowup_buffdeactivate", 188382466, 1.4, -3),
    "league_lucian_sfx_r_cast": ("Play_sfx_Lucian_LucianR_OnCast", 335009448, 1.3, -3),
    "league_lucian_sfx_r_loop": ("Play_sfx_Lucian_LucianR_OnBuffActivate", 134398349, 3.1, -3),
    "league_lucian_vo_e": ("Play_vo_Lucian_LucianE_cast3D", 1201627478, 1.8, -2),
    "league_lucian_vo_r": ("Play_vo_Lucian_LucianR_cast3D", 177848601, 2.4, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (skill2 is Relentless Pursuit with Ardent Blaze folded in: E's icon)
    "league_lucian_skill": "ASSETS/Characters/Lucian/HUD/Icons2D/Lucian_Q.dds",
    "league_lucian_skill2": "ASSETS/Characters/Lucian/HUD/Icons2D/Lucian_E.dds",
    "league_lucian_ult": "ASSETS/Characters/Lucian/HUD/Icons2D/Lucian_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Lucian.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Lucian.{args.lang}.wad.client"))
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
