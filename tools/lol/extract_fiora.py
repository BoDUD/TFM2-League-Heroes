"""Pull Fiora's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_fiora.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Fiora.wad.client and Fiora.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Fiora's skin bin. The basic attack has its swing and its hit, Bladework (E) the cast, the
first empowered hit and the second (the crit, whose swing is the crit attack's); Lunge (Q) the dash and the stab's
own hit (the first four variants of FioraQAttack are Q's, the rest are the shared attack hits); Duelist's Dance the
chime of a revealed Vital and the burst of speed when one is struck; Riposte (W) the parry, the parried crowd
control (played when the stab stuns), the stab and its slow and stun hits; Grand Challenge (R) the four Vitals
appearing, a Vital struck and the healing zone. Voice (zh_CN): Q's grunt on the stab, W's and R's cast lines (the
longest take of R's four); Bladework has no voice event.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/fiora/skins/base/fiora_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/fiora/skins/base/fiora_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_fiora_sfx_attack_swing": ("Play_sfx_Fiora_FioraBasicAttack_OnCast", 227402369, 0.45, -6),
    "league_fiora_sfx_attack_hit": ("Play_sfx_Fiora_FioraBasicAttack_OnHit", 492333429, 0.45, -8),
    "league_fiora_sfx_e_cast": ("Play_sfx_Fiora_FioraE_OnCast", 687216270, 1.1, -6),
    "league_fiora_sfx_e_hit": ("Play_sfx_Fiora_FioraEAttack_OnHit", 751359322, 0.8, -5),
    "league_fiora_sfx_e_crit": ("Play_sfx_Fiora_FioraEAttack2_OnHit", 813003588, 1.0, -4),
    "league_fiora_sfx_q_cast": ("Play_sfx_Fiora_FioraQ_OnCast", 4179099, 0.8, -4),
    "league_fiora_sfx_q_hit": ("Play_sfx_Fiora_FioraQAttack_OnBuffCast", 759936634, 0.85, -5),
    "league_fiora_sfx_vital_ready": ("Play_sfx_Fiora_FioraPassiveReadySound_OnBuffActivate", 531862447, 0.8, -8),
    "league_fiora_sfx_vital_hit": ("Play_sfx_Fiora_FioraPassiveSpeed_OnBuffActivate", 512697418, 1.6, -4),
    "league_fiora_sfx_w_cast": ("Play_sfx_Fiora_FioraW_OnCast", 51453556, 0.9, -4),
    "league_fiora_sfx_w_block": ("Play_sfx_Fiora_FioraWBlockCCSound_OnBuffCast", 164745483, 1.0, -4),
    "league_fiora_sfx_w_stab": ("Play_sfx_Fiora_FioraWMissile_OnMissileLaunch", 748161656, 0.7, -4),
    "league_fiora_sfx_w_slow": ("Play_sfx_Fiora_FioraWSlow_hit", 138233965, 0.7, -5),
    "league_fiora_sfx_w_stun": ("Play_sfx_Fiora_FioraWStun_hit", 1022722360, 1.0, -4),
    "league_fiora_sfx_r_cast": ("Play_sfx_Fiora_FioraRMark_OnBuffActivate", 172374818, 2.0, -4),
    "league_fiora_sfx_r_hit": ("Play_sfx_Fiora_FioraRHitSound_OnBuffActivate", 489521047, 1.1, -4),
    "league_fiora_sfx_r_heal": ("Play_sfx_Fiora_FioraRHeal_buffactivate", 45821837, 3.0, -5),
    "league_fiora_vo_q": ("Play_vo_Fiora_Spell3DQHit", 1665959421, 0.55, -2),
    "league_fiora_vo_w": ("Play_vo_Fiora_FioraW_cast3D", 597970829, 0.95, -2),
    "league_fiora_vo_r": ("Play_vo_Fiora_FioraR_cast3D", 635146265, 2.1, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_fiora_skill": "ASSETS/Characters/Fiora/HUD/Icons2D/Fiora_Q.dds",
    "league_fiora_skill2": "ASSETS/Characters/Fiora/HUD/Icons2D/Fiora_W.dds",
    "league_fiora_ult": "ASSETS/Characters/Fiora/HUD/Icons2D/Fiora_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Fiora.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Fiora.{args.lang}.wad.client"))
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
