"""Pull Malphite's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_malphite.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Malphite.wad.client and Malphite.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

His spells go by these names in the base bins: SeismicShard = Q, MalphiteThunderclap / CleaveArc = W (the
buff and the cone hit of its empowered attacks), Landslide = Ground Slam (E), UFSlash = Unstoppable Force
(R), MalphiteShieldEffect = Granite Shield (it comes back). The zh_CN voice bank has only twelve events and
no spell lines: League plays one of four efforts (Spell3DBasic, the same four as Landslide_cast3D) on his
spells, so Seismic Shard and Ground Slam take two of those, and Unstoppable Force takes a short attack line
(Attack2DGeneral) in their place.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/malphite/skins/base/malphite_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/malphite/skins/base/malphite_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_malphite_sfx_attack_hit": ("Play_sfx_Malphite_MalphiteBasicAttack_OnHit", 365680144, 0.6, -6),
    "league_malphite_sfx_w_hit": ("Play_sfx_Malphite_CleaveArc_hit", 420359461, 0.8, -4),
    "league_malphite_sfx_w_on": ("Play_sfx_Malphite_MalphiteThunderclap_OnBuffActivate", 255731332, 1.2, -8),
    "league_malphite_sfx_q_cast": ("Play_sfx_Malphite_SeismicShard_OnCast", 80020153, 0.9, -4),
    "league_malphite_sfx_q_hit": ("Play_sfx_Malphite_SeismicShard_OnHit", 834748279, 1.1, -4),
    "league_malphite_sfx_e_cast": ("Play_sfx_Malphite_Landslide_OnCast", 1045794121, 0.4, -5),
    "league_malphite_sfx_e_hit": ("Play_sfx_Malphite_Landslide_hit", 233503083, 1.3, -3),
    "league_malphite_sfx_r_cast": ("Play_sfx_Malphite_UFSlash_OnCast", 50545186, 1.6, -4),
    "league_malphite_sfx_r_land": ("Play_sfx_Malphite_UFSlash_land", 365334701, 1.5, -2),
    "league_malphite_sfx_r_hit": ("Play_sfx_Malphite_UFSlash_hit", 586583816, 1.2, -4),
    "league_malphite_sfx_granite": ("Play_sfx_Malphite_MalphiteShieldEffect_OnBuffActivate", 203686964, 1.1, -6),
    "league_malphite_vo_q": ("Play_vo_Malphite_Spell3DBasic", 865060095, 0.8, -2),
    "league_malphite_vo_e": ("Play_vo_Malphite_Landslide_cast3D", 1000912454, 0.8, -2),
    "league_malphite_vo_r": ("Play_vo_Malphite_Attack2DGeneral", 526103148, 2.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Thunderclap rides on Ground Slam, Granite Shield is the passive: no slots)
    "league_malphite_skill": "ASSETS/Characters/Malphite/HUD/Icons2D/Malphite_Q.dds",
    "league_malphite_skill2": "ASSETS/Characters/Malphite/HUD/Icons2D/Malphite_E.dds",
    "league_malphite_ult": "ASSETS/Characters/Malphite/HUD/Icons2D/Malphite_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Malphite.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Malphite.{args.lang}.wad.client"))
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
            print(f"{name:36s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:36s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
