"""Pull Annie's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_annie.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Annie.wad.client and Annie.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Annie's champion bin. The basic attack uses the fireball's launch and hit;
Pyromania's "stun ready" chime is AnniePassivePrimed. W and E have no voice line, Q and R do. R: the
summon, Tibbers landing (AnnieR_OnHitLocation), one of his claw hits for the burn he keeps up, and his
death puff when he leaves (AnnieTibbers_AnnieR_death). Voice variants were picked by length.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/annie/skins/base/annie_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/annie/skins/base/annie_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_annie_sfx_attack_cast": ("Play_sfx_Annie_AnnieBasicAttack_OnMissileLaunch", 737347388, 0.6, -6),
    "league_annie_sfx_attack_hit": ("Play_sfx_Annie_AnnieBasicAttack_OnHit", 217008179, 0.6, -6),
    "league_annie_sfx_q_cast": ("Play_sfx_Annie_AnnieQ_OnMissileLaunch", 826331018, 0.8, -4),
    "league_annie_sfx_q_hit": ("Play_sfx_Annie_AnnieQ_OnHit", 902755762, 1.0, -4),
    "league_annie_sfx_w_cast": ("Play_sfx_Annie_AnnieW_OnCast", 573847713, 1.2, -4),
    "league_annie_sfx_w_hit": ("Play_sfx_Annie_AnnieW_hit", 339807363, 1.0, -5),
    "league_annie_sfx_e_cast": ("Play_sfx_Annie_AnnieE_OnCast", 70623096, 1.2, -5),
    "league_annie_sfx_pyro_ready": ("Play_sfx_Annie_AnniePassivePrimed_OnBuffActivate", 989931317, 1.2, -6),
    "league_annie_sfx_r_cast": ("Play_sfx_Annie_AnnieR_OnCast", 637486965, 1.5, -4),
    "league_annie_sfx_r_hit": ("Play_sfx_Annie_AnnieR_OnHitLocation", 840469966, 1.0, -3),
    "league_annie_sfx_r_swipe": ("Play_sfx_AnnieTibbers_AnnieTibbersBasicAttack_OnHit", 149458517, 0.4, -8),
    "league_annie_sfx_r_vanish": ("Play_sfx_AnnieTibbers_AnnieR_death_buffactivate", 472797351, 1.2, -5),
    "league_annie_vo_q": ("Play_vo_Annie_Spell3DQCast", 1875196408, 1.1, -2),
    "league_annie_vo_r": ("Play_vo_Annie_Spell3DRCast", 726514407, 1.7, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (skill2 is W with E folded in: W's icon)
    "league_annie_skill": "ASSETS/Characters/Annie/HUD/Icons2D/Annie_Q.dds",
    "league_annie_skill2": "ASSETS/Characters/Annie/HUD/Icons2D/Annie_W.dds",
    "league_annie_ult": "ASSETS/Characters/Annie/HUD/Icons2D/Annie_R1.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Annie.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Annie.{args.lang}.wad.client"))
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
            print(f"{name:32s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:32s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
