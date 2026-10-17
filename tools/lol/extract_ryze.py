"""Pull Ryze's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_ryze.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Ryze.wad.client and Ryze.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN
(Tencent client) by default.

His events in the base bank: RyzeBasicAttack_OnMissileLaunch / _OnHit (the rune orb), RyzeQ_OnMissileLaunch,
RyzeQ_hit and RyzeQ_hit_bounce (Overload, its bounce on the Flux'd), RyzeW_OnCast and RyzeW_hit (Rune Prison),
RyzeE_OnMissileLaunch and RyzeEMissile_OnHit (Spell Flux), RyzeRChannel_buffactivate and RyzeR_teleport (Realm Warp);
voice: RyzeQ_cast3D, RyzeE_cast3D and RyzeR_cast3D (spoken in the client's language). The icons: Ryze_Q = Q,
Ryze_W = skill2 (the combo E -> W -> Q, named after its root), Ryze_R = R (the passive has no slot).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/ryze/skins/base/ryze_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/ryze/skins/base/ryze_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_ryze_sfx_attack": ("Play_sfx_Ryze_RyzeBasicAttack_OnMissileLaunch", 476753897, 0.7, -10),
    "league_ryze_sfx_attack_hit": ("Play_sfx_Ryze_RyzeBasicAttack_OnHit", 1006539441, 0.6, -10),
    "league_ryze_sfx_q_cast": ("Play_sfx_Ryze_RyzeQ_OnMissileLaunch", 188848889, 1.2, -7),
    "league_ryze_sfx_q_hit": ("Play_sfx_Ryze_RyzeQ_hit", 522428877, 0.8, -8),
    "league_ryze_sfx_q_pop": ("Play_sfx_Ryze_RyzeQ_hit_bounce", 966785484, 0.5, -9),
    "league_ryze_sfx_w_cast": ("Play_sfx_Ryze_RyzeW_OnCast", 30382961, 0.5, -8),
    "league_ryze_sfx_w_hit": ("Play_sfx_Ryze_RyzeW_hit", 109603367, 1.8, -7),
    "league_ryze_sfx_e_cast": ("Play_sfx_Ryze_RyzeE_OnMissileLaunch", 146645905, 0.6, -8),
    "league_ryze_sfx_e_hit": ("Play_sfx_Ryze_RyzeEMissile_OnHit", 253034213, 0.45, -8),
    "league_ryze_sfx_r_cast": ("Play_sfx_Ryze_RyzeRChannel_buffactivate", 445978756, 2.4, -6),
    "league_ryze_sfx_r_warp": ("Play_sfx_Ryze_RyzeR_teleport", 151293173, 1.4, -6),
    "league_ryze_sfx_vo_q": ("Play_vo_Ryze_RyzeQ_cast3D", 380104592, 1.0, -2),
    "league_ryze_sfx_vo_e": ("Play_vo_Ryze_RyzeE_cast3D", 1059162823, 1.0, -2),
    "league_ryze_sfx_vo_r": ("Play_vo_Ryze_RyzeR_cast3D", 337088990, 2.6, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_ryze_skill": "ASSETS/Characters/Ryze/HUD/Icons2D/Ryze_Q.dds",
    "league_ryze_skill2": "ASSETS/Characters/Ryze/HUD/Icons2D/Ryze_W.dds",
    "league_ryze_ult": "ASSETS/Characters/Ryze/HUD/Icons2D/Ryze_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Ryze.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Ryze.{args.lang}.wad.client"))
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
