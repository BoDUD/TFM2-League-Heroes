"""Pull Miss Fortune's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_missfortune.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/MissFortune.wad.client and MissFortune.<lang>.wad.client, resolves the
base-skin Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs
to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in her base bins (Play_sfx_MissFortune_* / Play_vo_MissFortune_*); her spells go
by their old names there: RicochetShot = Double Up (Q), ViciousStrikes = Strut (W), Scattershot = Make
It Rain (E), BulletTime (R), PassiveAttack = the Love Tap shot. The basic attack is the pistol shot
(OnMissileLaunch) and its impact; Love Tap's own sting is PassiveAttack_OnHitLocation. Double Up's
bounce takes the heaviest of the four RicochetShot impacts when it crits. Make It Rain's cast is the
whole rain (2.4 s, the zone lasts 2 s) with Strut's activation laid over it, since Strut rides on it.
Bullet Time's waves each play one short burst of BulletEMPTY_OnMissileLaunch (the wave missile's
launch; cut to 0.4 s, played every 0.25 s). The zh_CN voice bank has lines for Double Up, Strut and
Bullet Time (all translated: none is byte-equal to the en_US bank); Make It Rain has no voice event,
so its cast carries Strut's line.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/missfortune/skins/base/missfortune_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/missfortune/skins/base/missfortune_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_missfortune_sfx_attack_shot": ("Play_sfx_MissFortune_MissFortuneBasicAttack_OnMissileLaunch", 108461385, 0.6, -5),
    "league_missfortune_sfx_attack_hit": ("Play_sfx_MissFortune_MissFortuneBasicAttack_OnHit", 12546636, 0.5, -7),
    "league_missfortune_sfx_lovetap": ("Play_sfx_MissFortune_MissFortunePassiveAttack_OnHitLocation", 192796325, 0.8, -4),
    "league_missfortune_sfx_q_cast": ("Play_sfx_MissFortune_MissFortuneRicochetShot_OnMissileLaunch", 648037541, 0.9, -4),
    "league_missfortune_sfx_q_hit": ("Play_sfx_MissFortune_MissFortuneRicochetShot_OnHit", 1045719607, 0.7, -5),
    "league_missfortune_sfx_q_crit": ("Play_sfx_MissFortune_MissFortuneRicochetShot_OnHit", 695039564, 1.2, -3),
    "league_missfortune_sfx_e_cast": ("Play_sfx_MissFortune_MissFortuneScattershot_OnCast", 1003982027, 2.4, -4),
    "league_missfortune_sfx_w_cast": ("Play_sfx_MissFortune_MissFortuneViciousStrikes_OnCast", 404636949, 1.2, -6),
    "league_missfortune_sfx_r_cast": ("Play_sfx_MissFortune_MissFortuneBulletTime_OnCast", 58950279, 1.9, -4),
    "league_missfortune_sfx_r_wave": ("Play_sfx_MissFortune_MissFortuneBulletEMPTY_OnMissileLaunch", 144571401, 0.4, -8),
    "league_missfortune_vo_q": ("Play_vo_MissFortune_MissFortuneRicochetShot_cast3D", 2124526640, 1.4, -2),
    "league_missfortune_vo_w": ("Play_vo_MissFortune_MissFortuneViciousStrikes_cast3D", 200074209, 2.0, -2),
    "league_missfortune_vo_r": ("Play_vo_MissFortune_MissFortuneBulletTime_cast3D", 1460557540, 3.2, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Strut rides on Make It Rain, Love Tap is a passive: no slots)
    "league_missfortune_skill": "ASSETS/Characters/MissFortune/HUD/Icons2D/MissFortune_Q.dds",
    "league_missfortune_skill2": "ASSETS/Characters/MissFortune/HUD/Icons2D/MissFortune_E.dds",
    "league_missfortune_ult": "ASSETS/Characters/MissFortune/HUD/Icons2D/MissFortune_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "MissFortune.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"MissFortune.{args.lang}.wad.client"))
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
