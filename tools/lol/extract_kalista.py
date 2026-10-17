r"""Pull Kalista's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_kalista.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_elise.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Kalista.wad.client and Kalista.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

Her events (named in skin0.bin, listed with work/kl/sndprobe.py): the spear's wind-up KalistaBasicAttack_precast, its
throw _OnMissileLaunch and the hop _dash (Martial Poise); no basic-attack hit event exists, the spear's hit takes the
Oathsworn proc's KalistaCoopStrikeProc_hit_champ; Pierce KalistaMysticShot_OnCast and KalistaMysticShotMisTrue_hit;
Rend KalistaExpunge_cast; Fate's Call KalistaRx_OnCast (the call), KalistaRVFX_buffcast (the ally taken in),
KalistaRMis_OnMissileLaunch (the ally hurled) and KalistaRMis_hit (the knock-up). Voice: KalistaMysticShot_cast3D,
KalistaExpunge_cast3D, KalistaRMis_cast3D and KalistaVORNormal_OnBuffCast (the call).
Icons: Kalista_Q (Pierce) = skill, Kalista_E (Rend) = skill2, Kalista_R (Fate's Call) = ult; W (Sentinel, its passive
folded into the attack) and the passive are written too (league_kalista_w / _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/kalista/skins/base/kalista_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/kalista/skins/base/kalista_base_vo_"  # same in every language
P = "Play_sfx_Kalista_Kalista"
V = "Play_vo_Kalista_Kalista"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_kalista_sfx_a_wind": (P + "BasicAttack_precast", 164767999, 0.7, -14),
    "league_kalista_sfx_a_throw": (P + "BasicAttack_OnMissileLaunch", 390402215, 0.65, -13),
    "league_kalista_sfx_a_hit": (P + "CoopStrikeProc_hit_champ", 43133646, 0.6, -14),
    "league_kalista_sfx_hop": (P + "BasicAttack_dash", 1008159593, 0.6, -13),
    "league_kalista_sfx_w_hit": (P + "CoopStrikeProc_hit_champ", 902446865, 0.9, -11),
    "league_kalista_sfx_q": (P + "MysticShot_OnCast", 14780541, 1.3, -11),
    "league_kalista_sfx_q_hit": (P + "MysticShotMisTrue_hit", 284829634, 1.4, -11),
    "league_kalista_sfx_e": (P + "Expunge_cast", 234068376, 1.8, -10),
    "league_kalista_sfx_r": (P + "Rx_OnCast", 757480110, 2.0, -10),
    "league_kalista_sfx_r_take": (P + "RVFX_buffcast", 719119105, 1.6, -11),
    "league_kalista_sfx_r_fly": (P + "RMis_OnMissileLaunch", 512911862, 1.6, -11),
    "league_kalista_sfx_r_hit": (P + "RMis_hit", 308619276, 1.8, -10),
    "league_kalista_sfx_vo_q": (V + "MysticShot_cast3D", 1217008043, 1.6, -6),
    "league_kalista_sfx_vo_e": (V + "Expunge_cast3D", 1237865173, 1.6, -6),
    "league_kalista_sfx_vo_r": (V + "VORNormal_OnBuffCast", 230591231, 2.6, -6),
    "league_kalista_sfx_vo_r_fly": (V + "RMis_cast3D", 2032503181, 1.6, -6),
}
I = "ASSETS/Characters/Kalista/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_kalista_skill": I + "Kalista_Q.dds",
    "league_kalista_skill2": I + "Kalista_E.dds",
    "league_kalista_ult": I + "Kalista_R.dds",
    "league_kalista_w": I + "Kalista_W.dds",
    "league_kalista_passive": I + "Kalista_Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Kalista.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Kalista.{args.lang}.wad.client"))
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
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
