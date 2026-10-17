"""Pull Lissandra's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_lissandra.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Lissandra.wad.client and Lissandra.<lang>.wad.client, resolves the base-skin Wwise events
below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

Her events in the base bank (the client's own names): the attack is LissandraBasicAttack_OnCast and _OnMissileLaunch
(its _OnHit events hold no media, so the bolt's impact borrows LissandraREnemy_hit's shortest crack); Ice Shard casts
with LissandraQ_OnCast and LissandraQMissile_OnMissileLaunch and hits with LissandraQMissile_hit; Ring of Frost's cast
event is empty - the ring is LissandraWShards_buffdeactivate (the shards bursting out) and the root
LissandraWFrozen_root_champ; Glacial Path casts with LissandraE_OnCast and hits with LissandraEMissile_hit (another
variant is the blink); Frozen Tomb: LissandraRHandCas_buffactivate (the cast), LissandraRStun_hit (the tomb on a
champion), LissandraRSelf_OnBuffActivate (her own tomb), LissandraREnemy_hit (the burst's hits); the thrall:
LissandraPassiveVictim_OnBuffActivate (it rises) and _deactivate (it shatters). Voice: the Q, W, E lines and both R lines.
Icons: Lissandra_Q = skill, Lissandra_W = skill2 (E is folded into it), Lissandra_R = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/lissandra/skins/base/lissandra_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/lissandra/skins/base/lissandra_base_vo_"  # same in every language
P = "Play_sfx_Lissandra_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_lissandra_sfx_attack": (P + "LissandraBasicAttack_OnCast", 473899576, 0.5, -10),
    "league_lissandra_sfx_bolt": (P + "LissandraBasicAttack_OnMissileLaunch", 16230143, 0.4, -12),
    "league_lissandra_sfx_bolt_hit": (P + "LissandraREnemy_hit", 46634445, 0.4, -12),
    "league_lissandra_sfx_q": (P + "LissandraQ_OnCast", 643825179, 0.7, -8),
    "league_lissandra_sfx_q_fly": (P + "LissandraQMissile_OnMissileLaunch", 413378734, 0.8, -11),
    "league_lissandra_sfx_q_hit": (P + "LissandraQMissile_hit", 89890284, 0.6, -10),
    "league_lissandra_sfx_w": (P + "LissandraWShards_buffdeactivate", 818352297, 1.0, -7),
    "league_lissandra_sfx_w_root": (P + "LissandraWFrozen_root_champ", 190906653, 1.2, -9),
    "league_lissandra_sfx_e": (P + "LissandraE_OnCast", 433075901, 1.2, -8),
    "league_lissandra_sfx_e_hit": (P + "LissandraEMissile_hit", 967854283, 0.8, -9),
    "league_lissandra_sfx_e_port": (P + "LissandraEMissile_hit", 84981947, 0.8, -8),
    "league_lissandra_sfx_r": (P + "LissandraRHandCas_buffactivate", 120155278, 1.0, -8),
    "league_lissandra_sfx_r_tomb": (P + "LissandraRStun_hit", 29876803, 2.0, -7),
    "league_lissandra_sfx_r_self": (P + "LissandraRSelf_OnBuffActivate", 250995134, 2.6, -7),
    "league_lissandra_sfx_r_hit": (P + "LissandraREnemy_hit", 250748174, 0.5, -10),
    "league_lissandra_sfx_r_field": (P + "LissandraRExpand_buffactivate", 24355757, 2.0, -11),
    "league_lissandra_sfx_p_rise": (P + "LissandraPassiveVictim_OnBuffActivate", 208358864, 1.6, -9),
    "league_lissandra_sfx_p_burst": (P + "LissandraPassiveVictim_deactivate", 813373446, 1.4, -7),
    "league_lissandra_vo_q": ("Play_vo_Lissandra_LissandraQ_cast3D", 1675959389, 1.0, -4),
    "league_lissandra_vo_w": ("Play_vo_Lissandra_LissandraW_cast3D", 986867511, 1.0, -4),
    "league_lissandra_vo_e": ("Play_vo_Lissandra_LissandraE_cast3D", 394740928, 1.0, -4),
    "league_lissandra_vo_r": ("Play_vo_Lissandra_LissandraR_hit3DEnemy", 1961733793, 1.4, -3),
    "league_lissandra_vo_r_self": ("Play_vo_Lissandra_LissandraR_hit3DSelf", 1364197597, 1.4, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_lissandra_skill": "ASSETS/Characters/Lissandra/HUD/Icons2D/Lissandra_Q.dds",
    "league_lissandra_skill2": "ASSETS/Characters/Lissandra/HUD/Icons2D/Lissandra_W.dds",
    "league_lissandra_ult": "ASSETS/Characters/Lissandra/HUD/Icons2D/Lissandra_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Lissandra.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Lissandra.{args.lang}.wad.client"))
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
