"""Pull Diana's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_diana.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Diana.wad.client and Diana.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Diana's skin bin. The basic attack keeps its hit (the engine plays nothing of its own);
Moonsilver Blade the passive's cleave hit; Crescent Strike the cast and the hit; Lunar Rush (DianaTeleport) the
cast, the hit and the reset that League plays when Moonlight refreshes it (our second dash); Pale Cascade
(DianaOrbs) the cast and an orb bursting; Moonfall the cast and the explosion. Of the zh_CN voice takes (each its
own recording) the longest ones are used.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/diana/skins/base/diana_base_sfx_"
# the same path in every language WAD
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/diana/skins/base/diana_base_vo_"

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_diana_sfx_attack_hit": ("Play_sfx_Diana_DianaBasicAttack_OnHit", 363509313, 0.6, -6),
    "league_diana_sfx_p_cleave": ("Play_sfx_Diana_DianaPassive_hit", 138429463, 0.8, -4),
    "league_diana_sfx_q_cast": ("Play_sfx_Diana_DianaQ_OnCast", 652835584, 1.0, -4),
    "league_diana_sfx_q_hit": ("Play_sfx_Diana_DianaQ_hit", 818928799, 1.1, -4),
    "league_diana_sfx_e_cast": ("Play_sfx_Diana_DianaTeleport_OnCast", 222728383, 0.8, -4),
    "league_diana_sfx_e_hit": ("Play_sfx_Diana_DianaTeleport_hit", 251927895, 1.25, -3),
    "league_diana_sfx_e_reset": ("Play_sfx_Diana_DianaTeleport_reset", 1065466632, 1.35, -4),
    "league_diana_sfx_w_cast": ("Play_sfx_Diana_DianaOrbs_OnCast", 190100675, 1.5, -4),
    "league_diana_sfx_w_boom": ("Play_sfx_Diana_DianaOrbs_hit", 397954602, 0.7, -5),
    "league_diana_sfx_r_cast": ("Play_sfx_Diana_DianaR_OnCast", 263775990, 1.4, -3),
    "league_diana_sfx_r_crash": ("Play_sfx_Diana_DianaR_explosion", 638743450, 1.35, -2),
    "league_diana_vo_q": ("Play_vo_Diana_DianaQ_cast3D", 62500138, 0.8, -2),
    "league_diana_vo_e": ("Play_vo_Diana_DianaTeleport_cast3D", 1260035381, 0.5, -2),
    "league_diana_vo_w": ("Play_vo_Diana_DianaOrbs_cast3D", 357232304, 0.6, -2),
    "league_diana_vo_r": ("Play_vo_Diana_DianaR_cast3D", 732886826, 1.3, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (skill2 is Lunar Rush with Pale Cascade folded in: E's icon)
    "league_diana_skill": "ASSETS/Characters/Diana/HUD/Icons2D/Diana_Q_MoonsEdge.dds",
    "league_diana_skill2": "ASSETS/Characters/Diana/HUD/Icons2D/Diana_E_FasterThanLight.dds",
    "league_diana_ult": "ASSETS/Characters/Diana/HUD/Icons2D/Diana_R_MoonFall.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Diana.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Diana.{args.lang}.wad.client"))
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
