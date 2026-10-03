"""Pull Kayn's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_kayn.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Kayn.wad.client and Kayn.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events in the base bank: KaynBasicAttack_OnHit (one of 24 scythe hits), KaynQ_OnCast (the dash), KaynQ_spin,
KaynQ_hit, KaynE_OnBuffActivate (Shadow Step's ghost loop: its first second), KaynW_OnCast (the wind-up with the slash at
0.55 s, League's own cast time: one of the light set for the base and the Shadow Assassin, one of the heavy set for the
Darkin), KaynW_tar_B (a W hit), KaynR_Enemy_cast (the dive), KaynRHost_OnBuffActivate (inside the host),
KaynRExitCeremony_Self_buffdeactivate (bursting out), KaynW_tar_A (the exit's heavy hit), Recall3D_leadout_Slayer and
KaynPassive_Transform_Assassin_cast (the two transformations). Voice: Q, W and R casts, an R line for the exit, and
the passive's transformation lines of Rhaast and of the Shadow Assassin.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/kayn/skins/base/kayn_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/kayn/skins/base/kayn_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_kayn_sfx_attack_hit": ("Play_sfx_Kayn_KaynBasicAttack_OnHit", 549777424, 0.6, -12),
    "league_kayn_sfx_q_cast": ("Play_sfx_Kayn_KaynQ_OnCast", 978698516, 1.0, -9),
    "league_kayn_sfx_q_spin": ("Play_sfx_Kayn_KaynQ_spin", 1026080064, 1.2, -8),
    "league_kayn_sfx_q_hit": ("Play_sfx_Kayn_KaynQ_hit", 128231350, 0.5, -12),
    "league_kayn_sfx_e_cast": ("Play_sfx_Kayn_KaynE_OnBuffActivate", 763851370, 1.0, -12),
    "league_kayn_sfx_w_cast": ("Play_sfx_Kayn_KaynW_OnCast", 489721999, 1.5, -8),
    "league_kayn_sfx_w_cast_d": ("Play_sfx_Kayn_KaynW_OnCast", 524982709, 1.6, -7),
    "league_kayn_sfx_w_hit": ("Play_sfx_Kayn_KaynW_tar_B", 454572908, 1.0, -10),
    "league_kayn_sfx_r_cast": ("Play_sfx_Kayn_KaynR_Enemy_cast", 373471911, 1.4, -8),
    "league_kayn_sfx_r_enter": ("Play_sfx_Kayn_KaynRHost_OnBuffActivate", 1059587562, 1.5, -10),
    "league_kayn_sfx_r_exit": ("Play_sfx_Kayn_KaynRExitCeremony_Self_buffdeactivate", 283930643, 1.6, -6),
    "league_kayn_sfx_r_exit_hit": ("Play_sfx_Kayn_KaynW_tar_A", 366942513, 1.0, -8),
    "league_kayn_sfx_tf_d": ("Play_sfx_Kayn_Recall3D_leadout_Slayer", 905789645, 2.0, -6),
    "league_kayn_sfx_tf_s": ("Play_sfx_Kayn_KaynPassive_Transform_Assassin_cast", 671164105, 2.0, -6),
    "league_kayn_vo_q": ("Play_vo_Kayn_KaynQ_cast3D", 1740709634, 1.3, -2),
    "league_kayn_vo_w": ("Play_vo_Kayn_KaynW_cast3D", 345755885, 1.7, -2),
    "league_kayn_vo_r": ("Play_vo_Kayn_KaynR_cast3D", 1598390989, 1.9, -2),
    "league_kayn_vo_r_exit": ("Play_vo_Kayn_KaynR_cast3D", 822258008, 1.3, -2),
    "league_kayn_vo_tf_d": ("Play_vo_Kayn_Spell3DPCastRhaast", 376972408, 3.9, -1),
    "league_kayn_vo_tf_s": ("Play_vo_Kayn_Spell3DPCastAssassin", 656938422, 4.0, -1),
}
ICONS = {  # TFM2 slot -> Riot icon (Shadow Step rides on Reaping Slash, the passive on the hits)
    "league_kayn_skill": "ASSETS/Characters/Kayn/HUD/Icons2D/Kayn_Q_Primary.dds",
    "league_kayn_skill2": "ASSETS/Characters/Kayn/HUD/Icons2D/Kayn_W_Primary.dds",
    "league_kayn_ult": "ASSETS/Characters/Kayn/HUD/Icons2D/Kayn_R1_Primary.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Kayn.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Kayn.{args.lang}.wad.client"))
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
