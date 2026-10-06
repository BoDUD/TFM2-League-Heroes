"""Pull Sona's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_sona.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Sona.wad.client and Sona.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN
(Tencent client) by default.

Her events in the base bank: SonaBasicAttack_OnMissileLaunch / _OnHit (the note), SonaP_stack_buffactivate / _hit
(Power Chord ready / its hit), SonaQ_OnCast and SonaQMissile_OnHit (Q), SonaW_OnCast (W), SonaE_OnCast (E), SonaR_OnCast,
SonaR_OnMissileLaunch and SonaR_OnHit (R); voice: SonaQ_cast2D, SonaW_cast2D, SonaE_cast2D and SonaR_cast2D (her lines
are spoken in the client's language). The icons: Sona_Q = Q, Sona_W = W (E rides on it), Sona_R = R (Power Chord and
Song of Celerity are folded into the attack and W, which have no icon of their own).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/sona/skins/base/sona_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/sona/skins/base/sona_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_sona_sfx_attack": ("Play_sfx_Sona_SonaBasicAttack_OnMissileLaunch", 73391190, 0.8, -10),
    "league_sona_sfx_attack_hit": ("Play_sfx_Sona_SonaBasicAttack_OnHit", 712339436, 0.6, -10),
    "league_sona_sfx_pc_ready": ("Play_sfx_Sona_SonaP_stack_buffactivate", 649063422, 1.2, -9),
    "league_sona_sfx_pc_hit": ("Play_sfx_Sona_SonaP_stack_hit", 222762516, 0.9, -7),
    "league_sona_sfx_q_cast": ("Play_sfx_Sona_SonaQ_OnCast", 935538306, 1.5, -7),
    "league_sona_sfx_q_hit": ("Play_sfx_Sona_SonaQMissile_OnHit", 570612907, 0.9, -9),
    "league_sona_sfx_w_cast": ("Play_sfx_Sona_SonaW_OnCast", 408552087, 1.8, -7),
    "league_sona_sfx_e_cast": ("Play_sfx_Sona_SonaE_OnCast", 995490257, 1.8, -8),
    "league_sona_sfx_r_cast": ("Play_sfx_Sona_SonaR_OnCast", 497885951, 1.8, -5),
    "league_sona_sfx_r_wave": ("Play_sfx_Sona_SonaR_OnMissileLaunch", 1012366840, 1.5, -6),
    "league_sona_sfx_r_hit": ("Play_sfx_Sona_SonaR_OnHit", 702153267, 1.1, -6),
    "league_sona_sfx_vo_q": ("Play_vo_Sona_SonaQ_cast2D", 998215567, 2.6, -2),
    "league_sona_sfx_vo_w": ("Play_vo_Sona_SonaW_cast2D", 265806099, 2.8, -2),
    "league_sona_sfx_vo_e": ("Play_vo_Sona_SonaE_cast2D", 2146325456, 2.7, -2),
    "league_sona_sfx_vo_r": ("Play_vo_Sona_SonaR_cast2D", 966893816, 2.6, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_sona_skill": "ASSETS/Characters/Sona/HUD/Icons2D/Sona_Q.dds",
    "league_sona_skill2": "ASSETS/Characters/Sona/HUD/Icons2D/Sona_W.dds",
    "league_sona_ult": "ASSETS/Characters/Sona/HUD/Icons2D/Sona_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Sona.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Sona.{args.lang}.wad.client"))
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
            print(f"{name:34s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:34s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
