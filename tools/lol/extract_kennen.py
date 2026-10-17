"""Pull Kennen's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_kennen.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Kennen.wad.client and Kennen.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

His events in the base bank (the client's own names): KennenBasicAttack_OnMissileLaunch (the shuriken),
KennenMegaProc_OnMissileLaunch / _OnHit (W's passive, the charged fifth attack), KennenShurikenHurlMissile1_OnCast /
_OnMissileLaunch (Q, Thundering Shuriken), KennenBringTheLight_OnCast / _hit (W's active, Electrical Surge),
KennenLightningRush_OnCast / _OnBuffDeactivate (E), KennenShurikenStorm_OnCast / _OnBuffDeactivate (R, Slicing
Maelstrom) and KennenMarkoftheStorm_stun (the passive's stun). The hit events of the attack, Q, E and R have no media,
so those hits borrow the electric crackles of the stun / surge banks (quieter). Voice: KennenShurikenHurlMissile1 /
KennenBringTheLight / KennenShurikenStorm _cast3D and Spell3DEEnd. The icons: Kennen_Q = Q, Kennen_E = E, Kennen_R = R
(W rides on the attack, E and Q; the passive has no slot).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/kennen/skins/base/kennen_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/kennen/skins/base/kennen_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_kennen_sfx_attack": ("Play_sfx_Kennen_KennenBasicAttack_OnMissileLaunch", 482567023, 0.6, -10),
    "league_kennen_sfx_attack_hit": ("Play_sfx_Kennen_KennenMegaProc_OnHit", 712972053, 0.5, -16),
    "league_kennen_sfx_mega_cast": ("Play_sfx_Kennen_KennenMegaProc_OnMissileLaunch", 447960467, 0.8, -8),
    "league_kennen_sfx_mega_hit": ("Play_sfx_Kennen_KennenMegaProc_OnHit", 561930678, 0.8, -8),
    "league_kennen_sfx_q_cast": ("Play_sfx_Kennen_KennenShurikenHurlMissile1_OnMissileLaunch", 382471083, 0.8, -7),
    "league_kennen_sfx_q_hit": ("Play_sfx_Kennen_KennenMegaProc_OnHit", 850375143, 0.6, -9),
    "league_kennen_sfx_w_cast": ("Play_sfx_Kennen_KennenBringTheLight_OnCast", 644827456, 1.0, -6),
    "league_kennen_sfx_w_hit": ("Play_sfx_Kennen_KennenBringTheLight_hit", 129502230, 0.8, -9),
    "league_kennen_sfx_e_cast": ("Play_sfx_Kennen_KennenLightningRush_OnCast", 956536846, 1.0, -6),
    "league_kennen_sfx_e_hit": ("Play_sfx_Kennen_KennenBringTheLight_hit", 286257656, 0.6, -12),
    "league_kennen_sfx_e_end": ("Play_sfx_Kennen_KennenLightningRush_OnBuffDeactivate", 632022094, 0.8, -8),
    "league_kennen_sfx_stun": ("Play_sfx_Kennen_KennenMarkoftheStorm_stun", 139579831, 1.0, -6),
    "league_kennen_sfx_r_cast": ("Play_sfx_Kennen_KennenShurikenStorm_OnCast", 274150043, 3.0, -5),
    "league_kennen_sfx_r_hit": ("Play_sfx_Kennen_KennenBringTheLight_hit", 985698738, 0.6, -13),
    "league_kennen_vo_q": ("Play_vo_Kennen_KennenShurikenHurlMissile1_cast3D", 980636520, 1.4, -2),
    "league_kennen_vo_w": ("Play_vo_Kennen_KennenBringTheLight_cast3D", 211352200, 1.6, -2),
    "league_kennen_vo_e": ("Play_vo_Kennen_Spell3DEEnd", 445325403, 1.6, -2),
    "league_kennen_vo_r": ("Play_vo_Kennen_KennenShurikenStorm_cast3D", 1267184378, 2.6, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_kennen_skill": "ASSETS/Characters/Kennen/HUD/Icons2D/Kennen_Q.dds",
    "league_kennen_skill2": "ASSETS/Characters/Kennen/HUD/Icons2D/Kennen_E.dds",
    "league_kennen_ult": "ASSETS/Characters/Kennen/HUD/Icons2D/Kennen_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Kennen.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Kennen.{args.lang}.wad.client"))
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
